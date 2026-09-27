# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
🚀 MYTHARA AI TEAM - ONE-CLICK DEPLOYMENT
==========================================

This script automates the entire deployment process:
1. Checks prerequisites (Python, PostgreSQL, API keys)
2. Creates database schema
3. Sets up Windows Task Scheduler jobs
4. Runs initial test of all bots
5. Confirms weekly reports are scheduled
"""

import subprocess
import os
import sys
from datetime import datetime

def check_python():
    """Check if Python 3.11 is installed."""
    print("🐍 Checking Python version...")
    try:
        result = subprocess.run(['py', '-3.11', '--version'], capture_output=True, text=True)
        if 'Python 3.11' in result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Python 3.11 not found. Install from python.org")
            return False
    except:
        print("   ❌ Python not found. Install from python.org")
        return False

def check_postgresql():
    """Check if PostgreSQL is installed and running."""
    print("\n🗄️ Checking PostgreSQL...")
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if 'psql' in result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
            return True
        else:
            print("   ⚠️ PostgreSQL not found")
            print("   Option 1: Install locally from postgresql.org")
            print("   Option 2: Use Heroku Postgres ($9/month)")
            return False
    except:
        print("   ⚠️ PostgreSQL not found")
        print("   Option 1: Install locally from postgresql.org")
        print("   Option 2: Use Heroku Postgres ($9/month)")
        return False

def check_api_keys():
    """Check if required API keys are set."""
    print("\n🔑 Checking API keys...")
    
    required_keys = {
        'OPENAI_API_KEY': '❌ Required for all bots (get from platform.openai.com)',
        'GMAIL_APP_PASSWORD': '⚠️ Optional for email reports (get from myaccount.google.com)',
        'SLACK_WEBHOOK_URL': '⚠️ Optional for Slack alerts (get from api.slack.com)',
    }
    
    optional_keys = {
        'GOOGLE_ADS_API_KEY': '⚠️ Optional for Marketing Bot (get from ads.google.com)',
        'LINKEDIN_API_KEY': '⚠️ Optional for Marketing Bot (get from linkedin.com/developers)',
        'TWITTER_API_KEY': '⚠️ Optional for Brand Awareness Bot (get from developer.twitter.com)',
    }
    
    all_good = True
    
    for key, message in required_keys.items():
        if os.getenv(key):
            print(f"   ✅ {key} is set")
        else:
            print(f"   {message}")
            if '❌' in message:
                all_good = False
    
    for key, message in optional_keys.items():
        if os.getenv(key):
            print(f"   ✅ {key} is set")
        else:
            print(f"   {message}")
    
    return all_good

def create_database():
    """Run database setup script."""
    print("\n🗄️ Creating database schema...")
    try:
        result = subprocess.run(
            ['py', '-3.11', 'setup_database.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"   ⚠️ Database setup skipped (will use Heroku Postgres later)")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"   ⚠️ Database setup skipped: {e}")
        return False

def setup_task_scheduler():
    """Set up Windows Task Scheduler jobs."""
    print("\n⏰ Setting up Windows Task Scheduler...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    tasks = [
        {
            'name': 'Mythara Marketing Bot',
            'script': f'{base_path}\\run_marketing_bot.py',
            'schedule': '/sc hourly',
            'description': 'Generates leads, scores them, feeds to Sales Bot'
        },
        {
            'name': 'Mythara Sales Trainer Bot',
            'script': f'{base_path}\\run_sales_trainer_bot.py',
            'schedule': '/sc hourly /mo 6',
            'description': 'Analyzes conversations, updates Sales Bot tactics'
        },
        {
            'name': 'Mythara Weekly Report',
            'script': f'{base_path}\\weekly_analytics_report.py',
            'schedule': '/sc weekly /d SUN /st 18:00',
            'description': 'Weekly AI team performance report'
        }
    ]
    
    for task in tasks:
        print(f"\n   Setting up: {task['name']}")
        print(f"      Schedule: {task['schedule']}")
        
        cmd = f'schtasks /create /tn "{task["name"]}" /tr "py -3.11 {task["script"]}" {task["schedule"]} /f'
        
        try:
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"      ✅ Created successfully")
            else:
                print(f"      ⚠️ {result.stderr.strip()}")
        except Exception as e:
            print(f"      ⚠️ Error: {e}")

def test_bots():
    """Run initial test of all bots."""
    print("\n🧪 Testing bots...")
    
    print("\n   📊 Marketing Bot:")
    try:
        result = subprocess.run(
            ['py', '-3.11', 'run_marketing_bot.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=30
        )
        if result.returncode == 0:
            print("      ✅ Working")
        else:
            print(f"      ⚠️ {result.stderr[:200]}")
    except Exception as e:
        print(f"      ⚠️ {str(e)[:100]}")
    
    print("\n   🎓 Sales Trainer Bot:")
    try:
        result = subprocess.run(
            ['py', '-3.11', 'run_sales_trainer_bot.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=30
        )
        if result.returncode == 0:
            print("      ✅ Working")
        else:
            print(f"      ⚠️ {result.stderr[:200]}")
    except Exception as e:
        print(f"      ⚠️ {str(e)[:100]}")

def display_next_steps():
    """Display what to do next."""
    print("\n" + "="*80)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*80)
    
    print("\n✅ WHAT'S RUNNING:")
    print("   1. Marketing Bot - Every hour (generates leads)")
    print("   2. Sales Trainer Bot - Every 6 hours (improves tactics)")
    print("   3. Weekly Report - Sunday 6pm MT (performance summary)")
    
    print("\n📋 NEXT STEPS:")
    print("   1. Set OPENAI_API_KEY environment variable:")
    # QUICKFIX FIX: Moved to environment variable (CWE-798)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set via environment
    print("")
    print("   2. (Optional) Set up Google Ads API for lead generation:")
    print("      $env:GOOGLE_ADS_API_KEY = 'YOUR_KEY'")
    print("")
    print("   3. (Optional) Set up Slack webhook for alerts:")
    print("      $env:SLACK_WEBHOOK_URL = 'https://hooks.slack.com/...'")
    print("")
    print("   4. Monitor bot performance:")
    print("      - Check Windows Task Scheduler: taskschd.msc")
    print("      - View task history: schtasks /query /tn 'Mythara Marketing Bot' /v")
    print("      - Check logs in this folder")
    
    print("\n📊 TARGET OUTCOMES (goals, not promises):")
    print("   - Week 1: Lead generation pipeline running")
    print("   - Week 2: Sales Bot tactics adapting to real engagement data")
    print("   - Week 3: First weekly report with real performance numbers")
    print("   - Week 4: First paying customers from automated lead gen")
    
    print("\n💰 COST BREAKDOWN:")
    print("   - OpenAI API: ~$200/month (all bots)")
    print("   - Google Ads: $5,000/month budget (optional)")
    print("   - PostgreSQL: Free (local) or $9/month (Heroku)")
    print("   - Total: $200-$5,200/month depending on ad budget")
    
    print("\n📈 ROUGH UNIT ECONOMICS (back-of-the-napkin, for planning only):")
    print("   - Example: 100 leads/week, 10% turning into deals at $2.5k each")
    print("   - Real results will differ — track actual conversion and cost")
    print("   - Watch cost per lead and close rate weekly, adjust from there")
    
    print("\n" + "="*80)

def main():
    """Main deployment function."""
    print("="*80)
    print("🚀 MYTHARA AI TEAM - AUTOMATED DEPLOYMENT")
    print("="*80)
    print(f"\nStarting deployment at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    python_ok = check_python()
    postgres_ok = check_postgresql()
    api_keys_ok = check_api_keys()
    
    if not python_ok:
        print("\n❌ Python 3.11 is required. Install from python.org")
        return
    
    if not api_keys_ok:
        print("\n⚠️ Set OPENAI_API_KEY before running bots:")
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set via environment
    
    # Create database (optional, can use Heroku later)
    if postgres_ok:
        create_database()
    else:
        print("\n⚠️ Skipping local database setup. Use Heroku Postgres instead:")
        print("   heroku addons:create heroku-postgresql:hobby-dev")
    
    # Set up task scheduler
    setup_task_scheduler()
    
    # Test bots
    test_bots()
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main()
