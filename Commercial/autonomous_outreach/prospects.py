# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Prospect discovery, scoring, and state.

Prospects are founders/teams deploying AI agents — the "Accountable AI
builds" ($5-15K service) customer. Legitimate sources only:

  * manual import (CSV) — Herb or the main agent feeds researched lists.
  * research notes — per-prospect facts gathered by real research, each with
    a source. NEVER invented.

There is deliberately no scraper and no purchased-list importer here.
Fabricated prospect data is a fabrication like any other: HONEST_CLAIMS_ONLY
covers the pipeline too.

Scoring is a deterministic rubric over OBSERVED signals, not vibes.
A prospect with no verifiable signals scores low — the machine says so
honestly instead of inflating the pipeline.
"""

import csv
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import config

# Prospect lifecycle. Touches advance only through the scheduler.
STATUS_NEW = "new"            # discovered, not yet researched
STATUS_RESEARCHED = "researched"
STATUS_SENT = "sent"          # touch 1 sent
STATUS_FOLLOWUP = "followup"  # in follow-up sequence
STATUS_REPLIED = "replied"
STATUS_INTERESTED = "interested"  # hot — routed to Herb
STATUS_CLOSED = "closed"      # won
STATUS_DEAD = "dead"          # not interested / bounced / unsubscribed

TERMINAL = {STATUS_CLOSED, STATUS_DEAD}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_all() -> Dict[str, Dict[str, Any]]:
    """id -> prospect dict."""
    out: Dict[str, Dict[str, Any]] = {}
    p = config.PROSPECTS_FILE
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                d = json.loads(line)
                out[d["id"]] = d
    return out


def _save_all(prospects: Dict[str, Dict[str, Any]]) -> None:
    config.PROSPECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.PROSPECTS_FILE, "w", encoding="utf-8") as fh:
        for d in prospects.values():
            fh.write(json.dumps(d) + "\n")


def score_prospect(signals: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Deterministic 0-100 rubric over observed signals.

    Signals (all caller-attested; unknown = absent = 0 points):
      deploys_ai_agents (bool, 30) — they ship agents to real users
      agent_trust_pain  (bool, 25) — public evidence they need accountability
                                     (incident, compliance ask, enterprise buyers)
      contactable       (bool, 20) — real email or real contact path known
      team_size_fit     (bool, 15) — small team / founder-led (buys services)
      budget_signal     (bool, 10) — funded, hiring, or paying for tools
    Returns (score, reasons). No signal inflation: missing keys score 0.
    """
    reasons: List[str] = []
    score = 0
    checks = [
        ("deploys_ai_agents", 30, "deploys AI agents to real users"),
        ("agent_trust_pain", 25, "visible trust/accountability pain"),
        ("contactable", 20, "real contact path known"),
        ("team_size_fit", 15, "founder-led / small team"),
        ("budget_signal", 10, "funding/hiring/tool-spend signal"),
    ]
    for key, pts, label in checks:
        if signals.get(key) is True:
            score += pts
            reasons.append(f"+{pts} {label}")
    return score, reasons


def add_prospect(
    name: str,
    email: str,
    company: str = "",
    role: str = "",
    signals: Optional[Dict[str, Any]] = None,
    source: str = "manual",
    notes: str = "",
) -> Dict[str, Any]:
    """Add one prospect. Email is required; duplicates (by email) are refused."""
    email = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError(f"not a valid email: {email!r}")
    prospects = _load_all()
    for d in prospects.values():
        if d["email"] == email:
            raise ValueError(f"duplicate prospect email: {email}")
    signals = signals or {}
    score, reasons = score_prospect(signals)
    pid = uuid.uuid4().hex[:12]
    d: Dict[str, Any] = {
        "id": pid,
        "name": name.strip(),
        "email": email,
        "company": company.strip(),
        "role": role.strip(),
        "signals": signals,
        "score": score,
        "score_reasons": reasons,
        "source": source,
        "notes": notes,
        "status": STATUS_NEW,
        "touches": [],          # [{n, at, variant, witness_ref}]
        "research_brief": None,  # filled by research.py
        "created_at": _now(),
        "updated_at": _now(),
    }
    prospects[pid] = d
    _save_all(prospects)
    return d


def import_csv(path: str, source: str = "manual") -> Dict[str, int]:
    """Import prospects from a CSV with headers: name,email,company,role,notes.

    Signal columns (optional, values 'yes'/'no'): deploys_ai_agents,
    agent_trust_pain, contactable, team_size_fit, budget_signal.
    Returns {'added': n, 'skipped': n}.
    """
    added, skipped = 0, 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            email = (row.get("email") or "").strip()
            if not email:
                skipped += 1
                continue
            signals = {
                k: (row.get(k, "").strip().lower() in ("yes", "true", "1"))
                for k in (
                    "deploys_ai_agents",
                    "agent_trust_pain",
                    "contactable",
                    "team_size_fit",
                    "budget_signal",
                )
            }
            # contactable is true by construction when a real email is given
            signals["contactable"] = True
            try:
                add_prospect(
                    name=row.get("name", "").strip(),
                    email=email,
                    company=row.get("company", "").strip(),
                    role=row.get("role", "").strip(),
                    signals=signals,
                    source=source,
                    notes=row.get("notes", "").strip(),
                )
                added += 1
            except ValueError:
                skipped += 1
    return {"added": added, "skipped": skipped}


def get(pid: str) -> Optional[Dict[str, Any]]:
    return _load_all().get(pid)


def update(pid: str, **fields: Any) -> Dict[str, Any]:
    prospects = _load_all()
    if pid not in prospects:
        raise KeyError(pid)
    prospects[pid].update(fields)
    prospects[pid]["updated_at"] = _now()
    _save_all(prospects)
    return prospects[pid]


def record_touch(pid: str, touch_n: int, variant: str, send_ref: str) -> Dict[str, Any]:
    prospects = _load_all()
    d = prospects[pid]
    d["touches"].append(
        {"n": touch_n, "at": _now(), "variant": variant, "send_ref": send_ref}
    )
    d["status"] = STATUS_SENT if touch_n == 1 else STATUS_FOLLOWUP
    d["updated_at"] = _now()
    _save_all(prospects)
    return d


def due_for_first_touch(limit: int) -> List[Dict[str, Any]]:
    """Highest-scored new, researched prospects ready for touch 1."""
    cands = [
        d
        for d in _load_all().values()
        if d["status"] == STATUS_RESEARCHED and d["research_brief"]
    ]
    cands.sort(key=lambda d: (-d["score"], d["created_at"]))
    return cands[:limit]
