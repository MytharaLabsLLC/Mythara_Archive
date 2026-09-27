# Mythara Engine — Evaluation Package

**Version:** 1.0.0  
**Release Date:** November 2, 2025  
**Manifest ID:** ME-archive-0001  
**Copyright:** © 2025 Herbert Velez Jr. All rights reserved.  
**License:** Proprietary (see LICENSE.md and COPYRIGHT.md)

---

## Overview

This package contains the Mythara codebase in its current working state, released under a proprietary license for evaluation. It is research software, not a finished commercial product. Read the [Mythara Bible](../docs/📖 Mythara Bible Books I–V.md) first — it describes the system as it actually works today, and this package should be judged against that account, not against marketing language.

**What the system is:**

- **Soul Cradle core** — the governing mechanism. It scores actions on integrity, defined as *Alignment × Tolerance*: how well an action lines up with the principal's aims, multiplied by how much room for error and recovery it leaves. Stated math, stated limits.
- **Eight assessor-witnesses** — demeter, dionysus, eros, hades, hermes, janus, nemesis, persephone. Evidence-fed witnesses under versioned rubrics. They abstain when their domain is not engaged; they fail closed when evidence is missing; a critical finding from any one of them blocks the action; disagreement is surfaced, not averaged away. Every judgment is content-hashed and chained to the record it judges.
- **Hash-chained emotional chain** — tamper-evident emotional records, each attested by the engaged witnesses with sealed judgments chained alongside. The chain proves a record is unaltered. It does not prove the record is true.
- **Aries, defanged** — the system's most capable actor runs behind signed action envelopes, limited to benign, pre-approved handlers. Capability without a leash is not a feature.
- **SERE, the training simulation** — trainees face simulated adversaries inside a sealed virtual environment; everything is recorded to the tamper-evident log and nothing touches the real world. Be plain about this: SERE is a training simulation. It is not a military capability, not an operational cyber weapon, and it never strikes back outside the sandbox.
- **Witnessed Journal** — a local prototype interface on the real chain (`journal_app/server.py`), stdlib-only, localhost by design.

**Package contents for evaluation:**

- ✅ PGP-signed manifests and checksums for authenticity verification
- ✅ Validation suite with determinism tests, leakage probes, and integrity audits
- ✅ Docker container with reproducible builds (runs the validation suite by default)
- ✅ Complete licensing templates (proposed terms — see Licensing Options below)

**All source code, documentation, and materials are proprietary and confidential.**

---

## What's Included

### Core Engine
- `core/` — API specifications, explainability guide, escrow documentation
- `Dockerfile` — Reproducible container build (Python 3.11.6-slim)
- `requirements.txt` — Pinned dependencies

### Validation & Testing
- `tests/` — Determinism tests, leakage probes, SSIP audits
- `Evidence/` — Test results, penetration summaries, drift suppression stats
- `validate_suite/` — Automated validation scripts

### Documentation
- `docs/` — Symbolic glossary, invocation manuals, audit protocols
- `Commercial/` — Pricing tiers, one-pager, clause behavior specs
- `Legal/` — Compliance frameworks, IP assignment and licensing agreements

### Verification Artifacts
- `manifest/RELEASE_MANIFEST.json` + `.asc` (PGP-signed file inventory)
- `manifest/checksums.sha256` + `.asc` (SHA256 hashes with signature)
- `forensic_manifest.json` + `.asc` (Forensic audit manifest)
- `forensic_public_key.asc` (PGP public key for verification)

---

## Quick Start

### 1. Verify Integrity

Import the PGP public key:

```bash
gpg --import forensic_public_key.asc
```

Verify signatures:

```bash
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
gpg --verify manifest/checksums.sha256.asc manifest/checksums.sha256
gpg --verify forensic_manifest.json.asc forensic_manifest.json
```

Expected output: `Good signature from "Mythara Engine <Mythara.Engine@yahoo.com>"`

Verify file checksums:

```bash
cd manifest
sha256sum -c checksums.sha256
```

All files should show `OK`.

### 2. Review Documentation

Start with these files:
- `README.md` (this file)
- `docs/📖 Mythara Bible Books I–V.md` — how the system actually works today; the authoritative technical account
- `Commercial/one_pager.md` — business overview (aspirational; read it against the Bible, not in place of it)
- `core/API_SPEC_PUBLIC.md` — API endpoints and authentication
- `core/EXPLAINABILITY_GUIDE.md` — how audit trails work

### 3. Run Validation Suite

Build the Docker container:

```bash
docker build -t mythara-engine:1.0.0 -f core/Dockerfile .
```

Run determinism tests:

```bash
python tests/run_determinism_test.py --iterations 3
```

Run security validation:

```bash
python tests/run_leakage_probes.py --count 1000
```

See `tests/README.md` for full validation suite instructions.

### 4. Evaluate

**Option A: Container evaluation**
- Build the Docker container and run the included validation suite (see `INSTALL.md`)

**Option B: Sovereign/Air-Gapped evaluation**
- Transfer this entire package to the air-gapped environment
- Verify signatures offline
- Build the container and run the validation suite there

---

## Licensing Options

> **Plainly stated:** commercial licensing is a planned program, not a live one. The tiers below are proposed draft terms. No licenses have been issued, no pilots are running, and no enterprise or government deployments exist. Anyone representing otherwise is not describing this system.

### Development License (proposed)
- **Use Case:** Internal testing, proof-of-concept
- **Restrictions:** Non-production environments only

### Enterprise License (proposed)
- **Use Case:** Production deployment
- **Restrictions:** To be defined in a signed agreement

### Sovereign License (proposed)
- **Use Case:** Air-gapped deployments
- **Restrictions:** To be defined in a signed agreement
- **Includes:** Source code access via escrow release, with an escrow agent of the licensee's choosing

See `Commercial/Pricing_Tiers.md` for the current draft pricing.

---

## Support & Contact

**Herbert Velez Jr.**

- **Email:** mytharalabs@yahoo.com
- **PGP Fingerprint:** `571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C`

**For Technical Questions:**
- Describe your evaluation environment and what you ran
- Attach relevant log files from `tests/output/`

**For Escrow Services:**
- Escrow release conditions, where applicable, are defined in the signed licensing agreement

---

## Security Notice

This package contains proprietary technology protected by:
- Trade secret law
- Copyright (© 2025 Herbert Velez Jr.)
- Contractual NDA obligations

**Unauthorized distribution, reverse engineering, or disclosure is prohibited.**

By downloading this package, you agree to:
1. Maintain confidentiality of all contents
2. Use only for authorized evaluation
3. Not redistribute without written permission from Herbert Velez Jr.

---

## Version History

### v1.0.0 (November 2, 2025)
- Initial release package
- PGP-signed manifest and checksums
- Validation suite
- Docker container with reproducible builds
- Documentation and proposed licensing templates

---

## Next Steps

1. **Verify the package** — import the PGP key and check signatures (steps above)
2. **Run the validation suite** — see `INSTALL.md`
3. **Read the Bible** — `docs/📖 Mythara Bible Books I–V.md` is the authoritative account of how the system works
4. **Talk licensing** — email mytharalabs@yahoo.com with your organization and use case; any engagement begins with a mutual NDA and a written agreement
