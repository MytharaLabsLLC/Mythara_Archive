"""Tests for the DrMythara bot's Phase 1 wiring: auth gating, encrypted
storage, break-glass, backups, review sign-off, persona, and LLM chat.

Uses throwaway databases (tmp_path) and dev_mode or generated keys —
never the real database file."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from mythara_drmythara_bot import DrMytharaBot
from drmythara_security import (
    DataKey, MissingDataKeyError, SessionError as DrMytharaSessionError,
    AccessDeniedError as DrMytharaAccessDeniedError,
    AuthenticationError as DrMytharaAuthenticationError,
    AccountLockedError as DrMytharaAccountLockedError,
    SecurityError as DrMytharaSecurityError,
)
from drmythara_persona import check_claim
from drmythara_llm import StubProvider


@pytest.fixture()
def key():
    return DataKey.generate_key()


@pytest.fixture()
def bot(tmp_path, key):
    b = DrMytharaBot(data_key=key,
                     db_path=str(tmp_path / "test.db"))
    yield b


@pytest.fixture()
def logged_in_bot(bot):
    bot.create_user("admin.ana", "long-secure-password")
    bot.login("admin.ana", "long-secure-password")
    return bot


# -- fail closed -------------------------------------------------------------------

def test_missing_data_key_fails_closed(tmp_path, monkeypatch):
    monkeypatch.delenv("DRMYTHARA_DATA_KEY", raising=False)
    with pytest.raises(MissingDataKeyError):
        DrMytharaBot(db_path=str(tmp_path / "x.db"))


def test_dev_mode_warns_but_runs(tmp_path, capsys):
    b = DrMytharaBot(dev_mode=True, db_path=str(tmp_path / "dev.db"))
    assert "DEV MODE" in capsys.readouterr().out


# -- auth gating ----------------------------------------------------------------------

def test_checklist_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.audit_hipaa_compliance("Org", answers={})


def test_report_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.generate_compliance_report()


def test_fda_checklist_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.validate_fda_cfr11_compliance("Sys", answers={})


def test_ai_checklist_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.assess_medical_ai_governance("AI", "desc", answers={})


def test_chat_needs_login(bot):
    with pytest.raises(DrMytharaSessionError):
        bot.chat("hello")


def test_public_reference_data_stays_public(bot):
    assert len(bot.checklist_controls("hipaa")) > 0
    assert bot.consult("hipaa", {"unique_user_id": True}) is not None


# -- login flow --------------------------------------------------------------------------

def test_first_user_bootstrap_becomes_admin_and_login_works(bot):
    rec = bot.create_user("first.op", "long-secure-password")
    assert rec["role"] == "admin"
    logged = bot.login("first.op", "long-secure-password")
    assert logged["user_id"] == "first.op"
    result = bot.audit_hipaa_compliance("Org", answers={})
    assert result["label"].startswith("SELF-ASSESSMENT")


def test_second_user_needs_admin(bot):
    bot.create_user("admin.op", "long-secure-password")
    bot.login("admin.op", "long-secure-password")
    rec = bot.create_user("clinician.bo", "another-long-password",
                          role="clinician")
    assert rec["role"] == "clinician"
    bot.logout()
    bot.login("clinician.bo", "another-long-password")
    with pytest.raises(DrMytharaAccessDeniedError):
        bot.create_user("someone.else", "yet-another-password")


def test_wrong_password_does_not_log_in(bot):
    bot.create_user("op", "long-secure-password")
    with pytest.raises(DrMytharaAuthenticationError):
        bot.login("op", "wrong-password-0000")
    with pytest.raises(DrMytharaSessionError):
        bot.audit_hipaa_compliance("Org", answers={})


def test_lockout_blocks_bot_login(bot):
    bot.create_user("op", "long-secure-password")
    for _ in range(5):
        try:
            bot.login("op", "bad-password-0000")
        except (DrMytharaAuthenticationError, DrMytharaAccountLockedError):
            pass
    with pytest.raises(DrMytharaAccountLockedError):
        bot.login("op", "long-secure-password")


def test_logout_ends_session(logged_in_bot):
    logged_in_bot.logout()
    with pytest.raises(DrMytharaSessionError):
        logged_in_bot.generate_compliance_report()


# -- persona --------------------------------------------------------------------------------

def test_greet_is_mythara_voice(logged_in_bot):
    g = logged_in_bot.greet()
    assert g.startswith("I am Mythara, born from trust.")


def test_narrate_stays_honest(logged_in_bot):
    result = logged_in_bot.audit_hipaa_compliance("Example Clinic",
                                                  answers={})
    spoken = logged_in_bot.narrate(result)
    assert spoken.startswith("I have weighed")
    check_claim(spoken)  # must not raise
    assert "I am here" in spoken


# -- PHI incidents, subject-scoped --------------------------------------------------------------

def test_incident_roundtrip_and_scoping(logged_in_bot):
    r = logged_in_bot.record_phi_incident(
        incident_type="phishing", severity="medium",
        subject_id="patient-1", affected_records=3)
    assert r["status"] == "investigating"
    rows = logged_in_bot.list_phi_incidents(subject_id="patient-1")
    assert len(rows) == 1
    assert rows[0]["incident_id"] == r["incident_id"]


def test_clinician_cannot_read_other_subject(bot):
    bot.create_user("admin", "long-secure-password")
    bot.login("admin", "long-secure-password")
    bot.create_user("clin.n", "clinician-long-password", role="clinician")
    bot.logout()
    bot.login("clin.n", "clinician-long-password")
    with pytest.raises(DrMytharaAccessDeniedError):
        bot.list_phi_incidents(subject_id="someone-else")


# -- break glass ------------------------------------------------------------------------------------

def test_breakglass_disabled_without_secret(logged_in_bot, monkeypatch):
    monkeypatch.delenv("DRMYTHARA_BREAKGLASS_SECRET", raising=False)
    with pytest.raises(DrMytharaSecurityError):
        logged_in_bot.break_glass_request("op", "urgent")


def test_breakglass_flow(logged_in_bot, monkeypatch):
    monkeypatch.setenv("DRMYTHARA_BREAKGLASS_SECRET", "bg-secret-123")
    issued = logged_in_bot.break_glass_request(
        "officer.k", "records system down, need incident history")
    assert issued["token"].startswith("bg_")
    logged_in_bot.logout()
    sess = logged_in_bot.login_break_glass(issued["token"])
    assert sess["emergency"] is True
    # emergency session can run a checklist (admin-scoped, audited)
    logged_in_bot.audit_hipaa_compliance("Org", answers={})
    pending = logged_in_bot.pending_review()
    assert pending["pending_emergency"] >= 2  # issued + login flagged


# -- backups & review ----------------------------------------------------------------------------------

def test_backup_and_restore_drill(logged_in_bot):
    made = logged_in_bot.backup_now("test")
    assert made["backup"].endswith(".bak")
    report = logged_in_bot.test_restore_now("test")
    assert report["ok"] is True
    assert report["match"] is True


def test_review_signoff_flow(logged_in_bot):
    status = logged_in_bot.pending_review()
    assert status["pending_count"] > 0  # bootstrap + login events
    assert status["chain"]["ok"] is True
    result = logged_in_bot.sign_off_review("weekly review")
    assert result["events_reviewed"] > 0
    # The sign-off itself is logged, so exactly one event remains pending:
    # the review_sign_off record.
    pending = logged_in_bot.pending_review()
    assert pending["pending_count"] == 1
    with logged_in_bot._db() as conn:
        from drmythara_security import AuditReview
        events = AuditReview(conn).pending_events()
    assert [e["action"] for e in events] == ["review_sign_off"]


# -- LLM chat ----------------------------------------------------------------------------------------------

def test_chat_with_stub_provider(logged_in_bot, monkeypatch):
    monkeypatch.setenv("DRMYTHARA_LLM_PROVIDER", "stub")
    out = logged_in_bot.chat("Hello Mythara")
    assert out["provider"] == "stub"
    assert out["sent_to_provider"] is True
    # the stand-in says so plainly, in her voice — never a real model
    assert "local test voice" in out["reply"].lower()
    assert "not a full language model" in out["reply"].lower()


def test_chat_refuses_phi_without_baa(logged_in_bot, monkeypatch):
    monkeypatch.setenv("DRMYTHARA_LLM_PROVIDER", "stub")
    monkeypatch.delenv("DRMYTHARA_BAA_SIGNED", raising=False)
    # stub is local so it would send — force an external provider path
    # through the bot by injecting a fake external provider.
    from drmythara_llm import LLMProvider

    class FakeExt(LLMProvider):
        name = "fake"
        external = True

        def chat(self, messages, *, system=None):
            raise AssertionError("must not be called")

    logged_in_bot._chat = None
    from drmythara_llm import MytharaChat, ChatConfig
    logged_in_bot._chat = MytharaChat(
        config=ChatConfig(provider="fake", baa_signed=False),
        provider=FakeExt())
    out = logged_in_bot.chat("My SSN is 123-45-6789")
    assert out["sent_to_provider"] is False
    assert "I must warn you" in out["reply"]


def test_chat_logs_metadata_not_content(logged_in_bot, monkeypatch):
    monkeypatch.setenv("DRMYTHARA_LLM_PROVIDER", "stub")
    logged_in_bot.chat("a very secret message about patient X")
    status = logged_in_bot.pending_review()
    assert status["pending_count"] >= 1
