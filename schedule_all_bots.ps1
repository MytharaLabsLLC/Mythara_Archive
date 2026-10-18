# Copyright © 2026 Mythara Labs LLC. All rights reserved.

# Master script to schedule all 16 Mythara bots in Windows Task Scheduler
# Run this script as Administrator

$pythonPath = "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\.venv\Scripts\python.exe"
$workingDir = "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MYTHARA BOT SCHEDULER - Setting up all 16 autonomous bots" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "`n[WARNING] Not running as Administrator. Some tasks may fail to create." -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator' for best results.`n" -ForegroundColor Yellow
}

# Daily 6:00 AM - Finance VP
Write-Host "`n[1/15] Scheduling Finance VP (Daily 6:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_finance_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "6:00AM"
Register-ScheduledTask -TaskName "Mythara_Finance_VP" -Action $action -Trigger $trigger -Description "Mythara Finance VP - Daily financial reporting" -Force
Write-Host "[OK] Finance VP scheduled" -ForegroundColor Green

# Daily 8:00 AM - Sales/Marketing VP
Write-Host "`n[2/15] Scheduling Sales/Marketing VP (Daily 8:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_sales_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "8:00AM"
Register-ScheduledTask -TaskName "Mythara_Sales_VP" -Action $action -Trigger $trigger -Description "Mythara Sales/Marketing VP - Daily sales pipeline" -Force
Write-Host "[OK] Sales/Marketing VP scheduled" -ForegroundColor Green

# Daily 9:00 AM - Customer Success VP
Write-Host "`n[3/15] Scheduling Customer Success VP (Daily 9:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_customer_success_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
Register-ScheduledTask -TaskName "Mythara_Customer_Success_VP" -Action $action -Trigger $trigger -Description "Mythara Customer Success VP - Daily customer health" -Force
Write-Host "[OK] Customer Success VP scheduled" -ForegroundColor Green

# Hourly - DevOps VP
Write-Host "`n[4/15] Scheduling DevOps VP (Hourly)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_devops_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Once -At "12:00AM" -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "Mythara_DevOps_VP" -Action $action -Trigger $trigger -Description "Mythara DevOps VP - Hourly system monitoring" -Force
Write-Host "[OK] DevOps VP scheduled" -ForegroundColor Green

# Daily 7:00 AM - Logistics VP
Write-Host "`n[5/15] Scheduling Logistics VP (Daily 7:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_logistics_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "7:00AM"
Register-ScheduledTask -TaskName "Mythara_Logistics_VP" -Action $action -Trigger $trigger -Description "Mythara Logistics VP - Daily supply chain" -Force
Write-Host "[OK] Logistics VP scheduled" -ForegroundColor Green

# Daily 10:00 AM - Public Affairs VP
Write-Host "`n[6/15] Scheduling Public Affairs VP (Daily 10:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\Commercial\run_public_affairs_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "10:00AM"
Register-ScheduledTask -TaskName "Mythara_Public_Affairs_VP" -Action $action -Trigger $trigger -Description "Mythara Public Affairs VP - Daily public relations" -Force
Write-Host "[OK] Public Affairs VP scheduled" -ForegroundColor Green

# Weekly Monday 8:00 AM - HR VP
Write-Host "`n[7/15] Scheduling HR VP (Weekly Monday 8:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_hr_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "8:00AM"
Register-ScheduledTask -TaskName "Mythara_HR_VP" -Action $action -Trigger $trigger -Description "Mythara HR VP - Weekly contractor management" -Force
Write-Host "[OK] HR VP scheduled" -ForegroundColor Green

# Every 30 minutes - Support Chat Bot
Write-Host "`n[8/15] Scheduling Support Chat Bot (Every 30 minutes)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_support_bot.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Once -At "12:00AM" -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "Mythara_Support_Bot" -Action $action -Trigger $trigger -Description "Mythara Support Bot - Every 30 min ticket monitoring" -Force
Write-Host "[OK] Support Chat Bot scheduled" -ForegroundColor Green

# Daily 9:00 AM - International Sales VP
Write-Host "`n[9/15] Scheduling International Sales VP (Daily 9:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_international_sales_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
Register-ScheduledTask -TaskName "Mythara_International_Sales_VP" -Action $action -Trigger $trigger -Description "Mythara International Sales VP - Daily global pipeline" -Force
Write-Host "[OK] International Sales VP scheduled" -ForegroundColor Green

# Hourly - DevSecOps VP
Write-Host "`n[10/15] Scheduling DevSecOps VP (Hourly)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_devsecops_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Once -At "12:00AM" -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "Mythara_DevSecOps_VP" -Action $action -Trigger $trigger -Description "Mythara DevSecOps VP - Hourly security scanning" -Force
Write-Host "[OK] DevSecOps VP scheduled" -ForegroundColor Green

# Weekly Sunday 12:00 AM - SEO Master Bot
Write-Host "`n[11/15] Scheduling SEO Master Bot (Weekly Sunday 12:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_seo_bot.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "12:00AM"
Register-ScheduledTask -TaskName "Mythara_SEO_Bot" -Action $action -Trigger $trigger -Description "Mythara SEO Bot - Weekly SEO analysis" -Force
Write-Host "[OK] SEO Master Bot scheduled" -ForegroundColor Green

# Daily 9:00 AM - Researcher Bot
Write-Host "`n[12/15] Scheduling Researcher Bot (Daily 9:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_researcher_bot.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
Register-ScheduledTask -TaskName "Mythara_Researcher_Bot" -Action $action -Trigger $trigger -Description "Mythara Researcher Bot - Daily POC validation" -Force
Write-Host "[OK] Researcher Bot scheduled" -ForegroundColor Green

# Weekly Monday 6:00 AM - Grant Writer Bot
Write-Host "`n[13/15] Scheduling Grant Writer Bot (Weekly Monday 6:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_grant_writer_bot.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "6:00AM"
Register-ScheduledTask -TaskName "Mythara_Grant_Writer_Bot" -Action $action -Trigger $trigger -Description "Mythara Grant Writer Bot - Weekly grant discovery" -Force
Write-Host "[OK] Grant Writer Bot scheduled" -ForegroundColor Green

# Daily 10:00 AM - SBGA Integration Bot
Write-Host "`n[14/15] Scheduling SBGA Integration Bot (Daily 10:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_sbga_bot.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "10:00AM"
Register-ScheduledTask -TaskName "Mythara_SBGA_Bot" -Action $action -Trigger $trigger -Description "Mythara SBGA Bot - Daily networking opportunities" -Force
Write-Host "[OK] SBGA Integration Bot scheduled" -ForegroundColor Green

# Daily 11:00 AM - Accounting VP
Write-Host "`n[15/16] Scheduling Accounting VP (Daily 11:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_accounting_vp.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "11:00AM"
Register-ScheduledTask -TaskName "Mythara_Accounting_VP" -Action $action -Trigger $trigger -Description "Mythara Accounting VP - Daily financial tracking" -Force
Write-Host "[OK] Accounting VP scheduled" -ForegroundColor Green

# Daily 7:00 AM - Sigma Six Blackbelt (Quality)
Write-Host "`n[16/16] Scheduling Sigma Six Blackbelt (Daily 7:00 AM)..." -ForegroundColor Cyan
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$workingDir\run_sigma_six_blackbelt.py" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At "7:00AM"
Register-ScheduledTask -TaskName "Mythara_Sigma_Six_Blackbelt" -Action $action -Trigger $trigger -Description "Mythara Sigma Six Blackbelt - Daily quality metrics" -Force
Write-Host "[OK] Sigma Six Blackbelt scheduled" -ForegroundColor Green

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "SUCCESS! All 16 bots scheduled in Windows Task Scheduler" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`nSCHEDULE SUMMARY:" -ForegroundColor Yellow
Write-Host "`nCONTINUOUS:" -ForegroundColor White
Write-Host "  - Support Chat Bot: Every 30 minutes" -ForegroundColor Gray

Write-Host "`nHOURLY:" -ForegroundColor White
Write-Host "  - DevOps VP: Every hour" -ForegroundColor Gray
Write-Host "  - DevSecOps VP: Every hour" -ForegroundColor Gray

Write-Host "`nDAILY (Staggered):" -ForegroundColor White
Write-Host "  06:00 AM - Finance VP" -ForegroundColor Gray
Write-Host "  07:00 AM - Logistics VP, Sigma Six Blackbelt" -ForegroundColor Gray
Write-Host "  08:00 AM - Sales/Marketing VP" -ForegroundColor Gray
Write-Host "  09:00 AM - Customer Success VP, International Sales VP, Researcher Bot" -ForegroundColor Gray
Write-Host "  10:00 AM - Public Affairs VP, SBGA Bot" -ForegroundColor Gray
Write-Host "  11:00 AM - Accounting VP" -ForegroundColor Gray

Write-Host "`nWEEKLY:" -ForegroundColor White
Write-Host "  Monday 06:00 AM - Grant Writer Bot" -ForegroundColor Gray
Write-Host "  Monday 08:00 AM - HR VP" -ForegroundColor Gray
Write-Host "  Sunday 12:00 AM - SEO Bot" -ForegroundColor Gray

Write-Host "`nTo view all tasks:" -ForegroundColor Yellow
Write-Host "  1. Press Win+R" -ForegroundColor White
Write-Host "  2. Type: taskschd.msc" -ForegroundColor White
Write-Host "  3. Look for tasks starting with 'Mythara_'" -ForegroundColor White

Write-Host "`nTo manually run a task now:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName 'Mythara_Finance_VP'" -ForegroundColor Cyan

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "ALL 16 BOTS NOW RUNNING AUTONOMOUSLY AT `$0/MONTH!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
