# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Windows Task Scheduler Setup for Weekly Analytics Report

Automatically runs weekly_analytics_report.py every Sunday at 6:00 PM MT
Sends PDF report to Herbievelezjr@gmail.com
"""

SETUP_INSTRUCTIONS = """
================================================================================
📅 SCHEDULE WEEKLY ANALYTICS REPORT (Windows Task Scheduler)
================================================================================

1. Open Task Scheduler:
   - Press Win+R, type 'taskschd.msc', press Enter

2. Create Basic Task:
   - Click "Create Basic Task..." in right panel
   - Name: "Mythara Weekly Analytics Report"
   - Description: "Automated weekly analytics report for Mythara Engine"
   - Click Next

3. Trigger:
   - Select "Weekly"
   - Click Next
   - Start date: Today
   - Start time: 18:00 (6:00 PM)
   - Recur every: 1 week
   - Check: Sunday
   - Click Next

4. Action:
   - Select "Start a program"
   - Click Next
   - Program/script: Browse to python.exe (e.g., C:\\Python311\\python.exe)
   - Add arguments: "C:\\path\\to\\Mythara_Archive\\Commercial\\weekly_analytics_report.py"
   - Start in: C:\\path\\to\\Mythara_Archive\\Commercial
   - Click Next

5. Finish:
   - Review settings
   - Check "Open the Properties dialog"
   - Click Finish

6. Additional Settings (in Properties dialog):
   - General tab:
     - Check "Run whether user is logged on or not"
     - Check "Run with highest privileges"
   - Conditions tab:
     - Uncheck "Start the task only if the computer is on AC power"
   - Settings tab:
     - Check "Run task as soon as possible after a scheduled start is missed"
   - Click OK

7. Test:
   - Right-click the task → Run
   - Check email for PDF report

💡 To Test Now:
   - Right-click task in Task Scheduler
   - Click "Run"
   - Check Commercial folder for PDF

================================================================================
"""

import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Schedule the weekly analytics report (see instructions)")
    parser.add_argument('--show-instructions', action='store_true', 
                       help='Print setup instructions and exit')
    args = parser.parse_args()
    
    if args.show_instructions:
        print(SETUP_INSTRUCTIONS)
        return
    
    print("This script displays setup instructions for Task Scheduler.")
    print("Run with --show-instructions to see full setup guide.")

if __name__ == "__main__":
    main()
