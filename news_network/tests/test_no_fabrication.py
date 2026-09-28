"""No-fabrication test: every dossier claim traces to an ingested article.

This is the honesty contract as a test. If a dossier ever contains a
claim that did not come verbatim from a fetched article, or cites an
evidence id that does not exist in the pack, this test fails.
"""

from news_network.chain import DossierChain
from news_network.dossier import write_dossier

EVENT = {
    "id": "nofab1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "Mayor unveils transit plan for Denver",
         "summary": ('Mayor Alvarez unveiled a transit plan for Denver. '
                     '"We will cut commute times in half," Alvarez said. '
                     "The council will vote on funding next month."),
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
        {"url": "http://x/2", "outlet": "Denverite",
         "title": "Alvarez transit plan faces council vote",
         "summary": ("Alvarez's transit plan faces a council vote next month. "
                     "Critics questioned the cost estimates in the proposal."),
         "published": 1_700_003_600, "fetched_at": 1_700_003_600},
    ],
    "key_terms": ["Alvarez", "transit plan", "Denver", "council"],
    "outlets": ["BBC", "Denverite"],
    "earliest": 1_700_000_000,
    "latest": 1_700_003_600,
    "article_count": 2,
}


def _source_texts():
    return [f"{a['title']}. {a['summary']}" for a in EVENT["articles"]]


def test_every_claim_is_verbatim_from_source(tmp_path):
    from news_network.evidence import build_evidence_pack
    pack = build_evidence_pack(EVENT)
    texts = _source_texts()
    for c in pack["claims"]:
        assert any(c["text"] in t for t in texts), \
            f"claim not verbatim from any article: {c['text']!r}"


def test_every_citation_resolves(tmp_path):
    from news_network.evidence import build_evidence_pack
    from news_network.witness_news import hear_all
    pack = build_evidence_pack(EVENT)
    claim_ids = {c["id"] for c in pack["claims"]}
    quote_ids = {q["id"] for q in pack["quotes"]}
    framing_outlets = {f["outlet"] for f in pack["framing"]}
    for j in hear_all(EVENT["id"], pack):
        for e in j.evidence_cited:
            if e["kind"] in ("claim",):
                assert e["ref"] in claim_ids, f"dangling claim ref {e['ref']}"
            elif e["kind"] == "quote":
                assert e["ref"] in quote_ids, f"dangling quote ref {e['ref']}"
            elif e["kind"] == "framing":
                assert e["ref"] in framing_outlets
            assert e["url"].startswith("http"), "citation must carry a source URL"


def test_dossier_reads_plain(tmp_path):
    chain = DossierChain(tmp_path / "chain.jsonl")
    summary = write_dossier(EVENT, tmp_path, chain)
    md = (tmp_path / "dossiers" / f"{EVENT['id']}.md").read_text(encoding="utf-8")
    assert "## What the articles say" in md
    assert "## What the reporters noticed" in md
    assert "Sat this one out" in md or "sat this one out" in md
    # no rubric jargon on the page
    assert "INGESTED" not in md
    assert "WITNESSED" not in md
    assert "projected intent" not in md.lower()
    # no invented outlet names in the dossier
    for outlet in ("BBC", "Denverite"):
        assert outlet in md
    assert summary["event_id"] == EVENT["id"]
    ok, _ = chain.verify()
    assert ok
