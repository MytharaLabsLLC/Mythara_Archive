# Your AI Agents Have a Receipts Problem

*They act. You can't prove what they did. Here's the gap, what fills it, and what to demand from anyone selling you "agent accountability."*

The agent era arrived fast. Frameworks everywhere, agents sending emails, writing code, querying databases, talking to customers. Impressive — and underneath it, a hole:

**Nobody can prove what any of these agents did.**

Ask your vendor for proof — not a dashboard, not a CSV export, *proof* — of what their agent did last Tuesday at 2pm, and watch what happens. You'll get a log file. Log files are text. Text can be edited. By the vendor. By your own engineers. In some architectures, by the agent itself.

This is the receipts problem, and it's about to become everyone's problem: yours when the auditor asks, your customer's when their data is involved, your lawyer's when something goes wrong.

## Why this is suddenly urgent

Three forces converging:

1. **Agents touch the real world now.** Email, money, customer data, production systems. The blast radius of an unaccounted action keeps growing.
2. **Regulators are waking up.** AI audit requirements are tightening across finance, healthcare, and insurance. "Our vendor has logs" will not survive a serious examination.
3. **The frameworks don't solve it.** Every major agent framework gives you observability — traces, spans, logs. Observability is not accountability. Observability tells you what the system *claims* happened. Accountability tells you what happened *in a way no one can secretly rewrite*, judged by *someone other than the actor*.

## What actually fills the gap

Not another dashboard. A witness layer — infrastructure that sits beside your agents and does four things:

**Watches independently.** Separate assessors, separate rubrics, judging actions against observable evidence. Not the agent reporting on itself.

**Records tamper-evidently.** Hash-chained records, each bound to the last. Verification with standard tools, by anyone — not the vendor's proprietary viewer.

**Preserves disagreement.** When assessors disagree, the dissent goes in the record permanently. Averaged oversight is theater.

**Fails closed.** A critical finding blocks the action. A dead witness halts the pipeline. The system never shrugs and proceeds.

And it keeps a longitudinal ledger — because one verified action is an anecdote, and a thousand are a pattern.

## The build-vs-buy question

You have three options:

**Build it yourself.** Possible, and the primitives are public (hash-chaining is decades old; the design patterns are documented — including in our public repo). Budget real engineering time: the mechanics are straightforward, the edge cases (what counts as evidence, who watches the watchers, how dissent resolves) are where the work lives.

**Buy a sidecar.** A drop-in accountability layer for your existing agents — this is the product category forming right now. Evaluate ruthlessly with the checklist below.

**Do nothing.** This is also a choice, with a price: the first time an auditor, a customer, or a court asks what your agent did, "we have logs" will be your entire defense. Plan accordingly.

## The evaluation checklist

For any accountability product — ours, anyone's:

1. **Tamper-evidence:** hash-chained? Independently verifiable? Externally anchored?
2. **Independent witnesses:** who judges — the actor or separate assessors? Rubrics public and versioned?
3. **Dissent:** published or averaged? Can one critical finding block?
4. **Fail-closed:** what happens when verification fails — halt or proceed-and-log?
5. **Longitudinal:** per-event only, or a pattern ledger over time?
6. **Honest contract:** does the vendor distinguish "unaltered" from "true"? If they claim their chain proves what *really happened*, they're overselling their own math.

## The uncomfortable truth

The industry's accountability model right now is "trust us" — from vendors whose entire business depends on you not looking too closely. That worked when AI wrote poems. It doesn't work when AI moves money.

Receipts aren't optional anymore. They're infrastructure. Build them, buy them, or be ready to explain their absence.

---

*We're building the witness layer in the open: eight assessor-witnesses, three hash-chained ledgers, dissent preserved, fail-closed — at [github.com/herbievelezjr/Mythara_Archive](https://github.com/herbievelezjr/Mythara_Archive). No pitch beyond that. Inspect it.*
