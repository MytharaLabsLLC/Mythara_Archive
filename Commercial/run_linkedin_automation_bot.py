# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner for the LinkedIn Outreach Planner.

Finds prospects in the curated database and queues personalized
connection-note drafts for Herb's approval. Sends nothing.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_linkedin_automation_bot import LinkedInAutomationBot


def main() -> None:
    bot = LinkedInAutomationBot()
    paths = bot.run(priority="critical", limit=10)

    pending = bot.queue.list_pending()
    print(f"\n📬 Drafts awaiting your approval: {len(pending)}")
    for p in pending[-5:]:
        print(f"   • {p['title']}")


if __name__ == "__main__":
    main()
