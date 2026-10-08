# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""Dr Mythara — scripted end-to-end demo conversation.

Runs with NO credentials and NO network: throwaway dev database,
local stub LLM provider. This is the internal readiness proof, not a
public demo.

Scenes:
  1. greeting (honest intro + disclosure)
  2. record vitals (normal readings)
  3. wellness check (all clear + care council)
  4. more readings (patterns: rising resting HR, short sleep)
  5. wellness check (nudges, voiced clinically)
  6. symptom pre-screen (emergency -> direct escalation)
  7. conversational chat (stub LLM path)
  8. "bring to your doctor" export + ledger chain verification

Run:  python3 Commercial/drmythara_demo.py
"""

import os
import sys
import tempfile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Stub LLM: local only, no network, no API key, no ePHI leaves.
os.environ["DRMYTHARA_LLM_PROVIDER"] = "stub"

from mythara_drmythara_bot import DrMytharaBot


def scene(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)
    print()


def main() -> None:
    tmpdir = tempfile.mkdtemp(prefix="drmythara-demo-")
    bot = DrMytharaBot(dev_mode=True,
                       db_path=os.path.join(tmpdir, "demo.db"))
    print("Dr Mythara demo — throwaway database at", tmpdir)
    bot.create_user("demo", "demo-password-1234", role="admin")
    bot.login("demo", "demo-password-1234")

    # -- 1. greeting -------------------------------------------------------
    scene("1 · She introduces herself")
    print(bot.introduce())

    # -- 2. record vitals ---------------------------------------------------
    scene("2 · Recording vitals")
    for vt, val, unit, extra in [
        ("heart_rate", 68, "bpm", {}),
        ("blood_pressure", 118, "mmHg", {"secondary": 76}),
        ("temperature", 98.6, "°F", {}),
        ("spo2", 98, "%", {}),
    ]:
        r = bot.record_vitals(vt, val, unit=unit, **extra)
        print(r["spoken"])
    for _ in range(7):
        bot.record_vitals("sleep_hours", 7.5, unit="h")
    for _ in range(5):
        bot.record_vitals("steps", 8000, unit="steps")

    # -- 3. wellness check: all clear ---------------------------------------
    scene("3 · Wellness check — steady week")
    result = bot.wellness_check()
    print(result["spoken"])
    print(f"\n(council verdict: {result['council_verdict']})")

    # -- 4. patterns emerge --------------------------------------------------
    scene("4 · A week later: resting HR climbing, sleep slipping")
    bot.record_vitals("heart_rate", 68, unit="bpm",
                      taken_at="2026-09-20T08:00:00+00:00")
    bot.record_vitals("heart_rate", 82, unit="bpm",
                      taken_at="2026-09-28T09:00:00+00:00")
    for _ in range(7):
        bot.record_vitals("sleep_hours", 5.2, unit="h")

    # -- 5. wellness check: nudges -------------------------------------------
    scene("5 · Wellness check — patterns worth discussing")
    result = bot.wellness_check()
    print(result["spoken"])
    print(f"\n(council verdict: {result['council_verdict']})")
    for o in result["observations"]:
        if o["severity"] in ("nudge", "escalate"):
            print(f"\n  reasoning for '{o['title']}':")
            for line in o["reasoning"]:
                print(f"    · {line}")

    # -- 6. symptom pre-screen: emergency ------------------------------------
    scene("6 · 'I have chest pressure and I can't breathe'")
    screen = bot.symptom_prescreen(
        "I have chest pressure and I can't breathe")
    print(screen["spoken"])

    # -- 7. conversational chat (stub LLM) ------------------------------------
    scene("7 · Conversation")
    chat = bot.chat("What are some gentle ways to wind down before bed?")
    print(chat["reply"])
    print(f"\n(provider={chat['provider']} "
          f"sent_to_provider={chat['sent_to_provider']} "
          f"escalated={chat['escalated']})")

    # -- 8. export + chain verification ---------------------------------------
    scene("8 · Bring-to-your-doctor summary + ledger check")
    summary = bot.export_doctor_summary()
    print(summary[:2200])
    if len(summary) > 2200:
        print("\n  … (truncated for the demo)")

    print()
    print("Dr Mythara demo complete — no errors, no network, no credentials.")


if __name__ == "__main__":
    main()
