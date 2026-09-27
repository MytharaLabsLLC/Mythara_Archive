# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Outreach pipeline — the daily run.

Purpose (redesigned 2026-09-27): this is an operator-run conversation
pipeline, not an autonomous sending machine. Sending is the means;
qualified conversations are the end. The operator reads the brief,
works the replies, and owns every send the machine makes.

Pipeline per cycle:
  1. Kill switch / reservoir / caps pre-checks (halt loudly on any failure)
  2. Inbox triage  — read replies where they land (Yahoo IMAP first),
                     classify, route hot ones to the operator, feed learning
  3. Follow-ups    — due sequences, freshly composed, fully gated
  4. First touches — researched prospects, variant selected by the learner,
                     composed in the fresh voice, fully gated
  5. Report       — what ran, what sent, what escalated, what's blocked,
                     plus a readable operator brief on disk

Every send passes safety.clear_to_send() AND safety.witness_send().
A witness block or a witness outage NEVER sends (fail-closed: pre-send
approval no longer exists to catch a miss). Real (non-dry-run) sends
also require the CAN-SPAM postal address in config — cold outreach
without one is illegal, so the run refuses until Herb sets it.
Post-send audit lives in the witness log + send ledger, both hash-chained.

Designed for cron:  `python -m Commercial.autonomous_outreach.run`
Exits 0 on a clean run, 2 when halted by a gate (cron-safe: not a crash).
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from soul_cradle.bot_witness import WitnessBlocked, WitnessUnavailable

from Commercial.autonomous_outreach import (
    config,
    learning,
    prospects,
    receipts,
    safety,
    sender,
    sequences,
    triage,
    voice,
)


def _execute_send(
    p: Dict[str, Any],
    subject: str,
    body: str,
    kind: str,          # "new" | "followup"
    touch_n: int,
    variant: str,
    snd: sender.BaseSender,
) -> Dict[str, Any]:
    """One gated send. Raises safety.SafetyHalt / WitnessBlocked /
    WitnessUnavailable / sender.SenderBlocked instead of half-sending."""
    ok, reason = safety.clear_to_send(p["email"], kind)
    if not ok:
        raise safety.SafetyHalt(reason)
    # CAN-SPAM: a real send without a physical postal address in the
    # footer is illegal. Dry-run is unaffected — nothing leaves the machine.
    if snd.name != "dryrun" and not config.CANSPAM_POSTAL_ADDRESS.strip():
        raise safety.SafetyHalt(
            "real sends need config.CANSPAM_POSTAL_ADDRESS set to Herb's "
            "mailing address (CAN-SPAM requirement). Nothing was sent."
        )
    # Witness the FINAL text. Fail-closed on outage.
    research_basis = ""
    brief = p.get("research_brief") or {}
    facts = brief.get("facts", [])
    if facts:
        research_basis = "; ".join(
            f"{f['fact']} [{f['source']}]" for f in facts
        )
    witnessed = safety.witness_send(
        subject=subject,
        body=body,
        recipient_email=p["email"],
        declared_intent=(
            "honest first-touch outreach for Accountable AI builds "
            f"($5-15K project work); touch {touch_n}; variant {variant}"
            if kind == "new"
            else f"honest follow-up (touch {touch_n}) for Accountable AI builds"
        ),
        research_basis=research_basis,
    )
    sender.pace()
    entry = snd.send(p["email"], subject, body)
    # Notarize it: the receipt proves the panel cleared THIS text and
    # THESE bytes went out. Anyone holding it can verify independently.
    # (witnessed is None only under test stubs — no receipt then.)
    if witnessed is not None:
        receipt = receipts.issue_receipt(witnessed, entry)
        entry["receipt_id"] = receipt["receipt_id"]
    safety.record_send_made(kind)
    prospects.record_touch(p["id"], touch_n, variant, entry["body_sha256"])
    return entry


def _write_operator_brief(report: Dict[str, Any], snd: sender.BaseSender) -> str:
    """Write the human-readable run brief the operator actually reads.

    Raw JSONL is for audit; this file is for the morning check: what
    happened, what needs a human, what's broken. Returns the path."""
    brief_path = config.STATE_DIR / "operator_brief.md"
    lines = [
        f"# Outreach operator brief — {report['at']}",
        "",
        f"sender mode: {snd.name}",
        f"inbox: {report.get('inbox', 'unknown')}",
        f"halted: {report['halted'] or 'no'}",
        "",
        f"first touches sent: {report['first_touches_sent']}",
        f"follow-ups sent: {report['followups_sent']}",
        f"replies triaged: {len(report['triaged'])}",
        "",
    ]
    if report["triaged"]:
        lines.append("## Replies")
        for t in report["triaged"]:
            lines.append(f"- {t.get('from', '?')}: {t.get('action', '?')}")
        lines.append("")
    if report["escalations"]:
        lines.append("## Needs a human")
        for e in report["escalations"]:
            lines.append(f"- {e}")
        lines.append("")
    if report["errors"]:
        lines.append("## Errors")
        for e in report["errors"]:
            lines.append(f"- {e}")
        lines.append("")
    lines.append("Ledger: state/send_log.jsonl — every attempt, hashed.")
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text("\n".join(lines), encoding="utf-8")
    return str(brief_path)


def run_cycle(snd: sender.BaseSender) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "halted": None,
        "inbox": "unknown",
        "triaged": [],
        "followups_sent": 0,
        "first_touches_sent": 0,
        "escalations": [],
        "errors": [],
    }

    # --- gate 0: kill switch + reservoir ------------------------------------
    if safety.kill_switch_engaged():
        report["halted"] = "kill switch engaged"
        _write_operator_brief(report, snd)
        return report
    tier, note = safety.reservoir_tier()
    if tier == "depleted":
        path = safety.escalate(
            "RESERVOIR DEPLETED — outreach halted",
            f"{note}\n\nAll sending stopped until benevolence replenishes. "
            "Herb: review the ledger, then say the word.",
        )
        report["halted"] = "reservoir depleted"
        report["escalations"].append(path)
        _write_operator_brief(report, snd)
        return report

    # --- 1. inbox triage ------------------------------------------------------
    # Read where replies actually land: the Yahoo mailbox first (IMAP),
    # legacy Gmail API as fallback. If neither is readable, say so loudly
    # in the report instead of silently assuming no replies.
    try:
        if triage.yahoo_inbox_readable():
            replies = triage.fetch_recent_replies_yahoo()
            report["inbox"] = "yahoo-imap"
        else:
            gmail_service = _gmail_service_if_available()
            if gmail_service is not None:
                replies = triage.fetch_recent_replies(gmail_service)
                report["inbox"] = "gmail-api"
            else:
                replies = []
                report["inbox"] = "unreadable"
                report["errors"].append(
                    "triage: inbox unreadable (no Yahoo app-password file, "
                    "no Gmail service) — replies were NOT processed this run."
                )
        for r in replies:
            pid = triage.match_to_prospect(r["from"])
            if not pid:
                continue
            cls = triage.classify_reply(r["subject"], r["snippet"])
            if cls in ("autoresponder",):
                continue
            done = triage.route_classification(
                pid, cls, r["subject"], r["snippet"]
            )
            report["triaged"].append({"from": r["from"], **done})
            if done.get("file"):
                report["escalations"].append(done["file"])
    except Exception as exc:  # triage must never kill the send pipeline
        report["errors"].append(f"triage failed (non-fatal): {exc}")

    # --- 2. follow-ups due ----------------------------------------------------
    sent = safety.daily_sent_total()
    followup_budget = config.MAX_FOLLOWUPS_PER_DAY - sent.get("followup", 0)
    for prospect, touch_n in sequences.due_followups()[: max(followup_budget, 0)]:
        try:
            variant = prospect["touches"][-1]["variant"]  # stay consistent
            subject, body = voice.compose(prospect, variant, touch_n)
            _execute_send(prospect, subject, body, "followup", touch_n, variant, snd)
            report["followups_sent"] += 1
        except (safety.SafetyHalt, WitnessBlocked, WitnessUnavailable,
                sender.SenderBlocked, ValueError) as exc:
            report["errors"].append(f"followup {prospect['email']}: {exc}")
            if isinstance(exc, safety.SafetyHalt) and "kill switch" in str(exc):
                report["halted"] = str(exc)
                return report

    # --- 3. first touches ------------------------------------------------------
    sent = safety.daily_sent_total()
    new_budget = config.MAX_NEW_PROSPECTS_PER_DAY - sent.get("new", 0)
    for prospect in prospects.due_for_first_touch(max(new_budget, 0)):
        try:
            variant = learning.select_variant()
            subject, body = voice.compose(prospect, variant, touch_n=1)
            _execute_send(prospect, subject, body, "new", 1, variant, snd)
            report["first_touches_sent"] += 1
        except (safety.SafetyHalt, WitnessBlocked, WitnessUnavailable,
                sender.SenderBlocked, ValueError) as exc:
            report["errors"].append(f"first touch {prospect['email']}: {exc}")
            if isinstance(exc, safety.SafetyHalt) and "kill switch" in str(exc):
                report["halted"] = str(exc)
                _write_operator_brief(report, snd)
                return report

    _write_operator_brief(report, snd)
    return report


def _gmail_service_if_available():
    """Best-effort Gmail service for triage reads. None when unavailable."""
    try:
        from Commercial.autonomous_outreach.sender import GmailSender
        return GmailSender()._service_or_raise()
    except Exception:
        return None


def main() -> int:
    snd = sender.get_sender()
    print(f"[outreach] sender={snd.name} reservoir={safety.reservoir_tier()[0]}")
    try:
        report = run_cycle(snd)
    except Exception:
        traceback.print_exc()
        return 1
    print(
        f"[outreach] done: first_touches={report['first_touches_sent']} "
        f"followups={report['followups_sent']} triaged={len(report['triaged'])} "
        f"escalations={len(report['escalations'])} errors={len(report['errors'])}"
    )
    if report["halted"]:
        print(f"[outreach] HALTED: {report['halted']}")
        return 2
    for e in report["errors"]:
        print(f"[outreach] error: {e}")
    for e in report["escalations"]:
        print(f"[outreach] escalation: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
