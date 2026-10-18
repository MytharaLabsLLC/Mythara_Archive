# Mythara Email Bot - Setup Guide

## Quick Start

### 1. Get Yahoo App Password

1. Go to: https://account.yahoo.com/security
2. Click "Generate app password"
3. Select "Other App" and name it "Mythara Bot"
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
5. Save it securely—you can't view it again

### 2. Set Environment Variables

**Linux/Mac:**
```bash
export YAHOO_APP_PASSWORD="your_16_char_password_here"
export MYTHARA_API_URL="http://localhost:8000"
export MYTHARA_API_KEY="ent_prod_key_001"
```

**Windows (PowerShell):**
```powershell
$env:YAHOO_APP_PASSWORD="your_16_char_password_here"
$env:MYTHARA_API_URL="http://localhost:8000"
$env:MYTHARA_API_KEY="ent_prod_key_001"
```

**Or create a `.env` file:**
```
YAHOO_APP_PASSWORD=your_16_char_password_here
MYTHARA_API_URL=http://localhost:8000
MYTHARA_API_KEY=ent_prod_key_001
```

### 3. Install Dependencies

```bash
pip install requests
```

(No additional dependencies needed—uses Python stdlib for email/IMAP)

### 4. Run the Bot

Make sure Mythara Engine is running first:
```bash
python core/source_proprietary/main.py
```

Then in another terminal:
```bash
python email_bot.py
```

### 5. Review Drafts

Drafts are saved to `email_drafts/` folder. Each file contains:
- Email metadata (sender, subject, classification)
- Generated draft body
- Review instructions

Example output:
```
email_drafts/
├── draft_20251110_143022_12345.txt
├── draft_20251110_143145_12346.txt
└── email_bot.log
```

Open a draft file, review/edit it, then copy-paste into Yahoo Mail to send.

---

## How It Works

1. **Connects** to MytharaLabsLLC@yahoo.com via IMAP (read-only)
2. **Fetches** unread emails
3. **Classifies** each email:
   - Pilot inquiry → sends pilot delivery template
   - Pricing question → sends ROI/objection template
   - Follow-up needed → sends follow-up template
   - Initial contact → sends initial outreach template
4. **Generates** personalized draft using templates
5. **Saves** draft to `email_drafts/` for your review
6. **Logs** all activity to `email_drafts/email_bot.log`

**No emails are sent automatically**—you maintain full control.

---

## Scheduling (Optional)

To run the bot every 15 minutes:

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add this line (adjust paths):
*/15 * * * * cd /path/to/Mythara_Archive && /usr/bin/python3 email_bot.py
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 15 minutes
4. Action: Start Program → `python.exe`
5. Arguments: `email_bot.py`
6. Start in: `C:\path\to\Mythara_Archive`

---

## Security Notes

- **App password** is not your main Yahoo password—it's safer
- **Never commit** `.env` file or passwords to git
- **Bot only reads** emails; cannot send or delete
- **Drafts stay local** until you manually send them

---

## Troubleshooting

**"YAHOO_APP_PASSWORD not set"**
- Set the environment variable before running
- Or create a `.env` file (requires `python-dotenv`)

**"Authentication failed"**
- Double-check app password (no spaces)
- Ensure Yahoo account has "Allow apps that use less secure sign in" enabled (usually not needed with app passwords)

**"Connection timeout"**
- Check internet connection
- Verify firewall allows IMAP port 993

**"No new emails"**
- Bot only processes UNSEEN emails
- Manually mark an email as unread to test

**"Mythara API error"**
- Ensure `python core/source_proprietary/main.py` is running
- Check API URL and key are correct

---

## Customization

Edit `email_bot.py` to:
- Add more template mappings in `generate_draft()`
- Improve classification logic in `classify_email()`
- Extract company info from email signatures
- Add sentiment analysis or urgency scoring

---

## Next Steps

1. Run bot manually first to test
2. Review a few drafts to verify quality
3. Adjust templates in `EMAIL_TEMPLATES.md` as needed
4. Set up automated scheduling once confident

Questions? Check logs in `email_drafts/email_bot.log`
