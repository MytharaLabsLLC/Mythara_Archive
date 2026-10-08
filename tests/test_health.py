"""Tests for DrMythara's health-reasoning core (soul_cradle/health.py).

She is the health-reasoning organ: deterministic consults, versioned
rules, a fail-closed membrane hook, and a humility mechanism
(outside_scope). If any of these fail, she must not gate health actions.
"""

import importlib.util
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soul_cradle import health
from soul_cradle.health import (
    CLEAR,
    FLAGGED,
    OUTSIDE_SCOPE,
    RULE_TABLES,
    consult_health,
    health_bounds_check,
    health_witness_declaration,
    screen_health,
    verify_judgment,
)
from soul_cradle.pantheon import (
    PANTHEON,
    core_function,
    health_authority,
    organs,
    user_facing,
)
from soul_cradle.standing import StandingAuthority, WITNESS


def _full_evidence(*table_names):
    """Evidence satisfying every rule in the named tables."""
    ev = {}
    for name in table_names:
        for rule in RULE_TABLES[name].rules:
            ev[rule.check] = True
    return ev


HIPAA_TABLES = ["hipaa_technical", "hipaa_administrative", "hipaa_physical"]

# ---------------------------------------------------------------------------
# consult: clear / flagged / outside_scope
# ---------------------------------------------------------------------------


def test_consult_clear_when_all_rules_satisfied():
    j = consult_health("hipaa", _full_evidence(*HIPAA_TABLES))
    assert j.verdict == CLEAR
    assert j.findings == []
    assert verify_judgment(j)


def test_consult_flagged_when_control_missing():
    ev = _full_evidence(*HIPAA_TABLES)
    ev["encryption"] = False  # critical control absent
    j = consult_health("hipaa", ev)
    assert j.verdict == FLAGGED
    assert any(f["rule_id"] == "hipaa.tech.access.encryption" for f in j.findings)
    assert verify_judgment(j)


def test_consult_outside_scope_declares_limit():
    j = consult_health("astrology compatibility", {"stars_aligned": True})
    assert j.verdict == OUTSIDE_SCOPE
    assert j.findings == []
    # humility: she declines instead of scoring anyway
    assert "outside_scope" in j.note.lower() or "declines" in j.note.lower()
    assert verify_judgment(j)


def test_consult_deterministic():
    ev = _full_evidence("fda_records", "fda_signatures")
    a = consult_health("fda 21 cfr 11", ev)
    b = consult_health("fda 21 cfr 11", ev)
    assert a.verdict == b.verdict == CLEAR
    assert [f["rule_id"] for f in a.findings] == [f["rule_id"] for f in b.findings]


# ---------------------------------------------------------------------------
# rule versioning
# ---------------------------------------------------------------------------


def test_every_table_versioned_with_source():
    for name, table in RULE_TABLES.items():
        assert re.fullmatch(r"\d{4}\.\d+", table.version), name
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", table.effective_date), name
        assert table.source and len(table.source) > 10, name
        assert len(table.rules) > 0, name


def test_judgment_records_rule_versions():
    j = consult_health("hipaa", _full_evidence(*HIPAA_TABLES))
    assert j.rule_versions == {
        name: RULE_TABLES[name].version for name in HIPAA_TABLES
    }


def test_ai_governance_source_is_honest():
    src = RULE_TABLES["ai_governance"].source.lower()
    assert "internal" in src  # labeled as Herb's own checklist, not a regulation


# ---------------------------------------------------------------------------
# membrane hook: screen_health
# ---------------------------------------------------------------------------


def test_screen_blocks_flagged_health_action():
    j = screen_health("export patient PHI to external vendor")
    assert j.verdict == FLAGGED  # health-touching + no evidence = fail-closed
    assert verify_judgment(j)


def test_screen_passes_clear_health_action():
    ev = _full_evidence(*HIPAA_TABLES)
    j = screen_health("export patient PHI to external vendor", ev)
    assert j.verdict == CLEAR


def test_screen_ignores_non_health_action():
    j = screen_health("restart the web server")
    assert j.verdict == CLEAR
    assert j.findings == []
    assert "no health surface" in j.note.lower()


# ---------------------------------------------------------------------------
# Soul Cradle adapter: bounds check with the exact contract signature
# ---------------------------------------------------------------------------


def test_bounds_check_refuses_flagged_action():
    reason = health_bounds_check(
        "send patient records to vendor", "emit_text", {"to": "vendor@example.com"}
    )
    assert isinstance(reason, str) and len(reason) > 0
    assert "health" in reason.lower()


def test_bounds_check_allows_clear_action():
    reason = health_bounds_check(
        "send patient records to vendor",
        "emit_text",
        {
            "to": "vendor@example.com",
            "health_evidence": _full_evidence(*HIPAA_TABLES),
        },
    )
    assert reason is None


def test_bounds_check_allows_non_health_action():
    assert health_bounds_check("restart server", "emit_text", {}) is None


# ---------------------------------------------------------------------------
# standing-matrix adapter: she testifies only as witness
# ---------------------------------------------------------------------------


def test_health_judgment_becomes_witness_statement():
    authority = StandingAuthority(key=b"test-health-key-0000000000000000")
    j = consult_health("hipaa", _full_evidence(*HIPAA_TABLES))
    decl = health_witness_declaration(authority, "event-123", j)
    assert decl.role == WITNESS
    assert decl.actor == "drmythara"
    ok, reason = authority.verify(decl)
    assert ok, reason
    assert decl.scope["observed"] is True
    assert decl.scope["verdict"] == CLEAR


# ---------------------------------------------------------------------------
# pantheon registry
# ---------------------------------------------------------------------------


def test_drmythara_registered_as_health_authority():
    assert health_authority() == "drmythara"
    entry = PANTHEON["drmythara"]
    assert entry["organ"] is True
    assert entry["faces_user"] is True
    assert "not a medical professional" in entry["core_function"].lower()
    assert "drmythara" in organs()
    assert "drmythara" in user_facing()


def test_every_pantheon_entry_has_core_function():
    for bot_id, entry in PANTHEON.items():
        assert entry["core_function"], bot_id
    assert "health" in core_function("drmythara").lower()
    assert core_function("no_such_bot").startswith("unknown bot")


# ---------------------------------------------------------------------------
# thin wrapper still works
# ---------------------------------------------------------------------------


def _load_wrapper():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Commercial",
        "mythara_drmythara_bot.py",
    )
    spec = importlib.util.spec_from_file_location("drmythara_wrapper", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_wrapper_instantiates_and_consults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # sqlite db lands in tmp, not the repo
    mod = _load_wrapper()
    # dev_mode: tests never touch real data; the checklist API now
    # requires sign-in (Phase 1 auth boundary).
    bot = mod.DrMytharaBot(dev_mode=True)
    assert bot.bot_id == "drmythara_bot"

    j = bot.consult("hipaa", _full_evidence(*HIPAA_TABLES))
    assert j.verdict == CLEAR
    assert mod.verify_judgment(j)

    # wrapper rules are projections of the canonical core
    assert set(bot.hipaa_rules["technical_safeguards"]["access_control"]) == {
        r.check for r in RULE_TABLES["hipaa_technical"].rules
        if r.category == "access_control"
    }

    # gated checklist flow: sign in first
    bot.create_user("tester", "test-password-1234")
    bot.login("tester", "test-password-1234")
    result = bot.audit_hipaa_compliance("Test Clinic", scope="technical")
    assert result["organization"] == "Test Clinic"
    assert "overall_score" in result

    report = bot.generate_compliance_report()
    assert "NOT A MEDICAL PROFESSIONAL" in report


def test_wrapper_screen_passthrough(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = _load_wrapper()
    bot = mod.DrMytharaBot(dev_mode=True)
    j = bot.screen("email patient lab results", _full_evidence(*HIPAA_TABLES))
    assert j.verdict == CLEAR
    j2 = bot.screen("email patient lab results")
    assert j2.verdict == FLAGGED
