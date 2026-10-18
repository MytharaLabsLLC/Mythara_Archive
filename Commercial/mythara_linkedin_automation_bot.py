# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
LinkedIn Outreach Planner (honest rebuild 2026-09-22)

WHAT IT DOES:
  Reads the curated prospect database (MytharaProspectDatabase), picks
  uncontacted prospects by priority, and writes personalized LinkedIn
  connection-note DRAFTS to Commercial/outreach_queue/ for Herb's approval.

WHAT IT DOES NOT DO — DELIBERATELY:
  It never logs into LinkedIn, never scrapes, never clicks, never sends.
  Automated LinkedIn outreach (bots clicking Connect, auto-messaging)
  violates LinkedIn's Terms of Service and risks a permanent restriction
  of the user's LinkedIn account. This module is architecturally incapable
  of it: there is no browser, no session, no credentials anywhere here.
  Herb reads each draft and sends every connection himself.

Prospect source: Commercial/mythara_prospect_database.py (Herb's curated
target list — company-level research, not verified individual leads).
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_prospect_database import MytharaProspectDatabase
from outreach_queue import OutreachQueue


NOTE_TEMPLATE = """Hi — I run Mythara, where we do cryptographic validation of AI
compliance controls (audit trails you can actually prove).

{company} came up in my research — {pain_note} Worth a connection?
No pitch unless you're curious.

— Herb
"""


class LinkedInAutomationBot:
    """Plans LinkedIn outreach. Drafts only — never sends, never automates."""

    # Caps how many drafts one run may queue. A human still reviews each one.
    max_drafts_per_run = 10

    def __init__(self, queue: Optional[OutreachQueue] = None):
        self.db = MytharaProspectDatabase()
        self.queue = queue or OutreachQueue()
        self.drafts_queued = 0

    def find_prospects(self, priority: str = "critical",
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        REAL prospect source: Herb's curated prospect database.
        Returns uncontacted prospects at the given priority, best fit first.
        These are company-level targets, not scraped individuals.
        """
        prospects = self.db.get_prospects_by_priority(priority)
        fresh = [p for p in prospects if p.get("contact_status") == "not_contacted"]
        return fresh[:limit]

    def draft_connection_note(self, prospect: Dict[str, Any]) -> str:
        """Personalize a connection note from the prospect's recorded pain points."""
        pains = prospect.get("pain_points") or []
        pain_note = (
            f"the {pains[0].lower()} challenge stood out."
            if pains else "your space is one we work in."
        )
        return NOTE_TEMPLATE.format(
            company=prospect.get("company_name", "your company"),
            pain_note=pain_note,
        ).strip()

    def queue_connection_drafts(self,
                                prospects: List[Dict[str, Any]]) -> List[str]:
        """Write one approval draft per prospect. Returns draft file paths."""
        paths = []
        for prospect in prospects[: self.max_drafts_per_run]:
            note = self.draft_connection_note(prospect)
            path = self.queue.queue(
                kind="message",
                title=f"LinkedIn connect: {prospect.get('company_name')}",
                body=(
                    f"Prospect: {prospect.get('company_name')} "
                    f"({prospect.get('industry')})\n"
                    f"Decision maker: {prospect.get('decision_maker')}\n"
                    f"Website: {prospect.get('website')}\n"
                    f"Fit score: {prospect.get('fit_score')}/100\n\n"
                    f"Suggested connection note (edit before sending):\n\n{note}\n"
                ),
                meta={
                    "channel": "linkedin",
                    "prospect_id": prospect.get("prospect_id"),
                    "company": prospect.get("company_name"),
                },
            )
            paths.append(path)
            self.drafts_queued += 1
        return paths

    def run(self, priority: str = "critical", limit: int = 10) -> List[str]:
        """Plan a batch: find prospects, queue drafts. Sends nothing."""
        print("🤖 LinkedIn Outreach Planner")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        prospects = self.find_prospects(priority=priority, limit=limit)
        print(f"   Prospects found in database ({priority}): {len(prospects)}")
        paths = self.queue_connection_drafts(prospects)
        print(f"   Drafts queued for your approval: {len(paths)}")
        print("   Sent: 0 (this bot cannot send — you send each connection)")
        return paths


if __name__ == "__main__":
    bot = LinkedInAutomationBot()
    bot.run()
