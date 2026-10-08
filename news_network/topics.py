"""Topic sections for the Mythara News Network.

Every part of the news — the brief, the published posts, the homepage —
is organized by topic. US trade negotiations is the standing lead topic:
it is classified first and guaranteed space in every brief.
"""

from __future__ import annotations

from typing import Dict, List

TOPICS: List[Dict] = [
    {
        "slug": "trade",
        "title": "US trade negotiations",
        "keywords": [
            "tariff", "trade deal", "trade talks", "trade negotiation",
            "ustr", "trade representative", "reciprocal tariff", "trade war",
            "trade deficit", "trade agreement",
        ],
    },
    {
        "slug": "washington",
        "title": "Washington",
        "keywords": [
            "white house", "senate", "house of representatives",
            "supreme court", "congress", "midterm", "capitol hill",
        ],
    },
    {
        "slug": "world",
        "title": "World",
        "keywords": [
            "gaza", "ukraine", "nato", "united nations", "putin", "zelensky",
            "hamas", "taiwan", "beijing", "kremlin", "ceasefire", "vatican",
            "pope", "france", "paris", "germany", "europe", "africa",
            "middle east", "israel", "latin america", "asia",
        ],
    },
    {
        "slug": "money",
        "title": "Money & markets",
        "keywords": [
            "federal reserve", "interest rate", "inflation", "stock market",
            "wall street", "recession", "jobs report", "unemployment",
            "gross domestic product",
        ],
    },
    {
        "slug": "business",
        "title": "Business",
        "keywords": [
            "ipo", "initial public offering", "goes public", "going public",
            "s-1 filing", "ipo filing", "roadshow", "spac",
            "earnings report", "quarterly earnings", "merger", "acquisition",
            "venture capital", "funding round", "private equity",
            "stock buyback", "dividend", "market cap", "unicorn",
            "nasdaq listing", "nyse listing",
        ],
    },
    {
        "slug": "tech",
        "title": "TechTalk",
        "keywords": [
            "artificial intelligence", "openai", "nvidia", "large language model",
            "semiconductor", "data center", "startup", "silicon valley",
            "gadget", "smartphone", "iphone", "android", "app store",
            "cybersecurity", "cyberattack", "ransomware", "data breach",
            "quantum", "robot", "robotics", "humanoid", "drone",
            "microchip", "cloud computing", "electric vehicle",
        ],
    },
    {
        "slug": "denver",
        "title": "Denver & Colorado",
        "keywords": [
            "denver", "colorado", "aurora", "boulder", "colorado springs",
            "fort collins",
        ],
    },
    {
        "slug": "sports",
        "title": "Sports",
        "keywords": [
            "nfl", "mlb", "nba", "nhl", "super bowl", "world series",
            "olympics", "championship", "playoff", "broncos", "nuggets",
            "rockies", "avalanche",
        ],
    },
    {
        "slug": "culture",
        "title": "Culture",
        "keywords": [
            "hollywood", "box office", "grammy", "oscar", "netflix",
            "broadway", "album", "concert tour",
        ],
    },
    {
        "slug": "science",
        "title": "Science & health",
        "keywords": [
            "nasa", "spacex", "clinical trial", "vaccine", "cancer",
            "climate", "earthquake", "hurricane", "wildfire", "outbreak",
        ],
    },
]

FALLBACK_TOPIC: Dict = {"slug": "more", "title": "More news"}

MIN_HITS = 2  # distinct keyword hits needed to claim a topic


def classify(text: str) -> Dict:
    """Pick the topic whose keywords hit the text hardest.

    Scores by distinct keyword hits; ties go to the earlier topic, so the
    lead topic (trade) wins ties. Fewer than MIN_HITS distinct hits means
    the story doesn't belong to any topic — it lands in "More news".
    """
    low = (text or "").lower()
    best: Dict = FALLBACK_TOPIC
    best_hits = 0
    for topic in TOPICS:
        hits = sum(1 for kw in topic["keywords"] if kw in low)
        if hits > best_hits:
            best, best_hits = topic, hits
    if best_hits < MIN_HITS:
        return FALLBACK_TOPIC
    return best


def topic_for_slug(slug: str) -> Dict:
    """Topic dict for a stored slug; falls back to "More news"."""
    for topic in TOPICS:
        if topic["slug"] == slug:
            return topic
    return FALLBACK_TOPIC
