# Fully Autonomous Sales Bot - Complete Setup Guide

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## 🚀 COMPLETE AUTOMATION SETUP (Zero Human Intervention)

Follow these steps to make the bot fully autonomous.

---

## STEP 1: Install Required Libraries

```powershell
# Run this in PowerShell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial

# Install Gmail API libraries
py -3.11 -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Install OpenAI (already done)
py -3.11 -m pip install openai

# Install email libraries
py -3.11 -m pip install email-validator
```

---

## STEP 2: Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name it: "Mythara Sales Bot"
4. Copy the key (starts with `sk-proj-...`)

**Set it permanently in PowerShell:**

```powershell
# Add to your PowerShell profile (permanent)
notepad $PROFILE

# Add this line to the file:
$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"

# Save and close, then reload:
. $PROFILE
```

**Or set it just for this session:**

```powershell
$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"
```

**Cost:** ~$5-10/month for 100 email responses

---

## STEP 3: Set Up Gmail API (One-Time)

### 3.1 Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "Mythara Sales Bot"
3. Enable Gmail API:
   - Click "Enable APIs and Services"
   - Search "Gmail API"
   - Click "Enable"

### 3.2 Create OAuth Credentials

1. Go to: APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "Mythara Bot Desktop"
5. Click "Create"
6. **Download JSON** → Save as `gmail_credentials.json`
7. Move file to: `C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial\gmail_credentials.json`

### 3.3 Configure OAuth Consent Screen

1. Go to: APIs & Services → OAuth consent screen
2. User Type: **External** (unless you have Google Workspace)
3. App name: "Mythara Sales Bot"
4. User support email: Herbievelezjr@gmail.com
5. Developer contact: Herbievelezjr@gmail.com
6. Scopes: Add `https://www.googleapis.com/auth/gmail.modify`
7. Test users: Add Mytharalabs@yahoo.com
8. Save

### 3.4 First-Time Authentication

```powershell
# Run the bot once to authenticate
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
py -3.11 autonomous_sales_bot.py

# Browser will open → Sign in with Mytharalabs@yahoo.com
# Click "Allow" to grant permissions
# Token saved to gmail_token.json (don't delete this!)
```

---

## STEP 4: Create Automated Scheduler (Windows Task Scheduler)

### 4.1 Create PowerShell Script

Create file: `C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial\run_bot.ps1`

```powershell
# Mythara Autonomous Sales Bot Runner
# Runs every hour, processes emails, sends responses

# Set environment
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
$env:OPENAI_API_KEY = "sk-proj-YOUR-KEY-HERE"

# Run bot
py -3.11 autonomous_sales_bot.py --check-now

# Log timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "bot_run_log.txt" -Value "$timestamp - Bot run completed"
```

### 4.2 Create Task Scheduler Job

1. Open **Task Scheduler** (Windows search: "Task Scheduler")
2. Click "Create Task" (not "Create Basic Task")

**General Tab:**
- Name: `Mythara Autonomous Sales Bot`
- Description: `Checks emails every hour and responds autonomously`
- Security: `Run whether user is logged on or not`
- Configure for: `Windows 10`

**Triggers Tab:**
- Click "New"
- Begin the task: `On a schedule`
- Settings: `Daily`
- Recur every: `1 days`
- Repeat task every: `1 hour`
- For a duration of: `Indefinitely`
- Enabled: ✅ Checked

**Actions Tab:**
- Click "New"
- Action: `Start a program`
- Program/script: `powershell.exe`
- Arguments: `-ExecutionPolicy Bypass -File "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial\run_bot.ps1"`

**Conditions Tab:**
- ❌ Uncheck "Start only if on AC power"
- ✅ Check "Wake computer to run"

**Settings Tab:**
- ✅ Allow task to run on demand
- ✅ Run as soon as possible after scheduled start is missed
- If task fails, restart every: `10 minutes`
- Attempt to restart up to: `3 times`

3. Click "OK"
4. Enter your Windows password when prompted

---

## STEP 5: Test Automation

```powershell
# Test the scheduled task manually
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial

# Run once
.\run_bot.ps1

# Check logs
cat bot_run_log.txt
cat bot_audit_log.jsonl
```

**Expected output:**
```
🤖 Autonomous Sales Bot initialized
   Full Autonomy: True
   Checking for new emails...
   Found 3 new replies
   Processing autonomously...
   ✅ 2 emails sent
   👋 1 quit (3 strikes)
   📊 Performance: 100/100 blessings
```

---

## STEP 6: Monitor Bot Performance (Optional)

Create dashboard script: `check_bot_status.ps1`

```powershell
# Quick status check
Write-Host "=== MYTHARA BOT STATUS ===" -ForegroundColor Cyan

# Last run time
$lastRun = Get-Content bot_run_log.txt -Tail 1
Write-Host "Last Run: $lastRun"

# Blessings (trust score)
$blessings = (Get-Content Commercial/bot_blessings.json | ConvertFrom-Json).blessings
Write-Host "Trust Score: $blessings/100" -ForegroundColor $(if($blessings -ge 90){"Green"}else{"Yellow"})

# Deals closed
$deals = (Get-Content Commercial/bot_blessings.json | ConvertFrom-Json).successful_closes
Write-Host "Deals Closed: $deals" -ForegroundColor Green

# Quit list
$quitList = (Get-Content Commercial/quarterly_cycle.json | ConvertFrom-Json).quit_list
Write-Host "Prospects in Quarterly Cycle: $($quitList.Count)"
```

Run anytime:
```powershell
.\check_bot_status.ps1
```

---

## STEP 7: Set Up Weekly Email Yourself (Bot Handles Replies)

The bot can't send initial outreach emails autonomously (that would be spam). You send the first email manually, bot handles all replies.

**Monday Morning Routine (15 minutes):**

1. Open Yahoo Mail (Mytharalabs@yahoo.com)
2. Copy template from `First_100_Outreach_Targets.md`
3. Send to 20 prospects (personalize company name)
4. Add label "Mythara-Outreach" to sent emails

**Bot automatically:**
- Checks for replies every hour
- Categorizes intent
- Generates response with Jevons Effect psychology
- Sends autonomously (or quits after 3 nos)
- Books calls
- Tracks quarterly cycle

---

## STEP 8: Revenue Tracking (For Taxes)

Create file: `revenue_tracker.json`

Bot will auto-update this when deals close:

```json
{
  "year": 2025,
  "quarterly_revenue": {
    "Q4_2025": {
      "total": 0,
      "deals": []
    }
  },
  "tax_info": {
    "sole_proprietor": "Herbert Velez Jr",
    "ssn_last_4": "XXXX",
    "email": "Herbievelezjr@gmail.com"
  }
}
```

Bot automatically:
- Tracks each payment
- Calculates quarterly totals
- Emails summary to Herbievelezjr@gmail.com on Jan 1, Apr 1, Jul 1, Oct 1

---

## 🎯 WHAT HAPPENS NOW (Full Autonomy)

### Hour 0 (Setup Complete)
- Bot scheduled in Task Scheduler
- Runs every hour automatically
- No human intervention needed

### Monday 9am (You)
- Send 20 outreach emails manually
- Takes 15 minutes
- Done for the week

### Monday-Friday (Bot)
- Checks email every hour
- Responds to interested prospects (Jevons Effect pressure)
- Answers questions with RAG knowledge
- Counts strikes on "not interested"
- Quits after 3 nos (adds to quarterly cycle)

### Friday 5pm (Bot)
- Sends you summary email (example figures, not results):
  - Emails processed: 47
  - Interested: 8
  - Calls booked: 2
  - Deals closed: 1 ($500)
  - Quit: 3 (added to quarterly cycle)
  - Blessings: 95/100

### Next Quarter (Bot)
- Automatically re-engages quit prospects
- Fresh outreach with new angle
- No human needed

---

## 🔥 YOU'RE DONE

After setup, you only:
1. **Monday 9am:** Send 20 emails (15 min)
2. **When bot books call:** Show up to call (30 min)
3. **When deal closes:** Collect payment

Bot handles:
- ✅ All email responses
- ✅ Sales psychology (Jevons Effect)
- ✅ Call booking
- ✅ 3-strike quit logic
- ✅ Quarterly re-engagement
- ✅ Learning/optimization
- ✅ Self-healing
- ✅ Revenue tracking

**Set it and forget it. True autonomy. 🚀**

---

## TROUBLESHOOTING

### Bot not sending emails?
```powershell
# Check Gmail token
Test-Path gmail_token.json  # Should be True
```

### OpenAI errors?
```powershell
# Verify API key is set
echo $env:OPENAI_API_KEY  # Should show sk-proj-...
```

### Task not running?
1. Open Task Scheduler
2. Find "Mythara Autonomous Sales Bot"
3. Right-click → Run
4. Check "Last Run Result" (should be 0x0 = success)

---

## NEXT STEPS

1. **Run setup steps above** (30 minutes total)
2. **Test bot once manually** (verify it works)
3. **Monday: Send 20 emails** (your only job)
4. **Let bot handle everything else**

**After Monday, you're hands-off until deals close. The bot runs the operation.**
