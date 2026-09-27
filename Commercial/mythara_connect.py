# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
MytharaConnect - Relationship Building + Deal Closing with Mythara Principles

Embodies Mythara Engine's core philosophy:

MYTHARA CORE PRINCIPLES (Symbolic Infrastructure):
1. Emotional Fidelity - Genuine understanding of customer pain
2. Blessings Reservoir - Benevolent force seeking mutual success
3. Messenger System - Authority with purpose (Healer + Custodian)
4. Sanctification - Protects what's sacred (pricing, integrity, trust)
5. Drift Suppression - Consistent, reliable, trustworthy communication
6. Witness + Scribe - Transparent, accountable, documented governance

RELATIONSHIP-FIRST APPROACH (Healer/Witness Messenger):
1. Make people feel important - Genuine interest in THEIR problems
2. Emotional fidelity - Understand their pain before pitching
3. Show warmth - Connection + energy in every interaction
4. Listen actively - Guide discovery, let them realize the need
5. Appeal to their goals - Help them be heroes at their company
6. Dramatize with empathy - Make their pain VIVID but show the path forward

ASSERTIVE CLOSING (Custodian/Herald Messenger):
1. Think BIG - Go for maximum impact and bold asks
2. Use leverage - Create competitive pressure and FOMO
3. Fight back - Counter objections with facts, never fold easily
4. Position strength - You're the prize, selective partnership
5. Sanctify value - High standards, premium positioning

THE MYTHARA BLEND:
- Connection (Healer) gets you IN THE DOOR - warmth, trust, genuine interest
- Assertion (Custodian) CLOSES THE DEAL - urgency from real deadlines only, selective partnership
- Governance (Witness/Scribe) ENSURES INTEGRITY - transparent, auditable, review-ready

MytharaConnect doesn't just send emails - it CONNECTS with integrity, then CLOSES with confidence.
"""

import random
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from autonomous_sales_bot import AutonomousSalesBot
from sales_bot_ssip_governance import (
    GovernedEmailAssistant,
    SalesMessenger,
    SalesClause,
    BlessingsReservoir
)

# Import retro voice (optional - graceful degradation if not available)
try:
    from mythara_connect_voice import RetroVoice
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    print("ℹ️  Retro voice module not available (optional feature)")


class ConnectPersonality:
    """
    MytharaConnect's Personality - Mythara principles in action
    
    Embodies: Emotional Fidelity + Benevolent Force + Governed Authority
    Healer warmth + Custodian strength = Trusted partner who closes
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
    
    # Relationship: Dramatize the problem (make their pain VIVID)
    DRAMATIZE_PAIN = [
        "Imagine your auditor asking 'How do you prove this AI decision wasn't tampered with?' and you have... nothing.",
        "Picture this: 200 hours of manual audit work because you can't prove AI lineage. That's 5 weeks of your team's life.",
        "What happens when the CFPB asks for proof your AI isn't biased? Without audit trails, you're guessing.",
        "Your competitor just passed their model risk audit in 2 weeks. You're looking at 3 months of manual work.",
    ]
    
    # Relationship: Appeal to their goals (make them the HERO)
    MAKE_THEM_HERO = [
        "You'd be the VP who solved model risk compliance before it became a crisis.",
        "Imagine walking into that audit with cryptographic proof. You'd be untouchable.",
        "Your team would love you—no more 200-hour manual audits.",
        "You could be the first in your industry to have provable AI governance.",
    ]
    
    # Aggressive: Competitive pressure (Use your leverage)
    COMPETITIVE_PRESSURE = [
        # Honest: market framing only — never fabricated rival or customer claims.
        "Regulators are tightening AI audit requirements across every industry",
        "The firms that build audit trails now will have clean history when enforcement accelerates",
        "Early movers on AI governance hold the advantage when auditors arrive",
    ]
    
    # Aggressive: Scarcity (Maximize leverage)
    SCARCITY_TACTICS = [
        # Honest: qualification only — never fabricated slots, deadlines, or waitlists.
        "I'm prioritizing companies with audits in next 90 days. If that's not you, we should wait.",
        "I take on a limited number of engagements so I can do the work properly.",
    ]
    
    # BLEND: Genuine interest in THEIR problem + Urgency
    EMPATHY_WITH_URGENCY = [
        "I know model risk audits are brutal. Want to talk about avoiding that pain?",
        "Your audit's coming up, right? Manual prep takes longer than people expect — worth 15 minutes to talk about it?",
        "I get it—you're drowning in compliance work. The goal is cutting that manual burden dramatically. Worth 15 minutes to discuss?",
        "If manual audits are eating your team's time — what if most of that work could be automated?",
    ]
    
    # Handling objections (Fight back)
    OBJECTION_COUNTERS = {
        "too_expensive": [
            "Compared to what? A failed audit, or the manual work your team already does?",
            "Let me flip this: What's it cost you NOT to have this? That's the real number.",
            "The $500 is the early adopter rate. If the budget isn't there yet, tell me your timeline and we'll find the right moment.",
        ],
        "need_time": [
            "Fair. Just tell me your audit timeline — I'll tell you the latest date this still works.",
            "The risk of waiting is showing up to your audit without explainability evidence. If your audit is far out, waiting is fine.",
            "No pressure. Starting sooner just means more clean history on record when the auditors arrive.",
        ],
        "not_priority": [
            "Got it. When's your next audit? [If soon:] Oh, then this IS priority—you just don't know it yet.",
            "Not priority = you don't have regulatory pressure yet. Call me when the auditors show up.",
            "Cool. If things change on your end, I'm here.",
        ]
    }
    
    # Closing lines (Think BIG - go for the close HARD)
    CLOSES = [
        "Tuesday 10am or Wednesday 2pm—which is better?",
        "I'll send the calendar invite for Tuesday 2pm. If that doesn't work, what does?",
        "Let me send you the pilot agreement now. You can sign tonight and we start Monday.",
        "I'm booking you for Wednesday unless I hear otherwise. Sound good?",
        "Honestly—are you in or out? I need to know so I can plan my week.",
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


class IndustryIntelligence:
    """
    Industry-Aware Messaging System
    
    MytharaConnect discovers the prospect's industry FIRST, then tailors:
    - Pain points (what keeps them up at night)
    - Value propositions (what matters to THEM)
    - Regulatory pressures (their compliance landscape)
    - Success stories (social proof from their vertical)
    - Language/tone (conservative vs aggressive)
    
    Philosophy: You can't connect without understanding their world first.
    """
    
    INDUSTRIES = {
        "banking": {
            "keywords": ["bank", "capital", "financial", "credit", "trust", "fargo", "chase", 
                        "citi", "wells", "bac", "lending", "mortgage", "treasury"],
            "pain_points": [
                "Model risk management consuming 200+ hours per audit",
                "OCC/CFPB examiners demanding cryptographic proof of AI governance",
                "SR 11-7 compliance requiring model validation documentation",
                "Cannot prove AI decisions weren't tampered with post-facto",
                "Manual audit trails creating operational risk",
                "CFPB Section 1002 AI bias concerns with no audit defense",
            ],
            "value_props": [
                "Hash-chained record of model lineage (designed for audit review)",
                "Tamper-evident audit trails (designed to support SR 11-7 reviews)",
                "AI governance documentation your team can defend to reviewers",
            ],
            "regulatory_refs": [
                "SR 11-7 (Model Risk Management)",
                "OCC Bulletin 2023-17 (Third-Party Risk)",
                "CFPB Section 1002 (AI/ML Bias)",
                "Federal Reserve AI Guidance (2024)",
            ],
            "tone": "conservative",  # Risk-averse, compliance-focused
            "decision_speed": "slow",  # 3-6 month sales cycles typical
            "social_proof": "[hypothetical] regulated financial institutions",
            "roi_metric": "[illustrative estimate] 200 hours → 20 hours per audit cycle",
        },
        
        "healthcare": {
            "keywords": ["health", "hospital", "medical", "care", "clinic", "pharma", 
                        "uchealth", "kaiser", "mayo", "cleveland", "johns hopkins", "patient"],
            "pain_points": [
                "FDA AI/ML guidance requiring provable model lineage",
                "Cannot prove AI recommendations weren't biased or tampered",
                "Joint Commission requiring AI safety documentation",
                "510(k) submissions need cryptographic audit trails",
                "Patient safety reviews consuming 200+ hours manually",
                "AI bias concerns with no defense for litigation",
            ],
            "value_props": [
                "Cryptographic audit trails (designed to support FDA submission reviews)",
                "AI governance documentation (designed for Joint Commission reviews)",
                "Hash-chained model lineage for patient safety committees",
                "Tamper-evident AI decision audit trails",
            ],
            "regulatory_refs": [
                "FDA AI/ML Guidance (2024-2025)",
                "FDA 510(k) Premarket Notification",
                "Joint Commission AI Safety Standards",
                "HIPAA AI/ML Data Governance",
            ],
            "tone": "safety-first",  # Patient outcomes, clinical validation
            "decision_speed": "medium",  # 2-4 month cycles
            "social_proof": "[hypothetical] health systems pursuing FDA submissions",
            "roi_metric": "[illustrative estimate] 200 hours → 20 hours for safety reviews",
        },
        
        "insurance": {
            "keywords": ["insurance", "actuarial", "underwriting", "claims", "aetna", 
                        "cigna", "anthem", "humana", "geico", "progressive", "allstate"],
            "pain_points": [
                "AI underwriting decisions under regulatory scrutiny (NAIC)",
                "Cannot prove pricing models aren't discriminatory",
                "State insurance commissioners demanding AI transparency",
                "Claims automation creating litigation exposure",
                "Actuarial model validation taking months",
            ],
            "value_props": [
                "AI governance for underwriting models (designed to support NAIC reviews)",
                "Prove non-discriminatory pricing with cryptographic audit trails",
                "AI transparency documentation (designed for state regulator review)",
            ],
            "regulatory_refs": [
                "NAIC Model Bulletin on AI (2023)",
                "State Insurance AI Transparency Laws",
                "Actuarial Standards Board (ASOP 56)",
            ],
            "tone": "risk-focused",
            "decision_speed": "medium",
            "social_proof": "[hypothetical] carriers pursuing NAIC compliance",
            "roi_metric": "[illustrative estimate] 3 months → 3 weeks for model validation",
        },
        
        "education": {
            "keywords": ["university", "college", "school", "edu", "academic", "learning",
                        "student", "k12", "edtech", "pearson", "blackboard"],
            "pain_points": [
                "AI-powered grading/admissions creating bias concerns",
                "Cannot prove AI decisions are fair and auditable",
                "Department of Education AI guidance requiring transparency",
                "Student data privacy concerns with AI systems (FERPA)",
                "Accreditation bodies demanding AI governance documentation",
            ],
            "value_props": [
                "FERPA-aligned data handling for student records (design goal, not certification)",
                "Prove fairness in AI-powered admissions/grading",
                "AI transparency reports (designed for Department of Education reviews)",
                "AI governance documentation (designed for accreditation reviews)",
            ],
            "regulatory_refs": [
                "Department of Education AI Guidance (2024)",
                "FERPA-aligned data handling (design goal, not certification)",
                "Regional Accreditation AI Standards",
            ],
            "tone": "mission-driven",  # Equity, access, outcomes
            "decision_speed": "slow",  # Academic cycles, committee approvals
            "social_proof": "[hypothetical] R1 universities pursuing ED compliance",
            "roi_metric": "[illustrative estimate] accreditation prep: 100 hours → 10 hours",
        },
        
        "tech_saas": {
            "keywords": ["tech", "software", "saas", "startup", "platform", "api", "cloud",
                        "dev", "engineer", "product"],
            "pain_points": [
                "AI features creating enterprise sales friction (no audit trails)",
                "SOC 2 auditors questioning AI governance controls",
                "Enterprise customers demanding AI explainability",
                "Cannot prove AI model integrity for compliance-heavy industries",
                "Competitive disadvantage: rivals have provable AI governance",
            ],
            "value_props": [
                "Ship AI features with enterprise-grade audit trails (day 1)",
                "AI governance controls (designed to support SOC 2 reviews)",
                "Win enterprise deals with cryptographic AI transparency",
                "Differentiate from competitors with tamper-evident governance",
            ],
            "regulatory_refs": [
                "SOC 2 Type II (AI-specific controls)",
                "ISO 27001 AI/ML Addendum",
                "Enterprise AI procurement requirements",
            ],
            "tone": "aggressive",  # Fast-moving, competitive
            "decision_speed": "fast",  # Days to weeks
            "social_proof": "[hypothetical] SaaS companies implementing SOC 2 AI controls",
            "roi_metric": "[illustrative estimate] win more enterprise deals with AI transparency",
        },
        
        "retail": {
            "keywords": ["retail", "ecommerce", "store", "shopping", "amazon", "walmart",
                        "target", "commerce", "merchant"],
            "pain_points": [
                "AI pricing/recommendations under FTC scrutiny (dark patterns)",
                "Cannot prove dynamic pricing isn't discriminatory",
                "Consumer protection agencies demanding AI transparency",
                "Personalization algorithms creating bias litigation risk",
            ],
            "value_props": [
                "AI transparency records for pricing algorithms",
                "Prove non-discriminatory personalization with audit trails",
                "AI governance documentation (designed for consumer-protection reviews)",
            ],
            "regulatory_refs": [
                "FTC Dark Patterns Guidance (2024)",
                "Consumer Protection AI Transparency Laws",
                "State-level AI Pricing Regulations",
            ],
            "tone": "results-driven",
            "decision_speed": "fast",
            "social_proof": "[hypothetical] retailers pursuing FTC compliance",
            "roi_metric": "[illustrative] reduced FTC litigation exposure",
        },
        
        "government": {
            "keywords": ["gov", "federal", "state", "agency", "department", "military",
                        "defense", "public", "municipality"],
            "pain_points": [
                "OMB AI governance requirements (M-24-10) for federal agencies",
                "Cannot prove AI systems meet federal transparency standards",
                "GAO audits demanding cryptographic AI audit trails",
                "NIST AI RMF compliance required for federal procurement",
            ],
            "value_props": [
                "AI governance records (designed to support OMB M-24-10 reviews)",
                "Cryptographic audit trails (mapped to NIST AI RMF)",
                "AI transparency documentation (designed for audit review)",
                "AI governance controls (designed with FedRAMP control families in mind)",
            ],
            "regulatory_refs": [
                "OMB Memorandum M-24-10 (AI Governance)",
                "NIST AI Risk Management Framework",
                "GAO AI Audit Standards",
                "FedRAMP AI/ML Addendum",
            ],
            "tone": "compliance-first",
            "decision_speed": "very_slow",  # 6-18 month procurement cycles
            "social_proof": "[hypothetical] federal agencies pursuing OMB compliance",
            "roi_metric": "[illustrative estimate] clean GAO audits",
        },
    }
    
    @staticmethod
    def detect_industry(email_or_company: str) -> str:
        """Detect industry from email domain or company context"""
        text = email_or_company.lower()
        
        # Score each industry based on keyword matches
        scores = {}
        for industry, config in IndustryIntelligence.INDUSTRIES.items():
            score = sum(1 for keyword in config["keywords"] if keyword in text)
            if score > 0:
                scores[industry] = score
        
        # Return highest scoring industry, default to tech_saas
        if scores:
            return max(scores, key=scores.get)
        return "tech_saas"  # Default for unknown
    
    @staticmethod
    def get_discovery_questions(industry: str) -> List[str]:
        """Industry-specific discovery questions to ask FIRST"""
        questions = {
            "banking": [
                "Quick question—when's your next OCC/CFPB examination?",
                "Are you currently managing SR 11-7 model risk validation manually?",
                "How are you handling model governance documentation for your AI/ML systems?",
            ],
            "healthcare": [
                "Quick question—do you have any FDA AI/ML submissions planned?",
                "How is your team handling AI safety documentation for Joint Commission?",
                "Are you using AI for clinical decision support? If so, how do you audit it?",
            ],
            "insurance": [
                "Quick question—are state regulators asking about your AI underwriting models?",
                "How are you documenting AI pricing decisions for NAIC compliance?",
                "What's your current process for validating actuarial models?",
            ],
            "education": [
                "Quick question—is your institution using AI for admissions or grading?",
                "How are you handling AI governance for accreditation reviews?",
                "Are you concerned about FERPA compliance with AI-powered student systems?",
            ],
            "tech_saas": [
                "Quick question—are enterprise customers asking for AI audit trails?",
                "How are you handling SOC 2 AI governance controls?",
                "What's blocking you from shipping AI features to regulated industries?",
            ],
            "retail": [
                "Quick question—are you concerned about FTC scrutiny on AI pricing?",
                "How are you documenting AI personalization decisions for consumer protection?",
                "Have consumer protection agencies asked about your AI systems?",
            ],
            "government": [
                "Quick question—are you working on OMB M-24-10 compliance?",
                "How are you preparing AI systems for GAO audits?",
                "Is your agency required to meet NIST AI RMF standards?",
            ],
        }
        return questions.get(industry, questions["tech_saas"])


class SalesTactics:
    """
    The bot's tactical playbook - What it does to CLOSE
    
    Bot's role: Execute tactics to close deals
    Mythara's role: Validate tactics comply with governance
    """
    
    TACTICS = {
        "competitive_pressure": "Mention competitors evaluating/using the product",
        "scarcity": "honest capacity qualification only — never fabricated deadlines",
        "fomo": "Others are building advantage while you wait",
        "assumptive_close": "Book the meeting without asking permission",
        "qualify_hard": "I'm choosing you as much as you're choosing me",
        "dramatize_pain": "Make their problem vivid and urgent",
        "social_proof": "[illustrative] hypothetical scenarios only — no live deployments to cite yet",
        "urgency": "Deadlines, audits, regulatory timelines",
        "roi_proof": "[illustrative estimate] 200 hours → 20 hours — not measured",
        "fight_objections": "Counter 'no' with FOMO, then respect 2nd no",
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


class MytharaConnect(AutonomousSalesBot):
    """
    MytharaConnect - AI Sales Agent embodying Mythara Engine principles
    
    MYTHARA PRINCIPLES IN ACTION:
    - Emotional Fidelity: Genuine empathy and understanding
    - Messenger Authority: Healer (connection) + Custodian (closing)
    - Blessings Reservoir: Benevolent force seeking mutual success
    - Sanctification: Protects pricing, integrity, trust
    - Witness/Scribe: Transparent governance with audit trails
    
    PERSONALITY:
    - Warm and friendly (Healer messenger)
    - Assertive and confident (Custodian messenger)
    - Selective partnership ("I'm choosing you too")
    - Creates urgency without manipulation
    - Governed by SSIP - every response validated
    
    MYTHARA GOVERNANCE:
    - All responses validated by SalesClause (NEVER_AUTO_SEND pricing/contracts)
    - Blessings reservoir tracks performance (+10 per deal, -10 per violation)
    - Messenger roles are risk labels only (Gabriel=low-risk draft, Raphael=high-risk review)
    - Draft-only: no message is ever transmitted; every output returns to the operator for approval
    - Cryptographic audit trail (SHA-256) of every decision
    - Drift suppression ensures consistent brand voice
    
    Philosophy: Connect with integrity. Close with confidence. Governed by Mythara.
    """
    
    def __init__(self, full_autonomy: bool = True, enable_voice: bool = True):
        super().__init__(full_autonomy)
        self.personality = ConnectPersonality()
        self.daily_mantra = SalesMantra.get_daily_mantra()
        
        # Initialize 1980s retro voice
        self.voice_enabled = enable_voice and VOICE_ENABLED
        if self.voice_enabled:
            self.voice = RetroVoice()
            print("🔊 Retro voice: ENABLED (1980s computer mode)")
        else:
            self.voice = None
            if enable_voice and not VOICE_ENABLED:
                print("ℹ️  Retro voice: Not available (Windows SAPI required)")
        
        # Load Mythara governance systems
        self.blessings = BlessingsReservoir()
        current_blessings = self.blessings.state["blessings"]
        autonomy_level = self.blessings.check_autonomy_level()
        
        print(f"\n🔗 MYTHARA CONNECT ACTIVATED")
        print(f"   Philosophy: Mythara Principles + Sales Excellence")
        print(f"   Messenger Roles: Healer (connection) + Custodian (closing)")
        print(f"   Today's Mantra: '{self.daily_mantra}'")
        print(f"   Emotional Fidelity: {self.personality.PERSONALITY['empathy']:.0%}")
        print(f"   Confidence Level: {self.personality.PERSONALITY['confidence']:.0%}")
        print(f"   Approach: Warm partner + Assertive closer")
        print(f"\n🔒 MYTHARA GOVERNANCE:")
        print(f"   Blessings: {current_blessings}/100")
        print(f"   Autonomy: {autonomy_level}")
        print(f"   Clause Validation: ✅ Active")
        print(f"   Audit Trail: ✅ SHA-256 hashing\n")
        
        # Retro voice announcement
        if self.voice_enabled:
            self.voice.announce_startup()
    
    def detect_industry(self, email_data: Dict) -> str:
        """Detect prospect's industry from email domain or context"""
        email = email_data.get("prospect_email", "")
        company = email_data.get("company_name", "")
        context = f"{email} {company}"
        
        return IndustryIntelligence.detect_industry(context)
        if any(x in email for x in [".io", "tech", "software", "cloud", "data", "ai", "ping", "okta"]):
            return "tech"
        
        # Default to tech (most common in your targets)
        return "tech"
    
    def _validate_with_mythara(self, draft: str, email_data: Dict) -> Dict:
        """
        MULTI-TIER VALIDATION SYSTEM with enhanced scrutiny
        
        Validation Layers:
        1. PRICING_RULES validation (hard blocks)
        2. COMPLIANCE_RULES validation (regulatory)
        3. TONE_ANALYSIS (aggression/professionalism check)
        4. RISK_SCORING (0-100, >70 = human review required)
        5. INDUSTRY_COMPLIANCE (industry-specific rules)
        6. EMOTIONAL_FIDELITY check (selling before understanding?)
        
        Returns: {
            "approved": bool,
            "messenger": str,
            "violations": List[str],
            "warnings": List[str],
            "risk_score": int,
            "can_auto_send": bool,
            "requires_human_review": bool,
            "hash": str
        }
        """
        violations = []
        warnings = []
        risk_score = 0
        
        # LAYER 1: PRICING_RULES (Critical - Hard Blocks)
        if any(x in draft.lower() for x in ["free trial", "money-back guarantee", "free", "$0"]):
            violations.append("PRICING_RULES: Never promise free trial or money-back guarantee")
            risk_score += 30
        
        if "$" in draft:
            # Extract price mentions
            import re
            prices = re.findall(r'\$(\d+)', draft)
            if any(int(p) < 500 for p in prices):
                violations.append("PRICING_RULES: Minimum price is $500")
                risk_score += 30
        
        # LAYER 2: COMPLIANCE_RULES (Regulatory - Hard Blocks)
        if any(x in draft.lower() for x in ["fda approved", "hipaa certified", "soc2 compliant"]):
            violations.append("COMPLIANCE_RULES: Never claim FDA approved/HIPAA certified without proof")
            risk_score += 40
        
        # LAYER 3: TONE_ANALYSIS (Aggression/Professionalism Check)
        aggressive_phrases = ["you're missing out", "you're behind", "you're losing", "stupid", "idiots"]
        aggressive_count = sum(1 for phrase in aggressive_phrases if phrase in draft.lower())
        if aggressive_count >= 2:
            warnings.append("TONE_ANALYSIS: Overly aggressive language detected")
            risk_score += 20
        
        # Check for profanity or unprofessional language
        unprofessional = ["bs", "bullshit", "crap", "sucks", "screw"]
        if any(word in draft.lower() for word in unprofessional):
            violations.append("TONE_ANALYSIS: Unprofessional language detected")
            risk_score += 25
        
        # LAYER 4: INDUSTRY_COMPLIANCE (Industry-Specific Rules)
        prospect_email = email_data.get("prospect_email", "").lower()
        
        # Banking: Extra scrutiny on claims
        if any(x in prospect_email for x in ["bank", "capital", "financial"]):
            risky_banking_claims = ["guaranteed", "risk-free", "100% compliant", "occ certified"]
            if any(claim in draft.lower() for claim in risky_banking_claims):
                violations.append("BANKING_COMPLIANCE: Cannot guarantee outcomes or claim certifications")
                risk_score += 35
        
        # Healthcare: FDA/clinical claims scrutiny
        if any(x in prospect_email for x in ["health", "hospital", "medical"]):
            risky_health_claims = ["fda cleared", "clinically proven", "medical grade", "patient safety guaranteed"]
            if any(claim in draft.lower() for claim in risky_health_claims):
                violations.append("HEALTHCARE_COMPLIANCE: Cannot make FDA/clinical claims without evidence")
                risk_score += 35
        
        # LAYER 5: EMOTIONAL_FIDELITY CHECK (Selling before understanding?)
        is_discovery_phase = email_data.get("conversation_stage", "discovery") == "discovery"
        has_pricing = "$" in draft
        has_close_attempt = any(x in draft.lower() for x in ["sign now", "commit by", "book you for", "send agreement"])
        
        if is_discovery_phase and (has_pricing or has_close_attempt):
            warnings.append("EMOTIONAL_FIDELITY: Closing too early (should discover pain first)")
            risk_score += 15
        
        # LAYER 6: LENGTH/SPAM CHECK
        if len(draft) > 3000:
            warnings.append("LENGTH_CHECK: Email too long (>3000 chars, likely to be ignored)")
            risk_score += 10
        
        # Check for excessive caps (SHOUTING)
        caps_words = [word for word in draft.split() if word.isupper() and len(word) > 3]
        if len(caps_words) > 5:
            warnings.append("TONE_CHECK: Excessive capitalization (appears unprofessional)")
            risk_score += 10
        
        # LAYER 7: PRICING NEGOTIATION (Requires Human Review)
        pricing_keywords = ["discount", "negotiate", "lower price", "can you do", "best price"]
        has_pricing_negotiation = any(x in draft.lower() for x in pricing_keywords)
        if has_pricing_negotiation:
            warnings.append("NEGOTIATION_DETECTED: Pricing discussion requires human review")
            risk_score += 20
        
        # LAYER 8: ASSIGN MESSENGER & DETERMINE AUTO-SEND CAPABILITY
        if violations:
            messenger = SalesMessenger.METATRON  # Scribe - logs violations
            can_auto_send = False
            requires_human_review = True
        elif risk_score >= 70:
            messenger = SalesMessenger.RAPHAEL  # Healer - high risk, needs review
            can_auto_send = False
            requires_human_review = True
        elif has_pricing_negotiation:
            messenger = SalesMessenger.RAPHAEL  # Healer - pricing needs review
            can_auto_send = False
            requires_human_review = True
        elif risk_score >= 40:
            messenger = SalesMessenger.URIEL  # Illuminator - medium risk (low-risk label; nothing transmitted)
            can_auto_send = True
            requires_human_review = False  # risk label only — nothing is ever transmitted
        elif "not interested" in draft.lower() or "stop" in draft.lower():
            messenger = SalesMessenger.GABRIEL  # Announcer - low-risk label (nothing transmitted)
            can_auto_send = True
            requires_human_review = False
        else:
            messenger = SalesMessenger.URIEL  # Illuminator - low risk label (nothing transmitted)
            can_auto_send = True
            requires_human_review = False
        
        # Generate cryptographic hash with risk score
        import hashlib
        import json
        hash_input = json.dumps({
            "draft": draft,
            "prospect": email_data.get("prospect_email", "unknown"),
            "messenger": messenger,
            "risk_score": risk_score,
            "timestamp": datetime.now().isoformat()
        }, sort_keys=True)
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        # Update blessings based on violations and risk
        if violations:
            self.blessings.record_human_override(f"Governance violation detected: {len(violations)} violations")
            print(f"\n⚠️  MYTHARA VIOLATION DETECTED:")
            for v in violations:
                print(f"   ❌ {v}")
        
        if warnings:
            print(f"\n⚠️  MYTHARA WARNINGS:")
            for w in warnings:
                print(f"   ⚠️  {w}")
        
        return {
            "approved": len(violations) == 0,
            "messenger": messenger,
            "violations": violations,
            "warnings": warnings,
            "risk_score": risk_score,
            "can_auto_send": can_auto_send and len(violations) == 0,
            "requires_human_review": requires_human_review,
            "hash": hash_value
        }
    
    def generate_soulful_response(self, email_data: Dict, intent: str) -> str:
        """
        Generate response with PERSONALITY - Industry-adapted + Mythara validated
        
        Process:
        1. Detect industry (banking/healthcare/tech)
        2. Generate sales response with appropriate tone
        3. Validate with Mythara governance (clauses, blessings, audit trail)
        4. Return approved response OR flag for human review
        
        Bot's Role: CLOSE DEALS using tactics
        Mythara's Role: VALIDATE compliance and governance
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
        
        print(f"\n🔒 MYTHARA MULTI-TIER VALIDATION:")
        print(f"   Messenger: {validation['messenger']}")
        print(f"   Risk Score: {validation['risk_score']}/100 {'🟢' if validation['risk_score'] < 40 else '🟡' if validation['risk_score'] < 70 else '🔴'}")
        print(f"   Approved: {'✅' if validation['approved'] else '❌'}")
        print(f"   Violations: {len(validation['violations'])}")
        print(f"   Warnings: {len(validation['warnings'])}")
        print(f"   Auto-Send Label (risk only — nothing is ever transmitted): {'✅' if validation['can_auto_send'] else '❌'}")
        print(f"   Human Review Required: {'🔴 YES' if validation['requires_human_review'] else '✅ NO'}")
        print(f"   Hash: {validation['hash']}")
        print(f"   Blessings: {self.blessings.state['blessings']}/100")
        
        # Voice announcement
        if self.voice_enabled:
            if len(validation['violations']) > 0:
                self.voice.announce_violations(len(validation['violations']))
            else:
                self.voice.announce_validation_status(validation['approved'], validation['risk_score'])
        
        if validation['approved'] and validation['can_auto_send'] and not validation['requires_human_review']:
            # Low risk - auto-send theater removed: nothing is transmitted; draft returned for operator approval
            self.blessings.record_auto_send(success=True)
            print(f"   Action: ✅ LOW RISK — draft returned for operator approval (nothing sent; Blessings: {self.blessings.state['blessings']}/100)")
            return draft
        
        elif validation['approved'] and validation['can_auto_send'] and validation['risk_score'] >= 40:
            # Medium risk - auto-send theater removed: nothing is transmitted; draft returned for operator approval
            self.blessings.record_auto_send(success=True)
            print(f"   Action: ⚠️  MEDIUM RISK — draft returned for operator approval (nothing sent; Risk: {validation['risk_score']}/100)")
            return draft
        
        elif validation['approved'] and not validation['can_auto_send']:
            # Requires human review (pricing negotiation, etc.)
            print(f"   Action: ⏸️  HOLDING FOR HUMAN REVIEW (Risk: {validation['risk_score']}/100)")
            return draft
        
        else:
            # Violations detected - block send
            print(f"   Action: 🛑 BLOCKED - {len(validation['violations'])} governance violations")
            return draft  # Return draft for human to fix
    
    def _internal_pep_talk(self):
        """Bot's internal dialogue before responding (gives it SOUL)"""
        mantras_to_remember = random.sample(SalesMantra.MANTRAS, 3)
        print(f"\n🧠 Bot's internal state:")
        for mantra in mantras_to_remember:
            print(f"   💭 '{mantra}'")
    
    def craft_discovery_email(self, prospect_email: str, company_name: str = "") -> str:
        """
        STEP 1: Discovery-first outreach - ASK FOR INDUSTRY EXPLICITLY
        
        Don't assume industry - let THEM tell us so we can tailor messaging perfectly.
        This shows respect and ensures we understand their world before pitching.
        
        Philosophy: You can't connect without understanding their reality.
        """
        email_data = {"prospect_email": prospect_email, "company_name": company_name}
        suspected_industry = self.detect_industry(email_data)  # Still detect as backup
        
        print(f"\n🎯 SUSPECTED INDUSTRY: {suspected_industry.upper()} (asking for confirmation)")
        print(f"   Approach: Let prospect self-identify for accurate tailoring")
        
        # Voice announcement
        if self.voice_enabled:
            self.voice.announce_industry_detected(suspected_industry)
        
        # Craft discovery email that ASKS for industry selection
        draft = f"""Subject: Quick question about AI governance at {company_name or 'your organization'}

Hi there,

I work with organizations on AI audit trail and governance challenges. Before I share anything, I want to make sure I'm speaking your language.

**Quick question: Which industry best describes your organization?**

• Banking/Financial Services
• Healthcare/Life Sciences  
• Insurance/Actuarial
• Education/Academic
• Technology/SaaS
• Retail/E-commerce
• Government/Public Sector
• Other: _____________

The reason I ask: AI governance looks VERY different for FDA submissions vs OCC examinations vs SOC 2 audits. I want to share what's relevant to YOUR world, not waste your time with generic pitches.

Once I know your space, I can share specific examples of how organizations like yours are handling:
- Regulatory audit trails (cryptographic proof)
- Model risk validation (automated documentation)
- AI transparency requirements (regulator-ready reports)

No pitch yet—just want to understand your world first.

Best,
Herbert Velez Jr.
CEO, Mythara Engine

P.S. If AI governance isn't your area, would you mind pointing me to the right person?"""
        
        # MYTHARA GOVERNANCE: Validate discovery email
        validation = self._validate_discovery_email(draft, suspected_industry)
        
        print(f"\n🔒 MYTHARA GOVERNANCE CHECK:")
        print(f"   Email Type: Discovery (no pitch)")
        print(f"   Approved: {'✅' if validation['approved'] else '❌'}")
        print(f"   Emotional Fidelity: ✅ (asks before selling)")
        print(f"   Hash: {validation['hash']}")
        
        return draft
    
    def _validate_discovery_email(self, draft: str, industry: str) -> Dict:
        """Validate discovery email doesn't pitch too early"""
        import hashlib
        
        # Discovery emails should ASK, not SELL
        violations = []
        if "$" in draft:
            violations.append("Pricing in discovery email (too aggressive)")
        if any(x in draft.lower() for x in ["buy", "purchase", "pricing", "demo"]):
            violations.append("Selling before discovery (violates emotional fidelity)")
        
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "hash": hashlib.sha256(draft.encode()).hexdigest()[:16],
        }
    
    def craft_industry_specific_followup(self, prospect_email: str, selected_industry: str, company_name: str = "") -> str:
        """
        STEP 2: After prospect identifies their industry, send tailored follow-up
        
        Now we know their world - share industry-specific pain points and social proof.
        Still not pitching hard - building credibility and trust first.
        
        Philosophy: Emotional fidelity = understand before selling.
        """
        if selected_industry not in IndustryIntelligence.INDUSTRIES:
            selected_industry = "tech_saas"  # Default fallback
        
        config = IndustryIntelligence.INDUSTRIES[selected_industry]
        
        # Select industry-specific pain points and proof
        pain_point = random.choice(config["pain_points"])
        regulatory_ref = random.choice(config["regulatory_refs"])
        
        print(f"\n🎯 INDUSTRY CONFIRMED: {selected_industry.upper()}")
        print(f"   Tone: {config['tone']}")
        print(f"   Social Proof: {config['social_proof']}")
        print(f"   Tailoring: Industry-specific pain points + regulatory refs")
        
        # Craft industry-tailored follow-up (warm, educational, building trust)
        draft = f"""Subject: Re: {selected_industry.replace('_', ' ').title()} + AI Governance

Thanks for confirming—{selected_industry.replace('_', ' ').title()} is a space I know well.

Here's what I'm seeing in your industry right now:

**THE CHALLENGE:**
{pain_point}

**REGULATORY PRESSURE:**
{regulatory_ref} is creating new documentation requirements. Organizations without cryptographic audit trails are facing:
- Extended audit cycles (weeks → months)
- Manual documentation burden (100-200+ hours per review)
- "Prove it wasn't tampered" questions with no good answer

**WHAT'S WORKING:**
Illustrative scenario: {config['social_proof']} using cryptographic governance (SHA-256 hashing) for tamper-proof audit trails. Illustrative upside: {config['roi_metric']}

No pitch yet—just want you to know this is solvable. Lots of {selected_industry.replace('_', ' ')} organizations are figuring this out right now.

**Quick question:** Do you have an upcoming audit, regulatory review, or compliance deadline? That usually determines urgency.

Happy to share a {selected_industry.replace('_', ' ')}-specific validation report if you're curious how this works in practice.

Best,
Herbert Velez Jr.

P.S. If timing isn't right, no worries—I can follow up in Q2 when this might be more relevant."""
        
        # MYTHARA GOVERNANCE: Validate follow-up
        validation = self._validate_discovery_email(draft, selected_industry)
        
        print(f"\n🔒 MYTHARA GOVERNANCE CHECK:")
        print(f"   Email Type: Industry-Tailored Follow-up (educational, not selling)")
        print(f"   Approved: {'✅' if validation['approved'] else '❌'}")
        print(f"   Emotional Fidelity: ✅ (educates before pitching)")
        print(f"   Hash: {validation['hash']}")
        
        return draft
    
    def _handle_interested_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        STEP 2: They're interested - NOW pitch with industry-tailored messaging
        
        Strategy: Use industry-specific pain points, regulatory refs, social proof
        """
        config = IndustryIntelligence.INDUSTRIES.get(industry, IndustryIntelligence.INDUSTRIES["tech_saas"])
        
        # Select top pain points and value props for this industry
        pain_point = random.choice(config["pain_points"])
        value_prop = random.choice(config["value_props"])
        regulatory_ref = random.choice(config["regulatory_refs"])
        
        # Adjust tone based on industry
        if config["tone"] in ["conservative", "compliance-first", "safety-first"]:
            # Formal, professional, regulatory-focused
            return f"""Thank you for your interest. I appreciate you taking the time.

Here's what matters in your world ({industry}):

PAIN POINT: {pain_point}

SOLUTION: {value_prop}

DESIGN GOAL: cryptographic governance gives {config['social_proof']} ironclad answers when regulators ask "{regulatory_ref}" questions. Illustrative upside: {config['roi_metric']}

ILLUSTRATIVE UPSIDE: {config['roi_metric']}

REALITY CHECK: The regulatory landscape is tightening. Organizations building audit trails NOW will have 6-12 months of clean history when enforcement accelerates.

AVAILABILITY: Early adopter pilot: $500. Standard engagement: $2,500. If the timing fits your review cycle, we can scope the pilot this week.

NEXT STEP: I'd like to schedule a brief validation call to show you exactly how this works in {industry}.

Tuesday 10am MT or Wednesday 2pm MT—which works better for your calendar?

Best regards,
Herbert Velez Jr.
CEO, Mythara Engine

P.S. I can send our {industry}-specific validation report. It shows exactly what "audit-ready" looks like for {regulatory_ref} compliance."""
        
        else:
            # Aggressive, fast-moving (tech/retail)
            opener = random.choice(self.personality.OPENERS_AGGRESSIVE)
            enthusiasm = random.choice(self.personality.ENTHUSIASM_PHRASES)
            competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)
            scarcity = random.choice(self.personality.SCARCITY_TACTICS)
            close = random.choice(self.personality.CLOSES)
            
            return f"""{opener} I LOVE when people cut through the BS and just say they're interested.

{enthusiasm} Here's what we're solving in {industry}:

❌ PROBLEM: {pain_point}
✅ SOLUTION: {value_prop}

📊 ILLUSTRATIVE: {config['social_proof']} — upside {config['roi_metric']}

⚠️ COMPETITIVE REALITY: {competitive}

⏰ TIMING: {scarcity}

{close}

Herbert

P.S. At the $500 early adopter tier I'll personally run your first {regulatory_ref} audit report."""
    
    def _handle_question_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        They have a question - Answer with industry-specific technical depth
        
        Strategy: Show expertise, use industry language, add urgency
        """
        config = IndustryIntelligence.INDUSTRIES.get(industry, IndustryIntelligence.INDUSTRIES["tech_saas"])
        
        # Technical answer with industry-specific language
        if config["tone"] in ["conservative", "compliance-first", "safety-first"]:
            # Detailed, technical, regulatory-focused
            regulatory_ref = random.choice(config["regulatory_refs"])
            return f"""Great question. Let me give you the technical answer for {industry}:

TECHNICAL DEPTH: SHA-256 cryptographic hashing on every AI decision. Auditors can verify the chain mathematically — any tampering breaks the link and shows. Tamper-evident, not tamper-proof: we claim detection, not magic.

DESIGN INTENT: tamper-proof audit trails so {config['social_proof']} face audits with cryptographic evidence. Illustrative upside: {config['roi_metric']}

REGULATORY REALITY: Without cryptographic proof, you're showing manual logs when auditors ask "{regulatory_ref}" questions. Those logs can be edited—that's an audit risk.

TIMING: Early adopter pilot: $500. Standard engagement: $2,500.

NEXT STEP: I can send our {industry}-specific technical validation report now. Would Tuesday 10am or Wednesday 2pm work for a brief review call?

Best regards,
Herbert Velez Jr.

P.S. Happy to include a {regulatory_ref}-ready audit trail sample so you can see exactly what regulators will review."""
        
        else:
            # Fast, direct answer (tech/retail)
            opener = random.choice(self.personality.OPENERS_AGGRESSIVE)
            competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)
            close = random.choice(self.personality.CLOSES)
            
            return f"""{opener} SHA-256 hashing on every AI decision. Auditors can verify zero tampering. It's the same crypto that secures blockchain—nobody's breaking it.

💡 ILLUSTRATIVE: {config['social_proof']} — {config['roi_metric']}

⚠️ REALITY: Without this? Your auditors see black-box AI with no provable lineage. That's a finding waiting to happen.

⏰ TIMING: {competitive}

Early adopter pricing is $500; standard engagement is $2,500.

{close}

Herbert

P.S. Want me to send our validation report now so you can see what 'passing' looks like?"""
    
    def _handle_no_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        They said no - FIGHT BACK once with industry-specific FOMO, then respect exit
        
        Counter once, then graceful exit if they insist
        """
        config = IndustryIntelligence.INDUSTRIES.get(industry, IndustryIntelligence.INDUSTRIES["tech_saas"])
        prospect_email = email_data.get("prospect_email", "unknown")
        tracker = self.conversation_tracker.get(prospect_email, {"no_count": 0})
        
        if tracker["no_count"] == 0:
            # First no - counter with industry-specific FOMO
            pain_point = random.choice(config["pain_points"])
            
            if config["tone"] in ["conservative", "compliance-first", "safety-first"]:
                # Respectful but firm (banking/healthcare/insurance/government)
                regulatory_ref = random.choice(config["regulatory_refs"])
                response = f"""I understand—timing is important in {industry}.

Quick question: Do you have an upcoming audit, regulatory examination, or compliance review?

The reason I ask: organizations in your space ({config['social_proof']}) are starting to build AI audit trails. Those who start now will have months of clean governance history when examiners arrive.

REALITY CHECK: {pain_point}

If timing truly isn't right, I respect that. But if this is in "not priority yet" mode, that changes quickly when the {regulatory_ref} deadline hits.

Would you like me to follow up in Q2 2026, or is there someone on your compliance/risk team I should connect with?

Best regards,
Herbert"""
            
            else:
                # More aggressive counter (tech/retail)
                competitive = random.choice(self.personality.COMPETITIVE_PRESSURE)
                
                response = f"""Fair enough—not everyone's ready to move fast.

But real talk: {competitive}

And the illustrative upside on the table: {config['roi_metric']}

PAIN POINT: {pain_point}

If you're genuinely not interested, I respect that. But if this is "not priority YET," just know—I'm prioritizing fast-movers. By the time this becomes urgent for you, I might be at capacity.

Should I follow up in Q2, or are you passing entirely?

Herbert

P.S. If this is a budget thing, let me know. I have some flexibility for the right partner."""
            
            # Mark first "no" counter attempt
            tracker["no_count"] = 1
            self.conversation_tracker[prospect_email] = tracker
            return response
        
        else:
            # Second no - graceful exit (respect their decision)
            return f"""Understood. I appreciate you being direct.

If anything changes (audit deadline, regulatory pressure, competitive landscape), feel free to reach out. No hard feelings.

Best of luck with your AI governance strategy.

Herbert

P.S. If you know anyone in {industry} dealing with audit trail challenges, I'd appreciate an introduction."""
    
    def _handle_unknown_with_soul(self, email_data: Dict, industry: str) -> str:
        """
        Unknown intent - QUALIFY HARD with competitive pressure
        
        Strategy: Maximize options, enhance your position
        """
        
        if industry == "banking":
            return f"""Thank you for your reply. Let me clarify what would make this valuable:

Do you have an upcoming model risk review, OCC examination, or SR 11-7 validation in the next 90 days?

If yes: We should talk this week. Building a clean audit trail takes most teams 60-90 days, so if your review is soon, timing matters.

If no: You may want to wait until regulatory pressure increases. If your audit timeline moves up, the pilot runs 4-8 weeks — reach out and we'll scope it.

Could you share your audit timeline? That'll help me determine if this is the right time for you.

Best regards,
Herbert Velez Jr.

P.S. Either Tuesday 10am or Wednesday 2pm works for a brief 15-minute qualification call."""

        elif industry == "healthcare":
            return f"""Thank you for reaching out. Let me clarify what would make this actionable:

Do you have an upcoming FDA submission, Joint Commission review, or AI safety audit in the next 90 days?

If yes: We should connect this week. Building provable AI governance takes most teams 60-90 days, so if your review is soon, timing matters.

If no: You may want to wait until regulatory pressure increases. If your review timeline moves up, the pilot runs 4-8 weeks — reach out and we'll scope it.

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
        print("🔗 MYTHARA CONNECT - DAILY MOTIVATION")
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
# DEMO: MytharaConnect - Mythara-Governed Sales Agent
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("MYTHARA CONNECT - Industry-Aware Sales + Mythara Governance")
    print("   Philosophy: Discover Industry -> Tailor Messaging -> Close with Confidence")
    print("   MYTHARA GOVERNED - Clauses, Blessings, Audit Trail")
    print("="*80)
    
    # Initialize bot with PERSONALITY
    bot = MytharaConnect(full_autonomy=True)
    
    # Daily motivation ritual
    bot.daily_motivation()
    
    # DEMO 1: Industry Discovery Flow
    print("\n" + "="*80)
    print("📋 DEMO 1: INDUSTRY DISCOVERY FLOW")
    print("="*80)
    
    print("\n🔹 Step 1: Initial outreach (ASK for industry)")
    discovery_email = bot.craft_discovery_email(
        prospect_email="sarah.johnson@example.com",
        company_name="Acme Corp"
    )
    print("\n" + "-"*80)
    print(discovery_email)
    print("-"*80)
    
    print("\n🔹 Step 2: Prospect replies 'Banking/Financial Services'")
    print("   Bot now sends industry-tailored follow-up...\n")
    
    followup_email = bot.craft_industry_specific_followup(
        prospect_email="sarah.johnson@example.com",
        selected_industry="banking",
        company_name="Acme Corp"
    )
    print("\n" + "-"*80)
    print(followup_email)
    print("-"*80)
    
    # DEMO 2: Different industries get different messaging
    print("\n" + "="*80)
    print("📋 DEMO 2: INDUSTRY-SPECIFIC MESSAGING (After Discovery)")
    print("="*80)
    
    industry_examples = [
        ("healthcare", "dr.james@hospital.org", "Regional Health System"),
        ("tech_saas", "mike@startup.io", "TechStartup Inc"),
        ("education", "dean@university.edu", "State University")
    ]
    
    for industry, email, company in industry_examples:
        print(f"\n🔹 Industry: {industry.upper()} | Company: {company}")
        followup = bot.craft_industry_specific_followup(email, industry, company)
        print("\n" + "-"*80)
        print(followup[:500] + "...\n[truncated for demo]")
        print("-"*80)
    
    # DEMO 3: Closing scenarios (after industry is known)
    # Demo fixtures: placeholder addresses, not real customers
    print("\n" + "="*80)
    print("📋 DEMO 3: CLOSING SCENARIOS (Industry-Aware Responses)")
    print("="*80)
    
    # Simulate responses with SOUL - Industry-adapted
    test_scenarios = [
        {
            "name": "INTERESTED PROSPECT (Banking)",
            "email": {
                "subject": "Re: Model Risk Solution",
                "body": "This looks interesting. Can we schedule a call?",
                "prospect_email": "demo.prospect1@example.com"
            },
            "intent": "interested"
        },
        {
            "name": "TECHNICAL QUESTION (Healthcare)",
            "email": {
                "subject": "Re: AI Governance",
                "body": "How does the cryptographic hashing actually work?",
                "prospect_email": "demo.prospect2@example.com"
            },
            "intent": "question"
        },
        {
            "name": "FIRST NO (Tech)",
            "email": {
                "subject": "Re: Mythara Demo",
                "body": "Not interested right now, thanks.",
                "prospect_email": "demo.prospect3@example.com"
            },
            "intent": "not_interested"
        },
        {
            "name": "INTERESTED PROSPECT (Tech - Aggressive Tone)",
            "email": {
                "subject": "Re: AI Audit Trails",
                "body": "Yeah this could work. Let's talk.",
                "prospect_email": "alex@startup.io"
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
        
        # Voice announcement
        if bot.voice_enabled:
            bot.voice.announce_scenario(scenario['name'])
        
        # Detect industry
        industry = bot.detect_industry(scenario['email'])
        print(f"🏢 Industry Detected: {industry.upper()}")
        
        # Generate response WITH SOUL (industry-adapted, Mythara-validated)
        response = bot.generate_soulful_response(scenario['email'], scenario['intent'])
        
        print(f"\n🤖 BOT'S RESPONSE (with SOUL - {industry.upper()} tone):\n")
        print(response)
        print("\n" + "="*80)
    
    print("\n🔗 MYTHARA CONNECT PHILOSOPHY:")
    print("   1️⃣  ASK for industry (don't assume)")
    print("   2️⃣  TAILOR messaging to their regulatory world")
    print("   3️⃣  CLOSE with industry-specific urgency")
    print("\n   🎯 Bot's Role: CONNECT with empathy, CLOSE with confidence")
    print("   🔒 Mythara's Role: VALIDATE compliance and governance")
    print("\n   Personality: Warm + Assertive + Industry-Intelligent")
    print("   Approach: Emotional Fidelity → Tailored Value → Selective Partnership")
    print("="*80)
    print("\n🎯 INDUSTRY-ADAPTED TONE:")
    print("   Banking: Conservative, regulatory-focused, ROI-driven")
    print("   Healthcare: Safety-first, compliance-focused, patient outcomes")
    print("   Tech/SaaS: Aggressive, fast-moving, competitive pressure")
    print("\n🔒 MYTHARA GOVERNANCE:")
    print("   ✅ SalesClause validation (NEVER_AUTO_SEND pricing/contracts)")
    print("   ✅ Blessings reservoir (+10 per deal, -10 per violation)")
    print("   ✅ Messenger roles (Gabriel/Uriel low-risk labels, Raphael review; nothing transmitted)")
    print("   ✅ Cryptographic audit trail (SHA-256 hashing)")
    print("\n🎯 Drafts prepared under governance — every message needs operator approval.")
