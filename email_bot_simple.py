#!/usr/bin/env python3
"""
Mythara Email Bot - Simple Manual Version
Read exported emails and generate drafts using local keyword classification
and templates. Draft-only: it never sends email.

Copyright © 2025 Herbert Velez Jr. All rights reserved.

SETUP INSTRUCTIONS:
1. Export emails from Yahoo Mail to a folder (as .eml files)
2. Point INBOX_DIR at that folder (default: ./inbox_export)
3. Run this script: it processes the exports, then offers interactive mode
4. Drafts land in email_drafts/ AND in Commercial/outreach_queue/
   (pending Herb's approval) for review
"""

import os
import sys
import email
from email.header import decode_header
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories
INBOX_DIR = Path("inbox_export")  # Put exported .eml emails here
DRAFTS_DIR = Path("email_drafts")
DRAFTS_DIR.mkdir(exist_ok=True)
LOG_FILE = DRAFTS_DIR / "email_bot.log"

# Outreach queue (draft-only approval queue). Optional: if unavailable,
# drafts still land in email_drafts/.
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Commercial"))
    from outreach_queue import OutreachQueue
    OUTREACH_AVAILABLE = True
except Exception:
    OUTREACH_AVAILABLE = False

# ============================================================================
# SIMPLIFIED APPROACH
# ============================================================================

def log(message):
    """Log messages"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def classify_email(sender, subject, body):
    """Classify email intent"""
    body_lower = body.lower()
    
    if any(word in body_lower for word in ["trial", "pilot", "demo"]):
        return {"intent": "pilot_inquiry", "template": "pilot_delivery"}
    elif any(word in body_lower for word in ["price", "cost", "expensive"]):
        return {"intent": "pricing_objection", "template": "objection_price"}
    elif "re:" in subject.lower():
        return {"intent": "follow_up", "template": "follow_up"}
    else:
        return {"intent": "initial_inquiry", "template": "initial_outreach"}

def generate_draft(sender_name, classification):
    """Generate email draft"""
    templates = {
        "initial_outreach": f"""Hi {sender_name},

Thanks for reaching out about Mythara Engine.

We help compliance-focused organizations deliver cryptographic integrity proofs and SSIP audit metrics
that make validation faster and easier to repeat.

Would a 30-day pilot be valuable? I can send the pilot package today.

Best,
Herbert Velez Jr.
Mythara (planned)
mythara.engine@yahoo.com
Enterprise: $60K/year (firm pricing)""",

        "pilot_delivery": f"""Hi {sender_name},

Great! I'll send your pilot package today with:
- Secure pilot ZIP with documentation
- Unique API key for 30-day trial
- Container registry access

I'll follow up within 2 hours with the package.

Best,
Herbert""",

        "follow_up": f"""Hi {sender_name},

Following up on my previous note. Mythara Engine provides cryptographic integrity proofs for compliance validation.

30-day container-based pilot available if timing works.

Best,
Herbert""",

        "objection_price": f"""Hi {sender_name},

I understand budget considerations.

$60K/year covers:
- Cryptographic integrity proofs
- Deterministic reproducibility runs
- SSIP audit metrics
- Priority support

Even one prevented compliance incident offsets the subscription.

Firm pricing; 30-day trial is the evaluation period.

Best,
Herbert"""
    }
    
    template_id = classification.get("template", "initial_outreach")
    return templates.get(template_id, templates["initial_outreach"])

def decode_email_header(header):
    """Decode a possibly-encoded email header"""
    if header is None:
        return ""
    parts = []
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            parts.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            parts.append(part)
    return "".join(parts)


def get_email_body(msg):
    """Extract plain text body from a parsed email message"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode("utf-8", errors="ignore")
                except Exception:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception:
            pass
    return ""


def extract_sender_info(sender):
    """Split 'John Doe <john@example.com>' into (name, email)"""
    if "<" in sender and ">" in sender:
        name_part = sender.split("<")[0].strip().strip('"')
        email_part = sender.split("<")[1].split(">")[0].strip()
        return name_part, email_part
    return "", sender


def process_manual_email(sender, sender_name, subject, body):
    """Process a single email and generate draft"""
    classification = classify_email(sender, subject, body)
    draft_body = generate_draft(sender_name, classification)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    draft_filename = DRAFTS_DIR / f"draft_{timestamp}.txt"

    with open(draft_filename, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("MYTHARA EMAIL BOT - DRAFT FOR REVIEW\n")
        f.write("="*80 + "\n\n")
        f.write(f"To: {sender}\n")
        f.write(f"Subject: Re: {subject}\n")
        f.write(f"\nClassification: {classification['intent']}\n")
        f.write("\n" + "-"*80 + "\n\n")
        f.write(draft_body)
        f.write("\n\n" + "="*80 + "\n")

    log(f"Draft created: {draft_filename}")

    # Also queue for Herb's approval in the shared outreach queue.
    if OUTREACH_AVAILABLE:
        queued = OutreachQueue().queue(
            kind="email",
            title=f"Reply to {sender_name or sender}",
            body=f"To: {sender}\nSubject: Re: {subject}\n\n{draft_body}",
            meta={
                "to": sender,
                "classification": classification["intent"],
                "source": "email_bot_simple",
            },
        )
        log(f"Queued for approval: {queued}")

    return draft_filename


def process_export_folder(folder=None):
    """
    Read .eml files exported from Yahoo Mail and generate a draft for each.
    This is what INBOX_DIR is for — previously nothing ever read it.
    """
    folder = Path(folder) if folder else INBOX_DIR
    eml_files = sorted(folder.glob("*.eml")) if folder.exists() else []

    if not eml_files:
        log(f"No .eml files in {folder} — export emails from Yahoo Mail there first.")
        return []

    results = []
    for eml_path in eml_files:
        try:
            with open(eml_path, "rb") as f:
                msg = email.message_from_binary_file(f)
            sender = decode_email_header(msg.get("From", ""))
            subject = decode_email_header(msg.get("Subject", ""))
            body = get_email_body(msg)
            sender_name, sender_email = extract_sender_info(sender)
            draft = process_manual_email(
                sender=sender_email or sender,
                sender_name=sender_name or "there",
                subject=subject,
                body=body,
            )
            results.append(str(draft))
            log(f"✓ {eml_path.name} -> {draft}")
        except Exception as e:
            log(f"ERROR processing {eml_path.name}: {e}")

    return results

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """Run bot in interactive mode - you paste email details"""
    log("="*80)
    log("MYTHARA EMAIL BOT - Interactive Mode")
    log("="*80)
    
    print("\n" + "="*80)
    print("MYTHARA EMAIL BOT")
    print("="*80)
    print("\nThis bot will help you generate email drafts.")
    print("You'll paste email details, and it will create a draft response.\n")
    
    while True:
        print("\n" + "-"*80)
        print("Enter email details (or type 'quit' to exit):")
        print("-"*80)
        
        sender_email = input("\nSender's email address: ").strip()
        if sender_email.lower() == 'quit':
            break
            
        sender_name = input("Sender's name (or press Enter to skip): ").strip() or "there"
        subject = input("Email subject: ").strip()
        
        print("\nEmail body (paste the message, then press Enter twice):")
        body_lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                body_lines.append(line)
        body = "\n".join(body_lines)
        
        # Generate draft
        print("\n" + "="*80)
        print("Generating draft...")
        print("="*80)
        
        draft_file = process_manual_email(
            sender=sender_email,
            sender_name=sender_name,
            subject=subject,
            body=body
        )
        
        print(f"\n✓ Draft saved to: {draft_file}")
        print("\nYou can:")
        print("1. Open the file to review the draft")
        print("2. Copy it to Yahoo Mail")
        print("3. Process another email\n")
        
        continue_prompt = input("Process another email? (yes/no): ").strip().lower()
        if continue_prompt != 'yes':
            break
    
    print("\n" + "="*80)
    print(f"All drafts saved to: {DRAFTS_DIR}")
    if OUTREACH_AVAILABLE:
        print("Also queued in Commercial/outreach_queue/ pending Herb's approval.")
    else:
        print("NOTE: outreach queue unavailable — drafts are in email_drafts/ only.")
    print("="*80)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # First, process any exported .eml files (the documented setup path).
    process_export_folder()
    # Then offer interactive mode.
    interactive_mode()
