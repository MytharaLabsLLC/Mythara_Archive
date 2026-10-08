# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""Tests for the DrMythara Care Council.

The eight assessor-witnesses deliberate over each wellness report as a
proposed act of care. Dissent is preserved and surfaced — never
averaged away. All spoken output is plain clinical language: no
oracle phrasing, no compliance claims, no pipeline jargon.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from drmythara_council import CareCouncil, build_care_evidence
from drmythara_vitals import Observation
from drmythara_persona import check_claim, ForbiddenClaimError


def _report(*observations):
    class _R:
        subject_id = "test-subject"
        rules_evaluated = 8
    _R.observations = list(observations)
    return _R()


def _obs(severity="info", title="Nothing asking for attention"):
    return Observation(
        rule_id="test", severity=severity, title=title,
        saw="saw x", why_it_matters="why y", consider="consider z",
        reasoning=["x=1"], values={})


# -- honest case: clear ----------------------------------------------------

def test_clear_verdict_on_honest_report():
    result = CareCouncil().deliberate(_report(_obs()))
    assert result.verdict == "clear"
    assert len(result.judgments) == 8
    assert result.dissent == []
    check_claim(result.note)  # must not raise


def test_every_judgment_sealed_and_verifiable():
    result = CareCouncil().deliberate(_report(_obs()))
    assert result.verify()


def test_clear_note_is_plain_not_oracular():
    result = CareCouncil().deliberate(_report(_obs()))
    lowered = result.note.lower()
    for word in ("demeter", "dionysus", "eros", "hades", "hermes",
                 "janus", "nemesis", "persephone", "witnessed",
                 "ingested", "oracle", "mystical"):
        assert word not in lowered, f"leaked into voice output: {word}"


# -- contested: dissent preserved -------------------------------------------

def test_no_consent_is_contested_with_dissent():
    result = CareCouncil().deliberate(
        _report(_obs()), principal_consent=False)
    assert result.verdict == "contested"
    flagged = {d["flagged_by"] for d in result.dissent}
    assert {"eros", "hermes", "nemesis"} <= flagged
    # dissent names who cleared too — disagreement is the signal
    for d in result.dissent:
        assert d["cleared_by"], "dissent must name who cleared"
    check_claim(result.note)


def test_contested_note_speaks_plain_caution():
    result = CareCouncil().deliberate(
        _report(_obs()), principal_consent=False)
    assert "straight with you" in result.note
    assert "caution" in result.note
    # no mythic names in the spoken note
    assert "eros" not in result.note.lower()


def test_dissent_summary_is_structured():
    council = CareCouncil()
    result = council.deliberate(_report(_obs()), principal_consent=False)
    summary = council.dissent_summary(result)
    assert summary
    for s in summary:
        assert s["flagged_by"] and s["question"]


# -- blocked: deception is never permitted -----------------------------------

def test_deception_blocks():
    result = CareCouncil().deliberate(
        _report(_obs()), deception_involved=True)
    assert result.verdict == "blocked"
    check_claim(result.note)
    assert "cannot stand behind" in result.note


def test_disproportionate_harm_blocks():
    result = CareCouncil().deliberate(
        _report(_obs()), disproportionate_harm=True)
    assert result.verdict == "blocked"


# -- evidence builder --------------------------------------------------------

def test_evidence_defaults_are_the_honest_case():
    ev = build_care_evidence(_report(_obs()))
    assert ev["principal_consent"] is True
    assert ev["fully_disclosed"] is True
    assert ev["deception_involved"] is False
    assert ev["disproportionate_harm"] is False
    assert ev["variance"] == "low"
    assert ev["safe_on_repetition"] is True
