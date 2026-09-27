# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara Email Assistant - AI-powered outreach reply handler

This script:
1. Monitors your email inbox for replies to Mythara outreach
2. Categorizes intent (interested, question, not-interested)
3. Generates draft responses using OpenAI
4. Saves drafts for your review
5. Tracks conversations in CSV
6. Sends daily summary

Usage:
    python email_assistant.py --check-now
    python email_assistant.py --daemon  # runs every hour

Setup required:
    - Gmail/Yahoo API credentials (see SETUP_GUIDE.md)
    - OpenAI API key in environment variable
    - pip install openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import sys
import json
import csv
import base64
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
import argparse

# Email handling
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Warning: Gmail libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# OpenAI for draft generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Conversation tracking
TRACKING_FILE = Path(__file__).parent / "email_tracking.csv"
DRAFTS_LOG = Path(__file__).parent / "draft_responses.json"
CONFIG_FILE = Path(__file__).parent / "email_assistant_config.json"


class EmailAssistant:
    """AI-powered email assistant for Mythara outreach with sales psychology"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_FILE
        self.config = self.load_config()
        self.gmail_service = None
        self.openai_client = None
        self.knowledge_base = None
        
        # Initialize services
        if GMAIL_AVAILABLE:
            self.gmail_service = self.authenticate_gmail()
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize RAG knowledge base
        try:
            from build_knowledge_base import KnowledgeBaseBuilder
            archive_root = Path(__file__).parent.parent
            self.knowledge_base = KnowledgeBaseBuilder(archive_root)
            print("✅ Knowledge base connected")
        except Exception as e:
            print(f"⚠️  Knowledge base not available: {e}")
            self.knowledge_base = None
        
        # Ensure tracking files exist
        self.init_tracking_files()
    
    def load_config(self) -> Dict:
        """Load configuration from file or create defaults"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default config
        default_config = {
            "email_address": "mythara.engine@yahoo.com",
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
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = Path(__file__).parent / 'gmail_token.json'
        credentials_path = Path(__file__).parent / 'gmail_credentials.json'
        
        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    print(f"\nError: Gmail credentials not found at {credentials_path}")
                    print("Follow SETUP_GUIDE.md to create OAuth credentials")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def init_tracking_files(self):
        """Initialize CSV tracking and JSON logs"""
        # CSV tracking
        if not TRACKING_FILE.exists():
            with open(TRACKING_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'message_id', 'thread_id', 'from_email', 
                    'from_name', 'subject', 'intent', 'response_generated',
                    'draft_id', 'sent', 'notes'
                ])
        
        # JSON drafts log
        if not DRAFTS_LOG.exists():
            with open(DRAFTS_LOG, 'w') as f:
                json.dump([], f)
    
    def get_recent_replies(self, days_back: int = 7) -> List[Dict]:
        """Fetch recent email replies"""
        if not self.gmail_service:
            print("Gmail service not authenticated")
            return []
        
        try:
            # Search for recent emails (not sent by you)
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date} -from:me'
            
            # Add label filter if configured
            if self.config.get('outreach_label'):
                query += f' label:{self.config["outreach_label"]}'
            
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            
            # Fetch full message details
            emails = []
            for msg in messages:
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        
        except HttpError as error:
            print(f'Gmail API error: {error}')
            return []
    
    def get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get full email details"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Extract body
            body = self.extract_body(message['payload'])
            
            return {
                'id': message_id,
                'thread_id': message['threadId'],
                'from': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'body': body,
                'snippet': message.get('snippet', '')
            }
        
        except HttpError as error:
            print(f'Error fetching message {message_id}: {error}')
            return None
    
    def extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def categorize_intent(self, email_body: str, subject: str) -> Tuple[str, float]:
        """Categorize email intent using OpenAI"""
        if not self.openai_client:
            # Fallback to keyword matching
            return self.keyword_intent(email_body, subject)
        
        prompt = f"""Analyze this email reply to a B2B software sales outreach about Mythara Engine (an AI integrity/SSIP platform).

Subject: {subject}

Body:
{email_body}

Categorize the intent as ONE of:
- interested (wants a demo, call, more info, pricing)
- question (has a specific question, needs clarification)
- not_interested (no thanks, not now, not a fit)
- out_of_office (auto-reply, OOO)

Return ONLY the category name and a confidence score (0-1) as JSON:
{{"intent": "interested", "confidence": 0.95}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper model
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing sales email replies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            result = json.loads(response.choices[0].message.content)
            return result['intent'], result['confidence']
        
        except Exception as e:
            print(f"OpenAI categorization error: {e}")
            return self.keyword_intent(email_body, subject)
    
    def keyword_intent(self, body: str, subject: str) -> Tuple[str, float]:
        """Fallback keyword-based intent detection"""
        text = (body + " " + subject).lower()
        
        interested_keywords = ['interested', 'demo', 'call', 'meeting', 'pricing', 'more info', 'tell me more', 'sounds good']
        question_keywords = ['question', 'how does', 'what is', 'can you', 'clarify', 'explain']
        not_interested_keywords = ['not interested', 'no thanks', 'not a fit', 'not right now', 'remove', 'unsubscribe']
        ooo_keywords = ['out of office', 'away from', 'automatic reply', 'on vacation']
        
        if any(kw in text for kw in ooo_keywords):
            return 'out_of_office', 0.9
        elif any(kw in text for kw in interested_keywords):
            return 'interested', 0.7
        elif any(kw in text for kw in not_interested_keywords):
            return 'not_interested', 0.8
        elif any(kw in text for kw in question_keywords):
            return 'question', 0.6
        else:
            return 'unknown', 0.3
    
    def generate_draft_response(self, email_data: Dict, intent: str) -> str:
        """Generate draft response using OpenAI + RAG + sales psychology"""
        if not self.openai_client:
            return self.get_template_response(intent)
        
        # Search knowledge base for relevant context
        context_chunks = []
        if self.knowledge_base:
            try:
                search_query = f"{email_data['subject']} {email_data['body'][:200]}"
                context_chunks = self.knowledge_base.search(search_query, n_results=3)
            except Exception as e:
                print(f"Knowledge base search error: {e}")
        
        # Build context from RAG results
        rag_context = ""
        if context_chunks:
            rag_context = "\n\n**RELEVANT MYTHARA DOCS:**\n"
            for chunk in context_chunks:
                rag_context += f"- From {chunk['filepath']}: {chunk['text'][:300]}...\n"
        
        # Honest framing for outbound drafts (no invented scarcity, no fake deadlines)
        sales_psychology = """
**HONEST FRAMING FOR OUTBOUND DRAFTS:**

Hard rule: never invent slot counts, customer numbers, deadlines, prices,
or what other companies are doing. If you do not know it, do not write it.
Real constraints (e.g. Herb's actual onboarding capacity) may be stated
only if Herb provided the exact number.

1. STRAIGHT VALUE (instead of manufactured scarcity):
   - Say what it is: "$500 SSIP audit, 5-day delivery, findings report included"
   - Say who it is for: "teams facing AI audit pressure in the next 90 days"
   - Let fit do the qualifying: "If that is not you, no hard feelings"

2. HONEST RISK FRAMING (instead of invented fines):
   - Reference real obligations: "If your next audit asks for AI explainability evidence, this is the artifact they want"
   - No invented fine amounts, no invented competitor behavior, no invented hours-saved numbers

3. REAL TIMING (instead of fake deadlines):
   - Tie timing to THEIR calendar: "Your audit is in 6 weeks — we deliver in 5 days"
   - Never invent a Friday deadline, a slot count, or a customer count

4. STRATEGIC INDIFFERENCE (takeaway selling):
   - NOT CONVINCING, QUALIFYING: "This might not be a fit if you don't have regulatory pressure right now"
   - WILLING TO WALK: "If timing's not right, totally understand. I'll check back next quarter"
   - SELECTIVE AVAILABILITY: "I'm prioritizing companies with audits in next 90 days—is that you?"
   - HIGH-STATUS POSITIONING: "I only work with teams that can move fast. Can you decide this week or do you need more approvals?"

5. OBJECTION REFRAMING (honest):
   - "Too expensive" → "Compared to what? A failed audit, or the manual work your team already does?"
   - "Need time to think" → "Totally fair. Just tell me your audit timeline and I'll tell you the latest date this still works"
   - "Already have logs" → "That's great—this replaces them with cryptographic proof. But if your current solution passes audits, you probably don't need this"
   - "Not priority" → "Got it. Out of curiosity, when's your next model risk review? [If soon] Ah, then you might want this sooner than you think"
   
6. TONE CALIBRATION:
   - Confident, not arrogant
   - Helpful, not needy
   - Selective, not desperate
   - Indifferent to outcome, obsessed with fit
   - "I don't chase—I qualify and close"

7. CLOSING MECHANICS:
   - ASSUMPTIVE: "I'll send the calendar invite for Tuesday 2pm—does that work or is Wednesday better?"
   - ALTERNATIVE CHOICE: "Do you want the full audit module or just agent override tracking to start?"
   - TIMING TIE: "If your audit is coming up, let's lock a date now so the report is ready in time"
   - TAKEAWAY CLOSE: "If you're not 100% sure, let's not waste time. I'd rather you be certain this solves your problem"
"""
        
        # Build prompt based on intent
        if intent == 'interested':
            instruction = """They are interested. Your goal: QUALIFY + CLOSE FAST.

**HONEST APPLICATION:**
1. Acknowledge interest (1 sentence do not gush)
2. QUALIFY HARD - Quick question do you have regulatory pressure in next 90 days or is this exploratory
3. HONEST FIT - At the $500 early adopter rate I am prioritizing companies with near-term audit pressure
4. REAL TIMING - Starting sooner means more audit evidence on record when you need it
5. ASSUMPTIVE CLOSE - I am booking Tuesday or Wednesday this week Which works better 10am or 2pm MT
6. INDIFFERENCE SAFETY NET - If timing is not right totally understand — no pressure, the early adopter rate stands while the program runs
7. Keep under 130 words
8. Sign as Herbert

**TONE:** Confident selector. Helpful but outcome-independent.

**DO NOT:**
- Sound desperate
- Over-explain features
- Ask permission (TELL them the next step)"""

        elif intent == 'question':
            instruction = """They have a question. Your goal: ANSWER BRIEFLY + ADVANCE.

**HONEST APPLICATION:**
1. Answer their question directly (2 sentences max use RAG context)
2. REFRAME TO TIMING - Tie answer to their audit timeline, not an invented deadline
3. HONEST NEXT STEP - Offer the validation report sample so they can evaluate async
4. REAL TIMING - Reference the $500 early adopter rate and their own calendar, never invent a deadline
5. ASSUMPTIVE ADVANCE - 15-min screen share Tuesday or Wednesday which is better
6. INDIFFERENCE OPTION - Or I can send our validation report now and you can evaluate async up to you
7. Keep under 140 words
8. Sign as Herbert

**TONE:** Expert who is busy. Helpful but not hand-holding.

**DO NOT:**
- Write a technical manual
- Say let me know if you have more questions (too passive)
- Invent deadlines, slot counts, or customer numbers"""

        elif intent == 'not_interested':
            instruction = """They are not interested RIGHT NOW. Your goal: STRATEGIC INDIFFERENCE + PLANT FEAR SEED + REFERRAL.

**HONEST APPLICATION:**
1. TOTAL INDIFFERENCE - No problem at all appreciate you letting me know
2. HONEST DOOR-OPEN - If your next audit asks for AI explainability evidence, feel free to reach out (casual not pushy)
3. CLEAN EXIT - I only take on new clients when the timing is right for both sides, so no hard feelings
4. REFERRAL ASK - Quick question do you know anyone at competitor handling model risk Happy to help them out
5. FINAL VALUE OFFER - If you ever need our validation report as a benchmark just ping me
6. Keep under 70 words
7. Sign as Herbert

**TONE:** Completely outcome-independent. High status.

**DO NOT:**
- Try to overcome objection
- Sound rejected or defensive
- Use needy language"""

        else:  # unknown/question
            instruction = """Unclear intent. Your goal: QUALIFY HARD + ADVANCE TO A DECISION.

**HONEST APPLICATION:**
1. Acknowledge their email (1 sentence)
2. QUALIFY HARD - Quick clarification do you have an upcoming audit or review or is this more exploratory
3. HONEST FIT - At the $500 early adopter rate I am prioritizing companies with near-term need
4. REAL TIMING - If they are exploratory, suggest reconnecting when audit pressure arrives
5. ASSUMPTIVE CLOSE - If it is urgent Tuesday 10am or Wednesday 2pm MT work for a 15-min overview
6. INDIFFERENT EXIT - If timing is not right totally cool — happy to reconnect when it is
7. Keep under 110 words
8. Sign as Herbert

**TONE:** Qualifying gatekeeper. Outcome-independent."""
        
        prompt = f"""You are Herbert Velez Jr., founder of Mythara Engine (SSIP platform for AI accountability).

You are a SALES CLOSER, not customer support. Every email must advance the deal.

**THEIR EMAIL:**
Subject: {email_data['subject']}
Body: {email_data['body']}

{rag_context}

{sales_psychology}

**INSTRUCTIONS FOR THIS RESPONSE:**
{instruction}

**NOW WRITE THE EMAIL:**"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Herbert, founder of Mythara Engine. You sell honestly: consultative, pain-point focused, always advancing toward a clear next step. You are direct and helpful. You never invent deadlines, slot counts, customer numbers, or prices — no manufactured urgency."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI draft generation error: {e}")
            return self.get_template_response(intent)
        
        instruction = templates.get(intent, templates['interested'])
        
        prompt = f"""You are Herbert Velez Jr., founder of Mythara Engine (AI integrity/SSIP platform for model risk, clinical AI, and cybersecurity).

Original email you sent was about: Mythara Engine - cryptographic integrity + SSIP audit trails for AI workflows. Pricing: $500 early adopter or $2,500 standard.

They replied:
---
Subject: {email_data['subject']}
{email_data['body']}
---

{instruction}

Write the draft response now:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Herbert, a technical founder who writes concise, helpful B2B sales emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI draft generation error: {e}")
            return self.get_template_response(intent)
    
    def get_template_response(self, intent: str) -> str:
        """Fallback template responses"""
        templates = {
            'interested': """Thanks for getting back to me!

I'd love to show you Mythara's SSIP audit logs and integrity hashing in action. Would you be open to a quick 15-minute walkthrough this week?

Here are a few times that work for me:
- Tuesday 2pm MT
- Wednesday 10am MT
- Thursday 3pm MT

Let me know what works best, or feel free to suggest another time.

— Herbert
Mythara.Engine@yahoo.com""",
            
            'question': """Great question. [ANSWER THEIR QUESTION HERE]

The easiest way to see how this works is a quick 15-minute screen share. Would Tuesday or Wednesday this week work for a call?

— Herbert
Mythara.Engine@yahoo.com""",
            
            'not_interested': """No problem at all — thanks for considering it.

If your priorities shift or you know someone at another company who might be interested in AI integrity/SSIP compliance, I'd appreciate the intro.

Best of luck!

— Herbert"""
        }
        
        return templates.get(intent, templates['interested'])
    
    def create_gmail_draft(self, thread_id: str, to_email: str, subject: str, body: str) -> Optional[str]:
        """Create draft in Gmail"""
        if not self.gmail_service:
            print("Gmail service not available")
            return None
        
        try:
            message = {
                'message': {
                    'threadId': thread_id,
                    'raw': self.create_message(to_email, subject, body)
                }
            }
            
            draft = self.gmail_service.users().drafts().create(
                userId='me',
                body=message
            ).execute()
            
            return draft['id']
        
        except HttpError as error:
            print(f'Error creating draft: {error}')
            return None
    
    def create_message(self, to: str, subject: str, body: str) -> str:
        """Create base64 encoded email message"""
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
        
        return base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    def track_conversation(self, email_data: Dict, intent: str, draft_id: Optional[str]):
        """Log conversation to CSV"""
        from_match = re.search(r'<(.+?)>', email_data['from'])
        from_email = from_match.group(1) if from_match else email_data['from']
        from_name = email_data['from'].split('<')[0].strip() if '<' in email_data['from'] else from_email
        
        with open(TRACKING_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                email_data['id'],
                email_data['thread_id'],
                from_email,
                from_name,
                email_data['subject'],
                intent,
                True,
                draft_id or '',
                False,
                ''
            ])
    
    def process_new_replies(self) -> Dict:
        """Main processing loop"""
        print("\n🔍 Checking for new email replies...")
        
        # Get recent emails
        emails = self.get_recent_replies(days_back=self.config['search_days_back'])
        
        if not emails:
            print("No new emails found")
            return {'processed': 0, 'drafts_created': 0}
        
        print(f"Found {len(emails)} emails to process")
        
        # Load existing tracking to avoid duplicates
        tracked_ids = set()
        if TRACKING_FILE.exists():
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                tracked_ids = {row['message_id'] for row in reader}
        
        processed = 0
        drafts_created = 0
        
        for email in emails:
            # Skip if already processed
            if email['id'] in tracked_ids:
                continue
            
            print(f"\n📧 Processing: {email['subject'][:50]}...")
            
            # Categorize intent
            intent, confidence = self.categorize_intent(email['body'], email['subject'])
            print(f"   Intent: {intent} ({confidence:.0%} confidence)")
            
            # Skip out-of-office
            if intent == 'out_of_office':
                print("   ⏭️  Skipping (out of office)")
                continue
            
            # Generate draft response
            draft_body = self.generate_draft_response(email, intent)
            print(f"   ✍️  Draft generated ({len(draft_body)} chars)")
            
            # Extract sender email
            from_match = re.search(r'<(.+?)>', email['from'])
            to_email = from_match.group(1) if from_match else email['from']
            
            # Create draft in Gmail
            draft_id = self.create_gmail_draft(
                email['thread_id'],
                to_email,
                email['subject'],
                draft_body
            )
            
            if draft_id:
                print(f"   ✅ Draft created in Gmail (ID: {draft_id})")
                drafts_created += 1
            
            # Track conversation
            self.track_conversation(email, intent, draft_id)
            processed += 1
        
        print(f"\n✅ Processed {processed} new emails, created {drafts_created} drafts")
        return {'processed': processed, 'drafts_created': drafts_created}
    
    def generate_summary_report(self) -> str:
        """Generate daily summary from tracking CSV"""
        if not TRACKING_FILE.exists():
            return "No tracking data available"
        
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        
        # Last 24 hours
        cutoff = datetime.now() - timedelta(days=1)
        recent = [r for r in reader if datetime.fromisoformat(r['timestamp']) > cutoff]
        
        # Count by intent
        intent_counts = {}
        for row in recent:
            intent = row['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        report = f"""
📊 Mythara Email Assistant - 24 Hour Summary
{'='*50}

Total replies: {len(recent)}

By intent:
"""
        for intent, count in sorted(intent_counts.items(), key=lambda x: -x[1]):
            report += f"  • {intent}: {count}\n"
        
        report += f"\nDrafts created: {sum(1 for r in recent if r['draft_id'])}\n"
        report += f"Sent: {sum(1 for r in recent if r['sent'] == 'True')}\n"
        
        # Action items
        needs_review = [r for r in recent if r['draft_id'] and r['sent'] == 'False']
        if needs_review:
            report += f"\n⚠️  {len(needs_review)} drafts waiting for your review in Gmail\n"
        
        return report


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Mythara Email Assistant')
    parser.add_argument('--check-now', action='store_true', help='Check emails once and exit')
    parser.add_argument('--daemon', action='store_true', help='Run continuously (check every hour)')
    parser.add_argument('--summary', action='store_true', help='Generate 24-hour summary report')
    parser.add_argument('--setup', action='store_true', help='Run first-time setup wizard')
    
    args = parser.parse_args()
    
    # Setup wizard
    if args.setup:
        print("\n🚀 Mythara Email Assistant Setup")
        print("="*50)
        print("\nThis will guide you through:")
        print("1. Gmail API credentials")
        print("2. OpenAI API key")
        print("3. Email preferences")
        print("\nSee SETUP_GUIDE.md for detailed instructions")
        return
    
    # Create assistant
    assistant = EmailAssistant()
    
    # Summary report
    if args.summary:
        print(assistant.generate_summary_report())
        return
    
    # Check now
    if args.check_now:
        assistant.process_new_replies()
        return
    
    # Daemon mode
    if args.daemon:
        print("🤖 Starting email assistant daemon (checks every hour)")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                assistant.process_new_replies()
                print("\n💤 Sleeping for 1 hour...")
                time.sleep(3600)  # 1 hour
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                break
    else:
        # No args = show help
        parser.print_help()


if __name__ == '__main__':
    main()
