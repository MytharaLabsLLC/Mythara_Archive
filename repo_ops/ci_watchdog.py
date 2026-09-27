#!/usr/bin/env python3
"""CI watchdog: polls GitHub Actions, diagnoses failures, fixes the safe
ones, verifies with the test suites, and pushes the fix.

SAFETY (hard, non-negotiable):
  - READ-ONLY BY DEFAULT. The only write path is the CI-fix push, and only
    when ALL of these hold:
      1. The working tree was clean before the watchdog touched anything
         (so the fix commit contains ONLY the fix).
      2. The failure reproduces locally AND belongs to a safe-fix class:
           * black formatting drift  -> run black on the flagged paths
           * ruff F401 unused imports -> ruff --fix --select F401 only
         Everything else (test failures, docker, gpg, trufflehog,
         determinism, infra flakes) is diagnosed and REPORTED, never fixed.
      3. The local repro passes after the fix.
      4. The full named test suites pass after the fix.
      5. No touched file matches a secret pattern, and no diff introduces
         anything secret-shaped.
  - Push goes through bin/gh_api_push.py, which ABORTS if the remote moved.
    That abort is mandatory and is never bypassed, worked around, or retried
    as a force-push. NEVER rewrite history. NEVER force-push. NEVER merge.
  - NEVER touch credentials, secrets, or .env material. NEVER close or merge
    anything involving other contributors.

Usage:
  python3 repo_ops/ci_watchdog.py          # one poll-and-act cycle
  python3 repo_ops/ci_watchdog.py --check  # report CI status only, fix nothing
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OPS = Path(__file__).resolve().parent
sys.path.insert(0, str(OPS))
import gh  # noqa: E402

OWNER, NAME = gh.OWNER, gh.REPO

# Deploy-critical paths, mirroring .github/workflows/ci.yml lint/format steps.
CRITICAL_PATHS = [
    "Commercial/mythara_connect_api.py",
    "mythara_engine_sdk.py",
    "mythara_gopher_api.py",
    "core/source_proprietary/",
]

SECRET_PATH_HINTS = ("secret", "credential", ".pem", ".key", ".env", "token")
SECRET_VALUE_RE = re.compile(
    r"(sk_(live|test|pilot)_[A-Za-z0-9]+|"
    r"(api[_-]?key|password|passwd|secret|bearer)\s*[:=]\s*['\"][^'\"]{8,}['\"])",
    re.IGNORECASE,
)


def sh(*args, timeout=300):
    r = subprocess.run(args, capture_output=True, text=True,
                       timeout=timeout, cwd=REPO)
    return r.returncode, r.stdout, r.stderr


def tree_clean():
    code, out, _ = sh("git", "status", "--porcelain")
    return code == 0 and out.strip() == ""


def ensure_tools():
    """black/ruff are free local tools; install if missing. Returns (black, ruff)."""
    def has(mod):
        return sh(sys.executable, "-m", mod, "--version")[0] == 0
    if not has("black") or not has("ruff"):
        sh(sys.executable, "-m", "pip", "install", "-q", "black", "ruff",
           timeout=600)
    return has("black"), has("ruff")


def latest_runs_by_workflow():
    """Latest run per workflow name, main branch only."""
    seen = {}
    for r in gh.workflow_runs(per_page=25):
        if r["head_branch"] != "main":
            continue
        if r["name"] not in seen:
            seen[r["name"]] = r
    return seen


def failed_steps(run_id):
    """Names of failed steps across jobs in a run."""
    bad = []
    for job in gh.run_jobs(run_id):
        if job["conclusion"] == "failure":
            for s in job["steps"]:
                if s["conclusion"] == "failure":
                    bad.append((job["name"], s["name"]))
    return bad


def classify(step_name):
    s = step_name.lower()
    if "ruff" in s:
        return "ruff"
    if "black" in s:
        return "black"
    if "run tests" in s or s.strip() == "pytest":
        return "pytest"
    if "validation suite" in s:
        return "validation"
    return "other"


REPRO = {
    "ruff": [sys.executable, "-m", "ruff", "check", "--select", "E4,E7,E9,F"],
    "black": [sys.executable, "-m", "black", "--check"],
}


def safe_to_touch(paths):
    for p in paths:
        low = p.lower()
        if any(h in low for h in SECRET_PATH_HINTS):
            return False, f"refusing to touch secret-adjacent path: {p}"
    return True, ""


def diff_has_secret():
    code, out, _ = sh("git", "diff")
    for line in out.splitlines():
        if line.startswith("+") and SECRET_VALUE_RE.search(line):
            return True
    return False


def fix_ruff_f401():
    code, out, err = sh(sys.executable, "-m", "ruff", "check",
                        "--select", "F401", "--fix", *CRITICAL_PATHS)
    return (out + err).strip()


def fix_black():
    code, out, err = sh(sys.executable, "-m", "black", *CRITICAL_PATHS)
    return (out + err).strip()


def commit_fix(message, paths):
    sh("git", "add", *paths)
    code, staged, _ = sh("git", "diff", "--cached", "--name-only")
    staged_set = set(staged.split())
    if staged_set != set(paths):
        return None, f"staged set {staged_set} != fixed set {set(paths)}; aborting"
    if diff_has_secret():
        sh("git", "reset", "HEAD", "--", *paths)
        return None, "secret-shaped content in diff; fix discarded"
    code, _, err = sh("git", "commit", "-m", message)
    if code != 0:
        return None, f"commit failed: {err[-300:]}"
    code, sha, _ = sh("git", "rev-parse", "HEAD")
    return sha.strip(), ""


def push_fix(new_sha, message):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(message)
        msgfile = f.name
    base = gh.main_branch_sha()
    push_script = (Path.home() / "workspace" / "skills" / "github" / "bin"
                   / "gh_api_push.py")
    code, out, err = sh(sys.executable, str(push_script),
                        str(REPO), OWNER, NAME, base, new_sha, msgfile)
    # NOTE: gh_api_push.py ABORTS (exit 2) if the remote moved. That abort is
    # mandatory. We surface it and stop; we never retry, never force.
    return code, (out + err).strip()


def main():
    check_only = "--check" in sys.argv
    report = []
    runs = latest_runs_by_workflow()
    if not runs:
        print("CI: no runs found on main")
        return 0
    for wf, r in sorted(runs.items()):
        report.append(f"{wf}: #{r['run_number']} {r['status']}/{r['conclusion']}")

    failures = [(wf, r) for wf, r in runs.items() if r["conclusion"] == "failure"]
    if not failures:
        print("\n".join(report))
        print("CI GREEN")
        return 0

    print("\n".join(report))
    if check_only:
        print("FAILURES PRESENT (check-only mode; nothing fixed)")
        return 1

    if not tree_clean():
        print("WORKING TREE DIRTY — watchdog will not touch anything. Report:")
        for wf, r in failures:
            for job, step in failed_steps(r["id"]):
                print(f"  {wf} / {job} / {step}: needs a human (dirty tree)")
        return 1

    has_black, has_ruff = ensure_tools()
    acted = False
    for wf, r in failures:
        steps = failed_steps(r["id"])
        if not steps:
            print(f"{wf}: run failed but no failed steps visible; needs a human")
            continue
        for job, step in steps:
            kind = classify(step)
            print(f"{wf} / {job} / {step} -> class={kind}")
            if kind not in ("ruff", "black"):
                print(f"  DIAGNOSIS: {kind} failure is not a safe-fix class; "
                      f"reporting for Herb, changing nothing.")
                continue
            if kind == "ruff" and not has_ruff:
                print("  ruff unavailable; reporting for Herb.")
                continue
            if kind == "black" and not has_black:
                print("  black unavailable; reporting for Herb.")
                continue
            # Reproduce locally. If CI failed but local passes, it's an
            # infra flake — do not touch the tree.
            code, out, err = sh(*(REPRO[kind] + CRITICAL_PATHS))
            if code == 0:
                print(f"  local repro PASSES but CI failed — likely infra flake; "
                      f"changing nothing.")
                continue
            print(f"  reproduced locally:\n    " + (out + err).strip().splitlines()[-1][:200])
            ok, why = safe_to_touch(CRITICAL_PATHS)
            if not ok:
                print(f"  {why}")
                continue
            fix_out = fix_ruff_f401() if kind == "ruff" else fix_black()
            print(f"  applied fix: {fix_out.splitlines()[-1][:200] if fix_out else '(no output)'}")
            # Verify: repro passes now.
            code2, _, _ = sh(*(REPRO[kind] + CRITICAL_PATHS))
            if code2 != 0:
                print("  repro still failing after fix; reverting and reporting.")
                sh("git", "checkout", "--", *CRITICAL_PATHS)
                continue
            # Verify: full named suites.
            code3, out3, _ = sh(sys.executable, str(OPS / "test_runner.py"))
            if code3 != 0:
                print("  named suites FAILED after fix; reverting and reporting.")
                print("  " + "\n  ".join(out3.strip().splitlines()[-6:]))
                sh("git", "checkout", "--", *CRITICAL_PATHS)
                continue
            # Commit only the fixed files, then push via the abort-on-move path.
            code4, changed, _ = sh("git", "status", "--porcelain")
            fixed = sorted({l[3:] for l in changed.splitlines() if l.strip()})
            msg = (f"CI watchdog: fix {kind} failure ({wf} #{r['run_number']})\n\n"
                   f"Failed step: {step}\nApplied: {'ruff --fix --select F401' if kind == 'ruff' else 'black'} "
                   f"on deploy-critical paths. Repro passes; named suites green.")
            sha, errm = commit_fix(msg, fixed)
            if not sha:
                print(f"  {errm}")
                sh("git", "checkout", "--", *CRITICAL_PATHS)
                continue
            pcode, pout = push_fix(sha, msg)
            if pcode != 0:
                print(f"  PUSH RESULT (code {pcode}): {pout[-300:]}")
                if "ABORT" in pout or "remote moved" in pout:
                    print("  remote moved — fix stays local; a human must rebase/retry.")
                continue
            print(f"  PUSHED fix as {sha[:8]}")
            acted = True

    print("WATCHDOG DONE — fixes pushed" if acted else "WATCHDOG DONE — no safe fixes applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
