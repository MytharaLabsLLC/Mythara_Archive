"""Tests for sere_aries.py — Aries at war, in the bronze jar.

What these prove:
  - The jar holds: anything that is not a vr:// target is refused.
  - The membrane holds: no exercise, no war; bad envelopes never dispatch.
  - The war is fake: zero real packets, zero real systems, zero real data.
  - The log is honest: the hash chain verifies, tampering is caught.
  - Aries learns: the playbook evolves with experience.
  - Separation: the defanged aries_bot.py cannot wage war.
"""

import json
import sys

import pytest

import sere_aries
from sere_aries import (
    AriesWar,
    ContainmentBreach,
    _assert_virtual_target,
)
from soul_cradle.authorization import (
    AuthorizationError,
    SoulCradleAuthority,
)


@pytest.fixture()
def war(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "chain.jsonl"),
        playbook_path=str(tmp_path / "playbook.json"),
    )
    eid = w.begin_exercise(objective="test exercise", operator="tester")
    yield w, eid
    try:
        w.end_exercise()
    except AuthorizationError:
        pass


# -- the bronze jar ---------------------------------------------------------

REAL_TARGETS = [
    "192.168.1.1",
    "10.0.0.5",
    "example.com",
    "https://example.com",
    "/etc/passwd",
    "C:\\Windows\\System32",
    "",
    "vr ://spoof",
]


def test_virtual_targets_accepted():
    assert _assert_virtual_target("vr://db-vault") == "vr://db-vault"


@pytest.mark.parametrize("bad", REAL_TARGETS)
def test_real_targets_refused_at_gate(bad):
    with pytest.raises(ContainmentBreach):
        _assert_virtual_target(bad)


@pytest.mark.parametrize("bad", REAL_TARGETS)
def test_war_tactics_refuse_real_targets(war, bad):
    w, _eid = war
    for tactic in (w.recon, w.flood, w.ravage):
        with pytest.raises(ContainmentBreach):
            tactic(bad)
    with pytest.raises(ContainmentBreach):
        w.breach(bad, "phishing")


def test_unknown_virtual_node_refused(war):
    w, _eid = war
    with pytest.raises(ContainmentBreach):
        w.flood("vr://no-such-node")


# -- the membrane: no exercise, no war --------------------------------------

def test_war_without_exercise_refused(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "c.jsonl"),
        playbook_path=str(tmp_path / "p.json"),
    )
    with pytest.raises(AuthorizationError):
        w.flood("vr://db-vault")


def test_wrong_purpose_cannot_mint(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "c.jsonl"),
        playbook_path=str(tmp_path / "p.json"),
    )
    with pytest.raises(AuthorizationError):
        w.authority.authorize(
            "war_flood",
            {"exercise_id": "x", "target": "vr://db-vault"},
            issuer="sere_command",
            purpose="not-an-exercise",
        )


def test_expired_envelope_never_dispatches(war):
    w, eid = war
    payload = {"exercise_id": eid, "target": "vr://db-vault", "intensity": 5}
    env = w.authority.authorize(
        "war_flood", payload, issuer="sere_command",
        purpose="sere_exercise", ttl_seconds=-1,
    )
    with pytest.raises(AuthorizationError):
        w.authority.dispatch(env, payload)


def test_tampered_payload_never_dispatches(war):
    w, eid = war
    payload = {"exercise_id": eid, "target": "vr://db-vault", "intensity": 5}
    env = w.authority.authorize(
        "war_flood", payload, issuer="sere_command", purpose="sere_exercise"
    )
    evil = dict(payload, intensity=10, target="vr://gateway")
    with pytest.raises(AuthorizationError):
        w.authority.dispatch(env, evil)


# -- the war is fake: zero real effects --------------------------------------

def test_module_has_no_real_weapons():
    """Parse the module's AST: no real weapon imports or calls, docstring
    mentions excluded by construction."""
    import ast

    tree = ast.parse(open(sere_aries.__file__, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in (
                    "socket",
                    "subprocess",
                    "pty",
                    "ctypes",
                ), f"forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in (
                "socket",
                "subprocess",
                "pty",
                "ctypes",
            ), f"forbidden from-import: {node.module}"
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in ("eval", "exec"), f"forbidden call: {func.id}()"
            elif isinstance(func, ast.Attribute):
                assert (func.attr, getattr(func.value, "id", "")) not in (
                    ("system", "os"),
                    ("popen", "os"),
                    ("run", "subprocess"),
                    ("Popen", "subprocess"),
                    ("call", "subprocess"),
                ), f"forbidden call: os/subprocess.{func.attr}"


def test_flood_sends_zero_real_packets(war):
    w, _eid = war
    before = set(sys.modules)
    out = w.flood("vr://db-vault", intensity=10)
    assert out["real_packets_sent"] == 0
    assert out["simulated"] is True
    assert "socket" not in set(sys.modules) - before


def test_breach_touches_zero_real_systems(war):
    w, _eid = war
    out = w.breach("vr://workstation-7", "phishing")
    assert out["real_systems_touched"] == 0
    assert out["breached"] is True  # the virtual node fell


def test_ravage_harms_zero_real_data(war):
    w, _eid = war
    w.breach("vr://workstation-7", "phishing")
    out = w.ravage("vr://workstation-7")
    assert out["real_data_harmed"] == 0
    assert out["ravaged"] is True  # ...but the virtual node burned


def test_ravage_uncompromised_node_does_nothing(war):
    w, _eid = war
    out = w.ravage("vr://gateway")
    assert out["ravaged"] is False


# -- defense by recording -----------------------------------------------------

def test_chain_verifies_after_exercise(war):
    w, _eid = war
    w.recon("vr://gateway")
    w.flood("vr://gateway", intensity=4)
    ok, msg = w.verify_chain()
    assert ok, msg
    assert "intact" in msg


def test_chain_catches_tampering(war):
    w, _eid = war
    w.recon("vr://gateway")
    path = w.chain_path
    lines = open(path, encoding="utf-8").read().strip().split("\n")
    rec = json.loads(lines[-1])
    rec["detail"] = {"forged": True}
    lines[-1] = json.dumps(rec)
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    ok, msg = w.verify_chain()
    assert not ok


# -- evolution ------------------------------------------------------------------

def test_playbook_evolves_with_experience(war):
    w, _eid = war
    before = dict(w.playbook["war_breach"])
    w.breach("vr://workstation-7", "phishing")
    after = w.playbook["war_breach"]
    assert after["attempts"] == before["attempts"] + 1
    assert after["successes"] == before["successes"] + 1


def test_campaign_runs_and_learns(war):
    w, _eid = war
    report = w.campaign(rounds=6)
    assert len(report) >= 1
    total_attempts = sum(v["attempts"] for v in w.playbook.values())
    assert total_attempts >= len([r for r in report if "refused" not in r])


# -- separation from the defanged Aries -----------------------------------------

def test_defanged_aries_cannot_wage_war():
    from aries_bot import AriesBot

    assert not issubclass(AriesWar, AriesBot)
    calm = AriesBot()  # the defanged executor, default authority
    with pytest.raises(AuthorizationError):
        calm.authority.authorize(
            "war_flood",
            {"exercise_id": "x", "target": "vr://db-vault"},
            issuer="olympus_council",
            purpose="sere_exercise",
        )


def test_war_handlers_are_simulation_only():
    import inspect

    handlers = {
        "war_recon": sere_aries._handle_war_recon,
        "war_flood": sere_aries._handle_war_flood,
        "war_breach": sere_aries._handle_war_breach,
        "war_ravage": sere_aries._handle_war_ravage,
    }
    for name, fn in handlers.items():
        src = inspect.getsource(fn)
        assert "socket" not in src, name
        assert "subprocess" not in src, name


# -- military expectations: ATT&CK, kill chain, AAR -----------------------------

def test_tactics_carry_attck_and_kill_chain(war):
    w, _eid = war
    checks = [
        (w.recon("vr://gateway"), "TA0043", "Reconnaissance"),
        (w.flood("vr://gateway"), "TA0040", "Actions on Objectives"),
        (w.breach("vr://workstation-7", "phishing"), "TA0001", "Exploitation"),
    ]
    w.breach("vr://workstation-7", "phishing")  # ensure compromised for ravage
    checks.append((w.ravage("vr://workstation-7"), "TA0040", "Actions on Objectives"))
    for out, tactic, kc in checks:
        attck = out.get("attck", {})
        assert attck.get("tactic") == tactic, out
        assert attck.get("tactic_name"), out
        assert attck.get("technique", "").startswith("T"), out
        assert attck.get("technique_name"), out
        assert out.get("kill_chain") == kc, out


def test_breach_vector_attck_mapping(war):
    w, _eid = war
    out = w.breach("vr://workstation-7", "phishing")
    assert out["attck"]["technique"] == "T1566"
    assert out["attck"]["technique_name"] == "Phishing"
    out2 = w.breach("vr://db-vault", "sql-injection")
    assert out2["attck"]["technique"] == "T1190"


def test_aar_has_military_sections(war, tmp_path):
    w, _eid = war
    w.recon("vr://gateway")
    w.flood("vr://gateway", intensity=6)
    w.breach("vr://workstation-7", "phishing")
    w.end_exercise()
    aar = w.generate_aar()
    for section in (
        "AFTER ACTION REVIEW",
        "OPFOR",
        "EXCON",
        "1. EXECUTIVE SUMMARY",
        "2. EXERCISE TIMELINE",
        "3. ATT&CK COVERAGE",
        "4. BLUE TEAM ASSESSMENT",
        "5. SUSTAIN / IMPROVE",
        "6. OPFOR EVOLUTION",
        "SIMULATION ONLY",
        "test exercise",  # the objective, reported not retold
    ):
        assert section in aar, f"missing section: {section}"


def test_aar_reflects_recorded_actions(war):
    w, _eid = war
    w.breach("vr://workstation-7", "phishing")
    w.end_exercise()
    aar = w.generate_aar()
    assert "war_breach" in aar
    assert "T1566" in aar
    assert "vr://workstation-7" in aar


def test_aar_honest_about_empty_exercise(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "c.jsonl"),
        playbook_path=str(tmp_path / "p.json"),
    )
    w.begin_exercise(objective="nothing happens", operator="tester")
    w.end_exercise()
    aar = w.generate_aar()
    assert "tested nothing" in aar


def test_aar_requires_exercise(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "c.jsonl"),
        playbook_path=str(tmp_path / "p.json"),
    )
    with pytest.raises(AuthorizationError):
        w.generate_aar()


def test_export_aar_writes_file(war, tmp_path):
    w, _eid = war
    w.recon("vr://gateway")
    w.end_exercise()
    path = w.export_aar(str(tmp_path / "aar.txt"))
    text = open(path, encoding="utf-8").read()
    assert "AFTER ACTION REVIEW" in text


# -- the professor --------------------------------------------------------------

def test_lesson_returns_teaching(war):
    w, _eid = war
    text = w.lesson("T1566")
    assert "Phishing" in text
    assert "Your turn" in text
    assert "_handle_war_breach" in text  # points at the real code


def test_lesson_unknown_technique_refused(war):
    w, _eid = war
    with pytest.raises(ValueError):
        w.lesson("T9999")


def test_aar_teaches_exercised_techniques(war):
    w, _eid = war
    w.breach("vr://workstation-7", "phishing")
    w.flood("vr://db-vault", intensity=7)
    w.end_exercise()
    aar = w.generate_aar()
    assert "7. PROFESSOR'S NOTES" in aar
    assert "T1566 — Phishing" in aar
    assert "T1498 — Network Denial of Service" in aar
    assert "Your turn" in aar
    # techniques NOT exercised are not taught
    assert "T1110 — Brute Force" not in aar


def test_aar_notes_are_honest_when_idle(tmp_path):
    w = AriesWar(
        chain_path=str(tmp_path / "c.jsonl"),
        playbook_path=str(tmp_path / "p.json"),
    )
    w.begin_exercise(objective="quiet", operator="tester")
    w.end_exercise()
    aar = w.generate_aar()
    assert "nothing to teach" in aar


# -- separation of powers -------------------------------------------------------

def test_war_handlers_never_enter_shared_registry(war):
    # The defanged Aries' world must stay exactly {emit_text, write_report},
    # no matter what the war machine does. This is the regression test for
    # the pollution bug: war handlers once registered globally.
    import sere_aries
    from soul_cradle.authorization import action_types

    w, _eid = war
    w.recon("vr://workstation-7")
    w.flood("vr://db-vault", intensity=6)
    assert "war_recon" not in action_types()
    assert "war_flood" not in action_types()
    assert set(action_types()) == {"emit_text", "write_report"}
    assert set(sere_aries._WAR_HANDLERS) == set(sere_aries.WAR_ACTIONS)


# -- professor notes: every entry complete and renderable ----------------------

def test_all_professor_notes_complete_and_render(war):
    from sere_aries import PROFESSOR_NOTES
    required = {"title", "builds", "what", "in_the_sim", "key_idea", "your_turn"}
    w, _eid = war
    assert len(PROFESSOR_NOTES) == 17
    for key, note in PROFESSOR_NOTES.items():
        assert required <= set(note), f"{key} missing {required - set(note)}"
        text = w.lesson(key)  # must render without KeyError
        assert note["title"] in text
        assert "Your turn" in text
