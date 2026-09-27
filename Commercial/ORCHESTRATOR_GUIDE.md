# Mythara Token-Based Orchestrator System
## Architecture plan — deploy before treating as operational

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## 🎯 System Overview

The design for a **token-based orchestrator** managing all AI bots:
- **Minimal human contact by design** (VP Bot makes routine decisions)
- **$0/month code operating cost** (third-party APIs bill separately by usage)
- **SSIP integration** (Sanctification, Integrity Hashes, Blessings Reservoir)
- **Centralized decision-making** via VP Bot
- **SQLite database** for shared state
- **REST API** for bot coordination

> Status: architecture and code (`mythara_orchestrator.py`) exist. The orchestrator is not confirmed running — "System Status" below describes the intended deployment, not current operations.

---

## 🔐 Token Architecture

### Master VP Token:
```
<redacted — generate at deploy time, store outside the repo, never commit a real token>
```
**Generate this at deployment** — a master token committed to a document is a compromised token. Only the VP Bot uses it.

### How It Works:

```
1. Bot wants to take action
   └─> Requests approval from Orchestrator API
       └─> Sends: bot_id, token, action, reason
           └─> VP validates token
               └─> Logs decision with SSIP integrity hash
                   └─> Returns: approved/denied + decision_id
```

### Token Flow:

```
VP Bot (Master Token)
    ↓ registers
Worker Bots (Individual Tokens)
    ↓ authenticate
Orchestrator API (validates)
    ↓ logs
SQLite Database (audit trail)
```

---

## 🤖 Your AI Org Chart

```
YOU (Owner - Zero Contact)
    |
    └─ 🎯 VP Bot (Daily 8am)
        ├─ Token: <generated at registration>
        ├─ Analyzes KPIs
        ├─ Deploys new bots
        └─ Makes all decisions
            |
            ├─ 📧 Autonomous Sales Bot (Daily 9am)
            │   └─ Token: Generated on registration
            │
            ├─ 💰 Affiliate Bot (Friday 5pm)
            │   └─ Token: Generated on registration
            │
            ├─ 💳 Payment Monitor (Hourly)
            │   └─ Token: Generated on registration
            │
            ├─ 📊 Marketing Bot (Hourly)
            │   └─ Token: Generated on registration
            │
            ├─ 📈 Sales Trainer (Every 6hrs)
            │   └─ Token: Generated on registration
            │
            ├─ 🔗 LinkedIn Bot (Daily 10am) ← NEW
            │   └─ Token: Pending registration
            │
            ├─ 📨 Email Nurture Bot ← PENDING
            │   └─ Token: Will generate on deploy
            │
            └─ 🤝 Affiliate Recruiter ← PENDING
                └─ Token: Will generate on deploy
```

---

## 📊 Orchestrator API

**Base URL:** `http://localhost:5000`

### Endpoints:

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | None |
| GET | `/dashboard` | System overview | None |
| POST | `/register_bot` | Register new bot | VP Token |
| POST | `/request_approval` | Request action approval | Bot Token |
| POST | `/get_task` | Get next task | Bot Token |
| POST | `/complete_task` | Mark task done | Bot Token |
| POST | `/create_task` | Create new task | VP Token |
| POST | `/get_state` | Get shared state | None |
| POST | `/set_state` | Set shared state | None |

---

## 🔄 Automatic Workflows

### Daily (8am) - VP Bot Reviews Performance:
```python
1. Check revenue vs $10k target
   └─ If below → Deploy conversion bot
2. Check leads vs 100 target
   └─ If below → Deploy LinkedIn bot
3. Check costs vs $500 budget
   └─ If over → Pause expensive bots
4. Log all decisions with SSIP integrity hashes
```

### Hourly - Worker Bots Execute:
```python
1. Authenticate with token
2. Request approval for actions
3. Get tasks from queue
4. Execute tasks
5. Report completion
6. Update performance score
```

### Weekly (Friday 5pm) - Affiliate Payouts:
```python
1. Calculate commissions
2. Request approval for payouts >$50
3. Send PayPal payments
4. Log transactions
5. Update affiliate stats
```

---

## 💾 Database Schema

### `bots` table:
- `bot_id` (PRIMARY KEY)
- `bot_name`
- `status` (active/paused/retired)
- `last_run` (timestamp)
- `performance_score` (0-100)
- `token` (unique auth token)

### `decisions` table (SSIP Audit Trail):
- `decision_id` (PRIMARY KEY)
- `timestamp`
- `bot_id`
- `action`
- `approved` (true/false)
- `reason`
- `integrity_hash` (SSIP hash)

### `tasks` table:
- `task_id` (PRIMARY KEY)
- `assigned_to` (bot_id)
- `task_type`
- `payload` (JSON)
- `status` (pending/completed)
- `created_at`
- `completed_at`

### `shared_state` table:
- `key` (PRIMARY KEY)
- `value` (JSON)
- `updated_at`

---

## 🚀 How to Use

### Start Orchestrator:
```bash
# Double-click this file:
START_ORCHESTRATOR.bat

# Or run manually:
py -3.11 mythara_orchestrator.py
```

**Orchestrator runs on:** `http://localhost:5000`

### View Dashboard:
```
Open browser: http://localhost:5000/dashboard
```

### Register New Bot:
```python
import requests

response = requests.post('http://localhost:5000/register_bot', json={
    'vp_token': 'YOUR_VP_MASTER_TOKEN',
    'bot_id': 'my_new_bot',
    'bot_name': 'My New Bot'
})

bot_token = response.json()['bot_token']
# Save this token - bot uses it for all requests
```

### Worker Bot Example:
```python
import requests

# Request approval
response = requests.post('http://localhost:5000/request_approval', json={
    'bot_id': 'my_bot',
    'token': 'my_bot_token',
    'action': 'send_email',
    'reason': 'lead_nurture',
    'count': 10
})

if response.json()['approved']:
    # Do the action
    send_emails()
    
    # Report completion
    requests.post('http://localhost:5000/complete_task', json={
        'bot_id': 'my_bot',
        'token': 'my_bot_token',
        'task_id': 'task_123',
        'result': {'emails_sent': 10}
    })
```

---

## 🔐 SSIP Integration

### Sanctification (Token Validation):
```python
def validate_token(token, bot_id):
    # VP Master token always valid
    if token == VP_MASTER_TOKEN:
        return True
    
    # Check bot's individual token
    if bot_token_matches(bot_id, token):
        return True
    
    # Shadow_Resolver: deny if invalid
    return False
```

### Integrity Hashing (Decision Audit):
```python
def log_decision(bot_id, action, approved):
    integrity_hash = sha256({
        'bot_id': bot_id,
        'action': action,
        'approved': approved
    })
    
    # Store with hash for tamper detection
    db.store(decision_id, integrity_hash)
```

### Blessings Reservoir (Performance Tracking):
```python
# Each successful task → +1 performance score
# Failed task → -5 performance score
# Score used to allocate resources
```

---

**KPIs Tracked** (operating targets — aspirational, not achieved)

**Sanctified Targets** (configuration constants, reviewed before each cycle):
- Monthly Revenue: **$10,000**
- Monthly Leads: **100**
- Conversion Rate: **5%**
- Max CAC: **$200**
- Max Budget: **$500/month**

**Deployment state (intended, not current):**
- Bots Active: **5** (3 more to deploy)
- Code cost: **$0/month**
- Decisions Made: **Logged in DB**
- Tasks Completed: **Tracked per bot**

---

## 🎯 Intended Automation (after deployment)

### Routine decisions the VP Bot handles:

1. **Sales** → Autonomous Sales Bot handles drafting and clause checks
2. **Affiliates** → Recruiter Bot + Payout Bot handle tracking and payouts
3. **Payments** → Payment Monitor tracks, VP Bot allocates
4. **Lead Gen** → LinkedIn Bot + Marketing Bot handle outreach
5. **Nurture** → Email Bot follows up automatically
6. **Decisions** → VP Bot makes routine calls within its targets
7. **Deployment** → VP Bot deploys new bots when targets call for it

### Operator checks (not "zero human contact"):
- **Dashboard** (optional): see what's happening
- **Bank account**: verify money that actually arrives
- **Email** (optional): bots CC you on major events
- **Clause violations**: review what the orchestrator blocked

Human judgment stays in the loop on pricing, contracts, and anything outside the sanctified targets.

---

## 🔧 Maintenance

### Orchestrator Auto-Starts:
Add to Windows Task Scheduler:
```powershell
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 mythara_orchestrator.py" -WorkingDirectory "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "Mythara_Orchestrator" -Action $action -Trigger $trigger
```

### Database Backups:
```bash
# Automatic backups every week
copy mythara_orchestrator.db mythara_orchestrator_backup_YYYY-MM-DD.db
```

### Token Rotation (If Compromised):
```python
# 1. Generate new VP token
new_token = sha256("MYTHARA_VP_2026")

# 2. Update orchestrator.py
VP_MASTER_TOKEN = new_token

# 3. Restart orchestrator
# All bots re-authenticate automatically
```

---

## 💰 Revenue Tracking

### Direct Sales:
- Autonomous Sales Bot → PayPal → Loyverse → Payment Monitor → You

### Affiliate Sales:
- Affiliate shares link → Customer buys → Commission calculated → Friday payout

### All Tracked:
- Every payment logged with SSIP integrity hash
- Revenue aggregated in orchestrator
- VP Bot optimizes based on ROI

---

## ✅ System Status (intended deployment)

**Orchestrator:** localhost:5000 (when started)  
**VP Bot:** scheduled daily 8am (to configure)  
**Worker Bots:** 5 planned active, 3 to deploy  
**Database:** mythara_orchestrator.db  
**Code cost:** $0/month  
**Human contact:** minimized by design, not zero — pricing, contracts, and clause violations come to you

---

## 🎉 Deployment Summary

The orchestrator architecture is documented above with:
- Token-based security (generate the master token at deploy time)
- Central orchestration
- SSIP integrity
- Routine decisions automated; exceptions escalated to you

**Next steps:** generate tokens, start the orchestrator, schedule the VP Bot, verify the dashboard — then run it a week and review the decision log.

---

**Mythara Engine - Autonomous Operations**  
**Proprietary and Confidential**
