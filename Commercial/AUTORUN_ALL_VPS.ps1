# Copyright © 2026 Mythara Labs LLC. All rights reserved.
#
# Schedule all Mythara VP bots in Windows Task Scheduler

Write-Host "============================================================"
Write-Host "MYTHARA VP AUTORUN SCHEDULER"
Write-Host "============================================================"
Write-Host ""
Write-Host "Scheduling all 6 VP bots:"
Write-Host "  1. VP of Finance - Daily 7am"
Write-Host "  2. VP of Sales & Marketing - Daily 8am"  
Write-Host "  3. VP of Customer Success - Daily 10am"
Write-Host "  4. VP of DevOps - Hourly"
Write-Host "  5. VP of Logistics - Hourly"
Write-Host "  6. VP of Public Affairs - Every 4 hours"
Write-Host ""

$WorkingDir = Get-Location

# Finance VP - Daily 7am
Write-Host "[1/6] Scheduling Finance VP (Daily 7am)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_finance_vp.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
try {
    Register-ScheduledTask -TaskName "Mythara_Finance_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

# Sales & Marketing VP - Daily 8am
Write-Host "[2/6] Scheduling Sales & Marketing VP (Daily 8am)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 mythara_vp_bot.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
try {
    Register-ScheduledTask -TaskName "Mythara_Sales_Marketing_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

# Customer Success VP - Daily 10am
Write-Host "[3/6] Scheduling Customer Success VP (Daily 10am)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_customer_success_vp.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 10am
try {
    Register-ScheduledTask -TaskName "Mythara_Customer_Success_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

# DevOps VP - Hourly
Write-Host "[4/6] Scheduling DevOps VP (Hourly)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_devops_vp.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
try {
    Register-ScheduledTask -TaskName "Mythara_DevOps_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

# Logistics VP - Hourly
Write-Host "[5/6] Scheduling Logistics VP (Hourly)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_logistics_vp.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
try {
    Register-ScheduledTask -TaskName "Mythara_Logistics_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

# Public Affairs VP - Every 4 hours
Write-Host "[6/6] Scheduling Public Affairs VP (Every 4 hours)..."
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_public_affairs_vp.py" -WorkingDirectory $WorkingDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4)
try {
    Register-ScheduledTask -TaskName "Mythara_Public_Affairs_VP" -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "   [OK] Scheduled" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================"
Write-Host "SCHEDULING COMPLETE"
Write-Host "============================================================"
Write-Host ""

# Verify tasks
Write-Host "Verifying scheduled tasks..."
Get-ScheduledTask | Where-Object {$_.TaskName -like "Mythara*"} | Select-Object TaskName, State, @{Name="NextRun";Expression={(Get-ScheduledTaskInfo $_).NextRunTime}} | Format-Table -AutoSize

Write-Host ""
Write-Host "To manually run a VP:"
Write-Host '  schtasks /Run /TN "Mythara_Finance_VP"'
Write-Host ""
Write-Host "To view all tasks: taskschd.msc"
Write-Host ""
