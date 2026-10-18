# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Real tests for the sales bot stack.

Non-negotiables under test:
- Outreach is DRAFT-ONLY. Every "send" path must queue a pending_approval
  draft through outreach_queue.py and never auto-send.
- Generated copy must not contain fabricated claims (invented customers,
  slot counts, deadlines, regulatory events, price windows, outcomes).

All tests run in temporary directories — no production state is touched.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from outreach_queue import OutreachQueue  # noqa: E402
from sales_bot_ssip_governance import (  # noqa: E402
    GovernedEmailAssistant,
    BlessingsReservoir,
    SalesGovernanceEngine,
)
from autonomous_sales_bot import AutonomousSalesBot  # noqa: E402
from sales_bot_with_soul import (  # noqa: E402
    SalesBotWithSoul,
    DealMakerPersonality,
)
from sales_bot_public_interface import PublicSalesBotInterface  # noqa: E402
import obfuscate_sales_bot as obfuscator  # noqa: E402

# Phrases that must never appear in generated or template copy.
BANNED_PHRASES = [
    "3 other banks in your region",
    "competitor [COMPETITOR]",
    "2 health systems",
    "5 other VPs",
    "2 slots left",
    "slots remaining",
    "waitlist through Q1",
    "pricing expires Friday",
    "expires Friday",
    "commit by Friday",
    "normally $2,500",
    "reg. $2,500",
    "zero findings",
    "Fed guidance just dropped",
    "passed their AI safety reviews",
    "worked with 3 VPs",
    "3 companies pass",
    "3 peer institutions",
    "200 hours to 20 hours",
    "same standard used by Federal Reserve's FedNow",
    "same cryptographic standard the VA uses",
    "OCC-style validation report",
    "FDA-style validation report",
    "nobody's breaking it",
]


def make_tmp():
    tmp = tempfile.TemporaryDirectory()
    base = Path(tmp.name)
    return tmp, base


class TestGovernanceDraftOnly(unittest.TestCase):
    def test_process_email_queues_draft_never_sends(self):
        tmp, base = make_tmp()
        try:
            bot = GovernedEmailAssistant(
                audit_log_path=base / "audit.jsonl"
            )
            email = {
                "subject": "Re: AI Governance",
                "body": "Thanks but we're not interested right now.",
                "prospect_email": "prospect@example.com",
            }
            result = bot.process_email(email, queue_dir=base / "queue")

            self.assertFalse(result["can_auto_send"])
            self.assertEqual(result["action_taken"], "DRAFT_QUEUED_FOR_APPROVAL")
            self.assertIsNotNone(result["queue_path"])
            self.assertTrue(Path(result["queue_path"]).exists())

            text = Path(result["queue_path"]).read_text()
            self.assertIn("pending_approval", text)
            # exactly one draft file queued
            self.assertEqual(len(list((base / "queue").glob("*.md"))), 1)
        finally:
            tmp.cleanup()

    def test_queue_draft_false_does_not_double_queue(self):
        tmp, base = make_tmp()
        try:
            bot = GovernedEmailAssistant(
                audit_log_path=base / "audit.jsonl"
            )
            email = {"subject": "Hi", "body": "This looks interesting."}
            result = bot.process_email(
                email, queue_draft=False, queue_dir=base / "queue"
            )
            self.assertEqual(result["action_taken"], "DRAFT_READY_CALLER_QUEUES")
            self.assertIsNone(result["queue_path"])
            self.assertFalse((base / "queue").exists())
        finally:
            tmp.cleanup()

    def test_governance_report_is_draft_only(self):
        tmp, base = make_tmp()
        try:
            bot = GovernedEmailAssistant(
                audit_log_path=base / "audit.jsonl"
            )
            report = bot.get_governance_report()
            self.assertEqual(report["outbound_policy"], "draft_only")
            self.assertFalse(report["auto_send_enabled"])
        finally:
            tmp.cleanup()

    def test_pricing_violation_blocks_and_never_sends(self):
        bot = SalesGovernanceEngine(audit_log_path=Path(tempfile.mkdtemp()) / "a.jsonl")
        validation = bot.validate_email_draft(
            {"subject": "x", "body": "y"},
            "Sure! I can do $300 for you as a special early adopter rate.",
            "question",
        )
        self.assertTrue(validation["violations"])
        self.assertFalse(validation["can_auto_send"])


class TestAutonomousBot(unittest.TestCase):
    def test_interested_queues_single_draft(self):
        tmp, base = make_tmp()
        try:
            bot = AutonomousSalesBot(
                full_autonomy=True,
                queue_dir=base / "queue",
                state_dir=base / "state",
            )
            email = {
                "subject": "Re: Model Risk Solution",
                "body": "This looks interesting. Can we schedule a call?",
                "prospect_email": "lead@example.com",
            }
            result = bot.process_email_autonomously(email)

            self.assertTrue(result["queued"])
            self.assertFalse(result.get("sent", False))
            self.assertIn("queue_path", result)
            self.assertEqual(
                result["autonomous_decision"]["action"], "QUEUE_DRAFT"
            )
            drafts = list((base / "queue").glob("*.md"))
            self.assertEqual(len(drafts), 1, "expected exactly one queued draft")
            self.assertIn("pending_approval", drafts[0].read_text())
        finally:
            tmp.cleanup()

    def test_three_nos_queues_final_quit(self):
        tmp, base = make_tmp()
        try:
            bot = AutonomousSalesBot(
                full_autonomy=True,
                queue_dir=base / "queue",
                state_dir=base / "state",
            )
            email = {
                "subject": "Re: Mythara",
                "body": "Not interested right now, thanks.",
                "prospect_email": "cold@example.com",
            }
            last = None
            for _ in range(3):
                last = bot.process_email_autonomously(email)

            self.assertEqual(
                last["autonomous_decision"]["action"], "QUEUE_FINAL_QUIT"
            )
            self.assertTrue(last["queued"])
            self.assertIn("cold@example.com", bot.quarterly_cycle["quit_list"])
            # one draft per no
            self.assertEqual(len(list((base / "queue").glob("*.md"))), 3)
        finally:
            tmp.cleanup()

    def test_quarterly_reengagement_queues_draft(self):
        tmp, base = make_tmp()
        try:
            bot = AutonomousSalesBot(
                full_autonomy=True,
                queue_dir=base / "queue",
                state_dir=base / "state",
            )
            # seed a quit prospect whose recontact date is in the past
            bot._add_to_quarterly_cycle("old@example.com", "Not interested")
            entry = bot.quarterly_cycle["quit_list"]["old@example.com"]
            entry["recontact_date"] = "2020-01-01T00:00:00"
            entry["quit_date"] = "2019-10-01T00:00:00"
            bot.run_quarterly_cycle()

            drafts = list((base / "queue").glob("*.md"))
            self.assertEqual(len(drafts), 1)
            text = drafts[0].read_text()
            self.assertIn("pending_approval", text)
            for banned in ["Fed guidance just dropped", "normally $2,500"]:
                self.assertNotIn(banned, text)
        finally:
            tmp.cleanup()

    def test_corrupt_learning_state_fails_honestly(self):
        tmp, base = make_tmp()
        try:
            bad = base / "bad.json"
            bad.write_text("{not valid json")
            from autonomous_sales_bot import AdaptiveLearningEngine
            with self.assertRaises(ValueError) as ctx:
                AdaptiveLearningEngine(filepath=bad)
            self.assertIn("Corrupt", str(ctx.exception))
        finally:
            tmp.cleanup()


class TestSoulBot(unittest.TestCase):
    def test_soul_bot_queues_draft_never_sends(self):
        tmp, base = make_tmp()
        try:
            bot = SalesBotWithSoul(full_autonomy=True, queue_dir=base / "queue")
            email = {
                "subject": "Re: Model Risk Solution",
                "body": "This looks interesting. Can we schedule a call?",
                "prospect_email": "lead@example.com",
            }
            draft = bot.generate_soulful_response(
                email, "interested", queue_dir=base / "queue"
            )
            self.assertTrue(draft)
            drafts = list((base / "queue").glob("*.md"))
            self.assertEqual(len(drafts), 1)
            self.assertIn("pending_approval", drafts[0].read_text())
        finally:
            tmp.cleanup()

    def test_no_banned_fabricated_phrases_in_templates(self):
        texts = []
        texts.extend(DealMakerPersonality.COMPETITIVE_PRESSURE)
        texts.extend(DealMakerPersonality.SCARCITY_TACTICS)
        texts.extend(DealMakerPersonality.EMPATHY_WITH_URGENCY)
        texts.extend(DealMakerPersonality.DRAMATIZE_PAIN)
        for counters in DealMakerPersonality.OBJECTION_COUNTERS.values():
            texts.extend(counters)

        bot = SalesBotWithSoul(full_autonomy=False, queue_dir=Path(tempfile.mkdtemp()))
        # generate every template variant and scan the output too
        probe = {"subject": "Re: probe", "body": "probe", "prospect_email": "p@example.com"}
        for industry in ("banking", "healthcare", "tech"):
            for intent in ("interested", "question", "not_interested", "unknown"):
                texts.append(bot._handle_interested_with_soul(probe, industry)
                             if intent == "interested"
                             else bot._handle_question_with_soul(probe, industry)
                             if intent == "question"
                             else bot._handle_no_with_soul(probe, industry)
                             if intent == "not_interested"
                             else bot._handle_unknown_with_soul(probe, industry))

        for text in texts:
            for banned in BANNED_PHRASES:
                self.assertNotIn(
                    banned, text,
                    f"banned fabricated phrase found: {banned!r}\n---\n{text[:300]}",
                )

    def test_soul_validation_never_auto_sends(self):
        bot = SalesBotWithSoul(full_autonomy=False, queue_dir=Path(tempfile.mkdtemp()))
        validation = bot._validate_with_mythara(
            "A plain draft with no violations.",
            {"subject": "x", "body": "y"},
        )
        self.assertFalse(validation["can_auto_send"])


class TestPublicInterface(unittest.TestCase):
    def test_process_email_returns_draft_only_metadata(self):
        tmp, base = make_tmp()
        try:
            bot = PublicSalesBotInterface(
                queue_dir=base / "queue",
                audit_log_path=base / "audit.jsonl",
            )
            result = bot.process_email({
                "subject": "Re: Demo",
                "body": "This looks interesting. Can we schedule a call?",
                "prospect_email": "demo@example.com",
            })
            self.assertEqual(result["status"], "pending_approval")
            self.assertFalse(result["sent"])
            self.assertFalse(result["can_auto_send"])
            self.assertTrue(Path(result["queue_path"]).exists())
        finally:
            tmp.cleanup()

    def test_audit_log_newest_first_skips_corrupt_lines(self):
        tmp, base = make_tmp()
        try:
            log = base / "audit.jsonl"
            log.write_text(
                '{"a": 1}\nnot json\n{"a": 2}\n',
            )
            bot = PublicSalesBotInterface(
                queue_dir=base / "queue", audit_log_path=log
            )
            entries = bot.get_audit_log()
            self.assertEqual([e["a"] for e in entries], [2, 1])
        finally:
            tmp.cleanup()


class TestObfuscator(unittest.TestCase):
    def test_preflight_runs_without_pyarmor(self):
        report = obfuscator.preflight()
        self.assertIn("pyarmor_found", report)
        self.assertIn("files", report)
        for name, present in report["files"].items():
            self.assertTrue(present, f"expected source file present: {name}")

    def test_dry_run_does_not_touch_filesystem(self):
        tmp, base = make_tmp()
        try:
            result = obfuscator.obfuscate_sales_bot(
                output_dir=base / "dist", dry_run=True
            )
            self.assertTrue(result["ok"])
            self.assertFalse((base / "dist").exists())
        finally:
            tmp.cleanup()


class TestBlessingsState(unittest.TestCase):
    def test_corrupt_blessings_state_fails_honestly(self):
        tmp, base = make_tmp()
        try:
            bad = base / "blessings.json"
            bad.write_text("nope{")
            with self.assertRaises(ValueError) as ctx:
                BlessingsReservoir(filepath=bad)
            self.assertIn("Corrupt", str(ctx.exception))
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
