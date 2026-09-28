"""Dossier builder — one markdown dossier per event.

The dossier is the public surface: it reads like a reporter's notebook,
not a form. Underneath, the honesty contract still holds — every claim
traces to a fetched article, every witness reading cites its evidence,
and the evidence pack + sealed judgments are chained (chain.py)
alongside the dossier's markdown hash.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .chain import DossierChain
from .evidence import build_evidence_pack
from .witness_news import hear_all, panel_summary, VERDICT_WORDS
from .witness_news import ALIGNED, DIVERGENT, ABSTAIN  # machine verdicts


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
    A("## What the reporters noticed")
    A("")
    A("_Eight reporters, each on their own beat. They read the articles "
      "above and tell you what they see — suggestion with citations, never "
      "proof of anyone's motive._")
    A("")
    for j in judgments:
        A(f"### {j.name} — {VERDICT_WORDS[j.verdict]}")
        A("")
        if j.verdict == ABSTAIN:
            A(f"Sat this one out: {j.abstain_reason}")
        else:
            A(j.projected_intent)
            A("")
            A(j.shadow_intent)
            src = _sources_line(j.evidence_cited)
            if src:
                A("")
                A(f"_{src}_")
        A("")
    A("---")
    A("")
    A("### Where the reporters disagree")
    A("")
    if panel["verdict"] == "silent":
        A("No disagreement to report — nobody engaged.")
    elif panel["dissent"]:
        A(f"**{VERDICT_WORDS[panel['verdict']]}.** Pushing back: "
          f"{', '.join(panel['divergent'])}. Checked out: "
          f"{', '.join(panel['aligned']) or 'none'}. Both readings stand — "
          f"the disagreement is the signal.")
    else:
        A(f"**{VERDICT_WORDS[panel['verdict']]}.** No reporter found a gap "
          f"between what the story claims and what the evidence suggests.")
    if panel["abstained"]:
        A("")
        A("Sat this one out: "
          + ", ".join(a["assessor_id"] for a in panel["abstained"]) + ".")
    A("")
    A("---")
    A("_Every claim above traces to a fetched article, linked inline. The "
      "witness readings are sealed and hash-chained with the evidence — the "
      "chain proves this page is unaltered, not that the reporting is true. "
      "Mythara News Network._")
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
