"""Topic classification tests — every part of the news is organized by topic."""

from news_network.topics import TOPICS, FALLBACK_TOPIC, classify, topic_for_slug


def test_trade_wins_on_trade_language():
    text = ("Trump announced new reciprocal tariff rates. USTR Greer said the "
            "trade deal talks resume Monday amid the tariff standoff.")
    assert classify(text)["slug"] == "trade"


def test_trade_wins_ties_by_standing_order():
    # Mentions both trade and Washington language; trade is the lead topic.
    text = ("The White House announced a tariff. Congress debated the trade "
            "negotiation while the Senate weighed the trade deal.")
    assert classify(text)["slug"] == "trade"


def test_washington_classifies():
    text = ("The Senate passed the bill. The White House confirmed. "
            "Congress returns after the midterm recess.")
    assert classify(text)["slug"] == "washington"


def test_denver_classifies():
    text = ("Denver city council voted. Colorado lawmakers in Boulder and "
            "Aurora responded to the Denver measure.")
    assert classify(text)["slug"] == "denver"


def test_thin_evidence_falls_back_to_more_news():
    assert classify("A quiet story about a local bake sale.") == FALLBACK_TOPIC
    assert classify("tariff") == FALLBACK_TOPIC  # one hit is not enough


def test_topic_for_slug_roundtrip():
    for t in TOPICS:
        assert topic_for_slug(t["slug"]) == t
    assert topic_for_slug("nope") == FALLBACK_TOPIC
