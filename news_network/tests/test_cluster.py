"""Clustering tests: same story clusters, different stories don't."""

from news_network.cluster import cluster, proper_nouns

BASE = 1_700_000_000


def art(url, outlet, title, summary, published):
    return {"url": url, "outlet": outlet, "title": title,
            "summary": summary, "published": published,
            "fetched_at": BASE}


def test_same_story_clusters():
    a1 = art("http://x/1", "BBC",
             "Senate votes to advance infrastructure bill",
             "The Senate voted to advance the infrastructure bill. Senator Smith praised the vote.",
             BASE)
    a2 = art("http://x/2", "NPR",
             "Infrastructure bill advances in Senate",
             "Senators advanced the infrastructure bill on Tuesday. Smith said it will help workers.",
             BASE + 7200)
    events = cluster([a1, a2])
    assert len(events) == 1
    assert events[0]["article_count"] == 2
    assert set(events[0]["outlets"]) == {"BBC", "NPR"}


def test_different_stories_stay_apart():
    a1 = art("http://x/1", "BBC",
             "Senate votes to advance infrastructure bill",
             "The Senate voted to advance the infrastructure bill in Washington.",
             BASE)
    a2 = art("http://x/2", "Denverite",
             "Denver council approves new bike lanes",
             "The Denver council approved bike lanes downtown on Monday.",
             BASE + 3600)
    events = cluster([a1, a2])
    assert len(events) == 2


def test_time_window_separates():
    a1 = art("http://x/1", "BBC",
             "Senate votes to advance infrastructure bill",
             "The Senate voted to advance the infrastructure bill. Senator Smith praised it.",
             BASE)
    a2 = art("http://x/2", "NPR",
             "Infrastructure bill advances in Senate",
             "Senators advanced the infrastructure bill. Smith praised the move.",
             BASE + 4 * 24 * 3600)  # 4 days later
    events = cluster([a1, a2])
    assert len(events) == 2


def test_proper_nouns_extracts_names():
    nouns = proper_nouns("Senator Smith met Mayor Johnson at the White House in Denver.")
    assert "Smith" in nouns or "Senator Smith" in nouns
    assert "Denver" in nouns
    # common words excluded
    assert "the" not in nouns
