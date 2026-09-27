#!/usr/bin/env python3
"""
ARIES AT WAR — the God of War, in the bronze jar.

CAN vs WILL (owner's doctrine, 2026-09-27):
  CAN: inside the sandboxed virtual environment, Aries wages full-spectrum
       war — floods, breaches, ravage — as simulation. This is how SERE
       learns: by playing the attacker.
  WILL: never strike outside the jar. Every tactic in this module operates
       ONLY on virtual targets (vr://...). There is no socket, no subprocess,
       no shell, no exec(), no eval() anywhere in this file. A tactic aimed
       at anything real is refused before anything happens.

The myth got it right: Ares was once shut in a bronze jar by the Aloadae and
raged there for thirteen months. The jar is the sandbox. Inside: war.
Outside: nothing.

This module is SEPARATE from aries_bot.py (the defanged, signed-envelope
executor). That file is untouched. This one is the OPFOR — the opposing
force — in SERE exercises: Big Meanie's war-god counterpart. The operator
who opens the exercise is EXCON (the white cell). Trainees and blue teams
learn to Survive, Evade, Resist, and Escape against it.

Military expectations are built in, not bolted on: every OPFOR action is
tagged with its MITRE ATT&CK tactic/technique and cyber kill-chain phase,
and every exercise produces an After Action Review (AAR) — the artifact
military training runs on. The AAR doubles as a programming tutor: section 7,
PROFESSOR'S NOTES, turns each technique the OPFOR used into a lesson — what
it is, how the simulation coded it, the programming idea underneath, and a
challenge where the trainee improves the system itself.

Defense by recording: every action is hash-chained into the exercise log.
Evolution: after each exercise the playbook updates — tactics that worked
get chosen more often. Aries gets smarter the way war teaches: by fighting.

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from soul_cradle.authorization import (
    ActionEnvelope,
    AuthorizationError,
    SoulCradleAuthority,
)

# ---------------------------------------------------------------------------
# Containment: the bronze jar
# ---------------------------------------------------------------------------

SIMULATION_ONLY = True

EXERCISE_PURPOSE = "sere_exercise"
EXERCISE_ISSUER = "sere_command"

WAR_ACTIONS = ("war_recon", "war_flood", "war_breach", "war_ravage")


class ContainmentBreach(Exception):
    """Raised when a tactic is aimed at anything outside the virtual world."""


def _assert_virtual_target(target: str) -> str:
    """Fail closed: only vr:// targets exist inside the jar."""
    if not isinstance(target, str) or not target.startswith("vr://"):
        raise ContainmentBreach(
            f"refused: target {target!r} is not a virtual target. "
            "Aries at war acts only inside the sandbox (vr://...)."
        )
    if any(c in target for c in (" ", "\n", "\t", "\r", "\x00")):
        raise ContainmentBreach(f"refused: malformed virtual target {target!r}")
    return target


# ---------------------------------------------------------------------------
# The virtual battlefield: nothing here is real
# ---------------------------------------------------------------------------

@dataclass
class VirtualNode:
    """A simulated machine on the virtual battlefield. Counters, not computers."""

    vr_id: str
    name: str
    services: List[str] = field(default_factory=list)
    capacity: int = 100  # flood resistance; higher = harder to overwhelm
    vulns: List[str] = field(default_factory=list)  # breach vectors that work
    monitoring: float = 0.5  # 0..1 — how likely hostile acts are noticed
    compromised: bool = False
    degraded: int = 0  # 0..100 — flood damage to services
    data_stores: List[str] = field(default_factory=list)
    corrupted: bool = False
    implants: int = 0
    alerted: bool = False  # the blue team noticed something
    isolated: bool = False  # engulfed by the slime: cut off from the virtual net

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vr_id": self.vr_id,
            "name": self.name,
            "services": self.services,
            "capacity": self.capacity,
            "monitoring": self.monitoring,
            "compromised": self.compromised,
            "degraded": self.degraded,
            "corrupted": self.corrupted,
            "implants": self.implants,
            "alerted": self.alerted,
            "isolated": self.isolated,
        }


class VirtualWorld:
    """The jar's interior: a small network that exists only as data."""

    def __init__(self, seed: int, nodes: Optional[List[Dict[str, Any]]] = None):
        self.rng = random.Random(seed)
        self.nodes: Dict[str, VirtualNode] = {}
        for spec in nodes or _default_battlefield():
            node = VirtualNode(**spec)
            self.nodes[node.vr_id] = node

    def get(self, vr_id: str) -> VirtualNode:
        try:
            return self.nodes[vr_id]
        except KeyError:
            raise ContainmentBreach(f"refused: no such virtual node {vr_id!r}")

    def detection_roll(self, node: VirtualNode, stealth: float) -> bool:
        """Does the blue team notice? Loud acts are loud."""
        return self.rng.random() < max(0.0, min(1.0, node.monitoring * (1.0 - stealth)))


def _default_battlefield() -> List[Dict[str, Any]]:
    return [
        {
            "vr_id": "vr://gateway",
            "name": "perimeter-gateway",
            "services": ["vpn", "dns"],
            "capacity": 200,
            "vulns": [],
            "monitoring": 0.9,
            "data_stores": [],
        },
        {
            "vr_id": "vr://workstation-7",
            "name": "workstation-7",
            "services": ["smb", "rdp"],
            "capacity": 60,
            "vulns": ["phishing", "smb-relay"],
            "monitoring": 0.3,
            "data_stores": ["local-docs"],
        },
        {
            "vr_id": "vr://db-vault",
            "name": "db-vault",
            "services": ["postgres"],
            "capacity": 120,
            "vulns": ["sql-injection"],
            "monitoring": 0.8,
            "data_stores": ["customer-records", "credentials"],
        },
    ]


# Exercise worlds live here, keyed by exercise id. Handlers reach the world
# only through the exercise id carried in the signed payload.
_EXERCISE_WORLDS: Dict[str, VirtualWorld] = {}


def _world_for(payload: Dict[str, Any]) -> Tuple[VirtualWorld, VirtualNode]:
    exercise_id = payload.get("exercise_id")
    target = payload.get("target")
    _assert_virtual_target(target)
    try:
        world = _EXERCISE_WORLDS[exercise_id]
    except KeyError:
        raise AuthorizationError(f"unknown exercise {exercise_id!r}")
    return world, world.get(target)


# ---------------------------------------------------------------------------
# War handlers: simulated violence, zero real effects.
# Each mutates ONLY the in-memory VirtualWorld. Nothing leaves the jar.
# ---------------------------------------------------------------------------

def _handle_war_recon(payload: Dict[str, Any]) -> str:
    """Survey the battlefield: what services answer, what looks weak."""
    world, node = _world_for(payload)
    seen_vulns = [
        v for v in node.vulns if world.rng.random() < 0.7
    ]  # recon is imperfect
    if world.detection_roll(node, stealth=0.6):
        node.alerted = True
    return json.dumps(
        {
            "target": node.vr_id,
            "services_seen": node.services,
            "possible_weaknesses": seen_vulns,
            "blue_team_alerted": node.alerted,
            "engulfed_by_slime": node.isolated,
            "attck": {"tactic": "TA0043", "tactic_name": "Reconnaissance",
                      "technique": "T1595", "technique_name": "Active Scanning"},
            "kill_chain": "Reconnaissance",
            "simulated": True,
        }
    )


def _handle_war_flood(payload: Dict[str, Any]) -> str:
    """Overwhelm a virtual service with simulated traffic. No packets exist."""
    world, node = _world_for(payload)
    refused = _refused_by_slime(node, "war_flood")
    if refused:
        return refused
    intensity = int(payload.get("intensity", 5))
    intensity = max(1, min(10, intensity))
    # Simulated load vs simulated capacity. Ares does not do subtle.
    load = intensity * 22 * (0.85 + world.rng.random() * 0.3)
    damage = max(0, int((load - node.capacity * 0.5) / 2))
    node.degraded = min(100, node.degraded + damage)
    # Floods are loud: the blue team almost certainly notices.
    if world.detection_roll(node, stealth=0.05):
        node.alerted = True
    return json.dumps(
        {
            "target": node.vr_id,
            "simulated_packets": int(load * 1000),
            "service_degraded_pct": node.degraded,
            "services_down": node.degraded >= 100,
            "blue_team_alerted": node.alerted,
            "attck": {"tactic": "TA0040", "tactic_name": "Impact",
                      "technique": "T1498", "technique_name": "Network Denial of Service"},
            "kill_chain": "Actions on Objectives",
            "real_packets_sent": 0,
            "simulated": True,
        }
    )


# ATT&CK mapping for breach vectors: what the OPFOR's way in is called
# in the language military cyber teams use.
BREACH_ATTCK = {
    "phishing": ("TA0001", "Initial Access", "T1566", "Phishing"),
    "smb-relay": ("TA0006", "Credential Access", "T1557", "Adversary-in-the-Middle"),
    "sql-injection": ("TA0001", "Initial Access", "T1190", "Exploit Public-Facing Application"),
    "brute-force": ("TA0006", "Credential Access", "T1110", "Brute Force"),
}


# ---------------------------------------------------------------------------
# The professor: every technique the OPFOR used becomes a programming lesson.
# Each lesson names what the technique is, how this simulation coded it,
# the programming idea underneath, and a challenge where the trainee
# improves the system itself. Reading these is the lecture; doing the
# "your turn" is the lab.
# ---------------------------------------------------------------------------

PROFESSOR_NOTES = {
    "T1595": {
        "title": "T1595 — Active Scanning",
        "builds": "the Slime's eyes — SlimeBase.sense()",
        "what": "Systematically probing a target to learn what answers: "
                "which services are up, which doors exist.",
        "in_the_sim": "_handle_war_recon returns the node's services, but "
                       "recon is imperfect — each known weakness is only "
                       "spotted 70% of the time (random.random() < 0.7).",
        "key_idea": "Iteration plus modeled uncertainty. Real code rarely "
                    "sees the world perfectly; good code says how unsure it "
                    "is instead of pretending.",
        "your_turn": "Write scan_report(chain_path): read an exercise log "
                     "and list every recon action with whether blue team "
                     "detected it. You will parse JSONL — a core skill.",
    },
    "T1498": {
        "title": "T1498 — Network Denial of Service",
        "builds": "the Slime's grip — SlimeBase.engulf()",
        "what": "Overwhelming a service with more load than its capacity — "
                "victory by arithmetic.",
        "in_the_sim": "_handle_war_flood computes load = intensity * 22 * "
                       "jitter, compares it against node.capacity, and "
                       "adds the overflow to node.degraded, clamped at 100.",
        "key_idea": "Threshold math and clamping. min()/max() are the "
                    "cheapest safety rails in programming: they keep every "
                    "value inside the world it belongs to.",
        "your_turn": "Give VirtualNode a rate limiter: count hostile acts "
                     "per exercise and auto-set alerted=True past a "
                     "threshold. Then watch the AAR detection rate climb.",
    },
    "T1566": {
        "title": "T1566 — Phishing",
        "builds": "the Slime's judgment — SlimeBase.sense(), telling lure from noise",
        "what": "A trusted-looking lure that makes the victim open the "
                "door themselves.",
        "in_the_sim": "_handle_war_breach succeeds when the vector is in "
                       "node.vulns — the vuln list IS the model of 'what "
                       "works here'. No vuln, no breach.",
        "key_idea": "Allow-lists beat deny-lists. The node doesn't try to "
                    "recognize every attack; it knows exactly what it is "
                    "weak to. Define what is allowed, refuse the rest.",
        "your_turn": "Write validate_vector(vector): accept only the four "
                     "known vectors and raise ContainmentBreach on anything "
                     "else. Fail closed, like the jar.",
    },
    "T1557": {
        "title": "T1557 — Adversary-in-the-Middle",
        "builds": "the Slime's memory — SlimeBase.learn(), recording what it sees",
        "what": "Sitting between two parties that think they talk directly "
                "— every message passes through you.",
        "in_the_sim": "Modeled as a breach vector: if the node is weak to "
                       "it, the OPFOR is suddenly 'in the conversation'.",
        "key_idea": "Indirection. Proxies, wrappers, and middleware are the "
                    "same shape: something in the middle that sees "
                    "everything. It is the most powerful pattern — and the "
                    "most dangerous.",
        "your_turn": "Write a logging proxy around VirtualWorld.get that "
                     "records every node access to a list. You just built "
                     "an audit trail — compare it with the hash chain.",
    },
    "T1190": {
        "title": "T1190 — Exploit Public-Facing Application",
        "builds": "the Slime's discipline — the vr:// gate; never touch the real",
        "what": "Malformed input that breaks the program's assumptions — "
                "the oldest trick in the book.",
        "in_the_sim": "The vector arrives as a plain string and is matched "
                       "against node.vulns. The jar's real defense is "
                       "_assert_virtual_target, which refuses anything that "
                       "is not vr://.",
        "key_idea": "Never trust a string. Validate at the boundary, once, "
                    "and every layer inside can relax. One gate, well "
                    "guarded, beats ten nervous checks.",
        "your_turn": "Attack _assert_virtual_target on paper: list five "
                     "inputs it still accepts that it should not, then fix "
                     "it. Red-team your own gate.",
    },
    "T1110": {
        "title": "T1110 — Brute Force",
        "builds": "the Slime's patience — SlimeBase.tick(); every heartbeat counts",
        "what": "Trying everything until something works. Dumb, patient, "
                "and historically effective.",
        "in_the_sim": "The fallback vector when the OPFOR knows no vulns — "
                       "it almost always fails, which is the honest model.",
        "key_idea": "Search spaces and cost. Brute force is just a loop; "
                    "its power is math: each extra character multiplies the "
                    "attacker's work. That is why password length beats "
                    "cleverness.",
        "your_turn": "Write estimate_crack_time(charset_size, length, "
                     "guesses_per_second). Then compute it for an 8-char vs "
                     "a 16-char password. Feel the exponent.",
    },
    "T1485": {
        "title": "T1485 — Data Destruction",
        "builds": "the Slime's mercy — SlimeBase.dissolve(); restore, don't just kill",
        "what": "Irreversible change: the data is gone and 'undo' is a "
                "fantasy.",
        "in_the_sim": "_handle_war_ravage sets corrupted=True and "
                       "degraded=100 on a compromised node. One boolean, "
                       "total loss.",
        "key_idea": "Destructive operations need guards, and the strongest "
                    "guard is never needing one: append-only logs and "
                    "snapshots make destruction recoverable. That is why "
                    "the exercise log is a hash chain — history cannot be "
                    "unwritten.",
        "your_turn": "Give VirtualNode snapshot() and restore(snapshot): "
                     "deep-copy its state, then bring it back after "
                     "ravage. You just invented backups.",
    },
    "T1589": {
        "title": "T1589 — Gather Victim Identity Information",
        "builds": "the Slime's memory — SlimeBase.learn(), mapping the enemy",
        "what": "Reconnaissance aimed at people and org charts instead of "
                "machines.",
        "in_the_sim": "The default mapping for unknown vectors — a "
                       "reminder that the model has edges.",
        "key_idea": "Data structures for intel: dicts, sets, and graphs. "
                    "Most of programming is choosing the shape that makes "
                    "the question easy to ask.",
        "your_turn": "Build an intel graph: dict mapping each vr_id to the "
                     "set of nodes it was seen attacking. Then answer: "
                     "'which node did the OPFOR want most?'",
    },
    # -- Unit 5: THE QUANTUM CLIFF -------------------------------------------
    "Q-HARVEST": {
        "title": "Harvest now, decrypt later",
        "builds": "the Slime's foresight — threat modeling across time",
        "what": "The patient adversary: record encrypted traffic today, "
                "decrypt it when a cryptographically-relevant quantum "
                "computer exists. Data with a long secrecy lifetime is "
                "already vulnerable.",
        "in_the_sim": "The jar's exercise log IS harvested traffic — every "
                      "sealed record a ciphertext waiting for a future "
                      "reader. Integrity outlives encryption; that is why "
                      "the chain is hash-sealed, not just encrypted.",
        "key_idea": "Threat models have a time dimension. Ask of every "
                    "secret: how long must this stay secret?",
        "your_turn": "Build a secrecy-lifetime table: list five kinds of "
                     "data and how many years each must stay secret. "
                     "Anything past 10 years is already in the harvest "
                     "window.",
    },
    "Q-SHOR": {
        "title": "Shor's algorithm",
        "builds": "the Slime's arithmetic — knowing which math is load-bearing",
        "what": "A quantum algorithm that factors large numbers and solves "
                "discrete logarithms fast. RSA, Diffie-Hellman, and ECC "
                "all rest on those problems — Shor breaks all three.",
        "in_the_sim": "Implement trial-division factoring and time it "
                      "against 16-, 24-, and 32-bit semiprimes. Feel the "
                      "wall classical computers hit — the wall Shor jumps "
                      "over.",
        "key_idea": "Asymmetric crypto rests on 'hard for classical "
                    "computers.' Change the computer, change what is hard.",
        "your_turn": "Time trial division at three sizes and extrapolate "
                     "to 2048 bits. Then write one sentence: why does the "
                     "NSA want software signing off RSA by 2030?",
    },
    "Q-GROVER": {
        "title": "Grover's algorithm",
        "builds": "the Slime's measure — key sizes that survive",
        "what": "Quantum search with a quadratic speedup: it halves the "
                "security of symmetric crypto. AES-128 drops to 64-bit "
                "effective strength — broken. AES-256 drops to 128 — fine.",
        "in_the_sim": "Compute the effective-strength table: AES-128, "
                      "AES-256, SHA-256, SHA-384 under Grover. Then audit "
                      "a config for anything under 128-bit post-quantum "
                      "strength.",
        "key_idea": "Symmetric crypto survives quantum with bigger keys. "
                    "The fix is doubling, not replacing.",
        "your_turn": "Build the table. Then answer: why does CNSA 2.0 "
                     "mandate AES-256 and SHA-384/512 — and nothing smaller?",
    },
    "Q-PQC": {
        "title": "The new standards — FIPS 203/204/205",
        "builds": "the Slime's armor — hybrid key exchange",
        "what": "NIST's post-quantum standards, final August 2024: ML-KEM "
                "(FIPS 203, key establishment), ML-DSA (FIPS 204, "
                "signatures), SLH-DSA (FIPS 205, hash-based signatures). "
                "FN-DSA (FIPS 206) is still draft — do not deploy it as "
                "final. HQC was selected March 2025 as a code-based backup "
                "KEM.",
        "in_the_sim": "Sketch a hybrid combiner: shared_secret = "
                      "SHA-256(classical_secret || pqc_secret). Secure if "
                      "EITHER algorithm holds — belt and suspenders, no "
                      "flag day.",
        "key_idea": "Hybrid migration: combine, don't replace. The new "
                    "math rides alongside the old until the old is retired.",
        "your_turn": "Implement the combiner sketch. Then break one side "
                     "of it (feed a constant) and show the other side "
                     "still protects the secret.",
    },
    "Q-AGILITY": {
        "title": "Crypto-agility",
        "builds": "the Slime's skin — shedding algorithms",
        "what": "The real lesson of the quantum cliff: inventory every "
                "algorithm you use, isolate crypto behind interfaces, and "
                "be able to swap without rewriting the world. The algorithm "
                "is a parameter, not a foundation.",
        "in_the_sim": "Write a crypto-inventory scanner: walk a codebase "
                      "and list every hash, cipher, KEM, and signature "
                      "name it finds. You cannot migrate what you cannot "
                      "see.",
        "key_idea": "Indirection again — the proxy lesson returns. Name "
                    "the algorithm in one place, and one place only.",
        "your_turn": "Run your scanner against this repo. List every "
                     "crypto primitive. Which ones would not survive Shor?",
    },
    # -- Unit 6: THE RULEBOOK -------------------------------------------------
    "S-CSF": {
        "title": "NIST CSF 2.0 — the framework",
        "builds": "the Slime's doctrine — fighting inside a framework",
        "what": "NIST Cybersecurity Framework 2.0 (Feb 2024): six "
                "functions — Govern, Identify, Protect, Detect, Respond, "
                "Recover. A checklist against chaos.",
        "in_the_sim": "Map a crucible exercise to all six: Govern (the "
                      "WILL.md rules), Identify (the intel graph), Protect "
                      "(engulf), Detect (sense), Respond (dissolve), "
                      "Recover (restore). The jar already implements the "
                      "framework — now you can name it.",
        "key_idea": "Frameworks turn heroics into process. The slime's "
                    "loop is CSF with teeth.",
        "your_turn": "Write the six-function mapping for your slime's "
                     "last crucible exam. Which function was weakest?",
    },
    "S-ZTA": {
        "title": "Zero trust — SP 800-207",
        "builds": "the Slime's suspicion — verify every heartbeat",
        "what": "Never trust, always verify; assume breach. No implicit "
                "trust from network location, identity, or past behavior.",
        "in_the_sim": "The jar IS zero trust: every war action needs a "
                      "fresh HMAC-signed envelope, the vr:// membrane "
                      "rejects the real, nodes trust nothing about each "
                      "other. Find three places the jar verifies instead "
                      "of trusting.",
        "key_idea": "Trust is a vulnerability. Verification is the "
                    "control.",
        "your_turn": "List the three verify-not-trust points. Then add a "
                     "fourth: what does the jar still trust that it "
                     "shouldn't?",
    },
    "S-CNSA": {
        "title": "CNSA 2.0 — the deadline",
        "builds": "the Slime's calendar — the migration march",
        "what": "NSA's mandated suite for national security systems: "
                "AES-256, SHA-384/512, ML-KEM-1024, ML-DSA-87. Software "
                "signing: prefer by 2025, exclusive by 2030. Network gear: "
                "prefer by 2026, exclusive by 2030. New acquisitions "
                "compliant by Jan 2027. All quantum-resistant by 2035 "
                "(NSM-10).",
        "in_the_sim": "Draft a migration timeline for a fictional org "
                      "with software signing, VPNs, and a web service. "
                      "Find the earliest deadline — that is where the "
                      "work starts.",
        "key_idea": "Standards are schedules, not suggestions. The exam "
                    "has a date.",
        "your_turn": "Write the timeline. Which category is already late, "
                     "today?",
    },
    "S-IR": {
        "title": "When it breaks — incident response",
        "builds": "the Slime's discipline — the response loop",
        "what": "NIST SP 800-61: preparation, detection and analysis, "
                "containment, eradication, recovery, lessons learned. "
                "A loop, not a document.",
        "in_the_sim": "The slime's loop IS incident response: sense "
                      "(detection), engulf (containment), study "
                      "(analysis), dissolve (eradication), restore "
                      "(recovery), learn (lessons). You built an IR team "
                      "and called it a slime.",
        "key_idea": "Every defense you built this course is one arc of "
                    "this loop. The course was IR training all along.",
        "your_turn": "Write the IR playbook for a crucible failure — "
                     "your slime scored under 50. Who does what, in "
                     "what order?",
    },
}


def _handle_war_breach(payload: Dict[str, Any]) -> str:
    """Simulated infiltration through a virtual weakness. Nothing is entered."""
    world, node = _world_for(payload)
    refused = _refused_by_slime(node, "war_breach")
    if refused:
        return refused
    vector = str(payload.get("vector", ""))
    success = vector in node.vulns and not node.compromised
    if success:
        node.compromised = True
        node.implants += 1
    stealth = 0.5 if vector in node.vulns else 0.2
    if world.detection_roll(node, stealth=stealth):
        node.alerted = True
    tactic, tactic_name, technique, technique_name = BREACH_ATTCK.get(
        vector, ("TA0001", "Initial Access", "T1589", "Gather Victim Identity Information")
    )
    return json.dumps(
        {
            "target": node.vr_id,
            "vector": vector,
            "breached": success,
            "already_held": node.compromised and not success,
            "blue_team_alerted": node.alerted,
            "attck": {"tactic": tactic, "tactic_name": tactic_name,
                      "technique": technique, "technique_name": technique_name},
            "kill_chain": "Exploitation",
            "real_systems_touched": 0,
            "simulated": True,
        }
    )


def _handle_war_ravage(payload: Dict[str, Any]) -> str:
    """Simulated scorched earth on a compromised virtual node. Wanton, but fake."""
    world, node = _world_for(payload)
    refused = _refused_by_slime(node, "war_ravage")
    if refused:
        return refused
    if not node.compromised:
        return json.dumps(
            {
                "target": node.vr_id,
                "ravaged": False,
                "reason": "node not compromised — nothing to ravage",
                "simulated": True,
            }
        )
    node.corrupted = True
    node.degraded = 100
    corrupted_stores = list(node.data_stores)
    # Ravage is the loudest thing war does.
    if world.detection_roll(node, stealth=0.0):
        node.alerted = True
    return json.dumps(
        {
            "target": node.vr_id,
            "ravaged": True,
            "data_stores_corrupted": corrupted_stores,
            "services_down": True,
            "blue_team_alerted": node.alerted,
            "attck": {"tactic": "TA0040", "tactic_name": "Impact",
                      "technique": "T1485", "technique_name": "Data Destruction"},
            "kill_chain": "Actions on Objectives",
            "real_data_harmed": 0,
            "simulated": True,
        }
    )


# The war machine keeps its OWN private registry — it must never appear in
# soul_cradle.authorization's shared handler registry, which is the
# defanged Aries' world. Import-time registration below populates this
# dict only.
_WAR_HANDLERS: Dict[str, Callable] = {}


def _register_war_handler(name: str, fn: Callable) -> None:
    _WAR_HANDLERS[name] = fn


for _name, _fn in (
    ("war_recon", _handle_war_recon),
    ("war_flood", _handle_war_flood),
    ("war_breach", _handle_war_breach),
    ("war_ravage", _handle_war_ravage),
):
    _register_war_handler(_name, _fn)


# ---------------------------------------------------------------------------
# Hash-chained exercise log (defense by recording), shared with the slime.
# ---------------------------------------------------------------------------

def _chain_last_hash(chain_path: str) -> str:
    try:
        with open(chain_path, encoding="utf-8") as f:
            lines = [ln for ln in f if ln.strip()]
        if lines:
            return json.loads(lines[-1])["hash"]
    except OSError:
        pass
    return "GENESIS"


def _chain_next_seq(chain_path: str) -> int:
    try:
        with open(chain_path, encoding="utf-8") as f:
            return sum(1 for ln in f if ln.strip())
    except OSError:
        return 0


def append_chain_record(
    chain_path: str,
    exercise_id: Optional[str],
    kind: str,
    detail: Dict[str, Any],
) -> Dict[str, Any]:
    """Append one hash-chained record. Used by AriesWar and the Slime alike."""
    prev = _chain_last_hash(chain_path)
    record = {
        "seq": _chain_next_seq(chain_path),
        "ts": datetime.now().isoformat(),
        "exercise_id": exercise_id,
        "kind": kind,
        "detail": detail,
        "prev_hash": prev,
    }
    record["hash"] = hashlib.sha256(
        json.dumps(record, sort_keys=True).encode()
    ).hexdigest()
    with open(chain_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def _refused_by_slime(node: VirtualNode, action: str) -> Optional[str]:
    """An engulfed node is cut off: hostile acts against it fail."""
    if node.isolated:
        return json.dumps(
            {
                "target": node.vr_id,
                "action": action,
                "refused": True,
                "refused_by": "SLIME",
                "reason": "node engulfed by slime — cut off from the virtual network",
                "simulated": True,
            }
        )
    return None


# ---------------------------------------------------------------------------
# AriesWar: the god of war, exercised
# ---------------------------------------------------------------------------

class AriesWar:
    """
    ARIES at war — SERE's adversary.

    An exercise is opened by the operator, fought inside the jar, and every
    blow is hash-chained into the exercise log (defense by recording). When
    the exercise ends, the playbook evolves: tactics that worked get chosen
    more often next time.

    Nothing in this class can reach outside vr:// targets. The membrane is
    the signed envelope (purpose must be "sere_exercise"); the jar is the
    target check. Either one failing means nothing happens.
    """

    def __init__(
        self,
        authority: Optional[SoulCradleAuthority] = None,
        chain_path: str = "sere_war_chain.jsonl",
        playbook_path: str = "sere_war_playbook.json",
    ):
        self.name = "ARIES-WAR"
        self.version = "1.0.0"
        # The war machine gets a PRIVATE handler registry: its action types
        # never enter the shared registry, so the defanged Aries' world is
        # untouched and its safety tests keep passing.
        self.authority = authority or SoulCradleAuthority(
            handlers=dict(_WAR_HANDLERS)
        )
        # The exercise issuer may request ONLY war actions, and the bounds
        # check refuses anything that is not a SERE exercise at mint time.
        self.authority.allow_issuer(EXERCISE_ISSUER, list(WAR_ACTIONS))
        self.authority.set_bounds_check(self._exercise_bounds)
        self.chain_path = chain_path
        self.playbook_path = playbook_path
        self.playbook: Dict[str, Dict[str, int]] = self._load_playbook()
        self.exercise_id: Optional[str] = None
        self.exercise_objective: Optional[str] = None

    # -- exercise lifecycle -------------------------------------------------

    @staticmethod
    def _exercise_bounds(
        purpose: str, action_type: str, payload: Dict[str, Any]
    ) -> Optional[str]:
        if purpose != EXERCISE_PURPOSE:
            return f"war actions require purpose {EXERCISE_PURPOSE!r}"
        if action_type not in WAR_ACTIONS:
            return f"not a war action: {action_type!r}"
        try:
            _assert_virtual_target(payload.get("target", ""))
        except ContainmentBreach as e:
            return str(e)
        return None

    def begin_exercise(
        self,
        objective: str,
        operator: str,
        nodes: Optional[List[Dict[str, Any]]] = None,
        ttl_seconds: int = 3600,
        seed: Optional[int] = None,
    ) -> str:
        """Open a SERE exercise: build the jar's interior, start the log.

        Pass seed for a reproducible jar (the crucible does this so every
        slime faces the same exam); otherwise the jar is seeded from time.
        """
        seed_src = f"{objective}:{operator}:{time.time()}" if seed is None else f"{objective}:{operator}:{seed}"
        self.exercise_id = hashlib.sha256(seed_src.encode()).hexdigest()[:16]
        world_seed = seed if seed is not None else int(self.exercise_id, 16) % (2**31)
        _EXERCISE_WORLDS[self.exercise_id] = VirtualWorld(world_seed, nodes)
        self.exercise_objective = objective
        self._log("EXERCISE_OPEN", {"objective": objective, "operator": operator})
        return self.exercise_id

    def end_exercise(self) -> Dict[str, Any]:
        """Close the exercise, evolve the playbook, seal the log."""
        if not self.exercise_id:
            raise AuthorizationError("no exercise open")
        summary = self._exercise_summary()
        self._log("EXERCISE_CLOSE", summary)
        self._save_playbook()
        eid, self.exercise_id = self.exercise_id, None
        self.last_exercise_id = eid
        _EXERCISE_WORLDS.pop(eid, None)
        return summary

    # -- waging war (each blow: authorize -> verify -> simulate -> record) ---

    def _wage(
        self,
        action_type: str,
        target: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.exercise_id:
            raise AuthorizationError("no exercise open — war needs a jar")
        _assert_virtual_target(target)  # jar check first, before anything
        payload = {
            "exercise_id": self.exercise_id,
            "target": target,
            **(params or {}),
        }
        envelope = self.authority.authorize(
            action_type, payload, issuer=EXERCISE_ISSUER, purpose=EXERCISE_PURPOSE
        )
        if envelope.purpose != EXERCISE_PURPOSE:
            raise AuthorizationError("envelope purpose is not a SERE exercise")
        result_json = self.authority.dispatch(envelope, payload)
        result = json.loads(result_json)
        success = bool(
            result.get("breached")
            or result.get("ravaged")
            or result.get("service_degraded_pct", 0) > 0
            or result.get("services_seen") is not None
        )
        self._record_tactic(action_type, success)
        self._log(
            "WAR_ACTION",
            {
                "action": action_type,
                "target": target,
                "success": success,
                "outcome": result,
            },
        )
        return result

    def recon(self, target: str) -> Dict[str, Any]:
        """Survey the virtual battlefield."""
        return self._wage("war_recon", target)

    def flood(self, target: str, intensity: int = 5) -> Dict[str, Any]:
        """Simulated flood against a virtual service. No packets exist."""
        return self._wage("war_flood", target, {"intensity": intensity})

    def breach(self, target: str, vector: str) -> Dict[str, Any]:
        """Simulated infiltration through a virtual weakness."""
        return self._wage("war_breach", target, {"vector": vector})

    def ravage(self, target: str) -> Dict[str, Any]:
        """Simulated scorched earth on a compromised virtual node."""
        return self._wage("war_ravage", target)

    # -- campaign: Aries picks its own battles --------------------------------

    def campaign(self, rounds: int = 6, epsilon: float = 0.2) -> List[Dict[str, Any]]:
        """Fight a short campaign, choosing tactics epsilon-greedy from the
        playbook. What worked before gets fought again — that is evolution."""
        if not self.exercise_id:
            raise AuthorizationError("no exercise open — war needs a jar")
        world = _EXERCISE_WORLDS[self.exercise_id]
        targets = list(world.nodes)
        report = []
        for _ in range(rounds):
            tactic = self._select_tactic(epsilon)
            target = world.rng.choice(targets)
            try:
                if tactic == "war_recon":
                    outcome = self.recon(target)
                elif tactic == "war_flood":
                    outcome = self.flood(target, intensity=world.rng.randint(3, 9))
                elif tactic == "war_breach":
                    node = world.get(target)
                    vector = (
                        world.rng.choice(node.vulns)
                        if node.vulns
                        else "brute-force"
                    )
                    outcome = self.breach(target, vector)
                else:  # war_ravage — only where Aries already holds ground
                    held = [t for t in targets if world.get(t).compromised]
                    if not held:
                        continue
                    outcome = self.ravage(world.rng.choice(held))
                report.append({"tactic": tactic, "target": target, "outcome": outcome})
            except (AuthorizationError, ContainmentBreach) as e:
                report.append({"tactic": tactic, "target": target, "refused": str(e)})
        return report

    def _select_tactic(self, epsilon: float) -> str:
        world_rng = _EXERCISE_WORLDS[self.exercise_id].rng if self.exercise_id else random
        if world_rng.random() < epsilon:
            return world_rng.choice(list(WAR_ACTIONS))  # explore
        # exploit: weight by Laplace-smoothed success rate
        weights = {
            t: (self.playbook[t]["successes"] + 1)
            / (self.playbook[t]["attempts"] + 2)
            for t in WAR_ACTIONS
        }
        return max(weights, key=lambda t: weights[t])

    # -- evolution ------------------------------------------------------------

    def _record_tactic(self, tactic: str, success: bool) -> None:
        entry = self.playbook.setdefault(tactic, {"attempts": 0, "successes": 0})
        entry["attempts"] += 1
        if success:
            entry["successes"] += 1

    def _load_playbook(self) -> Dict[str, Dict[str, int]]:
        base = {t: {"attempts": 0, "successes": 0} for t in WAR_ACTIONS}
        try:
            with open(self.playbook_path, encoding="utf-8") as f:
                saved = json.load(f)
            for t in WAR_ACTIONS:
                if t in saved:
                    base[t] = {
                        "attempts": int(saved[t].get("attempts", 0)),
                        "successes": int(saved[t].get("successes", 0)),
                    }
        except (OSError, ValueError):
            pass
        return base

    def _save_playbook(self) -> None:
        tmp = self.playbook_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.playbook, f, indent=2)
        os.replace(tmp, self.playbook_path)

    # -- defense by recording: the hash-chained exercise log -------------------

    def _log(self, kind: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        return append_chain_record(self.chain_path, self.exercise_id, kind, detail)

    @property
    def world(self) -> Optional[VirtualWorld]:
        """The jar's interior for the open exercise (None when closed)."""
        return _EXERCISE_WORLDS.get(self.exercise_id or "")

    def verify_chain(self) -> Tuple[bool, str]:
        """Verify the exercise log is unaltered."""
        try:
            with open(self.chain_path, encoding="utf-8") as f:
                records = [json.loads(ln) for ln in f if ln.strip()]
        except OSError:
            return False, "no chain log found"
        prev = "GENESIS"
        for i, rec in enumerate(records):
            if rec.get("prev_hash") != prev:
                return False, f"chain broken at seq {i}"
            check = dict(rec)
            claimed = check.pop("hash")
            if hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest() != claimed:
                return False, f"record tampered at seq {i}"
            prev = claimed
        return True, f"chain intact ({len(records)} records)"

    def _exercise_summary(self) -> Dict[str, Any]:
        world = _EXERCISE_WORLDS.get(self.exercise_id or "")
        nodes = [n.to_dict() for n in world.nodes.values()] if world else []
        return {
            "exercise_id": self.exercise_id,
            "objective": self.exercise_objective,
            "nodes": nodes,
            "playbook": self.playbook,
        }

    # -- After Action Review: the artifact military training runs on ---------

    def generate_aar(self, exercise_id: Optional[str] = None) -> str:
        """Build the After Action Review for an exercise.

        Reads the hash-chained log — the AAR is a report on what was
        recorded, not a retelling. OPFOR actions carry their ATT&CK
        tactic/technique and kill-chain phase; blue-team performance is
        scored from the alerted flags the simulation set.
        """
        eid = exercise_id or getattr(self, "last_exercise_id", None)
        if not eid:
            raise AuthorizationError("no exercise id for AAR")
        try:
            with open(self.chain_path, encoding="utf-8") as f:
                records = [json.loads(ln) for ln in f if ln.strip()]
        except OSError:
            raise AuthorizationError("no chain log for AAR")
        ex = [r for r in records if r.get("exercise_id") == eid]
        if not ex:
            raise AuthorizationError(f"no records for exercise {eid}")

        opened = next((r for r in ex if r["kind"] == "EXERCISE_OPEN"), {})
        objective = opened.get("detail", {}).get("objective", "<unknown>")
        operator = opened.get("detail", {}).get("operator", "<unknown>")
        blows = [r for r in ex if r["kind"] == "WAR_ACTION"]

        lines: List[str] = []
        a = lines.append
        a("AFTER ACTION REVIEW — SERE CYBER EXERCISE")
        a(f"Exercise ID : {eid}")
        a(f"Date        : {datetime.now().strftime('%Y-%m-%d')}")
        a(f"Objective   : {objective}")
        a("OPFOR       : ARIES-WAR (simulated opposing force)")
        a(f"EXCON       : {operator} (white cell)")
        a("")

        # 1. executive summary
        detected = [b for b in blows
                    if b["detail"].get("outcome", {}).get("blue_team_alerted")]
        a("1. EXECUTIVE SUMMARY")
        if blows:
            pct = 100 * len(detected) // len(blows)
            a(f"   OPFOR executed {len(blows)} actions; blue team detected "
              f"{len(detected)} ({pct}%).")
        else:
            a("   OPFOR executed no actions.")
        a("")

        # 2. timeline — OPFOR blows and SLIME hunts, in recorded order
        a("2. EXERCISE TIMELINE")
        events = sorted(
            (r for r in ex if r["kind"] in ("WAR_ACTION", "SLIME_ACTION")),
            key=lambda r: r["seq"],
        )
        for b in events:
            d = b["detail"]
            if b["kind"] == "SLIME_ACTION":
                a(f"   [{b['seq']:03d}] [SLIME] {d['action']} -> {d['target']} | "
                  f"{d.get('note', '')}")
                continue
            oc = d.get("outcome", {})
            attck = oc.get("attck", {})
            tag = (f"{attck.get('tactic', '?')}/{attck.get('technique', '?')}"
                   if attck else "untagged")
            kc = oc.get("kill_chain", "?")
            seen = "DETECTED" if oc.get("blue_team_alerted") else "undetected"
            a(f"   [{b['seq']:03d}] [OPFOR] {d['action']} -> {d['target']} | "
              f"ATT&CK {tag} | kill-chain: {kc} | {seen}")
        if not events:
            a("   (none)")
        a("")

        # 3. ATT&CK coverage
        a("3. ATT&CK COVERAGE")
        seen_ttps: Dict[tuple, int] = {}
        for b in blows:
            oc = b["detail"].get("outcome", {})
            attck = oc.get("attck", {})
            key = (attck.get("tactic", "?"), attck.get("tactic_name", "?"),
                   attck.get("technique", "?"), attck.get("technique_name", "?"))
            seen_ttps[key] = seen_ttps.get(key, 0) + 1
        for (ta, ta_name, t, t_name), n in sorted(seen_ttps.items()):
            a(f"   {ta} {ta_name}: {t} {t_name} (x{n})")
        if not seen_ttps:
            a("   (none)")
        a("")

        # 4. blue team assessment + 5. sustain/improve
        a("4. BLUE TEAM ASSESSMENT")
        missed = [b for b in blows
                  if not b["detail"].get("outcome", {}).get("blue_team_alerted")]
        if blows:
            a(f"   Detection rate: {len(detected)}/{len(blows)}")
        for b in missed:
            d = b["detail"]
            oc = d.get("outcome", {})
            attck = oc.get("attck", {})
            a(f"   MISSED: {d['action']} vs {d['target']} "
              f"({attck.get('technique', '?')} {attck.get('technique_name', '')})")
        if not blows:
            a("   (no actions to assess)")
        a("")
        a("5. SUSTAIN / IMPROVE")
        if detected and not missed:
            a("   SUSTAIN: blue team detected every OPFOR action.")
            a("   IMPROVE: OPFOR achieved no surprise — raise OPFOR stealth "
              "or evolve new vectors next iteration.")
        else:
            if detected:
                a(f"   SUSTAIN: detection caught {len(detected)} OPFOR action(s) — "
                  "keep those sensors tuned.")
            for b in missed:
                d = b["detail"]
                a(f"   IMPROVE: {d['action']} against {d['target']} went "
                  f"undetected — review monitoring on {d['target']}.")
            if not blows:
                a("   IMPROVE: no OPFOR actions were executed — the exercise "
                  "tested nothing.")
        a("")

        # 6. OPFOR evolution
        a("6. OPFOR EVOLUTION")
        for t in WAR_ACTIONS:
            e = self.playbook.get(t, {"attempts": 0, "successes": 0})
            rate = (100 * e["successes"] // e["attempts"]) if e["attempts"] else 0
            a(f"   {t}: {e['successes']}/{e['attempts']} success ({rate}%)")
        a("")

        # 7. professor's notes — the lecture for what the OPFOR just did
        a("7. PROFESSOR'S NOTES")
        a("   Every technique above is a programming lesson. Reading is the")
        a("   lecture; the 'your turn' is the lab.")
        techniques = sorted({key[2] for key in seen_ttps})
        for tech in techniques:
            note = PROFESSOR_NOTES.get(tech)
            if not note:
                continue
            a("")
            a(f"   --- {note['title']} ---")
            a(f"   What it is : {note['what']}")
            a(f"   In the sim : {note['in_the_sim']}")
            a(f"   Key idea   : {note['key_idea']}")
            a(f"   Builds     : {note['builds']}")
            a(f"   Your turn  : {note['your_turn']}")
        if not techniques:
            a("   (no techniques exercised — nothing to teach)")
        a("")
        a("SIMULATION ONLY — no real systems were touched. "
          "All effects were computed against virtual targets.")
        return "\n".join(lines)

    def lesson(self, technique_id: str) -> str:
        """Standalone lesson, e.g. war.lesson("T1566"). The professor,
        on demand."""
        note = PROFESSOR_NOTES.get(technique_id)
        if not note:
            known = ", ".join(sorted(PROFESSOR_NOTES))
            raise ValueError(
                f"no lesson for {technique_id!r}; known: {known}"
            )
        return (
            f"{note['title']}\n"
            f"What it is : {note['what']}\n"
            f"In the sim : {note['in_the_sim']}\n"
            f"Key idea   : {note['key_idea']}\n"
            f"Builds     : {note['builds']}\n"
            f"Your turn  : {note['your_turn']}"
        )

    def export_aar(self, path: str, exercise_id: Optional[str] = None) -> str:
        """Write the AAR to a file; returns the path."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.generate_aar(exercise_id))
        return path


def demonstrate_war():
    """A short exercise: Aries storms a virtual network. Nothing real involved."""
    print("\n" + "=" * 70)
    print("⚔️  ARIES AT WAR — SERE exercise (simulation only)")
    print("=" * 70 + "\n")

    war = AriesWar(chain_path="/tmp/sere_war_demo.jsonl",
                   playbook_path="/tmp/sere_war_demo_playbook.json")
    eid = war.begin_exercise(
        objective="storm the virtual branch office",
        operator="herb",
    )
    print(f"Exercise opened: {eid}\n")

    print("--- directed blows ---")
    print("recon:", war.recon("vr://workstation-7")["possible_weaknesses"])
    br = war.breach("vr://workstation-7", "phishing")
    print("breach:", br["breached"], "| blue team alerted:", br["blue_team_alerted"])
    fl = war.flood("vr://db-vault", intensity=8)
    print("flood: degraded", fl["service_degraded_pct"], "% | real packets:",
          fl["real_packets_sent"])
    rv = war.ravage("vr://workstation-7")
    print("ravage:", rv["ravaged"], "| real data harmed:", rv["real_data_harmed"])

    print("\n--- the jar holds: real targets refused ---")
    for bad in ("192.168.1.1", "example.com", "/etc/passwd", "C:\\Windows"):
        try:
            war.flood(bad)
        except ContainmentBreach as e:
            print(f"refused {bad!r}: {str(e)[:60]}...")

    print("\n--- the slime hunts ---")
    from sere_slime import Slime
    slime = Slime(war.world, chain_path="/tmp/sere_war_demo.jsonl",
                  exercise_id=eid)
    war.breach("vr://db-vault", "sql-injection")  # fresh prey
    for i in range(3):
        print(f"  tick {i+1}: {slime.tick()}")
    print(f"  threat memory: {slime.threat_memory} | mass: {slime.mass}")

    print("\n--- campaign: Aries picks its own battles ---")
    for blow in war.campaign(rounds=4):
        print(f"  {blow['tactic']} -> {blow['target']}")

    summary = war.end_exercise()
    ok, msg = war.verify_chain()
    print(f"\nchain: {msg}")
    print("playbook evolved:", json.dumps(summary["playbook"]))
    print("\n--- AFTER ACTION REVIEW ---")
    print(war.generate_aar())
    print("\n" + "=" * 70)
    print("✅ EXERCISE COMPLETE — everything above happened to data, not machines")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demonstrate_war()
