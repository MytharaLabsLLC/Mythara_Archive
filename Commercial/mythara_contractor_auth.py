# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara Contractor Authentication System
- Email-based login (email = ID)
- Password hashing with bcrypt
- Multi-step verification via email OTP (6-digit code)
- Session token generation
- Integration with contractor manager

Flow:
1. Contractor requests login with email + password
2. System validates credentials, generates 6-digit OTP, sends to email (simulated print)
3. Contractor submits OTP code
4. System validates OTP, issues session token
5. Contractor uses session token for authenticated API calls

Security:
- Passwords hashed with bcrypt (12 rounds)
- OTP expires after 10 minutes
- Session tokens expire after 24 hours
- All auth events audited with integrity hashes
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import bcrypt

DB_PATH = "mythara_contractor.db"


def _hash_record(obj: Dict[str, Any]) -> str:
    s = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()[:24]


class ContractorAuth:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_auth_tables()
    
    def _init_auth_tables(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Auth credentials table
        c.execute('''
            CREATE TABLE IF NOT EXISTS contractor_auth (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT,
                last_login TEXT,
                integrity_hash TEXT,
                FOREIGN KEY(email) REFERENCES contractors(email)
            )
        ''')
        
        # OTP table (multi-step verification)
        c.execute('''
            CREATE TABLE IF NOT EXISTS auth_otp (
                otp_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                otp_code TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                verified_at TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Session tokens table
        c.execute('''
            CREATE TABLE IF NOT EXISTS auth_sessions (
                session_token TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER DEFAULT 0,
                integrity_hash TEXT,
                FOREIGN KEY(email) REFERENCES contractors(email)
            )
        ''')
        
        # Auth audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS auth_audit (
                audit_id TEXT PRIMARY KEY,
                email TEXT,
                action TEXT NOT NULL,
                status TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _audit_auth(self, email: Optional[str], action: str, status: str, ip_address: str = "127.0.0.1", user_agent: str = "MytharaContractorPortal/1.0"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        created_at = datetime.now().isoformat()
        record = {
            'email': email,
            'action': action,
            'status': status,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': created_at
        }
        integrity_hash = _hash_record(record)
        audit_id = hashlib.sha256(f"{email}{action}{created_at}".encode()).hexdigest()[:16]
        
        c.execute('''INSERT INTO auth_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            audit_id, email, action, status, ip_address, user_agent, created_at, integrity_hash
        ))
        conn.commit()
        conn.close()
    
    # ---------------------- Registration ----------------------
    def register_contractor(self, email: str, password: str) -> Dict[str, Any]:
        """Register contractor auth credentials (called during onboarding)"""
        # Hash password with bcrypt (12 rounds)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        
        created_at = datetime.now().isoformat()
        record = {
            'email': email,
            'created_at': created_at
        }
        integrity_hash = _hash_record(record)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO contractor_auth VALUES (?, ?, ?, ?, ?, ?)''', (
                email, password_hash, 1, created_at, None, integrity_hash
            ))
            conn.commit()
            self._audit_auth(email, 'register', 'success')
            return {'email': email, 'registered': True}
        except sqlite3.IntegrityError:
            self._audit_auth(email, 'register', 'duplicate')
            return {'email': email, 'registered': False, 'error': 'Already registered'}
        finally:
            conn.close()
    
    # ---------------------- Login (Step 1) ----------------------
    def login_step1(self, email: str, password: str) -> Dict[str, Any]:
        """Validate email+password, generate OTP, return OTP ID"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check credentials
        c.execute('SELECT password_hash, enabled FROM contractor_auth WHERE email = ?', (email,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            self._audit_auth(email, 'login_step1', 'invalid_email')
            return {'success': False, 'error': 'Invalid credentials'}
        
        password_hash, enabled = row
        
        if not enabled:
            conn.close()
            self._audit_auth(email, 'login_step1', 'account_disabled')
            return {'success': False, 'error': 'Account disabled'}
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            conn.close()
            self._audit_auth(email, 'login_step1', 'invalid_password')
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Generate 6-digit OTP
        otp_code = f"{secrets.randbelow(1000000):06d}"
        otp_id = hashlib.sha256(f"{email}{otp_code}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        record = {
            'otp_id': otp_id,
            'email': email,
            'otp_code': otp_code,
            'created_at': created_at,
            'expires_at': expires_at
        }
        integrity_hash = _hash_record(record)
        
        c.execute('''INSERT INTO auth_otp VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            otp_id, email, otp_code, created_at, expires_at, 0, None, integrity_hash
        ))
        conn.commit()
        conn.close()
        
        # Send OTP via email (simulated - print to console)
        self._send_otp_email(email, otp_code)
        
        self._audit_auth(email, 'login_step1', 'otp_sent')
        
        return {
            'success': True,
            'otp_id': otp_id,
            'message': f'OTP sent to {email}. Code expires in 10 minutes.'
        }
    
    def _send_otp_email(self, email: str, otp_code: str):
        """Simulate sending OTP email (in production: use SendGrid/AWS SES)"""
        print(f"\n{'='*60}")
        print(f"[EMAIL] OTP Verification Code")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"Subject: Your Mythara Contractor Portal Login Code")
        print(f"\nYour verification code is: {otp_code}")
        print(f"\nThis code expires in 10 minutes.")
        print(f"If you did not request this code, please ignore this email.")
        print(f"{'='*60}\n")
    
    # ---------------------- Login (Step 2) ----------------------
    def login_step2(self, otp_id: str, otp_code: str) -> Dict[str, Any]:
        """Verify OTP, issue session token"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check OTP
        c.execute('SELECT email, otp_code, expires_at, verified FROM auth_otp WHERE otp_id = ?', (otp_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            self._audit_auth(None, 'login_step2', 'invalid_otp_id')
            return {'success': False, 'error': 'Invalid OTP'}
        
        email, stored_code, expires_at, verified = row
        
        if verified:
            conn.close()
            self._audit_auth(email, 'login_step2', 'otp_already_used')
            return {'success': False, 'error': 'OTP already used'}
        
        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            self._audit_auth(email, 'login_step2', 'otp_expired')
            return {'success': False, 'error': 'OTP expired'}
        
        if otp_code != stored_code:
            conn.close()
            self._audit_auth(email, 'login_step2', 'otp_mismatch')
            return {'success': False, 'error': 'Invalid OTP'}
        
        # Mark OTP as verified
        verified_at = datetime.now().isoformat()
        c.execute('UPDATE auth_otp SET verified = 1, verified_at = ? WHERE otp_id = ?', (verified_at, otp_id))
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        session_record = {
            'session_token': session_token,
            'email': email,
            'created_at': created_at,
            'expires_at': expires_at
        }
        integrity_hash = _hash_record(session_record)
        
        c.execute('''INSERT INTO auth_sessions VALUES (?, ?, ?, ?, ?, ?)''', (
            session_token, email, created_at, expires_at, 0, integrity_hash
        ))
        
        # Update last login
        c.execute('UPDATE contractor_auth SET last_login = ? WHERE email = ?', (created_at, email))
        
        conn.commit()
        conn.close()
        
        self._audit_auth(email, 'login_step2', 'success')
        
        return {
            'success': True,
            'session_token': session_token,
            'email': email,
            'expires_at': expires_at,
            'message': 'Login successful'
        }
    
    # ---------------------- Session validation ----------------------
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session token, return contractor email if valid"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT email, expires_at, revoked FROM auth_sessions WHERE session_token = ?', (session_token,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {'valid': False, 'error': 'Invalid session'}
        
        email, expires_at, revoked = row
        
        if revoked:
            return {'valid': False, 'error': 'Session revoked'}
        
        if datetime.now() > datetime.fromisoformat(expires_at):
            return {'valid': False, 'error': 'Session expired'}
        
        return {'valid': True, 'email': email}
    
    # ---------------------- Logout ----------------------
    def logout(self, session_token: str) -> Dict[str, Any]:
        """Revoke session token"""
        validation = self.validate_session(session_token)
        
        if not validation['valid']:
            return {'success': False, 'error': validation['error']}
        
        email = validation['email']
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE auth_sessions SET revoked = 1 WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
        
        self._audit_auth(email, 'logout', 'success')
        
        return {'success': True, 'message': 'Logged out successfully'}
    
    # ---------------------- Password reset ----------------------
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Generate password reset OTP (similar to login OTP)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT email FROM contractor_auth WHERE email = ?', (email,))
        if not c.fetchone():
            conn.close()
            self._audit_auth(email, 'password_reset_request', 'invalid_email')
            return {'success': False, 'error': 'Email not found'}
        
        # Generate OTP
        otp_code = f"{secrets.randbelow(1000000):06d}"
        otp_id = hashlib.sha256(f"reset_{email}{otp_code}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        record = {
            'otp_id': otp_id,
            'email': email,
            'otp_code': otp_code,
            'created_at': created_at,
            'expires_at': expires_at
        }
        integrity_hash = _hash_record(record)
        
        c.execute('''INSERT INTO auth_otp VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            otp_id, email, otp_code, created_at, expires_at, 0, None, integrity_hash
        ))
        conn.commit()
        conn.close()
        
        # Send reset OTP
        print(f"\n{'='*60}")
        print(f"[EMAIL] Password Reset Code")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"Subject: Reset Your Mythara Contractor Portal Password")
        print(f"\nYour password reset code is: {otp_code}")
        print(f"\nThis code expires in 10 minutes.")
        print(f"{'='*60}\n")
        
        self._audit_auth(email, 'password_reset_request', 'otp_sent')
        
        return {
            'success': True,
            'otp_id': otp_id,
            'message': f'Reset code sent to {email}'
        }
    
    def reset_password(self, otp_id: str, otp_code: str, new_password: str) -> Dict[str, Any]:
        """Verify reset OTP and update password"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verify OTP (same logic as login_step2)
        c.execute('SELECT email, otp_code, expires_at, verified FROM auth_otp WHERE otp_id = ?', (otp_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            self._audit_auth(None, 'password_reset', 'invalid_otp')
            return {'success': False, 'error': 'Invalid reset code'}
        
        email, stored_code, expires_at, verified = row
        
        if verified:
            conn.close()
            self._audit_auth(email, 'password_reset', 'otp_already_used')
            return {'success': False, 'error': 'Reset code already used'}
        
        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            self._audit_auth(email, 'password_reset', 'otp_expired')
            return {'success': False, 'error': 'Reset code expired'}
        
        if otp_code != stored_code:
            conn.close()
            self._audit_auth(email, 'password_reset', 'otp_mismatch')
            return {'success': False, 'error': 'Invalid reset code'}
        
        # Update password
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        c.execute('UPDATE contractor_auth SET password_hash = ? WHERE email = ?', (new_hash, email))
        
        # Mark OTP as used
        c.execute('UPDATE auth_otp SET verified = 1, verified_at = ? WHERE otp_id = ?', (datetime.now().isoformat(), otp_id))
        
        conn.commit()
        conn.close()
        
        self._audit_auth(email, 'password_reset', 'success')
        
        return {'success': True, 'message': 'Password reset successfully'}


# Self-test
if __name__ == '__main__':
    print('\n[ContractorAuth] Self-test starting...')
    auth = ContractorAuth()
    
    print('[TEST] Registering contractor john@example.com...')
    auth.register_contractor('john@example.com', 'SecurePass123!')
    
    print('[TEST] Login step 1 (email + password)...')
    step1 = auth.login_step1('john@example.com', 'SecurePass123!')
    if step1['success']:
        print(f"  OTP ID: {step1['otp_id']}")
        # Simulate user entering OTP from email
        otp_code = input("Enter OTP code from email (or check console output): ")
        
        print('[TEST] Login step 2 (OTP verification)...')
        step2 = auth.login_step2(step1['otp_id'], otp_code)
        if step2['success']:
            print(f"  Session token: {step2['session_token'][:20]}...")
            
            print('[TEST] Validating session...')
            valid = auth.validate_session(step2['session_token'])
            print(f"  Valid: {valid['valid']}, Email: {valid.get('email')}")
            
            print('[TEST] Logging out...')
            logout = auth.logout(step2['session_token'])
            print(f"  Logout: {logout['success']}")
        else:
            print(f"  Error: {step2['error']}")
    else:
        print(f"  Error: {step1['error']}")
    
    print('\n[ContractorAuth] Self-test complete.')
