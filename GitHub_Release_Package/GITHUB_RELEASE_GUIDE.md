# Mythara Engine — GitHub Release Guide

**Version:** 1.0.0  
**Date:** November 2, 2025  
**Repository:** Private (NDA-protected)

---

## Overview

This guide explains how to create a GitHub release with the licensing ZIP package that companies can download after signing an NDA.

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [github.com](https://github.com)
2. Click **New Repository** (+ icon, top right)
3. Configure:
   - **Repository name:** `mythara-engine`
   - **Description:** "Mythara Engine — Evaluation Package (Private/Proprietary)"
   - **Visibility:** ☑ **Private**
   - **Initialize:** ☐ Do NOT add README (we have our own)
4. Click **Create repository**

### Option B: Using GitHub CLI

```powershell
# Install GitHub CLI (if not already installed)
# Download from: https://cli.github.com/

# Authenticate
gh auth login

# Create private repository (replace YOUR_USERNAME with your GitHub username or org)
gh repo create YOUR_USERNAME/mythara-engine --private --description "Mythara Engine — Evaluation Package (Proprietary)"
```

---

## Step 2: Prepare Local Repository

```powershell
# Navigate to archive
cd C:\Users\HVele\OneDrive\Desktop\Mythara_Archive

# Initialize git (if not already done)
git init

# Add files
git add .

# Create initial commit
git commit -m "Initial release: Mythara Engine v1.0.0"

# Add remote (replace with your GitHub username/org)
git remote add origin https://github.com/YOUR_USERNAME/mythara-engine.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: Create Release ZIP

### PowerShell Script to Build ZIP

```powershell
# Set variables
$version = "1.0.0"
$releaseDir = "mythara-engine-v$version"
$zipName = "mythara-engine-v$version.zip"

# Create staging directory
New-Item -ItemType Directory -Path $releaseDir -Force

# Copy essential files
Copy-Item -Path "GitHub_Release_Package\README.md" -Destination "$releaseDir\"
Copy-Item -Path "GitHub_Release_Package\LICENSE.md" -Destination "$releaseDir\"
Copy-Item -Path "GitHub_Release_Package\INSTALL.md" -Destination "$releaseDir\"

# Copy core files
Copy-Item -Path "core\" -Destination "$releaseDir\core\" -Recurse
Copy-Item -Path "docs\" -Destination "$releaseDir\docs\" -Recurse
Copy-Item -Path "tests\" -Destination "$releaseDir\tests\" -Recurse
Copy-Item -Path "Evidence\" -Destination "$releaseDir\Evidence\" -Recurse
Copy-Item -Path "Commercial\" -Destination "$releaseDir\Commercial\" -Recurse
Copy-Item -Path "Legal\" -Destination "$releaseDir\Legal\" -Recurse
Copy-Item -Path "manifest\" -Destination "$releaseDir\manifest\" -Recurse
Copy-Item -Path "validate_suite\" -Destination "$releaseDir\validate_suite\" -Recurse

# Copy verification files
Copy-Item -Path "forensic_manifest.json" -Destination "$releaseDir\"
Copy-Item -Path "forensic_manifest.json.asc" -Destination "$releaseDir\"
Copy-Item -Path "forensic_public_key.asc" -Destination "$releaseDir\"

# Create ZIP
Compress-Archive -Path $releaseDir -DestinationPath $zipName -Force

# Cleanup staging directory
Remove-Item -Path $releaseDir -Recurse -Force

Write-Host "✅ Created $zipName"
Write-Host "📦 Size: $((Get-Item $zipName).Length / 1MB) MB"
```

Save this as `create_release_zip.ps1` and run it:

```powershell
.\create_release_zip.ps1
```

---

## Step 4: Create GitHub Release

### Option A: GitHub Web Interface

1. Go to your repository: `https://github.com/YOUR_USERNAME/mythara-engine`
2. Click **Releases** (right sidebar)
3. Click **Draft a new release**
4. Configure release:
   - **Tag version:** `v1.0.0`
   - **Target:** `main` branch
   - **Release title:** `Mythara Engine v1.0.0 — Release Package`
   - **Description:**

```markdown
# Mythara Engine v1.0.0

**Release Date:** November 2, 2025  
**Manifest ID:** ME-archive-0001  
**License:** Proprietary (NDA required)

## What's New

Initial release package with:
- ✅ Validation suite (determinism tests, leakage probes, integrity audits)
- ✅ PGP-signed manifests and checksums
- ✅ Docker container with reproducible builds
- ✅ Proposed licensing templates

## Verification

**PGP Fingerprint:** `571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C`

Verify integrity:
```bash
gpg --import forensic_public_key.asc
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
```

## Installation

See `INSTALL.md` for deployment instructions.

## Licensing

This software is proprietary. Contact mytharalabs@yahoo.com for licensing conversations.

**Proposed license tiers (draft terms, not yet in effect):**
- Development (internal testing)
- Enterprise (production)
- Sovereign (air-gapped)
```

5. **Attach ZIP:** Drag `mythara-engine-v1.0.0.zip` to the upload area
6. Click **Publish release**

### Option B: GitHub CLI

```powershell
# Create release with ZIP attached
gh release create v1.0.0 `
  --title "Mythara Engine v1.0.0 — Release Package" `
  --notes "Mythara Engine evaluation package. Proprietary license; contact mytharalabs@yahoo.com for licensing conversations." `
  mythara-engine-v1.0.0.zip

Write-Host "✅ Release published!"
```

---

## Step 5: Grant Repository Access

Since the repository is private, you'll need to invite companies after they sign NDAs.

### Add Collaborators

**GitHub Web Interface:**
1. Go to repository **Settings**
2. Click **Collaborators and teams**
3. Click **Add people**
4. Enter company contact's GitHub username
5. Set role to **Read** (view only)

**GitHub CLI:**
```powershell
gh api repos/YOUR_USERNAME/mythara-engine/collaborators/THEIR_USERNAME -X PUT -f permission=pull
```

---

## Step 6: Company Download Instructions

Send these instructions to licensed companies:

---

### **For Companies with GitHub Access**

1. **Accept Repository Invitation**
   - Check your email for GitHub invitation
   - Click **Accept Invitation**

2. **Download Release Package**
   - Go to: `https://github.com/YOUR_USERNAME/mythara-engine/releases`
   - Download `mythara-engine-v1.0.0.zip`

3. **Verify Integrity**

```bash
# Extract ZIP
unzip mythara-engine-v1.0.0.zip
cd mythara-engine-v1.0.0

# Import PGP key
gpg --import forensic_public_key.asc

# Verify signatures
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
gpg --verify manifest/checksums.sha256.asc manifest/checksums.sha256

# Verify checksums
cd manifest && sha256sum -c checksums.sha256 && cd ..
```

4. **Follow Installation Guide**
   - See `INSTALL.md` for deployment options
   - Review `README.md` for feature overview
   - Check `LICENSE.md` for usage restrictions

---

### **For Companies Without GitHub Access**

If a company doesn't use GitHub, send the ZIP directly:

1. **Upload ZIP to Secure File Sharing**
   - Use Box, Dropbox Business, or secure email
   - Include SHA256 hash for verification:

```powershell
# Calculate ZIP hash
(Get-FileHash -Algorithm SHA256 mythara-engine-v1.0.0.zip).Hash
```

2. **Send Instructions**

```
Subject: Mythara Engine v1.0.0 — License Package

Attached is the Mythara Engine licensing package.

Verify integrity:
- File: mythara-engine-v1.0.0.zip
- SHA256: [hash from above]

After extraction, follow verification steps in README.md.

Questions? Contact mytharalabs@yahoo.com
```

---

## Step 7: Automate Future Releases

Create `.github/workflows/release.yml`:

```yaml
name: Create Release Package

on:
  push:
    tags:
      - 'v*'

jobs:
  build-release:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build ZIP
        shell: powershell
        run: |
          $version = "${{ github.ref_name }}" -replace 'v',''
          $releaseDir = "mythara-engine-v$version"
          
          New-Item -ItemType Directory -Path $releaseDir -Force
          
          Copy-Item -Path "GitHub_Release_Package\*" -Destination "$releaseDir\" -Recurse
          Copy-Item -Path "core\","docs\","tests\","Evidence\","Commercial\","Legal\","manifest\","validate_suite\" -Destination "$releaseDir\" -Recurse
          Copy-Item -Path "forensic*","README.md" -Destination "$releaseDir\"
          
          Compress-Archive -Path $releaseDir -DestinationPath "mythara-engine-v$version.zip"
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: mythara-engine-v*.zip
          body: "Mythara Engine release. NDA required."
```

Now releases happen automatically when you push a tag:

```powershell
git tag v1.0.1
git push origin v1.0.1
```

---

## Troubleshooting

**Issue: "Permission denied" when pushing**

Solution:
```powershell
# Generate Personal Access Token
# GitHub → Settings → Developer settings → Personal access tokens → Generate new token
# Scopes needed: repo (full control)

# Use token as password when prompted
git push origin main
```

**Issue: "Repository not found"**

Solution: Verify repository name and ensure it's private.

**Issue: "Release ZIP too large"**

Solution: Exclude unnecessary files:
```powershell
# Don't include:
# - archive/DEPRECATED/
# - Printable Timestamped Forensic Report/ (create separately)
# - Large binary files (offer as separate download)
```

---

## Next Steps

1. ✅ Repository created on GitHub (private)
2. ✅ Release ZIP built with all necessary files
3. ✅ Release published with verification instructions
4. ✅ Company access workflow documented

**Repository ready for NDA-protected distribution!**
