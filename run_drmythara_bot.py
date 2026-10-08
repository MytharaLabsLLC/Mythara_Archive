# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""DrMythara runner — two modes.

DEMO (offline, no credentials, no network):
  DRMYTHARA_DEMO=1 python3 run_drmythara_bot.py
Runs the scripted end-to-end demo conversation (Commercial/drmythara_demo.py):
throwaway dev database, local stub LLM provider. This is the internal
readiness proof — not a public demo, not medical use.

PRODUCTION (fail-closed):
Reads everything from the environment and refuses to start without it:

  DRMYTHARA_DATA_KEY        Fernet key for the encrypted database
                            (generate with:
                             python3 -c "from cryptography.fernet import Fernet;
                             print(Fernet.generate_key().decode())")
  DRMYTHARA_USER            user ID to sign in as
  DRMYTHARA_PASSWORD        that user's password
  DRMYTHARA_BREAKGLASS_SECRET  (optional) enables break-glass access

No credentials on the command line, no defaults, no demo fallback.
"""

import sys
import os

# Add Commercial directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMERCIAL_PATH = os.path.join(CURRENT_DIR, "Commercial")
if COMMERCIAL_PATH not in sys.path:
    sys.path.insert(0, COMMERCIAL_PATH)

from mythara_drmythara_bot import (
    DrMytharaBot,
    DISCLAIMER,
    CHECKLIST_LABEL,
    MissingDataKeyError,
    DrMytharaAuthenticationError,
    DrMytharaAccountLockedError,
    DrMytharaSessionError,
)


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        print(f"Missing {name}.")
        print(__doc__)
        raise SystemExit(2)
    return value


def _demo() -> None:
    """Offline scripted demo: throwaway dev database, local stub LLM,
    no credentials, no network. Internal readiness proof only."""
    from drmythara_demo import main as demo_main
    demo_main()


def _production() -> None:
    print("DrMythara — your AI wellness companion.")
    print()
    try:
        bot = DrMytharaBot()  # raises MissingDataKeyError without a key
    except MissingDataKeyError as exc:
        print(exc)
        raise SystemExit(2)

    user = _required("DRMYTHARA_USER")
    password = _required("DRMYTHARA_PASSWORD")

    try:
        bot.login(user, password)
    except DrMytharaAccountLockedError as exc:
        print(f"Sign-in failed: {exc}")
        raise SystemExit(2)
    except DrMytharaAuthenticationError:
        print("Sign-in failed: invalid user ID or password.")
        raise SystemExit(2)

    print(bot.introduce())
    print()
    print("Talk to her, or use: record <type> <value> [unit] | "
          "check | screen <text> | summary | quit")
    print("  e.g.  record heart_rate 72 bpm")
    print("  e.g.  record blood_pressure 118/76 mmHg")
    print()
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        low = line.lower()
        if low in ("quit", "exit", "/quit"):
            break
        if low in ("check", "/check"):
            print(bot.wellness_check()["spoken"])
            print()
            continue
        if low in ("summary", "/summary"):
            print(bot.export_doctor_summary())
            print()
            continue
        if low.startswith("record "):
            _do_record(bot, line[len("record "):].strip())
            continue
        if low.startswith("screen "):
            result = bot.symptom_prescreen(line[len("screen "):].strip())
            print(result["spoken"])
            print()
            continue
        try:
            reply = bot.chat(line)
        except DrMytharaSessionError as exc:
            print(f"Session problem: {exc}")
            break
        print(reply["reply"])
        print()
    print(bot.voice.closing() if bot.voice else "Done.")


def _do_record(bot: DrMytharaBot, rest: str) -> None:
    """record heart_rate 72 bpm | record blood_pressure 118/76 mmHg"""
    parts = rest.split()
    if len(parts) < 2:
        print("Usage: record <type> <value> [unit]  "
              "(e.g. record heart_rate 72 bpm)")
        return
    vital_type, raw_value = parts[0], parts[1]
    unit = " ".join(parts[2:]) if len(parts) > 2 else ""
    secondary = None
    if "/" in raw_value:
        head, _, tail = raw_value.partition("/")
        raw_value, secondary = head, tail
    try:
        value = float(raw_value)
        if secondary is not None:
            secondary = float(secondary)
    except ValueError:
        print("The value must be a number, like 72 or 118/76.")
        return
    try:
        result = bot.record_vitals(vital_type, value, unit=unit,
                                   secondary=secondary)
    except ValueError as exc:
        print(f"Not recorded: {exc}")
        return
    print(result["spoken"])
    print()


def main() -> None:
    if os.environ.get("DRMYTHARA_DEMO") == "1":
        _demo()
        return
    _production()


if __name__ == "__main__":
    main()
