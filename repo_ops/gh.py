#!/usr/bin/env python3
"""Shared GitHub API client for repo_ops bots.

Uses the stored custom.github credential via api.github.com ONLY.
Never touches github.com, never prints or persists raw credentials.

SAFETY: read-only helpers are free to use. Anything that writes
(refs, merges, issues, PRs) must be called explicitly by name from a
bot whose task authorizes that exact write — the watchdog only ever
calls update_ref for the CI-fix push path.
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

API = "https://api.github.com"
HOSTS = ["api.github.com"]
OWNER = "herbievelezjr"
REPO = "Mythara_Archive"


def api(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.github", allowed_hosts=HOSTS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return read_json_response(resp)


def get(path):
    return api("GET", path)


def repo_path(path):
    return f"/repos/{OWNER}/{REPO}{path}"


def main_branch_sha():
    ref = get(repo_path("/git/ref/heads/main"))
    return ref["object"]["sha"]


def workflow_runs(per_page=10):
    return get(repo_path(f"/actions/runs?per_page={per_page}"))["workflow_runs"]


def run_jobs(run_id):
    return get(repo_path(f"/actions/runs/{run_id}/jobs"))["jobs"]


if __name__ == "__main__":
    print("main:", main_branch_sha()[:8])
    for r in workflow_runs(5):
        print(r["name"], "#%s" % r["run_number"], r["head_branch"],
              r["status"], r["conclusion"], r["head_sha"][:8])
