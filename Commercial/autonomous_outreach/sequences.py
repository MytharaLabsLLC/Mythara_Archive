# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Follow-up sequences.

State machine per prospect:
  touch 1 (day 0) -> touch 2 (+4d) -> touch 3 (+10d) -> done.
  Any reply stops the sequence immediately.
  "stop"/unsubscribe/bounce -> suppressed forever, sequence dead.

Each follow-up is freshly composed (voice.compose_followup) and goes
through the SAME gates as a first touch: kill switch, reservoir, daily
caps, suppression, witness panel. Follow-ups are not second-class sends.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from . import config, prospects, safety, voice


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def due_followups(now: datetime | None = None) -> List[Tuple[Dict[str, Any], int]]:
    """Prospects whose next follow-up is due. Returns [(prospect, touch_n)]."""
    now = now or datetime.now()
    due: List[Tuple[Dict[str, Any], int]] = []
    for d in _all_active():
        touches = d.get("touches", [])
        if not touches:
            continue
        last_n = touches[-1]["n"]
        if last_n >= config.MAX_TOUCHES:
            continue
        # next touch index into FOLLOWUP_SCHEDULE: touch 2 -> index 0, etc.
        sched_idx = last_n - 1
        if sched_idx >= len(config.FOLLOWUP_SCHEDULE):
            continue
        due_at = _parse_ts(touches[-1]["at"]) + timedelta(
            days=config.FOLLOWUP_SCHEDULE[sched_idx]
        )
        if now >= due_at:
            due.append((d, last_n + 1))
    # highest score first — limited daily follow-up budget goes to the best
    due.sort(key=lambda t: -t[0]["score"])
    return due


def _all_active() -> List[Dict[str, Any]]:
    return [
        d
        for d in prospects._load_all().values()
        if d["status"] in (prospects.STATUS_SENT, prospects.STATUS_FOLLOWUP)
    ]


def stop_sequence(pid: str, reason: str) -> None:
    """Kill the sequence (reply, unsubscribe, bounce). Never resumes."""
    d = prospects.get(pid)
    if not d:
        return
    if reason in ("unsubscribe", "bounce", "complaint"):
        safety.suppress(d["email"], reason)
        prospects.update(pid, status=prospects.STATUS_DEAD)
    elif d["status"] not in prospects.TERMINAL:
        prospects.update(pid, status=prospects.STATUS_REPLIED)
