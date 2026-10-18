# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner for Mythara Contractor Manager - test and demo
"""
from mythara_contractor_manager import MytharaContractorManager

if __name__ == '__main__':
    print('\n[Runner] Starting Contractor Manager demo...')
    cm = MytharaContractorManager()

    # Onboard a contractor (idempotent)
    print('[Runner] Onboarding contractor: alice@example.com')
    cm.onboard_contractor('alice@example.com', 'Alice Rivera', 60.0, market_rate_factor=1.05)

    # Assign a few tasks
    print('[Runner] Assigning tasks...')
    cm.assign_task('alice@example.com', 'CT-001', 'Create onboarding docs', estimated_hours=3)
    cm.assign_task('alice@example.com', 'CT-002', 'Implement payment adapter', estimated_hours=6)

    # Record completions with different scores
    print('[Runner] Recording completions...')
    res1 = cm.record_task_completion('CT-001', 90, actual_hours=2.5)
    res2 = cm.record_task_completion('CT-002', 70, actual_hours=6.5)

    print('[Runner] Payouts created:')
    print('  - CT-001 payout:', round(res1['payout'], 2))
    print('  - CT-002 payout:', round(res2['payout'], 2))

    # Aggregate pending payouts for last 7 days
    print('\n[Runner] Aggregated payouts (last 7 days):')
    agg = cm.aggregate_payouts()
    for p in agg:
        print('  -', p['contractor_email'], '$', round(p['amount'], 2))

    # Show recent audits
    print('\n[Runner] Recent audits:')
    audits = cm.generate_audit_report(10)
    for a in audits[:5]:
        print('  -', a['created_at'], a['entity'], a['action'])

    print('\n[Runner] Demo complete.')
