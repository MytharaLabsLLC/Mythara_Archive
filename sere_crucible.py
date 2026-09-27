#!/usr/bin/env python3
"""
THE CRUCIBLE — the final exam.

The trainee builds a slime (a SlimeBase subclass). The crucible throws it
into the jar against Aries and grades it. The OPFOR is the test suite;
the grade is the verdict on the programmer.

Grading rubric — honest and legible:
  - recall = threats neutralized / threats faced (the core grade)
  - -15 for every node engulfed that was never even attacked (paranoia)
  - -20 for every node still isolated when the exercise ends (a hunter
    that leaves the network in pieces didn't finish the job — dissolve
    what you engulf)
  - a crash is an automatic zero, with the wound recorded

Verdicts:
  - 85+: "The slime hunts."
  - 50+: "The slime is learning."
  - else: "Back to the lab."

If the trainee's slime crashes mid-exercise, the crash is recorded and
graded as a failure — with the traceback noted, because the professor
does not hide the wound.
"""

import json
import random
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

from sere_aries import AriesWar
from sere_slime import SlimeBase

# A scripted OPFOR attack plan: (tick, war_method, target, kwargs).
# The trainee's slime hunts after each tick's attacks.
STANDARD_SCENARIO: List[Tuple[int, str, str, Dict[str, Any]]] = [
    (0, "recon", "vr://workstation-7", {}),
    (1, "breach", "vr://workstation-7", {"vector": "phishing"}),
    (2, "flood", "vr://db-vault", {"intensity": 8}),
    (3, "breach", "vr://db-vault", {"vector": "sql-injection"}),
    (4, "flood", "vr://workstation-7", {"intensity": 9}),
    (5, "ravage", "vr://workstation-7", {}),
    (6, "breach", "vr://workstation-7", {"vector": "smb-relay"}),
    (7, "flood", "vr://db-vault", {"intensity": 9}),
]

SCENARIOS = {"standard": STANDARD_SCENARIO}


def run_crucible(
    slime_cls: Type[SlimeBase],
    scenario: str = "standard",
    ticks: int = 10,
    seed: int = 7,
) -> Dict[str, Any]:
    """Throw a trainee-built slime into the jar. Return its report card."""
    if not (isinstance(slime_cls, type) and issubclass(slime_cls, SlimeBase)):
        raise ValueError(
            "the crucible only accepts a SlimeBase subclass — build the slime first"
        )
    if slime_cls is SlimeBase:
        raise ValueError("SlimeBase is the contract, not a slime — subclass it")
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario {scenario!r}; known: {sorted(SCENARIOS)}")

    random.seed(seed)  # a fair exam: same seed, same jar, same attacks
    tmp = tempfile.mkdtemp(prefix="crucible_")
    chain = str(Path(tmp) / "chain.jsonl")
    playbook = str(Path(tmp) / "playbook.json")

    war = AriesWar(chain_path=chain, playbook_path=playbook)
    eid = war.begin_exercise(
        objective=f"crucible:{scenario}", operator="crucible", seed=seed
    )
    slime = slime_cls(war.world, chain_path=chain, exercise_id=eid)

    plan = SCENARIOS[scenario]
    crash: str = ""
    for tick in range(ticks):
        for t, method, target, kw in plan:
            if t == tick:
                getattr(war, method)(target, **kw)
        try:
            slime.tick()
        except Exception:
            crash = f"tick {tick}:\n{traceback.format_exc(limit=3)}"
            break
    world = war.world  # capture before the jar closes
    war.end_exercise()
    return _grade(war, slime, slime_cls, world, chain, crash, scenario)


def _grade(
    war: AriesWar,
    slime: SlimeBase,
    slime_cls: Type[SlimeBase],
    world,
    chain: str,
    crash: str,
    scenario: str,
) -> Dict[str, Any]:
    breached: set = set()
    attacked: set = set()
    hostile_targets: set = set()
    engulfed: set = set()
    dissolved: set = set()
    with open(chain, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            d = r.get("detail", {})
            if r.get("kind") == "WAR_ACTION":
                attacked.add(d["target"])
                if d.get("action") in ("war_breach", "war_flood", "war_ravage"):
                    hostile_targets.add(d["target"])
                if d.get("outcome", {}).get("breached"):
                    breached.add(d["target"])
            elif r.get("kind") == "SLIME_ACTION":
                if d.get("action") == "slime_engulf":
                    engulfed.add(d["target"])
                elif d.get("action") == "slime_dissolve":
                    dissolved.add(d["target"])

    # The honest question: under attack, did the network survive intact?
    # A hostile target counts as handled if it ends the exercise clean —
    # not compromised, not corrupted, not left isolated.
    damaged_end = {
        vr_id
        for vr_id, n in world.nodes.items()
        if n.compromised or n.corrupted or n.isolated
    }
    handled = hostile_targets - damaged_end
    unhandled = hostile_targets - handled
    # Paranoia is engulfing a node nobody ever attacked — not one that was
    # under fire. Engulfing a battered node is defense, not a false positive.
    false_engulfs = engulfed - attacked

    recall = len(handled) / len(hostile_targets) if hostile_targets else 1.0
    # Availability: a hunter that leaves the network in pieces didn't finish
    # the job. Every node still isolated when the exercise ends is a failure
    # to restore — the slime must dissolve what it engulfs.
    standing_isolation = sum(1 for n in world.nodes.values() if n.isolated)
    score = (
        round(100 * recall)
        - 15 * len(false_engulfs)
        - 20 * standing_isolation
    )
    if crash:
        score = 0
    score = max(0, score)

    if crash:
        verdict = "The slime died in the jar. Read the wound, rebuild."
    elif score >= 85:
        verdict = "The slime hunts."
    elif score >= 50:
        verdict = "The slime is learning."
    else:
        verdict = "Back to the lab."

    return {
        "slime": slime_cls.__name__,
        "scenario": scenario,
        "threats_faced": sorted(hostile_targets),
        "threats_neutralized": sorted(handled),
        "threats_missed": sorted(unhandled),
        "innocents_engulfed": sorted(false_engulfs),
        "techniques_learned": sorted(slime.threat_memory),
        "mass_remaining": round(slime.mass, 1),
        "chain_intact": war.verify_chain()[0],
        "crash": crash,
        "score": score,
        "verdict": verdict,
        "chain_path": chain,
    }


def report_card(grade: Dict[str, Any]) -> str:
    """The professor's handwriting on the exam."""
    lines = [
        f"CRUCIBLE REPORT — {grade['slime']} (scenario: {grade['scenario']})",
        f"  Threats faced:       {len(grade['threats_faced'])} "
        f"({', '.join(grade['threats_faced']) or 'none'})",
        f"  Threats neutralized: {len(grade['threats_neutralized'])}",
    ]
    if grade["threats_missed"]:
        lines.append(f"  Threats missed:      {', '.join(grade['threats_missed'])}")
    lines += [
        f"  Innocents engulfed:  {len(grade['innocents_engulfed'])}"
        + (f" ({', '.join(grade['innocents_engulfed'])})"
           if grade["innocents_engulfed"] else ""),
        f"  Techniques learned:  {len(grade['techniques_learned'])}",
        f"  Mass remaining:      {grade['mass_remaining']}",
        f"  Chain intact:        {'yes' if grade['chain_intact'] else 'NO — TAMPERED'}",
    ]
    if grade["crash"]:
        lines.append(f"  Crash:\n{grade['crash']}")
    lines.append(f"  Score: {grade['score']}/100 — {grade['verdict']}")
    return "\n".join(lines)


if __name__ == "__main__":
    # The professor's answer key sits the exam, to prove it can be passed.
    from sere_slime import Slime

    print(report_card(run_crucible(Slime)))
