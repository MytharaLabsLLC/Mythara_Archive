"""Witness tests: abstention contract, engagement, sealed judgments."""

from news_network.evidence import build_evidence_pack
from news_network.witness_news import (
    hear_all, panel_summary, verify_news_judgment,
    ABSTAIN, ALIGNED, DIVERGENT,
)

THIN_EVENT = {
    "id": "thin1",
    "articles": [
        {"url": "http://x/1", "outlet": "Denverite",
         "title": "Council approves bike lanes",
         "summary": "The council approved bike lanes downtown. Work begins in spring.",
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
    ],
    "key_terms": ["council", "bike lanes", "Denver"],
    "outlets": ["Denverite"],
    "earliest": 1_700_000_000,
    "latest": 1_700_000_000,
    "article_count": 1,
}

RICH_EVENT = {
    "id": "rich1",
    "articles": [
        {"url": "http://x/1", "outlet": "BBC",
         "title": "President announces troop withdrawal from region",
         "summary": ('The president announced plans to withdraw troops, vowing to "bring our people home," '
                     "President Rivera said. The defense ministry confirmed troops were deployed to the border last week. "
                     "The move aims to reduce tensions in the region."),
         "published": 1_700_000_000, "fetched_at": 1_700_000_000},
        {"url": "http://x/2", "outlet": "Fox News",
         "title": "Troop buildup continues despite withdrawal talk",
         "summary": ("Despite the president's announcement, the defense ministry ordered additional troops "
                     "deployed to the border. Critics warned the buildup contradicts the withdrawal pledge."),
         "published": 1_700_003_600, "fetched_at": 1_700_003_600},
    ],
    "key_terms": ["president", "troops", "Rivera", "border"],
    "outlets": ["BBC", "Fox News"],
    "earliest": 1_700_000_000,
    "latest": 1_700_003_600,
    "article_count": 2,
}


def test_thin_evidence_abstains_widely():
    pack = build_evidence_pack(THIN_EVENT)
    judgments = hear_all(THIN_EVENT["id"], pack)
    assert len(judgments) == 8
    abstained = [j for j in judgments if j.verdict == ABSTAIN]
    # single outlet, no quotes, no stated intents: most lenses must abstain
    assert len(abstained) >= 5, f"only {[j.assessor_id for j in abstained]} abstained"
    for j in abstained:
        assert j.abstain_reason, f"{j.assessor_id} abstained without a reason"
        assert not j.projected_intent and not j.shadow_intent
    panel = panel_summary(judgments)
    assert panel["verdict"] in ("silent", "aligned", "divergent", "contested")
    assert len(panel["abstained"]) == len(abstained)


def test_hermes_engages_on_multi_outlet():
    pack = build_evidence_pack(RICH_EVENT)
    judgments = {j.assessor_id: j for j in hear_all(RICH_EVENT["id"], pack)}
    assert judgments["hermes"].verdict != ABSTAIN
    assert judgments["hermes"].evidence_cited


def test_janus_spots_stated_vs_action_gap():
    pack = build_evidence_pack(RICH_EVENT)
    judgments = {j.assessor_id: j for j in hear_all(RICH_EVENT["id"], pack)}
    janus = judgments["janus"]
    assert janus.verdict == DIVERGENT, "withdrawal pledge vs troop deployment should diverge"
    assert janus.projected_intent and janus.shadow_intent
    assert janus.evidence_cited


def test_judgments_are_sealed():
    pack = build_evidence_pack(RICH_EVENT)
    for j in hear_all(RICH_EVENT["id"], pack):
        assert verify_news_judgment(j), f"{j.assessor_id} seal broken"
        assert j.rubric_version == "news-2026.3"
        assert j.base_rubric_version  # extends a real base rubric version


def test_dissent_preserved_not_averaged():
    pack = build_evidence_pack(RICH_EVENT)
    panel = panel_summary(hear_all(RICH_EVENT["id"], pack))
    # dissent entries carry full shadow readings, not a merged score
    for d in panel["dissent"]:
        assert d["shadow_intent"]
        assert d["evidence_cited"]
    assert "verdict" in panel and panel["verdict"] in (
        "aligned", "divergent", "contested", "silent")
