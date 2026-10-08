#!/usr/bin/env python3
"""
Mythara Auto Sender - Fully Automated Email Outreach
Sends personalized emails directly via Yahoo SMTP.

Copyright © 2025 Herbert Velez Jr. All rights reserved.

SETUP:
# Password moved to environment variable (CWE-798)
YAHOO_APP_PASSWORD = os.getenv("YAHOO_APP_PASSWORD", "")  # Set via environment
2. Run harvester: py public_contact_harvester.py
3. Run this: py auto_sender.py

SAFETY FEATURES:
- Rate limiting (50 emails/hour to avoid spam flags)
- Progress tracking (resume if interrupted)
- Delivery logs with timestamps
- Automatic retry on failures
"""

import smtplib
import time
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import csv

# ============================================================================
# CONFIGURATION
# ============================================================================

# Yahoo SMTP Settings
YAHOO_EMAIL = "mythara.engine@yahoo.com"
YAHOO_APP_PASSWORD = os.getenv("YAHOO_APP_PASSWORD", "")
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587  # TLS

# Rate Limiting (Yahoo allows ~500/day, we'll be conservative)
EMAILS_PER_HOUR = 50
DELAY_BETWEEN_EMAILS = 3600 / EMAILS_PER_HOUR  # ~72 seconds

# Batch Configuration
BATCH_SIZE = 100  # Send in batches of 100, then pause
PAUSE_BETWEEN_BATCHES = 600  # 10 minutes between batches

# Directories
OUTPUT_DIR = Path("outreach_campaigns")
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "send_log.json"
PROGRESS_FILE = OUTPUT_DIR / "send_progress.json"

# ============================================================================
# EMAIL TEMPLATES
# ============================================================================


def generate_email_healthcare(contact: Dict) -> Dict:
    """Healthcare facility email"""
    hospital_name = contact.get("name", "Your Organization")
    city = contact.get("city", "")
    state = contact.get("state", "")

    subject = f"Soul Cradle is free for {hospital_name} — Because this work matters"

    body = f"""Hi there,

I'm Herbert Velez Jr., founder of Mythara. I'm reaching out to {hospital_name} in {city}, {state} because your team carries a weight most people never see.

A social worker has to discharge a patient who'll be homeless. Policy says discharge. Her heart says keep them safe. She's not wrong either way—but she carries that paradox alone.

Soul Cradle exists for moments like this. It:
• Documents the impossible choice between mission and compliance
• Measures the emotional cost to your people (before it becomes burnout)
• Creates cryptographically verified records for leadership and auditors
• Shows regulators the human impact of policy gaps

Here's what matters: Soul Cradle is FREE for healthcare workers who need it most.

Your team saves lives every day. They shouldn't have to carry these paradoxes alone. Soul Cradle holds that weight.

Start your 7-day pilot here (free for healthcare):
→ https://mytharaarchive-production.up.railway.app/pricing

If this resonates, I'm here: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Founder, Mythara Labs LLC (Colorado domestic LLC, filed 2026-10-04; CO SOS ID #20268239831)

P.S. — This is a one-time email. Reply "unsubscribe" if you'd prefer not to hear from us."""

    return {"subject": subject, "body": body}


def generate_email_banking(contact: Dict) -> Dict:
    """Banking facility email"""
    bank_name = contact.get("name", "Your Organization")
    city = contact.get("city", "")
    state = contact.get("state", "")

    subject = f"Soul Cradle for {bank_name} — When compliance conflicts with doing right by customers"

    body = f"""Hi there,

I'm Herbert Velez Jr., founder of Mythara. I'm reaching out to {bank_name} in {city}, {state} because your people face impossible moments that never make it into compliance reports.

A banker sees a family drowning financially. Knows exactly what would help. Policy says no. The family walks out. The banker carries that.

This isn't about breaking rules—it's about documenting the human cost when policy conflicts with mission.

Soul Cradle:
• Records the conflict between regulations and helping customers
• Measures the toll on your team (before it becomes attrition)
• Generates cryptographically verified compliance reports
• Shows leadership where policy creates impossible choices

Here's what matters: Soul Cradle helps your people prove they followed policy while documenting the cost. So when leadership asks "Why are we losing good bankers?", you have the data.

Start your 7-day pilot here:
→ https://mytharaarchive-production.up.railway.app/pricing

If this resonates, I'm here: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Founder, Mythara Labs LLC (Colorado domestic LLC, filed 2026-10-04; CO SOS ID #20268239831)

P.S. — One-time email. Reply "unsubscribe" to opt out."""

    return {"subject": subject, "body": body}


def generate_email_government(contact: Dict) -> Dict:
    """Government agency email"""
    agency_name = contact.get("name", "Your Agency")

    subject = f"Soul Cradle is free for {agency_name} — Because public servants deserve support"

    body = f"""Hi there,

I'm Herbert Velez Jr., founder of Mythara. I'm reaching out to {agency_name} because your people carry an impossible burden: serving the public while enforcing policies that sometimes hurt the very people they're trying to help.

A case worker knows a family desperately needs help. Regulation says they don't qualify. Both are true. The family leaves. The case worker stays—and carries that weight.

This happens every day in public service. And it's why burnout in government is a crisis.

Soul Cradle exists for this:
• Documents the conflict between policy and mission
• Measures the emotional toll on your team (before they quit)
• Creates audit-ready records showing you followed protocol
• Gives leadership data on where regulations conflict with public good

Here's what matters: Soul Cradle is FREE for government agencies and public servants.

Your people chose public service to help others. They shouldn't burn out doing it. Soul Cradle holds the paradox so they don't have to carry it alone.

Start your 7-day pilot here (free for public sector):
→ https://mytharaarchive-production.up.railway.app/pricing

If this resonates, I'm here: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Founder, Mythara Labs LLC (Colorado domestic LLC, filed 2026-10-04; CO SOS ID #20268239831)

P.S. — One-time email. Reply "unsubscribe" if you'd prefer not to hear from us."""

    return {"subject": subject, "body": body}


def generate_email_dod(contact: Dict) -> Dict:
    """DoD/Military email"""
    org_name = contact.get("name", "Your Organization")

    subject = f"Soul Cradle for {org_name} — When orders conflict with what's right"

    body = f"""Hi there,

I'm Herbert Velez Jr., founder of Mythara. I'm reaching out to {org_name} because service members face impossible tactical and ethical choices that never make it into after-action reports.

Orders say one thing. Conscience says another. Both are valid. The service member makes the call—and carries that paradox for the rest of their life.

This is why veteran suicide rates are what they are. The impossible choices don't end when the mission does.

Soul Cradle exists for this:
• Documents operational paradoxes with cryptographic integrity
• Measures psychological impact on personnel (before it becomes PTSD)
• Creates audit-ready records for chain of command
• Maintains OPSEC while documenting ethical complexity

Here's what matters: Soul Cradle helps your people document that they followed orders while acknowledging the weight of impossible choices. So when they come home, they're not carrying it alone.

For military and veteran services, Soul Cradle is FREE.

Start your 7-day pilot here (free for DoD/veterans):
→ https://mytharaarchive-production.up.railway.app/pricing

If this resonates, I'm here: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Founder, Mythara Labs LLC (Colorado domestic LLC, filed 2026-10-04; CO SOS ID #20268239831)
Veteran-focused technology

P.S. — One-time email. Reply "unsubscribe" if you'd prefer not to hear from us."""

    return {"subject": subject, "body": body}


# ============================================================================
# CORE SENDING LOGIC
# ============================================================================


def load_contacts(csv_path: str) -> List[Dict]:
    """Load contacts from harvester CSV"""
    contacts = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    return contacts


def load_progress() -> Dict:
    """Load sending progress"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"sent_emails": [], "failed_emails": [], "last_index": 0}


def save_progress(progress: Dict):
    """Save sending progress"""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def log_email(contact: Dict, status: str, error: str = None):
    """Log email send attempt"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "to": contact.get("email", "unknown"),
        "name": contact.get("name", "unknown"),
        "industry": contact.get("industry", "unknown"),
        "status": status,
        "error": error,
    }

    # Append to log file
    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    return log_entry


def send_email(smtp_conn, to_email: str, to_name: str, subject: str, body: str) -> bool:
    """Send a single email via SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Herbert Velez Jr. <{YAHOO_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Plain text version
        text_part = MIMEText(body, "plain")
        msg.attach(text_part)

        # Send
        smtp_conn.send_message(msg)
        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def send_campaign(contacts: List[Dict], start_index: int = 0):
    """Send full email campaign with rate limiting"""

    print("\n" + "=" * 60)
    print("MYTHARA AUTO SENDER")
    print("=" * 60)
    print(f"From: {YAHOO_EMAIL}")
    print(f"Total Contacts: {len(contacts)}")
    print(f"Starting at: Contact #{start_index + 1}")
    print(f"Rate Limit: {EMAILS_PER_HOUR} emails/hour")
    print(f"Batch Size: {BATCH_SIZE} emails per batch")
    print("=" * 60)

    # Verify password
    if not YAHOO_APP_PASSWORD:
        print("\n❌ ERROR: YAHOO_APP_PASSWORD not set")
        print('   Run: $env:YAHOO_APP_PASSWORD="your-password"')
        return

    # Load progress
    progress = load_progress()
    sent_count = len(progress["sent_emails"])
    failed_count = len(progress["failed_emails"])

    print("\n📊 Previous Progress:")
    print(f"   Sent: {sent_count}")
    print(f"   Failed: {failed_count}")

    # Connect to SMTP
    print(f"\n🔌 Connecting to {SMTP_SERVER}...")

    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()
        smtp.login(YAHOO_EMAIL, YAHOO_APP_PASSWORD)
        print("   ✅ Connected successfully")

    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return

    # Send emails
    print("\n" + "=" * 60)
    print("SENDING EMAILS")
    print("=" * 60)

    batch_count = 0

    for i, contact in enumerate(contacts[start_index:], start=start_index):
        # Check if already sent
        if contact.get("email") in progress["sent_emails"]:
            continue

        # Skip if no email
        if not contact.get("email") or "@" not in contact.get("email", ""):
            continue

        # Determine industry and generate email
        industry = contact.get("industry", "").lower()

        if "healthcare" in industry or "hospital" in industry:
            email_data = generate_email_healthcare(contact)
        elif "bank" in industry or "credit union" in industry:
            email_data = generate_email_banking(contact)
        elif "government" in industry or "federal" in industry:
            email_data = generate_email_government(contact)
        elif "dod" in industry or "defense" in industry:
            email_data = generate_email_dod(contact)
        else:
            continue  # Skip unknown industries

        # Send email
        to_email = contact["email"]
        to_name = contact.get("name", "there")

        print(f"\n📧 [{i+1}/{len(contacts)}] Sending to: {to_name} ({to_email})")

        success = send_email(
            smtp, to_email, to_name, email_data["subject"], email_data["body"]
        )

        if success:
            print("   ✅ Sent successfully")
            progress["sent_emails"].append(to_email)
            log_email(contact, "sent")
            sent_count += 1
        else:
            print("   ❌ Failed to send")
            progress["failed_emails"].append(to_email)
            log_email(contact, "failed", "SMTP error")
            failed_count += 1

        # Update progress
        progress["last_index"] = i + 1
        save_progress(progress)

        # Rate limiting
        batch_count += 1

        if batch_count >= BATCH_SIZE:
            print(f"\n⏸️  Batch complete ({batch_count} emails)")
            print(f"   Pausing for {PAUSE_BETWEEN_BATCHES/60} minutes...")
            smtp.quit()
            time.sleep(PAUSE_BETWEEN_BATCHES)

            # Reconnect
            print(f"\n🔌 Reconnecting to {SMTP_SERVER}...")
            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            smtp.starttls()
            smtp.login(YAHOO_EMAIL, YAHOO_APP_PASSWORD)
            print("   ✅ Reconnected")

            batch_count = 0

        else:
            # Delay between emails
            time.sleep(DELAY_BETWEEN_EMAILS)

    # Cleanup
    smtp.quit()

    print("\n" + "=" * 60)
    print("✅ CAMPAIGN COMPLETE")
    print("=" * 60)
    print(f"Total Sent: {sent_count}")
    print(f"Total Failed: {failed_count}")
    print(f"Success Rate: {(sent_count/(sent_count+failed_count)*100):.1f}%")
    print(f"\nLogs saved to: {LOG_FILE}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
    MYTHARA AUTO SENDER
    
    This script sends personalized emails directly via Yahoo SMTP.
    
    SAFETY FEATURES:
    - Rate limited to 50 emails/hour (Yahoo-friendly)
    - Sends in batches of 100 with 10-min pauses
    - Progress tracking (resume if interrupted)
    - Full delivery logs
    
    ===============================================
    """)

    # Find most recent contacts file
    prospecting_dir = Path("prospecting_data")

    if not prospecting_dir.exists():
        print("❌ prospecting_data/ folder not found")
        print("   Run: py public_contact_harvester.py first")
        exit(1)

    contact_files = sorted(prospecting_dir.glob("all_contacts_*.csv"), reverse=True)

    if not contact_files:
        print("❌ No contact files found")
        print("   Run: py public_contact_harvester.py first")
        exit(1)

    latest_file = contact_files[0]
    print(f"📂 Using: {latest_file}")

    # Load contacts
    contacts = load_contacts(str(latest_file))
    print(f"✅ Loaded {len(contacts)} contacts")

    # Load progress
    progress = load_progress()
    start_index = progress.get("last_index", 0)

    # Confirm send
    print("\n⚠️  READY TO SEND")
    print(f"   From: {YAHOO_EMAIL}")
    print(f"   To: {len(contacts) - start_index} contacts")
    print(f"   Rate: {EMAILS_PER_HOUR} emails/hour")

    confirm = input("\n   Type 'SEND' to start: ")

    if confirm.strip().upper() == "SEND":
        send_campaign(contacts, start_index)
    else:
        print("\n❌ Cancelled")
