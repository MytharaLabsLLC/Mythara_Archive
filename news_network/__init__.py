"""Mythara News Network — a news-analysis pipeline.

An RSS ingest bot feeds world and local events to the 8 Soul Cradle
witness-assessors, which produce per-event dossiers contrasting PROJECTED
intent (what actors and outlet framing claim) vs SHADOW intent (what the
evidence pattern suggests). Dissent between witnesses is preserved,
never averaged.

Honesty contract (enforced, not aspirational):
  - Nothing is invented. Every dossier claim traces to a fetched article
    (url + fetched_at). If feeds fail, the pipeline says so and produces
    nothing rather than fabricating.
  - Every dossier is split INGESTED (fetched facts) vs WITNESSED (analysis).
  - This is an on-demand pipeline, not a live service. It runs when run.

Modules:
  sources  — curated, verified RSS/Atom feed list
  ingest   — fetch feeds (stdlib only), store raw articles as JSONL
  cluster  — group articles into events (time window + term overlap)
  evidence — build the structured evidence pack witnesses consume
  witness_news — the 8 assessors' news lenses (rubric extensions)
  dossier  — run witnesses, write markdown dossiers, chain them
  chain    — tamper-evident hash chain for dossiers
  brief    — daily brief assembling top events
  run      — one command: ingest -> cluster -> evidence -> dossiers -> brief
"""

__version__ = "1.0.0"
