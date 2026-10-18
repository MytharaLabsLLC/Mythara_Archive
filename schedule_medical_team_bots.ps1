# Copyright © 2026 Mythara Labs LLC. All rights reserved.

<#
.SYNOPSIS
    Schedule DrMythara Medical Team Suite bots in Windows Task Scheduler

.DESCRIPTION
    Automates scheduling of all medical team bots:
    - Essential bots (triage, compliance, clinical documentation, crisis response)
    - Non-essential support bots (scheduling, education, QA, admin, resources, training)
    
    Creates Windows Task Scheduler jobs with appropriate intervals

.NOTES
    Run this script as Administrator
    Tasks will run under current user context
#>

# Require Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script must be run as Administrator. Please re-run with elevated privileges."
    exit 1
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "DrMythara Medical Team Suite - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Get current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "python"

# Test Python availability
try {
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python and add to PATH." -ForegroundColor Red
    exit 1
}

# Task definitions
$tasks = @(
    @{
        Name = "DrMythara_MedicalTeamSuite_Hourly"
        Description = "DrMythara Medical Team Suite - Comprehensive health check (hourly)"
        Script = "run_medical_team_suite.py"
        Interval = "Hourly"
        RepetitionInterval = "PT1H"  # Every 1 hour
    },
    @{
        Name = "DrMythara_ComplianceMonitor_15Min"
        Description = "DrMythara Compliance Monitor - Critical compliance checks (every 15 minutes)"
        Script = "run_drmythara_bot.py"
        Interval = "15Minutes"
        RepetitionInterval = "PT15M"  # Every 15 minutes
    },
    @{
        Name = "DrMythara_TriageMonitor_Daily"
        Description = "DrMythara Triage Monitor - Daily triage case review"
        Script = "run_medical_team_suite.py"
        Interval = "Daily"
        RepetitionInterval = $null
        DailyTime = "08:00"  # 8 AM daily
    },
    @{
        Name = "DrMythara_QualityAssurance_Weekly"
        Description = "DrMythara Quality Assurance - Weekly quality metrics review"
        Script = "run_medical_team_suite.py"
        Interval = "Weekly"
        RepetitionInterval = $null
        WeeklyDay = "Monday"
        WeeklyTime = "09:00"  # 9 AM every Monday
    }
)

Write-Host "📋 Creating scheduled tasks..." -ForegroundColor Yellow
Write-Host ""

foreach ($task in $tasks) {
    Write-Host "  Creating: $($task.Name)" -ForegroundColor Cyan
    
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
    
    if ($existingTask) {
        Write-Host "    ⚠️  Task already exists. Removing..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false
    }
    
    # Build command
    $scriptFullPath = Join-Path $scriptPath $task.Script
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptFullPath`"" -WorkingDirectory $scriptPath
    
    # Build trigger based on interval type
    $trigger = $null
    
    if ($task.Interval -eq "Hourly") {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1)
    }
    elseif ($task.Interval -eq "15Minutes") {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 15)
    }
    elseif ($task.Interval -eq "Daily") {
        $trigger = New-ScheduledTaskTrigger -Daily -At $task.DailyTime
    }
    elseif ($task.Interval -eq "Weekly") {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $task.WeeklyDay -At $task.WeeklyTime
    }
    
    # Task settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable:$false `
        -MultipleInstances IgnoreNew
    
    # Register task
    try {
        Register-ScheduledTask `
            -TaskName $task.Name `
            -Description $task.Description `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -User $env:USERNAME `
            -ErrorAction Stop | Out-Null
        
        Write-Host "    ✅ Task created successfully" -ForegroundColor Green
        Write-Host "       Interval: $($task.Interval)" -ForegroundColor Gray
        
        if ($task.DailyTime) {
            Write-Host "       Time: $($task.DailyTime)" -ForegroundColor Gray
        }
        if ($task.WeeklyDay) {
            Write-Host "       Day: $($task.WeeklyDay) at $($task.WeeklyTime)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "    ❌ Failed to create task: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Summary
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 Task Scheduler Setup Complete" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Created tasks:" -ForegroundColor Yellow

foreach ($task in $tasks) {
    $scheduledTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
    if ($scheduledTask) {
        Write-Host "  ✅ $($task.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($task.Name)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Management commands:" -ForegroundColor Yellow
Write-Host "  View all tasks:" -ForegroundColor Cyan
Write-Host "    Get-ScheduledTask | Where-Object {`$_.TaskName -like 'DrMythara*'}" -ForegroundColor Gray
Write-Host ""
Write-Host "  Run a task manually:" -ForegroundColor Cyan
Write-Host "    Start-ScheduledTask -TaskName 'DrMythara_MedicalTeamSuite_Hourly'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Disable a task:" -ForegroundColor Cyan
Write-Host "    Disable-ScheduledTask -TaskName 'DrMythara_MedicalTeamSuite_Hourly'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Enable a task:" -ForegroundColor Cyan
Write-Host "    Enable-ScheduledTask -TaskName 'DrMythara_MedicalTeamSuite_Hourly'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Remove all DrMythara tasks:" -ForegroundColor Cyan
Write-Host "    Get-ScheduledTask | Where-Object {`$_.TaskName -like 'DrMythara*'} | Unregister-ScheduledTask -Confirm:`$false" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
