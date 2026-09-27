# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Voice composer for autonomous outreach.

NOT a template engine. There are no {first_name} mail-merges here. Each
email is composed from the prospect's research brief plus one structural
variant (the variant is what the learning loop selects and scores).

Voice principles (enforced by construction, not by hope):
  * Write like one person to another. Short sentences. No corporate gloss.
  * Exactly one real reason for contact, taken from the brief's
    reason_for_contact. Never invented.
  * Brief facts only. If the brief doesn't say it, the email doesn't say it.
  * No flattery, no fake familiarity, no urgency, no scarcity.
  * The pitch is one line: "I build AI that can answer for itself."
  * Plain subject lines a human would write.
  * Every email ends with the honest footer: who I am, why they got this,
    and a working opt-out ("reply stop").

Variants exist so the learning loop has something to learn over — they are
compositional approaches, not scripts. The composer renders each one fresh
from the brief every time.
"""

from typing import Any, Dict, List, Tuple

from . import config
from . import research

SENDER_NAME = "Herbert Velez Jr."
SENDER_LINE = "Herbert Velez Jr. — Mythara (mythara.engine@yahoo.com)"

FOOTER_BASE = (
    "\n\n—\n"
    f"{SENDER_LINE}\n"
    "You're getting this because I researched your work and thought this "
    "might be useful. If I'm wrong, reply 'stop' and I'll never email you again."
)


def _footer() -> str:
    """Honest footer: who I am, why they got this, working opt-out, and the
    CAN-SPAM postal address when configured. Real sends are blocked until
    the address is set (see run.py), so a missing address here means
    dry-run only — never a non-compliant real send."""
    footer = FOOTER_BASE
    if config.CANSPAM_POSTAL_ADDRESS.strip():
        footer += f"\n{config.CANSPAM_POSTAL_ADDRESS.strip()}"
    return footer

# The honest offer. Concrete, no hype, no fake numbers.
OFFER_DIRECT = (
    "I build AI systems that can prove what they did — every action "
    "hash-chained, every decision witnessed, receipts you can hand an "
    "auditor. I do it as project work, $5-15K per build, starting with a "
    "small paid pilot so you can see the receipts before committing to more."
)
OFFER_SHORT = (
    "I build AI that can answer for itself — hash-chained proof of every "
    "action, delivered as project work ($5-15K per build, starting with a "
    "small paid pilot)."
)

VARIANTS = ("direct", "mechanism", "question")


def _fact_line(facts: List[Dict[str, str]]) -> str:
    """Render the brief's facts as plain sentences. Facts only, no dressing."""
    if not facts:
        return "I'll be honest: I don't know much about your setup yet."
    return " ".join(f["fact"].rstrip(".") + "." for f in facts)


def _compose_direct(p: Dict[str, Any], brief: Dict[str, Any]) -> Tuple[str, str]:
    name = p["name"].split()[0] if p["name"] else "there"
    facts = _fact_line(brief["facts"])
    subject = f"quick question, {name}" if name != "there" else "quick question"
    body = (
        f"Hi {name},\n\n"
        f"{brief['reason_for_contact']}\n\n"
        f"{facts}\n\n"
        f"{OFFER_SHORT}\n\n"
        "Worth a 15-minute call next week, or am I off base?"
        f"{_footer()}"
    )
    return subject, body


def _compose_mechanism(p: Dict[str, Any], brief: Dict[str, Any]) -> Tuple[str, str]:
    name = p["name"].split()[0] if p["name"] else "there"
    subject = "AI that can answer for itself"
    body = (
        f"Hi {name},\n\n"
        f"{OFFER_DIRECT}\n\n"
        f"Why you specifically: {brief['reason_for_contact']} "
        f"{_fact_line(brief['facts'])}\n\n"
        "If accountability for your agents is on your roadmap, I'd like to "
        "show you what the receipts look like. 15 minutes, no deck."
        f"{_footer()}"
    )
    return subject, body


def _compose_question(p: Dict[str, Any], brief: Dict[str, Any]) -> Tuple[str, str]:
    name = p["name"].split()[0] if p["name"] else "there"
    subject = "how do you audit your agents?"
    body = (
        f"Hi {name},\n\n"
        "Genuine question: when someone asks what your agents did and why — "
        "a customer, an auditor, your own team — what do you show them?\n\n"
        f"{brief['reason_for_contact']} {_fact_line(brief['facts'])}\n\n"
        f"{OFFER_SHORT}\n\n"
        "Curious how you're handling this today, even if it's 'we aren't yet.'"
        f"{_footer()}"
    )
    return subject, body


_COMPOSERS = {
    "direct": _compose_direct,
    "mechanism": _compose_mechanism,
    "question": _compose_question,
}


def compose_followup(
    p: Dict[str, Any], touch_n: int, variant: str
) -> Tuple[str, str]:
    """Follow-ups reference the earlier note honestly. No 'just bumping this
    to the top of your inbox' theater — say what it is: a second/third note."""
    name = p["name"].split()[0] if p["name"] else "there"
    brief = p.get("research_brief") or {}
    reason = brief.get("reason_for_contact", "")
    if touch_n == 2:
        subject = f"re: quick question, {name}" if name != "there" else "re: quick question"
        body = (
            f"Hi {name},\n\n"
            f"Following up on my note from last week — {reason}\n\n"
            "No worries if the timing's off. One line back ('not now' or "
            "'stop') and I'll close the loop on my end."
            f"{_footer()}"
        )
    else:  # touch 3, the last one
        subject = "closing the loop"
        body = (
            f"Hi {name},\n\n"
            "Last note from me — I don't do endless follow-ups.\n\n"
            f"{OFFER_SHORT}\n\n"
            "If it's ever relevant, you know where to find me."
            f"{_footer()}"
        )
    return subject, body


def compose(p: Dict[str, Any], variant: str, touch_n: int = 1) -> Tuple[str, str]:
    """Compose (subject, body) for a prospect. touch_n=1 is the first email."""
    if variant not in _COMPOSERS:
        raise ValueError(f"unknown variant {variant!r}")
    if touch_n > 1:
        subject, body = compose_followup(p, touch_n, variant)
    else:
        subject, body = _COMPOSERS[variant](p, p.get("research_brief") or {})
    # Backstop: never ship anything that smells like fake personalization.
    suspects = research.check_copy_against_brief(body, p["id"])
    if suspects:
        raise ValueError(f"composer emitted suspect personalization: {suspects}")
    return subject, body
