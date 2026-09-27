# Outreach — Purpose

Redesigned 2026-09-27. This is the document of record for what this
system is for.

## The old purpose

An autonomous machine that sends cold email under Herb's granted
signature authority. Success was measured in emails sent. It could
send, but it couldn't hear — replies landed in a mailbox nothing read.

## The new purpose

An **operator-run conversation pipeline**. The machine handles the
mechanical top of the funnel — prospecting, research, composing,
sending, tracking. The operator (Cal) runs it, reads the brief, works
the replies, and owns every send.

**Sending is the means. Qualified conversations are the end.**

## Operating model

1. **The machine starts conversations; it never holds them.** Any reply
   that needs a human gets escalated to the operator, who replies as
   Herb. The machine never pretends to be in a conversation.
2. **Nothing sends that the operator can't defend.** Every send passes
   the witness gate, the manipulation scan, daily caps, the suppression
   list, and the kill switch — and real sends additionally require the
   CAN-SPAM postal address. The default is dry-run: nothing leaves the
   machine until Herb says so.
3. **The machine hears now.** Replies are read from the Yahoo inbox via
   IMAP — where responses to mythara.engine@yahoo.com actually land. If the
   inbox can't be read, the run says so loudly instead of assuming
   silence.
4. **The operator gets a brief, not a JSONL dump.** Every run writes
   `state/operator_brief.md`: what sent, what replied, what needs a
   human, what's broken.
5. **Learning is honest.** Variant selection learns only from observed
   outcomes. No invented metrics, no fake social proof, ever.

## Success metrics

- Conversations started (replies classified interested/question)
- Hot leads worked to a call
- Suppressions honored within one cycle

Not: emails sent.

## Standing recommendations (operator's)

- Start at ~5 new prospects/day until reply handling proves out in
  production. The 10/15/25 caps are Herb's knob — this is advice, not a
  change.
- Warm the sending identity with normal mail before any cold volume.
- Never buy lists. Research-first or nothing.

## What still needs Herb (once, then never again)

1. The Yahoo app password in `state/.yahoo_app_password` (sending + IMAP
   login use the same file).
2. `CANSPAM_POSTAL_ADDRESS` in `config.py` — his real mailing address.
   Real sends stay blocked until it's set.
3. Flip `SENDER_MODE = "yahoo"` when 1 and 2 are done.
