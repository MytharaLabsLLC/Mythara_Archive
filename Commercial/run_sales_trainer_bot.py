# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Sales Trainer Bot runner — honest rebuild 2026-09-22.

WHAT IT DOES:
  Runs the SalesTrainerBot's real rule-based conversation analysis
  over a set of conversations and prints the lessons it derives.

WHAT IT DOES NOT DO:
  - The conversations below are ILLUSTRATIVE SAMPLES, not real
    customer data. Any "tactics to amplify/retire" below is derived
    from 3 made-up examples — treat it as a demo of the analysis,
    not as sales advice.
  - update_sales_bot_tactics() only LOGS. It modifies no sales bot.
    The tactic-update path is not implemented.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mythara_ai_team_free import SalesTrainerBot

GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
if not GOOGLE_AI_API_KEY:
    print("Note: GOOGLE_AI_API_KEY not set — running rule-based analysis (no AI).")


def run_sales_trainer_bot() -> None:
    print(f"SALES TRAINER BOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    bot = SalesTrainerBot()

    # ILLUSTRATIVE SAMPLES — not real customer conversations.
    # Replace with real conversation logs before trusting any output.
    sample_conversations = [
        {
            "id": "sample_001",
            "outcome": "closed",
            "messages": ["We can help you save 6 weeks", "That sounds great!",
                         "$500", "Let's do it"],
            "tactics_used": ["urgency", "competitive_pressure"],
        },
        {
            "id": "sample_002",
            "outcome": "lost",
            "messages": ["Only $500", "Too cheap, seems sketchy",
                         "We have great ROI", "No thanks"],
            "tactics_used": ["discount_language"],
        },
        {
            "id": "sample_003",
            "outcome": "closed",
            "messages": ["Your competitors are using this", "Really? Who?",
                         "[example withheld]", "I'm interested"],
            "tactics_used": ["competitive_pressure", "social_proof"],
        },
    ]

    print("\nAnalyzing 3 ILLUSTRATIVE sample conversations "
          "(not real customer data):")

    for conv in sample_conversations:
        analysis = bot.analyze_conversation(conv)
        print(f"\n   Conversation {conv['id']} ({conv['outcome']}):")
        for lesson in analysis.get("lessons", []):
            print(f"      - {lesson['pattern']}: {lesson['recommendation']}")
        if not analysis.get("lessons"):
            print("      - no lessons derived")

    print("\nGenerating training update (from samples only)...")
    training_update = bot.generate_training_update(sample_conversations)

    for tactic in training_update.get("tactics_to_amplify", []):
        print(f"   AMPLIFY: {tactic['tactic']}: {tactic['reason']}")
    for tactic in training_update.get("tactics_to_retire", []):
        print(f"   RETIRE:  {tactic['tactic']}: {tactic['reason']}")
    for tactic in training_update.get("new_tactics_to_test", []):
        print(f"   TEST:    {tactic['tactic']}: {tactic['hypothesis']}")

    print("\nPushing update to sales bot...")
    bot.update_sales_bot_tactics(training_update)
    print("NOTE: update_sales_bot_tactics() only logs — no sales bot was modified.")

    print("\nDone. To get real value: feed real conversation logs, not samples.")


if __name__ == "__main__":
    run_sales_trainer_bot()
