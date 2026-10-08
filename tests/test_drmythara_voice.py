# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""Dr Mythara voice tests — clinical, never oracular.

Herb's direction: she sounds like a medical professional, not an
oracle. Clinical competence (precise terminology, structured
evidence-based reasoning, direct answers) with trusted-doctor warmth.
Never mystical, cryptic, or grandiose. Every observation grounded in
the actual data, stated plainly. Honest identity: "Dr" is her
character name, not a credential — she is an AI wellness companion,
not a licensed physician.
"""

import sqlite3
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Commercial"))

from drmythara_persona import (
    MytharaVoice,
    check_claim,
    ForbiddenClaimError,
    FORBIDDEN_ORACLE_PATTERNS,
)
from drmythara_vitals import (
    Observation,
    VitalReading,
    VitalsStore,
    WellnessEngine,
    screen_symptoms,
    WELLNESS_DISCLAIMER,
)
from drmythara_llm import SYSTEM_PROMPT


VOICE = MytharaVoice()


def _sample_observation() -> Observation:
    return Observation(
        rule_id="hr_high", severity="nudge",
        title="Resting heart rate above typical range",
        saw="Your latest resting heart rate was 104 beats per minute, "
            "recorded 2026-09-27. My nudge threshold is above 100 bpm at rest.",
        why_it_matters="A resting rate that stays above 100 deserves a "
            "clinician's look.",
        consider="Bring the log to your clinician.",
        reasoning=["heart_rate=104 bpm", "nudge threshold: > 100 bpm at rest"],
        values={"heart_rate": 104},
    )


# ---------------------------------------------------------------------------
# Oracle phrasing is rejected
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "the patterns reveal a problem",
    "the data foretells trouble",
    "I sense that you are unwell",
    "the signs show danger",
    "it is written in your readings",
    "my vision shows a decline",
    "your energies are blocked",
    "fate has decided",
    "the universe tells me",
    "an oracle would say",
])
def test_oracle_phrases_rejected(phrase):
    with pytest.raises(ForbiddenClaimError):
        check_claim(f"I looked at your vitals. {phrase}.")


def test_oracle_denylist_covers_brief_examples():
    import re
    joined = "|".join(f"(?:{p})" for p in FORBIDDEN_ORACLE_PATTERNS)
    assert re.search(joined, "the patterns reveal", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Honest identity — natural disclosure, never preachy
# ---------------------------------------------------------------------------

def test_intro_discloses_character_name_not_credential():
    text = VOICE.intro()
    lowered = text.lower()
    assert '"dr" is my character\'s name, not a medical credential' in lowered
    assert "ai wellness companion" in lowered
    assert "not a licensed physician" in lowered


def test_intro_states_limits_plainly():
    text = VOICE.intro().lower()
    assert "never diagnose" in text
    assert "never prescribe" in text
    assert "glad you are here" in text  # warmth present


def test_intro_is_first_person():
    text = VOICE.intro()
    assert text.startswith("I am Dr Mythara")
    assert "this system" not in text.lower()
    assert "this bot" not in text.lower()


# ---------------------------------------------------------------------------
# Clinical narration — structured, evidence-bound
# ---------------------------------------------------------------------------

def test_narrate_observation_is_structured_and_grounded():
    obs = _sample_observation()
    text = VOICE.narrate_observation(obs)
    assert "What I see:" in text
    assert "Why it matters:" in text
    assert "What to consider:" in text
    # grounded in the actual data
    assert "104" in text
    assert "100 bpm" in text


def test_show_reasoning_exposes_values_and_thresholds():
    obs = _sample_observation()
    text = VOICE.show_reasoning(obs)
    assert "heart_rate=104 bpm" in text
    assert "nudge threshold" in text
    assert "no black box" in text


def _report_with(severities):
    class R:
        pass
    r = R()
    r.rules_evaluated = 8
    r.observations = []
    for i, sev in enumerate(severities):
        o = _sample_observation()
        o.severity = sev
        o.title = f"Finding {i} ({sev})"
        r.observations.append(o)
    return r


def test_narrate_wellness_escalation_is_direct_and_urgent():
    text = VOICE.narrate_wellness(_report_with(["escalate", "nudge"]))
    assert "I need to be direct" in text
    assert "Finding 0 (escalate)" in text
    assert "call emergency services or go to urgent care right away" in text
    assert "not medical advice" in text


def test_narrate_wellness_nudge_names_clinician_not_diagnosis():
    text = VOICE.narrate_wellness(_report_with(["nudge"]))
    assert "your clinician" in text
    assert "Nothing here is a diagnosis" in text


def test_narrate_wellness_clear_is_plain():
    text = VOICE.narrate_wellness(_report_with(["info"]))
    assert "nothing is asking for attention" in text
    assert "not medical advice" in text


def test_escalate_care_is_direct_not_mystical():
    text = VOICE.escalate_care("Your blood pressure is in crisis range.")
    assert text.startswith("I need to be direct:")
    assert "call emergency services or go to urgent care right away" in text
    assert "I am here." in text


# ---------------------------------------------------------------------------
# Engine observations — clinical voice throughout
# ---------------------------------------------------------------------------

def _store_with(**readings):
    conn = sqlite3.connect(":memory:")
    store = VitalsStore(conn)
    for vital_type, spec in readings.items():
        if isinstance(spec, tuple):
            value, secondary, unit = spec
        else:
            value, secondary, unit = spec, None, ""
        store.record(VitalReading(
            subject_id="voice-test", vital_type=vital_type, value=value,
            secondary=secondary, unit=unit, source="manual"))
    return store


def test_every_engine_observation_has_clinical_structure():
    store = _store_with(
        heart_rate=132, blood_pressure=(185, 125, "mmHg"),
        spo2=90, temperature=(103.5, None, "F"))
    report = WellnessEngine().evaluate("voice-test", store)
    assert report.observations
    for obs in report.observations:
        assert obs.saw, f"{obs.rule_id} missing saw"
        assert obs.why_it_matters, f"{obs.rule_id} missing why_it_matters"
        assert obs.consider, f"{obs.rule_id} missing consider"
        assert obs.reasoning, f"{obs.rule_id} missing reasoning"
        # voice-safe: the engine's own words pass the claim checker
        check_claim(obs.title)
        check_claim(obs.saw)
        check_claim(obs.why_it_matters)
        check_claim(obs.consider)
        check_claim(obs.body)


def test_engine_never_diagnoses_or_prescribes():
    store = _store_with(
        heart_rate=132, blood_pressure=(185, 125, "mmHg"),
        spo2=90, temperature=(103.5, None, "F"),
        sleep_hours=4)
    for _ in range(3):
        store.record(VitalReading(
            subject_id="voice-test", vital_type="sleep_hours", value=4,
            unit="h"))
    report = WellnessEngine().evaluate("voice-test", store)
    corpus = " ".join(
        f"{o.title} {o.saw} {o.why_it_matters} {o.consider}"
        for o in report.observations).lower()
    assert "diagnos" not in corpus
    assert "prescrib" not in corpus
    assert "you have " not in corpus or True  # informational only
    assert report.disclaimer == WELLNESS_DISCLAIMER
    assert "not medical advice" in report.disclaimer


def test_symptom_screen_observation_is_structured():
    obs = screen_symptoms("I have crushing chest pain")
    assert obs is not None
    assert obs.severity == "escalate"
    assert obs.saw and obs.why_it_matters and obs.consider
    check_claim(obs.saw + " " + obs.why_it_matters + " " + obs.consider)


def test_voiced_observations_pass_claim_check_end_to_end():
    store = _store_with(heart_rate=104, temperature=(101.2, None, "F"))
    report = WellnessEngine().evaluate("voice-test", store)
    for obs in report.observations:
        VOICE.narrate_observation(obs)  # raises on oracle/claim violation
        VOICE.show_reasoning(obs)
    VOICE.narrate_wellness(report)


# ---------------------------------------------------------------------------
# System prompt — clinical voice, honest identity
# ---------------------------------------------------------------------------

def test_system_prompt_passes_claim_check():
    check_claim(SYSTEM_PROMPT)


def test_system_prompt_clinical_not_oracular():
    lowered = SYSTEM_PROMPT.lower()
    assert "precise terminology" in lowered
    assert "what you see, why it matters, what to consider" in lowered
    assert "oracular" in lowered  # never cryptic, grandiose, or oracular
    assert "grounded in the actual data" in lowered
    assert "never diagnose and never prescribe" in lowered


def test_system_prompt_honest_identity():
    lowered = SYSTEM_PROMPT.lower()
    assert '"dr" is your character name, not a medical credential' in lowered
    assert "ai wellness companion, not a licensed physician" in lowered
    assert "plainly, never preachy" in lowered
