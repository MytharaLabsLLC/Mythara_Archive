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
]


def all_sources() -> List[Dict[str, str]]:
    """The usable, verified source list."""
    return list(SOURCES)
