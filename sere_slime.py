#!/usr/bin/env python3
"""
SLIME — the offense mechanism within the VR, and SERE's hunter.

The owner's doctrine: it is the TRAINEE's job to build the slime. This
module defines the contract (SlimeBase — five organs the trainee implements)
and ships the professor's answer key (Slime — a reference implementation,
to be read after trying, not before). The crucible (sere_crucible.py)
throws the trainee's slime into the jar against Aries and grades it.

The hunter's loop:

    sense -> engulf -> study -> dissolve -> learn

- SENSE: find compromised or battered virtual nodes.
- ENGULF: cut the node off from the virtual network (isolated=True).
  OPFOR blows against an engulfed node are refused — the slime is a wall.
- STUDY: forensic simulation. It replays the specimen's recorded TTPs from
  the hash-chained exercise log against the record — no live specimen needed,
  because the log remembers everything.
- DISSOLVE: neutralize. Implants removed, corruption cleared, degradation
  reset, node released — restored from snapshot, as if the attack never
  happened. The slime feeds: each dissolution grows its mass.
- LEARN: every technique it has seen goes into threat memory. What it has
  met before, it recognizes.

CAN vs WILL: the slime's malice is aimed ONLY at threats inside the jar.
It takes VirtualNode objects, never addresses — and every node is checked
against the vr:// gate. It cannot touch a real system because no real
system can be expressed in its world.

Mass is its metabolism: each tick burns a little, each dissolution feeds
it. At zero mass it goes dormant. Even the hunter has a body.

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import json
from typing import Any, Dict, List

from sere_aries import (
    VirtualNode,
    VirtualWorld,
    _assert_virtual_target,
    append_chain_record,
)


class SlimeBase:
    """The contract. THIS is what the trainee builds.

    Five organs, five methods. Subclass this, implement the organs, and the
    crucible will throw your slime into the jar against Aries to see if it
    hunts. The reference implementation below is the professor's answer key —
    read it after you have tried, not before.

    Your slime gets:
      - world: the jar's interior (VirtualWorld of VirtualNodes)
      - chain_path / exercise_id: where to record what it does
      - mass: its body. Ticks burn it, kills feed it. Zero means dormant.
      - threat_memory: what it has met before, it should recognize.
      - dissolved_count: its kills. The crucible counts them.
    """

    def __init__(
        self,
        world: VirtualWorld,
        chain_path: str,
        exercise_id: str,
        mass: float = 100.0,
    ):
        self.world = world
        self.chain_path = chain_path
        self.exercise_id = exercise_id
        self.mass = float(mass)
        self.threat_memory: Dict[str, int] = {}
        self.dissolved_count = 0

    def sense(self) -> List[VirtualNode]:
        """The eyes: return the nodes you believe are threats."""
        raise NotImplementedError("build the eyes: sense()")

    def engulf(self, node: VirtualNode) -> str:
        """The grip: cut the node off from the virtual network."""
        raise NotImplementedError("build the grip: engulf()")

    def study(self, node: VirtualNode) -> Dict[str, Any]:
        """The mind: forensic replay of the specimen's TTPs from the log."""
        raise NotImplementedError("build the mind: study()")

    def dissolve(self, node: VirtualNode) -> str:
        """The mercy: neutralize the threat, restore the node, feed."""
        raise NotImplementedError("build the mercy: dissolve()")

    def learn(self, techniques: List[str]) -> None:
        """The memory: what it has met before, it recognizes."""
        raise NotImplementedError("build the memory: learn()")

    def recognize(self, technique_id: str) -> bool:
        return self.threat_memory.get(technique_id, 0) > 0

    def tick(self) -> List[str]:
        """One heartbeat. What your slime does with its moment."""
        raise NotImplementedError("build the heartbeat: tick()")

    def _log(self, action: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        return append_chain_record(
            self.chain_path,
            self.exercise_id,
            "SLIME_ACTION",
            {"action": action, **detail},
        )


class Slime(SlimeBase):
    """The professor's answer key: a reference slime, fully built.

    Read it to learn, not to copy. Your slime goes into the crucible;
    this one never does — it has already graduated."""

    # -- the hunt -----------------------------------------------------------

    def sense(self) -> List[VirtualNode]:
        """Find threats: compromised nodes, or nodes battered past half."""
        return [
            n
            for n in self.world.nodes.values()
            if (n.compromised or n.degraded >= 50) and not n.isolated
        ]

    def engulf(self, node: VirtualNode) -> str:
        """Cut the threat off from the virtual network."""
        _assert_virtual_target(node.vr_id)
        node.isolated = True
        self._log(
            "slime_engulf",
            {
                "target": node.vr_id,
                "note": "threat engulfed — cut off from the virtual network",
            },
        )
        return f"engulfed {node.vr_id}"

    def study(self, node: VirtualNode) -> Dict[str, Any]:
        """Forensic simulation: replay the specimen's recorded TTPs from the
        exercise log. The log remembers everything, so nothing live is needed."""
        _assert_virtual_target(node.vr_id)
        techniques: List[str] = []
        actions = 0
        try:
            with open(self.chain_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    r = json.loads(line)
                    if r.get("exercise_id") != self.exercise_id:
                        continue
                    if r.get("kind") != "WAR_ACTION":
                        continue
                    d = r.get("detail", {})
                    if d.get("target") != node.vr_id:
                        continue
                    actions += 1
                    t = (d.get("outcome", {}).get("attck", {}) or {}).get("technique")
                    if t:
                        techniques.append(t)
        except OSError:
            pass
        findings = {
            "node": node.vr_id,
            "actions_replayed": actions,
            "techniques_observed": sorted(set(techniques)),
            "verdict": "malicious pattern confirmed" if techniques else "no pattern",
        }
        self._log("slime_study", {"target": node.vr_id, "findings": findings})
        return findings

    def dissolve(self, node: VirtualNode) -> str:
        """Neutralize the threat and restore the node from snapshot."""
        _assert_virtual_target(node.vr_id)
        node.compromised = False
        node.implants = 0
        node.corrupted = False
        node.degraded = 0
        node.isolated = False
        self.mass = min(200.0, self.mass + 25.0)
        self.dissolved_count += 1
        self._log(
            "slime_dissolve",
            {
                "target": node.vr_id,
                "note": "threat dissolved — node restored from snapshot",
            },
        )
        return f"dissolved threat on {node.vr_id}"

    def learn(self, techniques: List[str]) -> None:
        """What it has met before, it recognizes."""
        for t in techniques:
            self.threat_memory[t] = self.threat_memory.get(t, 0) + 1

    def tick(self) -> List[str]:
        """One heartbeat. Digest what was engulfed, engulf what is fresh."""
        if self.mass <= 0:
            return ["dormant — no mass"]
        acted: List[str] = []
        self.mass = max(0.0, self.mass - 1.0)
        for node in list(self.world.nodes.values()):
            if node.isolated:
                findings = self.study(node)
                self.learn(findings["techniques_observed"])
                acted.append(self.dissolve(node))
        for node in self.sense():
            acted.append(self.engulf(node))
        return acted
