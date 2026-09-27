"""Dossier builder — one markdown dossier per event.

Structure (the honesty contract, in the document itself):
  INGESTED  — facts fetched from articles. Every claim carries its
              outlet and URL. Nothing here is analysis.
  WITNESSED — the eight lenses' projected-vs-shadow readings, each
              citing the evidence it leans on. Abstentions are listed
              with reasons. Dissent is preserved, never averaged.

The evidence pack + sealed judgments are chained (chain.py) alongside
the dossier's markdown hash.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .chain import DossierChain
from .evidence import build_evidence_pack
from .witness_news import hear_all, panel_summary, ALIGNED, DIVERGENT, ABSTAIN


def _ts(ts) -> str:
    if not ts:
        return "unknown time"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def build_dossier_markdown(event: Dict, pack: Dict,
                           judgments, panel: Dict) -> str:
    lines: List[str] = []
    A = lines.append

    A(f"# Event dossier — `{event['id']}`")
    A("")
    A(f"**Key terms:** {', '.join(pack['key_terms'][:8])}")
    A(f"**Outlets ({len(pack['outlets'])}):** {', '.join(pack['outlets'])}")
    A(f"**Articles:** {pack['article_count']} | **Window:** {_ts(pack['earliest'])} → {_ts(pack['latest'])}")
    A(f"**Panel:** {panel['verdict'].upper()} — "
      f"divergent: {', '.join(panel['divergent']) or 'none'}; "
      f"aligned: {', '.join(panel['aligned']) or 'none'}; "
      f"abstained: {', '.join(a['assessor_id'] for a in panel['abstained']) or 'none'}")
    A("")
    A("> Honesty contract: **INGESTED** = facts fetched from the articles "
      "below (each with its source). **WITNESSED** = the assessors' readings "
      "of that evidence — suggestion with citations, never proof of motive. "
      "The chain proves this dossier is unaltered, not that the reporting is true.")
    A("")
    A("---")
    A("")
    A("## INGESTED — the fetched record")
    A("")
    A("### Claims (verbatim sentences from the source text)")
    A("")
    for c in pack["claims"]:
        A(f"- `{c['id']}` **[{c['outlet']}]** {c['text']}")
        A(f"  <{c['url']}>")
    A("")
    A("### Direct quotes")
    A("")
    if pack["quotes"]:
        for q in pack["quotes"]:
            attr = f" — attributed to **{q['attributed_to']}**" if q["attributed_to"] else " — speaker not named in the text"
            A(f"- `{q['id']}` **[{q['outlet']}]** \"{q['text']}\"{attr}")
            A(f"  <{q['url']}>")
    else:
        A("_No direct quotes in the ingested text._")
    A("")
    A("### Framing — how each outlet headlined the same event")
    A("")
    for f in pack["framing"]:
        A(f"- **{f['outlet']}**: {f['headline']}")
        if f["lede"]:
            A(f"  Lede: {f['lede'][:220]}")
    A("")
    A(f"### Named actors: {', '.join(pack['actors'][:10]) or 'none extracted'}")
    A("")
    A("---")
    A("")
    A("## WITNESSED — the eight lenses")
    A("")
    A("_Each lens extends its Soul Cradle assessor's domain to news. "
      "Projected intent = what the actors/framing claim. Shadow intent = what "
      "the evidence pattern suggests (cited, heuristic, never proof of motive)._")
    A("")
    for j in judgments:
        A(f"### {j.name} `{j.assessor_id}` — {j.verdict.upper()}")
        A(f"_Domain: {j.domain_question}_")
        A(f"_Rubric: {j.rubric_version} (extends base {j.base_rubric_version})_")
        A("")
        if j.verdict == ABSTAIN:
            A(f"**Abstained.** {j.abstain_reason}")
        else:
            A(f"**Projected intent:** {j.projected_intent}")
            A("")
            A(f"**Shadow intent:** {j.shadow_intent}")
            A("")
            if j.evidence_cited:
                A("**Evidence leaned on:**")
                for e in j.evidence_cited:
                    A(f"- `{e['ref']}` ({e['kind']}) [{e['outlet']}] <{e['url']}>")
        A(f"_Seal: `{j.integrity_hash[:16]}…`_")
        A("")
    A("---")
    A("")
    A("## Panel dissent — preserved, not averaged")
    A("")
    if panel["verdict"] == "silent":
        A("Every lens abstained: the ingested evidence is too thin for any "
          "witness to speak. No analysis is offered rather than a thin one.")
    elif panel["dissent"]:
        A(f"**{panel['verdict'].upper()}**: these lenses see a gap between the "
          "projected and shadow intents:")
        for d in panel["dissent"]:
            A(f"- **{d['assessor_id']}**: {d['shadow_intent'][:300]}")
        if panel["aligned"]:
            A(f"Meanwhile {', '.join(panel['aligned'])} found no gap on the "
              "same evidence. Both readings stand; the disagreement is the signal.")
    else:
        A(f"**{panel['verdict'].upper()}**: no lens found a projected/shadow gap "
          "on this evidence.")
    if panel["abstained"]:
        A("")
        A("Abstained (domain not engaged):")
        for a in panel["abstained"]:
            A(f"- **{a['assessor_id']}**: {a['reason']}")
    A("")
    A("---")
    A("_Mythara News Network v1 — on-demand pipeline. Not a live service. "
      "Generated from fetched RSS articles; re-run to refresh._")
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
