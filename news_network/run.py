"""Mythara News Network — one command to run the whole pipeline.

    python3 -m news_network.run            # from the repo root
    python3 news_network/run.py            # also works

Steps: ingest -> cluster -> evidence -> dossiers (+chain) -> brief.
Prints a short human-readable summary. If no articles could be fetched,
it says so plainly and produces nothing rather than fabricating.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `python3 news_network/run.py` work as well as `-m news_network.run`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from news_network.sources import all_sources  # noqa: E402
from news_network.ingest import ingest, load_articles  # noqa: E402
from news_network.cluster import cluster  # noqa: E402
from news_network.dossier import write_dossier  # noqa: E402
from news_network.chain import DossierChain  # noqa: E402
from news_network.brief import build_brief  # noqa: E402

STATE_DIR = Path(__file__).resolve().parent / "state"


def main() -> int:
    print("Mythara News Network v1 — pipeline run")
    print("=" * 50)

    # 1. ingest
    print("\n[1/5] Ingesting feeds…")
    report = ingest(all_sources(), STATE_DIR)
    ok_feeds = [f for f in report["feeds"] if not f["error"]]
    print(f"  {report['new_articles']} new articles "
          f"({len(ok_feeds)}/{len(report['feeds'])} feeds ok)")
    for f in report["failed"]:
        print(f"  FAILED {f['outlet']}: {f['error'][:90]}")

    articles = load_articles(STATE_DIR)
    print(f"  {len(articles)} articles total in store")
    if not articles:
        print("\nNo articles available — feeds unreachable or empty. "
              "Nothing fabricated; run again when feeds respond.")
        return 1

    # 2. cluster
    print("\n[2/5] Clustering into events…")
    events = cluster(articles)
    multi = [e for e in events if e["article_count"] > 1]
    print(f"  {len(events)} events ({len(multi)} covered by 2+ articles)")

    # 3-4. evidence + dossiers (+chain)
    print("\n[3/5] Building evidence packs, hearing witnesses, chaining…")
    chain = DossierChain(STATE_DIR / "chain.jsonl")
    already = {r.event_id for r in chain.records if r.event_id != "GENESIS"}
    summaries = []
    skipped = 0
    for e in events:
        if e["id"] in already:
            skipped += 1
            continue
        s = write_dossier(e, STATE_DIR, chain)
        summaries.append(s)
        div = ",".join(s["divergent"]) or "-"
        print(f"  {e['id']} [{s['panel_verdict']:9s}] "
              f"{s['article_count']:2d} arts / {len(s['outlets'])} outlets "
              f"gap:{div} :: {', '.join(s['key_terms'][:4])}")
    if skipped:
        print(f"  skipped {skipped} event(s) already dossiered")

    ok, details = chain.verify()
    print(f"  chain verify: {'OK' if ok else 'FAILED'} "
          f"({details['records']} records)")

    # 5. brief — from ALL dossiered events, not just this run's
    print("\n[4/5] Assembling daily brief…")
    from news_network.brief import load_all_summaries  # noqa: E402
    brief_path = build_brief(load_all_summaries(STATE_DIR), STATE_DIR)
    print(f"  wrote {brief_path}")

    print("\n" + "=" * 50)
    from news_network.brief import load_all_summaries as _all  # noqa: E402
    total = len(_all(STATE_DIR))
    contested = sum(1 for s in _all(STATE_DIR) if s["panel_verdict"] == "contested")
    print(f"Done: {len(summaries)} new dossier(s), {total} total, "
          f"{contested} contested, brief at {brief_path}")
    print("On-demand run — not a live service. Re-run to refresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
