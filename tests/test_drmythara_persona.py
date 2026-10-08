"""Tests for Commercial/drmythara_persona.py — the "I Am Mythara"
character voice.

Two properties, both load-bearing:
  1. The bot stays in character: first-person Mythara voice.
  2. The bot NEVER makes unverified compliance claims — check_claim
     rejects them, and every voice method self-checks its output."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from drmythara_persona import (
    MytharaVoice,
    check_claim,
    ForbiddenClaimError,
    INTRO_MONOLOGUE,
    DOMAIN_LINES,
    HONEST_PHRASES,
)


# -- the canonical voice sample -------------------------------------------------

CANONICAL = (
    "I am Mythara, born from trust. With HIPAA and every safeguard woven "
    "into my core, I cannot do anything else but protect, honor, and secure. "
    "In mental health, I preserve compassion with compliance. "
    "In cyber security, I guard sovereignty. "
    "In education, I carry wisdom forward. "
    "I am not ordinary technology. I am living architecture. "
    "I am Mythara. I am here."
)


def test_greeting_is_the_canonical_monologue_verbatim():
    voice = MytharaVoice()
    assert voice.greet() == CANONICAL
    assert voice.greet() == INTRO_MONOLOGUE


def test_greeting_is_first_person_mythara():
    g = MytharaVoice().greet()
    assert g.startswith("I am Mythara")
    assert "I am here." in g


def test_domain_lines_match_video_script():
    voice = MytharaVoice()
    assert voice.domain_line("mental health") == \
        "In mental health, I preserve compassion with compliance."
    assert voice.domain_line("cybersecurity") == \
        "In cyber security, I guard sovereignty."
    assert voice.domain_line("education") == \
        "In education, I carry wisdom forward."


# -- in-character output ----------------------------------------------------------

def test_narrate_summary_is_first_person():
    voice = MytharaVoice()
    out = voice.narrate_summary({
        "domain": "Example Clinic", "total_controls": 10,
        "status_counts": {"compliant": 6, "partial": 2,
                          "non_compliant": 1, "unknown": 1}})
    assert out.startswith("I have weighed")
    assert "I will keep a faithful" in out
    assert "I am Mythara" not in out  # summary, not the greeting


def test_narrate_finding_is_first_person():
    voice = MytharaVoice()
    out = voice.narrate_finding({"control": "auto_logoff",
                                 "status": "non_compliant",
                                 "gap": "No timeout set."})
    assert out.startswith("I looked at auto_logoff")
    assert "does not hold" in out


def test_checklist_opening_is_protective_not_judgmental():
    voice = MytharaVoice()
    out = voice.checklist_opening("mental health")
    assert "I will not judge what you tell me" in out
    assert "Answer only what is true" in out


def test_closing():
    out = MytharaVoice().closing()
    assert out == ("I am here — and I am glad you came. Ask me what you need, "
                   "and I will answer plainly.")


def test_voice_carries_warmth():
    voice = MytharaVoice()
    assert "glad you brought this to me" in voice.checklist_opening("mental health")
    assert "Thank you for trusting me" in voice.narrate_summary(
        {"domain": "d", "total_controls": 1,
         "status_counts": {"compliant": 1}})
    assert "glad you came" in voice.closing()


# -- honesty guardrails --------------------------------------------------------------

@pytest.mark.parametrize("bad", [
    "We are HIPAA compliant.",
    "This system meets HIPAA compliance requirements.",
    "Our platform is FDA compliant.",
    "The product is certified.",
    "We hold HIPAA certification.",
    "This solution is fully compliant.",
    "With HIPAA woven into my core, we protect you.",  # outside monologue
    "Our database is unhackable.",
    "The system is 100% secure.",
])
def test_forbidden_claims_rejected(bad):
    with pytest.raises(ForbiddenClaimError):
        check_claim(bad)


@pytest.mark.parametrize("jargon", [
    "The record was witnessed by the panel.",
    "Data was ingested into the pipeline.",
    "Per our honesty contract, we comply.",
    "Projected intent differs from shadow intent.",
])
def test_pipeline_jargon_rejected_in_voice_output(jargon):
    with pytest.raises(ForbiddenClaimError):
        check_claim(jargon)


@pytest.mark.parametrize("honest", HONEST_PHRASES)
def test_honest_phrases_allowed(honest):
    assert check_claim(f"We are {honest}.") == f"We are {honest}."


def test_hipaa_discussed_without_claiming_is_fine():
    ok = ("The HIPAA Security Rule requires access controls. "
          "We are built with compliance in mind.")
    assert check_claim(ok) == ok


def test_monologue_exempt_as_character_identity():
    # The canonical monologue is the character's promo voice, documented
    # as exempt — but the SAME claim anywhere else is rejected.
    assert check_claim(INTRO_MONOLOGUE) == INTRO_MONOLOGUE
    with pytest.raises(ForbiddenClaimError):
        check_claim("I am Mythara, born from trust. We are HIPAA compliant.")


def test_every_voice_method_self_checks():
    voice = MytharaVoice()
    outputs = [
        voice.greet(),
        voice.checklist_opening("mental health"),
        voice.narrate_finding({"control": "c1", "status": "compliant"}),
        voice.narrate_summary({"domain": "d", "total_controls": 1,
                               "status_counts": {"compliant": 1}}),
        voice.narrate("The sky is blue."),
        voice.warn_limit("This may take a while."),
        voice.closing(),
    ]
    for out in outputs:
        check_claim(out)  # must not raise
        for word in ("witnessed", "ingested", "honesty contract"):
            assert word not in out.lower()
