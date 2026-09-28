"""Market analysis for the News Network — S&P 500, Nasdaq, NYSE.

Pulls daily closes from Yahoo Finance's public chart API (no key needed),
then reports honest, checkable numbers: last close, day/week/month change,
and position vs the 20-day average. No forecasts, no invented numbers — if
the feed is unreachable the section says so.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List, Optional

INDEXES: List[Dict] = [
    {"slug": "sp500", "name": "S&P 500", "symbol": "^GSPC"},
    {"slug": "nasdaq", "name": "Nasdaq Composite", "symbol": "^IXIC"},
    {"slug": "nyse", "name": "NYSE Composite", "symbol": "^NYA"},
]

_CHART_URL = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=3mo&interval=1d"
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
_TRADING_MONTH = 22  # ~22 trading days in a month


def fetch_closes(symbol: str, timeout: int = 20) -> Optional[Dict]:
    """Daily closes for a symbol. Returns {as_of, closes[]} or None."""
    try:
        url = _CHART_URL.format(symbol=urllib.request.quote(symbol, safe="^"))
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        result = (payload.get("chart") or {}).get("result") or []
        if not result:
            return None
        meta = result[0].get("meta") or {}
        quote = (result[0].get("indicators") or {}).get("quote") or [{}]
        closes = [c for c in (quote[0].get("close") or []) if c]
        if len(closes) < 2:
            return None
        as_of = meta.get("regularMarketTime")
        as_of_str = (
            datetime.fromtimestamp(as_of, tz=timezone.utc).strftime("%Y-%m-%d")
            if as_of else "unknown date"
        )
        return {"as_of": as_of_str, "closes": closes}
    except Exception:
        return None


def analyze(closes: List[float]) -> Dict:
    """Honest arithmetic over daily closes — levels, changes, trend."""
    last = closes[-1]
    prev = closes[-2]
    week = closes[-6] if len(closes) >= 6 else closes[0]
    month = closes[-_TRADING_MONTH - 1] if len(closes) > _TRADING_MONTH else closes[0]
    window = closes[-20:]
    dma20 = sum(window) / len(window)
    return {
        "last": last,
        "day_pct": (last - prev) / prev * 100,
        "week_pct": (last - week) / week * 100,
        "month_pct": (last - month) / month * 100,
        "vs_dma20_pct": (last - dma20) / dma20 * 100,
        "above_dma20": last >= dma20,
    }


def fmt_pct(x: float) -> str:
    return f"{x:+.2f}%"


def market_section(drivers: List[Dict] | None = None) -> List[str]:
    """Markdown lines for the brief's Market analysis section.

    `drivers` is a list of {"title": ..., "dossier_link": ...} money-topic
    events — what's moving markets, in the reporters' own coverage.
    """
    lines: List[str] = []
    A = lines.append
    A("## Market analysis")
    A("")
    rows = []
    as_of = None
    for idx in INDEXES:
        data = fetch_closes(idx["symbol"])
        if not data:
            continue
        as_of = data["as_of"]
        a = analyze(data["closes"])
        trend = "above" if a["above_dma20"] else "below"
        rows.append(
            f"- **{idx['name']}** {a['last']:,.2f} "
            f"({fmt_pct(a['day_pct'])} today; {fmt_pct(a['week_pct'])} this week; "
            f"{fmt_pct(a['month_pct'])} this month; {trend} its 20-day average)"
        )
    if not rows:
        A("_Market data was unreachable for this run — no numbers invented._")
        A("")
        return lines
    A(f"_Index levels as of {as_of} (Yahoo Finance)._")
    A("")
    lines.extend(rows)
    A("")
    if drivers:
        A("### What's moving markets")
        A("")
        for d in drivers[:3]:
            A(f"- {d['title']} — [full dossier]({d['dossier_link']})")
        A("")
    return lines
