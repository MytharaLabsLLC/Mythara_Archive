"""Tests for sere_crucible.py — the final exam.

The crucible throws a trainee-built slime into the jar against Aries and
grades it. These tests prove the exam is fair and honest:
  - the professor's answer key passes with full marks;
  - a slime that does nothing fails;
  - a slime that engulfs innocents is penalized for false positives;
  - a slime that crashes is graded as dead, with the wound recorded;
  - anything that is not a SlimeBase subclass is refused at the door.
"""

import pytest

from sere_crucible import report_card, run_crucible
from sere_slime import Slime, SlimeBase


class LazySlime(SlimeBase):
    """A trainee who never built the organs. Does nothing."""

    def tick(self):
        return []


class ParanoidSlime(SlimeBase):
    """A trainee with eyes but no judgment: engulfs everything,
    including the innocent gateway. Never dissolves."""

    def tick(self):
        acted = []
        for node in self.world.nodes.values():
            if not node.isolated:
                node.isolated = True
                self._log("slime_engulf", {"target": node.vr_id,
                                          "note": "paranoia"})
                acted.append(f"engulfed {node.vr_id}")
        return acted


class ClumsySlime(SlimeBase):
    """A trainee whose heartbeat throws."""

    def tick(self):
        raise RuntimeError("tentacle spasm")


def test_answer_key_passes():
    grade = run_crucible(Slime)
    assert grade["score"] == 100
    assert grade["verdict"] == "The slime hunts."
    assert grade["chain_intact"] is True
    assert grade["innocents_engulfed"] == []
    assert set(grade["threats_neutralized"]) == {
        "vr://workstation-7", "vr://db-vault"}
    assert len(grade["techniques_learned"]) >= 3
    card = report_card(grade)
    assert "100/100" in card and "The slime hunts." in card


def test_lazy_slime_fails():
    grade = run_crucible(LazySlime)
    assert grade["score"] < 50
    assert grade["verdict"] == "Back to the lab."
    assert len(grade["threats_missed"]) == 2
    assert grade["chain_intact"] is True  # the exam itself is still recorded


def test_paranoid_slime_penalized_for_false_positives():
    grade = run_crucible(ParanoidSlime)
    assert "vr://gateway" in grade["innocents_engulfed"]
    assert grade["score"] < 50
    assert grade["verdict"] == "Back to the lab."


def test_crashing_slime_graded_dead():
    grade = run_crucible(ClumsySlime)
    assert grade["score"] == 0
    assert "died in the jar" in grade["verdict"]
    assert "RuntimeError" in grade["crash"]
    assert "tentacle spasm" in grade["crash"]


def test_non_slime_refused():
    with pytest.raises(ValueError):
        run_crucible(object)
    with pytest.raises(ValueError):
        run_crucible(SlimeBase)  # the contract itself is not a slime


def test_exam_is_deterministic():
    first = run_crucible(Slime, seed=7)
    second = run_crucible(Slime, seed=7)
    for grade in (first, second):
        grade.pop("chain_path")  # tempdir name differs; everything else must not
    assert first == second
