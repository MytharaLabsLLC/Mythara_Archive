"""Evidence packs — the structured material the witnesses consume.

Per event:
  claims          one-line factual claims, each tagged with outlet + url
  quotes          direct quotes with attribution when the text names a
                  speaker (attribution=None when it does not — recorded,
                  not guessed)
  actors          most-mentioned proper nouns across the event
  framing         how each outlet headlined/led the same event
  stated_intents  claims/quotes where an actor states a purpose
  observed_actions claims describing actions taken

Everything in the pack traces to a fetched article. Nothing is
paraphrased into new assertions: claims are sentences lifted from the
source text, verbatim.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Dict, List, Optional

from .cluster import proper_nouns

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_QUOTE_RE = re.compile(r'"([^"]{12,300})"')
# "..." said X  /  X said "..."  /  according to X, "..."
_ATTR_AFTER = re.compile(
    r'"[^"]{12,300}"\s*,?\s*(?:said|told|added|stated|declared|warned|argued|explained)\s+'
    r"([A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*){0,3})"
)
_ATTR_BEFORE = re.compile(
    r"([A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*){0,3})\s+"
    r"(?:said|told|added|stated|declared|warned|argued|explained)[^A-Za-z]*\"[^\"\n]{12,300}\""
)
_ATTR_ACCORDING = re.compile(
    r"according to\s+([A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*){0,3})"
)

_INTENT_VERBS = (
    "announced plans", "plans to", "aims to", "vowed to", "promised to",
    "pledged to", "will ", "intends to", "committed to", "proposed",
    "called for", "urged", "demanded",
)
_ACTION_VERBS = (
    "signed", "ordered", "launched", "deployed", "filed", "voted",
    "struck", "fired", "arrested", "banned", "approved", "rejected",
    "announced", "unveiled", "imposed", "lifted", "resigned", "acquired",
    "struck down", "blocked",
)


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text or "") if len(s.strip()) > 20]


def _claim_id(event_id: str, url: str, idx: int) -> str:
    return hashlib.sha256(f"{event_id}:{url}:{idx}".encode()).hexdigest()[:10]


def extract_quotes(text: str) -> List[Dict[str, Optional[str]]]:
    """Quoted spans with best-effort attribution. Never guessed."""
    out = []
    for m in _QUOTE_RE.finditer(text or ""):
        quote = m.group(1).strip()
        window = text[max(0, m.start() - 160): m.end() + 160]
        attr = None
        ma = _ATTR_AFTER.search(window) or _ATTR_BEFORE.search(window)
        if ma:
            attr = ma.group(1).strip(" .,'")
        else:
            mb = _ATTR_ACCORDING.search(window)
            if mb:
                attr = mb.group(1).strip(" .,'")
        out.append({"text": quote, "attributed_to": attr})
    return out


def _has_any(text: str, verbs) -> bool:
    low = text.lower()
    return any(v in low for v in verbs)


def build_evidence_pack(event: Dict) -> Dict:
    """Build the witness-consumable evidence pack for one event."""
    event_id = event["id"]
    claims: List[Dict] = []
    quotes: List[Dict] = []
    actor_counts: Counter = Counter()
    framing: List[Dict] = []
    stated_intents: List[str] = []   # claim ids
    observed_actions: List[str] = []  # claim ids

    for art in event["articles"]:
        body = f"{art.get('title', '')}. {art.get('summary', '')}"
        sents = _sentences(body)[:4]  # title + first sentences; bounded
        for i, sent in enumerate(sents):
            cid = _claim_id(event_id, art["url"], i)
            claims.append({
                "id": cid, "text": sent, "outlet": art["outlet"],
                "url": art["url"], "published": art.get("published"),
            })
            if _has_any(sent, _INTENT_VERBS):
                stated_intents.append(cid)
            if _has_any(sent, _ACTION_VERBS):
                observed_actions.append(cid)
        for q in extract_quotes(body):
            qid = _claim_id(event_id, art["url"] + "#q", len(quotes))
            quotes.append({
                "id": qid, "text": q["text"], "attributed_to": q["attributed_to"],
                "outlet": art["outlet"], "url": art["url"],
            })
            if q["attributed_to"] and _has_any(q["text"], ("will", "plan", "aim", "vow", "promise", "pledge", "intend")):
                stated_intents.append(qid)
        actor_counts.update(proper_nouns(body))
        lede = sents[0] if sents else ""
        framing.append({
            "outlet": art["outlet"], "headline": art.get("title", ""),
            "lede": lede, "url": art["url"],
        })

    # Actors: frequent proper nouns, minus the event's generic key terms noise
    actors = [t for t, _ in actor_counts.most_common(12)]

    return {
        "event_id": event_id,
        "key_terms": event["key_terms"],
        "outlets": event["outlets"],
        "article_count": event["article_count"],
        "earliest": event["earliest"],
        "latest": event["latest"],
        "claims": claims,
        "quotes": quotes,
        "actors": actors,
        "framing": framing,
        "stated_intents": sorted(set(stated_intents)),
        "observed_actions": sorted(set(observed_actions)),
    }
