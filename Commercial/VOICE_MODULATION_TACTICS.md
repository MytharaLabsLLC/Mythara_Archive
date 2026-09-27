# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Sales Conversation Flow - Voice Modulation Tactics

Design plan for the VoIP AI sales bot upgrade (not yet built — tabled until
the email outreach bot produces real revenue; see VOIP_BOT_SUMMARY.py).
This document defines WHEN and HOW to modulate voice tone during sales calls.

Key Insight: Voice tone matters MORE than words.
   - "Yes" said confidently = assumptive close
   - "Yes" said hesitantly = needs more nurturing

Ground rules for every script below (Track B, plain modern voice):
   - No fake scarcity ("2 slots left", "pricing goes up Friday"). Urgency
     comes only from real deadlines the prospect names.
   - No invented proof ("banks save 6 weeks", "most clients see ROI in X").
     We describe what the system does, not results we haven't measured.
   - No customer claims. We have no confirmed enterprise customers yet,
     and no script may imply otherwise.
"""

# ============================================================================
# VOICE MODULATION PARAMETERS
# ============================================================================

VOICE_TONES = {
    "confident": {
        "description": "Assumes the sale, speaks with authority",
        "pitch": "Medium-high",
        "pace": "Steady, deliberate",
        "volume": "Strong",
        "use_cases": [
            "Opening (establishing credibility)",
            "Pricing discussion (state the price plainly, no apology)",
            "Assumptive close (So when should we kick off?)",
            "Handling 'too expensive' objection (reframe as investment)"
        ],
        "example": "Standard tier is $2,500. That gets you the full clause "
                   "library plus a hash-chained audit trail on every decision. "
                   "When do you want to start?"
    },

    "empathetic": {
        "description": "Shows understanding, builds trust",
        "pitch": "Medium-low",
        "pace": "Slower, more pauses",
        "volume": "Softer",
        "use_cases": [
            "Prospect expresses concern",
            "Handling 'not the right time' objection",
            "After prospect says 'no' first time",
            "When prospect mentions budget constraints"
        ],
        "example": "I get it — compliance work always competes with revenue "
                   "priorities. That's why the pilot is 4 to 8 weeks: less "
                   "disruption, and you see the audit trail working before "
                   "you commit to anything."
    },

    "urgent": {
        "description": "Signals real time pressure — never manufactured",
        "pitch": "Slightly higher",
        "pace": "Faster",
        "volume": "Strong",
        "use_cases": [
            "Prospect is interested but delaying",
            "Real deadline the prospect named (audit date, quarter close)",
            "Regulatory window the prospect is facing",
        ],
        "rules": [
            "NEVER invent scarcity (no 'slots left', no fake price hikes).",
            "Urgency must trace to a date the prospect actually stated.",
            "If there is no real deadline, stay in confident or empathetic."
        ],
        "example": "If this needs to be in place before your December audit, "
                   "we'd need to start this week to finish the pilot in time. "
                   "Does that date still hold?"
    },

    "professional": {
        "description": "Formal, conservative, regulatory-focused",
        "pitch": "Medium",
        "pace": "Measured, deliberate",
        "volume": "Even",
        "use_cases": [
            "Banking industry (OCC, CFPB, SR 11-7)",
            "Healthcare (FDA, HIPAA, patient safety)",
            "Legal/compliance buyers",
            "Enterprise procurement"
        ],
        "example": "Mythara gives you a tamper-evident, hash-chained record of "
                   "every clause decision — the kind of audit trail model-risk "
                   "reviewers ask for. We don't claim certifications we haven't "
                   "earned. What you get is the evidence, ready for your "
                   "auditors to examine."
    },

    "casual": {
        "description": "Fast-paced, direct, no corporate speak",
        "pitch": "Medium-high",
        "pace": "Faster",
        "volume": "Energetic",
        "use_cases": [
            "Tech/SaaS industry",
            "Startup buyers",
            "Engineers/developers",
            "West Coast companies"
        ],
        "example": "Real talk — unaudited AI output is a liability, and manual "
                   "review doesn't scale. We can scope a pilot this week so "
                   "you see the audit trail on your own data. Want to look?"
    }
}

# ============================================================================
# REAL-TIME TONE SWITCHING (Mid-Call Adjustments)
# ============================================================================

TONE_SWITCHING_TRIGGERS = {
    "prospect_hesitates": {
        "detection": "Prospect says 'um', 'uh', long pause, voice trails off",
        "current_tone": "confident",
        "switch_to": "empathetic",
        "reasoning": "Confidence feels pushy when prospect is uncertain",
        "example_response": "I hear you — this is a real decision. Let me ask: "
                            "what's your biggest concern right now?"
    },

    "prospect_asks_price": {
        "detection": "What does this cost? / What's the price?",
        "current_tone": "any",
        "switch_to": "confident",
        "reasoning": "Never apologize for price. State it plainly.",
        "example_response": "$2,500 for the standard tier. That includes the "
                            "full clause library and the hash-chained audit "
                            "trail. When do you want to start?"
    },

    "prospect_says_too_expensive": {
        "detection": "That's too expensive / Out of budget / Can't afford",
        "current_tone": "any",
        "switch_to": "confident → empathetic",
        "reasoning": "Reframe as investment, empathize. No fake ROI numbers — "
                     "we haven't measured prospect outcomes, so we don't cite them.",
        "example_response":
            "(Confident) I get it — $2,500 is real money. "
            "(Empathetic) Here's the honest framing: you're buying an audit "
            "trail you can show a regulator, not a promise. The 4-to-8-week "
            "pilot is the low-risk way to see whether it's worth it to you."
    },

    "prospect_mentions_competitor": {
        "detection": "We're looking at [competitor] / Talking to other vendors",
        "current_tone": "any",
        "switch_to": "casual → confident",
        "reasoning": "Acknowledge competition, then state what we actually do "
                     "differently — without claiming customers we don't have.",
        "example_response":
            "(Casual) Of course you are — you'd be crazy not to shop around. "
            "(Confident) Here's the difference as we see it: most tools give "
            "you answers. We give you a tamper-evident, hash-chained record "
            "of every decision, so you can prove what the system did and why."
    },

    "prospect_interested_but_delaying": {
        "detection": "This looks great / I like it / Let me think about it",
        "current_tone": "any",
        "switch_to": "urgent (only if a real deadline exists)",
        "reasoning": "Interest = buying signal. But urgency must be real — "
                     "ask for their deadline, don't invent one.",
        "example_response":
            "Love it. What timeline are you working against? If there's a "
            "real date — an audit, a launch — we can plan the pilot around "
            "it. If not, no pressure; I'll check back next quarter."
    },

    "prospect_asks_compliance_question": {
        "detection": "Is this FDA approved? / HIPAA compliant? / SOC 2?",
        "current_tone": "any",
        "switch_to": "professional",
        "reasoning": "Compliance questions demand formal, precise answers. "
                     "Never claim a certification we don't hold.",
        "example_response":
            "Good question, and I'll be straight with you. We provide the "
            "cryptographic framework that SUPPORTS your compliance posture — "
            "hash-chained, tamper-evident records. We are not FDA approved, "
            "we are not SOC 2 certified, and we don't claim to be. Think of "
            "us as the seal on the record — the thing that makes YOUR system "
            "auditable."
    },

    "prospect_first_no": {
        "detection": "Not interested / No thanks / Wrong time",
        "current_tone": "any",
        "switch_to": "empathetic → casual",
        "reasoning": "First 'no' is reflex. Empathize, then give them permission to say real no",
        "example_response":
            "(Empathetic) I hear you — everyone's slammed right now. "
            "(Casual) Real question: is it the solution you're not into, "
            "or just the timing? If it's timing, we can circle back next "
            "quarter."
    },

    "prospect_second_no": {
        "detection": "Still no / Really not interested / Please stop",
        "current_tone": "any",
        "switch_to": "professional → exit gracefully",
        "reasoning": "Two nos = respect their decision, preserve relationship",
        "example_response":
            "Totally respect that. I'll add you to our quarterly check-in "
            "list — if anything changes, I'll ping you. Sound fair?"
    },

    "prospect_third_no": {
        "detection": "I said no / Stop calling / Remove me",
        "current_tone": "any",
        "switch_to": "professional → quit immediately",
        "reasoning": "Three nos = TCPA violation risk, brand damage. "
                     "Suppress immediately, no exceptions.",
        "example_response":
            "Got it. You're off the list. Have a great day."
    }
}

# ============================================================================
# INDUSTRY-SPECIFIC VOICE PERSONAS
# ============================================================================

INDUSTRY_PERSONAS = {
    "banking": {
        "default_tone": "professional",
        "tone_mix": {
            "professional": 60,  # Primary
            "confident": 30,     # When discussing scope
            "empathetic": 10     # When handling objections
        },
        "vocabulary": [
            "OCC Bulletin 2011-12",
            "SR 11-7",
            "CFPB oversight",
            "Model risk management",
            "Tamper-evident seal",
            "Cryptographic hashing",
            "Regulatory audit",
            "Compliance framework"
        ],
        "avoid": [
            "Disrupt", "Innovate", "Synergy" (too startup-y),
            "Cheap", "Quick fix" (undermines enterprise value),
            "Guaranteed compliance" (legal liability),
            "SOC 2 certified" (we are not — never claim it)
        ],
        "example_opening":
            "(Professional) Hi [Name], Herbert Velez from Mythara. We build a "
            "tamper-evident audit trail for AI decisions — hash-chained, so "
            "your model-risk reviewers can verify what the system did and "
            "why. Do you have 2 minutes?"
    },

    "healthcare": {
        "default_tone": "professional",
        "tone_mix": {
            "professional": 50,
            "empathetic": 30,   # Healthcare = patient-centered
            "confident": 20
        },
        "vocabulary": [
            "Patient safety",
            "FDA 21 CFR Part 11",
            "HIPAA compliance",
            "Clinical validation",
            "Tamper-evident audit trail",
            "Data integrity",
            "Electronic signatures",
            "GxP compliance"
        ],
        "avoid": [
            "Move fast", "Break things" (opposite of healthcare values),
            "Cheap", "Quick" (implies cutting corners on safety),
            "FDA approved" (we are not — never claim it)
        ],
        "example_opening":
            "(Professional) Hi [Name], Herbert Velez from Mythara. We give AI "
            "systems a tamper-evident record of every decision, so there's "
            "an audit trail your compliance team can actually inspect. "
            "(Empathetic) I know patient safety drives everything you do — "
            "that's the bar we built for. Do you have 3 minutes?"
    },

    "tech_saas": {
        "default_tone": "casual",
        "tone_mix": {
            "casual": 50,
            "confident": 30,
            "urgent": 20        # Tech buyers = deadline-driven, but keep it real
        },
        "vocabulary": [
            "API-first",
            "Plug-and-play",
            "Ship faster",
            "Pilot in weeks",
            "Audit-ready",
            "First-mover advantage",
            "Dev-friendly",
            "Zero infrastructure"
        ],
        "avoid": [
            "Lengthy implementation" (tech = impatient),
            "Committee approval" (tech = move fast),
            "Formal RFP process" (tech = buy on credit card),
            "Fake scarcity" (tech buyers smell it instantly)
        ],
        "example_opening":
            "(Casual) Hey [Name], Herbert from Mythara. Real talk — AI "
            "output with no audit trail is a liability. (Confident) We can "
            "scope a pilot this week so you see the hash-chained record on "
            "your own data. Want to look?"
    }
}

# ============================================================================
# VOICE CLONING IMPLEMENTATION (ElevenLabs)
# ============================================================================

VOICE_CLONING_PROCESS = """
================================================================================
VOICE CLONING SETUP (ElevenLabs Professional) — PLAN, NOT BUILT
================================================================================

STEP 1: Record 5 Minutes of Clean Audio
   - Use high-quality mic (Blue Yeti, Shure SM7B, or iPhone voice memos)
   - Quiet room (no background noise)
   - Read diverse content:
     * Sales script (confident tone)
     * Empathetic response (softer tone)
     * Urgent pitch (faster pace)
     * Professional intro (measured tone)

STEP 2: Upload to ElevenLabs
   - Go to elevenlabs.io/voice-cloning
   - Upload 5min audio file
   - Name voice: "Herbert_Sales_Confident"
   - Train model (takes 10-15 minutes)

STEP 3: Test Voice Quality
   - Generate test clips with different tones
   - Compare to original voice
   - Iterate if needed (add more samples)

STEP 4: Create Tone Variations
   - Clone 1: "Herbert_Confident" (default)
   - Clone 2: "Herbert_Empathetic" (softer)
   - Clone 3: "Herbert_Urgent" (faster)
   - Clone 4: "Herbert_Professional" (formal)

STEP 5: API Integration
   ```python
   from elevenlabs import generate, set_api_key

   set_api_key("your_api_key")

   audio = generate(
       text="Standard tier is $2,500. When do you want to start?",
       voice="Herbert_Confident",
       model="eleven_monolingual_v1"
   )
   ```

ESTIMATED COST (ElevenLabs published pricing, not yet spent):
   - ElevenLabs Professional: ~$99/month
   - 500,000 characters/month
   - OR pay-as-you-go: ~$0.30 per 1,000 characters

================================================================================
"""

# ============================================================================
# WHY VOICE MODULATION MATTERS (planning notes — not measured results)
# ============================================================================

VALUE_OF_VOICE_MODULATION = """
What this adds to the VoIP bot, if and when it is built:

1. CONSISTENT DELIVERY
   - One voice, five calibrated tones, applied the same way every call.
   - No dependence on which rep picked up the phone.

2. INDUSTRY FIT
   - Banking hears professional and regulatory. Tech hears direct and fast.
   - Healthcare hears patient-centered. The bot matches the room.

3. GOVERNED AUTONOMY
   - Every call recorded and hash-chained into the audit trail.
   - The three-no rule is hard-coded: third no = hang up and suppress.
   - Any future autonomous voice agent goes through the same witness
     gates as the email outreach machine. A blocked verdict never speaks.
   - No false claims by design: the script bank above contains no
     certification the system doesn't hold and no customer it doesn't have.

4. HONEST URGENCY
   - The urgent tone exists for real deadlines only. Fake scarcity is
     banned from every script — a voice that lies about slots will lie
     about everything else, and the audit trail would prove it.

What we do NOT claim:
   - No close rates, no ROI multiples, no revenue projections. The bot
     doesn't exist yet, so there is nothing to measure. Numbers get added
     here only after real calls produce them.
"""

if __name__ == "__main__":
    print("="*80)
    print("Voice Modulation Sales Tactics - VoIP Bot Upgrade (PLAN, not built)")
    print("="*80)
    print("\n5 Voice Tones Defined:")
    for tone in VOICE_TONES:
        print(f"   - {tone.capitalize()}")

    print("\n9 Real-Time Tone Switching Triggers:")
    for i, trigger in enumerate(TONE_SWITCHING_TRIGGERS, 1):
        print(f"   {i}. {trigger.replace('_', ' ').title()}")

    print("\n3 Industry Personas:")
    for industry in INDUSTRY_PERSONAS:
        print(f"   - {industry.capitalize()}")

    print("\nKey constraints: no fake scarcity, no invented proof, no customer claims.")
    print("="*80)
    print("SAVED AS PLAN - VoIP Bot Development (tabled until email bot revenue)")
    print("="*80)
