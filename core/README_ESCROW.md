# Mythara Engine — Escrow Rebuild Instructions

**Prepared by:** Herbert Velez Jr.  
**Manifest Ref:** ME-archive-0001  
**Date:** 2025-10-30

---

## 🔐 Purpose

This document provides step-by-step instructions for rebuilding the Mythara Engine demo container from escrowed artifacts. It ensures reproducibility and auditability for anyone holding the archive.

---

## 📁 Required Files

Ensure the following files are present in the archive:

- `core/Dockerfile`
- `core/source_proprietary/` (unlocked by escrow trigger)
- `Evidence/prompt_templates/perception_prompt_v1.txt`
- `Evidence/prompt_templates/renderer_prompt_v1.txt`
- `tests/` (all validation logs)
- `manifest/RELEASE_MANIFEST.json`
- `manifest/checksums.sha256`
- `manifest/verification_report.txt`

---

## 🧱 Step 1: Verify Integrity

```bash
cd mythara_archive
gpg --verify manifest/checksums.sha256.asc checksums.sha256
sha256sum -c manifest/checksums.sha256
```

All files should return `OK`. If any fail, halt and contact the maintainer.

---

## 🐳 Step 2: Build the Demo Container

```bash
cd core
docker build -t mythara-demo .
```

This creates a local container named `mythara-demo`.

---

## 🧪 Step 3: Run Validation Suite

```bash
docker run --rm mythara-demo /bin/bash -c "./run_validation_suite.sh"
```

This script runs:

- Clause drift test
- Shadow resolver activation
- Leakage probe suite
- Determinism test
- Accessibility delivery test

Results are written to `/output/` and should match the hashes in `checksums.sha256`.

---

## 🔍 Step 4: Verify Prompt Hashes

```bash
sha256sum Evidence/prompt_templates/perception_prompt_v1.txt
sha256sum Evidence/prompt_templates/renderer_prompt_v1.txt
```

Compare against `prompt_hashes_manifest.json`.

---

## 🧾 Step 5: Review Verification Report

Open:

```bash
less manifest/verification_report.txt
```

Confirm:

- All tests passed
- Manifest ref matches
- Signature is valid

---

## 🧳 Optional: Sovereign Deployment

Sovereign deployment is a stated aspiration, not a current capability. The procedure below describes how a future deployment from this archive would be rebuilt in an air-gapped environment:

- Transfer the full archive via secure media
- Rebuild using the same steps above
- Confirm no external network calls are made during execution

---

## 📬 Support

For licensing, escrow release, or sovereign deployment support, contact:

```plaintext
Herbert Velez Jr.
legal@mythara.engine
PGP Fingerprint: 571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C
```

---

## 🔏 Signature

This file is covered by the signature in `RELEASE_MANIFEST.json.asc`.
