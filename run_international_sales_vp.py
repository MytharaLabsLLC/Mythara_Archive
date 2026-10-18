# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara International Sales VP
Execute via Windows Task Scheduler: Daily 9:00 AM
"""

import sys
import os

# Add Commercial directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMERCIAL_PATH = os.path.join(CURRENT_DIR, "Commercial")
if COMMERCIAL_PATH not in sys.path:
    sys.path.insert(0, COMMERCIAL_PATH)

from mythara_international_sales_vp import MytharaInternationalSalesVP

if __name__ == "__main__":
    print("Starting Mythara International Sales VP...")
    vp = MytharaInternationalSalesVP()
    
    # Generate daily international sales report
    report = vp.generate_regional_report()
    print(report)
    
    print("\nMythara International Sales VP execution complete.")
