# GitHub Copilot Instructions for Mythara Engine

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

These instructions are a compact, actionable reference for AI coding agents working in this repo. Keep edits small and always preserve the repository copyright header in any new files.

### Fast orientation (what matters)
- The API server is implemented at `core/source_proprietary/main.py` (FastAPI). Key endpoints:
	- POST `/v1/clauses/invoke` — clause invocation (see `ClauseInvocationRequest`/`Response` models).
	- GET `/v1/manifest/clauses` — returns clause manifest + integrity hashes.
	- Health/docs: `/health` and `/api/docs`.
- In-memory stubs: `CLAUSE_DB` and `BR_STATE` in `main.py`. Production systems must replace these with a DB/Redis.

### How to run & common developer workflows
- Run API locally (from `core/source_proprietary/` or set PYTHONPATH accordingly):
	- python: `python core/source_proprietary/main.py` (this script calls uvicorn)
	- uvicorn: `uvicorn core.source_proprietary.main:app --reload --host 0.0.0.0 --port 8000`
- Build container: `docker build -f core/Dockerfile -t mythara:v1.0.0 .`
- Run full validation suite (determinism, leakage, SSIP audits): `python run_validation_suite.py` (writes to `tests/output/`).
- Run tests: `pytest -q` (repo root). Validation scripts call tests like `tests/run_determinism_test.py`.
- Lint/typecheck: tools are listed in `requirements.txt` (black, ruff, mypy). Use the project's standard commands (e.g., `ruff check .`, `black . --check`).

### Secrets & configuration
- `core/source_proprietary/requirements-api.txt` shows runtime dependencies (fastapi/uvicorn, python-dotenv). The repository uses in-code `VALID_API_KEYS` for demos (see `main.py`).
- DO NOT hardcode production API keys: use environment variables or a secrets manager; prefer `.env` for local dev (python-dotenv is present).

### Project-specific conventions and patterns
- Copyright header: every new file (python and markdown) must include the repo header shown above.
- Integrity-first responses: endpoints generate SHA-256 integrity hashes for invocations and manifests — preserve this pattern when adding endpoints or background jobs.
- SSIP-first telemetry: return or emit SSIP metrics (drift suppression, messenger pairing fidelity, emotional fidelity) on audit endpoints and logs.
- Tests and validation produce artifacts in `tests/output/` (the validation runner documents expected file names).

### Integration points (observed in repo)
- PGP/forensic verification: `manifest/checksums.sha256` and `forensic_manifest.json.asc` — reviewers use `gpg --verify` and `sha256sum -c` (see `README.md`).
- Docker: `core/Dockerfile` for container builds.
- Optional DB/Redis hooks: `main.py` contains comments showing where to plug Postgres/Redis for production state.

### Minimal examples to cite in PRs and patches
- Add an endpoint that mirrors existing patterns: validate input with pydantic, authenticate with `verify_api_key` (or env-backed replacement), compute integrity hash via `hashlib.sha256`, log via `logging` and return the integrity hash in response.
- To run quick local validation in CI, call: `python run_validation_suite.py` and check `tests/output/` for reports.

### Where to look for details
- API code & behavior: `core/source_proprietary/main.py`
- API dependencies: `core/source_proprietary/requirements-api.txt`
- Root dependencies & dev tools: `requirements.txt`
- Validation runner & orchestration: `run_validation_suite.py` and `tests/`
- Build and escrow artifacts: `core/Dockerfile`, `manifest/`, `forensic_*` files

---

If any section above is unclear or you'd like me to expand with exact CLI snippets tailored to CI or a Docker-compose flow, tell me which area to expand and I'll update the file. 

---

**Do not remove or alter the copyright header in new files.**
