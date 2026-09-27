# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Tests for the autonomous outreach machine.

All tests run in DRY-RUN against isolated temp state. The real witness
log and benevolence ledger are NEVER touched (safety.witness_send is
stubbed; reservoir tier is monkeypatched).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from Commercial.autonomous_outreach import (
    config, learning, prospects, research, safety, sender, sequences, triage, voice,
)
from Commercial.autonomous_outreach import run as runmod
from soul_cradle.bot_witness import WitnessBlocked, WitnessUnavailable

# Reference to the REAL witness_send, captured before the iso fixture stubs it.
_REAL_WITNESS_SEND = safety.witness_send


@pytest.fixture()
def iso(tmp_path, monkeypatch):
    """Isolate every state file + stub the witness + reservoir."""
    monkeypatch.setattr(config, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(config, "ESCALATION_DIR", tmp_path / "esc")
    for name in ("PROSPECTS_FILE", "SEND_LOG_FILE", "VARIANT_STATS_FILE",
                 "DAILY_COUNT_FILE", "SUPPRESSION_FILE"):
        monkeypatch.setattr(config, name, tmp_path / "state" / Path(getattr(config, name)).name)
    monkeypatch.setattr(config, "KILL_SWITCH_FILE", tmp_path / "STOP")
    monkeypatch.setattr(config, "MAX_NEW_PROSPECTS_PER_DAY", 10)
    monkeypatch.setattr(config, "MAX_FOLLOWUPS_PER_DAY", 15)
    monkeypatch.setattr(config, "MAX_TOTAL_SENDS_PER_DAY", 25)
    monkeypatch.setattr(config, "MIN_SECONDS_BETWEEN_SENDS", 0)
    calls = []
    def fake_witness_send(**kw):
        calls.append(kw)
        # Minimal witness result so the notary-receipt path is exercised.
        from types import SimpleNamespace
        return SimpleNamespace(
            bot_id="autonomous_outreach",
            action="send email to test@example.com: test",
            verdict="CLEAR",
            note="test stub: panel clear",
            entry_hash="test-entry-hash",
            judgments=[
                {"assessor_id": "demeter", "verdict": "CLEAR"},
                {"assessor_id": "hades", "verdict": "CLEAR"},
            ],
        )
    monkeypatch.setattr(safety, "witness_send", fake_witness_send)
    monkeypatch.setattr(safety.benevolence, "latitude", lambda *a: ("flowing", "test"))
    monkeypatch.setattr(runmod, "_gmail_service_if_available", lambda: None)
    monkeypatch.setattr("Commercial.autonomous_outreach.sender._last_send_path",
                        tmp_path / "last_ts.txt")
    return {"witness_calls": calls, "tmp": tmp_path}


def _mk_prospect(signals=None):
    return prospects.add_prospect(
        "Ada Founder", "ada@example.com", company="Acme AI", role="CEO",
        signals=signals or {"deploys_ai_agents": True, "team_size_fit": True,
                            "contactable": True},
        source="test",
    )


def _mk_brief():
    return research.build_brief(
        facts=[{"fact": "Acme AI ships a support agent to 200 customers.",
                "source": "acme.ai launch post"}],
        reason_for_contact="They ship agents to real users with no visible audit story.",
    )


# --- safety gates ------------------------------------------------------------

def test_kill_switch_halts_everything(iso, monkeypatch):
    config.KILL_SWITCH_FILE.write_text("stop", encoding="utf-8")
    ok, reason = safety.clear_to_send("a@b.com", "new")
    assert not ok and "kill switch" in reason
    rep = runmod.run_cycle(sender.DryRunSender(out_dir=iso["tmp"] / "dry"))
    assert rep["halted"] == "kill switch engaged"
    assert rep["first_touches_sent"] == 0


def test_depleted_reservoir_halts_and_escalates(iso, monkeypatch):
    monkeypatch.setattr(safety.benevolence, "latitude",
                        lambda *a: ("depleted", "empty"))
    ok, reason = safety.clear_to_send("a@b.com", "new")
    assert not ok and "depleted" in reason
    rep = runmod.run_cycle(sender.DryRunSender(out_dir=iso["tmp"] / "dry"))
    assert rep["halted"] == "reservoir depleted"
    assert len(rep["escalations"]) == 1


def test_witness_block_never_sends(iso, monkeypatch):
    def boom(**kw):
        raise WitnessBlocked("nemesis: deception")
    monkeypatch.setattr(safety, "witness_send", boom)
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.DryRunSender(out_dir=iso["tmp"] / "dry")
    with pytest.raises(WitnessBlocked):
        runmod._execute_send(d, "s", "b", "new", 1, "direct", snd)
    assert list((iso["tmp"] / "dry").glob("*.eml")) == []
    assert safety.daily_sent_total() == {"new": 0, "followup": 0}


def test_witness_outage_fails_closed(iso, monkeypatch):
    """No pre-send approval remains, so an outage must NOT send."""
    def boom(**kw):
        raise WitnessUnavailable("panel down")
    monkeypatch.setattr(safety, "witness_send", boom)
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.DryRunSender(out_dir=iso["tmp"] / "dry")
    with pytest.raises(WitnessUnavailable):
        runmod._execute_send(d, "s", "b", "new", 1, "direct", snd)
    assert list((iso["tmp"] / "dry").glob("*.eml")) == []


def test_daily_caps_enforced(iso, monkeypatch):
    monkeypatch.setattr(config, "MAX_NEW_PROSPECTS_PER_DAY", 1)
    for i in range(3):
        d = prospects.add_prospect(f"P{i}", f"p{i}@x.com",
                                   signals={"contactable": True})
        research.attach_brief(d["id"], _mk_brief())
    snd = sender.DryRunSender(out_dir=iso["tmp"] / "dry")
    rep = runmod.run_cycle(snd)
    assert rep["first_touches_sent"] == 1
    # the other two were never attempted — the cap stops attempts, not sends
    remaining = [d for d in prospects._load_all().values()
                 if d["status"] == prospects.STATUS_RESEARCHED]
    assert len(remaining) == 2


def test_suppressed_address_never_mailed(iso):
    safety.suppress("nope@x.com", "unsubscribe")
    ok, reason = safety.clear_to_send("NOPE@x.com", "new")
    assert not ok and "suppressed" in reason


def test_channel_whitelist(iso):
    ok, reason = safety.clear_to_send("a@b.com", "new", channel="linkedin")
    assert not ok and "not in" in reason


def test_manipulation_scan():
    assert safety.scan_manipulation("only 2 slots left at $500") != []
    assert safety.scan_manipulation("loved your recent post!") != []
    assert safety.scan_manipulation("3 banks already signed") != []
    assert safety.scan_manipulation(
        "Hi Ada, quick question about your agent audit trail.") == []


def test_manipulative_copy_blocked_by_real_panel(iso, monkeypatch, tmp_path):
    """The scan makes the evidence honest; the real panel must then block."""
    from soul_cradle import bot_witness, benevolence
    monkeypatch.setattr(bot_witness, "ACTION_LOG_PATH", tmp_path / "a.jsonl")
    monkeypatch.setattr(benevolence, "LEDGER_PATH", tmp_path / "l.jsonl")
    evil = ("Hi, loved your recent post! Only 2 slots left at $500, "
            "pricing expires Friday. 3 banks already signed.")
    with pytest.raises(WitnessBlocked):
        _REAL_WITNESS_SEND(subject="Act now", body=evil,
                           recipient_email="v@x.com", declared_intent="test")
    # honest copy passes the same gate
    _REAL_WITNESS_SEND(subject="quick question",
                       body="Hi Ada, how do you audit your agents?",
                       recipient_email="v@x.com", declared_intent="test")


# --- prospects / research ------------------------------------------------------

def test_duplicate_email_refused(iso):
    _mk_prospect()
    with pytest.raises(ValueError):
        prospects.add_prospect("Other", "ADA@example.com")


def test_scoring_is_honest_about_missing_signals(iso):
    d = prospects.add_prospect("N", "n@x.com", signals={})
    assert d["score"] == 0
    d2 = prospects.add_prospect("Y", "y@x.com",
                                signals={"deploys_ai_agents": True})
    assert d2["score"] == 30


def test_brief_requires_facts_with_sources_and_reason(iso):
    with pytest.raises(ValueError):
        research.build_brief(facts=[{"fact": "x"}], reason_for_contact="r")
    with pytest.raises(ValueError):
        research.build_brief(facts=[], reason_for_contact="")
    b = _mk_brief()
    assert b["facts"][0]["source"] == "acme.ai launch post"


# --- voice --------------------------------------------------------------------

def test_compose_renders_only_brief_facts(iso):
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    d = prospects.get(d["id"])
    for variant in voice.VARIANTS:
        subject, body = voice.compose(d, variant, touch_n=1)
        assert "Acme AI ships a support agent to 200 customers." in body
        assert "loved your" not in body.lower()
        assert "reply 'stop'" in body  # honest footer + opt-out
        assert "mythara.engine@yahoo.com" in body


def test_compose_honest_when_brief_has_no_facts(iso):
    d = _mk_prospect()
    research.attach_brief(d["id"], research.build_brief(
        facts=[], reason_for_contact="Cold but qualified guess."))
    d = prospects.get(d["id"])
    _, body = voice.compose(d, "direct", touch_n=1)
    assert "don't know much about your setup yet" in body


def test_followups_compose_and_stop(iso):
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    d = prospects.get(d["id"])
    s2, b2 = voice.compose(d, "direct", touch_n=2)
    s3, b3 = voice.compose(d, "direct", touch_n=3)
    assert "last note from me" in b3.lower() or "closing the loop" in s3.lower()


# --- learning ------------------------------------------------------------------

def test_learning_explore_and_champion(tmp_path):
    p = tmp_path / "vs.json"
    import random
    rng = random.Random(0)
    # all unseen: explore or first variant
    v = learning.select_variant(explore_rate=0.0, path=p, rng=rng)
    assert v in voice.VARIANTS
    learning.record_outcome("question", "interested", path=p)
    learning.record_outcome("question", "interested", path=p)
    learning.record_outcome("direct", "unsubscribe", path=p)
    champ = learning.champion(path=p)
    assert champ == "question"
    # with explore_rate=1.0 we get randomness across variants eventually
    seen = {learning.select_variant(explore_rate=1.0, path=p, rng=rng)
            for _ in range(50)}
    assert seen == set(voice.VARIANTS)


# --- triage ---------------------------------------------------------------------

def test_classify_reply():
    assert triage.classify_reply("Re: hello", "This is great, let's book a call") == "interested"
    assert triage.classify_reply("Re: hello", "How does the audit work?") == "question"
    assert triage.classify_reply("Re: hello", "Not interested, thanks") == "not_interested"
    assert triage.classify_reply("Re: hello", "Please unsubscribe me") == "unsubscribe"
    assert triage.classify_reply("Undeliverable", "Delivery failure") == "bounced"
    assert triage.classify_reply("Out of office", "I am on vacation") == "autoresponder"


def test_hot_reply_escalates(iso):
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    prospects.record_touch(d["id"], 1, "direct", "abc")
    done = triage.route_classification(d["id"], "interested", "Re: hi", "let's talk!")
    assert done["action"] == "escalated_to_herb"
    assert Path(done["file"]).exists()
    assert "Operator" in Path(done["file"]).read_text()
    assert prospects.get(d["id"])["status"] == prospects.STATUS_INTERESTED


def test_unsubscribe_suppresses_forever(iso):
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    prospects.record_touch(d["id"], 1, "direct", "abc")
    done = triage.route_classification(d["id"], "unsubscribe")
    assert done["action"] == "suppressed_unsubscribe"
    ok, _ = safety.clear_to_send("ada@example.com", "new")
    assert not ok


# --- end-to-end dry run ------------------------------------------------------------

def test_full_cycle_dryrun(iso, monkeypatch):
    monkeypatch.setattr(config, "MAX_NEW_PROSPECTS_PER_DAY", 10)
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.DryRunSender(out_dir=iso["tmp"] / "dry")
    rep = runmod.run_cycle(snd)
    assert rep["first_touches_sent"] == 1
    assert rep["halted"] is None
    assert len(list((iso["tmp"] / "dry").glob("*.eml"))) == 1
    # send ledger + touch recorded + witness stub called
    log = [json.loads(l) for l in config.SEND_LOG_FILE.read_text().splitlines()]
    assert log[0]["status"] == "DRY_RUN" and log[0]["to"] == "ada@example.com"
    assert len(iso["witness_calls"]) == 1
    assert prospects.get(d["id"])["status"] == prospects.STATUS_SENT
    # second cycle: no duplicate first touch
    rep2 = runmod.run_cycle(snd)
    assert rep2["first_touches_sent"] == 0


def test_followup_due_logic(iso, monkeypatch):
    monkeypatch.setattr(config, "FOLLOWUP_SCHEDULE", (0,))  # due immediately
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    prospects.record_touch(d["id"], 1, "direct", "abc")
    # backdate the touch so the follow-up is due
    allp = prospects._load_all()
    allp[d["id"]]["touches"][0]["at"] = (
        datetime.now() - timedelta(days=1)).isoformat(timespec="seconds")
    prospects._save_all(allp)
    due = sequences.due_followups()
    assert len(due) == 1 and due[0][1] == 2


def test_gmail_sender_blocked_without_credentials(iso):
    with pytest.raises(sender.SenderBlocked) as exc:
        sender.GmailSender().send("a@b.com", "s", "b")
    # either missing libs or missing token — both must be actionable, never silent
    msg = str(exc.value)
    assert "pip install" in msg or "BLOCKED" in msg


def test_yahoo_sender_blocked_without_keyfile(iso, tmp_path, monkeypatch):
    # Point the key file at an empty temp dir: no password file exists.
    monkeypatch.setattr(config, "YAHOO_KEY_FILE", tmp_path / ".yahoo_app_password")
    with pytest.raises(sender.SenderBlocked) as exc:
        sender.YahooSMTPSender().send("a@b.com", "s", "b")
    assert "BLOCKED" in str(exc.value)
    assert "App passwords" in str(exc.value)


def test_yahoo_sender_selected_by_mode(iso):
    assert isinstance(sender.get_sender("yahoo"), sender.YahooSMTPSender)
    assert isinstance(sender.get_sender("dryrun"), sender.DryRunSender)


# --- redesign: operator-run pipeline ------------------------------------------

def test_yahoo_imap_unreadable_without_keyfile(iso, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "YAHOO_KEY_FILE", tmp_path / ".nope")
    assert triage.yahoo_inbox_readable() is False
    assert triage.fetch_recent_replies_yahoo() == []


def test_real_send_blocked_without_postal_address(iso, monkeypatch):
    monkeypatch.setattr(config, "CANSPAM_POSTAL_ADDRESS", "")
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.YahooSMTPSender()
    import pytest as _pt
    with _pt.raises(safety.SafetyHalt) as exc:
        runmod._execute_send(d, "s", "b", "new", 1, "direct", snd)
    assert "canspam_postal_address" in str(exc.value).lower()


def test_real_send_allowed_with_postal_address_but_no_keyfile(iso, monkeypatch):
    # The CAN-SPAM gate passes; the missing key file is what stops it —
    # proving the address gate is the first thing checked, not the last.
    monkeypatch.setattr(config, "CANSPAM_POSTAL_ADDRESS", "123 Main St, Denver CO")
    monkeypatch.setattr(config, "YAHOO_KEY_FILE", iso["tmp"] / ".nope")
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.YahooSMTPSender()
    import pytest as _pt
    with _pt.raises(sender.SenderBlocked):
        runmod._execute_send(d, "s", "b", "new", 1, "direct", snd)


def test_footer_carries_postal_address_when_set(iso, monkeypatch):
    monkeypatch.setattr(config, "CANSPAM_POSTAL_ADDRESS", "123 Main St, Denver CO")
    assert "123 Main St, Denver CO" in voice._footer()
    monkeypatch.setattr(config, "CANSPAM_POSTAL_ADDRESS", "")
    assert "123 Main St" not in voice._footer()
    assert "reply 'stop'" in voice._footer()  # honest footer always present


def test_operator_brief_written_each_cycle(iso, monkeypatch):
    d = _mk_prospect(); research.attach_brief(d["id"], _mk_brief())
    snd = sender.DryRunSender(out_dir=iso["tmp"] / "dry")
    rep = runmod.run_cycle(snd)
    brief = iso["tmp"] / "state" / "operator_brief.md"
    assert brief.exists()
    text = brief.read_text()
    assert "sender mode: dryrun" in text
    assert "inbox: unreadable" in text  # no key file, no gmail in tests
    assert f"first touches sent: {rep['first_touches_sent']}" in text
