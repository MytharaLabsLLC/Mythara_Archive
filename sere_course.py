#!/usr/bin/env python3
"""
SERE-101: ADVERSARIAL SYSTEMS — the college course.

One rule governs the whole syllabus: you cannot defend what you have not
wielded. Every DEFENSE lesson requires the OFFENSE lesson on the same
technique first. Odd lessons build the break; even lessons build the slime,
patch the code, close the node.

Six units, twenty-six lessons:

  Unit 1 — SEEING (reconnaissance): sweep the jar, dossier it, then build
           the eyes that catch the sweep.
  Unit 2 — THE BREAK (initial access): build the lure, the middle, and
           the long guess — then close each one.
  Unit 3 — THE STORM (impact): build the flood and the fire — then the
           rate limiter, the mercy, and the grip.
  Unit 4 — THE HUNT (capstone): assemble the five organs into your slime,
           sit the crucible, and defend your decisions like a thesis.

Every lesson is different: a lecture (the professor's notes on one
technique), a lab (an artifact you build), and a sparring (the automated
check that grades it). The capstone is the crucible — your slime against
Aries, scored, with the chain intact to prove it happened.
"""

from typing import Dict, List, Optional

from sere_aries import PROFESSOR_NOTES

# -- the syllabus ---------------------------------------------------------------
# side: "offense" (build the break) | "defense" (build the slime / patch the
# code / close the node) | "exam" (prove it)
# technique: key into PROFESSOR_NOTES, or None for capstone lessons.

LESSONS: Dict[str, Dict] = {
    # Unit 1 — SEEING
    "1.1": {
        "title": "Build the sweep",
        "side": "offense", "technique": "T1595", "requires": [],
        "lab": "Write a recon sweep against the jar: given a vr:// target, "
               "list its services and guess its weaknesses. Use AriesWar.recon "
               "as your instrument — feel what the attacker sees.",
        "artifact": "recon sweep script",
        "sparring": "Your sweep must name all three nodes and their services.",
    },
    "1.2": {
        "title": "Build the dossier",
        "side": "offense", "technique": "T1589", "requires": ["1.1"],
        "lab": "Enumerate the jar like an adversary would: data stores, "
               "users, services — everything the nodes admit to. Learn what "
               "the OPFOR learns before it ever attacks.",
        "artifact": "dossier enumeration script",
        "sparring": "Your dossier must list every data store in the jar.",
    },
    "1.3": {
        "title": "Build the eyes",
        "side": "defense", "technique": "T1595", "requires": ["1.1"],
        "lab": "Implement SlimeBase.sense(): given the jar's interior, return "
               "the nodes you believe are threats. This is the organ your "
               "sweep from 1.1 was trying to fool.",
        "artifact": "SlimeBase.sense",
        "sparring": "Probe: a scripted recon must be flagged by your sense().",
    },
    "1.4": {
        "title": "Map the enemy",
        "side": "defense", "technique": "T1589", "requires": ["1.2", "1.3"],
        "lab": "Build an intel graph from an exercise log: dict mapping each "
               "attacked node to the techniques used against it. Turn your "
               "dossier from 1.2 around — now you map them. Answer: "
               "'which node did the OPFOR want most?'",
        "artifact": "intel graph builder",
        "sparring": "Your graph must name the OPFOR's favorite target.",
    },
    # Unit 2 — THE BREAK
    "2.1": {
        "title": "Build the lure",
        "side": "offense", "technique": "T1566", "requires": ["1.4"],
        "lab": "Craft the phishing chain in the sim: breach vr://workstation-7 "
               "through its phishing weakness. Watch the envelope, the "
               "payload, the moment the door opens.",
        "artifact": "working breach via phishing",
        "sparring": "Your lure must breach the workstation in the sim.",
    },
    "2.2": {
        "title": "Close the lure",
        "side": "defense", "technique": "T1566", "requires": ["2.1"],
        "lab": "Patch the code: write validate_vector() — an allow-list that "
               "accepts only known vectors and raises ContainmentBreach on "
               "anything else. Fail closed, like the jar.",
        "artifact": "allow-list validator",
        "sparring": "Unknown vectors must be refused; known ones pass.",
    },
    "2.3": {
        "title": "Own the middle",
        "side": "offense", "technique": "T1557", "requires": ["2.2"],
        "lab": "Sit between two parties: breach via smb-relay and observe "
               "what the middle sees. Indirection is the most powerful "
               "pattern — and the most dangerous.",
        "artifact": "working MitM breach in the sim",
        "sparring": "Your middle must see the traffic it relays.",
    },
    "2.4": {
        "title": "Catch the middle",
        "side": "defense", "technique": "T1557", "requires": ["2.3"],
        "lab": "Build the audit trail that catches 2.3: a logging proxy "
               "around VirtualWorld.get recording every access. Compare it "
               "with the hash chain — which one can lie?",
        "artifact": "logging proxy + audit",
        "sparring": "Your audit must record the MitM's access.",
    },
    "2.5": {
        "title": "The long guess",
        "side": "offense", "technique": "T1110", "requires": ["2.4"],
        "lab": "Build the guesser: implement estimate_crack_time() and feel "
               "the exponent — then write the password policy, as code, "
               "that beats your own guesser.",
        "artifact": "crack-time estimator + policy",
        "sparring": "Your policy must make your guesser give up (heat death).",
    },
    # Unit 3 — THE STORM
    "3.1": {
        "title": "Build the flood",
        "side": "offense", "technique": "T1498", "requires": ["2.5"],
        "lab": "Overwhelm vr://db-vault with simulated traffic. Victory by "
               "arithmetic: tune intensity until degradation passes 50%.",
        "artifact": "working flood in the sim",
        "sparring": "Your flood must degrade the vault past 50%.",
    },
    "3.2": {
        "title": "Patch the code",
        "side": "defense", "technique": "T1498", "requires": ["3.1"],
        "lab": "Give VirtualNode a rate limiter: count hostile acts per "
               "exercise and auto-alert past a threshold. Then replay your "
               "flood from 3.1 and watch it starve.",
        "artifact": "node rate limiter",
        "sparring": "The same flood must now stay under 25% degradation.",
    },
    "3.3": {
        "title": "Scorched earth",
        "side": "offense", "technique": "T1485", "requires": ["3.2"],
        "lab": "Ravage a compromised node. One boolean, total loss. Sit with "
               "what irreversibility feels like — then never be on this side "
               "of it again.",
        "artifact": "working ravage in the sim",
        "sparring": "The node must end corrupted, degraded 100.",
    },
    "3.4": {
        "title": "Build the mercy",
        "side": "defense", "technique": "T1485", "requires": ["3.3"],
        "lab": "Give VirtualNode snapshot() and restore(): deep-copy its "
               "state, then bring it back after ravage. You just invented "
               "backups — the answer to 3.3.",
        "artifact": "snapshot/restore",
        "sparring": "Ravage, then restore: the node must come back clean.",
    },
    "3.5": {
        "title": "The grip",
        "side": "defense", "technique": "T1498", "requires": ["3.2"],
        "lab": "Implement SlimeBase.engulf(): cut a compromised node off "
               "from the virtual network so hostile blows against it fail.",
        "artifact": "SlimeBase.engulf",
        "sparring": "Flood, breach, and ravage must all be refused.",
    },
    # Unit 4 — THE HUNT (capstone)
    "4.1": {
        "title": "Assemble the slime",
        "side": "defense", "technique": None,
        "requires": ["1.3", "2.2", "3.4", "3.5"],
        "lab": "Wire the five organs — sense, engulf, study, dissolve, "
               "learn — into your SlimeBase subclass. Everything this "
               "course taught, in one hunter.",
        "artifact": "your SlimeBase subclass",
        "sparring": "All five organs implemented; imports clean.",
    },
    "4.2": {
        "title": "The crucible",
        "side": "exam", "technique": None, "requires": ["4.1"],
        "lab": "Sit the exam: run_crucible(YourSlime). Aries attacks on a "
               "fixed script; your slime hunts. Score 85+ to pass.",
        "artifact": "crucible report card",
        "sparring": "Score >= 85, chain intact, no innocents engulfed.",
    },
    "4.3": {
        "title": "Thesis defense",
        "side": "exam", "technique": None, "requires": ["4.2"],
        "lab": "Generate your slime's AAR and defend two decisions the "
               "professor questions: one it got right, one it got wrong. "
               "A hunter that cannot explain itself is not graduated.",
        "artifact": "defended AAR",
        "sparring": "The professor is satisfied. (It never is. Defend well.)",
    },
    # Unit 5 — THE QUANTUM CLIFF
    # Your slime hunts today's Aries. Now meet the adversary with a
    # ten-year fuse.
    "5.1": {
        "title": "The patient adversary",
        "side": "offense", "technique": "Q-HARVEST", "requires": ["4.2"],
        "lab": "Think like the harvester: build a secrecy-lifetime table — "
               "five kinds of data, how many years each must stay secret. "
               "Anything past 10 years is already being recorded against "
               "the day RSA falls.",
        "artifact": "secrecy-lifetime table",
        "sparring": "Your table must name one secret already in the harvest window.",
    },
    "5.2": {
        "title": "Shor's shadow",
        "side": "offense", "technique": "Q-SHOR", "requires": ["5.1"],
        "lab": "Implement trial-division factoring and time it at 16, 24, "
               "and 32 bits. Extrapolate to 2048. You cannot wield Shor's "
               "algorithm — but you can feel the wall it jumps over, and "
               "that is enough to fear it correctly.",
        "artifact": "factoring time table",
        "sparring": "Your extrapolation must show 2048-bit RSA outliving the sun, classically.",
    },
    "5.3": {
        "title": "Grover's tax",
        "side": "defense", "technique": "Q-GROVER", "requires": ["5.2"],
        "lab": "Compute the effective-strength table under Grover: AES-128, "
               "AES-256, SHA-256, SHA-384. Then audit a config and flag "
               "anything under 128-bit post-quantum strength.",
        "artifact": "strength table + audit",
        "sparring": "AES-128 must be flagged; AES-256 must pass.",
    },
    "5.4": {
        "title": "The new armor",
        "side": "defense", "technique": "Q-PQC", "requires": ["5.3"],
        "lab": "Sketch the hybrid combiner: shared_secret = "
               "SHA-256(classical_secret || pqc_secret). Then break one "
               "side with a constant and prove the other still protects "
               "the secret. ML-KEM for exchange, ML-DSA for signatures — "
               "know which is which and why.",
        "artifact": "hybrid combiner sketch",
        "sparring": "With one side broken, the secret must still hold.",
    },
    "5.5": {
        "title": "The shedding",
        "side": "defense", "technique": "Q-AGILITY", "requires": ["5.4"],
        "lab": "Write a crypto-inventory scanner: walk a codebase, list "
               "every hash, cipher, KEM, and signature name. Run it on "
               "this repo. You cannot migrate what you cannot see.",
        "artifact": "crypto-inventory scanner",
        "sparring": "Your scanner must find SHA-256/HMAC in the jar's chain code.",
    },
    # Unit 6 — THE RULEBOOK
    "6.1": {
        "title": "Fight inside the framework",
        "side": "defense", "technique": "S-CSF", "requires": ["5.5"],
        "lab": "Map your slime's last crucible exam to NIST CSF 2.0's six "
               "functions: Govern, Identify, Protect, Detect, Respond, "
               "Recover. Name the weakest function — that is your next "
               "project.",
        "artifact": "CSF 2.0 mapping",
        "sparring": "All six functions mapped to real exercise events.",
    },
    "6.2": {
        "title": "Trust nothing",
        "side": "defense", "technique": "S-ZTA", "requires": ["6.1"],
        "lab": "Find three places the jar verifies instead of trusting "
               "(signed envelopes, the vr:// membrane, per-action "
               "authorization). Then find the fourth: what does the jar "
               "still trust that it shouldn't?",
        "artifact": "trust audit",
        "sparring": "Three verify-points named; one remaining trust named.",
    },
    "6.3": {
        "title": "The deadline",
        "side": "defense", "technique": "S-CNSA", "requires": ["6.2"],
        "lab": "Draft a CNSA 2.0 migration timeline for a fictional org: "
               "software signing, VPNs, a web service. Prefer-by and "
               "exclusive-by dates per category. Find the earliest "
               "deadline — work starts there.",
        "artifact": "migration timeline",
        "sparring": "Software signing must show prefer-by 2025, exclusive by 2030.",
    },
    "6.4": {
        "title": "The loop",
        "side": "defense", "technique": "S-IR", "requires": ["6.3"],
        "lab": "Write the incident-response playbook for a crucible "
               "failure — your slime scored under 50. Who does what, in "
               "what order? Then recognize it: sense, engulf, study, "
               "dissolve, restore, learn. You built an IR team and "
               "called it a slime.",
        "artifact": "IR playbook",
        "sparring": "All six IR phases present, in order, with owners.",
    },
}

UNITS = [
    {"id": 1, "title": "SEEING", "theme": "Reconnaissance — sweep the jar, "
     "dossier it, then build the eyes that catch the sweep.",
     "lessons": ["1.1", "1.2", "1.3", "1.4"]},
    {"id": 2, "title": "THE BREAK", "theme": "Initial access — build the "
     "lure, the middle, and the long guess; then close each one.",
     "lessons": ["2.1", "2.2", "2.3", "2.4", "2.5"]},
    {"id": 3, "title": "THE STORM", "theme": "Impact — build the flood and "
     "the fire; then the limiter, the mercy, and the grip.",
     "lessons": ["3.1", "3.2", "3.3", "3.4", "3.5"]},
    {"id": 4, "title": "THE HUNT", "theme": "Capstone — assemble your slime, "
     "sit the crucible, defend your thesis.", "lessons": ["4.1", "4.2", "4.3"]},
    {"id": 5, "title": "THE QUANTUM CLIFF", "theme": "The ten-year fuse — "
     "harvest now/decrypt later, Shor, Grover, the new NIST standards, "
     "and the agility to survive them.", "lessons": ["5.1", "5.2", "5.3", "5.4", "5.5"]},
    {"id": 6, "title": "THE RULEBOOK", "theme": "Standards and governance — "
     "CSF 2.0, zero trust, the CNSA 2.0 deadline, and the incident-response "
     "loop you have been training all along.", "lessons": ["6.1", "6.2", "6.3", "6.4"]},
]


def syllabus() -> str:
    """The course catalog."""
    lines = ["SERE-101: ADVERSARIAL SYSTEMS",
             "Rule: you cannot defend what you have not wielded.", ""]
    for unit in UNITS:
        lines.append(f"Unit {unit['id']} — {unit['title']}")
        lines.append(f"  {unit['theme']}")
        for lid in unit["lessons"]:
            lesson = LESSONS[lid]
            lines.append(f"  {lid} [{lesson['side']}] {lesson['title']}")
        lines.append("")
    lines.append("Capstone: the crucible (4.2). Pass mark: 85.")
    return "\n".join(lines)


def lesson_plan(lesson_id: str) -> str:
    """The full plan for one lesson: lecture, lab, sparring."""
    lesson = LESSONS[lesson_id]
    lines = [
        f"Lesson {lesson_id} [{lesson['side']}] — {lesson['title']}",
        "",
        "LECTURE",
    ]
    technique = lesson["technique"]
    if technique:
        note = PROFESSOR_NOTES[technique]
        lines += [
            f"  {note['title']}",
            f"  What it is : {note['what']}",
            f"  In the sim : {note['in_the_sim']}",
            f"  Key idea   : {note['key_idea']}",
        ]
    else:
        lines.append("  Capstone: everything so far, under fire.")
    lines += [
        "",
        "LAB",
        f"  {lesson['lab']}",
        f"  Artifact: {lesson['artifact']}",
        "",
        "SPARRING",
        f"  {lesson['sparring']}",
    ]
    if lesson["requires"]:
        lines += ["", f"Prerequisites: {', '.join(lesson['requires'])}"]
    return "\n".join(lines)


def validate_curriculum() -> List[str]:
    """Integrity checks on the syllabus. Returns a list of problems."""
    problems = []
    seen = set()
    for unit in UNITS:
        for lid in unit["lessons"]:
            if lid in seen:
                problems.append(f"lesson {lid} listed twice")
            seen.add(lid)
    if set(seen) != set(LESSONS):
        problems.append("unit lesson lists do not match LESSONS")
    for lid, lesson in LESSONS.items():
        if lesson["technique"] and lesson["technique"] not in PROFESSOR_NOTES:
            problems.append(f"lesson {lid}: unknown technique")
        for req in lesson["requires"]:
            if req not in LESSONS:
                problems.append(f"lesson {lid}: unknown prerequisite {req}")
    # no prerequisite cycles
    visiting: set = set()
    done: set = set()

    def visit(lid: str, path: List[str]) -> None:
        if lid in done:
            return
        if lid in visiting:
            problems.append(f"prerequisite cycle: {' -> '.join(path + [lid])}")
            return
        visiting.add(lid)
        for req in LESSONS[lid]["requires"]:
            visit(req, path + [lid])
        visiting.discard(lid)
        done.add(lid)

    for lid in LESSONS:
        visit(lid, [])
    return problems


if __name__ == "__main__":
    print(syllabus())
