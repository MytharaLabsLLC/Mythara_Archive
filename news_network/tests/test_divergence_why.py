"""Divergence explanations: every divergent reporter must say WHY, in plain language."""

from news_network.dossier import build_dossier_markdown
from news_network.evidence import build_evidence_pack
from news_network.witness_news import (
    hear_all, panel_summary, verify_news_judgment, DIVERGENT,
)
from news_network.tests.test_witness import THIN_EVENT, RICH_EVENT

NEMESIS_EVENT = {
    "id": "nem1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "Relief bill aims to help Working Families",
         "summary": "The relief bill aims to help Working Families recover from the downturn. Supporters say the measure will protect Working Families for years.",
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
        {"url": "http://x/2", "outlet": "Reuters",
         "title": "President Rivera deploys troops to the border",
         "summary": "President Rivera ordered troops deployed to the northern border. Defense Minister Okafor confirmed the deployment began at dawn.",
         "published": 1_700_000_100, "fetched_at": 1_700_000_100},
    ],
    "key_terms": ["relief", "troops", "Rivera"], "outlets": ["BBC", "Reuters"],
    "earliest": 1_700_000_000, "latest": 1_700_000_100, "article_count": 2,
}

DIONYSUS_EVENT = {
    "id": "dio1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "Mayor confirms bridge will open Friday",
         "summary": "The mayor confirmed the downtown bridge will open Friday morning. Crews finished the inspection and the bridge will open Friday as planned.",
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
        {"url": "http://x/2", "outlet": "Fox News",
         "title": "Mayor delays bridge opening indefinitely",
         "summary": "The mayor announced the downtown bridge will not open Friday. Inspectors found new cracks and the bridge will never open Friday as planned.",
         "published": 1_700_000_100, "fetched_at": 1_700_000_100},
    ],
    "key_terms": ["bridge", "mayor", "Friday"], "outlets": ["BBC", "Fox News"],
    "earliest": 1_700_000_000, "latest": 1_700_000_100, "article_count": 2,
}

EROS_EVENT = {
    "id": "ero1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "Rivera addresses withdrawal timeline",
         "summary": 'President Rivera said "we will withdraw all troops by June". In the same briefing, President Rivera said "we will never withdraw our troops from the region". The statements came hours apart.',
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
    ],
    "key_terms": ["Rivera", "troops", "withdrawal"], "outlets": ["BBC"],
    "earliest": 1_700_000_000, "latest": 1_700_000_000, "article_count": 1,
}

BATTERY = [THIN_EVENT, RICH_EVENT, NEMESIS_EVENT, DIONYSUS_EVENT, EROS_EVENT]

JARGON = ("projected_intent", "shadow_intent", "ingest", "witnessed",
          "abstain", "sealed", "rubric")


def _all_divergent():
    out = []
    for ev in BATTERY:
        pack = build_evidence_pack(ev)
        out += [j for j in hear_all(ev["id"], pack) if j.verdict == DIVERGENT]
    return out


def test_all_eight_lenses_can_diverge_with_why():
    seen = {j.assessor_id for j in _all_divergent()}
    assert seen == {"hermes", "janus", "nemesis", "hades",
                    "demeter", "dionysus", "eros", "persephone"}, \
        f"lenses never diverging: {seen}"


def test_every_divergent_judgment_explains_why():
    for j in _all_divergent():
        assert j.divergence_why.strip(), f"{j.assessor_id} divergent with no why"
        assert len(j.divergence_why) > 120, \
            f"{j.assessor_id} why is too thin: {j.divergence_why!r}"
        low = j.divergence_why.lower()
        for word in JARGON:
            assert word not in low, \
                f"{j.assessor_id} why leaks jargon {word!r}: {j.divergence_why!r}"
        # the why must name the beat and the reasoning, not just restate the verdict
        assert "my beat is" in low, f"{j.assessor_id} why never states its beat"
        assert "that is why i am pushing back" in low, \
            f"{j.assessor_id} why never closes the reasoning"


def test_divergence_why_is_sealed():
    for j in _all_divergent():
        assert verify_news_judgment(j), f"{j.assessor_id} seal broken with new field"


def test_dossier_renders_divergence_why():
    pack = build_evidence_pack(RICH_EVENT)
    judgments = hear_all(RICH_EVENT["id"], pack)
    panel = panel_summary(judgments)
    md = build_dossier_markdown(RICH_EVENT, pack, judgments, panel)
    for j in judgments:
        if j.verdict == DIVERGENT:
            assert f"**Why {j.name} reads it this way:**" in md, \
                f"{j.assessor_id} why missing from dossier page"
            assert j.divergence_why[:60] in md
    assert "each one's reasons are under their name above" in md
