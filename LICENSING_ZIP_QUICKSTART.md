# Mythara Engine — Licensing ZIP Quick Start

**Package:** `mythara-engine-v1.0.0.zip`  
**Size:** 0.7 MB  
**SHA256:** `94b45d271f56b9cd06c9c1323aa09949cf81a9d9f1d951e20a7ee42180453da2`  
**Date:** November 2, 2025

---

## What You Have *(as assembled November 2025 — historical snapshot; the ZIP itself is not present in this archive)*

✅ **Licensing package contents** for private GitHub repository distribution

### Package Contents

- ✅ **README.md** — Feature overview, quick start, licensing options
- ✅ **LICENSE.md** — Proprietary license with evaluation terms
- ✅ **COPYRIGHT.md** — Comprehensive IP ownership notice (all components protected)
- ✅ **INSTALL.md** — Docker, native Python, and air-gapped deployment instructions
- ✅ **Mythara_Engine_Validation_Report_v1.0.0.txt** — Test results (the archive's own Nov 2025 summary reports 4 suites passing)
- ✅ **PGP-signed manifests** — RELEASE_MANIFEST.json.asc, checksums.sha256.asc
- ✅ **Complete documentation** — docs/, core/API_SPEC_PUBLIC.md (all with copyright headers)
- ✅ **Validation suite** — tests/, Evidence/ with all test results (copyright protected)
- ✅ **Legal templates** — Legal/ with NDA, Master License Agreement, SOW templates
- ✅ **Commercial materials** — Commercial/ with pricing, one-pager, clause specs
- ✅ **Accessibility test scripts** — braille and audio token delivery tests (no WCAG certification held)
- ✅ **Crisis resource links** — `docs/Mental_Health_Crisis_Resources.md` (not a clinical product; real emergencies belong with real crisis resources)

---

## How to Use This Package

### Option 1: Upload to Private GitHub Repository

1. **Create private repository** on GitHub
   ```powershell
   gh repo create mythara-labs/mythara-engine --private
   ```

2. **Create a GitHub release**
   - Go to repository → Releases → Draft a new release
   - Tag version: `v1.0.0`
   - Upload `mythara-engine-v1.0.0.zip`
   - Include SHA256 hash in release notes

3. **Invite licensed companies**
   - Repository → Settings → Collaborators
   - Add their GitHub usernames with Read access

**Full instructions:** See `GitHub_Release_Package/GITHUB_RELEASE_GUIDE.md`

---

### Option 2: Direct Distribution (Email/Secure File Sharing)

1. **Upload to secure platform**
   - Box, Dropbox Business, OneDrive for Business
   - Or attach to encrypted email (if < 10 MB)

2. **Include verification hash**

```text
Subject: Mythara Engine v1.0.0 — License Package

Attached: mythara-engine-v1.0.0.zip
SHA256: 94b45d271f56b9cd06c9c1323aa09949cf81a9d9f1d951e20a7ee42180453da2

After extraction:
1. Run verification (gpg --verify and sha256sum -c as shown below; note verify.ps1/verify.sh are not in this archive)
2. Review README.md for deployment options
3. Contact mytharalabs@yahoo.com with questions
```

3. **Company verifies integrity**
   ```powershell
   # Windows
   (Get-FileHash -Algorithm SHA256 mythara-engine-v1.0.0.zip).Hash
   
   # Compare with: 94b45d271f56b9cd06c9c1323aa09949cf81a9d9f1d951e20a7ee42180453da2
   ```

---

## What Companies Will See

When they extract the ZIP, they get:

```
mythara-engine-v1.0.0/
├── README.md                    # Start here
├── LICENSE.md                   # Proprietary terms
├── COPYRIGHT.md                 # Comprehensive IP protection notice
├── INSTALL.md                   # Deployment guide
├── forensic_manifest.json       # Signed manifest
├── forensic_manifest.json.asc   # PGP signature
├── forensic_public_key.asc      # Your public key
├── core/                        # Engine specifications
│   ├── API_SPEC_PUBLIC.md
│   ├── EXPLAINABILITY_GUIDE.md
│   ├── Dockerfile
│   └── README_ESCROW.md
├── docs/                        # Full documentation (copyright headers)
│   ├── Mental_Health_Crisis_Resources.md
│   └── [other docs]
├── tests/                       # Validation suite (all .py files have copyright)
│   ├── run_determinism_test.py
│   ├── run_leakage_probes.py
│   ├── run_ssip_audit.py
│   └── test_accessibility_delivery.py
├── Evidence/                    # Test results
├── Commercial/                  # Pricing, one-pager
├── Legal/                       # NDA, license templates, compliance
│   └── Compliance/
│       ├── ACCESSIBILITY_AND_COMPLIANCE_FRAMEWORK.md
│       ├── International/WCAG_2.1_AAA_Conformance.md
│       ├── US/Mental_Health_Clinical_Integration.md
│       └── [other compliance docs - all copyright protected]
├── manifest/                    # Signed manifests & checksums
└── validate_suite/              # Automated validation
```

---

## Verification Workflow (Company Side)

1. **Extract ZIP**
   ```bash
   unzip mythara-engine-v1.0.0.zip
   cd mythara-engine-v1.0.0
   ```

2. **Verify signatures**
   ```bash
   gpg --import forensic_public_key.asc
   gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
   ```
   
   Expected: `Good signature from "Mythara Engine <Mythara.Engine@yahoo.com>"`

3. **Verify checksums**
   ```bash
   cd manifest && sha256sum -c checksums.sha256
   ```
   
   Expected: All files show `OK`

4. **Review documentation**
   - Start with `README.md`
   - Check `INSTALL.md` for their deployment type (Docker/native/air-gapped)
   - Review `LICENSE.md` for usage restrictions
   - Review `COPYRIGHT.md` for IP ownership and protected components

---

## Licensing Process

### Step 1: NDA Execution

Company signs mutual NDA (template needed — `Legal/NDA_Mutual_Template.md` is not present in this archive)

### Step 2: Evaluation Period

- 30 days to test the package
- Run validation suite
- Review documentation
- Assess integration requirements

### Step 3: License Selection

**Development License** — Internal testing  
**Enterprise License** — Production deployment (100K req/month)  
**Sovereign License** — Air-gapped, government, defense + source code escrow

See `Commercial/Pricing_Tiers.md`

### Step 4: Pilot SOW (Optional)

4-8 week scoped integration with success metrics (template in `Legal/`)

### Step 5: Production Deployment

Company deploys using `INSTALL.md` instructions

---

## Support for Licensed Companies

**Herbert Velez Jr.** *(Mythara Labs LLC — formation filing attempted with the Colorado SOS on 2026-09-27 — not confirmed; entity not yet formed)*

- **Email:** mytharalabs@yahoo.com
- **PGP:** `571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C`
- **Response Time:** best effort — no SLAs currently offered

---

## Next Actions

### Immediately

- [ ] Decide on distribution method (GitHub private repo vs direct email)
- [ ] Test package yourself: extract and run verify.ps1/verify.sh
- [ ] Review `GitHub_Release_Package/GITHUB_RELEASE_GUIDE.md` if using GitHub

### Before Sending to Companies

- [ ] Ensure NDA template is updated with your details (`Legal/NDA_Mutual_Template.md`)
- [ ] Confirm pricing in `Commercial/### Pricing Tiers.txt`
- [ ] Test package extraction and verification on Windows and Linux

### When Company Requests Access

1. Execute mutual NDA
2. Send ZIP or grant GitHub repository access
3. Provide SHA256 hash for verification
4. Follow up in 1 week to answer questions
5. Schedule pilot scoping call after evaluation

---

## Files Created for You

| File | Purpose |
|------|---------|
| `mythara-engine-v1.0.0.zip` | Complete licensing package (0.7 MB) — **not present in this archive** (hash file only) |
| `mythara-engine-v1.0.0.zip.sha256` | SHA256 hash for verification |
| `create_release_zip.ps1` | Script to rebuild package for future versions |
| `GitHub_Release_Package/README.md` | Main documentation for companies |
| `GitHub_Release_Package/LICENSE.md` | Proprietary license terms |
| `GitHub_Release_Package/INSTALL.md` | Deployment instructions |
| `GitHub_Release_Package/GITHUB_RELEASE_GUIDE.md` | How to upload to GitHub |

---

## Rebuilding for Future Versions

When you update the archive:

```powershell
# Update version number in the script
.\create_release_zip.ps1 -Version "1.1.0"

# New ZIP will be created: mythara-engine-v1.1.0.zip
# New hash will be saved: mythara-engine-v1.1.0.zip.sha256
```

---

**Package contents as assembled November 2025 (historical snapshot). Nothing here is currently offered for sale, and no payment path exists.**
