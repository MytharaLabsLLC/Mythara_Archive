# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Support Chat Bot
Execute via Windows Task Scheduler: Every 30 minutes
"""

import sys
import os

# Add Commercial directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMERCIAL_PATH = os.path.join(CURRENT_DIR, "Commercial")
if COMMERCIAL_PATH not in sys.path:
    sys.path.insert(0, COMMERCIAL_PATH)

from mythara_support_bot import MytharaSupportBot

if __name__ == "__main__":
    print("Starting Mythara Support Bot...")
    bot = MytharaSupportBot()
    
    # Check for new tickets and respond
    report = bot.generate_support_report()
    print(report)
    
    print("\nMythara Support Bot execution complete.")
