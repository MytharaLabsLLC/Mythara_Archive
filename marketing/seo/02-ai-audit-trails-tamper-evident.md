# AI Audit Trails: What "Tamper-Evident" Actually Means

*Vendors throw the phrase around. Here's the mechanics, the limits, and how to tell the real thing from theater.*

"Tamper-evident audit trail" appears in half the AI governance pitches written this year. Most of the products behind the phrase would not survive five minutes of adversarial inspection. Let's fix that — here's what the term actually requires, mechanically.

## The mechanism: hash-chaining

The standard construction is simple:

1. Take the record of an action (what happened, when, the evidence, the judgment).
2. Hash it together with the hash of the *previous* record.
3. Store the resulting hash in the new record.

Now every record is cryptographically bound to all of history. Change one byte of record #412 and its hash changes — which invalidates #413's stored "previous hash," which invalidates #414, and so on down the line. To rewrite history undetected, you'd have to recompute the entire chain from the altered point forward.

Verification is equally simple: recompute the hashes from genesis and check that each link holds. Anyone can do it. That's the point.

## What it gives you — and what it doesn't

**It gives you:** detection. If anyone alters the record after the fact, verification fails, loudly. That's "tamper-evident" — the tampering shows.

**It does not give you:** prevention (someone with full control can recompute a whole chain — which is why you need external anchoring, like publishing checkpoints somewhere the operator can't rewrite), and it does not give you **truth**. A hash chain over lies is a perfectly tamper-evident record of lies.

This is the sentence most vendors won't say: **the chain proves the record is unaltered, not that it was true.** Garbage in, chained garbage out. Any audit-trail product that implies its cryptography proves *what really happened* is misrepresenting its own math. The chain secures the record; witnesses and evidence secure the truth of it. You need both.

## The five tests

Ask these of any "tamper-evident" AI audit trail:

**1. Where's the chaining?** Can the vendor show you, concretely, that each record commits to the previous one? "We use blockchain" is not an answer. "Each entry contains the SHA-256 of the prior entry's canonical serialization" is.

**2. Who holds the genesis?** A chain is only as trustworthy as its starting point and its operator. If one party controls the entire chain and never anchors it anywhere external, they can regenerate it at will. Look for external anchoring — published checkpoints, third-party witnesses, public ledgers.

**3. What's in each link?** A chain of timestamps and "action completed" strings is nearly content-free. Each link should bind the *evidence* (what was observed), the *judgment* (who assessed it, against what rubric), and any *dissent* (who disagreed). The richer the link, the harder it is to fake the history.

**4. Can I verify independently?** If verification requires the vendor's proprietary tool, you don't have tamper-evidence — you have a vendor assertion with extra steps. Real tamper-evidence is verifiable with standard tools by anyone.

**5. What happens on verification failure?** A system that detects tampering and then *continues operating normally* has a decorative chain. Detection must trigger a response: halt, escalate, alert. Otherwise it's theater with cryptography.

## The honest version

Here's our standing offer, and we'd make it to anyone: don't trust the phrase. Trust the mechanism, inspected. Our witness log, emotional chain, and benevolence ledger are each hash-chained, each link binds evidence + judgment + dissent, verification needs nothing proprietary, and a broken chain halts the system.

Read the code. Verify a chain yourself. That's the only pitch we'll make — because it's the only one that survives contact with a skeptic.

---

*The implementation is public at [github.com/herbievelezjr/Mythara_Archive](https://github.com/herbievelezjr/Mythara_Archive) (soul_cradle/). The honest contract is written into the code: unaltered, not true.*
