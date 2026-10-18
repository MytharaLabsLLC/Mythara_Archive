# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Grant Writer Bot
Execute via Windows Task Scheduler: Weekly Monday 6:00 AM
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.source_proprietary.mythara_grant_writer_bot import MytharaGrantWriterBot

if __name__ == "__main__":
    print("Starting Mythara Grant Writer Bot...")
    bot = MytharaGrantWriterBot()
    
    # Generate weekly grant report
    report = bot.generate_grant_report()
    print(report)
    
    print("\nMythara Grant Writer Bot execution complete.")
