#!/usr/bin/env python3
"""
Mythara Email Bot - Automated Draft Generator
Monitors mythara.engine@yahoo.com via Yahoo IMAP and generates email drafts
using local keyword classification. Draft-only: it never sends email.
Previously this file claimed an "OAuth Version" and a Mythara Engine
integration; neither was ever implemented, so both claims were removed.

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import imaplib
import email
import os
from datetime import datetime
from email.header import decode_header
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Yahoo Mail Settings
YAHOO_EMAIL = "mythara.engine@yahoo.com"
YAHOO_APP_PASSWORD = os.getenv("YAHOO_APP_PASSWORD", "")  # Set via environment variable
IMAP_SERVER = "imap.mail.yahoo.com"
IMAP_PORT = 993

# Drafts Directory
DRAFTS_DIR = Path("email_drafts")
DRAFTS_DIR.mkdir(exist_ok=True)

# Log File
LOG_FILE = DRAFTS_DIR / "email_bot.log"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(message):
    """Log messages to file and console"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def decode_email_header(header):
    """Decode email header to handle encoding"""
    if header is None:
        return ""
    decoded = decode_header(header)
    result = []
    for part, encoding in decoded:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or 'utf-8', errors='ignore'))
        else:
            result.append(part)
    return ''.join(result)

def get_email_body(msg):
    """Extract plain text body from email message"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            pass
    return ""

def classify_email(sender, subject, body):
    """Classify email intent using local keyword heuristics (no network, no LLM)"""
    # For now, use simple heuristics (you can add Email_Classifier clause later)
    body_lower = body.lower()
    subject_lower = subject.lower()
    
    # Check for specific patterns
    if any(word in body_lower for word in ["trial", "pilot", "demo", "evaluate"]):
        return {"intent": "pilot_inquiry", "template": "pilot_delivery", "priority": 0.9}
    elif any(word in body_lower for word in ["price", "cost", "expensive", "budget"]):
        return {"intent": "pricing_objection", "template": "objection_price", "priority": 0.8}
    elif any(word in subject_lower for word in ["re:", "fwd:"]):
        return {"intent": "follow_up", "template": "follow_up", "priority": 0.7}
    elif any(word in body_lower for word in ["thank", "received", "reviewing"]):
        return {"intent": "acknowledgement", "template": "thank_you", "priority": 0.5}
    else:
        return {"intent": "initial_inquiry", "template": "initial_outreach", "priority": 0.8}

def generate_draft(sender, sender_name, company, subject, classification):
    """Generate email draft based on classification"""
    
    # Template mappings
    templates = {
        "initial_outreach": """Hi {sender_name},

Thanks for reaching out about Mythara Engine.

We help {industry} organizations deliver cryptographic integrity proofs and SSIP audit metrics
that make compliance validation faster and easier to repeat.

Quick overview:
- **PGP-signed manifests** with SHA-256 integrity hashes
- **Deterministic reproducibility runs** (hash-chained artifacts)
- **Container-based deployment** (air-gap compatible)

Would a 30-day pilot be valuable? I can send the pilot package and credentials today.

Best,
Herbert Velez Jr.
Mythara (planned)
mythara.engine@yahoo.com
Enterprise: $60K/year (firm pricing)""",

        "pilot_delivery": """Hi {sender_name},

Great! I'll send your pilot package today.

You'll receive:
- Secure pilot ZIP with documentation and integrity proofs
- Unique API key (Bearer token) for 30-day trial
- Private container registry access
- 20-minute onboarding call link

I'll follow up in a separate email with the package and credentials within 2 hours.

Best,
Herbert""",

        "follow_up": """Hi {sender_name},

Following up on my previous note. I know schedules get busy.

Quick reminder: Mythara Engine provides cryptographic integrity proofs and SSIP metrics for compliance validation. 30-day container-based pilot available.

If timing isn't right now, no problem—happy to reconnect next quarter.

Best,
Herbert""",

        "objection_price": """Hi {sender_name},

I understand budget considerations. Here's the value perspective:

**What $60K/year covers:**
- Cryptographic integrity proofs (PGP signatures, SHA-256 hashes)
- Deterministic reproducibility runs (hash-chained artifacts)
- SSIP audit metrics (drift suppression, emotional fidelity)
- Priority support and compliance artifacts

**ROI:** Even one prevented compliance incident (~$15-25K) or one faster audit cycle (~$10K saved) offsets the subscription.

**Policy:** Firm pricing (no discounts); 30-day trial is the evaluation mechanism.

Happy to discuss technical details or ROI questions.

Best,
Herbert""",

        "thank_you": """Hi {sender_name},

Thanks for your message. I appreciate you taking the time.

If you have any questions about Mythara Engine or need additional information, feel free to reach out anytime.

Best,
Herbert Velez Jr.
Mythara (planned)
mythara.engine@yahoo.com"""
    }
    
    template_id = classification.get("template", "initial_outreach")
    template = templates.get(template_id, templates["initial_outreach"])
    
    # Simple substitutions
    draft = template.format(
        sender_name=sender_name or "there",
        company=company or "your organization",
        industry="compliance-focused"
    )
    
    return draft

def extract_sender_info(sender):
    """Extract name and email from sender field"""
    # Parse "John Doe <john@example.com>" format
    if "<" in sender and ">" in sender:
        name_part = sender.split("<")[0].strip().strip('"')
        email_part = sender.split("<")[1].split(">")[0].strip()
        return name_part, email_part
    else:
        return "", sender

def save_draft(msg_id, sender, subject, draft_body, classification):
    """Save draft to file for review"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    draft_filename = DRAFTS_DIR / f"draft_{timestamp}_{msg_id}.txt"
    
    with open(draft_filename, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("MYTHARA EMAIL BOT - DRAFT FOR REVIEW\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"Classification: {classification['intent']} (priority: {classification['priority']})\n")
        f.write(f"Template: {classification['template']}\n")
        f.write("\n" + "-"*80 + "\n\n")
        f.write(f"To: {sender}\n")
        f.write(f"Subject: Re: {subject}\n")
        f.write("\n" + "-"*80 + "\n\n")
        f.write(draft_body)
        f.write("\n\n" + "="*80 + "\n")
        f.write("REVIEW INSTRUCTIONS:\n")
        f.write("1. Edit the draft above as needed\n")
        f.write("2. Copy the final text to your email client\n")
        f.write("3. Send from mythara.engine@yahoo.com\n")
        f.write("="*80 + "\n")
    
    log(f"Draft saved: {draft_filename}")
    return draft_filename

# ============================================================================
# MAIN BOT LOGIC
# ============================================================================

def process_emails():
    """Connect to Yahoo Mail and process unread emails"""
    
    # Check for credentials
    if not YAHOO_APP_PASSWORD:
        log("ERROR: YAHOO_APP_PASSWORD environment variable not set")
        log("Generate an app password at: https://account.yahoo.com/security")
        return
    
    try:
        # Connect to Yahoo IMAP
        log(f"Connecting to {IMAP_SERVER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(YAHOO_EMAIL, YAHOO_APP_PASSWORD)
        log("Successfully connected to Yahoo Mail")
        
        # Select inbox
        mail.select("INBOX")
        
        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")
        
        if status != "OK":
            log("ERROR: Failed to search for emails")
            return
        
        msg_ids = messages[0].split()
        log(f"Found {len(msg_ids)} unread emails")
        
        if len(msg_ids) == 0:
            log("No new emails to process")
            mail.logout()
            return
        
        # Process each email
        for msg_id in msg_ids:
            try:
                log(f"Processing email ID: {msg_id.decode()}")
                
                # Fetch email
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                
                if status != "OK":
                    log(f"ERROR: Failed to fetch email {msg_id.decode()}")
                    continue
                
                # Parse email
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract fields
                sender = decode_email_header(email_message.get("From", ""))
                subject = decode_email_header(email_message.get("Subject", ""))
                body = get_email_body(email_message)
                
                log(f"From: {sender}")
                log(f"Subject: {subject}")
                
                # Extract sender name and email
                sender_name, sender_email = extract_sender_info(sender)
                
                # Classify email
                classification = classify_email(sender, subject, body)
                log(f"Classification: {classification['intent']} (template: {classification['template']})")
                
                # Generate draft
                draft_body = generate_draft(
                    sender=sender,
                    sender_name=sender_name,
                    company="",  # TODO: extract from email signature or lookup
                    subject=subject,
                    classification=classification
                )
                
                # Save draft for review
                draft_file = save_draft(
                    msg_id=msg_id.decode(),
                    sender=sender,
                    subject=subject,
                    draft_body=draft_body,
                    classification=classification
                )
                
                log(f"✓ Draft created successfully: {draft_file}")
                
                # Mark as read (optional - comment out to keep as unread)
                # mail.store(msg_id, '+FLAGS', '\\Seen')
                
            except Exception as e:
                log(f"ERROR processing email {msg_id.decode()}: {str(e)}")
                continue
        
        # Logout
        mail.logout()
        log("Disconnected from Yahoo Mail")
        log(f"Session complete. Check {DRAFTS_DIR} for drafts.")
        
    except Exception as e:
        log(f"ERROR in main process: {str(e)}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    log("="*80)
    log("MYTHARA EMAIL BOT - Starting")
    log("="*80)
    process_emails()
    log("="*80)
    log("MYTHARA EMAIL BOT - Complete")
    log("="*80)
