# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
LinkedIn Sales Bot — QUARANTINED Selenium attempt (2026-09-22).

⚠️  READ BEFORE RUNNING:
  - WINDOWS ONLY. It drives Microsoft Edge through Herb's own logged-in
    Windows user profile (hardcoded path below). It cannot run on Linux,
    macOS, or any server.
  - REQUIRES THE USER'S OWN SESSION. It automates Herb's personal LinkedIn
    login. Never point it at anyone else's account.
  - ACCOUNT RISK IS REAL. Automated connection requests and messaging
    violate LinkedIn's Terms of Service. LinkedIn detects automation and
    restricts or permanently bans accounts. "Safe limits" and random
    delays reduce but do not remove this risk.
  - NEVER RUN FROM A DATACENTER / VPN / SERVER IP. Automation from a
    datacenter IP is one of the strongest bot signals. Only run from
    Herb's own home machine on his normal residential IP.
  - XPaths are brittle and WILL rot as LinkedIn changes its markup.

Kept because the Connect-clicking flow is a genuine attempt worth
preserving — but it is not a production tool. The honest LinkedIn path
is Commercial/mythara_linkedin_automation_bot.py (planner: drafts only,
human sends).
"""

import sys
import time
import random
from datetime import datetime
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class LinkedInSalesBot:
    """QUARANTINED experiment. Drives Edge through Herb's own logged-in
    session to open LinkedIn pages for manual review. It does not
    reliably automate outreach — accept-detection and messaging are
    unimplemented; login/state checks only verify reachability.
    WINDOWS ONLY. Risks account restriction or permanent ban."""
    
    def __init__(self):
        self.driver = None
        self.sent_today = 0
        self.max_daily_connections = 15  # Safe limit
        
    def start_browser(self):
        """Start browser with existing LinkedIn session."""
        print("🌐 Starting browser...")
        
        # Use Edge with your existing session
        options = webdriver.EdgeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('user-data-dir=C:\\Users\\HVele\\AppData\\Local\\Microsoft\\Edge\\User Data')
        options.add_argument('profile-directory=Default')
        
        self.driver = webdriver.Edge(options=options)
        print("✅ Browser started with your LinkedIn session")
        
    def search_prospects(self, keywords: str, max_results: int = 15):
        """Search for prospects on LinkedIn."""
        print(f"\n🔍 Searching for: {keywords}")
        
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords.replace(' ', '%20')}"
        self.driver.get(search_url)
        
        time.sleep(3)  # Let page load
        
        # Scroll to load more results
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        print(f"✅ Search loaded")
        
    def send_connection_requests(self, message_template: str, target_count: int = 5):
        """Send connection requests with personalized messages."""
        print(f"\n📤 Sending {target_count} connection requests...")
        
        sent_count = 0
        
        try:
            # Find all "Connect" buttons
            connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Invite') or contains(text(), 'Connect')]")
            
            for button in connect_buttons[:target_count]:
                if sent_count >= target_count:
                    break
                
                try:
                    # Get prospect name from nearby elements
                    parent = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'entity-result')]")
                    name_element = parent.find_element(By.XPATH, ".//span[@aria-hidden='true']")
                    full_name = name_element.text
                    first_name = full_name.split()[0] if full_name else "there"
                    
                    # Click Connect button
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                    
                    # Add note
                    try:
                        add_note_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add a note')]"))
                        )
                        add_note_button.click()
                        time.sleep(1)
                        
                        # Personalize message
                        personalized_message = message_template.replace("[First Name]", first_name)
                        
                        note_field = self.driver.find_element(By.XPATH, "//textarea[@name='message']")
                        note_field.send_keys(personalized_message)
                        time.sleep(1)
                        
                        # Send
                        send_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Send')]")
                        send_button.click()
                        
                        sent_count += 1
                        print(f"   ➡️ Connect click attempted: {full_name} (delivery unconfirmed)")
                        
                        # Random delay (human-like behavior)
                        time.sleep(random.randint(5, 10))
                        
                    except:
                        # If can't add note, send without note
                        try:
                            send_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Send now')]")
                            send_button.click()
                            sent_count += 1
                            print(f"   ➡️ Connect click attempted: {full_name} (no note, delivery unconfirmed)")
                            time.sleep(random.randint(5, 10))
                        except:
                            print(f"   ⚠️ Skipped {full_name}")
                            continue
                
                except Exception as e:
                    print(f"   ⚠️ Error with prospect: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error finding prospects: {e}")
        
        print(f"\n➡️ Connect clicks attempted: {sent_count} (delivery unconfirmed)")
        return sent_count
    
    def check_pending_connections(self):
        """UNIMPLEMENTED: programmatic accept-detection was never built.

        Opens the sent-invitations page so Herb can review manually.
        Anything claiming to know who accepted is not implemented here.
        """
        print("\n📬 Checking for new connections...")
        print("   ⚠️  Accept-detection is NOT implemented — manual review required.")

        self.driver.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
        time.sleep(3)

        print("✅ Opened sent invitations. Review in the browser who accepted.")
        
    def send_follow_up_messages(self, message_template: str):
        """UNIMPLEMENTED: automated follow-up messaging was never built.

        Opens the connections page for manual follow-up. This method
        sends nothing.
        """
        print("\n💬 Follow-up messages are MANUAL ONLY — nothing is sent by this bot.")

        # Go to recent connections
        self.driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
        time.sleep(3)

        print("✅ Opened connections. Write follow-ups yourself.")
        
    def daily_outreach(self):
        """QUARANTINED outreach experiment. Clicks Connect in YOUR Edge
        session after explicit consent. Counts below are attempted clicks,
        not confirmed deliveries — LinkedIn can silently drop them, and
        selectors rot. Projections are not made; past acceptance rates
        are unknown."""
        print("="*60)
        print("🚀 LINKEDIN SALES BOT - DAILY OUTREACH (QUARANTINED EXPERIMENT)")
        print("="*60)
        print("   ⚠️  Attempted clicks are reported; LinkedIn delivery is")
        print("       not verifiable from here. No outcome is projected.")
        
        self.start_browser()
        
        # Campaign 1: Banking prospects (SSIP Audit $500)
        self.search_prospects("Chief Risk Officer AI Banking", max_results=15)
        
        message = """Hi [First Name], I'm building tools to help banks prove AI compliance cryptographically. With OCC/CFPB tightening AI regulations, thought our SSIP audit work might interest you. Would love to connect!"""
        
        sent = self.send_connection_requests(message, target_count=5)
        
        # Campaign 2: Healthcare prospects (Enterprise $25k)
        time.sleep(10)
        self.search_prospects("CISO Healthcare AI", max_results=15)
        
        message = """Hi [First Name], I'm working on AI safety validation for healthcare teams. Noticed your AI initiatives — would love to share what we're learning about compliance automation. Connect?"""
        
        sent += self.send_connection_requests(message, target_count=5)
        
        # Campaign 3: Tech prospects (Monthly Sub $300)
        time.sleep(10)
        self.search_prospects("Head of AI SaaS", max_results=15)
        
        message = """Hi [First Name], I'm building tools to help AI teams automate compliance validation. Saw your AI work — thought our API work might be relevant. Would love to connect!"""
        
        sent += self.send_connection_requests(message, target_count=5)
        
        print("\n" + "="*60)
        print(f"✅ DAILY OUTREACH ATTEMPT COMPLETE (quarantined experiment)")
        print(f"   • Connect clicks attempted: {sent}")
        print(f"   • Confirmed deliveries: unknown — LinkedIn does not confirm")
        print(f"   • Expected accepts: not projected (no data)")
        print(f"   • Next run: manual, at your discretion")
        print("="*60)
        
        # Keep browser open for manual review
        print("\n💡 Browser will stay open for you to review")
        print("   Press Ctrl+C to close when done")
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
            self.driver.quit()


def main():
    """Run the LinkedIn sales bot — quarantined, explicit consent required."""

    if not SELENIUM_AVAILABLE:
        print("❌ Selenium is not installed in this environment.")
        print("   This quarantined script also requires Windows + your own Edge profile.")
        return

    if sys.platform != "win32":
        print("❌ REFUSED: this script is Windows-only (it drives your Edge profile).")
        print(f"   Current platform: {sys.platform}")
        print("   Run it on your own Windows machine, on your home network —")
        print("   never from a server or datacenter IP.")
        return

    print("""
╔════════════════════════════════════════════════════════════╗
║   ⚠️  QUARANTINED: LINKEDIN SELENIUM AUTOMATION  ⚠️         ║
║                                                            ║
║  This bot will:                                           ║
║  1. Drive YOUR logged-in Edge/LinkedIn session            ║
║  2. Click Connect buttons automatically                  ║
║                                                            ║
║  RISKS YOU ARE ACCEPTING:                                 ║
║  • LinkedIn may restrict or PERMANENTLY BAN your account ║
║  • "Safe limits" and random delays do NOT make this safe ║
║  • Run ONLY from your home PC on your residential IP     ║
║  • Never run from a server, VPS, or datacenter IP        ║
║  • Selectors rot — expect breakage, verify every run     ║
║                                                            ║
║  The honest alternative: the Outreach Planner drafts      ║
║  connection notes and YOU send them by hand.              ║
╚════════════════════════════════════════════════════════════╝

Type I ACCEPT THE RISK to continue, anything else to cancel: """)

    response = input().strip()

    if response == 'I ACCEPT THE RISK':
        bot = LinkedInSalesBot()
        bot.daily_outreach()
    else:
        print("❌ Cancelled. No browser was started, nothing was sent.")


if __name__ == "__main__":
    main()
