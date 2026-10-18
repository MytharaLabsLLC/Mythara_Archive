# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Researcher Bot
Execute via Windows Task Scheduler: Daily 9:00 AM
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.source_proprietary.mythara_researcher_bot import MytharaResearcherBot

if __name__ == "__main__":
    print("Starting Mythara Researcher Bot...")
    bot = MytharaResearcherBot()
    
    # Generate daily research report
    report = bot.generate_research_report()
    print(report)
    
    print("\nMythara Researcher Bot execution complete.")
