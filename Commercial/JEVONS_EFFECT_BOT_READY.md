# Jevons Effect Email Bot - READY TO RUN

> **Status (2026-09-27):** November 2025 build plan, preserved as written. The bot was never run live — treat the "Run Live" steps below as a 2025 to-do, not as completed. Outreach stays dry-run only until Herb unblocks it (Yahoo app password, postal address, mode flip).

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## ✅ WHAT'S DONE

Your AI email assistant is now equipped with **Jevons Effect sales psychology:**

### 1. **Fear of Loss** (Loss Aversion)
- Regulatory exposure: name the regulation that actually applies to the prospect (OCC, CFPB, FDA, TCPA). Do not invent fine amounts or cite rules that don't exist.
- Competitive disadvantage: starting an audit trail now builds history sooner than starting later.
- Opportunity cost: manual prep time they can't get back.
- Pricing windows: only with real deadlines you can show (e.g., a rate schedule with a published change date).

### 2. **Scarcity** (Jevons Effect)
- Real capacity limits only: "I can onboard [N] companies this quarter" — where N is your actual capacity.
- Time constraints: only dates that are true on your calendar.
- Exclusive access: only when a tier or program genuinely has limits.

### 3. **Urgency** (Time Compression)
- External deadlines: the prospect's own audit or review dates (from what they told you)
- Internal constraints: only if your calendar is genuinely full
- Event-driven: their stated timelines, not invented ones
- Momentum loss: "the longer you wait, the less audit history you'll have by review time"

### 4. **Strategic Indifference** (Takeaway Selling)
- Qualifying, not convincing: "This might not be a fit if..."
- Willing to walk: "If timing's not right, totally understand"
- Selective availability: "I'm prioritizing companies with audits in next 90 days"
- High-status positioning: "Can you decide this week or do you need more approvals?"

---

## 🎯 HOW IT WORKS

The bot analyzes **every prospect reply** and applies the right psychology:

### **INTERESTED** → Qualify + Scarcity + Close Fast
```
Quick question—do you have regulatory pressure in next 90 days or is this exploratory?

I can onboard [N] companies this quarter at the early adopter rate ($500, normally $2,500). After that, it's full price. The earlier you start, the more audit history you'll have at your next review.

For example, an early adopter starting today would have months of audit data before a latecomer even started—early adopters bank a data head start.

I'm booking Tuesday/Wednesday this week. Which works better—10am or 2pm MT?
```

### **QUESTION** → Answer Briefly + Reframe to Loss + Advance
```
Cryptographic hashing (SHA-256) on every AI decision—auditors can verify zero tampering.

Without this, your auditors see black-box AI with no provable lineage. That's a compliance gap worth closing before your next review.

The early adopter rate ($500 vs $2,500) applies while slots last—I can confirm current availability when we talk.

15-min screen share Tuesday or Wednesday—which is better?
```

### **NOT INTERESTED** → Total Indifference + Plant Fear Seed + Referral
```
No problem—appreciate the heads up.

If your next audit gets flagged for AI explainability, feel free to reach out.

Quick question—do you know anyone at [competitor] handling model risk? Happy to help them out.
```

---

## 📚 FILES CREATED

### 1. `email_assistant.py` (776 lines)
- RAG integration (searches 33 Mythara docs, 300+ chunks)
- Jevons Effect psychology framework
- Intent categorization (interested/question/not_interested)
- Draft generation with sales psychology
- Gmail API integration

### 2. `build_knowledge_base.py` (418 lines)
- ChromaDB vector database
- 33 customer-facing docs indexed
- Semantic search
- RAG answer generation

### 3. `Jevons_Effect_Sales_Examples.md`
- 6 detailed email examples
- Psychology breakdowns
- "When NOT to use" guidance
- Formula: Acknowledge → Qualify → Scarcity → Fear → Social Proof → Urgency → Assumptive Close → Indifferent Exit

### 4. `test_rag_sales.py`
- Test script for bot responses
- RAG knowledge base search tests

---

## 🚀 NEXT STEPS (TO MAKE IT LIVE)

### Step 1: Set OpenAI API Key
```powershell
$env:OPENAI_API_KEY = 'sk-proj-YOUR-KEY-HERE'
```
Cost: ~$5-10/month for 100 email responses

### Step 2: Install Gmail Libraries
```powershell
py -3.11 -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Set Up Gmail OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth client ID (Desktop app)
3. Download `gmail_credentials.json`
4. Save to `Commercial/` directory

Full instructions: See `EMAIL_ASSISTANT_SETUP.md`

### Step 4: Test with Sample Email
```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
py -3.11 test_rag_sales.py
```

### Step 5: Run Live (Monday Nov 4)
1. Send 20 outreach emails (use `First_100_Outreach_Targets.md`)
2. Label them "Mythara-Outreach" in Gmail
3. Afternoon: Run bot to check replies
```powershell
py -3.11 email_assistant.py --check-now
```
4. Review drafts in Gmail
5. Edit if needed, send

---

## 🧠 THE PSYCHOLOGY

### **Jevons Effect**: Scarcity increases perceived value
- NOT fake countdown timers
- REAL capacity constraints ("I can only onboard 5 companies")
- Limited pricing windows (fill only as many slots as you can genuinely serve — no invented counts)

### **Loss Aversion**: Losses hurt 2x more than gains feel good
- Regulatory fines > "save time"
- Competitive disadvantage > "improve efficiency"
- Missed pricing window > "early bird discount"

### **Urgency**: Time pressure forces decisions
- External (Fed rules Q2 2026)
- Internal (booked until February)
- Event-driven (your audit in 6 weeks)

### **Strategic Indifference**: The moment you NEED the sale, you lose leverage
- "This might not be a fit if..."
- "If timing's not right, totally understand"
- "I'm interviewing them, not pitching"

---

## 📊 TARGETS (not results)

### Email Volume Strategy:
- **400 emails / 30 days**
- **15-20 replies** (target, ~4-5% response rate)
- **5-8 calls** (target, ~30% call conversion)
- **2-3 deals** at $2,500 = **$5k-$7.5k** (target)
- OR **10-15 deals** at $500 = **$5k-$7.5k** (target)

### Bot Impact:
- **Saves 10+ hours/week** (no manual email responses)
- **Consistent sales psychology** (no fatigue, always closing)
- **Archive-based answers** (uses your knowledge base, not generic templates)
- **Faster response time** (replies within hours, not days)

---

## 🎯 THE TONE (Outcome-Independent Closer)

**Good:**
- "Quick question—do you have regulatory pressure in next 90 days?"
- "I have [N] slots left at $500, at my real onboarding capacity. After that it's full price."
- "If timing's not right, no worries—just don't want you to miss the window."

> Standing rule: scarcity must be real. No invented slot counts, no fake deadlines, no fabricated fine amounts. If a slot number is in the copy, it matches the real onboarding plan.

**Bad:**
- "I'd love to chat whenever you're available!"
- "Let me know if you have any questions."
- "Hope to work together someday!"

---

## 🔥 YOU'RE READY

- ✅ RAG knowledge base (33 docs, 300+ chunks)
- ✅ Jevons Effect sales psychology
- ✅ Intent categorization
- ✅ Draft generation
- ✅ Gmail integration (pending OAuth setup)
- ✅ Cost-optimized (~$10/month total)

**All you need:** OpenAI API key + Gmail OAuth credentials

**Then:** Send 20 emails Monday → Let bot handle replies → Review drafts → Close deals

---

**The bot is a SALES CLOSER, not customer support.**

Every email advances the deal. Every response applies psychology. Every draft creates urgency — with real constraints, never invented ones.

The target: consistent follow-up that converts. Track real numbers weekly. 🚀
