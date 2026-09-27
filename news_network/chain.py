"""Dossier chain — tamper-evident chaining for news dossiers.

Mirrors the sealing contract of soul_cradle.emotional_chain: the chain
proves each dossier's evidence and judgments are UNALTERED since they
were written. It does not prove the underlying news is true.

Each record chains: the evidence pack, the eight sealed news judgments,
the panel summary, and the dossier's markdown hash.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


@dataclass
class DossierRecord:
    record_id: str
    event_id: str
    timestamp: int
    evidence_pack: Dict[str, Any] = field(default_factory=dict)
    judgments: List[Dict[str, Any]] = field(default_factory=list)
    panel: Dict[str, Any] = field(default_factory=dict)
    dossier_markdown_hash: str = ""
    prev_hash: str = ""
    record_hash: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("record_hash", None)
        return d

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _seal(r: DossierRecord) -> DossierRecord:
    r.record_hash = hashlib.sha256(_canonical(r.unsigned_dict())).hexdigest()
    return r


def _verify_seal(r: DossierRecord) -> bool:
    if not r.record_hash:
        return False
    return hashlib.sha256(_canonical(r.unsigned_dict())).hexdigest() == r.record_hash


class DossierChain:
    """Append-only hash chain of witnessed dossiers, persisted as JSONL."""

    def __init__(self, path: Path, operator: str = "news_network"):
        self.path = Path(path)
        self.operator = operator
        self.records: List[DossierRecord] = []
        self._load_or_genesis()

    # -- genesis ------------------------------------------------------
    def _genesis(self) -> DossierRecord:
        return _seal(DossierRecord(
            record_id="genesis",
            event_id="GENESIS",
            timestamp=int(time.time()),
            evidence_pack={"note": (
                "Genesis — the chain's founding record. Operator attests: "
                "every chained dossier's evidence pack contains only text "
                "fetched from the listed article URLs at the listed "
                "fetched_at times; every judgment is sealed at write time. "
                "The chain proves the dossiers are unaltered, not that the "
                "underlying reporting is true."
            )},
            panel={"verdict": "genesis"},
            prev_hash="0" * 64,
        ))

    def _load_or_genesis(self) -> None:
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.records.append(DossierRecord(**json.loads(line)))
        if not self.records:
            self.records.append(self._genesis())
            self._persist()

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            for r in self.records:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    # -- recording ----------------------------------------------------
    def append(self, event_id: str, evidence_pack: Dict[str, Any],
               judgments: List[Dict[str, Any]], panel: Dict[str, Any],
               dossier_markdown: str) -> DossierRecord:
        record_id = hashlib.sha256(
            f"dossier-chain:{event_id}:{int(time.time())}".encode()
        ).hexdigest()[:16]
        record = _seal(DossierRecord(
            record_id=record_id,
            event_id=event_id,
            timestamp=int(time.time()),
            evidence_pack=evidence_pack,
            judgments=judgments,
            panel=panel,
            dossier_markdown_hash=hashlib.sha256(
                dossier_markdown.encode("utf-8")).hexdigest(),
            prev_hash=self.records[-1].record_hash,
        ))
        self.records.append(record)
        self._persist()
        return record

    # -- verification -------------------------------------------------
    def verify(self) -> Tuple[bool, Dict[str, Any]]:
        details: Dict[str, Any] = {
            "records": len(self.records), "failures": []}
        for i, record in enumerate(self.records):
            if not _verify_seal(record):
                details["failures"].append(
                    {"record_id": record.record_id,
                     "reason": "record seal mismatch — tampered"})
                continue
            if i > 0 and record.prev_hash != self.records[i - 1].record_hash:
                details["failures"].append(
                    {"record_id": record.record_id,
                     "reason": "prev_hash link broken"})
            for j in record.judgments:
                unsigned = {k: v for k, v in j.items() if k != "integrity_hash"}
                expect = hashlib.sha256(_canonical(unsigned)).hexdigest()
                if j.get("integrity_hash") != expect:
                    details["failures"].append(
                        {"record_id": record.record_id,
                         "reason": f"witness {j.get('assessor_id')} seal mismatch — forged"})
        details["ok"] = not details["failures"]
        return details["ok"], details
