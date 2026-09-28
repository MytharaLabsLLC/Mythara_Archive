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
        bits.append(f"{', '.join(div)} pushed back on the official telling")
    if al:
        bits.append(f"{', '.join(al)} checked out")
    return (
        f"{n_articles} articles, {n_outlets} outlets, one event. "
        f"The panel reads **{word}** — " + "; ".join(bits) + ". "
        f"Here is what the articles say, and what our reporters noticed."
    )


def _paradox_lines(judgments, panel) -> List[str]:
    """The whole split, first and unsoftened: every reporter's position,
    divergent readings in full. Readers meet the paradox before the
    articles — the disagreement is the signal, stated completely."""
    out: List[str] = []
    A = out.append
    A("## The paradox")
    A("")
    A("_Eight reporters, each on their own beat. They read the same articles "
      "and tell you what they see — suggestion with citations, never "
      "proof of anyone's motive. When they split, the split is the story._")
    A("")
    if panel["verdict"] == "silent":
        A("No disagreement to report — every reporter sat this one out. "
          "What follows is what the articles say, and nothing more.")
        A("")
        return out
    word = VERDICT_WORDS[panel["verdict"]]
    bits = []
    if panel["divergent"]:
        bits.append(f"{', '.join(panel['divergent'])} pushed back")
    if panel["aligned"]:
        bits.append(f"{', '.join(panel['aligned'])} checked out")
    if panel["abstained"]:
        bits.append(
            f"{', '.join(a['assessor_id'] for a in panel['abstained'])} sat it out")
    A(f"**{word}.** " + "; ".join(bits)
      + ". Both readings stand — here is the whole split, nothing softened.")
    A("")
    for j in judgments:
        if j.verdict != DIVERGENT:
            continue
        A(f"### {j.name} — pushes back")
        A("")
        A(f"_Beat: {_beat_line(j)}_")
        A("")
        A(j.projected_intent)
        A("")
        A(j.shadow_intent)
        if j.divergence_why:
            A("")
            A(f"**Why {j.name} reads it this way:** {j.divergence_why}")
        src = _sources_line(j.evidence_cited)
        if src:
            A("")
            A(f"_{src}_")
        A("")
    for j in judgments:
        if j.verdict != ALIGNED:
            continue
        A(f"### {j.name} — checks out")
        A("")
        A(f"_Beat: {_beat_line(j)}_")
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
    }
    (dossier_dir / f"{event['id']}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
