#!/usr/bin/env python3
"""
Mythara Email Bot - AI Email Assistant
Smart inbox triage, phishing detection, auto-responses with Soul Cradle manipulation detection

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os
import re

# Mythara Engine integration (when SDK available)
try:
    from mythara_engine_sdk import MytharaEngine, ProductConfig
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  Mythara Engine SDK not available - running in standalone mode")


class EmailPriority(Enum):
    """Email priority levels"""
    URGENT = "URGENT"           # Requires immediate response
    HIGH = "HIGH"               # Important, respond today
    NORMAL = "NORMAL"           # Regular priority
    LOW = "LOW"                 # Can wait
    SPAM = "SPAM"               # Likely spam/phishing


class EmailCategory(Enum):
    """Email categories"""
    WORK = "WORK"
    PERSONAL = "PERSONAL"
    FINANCE = "FINANCE"
    SHOPPING = "SHOPPING"
    SOCIAL = "SOCIAL"
    NEWSLETTER = "NEWSLETTER"
    SPAM = "SPAM"
    PHISHING = "PHISHING"


@dataclass
class EmailAnalysis:
    """Email analysis result"""
    email_id: str
    from_address: str
    to_address: str
    subject: str
    body_preview: str
    received_date: datetime
    priority: EmailPriority
    category: EmailCategory
    is_phishing: bool
    phishing_indicators: List[str]
    manipulation_detected: bool
    manipulation_tactics: List[str]
    suggested_response: Optional[str]
    sentiment_score: float  # 0.0-1.0
    integrity_hash: str


@dataclass
class AutoResponse:
    """Auto-response template"""
    response_id: str
    trigger_keywords: List[str]
    category: EmailCategory
    response_template: str
    use_count: int


class EmailBot:
    """
    Mythara Email Bot - AI Email Assistant

    Analyzes email text you supply (it has no inbox connection and no
    send capability — drafts/suggestions only, by design).

    Features:
    - Email triage (priority + category classification)
    - Phishing detection (URL analysis, sender verification)
    - Manipulation detection (emotional extortion, urgency tactics)
    - Auto-responses (template-based reply suggestions)
    - Email summarization
    """

    def __init__(self, user_email: str, database_path: Optional[str] = None):
        self.user_email = user_email

        # Database setup
        if database_path:
            self.db_path = database_path
        else:
            home_dir = os.path.expanduser("~")
            mythara_dir = os.path.join(home_dir, ".mythara_engine", "EmailBot")
            os.makedirs(mythara_dir, exist_ok=True)
            self.db_path = os.path.join(mythara_dir, "email_bot.db")

        self._init_database()

        # Mythara Engine integration
        if SDK_AVAILABLE:
            config = ProductConfig(
                product_name="EmailBot",
                product_version="1.0.0",
                database_name=self.db_path,
                custom_clauses=["phishing_detection", "manipulation_detection"],
                branding={"tagline": "Smart Email Management"}
            )
            self.engine = MytharaEngine(config, user_id=user_email)
        else:
            self.engine = None
        
        # Phishing indicators
        self.phishing_domains = [
            "paypal-security.com", "amazon-verify.com", "apple-support.net",
            "microsoft-account.com", "bank-alert.com", "irs-refund.com"
        ]
        
        self.phishing_keywords = [
            "verify your account", "confirm your identity", "urgent action required",
            "click here immediately", "suspended account", "unusual activity",
            "claim your prize", "limited time offer", "act now"
        ]
        
        # Manipulation tactics (emotional extortion)
        self.manipulation_keywords = [
            "you must", "you have to", "final notice", "last chance",
            "don't miss out", "everyone else", "you'll regret",
            "limited spots", "exclusive invitation", "fear of missing out"
        ]
        
        print(f"\n📧 Mythara Email Bot initialized for: {user_email}")
        print(f"📊 Database: {self.db_path}")
        print("📝 Mode: analyze supplied text only — no inbox, no sending (draft-only)")
        if self.engine:
            print(f"✅ Mythara Engine SDK: ACTIVE")
        print()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                email_id TEXT PRIMARY KEY,
                from_address TEXT,
                to_address TEXT,
                subject TEXT,
                body_preview TEXT,
                received_date TEXT,
                priority TEXT,
                category TEXT,
                is_phishing INTEGER,
                phishing_indicators TEXT,  -- JSON array
                manipulation_detected INTEGER,
                manipulation_tactics TEXT,  -- JSON array
                sentiment_score REAL,
                processed INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0,
                integrity_hash TEXT
            )
        """)
        
        # Auto-responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_responses (
                response_id TEXT PRIMARY KEY,
                trigger_keywords TEXT,  -- JSON array
                category TEXT,
                response_template TEXT,
                use_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        
        # Sent responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_responses (
                sent_id TEXT PRIMARY KEY,
                email_id TEXT,
                response_text TEXT,
                sent_date TEXT,
                FOREIGN KEY (email_id) REFERENCES emails(email_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Create default auto-responses
        self._create_default_auto_responses()
    
    def _create_default_auto_responses(self):
        """Create default auto-response templates"""
        default_responses = [
            {
                "trigger_keywords": ["meeting", "schedule", "availability"],
                "category": EmailCategory.WORK,
                "template": "Thank you for your email. I'm happy to schedule a meeting. My availability this week is [INSERT AVAILABILITY]. Please let me know what works for you."
            },
            {
                "trigger_keywords": ["invoice", "payment", "receipt"],
                "category": EmailCategory.FINANCE,
                "template": "Thank you for your message. I've received your invoice and will process payment within [INSERT TIMEFRAME]. Please let me know if you need any additional information."
            },
            {
                "trigger_keywords": ["question", "help", "support"],
                "category": EmailCategory.WORK,
                "template": "Thank you for reaching out. I'd be happy to help. [INSERT ANSWER]. Please let me know if you have any other questions."
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for resp in default_responses:
            response_id = f"AUTO_{resp['category'].value}_{len(resp['trigger_keywords'])}"
            
            cursor.execute("SELECT response_id FROM auto_responses WHERE response_id = ?", (response_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO auto_responses
                    (response_id, trigger_keywords, category, response_template, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    response_id,
                    json.dumps(resp['trigger_keywords']),
                    resp['category'].value,
                    resp['template'],
                    datetime.utcnow().isoformat()
                ))
        
        conn.commit()
        conn.close()
    
    def _compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def analyze_email(self, from_address: str, subject: str, body: str,
                     received_date: Optional[datetime] = None) -> EmailAnalysis:
        """
        Analyze email for priority, category, phishing, and manipulation
        
        Returns EmailAnalysis with classification and security results
        """
        email_id = f"EMAIL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{from_address[:8]}"
        
        if not received_date:
            received_date = datetime.utcnow()
        
        body_lower = body.lower()
        subject_lower = subject.lower()
        combined_text = f"{subject_lower} {body_lower}"
        
        # Phishing detection
        is_phishing = False
        phishing_indicators = []
        
        # Check domain
        for domain in self.phishing_domains:
            if domain in from_address.lower():
                is_phishing = True
                phishing_indicators.append(f"Suspicious domain: {domain}")
        
        # Check phishing keywords
        for keyword in self.phishing_keywords:
            if keyword in combined_text:
                is_phishing = True
                phishing_indicators.append(f"Phishing keyword: '{keyword}'")
        
        # Check for suspicious URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, body)
        for url in urls:
            if any(domain in url.lower() for domain in self.phishing_domains):
                is_phishing = True
                phishing_indicators.append(f"Suspicious URL: {url}")
        
        # Manipulation detection
        manipulation_detected = False
        manipulation_tactics = []
        
        for tactic in self.manipulation_keywords:
            if tactic in combined_text:
                manipulation_detected = True
                manipulation_tactics.append(tactic)
        
        # Category classification
        if is_phishing:
            category = EmailCategory.PHISHING
        elif "invoice" in combined_text or "payment" in combined_text:
            category = EmailCategory.FINANCE
        elif "meeting" in combined_text or "schedule" in combined_text:
            category = EmailCategory.WORK
        elif "order" in combined_text or "shipping" in combined_text:
            category = EmailCategory.SHOPPING
        elif "unsubscribe" in body_lower:
            category = EmailCategory.NEWSLETTER
        else:
            category = EmailCategory.PERSONAL
        
        # Priority classification
        if is_phishing:
            priority = EmailPriority.SPAM
        elif "urgent" in combined_text or "asap" in combined_text or "immediately" in combined_text:
            priority = EmailPriority.URGENT
        elif category == EmailCategory.WORK and not manipulation_detected:
            priority = EmailPriority.HIGH
        elif category == EmailCategory.NEWSLETTER:
            priority = EmailPriority.LOW
        else:
            priority = EmailPriority.NORMAL
        
        # Sentiment analysis (simple)
        positive_words = ["thank", "appreciate", "great", "excellent", "wonderful"]
        negative_words = ["complaint", "issue", "problem", "disappointed", "unacceptable"]
        
        positive_count = sum(1 for word in positive_words if word in combined_text)
        negative_count = sum(1 for word in negative_words if word in combined_text)
        
        sentiment_score = 0.5 + (positive_count * 0.1) - (negative_count * 0.1)
        sentiment_score = max(0.0, min(1.0, sentiment_score))
        
        # Generate suggested response (if applicable)
        suggested_response = None
        if category == EmailCategory.WORK and not is_phishing:
            suggested_response = self._generate_suggested_response(subject, body, category)
        
        # Create analysis
        body_preview = body[:200] + "..." if len(body) > 200 else body
        
        data = {
            "email_id": email_id,
            "from_address": from_address,
            "subject": subject,
            "received_date": received_date.isoformat()
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        analysis = EmailAnalysis(
            email_id=email_id,
            from_address=from_address,
            to_address=self.user_email,
            subject=subject,
            body_preview=body_preview,
            received_date=received_date,
            priority=priority,
            category=category,
            is_phishing=is_phishing,
            phishing_indicators=phishing_indicators,
            manipulation_detected=manipulation_detected,
            manipulation_tactics=manipulation_tactics,
            suggested_response=suggested_response,
            sentiment_score=sentiment_score,
            integrity_hash=integrity_hash
        )
        
        # Store in database
        self._store_email_analysis(analysis)
        
        # Mythara Engine integration
        if self.engine:
            self.engine.soul_cradle.analyze(body)
            if manipulation_detected:
                self.engine.soul_cradle.detect_manipulation(
                    text=body,
                    manipulation_types=manipulation_tactics
                )
        
        return analysis
    
    def _generate_suggested_response(self, subject: str, body: str, category: EmailCategory) -> Optional[str]:
        """Generate suggested response based on email content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find matching auto-response template
        cursor.execute("""
            SELECT response_template, trigger_keywords
            FROM auto_responses
            WHERE category = ?
        """, (category.value,))
        
        for row in cursor.fetchall():
            template = row[0]
            keywords = json.loads(row[1])
            
            # Check if any trigger keyword matches
            body_lower = f"{subject.lower()} {body.lower()}"
            if any(keyword in body_lower for keyword in keywords):
                conn.close()
                return template
        
        conn.close()
        return None
    
    def _store_email_analysis(self, analysis: EmailAnalysis):
        """Store email analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO emails
            (email_id, from_address, to_address, subject, body_preview, received_date,
             priority, category, is_phishing, phishing_indicators, manipulation_detected,
             manipulation_tactics, sentiment_score, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis.email_id, analysis.from_address, analysis.to_address,
            analysis.subject, analysis.body_preview, analysis.received_date.isoformat(),
            analysis.priority.value, analysis.category.value, int(analysis.is_phishing),
            json.dumps(analysis.phishing_indicators), int(analysis.manipulation_detected),
            json.dumps(analysis.manipulation_tactics), analysis.sentiment_score,
            analysis.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def get_inbox_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get inbox summary for past N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Total emails by priority
        cursor.execute("""
            SELECT priority, COUNT(*) as count
            FROM emails
            WHERE DATE(received_date) >= ?
            GROUP BY priority
        """, (start_date,))
        
        priority_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total emails by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM emails
            WHERE DATE(received_date) >= ?
            GROUP BY category
        """, (start_date,))
        
        category_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Phishing/manipulation stats
        cursor.execute("""
            SELECT 
                SUM(is_phishing) as phishing_count,
                SUM(manipulation_detected) as manipulation_count
            FROM emails
            WHERE DATE(received_date) >= ?
        """, (start_date,))
        
        row = cursor.fetchone()
        phishing_count = row[0] or 0
        manipulation_count = row[1] or 0
        
        conn.close()
        
        return {
            "period": f"{days} days",
            "priority_breakdown": priority_counts,
            "category_breakdown": category_counts,
            # Detected, not blocked: this bot analyzes supplied text and has
            # no inbox connection, so it cannot block anything.
            "phishing_detected": phishing_count,
            "manipulation_detected": manipulation_count
        }
    
    def create_auto_response(self, trigger_keywords: List[str], category: EmailCategory,
                            response_template: str) -> str:
        """Create custom auto-response template"""
        response_id = f"AUTO_{category.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO auto_responses
            (response_id, trigger_keywords, category, response_template, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            response_id,
            json.dumps(trigger_keywords),
            category.value,
            response_template,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Auto-response created: {response_id}")
        return response_id


def main():
    """Demo: Email Bot usage (all examples below are synthetic, not real emails)"""
    print("="*70)
    print("    MYTHARA EMAIL BOT - AI EMAIL ASSISTANT")
    print("="*70)
    print("  NOTE: every demo email below is a SYNTHETIC example,")
    print("  written for this demo. None of them are real messages.")
    print("="*70)
    
    # Initialize bot
    bot = EmailBot(user_email="user@example.com")
    
    # Demo 1: Normal work email (SYNTHETIC example)
    print("\n📧 DEMO 1: Normal Work Email [synthetic]")
    print("-"*70)
    analysis1 = bot.analyze_email(
        from_address="colleague@company.com",
        subject="Q4 Budget Meeting",
        body="Hi, can we schedule a meeting to discuss the Q4 budget? I'm available Tuesday and Thursday this week. Let me know what works for you."
    )
    print(f"\n✅ Email Analysis:")
    print(f"   Priority: {analysis1.priority.value}")
    print(f"   Category: {analysis1.category.value}")
    print(f"   Phishing: {analysis1.is_phishing}")
    print(f"   Manipulation: {analysis1.manipulation_detected}")
    print(f"   Sentiment: {analysis1.sentiment_score:.2f}")
    if analysis1.suggested_response:
        print(f"\n💡 Suggested Response:")
        print(f"   {analysis1.suggested_response}")
    
    # Demo 2: Phishing email (SYNTHETIC example)
    print("\n📧 DEMO 2: Phishing Email [synthetic]")
    print("-"*70)
    analysis2 = bot.analyze_email(
        from_address="security@paypal-security.com",
        subject="URGENT: Verify Your Account",
        body="Your PayPal account has been suspended due to unusual activity. Click here immediately to verify your identity or your account will be permanently closed. Act now!"
    )
    print(f"\n🚨 Email Analysis:")
    print(f"   Priority: {analysis2.priority.value}")
    print(f"   Category: {analysis2.category.value}")
    print(f"   Phishing: {analysis2.is_phishing} ⚠️")
    print(f"   Phishing Indicators:")
    for indicator in analysis2.phishing_indicators:
        print(f"      • {indicator}")
    
    # Demo 3: Manipulation tactics (SYNTHETIC example)
    print("\n📧 DEMO 3: Marketing Email with Manipulation [synthetic]")
    print("-"*70)
    analysis3 = bot.analyze_email(
        from_address="marketing@deals.com",
        subject="Last Chance! Limited Time Offer",
        body="You must act now! This is your final notice. Everyone else has already signed up. Don't miss out on this exclusive invitation. Limited spots remaining!"
    )
    print(f"\n⚠️ Email Analysis:")
    print(f"   Priority: {analysis3.priority.value}")
    print(f"   Category: {analysis3.category.value}")
    print(f"   Manipulation Detected: {analysis3.manipulation_detected}")
    print(f"   Manipulation Tactics:")
    for tactic in analysis3.manipulation_tactics:
        print(f"      • {tactic}")
    
    # Demo 4: Inbox summary
    print("\n📊 DEMO 4: Inbox Summary (7 Days)")
    print("-"*70)
    summary = bot.get_inbox_summary(days=7)
    print(f"\n📈 Inbox Summary:")
    print(f"   Period: {summary['period']}")
    print(f"\n   Priority Breakdown:")
    for priority, count in summary['priority_breakdown'].items():
        print(f"      {priority}: {count}")
    print(f"\n   Category Breakdown:")
    for category, count in summary['category_breakdown'].items():
        print(f"      {category}: {count}")
    print(f"\n   🛡️ Security:")
    print(f"      Phishing Detected: {summary['phishing_detected']}")
    print(f"      Manipulation Detected: {summary['manipulation_detected']}")
    
    # Demo 5: Create custom auto-response
    print("\n📧 DEMO 5: Create Custom Auto-Response")
    print("-"*70)
    response_id = bot.create_auto_response(
        trigger_keywords=["demo", "presentation", "showcase"],
        category=EmailCategory.WORK,
        response_template="Thank you for your interest in a demo. I'd be happy to showcase our product. Please book a time on my calendar: [INSERT CALENDAR LINK]"
    )
    print(f"   Response ID: {response_id}")
    
    print("\n" + "="*70)
    print("✅ Email Bot demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
