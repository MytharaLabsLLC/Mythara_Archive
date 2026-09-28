"""Curated RSS/Atom source list for the Mythara News Network.

Every URL below was verified live on 2026-09-27 by fetching it and
confirming it parses as RSS/Atom with items present. Dead or
bot-blocked feeds are documented, not silently included.

Spectrum: wire/international, US across the political spectrum,
independent outlets, and Denver/local (Herb is in Denver).
"""

from typing import Dict, List

# Each source: id, outlet label, political/cultural lean (labeled, not
# endorsed), beat, and the verified feed URL.
SOURCES: List[Dict[str, str]] = [
    # -- wire / international -------------------------------------------
    {"id": "bbc-world", "outlet": "BBC", "lean": "center",
     "beat": "international",
     "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"id": "bbc-top", "outlet": "BBC", "lean": "center",
     "beat": "top stories",
     "url": "http://feeds.bbci.co.uk/news/rss.xml"},
    {"id": "aljazeera", "outlet": "Al Jazeera", "lean": "center-left / intl",
     "beat": "international",
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    # -- US spectrum -----------------------------------------------------
    {"id": "npr", "outlet": "NPR", "lean": "center-left",
     "beat": "us news",
     "url": "https://feeds.npr.org/1001/rss.xml"},
    {"id": "cnn", "outlet": "CNN", "lean": "center-left",
     "beat": "us/world",
     "url": "http://rss.cnn.com/rss/edition.rss"},
    {"id": "nbc", "outlet": "NBC News", "lean": "center-left",
     "beat": "us news",
     "url": "https://feeds.nbcnews.com/nbcnews/public/news"},
    {"id": "abc", "outlet": "ABC News", "lean": "center",
     "beat": "us news",
     "url": "https://abcnews.go.com/abcnews/topstories"},
    {"id": "cbs", "outlet": "CBS News", "lean": "center",
     "beat": "us news",
     "url": "https://www.cbsnews.com/latest/rss/main"},
    {"id": "nyt", "outlet": "New York Times", "lean": "center-left",
     "beat": "us/world",
     "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"id": "wapo", "outlet": "Washington Post", "lean": "center-left",
     "beat": "us/world",
     "url": "https://feeds.washingtonpost.com/rss/world"},
    {"id": "guardian", "outlet": "The Guardian", "lean": "center-left / intl",
     "beat": "international",
     "url": "https://www.theguardian.com/world/rss"},
    {"id": "bloomberg", "outlet": "Bloomberg", "lean": "center / business",
     "beat": "politics",
     "url": "https://feeds.bloomberg.com/politics/news.rss"},
    {"id": "wsj-world", "outlet": "Wall Street Journal", "lean": "center-right",
     "beat": "world/business",
     "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"id": "fox", "outlet": "Fox News", "lean": "right",
     "beat": "us news",
     "url": "http://feeds.foxnews.com/foxnews/latest"},
    # -- independent -----------------------------------------------------
    {"id": "democracynow", "outlet": "Democracy Now!", "lean": "left / independent",
     "beat": "us/world",
     "url": "https://www.democracynow.org/democracynow.rss"},
    {"id": "intercept", "outlet": "The Intercept", "lean": "left / independent",
     "beat": "investigations",
     "url": "https://theintercept.com/feed/?lang=en"},
    {"id": "propublica", "outlet": "ProPublica", "lean": "nonprofit investigative",
     "beat": "investigations",
     "url": "https://www.propublica.org/feeds/propublica/main"},
    # -- topic feeds: standing coverage beats --------------------------------
    # Google News topic search — verified live 2026-09-27 (fetched, parsed,
    # ~100 items each). Item-level <source> names the real outlet; ingest.py
    # prefers it over this feed-level label.
    {"id": "gnews-trade", "outlet": "Google News", "lean": "aggregator / multi-outlet",
     "beat": "topic: us trade negotiations",
     "url": "https://news.google.com/rss/search?q=US%20trade%20negotiations&hl=en-US&gl=US&ceid=US:en"},
    {"id": "gnews-tariffs", "outlet": "Google News", "lean": "aggregator / multi-outlet",
     "beat": "topic: us tariffs & trade deals",
     "url": "https://news.google.com/rss/search?q=US%20tariffs%20trade%20deal&hl=en-US&gl=US&ceid=US:en"},
    # -- Denver / local (Herb is in Denver) --------------------------------
    {"id": "cosun", "outlet": "Colorado Sun", "lean": "center / nonprofit local",
     "beat": "colorado",
     "url": "https://coloradosun.com/feed/"},
    {"id": "denverite", "outlet": "Denverite", "lean": "local",
     "beat": "denver",
     "url": "https://denverite.com/feed/"},
    {"id": "9news", "outlet": "9News Denver", "lean": "local",
     "beat": "denver/colorado",
     "url": "https://www.9news.com/feeds/syndication/rss/news/local"},
    {"id": "cpr", "outlet": "Colorado Public Radio", "lean": "center / public",
     "beat": "colorado",
     "url": "https://www.cpr.org/feed/"},
]

# Feeds that were checked and could NOT be used, with the reason.
# Documented so nobody "fixes" them back in without re-verifying.
BLOCKED_SOURCES: List[Dict[str, str]] = [
    {"outlet": "Associated Press",
     "url": "https://apnews.com/rss",
     "reason": "HTTP 403 to automated fetches (bot-blocking) as of 2026-09-27."},
    {"outlet": "Denver Post",
     "url": "https://www.denverpost.com/feed/",
     "reason": "HTTP 403 to automated fetches (bot-blocking) as of 2026-09-27."},
    {"outlet": "Reuters",
     "url": "https://www.reuters.com/rssfeed/worldNews",
     "reason": "HTTP 401/404 to automated fetches (bot-blocking) as of 2026-09-27."},
    {"outlet": "Politico",
     "url": "https://www.politico.com/rss/politicopicks.xml",
     "reason": "HTTP 403 to automated fetches (bot-blocking) as of 2026-09-27."},
    {"outlet": "USA Today",
     "url": "https://www.usatoday.com/rss/news/",
     "reason": "No usable RSS endpoint found as of 2026-09-27 (404 / zero items)."},
]


def all_sources() -> List[Dict[str, str]]:
    """The usable, verified source list."""
    return list(SOURCES)
