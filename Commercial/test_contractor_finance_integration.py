# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Test integration between Contractor Manager and Finance VP
Shows contractor payouts being recorded as expenses
"""

from mythara_contractor_manager import MytharaContractorManager
from mythara_finance_vp import MytharaFinanceVP

def main():
    print('\n' + '='*70)
    print('CONTRACTOR-FINANCE INTEGRATION TEST')
    print('='*70)
    
    cm = MytharaContractorManager()
    finance = MytharaFinanceVP()
    
    # Onboard contractor
    print('\n[1] Onboarding contractor...')
    cm.onboard_contractor('bob@contractor.com', 'Bob Martinez', 80.0, market_rate_factor=1.10)
    
    # Assign and complete task
    print('\n[2] Assigning task...')
    cm.assign_task('bob@contractor.com', 'TASK-INT-001', 'API integration testing', estimated_hours=10)
    
    print('\n[3] Recording completion...')
    completion = cm.record_task_completion('TASK-INT-001', 88, actual_hours=9.5)
    print(f"    Payout calculated: ${completion['payout']:.2f}")
    
    # Get payout ID
    import sqlite3
    conn = sqlite3.connect('mythara_contractor.db')
    c = conn.cursor()
    c.execute('SELECT payout_id FROM payouts WHERE contractor_email = ? AND status = ?', ('bob@contractor.com', 'pending'))
    payout_id = c.fetchone()[0]
    conn.close()
    
    # Finalize payout (this triggers Finance VP expense recording)
    print('\n[4] Finalizing payout (triggers Finance VP integration)...')
    result = cm.finalize_payout(payout_id)
    print(f"    Payout finalized: {result['status']}")
    
    # Check Finance VP metrics
    print('\n[5] Finance VP Metrics (after contractor expense)...')
    metrics = finance.calculate_metrics()
    print(f"    Contractor Expenses (Pending): ${metrics['contractor_expenses_pending']:,.2f}")
    print(f"    Contractor Expenses (Paid): ${metrics['contractor_expenses_paid']:,.2f}")
    print(f"    Total Contractor Costs: ${metrics['contractor_expenses_total']:,.2f}")
    print(f"    Net Margin: ${metrics['net_margin']:,.2f}")
    
    # Generate Finance VP report
    print('\n[6] Full Finance VP Report...')
    print(finance.generate_finance_report())
    
    print('='*70)
    print('[OK] Integration test complete')
    print('='*70 + '\n')

if __name__ == '__main__':
    main()
