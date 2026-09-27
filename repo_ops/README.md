# repo_ops — repo-management bots

Bots that keep Herb's repo healthy without him touching it. Read-only by
default. The ONLY writes these bots ever make:

- **ci_watchdog.py** — pushes a CI fix, and only after: the tree was clean,
  the failure reproduced locally, the fix is mechanical (black formatting or
  ruff F401 unused imports), the repro passes, and the full named suites pass.
  Push goes through `bin/gh_api_push.py`, which **aborts if the remote moved**
  — that abort is never bypassed, never retried as a force-push.
- **tree_hygiene.py** — adds missing junk patterns to `.gitignore`.

NEVER: rewrite history, force-push, merge, touch secrets/credentials,
close or merge anything involving other contributors. Test failures, docker,
gpg, TruffleHog, determinism, and infra flakes are diagnosed and REPORTED,
never auto-fixed.

## The bots

| Bot | What it does | Run |
|---|---|---|
| `gh.py` | Shared GitHub API client (`custom.github` via `api.github.com` only) | `python3 repo_ops/gh.py` |
| `test_runner.py` | Named suites: sales 16, assessors 35, emotional chain 13, journal 2, Aries 17, witness/reservoir 7 custom checks (temp dirs — nothing lands in the repo). Exit 0 = all green. | `python3 repo_ops/test_runner.py` |
| `ci_watchdog.py` | Polls Actions runs on main; on failure diagnoses, safe-fixes, verifies, pushes. `--check` = report only, fix nothing. | `python3 repo_ops/ci_watchdog.py` |
| `tree_hygiene.py` | Enforces `.gitignore` junk coverage (`__pycache__/`, `*.jsonl`, `.pytest_cache/`, `**/bot_blessings.json`); flags staged or tracked junk. `--check` = report only. | `python3 repo_ops/tree_hygiene.py` |
| `health_report.py` | One phone-readable summary: git state, CI, tests, hygiene. `--fast` skips the suites. | `python3 repo_ops/health_report.py` |

## Scheduling (not yet wired)

These are built to be scheduled but no cron jobs were created — that needs
Herb's go. Intended cadence:

- `health_report.py` — daily morning ping.
- `test_runner.py` — after every push, or nightly.
- `ci_watchdog.py --check` — every 30 min; full mode only with approval,
  since it can push.
- `tree_hygiene.py` — before every commit/push.

## Kill switch

Herb: say "stop the repo bots" and nothing here runs again. Nothing in this
directory commits or pushes on its own — every run is started by a human or
by a scheduler Herb approved.
