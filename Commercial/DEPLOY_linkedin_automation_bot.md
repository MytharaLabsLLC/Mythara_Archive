
# Deployment Instructions: LinkedIn Automation Bot

## What it does:
Auto-send connection requests and messages

## Expected impact:
- Expected leads/month: 50 (target, not a measured result)

## To deploy:

1. Review code: mythara_linkedin_automation_bot.py
2. Test manually:
   ```
   py -3.11 run_linkedin_automation_bot.py
   ```
3. Schedule task (Windows):
   ```powershell
   $action = New-ScheduledTaskAction -Execute "py" -Argument "-3.11 run_linkedin_automation_bot.py" -WorkingDirectory "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\Commercial"
   $trigger = New-ScheduledTaskTrigger -Daily -At 10am
   Register-ScheduledTask -TaskName "Mythara_linkedin_automation_bot" -Action $action -Trigger $trigger
   ```

## Monitoring:
- Check logs in: mythara_linkedin_automation_bot.log
- Performance tracked by VP Bot

Deployed by: VP Bot
Date: 2025-11-03T08:15:44.652995
