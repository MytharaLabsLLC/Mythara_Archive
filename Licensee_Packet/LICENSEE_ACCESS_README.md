**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  
**Proprietary and Confidential.**

# Licensee Access Readme — Mythara Engine (Private, Non-Exclusive Evaluation)

> **TEMPLATE — no licenses sold, no licensees exist as of September 2026.**
> This document is a template for a future licensee packet. Nothing here
> implies any licensee has been granted access or any evaluation is underway.

This repository is private. Your access is Read-only and governed by `../LICENSE.md`. Access is granted under a non-exclusive, non-transferable, revocable evaluation license strictly for internal evaluation. If you do not agree to LICENSE.md, do not access or use these materials.

## Your access level

- Permission: Read (no write, no admin)  
- Scope: View code, download releases, open issues (if enabled)  
- Forking: Private repo; forking is not permitted outside the owner’s controls. You may still clone to your internal systems; all confidentiality and license restrictions apply.

## What you can do

- Evaluate internally and assess integrations and SSIP conformance.  
- Run the provided validation suite locally.  
- Review FastAPI reference implementation under `../core/source_proprietary/` (not for production without a paid license).

## What you cannot do

- No redistribution, sublicensing, or public disclosure.  
- No derivative works without prior written consent.  
- No removal of proprietary headers or notices.  
- No production deployment without a signed production license.

## Download and verify the licensed artifact

- Go to GitHub → Releases → mythara-engine-v1.0.0.zip  
- Download both files:
  - mythara-engine-v1.0.0.zip
  - mythara-engine-v1.0.0.zip.sha256
- Verify on Windows PowerShell:

```powershell
Get-FileHash .\mythara-engine-v1.0.0.zip -Algorithm SHA256
```

Compare to the value in mythara-engine-v1.0.0.zip.sha256 and in the release notes. They must match exactly.

## Running locally (evaluation only)

- Validation suite: see `../run_validation_suite.py` and the `../tests/` directory.
- FastAPI reference server: see `../core/source_proprietary/README_API.md`.

## Security and reporting

- Treat all materials as confidential and proprietary.  
- Report suspected vulnerabilities privately to: [Mythara.Engine@yahoo.com](mailto:Mythara.Engine@yahoo.com)

## Contact

- Licensing and support: [Mythara.Engine@yahoo.com](mailto:Mythara.Engine@yahoo.com)
