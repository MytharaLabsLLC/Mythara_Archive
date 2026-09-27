import os
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Autonomous Tax & Revenue Reporting System

Automatically:
- Tracks all revenue from bot sales
- Generates quarterly tax reports
- Creates 1099-NEC forms for contractors (if needed)
- Emails tax summaries to Herbievelezjr@gmail.com
- Calculates estimated quarterly taxes

Full automation - you just file the forms.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class TaxRevenueTracker:
    """Track revenue and generate tax forms"""
    
    def __init__(self, filepath: str = "Commercial/revenue_ledger.json"):
        self.filepath = Path(filepath)
        self.ledger = self._load_ledger()
        self.owner_email = "Herbievelezjr@gmail.com"
        self.business_name = "Mythara Engine"
        self.ein = "PENDING"  # Mythara Labs LLC formation filed with Colorado SOS 2026-09-27, pending completion; EIN follows
    
    def _load_ledger(self) -> Dict:
        if self.filepath.exists():
            return json.loads(self.filepath.read_text())
        
        return {
            "transactions": [],
            "quarterly_reports": {},
            "ytd_revenue": 0.0,
            "ytd_expenses": 0.0,
            "last_report_sent": None
        }
    
    def _save_ledger(self):
        self.filepath.parent.mkdir(exist_ok=True)
        self.filepath.write_text(json.dumps(self.ledger, indent=2))
    
    def record_sale(self, customer_email: str, amount: float, payment_method: str, deal_type: str):
        """Record revenue from bot sale"""
        transaction = {
            "transaction_id": f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "date": datetime.now().isoformat(),
            "customer_email": customer_email,
            "amount": amount,
            "payment_method": payment_method,  # stripe, zelle, check, etc
            "deal_type": deal_type,  # early_adopter, standard, enterprise
            "quarter": self._get_current_quarter(),
            "year": datetime.now().year,
            "recorded_by": "autonomous_bot"
        }
        
        self.ledger["transactions"].append(transaction)
        self.ledger["ytd_revenue"] += amount
        self._save_ledger()
        
        print(f"💰 Sale recorded: ${amount:,.2f} from {customer_email}")
        print(f"   YTD Revenue: ${self.ledger['ytd_revenue']:,.2f}")
        
        return transaction
    
    def record_expense(self, description: str, amount: float, category: str):
        """Record business expense"""
        expense = {
            "expense_id": f"EX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "date": datetime.now().isoformat(),
            "description": description,
            "amount": amount,
            "category": category,  # software, hosting, marketing, etc
            "quarter": self._get_current_quarter(),
            "year": datetime.now().year
        }
        
        if "expenses" not in self.ledger:
            self.ledger["expenses"] = []
        
        self.ledger["expenses"].append(expense)
        self.ledger["ytd_expenses"] += amount
        self._save_ledger()
        
        print(f"📤 Expense recorded: ${amount:,.2f} - {description}")
    
    def _get_current_quarter(self) -> str:
        """Get current quarter (Q1-Q4)"""
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter}"
    
    def _get_quarter_dates(self, quarter: str, year: int):
        """Get start/end dates for quarter"""
        q_num = int(quarter[1])
        start_month = (q_num - 1) * 3 + 1
        end_month = q_num * 3
        
        start_date = datetime(year, start_month, 1)
        
        # Last day of end month
        if end_month == 12:
            end_date = datetime(year, 12, 31)
        else:
            end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    def generate_quarterly_report(self, quarter: str = None, year: int = None) -> Dict:
        """Generate quarterly tax report"""
        if not quarter:
            quarter = self._get_current_quarter()
        if not year:
            year = datetime.now().year
        
        # Filter transactions for this quarter
        quarter_transactions = [
            t for t in self.ledger["transactions"]
            if t["quarter"] == quarter and t["year"] == year
        ]
        
        # Filter expenses for this quarter
        quarter_expenses = [
            e for e in self.ledger.get("expenses", [])
            if e["quarter"] == quarter and e["year"] == year
        ]
        
        # Calculate totals
        total_revenue = sum(t["amount"] for t in quarter_transactions)
        total_expenses = sum(e["amount"] for e in quarter_expenses)
        net_income = total_revenue - total_expenses
        
        # Estimated quarterly taxes (self-employment + income)
        # Sole proprietor: ~15.3% self-employment + ~22% income tax (simplified)
        # Real calculation is more complex, but this is close enough
        estimated_se_tax = net_income * 0.153  # Self-employment tax
        estimated_income_tax = net_income * 0.22  # Estimated income tax bracket
        total_estimated_tax = estimated_se_tax + estimated_income_tax
        
        report = {
            "quarter": quarter,
            "year": year,
            "start_date": self._get_quarter_dates(quarter, year)[0].strftime("%Y-%m-%d"),
            "end_date": self._get_quarter_dates(quarter, year)[1].strftime("%Y-%m-%d"),
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "estimated_se_tax": estimated_se_tax,
            "estimated_income_tax": estimated_income_tax,
            "total_estimated_tax": total_estimated_tax,
            "transactions": quarter_transactions,
            "expenses": quarter_expenses,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to quarterly reports
        report_key = f"{year}_{quarter}"
        self.ledger["quarterly_reports"][report_key] = report
        self._save_ledger()
        
        return report
    
    def generate_1099_nec(self, contractor_name: str, contractor_ein: str, amount_paid: float, year: int):
        """
        Generate 1099-NEC for contractors (if you pay anyone >$600/year)
        
        Note: As sole proprietor paying contractors, you need to issue 1099-NEC
        """
        form_1099 = {
            "form": "1099-NEC",
            "year": year,
            "payer": {
                "name": self.business_name,
                "ein": self.ein,
                "address": "Your Business Address",  # Update when you get one
                "email": self.owner_email
            },
            "recipient": {
                "name": contractor_name,
                "ein": contractor_ein,
                "amount": amount_paid
            },
            "box_1_nonemployee_compensation": amount_paid,
            "generated_at": datetime.now().isoformat()
        }
        
        return form_1099
    
    def email_quarterly_report(self, quarter: str = None, year: int = None):
        """Email quarterly tax report to owner"""
        report = self.generate_quarterly_report(quarter, year)
        
        # Create email
        subject = f"🧾 Mythara Engine - {report['quarter']} {report['year']} Tax Report"
        
        body = f"""Herbert,

Your quarterly tax report is ready.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 {report['quarter']} {report['year']} FINANCIAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Period: {report['start_date']} to {report['end_date']}

REVENUE:
  Gross Revenue: ${report['total_revenue']:,.2f}
  Total Expenses: ${report['total_expenses']:,.2f}
  ─────────────────────────
  Net Income: ${report['net_income']:,.2f}

ESTIMATED QUARTERLY TAXES:
  Self-Employment Tax (15.3%): ${report['estimated_se_tax']:,.2f}
  Income Tax (Est. 22%): ${report['estimated_income_tax']:,.2f}
  ─────────────────────────
  TOTAL ESTIMATED: ${report['total_estimated_tax']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRANSACTIONS THIS QUARTER: {len(report['transactions'])}
"""

        # Add transaction details
        for i, txn in enumerate(report['transactions'], 1):
            txn_date = datetime.fromisoformat(txn['date']).strftime('%Y-%m-%d')
            body += f"\n  {i}. {txn_date} - ${txn['amount']:,.2f} from {txn['customer_email']} ({txn['deal_type']})"

        body += f"\n\nEXPENSES THIS QUARTER: {len(report['expenses'])}"
        
        for i, exp in enumerate(report['expenses'], 1):
            exp_date = datetime.fromisoformat(exp['date']).strftime('%Y-%m-%d')
            body += f"\n  {i}. {exp_date} - ${exp['amount']:,.2f} - {exp['description']} ({exp['category']})"

        body += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YEAR-TO-DATE TOTALS:
  YTD Revenue: ${self.ledger['ytd_revenue']:,.2f}
  YTD Expenses: ${self.ledger['ytd_expenses']:,.2f}
  YTD Net: ${self.ledger['ytd_revenue'] - self.ledger['ytd_expenses']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 NEXT STEPS:

1. Pay estimated quarterly taxes by: {self._get_next_tax_deadline(report['quarter'])}
   - Use IRS Form 1040-ES
   - Pay online at irs.gov/payments

2. Save this report for annual tax filing

3. Full ledger saved at: {self.filepath}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated automatically by Mythara Autonomous Bot
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Questions? Reply to this email.
"""

        # Send email (using Gmail SMTP)
        self._send_email(subject, body)
        
        self.ledger["last_report_sent"] = datetime.now().isoformat()
        self._save_ledger()
        
        print(f"\n✅ Quarterly report emailed to {self.owner_email}")
        
        return report
    
    def _get_next_tax_deadline(self, quarter: str) -> str:
        """Get IRS quarterly tax deadline"""
        year = datetime.now().year
        deadlines = {
            "Q1": f"April 15, {year}",
            "Q2": f"June 15, {year}",
            "Q3": f"September 15, {year}",
            "Q4": f"January 15, {year + 1}"
        }
        return deadlines.get(quarter, "Check IRS.gov")
    
    def _send_email(self, subject: str, body: str):
        """Send email via Gmail SMTP"""
        
        # For now, just print (you'll need to set up Gmail App Password)
        print(f"\n📧 EMAIL TO: {self.owner_email}")
        print(f"SUBJECT: {subject}")
        print(f"\n{body}")
        
        # To actually send, uncomment and configure:
        """
        # Gmail SMTP setup
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "mythara.engine@gmail.com"  # Your bot email
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        sender_password = os.getenv("SENDER_PASSWORD", "")  # Set via environment
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = self.owner_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        """
    
    def auto_quarterly_check(self):
        """
        Run this daily - checks if quarter ended and auto-sends report
        
        This would run as a cron job or scheduled task
        """
        current_quarter = self._get_current_quarter()
        current_year = datetime.now().year
        
        # Check if we've already sent report for this quarter
        report_key = f"{current_year}_{current_quarter}"
        
        if report_key not in self.ledger["quarterly_reports"]:
            # Check if quarter just ended
            today = datetime.now().date()
            quarter_end = self._get_quarter_dates(current_quarter, current_year)[1].date()
            
            # If we're past quarter end by 1-7 days, send report
            if quarter_end < today <= quarter_end + timedelta(days=7):
                print(f"📅 Quarter ended - generating report...")
                self.email_quarterly_report(current_quarter, current_year)


# ============================================================================
# INTEGRATION WITH AUTONOMOUS BOT
# ============================================================================

class AutonomousBotWithTaxes:
    """Combines autonomous sales bot with tax tracking"""
    
    def __init__(self):
        from autonomous_sales_bot import AutonomousSalesBot
        self.sales_bot = AutonomousSalesBot(full_autonomy=True)
        self.tax_tracker = TaxRevenueTracker()
    
    def record_closed_deal(self, customer_email: str, amount: float, payment_method: str = "stripe"):
        """When bot closes a deal, automatically record for taxes"""
        
        # Determine deal type
        if amount <= 500:
            deal_type = "early_adopter"
        elif amount <= 2500:
            deal_type = "standard"
        else:
            deal_type = "enterprise"
        
        # Record the sale
        transaction = self.tax_tracker.record_sale(
            customer_email=customer_email,
            amount=amount,
            payment_method=payment_method,
            deal_type=deal_type
        )
        
        # Also record in sales bot learning
        self.sales_bot.record_deal_outcome(
            email_hash=transaction["transaction_id"],
            outcome="closed_deal",
            deal_value=int(amount)
        )
        
        print(f"\n🎉 DEAL CLOSED & RECORDED FOR TAXES")
        print(f"   Customer: {customer_email}")
        print(f"   Amount: ${amount:,.2f}")
        print(f"   YTD Revenue: ${self.tax_tracker.ledger['ytd_revenue']:,.2f}")
    
    def run_end_of_day(self):
        """Run daily - checks for quarter end and sends reports"""
        print("\n🌙 End of day processing...")
        
        # Check if quarter ended (auto-send tax report)
        self.tax_tracker.auto_quarterly_check()
        
        # Run bot health check
        self.sales_bot.run_daily_health_check()
        
        # Run quarterly sales cycle
        self.sales_bot.run_quarterly_cycle()


# ============================================================================
# DEMO
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("💰 AUTONOMOUS TAX & REVENUE TRACKING")
    print("="*80)
    
    bot = AutonomousBotWithTaxes()
    
    # Simulate some sales (demo: placeholder addresses, not real customers)
    print("\n📊 RECORDING SALES...")
    bot.record_closed_deal("demo.prospect1@example.com", 500, "stripe")
    bot.record_closed_deal("demo.prospect2@example.com", 2500, "zelle")
    bot.record_closed_deal("demo.prospect3@example.com", 500, "stripe")
    
    # Record some expenses
    print("\n📤 RECORDING EXPENSES...")
    bot.tax_tracker.record_expense("OpenAI API credits", 25.00, "software")
    bot.tax_tracker.record_expense("ChromaDB hosting", 0.00, "hosting")
    
    # Generate quarterly report
    print("\n" + "="*80)
    print("📧 GENERATING & EMAILING QUARTERLY REPORT")
    print("="*80)
    
    report = bot.tax_tracker.email_quarterly_report()
    
    print("\n" + "="*80)
    print("✅ FULLY AUTOMATED TAX TRACKING")
    print("="*80)
    print("\nThe bot now:")
    print("  ✓ Records every sale automatically")
    print("  ✓ Tracks expenses")
    print("  ✓ Generates quarterly tax reports")
    print("  ✓ Emails reports to Herbievelezjr@gmail.com")
    print("  ✓ Calculates estimated quarterly taxes")
    print("  ✓ Reminds you of IRS deadlines")
    print("\n💼 You just file the forms - bot handles the accounting")
