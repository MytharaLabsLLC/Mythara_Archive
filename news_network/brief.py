"""Daily brief — the top events, ranked by outlet count.

More outlets covering the same event means more tellings to compare,
which is where the reporters have the most to work with. Each entry
is a short read plus a link to its full dossier.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .witness_news import VERDICT_WORDS


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


def _signal_line(s: Dict) -> str:
    word = VERDICT_WORDS[s["panel_verdict"]]
    div = ", ".join(s["divergent"])
    al = ", ".join(s["aligned"])
    abst = ", ".join(s["abstained"])
    bits = []
    if div:
        bits.append(f"{div} pushed back")
    if al:
        bits.append(f"{al} checked out")
    if abst:
        bits.append(f"{abst} sat it out")
    return f"Our reporters read it **{word}** — " + "; ".join(bits) + "."


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
    A(f"_On-demand pipeline run. {len(summaries)} event(s) read from "
      "fetched RSS articles; top events ranked by outlet count (more tellings "
      "= more to compare)._")
    A("")
    if not ranked:
        A("No events were dossiered in this run — feeds were unreachable or "
          "returned no articles. Nothing was fabricated to fill the gap.")
    for i, s in enumerate(ranked, 1):
        A(f"## {i}. {', '.join(s['key_terms'][:5])}")
        A("")
        A(f"{s['article_count']} articles across "
          f"{len(s['outlets'])} outlets: {', '.join(s['outlets'])}. "
          f"{_signal_line(s)}")
        A("")
        A(f"[full dossier](../dossiers/{s['event_id']}.md)")
        A("")

    brief_dir = state_dir / "briefs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    path = brief_dir / f"{today}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
