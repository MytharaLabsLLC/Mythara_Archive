# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Outreach Queue — real leaf executor for the VP's freelance campaign.

Writes outreach drafts (proposals, emails, messages) as timestamped markdown
files under Commercial/outreach_queue/, each stamped PENDING HERB'S APPROVAL.

This module has NO send capability by design. There is no SMTP, no API, no
browser automation here — a draft leaves this queue only when Herb himself
sends it. If you are looking for a send function, it does not exist and
must not be added without Herb's explicit approval (see WILL.md NO_AUTO_SEND).
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from soul_cradle.bot_witness import (
        witness_action,
        outreach_evidence,
        WitnessBlocked,
        WitnessUnavailable,
    )
except ImportError:  # pragma: no cover — direct-script fallback
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from soul_cradle.bot_witness import (
        witness_action,
        outreach_evidence,
        WitnessBlocked,
        WitnessUnavailable,
    )

QUEUE_DIR = Path(__file__).resolve().parent / "outreach_queue"

VALID_KINDS = ("proposal", "email", "message", "followup")


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "draft").lower()).strip("-")
    return slug[:40] or "draft"


class OutreachQueue:
    """Queue drafts for Herb's one-tap approval. Drafts only — never sends."""

    def __init__(self, queue_dir: Optional[Path] = None):
        self.queue_dir = Path(queue_dir) if queue_dir else QUEUE_DIR
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def queue(
        self,
        kind: str,
        title: str,
        body: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Write a draft file. Returns the file path. Status: pending_approval.

        The draft is witnessed by the Soul Cradle panel BEFORE it is
        written. A BLOCKED verdict stops the queue write entirely; a
        witnessing outage warns loudly but proceeds — Herb's explicit
        approval remains the primary safety for every draft.
        """
        if kind not in VALID_KINDS:
            raise ValueError(f"kind must be one of {VALID_KINDS}, got {kind!r}")
        # --- Soul Cradle witnessing: the outbound chokepoint ----------------
        meta = meta or {}
        evidence, bases = outreach_evidence(
            draft_text=body,
            recipient_kind=str(meta.get("recipient_kind", "prospect")),
            declared_intent=meta.get("declared_intent"),
        )
        try:
            witness_action(
                bot_id="outreach_queue",
                action=f"queue {kind} draft: {title[:60]}",
                evidence=evidence,
                evidence_bases=bases,
                assessor_ids=["hermes", "eros", "nemesis", "janus"],
                enforce=True,
            )
        except WitnessBlocked:
            raise  # do NOT write the file; the block is already chained
        except WitnessUnavailable as exc:
            print(f"[OUTREACH-QUEUE] WITNESS UNAVAILABLE — {exc}")
            print("[OUTREACH-QUEUE] Proceeding with queueing; Herb's approval "
                  "remains the primary safety.")
        # --- end witnessing --------------------------------------------------
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{stamp}-{kind}-{_slug(title)}.md"
        path = self.queue_dir / filename
        # Avoid collision on same-second writes.
        n = 1
        while path.exists():
            path = self.queue_dir / f"{stamp}-{kind}-{_slug(title)}-{n}.md"
            n += 1
        meta_lines = "".join(
            f"{k}: {v}\n" for k, v in (meta or {}).items()
        )
        path.write_text(
            "# DRAFT — PENDING HERB'S APPROVAL\n"
            f"kind: {kind}\n"
            f"title: {title}\n"
            f"created: {datetime.now().isoformat(timespec='seconds')}\n"
            f"status: pending_approval\n"
            f"{meta_lines}"
            "---\n\n"
            f"{body}\n\n"
            "---\n"
            "DO NOT SEND. Herb approves in chat, then sends himself.\n",
            encoding="utf-8",
        )
        return str(path)

    def list_pending(self) -> List[Dict[str, str]]:
        """List queued drafts still awaiting approval, newest last."""
        pending = []
        for path in sorted(self.queue_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            try:
                head = path.read_text(encoding="utf-8")[:600]
            except OSError:
                continue
            if "status: pending_approval" in head:
                kind = re.search(r"^kind: (.+)$", head, re.M)
                title = re.search(r"^title: (.+)$", head, re.M)
                pending.append(
                    {
                        "path": str(path),
                        "kind": kind.group(1) if kind else "?",
                        "title": title.group(1) if title else path.name,
                    }
                )
        return pending


if __name__ == "__main__":
    q = OutreachQueue()
    p = q.queue("proposal", "Example gig", "Hello — draft body here.")
    print(f"queued: {p}")
    print(f"pending: {len(q.list_pending())}")
