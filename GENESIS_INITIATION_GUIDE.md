# Mythara Engine Pilot - Distribution Guide
**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

## Overview

After a client purchases pilot access via Stripe, you send them TWO things:
1. **Email with access credentials**
2. **Pilot package download link**

---

## Step 1: Generate Client API Key (After Payment)

> **⚠️ DISABLED — no payment path exists.** All Stripe webhooks (Test and Live) were deleted, so no webhook can confirm payment. The key-generation instructions below are historical; do not present this as a live flow.

~~After Stripe webhook confirms payment, generate a unique API key for the client:~~

```bash
# Generate a unique pilot API key
python3 -c "import secrets; print('sk_pilot_' + secrets.token_urlsafe(32))"

# Example output: <YOUR_PILOT_API_KEY>
```

**Store this** in a simple JSON file or spreadsheet:
```json
{
  "client_email": "john@company.com",
  "company_name": "ACME Corp",
  "api_key": "<YOUR_PILOT_API_KEY>",
  "purchase_date": "2025-11-11",
  "expiry_date": "2025-12-11",
  "stripe_session_id": "cs_test_abc123"
}
```

---

## Step 2: Send Welcome Email

**Subject:** Mythara Engine Pilot - Access Details

**Body:**

```
Hi [Client Name],

Your Mythara Engine Pilot is ready! You have 30 days of full access starting today.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 DOWNLOAD PILOT PACKAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Download: https://github.com/herbievelezjr/Mythara_Archive/releases/download/v1.0.0/mythara-pilot-package.zip

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 YOUR ACCESS CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API Endpoint: https://mythara-engine.up.railway.app
API Key: <YOUR_PILOT_API_KEY>

Access Expires: December 11, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ QUICK TEST (30 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

curl -X POST https://mythara-engine.up.railway.app/v1/clauses/invoke \
  -H "X-API-Key: <YOUR_PILOT_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "cl_test", "invocation_context": {"test": true}}'

If you see a JSON response with "integrity_hash", you're connected!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 WHAT'S IN THE PACKAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ API documentation & examples
✓ Python client library
✓ Docker setup for local deployment (optional)
✓ Sample compliance workflows
✓ NIST SP 800-53 mapping guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 TWO WAYS TO USE YOUR PILOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option A: Cloud-hosted (recommended for pilot)
→ Use the API endpoint above directly
→ No infrastructure setup needed
→ Start testing immediately

Option B: Self-hosted (for air-gapped/compliance)
→ Unzip package and run: docker-compose up
→ Runs entirely in your environment
→ Follow README_SELFHOSTED.md in the zip

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ QUESTIONS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reply to this email or schedule a walkthrough:
https://calendly.com/mythara-engine/pilot-onboarding

Best,
Herbert Velez Jr.
Mythara.Engine@yahoo.com
```

---

## Step 3: Create the Pilot Package (One-Time Setup)

Create a distribution package that clients download:

### Package Contents
```
mythara-pilot-package/
├── README.md                    # Quick start guide
├── README_SELFHOSTED.md         # Docker setup instructions
├── docker-compose.yml           # Self-hosted deployment
├── .env.example                 # Environment template
├── examples/
│   ├── quickstart.py           # Python examples
│   ├── quickstart.sh           # Bash examples
│   └── postman_collection.json # Postman tests
├── client/
│   ├── mythara_client.py       # Python client library
│   └── requirements.txt        # Client dependencies
└── docs/
    ├── API_REFERENCE.md        # Full API docs
    ├── COMPLIANCE_GUIDE.md     # NIST/HIPAA mapping
    └── TROUBLESHOOTING.md      # Common issues
```

I'll create this structure for you now:

