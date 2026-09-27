# Mythara Contractor Delegation System

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  
**Proprietary and Confidential.**

---

## Overview

Complete contractor management system with:
- **Email-based authentication** (email = contractor ID)
- **Multi-step verification** (6-digit OTP via email, 10min expiry)
- **Performance-based payouts** with market rate adjustments
- **Automated expense tracking** in Finance VP
- **Full audit trail** with SSIP integrity hashing

---

## Files Created

| File | Purpose |
|------|---------|
| `mythara_contractor_manager.py` | Core contractor management (onboarding, tasks, payouts) |
| `mythara_contractor_auth.py` | Authentication system (2-step login, password reset, sessions) |
| `run_contractor_manager.py` | Basic contractor demo (no auth) |
| `run_contractor_auth_demo.py` | Full auth demo (onboarding → login → tasks → payout) |
| `test_contractor_finance_integration.py` | Test Finance VP integration |

---

## Database Schema

**Database:** `mythara_contractor.db`

### Tables

**contractors** (from contractor_manager)
- email (PK), name, hourly_rate, market_rate_factor, enabled, created_at, integrity_hash

**contractor_auth** (authentication)
- email (PK), password_hash (bcrypt), enabled, created_at, last_login, integrity_hash

**auth_otp** (multi-step verification)
- otp_id (PK), email, otp_code, created_at, expires_at, verified, verified_at, integrity_hash

**auth_sessions** (session tokens)
- session_token (PK), email, created_at, expires_at, revoked, integrity_hash

**tasks** (work assignments)
- task_id (PK), contractor_email, description, estimated_hours, assigned_at, completed_at, performance_score, payout_multiplier, payout_amount, integrity_hash

**payouts** (contractor payments)
- payout_id (PK), contractor_email, amount, period_start, period_end, status, created_at, integrity_hash

**audits** (system audit log)
- audit_id (PK), entity, action, details, created_at, integrity_hash

**auth_audit** (authentication events)
- audit_id (PK), email, action, status, ip_address, user_agent, created_at, integrity_hash

---

## Payout Formula

```python
# Step 1: Calculate effective hourly rate
effective_rate = hourly_rate * market_rate_factor

# Step 2: Calculate performance multiplier (baseline = 75)
multiplier = clamp(1 + (performance_score - 75) / 100, 0.75, 1.5)

# Examples:
#   score 75 → multiplier 1.00 (baseline)
#   score 90 → multiplier 1.15 (15% bonus)
#   score 60 → multiplier 0.85 (15% penalty)
#   score 100 → multiplier 1.25 (capped at +25%)
#   score 50 → multiplier 0.75 (capped at -25%)

# Step 3: Calculate payout
payout = hours * effective_rate * multiplier
```

### Example Calculation

Contractor: hourly_rate=$80, market_rate_factor=1.10  
Task: 9.5 hours, performance_score=88

```
effective_rate = $80 * 1.10 = $88
multiplier = 1 + (88 - 75) / 100 = 1.13
payout = 9.5 * $88 * 1.13 = $944.68
```

---

## Authentication Flow

### 1. Contractor Registration (during onboarding)

```python
from mythara_contractor_manager import MytharaContractorManager

cm = MytharaContractorManager()
cm.onboard_contractor(
    email='contractor@example.com',
    name='Jane Contractor',
    hourly_rate=75.0,
    market_rate_factor=1.05,  # 5% market adjustment
    password='<redacted>'  # Auto-registers auth
)
```

### 2. Login - Step 1 (Email + Password)

```python
from mythara_contractor_auth import ContractorAuth

auth = ContractorAuth()
step1 = auth.login_step1('contractor@example.com', '<redacted>')

if step1['success']:
    otp_id = step1['otp_id']
    # OTP code sent to email (6 digits, expires in 10 minutes)
```

### 3. Login - Step 2 (OTP Verification)

```python
# Contractor enters OTP from email
otp_code = "123456"  # From email

step2 = auth.login_step2(otp_id, otp_code)

if step2['success']:
    session_token = step2['session_token']
    # Token valid for 24 hours
```

### 4. Session Validation

```python
validation = auth.validate_session(session_token)

if validation['valid']:
    contractor_email = validation['email']
    # Proceed with authenticated operations
```

### 5. Logout

```python
auth.logout(session_token)
# Session revoked, token no longer valid
```

### 6. Password Reset

```python
# Step 1: Request reset
reset_request = auth.request_password_reset('contractor@example.com')
otp_id = reset_request['otp_id']
# Reset code sent to email

# Step 2: Submit new password with OTP
otp_code = "654321"  # From email
auth.reset_password(otp_id, otp_code, '<redacted>')
```

---

## Task Management

### Assign Task

```python
cm.assign_task(
    contractor_email='contractor@example.com',
    task_id='TASK-2025-001',
    description='Build payment integration',
    estimated_hours=8.0
)
```

### Record Completion

```python
completion = cm.record_task_completion(
    task_id='TASK-2025-001',
    performance_score=92,  # 0-100 scale
    actual_hours=7.5  # Optional, defaults to estimated_hours
)

print(f"Payout: ${completion['payout']:.2f}")
```

### Aggregate Payouts (Weekly)

```python
# Get pending payouts for period
payouts = cm.aggregate_payouts(
    period_start='2025-11-01T00:00:00',
    period_end='2025-11-07T23:59:59'
)

for p in payouts:
    print(f"{p['contractor_email']}: ${p['amount']:.2f}")
```

### Finalize Payout

```python
# Mark payout as paid AND record in Finance VP
result = cm.finalize_payout(payout_id)

# Automatically creates contractor_expense in mythara_finance.db
```

---

## Finance VP Integration

When you finalize a contractor payout, it automatically:

1. Marks payout as `paid` in `mythara_contractor.db`
2. Creates expense record in `mythara_finance.db` → `contractor_expenses` table
3. Updates Finance VP metrics:
   - `contractor_expenses_pending`
   - `contractor_expenses_paid`
   - `contractor_expenses_total`
   - `net_margin = total_margin - contractor_expenses`

View in Finance VP report:

```python
from mythara_finance_vp import MytharaFinanceVP

finance = MytharaFinanceVP()
report = finance.generate_finance_report()
print(report)
```

Output includes:

```
CONTRACTOR EXPENSES:
   Pending Payouts: $944.68
   Paid Expenses: $0.00
   Total Contractor Costs: $944.68
   Net Margin: $-674.68
```

---

## Audit Trail

Every action is logged with integrity hashes:

```python
# Get recent audit events
audits = cm.generate_audit_report(last_n=50)

for a in audits:
    print(f"{a['created_at']} | {a['entity']} | {a['action']} | {a['integrity_hash']}")
```

Authentication events are separately audited:

```python
import sqlite3
conn = sqlite3.connect('mythara_contractor.db')
c = conn.cursor()
c.execute('SELECT * FROM auth_audit ORDER BY created_at DESC LIMIT 20')
for row in c.fetchall():
    print(row)
conn.close()
```

---

## Security Features

✅ **Password hashing:** bcrypt with 12 rounds  
✅ **OTP expiry:** 10 minutes  
✅ **Session expiry:** 24 hours  
✅ **Integrity hashing:** All critical writes include SHA-256 hash  
✅ **Audit logging:** Every auth event logged with IP/user-agent  
✅ **Session revocation:** Logout invalidates token immediately  
✅ **Password reset:** Separate OTP flow with expiry  

---

## Testing

### Quick Test (No Auth)

```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
py -3.11 run_contractor_manager.py
```

### Full Auth Demo

```powershell
py -3.11 run_contractor_auth_demo.py
```

### Finance Integration Test

```powershell
py -3.11 test_contractor_finance_integration.py
```

---

## Next Steps

### 1. Schedule Automated Payouts

Add weekly contractor payout processing:

```powershell
# In AUTORUN_ALL_VPS.ps1, add:
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_contractor_payouts.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 5pm
Register-ScheduledTask -TaskName "Mythara_Contractor_Payouts" -Action $action -Trigger $trigger -Force
```

### 2. Email Integration

Replace simulated emails with real email service:

```python
# In mythara_contractor_auth.py, replace _send_otp_email():
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
message = Mail(
    from_email='noreply@mythara.com',  # placeholder — replace with your real sender
    to_emails=email,
    subject='Your Mythara Login Code',
    html_content=f'<p>Your code: <strong>{otp_code}</strong></p>'
)
sg.send(message)
```

### 3. Contractor Portal API

Create FastAPI endpoints:

```python
from fastapi import FastAPI, Depends, HTTPException
from mythara_contractor_auth import ContractorAuth

app = FastAPI()
auth = ContractorAuth()

@app.post("/auth/login/step1")
def login_step1(email: str, password: str):
    return auth.login_step1(email, password)

@app.post("/auth/login/step2")
def login_step2(otp_id: str, otp_code: str):
    return auth.login_step2(otp_id, otp_code)

@app.get("/tasks")
def get_tasks(session_token: str):
    validation = auth.validate_session(session_token)
    if not validation['valid']:
        raise HTTPException(401, "Invalid session")
    
    # Return tasks for contractor
    cm = MytharaContractorManager()
    # ... query tasks
```

### 4. Payment Gateway Integration

For live payouts:

```python
# PayPal Payouts API
import paypalrestsdk

paypalrestsdk.configure({
    "mode": "live",
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_SECRET')
})

payout = paypalrestsdk.Payout({
    "sender_batch_header": {
        "sender_batch_id": payout_id,
        "email_subject": "You have a payout from Mythara!"
    },
    "items": [{
        "recipient_type": "EMAIL",
        "amount": {"value": str(amount), "currency": "USD"},
        "receiver": contractor_email,
        "note": f"Payment for {task_count} tasks"
    }]
})

if payout.create():
    print(f"Payout {payout.batch_header.payout_batch_id} created")
```

---

## White-Label Configuration

To sell this system to other platforms:

1. **Branding:** Environment variables for logo, colors, company name
2. **Market rates:** JSON config file with regional hourly rate adjustments
3. **Contract templates:** PDF generation with platform-specific terms
4. **Multi-tenant:** Add `platform_id` to all tables, isolate data per customer

Example config:

```json
{
  "platform_name": "Acme Contractor Hub",
  "branding": {
    "logo_url": "https://acme.com/logo.png",
    "primary_color": "#FF6600"
  },
  "market_rates": {
    "US": 1.15,
    "EU": 1.10,
    "APAC": 0.95
  },
  "payout_schedule": "weekly",
  "performance_baseline": 75
}
```

---

## Support

For integration questions or white-label licensing:
- Email: support@mythara.com (placeholder — not a live address)
- Documentation: https://mythara.com/docs/contractor-api (placeholder — not a live site)

---

**Remember:** This is proprietary, NDA-protected software. Do not distribute without authorization.
