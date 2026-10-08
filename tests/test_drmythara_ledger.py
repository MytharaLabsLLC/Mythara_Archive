# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""Tests for the DrMythara tamper-evident vitals ledger.

Append-only hash chain per subject: vitals readings, wellness reports,
council deliberations, symptom screens. Altering or deleting any entry
breaks the chain. The doctor-summary export is plain language with an
honest disclaimer — the chain proves the record is unaltered, never
that it is medically authoritative.
"""

import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from drmythara_ledger import (
    VitalsLedger, LedgerEntry, export_doctor_summary,
    VITAL_READING, WELLNESS_REPORT, COUNCIL_DELIBERATION,
    SYMPTOM_SCREEN, CHAT_NOTE, GENESIS_HASH,
)
from drmythara_vitals import VitalReading, VitalsStore
from drmythara_persona import check_claim


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


@pytest.fixture()
def ledger(conn):
    VitalsStore(conn)
    return VitalsLedger(conn)


# -- chaining -----------------------------------------------------------------

def test_append_and_verify(ledger):
    e1 = ledger.record("s1", VITAL_READING,
                       {"vital_type": "heart_rate", "value": 68})
    e2 = ledger.record("s1", WELLNESS_REPORT, {"observations": []})
    assert e1.entry_id != e2.entry_id
    assert e1.prev_hash == GENESIS_HASH
    assert e2.prev_hash == e1.entry_hash
    result = ledger.verify_chain("s1")
    assert result["ok"] is True
    assert result["broken_at"] is None
    assert result["entries"] == 2


def test_chains_are_per_subject(ledger):
    ledger.record("s1", VITAL_READING, {"value": 68})
    ledger.record("s2", VITAL_READING, {"value": 72})
    for subject in ("s1", "s2"):
        assert ledger.verify_chain(subject)["ok"] is True


def test_empty_chain_is_valid(ledger):
    result = ledger.verify_chain("nobody")
    assert result["ok"] is True
    assert result["entries"] == 0


def test_tampered_payload_is_detected(ledger, conn):
    ledger.record("s1", VITAL_READING,
                  {"vital_type": "heart_rate", "value": 68})
    conn.execute(
        "UPDATE drmy_ledger SET payload = ? WHERE subject_id = ?",
        ('{"vital_type": "heart_rate", "value": 999}', "s1"))
    result = ledger.verify_chain("s1")
    assert result["ok"] is False
    assert result["broken_at"] is not None
    assert "payload" in result["reason"]


def test_broken_link_is_detected(ledger, conn):
    ledger.record("s1", VITAL_READING, {"value": 68})
    ledger.record("s1", VITAL_READING, {"value": 70})
    conn.execute(
        "UPDATE drmy_ledger SET prev_hash = ? "
        "WHERE subject_id = ? AND entry_id = "
        "(SELECT entry_id FROM drmy_ledger WHERE subject_id = ? "
        " ORDER BY recorded_at DESC LIMIT 1)",
        ("tampered", "s1", "s1"))
    result = ledger.verify_chain("s1")
    assert result["ok"] is False
    assert "prev_hash" in result["reason"]


def test_entries_ordered_oldest_first(ledger):
    for i in range(3):
        ledger.record("s1", VITAL_READING, {"seq": i})
    entries = ledger.entries("s1", VITAL_READING)
    assert [e.payload["seq"] for e in entries] == [0, 1, 2]


def test_deleted_entry_breaks_chain(ledger, conn):
    # append-only: deleting the first entry is detectable
    ledger.record("s1", VITAL_READING, {"value": 68})
    ledger.record("s1", VITAL_READING, {"value": 70})
    conn.execute(
        "DELETE FROM drmy_ledger WHERE subject_id = ? AND entry_id = "
        "(SELECT entry_id FROM drmy_ledger WHERE subject_id = ? "
        " ORDER BY recorded_at ASC LIMIT 1)",
        ("s1", "s1"))
    assert ledger.verify_chain("s1")["ok"] is False


def test_entry_is_sealed_dataclass(ledger):
    e = ledger.record("s1", SYMPTOM_SCREEN,
                      {"matched": [], "escalated": False})
    assert isinstance(e, LedgerEntry)
    assert e.entry_type == SYMPTOM_SCREEN
    assert e.subject_id == "s1"
    assert e.entry_hash and e.recorded_at


# -- doctor summary export -----------------------------------------------------

def test_export_is_plain_and_honest(ledger, conn):
    store = VitalsStore(conn)
    store.record(VitalReading(subject_id="s1", vital_type="heart_rate",
                              value=72, unit="bpm"))
    ledger.record("s1", WELLNESS_REPORT,
                  {"observations": [{
                      "rule_id": "sleep", "severity": "nudge",
                      "title": "Sleep averaging under 6 hours",
                      "saw": "avg 5.2h over 7 nights",
                      "why_it_matters": "rest recovery",
                      "consider": "keep bedtime consistent",
                      "reasoning": ["avg=5.2"], "values": {}}]})
    ledger.record("s1", COUNCIL_DELIBERATION,
                  {"verdict": "clear", "observations_count": 1,
                   "dissent": []})
    ledger.record("s1", SYMPTOM_SCREEN,
                  {"matched": [], "escalated": False})

    text = export_doctor_summary("s1", ledger, store)
    assert "wellness companion's record, not a medical record" in text
    assert "Heart rate: 72 bpm" in text
    assert "Sleep averaging under 6 hours" in text
    assert "clear" in text  # council verdict
    assert "not medical advice" in text
    assert "verified intact" in text
    assert "unaltered" in text  # unaltered, not authoritative
    check_claim(text)  # must not raise


def test_export_says_when_chain_is_broken(ledger, conn):
    store = VitalsStore(conn)
    ledger.record("s1", VITAL_READING, {"value": 68})
    ledger.record("s1", VITAL_READING, {"value": 70})
    # delete the FIRST entry only: the survivor's prev_hash no longer
    # resolves, which is exactly what tampering looks like
    conn.execute(
        "DELETE FROM drmy_ledger WHERE subject_id = ? AND entry_id = "
        "(SELECT entry_id FROM drmy_ledger WHERE subject_id = ? "
        " ORDER BY recorded_at ASC LIMIT 1)",
        ("s1", "s1"))
    text = export_doctor_summary("s1", ledger, store)
    assert "TAMPER DETECTED" in text
    assert "unaltered" in text  # the honest contract, still stated
    check_claim(text)


def test_export_for_empty_subject(ledger, conn):
    store = VitalsStore(conn)
    text = export_doctor_summary("new", ledger, store)
    assert "no readings recorded yet" in text
    assert "wellness companion's record, not a medical record" in text
    check_claim(text)
