# How to Use the Mythara API - Simple Instructions

Copyright © 2025 Herbert Velez Jr. All rights reserved.

---

## Step 1: Start the Server

Open PowerShell and run:

```powershell
cd "c:\Users\Mythara\Desktop\Clone Repo Mythara\Mythara_Archive\core\source_proprietary"
py main.py
```

**You should see:**
```
INFO: Mythara Engine API - Starting
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Keep this window open** - the server needs to stay running.

---

## Step 2: Test the API (Open a NEW PowerShell window)

### Option A: Using the Test Script

> **Note (Sept 2026):** `test_soul_api.py` is **not present in this archive** — this step is from an earlier draft and will not work as written. Use Option B below instead.

```powershell
cd "c:\Users\Mythara\Desktop\Clone Repo Mythara\Mythara_Archive"
py test_soul_api.py
```

**Done!** You'll see the soul status output.

---

### Option B: Using curl (if you want to learn the manual way)

Open a **NEW** PowerShell window (keep the server running in the first one).

**Check Soul Status (Mythic Framing):**
```powershell
curl.exe http://127.0.0.1:8000/v1/soul/status -H "Authorization: Bearer dev_test_key_001"
```

**Check Soul Status (Industry Framing):**
```powershell
curl.exe "http://127.0.0.1:8000/v1/soul/status?frame=industry" -H "Authorization: Bearer dev_test_key_001"
```

---

## Understanding the Parts

### What is `127.0.0.1:8000`?
- `127.0.0.1` = Your own computer (localhost)
- `8000` = The port number where the API is running

### What is `dev_test_key_001`?
This is your **API key** - like a password that lets you access the API.

**Available API Keys:** *(sample development keys from the original tutorial — not issued credentials)*
1. `dev_test_key_001` - Development (basic access)
2. `ent_prod_key_001` - Enterprise (more features)
3. `sov_airgap_key_001` - Sovereign (full access)

### What is `-H "Authorization: Bearer dev_test_key_001"`?
- `-H` means "add a header"
- Headers are like labels on a package that tell the server who you are
- `Authorization: Bearer dev_test_key_001` = "I'm authorized with this key"

### What is `?frame=industry`?
- The `?` starts extra options (called query parameters)
- `frame=industry` tells the API to use business-friendly language instead of mythic terms

---

## Common Issues

### "Connection refused" or "Couldn't connect"
**Solution:** Make sure the server is running (Step 1). Check the first PowerShell window.

### "Invalid API key"
**Solution:** Make sure you typed the key exactly: `dev_test_key_001` (all lowercase, underscores, not dashes)

### Server shuts down immediately
**Solution:** Use the test script instead: `py test_soul_api.py`

---

## What You're Checking

**Soul Status** shows:
- `S_t` - Soul proportion (0 to 1, higher = better emotional state)
- `emotion_features` - Current emotional metrics (valence, arousal, connectedness, etc.)
- `dynamics` - How fast the soul state changes (r, u, d parameters)
- `integrity_hash` - SHA-256 cryptographic proof (like a fingerprint)

---

## Quick Reference Card

| What I Want | Command |
|-------------|---------|
| Start server | `py main.py` (in core/source_proprietary folder) |
| Test API (easy) | `py test_soul_api.py` (in main folder) |
| Check soul status | `curl.exe http://127.0.0.1:8000/v1/soul/status -H "Authorization: Bearer dev_test_key_001"` |
| Use business terms | Add `?frame=industry` to the URL |
| Stop server | Press `CTRL+C` in the server window |

---

## Next Steps

Once you're comfortable with the basics, you can:
1. Try different endpoints (see README.md)
2. Use a different API key for more features
3. Build your own scripts that call the API
4. Deploy to a real server (not just localhost)

---

**Need help?** Check the full README.md or the API documentation at:
http://127.0.0.1:8000/api/docs (when server is running)
