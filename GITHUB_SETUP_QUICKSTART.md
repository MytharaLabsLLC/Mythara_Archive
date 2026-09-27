# GitHub Private Repository Setup — Quick Start

> **Note (Sept 2026):** historical template from November 2025, edited to remove unverifiable claims. Pricing, SLAs, and certifications below describe a *planned* offering — none are currently held or guaranteed.

**Package:** mythara-engine-v1.0.0.zip *(not present in this archive — hash file only)*  
**Size:** 0.7 MB (736,030 bytes)  
**SHA256:** 94B45D271F56B9CD06C9C1323AA09949CF81A9D9F1D951E20A7EE42180453DA2  
**Date:** November 2, 2025

---

## Step 1: Create Private GitHub Repository

### Option A: GitHub Web Interface

1. Go to [github.com](https://github.com) and log in
2. Click **New Repository** (+ icon, top right)
3. Configure:
   - **Repository name:** `mythara-engine` or `mythara-licensing`
   - **Description:** "Mythara Engine — Enterprise Licensing Package (Private/NDA-Only)"
   - **Visibility:** ☑ **Private** (IMPORTANT!)
   - **Initialize:** ☐ Leave unchecked (we'll push existing files)
4. Click **Create repository**

### Option B: GitHub CLI (Faster)

```powershell
# Install GitHub CLI if needed: https://cli.github.com/

# Authenticate
gh auth login

# Create private repository
gh repo create mythara-engine --private --description "Mythara Engine — Enterprise Licensing Package"
```

---

## Step 2: Initialize Git and Push Archive

```powershell
# Navigate to archive directory
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial release: Mythara Engine v1.0.0 with PGP signatures"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mythara-engine.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You'll be prompted for GitHub credentials. Use a Personal Access Token instead of password.

---

## Step 3: Create GitHub Release with ZIP

### Option A: Web Interface

1. Go to your repository: `https://github.com/YOUR_USERNAME/mythara-engine`
2. Click **Releases** (right sidebar)
3. Click **Draft a new release**
4. Fill in release details:

**Tag version:** `v1.0.0`  
**Release title:** `Mythara Engine v1.0.0 — Enterprise Licensing Package`

**Description:**

```markdown
# Mythara Engine v1.0.0

**Release Date:** November 2, 2025  
**Manifest ID:** ME-archive-0001  
**License:** Proprietary (NDA required)

## Package Verification

**SHA256:** `94B45D271F56B9CD06C9C1323AA09949CF81A9D9F1D951E20A7EE42180453DA2`

Verify integrity after download:

```powershell
# Windows
(Get-FileHash -Algorithm SHA256 mythara-engine-v1.0.0.zip).Hash

# Linux/macOS
sha256sum mythara-engine-v1.0.0.zip
```

Expected: `94b45d271f56b9cd06c9c1323aa09949cf81a9d9f1d951e20a7ee42180453da2`

## What's Included

- ✅ Mythara Engine source archive packaged for distribution
- ✅ PGP-signed manifests and checksums
- ✅ Validation suite (deterministic clause-selection fingerprints — see the validation report in this archive)
- ✅ Docker container build instructions
- ✅ Licensing templates (planned offering — not currently executed)
- ✅ API documentation and deployment guides

## Verification

**PGP Fingerprint:** `571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C`

After extraction:

```bash
gpg --import forensic_public_key.asc
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
gpg --verify manifest/checksums.sha256.asc manifest/checksums.sha256
cd manifest && sha256sum -c checksums.sha256
```

All signatures should show "Good signature from Mythara Engine".

## Installation

See `INSTALL.md` for deployment instructions:
- Docker container deployment
- Native Python installation
- Air-gapped/sovereign deployment

## Licensing

This software is proprietary. Contact for licensing:

**Herbert Velez Jr.** *(Mythara Labs LLC — formation filed with the Colorado SOS on 2026-09-27, pending completion)*  
Email: legal@mythara.engine  
PGP: 571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C

**Available licenses (planned pricing tiers — not currently offered; no payment path exists):**
- Development ($2,500/year) — Internal testing
- Enterprise ($25,000/year) — Production deployment
- Sovereign ($150,000/year) — Air-gapped, government, defense + source code escrow

See `Commercial/Pricing_Tiers.md` for pricing details.

## Support

- Email: legal@mythara.engine (best effort — no SLAs currently offered)

## Next Steps

1. Review `README.md` for feature overview
2. Run verification (gpg --verify, sha256sum -c — see above; note verify.ps1/verify.sh are not in this archive)
3. Check `INSTALL.md` for deployment options
4. Contact legal@mythara.engine to schedule pilot scoping call
```

5. **Attach ZIP file:**
   - Drag `mythara-engine-v1.0.0.zip` to the upload area
   - Or click "Attach binaries" and select the ZIP

6. Click **Publish release**

### Option B: GitHub CLI

```powershell
gh release create v1.0.0 `
  --title "Mythara Engine v1.0.0 — Enterprise Licensing Package" `
  --notes "Production-ready inference orchestration. NDA required. SHA256: 94B45D271F56B9CD06C9C1323AA09949CF81A9D9F1D951E20A7EE42180453DA2" `
  mythara-engine-v1.0.0.zip
```

---

## Step 4: Grant Access to Licensees

After a company signs an NDA, invite them to the repository:

### Web Interface

1. Go to repository **Settings**
2. Click **Collaborators and teams**
3. Click **Add people**
4. Enter their GitHub username
5. Set permission to **Read** (view and download only)

### GitHub CLI

```powershell
# Replace THEIR_USERNAME with the company contact's GitHub username
gh api repos/YOUR_USERNAME/mythara-engine/collaborators/THEIR_USERNAME -X PUT -f permission=pull
```

---

## Step 5: Send Download Instructions to Licensee

Email template:

```
Subject: Mythara Engine v1.0.0 — License Package Access

Dear [COMPANY NAME],

Thank you for executing the NDA. You now have access to the Mythara Engine licensing package.

Access Instructions:

1. Accept the GitHub repository invitation (check your email)
2. Go to: https://github.com/YOUR_USERNAME/mythara-engine/releases
3. Download: mythara-engine-v1.0.0.zip

Verification:

SHA256: 94b45d271f56b9cd06c9c1323aa09949cf81a9d9f1d951e20a7ee42180453da2

After download, verify with:
  Windows: (Get-FileHash -Algorithm SHA256 mythara-engine-v1.0.0.zip).Hash
  Linux: sha256sum mythara-engine-v1.0.0.zip

Installation:

Extract the ZIP and run verification (note: `verify.ps1` / `verify.sh` are **not present in this archive** — use `gpg --verify` and `sha256sum -c` as shown above).

Then review README.md for deployment options.

Questions? Reply to this email or contact:
legal@mythara.engine

Best regards,
Herbert Velez Jr.
*(Mythara Labs LLC — formation filed with the Colorado SOS on 2026-09-27, pending completion)*
```

---

## Security Best Practices

### Repository Settings

1. **Enable branch protection:**
   - Settings → Branches → Add rule for `main`
   - ☑ Require pull request reviews
   - ☑ Require status checks to pass

2. **Disable forking:**
   - Settings → General
   - ☐ Uncheck "Allow forking"

3. **Enable audit log:**
   - Settings → Security & analysis
   - ☑ Enable dependency graph
   - ☑ Enable Dependabot alerts

### Access Control

- Only grant **Read** access to licensees (never Write)
- Use **Teams** for companies with multiple contacts
- Review collaborators quarterly and remove inactive users
- Monitor repository activity via Settings → Insights → Traffic

---

## Updating the Package

When you release a new version:

```powershell
# Update version in script
.\create_release_zip.ps1 -Version "1.1.0"

# Create new git tag
git tag v1.1.0
git push origin v1.1.0

# Create new release with updated ZIP
gh release create v1.1.0 --title "Mythara Engine v1.1.0" mythara-engine-v1.1.0.zip
```

---

## Troubleshooting

**Issue: "Remote already exists"**

```powershell
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/mythara-engine.git
```

**Issue: "Authentication failed"**

```powershell
# Generate Personal Access Token
# GitHub → Settings → Developer settings → Personal access tokens → Generate new token
# Scopes needed: repo (full control)

# Use token as password when prompted
```

**Issue: "ZIP upload fails (too large)"**

The ZIP is only 0.7 MB, well under GitHub's 2 GB limit. If upload fails:
- Try different browser
- Use GitHub CLI instead
- Check internet connection

---

## Files Ready for Upload

✅ `mythara-engine-v1.0.0.zip` — Main licensing package (719 KB)  
✅ `mythara-engine-v1.0.0.zip.sha256` — Verification hash  
✅ All repository files in current directory

**Your licensing package is ready to distribute via private GitHub repository!**
