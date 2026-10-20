# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara VP of Accounting Bot
Autonomous financial accounting, bookkeeping, tax compliance, audit preparation,
financial reporting, grant fund tracking, and regulatory compliance
"""

import os
import sqlite3
import hashlib
import json
import requests
from datetime import datetime
from typing import List


class MytharaAccountingVP:
    def __init__(self, db_path: str = "mythara_accounting.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.orchestrator_url = os.getenv(
            "MYTHARA_ORCHESTRATOR_URL", "http://localhost:5000"
        )
        self._init_database()
        self._register_with_orchestrator()

    def _init_database(self):
        """Initialize accounting database schema"""
        c = self.conn.cursor()

        # Chart of accounts
        c.execute("""
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT UNIQUE NOT NULL,
                account_name TEXT NOT NULL,
                account_type TEXT CHECK(account_type IN ('asset', 'liability', 'equity', 'revenue', 'expense')),
                account_subtype TEXT,
                normal_balance TEXT CHECK(normal_balance IN ('debit', 'credit')),
                description TEXT,
                is_active INTEGER DEFAULT 1,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # General ledger entries
        c.execute("""
            CREATE TABLE IF NOT EXISTS general_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL,
                account_number TEXT NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('debit', 'credit')),
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT NOT NULL,
                reference_number TEXT,
                posted_by TEXT DEFAULT 'VP_Accounting_Bot',
                reconciled INTEGER DEFAULT 0,
                fiscal_year INTEGER,
                fiscal_quarter INTEGER CHECK(fiscal_quarter BETWEEN 1 AND 4),
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES chart_of_accounts(account_number)
            )
        """)

        # Accounts payable
        c.execute("""
            CREATE TABLE IF NOT EXISTS accounts_payable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                amount_paid REAL DEFAULT 0 CHECK(amount_paid >= 0),
                status TEXT CHECK(status IN ('pending', 'approved', 'paid', 'overdue', 'disputed')),
                category TEXT,
                payment_terms TEXT,
                notes TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Accounts receivable
        c.execute("""
            CREATE TABLE IF NOT EXISTS accounts_receivable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                amount_received REAL DEFAULT 0 CHECK(amount_received >= 0),
                status TEXT CHECK(status IN ('pending', 'sent', 'paid', 'overdue', 'collections')),
                payment_terms TEXT,
                contract_reference TEXT,
                notes TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Grant fund tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_funds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_name TEXT NOT NULL,
                grantor TEXT NOT NULL,
                grant_type TEXT,
                award_amount REAL NOT NULL CHECK(award_amount > 0),
                amount_received REAL DEFAULT 0,
                amount_spent REAL DEFAULT 0,
                award_date DATE,
                start_date DATE,
                end_date DATE,
                status TEXT CHECK(status IN ('awarded', 'active', 'completed', 'audited')),
                restrictions TEXT,
                reporting_requirements TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Grant expenditure tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_expenditures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_id INTEGER NOT NULL,
                expenditure_date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                vendor TEXT,
                description TEXT NOT NULL,
                allowable INTEGER DEFAULT 1 CHECK(allowable IN (0, 1)),
                receipt_number TEXT,
                gl_entry_id INTEGER,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grant_id) REFERENCES grant_funds(id),
                FOREIGN KEY (gl_entry_id) REFERENCES general_ledger(id)
            )
        """)

        # Tax compliance tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS tax_obligations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tax_type TEXT CHECK(tax_type IN ('federal_income', 'state_income', 'payroll', 'sales', 'property', 'estimated')),
                filing_period TEXT NOT NULL,
                due_date DATE NOT NULL,
                amount_owed REAL,
                amount_paid REAL DEFAULT 0,
                status TEXT CHECK(status IN ('pending', 'filed', 'paid', 'overdue', 'amended')),
                confirmation_number TEXT,
                filed_date DATE,
                notes TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Financial statements cache
        c.execute("""
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement_type TEXT CHECK(statement_type IN ('balance_sheet', 'income_statement', 'cash_flow', 'trial_balance')),
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                statement_data TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Audit trail
        c.execute("""
            CREATE TABLE IF NOT EXISTS accounting_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                performed_by TEXT DEFAULT 'VP_Accounting_Bot',
                integrity_hash TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        self._initialize_chart_of_accounts()

    def _initialize_chart_of_accounts(self):
        """Initialize standard chart of accounts for small business"""
        c = self.conn.cursor()

        # Check if already initialized
        c.execute("SELECT COUNT(*) FROM chart_of_accounts")
        if c.fetchone()[0] > 0:
            return

        standard_accounts = [
            # Assets
            (
                "1000",
                "Cash - Operating Account",
                "asset",
                "current_asset",
                "debit",
                "Primary operating bank account",
            ),
            (
                "1010",
                "Cash - Payroll Account",
                "asset",
                "current_asset",
                "debit",
                "Dedicated payroll account",
            ),
            (
                "1020",
                "Cash - Savings Account",
                "asset",
                "current_asset",
                "debit",
                "Emergency fund and reserves",
            ),
            (
                "1100",
                "Accounts Receivable",
                "asset",
                "current_asset",
                "debit",
                "Customer invoices outstanding",
            ),
            (
                "1200",
                "Prepaid Expenses",
                "asset",
                "current_asset",
                "debit",
                "Prepaid insurance, rent, etc.",
            ),
            (
                "1500",
                "Computer Equipment",
                "asset",
                "fixed_asset",
                "debit",
                "Servers, laptops, hardware",
            ),
            (
                "1510",
                "Software & Licenses",
                "asset",
                "fixed_asset",
                "debit",
                "Capitalized software costs",
            ),
            (
                "1520",
                "Accumulated Depreciation",
                "asset",
                "fixed_asset",
                "credit",
                "Contra-asset for depreciation",
            ),
            # Liabilities
            (
                "2000",
                "Accounts Payable",
                "liability",
                "current_liability",
                "credit",
                "Vendor invoices due",
            ),
            (
                "2100",
                "Payroll Liabilities",
                "liability",
                "current_liability",
                "credit",
                "Withheld taxes, benefits",
            ),
            (
                "2110",
                "Accrued Payroll",
                "liability",
                "current_liability",
                "credit",
                "Unpaid salaries/wages",
            ),
            (
                "2200",
                "Sales Tax Payable",
                "liability",
                "current_liability",
                "credit",
                "Collected sales tax",
            ),
            (
                "2300",
                "Deferred Revenue",
                "liability",
                "current_liability",
                "credit",
                "Unearned customer payments",
            ),
            (
                "2500",
                "Notes Payable - Short Term",
                "liability",
                "current_liability",
                "credit",
                "Loans due within 1 year",
            ),
            (
                "2600",
                "Notes Payable - Long Term",
                "liability",
                "long_term_liability",
                "credit",
                "Loans due after 1 year",
            ),
            # Equity
            (
                "3000",
                "Owner Equity",
                "equity",
                "owner_equity",
                "credit",
                "Founder investment",
            ),
            (
                "3100",
                "Retained Earnings",
                "equity",
                "retained_earnings",
                "credit",
                "Cumulative profits/losses",
            ),
            (
                "3200",
                "Current Year Earnings",
                "equity",
                "current_earnings",
                "credit",
                "Year-to-date profit/loss",
            ),
            # Revenue
            (
                "4000",
                "SaaS Subscription Revenue",
                "revenue",
                "operating_revenue",
                "credit",
                "Recurring subscription fees",
            ),
            (
                "4010",
                "Professional Services Revenue",
                "revenue",
                "operating_revenue",
                "credit",
                "Implementation, consulting",
            ),
            (
                "4020",
                "Grant Revenue",
                "revenue",
                "non_operating_revenue",
                "credit",
                "Government and private grants",
            ),
            (
                "4100",
                "Interest Income",
                "revenue",
                "non_operating_revenue",
                "credit",
                "Bank interest earned",
            ),
            # Operating Expenses
            (
                "5000",
                "Salaries - Full Time",
                "expense",
                "operating_expense",
                "debit",
                "Employee salaries",
            ),
            (
                "5010",
                "Contractor Payments",
                "expense",
                "operating_expense",
                "debit",
                "1099 contractor fees",
            ),
            (
                "5020",
                "Payroll Taxes",
                "expense",
                "operating_expense",
                "debit",
                "Employer FICA, FUTA, SUTA",
            ),
            (
                "5030",
                "Employee Benefits",
                "expense",
                "operating_expense",
                "debit",
                "Health insurance, 401k match",
            ),
            (
                "5100",
                "Cloud Infrastructure - AWS",
                "expense",
                "operating_expense",
                "debit",
                "AWS hosting costs",
            ),
            (
                "5110",
                "Cloud Infrastructure - Azure",
                "expense",
                "operating_expense",
                "debit",
                "Azure hosting costs",
            ),
            (
                "5120",
                "SaaS Subscriptions",
                "expense",
                "operating_expense",
                "debit",
                "Business software tools",
            ),
            (
                "5200",
                "Marketing & Advertising",
                "expense",
                "operating_expense",
                "debit",
                "Digital ads, campaigns",
            ),
            (
                "5210",
                "Sales Commissions",
                "expense",
                "operating_expense",
                "debit",
                "Sales team commissions",
            ),
            (
                "5300",
                "Professional Fees - Legal",
                "expense",
                "operating_expense",
                "debit",
                "Attorney fees",
            ),
            (
                "5310",
                "Professional Fees - Accounting",
                "expense",
                "operating_expense",
                "debit",
                "CPA, bookkeeping",
            ),
            (
                "5320",
                "Professional Fees - Consulting",
                "expense",
                "operating_expense",
                "debit",
                "Business consultants",
            ),
            (
                "5400",
                "Office Rent",
                "expense",
                "operating_expense",
                "debit",
                "Office space lease",
            ),
            (
                "5410",
                "Utilities",
                "expense",
                "operating_expense",
                "debit",
                "Electric, internet, phone",
            ),
            (
                "5420",
                "Office Supplies",
                "expense",
                "operating_expense",
                "debit",
                "Supplies, equipment",
            ),
            (
                "5500",
                "Insurance - General Liability",
                "expense",
                "operating_expense",
                "debit",
                "Business insurance",
            ),
            (
                "5510",
                "Insurance - E&O",
                "expense",
                "operating_expense",
                "debit",
                "Errors & omissions",
            ),
            (
                "5520",
                "Insurance - Cyber",
                "expense",
                "operating_expense",
                "debit",
                "Cybersecurity insurance",
            ),
            (
                "5600",
                "Research & Development",
                "expense",
                "operating_expense",
                "debit",
                "Product development",
            ),
            (
                "5700",
                "Depreciation Expense",
                "expense",
                "operating_expense",
                "debit",
                "Asset depreciation",
            ),
            (
                "5800",
                "Interest Expense",
                "expense",
                "non_operating_expense",
                "debit",
                "Loan interest",
            ),
            (
                "5900",
                "Taxes - Income",
                "expense",
                "non_operating_expense",
                "debit",
                "Federal and state income tax",
            ),
        ]

        for acct in standard_accounts:
            data = {
                "account_number": acct[0],
                "account_name": acct[1],
                "account_type": acct[2],
                "account_subtype": acct[3],
                "normal_balance": acct[4],
                "description": acct[5],
            }

            integrity_hash = self._calculate_integrity_hash(data)

            c.execute(
                """
                INSERT INTO chart_of_accounts (
                    account_number, account_name, account_type, account_subtype,
                    normal_balance, description, integrity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (acct[0], acct[1], acct[2], acct[3], acct[4], acct[5], integrity_hash),
            )

        self.conn.commit()
        print(f"[OK] Initialized {len(standard_accounts)} standard accounts")

    def _calculate_integrity_hash(self, data: dict) -> str:
        """Calculate SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _register_with_orchestrator(self):
        """Register with Mythara Orchestrator"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/register",
                json={
                    "vp_name": "VP of Accounting",
                    "capabilities": [
                        "financial_accounting",
                        "tax_compliance",
                        "grant_tracking",
                        "financial_reporting",
                    ],
                    "status": "active",
                },
            )
            if response.status_code == 200:
                print("[OK] Registered with Mythara Orchestrator")
            else:
                print(f"[!] Orchestrator registration failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Could not connect to orchestrator (simulated): {e}")

    def record_journal_entry(
        self,
        date: str,
        account_debits: List[tuple],
        account_credits: List[tuple],
        description: str,
        reference: str = None,
    ) -> dict:
        """Record a double-entry journal entry"""
        c = self.conn.cursor()

        # Validate debits = credits
        total_debits = sum(amount for _, amount in account_debits)
        total_credits = sum(amount for _, amount in account_credits)

        if abs(total_debits - total_credits) > 0.01:
            raise ValueError(
                f"Journal entry not balanced: Debits={total_debits}, Credits={total_credits}"
            )

        entry_ids = []

        # Record debits
        for account_number, amount in account_debits:
            data = {
                "entry_date": date,
                "account_number": account_number,
                "transaction_type": "debit",
                "amount": amount,
                "description": description,
                "reference_number": reference,
            }

            integrity_hash = self._calculate_integrity_hash(data)

            c.execute(
                """
                INSERT INTO general_ledger (
                    entry_date, account_number, transaction_type, amount,
                    description, reference_number, integrity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    date,
                    account_number,
                    "debit",
                    amount,
                    description,
                    reference,
                    integrity_hash,
                ),
            )

            entry_ids.append(c.lastrowid)

        # Record credits
        for account_number, amount in account_credits:
            data = {
                "entry_date": date,
                "account_number": account_number,
                "transaction_type": "credit",
                "amount": amount,
                "description": description,
                "reference_number": reference,
            }

            integrity_hash = self._calculate_integrity_hash(data)

            c.execute(
                """
                INSERT INTO general_ledger (
                    entry_date, account_number, transaction_type, amount,
                    description, reference_number, integrity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    date,
                    account_number,
                    "credit",
                    amount,
                    description,
                    reference,
                    integrity_hash,
                ),
            )

            entry_ids.append(c.lastrowid)

        self.conn.commit()
        self._log_action(
            f"Recorded journal entry: {description}", f"Amount: ${total_debits:.2f}"
        )

        return {
            "entry_ids": entry_ids,
            "total_amount": total_debits,
            "description": description,
            "balanced": True,
        }

    def create_ap_invoice(
        self,
        vendor: str,
        invoice_number: str,
        invoice_date: str,
        due_date: str,
        amount: float,
        category: str,
        payment_terms: str = "Net 30",
    ) -> dict:
        """Create accounts payable invoice"""
        c = self.conn.cursor()

        data = {
            "vendor_name": vendor,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "amount": amount,
            "category": category,
            "payment_terms": payment_terms,
            "status": "pending",
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO accounts_payable (
                vendor_name, invoice_number, invoice_date, due_date, amount,
                status, category, payment_terms, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                vendor,
                invoice_number,
                invoice_date,
                due_date,
                amount,
                "pending",
                category,
                payment_terms,
                integrity_hash,
            ),
        )

        invoice_id = c.lastrowid
        self.conn.commit()

        self._log_action(
            f"Created AP invoice: {vendor}",
            f"Invoice: {invoice_number}, Amount: ${amount:.2f}",
        )

        return {
            "invoice_id": invoice_id,
            "vendor": vendor,
            "invoice_number": invoice_number,
            "amount": amount,
            "due_date": due_date,
            "integrity_hash": integrity_hash,
        }

    def create_ar_invoice(
        self,
        customer: str,
        invoice_number: str,
        invoice_date: str,
        due_date: str,
        amount: float,
        contract_ref: str = None,
        payment_terms: str = "Net 30",
    ) -> dict:
        """Create accounts receivable invoice"""
        c = self.conn.cursor()

        data = {
            "customer_name": customer,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "amount": amount,
            "contract_reference": contract_ref,
            "payment_terms": payment_terms,
            "status": "pending",
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO accounts_receivable (
                customer_name, invoice_number, invoice_date, due_date, amount,
                status, contract_reference, payment_terms, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                customer,
                invoice_number,
                invoice_date,
                due_date,
                amount,
                "pending",
                contract_ref,
                payment_terms,
                integrity_hash,
            ),
        )

        invoice_id = c.lastrowid
        self.conn.commit()

        # Record journal entry for AR
        self.record_journal_entry(
            invoice_date,
            [("1100", amount)],  # Debit AR
            [("4000", amount)],  # Credit Revenue
            f"Customer invoice: {customer}",
            invoice_number,
        )

        self._log_action(
            f"Created AR invoice: {customer}",
            f"Invoice: {invoice_number}, Amount: ${amount:.2f}",
        )

        return {
            "invoice_id": invoice_id,
            "customer": customer,
            "invoice_number": invoice_number,
            "amount": amount,
            "due_date": due_date,
            "integrity_hash": integrity_hash,
        }

    def track_grant_fund(
        self,
        grant_name: str,
        grantor: str,
        award_amount: float,
        award_date: str,
        start_date: str,
        end_date: str,
        restrictions: str = None,
    ) -> dict:
        """Track awarded grant funds"""
        c = self.conn.cursor()

        data = {
            "grant_name": grant_name,
            "grantor": grantor,
            "award_amount": award_amount,
            "award_date": award_date,
            "start_date": start_date,
            "end_date": end_date,
            "status": "awarded",
            "restrictions": restrictions,
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO grant_funds (
                grant_name, grantor, award_amount, award_date, start_date,
                end_date, status, restrictions, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                grant_name,
                grantor,
                award_amount,
                award_date,
                start_date,
                end_date,
                "awarded",
                restrictions,
                integrity_hash,
            ),
        )

        grant_id = c.lastrowid
        self.conn.commit()

        self._log_action(
            f"Tracked grant: {grant_name}",
            f"Grantor: {grantor}, Award: ${award_amount:,.2f}",
        )

        return {
            "grant_id": grant_id,
            "grant_name": grant_name,
            "award_amount": award_amount,
            "integrity_hash": integrity_hash,
        }

    def record_grant_expenditure(
        self,
        grant_id: int,
        date: str,
        category: str,
        amount: float,
        vendor: str,
        description: str,
        allowable: bool = True,
    ) -> dict:
        """Record expenditure against grant funds"""
        c = self.conn.cursor()

        # Verify grant exists and has budget
        c.execute(
            "SELECT amount_spent, award_amount FROM grant_funds WHERE id = ?",
            (grant_id,),
        )
        result = c.fetchone()
        if not result:
            raise ValueError(f"Grant ID {grant_id} not found")

        spent, award = result
        if spent + amount > award:
            raise ValueError(
                f"Expenditure exceeds grant budget: ${spent + amount:.2f} > ${award:.2f}"
            )

        data = {
            "grant_id": grant_id,
            "expenditure_date": date,
            "category": category,
            "amount": amount,
            "vendor": vendor,
            "description": description,
            "allowable": 1 if allowable else 0,
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO grant_expenditures (
                grant_id, expenditure_date, category, amount, vendor,
                description, allowable, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                grant_id,
                date,
                category,
                amount,
                vendor,
                description,
                1 if allowable else 0,
                integrity_hash,
            ),
        )

        exp_id = c.lastrowid

        # Update grant spent amount
        c.execute(
            "UPDATE grant_funds SET amount_spent = amount_spent + ? WHERE id = ?",
            (amount, grant_id),
        )

        self.conn.commit()

        self._log_action(
            f"Recorded grant expenditure: {category}",
            f"Grant ID: {grant_id}, Amount: ${amount:.2f}",
        )

        return {
            "expenditure_id": exp_id,
            "grant_id": grant_id,
            "amount": amount,
            "integrity_hash": integrity_hash,
        }

    def generate_balance_sheet(self, as_of_date: str) -> dict:
        """Generate balance sheet as of specific date"""
        c = self.conn.cursor()

        balance_sheet = {
            "as_of_date": as_of_date,
            "assets": {},
            "liabilities": {},
            "equity": {},
            "total_assets": 0,
            "total_liabilities": 0,
            "total_equity": 0,
        }

        # Calculate account balances
        c.execute(
            """
            SELECT coa.account_number, coa.account_name, coa.account_type, 
                   coa.normal_balance,
                   COALESCE(SUM(CASE WHEN gl.transaction_type = 'debit' THEN gl.amount ELSE -gl.amount END), 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_number = gl.account_number 
                AND gl.entry_date <= ?
            WHERE coa.account_type IN ('asset', 'liability', 'equity')
            GROUP BY coa.account_number, coa.account_name, coa.account_type, coa.normal_balance
            ORDER BY coa.account_number
        """,
            (as_of_date,),
        )

        for row in c.fetchall():
            acct_num, acct_name, acct_type, normal_bal, balance = row

            # Adjust balance based on normal balance
            if normal_bal == "credit":
                balance = -balance

            if acct_type == "asset":
                balance_sheet["assets"][acct_name] = balance
                balance_sheet["total_assets"] += balance
            elif acct_type == "liability":
                balance_sheet["liabilities"][acct_name] = balance
                balance_sheet["total_liabilities"] += balance
            elif acct_type == "equity":
                balance_sheet["equity"][acct_name] = balance
                balance_sheet["total_equity"] += balance

        return balance_sheet

    def generate_income_statement(self, start_date: str, end_date: str) -> dict:
        """Generate income statement for date range"""
        c = self.conn.cursor()

        income_stmt = {
            "period_start": start_date,
            "period_end": end_date,
            "revenue": {},
            "expenses": {},
            "total_revenue": 0,
            "total_expenses": 0,
            "net_income": 0,
        }

        # Calculate revenue and expense balances
        c.execute(
            """
            SELECT coa.account_number, coa.account_name, coa.account_type,
                   COALESCE(SUM(CASE WHEN gl.transaction_type = 'credit' THEN gl.amount ELSE -gl.amount END), 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_number = gl.account_number
                AND gl.entry_date BETWEEN ? AND ?
            WHERE coa.account_type IN ('revenue', 'expense')
            GROUP BY coa.account_number, coa.account_name, coa.account_type
            ORDER BY coa.account_number
        """,
            (start_date, end_date),
        )

        for row in c.fetchall():
            acct_num, acct_name, acct_type, balance = row

            if acct_type == "revenue":
                income_stmt["revenue"][acct_name] = balance
                income_stmt["total_revenue"] += balance
            elif acct_type == "expense":
                income_stmt["expenses"][
                    acct_name
                ] = -balance  # Expenses displayed as positive
                income_stmt["total_expenses"] += -balance

        income_stmt["net_income"] = (
            income_stmt["total_revenue"] - income_stmt["total_expenses"]
        )

        return income_stmt

    def generate_accounting_report(self) -> str:
        """Generate comprehensive accounting report"""
        c = self.conn.cursor()

        today = datetime.now().date()

        # Get AP summary
        c.execute(
            'SELECT COUNT(*), COALESCE(SUM(amount - amount_paid), 0) FROM accounts_payable WHERE status != "paid"'
        )
        ap_count, ap_total = c.fetchone()

        # Get AR summary
        c.execute(
            'SELECT COUNT(*), COALESCE(SUM(amount - amount_received), 0) FROM accounts_receivable WHERE status != "paid"'
        )
        ar_count, ar_total = c.fetchone()

        # Get overdue AP
        c.execute(
            'SELECT COUNT(*) FROM accounts_payable WHERE due_date < ? AND status != "paid"',
            (today,),
        )
        ap_overdue = c.fetchone()[0]

        # Get overdue AR
        c.execute(
            'SELECT COUNT(*) FROM accounts_receivable WHERE due_date < ? AND status != "paid"',
            (today,),
        )
        ar_overdue = c.fetchone()[0]

        # Get grant tracking
        c.execute(
            'SELECT COUNT(*), COALESCE(SUM(award_amount), 0), COALESCE(SUM(amount_spent), 0) FROM grant_funds WHERE status = "active"'
        )
        grant_count, grant_total, grant_spent = c.fetchone()

        # Get tax obligations
        c.execute(
            'SELECT COUNT(*) FROM tax_obligations WHERE status IN ("pending", "overdue")'
        )
        tax_pending = c.fetchone()[0]

        # Get recent GL entries
        c.execute("""
            SELECT entry_date, account_number, transaction_type, amount, description
            FROM general_ledger
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_entries = c.fetchall()

        report = f"""
================================================================================
MYTHARA VP OF ACCOUNTING - FINANCIAL REPORT
================================================================================

ACCOUNTS PAYABLE (Money We Owe):
   Outstanding Invoices: {ap_count}
   Total Amount Due: ${ap_total:,.2f}
   Overdue Invoices: {ap_overdue}

ACCOUNTS RECEIVABLE (Money Owed to Us):
   Outstanding Invoices: {ar_count}
   Total Amount Due: ${ar_total:,.2f}
   Overdue Invoices: {ar_overdue}

GRANT FUND TRACKING:
   Active Grants: {grant_count or 0}
   Total Grant Funds Awarded: ${grant_total:,.2f}
   Total Grant Funds Spent: ${grant_spent:,.2f}
   Remaining Grant Budget: ${(grant_total - grant_spent):,.2f}

TAX COMPLIANCE:
   Pending Tax Filings: {tax_pending or 0}

RECENT GENERAL LEDGER ENTRIES:
"""

        for entry in recent_entries:
            date, acct, trans_type, amt, desc = entry
            report += (
                f"\n   {date} | {acct} | {trans_type.upper()} ${amt:,.2f} | {desc}"
            )

        report += "\n\n" + "=" * 80 + "\n"

        return report

    def _log_action(self, action: str, details: str = None):
        """Log action to audit trail"""
        c = self.conn.cursor()

        data = {
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO accounting_audit (action, details, integrity_hash)
            VALUES (?, ?, ?)
        """,
            (action, details, integrity_hash),
        )

        self.conn.commit()


if __name__ == "__main__":
    print("Initializing Mythara VP of Accounting...")
    print("=" * 80)

    vp = MytharaAccountingVP()

    # Demo workflow
    print("\n[DEMO] Recording customer invoice (AR)\n")
    ar_invoice = vp.create_ar_invoice(
        "Microsoft Corporation",
        "INV-2025-001",
        "2025-11-01",
        "2025-12-01",
        150000.00,
        "MSA-2025-001",
        "Net 30",
    )
    print(
        f"[OK] Created AR invoice: {ar_invoice['customer']} - ${ar_invoice['amount']:,.2f}"
    )

    print("\n[DEMO] Recording vendor invoice (AP)\n")
    ap_invoice = vp.create_ap_invoice(
        "AWS - Amazon Web Services",
        "AWS-NOV-2025",
        "2025-11-01",
        "2025-11-15",
        8500.00,
        "Cloud Infrastructure",
        "Net 15",
    )
    print(
        f"[OK] Created AP invoice: {ap_invoice['vendor']} - ${ap_invoice['amount']:,.2f}"
    )

    print("\n[DEMO] Tracking grant fund\n")
    grant = vp.track_grant_fund(
        "NSF SBIR Phase II - Cybersecurity Infrastructure",
        "National Science Foundation",
        750000.00,
        "2025-12-15",
        "2026-01-01",
        "2027-12-31",
        "Must be used for infrastructure and R&D only",
    )
    print(f"[OK] Tracked grant: {grant['grant_name']} - ${grant['award_amount']:,.2f}")

    print("\n[DEMO] Recording grant expenditure\n")
    grant_exp = vp.record_grant_expenditure(
        grant["grant_id"],
        "2026-01-15",
        "GPU Servers",
        50000.00,
        "Dell Technologies",
        "4x NVIDIA A100 GPU servers for AI/ML processing",
    )
    print(f"[OK] Recorded grant expenditure: GPU Servers - ${grant_exp['amount']:,.2f}")

    print("\n[DEMO] Recording payroll journal entry\n")
    payroll = vp.record_journal_entry(
        "2025-11-15",
        [("5000", 25000.00), ("5020", 1912.50)],  # Debit: Salaries + Payroll Tax
        [("1000", 23087.50), ("2100", 3825.00)],  # Credit: Cash + Payroll Liabilities
        "November 2025 payroll - salaried employees",
        "PAYROLL-NOV-2025",
    )
    print(f"[OK] Recorded payroll journal entry: ${payroll['total_amount']:,.2f}")

    # Generate reports
    print("\n" + vp.generate_accounting_report())

    print("\n[OK] VP of Accounting demo complete!")
    print("=" * 80)
