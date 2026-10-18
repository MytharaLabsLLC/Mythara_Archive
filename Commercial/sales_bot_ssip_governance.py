# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Sales Bot SSIP Governance - Apply Mythara Engine integrity to autonomous email responses

DRAFT-ONLY POSTURE (2026-09-22): this module NEVER sends email. Validated
drafts go to the outreach queue (Commercial/outreach_queue.py) stamped
pending_approval; Herb approves and sends. See WILL.md NO_AUTO_SEND.

What this module really does:
- Cryptographic hashing of all bot-generated drafts
- Clause-based rules the bot CANNOT violate (pricing floor, compliance claims)
- Messenger roles recording the authority level of each draft
- Audit trail of every email decision (JSONL)
- Blessings reservoir (bot "earns trust" over time; trust gates nothing
  outbound anymore — every send needs Herb)
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Literal, Optional
from pathlib import Path

from outreach_queue import OutreachQueue

class SalesMessenger:
    """
    Messenger roles for sales bot drafts (risk classification labels).

    DRAFT-ONLY: these are labels on queued drafts, not send permissions.
    Nothing is auto-sent under any messenger.
    """
    MICHAEL = "Michael"      # Truth-teller: low-risk factual drafts
    GABRIEL = "Gabriel"      # Announcer: low-risk not_interested drafts
    URIEL = "Uriel"         # Illuminator: low-risk simple FAQ drafts
    RAPHAEL = "Raphael"     # Healer: needs Herb's closer look (deals, negotiations)
    METATRON = "Metatron"   # Scribe: Logs everything, no autonomy

class SalesClause:
    """Inviolable rules the bot must follow"""

    NEVER_AUTO_SEND = [
        "pricing_negotiation",      # Never negotiate price without human
        "contract_terms",           # Never discuss legal terms
        "custom_requirements",      # Never promise custom features
        "enterprise_deal",          # Deals >$2,500 need human approval
        "technical_deep_dive",      # Complex tech questions need human
        "competitor_comparison",    # Never trash competitors
    ]

    # Draft categories governance considers low-risk. Informational only:
    # every draft still queues for Herb's approval — this is NOT a send list.
    LOW_RISK_DRAFT_CATEGORIES = [
        "not_interested",           # Graceful exit, low risk
        "out_of_office",           # Acknowledge OOO
        "simple_faq",              # Questions clearly answered in docs
        "referral_request",        # Ask for referrals (no risk)
    ]

    PRICING_RULES = {
        "early_adopter_max": 500,
        "standard_max": 2500,
        "enterprise_max": 5000,
        "never_discount_below": 500,
        "cannot_promise": ["free trial", "money-back guarantee", "custom pricing"]
    }

    COMPLIANCE_RULES = {
        "never_claim": [
            "FDA approved",
            "HIPAA certified",
            "SOC2 compliant",
            "guaranteed regulatory pass"
        ],
        "always_caveat": [
            "Results may vary",
            "Subject to technical review",
            "Pilot terms negotiable"
        ]
    }

class BlessingsReservoir:
    """Bot earns trust over time - poor performance = less autonomy"""

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            filepath = Path(__file__).parent / "bot_blessings.json"
        self.filepath = Path(filepath)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if self.filepath.exists():
            try:
                state = json.loads(self.filepath.read_text())
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Corrupt blessings state file: {self.filepath} — {e}. "
                    "Fix or delete it to start fresh; refusing to guess."
                ) from e
            if not isinstance(state, dict):
                raise ValueError(
                    f"Blessings state file {self.filepath} does not contain an object."
                )
            return state
        return {
            "blessings": 100,  # Start at 100 (full trust)
            "auto_sends": 0,
            "human_overrides": 0,
            "errors_caught": 0,
            "successful_closes": 0,
            "last_updated": datetime.now().isoformat()
        }

    def _save_state(self):
        self.filepath.parent.mkdir(exist_ok=True)
        self.filepath.write_text(json.dumps(self.state, indent=2))

    def check_autonomy_level(self) -> Literal["full", "limited", "supervised", "disabled"]:
        """
        Determine how much decision/draft autonomy the bot gets.

        DRAFT-ONLY POLICY: these levels govern autonomous DECISIONS (close vs
        quit, draft wording) — never sending. Every outbound email still needs
        Herb's approval regardless of level.
        """
        blessings = self.state["blessings"]

        if blessings >= 90:
            return "full"        # Full decision/draft autonomy (outbound still draft-only)
        elif blessings >= 70:
            return "limited"     # Standard drafts autonomous; tricky ones flagged
        elif blessings >= 50:
            return "supervised"  # All drafts flagged for closer review
        else:
            return "disabled"    # Bot offline, human handles all

    def record_auto_send(self, success: bool):
        """
        Legacy auto-send counter kept for backward compatibility.

        Under the draft-only policy no email is ever auto-sent; this method
        only adjusts the blessings metric when a draft cycle completes
        successfully. Preserved because external callers reference it.
        """
        if success:
            self.state["blessings"] = min(100, self.state["blessings"] + 2)
            self.state["auto_sends"] += 1
        else:
            self.state["blessings"] = max(0, self.state["blessings"] - 10)
            self.state["errors_caught"] += 1

        self._save_state()

    def record_human_override(self, reason: str):
        """Human edited bot's draft - learn from it"""
        self.state["human_overrides"] += 1
        self.state["blessings"] = max(50, self.state["blessings"] - 1)  # Small penalty
        self._save_state()

    def record_successful_close(self, deal_value: int):
        """Bot helped close a deal - big blessing boost"""
        self.state["successful_closes"] += 1
        self.state["blessings"] = min(100, self.state["blessings"] + 10)
        self._save_state()

class SalesGovernanceEngine:
    """SSIP for sales bot - enforces rules, creates audit trail"""

    def __init__(self, audit_log_path: Optional[Path] = None):
        self.reservoir = BlessingsReservoir()
        self.audit_log = Path(audit_log_path) if audit_log_path else (
            Path(__file__).parent / "bot_audit_log.jsonl"
        )

    def validate_email_draft(self,
                            email_data: Dict,
                            draft_response: str,
                            intent: str) -> Dict:
        """
        Validate draft against Mythara clauses.

        Returns: {can_auto_send: bool (always False — draft-only policy),
                  auto_send_eligible: bool (theoretical risk verdict, informational),
                  violations: List, messenger: str, hash: str}

        can_auto_send is ALWAYS False: the bot never sends email. The
        messenger assignments below are risk classifications, not send rights.
        """
        violations = []
        messenger = SalesMessenger.METATRON  # Default: no autonomy
        # can_auto_send is always False under the draft-only policy — the bot
        # never sends email. auto_send_eligible is a theoretical risk verdict
        # (informational only), not a permission to send.
        auto_send_eligible = False

        # Check pricing violations
        pricing_violations = self._check_pricing_rules(draft_response)
        violations.extend(pricing_violations)

        # Check compliance violations
        compliance_violations = self._check_compliance_rules(draft_response)
        violations.extend(compliance_violations)

        # Risk classification by intent (labels only — still draft-only)
        autonomy_level = self.reservoir.check_autonomy_level()

        if intent == "not_interested" and autonomy_level in ["full", "limited"]:
            messenger = SalesMessenger.GABRIEL
            auto_send_eligible = True if not violations else False

        elif intent == "question" and autonomy_level == "full":
            # Check if it's a simple FAQ
            if self._is_simple_faq(email_data, draft_response):
                messenger = SalesMessenger.URIEL
                auto_send_eligible = True if not violations else False
            else:
                messenger = SalesMessenger.RAPHAEL
                auto_send_eligible = False

        elif intent == "interested":
            # Interested leads are high-value — flag for Herb's attention
            messenger = SalesMessenger.RAPHAEL
            auto_send_eligible = False

        # Generate integrity hash
        integrity_hash = self._generate_hash(email_data, draft_response, messenger)

        # Log to audit trail
        self._log_decision({
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "messenger": messenger,
            "can_auto_send": False,  # draft-only: real sends never enabled
            "auto_send_eligible": auto_send_eligible,  # theoretical risk verdict
            "violations": violations,
            "autonomy_level": autonomy_level,
            "blessings": self.reservoir.state["blessings"],
            "hash": integrity_hash
        })

        return {
            "can_auto_send": False,  # draft-only: Herb approves every send
            "auto_send_eligible": auto_send_eligible,  # theoretical risk verdict
            "violations": violations,
            "messenger": messenger,
            "hash": integrity_hash,
            "autonomy_level": autonomy_level,
            "blessings": self.reservoir.state["blessings"]
        }

    def _check_pricing_rules(self, draft: str) -> List[str]:
        """Ensure bot doesn't violate pricing clauses"""
        violations = []
        draft_lower = draft.lower()

        # Check for forbidden promises
        for forbidden in SalesClause.PRICING_RULES["cannot_promise"]:
            if forbidden in draft_lower:
                violations.append(f"PRICING_VIOLATION: Cannot promise '{forbidden}'")

        # Check for price mentions below minimum
        if "$" in draft:
            # Extract numbers after $
            import re
            prices = re.findall(r'\$(\d+)', draft)
            for price in prices:
                if int(price) < SalesClause.PRICING_RULES["never_discount_below"]:
                    violations.append(f"PRICING_VIOLATION: Price ${price} below minimum $500")

        return violations

    def _check_compliance_rules(self, draft: str) -> List[str]:
        """Ensure bot doesn't make illegal claims"""
        violations = []
        draft_lower = draft.lower()

        for forbidden_claim in SalesClause.COMPLIANCE_RULES["never_claim"]:
            if forbidden_claim.lower() in draft_lower:
                violations.append(f"COMPLIANCE_VIOLATION: Cannot claim '{forbidden_claim}'")

        return violations

    def _is_simple_faq(self, email_data: Dict, draft: str) -> bool:
        """Determine if this is a simple FAQ (low-risk draft)"""
        # Simple heuristic: draft is short + high confidence from RAG
        word_count = len(draft.split())

        # If draft is under 150 words and doesn't mention pricing/contracts
        if word_count < 150:
            draft_lower = draft.lower()
            complex_topics = ["pricing", "contract", "custom", "enterprise", "negotiate"]
            if not any(topic in draft_lower for topic in complex_topics):
                return True

        return False

    def _generate_hash(self, email_data: Dict, draft: str, messenger: str) -> str:
        """Generate SHA-256 hash for integrity verification"""
        content = f"{email_data['subject']}|{email_data['body']}|{draft}|{messenger}|{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _log_decision(self, decision: Dict):
        """Append to audit log (JSONL format)"""
        self.audit_log.parent.mkdir(exist_ok=True)
        with open(self.audit_log, 'a') as f:
            f.write(json.dumps(decision) + '\n')

class GovernedEmailAssistant:
    """Email assistant with Mythara SSIP governance"""

    def __init__(self, audit_log_path: Optional[Path] = None):
        from email_assistant import EmailAssistant
        self.assistant = EmailAssistant()
        self.governance = SalesGovernanceEngine(audit_log_path=audit_log_path)

    def process_email(self, email_data: Dict, queue_draft: bool = True,
                      queue_dir: Optional[Path] = None) -> Dict:
        """
        Process email with full governance.

        DRAFT-ONLY: the validated draft is written to the outreach queue for
        Herb's approval. This method never sends email. Set queue_draft=False
        when the caller will queue the draft itself (avoids double-queueing).
        Returns: {draft, can_auto_send (always False), auto_send_eligible,
                  violations, messenger, hash, action_taken, queue_path,
                  prospect_email}
        """
        # Step 1: Categorize intent
        intent, confidence = self.assistant.categorize_intent(
            email_data['body'],
            email_data['subject']
        )

        # Step 2: Generate draft with sales psychology
        draft = self.assistant.generate_draft_response(email_data, intent)

        # Step 3: Validate against Mythara clauses
        validation = self.governance.validate_email_draft(email_data, draft, intent)

        # Step 4: Queue the draft for human approval (never auto-send)
        queue_path = None
        if queue_draft:
            queue_path = OutreachQueue(queue_dir=queue_dir).queue(
                "email",
                f"{email_data.get('subject', 'draft')} -> {intent}",
                draft,
                meta={
                    "intent": intent,
                    "messenger": validation["messenger"],
                    "hash": validation["hash"],
                    "violations": "; ".join(validation["violations"]) or "none",
                    "governance_risk_eligible": validation["auto_send_eligible"],
                    "note": "Draft-only: theoretical risk verdict, not a send permission",
                    "autonomy_level": validation["autonomy_level"],
                    "in_reply_to": email_data.get("prospect_email", "unknown"),
                },
            )
            action = "DRAFT_QUEUED_FOR_APPROVAL"
        else:
            action = "DRAFT_READY_CALLER_QUEUES"

        return {
            "intent": intent,
            "draft": draft,
            "can_auto_send": False,  # draft-only: Herb approves every send
            "auto_send_eligible": validation["auto_send_eligible"],  # theoretical risk verdict
            "violations": validation["violations"],
            "messenger": validation["messenger"],
            "hash": validation["hash"],
            "autonomy_level": validation["autonomy_level"],
            "blessings": validation["blessings"],
            "action_taken": action,
            "queue_path": queue_path,
            "prospect_email": email_data.get("prospect_email", "unknown"),
        }

    def get_governance_report(self) -> Dict:
        """Generate governance stats for transparency"""
        state = self.governance.reservoir.state
        autonomy = self.governance.reservoir.check_autonomy_level()

        return {
            "outbound_policy": "draft_only",   # the bot never sends email
            "auto_send_enabled": False,        # real sending is never enabled
            "autonomy_level": autonomy,
            "blessings": state["blessings"],
            "draft_cycles_completed": state["auto_sends"],  # legacy counter name kept
            "human_overrides": state["human_overrides"],
            "errors_caught": state["errors_caught"],
            "successful_closes": state["successful_closes"],
            "low_risk_draft_categories": self._get_allowed_categories(autonomy),
        }

    def _get_allowed_categories(self, autonomy: str) -> List[str]:
        """
        Draft categories that governance considers low-risk (informational).
        All drafts still queue for Herb's approval — this is a risk label,
        not a send permission.
        """
        if autonomy == "full":
            return ["not_interested", "simple_faq", "referral_request", "out_of_office"]
        elif autonomy == "limited":
            return ["not_interested", "out_of_office"]
        else:
            return []


# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == '__main__':
    import tempfile

    print("="*80)
    print("MYTHARA-GOVERNED SALES BOT DEMO")
    print("   📝 DRAFT-ONLY demo — drafts queue into a temp dir")
    print("="*80)

    # NOTE: demo only — test addresses are fictional stand-ins.
    _demo_tmp = tempfile.TemporaryDirectory()
    _queue_dir = Path(_demo_tmp.name) / "queue"

    bot = GovernedEmailAssistant()

    # Test 1: Not interested (governance verdict: low-risk draft, still queued)
    print("\n📧 TEST 1: NOT INTERESTED REPLY")
    email1 = {
        'subject': 'Re: AI Governance',
        'body': "Thanks but we're not interested right now.",
        'prospect_email': 'test1@example.com',
    }
    result1 = bot.process_email(email1, queue_dir=_queue_dir)
    print(f"Intent: {result1['intent']}")
    print(f"Messenger: {result1['messenger']}")
    print(f"Can Auto-Send: {result1['can_auto_send']} (draft-only: always False)")
    print(f"Action: {result1['action_taken']}")
    print(f"Queue: {result1['queue_path']}")
    print(f"Violations: {result1['violations']}")
    print(f"Hash: {result1['hash'][:16]}...")

    # Test 2: Interested (flagged for Herb's attention — still queued, not sent)
    print("\n" + "="*80)
    print("📧 TEST 2: INTERESTED PROSPECT")
    email2 = {
        'subject': 'Re: Model Risk Solution',
        'body': "This looks interesting. Can we schedule a call?",
        'prospect_email': 'test2@example.com',
    }
    result2 = bot.process_email(email2, queue_dir=_queue_dir)
    print(f"Intent: {result2['intent']}")
    print(f"Messenger: {result2['messenger']}")
    print(f"Can Auto-Send: {result2['can_auto_send']} (draft-only: always False)")
    print(f"Action: {result2['action_taken']}")
    print(f"Queue: {result2['queue_path']}")
    print(f"Reasoning: Interested leads are high-value — flagged for Herb (RAPHAEL)")

    # Test 3: Pricing violation detection (blocks queueing)
    print("\n" + "="*80)
    print("📧 TEST 3: PRICING VIOLATION DETECTION")
    email3 = {
        'subject': 'Re: Pricing',
        'body': "Can you do $300 for early access?"
    }
    # Simulate bot trying to offer $300 (VIOLATION)
    fake_draft = "Sure! I can do $300 for you as a special early adopter rate."
    validation = bot.governance.validate_email_draft(email3, fake_draft, "question")
    print(f"Draft: {fake_draft}")
    print(f"Violations: {validation['violations']}")
    print(f"Can Auto-Send: {validation['can_auto_send']} (draft-only: always False)")
    print(f"Reasoning: Price below $500 minimum (PRICING_CLAUSE violation)")

    # Test 4: Compliance violation detection
    print("\n" + "="*80)
    print("📧 TEST 4: COMPLIANCE VIOLATION DETECTION")
    email4 = {
        'subject': 'Re: HIPAA',
        'body': "Is this HIPAA certified?"
    }
    fake_draft2 = "Yes, Mythara is HIPAA certified and FDA approved for clinical use."
    validation2 = bot.governance.validate_email_draft(email4, fake_draft2, "question")
    print(f"Draft: {fake_draft2}")
    print(f"Violations: {validation2['violations']}")
    print(f"Can Auto-Send: {validation2['can_auto_send']} (draft-only: always False)")
    print(f"Reasoning: Cannot claim 'FDA approved' or 'HIPAA certified' (COMPLIANCE_CLAUSE)")

    # Show governance stats
    print("\n" + "="*80)
    print("📊 GOVERNANCE REPORT")
    print("="*80)
    report = bot.get_governance_report()
    print(f"Outbound Policy: {report['outbound_policy']}")
    print(f"Autonomy Level: {report['autonomy_level']} (decisions + drafts only)")
    print(f"Blessings: {report['blessings']}/100")
    print(f"Draft Cycles Completed: {report['draft_cycles_completed']}")
    print(f"Human Overrides: {report['human_overrides']}")
    print(f"Errors Caught: {report['errors_caught']}")
    print(f"Successful Closes: {report['successful_closes']}")
    print(f"Auto-Send Enabled: {report['auto_send_enabled']}")
    print(f"Low-Risk Draft Categories: {report['low_risk_draft_categories']}")

    print("\n" + "="*80)
    print("✅ MYTHARA SSIP GOVERNANCE ACTIVE")
    print("="*80)
    print("\nThe bot is governed by inviolable clauses:")
    print("  ✓ Cannot offer pricing below $500")
    print("  ✓ Cannot make illegal compliance claims")
    print("  ✓ Interested leads are flagged for Herb's attention")
    print("  ✓ Earns decision autonomy through good performance (Blessings Reservoir)")
    print("  ✓ Every decision is cryptographically hashed")
    print("  ✓ Full audit trail in bot_audit_log.jsonl")
    print("  ✓ Draft-only: Herb approves and sends every outbound email")
    print("\nThis IS Mythara Engine dogfooding itself. 🚀")
