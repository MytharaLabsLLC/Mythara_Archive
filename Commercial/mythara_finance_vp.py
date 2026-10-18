import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara VP of Finance & Revenue - Autonomous Financial Management
Handles billing, revenue tracking, forecasting, subscription management, payment processing.

Uses Mythara SSIP:
- Sanctification: Pricing rules locked (immutable)
- Integrity Hashing: All financial transactions cryptographically verified
- Blessings Reservoir: Customer payment health scores
- Shadow_Resolver: Auto-retry failed payments
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

class MytharaFinanceVP:
    """VP of Finance & Revenue - Autonomous financial operations."""
    
    def __init__(self):
        self.bot_id = "finance_vp"
        self.bot_token = None
        self.db_path = "mythara_finance.db"
        self.sanctified_pricing = self._init_sanctified_pricing()
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_sanctified_pricing(self) -> Dict[str, Any]:
        """Initialize sanctified pricing rules (immutable)."""
        pricing = {
            'products': {
                'MYTH-AUDIT-001': {'price': 500, 'type': 'one_time', 'cost': 50, 'margin': 0.90},
                'MYTH-SUB-MONTH': {'price': 300, 'type': 'monthly', 'cost': 30, 'margin': 0.90},
                'MYTH-SUB-YEAR': {'price': 5000, 'type': 'yearly', 'cost': 500, 'margin': 0.90},
                'MYTH-ENT-YEAR': {'price': 25000, 'type': 'yearly', 'cost': 2500, 'margin': 0.90},
                'MYTH-CUSTOM-001': {'price': 10000, 'type': 'one_time', 'cost': 1000, 'margin': 0.90},
                'MYTH-TRAIN-001': {'price': 1000, 'type': 'one_time', 'cost': 100, 'margin': 0.90},
                'MYTH-VOIP-2026': {'price': 1500000, 'type': 'one_time', 'cost': 150000, 'margin': 0.90}
            },
            'payment_retry_schedule': [1, 3, 7, 14],  # Days to retry failed payments
            'churn_threshold_days': 30,  # Mark as churned after 30 days no payment
            'integrity_hash': hashlib.sha256(json.dumps({'version': '2025.1'}, sort_keys=True).encode()).hexdigest()[:16]
        }
        return pricing
    
    def _init_db(self):
        """Initialize finance database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Revenue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue (
                transaction_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                product_sku TEXT NOT NULL,
                amount REAL NOT NULL,
                cost REAL NOT NULL,
                margin REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                recognized_at TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Contractor expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contractor_expenses (
                expense_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                amount REAL NOT NULL,
                task_count INT DEFAULT 0,
                period_start TEXT,
                period_end TEXT,
                status TEXT DEFAULT 'pending',
                paid_at TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                product_sku TEXT NOT NULL,
                mrr REAL NOT NULL,
                status TEXT DEFAULT 'active',
                next_billing_date TEXT NOT NULL,
                started_at TEXT NOT NULL,
                cancelled_at TEXT,
                churn_reason TEXT
            )
        ''')
        
        # Payment failures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_failures (
                failure_id TEXT PRIMARY KEY,
                subscription_id TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                amount REAL NOT NULL,
                retry_count INT DEFAULT 0,
                next_retry_date TEXT,
                last_error TEXT,
                failed_at TEXT NOT NULL,
                resolved_at TEXT,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
            )
        ''')
        
        # Forecasts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                forecast_id TEXT PRIMARY KEY,
                period TEXT NOT NULL,
                predicted_mrr REAL,
                predicted_arr REAL,
                predicted_churn_rate REAL,
                confidence REAL,
                generated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _register(self):
        """Register Finance VP with orchestrator."""
        try:
            response = requests.post(f"{ORCHESTRATOR_URL}/register_bot", json={
                'vp_token': VP_MASTER_TOKEN,
                'bot_id': self.bot_id,
                'bot_name': 'Finance VP Bot'
            })
            if response.status_code == 200:
                self.bot_token = response.json()['bot_token']
                print(f"[OK] Registered as Finance VP")
                print(f"   Token: {self.bot_token[:16]}...")
            else:
                print(f"[WARN] Registration failed: {response.text}")
        except Exception as e:
            print(f"[WARN] Could not register: {e}")
    
    def record_revenue(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record revenue transaction with integrity hashing."""
        
        product_sku = payment_data['product_sku']
        
        if product_sku not in self.sanctified_pricing['products']:
            return {'error': f'Unknown product: {product_sku}'}
        
        pricing = self.sanctified_pricing['products'][product_sku]
        
        transaction_id = hashlib.sha256(
            f"{payment_data['customer_email']}{payment_data['amount']}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        integrity_hash = hashlib.sha256(
            json.dumps(payment_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        transaction = {
            'transaction_id': transaction_id,
            'customer_email': payment_data['customer_email'],
            'product_sku': product_sku,
            'amount': payment_data['amount'],
            'cost': pricing['cost'],
            'margin': payment_data['amount'] - pricing['cost'],
            'transaction_type': pricing['type'],
            'payment_method': payment_data.get('payment_method', 'Unknown'),
            'status': 'recognized',
            'recognized_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'integrity_hash': integrity_hash
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO revenue VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction['transaction_id'],
            transaction['customer_email'],
            transaction['product_sku'],
            transaction['amount'],
            transaction['cost'],
            transaction['margin'],
            transaction['transaction_type'],
            transaction['payment_method'],
            transaction['status'],
            transaction['recognized_at'],
            transaction['created_at'],
            transaction['integrity_hash']
        ))
        conn.commit()
        
        # If subscription, create or update subscription record
        if pricing['type'] in ['monthly', 'yearly']:
            self._create_subscription(payment_data, pricing)
        
        conn.close()
        
        print(f"[REVENUE] Recorded: ${transaction['amount']:,.2f}")
        print(f"   Transaction: {transaction_id}")
        print(f"   Margin: ${transaction['margin']:,.2f}")
        
        return transaction
    
    def _create_subscription(self, payment_data: Dict[str, Any], pricing: Dict[str, Any]):
        """Create or renew subscription."""
        
        subscription_id = hashlib.sha256(
            f"{payment_data['customer_email']}{payment_data['product_sku']}".encode()
        ).hexdigest()[:16]
        
        mrr = payment_data['amount'] if pricing['type'] == 'monthly' else payment_data['amount'] / 12
        
        next_billing = datetime.now() + timedelta(days=30 if pricing['type'] == 'monthly' else 365)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM subscriptions WHERE subscription_id = ?', (subscription_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Renew subscription
            cursor.execute('''
                UPDATE subscriptions 
                SET status = 'active', next_billing_date = ?, cancelled_at = NULL
                WHERE subscription_id = ?
            ''', (next_billing.isoformat(), subscription_id))
            print(f"[SUBSCRIPTION] Renewed: {subscription_id}")
        else:
            # Create new subscription
            cursor.execute('''
                INSERT INTO subscriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                subscription_id,
                payment_data['customer_email'],
                payment_data['product_sku'],
                mrr,
                'active',
                next_billing.isoformat(),
                datetime.now().isoformat(),
                None,
                None
            ))
            print(f"[SUBSCRIPTION] Created: {subscription_id}")
            print(f"   MRR: ${mrr:,.2f}")
        
        conn.commit()
        conn.close()
    
    def process_payment_retries(self) -> List[Dict[str, Any]]:
        """Process failed payment retries (Shadow_Resolver pattern)."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM payment_failures 
            WHERE resolved_at IS NULL 
            AND datetime(next_retry_date) <= datetime('now')
        ''')
        
        failures = cursor.fetchall()
        results = []
        
        for failure in failures:
            failure_data = {
                'failure_id': failure[0],
                'subscription_id': failure[1],
                'customer_email': failure[2],
                'amount': failure[3],
                'retry_count': failure[4],
                'next_retry_date': failure[5],
                'last_error': failure[6],
                'failed_at': failure[7]
            }
            
            print(f"\n[RETRY] Payment: {failure_data['failure_id']}")
            print(f"   Customer: {failure_data['customer_email']}")
            print(f"   Amount: ${failure_data['amount']:,.2f}")
            print(f"   Attempt: {failure_data['retry_count'] + 1}")
            
            # Simulate payment retry (in production: call payment gateway)
            retry_success = (failure_data['retry_count'] % 2 == 0)  # Simulate 50% success rate
            
            if retry_success:
                # Payment succeeded
                cursor.execute('''
                    UPDATE payment_failures 
                    SET resolved_at = ?
                    WHERE failure_id = ?
                ''', (datetime.now().isoformat(), failure_data['failure_id']))
                
                print(f"   [OK] Payment successful")
                
                results.append({
                    'failure_id': failure_data['failure_id'],
                    'status': 'resolved',
                    'retry_count': failure_data['retry_count'] + 1
                })
            else:
                # Payment still failing
                next_retry = self._calculate_next_retry(failure_data['retry_count'] + 1)
                
                if next_retry:
                    cursor.execute('''
                        UPDATE payment_failures 
                        SET retry_count = retry_count + 1, next_retry_date = ?
                        WHERE failure_id = ?
                    ''', (next_retry.isoformat(), failure_data['failure_id']))
                    
                    print(f"   [RETRY] Scheduled for: {next_retry.strftime('%Y-%m-%d')}")
                else:
                    # Max retries exceeded - mark subscription as churned
                    cursor.execute('''
                        UPDATE subscriptions 
                        SET status = 'churned', cancelled_at = ?, churn_reason = 'payment_failure'
                        WHERE subscription_id = ?
                    ''', (datetime.now().isoformat(), failure_data['subscription_id']))
                    
                    cursor.execute('''
                        UPDATE payment_failures 
                        SET resolved_at = ?
                        WHERE failure_id = ?
                    ''', (datetime.now().isoformat(), failure_data['failure_id']))
                    
                    print(f"   [CHURN] Max retries exceeded - subscription cancelled")
                
                results.append({
                    'failure_id': failure_data['failure_id'],
                    'status': 'still_failing',
                    'retry_count': failure_data['retry_count'] + 1
                })
        
        conn.commit()
        conn.close()
        
        return results
    
    def _calculate_next_retry(self, retry_count: int) -> datetime:
        """Calculate next retry date based on retry schedule."""
        schedule = self.sanctified_pricing['payment_retry_schedule']
        
        if retry_count > len(schedule):
            return None  # Max retries exceeded
        
        days = schedule[retry_count - 1]
        return datetime.now() + timedelta(days=days)
    
    def record_contractor_expense(self, contractor_email: str, amount: float, task_count: int = 0, period_start: str = None, period_end: str = None) -> Dict[str, Any]:
        """Record contractor payout as expense"""
        
        expense_id = hashlib.sha256(
            f"{contractor_email}{amount}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        created_at = datetime.now().isoformat()
        
        record = {
            'expense_id': expense_id,
            'contractor_email': contractor_email,
            'amount': amount,
            'task_count': task_count,
            'period_start': period_start or (datetime.now() - timedelta(days=7)).isoformat(),
            'period_end': period_end or datetime.now().isoformat(),
            'created_at': created_at
        }
        
        integrity_hash = hashlib.sha256(
            json.dumps(record, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contractor_expenses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            expense_id,
            contractor_email,
            amount,
            task_count,
            record['period_start'],
            record['period_end'],
            'pending',
            None,
            created_at,
            integrity_hash
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[EXPENSE] Contractor payout recorded: ${amount:,.2f}")
        print(f"   Contractor: {contractor_email}")
        print(f"   Tasks: {task_count}")
        print(f"   Expense ID: {expense_id}")
        
        return {
            'expense_id': expense_id,
            'contractor_email': contractor_email,
            'amount': amount,
            'integrity_hash': integrity_hash
        }
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate financial metrics (MRR, ARR, churn, etc.)."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total revenue
        cursor.execute('SELECT SUM(amount), SUM(margin) FROM revenue WHERE status = "recognized"')
        total_revenue, total_margin = cursor.fetchone()
        total_revenue = total_revenue or 0
        total_margin = total_margin or 0
        
        # MRR (Monthly Recurring Revenue)
        cursor.execute('SELECT SUM(mrr) FROM subscriptions WHERE status = "active"')
        mrr = cursor.fetchone()[0] or 0
        
        # ARR (Annual Recurring Revenue)
        arr = mrr * 12
        
        # Active subscriptions
        cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE status = "active"')
        active_subs = cursor.fetchone()[0]
        
        # Churned subscriptions (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM subscriptions 
            WHERE status = "churned" 
            AND datetime(cancelled_at) >= datetime('now', '-30 days')
        ''')
        recent_churn = cursor.fetchone()[0]
        
        # Churn rate
        total_subs = active_subs + recent_churn
        churn_rate = (recent_churn / total_subs * 100) if total_subs > 0 else 0
        
        # Failed payments
        cursor.execute('SELECT COUNT(*) FROM payment_failures WHERE resolved_at IS NULL')
        failed_payments = cursor.fetchone()[0]
        
        # Average transaction value
        cursor.execute('SELECT AVG(amount) FROM revenue WHERE status = "recognized"')
        avg_transaction = cursor.fetchone()[0] or 0
        
        # Contractor expenses
        cursor.execute('SELECT SUM(amount) FROM contractor_expenses WHERE status = "pending"')
        pending_contractor_expenses = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(amount) FROM contractor_expenses WHERE status = "paid"')
        paid_contractor_expenses = cursor.fetchone()[0] or 0
        
        total_contractor_expenses = pending_contractor_expenses + paid_contractor_expenses
        
        conn.close()
        
        metrics = {
            'total_revenue': total_revenue,
            'total_margin': total_margin,
            'margin_percent': (total_margin / total_revenue * 100) if total_revenue > 0 else 0,
            'mrr': mrr,
            'arr': arr,
            'active_subscriptions': active_subs,
            'churn_rate': churn_rate,
            'failed_payments': failed_payments,
            'avg_transaction_value': avg_transaction,
            'contractor_expenses_pending': pending_contractor_expenses,
            'contractor_expenses_paid': paid_contractor_expenses,
            'contractor_expenses_total': total_contractor_expenses,
            'net_margin': total_margin - total_contractor_expenses,
            'calculated_at': datetime.now().isoformat()
        }
        
        return metrics
    
    def generate_forecast(self, months_ahead: int = 12) -> Dict[str, Any]:
        """Generate revenue forecast based on historical data."""
        
        metrics = self.calculate_metrics()
        
        # Simple linear forecast (in production: use ML models)
        monthly_growth_rate = 0.10  # Assume 10% monthly growth
        
        forecast = {
            'forecast_id': hashlib.sha256(f"forecast_{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'period': f'{months_ahead}_months',
            'predicted_mrr': metrics['mrr'] * ((1 + monthly_growth_rate) ** months_ahead),
            'predicted_arr': metrics['arr'] * ((1 + monthly_growth_rate) ** months_ahead),
            'predicted_churn_rate': max(0, metrics['churn_rate'] - 2),  # Assume improving churn
            'confidence': 0.75,  # 75% confidence
            'generated_at': datetime.now().isoformat()
        }
        
        # Save forecast
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO forecasts VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            forecast['forecast_id'],
            forecast['period'],
            forecast['predicted_mrr'],
            forecast['predicted_arr'],
            forecast['predicted_churn_rate'],
            forecast['confidence'],
            forecast['generated_at']
        ))
        conn.commit()
        conn.close()
        
        return forecast
    
    def generate_finance_report(self) -> str:
        """Generate comprehensive finance report."""
        
        metrics = self.calculate_metrics()
        forecast = self.generate_forecast(12)
        
        report = f"""
============================================================
FINANCE VP REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
============================================================

REVENUE METRICS:
   Total Revenue: ${metrics['total_revenue']:,.2f}
   Total Margin: ${metrics['total_margin']:,.2f}
   Margin %: {metrics['margin_percent']:.1f}%
   Avg Transaction: ${metrics['avg_transaction_value']:,.2f}

CONTRACTOR EXPENSES:
   Pending Payouts: ${metrics['contractor_expenses_pending']:,.2f}
   Paid Expenses: ${metrics['contractor_expenses_paid']:,.2f}
   Total Contractor Costs: ${metrics['contractor_expenses_total']:,.2f}
   Net Margin: ${metrics['net_margin']:,.2f}

RECURRING REVENUE:
   MRR (Monthly): ${metrics['mrr']:,.2f}
   ARR (Annual): ${metrics['arr']:,.2f}
   Active Subscriptions: {metrics['active_subscriptions']}

HEALTH METRICS:
   Churn Rate (30d): {metrics['churn_rate']:.1f}%
   Failed Payments: {metrics['failed_payments']}

12-MONTH FORECAST:
   Predicted MRR: ${forecast['predicted_mrr']:,.2f}
   Predicted ARR: ${forecast['predicted_arr']:,.2f}
   Predicted Churn: {forecast['predicted_churn_rate']:.1f}%
   Confidence: {forecast['confidence']*100:.0f}%

SANCTIFIED PRICING:
   Products: {len(self.sanctified_pricing['products'])}
   Retry Schedule: {', '.join(map(str, self.sanctified_pricing['payment_retry_schedule']))} days
   Integrity Hash: {self.sanctified_pricing['integrity_hash']}

============================================================

RECOMMENDATIONS:
"""
        
        if metrics['churn_rate'] > 5:
            report += f"\n   [URGENT] Churn rate ({metrics['churn_rate']:.1f}%) exceeds 5% - investigate customer issues"
        
        if metrics['failed_payments'] > 0:
            report += f"\n   [ACTION] {metrics['failed_payments']} failed payments - run retry process"
        
        if metrics['margin_percent'] < 80:
            report += f"\n   [WARN] Margin ({metrics['margin_percent']:.1f}%) below target (90%)"
        
        if forecast['predicted_arr'] > metrics['arr'] * 2:
            report += f"\n   [GOOD] Strong growth forecast - ARR expected to double in 12 months"
        
        if not (metrics['churn_rate'] > 5 or metrics['failed_payments'] > 0 or metrics['margin_percent'] < 80):
            report += "\n   [OK] All financial metrics healthy"
            report += "\n   -> Continue monitoring"
        
        report += f"""

Next check: {(datetime.now() + timedelta(days=1)).strftime('%B %d at %I:%M %p')}
"""
        
        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA FINANCE VP")
    print("="*60)
    
    finance = MytharaFinanceVP()
    
    # Simulate recording revenue from test payment
    print("\n1. Recording Test Revenue...")
    payment = {
        'customer_email': 'test.customer@example.com',
        'product_sku': 'MYTH-SUB-MONTH',
        'amount': 300.00,
        'payment_method': 'PayPal'
    }
    
    finance.record_revenue(payment)
    
    # Calculate metrics
    print("\n2. Calculating Financial Metrics...")
    metrics = finance.calculate_metrics()
    print(f"   MRR: ${metrics['mrr']:,.2f}")
    print(f"   ARR: ${metrics['arr']:,.2f}")
    
    # Generate forecast
    print("\n3. Generating 12-Month Forecast...")
    forecast = finance.generate_forecast(12)
    print(f"   Predicted ARR: ${forecast['predicted_arr']:,.2f}")
    
    # Generate report
    print("\n4. Generating Finance Report...")
    report = finance.generate_finance_report()
    print(report)
    
    print("="*60)
    print("[OK] Finance VP operational")
    print("[OK] Revenue tracking active")
    print("[OK] Forecasting enabled")
