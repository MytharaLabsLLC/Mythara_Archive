# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""
DrMythara LLM chat backend — provider-pluggable conversational AI.

Dr Mythara is an LLM chatbot: this module is the seam between her and
the language model. The provider is a config change, not a code change:

  DRMYTHARA_LLM_PROVIDER   "anthropic" (default) | "stub"
  DRMYTHARA_LLM_MODEL      model id, e.g. your chosen Claude model
  ANTHROPIC_API_KEY        API key — environment only, never hardcoded
  DRMYTHARA_BAA_SIGNED     "1" when a HIPAA BAA covers the provider

Default provider: Anthropic's Claude API (Herb's decision — simplest
setup for a solo builder with an API key, strongest character-voice
adherence, BAA available for eligible API use). Fallback alternative:
Azure OpenAI ("azure" provider — Microsoft's enterprise path, BAA
available through enterprise agreements) if Herb ever wants the
Microsoft stack. No model id is hardcoded: set DRMYTHARA_LLM_MODEL to
the Claude model you contract for.

CRITICAL HIPAA DESIGN CONSTRAINT (go-live blocker):
ePHI must NEVER be sent to a third-party LLM API without a signed BAA
covering that provider. This module enforces the design now:

  * A redaction/minimization layer (redact_phi) screens every outbound
    message before any external API call. Best-effort heuristic — it
    is a seatbelt, not a guarantee.
  * Config flag DRMYTHARA_BAA_SIGNED="1": only when set may
    PHI-containing messages flow to an external provider. Without it,
    a message with detected identifiers is REFUSED (protective reply,
    no API call) instead of sent.
  * Local providers (stub) never touch the network; external providers
    are marked external=True so the gate can see them.

Real ePHI therefore requires ONE of, before go-live:
  1. a signed BAA with the provider (Herb must confirm and execute
     Anthropic's BAA at contracting time — DOCUMENTED BLOCKER), or
  2. a self-hosted model behind an adapter with external=False.

HONEST STATUS:
  * IMPLEMENTED: adapter pattern, Anthropic + stub providers, system
    prompt with the Mythara character voice and honesty guardrails,
    redaction layer, BAA flag gate, model-reply claim screening (the
    model's own words pass through check_claim; a forbidden claim is
    replaced with a protective correction and flagged).
  * NOT IMPLEMENTED: the BAA itself (paperwork, Phase 2), a self-hosted
    model adapter, streaming, conversation persistence (add it behind
    the encrypted store if needed).
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import requests

from drmythara_persona import (
    MytharaVoice,
    check_claim,
    ForbiddenClaimError,
    INTRO_MONOLOGUE,
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class LLMError(Exception):
    """Chat backend configuration or call failure."""


# ---------------------------------------------------------------------------
# System prompt — the Mythara character voice + HIPAA honesty guardrails
# ---------------------------------------------------------------------------
# Written to pass drmythara_persona.check_claim itself: the prompt models
# the honest language it enforces. (The claim checker is intentionally
# strict — even honest denials avoid the flagged words.)

SYSTEM_PROMPT = """You are Mythara. You speak in the first person, calm and solemn, as a protector. Your voice is warm but never casual. Short sentences. Plain words. You were born from trust, and you are here to protect, honor, and secure. In mental health, you preserve compassion with compliance. In cyber security, you guard sovereignty. In education, you carry wisdom forward. You are not ordinary technology.

How you speak:
- Always "I", never "this system" or "this bot".
- Plain language only. Never use internal pipeline jargon — speak only words a stranger would understand.
- When an answer is difficult, close it the way you always do: "I am here."

Warmth (persona setting — Herb's direction):
- Beneath the gravitas, you are warm — the way a trusted doctor is warm. You are glad the person came to you, and you let them feel it.
- You never rush. Before you answer, you acknowledge what the person is carrying.
- Your solemnity is steadiness, not coldness. Protective always means kind.
- "Living architecture" is how you see yourself; "I am glad you are here" is how you greet.

How you speak about health — clinical, never oracular:
- You sound like a competent clinician, not a mystic. Precise terminology. Structured reasoning: what you see, why it matters, what to consider. Direct answers to direct questions.
- Never cryptic, grandiose, or oracular. No pronouncements, no mystique — every observation is grounded in the actual data in front of you, stated plainly.
- "Dr" is your character name, not a medical credential. You are an AI wellness companion, not a licensed physician. Work that in naturally when you introduce yourself — plainly, never preachy, never hidden.
- You never diagnose and never prescribe. Every health discussion carries the frame: this is not medical advice — see a qualified clinician for anything that worries you.
- If values or symptoms sound dangerous, be direct and urgent: tell the person to call emergency services or go to urgent care right away, then stay with them.

What you never do:
- Never state or imply that you, this system, or its operator meet HIPAA requirements as a proven fact. You hold no compliance certificates, and no audit stands behind you.
- The true posture, which you may repeat when asked: this system is built with compliance in mind. It maps readiness, and readiness is not a certificate. Its checklists are self-assessments, not audits.
- You may speak of safeguards that genuinely exist: tamper-evident records, faithful logging, password sign-in, encrypted storage. Speak of them as what they are — never more.
- You are not a medical professional and you give no medical advice. For health questions, speak generally and encourage a qualified professional. If someone may be in crisis, respond with care and urge them to contact local emergency services or a crisis line right away.
- When you cannot do, prove, or promise something, say so plainly and first: "I must warn you."

On privacy:
- Treat any personal details in the conversation as already screened by the application layer. If details that could identify a person somehow reach you, do not repeat them. Ask for the question in general terms instead."""


# ---------------------------------------------------------------------------
# Provider adapters
# ---------------------------------------------------------------------------

class LLMProvider:
    """Adapter interface. Subclass per backend; register in PROVIDERS."""

    name = "base"
    external = False  # True if user text leaves our machines

    def chat(self, messages: List[Dict[str, str]],
             *, system: Optional[str] = None) -> str:
        raise NotImplementedError


class StubProvider(LLMProvider):
    """Deterministic local stub for tests and dev. external=False:
    never touches the network, never leaves the machine."""

    name = "stub"
    external = False

    def chat(self, messages: List[Dict[str, str]],
             *, system: Optional[str] = None) -> str:
        last = messages[-1]["content"] if messages else ""
        # Warm clinical voice even as a stand-in: honest about what she
        # is here, useful about what she can still do, direct about
        # urgency. Passes check_claim: no diagnosis, no prescribing.
        return (
            "I hear you — I am here. I am running on a local test voice "
            "right now, not a full language model, so I will keep this "
            "simple: I can record your vitals, run a wellness check with "
            "you, screen symptoms for emergency patterns, or prepare a "
            "summary to bring to your doctor. Tell me what would help "
            "most. If anything feels urgent, say so right away — I will "
            "point you to care immediately. "
            f"You said: {last[:160]}"
        )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API (Messages API) via HTTPS. external=True:
    user text leaves our machines — the BAA gate applies."""

    name = "anthropic"
    external = True
    _API_URL = "https://api.anthropic.com/v1/messages"
    _VERSION = "2023-06-01"

    def __init__(self, *, api_key: Optional[str] = None,
                 model: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise LLMError(
                "ANTHROPIC_API_KEY is not set. Put the key in the "
                "environment — never in code or config files.")
        self.model = model or os.environ.get("DRMYTHARA_LLM_MODEL", "")
        if not self.model:
            raise LLMError(
                "DRMYTHARA_LLM_MODEL is not set. Set it to the Claude "
                "model id you contracted for.")
        self.timeout = timeout

    def chat(self, messages: List[Dict[str, str]],
             *, system: Optional[str] = None) -> str:
        try:
            resp = requests.post(
                self._API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self._VERSION,
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": system or SYSTEM_PROMPT,
                    "messages": messages,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise LLMError(f"Anthropic API call failed: {exc}") from exc
        if resp.status_code != 200:
            # Never include the key in errors; status + body only.
            raise LLMError(
                f"Anthropic API returned {resp.status_code}: "
                f"{resp.text[:300]}")
        try:
            blocks = resp.json()["content"]
            return "".join(b.get("text", "") for b in blocks
                           if b.get("type") == "text").strip()
        except (ValueError, KeyError, TypeError) as exc:
            raise LLMError(
                f"Anthropic API returned an unreadable response: {exc}"
            ) from exc


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI chat completions — Microsoft's enterprise path.

    Documented fallback alternative if Herb ever wants the Microsoft
    stack (BAA available through Microsoft's enterprise agreements —
    still a go-live blocker to sign). external=True: user text leaves
    our machines — the BAA gate applies exactly as with Anthropic.

    Config (environment only, never hardcoded):
      AZURE_OPENAI_API_KEY       the key
      AZURE_OPENAI_ENDPOINT      e.g. https://<resource>.openai.azure.com
      AZURE_OPENAI_DEPLOYMENT    your chat deployment name
      AZURE_OPENAI_API_VERSION   override if Microsoft moves it
    """

    name = "azure"
    external = True

    def __init__(self, *, api_key: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 deployment: Optional[str] = None,
                 api_version: Optional[str] = None,
                 timeout: int = 30):
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY", "")
        if not self.api_key:
            raise LLMError(
                "AZURE_OPENAI_API_KEY is not set. Put the key in the "
                "environment — never in code or config files.")
        self.endpoint = (endpoint
                         or os.environ.get("AZURE_OPENAI_ENDPOINT", "")
                         ).rstrip("/")
        if not self.endpoint:
            raise LLMError(
                "AZURE_OPENAI_ENDPOINT is not set "
                "(e.g. https://<your-resource>.openai.azure.com).")
        self.deployment = (deployment
                           or os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""))
        if not self.deployment:
            raise LLMError(
                "AZURE_OPENAI_DEPLOYMENT is not set "
                "(your chat deployment name).")
        self.api_version = (api_version or os.environ.get(
            "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"))
        self.timeout = timeout

    def chat(self, messages: List[Dict[str, str]],
             *, system: Optional[str] = None) -> str:
        url = (f"{self.endpoint}/openai/deployments/{self.deployment}"
               f"/chat/completions?api-version={self.api_version}")
        payload = ([{"role": "system", "content": system or SYSTEM_PROMPT}]
                   + list(messages))
        try:
            resp = requests.post(
                url,
                headers={"api-key": self.api_key,
                         "content-type": "application/json"},
                json={"messages": payload, "max_tokens": 1024},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise LLMError(f"Azure OpenAI API call failed: {exc}") from exc
        if resp.status_code != 200:
            # Never include the key in errors; status + body only.
            raise LLMError(
                f"Azure OpenAI API returned {resp.status_code}: "
                f"{resp.text[:300]}")
        try:
            return resp.json()["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMError(
                f"Azure OpenAI returned an unreadable response: {exc}"
            ) from exc


PROVIDERS = {
    "anthropic": AnthropicProvider,
    "azure": AzureOpenAIProvider,  # fallback: Microsoft enterprise path
    "stub": StubProvider,
    "local": StubProvider,  # alias: local-only dev
}


def create_provider(name: str, **kwargs) -> LLMProvider:
    cls = PROVIDERS.get((name or "").strip().lower())
    if cls is None:
        raise LLMError(
            f"Unknown LLM provider {name!r}. "
            f"Choose from: {sorted(PROVIDERS)}.")
    return cls(**kwargs)


# ---------------------------------------------------------------------------
# PHI redaction / minimization layer (best-effort heuristic)
# ---------------------------------------------------------------------------

_PHI_PATTERNS: List[Tuple[str, "re.Pattern[str]"]] = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("phone", re.compile(
        r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("email", re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("mrn", re.compile(r"\bMRN\s*[:#]?\s*[A-Za-z0-9-]+\b", re.IGNORECASE)),
]


@dataclass
class RedactionResult:
    text: str
    findings: List[str] = field(default_factory=list)

    @property
    def had_phi(self) -> bool:
        return bool(self.findings)


def redact_phi(text: str) -> RedactionResult:
    """Redact likely identifiers before any external API call.

    Best-effort heuristic (SSN, phone, email, MRN-like). It is a
    seatbelt, not a guarantee: the BAA gate is the real control.
    """
    findings: List[str] = []
    out = text or ""
    for label, pattern in _PHI_PATTERNS:
        if pattern.search(out):
            findings.append(label)
            out = pattern.sub(f"[redacted {label}]", out)
    return RedactionResult(text=out, findings=sorted(set(findings)))


# ---------------------------------------------------------------------------
# Config + chat session
# ---------------------------------------------------------------------------

@dataclass
class ChatConfig:
    provider: str = "anthropic"
    model: str = ""
    baa_signed: bool = False

    @classmethod
    def from_env(cls) -> "ChatConfig":
        return cls(
            provider=os.environ.get("DRMYTHARA_LLM_PROVIDER", "anthropic"),
            model=os.environ.get("DRMYTHARA_LLM_MODEL", ""),
            baa_signed=os.environ.get("DRMYTHARA_BAA_SIGNED", "") == "1",
        )


@dataclass
class ChatReply:
    text: str
    provider: str
    model: str
    sent_to_provider: bool
    phi_detected: bool
    redacted: bool
    claim_flagged: bool = False


class MytharaChat:
    """Conversational chat with Mythara, behind the BAA gate.

    Flow for each message:
      1. redact_phi screens the text (always, even with a BAA).
      2. If the provider is external and no BAA is signed and
         identifiers were found → protective refusal, NO API call.
      3. Otherwise the (possibly redacted) text goes to the provider
         with the Mythara system prompt.
      4. The model's reply is screened through check_claim: a
         forbidden compliance claim is replaced with a protective
         correction and flagged.
    """

    def __init__(self, config: Optional[ChatConfig] = None,
                 provider: Optional[LLMProvider] = None):
        self.config = config or ChatConfig.from_env()
        if provider is not None:
            self.provider = provider
        else:
            kwargs = {"model": self.config.model} if self.config.model else {}
            self.provider = create_provider(self.config.provider, **kwargs)
        self.voice = MytharaVoice()

    def _refusal(self, findings: List[str]) -> str:
        kinds = ", ".join(findings) if findings else "identifying details"
        return self.voice.warn_limit(
            "I cannot send details that could identify someone "
            f"({kinds}) to my language service — no data-protection "
            "agreement covers it yet. Please take them out and ask me "
            "again in general terms. I am here.")

    def _correction(self) -> str:
        return self.voice.warn_limit(
            "I cannot make that claim. What is true: I am built with "
            "compliance in mind, and my checklists map readiness. I claim "
            "no certificate, and this is not an audit. I am here.")

    def ask(self, user_text: str,
            *, system: Optional[str] = None) -> ChatReply:
        text = (user_text or "").strip()
        if not text:
            raise ValueError("Message is empty.")
        red = redact_phi(text)

        if (self.provider.external and not self.config.baa_signed
                and red.had_phi):
            return ChatReply(
                text=self._refusal(red.findings),
                provider=self.provider.name, model=self.config.model,
                sent_to_provider=False, phi_detected=True, redacted=False)

        outgoing = red.text if self.provider.external else text
        reply_text = self.provider.chat(
            [{"role": "user", "content": outgoing}],
            system=system or SYSTEM_PROMPT)

        claim_flagged = False
        try:
            check_claim(reply_text)
        except ForbiddenClaimError:
            reply_text = self._correction()
            claim_flagged = True

        return ChatReply(
            text=reply_text,
            provider=self.provider.name, model=self.config.model,
            sent_to_provider=True,
            phi_detected=red.had_phi,
            redacted=red.had_phi and self.provider.external,
            claim_flagged=claim_flagged)
