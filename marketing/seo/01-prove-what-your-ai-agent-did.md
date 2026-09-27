# How to Prove What Your AI Agent Did

*The accountability problem every agent deployer has, and what a real answer requires.*

Your AI agent just sent 400 emails, queried your database 90 times, and issued two refunds. Prove it.

Not "show me the log." The log is a text file. Anyone with write access can edit it, and in most agent frameworks, that includes the agent itself. Not "show me the dashboard" either — the dashboard is the vendor telling you what the vendor wants you to see.

Proof means something stronger: a record that **cannot be secretly rewritten**, judged by **someone other than the actor**, with a process that **fails closed** when verification isn't possible. Here's what that actually takes, piece by piece.

## 1. Tamper-evident records, not just logs

A log says what happened. A tamper-evident record says what happened *and proves nobody changed it since*. The standard mechanism is hash-chaining: each record contains the hash of the previous one, so altering any entry breaks every link after it.

This doesn't prove the record was true when written. It proves it's unaltered since. That distinction matters — "unaltered, not true" is the honest contract of every real accountability system. Anyone selling you "provably true" AI logs is selling you something cryptography can't deliver.

## 2. Witnesses, not self-reporting

An agent grading its own actions is not oversight. You need independent assessors — separate components with their own rubrics, judging the action against observable evidence.

The bar worth demanding:

- **Multiple independent witnesses**, not one. One witness is one point of failure.
- **Versioned rubrics.** The criteria must be written down, versioned, and inspectable — not vibes.
- **Abstention.** A witness should be able to say "this isn't my domain" instead of guessing. Forced judgments are noise.
- **Fail-closed on missing evidence.** If the evidence isn't there, the verdict is "can't verify" — and the action doesn't proceed on "can't verify."

## 3. Dissent preserved, not averaged

When witnesses disagree, most systems average the scores and move on. That's manufactured consensus — the disagreement, which was the most informative part, vanishes into a number.

Keep the dissent. Record who disagreed, what they found, and why — permanently, in the record itself. And give a single critical finding the power to block: if one witness finds something genuinely wrong, the action stops. That's what witnesses are for.

## 4. A memory of patterns, not just events

Single actions can be gamed. Patterns can't — or at least, they're much harder to fake. Keep a ledger of deeds over time: what the system did, what it declared it intended, and what the witnesses actually observed. Over a long enough history, the pattern reveals what any single act can hide: is this system genuinely serving its principals, or performing benevolence as cover?

Score the pattern, not the moment. And let a bad pattern constrain future latitude — a system with a depleted record of good behavior should face more scrutiny, not less.

## 5. Fail closed, always

The whole structure collapses if the system can shrug and proceed when verification fails. Two rules:

- A critical witness finding **blocks the action**. Not "flags for review." Blocks.
- A witness outage **halts the pipeline**. If the watchers are down, nothing consequential happens until they're back. Silent continuation is the failure mode.

## The checklist

If you're evaluating an "accountable AI" product — ours or anyone's — ask:

1. Can the records be secretly rewritten? (Demand hash-chaining.)
2. Who judges the actions — the actor, or independent witnesses?
3. Are the rubrics public and versioned?
4. What happens to dissent — published or averaged?
5. What happens when verification fails — block, or proceed-and-log?
6. Is there a longitudinal record, or only per-event logs?

If the vendor can't answer all six concretely, you don't have accountability. You have a dashboard.

---

*We're building this in the open at [github.com/herbievelezjr/Mythara_Archive](https://github.com/herbievelezjr/Mythara_Archive) — eight assessor-witnesses, three hash-chained ledgers, dissent preserved, fail-closed. Read the code. Try to fool it.*
