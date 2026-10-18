# Mythara Engine - Quick Deploy to Railway
**Copyright © 2026 Mythara Labs LLC. All rights reserved.**

## ⚡ Deploy in 5 Minutes

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login & Initialize

```bash
railway login
# Opens browser for authentication

cd /workspaces/Mythara_Archive
railway init
# Choose: "Create new project"
# Name: mythara-engine-api
```

### Step 3: Set Environment Variables

```bash
# CRITICAL SECURITY: CORS allowed origins (REQUIRED in production)
# Replace with your actual frontend domains (comma-separated)
railway variables set MYTHARA_ALLOWED_ORIGINS=https://app.yourcompany.com,https://www.yourcompany.com

# Enable pilot paywall
railway variables set MYTHARA_PILOT_PAYWALL=true

# Your Stripe Payment Link
railway variables set MYTHARA_PILOT_PURCHASE_URL=https://buy.stripe.com/28E9AU85SfFCa5MbucgjC01

# For testing: force unlock (set to false after wiring webhook)
railway variables set MYTHARA_PILOT_FORCE_UNLOCK=true

# Placeholder webhook secret (get real one after deployment)
railway variables set STRIPE_WEBHOOK_SECRET=whsec_placeholder

# Port configuration
railway variables set PORT=8000
```

**⚠️ CRITICAL:** `MYTHARA_ALLOWED_ORIGINS` is **REQUIRED** in production. The API will refuse to start without it to prevent CORS security vulnerabilities.

### Step 4: Set Dockerfile Path

Railway needs to know which Dockerfile to use:

```bash
# Tell Railway to use the API Dockerfile
railway variables set DOCKERFILE_PATH=core/Dockerfile.api
```

Or create a `railway.toml` file:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "core/Dockerfile.api"

[deploy]
startCommand = "python core/source_proprietary/main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

### Step 5: Deploy

```bash
railway up
# This builds and deploys your container
```

### Step 6: Get Your Public URL

```bash
# Generate a public domain
railway domain

# If domain already exists, check it:
railway status

# Your API will be at:
# https://mythara-engine-production.up.railway.app
```

### Step 7: Test Deployment

```bash
# Replace with your actual Railway URL
export API_URL="https://your-app.up.railway.app"

# Health check
curl $API_URL/health

# Pilot status
curl $API_URL/v1/pilot/status
# Should return: access_granted: true (because force unlock is on)
```

### ~~Step 8: Wire Stripe Webhook~~ — DISABLED (historical)

> **⚠️ DISABLED — webhooks deleted, no fulfillment path. Do not follow these steps.** All Stripe webhooks (Test and Live) were deleted from the account. The instructions below are historical — the webhook endpoints no longer exist and re-creating them requires new account work. Do not rely on or share these steps.

1. **Go to Stripe Dashboard → Developers → Webhooks**
2. **Add endpoint:**
   - URL: `https://your-app.up.railway.app/api/webhooks/stripe`
   - Events: Select `checkout.session.completed`
3. **Reveal signing secret** → Copy `whsec_xxx`
4. **Update Railway:**
   ```bash
   railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxx
   railway up  # Redeploy
   ```

### Step 9: Disable Force Unlock (Production Ready)

```bash
railway variables set MYTHARA_PILOT_FORCE_UNLOCK=false
railway up  # Redeploy
```

### Step 10: Update Success Page & Pilot Package

1. Update `pilot_package/success.html` line 71:
   ```html
   <code id="api-endpoint">https://your-app.up.railway.app</code>
   ```

2. Update `pilot_package/.env.example` with your Railway URL

3. Create GitHub release with updated package

---

## Alternative: Deploy to Render.com

### Step 1: Create Account
Go to https://render.com and sign up

### Step 2: New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Select `Mythara_Archive`

### Step 3: Configure
- **Name:** `mythara-engine-api`
- **Region:** Choose closest to your customers
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** Docker
- **Dockerfile Path:** `core/Dockerfile.api`
- **Instance Type:** Free (or Starter for production)

### Step 4: Environment Variables
Add these in Render dashboard:
```
MYTHARA_PILOT_PAYWALL=true
MYTHARA_PILOT_PURCHASE_URL=https://buy.stripe.com/28E9AU85SfFCa5MbucgjC01
MYTHARA_PILOT_FORCE_UNLOCK=true
STRIPE_WEBHOOK_SECRET=whsec_placeholder
PORT=8000
```

### Step 5: Deploy
Click "Create Web Service" - Render builds & deploys automatically

Your URL: `https://mythara-engine-api.onrender.com`

---

## Which to Choose?

### Railway
- ✅ Faster deploys
- ✅ Better CLI
- ✅ $5/month after free trial
- ✅ Easier environment management

### Render
- ✅ Free tier (spins down after 15 min idle)
- ✅ More mature platform
- ✅ Good for production
- ✅ Auto-deploy on git push

**For pilot testing:** Railway (easier)
**For production:** Render (more reliable free tier) or Railway paid

---

## Troubleshooting

### Build fails
```bash
# Check logs
railway logs

# Common issues:
# - Wrong Dockerfile path → Check railway.toml or DOCKERFILE_PATH
# - Missing requirements.txt → Verify core/source_proprietary/requirements-api.txt exists
```

### API not accessible
```bash
# Check if service is running
railway status

# View logs
railway logs --follow

# Check domain
railway domain
```

### Webhook fails
```bash
# Check webhook logs in Stripe Dashboard
# Common issues:
# - Wrong URL in Stripe → Should match Railway/Render URL exactly
# - Wrong event selected → Must be "checkout.session.completed"
# - Invalid webhook secret → Copy from Stripe, no extra spaces
```

---

## Next Steps After Deployment

1. ✅ Copy your Railway/Render URL
2. ✅ Update success.html with real API URL
3. ✅ Create GitHub Pages for success page
4. ✅ Create GitHub Release with pilot package
5. ~~✅ Update Stripe Payment Link redirect URL~~ — disabled: webhooks deleted
6. ~~✅ Test full flow with $0.50 test purchase~~ — disabled: no fulfillment path

**Ready to deploy?** Run the commands above!
