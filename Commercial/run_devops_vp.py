# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara DevOps VP Bot
Monitors infrastructure and auto-remediates issues
"""

from mythara_devops_vp import MytharaDevOpsVP
from datetime import datetime

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA DEVOPS VP - INFRASTRUCTURE MONITOR")
    print(f"Run Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*60)
    
    # Initialize DevOps VP
    devops = MytharaDevOpsVP()
    
    # Check system health
    print("\n[CHECK] System health...")
    health = devops.check_system_health()
    
    # Check running bots
    print("[CHECK] Bot processes...")
    bots = devops.check_bot_processes()
    
    # Check orchestrator
    print("[CHECK] Orchestrator...")
    try:
        orch = devops.check_orchestrator_health()
        if orch['status'] != 'healthy':
            print("\n[CRITICAL] Orchestrator unhealthy - attempting restart...")
            issue = {'type': 'orchestrator_down', 'severity': 'critical'}
            result = devops.auto_remediate(issue)
            status = "[OK] Restarted" if result['success'] else "[FAIL]"
            print(f"   Orchestrator: {status}")
    except Exception as e:
        print(f"[WARN] Orchestrator check failed: {str(e)[:80]}")
        print("   Continuing with infrastructure check...")
    
    # Auto-remediate critical issues
    if health['issues']:
        print(f"\n[WARN] {len(health['issues'])} issues detected - auto-remediating...")
        for issue in health['issues']:
            if issue['severity'] in ['high', 'critical']:
                result = devops.auto_remediate(issue)
                status = "[OK] Fixed" if result['success'] else "[FAIL]"
                print(f"   {issue['type']}: {status}")
    
    # Generate and print report
    print("\n" + "="*60)
    report = devops.generate_devops_report()
    print(report)
    
    print("="*60)
    print("[OK] DevOps VP check complete")
    print(f"Next run: Schedule hourly via Windows Task Scheduler")
