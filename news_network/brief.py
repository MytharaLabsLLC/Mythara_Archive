"""Daily brief — the top events, organized by topic.

US trade negotiations is the standing lead topic: the top trade events are
guaranteed space in every brief, and the rest of the news follows under its
own topic sections. More outlets covering the same event means more tellings
to compare, which is where the reporters have the most to work with.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .topics import TOPICS, FALLBACK_TOPIC, classify
from .dossier import display_title
from .market import market_section
from .witness_news import VERDICT_WORDS

TRADE_SLUG = "trade"
TRADE_GUARANTEED = 3  # trade events always in the brief, even below the cutoff


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


def _dossier_md(summary: Dict, dossier_dir: Path) -> str:
    md = dossier_dir / (summary["event_id"] + ".md")
    try:
        return md.read_text(encoding="utf-8") if md.exists() else ""
    except OSError:
        return ""


def _topic_of(summary: Dict, dossier_dir: Path) -> str:
    """Classify an event from its dossier text; key terms as fallback."""
    md_text = _dossier_md(summary, dossier_dir)
    if md_text:
        return classify(md_text)["slug"]
    return classify(" ".join(summary.get("key_terms", [])))["slug"]


def _rank_key(s: Dict):
    return (len(s["outlets"]), s["article_count"])


def build_brief(summaries: List[Dict], state_dir: Path,
                max_events: int = 10) -> Path:
    """Write the daily brief markdown, grouped by topic. Returns the path."""
    state_dir = Path(state_dir)
    dossier_dir = state_dir / "dossiers"
    ranked = sorted(summaries, key=_rank_key, reverse=True)

    # Lead topic first: the top trade events are guaranteed space.
    trade = [s for s in ranked if _topic_of(s, dossier_dir) == TRADE_SLUG][:TRADE_GUARANTEED]
    picked = list(trade)
    for s in ranked:
        if len(picked) >= max_events:
            break
        if s not in picked:
            picked.append(s)

    # Group the picked events by topic, topics in standing order.
    order = [t["slug"] for t in TOPICS] + [FALLBACK_TOPIC["slug"]]
    groups: Dict[str, List[Dict]] = {slug: [] for slug in order}
    for s in picked:
        groups[_topic_of(s, dossier_dir)].append(s)

    # Market drivers: top money-topic events across the whole ranking.
    # Tariff stories move markets too — trade fills any empty driver slots.
    drivers = []
    for want in ("money", "trade"):
        for s in ranked:
            if len(drivers) >= 3:
                break
            if _topic_of(s, dossier_dir) == want and all(
                    d["dossier_link"] != f"../dossiers/{s['event_id']}.md" for d in drivers):
                drivers.append({
                    "title": display_title(s, _dossier_md(s, dossier_dir)),
                    "dossier_link": f"../dossiers/{s['event_id']}.md",
                })
        if len(drivers) >= 3:
            break

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    lines: List[str] = []
    A = lines.append
    A(f"# Mythara News Network — brief for {today}")
    A("")
    A(f"_On-demand pipeline run. {len(summaries)} event(s) read from "
      "fetched RSS articles; top events ranked by outlet count (more tellings "
      "= more to compare)._")
    A("")
    if not picked:
        A("No events were dossiered in this run — feeds were unreachable or "
          "returned no articles. Nothing was fabricated to fill the gap.")
    for slug in order:
        events = groups[slug]
        if not events:
            continue
        title = next((t["title"] for t in TOPICS if t["slug"] == slug),
                      FALLBACK_TOPIC["title"])
        A(f"## {title}")
        A("")
        for i, s in enumerate(events, 1):
            A(f"### {i}. {display_title(s, _dossier_md(s, dossier_dir))}")
            A("")
            A(f"{s['article_count']} articles across "
              f"{len(s['outlets'])} outlets: {', '.join(s['outlets'])}. "
              f"{_signal_line(s)}")
            A("")
            A(f"[full dossier](../dossiers/{s['event_id']}.md)")
            A("")
        A("")
        if slug == TRADE_SLUG:
            # The numbers desk sits right behind the lead topic.
            lines.extend(market_section(drivers))

    brief_dir = state_dir / "briefs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    path = brief_dir / f"{today}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
