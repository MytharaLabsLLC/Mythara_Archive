# Witnessed Journal — v1 prototype

A working product surface for the Soul Cradle emotional chain: a
tamper-evident journaling app where every entry is attested by the
eight assessor-witnesses, whose sealed judgments are hash-chained with
the entry. Stdlib only — no dependencies.

## Run it

```bash
python3 journal_app/server.py
# open http://127.0.0.1:8137
```

## What it does

- **Write** — attest a journal entry. The eight witnesses judge the
  attestation on observable evidence; their sealed judgments are chained
  with the entry. You see the panel verdict (clear / contested / flagged /
  blocked) and which witnesses flagged, with what they cited.
- **Record** — your witnessed history, per name, with hashes.
- **Verify** — re-checks every record seal, every witness seal, every
  chain link. Also downloadable as a full verification report (JSON)
  via **Export** — the chain-of-custody artifact.
- **Pattern analysis** — descriptive heuristics over your record
  (contested rate, volatility, coercion markers). Labeled as heuristic,
  not a diagnosis.

## The contract (shown in the UI)

The journal proves your records are **unaltered** — never that they are
true. Nothing here verifies what you felt. That remains yours.

## v1 limits — read before any real use

- Binds to 127.0.0.1 only. Single local user. **No auth, no TLS.**
- Chain persists to `journal_app/chain_data.json` (created on first write).
- NOT production. Real users need: authentication, TLS, backups, terms
  of service, a legal entity, and attorney review. None of that exists yet.
