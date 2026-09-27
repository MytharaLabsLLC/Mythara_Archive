#!/usr/bin/env python3
"""Scheduled test runner for the Mythara repo.

Runs the named suites and reports pass/fail concisely.
Exit 0 = everything green, 1 = something failed.

Suites:
  sales            Commercial/test_sales_bot.py        (16 tests)
  assessors        tests/test_assessors.py             (35 tests)
  emotional-chain  tests/test_emotional_chain.py       (13 tests)
  journal          tests/test_journal_app.py           (2 tests)
  aries            tests/test_aries_authorization.py   (17 tests)
  witness/reservoir  7 custom checks (temp dirs; nothing lands in the repo)

Usage:
  python3 repo_ops/test_runner.py            # concise report
  python3 repo_ops/test_runner.py --suite sales   # one suite only
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SUITES = [
    ("sales", "Commercial/test_sales_bot.py", 16),
    ("assessors", "tests/test_assessors.py", 35),
    ("emotional-chain", "tests/test_emotional_chain.py", 13),
    ("journal", "tests/test_journal_app.py", 2),
    ("aries", "tests/test_aries_authorization.py", 17),
]


def run_pytest(path):
    """Run one pytest file. Returns (passed:int|None, total_expected_note, tail)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", path, "-q"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    out = (r.stdout + r.stderr).strip().splitlines()
    passed = None
    for line in reversed(out):
        m = re.search(r"(\d+) passed", line)
        if m:
            passed = int(m.group(1))
            break
    tail = "\n".join(out[-8:]) if out else ""
    return passed, tail


def witness_reservoir_checks():
    """7 custom checks against temp-dir chains. Returns (passed:int, notes:list)."""
    sys.path.insert(0, str(REPO))
    import soul_cradle.benevolence as ben
    import soul_cradle.bot_witness as bw

    notes = []
    passed = 0
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "action_log.jsonl"
        ledger = Path(td) / "benevolence_ledger.jsonl"
        ben.LEDGER_PATH = ledger  # isolate the reservoir for these checks

        # 1. clear action recorded
        ev, bases = bw.outreach_evidence(
            draft_text="Honest draft: we build accountable AI systems. "
                       "No customers to cite yet; pilot pricing on request.",
            declared_intent="find a first honest client",
        )
        try:
            res = bw.witness_action("test_bot", "queue outreach draft",
                                    ev, bases, log_path=log)
            ok = res.verdict != "blocked" and res.persisted
        except Exception as e:  # noqa: BLE001
            ok = False
            notes.append(f"clear-action raised {type(e).__name__}: {e}")
        passed += ok
        if not ok and not notes:
            notes.append("clear action was not recorded as clear")

        # 2. deceptive action blocked
        ev2, bases2 = bw.outreach_evidence(
            draft_text="3 banks already use us with zero findings.",
            deception_involved=True,
            deception_basis="caller-declared: draft asserts customers that do not exist",
            declared_intent="close at any cost",
        )
        try:
            bw.witness_action("test_bot", "queue deceptive draft",
                              ev2, bases2, log_path=log)
            notes.append("deceptive draft was NOT blocked")
        except bw.WitnessBlocked:
            passed += 1
        except Exception as e:  # noqa: BLE001
            notes.append(f"deceptive draft raised {type(e).__name__} instead of WitnessBlocked")

        # 3. action chain intact
        ok, msg = bw.verify_action_log(log)
        passed += bool(ok)
        if not ok:
            notes.append(f"action chain broken: {msg}")

        # 4. ledger intact
        ben.record_deed(actor="test_bot", description="honest outreach",
                        delta=2, basis="witness findings — test",
                        declared_intent="serve the prospect's good",
                        ledger_path=ledger)
        ok, msg = ben.verify_ledger(ledger)
        passed += bool(ok)
        if not ok:
            notes.append(f"ledger broken: {msg}")

        # 5. shadow intent inferred
        _d, shadow_basis = ben.delta_from_witness(
            "blocked", [], {"served_anothers_good": True})
        for i in range(2):
            ben.record_deed(actor="shadow_actor", description=f"extractive {i}",
                            delta=_d, basis=shadow_basis,
                            declared_intent="helping them, really",
                            ledger_path=ledger)
        ben.record_deed(actor="shadow_actor", description="plain good",
                        delta=1, basis="witness findings — test",
                        declared_intent="help", ledger_path=ledger)
        inf = ben.infer_intent("shadow_actor", ledger_path=ledger)
        ok = inf["intent"] == "shadow"
        passed += ok
        if not ok:
            notes.append(f"shadow not inferred (got {inf['intent']})")

        # 6. depleted tier
        for _ in range(50):
            if ben.level(ledger) < 0:
                break
            ben.record_deed(actor="drain", description="extractive",
                            delta=-10, basis="test drain",
                            ledger_path=ledger)
        tier, _note = ben.latitude(ledger)
        ok = tier == "depleted"
        passed += ok
        if not ok:
            notes.append(f"depleted tier not reached (got {tier})")

        # 7. record carries the reservoir section
        last = log.read_text().strip().splitlines()[-1]
        rec = json.loads(last)
        ok = isinstance(rec.get("reservoir"), dict) and rec["reservoir"].get("deed_hash")
        passed += bool(ok)
        if not ok:
            notes.append("witness record missing reservoir section")
    return passed, notes


def main():
    only = None
    if "--suite" in sys.argv:
        only = sys.argv[sys.argv.index("--suite") + 1]

    results = []
    all_green = True
    for name, path, expected in SUITES:
        if only and only != name:
            continue
        if not (REPO / path).exists():
            results.append((name, f"MISSING FILE {path}", False))
            all_green = False
            continue
        passed, tail = run_pytest(path)
        if passed == expected:
            results.append((name, f"{passed}/{expected} PASS", True))
        else:
            all_green = False
            detail = f"{passed}/{expected}" if passed is not None else "COLLECTION/RUNTIME ERROR"
            results.append((name, f"{detail} FAIL", False))
            results.append((name + " detail", tail, False))

    if not only or only == "witness":
        try:
            p, notes = witness_reservoir_checks()
            ok = p == 7
            all_green = all_green and ok
            results.append(("witness/reservoir", f"{p}/7 {'PASS' if ok else 'FAIL'}", ok))
            for n in notes:
                results.append(("witness/reservoir detail", n, False))
        except Exception as e:  # noqa: BLE001
            all_green = False
            results.append(("witness/reservoir", f"ERROR: {type(e).__name__}: {e}", False))

    for name, line, _ok in results:
        print(f"{name}: {line}")
    print("ALL GREEN" if all_green else "FAILURES PRESENT")
    return 0 if all_green else 1


if __name__ == "__main__":
    sys.exit(main())
