# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner for the canonical Autonomous Sales Bot — honest rebuild 2026-09-22.

WHAT IT DOES:
  1. Loads prospects with real contact emails from
     Commercial/sales_prospects.json (you maintain this file).
  2. Runs each through the canonical sales bot
     (Commercial/mythara_autonomous_sales.py) — the adaptive
     prospect → engagement → invoice pipeline.
  3. Queues every resulting action as a draft in
     Commercial/outreach_queue/ for Herb's approval.

WHAT IT DOES NOT DO:
  It does not send email. It does not auto-invoice. The canonical bot
  produces ACTION DICTS (e.g. {'action': 'send_email', ...}) — this
  runner turns each one into an approval draft. Nothing leaves this
  machine without Herb.

  The curated prospect database (mythara_prospect_database.py) has no
  contact emails on file, so it is used here for the research shortlist
  only — not for outreach.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_autonomous_sales import AutonomousSalesBot
from mythara_prospect_database import MytharaProspectDatabase
from outreach_queue import OutreachQueue

PROSPECTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "sales_prospects.json")


def load_emailed_prospects() -> list:
    """Load real prospects with contact emails. Empty list if none on file."""
    if not os.path.exists(PROSPECTS_FILE):
        return []
    try:
        with open(PROSPECTS_FILE) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    return [p for p in data if isinstance(p, dict) and p.get("email")]


def main() -> None:
    print("AUTONOMOUS SALES BOT RUNNER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Pipeline: prospects → canonical sales bot → approval drafts.")
    print("Sending: none. Every action waits for Herb.\n")

    bot = AutonomousSalesBot()
    queue = OutreachQueue()

    # Research shortlist from the curated DB (no emails on file there).
    db = MytharaProspectDatabase()
    db_prospects = db.get_all_prospects()
    print(f"Curated database prospects (research only, no emails): "
          f"{len(db_prospects)}")
    top = sorted(db_prospects, key=lambda p: p.get("fit_score", 0),
                 reverse=True)[:5]
    print("Top 5 by fit score — research contact emails for these:")
    for p in top:
        print(f"   • {p['company_name']} ({p['industry']}) — "
              f"{p['decision_maker']}")

    # Real outreach list: only prospects with contact emails.
    prospects = load_emailed_prospects()
    print(f"\nProspects with contact emails ({PROSPECTS_FILE}): {len(prospects)}")
    if not prospects:
        print("Nothing to process. To run outreach:")
        print(f"  1. Create {PROSPECTS_FILE}")
        print('  2. Add entries like: '
              '[{"email": "a@company.com", "name": "Ann", '
              '"company": "Acme", "industry": "Banking"}]')

    drafts_queued = 0
    for prospect in prospects:
        result = bot.process_prospect(prospect)
        for action in result["actions_taken"]:
            queue.queue(
                kind="email",
                title=f"Sales action [{action['action']}] → {action['recipient']}",
                body=(f"Recipient: {action['recipient']}\n"
                      f"Action: {action['action']}\n"
                      f"Clause: {action.get('clause', '?')}\n"
                      f"Stage: {result['current_stage']} "
                      f"(score {result['current_score']})\n\n"
                      f"--- draft message ---\n\n{action['message']}\n"),
                meta={"action": action["action"],
                      "recipient": action["recipient"],
                      "clause": action.get("clause"),
                      "stage": result["current_stage"]},
            )
            drafts_queued += 1
        print(f"   • {prospect['email']}: stage={result['current_stage']}, "
              f"score={result['current_score']}, "
              f"actions={len(result['actions_taken'])} → drafts")

    pipeline = bot.get_pipeline_report()
    print("\n" + "=" * 60)
    print("SALES REPORT (canonical bot, persistent state)")
    print("=" * 60)
    print(f"Total prospects: {pipeline['total_prospects']}")
    print(f"Stages: {pipeline['pipeline_stages']}")
    print(f"Closed deals: {pipeline['closed_deals']}")
    print(f"Total revenue: ${pipeline['total_revenue']:,.2f}")
    print(f"\nDrafts queued this run: {drafts_queued}")
    print("Emails sent: 0 — drafts await Herb's approval in "
          "Commercial/outreach_queue/.")


if __name__ == "__main__":
    main()
