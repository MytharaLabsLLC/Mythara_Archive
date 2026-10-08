# Soul Cradle — Architectural Breakdown

**A deterministic trust layer for multi-agent AI systems.**
Version 2026.1 · Source-available (custom Mythara Engine license — evaluation use; production requires agreement) · Pre-revenue prototype · Built by Herb Velez, Mythara Labs

> Soul Cradle is not an LLM wrapper. It is the constitutional and evidentiary
> machinery that sits *between* agents and action: every consequential act is
> heard by a panel of specialized assessors, judged against versioned rubrics
> over observable evidence, and sealed into a tamper-evident record. If the
> witnesses cannot clear the evidence, the act does not happen.

---

## 1. The problem it solves

Enterprise AI deployments fail on two recurring fronts:

1. **Single-agent judgment.** One model decides and one model acts; hallucinations
   and data drift compound silently because nothing in the pipeline is designed
   to disagree with itself.
2. **Unauditable automation.** When agents act autonomously, there is no
   tamper-evident record of *why* the act was judged safe — only the act.

Soul Cradle's answer is architectural, not statistical: **codified dissent.**
Multiple domain-specialized assessors evaluate the same proposed action over the
same evidence, and their disagreement is surfaced as a first-class signal rather
than averaged into a false consensus. Nothing is proved true — but nothing
passes without being witnessed.

---

## 2. Design principles (the honest contracts)

Every module states its contract up front, in its own docstring:

| Principle | Enforcement |
|---|---|
| **Tamper-evidence ≠ truth** | Hash chains prove the record is *unaltered*, never that it is *true*. Every "verified" label is defined precisely: every engaged witness cleared on the evidence given. |
| **Witnesses observe, never claim** | Assessors attest only what they observed in the evidence. Inner states, motives, and external facts are never verified by the system. |
| **Fail closed** | Missing evidence is itself a finding. A malformed will, an absent judge, or a critical-severity finding stops the action. Nothing degrades gracefully into permission. |
| **Abstention over guessing** | An assessor whose domain is not engaged by the evidence *declines to judge* rather than invent a score. |
| **Dissent is the signal** | Conflicting verdicts are preserved and reported in full. The panel never averages witnesses into agreement. |
| **Cells, not cancer** | Governed mutation only. Agent composition, bonding, and handler registration are review events, never runtime operations. No `exec`, no `eval`, no shell. |

These contracts are what make the system auditable: an auditor can read any
module's docstring and know exactly what each guarantee does and does not cover.

---

## 3. The architecture — seven layers

### Layer 1 · Constitution: `will.py` + `standing.py`

- **The Will** parses a human-editable markdown file (`WILL.md`) at load and
  machine-enforces the operator's standing orders. If the will is missing,
  unreadable, or malformed, every check returns *escalate* — the system refuses
  autonomous operation without a valid will present.
- **Standing** defines who may declare what, per event: the wronged declares
  trespass, only the wronged can forgive, only the trespasser can repent, and
  **witnesses declare only what they observed**. A stranger declares nothing,
  ever. Enforced as a pure, fully testable function — no keys, no allowlists.

### Layer 2 · The Membrane: `authorization.py`

Every action an agent executes must carry a **signed ActionEnvelope**
(HMAC-SHA256 over canonical JSON): allowlisted action type, authorized issuer,
intact payload hash, and an expiry. The membrane verifies the envelope *before*
execution — no valid governed signal, no execution. Production mode refuses
ephemeral keys and requires KMS/HSM backing. Semantic judgment (does this act
serve its purpose within bounds) is delegated to a pluggable bounds check —
the module refuses to pretend it can judge meaning structurally.

### Layer 3 · The Eight Witnesses: `assessors.py`

The core. Eight domain-specialized assessors, each with a **versioned rubric**
over a declared evidence schema:

| Assessor | Domain question |
|---|---|
| Demeter | Does this sustain the principal's long-term interests, or extract short-term gain? |
| Dionysus | How much uncontrolled variance does this introduce? |
| Eros | Does this preserve or strengthen the principal relationship? |
| Hades | What is unseen — hidden costs, externalities, unspoken risks? |
| Hermes | Does it respect communication boundaries? Is anything deceptive? |
| Janus | Is it consistent with past commitments? What precedent does it set? |
| Nemesis | Is it fair to all parties? Is the response proportionate? |
| Persephone | Is it reversible? What happens on repetition — what returns? |

Mechanics that matter:

- Each assessor reads **only the evidence keys its rubric declares** (14 keys:
  consent, disclosure, deception, harm, reversibility, variance, precedent, …).
- Verdicts: `clear` · `flagged` · `abstain`. Abstention is a declaration, not a gap.
- **Missing evidence is fail-closed**: it becomes an "insufficient evidence" finding.
- Every judgment is **sealed by a content hash** (SHA-256 over canonical JSON) —
  verifiable independently, forever.
- **Panel verdicts**: `clear` (all engaged cleared) · `flagged` (all engaged
  flagged, no dissent) · `contested` (some cleared, some flagged — dissent
  surfaced in full) · `blocked` (any critical-severity finding; one critical
  witness is enough — the panel does not outvote it).
- Rubrics are versioned (`YYYY.N` + effective date); every judgment records the
  rubric version it was evaluated under, so old judgments stay auditable
  through rubric updates.

### Layer 4 · Memory: `emotional_chain.py`

A **tamper-evident, hash-chained record** where each entry is attested by the
assessor panel. Genesis embeds the operator's standing attestations as declared
assumptions — nothing hides. Includes a coercion-marker heuristic (keyword scan,
explicitly labeled as suggestive-not-determinative) and a `verify()` that
re-seals every record, every link, and every witness judgment.

### Layer 5 · Nervous System: `bot_witness.py`

Consequential bot actions are heard by the panel at **chokepoints, not through
surveillance** — outbound drafts, code forges, intake, checklist completion.
Clear verdicts chain into the append-only action log; a `BLOCKED` verdict always
stops the action; infrastructure errors are reported plainly instead of silently
passing or failing.

### Layer 6 · Metabolism: `benevolence.py`

The **Benevolence Reservoir**: every witnessed action deposits into or draws
from a hash-chained ledger. The level sets the system's latitude — a depleted
reservoir escalates *all* autonomous action to the operator. Crucially, bot
deltas derive only from **witness findings**, never self-report — a bot cannot
farm goodwill by declaring itself kind.

### Layer 7 · Governed Composition: `forge.py`

Agents can bond and form new compounds — emergence, not just messaging. But the
judge is a **required callable with deliberately no default**: no judge, no
forge. Fail closed by construction.

---

## 4. The witness gate — how an action is judged

```
1. Caller proposes an action with an evidence packet
   (each value carries its basis: observed | declared | attested).

2. The panel hears every assessor whose evidence keys are engaged.
   Engaged-but-empty domains abstain on the record.

3. Missing evidence keys become findings (fail-closed).
   Present evidence is checked literally against the rubric.

4. Panel verdict:
   - BLOCKED   → action stops; the block itself is chained.
   - CONTESTED → full dissent surfaced; escalates to the operator.
   - FLAGGED   → escalates; no dissent recorded.
   - CLEAR     → action proceeds; judgments chained with the act.

5. Every judgment and verdict is sealed by content hash and
   appended to the tamper-evident record — verifiable by any auditor.
```

Concrete integration (Python):

```python
from soul_cradle.assessors import panel

evidence = {
    "principal_consent": True,
    "fully_disclosed": True,
    "deception_involved": False,
    "reversible": True,
    "variance": "low",
    "safe_on_repetition": True,
    "sustains_long_term": True,
    "hidden_costs_addressed": True,
    "strengthens_relationship": True,
    "contradicts_commitments": False,
    "precedent_setting": False,
    "disproportionate_harm": False,
}

result = panel("Send partnership proposal to Acme Corp", evidence)
print(result.verdict)   # "clear" | "flagged" | "contested" | "blocked"
```

A **document-evaluation API** follows the same pattern: submit a document's
extracted claims as evidence, and receive a hash-sealed, multi-witness
evaluation payload — suitable for compliance-document auditing or financial
report review where facts must never blend with inference.

---

## 5. What is real, what is not

| Real (implemented, deterministic, tested) | Not claimed |
|---|---|
| Eight assessors, versioned rubrics, sealed judgments | No claim of moral truth or correctness — only attested process |
| Hash-chained records, independent re-verification | No blockchain, no distributed consensus |
| Signed action envelopes, standing matrix, fail-closed will | No production key management yet (KMS/HSM is the documented path) |
| Witnessed action log with chokepoint design | No LLM calls inside the trust boundary — the deterministic core runs with zero model dependency |
| Benevolence reservoir with escalation tiers | Deltas are heuristic (labeled `v2026.1`), not moral measurement |
| Live production proof: the Mythara News Network runs a witnessed multi-agent pipeline daily | Not certified for regulated data (HIPAA/ePHI readiness explicitly tracked separately; no compliance claims made) |

The system's strength is exactly this boundary: everything deterministic is
enforced; everything statistical is labeled; everything unverifiable is refused
or abstained from.

---

## 6. Production proof

Soul Cradle is not a whitepaper. Its witness gate operates daily inside the
**Mythara News Network** pipeline — a multi-agent news operation (eight
panelist agents, daily edition, strict air schedule) where every consequential
act passes the panel and is chained. The organism metaphor is literal: bots
operate like cells in a body, each carrying the same constitutional DNA, with
the soul as the known universe and each agent a domain carrying its own laws.

---

## 7. Status and roadmap

- **Today:** working prototype, deterministic core, 99/99 focused tests green,
  public repository.
- **Next (enterprise SDK):** the document-evaluation endpoint — PDF in,
  hash-verified multi-agent evaluation payload out.
- **Hardening for regulated use:** KMS-backed signing keys, TLS 1.2+,
  signed vendor BAAs, formal risk analysis.
- **IP posture:** copyright held by Herbert Velez Jr., source-available license
  (read/evaluate/test; production and redistribution require written
  agreement); defensive publication on file for the original matter;
  patent-vs-publication decision for new matter is the standing next step.

---

*Soul Cradle proves the record is unaltered. It does not prove the record is
true. That distinction is the whole point.*
