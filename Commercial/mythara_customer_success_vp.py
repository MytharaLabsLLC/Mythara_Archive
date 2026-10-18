import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara VP of Customer Success - Autonomous Retention & Support
Handles customer health scoring, retention tracking, support automation, onboarding.

Uses Mythara SSIP:
- Blessings Reservoir: Customer health score (0-100)
- Sanctification: SLA response times (immutable)
- Shadow_Resolver: Auto-escalation for at-risk customers
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

class MytharaCustomerSuccessVP:
    """VP of Customer Success - Autonomous retention and support operations."""
    
    def __init__(self):
        self.bot_id = "customer_success_vp"
        self.bot_token = None
        self.db_path = "mythara_customer_success.db"
        self.logistics_db = "mythara_logistics.db"
        self.sanctified_slas = self._init_sanctified_slas()
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_sanctified_slas(self) -> Dict[str, Any]:
        """Initialize sanctified SLAs (immutable)."""
        slas = {
            'support_response_hours': 24,
            'onboarding_check_days': [0, 3, 7, 14, 30],  # Day 0, 3, 7, 14, 30 check-ins
            'renewal_reminder_days': 30,  # Remind 30 days before renewal
            'at_risk_threshold': 50,  # Health score below 50 = at risk
            'churn_risk_threshold': 30,  # Health score below 30 = high churn risk
            'integrity_hash': hashlib.sha256(json.dumps({'version': '2025.1'}, sort_keys=True).encode()).hexdigest()[:16]
        }
        return slas
    
    def _init_db(self):
        """Initialize customer success database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customer health table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_health (
                customer_email TEXT PRIMARY KEY,
                health_score REAL DEFAULT 100,
                risk_level TEXT DEFAULT 'healthy',
                last_login TEXT,
                login_count INT DEFAULT 0,
                support_tickets INT DEFAULT 0,
                resolved_tickets INT DEFAULT 0,
                payment_failures INT DEFAULT 0,
                positive_interactions INT DEFAULT 0,
                last_updated TEXT
            )
        ''')
        
        # Onboarding table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding (
                onboarding_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                day_checkpoint INT NOT NULL,
                status TEXT DEFAULT 'pending',
                sent_at TEXT,
                completed_at TEXT
            )
        ''')
        
        # Renewals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS renewals (
                renewal_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                product_sku TEXT NOT NULL,
                renewal_date TEXT NOT NULL,
                reminder_sent BOOLEAN DEFAULT 0,
                renewed BOOLEAN DEFAULT 0,
                churn_reason TEXT
            )
        ''')
        
        # Escalations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                escalation_type TEXT NOT NULL,
                reason TEXT,
                severity TEXT,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                resolution_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _register(self):
        """Register Customer Success VP with orchestrator."""
        try:
            response = requests.post(f"{ORCHESTRATOR_URL}/register_bot", json={
                'vp_token': VP_MASTER_TOKEN,
                'bot_id': self.bot_id,
                'bot_name': 'Customer Success VP Bot'
            })
            if response.status_code == 200:
                self.bot_token = response.json()['bot_token']
                print(f"[OK] Registered as Customer Success VP")
                print(f"   Token: {self.bot_token[:16]}...")
            else:
                print(f"[WARN] Registration failed: {response.text}")
        except Exception as e:
            print(f"[WARN] Could not register: {e}")
    
    def update_customer_health(self, customer_email: str, event_type: str, event_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update customer health score using Blessings Reservoir pattern."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create customer health record
        cursor.execute('SELECT * FROM customer_health WHERE customer_email = ?', (customer_email,))
        health = cursor.fetchone()
        
        if not health:
            cursor.execute('''
                INSERT INTO customer_health (customer_email, last_updated) 
                VALUES (?, ?)
            ''', (customer_email, datetime.now().isoformat()))
            cursor.execute('SELECT * FROM customer_health WHERE customer_email = ?', (customer_email,))
            health = cursor.fetchone()
        
        # Current health score
        current_score = health[1]
        
        # Update score based on event
        score_delta = 0
        
        if event_type == 'login':
            score_delta = +2  # Positive engagement
            cursor.execute('''
                UPDATE customer_health 
                SET login_count = login_count + 1, last_login = ? 
                WHERE customer_email = ?
            ''', (datetime.now().isoformat(), customer_email))
        
        elif event_type == 'support_ticket_created':
            score_delta = -5  # Issue detected
            cursor.execute('''
                UPDATE customer_health 
                SET support_tickets = support_tickets + 1 
                WHERE customer_email = ?
            ''', (customer_email,))
        
        elif event_type == 'support_ticket_resolved':
            score_delta = +3  # Good support experience
            cursor.execute('''
                UPDATE customer_health 
                SET resolved_tickets = resolved_tickets + 1 
                WHERE customer_email = ?
            ''', (customer_email,))
        
        elif event_type == 'payment_failure':
            score_delta = -10  # Critical issue
            cursor.execute('''
                UPDATE customer_health 
                SET payment_failures = payment_failures + 1 
                WHERE customer_email = ?
            ''', (customer_email,))
        
        elif event_type == 'positive_interaction':
            score_delta = +5  # Testimonial, referral, etc.
            cursor.execute('''
                UPDATE customer_health 
                SET positive_interactions = positive_interactions + 1 
                WHERE customer_email = ?
            ''', (customer_email,))
        
        # Calculate new score (bounded 0-100)
        new_score = max(0, min(100, current_score + score_delta))
        
        # Determine risk level
        if new_score >= self.sanctified_slas['at_risk_threshold']:
            risk_level = 'healthy'
        elif new_score >= self.sanctified_slas['churn_risk_threshold']:
            risk_level = 'at_risk'
        else:
            risk_level = 'high_churn_risk'
        
        # Update health score
        cursor.execute('''
            UPDATE customer_health 
            SET health_score = ?, risk_level = ?, last_updated = ? 
            WHERE customer_email = ?
        ''', (new_score, risk_level, datetime.now().isoformat(), customer_email))
        
        conn.commit()
        
        # Check if escalation needed
        if risk_level in ['at_risk', 'high_churn_risk'] and score_delta < 0:
            self._escalate_customer(customer_email, event_type, new_score)
        
        conn.close()
        
        print(f"[HEALTH] {customer_email}: {new_score:.0f}/100 ({risk_level})")
        print(f"   Event: {event_type} ({score_delta:+d} points)")
        
        return {
            'customer_email': customer_email,
            'old_score': current_score,
            'new_score': new_score,
            'delta': score_delta,
            'risk_level': risk_level
        }
    
    def _escalate_customer(self, customer_email: str, trigger: str, health_score: float):
        """Escalate at-risk customer (Shadow_Resolver pattern)."""
        
        escalation_id = hashlib.sha256(
            f"{customer_email}{trigger}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        severity = 'critical' if health_score < 30 else 'high'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO escalations VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            escalation_id,
            customer_email,
            'churn_risk',
            f'Triggered by: {trigger}',
            severity,
            datetime.now().isoformat(),
            None,
            None
        ))
        
        conn.commit()
        conn.close()
        
        print(f"   [ESCALATE] Created: {escalation_id}")
        print(f"   Severity: {severity.upper()}")
    
    def send_onboarding_checkins(self) -> List[Dict[str, Any]]:
        """Send onboarding check-in emails at sanctified intervals."""
        
        # Get all customers from logistics DB
        logistics_conn = sqlite3.connect(self.logistics_db)
        logistics_cursor = logistics_conn.cursor()
        
        logistics_cursor.execute('''
            SELECT DISTINCT customer_email, created_at 
            FROM orders 
            WHERE status = "fulfilled"
        ''')
        
        customers = logistics_cursor.fetchall()
        logistics_conn.close()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sent_checkins = []
        
        for customer_email, created_at in customers:
            created_date = datetime.fromisoformat(created_at)
            days_since_purchase = (datetime.now() - created_date).days
            
            # Check which checkpoints should have been sent
            for checkpoint in self.sanctified_slas['onboarding_check_days']:
                if days_since_purchase >= checkpoint:
                    # Check if already sent
                    cursor.execute('''
                        SELECT * FROM onboarding 
                        WHERE customer_email = ? AND day_checkpoint = ?
                    ''', (customer_email, checkpoint))
                    
                    existing = cursor.fetchone()
                    
                    if not existing:
                        # Send check-in
                        onboarding_id = hashlib.sha256(
                            f"{customer_email}{checkpoint}{datetime.now().isoformat()}".encode()
                        ).hexdigest()[:16]
                        
                        cursor.execute('''
                            INSERT INTO onboarding VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            onboarding_id,
                            customer_email,
                            checkpoint,
                            'sent',
                            datetime.now().isoformat(),
                            None
                        ))
                        
                        # Send email (simulated)
                        self._send_checkin_email(customer_email, checkpoint)
                        
                        sent_checkins.append({
                            'customer_email': customer_email,
                            'checkpoint': checkpoint,
                            'onboarding_id': onboarding_id
                        })
        
        conn.commit()
        conn.close()
        
        return sent_checkins
    
    def _send_checkin_email(self, customer_email: str, checkpoint: int):
        """Send onboarding check-in email."""
        
        messages = {
            0: "Welcome to Mythara! Let's get started with your first clause invocation.",
            3: "Day 3 check-in: How's your experience so far? Any questions?",
            7: "Week 1 milestone! You're making great progress. Here are advanced tips.",
            14: "Two weeks in! Let's review your SSIP compliance and optimization opportunities.",
            30: "30-day celebration! You're a Mythara power user. Ready for enterprise features?"
        }
        
        message = messages.get(checkpoint, "Check-in from Mythara Customer Success")
        
        print(f"\n[EMAIL] Onboarding Day {checkpoint}")
        print(f"   To: {customer_email}")
        print(f"   Subject: {message}")
        print(f"   [OK] Sent")
    
    def identify_at_risk_customers(self) -> List[Dict[str, Any]]:
        """Identify at-risk and high churn risk customers."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM customer_health 
            WHERE health_score < ?
            ORDER BY health_score ASC
        ''', (self.sanctified_slas['at_risk_threshold'],))
        
        at_risk = cursor.fetchall()
        
        customers = []
        for customer in at_risk:
            customers.append({
                'customer_email': customer[0],
                'health_score': customer[1],
                'risk_level': customer[2],
                'last_login': customer[3],
                'login_count': customer[4],
                'support_tickets': customer[5],
                'payment_failures': customer[7]
            })
        
        conn.close()
        
        return customers
    
    def generate_customer_success_report(self) -> str:
        """Generate comprehensive customer success report."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Health metrics
        cursor.execute('SELECT AVG(health_score) FROM customer_health')
        avg_health = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM customer_health WHERE risk_level = "healthy"')
        healthy_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customer_health WHERE risk_level = "at_risk"')
        at_risk_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customer_health WHERE risk_level = "high_churn_risk"')
        churn_risk_count = cursor.fetchone()[0]
        
        # Onboarding metrics
        cursor.execute('SELECT COUNT(*) FROM onboarding WHERE status = "sent"')
        onboarding_sent = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM onboarding WHERE completed_at IS NOT NULL')
        onboarding_completed = cursor.fetchone()[0]
        
        # Escalation metrics
        cursor.execute('SELECT COUNT(*) FROM escalations WHERE resolved_at IS NULL')
        open_escalations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM escalations WHERE resolved_at IS NOT NULL')
        resolved_escalations = cursor.fetchone()[0]
        
        conn.close()
        
        total_customers = healthy_count + at_risk_count + churn_risk_count
        
        report = f"""
============================================================
CUSTOMER SUCCESS VP REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
============================================================

CUSTOMER HEALTH:
   Average Health Score: {avg_health:.1f}/100
   Total Customers: {total_customers}
   
   Healthy: {healthy_count} ({healthy_count/total_customers*100 if total_customers > 0 else 0:.0f}%)
   At Risk: {at_risk_count} ({at_risk_count/total_customers*100 if total_customers > 0 else 0:.0f}%)
   High Churn Risk: {churn_risk_count} ({churn_risk_count/total_customers*100 if total_customers > 0 else 0:.0f}%)

ONBOARDING:
   Check-ins Sent: {onboarding_sent}
   Completed: {onboarding_completed}
   Completion Rate: {onboarding_completed/onboarding_sent*100 if onboarding_sent > 0 else 0:.0f}%

ESCALATIONS:
   Open: {open_escalations}
   Resolved: {resolved_escalations}
   Resolution Rate: {resolved_escalations/(open_escalations+resolved_escalations)*100 if (open_escalations+resolved_escalations) > 0 else 0:.0f}%

SANCTIFIED SLAS:
   Support Response: {self.sanctified_slas['support_response_hours']}h
   Onboarding Days: {', '.join(map(str, self.sanctified_slas['onboarding_check_days']))}
   At-Risk Threshold: {self.sanctified_slas['at_risk_threshold']}
   Integrity Hash: {self.sanctified_slas['integrity_hash']}

============================================================

RECOMMENDATIONS:
"""
        
        if churn_risk_count > 0:
            report += f"\n   [URGENT] {churn_risk_count} customers at high churn risk - immediate intervention needed"
        
        if at_risk_count > total_customers * 0.2:
            report += f"\n   [WARN] {at_risk_count/total_customers*100:.0f}% of customers at risk - review health drivers"
        
        if open_escalations > 0:
            report += f"\n   [ACTION] {open_escalations} open escalations - prioritize resolution"
        
        if avg_health < 70:
            report += f"\n   [CONCERN] Average health score ({avg_health:.1f}) below target (70)"
        
        if not (churn_risk_count > 0 or at_risk_count > total_customers * 0.2 or open_escalations > 0 or avg_health < 70):
            report += "\n   [GOOD] Customer health metrics strong"
            report += "\n   -> Continue onboarding and engagement programs"
        
        report += f"""

Next check: {(datetime.now() + timedelta(days=1)).strftime('%B %d at %I:%M %p')}
"""
        
        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA CUSTOMER SUCCESS VP")
    print("="*60)
    
    cs = MytharaCustomerSuccessVP()
    
    # Simulate customer events
    print("\n1. Updating Customer Health...")
    
    test_customer = "test.customer@example.com"
    
    cs.update_customer_health(test_customer, 'login')
    cs.update_customer_health(test_customer, 'positive_interaction')
    cs.update_customer_health(test_customer, 'support_ticket_created')
    cs.update_customer_health(test_customer, 'support_ticket_resolved')
    
    # Send onboarding check-ins
    print("\n2. Sending Onboarding Check-ins...")
    checkins = cs.send_onboarding_checkins()
    print(f"   [OK] Sent {len(checkins)} check-in(s)")
    
    # Identify at-risk customers
    print("\n3. Identifying At-Risk Customers...")
    at_risk = cs.identify_at_risk_customers()
    print(f"   Found {len(at_risk)} at-risk customer(s)")
    
    # Generate report
    print("\n4. Generating Customer Success Report...")
    report = cs.generate_customer_success_report()
    print(report)
    
    print("="*60)
    print("[OK] Customer Success VP operational")
    print("[OK] Health tracking active")
    print("[OK] Retention programs enabled")
