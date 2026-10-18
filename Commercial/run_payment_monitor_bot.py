# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Payment Monitor Bot.
Checks Loyverse for new receipts and prints alerts for notable ones.

Honest contract: alerts PRINT HERE. No email/SMS is configured —
send_alert() is print-only. The Loyverse read path is real
(GET api.loyverse.com/v1.0/receipts); everything after the fetch is
local analysis.
"""

import sys
import os

# Add parent directory to path to import mythara_ai_team_free
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mythara_ai_team_free import MytharaAITeam

def main():
    team = MytharaAITeam()
    
    # Run payment monitoring
    print("💰 Running Payment Monitor Bot...")
    result = team.run_payment_monitor()
    
    print("\n" + "="*60)
    print("PAYMENT MONITOR REPORT")
    print("="*60)
    print(result)
    print("="*60)
    print("\nNOTE: alerts above are print-only — no email/SMS is configured.")
    print("Loyverse token: read from LOYVERSE_ACCESS_TOKEN env var. "
          "A hardcoded fallback exists in mythara_ai_team_free.py — "
          "replace it before any production use.")

if __name__ == "__main__":
    main()
