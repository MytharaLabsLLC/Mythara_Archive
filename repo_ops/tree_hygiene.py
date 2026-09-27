#!/usr/bin/env python3
"""Tree hygiene: runtime junk must NEVER be committed.

Enforces via .gitignore (the one git write this bot is allowed, besides
the CI watchdog's fix push). Checks:

  1. .gitignore contains the required junk patterns (adds missing ones).
  2. Junk present in the working tree is actually ignored.
  3. No junk is staged for commit (violation -> report, never auto-unstage).
  4. Junk already TRACKED in git is flagged for a human (never auto-untracks).

Junk classes: __pycache__/, *.jsonl ledgers, .pytest_cache/, bot_blessings.json.

Usage:
  python3 repo_ops/tree_hygiene.py          # check + enforce .gitignore
  python3 repo_ops/tree_hygiene.py --check   # report only
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REQUIRED_PATTERNS = {
    "__pycache__/",
    "*.jsonl",
    "**/bot_blessings.json",
    ".pytest_cache/",
}

JUNK_FINDERS = [
    ("__pycache__", ["-type", "d", "-name", "__pycache__"]),
    ("jsonl ledger", ["-type", "f", "-name", "*.jsonl"]),
    (".pytest_cache", ["-type", "d", "-name", ".pytest_cache"]),
    ("bot_blessings.json", ["-type", "f", "-name", "bot_blessings.json"]),
]


def sh(*args, timeout=120):
    r = subprocess.run(args, capture_output=True, text=True,
                       timeout=timeout, cwd=REPO)
    return r.returncode, r.stdout, r.stderr


def gitignore_patterns():
    pats = set()
    gi = REPO / ".gitignore"
    if gi.exists():
        for line in gi.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                pats.add(line)
    return pats


def main():
    check_only = "--check" in sys.argv
    problems = []

    # 1. .gitignore must contain every required pattern.
    pats = gitignore_patterns()
    missing = REQUIRED_PATTERNS - pats
    if missing and not check_only:
        gi = REPO / ".gitignore"
        with open(gi, "a", encoding="utf-8") as fh:
            fh.write("\n# repo_ops/tree_hygiene.py — runtime junk, never committed\n")
            for m in sorted(missing):
                fh.write(m + "\n")
        print(f"HYGIENE: added to .gitignore: {sorted(missing)}")
        pats = gitignore_patterns()
    elif missing:
        problems.append(f".gitignore missing patterns: {sorted(missing)}")

    # 2. Every junk file on disk must be ignored.
    for label, find_args in JUNK_FINDERS:
        code, out, _ = sh("find", ".", "-path", "./.git", "-prune", "-o",
                          *find_args, "-print")
        for p in out.splitlines():
            rel = p[2:] if p.startswith("./") else p
            code2, _, _ = sh("git", "check-ignore", "-q", rel)
            if code2 != 0:
                # Tracked files are never "ignored" — handled in step 4.
                tcode, tout, _ = sh("git", "ls-files", rel)
                if tout.strip():
                    continue
                problems.append(f"junk NOT ignored: {rel} ({label})")

    # 3. Staged junk is a hard violation.
    code, staged, _ = sh("git", "diff", "--cached", "--name-only")
    staged_junk = []
    for f in staged.splitlines():
        f = f.strip()
        if (f.endswith(".jsonl") or "__pycache__" in f
                or f.endswith("bot_blessings.json")
                or ".pytest_cache" in f):
            staged_junk.append(f)
    if staged_junk:
        problems.append(f"JUNK STAGED FOR COMMIT: {staged_junk} — unstage before any push")

    # 4. Junk already tracked: flag for a human, never auto-untrack.
    code, tracked, _ = sh("git", "ls-files")
    tracked_junk = [f for f in tracked.splitlines()
                    if f.strip().endswith(".jsonl")
                    or f.strip().endswith("bot_blessings.json")]
    if tracked_junk:
        problems.append(f"junk already TRACKED in git (human decision needed): {tracked_junk}")

    if problems:
        print("HYGIENE ISSUES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("HYGIENE CLEAN: .gitignore covers all junk classes; no junk staged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
