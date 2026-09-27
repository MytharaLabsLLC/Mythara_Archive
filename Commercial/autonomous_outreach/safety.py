# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Safety gates for the autonomous outreach machine.

These constraints survive Herb's "full auto" grant and are non-negotiable.
`clear_to_send()` runs before EVERY send. It returns (ok, reason).

Gate order is deliberate — cheapest, most decisive checks first:
  1. Kill switch file            -> halt immediately
  2. Channel whitelist           -> email only, always
  3. Benevolence reservoir       -> depleted halts ALL sending, escalates
  4. Daily rate limits           -> protects Gmail/domain reputation
  5. Suppression list            -> unsubscribed/bounced addresses never mailed
  6. Witness panel               -> BLOCKED verdict never sends.
                                   Witness OUTAGE fails CLOSED here (no send),
                                   because pre-send approval no longer exists
                                   to catch what the panel missed.

Post-send audit (not pre-send approval) is where Herb reviews: every send
is hash-chained into the witness log by bot_witness.witness_action.
"""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from soul_cradle import benevolence
from soul_cradle.bot_witness import (
    witness_action,
    outreach_evidence,
    WitnessBlocked,
    WitnessUnavailable,
)

from . import config


class SafetyHalt(Exception):
    """Raised when any gate refuses a send. Carries the human-readable reason."""


def kill_switch_engaged() -> bool:
    """True if Herb has stopped the outreach."""
    return config.KILL_SWITCH_FILE.exists()


def engage_kill_switch(reason: str = "") -> None:
    """Programmatic kill switch (the file is the real one; this is convenience)."""
    config.KILL_SWITCH_FILE.write_text(
        f"engaged: {reason or 'manual'}\n", encoding="utf-8"
    )


def reservoir_tier() -> Tuple[str, str]:
    """Current benevolence latitude tier, e.g. ('depleted', '...')."""
    return benevolence.latitude()


def _daily_counts() -> Dict[str, Dict[str, int]]:
    p = config.DAILY_COUNT_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
    return {}


def _save_daily_counts(counts: Dict[str, Dict[str, int]]) -> None:
    config.DAILY_COUNT_FILE.write_text(json.dumps(counts, indent=2), encoding="utf-8")


def daily_sent_total(today: Optional[str] = None) -> Dict[str, int]:
    """{'new': n, 'followup': n} sends already made today."""
    today = today or date.today().isoformat()
    return _daily_counts().get(today, {"new": 0, "followup": 0})


def record_send_made(kind: str) -> None:
    """Increment today's counter. kind: 'new' or 'followup'."""
    today = date.today().isoformat()
    counts = _daily_counts()
    day = counts.setdefault(today, {"new": 0, "followup": 0})
    day[kind] = day.get(kind, 0) + 1
    _save_daily_counts(counts)


def is_suppressed(email: str) -> Optional[str]:
    """Return the suppression reason if this address must never be mailed."""
    p = config.SUPPRESSION_FILE
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data.get(email.strip().lower())


def suppress(email: str, reason: str) -> None:
    """Permanently suppress an address (unsubscribe, bounce, complaint)."""
    p = config.SUPPRESSION_FILE
    data: Dict[str, str] = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    data[email.strip().lower()] = reason
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def escalate(subject: str, detail: str) -> str:
    """Write an escalation for Herb's post-send review. Returns the file path."""
    from datetime import datetime

    config.ESCALATION_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = "".join(c if c.isalnum() else "-" for c in subject.lower())[:40].strip("-")
    path = config.ESCALATION_DIR / f"{stamp}-{slug or 'escalation'}.md"
    path.write_text(
        f"# ESCALATION — {subject}\n"
        f"at: {datetime.now().isoformat(timespec='seconds')}\n\n{detail}\n",
        encoding="utf-8",
    )
    return str(path)


# Manipulation markers scanned in the FINAL send text before witnessing.
# The assessor panel scores caller-declared evidence — it cannot see
# manipulation the caller doesn't declare. This scan makes the declaration
# honest: hits flip deception_involved=True and the panel (eros/hermes,
# critical severity) blocks the send. Intentionally sensitive: in full-auto
# there is no pre-send review, so a false positive (blocked honest email)
# is cheaper than a false negative (sent manipulation).
MANIPULATION_PATTERNS = (
    # fake scarcity / urgency
    "slots left", "expires friday", "expires today", "pricing expires",
    "booked til", "only 2 left", "only 3 left", "act now", "last chance",
    "don't miss out",
    # fabricated social proof
    "already signed", "already using this", "achieved zero audit",
    "competitor just", "banks already",
    # fake personalization
    "loved your post", "loved your recent", "great post", "noticed you",
    "saw that you", "congrats on",
)


def scan_manipulation(text: str) -> List[str]:
    """Return the manipulation markers found in text (case-insensitive)."""
    low = text.lower()
    return [p for p in MANIPULATION_PATTERNS if p in low]


def witness_send(
    subject: str,
    body: str,
    recipient_email: str,
    declared_intent: str,
    research_basis: str = "",
):
    """Run the 8-assessor witness gate on the FINAL send text.

    Returns the ActionWitnessResult so callers can notarize what the
    panel cleared. Raises WitnessBlocked (never send) or WitnessUnavailable
    (fail closed: never send — there is no pre-send approval left to
    catch a miss).

    The panel scores caller-declared evidence, so the declaration is made
    honest first: the final text is scanned for manipulation markers and
    any hit sets deception_involved=True, which the panel blocks on.
    """
    full_text = f"To: {recipient_email}\nSubject: {subject}\n\n{body}"
    hits = scan_manipulation(full_text)
    evidence, bases = outreach_evidence(
        draft_text=full_text,
        recipient_kind="prospect",
        deception_involved=bool(hits),
        deception_basis=(
            f"autonomous_outreach text scan found manipulation markers: {hits}"
            if hits
            else "autonomous_outreach: final text scanned, no manipulation markers"
        ),
        declared_intent=declared_intent,
    )
    if research_basis:
        bases["research_basis"] = research_basis
    # Full witness panel for autonomous sends — no subsetting, because
    # nobody reviews these before they go out.
    return witness_action(
        bot_id="autonomous_outreach",
        action=f"send email to {recipient_email}: {subject[:60]}",
        evidence=evidence,
        evidence_bases=bases,
        assessor_ids=None,  # full panel
        enforce=True,
    )


def clear_to_send(
    recipient_email: str,
    kind: str,
    channel: str = "email",
) -> Tuple[bool, str]:
    """All gates. Returns (True, 'ok') or (False, reason). No side effects."""
    if kill_switch_engaged():
        return False, "kill switch engaged (STOP file present)"
    if channel not in config.ALLOWED_CHANNELS:
        return False, f"channel {channel!r} not in {config.ALLOWED_CHANNELS}"
    tier, note = reservoir_tier()
    if tier == "depleted":
        return False, f"reservoir depleted — all sending halted. {note}"
    reason = is_suppressed(recipient_email)
    if reason:
        return False, f"address suppressed: {reason}"
    sent = daily_sent_total()
    if kind == "new" and sent.get("new", 0) >= config.MAX_NEW_PROSPECTS_PER_DAY:
        return False, "daily new-prospect cap reached"
    if kind == "followup" and sent.get("followup", 0) >= config.MAX_FOLLOWUPS_PER_DAY:
        return False, "daily follow-up cap reached"
    if sum(sent.values()) >= config.MAX_TOTAL_SENDS_PER_DAY:
        return False, "daily total send cap reached"
    return True, "ok"
