# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Marketing Bot runner — honest rebuild 2026-09-22.

WHAT IT DOES:
  Scores real prospects from MytharaProspectDatabase with the
  MarketingBot's rule-based lead scoring, queues outreach drafts for
  HOT leads (>70), and pulls the sales-bot training config.

WHAT IT DOES NOT DO:
  No Google Ads, no LinkedIn, no campaigns exist — there are no ad
  accounts connected, so there are no campaign stats to report. The old
  version printed hardcoded "5 clicks, 2 conversions" fiction. That is
  gone. Engagement scoring starts at zero until real engagement data
  exists.
"""

import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_ai_team_free import MarketingBot
from mythara_prospect_database import MytharaProspectDatabase
from outreach_queue import OutreachQueue

GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
if not GOOGLE_AI_API_KEY:
    print("Note: GOOGLE_AI_API_KEY not set — running rule-based scoring (no AI).")


def _revenue_bucket(revenue_range: str) -> str:
    """Map the prospect DB's revenue strings onto the scorer's buckets."""
    m = re.search(r"\$([\d.]+)\s*([TBM])", (revenue_range or "").upper())
    if not m:
        return "<$10M"
    num, unit = float(m.group(1)), m.group(2)
    millions = num * {"T": 1_000_000, "B": 1_000, "M": 1}[unit]
    if millions > 100:
        return ">$100M"
    if millions >= 50:
        return "$50M-$100M"
    if millions >= 10:
        return "$10M-$50M"
    return "<$10M"


def _to_lead(prospect: dict) -> dict:
    return {
        "email": "",  # curated DB has no contact emails — fit scoring only
        "company": prospect.get("company_name", ""),
        "industry": prospect.get("industry", ""),
        "revenue": _revenue_bucket(prospect.get("revenue_range", "")),
        "email_opens": 0,
        "clicked_link": False,
    }


def run_marketing_bot() -> None:
    print(f"MARKETING BOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Mode: rule-based lead scoring over the curated prospect database.")
    print("Campaign stats: none — no ad accounts connected (nothing simulated).")

    bot = MarketingBot()
    db = MytharaProspectDatabase()
    queue = OutreachQueue()

    prospects = db.get_all_prospects()
    print(f"\nProspects evaluated: {len(prospects)}")

    already_queued = {p["title"] for p in queue.list_pending()}
    hot, warm, cold = 0, 0, 0

    print("\nLead scores (fit only — no engagement data yet):")
    for prospect in prospects:
        lead = _to_lead(prospect)
        score = bot.score_lead(lead)
        company = lead["company"]
        if score > 70:
            hot += 1
            tag = "HOT "
            title = f"Hot lead: {company} (score {score})"
            if title not in already_queued:
                queue.queue(
                    kind="email",
                    title=title,
                    body=(
                        f"Company: {company} ({lead['industry']})\n"
                        f"Decision maker: {prospect.get('decision_maker')}\n"
                        f"Website: {prospect.get('website')}\n"
                        f"Fit score: {score}/100 (rule-based, fit only)\n"
                        f"Pain points: {', '.join(prospect.get('pain_points', [])[:3])}\n\n"
                        f"Draft a personalized outreach email for Herb's approval.\n"
                        f"NOTE: no contact email on file — research one before sending.\n"
                    ),
                    meta={"company": company, "lead_score": score,
                          "prospect_id": prospect.get("prospect_id")},
                )
                print(f"   HOT  - {company}: {score}/100 → draft queued")
            else:
                print(f"   HOT  - {company}: {score}/100 → draft already pending")
        elif score > 40:
            warm += 1
            tag = "WARM"
            print(f"   WARM - {company}: {score}/100")
        else:
            cold += 1
            print(f"   COLD - {company}: {score}/100")

    print(f"\nSummary: {hot} hot, {warm} warm, {cold} cold.")

    training_data = bot.train_sales_bot()
    print("\nSales-bot training config (rule-based defaults):")
    print(f"   - Subject lines: {len(training_data['best_performing_subject_lines'])}")
    print(f"   - Send-time rules: {len(training_data['optimal_send_times'])} industries")
    print(f"   - Hot threshold: {training_data['hot_leads_threshold']}")

    print("\nDone. Hot-lead drafts wait in Commercial/outreach_queue/ for approval.")


if __name__ == "__main__":
    run_marketing_bot()
