# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara SBGA Integration Bot
Execute via Windows Task Scheduler: Daily 10:00 AM
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.source_proprietary.mythara_sbga_bot import MytharaSBGABot

if __name__ == "__main__":
    print("Starting Mythara SBGA Integration Bot...")
    bot = MytharaSBGABot()
    
    # Discover new grants from Grants.gov API
    print("\n[CHECK] Fetching opportunities from Grants.gov API...")
    grants = bot.discover_sbga_grants()
    print(f"[OK] Discovered {len(grants)} grant opportunities")
    
    # Generate daily SBGA report
    report = bot.generate_sbga_report()
    print(report)
    
    print("\nMythara SBGA Integration Bot execution complete.")
