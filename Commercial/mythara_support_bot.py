import os
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara Support Chat Bot - Customer Support Automation
- Ticket creation and management
- FAQ responses with keyword matching
- Escalation logic for complex issues
- Customer satisfaction tracking
- Response time monitoring
- Knowledge base management

Customer channel: a minimal stdlib-only HTTP intake (POST /ticket) that runs
on localhost via start_intake_server(). That is the ONLY customer-facing
entry point this module provides — there is no public website widget, email
listener, or chat integration wired up. For anything beyond local testing,
the intake must be fronted by real infrastructure.

Uses Mythara SSIP:
- Sanctification: SLA rules locked (immutable)
- Integrity Hashing: All tickets cryptographically verified
- Blessings Reservoir: Customer satisfaction scores
- Shadow_Resolver: Auto-escalate unresolved tickets
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import requests
import re

try:
    from soul_cradle.bot_witness import (
        witness_action,
        intake_evidence,
        WitnessUnavailable,
    )
except ImportError:  # pragma: no cover — direct-script fallback
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from soul_cradle.bot_witness import (
        witness_action,
        intake_evidence,
        WitnessUnavailable,
    )

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment


class _SupportIntakeHandler(BaseHTTPRequestHandler):
    """Minimal local HTTP intake: POST /ticket (JSON) -> create_ticket().

    This is the module's only customer entry point. It binds to localhost by
    default and exists for local testing/use — it is NOT a public channel.
    """
    bot: "MytharaSupportBot" = None  # set by start_intake_server()

    def _send_json(self, status: int, payload: Dict[str, Any]):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/health"):
            self._send_json(200, {"status": "ok", "channel": "local-http-intake"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/ticket":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid JSON body"})
            return
        if not isinstance(data, dict):
            self._send_json(400, {"error": "JSON body must be an object"})
            return
        missing = [f for f in ("customer_email", "subject") if not data.get(f)]
        if missing:
            self._send_json(
                400, {"error": "missing required fields: " + ", ".join(missing)}
            )
            return
        try:
            result = self.bot.create_ticket(
                customer_email=data["customer_email"],
                customer_name=data.get("customer_name", ""),
                subject=data["subject"],
                description=data.get("description", ""),
                category=data.get("category", "general"),
                priority=data.get("priority", "normal"),
            )
        except Exception as e:  # never leak a traceback over HTTP
            self._send_json(500, {"error": f"ticket creation failed: {e}"})
            return
        self._send_json(201, result)

    def log_message(self, fmt, *args):  # keep the stdlib server quiet
        pass

class MytharaSupportBot:
    """Support Chat Bot - Customer support automation."""
    
    def __init__(self):
        self.bot_id = "support_bot"
        self.bot_token = None
        self.db_path = "mythara_support.db"
        
        # FAQ knowledge base
        self.faq_db = self._init_faq_database()
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_faq_database(self) -> Dict[str, str]:
        """Initialize FAQ responses."""
        return {
            "pricing": "Our pricing starts at $300/month for individual subscriptions. Enterprise plans start at $25,000/year. Visit mythara.com/pricing for details.",
            "trial": "Yes! We offer a 14-day free trial with full access to all features. No credit card required.",
            "api": "Our API documentation is available at docs.mythara.com/api. We support REST and GraphQL endpoints.",
            "security": "Mythara uses enterprise-grade encryption (AES-256) and SSIP integrity hashing. We are not SOC 2 certified — ask us for our current security documentation.",
            "support": "Premium support includes 24/7 email, priority Slack channel, and dedicated account manager for Enterprise clients.",
            "integration": "We integrate with GitHub, GitLab, Jira, Slack, Microsoft Teams, and 100+ tools via Zapier.",
            "deployment": "Available as cloud SaaS, on-premise deployment, or hybrid. Contact sales for deployment options.",
            "training": "Free onboarding training included. Advanced workshops available for $1,000 per session.",
            "sla": "Enterprise SLA guarantees 99.9% uptime with 4-hour response time for critical issues.",
            "compliance": "Mythara is designed with GDPR and HIPAA principles in mind. We hold no compliance certifications — ask us for our current documentation on request."
        }
    
    def _init_db(self):
        """Initialize support database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Support tickets
        c.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                customer_name TEXT,
                subject TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'open',
                assigned_to TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                resolved_at TEXT,
                resolution TEXT,
                first_response_time INT,
                resolution_time INT,
                integrity_hash TEXT
            )
        ''')
        
        # Chat messages
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                sender_type TEXT DEFAULT 'customer',
                message TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
            )
        ''')
        
        # Customer satisfaction
        c.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_ratings (
                rating_id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                rating INT,
                feedback TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
            )
        ''')
        
        # Knowledge base articles
        c.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                keywords TEXT,
                views INT DEFAULT 0,
                helpful_count INT DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Support audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS support_audit (
                audit_id TEXT PRIMARY KEY,
                entity TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[OK] Support Bot database initialized: {self.db_path}")
    
    def _register(self):
        """Register with orchestrator."""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/register_bot",
                json={
                    "bot_id": self.bot_id,
                    "capabilities": ["customer_support", "ticketing", "faq", "chat", "satisfaction_tracking"],
                    "master_token": VP_MASTER_TOKEN
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.bot_token = data.get("bot_token")
                print(f"[OK] Registered as Support Bot: {self.bot_id}")
            else:
                print(f"[WARN] Orchestrator registration failed: {response.status_code}")
        except Exception as e:
            print(f"[WARN] Could not connect to orchestrator: {e}")
    
    def start_intake_server(self, host: str = "127.0.0.1", port: int = 8088) -> ThreadingHTTPServer:
        """Start the minimal local customer-intake channel.

        stdlib-only http.server: POST /ticket with a JSON body
        {customer_email, customer_name, subject, description, category, priority}
        creates a ticket and returns it with HTTP 201; GET /health is a
        liveness check. Binds to localhost by default.

        This is a LOCAL intake endpoint for testing/local use — the module's
        only customer entry point, and not a public channel. Blocking: run
        serve_forever() on the returned server, or serve it in a thread.
        """
        _SupportIntakeHandler.bot = self
        server = ThreadingHTTPServer((host, port), _SupportIntakeHandler)
        print(f"[SUPPORT] Local intake channel on http://{host}:{server.server_port}/ticket")
        return server

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Read a ticket back by ID (None if not found)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM support_tickets WHERE ticket_id = ?", (ticket_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def _generate_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for audit trail."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _audit(self, entity: str, action: str, details: Dict[str, Any]):
        """Log action to audit trail."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        audit_id = hashlib.sha256(f"{entity}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        integrity_hash = self._generate_integrity_hash({"entity": entity, "action": action, "details": details})
        
        c.execute('''
            INSERT INTO support_audit (audit_id, entity, action, details, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (audit_id, entity, action, json.dumps(details), datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
    
    def create_ticket(self, customer_email: str, customer_name: str, subject: str,
                     description: str, category: str = "general", priority: str = "normal") -> Dict[str, Any]:
        """Create support ticket."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{customer_email}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        # Auto-escalate high priority tickets
        if priority == "critical":
            assigned_to = "senior_support@mythara.com"
        else:
            assigned_to = "support@mythara.com"
        
        record = {
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "subject": subject,
            "category": category,
            "priority": priority
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO support_tickets
            (ticket_id, customer_email, customer_name, subject, description, category,
             priority, assigned_to, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, customer_email, customer_name, subject, description, category,
              priority, assigned_to, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("ticket", "created", record)

        # --- Soul Cradle witnessing: record-only, intake is never blocked --
        try:
            evidence, bases = intake_evidence(
                ticket_id=ticket_id,
                fields_present=["customer_email", "customer_name", "subject",
                                "description", "category", "priority"],
                declared_intent="store the customer's request verbatim",
            )
            witness_action(
                bot_id="support_bot",
                action=f"intake ticket {ticket_id}",
                evidence=evidence,
                evidence_bases=bases,
                enforce=False,
            )
        except WitnessUnavailable as exc:
            print(f"[SUPPORT] WITNESS UNAVAILABLE — {exc}; proceeding.")
        # --- end witnessing --------------------------------------------------

        print(f"[SUPPORT] Created ticket: {ticket_id}")
        print(f"          Customer: {customer_name} ({customer_email})")
        print(f"          Priority: {priority}")
        
        return {"success": True, "ticket_id": ticket_id, "assigned_to": assigned_to}
    
    def search_faq(self, query: str) -> Dict[str, Any]:
        """Search FAQ for answer."""
        query_lower = query.lower()
        
        # Keyword matching
        matched_topics = []
        for topic, answer in self.faq_db.items():
            if topic in query_lower or any(word in query_lower for word in topic.split()):
                matched_topics.append({"topic": topic, "answer": answer})
        
        if matched_topics:
            print(f"[SUPPORT] Found {len(matched_topics)} FAQ match(es) for: '{query}'")
            return {"success": True, "matches": matched_topics}
        else:
            print(f"[SUPPORT] No FAQ match for: '{query}' - Escalating to human support")
            return {"success": False, "message": "No FAQ match found. Creating support ticket."}
    
    def add_message(self, ticket_id: str, sender: str, message: str, sender_type: str = "customer") -> Dict[str, Any]:
        """Add message to ticket thread."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        message_id = hashlib.sha256(f"{ticket_id}{sender}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "message_id": message_id,
            "ticket_id": ticket_id,
            "sender": sender,
            "message": message
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO chat_messages
            (message_id, ticket_id, sender, sender_type, message, sent_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, ticket_id, sender, sender_type, message,
              datetime.now().isoformat(), integrity_hash))
        
        # Update ticket timestamp
        c.execute('UPDATE support_tickets SET updated_at = ? WHERE ticket_id = ?',
                 (datetime.now().isoformat(), ticket_id))
        
        # Calculate first response time if this is first agent response
        if sender_type == "agent":
            c.execute('SELECT created_at, first_response_time FROM support_tickets WHERE ticket_id = ?', (ticket_id,))
            row = c.fetchone()
            if row and row[1] is None:  # No first response time yet
                created = datetime.fromisoformat(row[0])
                response_time = int((datetime.now() - created).total_seconds())
                c.execute('UPDATE support_tickets SET first_response_time = ? WHERE ticket_id = ?',
                         (response_time, ticket_id))
                print(f"[SUPPORT] First response time: {response_time}s ({response_time//60}min)")
        
        conn.commit()
        conn.close()
        
        self._audit("message", "added", record)
        
        return {"success": True, "message_id": message_id}
    
    def resolve_ticket(self, ticket_id: str, resolution: str) -> Dict[str, Any]:
        """Resolve support ticket."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get ticket creation time
        c.execute('SELECT created_at FROM support_tickets WHERE ticket_id = ?', (ticket_id,))
        row = c.fetchone()
        if row:
            created = datetime.fromisoformat(row[0])
            resolution_time = int((datetime.now() - created).total_seconds())
        else:
            resolution_time = 0
        
        c.execute('''
            UPDATE support_tickets
            SET status = 'resolved', resolution = ?, resolved_at = ?, resolution_time = ?
            WHERE ticket_id = ?
        ''', (resolution, datetime.now().isoformat(), resolution_time, ticket_id))
        
        conn.commit()
        conn.close()
        
        self._audit("ticket", "resolved", {
            "ticket_id": ticket_id,
            "resolution_time": resolution_time
        })
        
        print(f"[SUPPORT] Resolved ticket: {ticket_id}")
        print(f"          Resolution time: {resolution_time//3600}h {(resolution_time%3600)//60}min")
        
        return {"success": True, "ticket_id": ticket_id, "resolution_time": resolution_time}
    
    def record_satisfaction(self, ticket_id: str, customer_email: str, 
                           rating: int, feedback: str = "") -> Dict[str, Any]:
        """Record customer satisfaction rating (1-5)."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        rating_id = hashlib.sha256(f"{ticket_id}{customer_email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "rating_id": rating_id,
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "rating": rating
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO satisfaction_ratings
            (rating_id, ticket_id, customer_email, rating, feedback, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rating_id, ticket_id, customer_email, rating, feedback,
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("satisfaction", "recorded", record)
        
        emoji = "😊" if rating >= 4 else "😐" if rating == 3 else "😞"
        print(f"[SUPPORT] Customer satisfaction: {rating}/5 {emoji}")
        print(f"          Ticket: {ticket_id}")
        
        return {"success": True, "rating_id": rating_id, "rating": rating}
    
    def escalate_ticket(self, ticket_id: str, reason: str) -> Dict[str, Any]:
        """Escalate ticket to senior support."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE support_tickets
            SET priority = 'high', assigned_to = 'senior_support@mythara.com'
            WHERE ticket_id = ?
        ''', (ticket_id,))
        
        conn.commit()
        conn.close()
        
        self._audit("ticket", "escalated", {"ticket_id": ticket_id, "reason": reason})
        
        print(f"[SUPPORT] ⚠️ ESCALATED ticket: {ticket_id}")
        print(f"          Reason: {reason}")
        
        return {"success": True, "ticket_id": ticket_id, "escalated": True}
    
    def generate_support_report(self) -> str:
        """Generate support metrics report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ticket stats
        c.execute('SELECT COUNT(*) FROM support_tickets WHERE status = "open"')
        open_tickets = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM support_tickets WHERE status = "resolved"')
        resolved_tickets = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM support_tickets WHERE priority = "critical" AND status = "open"')
        critical_tickets = c.fetchone()[0]
        
        # Response times (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        c.execute('SELECT AVG(first_response_time) FROM support_tickets WHERE created_at > ? AND first_response_time IS NOT NULL',
                 (thirty_days_ago,))
        avg_response = c.fetchone()[0] or 0
        
        c.execute('SELECT AVG(resolution_time) FROM support_tickets WHERE created_at > ? AND resolution_time IS NOT NULL',
                 (thirty_days_ago,))
        avg_resolution = c.fetchone()[0] or 0
        
        # Satisfaction
        c.execute('SELECT AVG(rating), COUNT(*) FROM satisfaction_ratings WHERE created_at > ?',
                 (thirty_days_ago,))
        row = c.fetchone()
        avg_satisfaction = row[0] or 0.0
        total_ratings = row[1]
        
        # Category breakdown
        c.execute('SELECT category, COUNT(*) FROM support_tickets GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5')
        top_categories = c.fetchall()
        
        conn.close()
        
        report = f"""
================================================================
      MYTHARA SUPPORT BOT - CUSTOMER SUPPORT REPORT
                     {datetime.now().strftime("%Y-%m-%d %H:%M")}
================================================================

TICKET STATUS:
   Open Tickets: {open_tickets}
   Resolved Tickets: {resolved_tickets}
   Critical Open: {critical_tickets}
   {"[!] CRITICAL TICKETS NEED ATTENTION" if critical_tickets > 0 else "[OK] No critical tickets"}

RESPONSE METRICS (Last 30 Days):
   Avg First Response Time: {avg_response//60}min {avg_response%60}sec
   Avg Resolution Time: {avg_resolution//3600}h {(avg_resolution%3600)//60}min
   SLA Target: <4 hours ({"[PASS]" if avg_response < 14400 else "[FAIL]"})

CUSTOMER SATISFACTION:
   Avg Rating: {avg_satisfaction:.2f}/5.0
   Total Ratings: {total_ratings}
   {"EXCELLENT" if avg_satisfaction >= 4.5 else "GOOD" if avg_satisfaction >= 3.5 else "NEEDS IMPROVEMENT"}

TOP CATEGORIES:
"""
        for cat, count in top_categories:
            report += f"   {cat}: {count} tickets\n"
        
        report += "\n================================================================\n"
        
        return report

if __name__ == "__main__":
    print("Mythara Support Chat Bot - Customer Support Automation")
    print("=" * 60)
    
    bot = MytharaSupportBot()
    
    # Demo: Search FAQ
    print("\n[1] FAQ Search Demo:")
    bot.search_faq("What is your pricing?")
    bot.search_faq("Do you offer a trial?")
    bot.search_faq("How secure is Mythara?")
    
    # Demo: Create ticket
    print("\n[2] Ticket Creation Demo:")
    ticket = bot.create_ticket(
        customer_email="customer@acme.com",
        customer_name="John Doe",
        subject="API Integration Help",
        description="Need help integrating Mythara API with our CRM",
        category="technical",
        priority="normal"
    )
    
    # Add messages
    print("\n[3] Message Thread Demo:")
    bot.add_message(ticket['ticket_id'], "customer@acme.com", 
                   "We're getting 401 errors when calling /api/authenticate", 
                   sender_type="customer")
    
    bot.add_message(ticket['ticket_id'], "support@mythara.com",
                   "Please check that you're including the API key in the Authorization header as 'Bearer YOUR_KEY'",
                   sender_type="agent")
    
    bot.add_message(ticket['ticket_id'], "customer@acme.com",
                   "That worked! Thank you!",
                   sender_type="customer")
    
    # Resolve ticket
    print("\n[4] Resolution Demo:")
    bot.resolve_ticket(ticket['ticket_id'], "API authentication issue resolved - header format corrected")
    
    # Record satisfaction
    print("\n[5] Satisfaction Rating Demo:")
    bot.record_satisfaction(ticket['ticket_id'], "customer@acme.com", 5, "Fast and helpful!")
    
    # Generate report
    print("\n[6] Support Report:")
    print(bot.generate_support_report())
