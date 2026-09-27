# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Notary receipts — proof of what the bot did.

Every witnessed send gets a receipt: a self-contained JSON document proving

  (a) the 8-assessor panel cleared the EXACT text that went out,
  (b) the EXACT bytes that left the machine (body hash), and
  (c) both facts are chained into tamper-evident logs.

Anyone holding a receipt can run verify_receipt() and get a yes/no:
the receipt hash recomputes, the witness-log entry it cites exists and
its chain is intact, and the send ledger holds the same body hash.

The honest contract, same as the emotional chain: a receipt proves the
record is UNALTERED. It does not prove the claims inside the email are
true — that was the panel's witnessed judgment call, preserved here
with any dissent intact.

Receipts form their own hash chain (state/receipts.jsonl) so a missing
or reordered receipt is detectable.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from . import config

try:
    from soul_cradle.bot_witness import (
        ACTION_LOG_PATH,
        ActionWitnessResult,
        verify_action_log,
    )
except ImportError:  # pragma: no cover — exercised via repo-root runs
    ACTION_LOG_PATH = None  # type: ignore
    ActionWitnessResult = Any  # type: ignore
    verify_action_log = None  # type: ignore

RECEIPT_VERSION = "mythara-receipt/1"


def _receipts_file() -> Path:
    # Resolved at call time: tests relocate config.STATE_DIR per-run.
    return config.STATE_DIR / "receipts.jsonl"


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _last_receipt_hash() -> str:
    receipts_file = _receipts_file()
    if not receipts_file.exists():
        return "GENESIS"
    last = None
    with open(receipts_file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                last = line
    if not last:
        return "GENESIS"
    return json.loads(last).get("receipt_hash", "GENESIS")


def issue_receipt(
    witness_result: "ActionWitnessResult",
    send_entry: Dict[str, Any],
) -> Dict[str, Any]:
    """Build, chain, and persist a notary receipt for one witnessed send.

    witness_result comes from safety.witness_send() (the 8-assessor panel);
    send_entry comes from sender.BaseSender.send() (what actually went out).
    """
    judgments = []
    for j in witness_result.judgments or []:
        judgments.append(
            {
                "assessor": j.get("assessor_id") or j.get("assessor"),
                "verdict": j.get("verdict"),
                # The sealed judgment hash: proves this exact judgment was
                # the one the panel rendered, without stuffing the whole
                # rubric text into every receipt.
                "judgment_hash": hashlib.sha256(_canonical(j)).hexdigest(),
            }
        )
    receipt = {
        "receipt_version": RECEIPT_VERSION,
        "receipt_id": "",
        "issued_at": int(time.time()),
        "bot_id": witness_result.bot_id,
        "action": witness_result.action,
        "body_sha256": send_entry.get("body_sha256"),
        "send": {
            "sender": send_entry.get("sender"),
            "status": send_entry.get("status"),
            "detail": send_entry.get("detail", ""),
            "message_id": send_entry.get("message_id", ""),
        },
        "witness": {
            "verdict": witness_result.verdict,
            "panel_note": witness_result.note,
            "entry_hash": witness_result.entry_hash,
            "judgments": judgments,
        },
        "prev_receipt_hash": _last_receipt_hash(),
    }
    receipt["receipt_id"] = hashlib.sha256(
        _canonical({k: v for k, v in receipt.items() if k != "receipt_hash"})
    ).hexdigest()[:16]
    receipt["receipt_hash"] = hashlib.sha256(
        receipt["prev_receipt_hash"].encode() + _canonical(
            {k: v for k, v in receipt.items() if k != "receipt_hash"}
        )
    ).hexdigest()

    receipts_file = _receipts_file()
    receipts_file.parent.mkdir(parents=True, exist_ok=True)
    with open(receipts_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def _find_witness_entry(entry_hash: str) -> Optional[Dict[str, Any]]:
    if ACTION_LOG_PATH is None or not Path(ACTION_LOG_PATH).exists():
        return None
    with open(ACTION_LOG_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("entry_hash") == entry_hash:
                return entry
    return None


def _body_in_send_ledger(body_sha256: str) -> bool:
    log = Path(config.SEND_LOG_FILE)
    if not log.exists():
        return False
    with open(log, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if json.loads(line).get("body_sha256") == body_sha256:
                return True
    return False


def verify_receipt(receipt: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Verify a notary receipt. Returns (ok, details)."""
    details: Dict[str, Any] = {"receipt_id": receipt.get("receipt_id")}

    # 1. The receipt's own hash recomputes.
    recomputed = hashlib.sha256(
        str(receipt.get("prev_receipt_hash", "")).encode()
        + _canonical({k: v for k, v in receipt.items() if k != "receipt_hash"})
    ).hexdigest()
    if recomputed != receipt.get("receipt_hash"):
        return False, {**details, "fail": "receipt_hash mismatch — receipt altered"}

    # 2. The witness chain it cites is intact.
    if verify_action_log is None:
        return False, {**details, "fail": "witness verifier unavailable"}
    chain_ok, chain_msg = verify_action_log()
    details["witness_chain"] = chain_msg
    if not chain_ok:
        return False, {**details, "fail": f"witness chain broken: {chain_msg}"}

    # 3. The cited witness entry exists and cleared the action.
    entry = _find_witness_entry(receipt["witness"]["entry_hash"])
    if entry is None:
        return False, {**details, "fail": "witness entry not found in action log"}
    details["witness_verdict"] = entry.get("verdict")
    if entry.get("verdict") != receipt["witness"]["verdict"]:
        return False, {**details, "fail": "witness verdict mismatch"}

    # 4. The exact bytes went out — the send ledger holds the body hash.
    if not _body_in_send_ledger(receipt["body_sha256"]):
        return False, {**details, "fail": "body hash not found in send ledger"}

    details["send_status"] = "bytes accounted for in send ledger"
    return True, details
