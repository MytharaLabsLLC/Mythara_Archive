# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner for the Affiliate Tracker.

Approves pending affiliate payouts that cleared the $50 threshold and
prints the program report.

Honest contract: APPROVAL is not PAYMENT. This bot moves no money —
there is no PayPal/Stripe API here. Every "approved" payout still
needs Herb to send it manually via PayPal. Status: approved_for_payout.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_affiliate_bot import AutonomousAffiliateBot


def main() -> None:
    bot = AutonomousAffiliateBot()

    print("Mythara Affiliate Tracker - payout approval run")
    print("=" * 60)

    print("\nApproving payouts at/above the $50 threshold...")
    print("(Approval only — Herb sends each payout manually via PayPal.)")
    payouts = bot.process_weekly_payouts()

    if payouts:
        print(f"\nApproved {len(payouts)} payout(s):")
        for payout_data in payouts:
            payout = payout_data["payout"]
            print(f"\n   Affiliate: {payout['affiliate_email']}")
            print(f"   Amount: ${payout['amount']:.2f}")
            print(f"   Commissions: {len(payout['commissions_included'])}")
            print(f"   Status: {payout['status']}")
            print(f"   ACTION REQUIRED: {payout['payout_note']}")
    else:
        print("\nNo payouts ready (minimum $50 not reached, or none pending).")

    print("\nAffiliate Program Stats:")
    report = bot.get_affiliate_report()
    print(f"   Total Affiliates: {report['total_affiliates']}")
    print(f"   Active Affiliates: {report['active_affiliates']}")
    print(f"   Total Sales Generated: ${report['total_sales_generated']:,.2f}")
    print(f"   Total Commissions Earned: ${report['total_commissions_earned']:,.2f}")
    print(f"   Pending Payouts: ${report['pending_payouts']:,.2f}")

    if report["top_affiliates"]:
        print("\nTop Affiliates:")
        for i, aff in enumerate(report["top_affiliates"][:3], 1):
            print(f"   {i}. {aff['name']}: ${aff['earnings']:,.2f}")

    print("\n" + "=" * 60)
    print("Done. Ledger saved; money moves only when Herb sends it.")


if __name__ == "__main__":
    main()
