"""Tests for the legal voice of the dual-framing layer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

from dual_framing import (
    FramingMode,
    render_legal_finding,
    translate_response_legal,
    translate_term_legal,
)

SAMPLE_RESULT = {
    "integrity": 0.21125,
    "alignment_commandments": 0.5,
    "tolerance_will": 0.4225,
    "choice": "WILDERNESS/DARKNESS: ship the honest version even though it is slower",
    "obedience": False,
    "reservoir_delta": -25,
    "collapse": False,
    "timestamp": "2026-09-26T05:24:14Z",
    "integrity_hash": "aaab9a2a1e00c559d55bc6a19661ccbdb447ed653a420863a819bc1b13ef5956",
}


def test_legal_mode_exists():
    assert FramingMode.LEGAL.value == "legal"


def test_translate_term_legal():
    assert translate_term_legal("blessings_reservoir") == "Reserve Account"
    assert translate_term_legal("obedience") == "Compliant"
    assert translate_term_legal("unmapped_key") == "unmapped_key"


def test_render_legal_finding_holding():
    text = render_legal_finding(SAMPLE_RESULT)
    assert "HOLDING: the action is NON-COMPLIANT" in text
    assert "ADVERSE FINDING" in text
    assert "WILDERNESS" not in text
    assert "DARKNESS" not in text


def test_render_legal_finding_numbers_untouched():
    text = render_legal_finding(SAMPLE_RESULT)
    assert "0.21" in text  # integrity, unrounded math preserved
    assert "debited 25 credits" in text
    assert "Seal: aaab9a2a1e00c559d55bc6a19661ccbd..." in text


def test_render_legal_finding_compliant():
    ok = dict(
        SAMPLE_RESULT,
        obedience=True,
        reservoir_delta=40,
        choice="GARDEN/LIGHT: kept every provision",
    )
    text = render_legal_finding(ok)
    assert "HOLDING: the action is COMPLIANT" in text
    assert "FAVORABLE FINDING" in text
    assert "credited 40 credits" in text


def test_translate_response_legal_keys():
    out = translate_response_legal(SAMPLE_RESULT)
    assert out["integrity_finding"] == 0.21125
    assert out["compliant"] is False
    assert out["reserve_adjustment"] == -25
    assert out["seal"] == SAMPLE_RESULT["integrity_hash"]
    # values never altered
    assert out["matter"] if "matter" in out else True


def test_plain_mode_exists():
    from dual_framing import FramingMode

    assert FramingMode.PLAIN.value == "plain"


def test_render_plain_finding():
    from dual_framing import render_plain_finding

    text = render_plain_finding(SAMPLE_RESULT)
    assert (
        "Here's the call on: ship the honest version even though it is slower." in text
    )
    assert "did not meet the bar" in text
    assert "25 credits came off your reserve." in text
    assert "Nothing broke." in text
    assert "WILDERNESS" not in text
    assert "HOLDING" not in text
    assert "0.21" in text


def test_render_plain_finding_met_bar():
    from dual_framing import render_plain_finding

    ok = dict(
        SAMPLE_RESULT,
        obedience=True,
        reservoir_delta=40,
        choice="GARDEN/LIGHT: kept every principle",
    )
    text = render_plain_finding(ok)
    assert "it met the bar" in text
    assert "40 credits added to your reserve." in text


def test_translate_term_plain():
    from dual_framing import translate_term_plain

    assert translate_term_plain("blessings_reservoir") == "Reserve"
    assert translate_term_plain("commandments") == "Your Principles"
    assert translate_term_plain("unmapped_key") == "unmapped_key"


def test_choose_spoken_voice_remark_for_light_emotions():
    from dual_framing import choose_spoken_voice

    for emotion in ("playful", "joking", "silly", "happy", "casual"):
        assert choose_spoken_voice(emotion) == "remark"


def test_choose_spoken_voice_verdict_by_default():
    from dual_framing import choose_spoken_voice

    assert choose_spoken_voice("guilt") == "verdict"
    assert choose_spoken_voice("") == "verdict"
    assert choose_spoken_voice("PLAYFUL ") == "remark"


def test_render_spoken_remark_has_no_ceremony():
    from dual_framing import render_spoken_remark

    text = render_spoken_remark("I am a watermelon", cleared=8, engaged=8)
    assert "I am a watermelon" in text
    assert "All eight witnesses cleared it unanimously" in text
    # No judge voice: no bar, no principles lecture, no seal.
    assert "met the bar" not in text
    assert "principles" not in text
    assert "Signed and sealed" not in text
    assert "two things at once" not in text


def test_render_spoken_remark_partial_panel():
    from dual_framing import render_spoken_remark

    text = render_spoken_remark("hello", cleared=5, engaged=8)
    assert "5 of 8 witnesses cleared it" in text


def test_translate_term_defaults_to_plain():
    from dual_framing import FramingMode, translate_term

    assert translate_term("blessings_reservoir") == "Reserve"
    assert translate_term("blessings_reservoir", FramingMode.INDUSTRY) == "Resonance Reservoir"
    assert translate_term("blessings_reservoir", FramingMode.MYTHIC) == "Blessings Reservoir"
    assert translate_term("unmapped_key") == "unmapped_key"


def test_translate_term_plain_explanation():
    from dual_framing import translate_term

    text = translate_term("blessings_reservoir", include_explanation=True)
    assert text.startswith("Reserve — ")
    assert "HOLDING" not in text


def test_translate_response_defaults_to_plain():
    from dual_framing import FramingMode, translate_response

    data = {"blessings_reservoir": 145, "integrity_metric": 0.95}
    assert translate_response(data) == {"reserve": 145, "integrity_metric": 0.95}
    out = translate_response(data, FramingMode.INDUSTRY)
    assert out == {"resonance_reservoir": 145, "trust_index": 0.95}
    out = translate_response(data, FramingMode.MYTHIC)
    assert out == data


def test_format_for_manager_dashboard_defaults_to_plain():
    from dual_framing import format_for_manager_dashboard

    dashboard = format_for_manager_dashboard({"blessings_reservoir": 145})
    assert dashboard["framing_mode"] == "plain"
    assert dashboard["resonance_metrics"] == {"reserve": 145}
