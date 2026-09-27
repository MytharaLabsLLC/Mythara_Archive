"""Tests for sere_slime.py — SERE's hunter inside the bronze jar.

What these prove:
  - The hunt works: sense -> engulf -> study -> dissolve -> learn.
  - An engulfed node is cut off: OPFOR blows against it are refused.
  - Study is a real forensic replay from the chained log.
  - The slime learns: recognized techniques are remembered.
  - Containment: the slime cannot be aimed at anything real.
  - Mass is metabolism: no mass, dormant.
  - The AAR records the hunt.
"""

import pytest

from sere_aries import AriesWar, ContainmentBreach, VirtualNode
from sere_slime import Slime


@pytest.fixture()
def ex(tmp_path):
    war = AriesWar(
        chain_path=str(tmp_path / "chain.jsonl"),
        playbook_path=str(tmp_path / "playbook.json"),
    )
    eid = war.begin_exercise(objective="slime test", operator="tester")
    slime = Slime(war.world, chain_path=str(tmp_path / "chain.jsonl"),
                  exercise_id=eid)
    yield war, slime, eid
    try:
        war.end_exercise()
    except Exception:
        pass


def test_slime_engulfs_then_dissolves(ex):
    war, slime, _eid = ex
    war.breach("vr://workstation-7", "phishing")
    assert slime.tick() == ["engulfed vr://workstation-7"]
    node = war.world.get("vr://workstation-7")
    assert node.isolated is True
    acted = slime.tick()
    assert acted == ["dissolved threat on vr://workstation-7"]
    assert node.compromised is False
    assert node.isolated is False
    assert node.implants == 0
    assert slime.dissolved_count == 1


def test_slime_blocks_opfor_on_engulfed_node(ex):
    war, slime, _eid = ex
    war.breach("vr://workstation-7", "phishing")
    node = war.world.get("vr://workstation-7")
    slime.engulf(node)
    flood_out = war.flood("vr://workstation-7", intensity=9)
    assert flood_out.get("refused_by") == "SLIME"
    breach_out = war.breach("vr://workstation-7", "smb-relay")
    assert breach_out.get("refused_by") == "SLIME"
    # recon still works — observation is not attack — and reports the truth
    recon_out = war.recon("vr://workstation-7")
    assert recon_out["engulfed_by_slime"] is True


def test_slime_study_replays_ttps(ex):
    war, slime, _eid = ex
    war.breach("vr://workstation-7", "phishing")
    war.flood("vr://workstation-7", intensity=8)
    node = war.world.get("vr://workstation-7")
    findings = slime.study(node)
    assert findings["verdict"] == "malicious pattern confirmed"
    assert "T1566" in findings["techniques_observed"]
    assert "T1498" in findings["techniques_observed"]
    assert findings["actions_replayed"] == 2


def test_slime_learns_and_recognizes(ex):
    war, slime, _eid = ex
    assert slime.recognize("T1566") is False
    war.breach("vr://workstation-7", "phishing")
    slime.tick()
    slime.tick()
    assert slime.recognize("T1566") is True
    assert slime.recognize("T9999") is False


def test_slime_refuses_nonvirtual_targets(ex):
    bad = VirtualNode(vr_id="10.0.0.5", name="real-box")
    slime = Slime.__new__(Slime)  # no world needed: the gate fires first
    with pytest.raises(ContainmentBreach):
        Slime.engulf(slime, bad)
    with pytest.raises(ContainmentBreach):
        Slime.study(slime, bad)
    with pytest.raises(ContainmentBreach):
        Slime.dissolve(slime, bad)


def test_slime_dormant_without_mass(ex):
    war, slime, eid = ex
    starved = Slime(war.world, chain_path=slime.chain_path,
                   exercise_id=eid, mass=0)
    war.breach("vr://workstation-7", "phishing")
    assert starved.tick() == ["dormant — no mass"]
    assert war.world.get("vr://workstation-7").compromised is True


def test_slime_mass_economy(ex):
    war, slime, _eid = ex
    assert slime.mass == 100.0
    slime.tick()  # quiet tick burns a little
    assert slime.mass == 99.0
    war.breach("vr://workstation-7", "phishing")
    slime.tick()  # engulf
    slime.tick()  # dissolve feeds
    assert slime.mass == 122.0


def test_slime_hunt_in_aar(ex):
    war, slime, _eid = ex
    war.breach("vr://workstation-7", "phishing")
    slime.tick()
    slime.tick()
    war.end_exercise()
    aar = war.generate_aar()
    assert "[SLIME]" in aar
    assert "slime_engulf" in aar
    assert "slime_dissolve" in aar
