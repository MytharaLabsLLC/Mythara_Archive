"""Event clustering — group articles into events.

Two articles join the same event when they were published within
~36 hours of each other AND share enough proper nouns (Jaccard >= 0.25
with at least 2 shared). Union-find over the pairwise links. No ML
libraries; a transparent heuristic, documented as such.

A "proper noun" here is a heuristic: capitalized tokens (length > 2)
that are not sentence-initial common words and not in the stopword
list, plus capitalized bigrams ("White House"). It will miss things
and occasionally misfire — the dossiers show the key terms so any
reader can see what drove the clustering.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Dict, List, Set

TIME_WINDOW_S = 36 * 3600
JACCARD_THRESHOLD = 0.25
MIN_SHARED_NOUNS = 2

STOPWORDS = frozenset("""
a an the and or but if then else when while of at by for with about into
through during before after above below to from up down in out on off over
under again further once here there all any both each few more most other
some such no nor not only own same so than too very can will just don should
now i you he she it we they them his her its our their this that these those
am is are was were be been being have has had having do does did doing would
could ought i'm you're he's she's it's we're they're i've you've we've they've
i'd you'd he'd she'd we'd they'd i'll you'll he'll she'll we'll they'll isn't
aren't wasn't weren't hasn't haven't hadn't doesn't don't didn't won't wouldn't
shouldn't can't couldn't must let's that's who's what's here's there's when's
where's why's how's one two three new said says say will would could after
today yesterday monday tuesday wednesday thursday friday saturday sunday
january february march april may june july august september october november
december us u.s u.s. vs
""".split())

_CAP_WORD = re.compile(r"[A-Z][a-zA-Z.'-]{2,}")
_STRIP_CHARS = ".'-"
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def proper_nouns(text: str) -> Set[str]:
    """Heuristic proper-noun extraction: capitalized words and bigrams."""
    nouns: Set[str] = set()
    for sent in _SENT_SPLIT.split(text or ""):
        words = re.findall(r"[A-Za-z][\w.'-]*", sent)
        caps = [w for w in _CAP_WORD.findall(sent)]
        for w in caps:
            clean = w.strip(".'-")
            if len(clean) > 2 and clean.lower() not in STOPWORDS:
                nouns.add(clean)
        # bigrams of consecutive capitalized words ("White House")
        for a, b in zip(words, words[1:]):
            if (_CAP_WORD.fullmatch(a) and _CAP_WORD.fullmatch(b)
                    and a.lower() not in STOPWORDS and b.lower() not in STOPWORDS):
                nouns.add(f"{a.strip(_STRIP_CHARS)} {b.strip(_STRIP_CHARS)}")
    return nouns


def article_nouns(article: Dict) -> Set[str]:
    return proper_nouns(f"{article.get('title', '')} {article.get('summary', '')}")


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _overlap(a: Set[str], b: Set[str]) -> float:
    """Overlap coefficient: shared / smaller set. Forgiving when one
    article is much longer than the other (common across outlets)."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def cluster(articles: List[Dict]) -> List[Dict]:
    """Group articles into events. Returns event dicts, newest first.

    Event dict: id, articles, key_terms, outlets, earliest, latest,
    article_count.
    """
    n = len(articles)
    if n == 0:
        return []
    nouns = [article_nouns(a) for a in articles]
    uf = _UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            pi, pj = articles[i].get("published"), articles[j].get("published")
            if pi and pj and abs(pi - pj) > TIME_WINDOW_S:
                continue
            shared = nouns[i] & nouns[j]
            if (len(shared) >= MIN_SHARED_NOUNS
                    and (_jaccard(nouns[i], nouns[j]) >= JACCARD_THRESHOLD
                         or _overlap(nouns[i], nouns[j]) >= 0.35)):
                uf.union(i, j)

    groups: Dict[int, List[int]] = {}
    for i in range(n):
        groups.setdefault(uf.find(i), []).append(i)

    events = []
    for idxs in groups.values():
        members = [articles[i] for i in idxs]
        term_counts = Counter()
        for i in idxs:
            term_counts.update(nouns[i])
        key_terms = [t for t, _ in term_counts.most_common(8)]
        pubs = [m["published"] for m in members if m.get("published")]
        seed = min(members, key=lambda m: (m.get("published") or 0, m["url"]))
        event_id = hashlib.sha256(f"mnn-event:{seed['url']}".encode()).hexdigest()[:12]
        events.append({
            "id": event_id,
            "articles": members,
            "key_terms": key_terms,
            "outlets": sorted({m["outlet"] for m in members}),
            "earliest": min(pubs) if pubs else None,
            "latest": max(pubs) if pubs else None,
            "article_count": len(members),
        })
    events.sort(key=lambda e: (e["latest"] or 0), reverse=True)
    return events
