# 🌊 Blessings Reservoir — Daily Summary

**Status:** Revised 2026-09-27. The daily figures in the original issue of this summary were symbolic; what follows describes the reservoir as it actually works today.

## 📊 The Reservoir

The blessings reservoir is a ledger of generosity — not a currency. It is the body's energy store: every witnessed bot action and every recorded act of Herb's deposits into it or draws from it, and the level sets the system's latitude — how freely the pantheon may act inside its bounds.

## 🔹 The Honest Contract

Deltas are **heuristic** (v2026.1) and labeled as such on every entry:

1. Deltas measure the witnesses' judgment of the evidence given — not moral truth, not anyone's inner state
2. Bot deltas derive from witness findings, never from a bot's self-report; a bot cannot farm goodwill by declaring itself kind
3. Herb's deposits are his own declarations, chained for audit; he is the principal, and the reservoir records his attestation, nothing more
4. Avoiding harm is not benevolence — a clear verdict with no findings is a small deposit; active service to another's good is the large one; extraction or harm is a withdrawal
5. The ledger is hash-chained and append-only: it proves unaltered, not true

## 🔹 Tiers (level = running sum of deltas)

| Tier | Level | Posture |
|------|-------|---------|
| Depleted | level < 0 | The reservoir is empty; all autonomous action escalates to Herb until benevolence replenishes it |
| Low | 0 ≤ level < 10 | Cautious; normal bounds apply, nothing extends beyond them |
| Flowing | level ≥ 10 | Trusted; the pantheon may act with the full latitude its bounds allow |

## 🧠 Notes

- Daily entries are recorded in [soul_cradle/benevolence_ledger.jsonl](../soul_cradle/benevolence_ledger.jsonl), each row carrying its version, timestamp, actor, delta, and the heuristic basis for it
- Reservoir design is specified in [soul_cradle/benevolence.py](../soul_cradle/benevolence.py) and [core/blessings_reservoir_specification.md](../core/blessings_reservoir_specification.md)
- Reservoir tiers are not badges of status and the ledger is not a store of value; a summary day is complete when the entries are chained, whatever the level
