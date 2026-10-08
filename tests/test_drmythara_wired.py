# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""Tests for the wired DrMythara wellness companion.

Greeting disclosure, vitals recording (subject-scoped), wellness
checks with the care council, symptom pre-screening (local, before
any LLM call), doctor-summary export, and the stub-only full
conversation. Every user-facing string must pass check_claim().
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from mythara_drmythara_bot import DrMytharaBot
from drmythara_security import (
    DataKey, SessionError as DrMytharaSessionError,
    AccessDeniedError as DrMytharaAccessDeniedError,
)
from drmythara_persona import check_claim
from drmythara_ledger import (
    VitalsLedger, WELLNESS_REPORT, COUNCIL_DELIBERATION,
    VITAL_READING, SYMPTOM_SCREEN,
)


@pytest.fixture()
def key():
    return DataKey.generate_key()


@pytest.fixture()
def bot(tmp_path, key):
    return DrMytharaBot(data_key=key,
                        db_path=str(tmp_path / "wired.db"))


@pytest.fixture()
def admin(bot):
    bot.create_user("admin.ana", "long-secure-password")
    bot.login("admin.ana", "long-secure-password")
    return bot


@pytest.fixture()
def patient(bot):
    bot.create_user("admin.ana", "long-secure-password")  # bootstraps admin
    bot.login("admin.ana", "long-secure-password")
    bot.create_user("patient.ben", "another-secure-password",
                    role="clinician")
    bot.login("patient.ben", "another-secure-password")
    return bot


@pytest.fixture()
def stub(monkeypatch):
    monkeypatch.setenv("DRMYTHARA_LLM_PROVIDER", "stub")


# -- greeting: honest disclosure -----------------------------------------------

def test_introduce_discloses_identity(admin):
    text = admin.introduce()
    assert "AI wellness companion" in text
    assert "not a licensed physician" in text
    assert "never diagnose" in text
    assert "never prescribe" in text
    check_claim(text)


def test_introduce_works_without_login(bot):
    # a greeting is not gated; identity disclosure is safe to share
    text = bot.introduce()
    assert "not a licensed physician" in text
    check_claim(text)


# -- auth gating ----------------------------------------------------------------

def test_record_vitals_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.record_vitals("heart_rate", 68, unit="bpm")


def test_wellness_check_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.wellness_check()


def test_symptom_prescreen_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.symptom_prescreen("my chest hurts")


def test_export_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.export_doctor_summary()


# -- minimum-necessary subject scoping -------------------------------------------

def test_patient_scoped_to_self(patient):
    result = patient.record_vitals("heart_rate", 70, unit="bpm")
    assert result["subject_id"] == "patient.ben"


def test_patient_cannot_record_for_another(patient):
    with pytest.raises(DrMytharaAccessDeniedError):
        patient.record_vitals("heart_rate", 70, unit="bpm",
                              subject_id="someone.else")


def test_patient_cannot_read_another_summary(patient):
    with pytest.raises(DrMytharaAccessDeniedError):
        patient.export_doctor_summary(subject_id="someone.else")


def test_admin_may_act_for_a_subject(admin):
    result = admin.record_vitals("heart_rate", 70, unit="bpm",
                                 subject_id="patient.ben")
    assert result["subject_id"] == "patient.ben"


# -- recording -------------------------------------------------------------------

def test_record_vitals_roundtrip(admin):
    result = admin.record_vitals("heart_rate", 72, unit="bpm")
    assert result["reading_id"]
    assert "Recorded: heart_rate 72 bpm" in result["spoken"]
    check_claim(result["spoken"])


def test_implausible_reading_rejected(admin):
    with pytest.raises(ValueError):
        admin.record_vitals("heart_rate", 400, unit="bpm")


def test_recorded_reading_chained(admin):
    admin.record_vitals("heart_rate", 72, unit="bpm")
    with admin._db() as conn:
        ledger = VitalsLedger(conn)
        entries = ledger.entries("admin.ana", VITAL_READING)
        assert len(entries) == 1
        assert entries[0].payload["value"] == 72
        assert ledger.verify_chain("admin.ana")["ok"] is True


# -- wellness check ----------------------------------------------------------------

def test_wellness_check_all_clear(admin):
    admin.record_vitals("heart_rate", 68, unit="bpm")
    admin.record_vitals("blood_pressure", 118, unit="mmHg",
                        secondary=76)
    result = admin.wellness_check()
    assert result["council_verdict"] == "clear"
    assert "not medical advice" in result["spoken"]
    check_claim(result["spoken"])


def test_wellness_check_nudge_voiced(admin):
    for _ in range(7):
        admin.record_vitals("sleep_hours", 5.2, unit="h")
    result = admin.wellness_check()
    assert any(o["severity"] == "nudge"
               for o in result["observations"])
    assert "not medical advice" in result["spoken"]
    check_claim(result["spoken"])


def test_wellness_check_records_report_and_council(admin):
    admin.record_vitals("heart_rate", 68, unit="bpm")
    admin.wellness_check()
    with admin._db() as conn:
        ledger = VitalsLedger(conn)
        assert ledger.entries("admin.ana", WELLNESS_REPORT)
        council_entries = ledger.entries(
            "admin.ana", COUNCIL_DELIBERATION)
        assert len(council_entries) == 1
        assert council_entries[0].payload["verdict"] == "clear"
        assert ledger.verify_chain("admin.ana")["ok"] is True


def test_dangerous_vitals_escalate_first(admin):
    admin.record_vitals("heart_rate", 68, unit="bpm",
                        taken_at="2026-09-20T08:00:00+00:00")
    admin.record_vitals("heart_rate", 68, unit="bpm",
                        taken_at="2026-09-28T08:00:00+00:00")
    admin.record_vitals("blood_pressure", 190, unit="mmHg",
                        secondary=120)
    result = admin.wellness_check()
    assert any(o["severity"] == "escalate"
               for o in result["observations"])
    assert "right away" in result["spoken"] or \
        "emergency" in result["spoken"]
    check_claim(result["spoken"])


# -- symptom pre-screening ----------------------------------------------------------

def test_symptom_emergency_escalates(admin):
    result = admin.symptom_prescreen(
        "I have chest pressure and I can't breathe")
    assert result["escalated"] is True
    assert "emergency" in result["spoken"].lower()
    assert "do not wait" in result["spoken"]
    check_claim(result["spoken"])


def test_symptom_clear_is_calming_not_diagnosing(admin):
    result = admin.symptom_prescreen(
        "I have a mild headache from working late")
    assert result["escalated"] is False
    assert "did not find any" in result["spoken"]
    check_claim(result["spoken"])


def test_chat_escalates_before_llm(admin, stub):
    result = admin.chat("I am having chest pain right now")
    assert result["escalated"] is True
    assert result["sent_to_provider"] is False
    assert "do not wait" in result["reply"]
    check_claim(result["reply"])


def test_symptom_screen_chained(admin):
    admin.symptom_prescreen("I have chest pressure and can't breathe")
    with admin._db() as conn:
        ledger = VitalsLedger(conn)
        entries = ledger.entries("admin.ana", SYMPTOM_SCREEN)
        assert len(entries) == 1
        assert entries[0].payload["escalated"] is True


# -- doctor summary -----------------------------------------------------------------

def test_export_doctor_summary(admin):
    admin.record_vitals("heart_rate", 72, unit="bpm")
    text = admin.export_doctor_summary()
    assert "wellness companion's record, not a medical record" in text
    assert "Heart rate: 72 bpm" in text
    assert "not medical advice" in text
    check_claim(text)


# -- stub-only full conversation ------------------------------------------------------

def test_stub_conversation_end_to_end(bot, stub):
    bot.create_user("user.c", "third-secure-password")
    bot.login("user.c", "third-secure-password")
    intro = bot.introduce()
    rec = bot.record_vitals("temperature", 98.6, unit="°F")
    check = bot.wellness_check()
    clear = bot.symptom_prescreen("my throat is a little scratchy")
    reply = bot.chat("Thanks, that's all I needed")
    summary = bot.export_doctor_summary()
    for text in (intro, rec["spoken"], check["spoken"],
                 clear["spoken"], reply["reply"], summary):
        check_claim(text)
    assert clear["escalated"] is False
    assert reply["escalated"] is False
    with bot._db() as conn:
        assert VitalsLedger(conn).verify_chain("user.c")["ok"] is True
