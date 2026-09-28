"""RSS/Atom ingestion — stdlib only (urllib + xml.etree).

Fetches every source in sources.py, parses RSS 2.0 and Atom, and stores
raw articles as JSONL under state/articles/. Dedupes by URL against what
is already stored. Fetch failures are logged and skipped — never fatal,
never filled in with invented content.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

USER_AGENT = "MytharaNewsNetwork/1.0 (research ingest bot; contact: mytharalabs@yahoo.com)"
ATOM_NS = "{http://www.w3.org/2005/Atom}"

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Remove tags and unescape entities; collapse whitespace."""
    text = _TAG_RE.sub(" ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_pubdate(raw: str) -> Optional[int]:
    """Parse an RSS (RFC 822) or Atom (ISO 8601) date to epoch seconds."""
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except (ValueError, TypeError):
        pass
    try:
        iso = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except (ValueError, TypeError):
        return None


def _text(elem: Optional[ET.Element]) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def parse_feed(data: bytes, outlet: str) -> List[Dict]:
    """Parse RSS 2.0 or Atom bytes into raw article dicts."""
    root = ET.fromstring(data)
    articles: List[Dict] = []
    fetched_at = int(time.time())

    if root.tag == "rss" or root.find("channel") is not None:
        for item in root.findall(".//item"):
            link = _text(item.find("link")).strip()
            title = strip_html(_text(item.find("title")))
            summary = strip_html(_text(item.find("description")))
            pub = parse_pubdate(_text(item.find("pubDate")))
            # Aggregator feeds (e.g. Google News topic search) name the real
            # outlet per item in <source> and append " - Outlet" to the title.
            item_outlet = _text(item.find("source")) or outlet
            suffix = " - " + item_outlet
            if title.endswith(suffix):
                title = title[: -len(suffix)]
            if link and title:
                articles.append({
                    "url": link, "outlet": item_outlet, "title": title,
                    "published": pub, "summary": summary,
                    "fetched_at": fetched_at,
                })
    else:  # Atom
        for entry in root.findall(f".//{ATOM_NS}entry"):
            link = ""
            for l in entry.findall(f"{ATOM_NS}link"):
                href = (l.get("href") or "").strip()
                if href and l.get("rel", "alternate") == "alternate":
                    link = href
                    break
            title = strip_html(_text(entry.find(f"{ATOM_NS}title")))
            summary = strip_html(_text(entry.find(f"{ATOM_NS}summary")))
            if not summary:
                summary = strip_html(_text(entry.find(f"{ATOM_NS}content")))
            raw_date = _text(entry.find(f"{ATOM_NS}published")) or _text(entry.find(f"{ATOM_NS}updated"))
            pub = parse_pubdate(raw_date)
            if link and title:
                articles.append({
                    "url": link, "outlet": outlet, "title": title,
                    "published": pub, "summary": summary,
                    "fetched_at": fetched_at,
                })
    return articles


def fetch_source(source: Dict[str, str], timeout: int = 25) -> Tuple[List[Dict], Optional[str]]:
    """Fetch one source. Returns (articles, error_or_None)."""
    try:
        req = urllib.request.Request(source["url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return parse_feed(data, source["outlet"]), None
    except Exception as exc:  # network/parse failure: log it, move on
        return [], f"{type(exc).__name__}: {exc}"


def article_path(state_dir: Path) -> Path:
    p = state_dir / "articles"
    p.mkdir(parents=True, exist_ok=True)
    return p / "articles.jsonl"


def load_known_urls(state_dir: Path) -> set:
    """URLs already ingested (dedupe key)."""
    path = article_path(state_dir)
    known = set()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        known.add(json.loads(line)["url"])
                    except (json.JSONDecodeError, KeyError):
                        continue
    return known


def ingest(sources: List[Dict[str, str]], state_dir: Path) -> Dict:
    """Fetch all sources, append new articles, return a run report.

    The report is honest by construction: per-feed article counts and
    per-feed errors. A feed that fails contributes zero articles and an
    error string — nothing is ever synthesized to fill the gap.
    """
    state_dir = Path(state_dir)
    known = load_known_urls(state_dir)
    path = article_path(state_dir)
    log_path = state_dir / "ingest_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    new_count = 0
    per_feed: List[Dict] = []
    with open(path, "a", encoding="utf-8") as out, \
         open(log_path, "a", encoding="utf-8") as log:
        for src in sources:
            articles, error = fetch_source(src)
            fresh = [a for a in articles if a["url"] not in known]
            for a in fresh:
                out.write(json.dumps(a, ensure_ascii=False) + "\n")
                known.add(a["url"])
            new_count += len(fresh)
            entry = {
                "ts": int(time.time()),
                "source_id": src["id"],
                "outlet": src["outlet"],
                "fetched": len(articles),
                "new": len(fresh),
                "error": error,
            }
            per_feed.append(entry)
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "new_articles": new_count,
        "feeds": per_feed,
        "failed": [e for e in per_feed if e["error"]],
    }


def load_articles(state_dir: Path) -> List[Dict]:
    """Read all ingested articles back."""
    path = article_path(state_dir)
    articles: List[Dict] = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        articles.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return articles
