"""Daily brief — the top events, ranked by outlet count.

More outlets covering the same event means more tellings to compare,
which is where the projected-vs-shadow analysis has the most to work
with. Each entry is three lines plus a link to its full dossier.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def load_all_summaries(state_dir: Path) -> List[Dict]:
    """Every dossier summary ever written (state/dossiers/*.json)."""
    dossier_dir = Path(state_dir) / "dossiers"
    summaries: List[Dict] = []
    if dossier_dir.exists():
        for p in sorted(dossier_dir.glob("*.json")):
            try:
                summaries.append(json.loads(p.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    return summaries


def build_brief(summaries: List[Dict], state_dir: Path,
                max_events: int = 8) -> Path:
    """Write the daily brief markdown. Returns the brief path."""
    state_dir = Path(state_dir)
    ranked = sorted(summaries,
                    key=lambda s: (len(s["outlets"]), s["article_count"]),
                    reverse=True)[:max_events]
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    lines: List[str] = []
    A = lines.append
    A(f"# Mythara News Network — brief for {today}")
    A("")
    A(f"_On-demand pipeline run. {len(summaries)} event(s) dossiered from "
      "fetched RSS articles; top events ranked by outlet count (more tellings "
      "= more to compare)._")
    A("")
    if not ranked:
        A("No events were dossiered in this run — feeds were unreachable or "
          "returned no articles. Nothing was fabricated to fill the gap.")
    for i, s in enumerate(ranked, 1):
        A(f"## {i}. {', '.join(s['key_terms'][:5])}")
        A("")
        A(f"- **What:** {s['article_count']} article(s) across "
          f"{', '.join(s['outlets'])}")
        div = ", ".join(s["divergent"]) or "none"
        abst = ", ".join(s["abstained"]) or "none"
        A(f"- **Witness signal:** panel {s['panel_verdict'].upper()} — "
          f"gap seen by: {div}; abstained: {abst}")
        A(f"- **Dossier:** [full dossier](../dossiers/{s['event_id']}.md)")
        A("")

    brief_dir = state_dir / "briefs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    path = brief_dir / f"{today}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
