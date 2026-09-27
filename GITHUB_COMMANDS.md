# GitHub Upload — Command Cheat Sheet

**Package:** mythara-engine-v1.0.0.zip (0.7 MB)  
**SHA256:** 94B45D271F56B9CD06C9C1323AA09949CF81A9D9F1D951E20A7EE42180453DA2

> **Note (Sept 2026):** `mythara-engine-v1.0.0.zip` is **not present in this archive** (only its hash file, `mythara-engine-v1.0.0.zip.sha256`). These are template instructions from November 2025 — adapt them to whatever package you actually distribute.

---

## Quick Upload (5 Commands)

```powershell
# 1. Create private repo on GitHub
gh repo create mythara-engine --private

# 2. Initialize git
git init
git add .
git commit -m "Mythara Engine v1.0.0"

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/mythara-engine.git
git branch -M main
git push -u origin main

# 4. Create release with ZIP
gh release create v1.0.0 --title "Mythara Engine v1.0.0" mythara-engine-v1.0.0.zip

# 5. Invite licensee (after NDA)
gh api repos/YOUR_USERNAME/mythara-engine/collaborators/THEIR_USERNAME -X PUT -f permission=pull
```

**Done!** Licensees can now download from: `https://github.com/YOUR_USERNAME/mythara-engine/releases`

---

## Manual Upload (Web Interface)

1. **Create repo:** github.com → New Repository → Private → Create
2. **Push code:** Follow commands shown on GitHub after repo creation
3. **Create release:** Releases → Draft new release → v1.0.0 → Attach ZIP → Publish
4. **Invite users:** Settings → Collaborators → Add people → Read access

---

## Verify Upload Success

```powershell
# Check release exists
gh release view v1.0.0

# Expected output:
# title: Mythara Engine v1.0.0
# assets: mythara-engine-v1.0.0.zip (0.7 MB)
```

---

**Full instructions:** See `GITHUB_SETUP_QUICKSTART.md`
