# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Finance VP
Executes daily at 7am to process revenue, renewals, and generate forecasts
"""

from mythara_finance_vp import MytharaFinanceVP
from datetime import datetime

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"FINANCE VP DAILY RUN - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print(f"{'='*60}\n")
    
    finance = MytharaFinanceVP()
    
    print("[CHECK] Processing payment retries...")
    retries = finance.process_payment_retries()
    print(f"   [OK] Processed {len(retries)} retry attempt(s)")
    
    print("\n[CHECK] Calculating financial metrics...")
    metrics = finance.calculate_metrics()
    print(f"   MRR: ${metrics['mrr']:,.2f}")
    print(f"   ARR: ${metrics['arr']:,.2f}")
    print(f"   Active Subscriptions: {metrics['active_subscriptions']}")
    
    print("\n[CHECK] Generating finance report...")
    report = finance.generate_finance_report()
    print(report)
    
    print(f"{'='*60}")
    print("[OK] Finance VP run complete")
    print(f"{'='*60}\n")
