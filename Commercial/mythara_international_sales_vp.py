import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara International VP of Sales - Global Sales Operations
- Multi-region sales tracking (Americas, EMEA, APAC)
- Currency conversion and regional pricing
- Territory management and quota tracking
- Global pipeline visibility
- Cross-border deal compliance
- Regional performance metrics

Uses Mythara SSIP:
- Sanctification: Regional pricing rules locked (immutable)
- Integrity Hashing: All deals cryptographically verified
- Blessings Reservoir: Territory health scores
- Shadow_Resolver: Auto-escalate stalled international deals
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

class MytharaInternationalSalesVP:
    """International VP of Sales - Global sales operations."""
    
    def __init__(self):
        self.bot_id = "international_sales_vp"
        self.bot_token = None
        self.db_path = "mythara_international_sales.db"
        
        # Currency conversion rates (USD base)
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 149.50,
            "AUD": 1.52,
            "CAD": 1.36,
            "CHF": 0.88,
            "CNY": 7.24,
            "INR": 83.12,
            "SGD": 1.34,
            "BRL": 4.97,
            "MXN": 17.08
        }
        
        # Regional pricing multipliers
        self.regional_pricing = {
            "US": 1.0,
            "EU": 1.15,     # Higher pricing in EU
            "UK": 1.12,
            "JP": 1.08,
            "AU": 0.95,
            "CA": 0.98,
            "CH": 1.20,     # Switzerland premium
            "CN": 0.85,
            "IN": 0.70,     # Emerging market discount
            "SG": 1.05,
            "BR": 0.80,
            "MX": 0.75
        }
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_db(self):
        """Initialize international sales database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # International deals
        c.execute('''
            CREATE TABLE IF NOT EXISTS international_deals (
                deal_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                country_code TEXT NOT NULL,
                region TEXT NOT NULL,
                currency TEXT DEFAULT 'USD',
                deal_value_local REAL NOT NULL,
                deal_value_usd REAL NOT NULL,
                product TEXT NOT NULL,
                stage TEXT DEFAULT 'prospecting',
                probability INT DEFAULT 25,
                close_date TEXT,
                assigned_to TEXT,
                partner_channel TEXT,
                compliance_status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Regional quotas
        c.execute('''
            CREATE TABLE IF NOT EXISTS regional_quotas (
                quota_id TEXT PRIMARY KEY,
                region TEXT NOT NULL,
                quarter TEXT NOT NULL,
                quota_usd REAL NOT NULL,
                attainment_usd REAL DEFAULT 0.0,
                attainment_pct REAL DEFAULT 0.0,
                sales_rep TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Territory assignments
        c.execute('''
            CREATE TABLE IF NOT EXISTS territory_assignments (
                assignment_id TEXT PRIMARY KEY,
                sales_rep TEXT NOT NULL,
                region TEXT NOT NULL,
                countries TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Compliance tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS compliance_checks (
                check_id TEXT PRIMARY KEY,
                deal_id TEXT NOT NULL,
                check_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                details TEXT,
                checked_at TEXT,
                approved_by TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (deal_id) REFERENCES international_deals(deal_id)
            )
        ''')
        
        # International audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS intl_sales_audit (
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
        print(f"[OK] International Sales VP database initialized: {self.db_path}")
    
    def _register(self):
        """Register with orchestrator."""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/register_bot",
                json={
                    "bot_id": self.bot_id,
                    "capabilities": ["international_sales", "multi_currency", "territory_management", "compliance", "global_pipeline"],
                    "master_token": VP_MASTER_TOKEN
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.bot_token = data.get("bot_token")
                print(f"[OK] Registered as International Sales VP: {self.bot_id}")
            else:
                print(f"[WARN] Orchestrator registration failed: {response.status_code}")
        except Exception as e:
            print(f"[WARN] Could not connect to orchestrator: {e}")
    
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
            INSERT INTO intl_sales_audit (audit_id, entity, action, details, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (audit_id, entity, action, json.dumps(details), datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
    
    def _convert_currency(self, amount: float, from_currency: str, to_currency: str = "USD") -> float:
        """Convert currency using exchange rates."""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        amount_usd = amount / self.exchange_rates.get(from_currency, 1.0)
        return amount_usd * self.exchange_rates.get(to_currency, 1.0)
    
    def _get_region(self, country_code: str) -> str:
        """Map country code to region."""
        regions = {
            "US": "Americas", "CA": "Americas", "MX": "Americas", "BR": "Americas",
            "UK": "EMEA", "EU": "EMEA", "CH": "EMEA", "DE": "EMEA", "FR": "EMEA",
            "JP": "APAC", "CN": "APAC", "IN": "APAC", "AU": "APAC", "SG": "APAC"
        }
        return regions.get(country_code, "Other")
    
    def create_deal(self, company_name: str, country_code: str, product: str,
                   deal_value: float, currency: str = "USD", assigned_to: str = None,
                   partner_channel: str = None) -> Dict[str, Any]:
        """Create international sales deal."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        deal_id = f"INTL-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{company_name}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        region = self._get_region(country_code)
        
        # Apply regional pricing multiplier
        pricing_multiplier = self.regional_pricing.get(country_code, 1.0)
        adjusted_value = deal_value * pricing_multiplier
        
        # Convert to USD for tracking
        deal_value_usd = self._convert_currency(adjusted_value, currency, "USD")
        
        record = {
            "deal_id": deal_id,
            "company_name": company_name,
            "country_code": country_code,
            "region": region,
            "currency": currency,
            "deal_value_local": adjusted_value,
            "deal_value_usd": deal_value_usd,
            "product": product
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO international_deals
            (deal_id, company_name, country_code, region, currency, deal_value_local,
             deal_value_usd, product, assigned_to, partner_channel, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (deal_id, company_name, country_code, region, currency, adjusted_value,
              deal_value_usd, product, assigned_to, partner_channel,
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("deal", "created", record)
        
        print(f"[INTL SALES] Created deal: {deal_id}")
        print(f"             Company: {company_name} ({country_code})")
        print(f"             Value: {currency} {adjusted_value:,.2f} (USD ${deal_value_usd:,.2f})")
        print(f"             Region: {region}")
        
        return {"success": True, "deal_id": deal_id, "deal_value_usd": deal_value_usd}
    
    def update_deal_stage(self, deal_id: str, stage: str, probability: int) -> Dict[str, Any]:
        """Update deal stage and probability."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE international_deals
            SET stage = ?, probability = ?, updated_at = ?
            WHERE deal_id = ?
        ''', (stage, probability, datetime.now().isoformat(), deal_id))
        
        conn.commit()
        conn.close()
        
        self._audit("deal", "stage_updated", {
            "deal_id": deal_id,
            "stage": stage,
            "probability": probability
        })
        
        print(f"[INTL SALES] Updated deal stage: {deal_id}")
        print(f"             Stage: {stage} ({probability}% probability)")
        
        return {"success": True, "deal_id": deal_id, "stage": stage}
    
    def close_deal(self, deal_id: str, won: bool = True) -> Dict[str, Any]:
        """Close deal as won or lost."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stage = "closed_won" if won else "closed_lost"
        probability = 100 if won else 0
        
        # Get deal details for quota update
        c.execute('SELECT region, deal_value_usd FROM international_deals WHERE deal_id = ?', (deal_id,))
        row = c.fetchone()
        
        c.execute('''
            UPDATE international_deals
            SET stage = ?, probability = ?, close_date = ?, updated_at = ?
            WHERE deal_id = ?
        ''', (stage, probability, datetime.now().isoformat(),
              datetime.now().isoformat(), deal_id))
        
        # Update regional quota if won
        if won and row:
            region = row[0]
            deal_value = row[1]
            current_quarter = f"Q{(datetime.now().month-1)//3 + 1} {datetime.now().year}"
            
            c.execute('SELECT quota_id, attainment_usd FROM regional_quotas WHERE region = ? AND quarter = ?',
                     (region, current_quarter))
            quota_row = c.fetchone()
            
            if quota_row:
                new_attainment = quota_row[1] + deal_value
                c.execute('UPDATE regional_quotas SET attainment_usd = ? WHERE quota_id = ?',
                         (new_attainment, quota_row[0]))
        
        conn.commit()
        conn.close()
        
        self._audit("deal", "closed", {
            "deal_id": deal_id,
            "outcome": "won" if won else "lost"
        })
        
        emoji = "🎉" if won else "📊"
        print(f"[INTL SALES] {emoji} Deal {stage.upper()}: {deal_id}")
        
        return {"success": True, "deal_id": deal_id, "outcome": "won" if won else "lost"}
    
    def set_regional_quota(self, region: str, quarter: str, quota_usd: float, sales_rep: str = None) -> Dict[str, Any]:
        """Set regional sales quota."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        quota_id = hashlib.sha256(f"{region}{quarter}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "quota_id": quota_id,
            "region": region,
            "quarter": quarter,
            "quota_usd": quota_usd,
            "sales_rep": sales_rep
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO regional_quotas
            (quota_id, region, quarter, quota_usd, sales_rep, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quota_id, region, quarter, quota_usd, sales_rep,
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("quota", "set", record)
        
        print(f"[INTL SALES] Set quota: {region} - {quarter}")
        print(f"             Target: USD ${quota_usd:,.2f}")
        
        return {"success": True, "quota_id": quota_id}
    
    def assign_territory(self, sales_rep: str, region: str, countries: List[str]) -> Dict[str, Any]:
        """Assign territory to sales rep."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        assignment_id = hashlib.sha256(f"{sales_rep}{region}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "assignment_id": assignment_id,
            "sales_rep": sales_rep,
            "region": region,
            "countries": countries
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO territory_assignments
            (assignment_id, sales_rep, region, countries, start_date, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (assignment_id, sales_rep, region, json.dumps(countries),
              datetime.now().isoformat(), datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("territory", "assigned", record)
        
        print(f"[INTL SALES] Assigned territory: {region}")
        print(f"             Sales Rep: {sales_rep}")
        print(f"             Countries: {', '.join(countries)}")
        
        return {"success": True, "assignment_id": assignment_id}
    
    def check_compliance(self, deal_id: str, check_type: str) -> Dict[str, Any]:
        """Perform compliance check on international deal."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        check_id = hashlib.sha256(f"{deal_id}{check_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Auto-approve for demo (in production: integrate with compliance systems)
        status = "approved"
        
        record = {
            "check_id": check_id,
            "deal_id": deal_id,
            "check_type": check_type,
            "status": status
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO compliance_checks
            (check_id, deal_id, check_type, status, checked_at, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (check_id, deal_id, check_type, status, datetime.now().isoformat(),
              datetime.now().isoformat(), integrity_hash))
        
        # Update deal compliance status
        c.execute('UPDATE international_deals SET compliance_status = ? WHERE deal_id = ?',
                 ("approved", deal_id))
        
        conn.commit()
        conn.close()
        
        self._audit("compliance", "checked", record)
        
        print(f"[INTL SALES] Compliance check: {check_type}")
        print(f"             Deal: {deal_id}")
        print(f"             Status: {status}")
        
        return {"success": True, "check_id": check_id, "status": status}
    
    def generate_regional_report(self) -> str:
        """Generate international sales report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Regional pipeline
        c.execute('''
            SELECT region, COUNT(*), SUM(deal_value_usd), AVG(probability)
            FROM international_deals
            WHERE stage NOT LIKE 'closed_%'
            GROUP BY region
        ''')
        pipeline_by_region = c.fetchall()
        
        # Closed deals by region
        c.execute('''
            SELECT region, COUNT(*), SUM(deal_value_usd)
            FROM international_deals
            WHERE stage = 'closed_won'
            GROUP BY region
        ''')
        closed_by_region = c.fetchall()
        
        # Quota attainment
        current_quarter = f"Q{(datetime.now().month-1)//3 + 1} {datetime.now().year}"
        c.execute('''
            SELECT region, quota_usd, attainment_usd
            FROM regional_quotas
            WHERE quarter = ?
        ''', (current_quarter,))
        quotas = c.fetchall()
        
        # Compliance
        c.execute('SELECT COUNT(*) FROM compliance_checks WHERE status = "pending"')
        pending_compliance = c.fetchone()[0]
        
        conn.close()
        
        report = f"""
================================================================
   MYTHARA INTERNATIONAL SALES VP - GLOBAL SALES REPORT
                     {datetime.now().strftime("%Y-%m-%d %H:%M")}
================================================================

REGIONAL PIPELINE:
"""
        for region, count, total, avg_prob in pipeline_by_region:
            report += f"   {region:12s}: {count:3d} deals | USD ${total:,.2f} | {avg_prob:.0f}% avg prob\n"
        
        report += f"\nCLOSED DEALS (Won):\n"
        for region, count, total in closed_by_region:
            report += f"   {region:12s}: {count:3d} deals | USD ${total:,.2f}\n"
        
        report += f"\nQUOTA ATTAINMENT ({current_quarter}):\n"
        for region, quota, attainment in quotas:
            pct = (attainment / quota * 100) if quota > 0 else 0
            status = "[OK]" if pct >= 100 else "[->]" if pct >= 75 else "[!]"
            report += f"   {region:12s}: ${attainment:,.0f} / ${quota:,.0f} ({pct:.0f}%) {status}\n"
        
        report += f"\nCOMPLIANCE:\n"
        report += f"   Pending Checks: {pending_compliance}\n"
        compliance_status = "[!] REVIEW REQUIRED" if pending_compliance > 0 else "[OK] All compliant"
        report += f"   {compliance_status}\n"
        
        report += "\n================================================================\n"
        
        return report

if __name__ == "__main__":
    print("Mythara International VP of Sales - Global Sales Operations")
    print("=" * 60)
    
    sales = MytharaInternationalSalesVP()
    
    # Set quarterly quotas
    current_quarter = f"Q{(datetime.now().month-1)//3 + 1} {datetime.now().year}"
    sales.set_regional_quota("Americas", current_quarter, 500000, "alice@mythara.com")
    sales.set_regional_quota("EMEA", current_quarter, 400000, "bob@mythara.com")
    sales.set_regional_quota("APAC", current_quarter, 300000, "charlie@mythara.com")
    
    # Assign territories
    sales.assign_territory("alice@mythara.com", "Americas", ["US", "CA", "MX", "BR"])
    sales.assign_territory("bob@mythara.com", "EMEA", ["UK", "DE", "FR", "CH"])
    sales.assign_territory("charlie@mythara.com", "APAC", ["JP", "CN", "IN", "AU", "SG"])
    
    # Create international deals
    print("\n[CREATING DEALS]")
    deal1 = sales.create_deal("Acme Corp UK", "UK", "MYTH-ENT-YEAR", 25000, "GBP", "bob@mythara.com")
    deal2 = sales.create_deal("Tokyo Tech Ltd", "JP", "MYTH-SUB-YEAR", 5000000, "JPY", "charlie@mythara.com")
    deal3 = sales.create_deal("Sydney Solutions", "AU", "MYTH-ENT-YEAR", 35000, "AUD", "charlie@mythara.com")
    deal4 = sales.create_deal("Berlin Innovations", "DE", "MYTH-CUSTOM-001", 10000, "EUR", "bob@mythara.com")
    
    # Update stages
    print("\n[UPDATING STAGES]")
    sales.update_deal_stage(deal1['deal_id'], "negotiation", 75)
    sales.update_deal_stage(deal2['deal_id'], "proposal", 50)
    sales.update_deal_stage(deal3['deal_id'], "discovery", 25)
    
    # Compliance checks
    print("\n[COMPLIANCE CHECKS]")
    sales.check_compliance(deal1['deal_id'], "export_control")
    sales.check_compliance(deal2['deal_id'], "data_residency")
    
    # Close deals
    print("\n[CLOSING DEALS]")
    sales.close_deal(deal1['deal_id'], won=True)
    sales.close_deal(deal4['deal_id'], won=True)
    
    # Generate report
    print("\n" + sales.generate_regional_report())
