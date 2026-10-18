import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Comprehensive demo of contractor system with authentication
Shows full flow: onboarding -> login (2-step) -> task assignment -> completion -> payout
"""

from mythara_contractor_manager import MytharaContractorManager
from mythara_contractor_auth import ContractorAuth

def main():
    print('\n' + '='*70)
    print('MYTHARA CONTRACTOR SYSTEM - FULL AUTHENTICATION DEMO')
    print('='*70)
    
    cm = MytharaContractorManager()
    auth = ContractorAuth()
    
    # ========== 1. ONBOARD CONTRACTOR WITH AUTH ==========
    print('\n[1] ONBOARDING CONTRACTOR')
    print('-'*70)
    
    contractor_email = 'sarah@contractor.example.com'
    # QUICKFIX FIX: Moved to environment variable (CWE-798)
    contractor_password = os.getenv("CONTRACTOR_PASSWORD", "")  # Set via environment
    
    print(f'Onboarding: {contractor_email}')
    cm.onboard_contractor(
        email=contractor_email,
        name='Sarah Chen',
        hourly_rate=75.0,
        market_rate_factor=1.08,  # 8% market adjustment
        password=contractor_password
    )
    print('[OK] Contractor onboarded with auth credentials')
    
    # ========== 2. LOGIN - STEP 1 (EMAIL + PASSWORD) ==========
    print('\n[2] LOGIN - STEP 1 (Email + Password)')
    print('-'*70)
    
    step1_result = auth.login_step1(contractor_email, contractor_password)
    
    if not step1_result['success']:
        print(f"[ERROR] Login failed: {step1_result['error']}")
        return
    
    print(f"[OK] Credentials verified")
    print(f"[OK] OTP sent to {contractor_email}")
    print(f"    OTP ID: {step1_result['otp_id']}")
    
    # ========== 3. LOGIN - STEP 2 (OTP VERIFICATION) ==========
    print('\n[3] LOGIN - STEP 2 (OTP Verification)')
    print('-'*70)
    
    # In real scenario, contractor enters OTP from email
    # For demo, we'll extract it from database (simulating contractor checking email)
    import sqlite3
    conn = sqlite3.connect('mythara_contractor.db')
    c = conn.cursor()
    c.execute('SELECT otp_code FROM auth_otp WHERE otp_id = ?', (step1_result['otp_id'],))
    otp_code = c.fetchone()[0]
    conn.close()
    
    print(f"Contractor enters OTP: {otp_code} (from email)")
    
    step2_result = auth.login_step2(step1_result['otp_id'], otp_code)
    
    if not step2_result['success']:
        print(f"[ERROR] OTP verification failed: {step2_result['error']}")
        return
    
    session_token = step2_result['session_token']
    print(f"[OK] Login successful!")
    print(f"    Session token: {session_token[:30]}...")
    print(f"    Expires: {step2_result['expires_at']}")
    
    # ========== 4. VALIDATE SESSION ==========
    print('\n[4] SESSION VALIDATION')
    print('-'*70)
    
    validation = auth.validate_session(session_token)
    if validation['valid']:
        print(f"[OK] Session valid for: {validation['email']}")
    else:
        print(f"[ERROR] Session invalid: {validation['error']}")
        return
    
    # ========== 5. ASSIGN TASKS (AUTHENTICATED) ==========
    print('\n[5] TASK ASSIGNMENT')
    print('-'*70)
    
    task1 = cm.assign_task(
        contractor_email=contractor_email,
        task_id='TASK-2025-001',
        description='Build API integration for payment gateway',
        estimated_hours=8.0
    )
    print(f"[OK] Assigned: {task1['task_id']} ({task1['estimated_hours']} hours)")
    
    task2 = cm.assign_task(
        contractor_email=contractor_email,
        task_id='TASK-2025-002',
        description='Create contractor portal UI components',
        estimated_hours=12.0
    )
    print(f"[OK] Assigned: {task2['task_id']} ({task2['estimated_hours']} hours)")
    
    # ========== 6. RECORD COMPLETIONS WITH PERFORMANCE SCORES ==========
    print('\n[6] TASK COMPLETION & PAYOUT CALCULATION')
    print('-'*70)
    
    print('\nTask 1 completion (Performance: 95/100)')
    completion1 = cm.record_task_completion(
        task_id='TASK-2025-001',
        performance_score=95,  # Excellent work
        actual_hours=7.5  # Under estimated time
    )
    print(f"  Hours: 7.5 (saved 0.5h)")
    print(f"  Performance: 95/100 (multiplier: {completion1['payout'] / (7.5 * 75 * 1.08):.3f})")
    print(f"  Payout: ${completion1['payout']:.2f}")
    
    print('\nTask 2 completion (Performance: 72/100)')
    completion2 = cm.record_task_completion(
        task_id='TASK-2025-002',
        performance_score=72,  # Slightly below baseline
        actual_hours=13.0  # Slightly over estimate
    )
    print(f"  Hours: 13.0 (over by 1h)")
    print(f"  Performance: 72/100 (multiplier: {completion2['payout'] / (13.0 * 75 * 1.08):.3f})")
    print(f"  Payout: ${completion2['payout']:.2f}")
    
    # ========== 7. AGGREGATE PAYOUTS ==========
    print('\n[7] PAYOUT AGGREGATION')
    print('-'*70)
    
    payouts = cm.aggregate_payouts()
    for p in payouts:
        print(f"Contractor: {p['contractor_email']}")
        print(f"Total payout: ${p['amount']:.2f}")
    
    # ========== 8. LOGOUT ==========
    print('\n[8] LOGOUT')
    print('-'*70)
    
    logout_result = auth.logout(session_token)
    if logout_result['success']:
        print('[OK] Session revoked - contractor logged out')
    
    # Verify session is now invalid
    validation2 = auth.validate_session(session_token)
    print(f"[VERIFY] Session now invalid: {not validation2['valid']}")
    
    # ========== 9. PASSWORD RESET FLOW ==========
    print('\n[9] PASSWORD RESET DEMO')
    print('-'*70)
    
    print('Contractor requests password reset...')
    reset_request = auth.request_password_reset(contractor_email)
    if reset_request['success']:
        print(f"[OK] Reset code sent to {contractor_email}")
        
        # Extract OTP for demo
        conn = sqlite3.connect('mythara_contractor.db')
        c = conn.cursor()
        c.execute('SELECT otp_code FROM auth_otp WHERE otp_id = ?', (reset_request['otp_id'],))
        reset_code = c.fetchone()[0]
        conn.close()
        
        print(f"Contractor enters reset code: {reset_code}")
        
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        new_password = os.getenv("NEW_PASSWORD", "")  # Set via environment
        reset_result = auth.reset_password(
            otp_id=reset_request['otp_id'],
            otp_code=reset_code,
            new_password=new_password
        )
        
        if reset_result['success']:
            print('[OK] Password reset successfully')
            
            # Verify new password works
            print('\nTesting login with new password...')
            test_login = auth.login_step1(contractor_email, new_password)
            if test_login['success']:
                print('[OK] New password verified - can login')
    
    # ========== 10. AUDIT TRAIL ==========
    print('\n[10] AUDIT TRAIL (Last 15 events)')
    print('-'*70)
    
    audits = cm.generate_audit_report(15)
    for i, a in enumerate(audits[:15], 1):
        print(f"{i:2}. [{a['created_at'][:19]}] {a['entity']:12} {a['action']}")
    
    print('\n' + '='*70)
    print('DEMO COMPLETE')
    print('='*70)
    print('\nSummary:')
    print('  - Contractor onboarded with secure auth (bcrypt hashed)')
    print('  - 2-step login with email OTP (10min expiry)')
    print('  - Session token issued (24h expiry)')
    print('  - Tasks assigned and completed with performance scoring')
    print('  - Payouts calculated with market adjustment + performance multiplier')
    print('  - Password reset flow with OTP')
    print('  - All actions audited with integrity hashes')
    print('\nDatabase: mythara_contractor.db')
    print('Tables: contractors, contractor_auth, auth_otp, auth_sessions,')
    print('        tasks, payouts, audits, auth_audit')
    print('='*70 + '\n')


if __name__ == '__main__':
    main()
