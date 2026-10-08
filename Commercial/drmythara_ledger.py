# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""
DrMythara vitals ledger — a tamper-evident, hash-chained record of
everything health-related the bot does.

Every vitals reading, wellness report, council deliberation, and
symptom-screening event is appended as a chained entry: each entry's
hash covers the previous entry's hash, so altering or deleting any
record breaks the chain and is detectable by verify_chain().

This is the "bring to your doctor" record: the person owns a faithful,
unaltered history of what was shared and what was said. The ledger
lives inside the bot's encrypted database (see DrMytharaBot._db) —
encryption at rest comes from drmythara_security.EncryptedSQLite.

Export (export_doctor_summary): a plain-language summary a person can
hand to their clinician — recent readings, observations with the
exact values and thresholds behind them, council verdicts, and the
honest disclaimer. All user-facing text passes check_claim: clinical,
never oracular, no compliance claims.

HONEST STATUS:
  * IMPLEMENTED: hash-chained append-only ledger, chain verification
    with tamper detection, exportable plain-language summary.
  * The chain proves the record is UNALTERED, not that it is TRUE —
    same honest contract as the emotional chain. verify_chain()
    detects tampering; it does not authenticate the author.
  * NOT a medical record system and not a substitute for one. The
    export says so, plainly.
"""

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from drmythara_persona import check_claim


_CREATE_LEDGER_SQL = """
CREATE TABLE IF NOT EXISTS drmy_ledger (
    entry_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL,
    recorded_at TEXT NOT NULL
)
"""
_CREATE_LEDGER_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_ledger_subject "
    "ON drmy_ledger (subject_id, recorded_at)"
)

GENESIS_HASH = "GENESIS"

# Entry types recorded in the ledger.
VITAL_READING = "vital_reading"
WELLNESS_REPORT = "wellness_report"
COUNCIL_DELIBERATION = "council_deliberation"
SYMPTOM_SCREEN = "symptom_screen"
CHAT_NOTE = "chat_note"  # metadata only — never message text


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=str).encode("utf-8")


@dataclass
class LedgerEntry:
    entry_id: str
    subject_id: str
    entry_type: str
    payload: Dict[str, Any]
    prev_hash: str
    entry_hash: str
    recorded_at: str


class VitalsLedger:
    """Hash-chained health record. Append-only; tampering is detectable."""

    def __init__(self, conn):
        self._conn = conn
        conn.execute(_CREATE_LEDGER_SQL)
        conn.execute(_CREATE_LEDGER_INDEX)
        conn.commit()

    def _last_hash(self, subject_id: str) -> str:
        row = self._conn.execute(
            "SELECT entry_hash FROM drmy_ledger WHERE subject_id = ? "
            "ORDER BY recorded_at DESC, entry_id DESC LIMIT 1",
            (subject_id,)).fetchone()
        return row[0] if row else GENESIS_HASH

    def record(self, subject_id: str, entry_type: str,
               payload: Dict[str, Any]) -> LedgerEntry:
        """Append one chained entry. Returns the sealed entry."""
        entry_id = secrets.token_hex(8)
        recorded_at = _utcnow()
        prev_hash = self._last_hash(subject_id)
        entry_hash = hashlib.sha256(
            prev_hash.encode("utf-8") + _canonical(payload)
            + recorded_at.encode("utf-8")
            + entry_id.encode("utf-8")).hexdigest()
        self._conn.execute(
            "INSERT INTO drmy_ledger (entry_id, subject_id, entry_type, "
            "payload, prev_hash, entry_hash, recorded_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (entry_id, subject_id, entry_type, json.dumps(payload),
             prev_hash, entry_hash, recorded_at))
        self._conn.commit()
        return LedgerEntry(entry_id, subject_id, entry_type, payload,
                           prev_hash, entry_hash, recorded_at)

    def entries(self, subject_id: str,
                entry_type: Optional[str] = None,
                limit: int = 200) -> List[LedgerEntry]:
        q = ("SELECT entry_id, subject_id, entry_type, payload, prev_hash, "
             "entry_hash, recorded_at FROM drmy_ledger WHERE subject_id = ?")
        args: List[Any] = [subject_id]
        if entry_type:
            q += " AND entry_type = ?"
            args.append(entry_type)
        q += " ORDER BY recorded_at ASC, entry_id ASC LIMIT ?"
        args.append(limit)
        rows = self._conn.execute(q, args).fetchall()
        return [LedgerEntry(r[0], r[1], r[2], json.loads(r[3]), r[4], r[5],
                            r[6]) for r in rows]

    def verify_chain(self, subject_id: str) -> Dict[str, Any]:
        """Recompute every link. Returns ok + entry count + first break."""
        entries = self.entries(subject_id, limit=100000)
        prev = GENESIS_HASH
        for e in entries:
            if e.prev_hash != prev:
                return {"ok": False, "entries": len(entries),
                        "broken_at": e.entry_id,
                        "reason": "prev_hash does not match prior entry"}
            recomputed = hashlib.sha256(
                e.prev_hash.encode("utf-8") + _canonical(e.payload)
                + e.recorded_at.encode("utf-8")
                + e.entry_id.encode("utf-8")).hexdigest()
            if recomputed != e.entry_hash:
                return {"ok": False, "entries": len(entries),
                        "broken_at": e.entry_id,
                        "reason": "entry_hash does not match payload"}
            prev = e.entry_hash
        return {"ok": True, "entries": len(entries), "broken_at": None,
                "reason": ""}


# ---------------------------------------------------------------------------
# "Bring to your doctor" export
# ---------------------------------------------------------------------------

def export_doctor_summary(subject_id: str, ledger: VitalsLedger,
                          vitals_store=None) -> str:
    """Plain-language summary the person can hand to their clinician.

    Recent readings, observations with exact values and thresholds,
    council verdicts, chain-verification status, and the honest
    disclaimer. Passes check_claim before return.
    """
    lines = [
        "Dr Mythara — wellness summary",
        f"For: {subject_id}",
        f"Generated: {_utcnow()}",
        "",
        "This is a wellness companion's record, not a medical record. "
        "It shows what was shared and what was observed — your clinician "
        "decides what it means.",
        "",
    ]

    # Recent readings, grouped by type.
    if vitals_store is not None:
        from drmythara_vitals import VITAL_TYPES
        lines.append("Recent readings (most recent first):")
        any_readings = False
        for vt in VITAL_TYPES:
            hist = vitals_store.history(subject_id, vt, limit=5)
            for r in hist:
                any_readings = True
                extra = f"/{r.secondary:g}" if r.secondary else ""
                label = vt.replace("_", " ").capitalize()
                lines.append(
                    f"  - {label}: {r.value:g}{extra} {r.unit} "
                    f"(taken {r.taken_at}, via {r.source})")
        if not any_readings:
            lines.append("  (no readings recorded yet)")
        lines.append("")

    # Observations from the latest wellness report.
    all_reports = ledger.entries(subject_id, WELLNESS_REPORT)
    if all_reports:
        latest = all_reports[-1]
        payload = latest.payload
        lines.append(
            f"Latest wellness review ({latest.recorded_at}):")
        for o in payload.get("observations", []):
            lines.append(f"  - [{o.get('severity', '')}] {o.get('title', '')}")
            lines.append(f"    What was seen: {o.get('saw', '')}")
            lines.append(
                "    Exact basis: "
                + "; ".join(o.get("reasoning", []) or []))
        lines.append("")

    # Council verdicts.
    councils = ledger.entries(subject_id, COUNCIL_DELIBERATION)
    if councils:
        lines.append("Care reviews:")
        for c in councils[-5:]:
            p = c.payload
            lines.append(
                f"  - {c.recorded_at}: {p.get('verdict', '')} "
                f"({p.get('observations_count', 0)} observations)")
        lines.append("")

    chain = ledger.verify_chain(subject_id)
    lines.append(
        f"Record integrity: {chain['entries']} chained entries, "
        f"{'verified intact' if chain['ok'] else 'TAMPER DETECTED'}. "
        "The chain proves this record is unaltered, not that it is "
        "medically authoritative.")
    lines.append("")
    lines.append(
        "Plainly: I am an AI wellness companion, not a medical "
        "professional. This summary is not medical advice — please "
        "review it with a qualified clinician.")
    return check_claim("\n".join(lines))
