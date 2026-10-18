# Copyright © 2026 Mythara Labs LLC. All rights reserved.

# MYTHARA DEVOPS VP - DEPLOYMENT INSTRUCTIONS

## Overview

The DevOps VP Bot monitors infrastructure health, auto-remediates issues, manages bot deployments, and ensures system stability.

## Features

✅ **System Health Monitoring**
   - CPU, memory, disk usage tracking
   - Network connections monitoring
   - Health score calculation (0-100)

✅ **Bot Process Management**
   - Detects running Mythara bots
   - Tracks resource usage per bot
   - Auto-restart crashed bots

✅ **Orchestrator Health Check**
   - API response time monitoring
   - Connection status verification
   - Auto-restart if down

✅ **Auto-Remediation (Shadow_Resolver Pattern)**
   - High CPU → Kill low-priority processes
   - High memory → Restart memory-intensive bots
   - Disk full → Cleanup old logs/temp files
   - Bot crashed → Auto-restart with retry limit
   - Orchestrator down → Restart orchestrator service

✅ **Bot Deployment**
   - Validates code exists
   - Installs dependencies
   - Registers with orchestrator
   - Generates Windows Task Scheduler commands
   - Tracks deployment status

✅ **SSIP Integration**
   - Sanctified Limits: Immutable infrastructure thresholds
   - Integrity Hashing: All incidents logged with cryptographic proof
   - Token-based Authentication: Registers with orchestrator

---

## Installation

### 1. Verify psutil Installed

```powershell
py -3.11 -m pip install psutil
```

### 2. Test DevOps VP

```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
py -3.11 run_devops_vp.py
```

**Expected Output:**
```
============================================================
MYTHARA DEVOPS VP - INFRASTRUCTURE MONITOR
Run Time: November 03, 2025 at 09:16 AM
============================================================
[OK] Registered as DevOps VP
   Token: fea78a37cbf76242...

[CHECK] System health...
[CHECK] Bot processes...
[CHECK] Orchestrator...

============================================================

DEVOPS VP REPORT
...
```

---

## Scheduling (Windows Task Scheduler)

### Run Hourly

```powershell
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_devops_vp.py" -WorkingDirectory "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "Mythara_DevOps_VP" -Action $action -Trigger $trigger
```

---

## Configuration

### Sanctified Limits (Immutable)

Located in `mythara_devops_vp.py` > `_init_sanctified_limits()`:

```python
{
    'max_cpu_percent': 80,        # CPU usage alert threshold
    'max_memory_percent': 80,      # Memory usage alert threshold
    'max_disk_percent': 90,        # Disk usage critical threshold
    'max_api_failures_per_hour': 5,  # Orchestrator API failure limit
    'max_bot_restart_attempts': 3,   # Shadow_Resolver retry limit
    'max_concurrent_deployments': 2, # Deployment queue limit
    'integrity_hash': 'cfb95f3ee42f180f'  # Sanctification proof
}
```

**WARNING:** These limits are sanctified (immutable). Changing them requires regenerating the integrity hash.

### Health Threshold

Located in `mythara_devops_vp.py` > `__init__()`:

```python
self.health_threshold = 80  # Minimum acceptable health score
```

Lower scores trigger urgent auto-remediation.

---

## Report Breakdown

### System Health Section

```
SYSTEM HEALTH:
   Health Score: 67.2/100       ← Overall health (lower = worse)
   CPU Usage: 19.8% (limit: 80%)
   Memory Usage: 87.1% (limit: 80%)  ← EXCEEDS LIMIT (issue detected)
   Disk Usage: 14.7% (limit: 90%)
   Network Connections: 103

   Status: 🔴 UNHEALTHY         ← Score < 80
```

**Health Score Formula:**
- Start at 100
- -20 points per (CPU / 100) × 20
- -20 points per (Memory / 100) × 20
- -10 points per (Disk / 100) × 10
- -10 points per issue detected

### Orchestrator Status

```
ORCHESTRATOR STATUS:
   Status: HEALTHY
   Response Time: 2045ms        ← API latency (normal < 500ms)
   URL: http://localhost:5000
```

Possible statuses:
- `healthy`: API responding with 200 OK
- `unhealthy`: API responding but not 200 OK
- `down`: Connection refused
- `error`: Exception (timeout, network error)

### Running Bots

```
RUNNING BOTS (7):

   ✅ mythara_orchestrator       ← Bot name
      PID: 10096                 ← Process ID
      CPU: 0.0%                   ← CPU usage
      Memory: 0.2%                ← Memory usage
```

Detects bots by scanning process command lines for:
- `mythara_orchestrator.py`
- `run_marketing_bot.py`
- `run_sales_trainer_bot.py`
- `run_payment_monitor_bot.py`
- `run_autonomous_sales_bot.py`
- `run_affiliate_bot.py`
- `mythara_vp_bot.py`

### Recent Incidents

```
RECENT INCIDENTS (1):

   • memory_high                  ← Issue type
     Action: restart_memory_intensive_bots  ← Remediation taken
     Success: ✅                  ← Outcome
```

**Incident Types:**
- `cpu_high`: CPU > 80%
- `memory_high`: Memory > 80%
- `disk_full`: Disk > 90%
- `bot_crashed`: Bot process died unexpectedly
- `orchestrator_down`: API not responding

### Recommendations

```
RECOMMENDATIONS:

   ⚠️ URGENT: System health below threshold
   → Run auto-remediation

   ⚠️ 1 issues detected
   → Fix memory_high: 87.1% > 80%
```

Provides actionable next steps based on detected issues.

---

## Auto-Remediation Actions

### CPU High

**Detection:** CPU > 80%

**Action:**
1. Identify heavy processes (via psutil)
2. Kill non-critical processes
3. Log incident with integrity hash

**Implementation:** `auto_remediate()` → `cpu_high` case

### Memory High

**Detection:** Memory > 80%

**Action:**
1. Identify memory-intensive bots
2. Restart heavy bots (clears memory leaks)
3. Log incident

**Implementation:** `auto_remediate()` → `memory_high` case

### Disk Full

**Detection:** Disk > 90%

**Action:**
1. Delete files older than 30 days
2. Patterns: `*.log`, `*.tmp`, `__pycache__`
3. Log cleanup results

**Implementation:** `auto_remediate()` → `disk_full` case → `_cleanup_old_files()`

### Bot Crashed

**Detection:** Expected bot not in process list

**Action:**
1. Map bot_id to script name
2. Restart via subprocess
3. Increment restart attempts
4. Give up after 3 attempts (sanctified limit)

**Implementation:** `auto_remediate()` → `bot_crashed` case → `_restart_bot()`

### Orchestrator Down

**Detection:** API connection refused or timeout

**Action:**
1. Kill existing orchestrator processes
2. Restart via `START_ORCHESTRATOR.bat`
3. Wait 8 seconds for startup
4. Verify health endpoint responds

**Implementation:** `auto_remediate()` → `orchestrator_down` case → `_restart_orchestrator()`

---

## Bot Deployment Workflow

### 1. VP Bot Generates Code

VP Bot decides to deploy new bot (e.g., Email Nurture Bot) and creates:
- `mythara_email_nurture_bot.py`
- `run_email_nurture_bot.py`
- `DEPLOY_email_nurture_bot.md`

### 2. DevOps VP Receives Deployment Task

```python
bot_spec = {
    'bot_id': 'email_nurture_bot',
    'bot_name': 'Email Nurture Sequence Bot',
    'schedule': 'daily'
}
```

### 3. Deployment Steps

**Step 1:** Validate code exists
- Check `mythara_email_nurture_bot.py` file exists
- If missing → deployment fails

**Step 2:** Install dependencies
- Check `requirements.txt` if present
- Install via pip
- Currently skipped (most bots have no extra deps)

**Step 3:** Register with orchestrator
- POST to `/register_bot` with VP master token
- Receive unique bot token
- Store in deployment record

**Step 4:** Generate schedule command
- Map schedule string to Windows Task Scheduler trigger:
  * `hourly` → `-RepetitionInterval (New-TimeSpan -Hours 1)`
  * `daily` → `-Daily -At 9am`
  * `weekly` → `-Weekly -DaysOfWeek Monday -At 9am`
  * `every_6_hours` → `-RepetitionInterval (New-TimeSpan -Hours 6)`

**Step 5:** Output schedule command
- Prints PowerShell command to console
- User runs command to activate bot

### 4. Deployment Tracking

```python
deployment = {
    'deployment_id': 'a3f8d2e1c9b7',  # SHA-256 hash
    'bot_spec': {...},
    'status': 'deployed',
    'started_at': '2025-11-03T09:16:00',
    'completed_at': '2025-11-03T09:16:05',
    'bot_token': '4923ceb949464cda...',
    'schedule_command': '$action = ...',
    'steps': [
        {'step': 'generate_code', 'status': 'completed'},
        {'step': 'install_dependencies', 'status': 'completed'},
        {'step': 'register_bot', 'status': 'completed'},
        {'step': 'schedule_task', 'status': 'completed'},
        {'step': 'start_bot', 'status': 'completed'}
    ]
}
```

All deployments stored in `self.deployments` list with full audit trail.

---

## Monitoring Orchestrator Instances

### Issue: Multiple Orchestrator Processes

**Detected:**
```
RUNNING BOTS (7):
   ✅ mythara_orchestrator (PID: 10096)
   ✅ mythara_orchestrator (PID: 15964)
   ✅ mythara_orchestrator (PID: 17576)
   ✅ mythara_orchestrator (PID: 18604)
   ✅ mythara_orchestrator (PID: 19324)
   ✅ mythara_orchestrator (PID: 19640)
   ✅ mythara_orchestrator (PID: 19652)
```

**Cause:** Multiple `START_ORCHESTRATOR.bat` instances launched

**Solution:**

1. Kill duplicate processes:
```powershell
Get-Process | Where-Object {$_.CommandLine -like "*mythara_orchestrator*"} | Stop-Process -Force
```

2. Start one instance:
```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
START_ORCHESTRATOR.bat
```

3. Verify single instance:
```powershell
py -3.11 run_devops_vp.py
```

---

## Integration with VP Bot

The DevOps VP works alongside the VP of Sales & Marketing:

**VP Bot (Strategic):**
- Analyzes KPIs
- Decides which bots to deploy
- Generates bot code
- Creates deployment tasks

**DevOps VP (Operational):**
- Monitors system health
- Deploys bots created by VP
- Manages infrastructure
- Auto-remediates issues

**Workflow:**
1. VP Bot detects low leads → Creates LinkedIn Automation Bot code
2. VP Bot creates deployment task in orchestrator
3. DevOps VP pulls task from queue
4. DevOps VP validates code, registers bot, schedules task
5. DevOps VP reports deployment success
6. DevOps VP monitors new bot's health hourly

---

## Troubleshooting

### "No connection could be made" Error

**Symptom:**
```
[CHECK] Orchestrator...
ConnectionRefusedError: [WinError 10061]
```

**Cause:** Orchestrator not running

**Fix:**
```powershell
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial
START_ORCHESTRATOR.bat
```

Wait 8 seconds, then rerun DevOps VP.

---

### "System health below threshold" Warning

**Symptom:**
```
Health Score: 67.2/100
Status: 🔴 UNHEALTHY
```

**Cause:** Memory usage (87.1%) exceeds limit (80%)

**Fix:** Auto-remediation already attempted. If persists:

1. Close unnecessary programs
2. Restart heavy bots manually
3. Increase `max_memory_percent` limit (requires regenerating integrity hash)

---

### "UnicodeEncodeError" in Output

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode characters
```

**Cause:** Windows terminal doesn't support emoji characters

**Fix:** Already fixed in `run_devops_vp.py` (removed emojis from print statements). If you see this, you're running an old version.

---

## Next Steps

1. ✅ DevOps VP created
2. ✅ psutil installed
3. ✅ Tested successfully
4. ⏳ Schedule hourly task (see "Scheduling" section above)
5. ⏳ Kill duplicate orchestrator processes
6. ⏳ Integrate with VP Bot deployment workflow

---

## Advanced: Scaling Resources

### Scale Up (Increase Frequency)

When load is high, increase bot run frequency:

```python
devops.scale_resources('up')
```

**Actions:**
- Marketing Bot: hourly → every 30 min
- Sales Bot: daily → every 12 hours
- Increases resource consumption but faster lead gen

### Scale Down (Decrease Frequency)

When load is low, decrease bot run frequency:

```python
devops.scale_resources('down')
```

**Actions:**
- Marketing Bot: hourly → every 2 hours
- Sales Bot: daily → every 2 days
- Saves CPU/memory but slower lead gen

**Note:** Scaling actions are currently logged but not automatically applied. Future enhancement: Auto-update Windows Task Scheduler triggers.

---

## Summary

**You now have:**
- ✅ DevOps VP monitoring infrastructure (CPU, memory, disk, bots, orchestrator)
- ✅ Auto-remediation for 5 issue types (Shadow_Resolver pattern)
- ✅ Bot deployment capability (validates, registers, schedules)
- ✅ SSIP integration (Sanctified limits, integrity hashing, token auth)
- ✅ Comprehensive hourly reports with health scores and recommendations

**Next:** Schedule hourly via Windows Task Scheduler to enable 24/7 autonomous infrastructure management.
