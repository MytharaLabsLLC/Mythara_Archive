# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Sales Bot Public Interface — honest draft-queue wrapper
======================================================

A simplified entry point for demoing the Mythara sales bot: hand it an
email, get back a governed draft queued for Herb's approval.

DRAFT-ONLY: this interface never sends email. The returned dict carries
status="pending_approval", queue_path, and sent=False.

NOTE ON "PROTECTION": the governance source (sales_bot_ssip_governance.py)
sits in this repo in plain Python — nothing here is compiled, obfuscated,
or hidden. Packaging options (PyArmor, .pyd, API-only) are discussed in
obfuscate_sales_bot.py as future work, not current state. Do not claim
otherwise.
"""

from pathlib import Path
import json

from sales_bot_ssip_governance import GovernedEmailAssistant


class PublicSalesBotInterface:
    """
    Public-facing wrapper around the governed email assistant.

    Contract:
    - Input:  email_data {"subject", "body", optional "prospect_email"}
    - Output: draft + governance decision + queue metadata
    - The draft is queued (status: pending_approval). Nothing is sent.
    """

    def __init__(self, queue_dir=None, audit_log_path=None):
        self._assistant = GovernedEmailAssistant(audit_log_path=audit_log_path)
        self._queue_dir = queue_dir

    def process_email(self, email_data: dict) -> dict:
        """
        Generate a governed draft and queue it for Herb's approval.

        Returns:
            {
                "draft": str,                    # Generated response
                "status": "pending_approval",    # Draft only — never sent
                "sent": False,                   # Always False
                "queue_path": str,               # Where the draft was queued
                "action_taken": str,             # DRAFT_QUEUED_FOR_APPROVAL
                "can_auto_send": False,          # Always False (draft-only)
                "messenger": str,                # Risk classification label
                "governance_summary": {
                    "intent": str,
                    "autonomy_level": str,
                    "blessings": int,
                    "violations": list,
                    "hash": str,
                }
            }
        """
        result = self._assistant.process_email(email_data, queue_dir=self._queue_dir)

        return {
            "draft": result["draft"],
            "status": "pending_approval",
            "sent": False,
            "queue_path": result["queue_path"],
            "action_taken": result["action_taken"],
            "can_auto_send": False,
            "auto_send_eligible": result.get("auto_send_eligible", False),
            "messenger": result["messenger"],
            "governance_summary": {
                "intent": result["intent"],
                "autonomy_level": result["autonomy_level"],
                "blessings": result["blessings"],
                "violations": result["violations"],
                "hash": result["hash"],
            },
        }

    def get_audit_log(self, limit: int = 100) -> list:
        """Newest-first governance decisions. Malformed lines are skipped."""
        log_path = self._assistant.governance.audit_log
        if not log_path.exists():
            return []

        entries = []
        with open(log_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # skip corrupt lines, keep the rest

        return list(reversed(entries))[:limit]

    def get_governance_stats(self) -> dict:
        """Public stats — draft-only posture stated plainly."""
        report = self._assistant.get_governance_report()
        return {
            "outbound_policy": report["outbound_policy"],
            "autonomy_level": report["autonomy_level"],
            "blessings": report["blessings"],
            "drafts_queued": report["draft_cycles_completed"],
            "human_overrides": report["human_overrides"],
            "violations_caught": report["errors_caught"],
            "auto_send_enabled": report["auto_send_enabled"],
        }


if __name__ == "__main__":
    import tempfile

    print("=" * 80)
    print("MYTHARA SALES BOT — PUBLIC INTERFACE (draft-only)")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmp:
        bot = PublicSalesBotInterface(queue_dir=Path(tmp) / "queue")

        email = {
            "subject": "Re: Mythara Demo",
            "body": "This looks interesting. Can we schedule a call?",
            "prospect_email": "demo@example.com",
        }

        print("\n📧 Processing email (governance running, draft-only):\n")
        result = bot.process_email(email)

        print(f"Draft: {result['draft'][:100]}...")
        print(f"\nStatus: {result['status']}")
        print(f"Sent: {result['sent']}")
        print(f"Queue: {result['queue_path']}")
        print(f"Action: {result['action_taken']}")
        print(f"Messenger: {result['messenger']}")
        print(f"\nGovernance Summary:")
        print(f"  Intent: {result['governance_summary']['intent']}")
        print(f"  Autonomy: {result['governance_summary']['autonomy_level']} (decisions + drafts only)")
        print(f"  Blessings: {result['governance_summary']['blessings']}/100")
        print(f"  Violations: {result['governance_summary']['violations']}")
        print(f"  Hash: {result['governance_summary']['hash'][:16]}...")

    print("\n" + "=" * 80)
    print("✅ Draft queued for Herb's approval — nothing was sent")
    print("=" * 80)
