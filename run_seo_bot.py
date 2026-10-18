# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara SEO Master Bot
Execute via Windows Task Scheduler: Weekly Sunday 12:00 AM
"""

import sys
import os

# Add Commercial directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMERCIAL_PATH = os.path.join(CURRENT_DIR, "Commercial")
if COMMERCIAL_PATH not in sys.path:
    sys.path.insert(0, COMMERCIAL_PATH)

from mythara_seo_bot import MytharaSEOMasterBot

if __name__ == "__main__":
    print("Starting Mythara SEO Master Bot...")
    bot = MytharaSEOMasterBot()
    
    # Generate weekly SEO report
    report = bot.generate_seo_report()
    print(report)
    
    print("\nMythara SEO Master Bot execution complete.")
