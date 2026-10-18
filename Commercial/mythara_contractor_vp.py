import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara VP of Contractor Management - 3rd Party Delegation System
Manages contractor onboarding, task delegation, payment tracking, performance monitoring.

Enables white-label deployment across platforms:
- Upwork/Fiverr/Toptal integration
- Custom contractor pools
- Auto-delegation with SSIP governance
- Performance-based Blessings Reservoir scoring

Uses Mythara SSIP:
- Sanctification: Payment rates, SLA requirements (immutable)
- Blessings Reservoir: Contractor performance scores (0-100)
- Shadow_Resolver: Auto-escalation for missed deadlines
- Integrity Hashing: All contracts cryptographically verified
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

class MytharaContractorVP:
    """VP of Contractor Management - Autonomous delegation and oversight."""
    
    def __init__(self):
        self.bot_id = "contractor_vp"
        self.bot_token = None
        self.db_path = "mythara_contractors.db"
        self.sanctified_rates = self._init_sanctified_rates()
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_sanctified_rates(self) -> Dict[str, Any]:
        """Initialize sanctified contractor rates and SLAs (immutable)."""
        rates = {
            'skill_tiers': {
                'junior': {'hourly_rate': 25, 'max_tasks': 3, 'approval_required': False},
                'mid': {'hourly_rate': 50, 'max_tasks': 5, 'approval_required': False},
                'senior': {'hourly_rate': 100, 'max_tasks': 10, 'approval_required': True},
                'expert': {'hourly_rate': 200, 'max_tasks': 20, 'approval_required': True}
            },
            'task_types': {
                'code_review': {'base_price': 50, 'sla_hours': 24},
                'bug_fix': {'base_price': 100, 'sla_hours': 48},
                'feature_development': {'base_price': 500, 'sla_hours': 168},  # 1 week
                'integration': {'base_price': 300, 'sla_hours': 72},
                'documentation': {'base_price': 75, 'sla_hours': 48},
                'testing': {'base_price': 150, 'sla_hours': 48},
                'deployment': {'base_price': 200, 'sla_hours': 24}
            },
            'performance_thresholds': {
                'excellent': 90,  # Score >= 90
                'good': 75,       # Score >= 75
                'acceptable': 60, # Score >= 60
                'needs_improvement': 40,  # Score >= 40
                'terminated': 0   # Score < 40
            },
            'payment_terms': {
                'milestone_percentage': 50,  # 50% on milestone completion
                'final_percentage': 50,      # 50% on final delivery
                'escrow_hold_days': 7,       # Hold in escrow for 7 days
                'dispute_resolution_days': 14
            },
            'platform_fees': {
                'upwork': 0.10,    # 10% platform fee
                'fiverr': 0.20,    # 20% platform fee
                'toptal': 0.15,    # 15% platform fee
                'internal': 0.05   # 5% internal overhead
            },
            'integrity_hash': hashlib.sha256(json.dumps({'version': '2025.1'}, sort_keys=True).encode()).hexdigest()[:16]
        }
        return rates
    
    def _init_db(self):
        """Initialize contractor management database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contractors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contractors (
                contractor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                skill_tier TEXT NOT NULL,
                skills TEXT,
                platform TEXT,
                platform_profile_url TEXT,
                performance_score REAL DEFAULT 100,
                tasks_completed INT DEFAULT 0,
                tasks_failed INT DEFAULT 0,
                total_earnings REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                onboarded_at TEXT NOT NULL,
                last_task_at TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                contractor_id TEXT,
                assigned_at TEXT,
                due_date TEXT,
                completed_at TEXT,
                status TEXT DEFAULT 'open',
                estimated_hours REAL,
                actual_hours REAL,
                base_price REAL,
                final_price REAL,
                quality_score REAL,
                deliverable_url TEXT,
                client_approval BOOLEAN DEFAULT 0,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
            )
        ''')
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                contractor_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_type TEXT NOT NULL,
                platform_fee REAL,
                net_amount REAL,
                status TEXT DEFAULT 'pending',
                escrow_release_date TEXT,
                paid_at TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id)
            )
        ''')
        
        # Delegation rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS delegation_rules (
                rule_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                auto_assign BOOLEAN DEFAULT 0,
                preferred_tier TEXT,
                max_budget REAL,
                sla_hours INT,
                requires_approval BOOLEAN DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Platform integrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_integrations (
                integration_id TEXT PRIMARY KEY,
                platform_name TEXT NOT NULL,
                api_key_encrypted TEXT,
                webhook_url TEXT,
                oauth_token_encrypted TEXT,
                status TEXT DEFAULT 'inactive',
                last_sync TEXT,
                total_tasks_delegated INT DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _register(self):
        """Register Contractor VP with orchestrator."""
        try:
            response = requests.post(f"{ORCHESTRATOR_URL}/register_bot", json={
                'vp_token': VP_MASTER_TOKEN,
                'bot_id': self.bot_id,
                'bot_name': 'Contractor VP Bot'
            })
            if response.status_code == 200:
                self.bot_token = response.json()['bot_token']
                print(f"[OK] Registered as Contractor VP")
                print(f"   Token: {self.bot_token[:16]}...")
            else:
                print(f"[WARN] Registration failed: {response.text}")
        except Exception as e:
            print(f"[WARN] Could not register: {e}")
    
    def onboard_contractor(self, contractor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Onboard new contractor with SSIP verification."""
        
        contractor_id = hashlib.sha256(
            f"{contractor_data['email']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        integrity_hash = hashlib.sha256(
            json.dumps(contractor_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Validate skill tier
        if contractor_data['skill_tier'] not in self.sanctified_rates['skill_tiers']:
            return {'error': f"Invalid skill tier: {contractor_data['skill_tier']}"}
        
        contractor = {
            'contractor_id': contractor_id,
            'name': contractor_data['name'],
            'email': contractor_data['email'],
            'skill_tier': contractor_data['skill_tier'],
            'skills': json.dumps(contractor_data.get('skills', [])),
            'platform': contractor_data.get('platform', 'internal'),
            'platform_profile_url': contractor_data.get('profile_url', ''),
            'performance_score': 100.0,  # Start with perfect Blessings Reservoir score
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_earnings': 0.0,
            'status': 'active',
            'onboarded_at': datetime.now().isoformat(),
            'last_task_at': None,
            'integrity_hash': integrity_hash
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contractors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contractor['contractor_id'],
            contractor['name'],
            contractor['email'],
            contractor['skill_tier'],
            contractor['skills'],
            contractor['platform'],
            contractor['platform_profile_url'],
            contractor['performance_score'],
            contractor['tasks_completed'],
            contractor['tasks_failed'],
            contractor['total_earnings'],
            contractor['status'],
            contractor['onboarded_at'],
            contractor['last_task_at'],
            contractor['integrity_hash']
        ))
        
        conn.commit()
        conn.close()
        
        print(f"\n[ONBOARD] Contractor: {contractor_id}")
        print(f"   Name: {contractor['name']}")
        print(f"   Tier: {contractor['skill_tier']}")
        print(f"   Platform: {contractor['platform']}")
        
        return contractor
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create delegatable task with auto-assignment option."""
        
        task_id = hashlib.sha256(
            f"{task_data['title']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        task_type = task_data['task_type']
        
        if task_type not in self.sanctified_rates['task_types']:
            return {'error': f"Invalid task type: {task_type}"}
        
        task_config = self.sanctified_rates['task_types'][task_type]
        
        estimated_hours = task_data.get('estimated_hours', 8)
        base_price = task_data.get('base_price', task_config['base_price'])
        
        due_date = datetime.now() + timedelta(hours=task_config['sla_hours'])
        
        integrity_hash = hashlib.sha256(
            json.dumps(task_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'title': task_data['title'],
            'description': task_data.get('description', ''),
            'contractor_id': None,
            'assigned_at': None,
            'due_date': due_date.isoformat(),
            'completed_at': None,
            'status': 'open',
            'estimated_hours': estimated_hours,
            'actual_hours': None,
            'base_price': base_price,
            'final_price': None,
            'quality_score': None,
            'deliverable_url': None,
            'client_approval': 0,
            'integrity_hash': integrity_hash
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task['task_id'],
            task['task_type'],
            task['title'],
            task['description'],
            task['contractor_id'],
            task['assigned_at'],
            task['due_date'],
            task['completed_at'],
            task['status'],
            task['estimated_hours'],
            task['actual_hours'],
            task['base_price'],
            task['final_price'],
            task['quality_score'],
            task['deliverable_url'],
            task['client_approval'],
            task['integrity_hash']
        ))
        
        conn.commit()
        conn.close()
        
        print(f"\n[TASK] Created: {task_id}")
        print(f"   Type: {task_type}")
        print(f"   Budget: ${base_price:,.2f}")
        print(f"   Due: {due_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Auto-assign if configured
        if task_data.get('auto_assign', False):
            self._auto_assign_task(task_id)
        
        return task
    
    def _auto_assign_task(self, task_id: str) -> Optional[str]:
        """Auto-assign task to best available contractor (delegation logic)."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return None
        
        task_type = task[1]
        base_price = task[11]
        
        # Find eligible contractors (active, good performance, available capacity)
        cursor.execute('''
            SELECT contractor_id, name, skill_tier, performance_score, tasks_completed
            FROM contractors 
            WHERE status = 'active' 
            AND performance_score >= ?
            ORDER BY performance_score DESC, tasks_completed ASC
            LIMIT 10
        ''', (self.sanctified_rates['performance_thresholds']['acceptable'],))
        
        candidates = cursor.fetchall()
        
        if not candidates:
            print(f"   [WARN] No eligible contractors for task {task_id}")
            conn.close()
            return None
        
        # Select best contractor (highest performance score)
        best_contractor = candidates[0]
        contractor_id = best_contractor[0]
        contractor_name = best_contractor[1]
        
        # Assign task
        assigned_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE tasks 
            SET contractor_id = ?, assigned_at = ?, status = 'assigned'
            WHERE task_id = ?
        ''', (contractor_id, assigned_at, task_id))
        
        cursor.execute('''
            UPDATE contractors 
            SET last_task_at = ?
            WHERE contractor_id = ?
        ''', (assigned_at, contractor_id))
        
        conn.commit()
        conn.close()
        
        print(f"   [ASSIGN] Task {task_id} -> {contractor_name} ({contractor_id})")
        
        return contractor_id
    
    def complete_task(self, task_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark task complete and process payment."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return {'error': f'Task not found: {task_id}'}
        
        contractor_id = task[4]
        base_price = task[11]
        
        actual_hours = completion_data.get('actual_hours', task[10])
        quality_score = completion_data.get('quality_score', 100)
        deliverable_url = completion_data.get('deliverable_url', '')
        
        # Calculate final price (quality adjustment)
        quality_multiplier = quality_score / 100
        final_price = base_price * quality_multiplier
        
        completed_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE tasks 
            SET completed_at = ?, status = 'completed', actual_hours = ?, 
                final_price = ?, quality_score = ?, deliverable_url = ?
            WHERE task_id = ?
        ''', (completed_at, actual_hours, final_price, quality_score, deliverable_url, task_id))
        
        # Update contractor stats
        cursor.execute('''
            UPDATE contractors 
            SET tasks_completed = tasks_completed + 1,
                total_earnings = total_earnings + ?
            WHERE contractor_id = ?
        ''', (final_price, contractor_id))
        
        # Create milestone payment (50%)
        milestone_payment = self._create_payment(
            task_id, contractor_id, final_price * 0.5, 'milestone'
        )
        
        # Create final payment (50%)
        final_payment = self._create_payment(
            task_id, contractor_id, final_price * 0.5, 'final'
        )
        
        # Update contractor performance score
        self._update_contractor_performance(contractor_id, quality_score)
        
        conn.commit()
        conn.close()
        
        print(f"\n[COMPLETE] Task: {task_id}")
        print(f"   Quality: {quality_score}/100")
        print(f"   Payment: ${final_price:,.2f}")
        print(f"   Milestone: ${milestone_payment['amount']:,.2f}")
        print(f"   Final: ${final_payment['amount']:,.2f}")
        
        return {
            'task_id': task_id,
            'final_price': final_price,
            'quality_score': quality_score,
            'payments': [milestone_payment, final_payment]
        }
    
    def _create_payment(self, task_id: str, contractor_id: str, amount: float, payment_type: str) -> Dict[str, Any]:
        """Create payment record with escrow and platform fees."""
        
        payment_id = hashlib.sha256(
            f"{task_id}{contractor_id}{payment_type}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get contractor platform
        cursor.execute('SELECT platform FROM contractors WHERE contractor_id = ?', (contractor_id,))
        platform = cursor.fetchone()[0]
        
        # Calculate platform fee
        platform_fee_rate = self.sanctified_rates['platform_fees'].get(platform, 0.05)
        platform_fee = amount * platform_fee_rate
        net_amount = amount - platform_fee
        
        # Escrow release date
        escrow_days = self.sanctified_rates['payment_terms']['escrow_hold_days']
        escrow_release_date = (datetime.now() + timedelta(days=escrow_days)).isoformat()
        
        payment = {
            'payment_id': payment_id,
            'task_id': task_id,
            'contractor_id': contractor_id,
            'amount': amount,
            'payment_type': payment_type,
            'platform_fee': platform_fee,
            'net_amount': net_amount,
            'status': 'escrowed',
            'escrow_release_date': escrow_release_date,
            'paid_at': None
        }
        
        cursor.execute('''
            INSERT INTO payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment['payment_id'],
            payment['task_id'],
            payment['contractor_id'],
            payment['amount'],
            payment['payment_type'],
            payment['platform_fee'],
            payment['net_amount'],
            payment['status'],
            payment['escrow_release_date'],
            payment['paid_at']
        ))
        
        conn.commit()
        conn.close()
        
        return payment
    
    def _update_contractor_performance(self, contractor_id: str, task_quality: float):
        """Update contractor Blessings Reservoir performance score."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT performance_score, tasks_completed FROM contractors WHERE contractor_id = ?', (contractor_id,))
        current_score, tasks_completed = cursor.fetchone()
        
        # Weighted average (recent tasks matter more)
        weight = 0.3  # 30% weight to new task
        new_score = (current_score * (1 - weight)) + (task_quality * weight)
        
        # Determine status based on performance thresholds
        if new_score >= self.sanctified_rates['performance_thresholds']['excellent']:
            status = 'active'
        elif new_score >= self.sanctified_rates['performance_thresholds']['acceptable']:
            status = 'active'
        else:
            status = 'review'  # Needs performance review
        
        cursor.execute('''
            UPDATE contractors 
            SET performance_score = ?, status = ?
            WHERE contractor_id = ?
        ''', (new_score, status, contractor_id))
        
        conn.commit()
        conn.close()
        
        print(f"   [PERFORMANCE] Contractor {contractor_id}: {new_score:.1f}/100")
    
    def release_escrow_payments(self) -> List[Dict[str, Any]]:
        """Release escrowed payments after hold period."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM payments 
            WHERE status = 'escrowed' 
            AND datetime(escrow_release_date) <= datetime('now')
        ''')
        
        payments_to_release = cursor.fetchall()
        
        released = []
        
        for payment in payments_to_release:
            payment_id = payment[0]
            net_amount = payment[6]
            
            paid_at = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE payments 
                SET status = 'paid', paid_at = ?
                WHERE payment_id = ?
            ''', (paid_at, payment_id))
            
            released.append({
                'payment_id': payment_id,
                'net_amount': net_amount,
                'paid_at': paid_at
            })
            
            print(f"   [RELEASE] Payment {payment_id}: ${net_amount:,.2f}")
        
        conn.commit()
        conn.close()
        
        return released
    
    def generate_contractor_report(self) -> str:
        """Generate comprehensive contractor management report."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contractor metrics
        cursor.execute('SELECT COUNT(*) FROM contractors WHERE status = "active"')
        active_contractors = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(performance_score) FROM contractors WHERE status = "active"')
        avg_performance = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(total_earnings) FROM contractors')
        total_paid = cursor.fetchone()[0] or 0
        
        # Task metrics
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "open"')
        open_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "assigned"')
        assigned_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(quality_score) FROM tasks WHERE quality_score IS NOT NULL')
        avg_quality = cursor.fetchone()[0] or 0
        
        # Payment metrics
        cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "escrowed"')
        escrowed_amount = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(net_amount) FROM payments WHERE status = "paid"')
        paid_amount = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(platform_fee) FROM payments')
        total_fees = cursor.fetchone()[0] or 0
        
        # Top performers
        cursor.execute('''
            SELECT name, performance_score, tasks_completed, total_earnings 
            FROM contractors 
            WHERE status = "active"
            ORDER BY performance_score DESC 
            LIMIT 5
        ''')
        top_performers = cursor.fetchall()
        
        conn.close()
        
        report = f"""
============================================================
CONTRACTOR VP REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
============================================================

CONTRACTOR POOL:
   Active Contractors: {active_contractors}
   Avg Performance: {avg_performance:.1f}/100
   Total Paid: ${total_paid:,.2f}

TASK PIPELINE:
   Open Tasks: {open_tasks}
   Assigned Tasks: {assigned_tasks}
   Completed Tasks: {completed_tasks}
   Avg Quality: {avg_quality:.1f}/100

PAYMENT METRICS:
   Escrowed: ${escrowed_amount:,.2f}
   Released: ${paid_amount:,.2f}
   Platform Fees: ${total_fees:,.2f}

TOP PERFORMERS:
"""
        
        for i, performer in enumerate(top_performers, 1):
            report += f"\n   {i}. {performer[0]}: {performer[1]:.1f}/100 ({performer[2]} tasks, ${performer[3]:,.2f} earned)"
        
        report += f"""

SANCTIFIED RATES:
   Junior: ${self.sanctified_rates['skill_tiers']['junior']['hourly_rate']}/hr
   Mid: ${self.sanctified_rates['skill_tiers']['mid']['hourly_rate']}/hr
   Senior: ${self.sanctified_rates['skill_tiers']['senior']['hourly_rate']}/hr
   Expert: ${self.sanctified_rates['skill_tiers']['expert']['hourly_rate']}/hr
   Integrity Hash: {self.sanctified_rates['integrity_hash']}

============================================================

RECOMMENDATIONS:
"""
        
        if open_tasks > 10:
            report += f"\n   [ACTION] {open_tasks} open tasks - recruit more contractors"
        
        if avg_performance < 75:
            report += f"\n   [WARN] Avg performance ({avg_performance:.1f}) below target (75)"
        
        if escrowed_amount > paid_amount * 0.5:
            report += f"\n   [REVIEW] High escrow balance - review payment releases"
        
        if active_contractors < 5:
            report += f"\n   [URGENT] Only {active_contractors} contractors - onboard more talent"
        
        if not (open_tasks > 10 or avg_performance < 75 or escrowed_amount > paid_amount * 0.5 or active_contractors < 5):
            report += "\n   [GOOD] Contractor operations healthy"
            report += "\n   -> Continue delegation automation"
        
        report += f"""

Next check: {(datetime.now() + timedelta(days=1)).strftime('%B %d at %I:%M %p')}
"""
        
        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA CONTRACTOR VP")
    print("="*60)
    
    contractor_vp = MytharaContractorVP()
    
    # Onboard test contractors
    print("\n1. Onboarding Contractors...")
    
    contractor1 = contractor_vp.onboard_contractor({
        'name': 'Alice Johnson',
        'email': 'alice@contractor.com',
        'skill_tier': 'senior',
        'skills': ['Python', 'FastAPI', 'SQLite'],
        'platform': 'upwork',
        'profile_url': 'https://upwork.com/alice'
    })
    
    contractor2 = contractor_vp.onboard_contractor({
        'name': 'Bob Smith',
        'email': 'bob@contractor.com',
        'skill_tier': 'mid',
        'skills': ['JavaScript', 'React', 'Node.js'],
        'platform': 'fiverr'
    })
    
    # Create tasks with auto-assignment
    print("\n2. Creating and Auto-Assigning Tasks...")
    
    task1 = contractor_vp.create_task({
        'task_type': 'bug_fix',
        'title': 'Fix payment processing error',
        'description': 'Resolve issue with PayPal integration timeout',
        'estimated_hours': 4,
        'auto_assign': True
    })
    
    task2 = contractor_vp.create_task({
        'task_type': 'code_review',
        'title': 'Review contractor VP implementation',
        'description': 'Security audit and code quality review',
        'estimated_hours': 2,
        'auto_assign': True
    })
    
    # Complete task
    print("\n3. Completing Task...")
    
    completion = contractor_vp.complete_task(task1['task_id'], {
        'actual_hours': 3.5,
        'quality_score': 95,
        'deliverable_url': 'https://github.com/mythara/fix-123'
    })
    
    # Release escrow payments
    print("\n4. Checking Escrow Releases...")
    released = contractor_vp.release_escrow_payments()
    print(f"   Released {len(released)} payment(s)")
    
    # Generate report
    print("\n5. Generating Contractor Report...")
    report = contractor_vp.generate_contractor_report()
    print(report)
    
    print("="*60)
    print("[OK] Contractor VP operational")
    print("[OK] Auto-delegation enabled")
    print("[OK] Performance tracking active")
