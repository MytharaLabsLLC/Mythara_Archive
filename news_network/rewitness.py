#!/usr/bin/env python3
"""Re-witness all events with the current lens code (e.g. after a voice fix).

Reloads articles, re-clusters, and rewrites every dossier with fresh
witness readings. Chain stays continuous: new records are appended.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from news_network.ingest import load_articles
from news_network.cluster import cluster
from news_network.dossier import write_dossier
from news_network.chain import DossierChain
from news_network.brief import build_brief, load_all_summaries

STATE_DIR = Path(__file__).resolve().parent / "state"


def main() -> int:
    articles = load_articles(STATE_DIR)
    events = cluster(articles)
    print(f"{len(articles)} articles, {len(events)} events")
    chain = DossierChain(STATE_DIR / "chain.jsonl")
    n = 0
    for e in events:
        write_dossier(e, STATE_DIR, chain)
        n += 1
    ok, details = chain.verify()
    print(f"rewrote {n} dossiers, chain verify: {'OK' if ok else 'FAILED'} "
          f"({details['records']} records)")
    brief_path = build_brief(load_all_summaries(STATE_DIR), STATE_DIR)
    print(f"brief at {brief_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
