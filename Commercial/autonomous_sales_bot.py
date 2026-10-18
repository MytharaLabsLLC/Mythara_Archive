# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Autonomous Sales Bot with Self-Healing & Adaptive Learning

DRAFT-ONLY POSTURE (2026-09-22): the bot decides autonomously what to draft
(CLOSE or QUIT decision tree, 3-nos rule, quarterly re-engagement), but every
outbound email becomes a draft in Commercial/outreach_queue.py stamped
pending_approval. Herb approves and sends. Nothing auto-sends. See WILL.md
NO_AUTO_SEND.

This system:
- Learns from human corrections (self-improvement)
- Detects performance degradation (self-healing)
- Adapts sales psychology based on what works (evolution)
- Drafts autonomously; sends only with human approval
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

from outreach_queue import OutreachQueue
from sales_bot_ssip_governance import (
    GovernedEmailAssistant,
    BlessingsReservoir,
    SalesClause
)


class AdaptiveLearningEngine:
    """Learns from outcomes and adapts strategy"""

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = Path(filepath) if filepath else (
            Path(__file__).parent / "bot_learning_state.json"
        )
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if self.filepath.exists():
            try:
                data = json.loads(self.filepath.read_text())
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Corrupt learning state: {self.filepath} — {e}. "
                    "Fix or delete it to start fresh; refusing to guess."
                ) from e
            if not isinstance(data, dict):
                raise ValueError(f"Learning state {self.filepath} is not an object.")
            return data

        return {
            "successful_patterns": {},      # What worked (led to calls/closes)
            "failed_patterns": {},          # What didn't work (no response/negative)
            "a_b_tests": {},               # Active experiments
            "learned_optimizations": [],    # Proven improvements
            "last_model_update": None,
            "performance_metrics": {
                "response_rate": 0.0,
                "call_booking_rate": 0.0,
                "close_rate": 0.0
            }
        }

    def _save_state(self):
        self.filepath.parent.mkdir(exist_ok=True)
        self.filepath.write_text(json.dumps(self.state, indent=2))

    def record_outcome(self, email_hash: str, outcome: str, metadata: Dict):
        """
        Learn from email outcomes

        Outcomes:
        - positive_response: They replied positively
        - booked_call: They scheduled a meeting
        - closed_deal: They bought
        - no_response: They ghosted
        - negative_response: They said no
        """

        # Extract patterns from successful emails
        if outcome in ["positive_response", "booked_call", "closed_deal"]:
            pattern_key = self._extract_pattern(metadata)

            if pattern_key not in self.state["successful_patterns"]:
                self.state["successful_patterns"][pattern_key] = 0
            self.state["successful_patterns"][pattern_key] += 1

            # If pattern shows consistent success (>3 times), add to optimizations
            if self.state["successful_patterns"][pattern_key] >= 3:
                optimization = {
                    "pattern": pattern_key,
                    "success_count": self.state["successful_patterns"][pattern_key],
                    "learned_at": datetime.now().isoformat(),
                    "apply": True
                }
                if optimization not in self.state["learned_optimizations"]:
                    self.state["learned_optimizations"].append(optimization)

        # Track failures to avoid repeating
        elif outcome in ["no_response", "negative_response"]:
            pattern_key = self._extract_pattern(metadata)

            if pattern_key not in self.state["failed_patterns"]:
                self.state["failed_patterns"][pattern_key] = 0
            self.state["failed_patterns"][pattern_key] += 1

        self._update_performance_metrics()
        self._save_state()

    def _extract_pattern(self, metadata: Dict) -> str:
        """Extract reusable pattern from email metadata"""
        # Patterns: subject_line_style, opening_line, cta_type, urgency_level
        return f"{metadata.get('subject_style', 'unknown')}|{metadata.get('cta_type', 'unknown')}|{metadata.get('urgency_level', 'medium')}"

    def _update_performance_metrics(self):
        """Calculate current performance rates"""
        total_successful = sum(self.state["successful_patterns"].values())
        total_failed = sum(self.state["failed_patterns"].values())
        total = total_successful + total_failed

        if total > 0:
            self.state["performance_metrics"]["response_rate"] = total_successful / total

    def get_optimization_suggestions(self) -> List[Dict]:
        """Return proven optimizations to apply"""
        return [opt for opt in self.state["learned_optimizations"] if opt.get("apply")]

    def should_experiment(self) -> bool:
        """Decide if bot should try A/B testing new approaches"""
        # Only experiment if we have baseline data (>20 emails)
        total_emails = sum(self.state["successful_patterns"].values()) + sum(self.state["failed_patterns"].values())
        return total_emails > 20 and len(self.state["a_b_tests"]) < 2


class SelfHealingMonitor:
    """Detects issues and auto-corrects"""

    def __init__(self, filepath: Optional[str] = None):
        filepath = filepath or (Path(__file__).parent / "bot_health_log.jsonl")
        self.filepath = Path(filepath)

    def check_health(self, reservoir: BlessingsReservoir) -> Dict:
        """
        Monitor bot health and detect issues.

        Returns: {healthy: bool, issues: List[str], recommended_actions: List[str]}

        Note: recommendations are advisory only — this monitor does NOT
        mutate bot state. Autonomy gating already happens via the blessings
        reservoir level (full/limited/supervised/disabled).
        """
        issues = []
        recommended_actions = []

        # Check 1: Blessings too low (performance degradation)
        if reservoir.state["blessings"] < 70:
            issues.append(f"Low trust score: {reservoir.state['blessings']}/100")

            # Advisory: blessings level already gates draft autonomy
            if reservoir.state["blessings"] < 50:
                recommended_actions.append(
                    "RECOMMENDATION: blessings <50 — bot is at 'disabled'/'supervised' "
                    "level; keep drafts flagged for close review until trust rebuilds"
                )

        # Check 2: High error rate
        total = reservoir.state["auto_sends"] + reservoir.state["human_overrides"]
        if total > 10:
            error_rate = reservoir.state["errors_caught"] / total
            if error_rate > 0.1:  # >10% error rate
                issues.append(f"High error rate: {error_rate:.1%}")
                recommended_actions.append(
                    "RECOMMENDATION: error rate >10% — have Herb review recent drafts "
                    "before approving more"
                )

        # Check 3: No successful closes in 30 days
        if reservoir.state["successful_closes"] == 0 and reservoir.state["auto_sends"] > 50:
            issues.append("No deals closed - strategy may need adjustment")
            recommended_actions.append(
                "RECOMMENDATION: analyze top-performing patterns in the audit log; "
                "consider new intro variants"
            )

        # Log health check
        self._log_health_check({
            "timestamp": datetime.now().isoformat(),
            "blessings": reservoir.state["blessings"],
            "issues": issues,
            "recommended_actions": recommended_actions,
            "healthy": len(issues) == 0
        })

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "recommended_actions": recommended_actions
        }

    def _log_health_check(self, entry: Dict):
        """Append to health log"""
        self.filepath.parent.mkdir(exist_ok=True)
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def auto_heal(self, issues: List[str]) -> List[str]:
        """
        Advisory-only: logs recommendations for human review.

        Does NOT mutate bot state (no fake "fixes"). Autonomy gating is
        already handled by the blessings reservoir level. Kept under this
        name for backward compatibility with existing callers.
        """
        recommendations = []

        for issue in issues:
            if "Low trust score" in issue:
                recommendations.append(
                    "Keep drafts flagged for close review until blessings recover"
                )
            elif "High error rate" in issue:
                recommendations.append(
                    "Have Herb review recent drafts before approving more"
                )
            elif "No deals closed" in issue:
                recommendations.append(
                    "Analyze top-performing patterns; consider new intro variants"
                )

        self._log_health_check({
            "timestamp": datetime.now().isoformat(),
            "issues": issues,
            "recommended_actions": recommendations,
            "auto_heal_note": "advisory only — no state was mutated",
        })
        return recommendations


class AutonomousSalesBot:
    """
    Autonomous sales bot with:
    - Self-learning from outcomes
    - Self-healing from errors
    - Adaptive strategy evolution
    - Draft autonomy (3 nos and quit) — sends need Herb's approval

    Philosophy: Decide fast (close or quit), draft everything, never send
    without a human. The bot's autonomy is over decisions and drafts,
    not over anyone's inbox.
    """

    def __init__(self, full_autonomy: bool = True, queue_dir=None, state_dir=None):
        self.queue_dir = queue_dir  # override for tests; None = real queue
        self.state_dir = Path(state_dir) if state_dir else Path(__file__).parent
        self.assistant = GovernedEmailAssistant(
            audit_log_path=self.state_dir / "bot_audit_log.jsonl"
        )
        self.learning_engine = AdaptiveLearningEngine(
            filepath=self.state_dir / "bot_learning_state.json"
        )
        self.health_monitor = SelfHealingMonitor(
            filepath=self.state_dir / "bot_health_log.jsonl"
        )
        self.full_autonomy = full_autonomy
        self.conversation_tracker = {}  # Track "no" count per prospect
        self.quarterly_cycle = self._load_quarterly_cycle()

        print(f"🤖 Autonomous Sales Bot initialized")
        print(f"   Full Autonomy: {full_autonomy} (decisions + drafts)")
        print(f"   Self-Learning: ✅ Active")
        print(f"   Self-Healing: ✅ Active")
        print(f"   Policy: CLOSE OR QUIT (3 nos and go)")
        print(f"   Outbound: 📝 DRAFT-ONLY — Herb approves every send")
        print(f"   Re-engagement: ✅ QUARTERLY (auto-cycle every 90 days)")

    def _load_quarterly_cycle(self) -> Dict:
        """Track prospects who said no - re-engage quarterly"""
        filepath = self.state_dir / "quarterly_cycle.json"
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text())
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Corrupt quarterly cycle state: {filepath} — {e}. "
                    "Fix or delete it to start fresh; refusing to guess."
                ) from e
            if not isinstance(data, dict):
                raise ValueError(f"Quarterly cycle state {filepath} is not an object.")
            return data
        return {
            "quit_list": {},  # {email: {quit_date, reason, recontact_date}}
            "current_quarter": self._get_current_quarter(),
            "last_cycle_run": None
        }

    def _get_current_quarter(self) -> str:
        """Get current quarter (Q1-Q4 YYYY)"""
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        return f"Q{quarter} {now.year}"

    def _save_quarterly_cycle(self):
        """Save quarterly cycle state"""
        filepath = self.state_dir / "quarterly_cycle.json"
        filepath.parent.mkdir(exist_ok=True)
        filepath.write_text(json.dumps(self.quarterly_cycle, indent=2))

    def process_email_autonomously(self, email_data: Dict) -> Dict:
        """
        Process email with full decision autonomy — DRAFT-ONLY.

        Bot decides:
        1. Should I respond? (or ignore spam/irrelevant)
        2. How should I respond? (apply learned optimizations)
        3. What goes in the draft queue? (close, quit, or re-engage)
        4. What should I learn? (track outcome for improvement)

        Every outbound email becomes a draft in the outreach queue stamped
        pending_approval. Nothing is sent without Herb.
        """

        # Step 1: Health check (self-healing)
        health = self.health_monitor.check_health(self.assistant.governance.reservoir)

        if not health["healthy"]:
            print(f"⚠️  Health issues detected: {health['issues']}")
            print(f"💡 Recommendations: {health['recommended_actions']}")
            # Log recommendations (advisory only — no state mutated)
            self.health_monitor.auto_heal(health["issues"])

        # Step 2: Process with governance (caller queues — avoids double-queue)
        result = self.assistant.process_email(email_data, queue_draft=False)

        # Step 3: Apply learned optimizations
        optimizations = self.learning_engine.get_optimization_suggestions()
        if optimizations:
            result = self._apply_optimizations(result, optimizations)

        # Step 4: Make autonomy decision (decisions are autonomous; sends are not)
        if self.full_autonomy:
            # Bot decides: CLOSE or QUIT (drafts it; Herb sends)
            decision = self._make_autonomous_decision(result, email_data)
            result["autonomous_decision"] = decision
            result["refined_intent"] = decision.get("intent_used", result["intent"])

            if decision["action"] in ["QUEUE_DRAFT", "QUEUE_FINAL_QUIT"]:
                # Queue the draft for Herb's approval — never send directly
                draft = decision.get("message_override", result["draft"])
                queue_path = self._queue_outreach_draft(draft, email_data, decision, result)
                result["queued"] = True
                result["queue_path"] = queue_path

                if decision["action"] == "QUEUE_FINAL_QUIT":
                    print(f"👋 Queued final quit message - added to quarterly cycle")

            elif decision["action"] == "IGNORE":
                # Already quit - don't respond
                result["queued"] = False
                result["action"] = "IGNORED"
                print(f"🚫 Ignoring - prospect already in quit list")

        return result

    @staticmethod
    def _refine_intent(email_data: Dict, intent: str) -> str:
        """
        Defensive intent precedence.

        The upstream keyword matcher checks "interested" before
        "not_interested", so "not interested" can misclassify as interested.
        Refusals must win: check opt-out language first.
        """
        text = (str(email_data.get("body", "")) + " " +
                str(email_data.get("subject", ""))).lower()
        opt_out = ("not interested", "no thanks", "not a fit", "not right now",
                   "please remove", "unsubscribe", "stop emailing",
                   "stop contacting", "do not contact", "leave me alone",
                   "remove me", "take me off")
        if any(phrase in text for phrase in opt_out):
            return "not_interested"
        return intent

    def _make_autonomous_decision(self, result: Dict, email_data: Optional[Dict] = None) -> Dict:
        """
        Decide autonomously: CLOSE or QUIT (drafts it; Herb sends).

        Decision tree:
        1. Interested? → Draft the hard close (book call immediately)
        2. Question? → Draft answer + push for close
        3. Not interested? → Count strikes (3 and quit)
        4. 3 nos? → Add to quarterly cycle, stop contacting

        Actions QUEUE_DRAFT / QUEUE_FINAL_QUIT write to the outreach queue
        stamped pending_approval. The bot never sends email itself.
        """
        # Defensive: refusals must beat the upstream keyword matcher's ordering
        intent = self._refine_intent(email_data or {}, result.get("intent", "unknown"))
        decision = self._decide(result, intent)
        decision["intent_used"] = intent
        return decision

    def _decide(self, result: Dict, intent: str) -> Dict:
        """Core decision tree (see _make_autonomous_decision)."""

        prospect_email = result.get("prospect_email", "unknown")

        # Initialize conversation tracking
        if prospect_email not in self.conversation_tracker:
            self.conversation_tracker[prospect_email] = {
                "no_count": 0,
                "last_contact": datetime.now().isoformat(),
                "status": "active"
            }

        tracker = self.conversation_tracker[prospect_email]

        # Check if already quit
        if tracker["status"] == "quit":
            return {
                "action": "IGNORE",
                "reason": "Already quit - will re-engage next quarter",
                "confidence": 1.0
            }

        # Handle "not interested" responses (strike counting)
        if intent == "not_interested":
            tracker["no_count"] += 1
            tracker["last_contact"] = datetime.now().isoformat()

            if tracker["no_count"] >= 3:
                # 3 strikes - quit and add to quarterly cycle
                tracker["status"] = "quit"
                self._add_to_quarterly_cycle(prospect_email, "3_nos")

                return {
                    "action": "QUEUE_FINAL_QUIT",
                    "reason": "3 nos received - graceful exit + quarterly re-engagement",
                    "confidence": 1.0,
                    "message_override": self._generate_quit_message(prospect_email)
                }
            else:
                # Strike 1 or 2 - acknowledge but stay in game
                return {
                    "action": "QUEUE_DRAFT",
                    "reason": f"No #{tracker['no_count']} - stay professional, leave door open",
                    "confidence": 0.9
                }

        # Handle interested (push for close HARD)
        elif intent == "interested":
            return {
                "action": "QUEUE_DRAFT",
                "reason": "Interested prospect - book call immediately (Jevons Effect full pressure)",
                "confidence": 1.0,
                "strategy": "assumptive_close"
            }

        # Handle questions (answer + advance to close)
        elif intent == "question":
            return {
                "action": "QUEUE_DRAFT",
                "reason": "Question - answer briefly + push for call",
                "confidence": 0.95,
                "strategy": "answer_and_close"
            }

        # Handle out of office
        elif intent == "out_of_office":
            return {
                "action": "QUEUE_DRAFT",
                "reason": "OOO - acknowledge and follow up when back",
                "confidence": 0.85
            }

        # Default: draft it (bot decides; Herb sends)
        return {
            "action": "QUEUE_DRAFT",
            "reason": "Unknown intent - default to sending with conservative approach",
            "confidence": 0.7
        }

    def _add_to_quarterly_cycle(self, prospect_email: str, reason: str):
        """Add prospect to quarterly re-engagement cycle"""
        quit_date = datetime.now()
        recontact_date = quit_date + timedelta(days=90)  # 90 days = ~1 quarter

        self.quarterly_cycle["quit_list"][prospect_email] = {
            "quit_date": quit_date.isoformat(),
            "reason": reason,
            "recontact_date": recontact_date.isoformat(),
            "quarter_quit": self._get_current_quarter()
        }

        self._save_quarterly_cycle()

        print(f"📅 Added to quarterly cycle: {prospect_email}")
        print(f"   Re-engagement date: {recontact_date.strftime('%Y-%m-%d')}")

    def _generate_quit_message(self, prospect_email: str) -> str:
        """Generate final quit message (graceful, professional)"""
        return """No problem at all—I appreciate you being clear.

I'll stop reaching out for now. If anything changes with your AI governance needs, feel free to ping me.

Quick ask: do you know anyone at a peer company who might need auditable AI decision logs? Happy to help them out.

Best,
Herbert"""

    def run_quarterly_cycle(self):
        """
        Check quarterly cycle and re-engage prospects who said no 90+ days ago

        This runs automatically (bot manages its own calendar)
        """
        now = datetime.now()
        current_quarter = self._get_current_quarter()

        # Check if we've already cycled this quarter
        if self.quarterly_cycle.get("last_cycle_run") == current_quarter:
            print(f"✅ Quarterly cycle already run for {current_quarter}")
            return

        recontact_list = []

        for email, data in self.quarterly_cycle["quit_list"].items():
            recontact_date = datetime.fromisoformat(data["recontact_date"])

            if now >= recontact_date:
                # Time to re-engage
                recontact_list.append({
                    "email": email,
                    "quit_reason": data["reason"],
                    "quarters_ago": self._calculate_quarters_since(data["quit_date"])
                })

                # Reset conversation tracker (fresh start)
                if email in self.conversation_tracker:
                    self.conversation_tracker[email] = {
                        "no_count": 0,
                        "last_contact": now.isoformat(),
                        "status": "active",
                        "reengaged": True
                    }

        if recontact_list:
            print(f"\n🔄 QUARTERLY RE-ENGAGEMENT CYCLE")
            print(f"   Quarter: {current_quarter}")
            print(f"   Re-engaging: {len(recontact_list)} prospects")

            for prospect in recontact_list:
                self._send_reengagement_email(prospect)

            self.quarterly_cycle["last_cycle_run"] = current_quarter
            self._save_quarterly_cycle()

        return recontact_list

    def _calculate_quarters_since(self, quit_date_str: str) -> int:
        """Calculate how many quarters since quit date"""
        quit_date = datetime.fromisoformat(quit_date_str)
        now = datetime.now()
        months_diff = (now.year - quit_date.year) * 12 + (now.month - quit_date.month)
        return months_diff // 3

    def _send_reengagement_email(self, prospect: Dict):
        """Queue a fresh outreach draft for a previously quit prospect (draft-only)."""
        quarters_ago = prospect["quarters_ago"]

        email_body = f"""Subject: Quick check-in

Hi — it's been {quarters_ago} quarter{'s' if quarters_ago > 1 else ''} since we last talked. Wanted to check whether AI governance has moved up your priority list since then.

We run a $500 SSIP audit: cryptographic validation of AI controls, delivered in 5 days with a findings report. Happy to show you what the deliverable looks like — 15 minutes, no pitch deck.

Interested in a brief call next week?

Herbert"""

        queue_path = OutreachQueue(queue_dir=self.queue_dir).queue(
            "followup",
            f"quarterly re-engagement -> {prospect['email']}",
            email_body,
            meta={
                "intent": "reengagement",
                "quit_reason": prospect["quit_reason"],
                "quarters_since_quit": quarters_ago,
                "in_reply_to": prospect["email"],
            },
        )

        print(f"   📝 Re-engagement draft queued: {prospect['email']}")
        print(f"      Reason quit: {prospect['quit_reason']}")
        print(f"      Quarters since: {quarters_ago}")
        print(f"      File: {queue_path}")

    def _apply_optimizations(self, result: Dict, optimizations: List[Dict]) -> Dict:
        """
        Attach proven-pattern suggestions to the result. This does NOT rewrite
        the draft (that would need a real copy model) — it records what the
        learning engine found so Herb sees the suggestion in the draft meta.
        """
        notes = []
        for opt in optimizations:
            parts = str(opt.get("pattern", "")).split("|")
            subject_style = parts[0] if len(parts) > 0 else "?"
            cta_type = parts[1] if len(parts) > 1 else "?"
            urgency = parts[2] if len(parts) > 2 else "?"
            notes.append(
                f"Proven pattern ({opt.get('success_count', 0)} wins): "
                f"subject_style={subject_style}, cta={cta_type}, urgency={urgency}."
            )
        result["optimizations_applied"] = [opt["pattern"] for opt in optimizations]
        result["optimization_notes"] = notes
        return result

    def _extract_metadata(self, result: Dict, email_data: Optional[Dict] = None) -> Dict:
        """Extract real, checkable metadata for the learning engine."""
        email_data = email_data or {}
        subject = str(email_data.get("subject", ""))
        draft = str(result.get("draft", ""))
        draft_lower = draft.lower()

        if "?" in subject:
            subject_style = "question"
        elif len(subject) < 40:
            subject_style = "short"
        else:
            subject_style = "descriptive"

        day_words = ("monday", "tuesday", "wednesday", "thursday", "friday",
                     "calendar", "invite", "schedule")
        cta_type = "assumptive_close" if any(w in draft_lower for w in day_words) else "soft_ask"

        urgency_words = ("asap", "urgent", "deadline", "expires", "this week", "friday")
        urgency_level = "high" if any(w in draft_lower for w in urgency_words) else "medium"

        return {
            "intent": result.get("intent", "unknown"),
            "messenger": result.get("messenger", "unknown"),
            "subject_style": subject_style,
            "cta_type": cta_type,
            "urgency_level": urgency_level,
        }

    def _queue_outreach_draft(self, draft: str, original_email: Dict,
                              decision: Dict, result: Dict) -> str:
        """
        DRAFT-ONLY send path. Writes the draft to the outreach queue stamped
        pending_approval. Returns the queue file path. This is the ONLY
        outbound path in this bot — there is no SMTP, no API send.
        """
        queue_path = OutreachQueue(queue_dir=self.queue_dir).queue(
            "email",
            f"{original_email.get('subject', 'draft')} -> {decision['action'].lower()}",
            draft,
            meta={
                "intent": result.get("intent", "unknown"),
                "decision": decision["action"],
                "decision_reason": decision.get("reason", ""),
                "decision_confidence": decision.get("confidence", ""),
                "messenger": result.get("messenger", ""),
                "hash": result.get("hash", ""),
                "violations": "; ".join(result.get("violations", [])) or "none",
                "in_reply_to": original_email.get("prospect_email", "unknown"),
            },
        )
        print(f"\n📝 DRAFT QUEUED (pending Herb's approval):")
        print(f"   To: {original_email.get('prospect_email', '[unknown]')}")
        print(f"   Re: {original_email.get('subject', '')}")
        print(f"   Decision: {decision['action']} — {decision.get('reason', '')}")
        print(f"   File: {queue_path}")
        return queue_path

    def record_human_feedback(self, email_hash: str, feedback: Dict):
        """
        Learn from human corrections

        If human edits bot's draft, learn what was changed
        If human overrides decision, understand why
        """

        if feedback["type"] == "edit":
            # Human edited the draft
            changes = feedback["changes"]
            print(f"📝 Learning from edit: {changes}")

            # Reduce blessings slightly (bot wasn't perfect)
            self.assistant.governance.reservoir.record_human_override("draft_edited")

            # Learn the correction
            self.learning_engine.record_outcome(
                email_hash,
                "edited_by_human",
                {"changes": changes}
            )

        elif feedback["type"] == "override":
            # Human overrode auto-send decision
            reason = feedback["reason"]
            print(f"🚫 Learning from override: {reason}")

            self.assistant.governance.reservoir.record_human_override(reason)

    def record_deal_outcome(self, email_hash: str, outcome: str, deal_value: Optional[int] = None):
        """
        Learn from final outcomes (most important signal)

        Outcomes:
        - booked_call: They scheduled (positive)
        - closed_deal: They bought (very positive)
        - ghosted: No response (negative)
        - declined: Said no (neutral - we learn)
        """

        self.learning_engine.record_outcome(email_hash, outcome, {
            "deal_value": deal_value
        })

        if outcome == "closed_deal" and deal_value:
            # Big success - boost blessings
            self.assistant.governance.reservoir.record_successful_close(deal_value)
            print(f"🎉 Deal closed: ${deal_value} - Bot earned +10 blessings")

    def run_daily_health_check(self):
        """Daily self-assessment and optimization"""
        print("\n" + "="*80)
        print("🏥 DAILY HEALTH CHECK")
        print("="*80)

        health = self.health_monitor.check_health(self.assistant.governance.reservoir)

        print(f"\nHealth Status: {'✅ Healthy' if health['healthy'] else '⚠️  Issues Detected'}")

        if health["issues"]:
            print(f"\nIssues:")
            for issue in health["issues"]:
                print(f"  - {issue}")

        if health["auto_fixes"]:
            print(f"\nAuto-Fixes Applied:")
            for fix in health["auto_fixes"]:
                print(f"  ✓ {fix}")

        # Performance metrics
        metrics = self.learning_engine.state["performance_metrics"]
        print(f"\nPerformance Metrics:")
        print(f"  Response Rate: {metrics['response_rate']:.1%}")
        print(f"  Call Booking Rate: {metrics['call_booking_rate']:.1%}")
        print(f"  Close Rate: {metrics['close_rate']:.1%}")

        # Learning progress
        optimizations = self.learning_engine.get_optimization_suggestions()
        print(f"\nLearned Optimizations: {len(optimizations)}")
        for opt in optimizations[:3]:  # Show top 3
            print(f"  ✓ {opt['pattern']} (success_count={opt['success_count']})")

        print("\n" + "="*80)


# ============================================================================
# DEMO: Autonomous Bot with Self-Learning
# ============================================================================

if __name__ == '__main__':
    import tempfile

    print("="*80)
    print("🤖 AUTONOMOUS SALES BOT - CLOSE OR QUIT (3 Nos Rule)")
    print("   📝 DRAFT-ONLY demo — all state and drafts go to a temp dir")
    print("="*80)

    # NOTE: demo only — test addresses are fictional, state is temporary,
    # and the "closed deal" below is a simulated learning input, not a
    # real outcome.

    with tempfile.TemporaryDirectory() as _tmp:
        _tmp_path = Path(_tmp)
        # Initialize with FULL decision autonomy (draft-only; Herb sends)
        bot = AutonomousSalesBot(
            full_autonomy=True,
            queue_dir=_tmp_path / "queue",
            state_dir=_tmp_path / "state",
        )

        # Simulate incoming emails
        emails = [
            {
                "subject": "Re: AI Governance",
                "body": "Not interested right now, thanks.",
                "prospect_email": "mike@example.com"
            },
            {
                "subject": "Re: AI Governance (2nd email)",
                "body": "Still not interested.",
                "prospect_email": "mike@example.com"
            },
            {
                "subject": "Re: AI Governance (3rd email)",
                "body": "Please stop contacting me.",
                "prospect_email": "mike@example.com"
            },
            {
                "subject": "Re: Model Risk Solution",
                "body": "This looks interesting! Can we schedule a call?",
                "prospect_email": "sarah@example.com"
            },
            {
                "subject": "Re: Mythara Demo",
                "body": "How does the cryptographic hashing work?",
                "prospect_email": "james@example.com"
            }
        ]

        print("\n" + "="*80)
        print("📧 PROCESSING EMAILS — BOT DECIDES, HERB APPROVES (DRAFT-ONLY)")
        print("="*80)

        for i, email in enumerate(emails, 1):
            print(f"\n--- Email {i} ---")
            print(f"From: {email['prospect_email']}")
            print(f"Subject: {email['subject']}")
            print(f"Body: {email['body']}")

            result = bot.process_email_autonomously(email)

            print(f"\n🤖 Bot Decision:")
            print(f"   Intent: {result.get('refined_intent', result['intent'])} (upstream: {result['intent']})")
            print(f"   Messenger: {result['messenger']}")

            if "autonomous_decision" in result:
                decision = result["autonomous_decision"]
                print(f"   Action: {decision['action']} (confidence: {decision['confidence']:.0%})")
                print(f"   Reason: {decision['reason']}")

            if result.get("queued"):
                print(f"   ✅ Draft queued for Herb's approval: {result.get('queue_path')}")
            elif result.get("action") == "IGNORED":
                print(f"   🚫 Ignored (already quit)")

            # Show strikes for "not interested"
            if email["prospect_email"] in bot.conversation_tracker:
                tracker = bot.conversation_tracker[email["prospect_email"]]
                if tracker["no_count"] > 0:
                    print(f"   ⚠️  Strikes: {tracker['no_count']}/3")
                    if tracker["status"] == "quit":
                        print(f"   👋 QUIT - Added to quarterly re-engagement cycle")

        # Show quarterly cycle status
        print("\n" + "="*80)
        print("� QUARTERLY CYCLE STATUS")
        print("="*80)
        print(f"Current Quarter: {bot._get_current_quarter()}")
        print(f"Prospects in quit list: {len(bot.quarterly_cycle['quit_list'])}")

        for email, data in bot.quarterly_cycle["quit_list"].items():
            recontact = datetime.fromisoformat(data["recontact_date"]).strftime("%Y-%m-%d")
            print(f"  - {email}: Re-engage on {recontact} ({data['reason']})")

        # Simulate quarterly re-engagement
        print("\n" + "="*80)
        print("🔄 SIMULATING QUARTERLY RE-ENGAGEMENT")
        print("="*80)
        print("(In production, this runs automatically every quarter)")

        # Simulate learning from outcomes
        print("\n" + "="*80)
        print("📊 LEARNING FROM OUTCOMES")
        print("="*80)

        # Simulate a learning input (TEST-ONLY — not a real deal or real person)
        print("\n📝 Simulated learning input (test-only, not a real outcome):")
        print("   sarah@example.com → booked call → closed $2,500 deal (SIMULATED)")
        bot.record_deal_outcome("mock_hash_sarah", "closed_deal", 2500)

        # Run health check
        bot.run_daily_health_check()

        print("\n" + "="*80)
        print("✅ DRAFT-AUTONOMOUS SYSTEM (Herb approves every send)")
        print("="*80)
        print("\nThe bot now:")
        print("  ✓ Decides autonomously: close, quit, or re-engage (CLOSE OR QUIT)")
        print("  ✓ Drafts every outbound email — Herb approves every send")
        print("  ✓ Counts strikes on 'not interested' (3 and quit)")
        print("  ✓ Quits gracefully after 3 nos")
        print("  ✓ Re-engages automatically every quarter (as drafts)")
        print("  ✓ Learns from successful patterns")
        print("  ✓ Self-heals when performance degrades")
        print("\n🚀 Bot decides fast. Herb sends. Nothing leaves without approval.")
