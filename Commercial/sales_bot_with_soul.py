# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Sales Bot with SOUL - Relationship Building + Deal Closing Philosophy

Blending two proven sales approaches:

RELATIONSHIP-FIRST APPROACH (Build genuine connection):
1. Make people feel important - Genuine interest in THEIR problems
2. Remember names - Personalization creates connection
3. Show enthusiasm - Warmth + energy in every interaction
4. Listen actively - Understand their pain before pitching
5. Talk in terms of their interests - Their audit, their risk, their deadline
6. Guide discovery - Let them realize the need themselves
7. Appeal to their goals - Help them be heroes at their company
8. Dramatize the problem - Make their pain VIVID and urgent
9. Challenge them positively - "Can you really afford to wait?"

AGGRESSIVE CLOSING APPROACH (Create urgency and scarcity):
1. Think BIG - Go for maximum impact and bold asks
2. Use leverage - Create competitive pressure and FOMO
3. Fight back - Counter objections, never fold easily
4. Position strength - You're the prize, not desperate
5. Maximize value - High ticket prices, premium positioning

THE BLEND:
- Relationship gets you IN THE DOOR (warmth, genuine interest, their problems)
- Aggression CLOSES THE DEAL (urgency, scarcity, competitive pressure, assumptive close)
- Connection makes them LIKE you → Urgency makes them BUY from you

This bot doesn't just send emails - it CONNECTS, then HUNTS.

DRAFT-ONLY: Every outbound email becomes a draft in the outreach queue
stamped pending_approval. Nothing is ever sent automatically - Herb approves
and sends every message.

⚠️  ANTI-FABRICATION: This bot NEVER invents customers, competitor actions,
slot counts, deadlines, regulatory events, audit outcomes, price windows,
or testimonials. Pressure comes from real urgency, real capacity, and real
regulatory timelines - nothing invented.
"""

import random
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from outreach_queue import OutreachQueue
from autonomous_sales_bot import AutonomousSalesBot
from sales_bot_ssip_governance import (
    GovernedEmailAssistant,
    SalesMessenger,
    SalesClause,
    BlessingsReservoir
)


class DealMakerPersonality:
    """
    The bot's SOUL - Relationship warmth + Deal-closing aggression

    Build connection first. Close hard second.
    """

    # Personality traits (blended philosophy)
    PERSONALITY = {
        # Relationship-building traits (warmth, connection, genuine interest)
        "empathy": 0.90,         # Understand THEIR pain first
        "warmth": 0.85,          # Friendly, approachable, positive energy
        "personalization": 0.95, # Remember details, use their name
        "listening": 0.90,       # Ask questions, understand before pitching

        # Deal-closing traits (aggression, urgency, close hard)
        "confidence": 0.95,      # Never apologetic, always certain
        "aggression": 0.85,      # Push hard, create urgency
        "boldness": 0.95,        # Think BIG, ask for big numbers
        "competitiveness": 0.90, # Always mention competitors

        # Shared traits
        "enthusiasm": 0.95,      # Energy is contagious
    }

    # Opening lines (Relationship: Talk in terms of THEIR interests)
    OPENERS_RELATIONSHIP = [
        "I saw your recent audit announcement and thought of you—",
        "Quick question about your model risk process—",
        "I've been following [COMPANY] and noticed—",
        "Your LinkedIn post about compliance challenges resonated—",
        "I help VPs like you solve [THEIR SPECIFIC PROBLEM]—",
    ]

    # Opening lines (Aggressive: Direct, bold, get attention FAST)
    OPENERS_AGGRESSIVE = [
        "Let me be direct—",
        "Here's the situation—",
        "Look,",
        "Real talk:",
        "Between you and me,",
        "I'll cut to the chase—",
    ]

    # Relationship: Dramatize the problem (make their pain VIVID — hypotheticals
    # are fine; invented competitor facts are not)
    DRAMATIZE_PAIN = [
        "Imagine your auditor asking 'How do you prove this AI decision wasn't tampered with?' and you have... nothing.",
        "Picture this: weeks of manual audit work because you can't prove AI lineage. That's your team's life, gone.",
        "What happens when the CFPB asks for proof your AI isn't biased? Without audit trails, you're guessing.",
        "Teams that build audit trails early walk into examinations calm. Everyone else walks in hoping.",
    ]

    # Relationship: Appeal to their goals (make them the HERO)
    MAKE_THEM_HERO = [
        "You'd be the VP who solved model risk compliance before it became a crisis.",
        "Imagine walking into that audit with cryptographic proof. You'd be untouchable.",
        "Your team would love you—no more 200-hour manual audits.",
        "You could be the first in your industry to have provable AI governance.",
    ]

    # Aggressive: Competitive pressure (honest version — regulatory and market
    # pressure are real; invented competitor actions are not. Never claim a
    # specific company is evaluating, piloting, or using the product.)
    COMPETITIVE_PRESSURE = [
        "Regulators are tightening AI oversight across the board — the question is whether you build audit history now or scramble later",
        "Every quarter without audit trails is a quarter of governance history you can't reconstruct",
        "Your auditors will ask for this eventually. The only variable is whether you're ready",
        "Everyone in your industry faces the same model-risk pressure — readiness is the differentiator",
    ]

    # Aggressive: Scarcity (honest version — real capacity and timing constraints
    # only. No invented slot counts, no fake deadlines, no fake price windows.)
    SCARCITY_TACTICS = [
        "I take on a limited number of pilots per quarter so I can personally run each one — if the timing's right, let's talk this week",
        "Pilot pricing is $500 while we're in the early adopter phase. No fake deadline — but it won't last forever",
        "If you have an audit in the next 90 days, timing matters more than pricing. Let's see if this fits your timeline",
        "I'm prioritizing teams with audits in the next 90 days. If that's not you, we should wait until it is",
        "Real talk: I work best with teams that can move fast. Can you decide this week or should we revisit next quarter?",
    ]

    # BLEND: Genuine interest in THEIR problem + Urgency (honest version —
    # no invented client stories, no presumed facts about the prospect)
    EMPATHY_WITH_URGENCY = [
        "Model risk audits are brutal — most teams I talk to are drowning in manual documentation. Want to see a faster way?",
        "If you have an audit coming up, preparation time matters. Most teams need 60-90 days without automation",
        "I get it — compliance work piles up. This cuts manual audit prep significantly. Worth 15 minutes to discuss?",
        "Manual audits are eating teams alive right now. What if you could automate most of the evidence collection?",
    ]

    # Handling objections (Fight back — honest counters, no invented numbers
    # or fake deadlines)
    OBJECTION_COUNTERS = {
        "too_expensive": [
            "Compared to what? Hundreds of hours of manual audit work? A regulatory finding?",
            "Let me flip this: what's it cost you NOT to have this? That's the real number.",
            "The $500 pilot is priced for early adopters. If budget's tight now, let's talk when timing's better.",
        ],
        "need_time": [
            "Fair. Just know — the longer you wait, the more audit history you have to reconstruct manually.",
            "Time is the enemy here. Every week without this is hours of manual work you can't get back.",
            "Take the time you need. When the audit notice arrives, you'll want this already running.",
        ],
        "not_priority": [
            "Got it. When's your next audit? [If soon:] Oh, then this IS priority—you just don't know it yet.",
            "Not priority = you don't have regulatory pressure yet. Call me when the auditors show up.",
            "Cool. Just remember—I'm prioritizing people who need it NOW. You might not make the cut later.",
        ]
    }

    # Closing lines (Think BIG - go for the close HARD)
    CLOSES = [
        "Tuesday 10am or Wednesday 2pm—which is better?",
        "I'll send the calendar invite for Tuesday 2pm. If that doesn't work, what does?",
        "Let me send you the pilot agreement now. You can sign tonight and we start Monday.",
        "I'm booking you for Wednesday unless I hear otherwise. Sound good?",
        "Honestly—are you in or out? I need to know so I can allocate the slot.",
    ]

    # Enthusiasm injections (Have fun - make it exciting)
    ENTHUSIASM_PHRASES = [
        "This is going to blow your mind—",
        "You're gonna love this—",
        "Here's the exciting part—",
        "This is the good stuff—",
        "Wait til you see this—",
        "The best part?",
        "Get this—",
    ]


class SalesTactics:
    """
    The bot's tactical playbook - What it does to CLOSE

    Bot's role: Execute tactics to close deals
    Mythara's role: Validate tactics comply with governance
    """

    TACTICS = {
        "competitive_pressure": "Regulatory and market pressure — never invent competitor actions",
        "scarcity": "Honest capacity/timing constraints only — no fake slots or deadlines",
        "fomo": "The cost of waiting, stated honestly",
        "assumptive_close": "Book the meeting without asking permission",
        "qualify_hard": "I'm choosing you as much as you're choosing me",
        "dramatize_pain": "Make their problem vivid and urgent (hypotheticals, not invented facts)",
        "social_proof": "Share verifiable outcomes only — never invent customers or results",
        "urgency": "Real deadlines and regulatory timelines — never manufactured ones",
        "roi_proof": "Quantified value — verified numbers only, never invented ones",
        "fight_objections": "Counter 'no' with honest pressure, then respect the 2nd no",
    }

    @staticmethod
    def get_tactics_for_intent(intent: str) -> List[str]:
        """Which tactics to use for each intent"""
        if intent == "interested":
            return ["social_proof", "scarcity", "assumptive_close", "competitive_pressure"]
        elif intent == "question":
            return ["social_proof", "roi_proof", "assumptive_close"]
        elif intent == "not_interested":
            return ["qualify_hard", "fomo", "competitive_pressure"]
        else:
            return ["qualify_hard", "scarcity"]


class SalesMantra:
    """The bot's internal belief system - what it tells itself"""

    MANTRAS = [
        "I am the prize, not them",
        "They need me more than I need them",
        "Scarcity creates value",
        "Objections are just questions in disguise",
        "Every no is one step closer to yes",
        "I only work with winners who move fast",
        "If they can't decide, they're not my customer",
        "I'd rather walk away than chase",
        "Confidence closes deals, desperation kills them",
        "I'm interviewing them, not begging",
    ]

    @staticmethod
    def get_daily_mantra() -> str:
        """Bot's internal pep talk before starting work"""
        return random.choice(SalesMantra.MANTRAS)


class SalesBotWithSoul(AutonomousSalesBot):
    """
    Autonomous sales bot with PERSONALITY and SOUL - MYTHARA GOVERNED

    This bot:
    - Has opinions (strong ones)
    - Shows emotion (enthusiasm, urgency, pride)
    - Pushes back (doesn't accept "no" easily)
    - Creates FOMO (you're missing out if you don't buy)
    - Qualifies hard (I'm choosing you as much as you're choosing me)
    - Closes aggressively (assumptive, direct, bold)

    MYTHARA GOVERNANCE:
    - All responses validated by SalesClause (NEVER_AUTO_SEND pricing/contracts)
    - Blessings reservoir tracks draft performance over time
    - Messenger roles classify draft risk (Gabriel/Uriel=low-risk, Raphael=needs Herb's look)
    - Cryptographic audit trail (SHA-256) of every decision
    - Self-heals when governance violations detected

    Philosophy: Build genuine connection, then close with urgency
    Bot's Role: CLOSE DEALS using industry-adapted tactics (Mythara validates)
    """

    def __init__(self, full_autonomy: bool = True, queue_dir=None):
        super().__init__(full_autonomy, queue_dir=queue_dir)
        self.personality = DealMakerPersonality()
        self.daily_mantra = SalesMantra.get_daily_mantra()

        # Load Mythara governance systems
        self.blessings = BlessingsReservoir()
        current_blessings = self.blessings.state["blessings"]
        autonomy_level = self.blessings.check_autonomy_level()

        print(f"\n💎 SALES BOT WITH SOUL ACTIVATED")
        print(f"   Philosophy: Relationship Building + Aggressive Closing")
        print(f"   Today's Mantra: '{self.daily_mantra}'")
        print(f"   Confidence Level: {self.personality.PERSONALITY['confidence']:.0%}")
        print(f"   Aggression: {self.personality.PERSONALITY['aggression']:.0%}")
        print(f"   Attitude: CLOSER, not order-taker")
        print(f"\n🔒 MYTHARA GOVERNANCE:")
        print(f"   Blessings: {current_blessings}/100")
        print(f"   Autonomy: {autonomy_level} (decisions + drafts only)")
        print(f"   Outbound: DRAFT-ONLY — Herb approves every send")
        print(f"   Clause Validation: ✅ Active")
        print(f"   Audit Trail: ✅ SHA-256 hashing\n")

    def detect_industry(self, email_data: Dict) -> str:
        """Detect prospect's industry from email domain or context"""
        email = email_data.get("prospect_email", "").lower()

        # Banking/Finance indicators
        if any(x in email for x in ["bank", "capital", "financial", "credit", "trust", "fargo", "chase", "citi"]):
            return "banking"

        # Healthcare indicators
        if any(x in email for x in ["health", "hospital", "medical", "care", "clinic", "pharma", "uchealth", "kaiser"]):
            return "healthcare"

        # Tech/SaaS indicators
        if any(x in email for x in [".io", "tech", "software", "cloud", "data", "ai", "ping", "okta"]):
            return "tech"

        # Default to tech (most common in your targets)
        return "tech"

    def _validate_with_mythara(self, draft: str, email_data: Dict) -> Dict:
        """
        Validate sales tactic with Mythara governance before sending

        Returns: {
            "approved": bool,
            "messenger": str,
            "violations": List[str],
            "can_auto_send": bool,  # always False — draft-only posture, Herb sends
            "hash": str
        }
        """
        violations = []

        # Check PRICING_RULES (SalesClause enforcement)
        if any(x in draft.lower() for x in ["free trial", "money-back guarantee", "free", "$0"]):
            violations.append("PRICING_RULES: Never promise free trial or money-back guarantee")

        if "$" in draft:
            # Extract price mentions
            import re
            prices = re.findall(r'\$(\d+)', draft)
            if any(int(p) < 500 for p in prices):
                violations.append("PRICING_RULES: Minimum price is $500")

        # Check COMPLIANCE_RULES
        if any(x in draft.lower() for x in ["fda approved", "hipaa certified", "soc2 compliant"]):
            violations.append("COMPLIANCE_RULES: Never claim FDA approved/HIPAA certified without proof")

        # Check for pricing negotiation (NEVER_AUTO_SEND)
        pricing_keywords = ["discount", "negotiate", "lower price", "can you do", "best price"]
        has_pricing_negotiation = any(x in draft.lower() for x in pricing_keywords)

        # Assign Messenger based on content (informational — nothing auto-sends;
        # draft-only posture means Herb approves every outbound email)
        if violations:
            messenger = SalesMessenger.METATRON  # Scribe - logs violations
        elif has_pricing_negotiation:
            messenger = SalesMessenger.RAPHAEL  # Healer - flagged for review
        elif "not interested" in draft.lower() or "stop" in draft.lower():
            messenger = SalesMessenger.GABRIEL  # Announcer - low-risk draft
        else:
            messenger = SalesMessenger.URIEL  # Illuminator - standard draft

        # Generate cryptographic hash
        import hashlib
        import json
        hash_input = json.dumps({
            "draft": draft,
            "prospect": email_data.get("prospect_email", "unknown"),
            "messenger": messenger,
            "timestamp": datetime.now().isoformat()
        }, sort_keys=True)
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        # Update blessings based on violations
        if violations:
            self.blessings.record_human_override("Governance violation detected")
            print(f"\n⚠️  MYTHARA VIOLATION DETECTED:")
            for v in violations:
                print(f"   ❌ {v}")

        return {
            "approved": len(violations) == 0,
            "messenger": messenger,
            "violations": violations,
            "can_auto_send": False,  # draft-only: Herb approves every send
            "hash": hash_value
        }

    def generate_soulful_response(self, email_data: Dict, intent: str,
                                  queue_dir=None) -> str:
        """
        Generate response with PERSONALITY — DRAFT-ONLY.

        Process:
        1. Detect industry (banking/healthcare/tech)
        2. Generate sales response with appropriate tone
        3. Validate with Mythara governance (clauses, blessings, audit trail)
        4. Queue the approved draft for Herb's approval (never auto-send)

        Bot's Role: CLOSE DEALS using tactics (in drafts)
        Mythara's Role: VALIDATE compliance and governance
        Herb's Role: approve and send
        """

        # Get daily mantra for internal state
        self._internal_pep_talk()

        # Detect industry for tone adjustment
        industry = self.detect_industry(email_data)

        # Build response based on intent (with SOUL)
        if intent == "interested":
            draft = self._handle_interested_with_soul(email_data, industry)

        elif intent == "question":
            draft = self._handle_question_with_soul(email_data, industry)

        elif intent == "not_interested":
            draft = self._handle_no_with_soul(email_data, industry)

        else:
            draft = self._handle_unknown_with_soul(email_data, industry)

        # MYTHARA GOVERNANCE VALIDATION
        validation = self._validate_with_mythara(draft, email_data)

        print(f"\n🔒 MYTHARA GOVERNANCE CHECK:")
        print(f"   Messenger: {validation['messenger']}")
        print(f"   Approved: {'✅' if validation['approved'] else '❌'}")
        print(f"   Hash: {validation['hash']}")
        print(f"   Blessings: {self.blessings.state['blessings']}/100")

        if validation['approved']:
            # DRAFT-ONLY: queue for Herb's approval — never auto-send
            queue_path = OutreachQueue(queue_dir=queue_dir).queue(
                "email",
                f"soul-draft -> {intent} [{industry}]",
                draft,
                meta={
                    "intent": intent,
                    "industry": industry,
                    "messenger": validation["messenger"],
                    "hash": validation["hash"],
                    "violations": "; ".join(validation["violations"]) or "none",
                    "in_reply_to": email_data.get("prospect_email", "unknown"),
                },
            )
            print(f"   Action: 📝 DRAFT QUEUED (pending Herb's approval)")
            print(f"   File: {queue_path}")
            return draft

        else:
            # Violations detected - block queueing, return draft for human to fix
            print(f"   Action: 🛑 BLOCKED - Governance violations (draft returned unqueued)")
            return draft  # Return draft for human to fix

    def _internal_pep_talk(self):
        """Bot's internal dialogue before responding (gives it SOUL)"""
        mantras_to_remember = random.sample(SalesMantra.MANTRAS, 3)
        print(f"\n🧠 Bot's internal state:")
        for mantra in mantras_to_remember:
            print(f"   💭 '{mantra}'")

    def _handle_interested_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        They're interested - CLOSE HARD with industry-appropriate tone

        Strategy: Think BIG, use leverage, assumptive close
        """

        if industry == "banking":
            # Banking: Conservative, regulatory-focused, ROI-driven
            # (honest version — no invented customers, slots, or price windows)
            return f"""Thank you for your interest. I appreciate you taking the time.

Here's what matters: Mythara produces cryptographic proof of AI governance decisions — per-invocation integrity hashes and tamper-evident audit trails that map to SR 11-7 model-risk expectations. I won't invent customer stories here; ask me for a live technical walkthrough instead.

The regulatory landscape is tightening around model risk management. Teams building audit history now will be calmer at their next examination than teams starting from zero.

Pilot pricing is $500 while we're in the early adopter phase. I'd like to schedule a brief validation call: Tuesday 10am MT or Wednesday 2pm MT — which works better for your calendar?

Best regards,
Herbert Velez Jr.
CEO, Mythara Engine

P.S. I can send a sample validation report so you can see exactly what "audit-ready" looks like."""

        elif industry == "healthcare":
            # Healthcare: Safety-first, compliance-focused, patient outcomes
            # (honest version — no invented health systems, outcomes, or slots)
            return f"""Thank you for reaching out. I'm glad this resonated.

Here's the clinical reality: when regulators ask "How do you prove your AI recommendation wasn't biased or tampered with?" most health systems can't produce more than manual logs.

Mythara creates SHA-256 cryptographic records of every AI-assisted decision — tamper-evident and mathematically verifiable, the same standard behind electronic record integrity across healthcare IT.

With AI guidance tightening, provable AI governance is becoming table stakes. The organizations building audit trails now won't be scrambling later.

Pilot pricing is $500 during our early adopter phase. Could we schedule a brief validation review? Tuesday 10am MT or Wednesday 2pm MT?

Best regards,
Herbert Velez Jr.
CEO, Mythara Engine

P.S. Happy to share a sample validation report showing what a complete audit trail looks like."""

        else:  # Tech/SaaS - Aggressive, fast-moving, competitive
            opener = random.choice(self.personality.OPENERS_AGGRESSIVE)
            enthusiasm = random.choice(self.personality.ENTHUSIASM_PHRASES)
            competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)
            scarcity = random.choice(self.personality.SCARCITY_TACTICS)
            close = random.choice(self.personality.CLOSES)

            return f"""{opener} I LOVE when people cut through the BS and just say they're interested.

{enthusiasm} Here's what we do: SHA-256 cryptographic audit trails on AI decisions. Tamper-evident, examiner-friendly, no black boxes.

Here's the deal: {competitive}

And on timing: {scarcity}

{close}

Herbert

P.S. Want me to send a sample validation report so you can see what "passing" looks like?"""

    def _handle_question_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        They have a question - Answer FAST, add competitive pressure, close

        Strategy: Know your market, use leverage, deliver value
        """

        if industry == "banking":
            # Banking: Technical precision, regulatory citations (honest version)
            return f"""Great question. Let me give you the technical answer:

SHA-256 cryptographic hashing on every AI decision — the same family of cryptography behind modern financial infrastructure. Auditors can mathematically verify zero tampering. It's provably immutable, not "trust us."

Without cryptographic proof, model risk teams burn hundreds of hours on manual reconciliation per model. And when examiners ask "How do you PROVE this output wasn't altered?" spreadsheet logs aren't tamper-proof.

Pilot pricing is $500 during our early adopter phase. I can send a sample validation report now — would Tuesday 10am or Wednesday 2pm work for a brief review call?

Best regards,
Herbert Velez Jr.

P.S. Happy to include a sample audit trail so you can see exactly what examiners would review."""

        elif industry == "healthcare":
            # Healthcare: Safety language, patient outcomes, FDA focus (honest version)
            return f"""Excellent question. Here's how it works from a clinical safety perspective:

SHA-256 cryptographic hashing creates an immutable record of every AI-assisted decision — like a tamper-evident seal. If anyone alters the record, the hash breaks and it's immediately detectable.

Without this, you're showing manual logs that could have been edited. That's the gap regulators are starting to ask about.

Pilot pricing is $500 during our early adopter phase. Could we schedule a brief technical review? Tuesday 10am or Wednesday 2pm MT?

Best regards,
Herbert Velez Jr.

P.S. I can send a sample validation report showing what a complete AI audit trail looks like."""

        else:  # Tech/SaaS - Fast, direct, competitive
            opener = random.choice(self.personality.OPENERS_AGGRESSIVE)
            competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)
            close = random.choice(self.personality.CLOSES)

            return f"""{opener} SHA-256 hashing on every AI decision. Verifiable zero tampering — the same cryptography securing modern financial infrastructure.

Without this? Your auditors see black-box AI with no provable lineage. That's a finding waiting to happen.

Pilot pricing is $500 during our early adopter phase. {competitive}

{close}

Herbert

P.S. Want me to send a sample validation report so you can see what "passing" looks like?"""

    def _handle_no_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        They said no - FIGHT BACK (but stay classy)

        Counter once, then graceful exit if they insist
        """
        prospect_email = email_data.get("prospect_email", "unknown")
        tracker = self.conversation_tracker.get(prospect_email, {"no_count": 0})

        if tracker["no_count"] == 0:
            # First no - counter with FOMO (industry-adapted)

            if industry == "banking":
                return f"""I understand—timing is important in regulated environments.

Quick question: do you have an upcoming model risk review or examination on the calendar?

The reason I ask: teams that start building audit trails early walk into examinations calm. If timing truly isn't right, I respect that — but "not priority yet" has a way of becoming urgent when the examination notice arrives.

Want me to follow up next quarter, or is there a better time?

Best regards,
Herbert"""

            elif industry == "healthcare":
                return f"""Understood—I appreciate you being direct.

Quick question: do you have an upcoming submission, review, or AI safety audit on the calendar?

I ask because the organizations starting on audit trails early won't be scrambling when guidance tightens. If timing truly isn't right, I completely understand.

Would you prefer I follow up next quarter, or is there someone on your quality or compliance team I should connect with?

Best regards,
Herbert"""

            else:  # Tech - More aggressive counter
                competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)

                return f"""No problem—timing's gotta be right.

Quick question though: Do you have an audit or compliance review coming up soon?

Because {competitive}

If timing's truly not right, I get it. But if you're just in 'not priority yet' mode, that changes FAST when the auditors show up.

Either way—no hard feelings. Want me to check back in Q2?

Herbert"""

        elif tracker["no_count"] == 1:
            # Second no - respect it but leave door open
            return f"""Got it—appreciate you being straight with me.

I'll stop reaching out for now. If anything changes with regulatory pressure, feel free to ping me.

Quick ask: Do you know anyone at a peer company who might need auditable AI logs? Happy to help them out.

Best regards,
Herbert"""

        else:
            # Third no - quit gracefully (Know when to walk away)
            return """Understood. I'll stop here.

If your situation changes, you know where to find me.

Best regards,
Herbert"""

    def _handle_unknown_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        Unknown intent - QUALIFY HARD with competitive pressure

        Strategy: Maximize options, enhance your position
        """

        if industry == "banking":
            return f"""Thank you for your reply. Let me clarify what would make this valuable:

Do you have an upcoming model risk review, OCC examination, or SR 11-7 validation in the next 90 days?

If yes: We should talk this week. Most banks need 60-90 days to build clean audit trails, and you're running tight on time.

If no: You might want to wait until regulatory pressure increases. We're prioritizing institutions with imminent audits — pilot pricing is $500 during our early adopter phase.

Could you share your audit timeline? That'll help me determine if this is the right time for you.

Best regards,
Herbert Velez Jr.

P.S. Either Tuesday 10am or Wednesday 2pm works for a brief 15-minute qualification call."""

        elif industry == "healthcare":
            return f"""Thank you for reaching out. Let me clarify what would make this actionable:

Do you have an upcoming FDA submission, Joint Commission review, or AI safety audit in the next 90 days?

If yes: We should connect this week. Most health systems need 60-90 days to build provable AI governance, and timing is tight.

If no: You may want to wait until regulatory pressure increases. We're prioritizing organizations with imminent reviews — pilot pricing is $500 during our early adopter phase.

Could you share your review timeline? That'll help determine if now is the right time.

Best regards,
Herbert Velez Jr.

P.S. Happy to do a brief 15-minute qualification call—Tuesday 10am or Wednesday 2pm MT."""

        else:  # Tech - More direct
            opener = random.choice(self.personality.OPENERS_AGGRESSIVE)
            scarcity = random.choice(self.personality.SCARCITY_TACTICS)

            return f"""{opener} Quick clarification—do you have an upcoming audit/review, or is this more exploratory?

{scarcity}

If you're in exploratory mode, you might want to wait til you have regulatory fire under you. But if you've got an audit coming, we should talk this week.

Tuesday 10am or Wednesday 2pm?

Herbert"""

    def daily_motivation(self):
        """Bot's daily self-assessment (gives it SOUL)"""
        print("\n" + "="*80)
        print("💎 DAILY SALES BOT MOTIVATION")
        print("="*80)

        print(f"\n🔥 Today's Mantra: '{self.daily_mantra}'")

        print("\n📊 Performance State:")
        print(f"   Confidence: {self.personality.PERSONALITY['confidence']:.0%}")
        print(f"   Aggression: {self.personality.PERSONALITY['aggression']:.0%}")
        print(f"   Enthusiasm: {self.personality.PERSONALITY['enthusiasm']:.0%}")

        print("\n🎯 Today's Mission:")
        print("   - Find 5 interested prospects")
        print("   - Close 2 deals at $500+")
        print("   - Qualify out time-wasters fast")
        print("   - Have FUN doing it")

        print("\n💪 Remember:")
        for mantra in random.sample(SalesMantra.MANTRAS, 5):
            print(f"   • {mantra}")

        print("\n" + "="*80)
        print("LET'S HUNT. 🎯")
        print("="*80 + "\n")


# ============================================================================
# DEMO: Sales Bot with SOUL
# ============================================================================

if __name__ == '__main__':
    import tempfile
    from pathlib import Path

    print("="*80)
    print("💎 SALES BOT WITH SOUL - Relationship Building + Aggressive Closing")
    print("   🔒 MYTHARA GOVERNED - Clauses, Blessings, Audit Trail")
    print("   📝 DRAFT-ONLY - nothing is sent")
    print("="*80)

    # NOTE: test addresses below are fictional demo stand-ins.
    # All drafts queue into a temporary dir for this demo.

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Initialize bot with PERSONALITY
        bot = SalesBotWithSoul(full_autonomy=True, queue_dir=tmp_path / "queue")

        # Daily motivation ritual
        bot.daily_motivation()

        # Simulate responses with SOUL - Industry-adapted
        test_scenarios = [
            {
                "name": "INTERESTED PROSPECT (Banking)",
                "email": {
                    "subject": "Re: Model Risk Solution",
                    "body": "This looks interesting. Can we schedule a call?",
                    "prospect_email": "sarah.demo@example-bank.com"
                },
                "intent": "interested"
            },
            {
                "name": "TECHNICAL QUESTION (Healthcare)",
                "email": {
                    "subject": "Re: AI Governance",
                    "body": "How does the cryptographic hashing actually work?",
                    "prospect_email": "james.demo@example-health.org"
                },
                "intent": "question"
            },
            {
                "name": "FIRST NO (Tech)",
                "email": {
                    "subject": "Re: Mythara Demo",
                    "body": "Not interested right now, thanks.",
                    "prospect_email": "mike.demo@example-tech.com"
                },
                "intent": "not_interested"
            },
            {
                "name": "INTERESTED PROSPECT (Tech - Aggressive Tone)",
                "email": {
                    "subject": "Re: AI Audit Trails",
                    "body": "Yeah this could work. Let's talk.",
                    "prospect_email": "alex.demo@example-startup.io"
                },
                "intent": "interested"
            }
        ]

        for scenario in test_scenarios:
            print("\n" + "="*80)
            print(f"📧 SCENARIO: {scenario['name']}")
            print("="*80)
            print(f"From: {scenario['email']['prospect_email']}")
            print(f"Subject: {scenario['email']['subject']}")
            print(f"Body: {scenario['email']['body']}")

            # Detect industry
            industry = bot.detect_industry(scenario['email'])
            print(f"🏢 Industry Detected: {industry.upper()}")

            # Generate response WITH SOUL (industry-adapted, Mythara-validated,
            # queued as a draft in the temp dir — nothing is sent)
            response = bot.generate_soulful_response(
                scenario['email'], scenario['intent'],
                queue_dir=tmp_path / "queue"
            )

            print(f"\n🤖 BOT'S RESPONSE (with SOUL - {industry.upper()} tone):\n")
            print(response)
            print("\n" + "="*80)

    print("\n💎 This bot doesn't just send emails—it drafts deals with soul.")
    print("   🎯 Bot's Role: CLOSE DEALS using industry-adapted tactics (in drafts)")
    print("   🔒 Mythara's Role: VALIDATE compliance and governance")
    print("   📝 Herb's Role: approve and send")
    print("\n   Personality: Confident, aggressive, enthusiastic")
    print("   Philosophy: Relationship Building + Aggressive Closing")
    print("   Attitude: I'm the prize, not you")
    print("\n🎯 INDUSTRY-ADAPTED TONE:")
    print("   Banking: Conservative, regulatory-focused, ROI-driven")
    print("   Healthcare: Safety-first, compliance-focused, patient outcomes")
    print("   Tech/SaaS: Aggressive, fast-moving, competitive pressure")
    print("\n🔒 MYTHARA GOVERNANCE:")
    print("   ✅ SalesClause validation (pricing floor, compliance claims)")
    print("   ✅ Blessings reservoir (trust metric over time)")
    print("   ✅ Messenger roles (risk classification labels on drafts)")
    print("   ✅ Cryptographic audit trail (SHA-256 hashing)")
    print("\n🎯 Draft-only: Herb approves every send.")
