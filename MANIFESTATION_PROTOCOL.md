# Mythara Engine - Iron Clad Deployment Checklist *(November 2025 draft)*

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

> **⚠️ HISTORICAL SNAPSHOT (November 2025) — voice-standard pass Sept 2026.** This checklist is the author's November 2025 self-assessment, not a verified status. All Stripe webhooks were deleted, so the payment flow it describes **does not exist**. Claims of "bulletproof"/"iron clad" robustness, production readiness, and the revenue math below are unverified and should not be repeated.

---

## ✅ Claimed completed (Nov 2025 self-assessment)

### 1. Database Persistence ✅
- **File**: `core/source_proprietary/database.py`
- **What it does**: PostgreSQL storage for pilots, usage tracking, domain registry
- **Why it matters**: Railway restart no longer wipes data
- **Status**: READY - SQLite for local testing, PostgreSQL for Railway production

### 2. Automated Email Delivery ✅
- **File**: `core/source_proprietary/email_service.py`
- **What it does**: Sends API keys, usage alerts, expiration warnings via SendGrid
- **Why it matters**: Zero manual work - customers get API keys instantly post-payment
- **Status**: Claimed READY in Nov 2025 — unverified in this archive *(a Sept 2026 review found zero API keys on the SendGrid account, and the prior SendGrid key was scrubbed; do not treat email delivery as configured)*

### 3. ~~Stripe Webhook Integration ✅~~ — DISABLED
- **File**: `core/source_proprietary/main.py` (webhook handler updated)
- **What it does**: Captures payment → creates pilot → emails API key
- **Why it matters**: End-to-end automation from payment to access
- **Status**: ❌ DISABLED — all Stripe webhooks (Test and Live) were deleted; no fulfillment path exists. Do not treat as live.

### 4. Pilot Dashboard Endpoint ✅
- **Endpoint**: `GET /v1/pilot/dashboard`
- **What it does**: Shows days remaining, calls used, strike count, expiration date
- **Why it matters**: Customer visibility = fewer support tickets
- **Status**: READY - Returns full pilot status with authentication

### 5. Usage Alert System ✅
- **Functions**: `send_usage_alert_80_percent()`, `send_expiration_alert_24hr()`
- **What it does**: Proactive warnings before lockout
- **Why it matters**: No surprise "why did my API stop working?" complaints
- **Status**: READY - Emails queued in database, sent automatically

### 6. Refund Policy ✅
- **File**: `COVENANT_DISSOLUTION_TERMS.md` *(the migration renamed `REFUND_POLICY.md`; that old name is not present in this archive)*
- **What it does**: "ALL SALES FINAL - Exchanges Only" legal protection
- **Why it matters**: Prevents refund abuse, protects revenue
- **Status**: Claimed READY in Nov 2025 — unverified

---

## 🚀 Deploy to Railway - 5 Steps

### Step 1: Add PostgreSQL Database
```bash
# In Railway dashboard:
1. Click your project
2. Click "New" → "Database" → "PostgreSQL"
3. Railway automatically creates DATABASE_URL environment variable
4. Done - database.py detects it automatically
```

### Step 2: Set Environment Variables
```bash
# In Railway → Variables tab, add:
SENDGRID_API_KEY=[REDACTED - set via environment]
FROM_EMAIL=Mythara.Engine@yahoo.com
SUPPORT_EMAIL=Mythara.Engine@yahoo.com
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# DATABASE_URL is auto-created by Railway PostgreSQL
```

### Step 3: Deploy Updated Code
```bash
git add .
git commit -m "Add database persistence and automated email delivery"
git push origin main
```

### ~~Step 4: Configure Stripe Webhook~~ — DISABLED (historical)

> **⚠️ DISABLED — webhooks deleted, no fulfillment path. Do not follow these steps.** Kept for historical reference only.

```bash
# In Stripe dashboard:
1. Go to Developers → Webhooks
2. Add endpoint: https://mythara-engine.railway.app/api/webhooks/stripe
3. Select event: checkout.session.completed
4. Copy webhook secret → paste into Railway STRIPE_WEBHOOK_SECRET variable
5. Add metadata fields to Stripe checkout: employee_count, license_type=pilot
```

### Step 5: Test End-to-End
**Test payment flow:** *(historical — no payment path exists)*
1. ~~Make test Stripe payment ($49 pilot)~~ — disabled: webhooks deleted
2. Check Railway logs: "Pilot created and email sent"
3. Check email inbox: API key delivery email received
4. Test API key: curl -H "Authorization: Bearer YOUR_KEY" https://mythara-engine.railway.app/v1/pilot/dashboard
5. Verify database: Pilot data persists after Railway restart

---

## 🛡️ What the draft claimed was addressed *(Nov 2025 self-assessment — unverified)*

| **Vulnerability** | **Before** | **After** |
|------------------|-----------|----------|
| Railway restart wipes data | ❌ Lost all pilots | ✅ PostgreSQL persistence |
| Payment but no API key | ❌ Manual email | ✅ Automatic SendGrid delivery |
| Webhook doesn't set pilot_start_date | ❌ Broken expiration | ✅ Timestamp from Stripe payment |
| Customer doesn't know pilot status | ❌ No visibility | ✅ /v1/pilot/dashboard endpoint |
| Surprise expiration | ❌ No warning | ✅ 80% + 24hr email alerts |
| Refund abuse | ❌ No policy | ✅ ALL SALES FINAL documented |

---

## 📊 Cost Analysis (100 Customers) — ⚠️ historical planning scenario (Nov 2025); illustrative math only, no customers existed

### Revenue *(illustrative only — not actual revenue)*
- 100 pilots × $49 = **$4,900**

### Costs *(illustrative estimates)*
- Railway PostgreSQL: $5/month
- Railway API calls: ~$300 (100 customers × $3 avg)
- SendGrid emails: $0 (free tier = 100/day)
- Total costs: **$305/month**

### Profit *(illustrative only)*
- **$4,595/month (94% margin)**

---

## ⚠️ Remaining Tasks (Non-Critical)

### 1. Link Refund Policy on Pricing Page
**File**: ~~`core/static/pricing.html`~~ *(not present in this archive)*
**Add**: Checkbox "I agree to Terms of Service" with link to COVENANT_DISSOLUTION_TERMS.md
**Priority**: Medium (legal protection)

### 2. Verify SendGrid Sender Email
**Action**: Check Mythara.Engine@yahoo.com inbox for SendGrid verification email
**Why**: Required before first email can send
**Priority**: High (blocks email delivery)

### 3. Create Stripe Product Metadata Template
**Action**: Add employee_count field to Stripe checkout form
**How**: Stripe Dashboard → Products → Pilot → Checkout settings → Custom fields
**Priority**: Medium (improves rate limit accuracy)

---

## 🎯 System Status: ~~PRODUCTION READY~~ — Nov 2025 self-assessment, not verified

**Database**: Claimed — persistent storage implemented *(claimed Nov 2025)*  
**Email**: Claimed — automated delivery configured *(claimed Nov 2025; SendGrid account shows zero API keys as of Sept 2026)*  
**Webhook**: ❌ DISABLED — webhooks deleted, no end-to-end payment flow  
**Dashboard**: Claimed — customer visibility enabled *(claimed Nov 2025)*  
**Alerts**: Claimed — proactive warnings implemented *(claimed Nov 2025)*  
**Policy**: Claimed — legal protection documented *(claimed Nov 2025)*  

**Next action (Nov 2025 plan):** ~~Deploy to Railway with PostgreSQL and test first pilot purchase.~~ *(No payment path exists; do not follow.)*

---

*Checklist ends as written November 2025. See the banner at the top before acting on any of it.*
