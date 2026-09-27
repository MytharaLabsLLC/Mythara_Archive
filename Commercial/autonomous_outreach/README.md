# Outreach — operator-run conversation pipeline

Sends email under Herb's granted signature authority (2026-09-22,
"full auto"). **Email channel only.** Every other bot stays draft-only.

The pitch: **"I build AI that can answer for itself."**
The customer: founders/teams deploying AI agents (Accountable AI builds,
$5–15K project work, paid pilots).

Purpose: start real conversations, not send emails. The machine handles
the mechanical top of the funnel; the operator works the replies.
See PURPOSE.md — it is the document of record.

## Architecture

```
prospects.py    discovery (manual CSV import) + deterministic scoring rubric
research.py     per-prospect briefs — verified facts with sources ONLY.
                The composer may render brief facts and nothing else.
voice.py        fresh human voice, composed per prospect. 3 structural
                variants (direct / mechanism / question) for the learner.
learning.py     epsilon-greedy variant selection (same pattern as the sales
                bot's select_clause). Rewards from observed engagement only.
sender.py       DryRunSender (default, writes .eml, sends nothing) and
                GmailSender (real sends; BLOCKED until OAuth — see below).
sequences.py    follow-up state machine: touch1 -> +4d -> +10d -> done.
                Any reply stops the sequence. Unsubscribe = suppressed forever.
triage.py       inbox reply classification via Yahoo IMAP (where replies
                actually land); hot replies escalate to the operator, who
                answers as Herb. Legacy Gmail API path kept as fallback.
safety.py       THE GATES. Kill switch, channel whitelist, reservoir tier,
                daily caps, suppression list, full witness panel (fail-closed).
run.py          daily scheduler: triage -> follow-ups -> first touches.
config.py       all knobs. Conservative defaults; Herb changes them, not code.
```

## Non-negotiable constraints (survive full-auto)

1. **Witness gate on every send** — full 8-assessor panel via
   `soul_cradle/bot_witness.py`. A BLOCKED verdict never sends.
   A witness *outage* fails **closed** (no send) — pre-send approval no
   longer exists to catch a miss. Before the panel, the final text is
   scanned for manipulation markers (fake scarcity, fabricated proof,
   fake personalization); any hit is declared as deception evidence and
   the panel blocks on it. The panel scores declared evidence, so the
   scan is what makes the declaration honest.
2. **Depleted reservoir halts everything** — `soul_cradle/benevolence.py`
   latitude tier `depleted` stops all sending and escalates to Herb.
3. **Daily caps** — 10 new prospects + 15 follow-ups max, 5-minute minimum
   spacing with jitter. Protects the Gmail account and domain reputation.
4. **Kill switch** — create the file `STOP` in this directory and the
   scheduler halts immediately, mid-run. (`touch STOP`)
   Say "stop the outreach" in chat and the main agent does the same.
5. **Post-send audit** — every send is hash-chained into the witness log
   and the send ledger (`state/send_log.jsonl`). Approval moved from
   pre-send to post-send; the receipts still exist.

## Current status: DRY-RUN

The machine runs end-to-end today in `dryrun` mode: it discovers, researches
(via attached briefs), composes, witnesses, paces, and writes `.eml` files
to `state/dryrun/` plus ledger entries. **It sends nothing.**

### Going live: Yahoo SMTP (needs Herb, once)

The send path is built. The machine sends as `mythara.engine@yahoo.com`
through Yahoo's own SMTP servers — no Gmail, no OAuth dance:

1. At Yahoo: Account Security → 2-Step Verification on → App passwords →
   Generate (name it "Mythara outreach") → copy the 16-character password.
2. Save it to `Commercial/autonomous_outreach/state/.yahoo_app_password`
   (one line, no trailing spaces), then `chmod 600` the file. This file is
   gitignored — it never gets committed, logged, or printed. The same file
   also powers IMAP reply ingestion, so this one step unblocks both
   sending and hearing.
3. Set `CANSPAM_POSTAL_ADDRESS` in `config.py` to Herb's real mailing
   address. Real sends stay blocked until this is set — cold outreach
   without a physical address violates CAN-SPAM.
4. Flip `SENDER_MODE = "yahoo"` in `config.py`.

Until then, `YahooSMTPSender` raises `SenderBlocked` with these exact steps
instead of failing silently. Nothing was hacked around. A legacy Gmail API
path (`SENDER_MODE = "gmail"`) is still in the code as a fallback.

> **Reputation note:** brand-new Gmail accounts that blast cold email get
> flagged. Warm the sending identity first (normal mail for a few weeks),
> keep the conservative caps, and never buy lists. The caps above assume a
> warmed identity.

## Daily operation

```bash
# one cycle (safe to cron daily)
python -m Commercial.autonomous_outreach.run

# add prospects (CSV: name,email,company,role,notes + optional signal cols)
python - <<'EOF'
from Commercial.autonomous_outreach import prospects
print(prospects.import_csv("Commercial/autonomous_outreach/import.csv"))
EOF

# attach a research brief (real facts with sources — never invented)
python - <<'EOF'
from Commercial.autonomous_outreach import prospects, research
d = prospects.add_prospect("Ada Founder", "ada@example.com", company="Acme AI",
    signals={"deploys_ai_agents": True, "team_size_fit": True})
brief = research.build_brief(
    facts=[{"fact": "Acme AI ships a support agent to 200 customers.",
            "source": "acme.ai launch post, 2026-09-01"}],
    reason_for_contact="They ship agents to real users with no visible audit story.",
    unknowns=["pricing", "who owns AI risk internally"])
research.attach_brief(d["id"], brief)
EOF

# review what would send / did send
ls Commercial/autonomous_outreach/state/dryrun/
cat Commercial/autonomous_outreach/state/send_log.jsonl

# the operator brief — what happened, what needs a human, what's broken
cat Commercial/autonomous_outreach/state/operator_brief.md

# hot replies land here for the operator (answered as Herb)
ls Commercial/autonomous_outreach/escalations/

# STOP everything
touch Commercial/autonomous_outreach/STOP
```

## What this does NOT do

- **LinkedIn**: untouched. The Selenium path stays quarantined (account-ban
  risk). LinkedIn remains manual, forever.
- **New APIs**: inbox reads use Yahoo IMAP (stdlib `imaplib`) — where
  replies to the sending identity actually land. The legacy Gmail code
  path stays as fallback.
- **Fake personalization**: structurally impossible — the composer only
  renders brief facts, and a heuristic backstop rejects anything that
  smells like "loved your post".
