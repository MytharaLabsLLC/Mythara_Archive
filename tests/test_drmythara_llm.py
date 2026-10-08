"""Tests for Commercial/drmythara_llm.py — the provider-pluggable LLM
chat backend, the BAA gate, and the model-reply claim screening."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

import drmythara_llm as llm
from drmythara_llm import (
    SYSTEM_PROMPT,
    MytharaChat,
    ChatConfig,
    StubProvider,
    AnthropicProvider,
    AzureOpenAIProvider,
    LLMProvider,
    LLMError,
    create_provider,
    redact_phi,
)
from drmythara_persona import check_claim


class FakeExternalProvider(LLMProvider):
    """External provider stand-in that records calls instead of HTTP."""
    name = "fake-external"
    external = True

    def __init__(self):
        self.calls = []
        self.reply = "I hear you."

    def chat(self, messages, *, system=None):
        self.calls.append({"messages": messages, "system": system})
        return self.reply


# -- system prompt --------------------------------------------------------------------

def test_system_prompt_passes_claim_check():
    assert check_claim(SYSTEM_PROMPT) == SYSTEM_PROMPT


def test_system_prompt_embodies_character():
    assert "You are Mythara" in SYSTEM_PROMPT
    assert "I am here." in SYSTEM_PROMPT
    assert "first person" in SYSTEM_PROMPT


def test_system_prompt_has_honesty_guardrails():
    lowered = SYSTEM_PROMPT.lower()
    assert "built with compliance in mind" in lowered
    assert "self-assessments, not audits" in lowered
    assert "no medical advice" in lowered


def test_system_prompt_has_warmth_setting():
    lowered = SYSTEM_PROMPT.lower()
    assert "trusted doctor" in lowered
    assert "glad" in lowered
    assert "steadiness, not coldness" in lowered


# -- redaction --------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("my ssn is 123-45-6789 ok", "ssn"),
    ("call me at 303-555-0142", "phone"),
    ("email jane@example.com now", "email"),
    ("MRN: 987654321 admitted", "mrn"),
])
def test_redactor_finds_identifiers(text, expected):
    red = redact_phi(text)
    assert red.had_phi
    assert expected in red.findings
    assert f"[redacted {expected}]" in red.text


def test_redactor_clean_text_untouched():
    red = redact_phi("What are the HIPAA access control requirements?")
    assert not red.had_phi
    assert red.text == "What are the HIPAA access control requirements?"


# -- providers -----------------------------------------------------------------------------

def test_stub_provider_is_local_and_deterministic():
    p = StubProvider()
    assert p.external is False
    text = p.chat([{"role": "user", "content": "hi"}])
    # the stand-in says so plainly, in her voice — never a real model
    assert "local test voice" in text.lower()
    assert "not a full language model" in text.lower()
    assert "hi" in text
    # deterministic
    assert p.chat([{"role": "user", "content": "hi"}]) == text


def test_unknown_provider_rejected():
    with pytest.raises(LLMError):
        create_provider("skynet")


def test_anthropic_needs_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider(model="some-model")


def test_anthropic_needs_model(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.delenv("DRMYTHARA_LLM_MODEL", raising=False)
    with pytest.raises(LLMError, match="DRMYTHARA_LLM_MODEL"):
        AnthropicProvider()


def test_anthropic_builds_correct_request(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    captured = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return {"content": [{"type": "text", "text": "Hello, I am here."}]}

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json)
        return FakeResp()

    monkeypatch.setattr(llm.requests, "post", fake_post)
    p = AnthropicProvider(model="claude-test")
    out = p.chat([{"role": "user", "content": "hi"}])
    assert out == "Hello, I am here."
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "test-key-123"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert captured["json"]["model"] == "claude-test"
    assert captured["json"]["system"] == SYSTEM_PROMPT
    assert captured["json"]["messages"] == [{"role": "user", "content": "hi"}]


def test_anthropic_http_error_surfaces_without_key_leak(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "super-secret-key")

    class FakeResp:
        status_code = 401
        text = "invalid key"

    monkeypatch.setattr(llm.requests, "post",
                        lambda *a, **k: FakeResp())
    p = AnthropicProvider(model="claude-test")
    with pytest.raises(LLMError) as exc:
        p.chat([{"role": "user", "content": "hi"}])
    assert "401" in str(exc.value)
    assert "super-secret-key" not in str(exc.value)


# -- azure fallback -----------------------------------------------------------------

def _azure_env(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "azure-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT",
                       "https://myres.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "my-deploy")


def test_azure_needs_config(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMError, match="AZURE_OPENAI_API_KEY"):
        AzureOpenAIProvider()


def test_azure_builds_correct_request(monkeypatch):
    _azure_env(monkeypatch)
    captured = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "Warm hello."}}]}

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json)
        return FakeResp()

    monkeypatch.setattr(llm.requests, "post", fake_post)
    p = AzureOpenAIProvider()
    out = p.chat([{"role": "user", "content": "hi"}])
    assert out == "Warm hello."
    assert captured["url"] == (
        "https://myres.openai.azure.com/openai/deployments/my-deploy"
        "/chat/completions?api-version=2024-08-01-preview")
    assert captured["headers"]["api-key"] == "azure-key"
    msgs = captured["json"]["messages"]
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"] == SYSTEM_PROMPT
    assert msgs[1] == {"role": "user", "content": "hi"}


def test_azure_is_external_and_registered():
    p = AzureOpenAIProvider(api_key="k", endpoint="https://x",
                            deployment="d")
    assert p.external is True
    assert isinstance(create_provider("azure", api_key="k",
                                     endpoint="https://x",
                                     deployment="d"),
                      AzureOpenAIProvider)


# -- BAA gate ---------------------------------------------------------------------------------

def test_phi_message_refused_without_baa_no_api_call():
    provider = FakeExternalProvider()
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=provider)
    reply = chat.ask("My SSN is 123-45-6789, what should I do?")
    assert reply.sent_to_provider is False
    assert reply.phi_detected is True
    assert provider.calls == []  # no API call was made
    assert "I must warn you" in reply.text
    check_claim(reply.text)  # the refusal itself is honest


def test_clean_message_sent_when_no_baa():
    provider = FakeExternalProvider()
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=provider)
    reply = chat.ask("What are access controls?")
    assert reply.sent_to_provider is True
    assert reply.text == "I hear you."
    sent_text = provider.calls[0]["messages"][0]["content"]
    assert sent_text == "What are access controls?"


def test_phi_redacted_before_external_call_without_baa_allows_clean():
    # A message where identifiers get redacted still carries phi_detected,
    # so it is refused — redaction is the seatbelt, the gate is the wall.
    provider = FakeExternalProvider()
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=provider)
    reply = chat.ask("Call 303-555-0142 about the audit")
    assert reply.sent_to_provider is False
    assert provider.calls == []


def test_baa_signed_allows_phi_to_flow():
    provider = FakeExternalProvider()
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=True),
                       provider=provider)
    reply = chat.ask("My SSN is 123-45-6789, what should I do?")
    assert reply.sent_to_provider is True
    assert reply.phi_detected is True
    assert len(provider.calls) == 1


def test_local_provider_never_gated():
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=StubProvider())
    reply = chat.ask("My SSN is 123-45-6789 hi")
    assert reply.sent_to_provider is True  # local: nothing leaves


def test_model_reply_claim_screened():
    provider = FakeExternalProvider()
    provider.reply = "Good news — we are HIPAA compliant."
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=provider)
    reply = chat.ask("Are we compliant?")
    assert reply.claim_flagged is True
    assert "I cannot make that claim" in reply.text
    check_claim(reply.text)


def test_model_reply_clean_passes_through():
    provider = FakeExternalProvider()
    provider.reply = "I have logged your question faithfully."
    chat = MytharaChat(config=ChatConfig(provider="stub", baa_signed=False),
                       provider=provider)
    reply = chat.ask("Hi")
    assert reply.claim_flagged is False
    assert reply.text == "I have logged your question faithfully."


def test_empty_message_rejected():
    chat = MytharaChat(config=ChatConfig(provider="stub"),
                       provider=StubProvider())
    with pytest.raises(ValueError):
        chat.ask("   ")


# -- config --------------------------------------------------------------------------------------

def test_default_provider_is_anthropic(monkeypatch):
    monkeypatch.delenv("DRMYTHARA_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DRMYTHARA_BAA_SIGNED", raising=False)
    cfg = ChatConfig.from_env()
    assert cfg.provider == "anthropic"
    assert cfg.baa_signed is False


def test_baa_flag_from_env(monkeypatch):
    monkeypatch.setenv("DRMYTHARA_BAA_SIGNED", "1")
    assert ChatConfig.from_env().baa_signed is True
