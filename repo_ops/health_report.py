#!/usr/bin/env python3
"""Health report: one concise, phone-readable repo status summary.

Sections: git state, CI status, named test suites, tree hygiene.
Prints ~8 lines. Exit 0 = green, 1 = something needs Herb.

Usage:
  python3 repo_ops/health_report.py           # full (runs the test suites)
  python3 repo_ops/health_report.py --fast    # skips test suites
"""
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OPS = Path(__file__).resolve().parent
sys.path.insert(0, str(OPS))

MDT = timezone(timedelta(hours=-6))  # America/Denver (MDT)


def sh(*args, timeout=120):
    r = subprocess.run(args, capture_output=True, text=True,
                       timeout=timeout, cwd=REPO)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    fast = "--fast" in sys.argv
    lines = []
    ok = True

    now = datetime.now(MDT).strftime("%Y-%m-%d %H:%M MDT")
    lines.append(f"MYTHARA REPO — {now}")

    # Git state
    _, branch, _ = sh("git", "branch", "--show-current")
    _, sha, _ = sh("git", "rev-parse", "--short", "HEAD")
    _, subject, _ = sh("git", "log", "-1", "--format=%s")
    _, dirty, _ = sh("git", "status", "--porcelain")
    state = "clean" if not dirty else f"DIRTY ({len(dirty.splitlines())} files)"
    if dirty:
        ok = False
    lines.append(f"git: {branch} @ {sha} — {state}")

    # CI status (read-only API)
    try:
        import gh
        seen = {}
        for r in gh.workflow_runs(per_page=25):
            if r["head_branch"] == "main" and r["name"] not in seen:
                seen[r["name"]] = r
        if seen:
            ci_bits = []
            for wf, r in sorted(seen.items()):
                c = r["conclusion"] or r["status"]
                mark = "pass" if c == "success" else c
                if c != "success":
                    ok = False
                ci_bits.append(f"{wf} #{r['run_number']} {mark}")
            lines.append("CI: " + " | ".join(ci_bits))
        else:
            lines.append("CI: no runs on main")
    except Exception as e:  # noqa: BLE001
        lines.append(f"CI: unreachable ({type(e).__name__})")
        ok = False

    # Named test suites
    if fast:
        lines.append("tests: skipped (--fast)")
    else:
        code, out, _ = sh(sys.executable, str(OPS / "test_runner.py"), timeout=900)
        summary = [l for l in out.splitlines()
                   if "PASS" in l or "FAIL" in l or "ERROR" in l or "MISSING" in l]
        counts = {}
        for l in summary:
            if "detail" in l or ":" not in l:
                continue
            name, rest = l.split(":", 1)
            counts[name.strip()] = rest.strip()
        bits = [f"{k} {v}" for k, v in counts.items()]
        lines.append("tests: " + ("; ".join(bits) if bits else "no output"))
        if code != 0:
            ok = False
            for l in summary:
                if "detail" in l:
                    lines.append(f"  ! {l.split(':',1)[1].strip()[:160]}")

    # Hygiene
    code, out, _ = sh(sys.executable, str(OPS / "tree_hygiene.py"), "--check")
    if code == 0:
        lines.append("hygiene: clean")
    else:
        ok = False
        first = out.splitlines()[1] if len(out.splitlines()) > 1 else out
        lines.append(f"hygiene: ISSUES — {first[:120]}")

    lines.append("STATUS: GREEN" if ok else "STATUS: NEEDS ATTENTION")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
