# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Tests for the prospect-discovery module.

All tests run against isolated temp state. No network, no witness log,
no sends — discovery is find-and-record only.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from Commercial.autonomous_outreach import config, discovery, prospects


@pytest.fixture()
def iso(tmp_path, monkeypatch):
    """Isolate the prospect store."""
    monkeypatch.setattr(config, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(
        config, "PROSPECTS_FILE", tmp_path / "state" / "prospects.jsonl"
    )
    return tmp_path


def _valid_record(**kw):
    rec = {
        "org": "Smith Family Law PLLC",
        "contact_name": "Jane Smith",
        "role": "Managing Partner",
        "email": "jane@smithfamilylaw.test",
        "email_verified": True,
        "email_source": "https://smithfamilylaw.test/contact",
        "field_sources": {
            "org": "https://smithfamilylaw.test/",
            "contact_name": "https://smithfamilylaw.test/team",
            "role": "https://smithfamilylaw.test/team",
            "email": "https://smithfamilylaw.test/contact",
        },
        "niche": "family-law-tx",
        "source_name": "firm-website",
        "observations": [
            {"fact": "Boutique firm, 4 attorneys per team page",
             "source": "https://smithfamilylaw.test/team"},
        ],
    }
    rec.update(kw)
    return rec


# --- source attribution ----------------------------------------------------

def test_validate_rejects_missing_org():
    with pytest.raises(ValueError, match="org name"):
        discovery.validate_record(_valid_record(org="  "))


def test_validate_rejects_field_without_source():
    rec = _valid_record()
    del rec["field_sources"]["role"]
    with pytest.raises(ValueError, match="no source URL"):
        discovery.validate_record(rec)


def test_validate_rejects_bad_source_url():
    rec = _valid_record()
    rec["field_sources"]["email"] = "not-a-url"
    with pytest.raises(ValueError, match="not a valid http"):
        discovery.validate_record(rec)


def test_validate_rejects_observation_without_source():
    rec = _valid_record(observations=[{"fact": "something", "source": ""}])
    with pytest.raises(ValueError, match="every observation"):
        discovery.validate_record(rec)


def test_validate_accepts_org_only_record():
    rec = {
        "org": "Doe Legal",
        "field_sources": {"org": "https://doelegal.test/"},
    }
    out = discovery.validate_record(rec)
    assert out["org"] == "Doe Legal" and out["fetched_at"]


# --- email verification flagging -------------------------------------------

def test_email_verified_must_be_bool():
    rec = _valid_record(email_verified="yes")
    with pytest.raises(ValueError, match="email_verified is not a bool"):
        discovery.validate_record(rec)


def test_unverified_email_needs_guess_basis():
    rec = _valid_record(email_verified=False, email_source="")
    with pytest.raises(ValueError, match="email_source"):
        discovery.validate_record(rec)


def test_derive_email_pattern_never_verified():
    for pattern in ("first.last", "firstlast", "f.last", "first", "first_last"):
        addr, verified = discovery.derive_email_pattern(
            "Jane", "Smith", "smithfamilylaw.test", pattern
        )
        assert verified is False
        assert addr.endswith("@smithfamilylaw.test")


def test_derive_email_pattern_rejects_unknown():
    with pytest.raises(ValueError, match="unknown email pattern"):
        discovery.derive_email_pattern("Jane", "Smith", "x.test", "weird")


def test_extract_emails_finds_observed():
    text = "Reach us at info@smithfamilylaw.test or jane@smithfamilylaw.test today."
    found = discovery.extract_emails_from_text(text)
    assert "info@smithfamilylaw.test" in found
    assert "jane@smithfamilylaw.test" in found


# --- rate limiter ------------------------------------------------------------

class _Clock:
    def __init__(self):
        self.t = 1000.0
        self.slept = []
    def __call__(self):
        return self.t
    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def test_rate_limiter_enforces_min_interval():
    c = _Clock()
    rl = discovery.RateLimiter(min_interval_s=2.0, clock=c, sleeper=c.sleep)
    assert rl.wait("example.com") == 0.0
    assert rl.wait("example.com") == pytest.approx(2.0)
    assert c.slept == [pytest.approx(2.0)]
    # a different host is unaffected
    assert rl.wait("other.com") == 0.0


def test_rate_limiter_backs_off_on_429_and_resets():
    c = _Clock()
    rl = discovery.RateLimiter(min_interval_s=0.0, backoff_base_s=5.0,
                               backoff_max_s=20.0, clock=c, sleeper=c.sleep)
    rl.wait("h.com")
    rl.note_result("h.com", 429)
    assert rl.backoff_level("h.com") == 1
    assert rl.wait("h.com") == pytest.approx(5.0)   # base
    rl.note_result("h.com", 429)
    assert rl.wait("h.com") == pytest.approx(10.0)  # doubled
    rl.note_result("h.com", 429)
    assert rl.wait("h.com") == pytest.approx(20.0)  # capped at max
    rl.note_result("h.com", 200)
    assert rl.backoff_level("h.com") == 0
    assert rl.wait("h.com") == 0.0                   # reset


# --- robots.txt --------------------------------------------------------------

_ROBOTS = """\
User-agent: *
Disallow: /private/
Disallow: /tmp

User-agent: MytharaBot
Disallow: /

User-agent: GoodBot
Allow: /public/
Disallow: /public/secret/
"""


def test_robots_default_group_disallow():
    assert discovery.robots_allows(_ROBOTS, "OtherBot", "/private/x") is False
    assert discovery.robots_allows(_ROBOTS, "OtherBot", "/open") is True


def test_robots_exact_agent_group_wins():
    assert discovery.robots_allows(_ROBOTS, "MytharaBot", "/anything") is False
    assert discovery.robots_allows(_ROBOTS, "GoodBot", "/public/page") is True


def test_robots_longest_match_wins():
    # /public/secret/ disallow is longer than /public/ allow
    assert discovery.robots_allows(_ROBOTS, "GoodBot", "/public/secret/f") is False


def test_robots_empty_is_allow_all():
    assert discovery.robots_allows("", "AnyBot", "/whatever") is True
    assert discovery.robots_allows(
        "User-agent: *\nDisallow:\n", "AnyBot", "/whatever") is True


# --- import into the prospect store ------------------------------------------

def test_signals_from_observations_keyword_map():
    rec = _valid_record()
    rec["observations"] = [
        {"fact": "YC Winter 2026, 2-person founding team", "source": "https://example.com/x"},
    ]
    sig = discovery.signals_for_record(rec)
    assert sig["team_size_fit"] is True
    assert sig["budget_signal"] is True


def test_import_records_lands_in_store_scored(iso):
    res = discovery.import_records([_valid_record()], source_name="firm-website")
    assert res == {"added": 1, "skipped": 0, "errors": []}
    allp = prospects._load_all()
    assert len(allp) == 1
    d = next(iter(allp.values()))
    assert d["company"] == "Smith Family Law PLLC"
    assert d["source"] == "discovery:firm-website"
    # verified email -> contactable (+20); boutique 4-attorney firm -> team_size_fit (+15)
    assert d["score"] == 35, d["score_reasons"]
    assert "email_verified: YES" in d["notes"]
    assert "https://smithfamilylaw.test/contact" in d["notes"]
    assert d["status"] == "new"


def test_import_records_flags_unverified_email(iso):
    addr, verified = discovery.derive_email_pattern(
        "Jane", "Smith", "smithfamilylaw.test", "first.last")
    rec = _valid_record(
        email=addr, email_verified=verified,
        email_source="pattern first.last@smithfamilylaw.test inferred from "
                     "listed jsmith@smithfamilylaw.test on contact page",
    )
    res = discovery.import_records([rec])
    assert res["added"] == 1
    d = next(iter(prospects._load_all().values()))
    assert "EMAIL UNVERIFIED" in d["notes"]
    # guessed email is NOT contactable -> no +20
    assert d["signals"]["contactable"] is False
    assert d["score"] == 15


def test_import_records_skips_duplicates_and_invalid(iso):
    ok = _valid_record()
    dup = _valid_record()  # same email -> duplicate
    bad = {"org": "", "field_sources": {}}
    res = discovery.import_records([ok, dup, bad])
    assert res["added"] == 1
    assert res["skipped"] == 2
    assert len(res["errors"]) == 2


def test_csv_roundtrip_through_existing_import(iso, tmp_path):
    rows = discovery.to_csv_rows([_valid_record()])
    assert rows[0]["contactable"] == "yes"
    csv_path = discovery.write_csv([_valid_record()], str(tmp_path / "d.csv"))
    res = prospects.import_csv(csv_path, source="discovery:csv")
    assert res["added"] == 1
    d = next(iter(prospects._load_all().values()))
    assert d["source"] == "discovery:csv"
    assert d["score"] == 35


def test_adapters_only_emit_observed(iso):
    text = "Contact our Houston office: intake@houstonfamilylaw.test"
    recs = discovery.adapt_firm_contact_page(
        "Houston Family Law", text, "https://houstonfamilylaw.test/contact")
    assert len(recs) == 1
    assert recs[0]["email_verified"] is True
    assert recs[0]["field_sources"]["email"] == \
        "https://houstonfamilylaw.test/contact"
    # no contact name invented
    assert "contact_name" not in recs[0]
    res = discovery.import_records(recs, source_name="firm-website")
    assert res["added"] == 1
