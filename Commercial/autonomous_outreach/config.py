# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Autonomous Outreach — configuration.

All knobs in one place. Conservative defaults protect the Gmail account
and the domain reputation; Herb changes them explicitly, never the code.
"""

from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
STATE_DIR = MODULE_DIR / "state"
ESCALATION_DIR = MODULE_DIR / "escalations"

# --- Authority ------------------------------------------------------------
# Herb's grant (2026-09-22, "full auto"): the outreach bot may SEND under
# Herb's name without per-message approval. SCOPED: EMAIL CHANNEL ONLY.
# Recorded in WILL.md (NO_AUTO_SEND exception). Everything else stays
# draft-only.
ALLOWED_CHANNELS = ("email",)

# --- Rate limits (reputation protection) -----------------------------------
MAX_NEW_PROSPECTS_PER_DAY = 10   # first-touch emails
MAX_FOLLOWUPS_PER_DAY = 15       # follow-up emails
MAX_TOTAL_SENDS_PER_DAY = MAX_NEW_PROSPECTS_PER_DAY + MAX_FOLLOWUPS_PER_DAY
MIN_SECONDS_BETWEEN_SENDS = 300  # 5 min floor; actual pacing adds jitter

# --- Kill switch -----------------------------------------------------------
# If this file exists, the scheduler halts IMMEDIATELY — mid-run, no
# exceptions, no "one more send". Herb creates it with:  touch STOP
# (or "stop the outreach" in chat, which the main agent turns into this).
KILL_SWITCH_FILE = MODULE_DIR / "STOP"

# --- Sender ----------------------------------------------------------------
# "dryrun"  — default. Writes .eml files + ledger entries, sends nothing.
# "yahoo"   — real sends via Yahoo SMTP as mythara.engine@yahoo.com. Needs the
#             Yahoo app password in YAHOO_KEY_FILE (0600, one line).
#             Missing file -> SenderBlocked with the exact fix, never silent.
# "gmail"   — real sends via Gmail API (legacy path). BLOCKED until Herb
#             completes the OAuth flow once (see README.md).
#
# Real sends (yahoo/gmail) are ALSO gated on CANSPAM_POSTAL_ADDRESS below:
# cold outreach without a physical postal address violates CAN-SPAM, so
# the run refuses to send until Herb sets it. Dry-run is unaffected.
SENDER_MODE = "dryrun"

# Yahoo SMTP identity. The app password file is created once by Herb and is
# gitignored — it must never be committed, logged, or printed.
YAHOO_FROM_ADDR = "mythara.engine@yahoo.com"
YAHOO_KEY_FILE = STATE_DIR / ".yahoo_app_password"

# Yahoo IMAP (reply ingestion — where responses to our mail actually land).
YAHOO_IMAP_HOST = "imap.mail.yahoo.com"
YAHOO_IMAP_PORT = 993

# CAN-SPAM postal address, printed in every email footer. Herb sets this
# once (his real mailing address). Empty string = real sends stay blocked.
CANSPAM_POSTAL_ADDRESS = ""

# --- Learning ---------------------------------------------------------------
# Epsilon-greedy over message variants (same pattern as the sales bot's
# select_clause). explore_rate: fraction of sends that try a non-champion
# variant so the system keeps learning instead of freezing on a winner.
EXPLORE_RATE = 0.2

# --- Follow-up cadence (days after previous touch, no reply) ----------------
FOLLOWUP_SCHEDULE = (4, 10)   # touch 2 at +4d, touch 3 at +10d, then stop
MAX_TOUCHES = 1 + len(FOLLOWUP_SCHEDULE)

# --- State files (JSONL unless noted) ----------------------------------------
PROSPECTS_FILE = STATE_DIR / "prospects.jsonl"
SEND_LOG_FILE = STATE_DIR / "send_log.jsonl"       # every attempt + outcome
VARIANT_STATS_FILE = STATE_DIR / "variant_stats.json"
DAILY_COUNT_FILE = STATE_DIR / "daily_counts.json"
SUPPRESSION_FILE = STATE_DIR / "suppressions.json"  # unsubscribes, bounces
