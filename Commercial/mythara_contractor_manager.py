# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara Contractor Delegation & Payout System
- Contractor onboarding
- Task delegation and tracking
- Performance recording and performance-based payouts (market-aware)
- Audit trail and integrity hashing (SSIP-compliant)
- Integration hooks for Finance VP/orchestrator

Design notes (kept deliberately simple and auditable):
- DB: SQLite file `mythara_contractor.db`
- Tables: contractors, tasks, payouts, audits
- Payout formula (example): payout = hours * hourly_rate * multiplier
    multiplier = clamp(1 + (performance_score - 75)/100, 0.75, 1.5)
  (Performance score is 0-100; 75 baseline -> no change)
- Market adjustment: optionally apply market_rate factor to hourly_rate
- Every sensitive write adds an integrity hash recorded in the DB
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os

# Import auth module for integrated registration
try:
    from mythara_contractor_auth import ContractorAuth
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Import finance VP for expense recording
try:
    from mythara_finance_vp import MytharaFinanceVP
    FINANCE_AVAILABLE = True
except ImportError:
    FINANCE_AVAILABLE = False

DB_PATH = "mythara_contractor.db"
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment


def _hash_record(obj: Dict[str, Any]) -> str:
    s = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()[:24]


class MytharaContractorManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS contractors (
                email TEXT PRIMARY KEY,
                name TEXT,
                hourly_rate REAL,
                market_rate_factor REAL DEFAULT 1.0,
                enabled INTEGER DEFAULT 1,
                created_at TEXT,
                integrity_hash TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                contractor_email TEXT,
                description TEXT,
                estimated_hours REAL DEFAULT 0,
                assigned_at TEXT,
                completed_at TEXT,
                performance_score INTEGER,
                payout_multiplier REAL DEFAULT 1.0,
                payout_amount REAL DEFAULT 0,
                integrity_hash TEXT,
                FOREIGN KEY(contractor_email) REFERENCES contractors(email)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS payouts (
                payout_id TEXT PRIMARY KEY,
                contractor_email TEXT,
                amount REAL,
                period_start TEXT,
                period_end TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                integrity_hash TEXT,
                FOREIGN KEY(contractor_email) REFERENCES contractors(email)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS audits (
                audit_id TEXT PRIMARY KEY,
                entity TEXT,
                action TEXT,
                details TEXT,
                created_at TEXT,
                integrity_hash TEXT
            )
        ''')

        conn.commit()
        conn.close()

    # --------------------------- Auditing ---------------------------
    def _audit(self, entity: str, action: str, details: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        record = {
            'entity': entity,
            'action': action,
            'details': details,
            'created_at': datetime.now().isoformat()
        }
        ah = _hash_record(record)
        audit_id = hashlib.sha256(f"{entity}{action}{ah}".encode()).hexdigest()[:16]

        c.execute('''INSERT INTO audits VALUES (?, ?, ?, ?, ?, ?)''', (
            audit_id,
            entity,
            action,
            json.dumps(details, default=str),
            record['created_at'],
            ah
        ))
        conn.commit()
        conn.close()
        return audit_id

    # --------------------------- Contractors -------------------------
    def onboard_contractor(self, email: str, name: str, hourly_rate: float, market_rate_factor: float = 1.0, password: Optional[str] = None) -> Dict[str, Any]:
        """Onboard contractor and optionally register auth credentials"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        created_at = datetime.now().isoformat()
        record = {
            'email': email,
            'name': name,
            'hourly_rate': hourly_rate,
            'market_rate_factor': market_rate_factor,
            'enabled': 1,
            'created_at': created_at
        }
        integrity_hash = _hash_record(record)

        c.execute('''INSERT OR REPLACE INTO contractors VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            email, name, hourly_rate, market_rate_factor, 1, created_at, integrity_hash
        ))
        conn.commit()
        conn.close()

        self._audit('contractor', 'onboard', record)
        
        # Register auth credentials if password provided
        if password and AUTH_AVAILABLE:
            auth = ContractorAuth(self.db_path)
            auth.register_contractor(email, password)

        return {'email': email, 'name': name, 'hourly_rate': hourly_rate, 'market_rate_factor': market_rate_factor, 'integrity_hash': integrity_hash}

    def list_contractors(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT email, name, hourly_rate, market_rate_factor, enabled, created_at FROM contractors')
        rows = c.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append({'email': r[0], 'name': r[1], 'hourly_rate': r[2], 'market_rate_factor': r[3], 'enabled': bool(r[4]), 'created_at': r[5]})
        return out

    # --------------------------- Tasks -------------------------------
    def assign_task(self, contractor_email: str, task_id: str, description: str, estimated_hours: float = 1.0) -> Dict[str, Any]:
        assigned_at = datetime.now().isoformat()
        record = {
            'task_id': task_id,
            'contractor_email': contractor_email,
            'description': description,
            'estimated_hours': estimated_hours,
            'assigned_at': assigned_at
        }
        integrity_hash = _hash_record(record)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO tasks (task_id, contractor_email, description, estimated_hours, assigned_at, integrity_hash) VALUES (?, ?, ?, ?, ?, ?)''', (
            task_id, contractor_email, description, estimated_hours, assigned_at, integrity_hash
        ))
        conn.commit()
        conn.close()

        self._audit('task', 'assign', record)
        return {'task_id': task_id, 'contractor_email': contractor_email, 'estimated_hours': estimated_hours, 'integrity_hash': integrity_hash}

    def record_task_completion(self, task_id: str, performance_score: int, actual_hours: Optional[float] = None) -> Dict[str, Any]:
        # Fetch task
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT task_id, contractor_email, description, estimated_hours, assigned_at FROM tasks WHERE task_id = ?', (task_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise ValueError('Task not found')

        contractor = row[1]
        estimated_hours = row[3]
        completed_at = datetime.now().isoformat()

        # Performance multiplier: baseline 75 => multiplier 1.0
        # multiplier = clamp(1 + (score - 75)/100, 0.75, 1.5)
        multiplier = max(0.75, min(1.5, 1 + (performance_score - 75) / 100.0))

        # Determine hours to pay
        hours = actual_hours if actual_hours is not None else estimated_hours

        # Get contractor rate
        c.execute('SELECT hourly_rate, market_rate_factor FROM contractors WHERE email = ?', (contractor,))
        cdata = c.fetchone()
        if not cdata:
            conn.close()
            raise ValueError('Contractor not found')
        hourly_rate, market_factor = cdata
        effective_rate = hourly_rate * market_factor

        payout = hours * effective_rate * multiplier

        integrity_obj = {
            'task_id': task_id,
            'contractor': contractor,
            'hours': hours,
            'hourly_rate': hourly_rate,
            'market_factor': market_factor,
            'performance_score': performance_score,
            'multiplier': multiplier,
            'payout': payout,
            'completed_at': completed_at
        }
        integrity_hash = _hash_record(integrity_obj)

        # Update task
        c.execute('''UPDATE tasks SET completed_at = ?, performance_score = ?, payout_multiplier = ?, payout_amount = ?, integrity_hash = ? WHERE task_id = ?''', (
            completed_at, performance_score, multiplier, payout, integrity_hash, task_id
        ))
        conn.commit()
        conn.close()

        # Create payout record (pending aggregation)
        payout_id = hashlib.sha256(f"{task_id}{integrity_hash}".encode()).hexdigest()[:16]
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        period_start = (datetime.now() - timedelta(days=7)).isoformat()
        period_end = datetime.now().isoformat()
        c.execute('''INSERT INTO payouts VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            payout_id, contractor, payout, period_start, period_end, 'pending', datetime.now().isoformat(), integrity_hash
        ))
        conn.commit()
        conn.close()

        self._audit('task', 'complete', integrity_obj)

        return {'task_id': task_id, 'contractor': contractor, 'payout': payout, 'integrity_hash': integrity_hash}

    # --------------------------- Payout aggregation ------------------
    def aggregate_payouts(self, period_start: str = None, period_end: str = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if not period_start:
            period_start = (datetime.now() - timedelta(days=7)).isoformat()
        if not period_end:
            period_end = datetime.now().isoformat()

        c.execute('''SELECT payout_id, contractor_email, SUM(amount) as total FROM payouts WHERE created_at BETWEEN ? AND ? GROUP BY contractor_email''', (period_start, period_end))
        rows = c.fetchall()
        out = []
        for r in rows:
            out.append({'payout_id': r[0], 'contractor_email': r[1], 'amount': r[2]})
        conn.close()
        return out

    def finalize_payout(self, payout_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT payout_id, contractor_email, amount FROM payouts WHERE payout_id = ?', (payout_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise ValueError('Payout not found')
        # Mark as paid
        c.execute('UPDATE payouts SET status = ?, created_at = ? WHERE payout_id = ?', ('paid', datetime.now().isoformat(), payout_id))
        conn.commit()
        conn.close()
        
        # Record in Finance VP
        if FINANCE_AVAILABLE:
            try:
                finance = MytharaFinanceVP()
                finance.record_contractor_expense(
                    contractor_email=row[1],
                    amount=row[2],
                    task_count=1,  # Could query for actual task count
                    period_start=(datetime.now() - timedelta(days=7)).isoformat(),
                    period_end=datetime.now().isoformat()
                )
            except Exception as e:
                print(f"[WARN] Could not record expense in Finance VP: {e}")
        
        self._audit('payout', 'finalize', {'payout_id': payout_id, 'contractor_email': row[1], 'amount': row[2]})
        return {'payout_id': payout_id, 'contractor_email': row[1], 'amount': row[2], 'status': 'paid'}

    # --------------------------- Reporting --------------------------
    def generate_audit_report(self, last_n: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT audit_id, entity, action, details, created_at, integrity_hash FROM audits ORDER BY created_at DESC LIMIT ?', (last_n,))
        rows = c.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append({'audit_id': r[0], 'entity': r[1], 'action': r[2], 'details': json.loads(r[3]), 'created_at': r[4], 'integrity_hash': r[5]})
        return out


# Quick self-test helper when run directly
if __name__ == '__main__':
    print('\n[Contractor Manager] Starting self-test...')
    m = MytharaContractorManager()
    print('[TEST] Onboarding contractor john@example.com...')
    m.onboard_contractor('john@example.com', 'John Doe', 50.0, market_rate_factor=1.1)
    print('[TEST] Assigning task T123 to john@example.com...')
    m.assign_task('john@example.com', 'T123', 'Implement integration adaptor', estimated_hours=5)
    print('[TEST] Recording completion for T123 (score 85)...')
    res = m.record_task_completion('T123', 85, actual_hours=4.5)
    print('[TEST] Payout calculated:', res['payout'])
    print('[TEST] Audit snapshot:')
    for a in m.generate_audit_report(10):
        print('  -', a['created_at'], a['entity'], a['action'])
    print('\n[Contractor Manager] Self-test complete.')
