"""Market analysis tests — arithmetic is checked against fixtures, never the live feed."""

from news_network import market


def _closes(last=100.0, n=30, drift=0.0):
    # n daily closes ending at `last`, each day drifting by `drift` fraction
    closes = [last]
    for _ in range(n - 1):
        closes.append(closes[-1] / (1 + drift))
    return list(reversed(closes))


def test_analyze_flat_market():
    closes = _closes(last=100.0, n=30, drift=0.0)
    a = market.analyze(closes)
    assert a["last"] == 100.0
    assert abs(a["day_pct"]) < 1e-9
    assert abs(a["week_pct"]) < 1e-9
    assert abs(a["month_pct"]) < 1e-9
    assert a["above_dma20"] is True  # exactly on the average counts as above


def test_analyze_rising_market():
    closes = _closes(last=110.0, n=30, drift=0.005)
    a = market.analyze(closes)
    assert a["day_pct"] > 0
    assert a["week_pct"] > a["day_pct"] > 0
    assert a["month_pct"] > a["week_pct"] > 0
    assert a["above_dma20"] is True
    assert a["vs_dma20_pct"] > 0


def test_analyze_falling_market():
    closes = _closes(last=90.0, n=30, drift=-0.005)
    a = market.analyze(closes)
    assert a["day_pct"] < 0
    assert a["above_dma20"] is False
    assert a["vs_dma20_pct"] < 0


def test_analyze_short_history_does_not_crash():
    a = market.analyze([100.0, 101.0, 102.0])
    assert a["last"] == 102.0
    assert a["day_pct"] > 0


def test_fmt_pct_signs():
    assert market.fmt_pct(1.234) == "+1.23%"
    assert market.fmt_pct(-0.5) == "-0.50%"
    assert market.fmt_pct(0.0) == "+0.00%"


def test_market_section_failure_is_honest(monkeypatch):
    monkeypatch.setattr(market, "fetch_closes", lambda symbol: None)
    lines = market.market_section()
    text = "\n".join(lines)
    assert "## Market analysis" in text
    assert "unreachable" in text
    assert "S&P 500" not in text  # no numbers invented


def test_market_section_renders_rows(monkeypatch):
    closes = _closes(last=7743.41, n=45, drift=0.002)

    def fake_fetch(symbol):
        return {"as_of": "2026-09-25", "closes": list(closes)}

    monkeypatch.setattr(market, "fetch_closes", fake_fetch)
    lines = market.market_section(drivers=[
        {"title": "Fed holds rates", "dossier_link": "../dossiers/abc123.md"},
    ])
    text = "\n".join(lines)
    assert "7,743.41" in text
    assert "S&P 500" in text and "Nasdaq Composite" in text and "NYSE Composite" in text
    assert "What's moving markets" in text
    assert "Fed holds rates" in text
    assert "2026-09-25" in text
