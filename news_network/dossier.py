"""Dossier builder — one markdown dossier per event.

The dossier is the public surface: it reads like a reporter's notebook,
not a form. Underneath, the honesty contract still holds — every claim
traces to a fetched article, every witness reading cites its evidence,
and the evidence pack + sealed judgments are chained (chain.py)
alongside the dossier's markdown hash.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .chain import DossierChain
from .evidence import build_evidence_pack
from .topics import classify
from .witness_news import hear_all, panel_summary, VERDICT_WORDS
from .witness_news import ALIGNED, DIVERGENT, ABSTAIN  # machine verdicts

# v2026.2 benevolence vocabulary: Δ Benevolence scores every dossier.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from soul_cradle.benevolence import calculate_delta

_FRAMING_RE = re.compile(r"(?m)^- \*\*[^*]+\*\*: (.+)$")


def lead_headline(md: str) -> str:
    """First outlet headline in the framing section.

    A real published headline, used as the event's display title instead of
    a key-term list. Capped so it works as a page title.
    """
    m = _FRAMING_RE.search(md or "")
    if not m:
        return ""
    title = m.group(1).strip()
    return title[:117] + "..." if len(title) > 120 else title


def display_title(summary: Dict, md: str = "") -> str:
    """Best human title for an event: real headline first, key terms fallback."""
    return lead_headline(md) or ", ".join(summary.get("key_terms", [])[:5])


def _ts(ts) -> str:
    if not ts:
        return "unknown time"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _beat_line(j) -> str:
    beat = j.domain_question
    if ":" in beat:
        beat = beat.split(":", 1)[1].strip()
    return beat


def _sources_line(cited) -> str:
    seen = []
    for e in cited:
        label = f"[{e['outlet']}]({e['url']})"
        if label not in seen:
            seen.append(label)
    return "Sources: " + ", ".join(seen) if seen else ""


def _lede(event: Dict, pack: Dict, panel: Dict) -> str:
    n_outlets = len(pack["outlets"])
    n_articles = pack["article_count"]
    div = panel["divergent"]
    al = panel["aligned"]
    word = VERDICT_WORDS[panel["verdict"]]
    if panel["verdict"] == "silent":
        return (
            f"{n_articles} articles across {n_outlets} outlet(s), and every one "
            f"of our reporters sat this one out — the record is too thin to "
            f"read with any confidence. What follows is what the articles say, "
            f"and nothing more."
        )
    bits = []
    if div:
        bits.append(f"{', '.join(div)} aren't buying the official story")
    if al:
        bits.append(f"{', '.join(al)} see it differently")
    disagree = f" — {'; '.join(bits)}" if bits else ""
    return (
        f"{n_articles} articles, {n_outlets} outlets, one event. "
        f"Our reporters don't all see it the same way{disagree}. "
        f"Here's what the articles say, and what our people are saying about them."
    )


def _paradox_lines(judgments, panel) -> List[str]:
    """The whole picture, first and unsoftened: every reporter's take,
    divergent readings in full. Readers meet the disagreement before the
    articles — when people see it differently, that's the story."""
    out: List[str] = []
    A = out.append
    A("## What our people are saying")
    A("")
    A("_Eight reporters, each with their own perspective. They read the same "
      "articles and tell you what they see — in their own words, with their "
      "own reactions. When they disagree, you'll see the disagreement._")
    A("")
    if panel["verdict"] == "silent":
        A("No strong takes on this one — the record is too thin for anyone "
          "to read with confidence. What follows is what the articles say, "
          "and nothing more.")
        A("")
        return out
    bits = []
    if panel["divergent"]:
        bits.append(f"{', '.join(panel['divergent'])} aren't buying it")
    if panel["aligned"]:
        bits.append(f"{', '.join(panel['aligned'])} see it differently")
    if panel["abstained"]:
        bits.append(
            f"{', '.join(a['assessor_id'] for a in panel['abstained'])} sat this one out")
    A("**Here's where people land:** " + "; ".join(bits) + ". "
      "Everyone's take stands on its own — nothing softened.")
    A("")
    for j in judgments:
        if j.verdict != DIVERGENT:
            continue
        A(f"### {j.name}")
        A("")
        # v2026.2: witness reading in plain English with emotions.
        # projected/shadow intent woven into natural voice, never labeled.
        A(j.projected_intent)
        A("")
        A(j.shadow_intent)
        if j.divergence_why:
            A("")
            A(j.divergence_why)
        src = _sources_line(j.evidence_cited)
        if src:
            A("")
            A(f"_{src}_")
        A("")
    for j in judgments:
        if j.verdict != ALIGNED:
            continue
        A(f"### {j.name}")
        A("")
        A(j.projected_intent)
        A("")
        A(j.shadow_intent)
        src = _sources_line(j.evidence_cited)
        if src:
            A("")
            A(f"_{src}_")
        A("")
    abstainers = [j for j in judgments if j.verdict == ABSTAIN]
    if abstainers:
        A("### Sat this one out")
        A("")
        for j in abstainers:
            A(f"- **{j.name}** — {_beat_line(j)}: {j.abstain_reason}")
        A("")
    return out


def _benevolence_data(judgments, panel) -> dict:
    """v2026.2 Δ Benevolence: calculated underneath, not displayed.

    Each engaged witness's benevolence_score (-5..+5) feeds calculate_delta.
    Returns {delta, gravity, basis} for topic ranking and frontmatter.
    The dossier body stays plain English — no visible scores.
    """
    engaged = [j for j in judgments if j.verdict != ABSTAIN]
    if not engaged:
        return {"delta": 0, "gravity": "UNKNOWN", "basis": "no engaged witnesses"}

    scores = [j.benevolence_score for j in engaged]
    shadow = any(
        "shadow" in (j.shadow_intent or "").lower()[:200]
        for j in engaged
    )
    affected = max(100, len(engaged) * 1000)

    delta, basis = calculate_delta(scores, affected, shadow)

    if delta <= -60:
        gravity = "HIGHEST"
    elif delta <= -30:
        gravity = "HIGH"
    elif delta <= -10:
        gravity = "MEDIUM"
    elif delta < 10:
        gravity = "LOW"
    else:
        gravity = "POSITIVE"
    return {"delta": delta, "gravity": gravity, "basis": basis,
            "shadow": shadow}


def build_dossier_markdown(event: Dict, pack: Dict,
                           judgments, panel: Dict) -> str:
    lines: List[str] = []
    A = lines.append

    A(f"# {', '.join(pack['key_terms'][:5])}")
    A("")
    A(f"_{pack['article_count']} articles across {', '.join(pack['outlets'])}. "
      f"{_ts(pack['earliest'])} → {_ts(pack['latest'])}._")
    A("")
    A(_lede(event, pack, panel))
    A("")
    A("---")
    A("")
    for line in _paradox_lines(judgments, panel):
        A(line)
    A("---")
    A("")
    A("## What the articles say")
    A("")
    A("### How each outlet framed it")
    A("")
    for f in pack["framing"]:
        A(f"- **{f['outlet']}**: {f['headline']}")
        if f["lede"]:
            A(f"  {f['lede'][:220]}")
    A("")
    A("### The key claims")
    A("")
    for c in pack["claims"][:25]:
        A(f"- **[{c['outlet']}]** {c['text']}")
        A(f"  <{c['url']}>")
    if len(pack["claims"]) > 25:
        A(f"_…and {len(pack['claims']) - 25} more claims in the chained record._")
    A("")
    if pack["quotes"]:
        A("### In their own words")
        A("")
        for q in pack["quotes"][:10]:
            attr = f" — **{q['attributed_to']}**" if q["attributed_to"] else " — speaker not named"
            A(f"- **[{q['outlet']}]** \"{q['text']}\"{attr}")
            A(f"  <{q['url']}>")
        A("")
    if pack["actors"]:
        A(f"_Named in the coverage: {', '.join(pack['actors'][:10])}_")
        A("")
    A("---")
    A("")
    A("---")
    A("_Every claim above comes from a linked article. The readings are "
      "locked to the evidence with a tamper-evident record — this page is "
      "unaltered, which doesn't prove the reporting was true. That's what "
      "the reporters are for. Mythara News Network._")
    return "\n".join(lines)


def write_dossier(event: Dict, state_dir: Path, chain: DossierChain) -> Dict:
    """Build evidence pack, hear witnesses, write dossier, chain it."""
    state_dir = Path(state_dir)
    pack = build_evidence_pack(event)
    judgments = hear_all(event["id"], pack)
    panel = panel_summary(judgments)
    # v2026.2: benevolence calculated underneath for gravity/topic ranking.
    # Not displayed in the dossier body — plain English with emotions only.
    benev = _benevolence_data(judgments, panel)
    md = build_dossier_markdown(event, pack, judgments, panel)

    dossier_dir = state_dir / "dossiers"
    dossier_dir.mkdir(parents=True, exist_ok=True)
    dossier_path = dossier_dir / f"{event['id']}.md"
    dossier_path.write_text(md, encoding="utf-8")

    record = chain.append(
        event_id=event["id"],
        evidence_pack=pack,
        judgments=[j.to_dict() for j in judgments],
        panel=panel,
        dossier_markdown=md,
    )
    summary = {
        "event_id": event["id"],
        "topic": classify(md)["slug"],
        "panel_verdict": panel["verdict"],
        "divergent": panel["divergent"],
        "aligned": panel["aligned"],
        "abstained": [a["assessor_id"] for a in panel["abstained"]],
        "chain_record": record.record_id,
        "outlets": pack["outlets"],
        "article_count": pack["article_count"],
        "key_terms": pack["key_terms"][:6],
        # v2026.2 benevolence (underneath — for gravity ranking, not display)
        "benevolence_delta": benev["delta"],
        "benevolence_gravity": benev["gravity"],
        "benevolence_basis": benev["basis"],
    }
    (dossier_dir / f"{event['id']}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
