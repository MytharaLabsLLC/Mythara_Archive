# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Customer Success VP
Executes daily at 10am to update health scores, send onboarding, identify at-risk customers
"""

from mythara_customer_success_vp import MytharaCustomerSuccessVP
from datetime import datetime

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"CUSTOMER SUCCESS VP DAILY RUN - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print(f"{'='*60}\n")
    
    cs = MytharaCustomerSuccessVP()
    
    print("[CHECK] Sending onboarding check-ins...")
    checkins = cs.send_onboarding_checkins()
    print(f"   [OK] Sent {len(checkins)} check-in(s)")
    
    print("\n[CHECK] Identifying at-risk customers...")
    at_risk = cs.identify_at_risk_customers()
    if at_risk:
        print(f"   [WARN] Found {len(at_risk)} at-risk customer(s)")
        for customer in at_risk[:5]:  # Show top 5
            print(f"      - {customer['customer_email']}: {customer['health_score']:.0f}/100")
    else:
        print(f"   [OK] No at-risk customers")
    
    print("\n[CHECK] Generating customer success report...")
    report = cs.generate_customer_success_report()
    print(report)
    
    print(f"{'='*60}")
    print("[OK] Customer Success VP run complete")
    print(f"{'='*60}\n")
