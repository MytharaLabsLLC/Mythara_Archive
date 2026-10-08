**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

# Email Assistant Setup Guide

## What You Get

The AI email assistant will:
- ✅ Check your inbox for replies to Mythara outreach
- ✅ Categorize intent (interested, question, not interested)
- ✅ Generate draft responses using your templates
- ✅ Save drafts in Gmail/Yahoo for you to review
- ✅ Track all conversations in CSV
- ✅ Send you daily summaries

**You stay in control:** The bot NEVER sends emails automatically. It creates drafts for your review.

---

## Setup Steps (30 minutes)

### Step 1: Install Python dependencies

```powershell
pip install openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Cost:** Free (libraries are open source)

---

### Step 2: Get OpenAI API Key

1. **Go to:** https://platform.openai.com/api-keys
2. **Sign up** (free account works)
3. **Create API key** → Copy it
4. **Add $5 credit:** Billing → Add payment method → Add $5
   - $5 = ~500 email responses (lasts months)
5. **Set environment variable:**

```powershell
# Temporary (this session only)
$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"

# Permanent (add to PowerShell profile)
notepad $PROFILE
# Add this line:
$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"
```

**Cost:** $5 one-time (lasts 3-6 months at your volume)

---

### Step 3: Set up Gmail API

#### Option A: Gmail (Recommended)

**Why Gmail:** Better API support, easier setup, free forever.

1. **Go to:** https://console.cloud.google.com/
2. **Create new project:** "Mythara Email Assistant"
3. **Enable Gmail API:**
   - APIs & Services → Enable APIs → Search "Gmail API" → Enable
4. **Create OAuth credentials:**
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: Desktop app
   - Name: "Mythara Email Bot"
   - Download JSON → Save as `gmail_credentials.json` in `Commercial/` folder
5. **First run will open browser to authorize**

**Cost:** Free (Gmail API has 1 billion quota/day)

#### Option B: Yahoo Mail (More complex)

Yahoo's API is harder to set up. **Recommendation: Forward MytharaLabsLLC@yahoo.com to a new Gmail** (Settings → Forwarding → Add Gmail address), then use Gmail API.

**How to forward Yahoo → Gmail:**
1. Create new Gmail: mythara.assistant@gmail.com (or reuse existing)
2. Yahoo Mail → Settings → Accounts → Add forwarding address
3. Confirm in Gmail
4. All Yahoo emails now go to Gmail
5. Use Gmail API (easier setup)

---

### Step 4: Download `gmail_credentials.json`

After creating OAuth credentials in Google Cloud Console:

1. Click **Download JSON** button
2. Rename file to: `gmail_credentials.json`
3. Move to: `C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial\`

**Security:** This file is private. Never commit to GitHub.

---

### Step 5: First Run (Authorize)

```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
python email_assistant.py --check-now
```

**What happens:**
1. Opens browser → "Sign in with Google"
2. Choose your Gmail account
3. Grant permissions (read/write emails, create drafts)
4. Saves `gmail_token.json` (reused for future runs)
5. Checks inbox for new replies
6. Generates drafts

**First run:** You'll see "No new emails found" (that's fine — you haven't sent outreach yet)

---

## Daily Usage

### Check emails once

```powershell
python email_assistant.py --check-now
```

**Output:**
```
🔍 Checking for new email replies...
Found 3 emails to process

📧 Processing: Re: SSIP for model risk audits...
   Intent: interested (95% confidence)
   ✍️  Draft generated (287 chars)
   ✅ Draft created in Gmail (ID: r-1234567890)

✅ Processed 3 new emails, created 3 drafts
```

### Run as background daemon (check every hour)

```powershell
python email_assistant.py --daemon
```

**Use case:** Leave running on your PC; checks inbox every hour automatically.

**To stop:** Press Ctrl+C

### Get 24-hour summary

```powershell
python email_assistant.py --summary
```

**Output:**
```
📊 Mythara Email Assistant - 24 Hour Summary
==================================================

Total replies: 5

By intent:
  • interested: 3
  • question: 1
  • not_interested: 1

Drafts created: 4
Sent: 0

⚠️  4 drafts waiting for your review in Gmail
```

---

## Workflow (Daily Routine)

### Morning (15 minutes)

1. **Send 20 outreach emails manually** (using your templates)
2. **Label them** in Gmail: "Mythara-Outreach" (optional, for tracking)

### Afternoon (5 minutes)

3. **Run email assistant:**
   ```powershell
   python email_assistant.py --check-now
   ```
4. **Open Gmail → Drafts** (you'll see AI-generated responses)
5. **Review each draft:**
   - Good? Click Send
   - Need edit? Tweak and Send
   - Bad? Delete and write manually
6. **Send 5-10 responses** (takes 5 mins instead of 30 mins)

### Evening (1 minute)

7. **Check summary:**
   ```powershell
   python email_assistant.py --summary
   ```

---

## Configuration

Edit `email_assistant_config.json` (auto-created on first run):

```json
{
  "email_address": "MytharaLabsLLC@yahoo.com",
  "outreach_label": "Mythara-Outreach",
  "search_days_back": 7,
  "templates": {
    "interested": "book_call",
    "question": "answer_question",
    "not_interested": "polite_close"
  },
  "pricing": {
    "early_adopter": 500,
    "standard": 2500
  }
}
```

**Customization:**
- `outreach_label`: Gmail label to filter (optional)
- `search_days_back`: How far back to check (7 days default)
- `pricing`: Used in draft generation

---

## Tracking Files

The bot creates 2 tracking files in `Commercial/`:

### 1. `email_tracking.csv`

All conversations logged:

| timestamp | message_id | from_email | subject | intent | draft_id | sent |
|---|---|---|---|---|---|---|
| 2025-11-04 10:23 | abc123 | john@example.com | Re: SSIP audit | interested | draft-456 | False |

**Use this to:**
- See all replies at a glance
- Track which drafts you've sent
- Export to Google Sheets for CRM

### 2. `draft_responses.json`

Backup of generated drafts (in case Gmail API fails):

```json
[
  {
    "timestamp": "2025-11-04T10:23:00",
    "message_id": "abc123",
    "intent": "interested",
    "draft_body": "Thanks for getting back to me!..."
  }
]
```

---

## Troubleshooting

### "Gmail service not authenticated"

**Fix:**
1. Make sure `gmail_credentials.json` exists in `Commercial/` folder
2. Run `python email_assistant.py --check-now` (will open browser)
3. Sign in and grant permissions

### "OpenAI API error: authentication"

**Fix:**
1. Check API key: `echo $env:OPENAI_API_KEY`
2. Should start with `sk-proj-...`
3. If empty, set it: `$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY"`

### "No module named 'google.auth'"

**Fix:**
```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Drafts not appearing in Gmail

**Check:**
1. Open Gmail → Drafts (not Inbox)
2. Look for "Re: [subject]" with your template text
3. If missing, check terminal output for errors

### Intent categorization is wrong

**Fix:**
- The bot learns from your edits
- If it says "interested" but you see "not interested," just delete the draft
- OpenAI model improves with more data (gets better after 10-20 emails)

---

## Advanced: Custom Templates

Edit `email_assistant.py` lines 280-320 to customize response templates:

```python
def get_template_response(self, intent: str) -> str:
    templates = {
        'interested': """Your custom interested template here""",
        'question': """Your custom question template here""",
        'not_interested': """Your custom not-interested template here"""
    }
    return templates.get(intent, templates['interested'])
```

---

## Security & Privacy

**What data is stored:**
- Gmail token (local file, encrypted by Google)
- Email tracking CSV (local, not uploaded anywhere)
- Email content is sent to OpenAI's API for intent categorization — handle it under your own API data-usage terms; no privacy guarantee about the provider's retention is made here

**What's NOT stored:**
- Passwords (OAuth uses tokens)
- Sent emails (only drafts created, you control sending)

**Best practices:**
- Keep `gmail_credentials.json` and `gmail_token.json` private
- Add to `.gitignore` (don't commit to GitHub)
- Set OpenAI API key as environment variable (not hardcoded)

---

## Cost Breakdown

| Item | Cost | Frequency |
|---|---|---|
| Python libraries | Free | One-time |
| Gmail API | Free | Forever |
| OpenAI API | $5 | 3-6 months |
| **Total first month** | **$5** | |
| **Ongoing** | **$1-2/month** | |

**ROI:** If this bot saves you 30 mins/day × 5 days = 2.5 hours/week, that's 10 hours/month. At even $25/hour value of your time, you save $250/month for $2/month cost.

---

## Next Steps

1. **Install dependencies** (5 mins)
2. **Get OpenAI API key** (5 mins)
3. **Set up Gmail API** (15 mins)
4. **Run first check** (5 mins)
5. **Send your first 20 outreach emails tomorrow** (use templates in `First_100_Outreach_Targets.md`)
6. **Run bot tomorrow afternoon** to handle replies

---

## Questions?

Email assistant runs locally on your PC. No cloud services, no subscriptions (except $5 OpenAI credit).

**Need help?** Check the troubleshooting section or run:
```powershell
python email_assistant.py --help
```

**Ready to start?** Run setup tomorrow after you send your first batch of outreach emails.
