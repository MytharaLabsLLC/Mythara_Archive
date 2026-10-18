# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara DevSecOps VP
Execute via Windows Task Scheduler: Hourly
"""

import sys
import os

# Add Commercial directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMERCIAL_PATH = os.path.join(CURRENT_DIR, "Commercial")
if COMMERCIAL_PATH not in sys.path:
    sys.path.insert(0, COMMERCIAL_PATH)

from mythara_devsecops_vp import MytharaDevSecOpsVP

if __name__ == "__main__":
    print("Starting Mythara DevSecOps VP...")
    vp = MytharaDevSecOpsVP()
    
    # Generate security report
    report = vp.generate_security_report()
    print(report)
    
    print("\nMythara DevSecOps VP execution complete.")
