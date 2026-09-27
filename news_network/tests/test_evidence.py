"""Evidence tests: quotes attributed, claims sourced, nothing invented."""

from news_network.evidence import build_evidence_pack, extract_quotes

EVENT = {
    "id": "evt1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "Senate votes to advance infrastructure bill",
         "summary": ('The Senate voted to advance the infrastructure bill. '
                     '"We will veto any attempt to block this," said Senator Smith. '
                     "The bill aims to repair roads across the country."),
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
        {"url": "http://x/2", "outlet": "NPR",
         "title": "Infrastructure bill advances",
         "summary": ("Senators advanced the infrastructure bill on Tuesday. "
                     "Critics warned the cost is too high."),
         "published": 1_700_003_600, "fetched_at": 1_700_003_600},
    ],
    "key_terms": ["Senate", "infrastructure bill", "Smith"],
    "outlets": ["BBC", "NPR"],
    "earliest": 1_700_000_000,
    "latest": 1_700_003_600,
    "article_count": 2,
}


def test_every_claim_carries_source():
    pack = build_evidence_pack(EVENT)
    assert pack["claims"], "expected claims extracted"
    for c in pack["claims"]:
        assert c["outlet"] in ("BBC", "NPR")
        assert c["url"] in ("http://x/1", "http://x/2")
        assert c["id"]
        # claim text is a verbatim sentence from the source text
        src = next(a for a in EVENT["articles"] if a["url"] == c["url"])
        assert c["text"] in f"{src['title']}. {src['summary']}"


def test_quotes_attributed():
    pack = build_evidence_pack(EVENT)
    veto = [q for q in pack["quotes"] if "veto" in q["text"]]
    assert veto, "expected the veto quote extracted"
    assert veto[0]["attributed_to"] is not None
    assert "Smith" in veto[0]["attributed_to"]
    assert veto[0]["outlet"] == "BBC"


def test_unattributed_quote_recorded_not_guessed():
    quotes = extract_quotes('A report noted "the numbers do not add up" without naming anyone.')
    assert quotes
    assert quotes[0]["attributed_to"] is None


def test_framing_covers_each_outlet():
    pack = build_evidence_pack(EVENT)
    outlets = {f["outlet"] for f in pack["framing"]}
    assert outlets == {"BBC", "NPR"}
    for f in pack["framing"]:
        assert f["headline"]  # headline preserved verbatim
