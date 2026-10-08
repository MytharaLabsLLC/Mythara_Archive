# Mythara Engine - Pilot Self-Hosted Deployment Guide

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

> **⚠️ HISTORICAL DESIGN (November 2025) — voice-standard pass Sept 2026.** This guide describes a pilot offering as it was planned. There is currently **no live payment path** (all Stripe webhooks were deleted), **no hosted pilot service** is offered, and the pilot license key, Docker image reference, and deployment targets below are **unverified in this archive**. Treat this as planning material, not current instructions.

---

## 🎯 Pilot Tier = Self-Hosted Only

**What You Get for $49:**
- ✅ Docker container with full Mythara Engine
- ✅ API documentation & SDK access
- ✅ License key for pilot evaluation
- ✅ Community support (GitHub issues)
- ✅ One pilot per business domain

**What You DON'T Get:**
- ❌ Hosted API service on Mythara's infrastructure
- ❌ 24/7 managed hosting
- ❌ SLA guarantees
- ❌ Priority support

**Why Self-Hosted?**
You deploy Mythara on YOUR infrastructure (Railway, AWS, Azure, etc.) and YOU pay the hosting costs. This keeps the pilot tier affordable at $49 while giving you full control over your deployment.

---

## 🚀 Quick Start (Deploy in 10 Minutes)

### Prerequisites
- Business email address (no free providers like gmail.com)
- Payment of $49 pilot fee via Stripe
- Docker installed locally OR hosting platform account (Railway/AWS/Azure)

### ~~Step 1: Purchase Pilot License~~ — DISABLED (placeholder)

> **DISABLED — webhooks deleted, no fulfillment path. Do not share.** The link below is an unwired placeholder (`your-pilot-link`), not a real payment page, and the receipt/key delivery it promises does not exist. URL text preserved for deactivation reference only.

Visit: https://buy.stripe.com/your-pilot-link

~~After payment, you'll receive:~~ — no live payment path exists:
- License key (email)
- Docker image access
- This deployment guide

### Step 2: Choose Your Hosting Platform

**Option A: Railway (Recommended for Beginners)**
- Free tier: $5/month credit (~50K API calls)
- One-click deploy
- Automatic HTTPS
- Cost: ~$5-20/month depending on usage

**Option B: AWS (Recommended for Enterprises)**
- Free tier: 1M requests/month free
- Full control
- Auto-scaling
- Cost: ~$10-50/month depending on usage

**Option C: Azure (Enterprise)**
- Enterprise integration
- Active Directory support
- Cost: ~$15-100/month

**Option D: Local Docker (Development Only)**
- Free
- Run on your laptop
- Not suitable for production

---

## 📦 Deployment Methods

### Method 1: Railway (Easiest)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Clone this repo or use your pilot download
git clone https://github.com/herbievelezjr/Mythara_Archive.git
cd Mythara_Archive

# Initialize Railway project
railway init

# Set your license key (received via email)
railway variables set MYTHARA_LICENSE_KEY=your_license_key_here

# Deploy
railway up

# Get your deployment URL
railway open
```

**Your API will be live at:** `https://your-app.railway.app`

**Monthly Cost:** $5-20 (you pay Railway directly)

---

### Method 2: Docker (Local Development)

```bash
# Pull the Mythara Engine image
# NOTE: image reference from Nov 2025 draft — no published image verified from this archive
docker pull herbievelezjr/mythara-engine:latest

# Run locally
docker run -d \
  -p 8000:8000 \
  -e MYTHARA_LICENSE_KEY=your_license_key_here \
  --name mythara-engine \
  herbievelezjr/mythara-engine:latest

# Access API
curl http://localhost:8000/health
```

**Access at:** `http://localhost:8000`

**Cost:** Free (local only, not production-ready)

---

### Method 3: AWS ECS (Production)

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Login to AWS
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name mythara-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://aws-task-definition.json

# Deploy service
aws ecs create-service \
  --cluster mythara-cluster \
  --service-name mythara-service \
  --task-definition mythara-engine \
  --desired-count 1 \
  --launch-type FARGATE
```

**Your API will be live at:** Your AWS load balancer URL

**Monthly Cost:** ~$10-50 (you pay AWS directly)

---

### Method 4: Azure Container Instances

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name mythara-rg --location eastus

# Deploy container
az container create \
  --resource-group mythara-rg \
  --name mythara-engine \
  --image herbievelezjr/mythara-engine:latest \
  --dns-name-label mythara-your-company \
  --ports 8000 \
  --environment-variables MYTHARA_LICENSE_KEY=your_license_key_here

# Get URL
az container show --resource-group mythara-rg --name mythara-engine --query ipAddress.fqdn
```

**Your API will be live at:** `http://mythara-your-company.eastus.azurecontainer.io:8000`

**Monthly Cost:** ~$15-100 (you pay Azure directly)

---

## 🔧 Configuration

### Required Environment Variables

```bash
# Your pilot license key (required)
MYTHARA_LICENSE_KEY=your_license_key_here

# Optional: Employee count for rate limiting
MYTHARA_EMPLOYEE_COUNT=50

# Optional: Custom port (default: 8000)
PORT=8000

# Optional: Enable debug logging
MYTHARA_DEBUG=true
```

### Optional: Custom Configuration

Create a `.env` file in your deployment:

```bash
# Pilot Configuration
MYTHARA_LICENSE_KEY=your_license_key_here
MYTHARA_EMPLOYEE_COUNT=50

# API Configuration
PORT=8000
MYTHARA_DEBUG=false

# Database (optional, uses in-memory by default)
DATABASE_URL=postgresql://mythara_app:CHANGEME_SET_VIA_ENV@localhost:5432/mythara

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379
```

---

## 📊 Monitoring Your Deployment

### Health Check

```bash
curl https://your-deployment-url.com/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-16T12:00:00Z",
  "license": "pilot",
  "uptime_seconds": 3600
}
```

### API Documentation

Visit: `https://your-deployment-url.com/api/docs`

Interactive Swagger UI for testing endpoints.

### Usage Metrics

Railway Dashboard: https://railway.app/dashboard
AWS CloudWatch: https://console.aws.amazon.com/cloudwatch
Azure Monitor: https://portal.azure.com/#blade/Microsoft_Azure_Monitoring

---

## 💰 Cost Breakdown

### Railway
- Free tier: $5/month credit
- Beyond free: ~$0.10 per 1K API calls
- **Estimated monthly cost:**
  - Light usage (<50K calls): $5-10
  - Medium usage (50-200K calls): $10-30
  - Heavy usage (200K+ calls): $30-100

### AWS
- Free tier: 1M requests/month
- Beyond free: $0.20 per 1M requests
- **Estimated monthly cost:**
  - Light usage: $0-10
  - Medium usage: $10-30
  - Heavy usage: $30-100

### Azure
- No free tier for containers
- ~$0.0025 per 1K requests
- **Estimated monthly cost:**
  - Light usage: $15-30
  - Medium usage: $30-60
  - Heavy usage: $60-150

**You pay your hosting provider directly. Mythara does not charge beyond the $49 pilot fee.**

---

## 🆙 Upgrading to Enterprise Hosted *(planned offering — not currently available)*

**When to upgrade:**
- You don't want to manage infrastructure
- You need 24/7 support with SLA guarantees
- You need multi-region deployment
- You want Mythara to absorb hosting costs
- Your team needs priority support

**Enterprise Tier ($25K-$300K/year — proposed pricing, not currently offered):**
- ✅ Fully managed hosting on Mythara's infrastructure
- ✅ Unlimited API calls (we absorb costs)
- ✅ 99.9% uptime SLA
- ✅ 24/7 priority support
- ✅ Dedicated account manager
- ✅ Custom integrations
- ✅ Multi-region deployment

**Contact:** Mythara.Engine@yahoo.com

---

## 🐛 Troubleshooting

### "License key invalid"
- Check your email for the correct license key
- Ensure no extra spaces or line breaks
- Contact support: Mythara.Engine@yahoo.com

### "Port already in use"
- Change PORT environment variable: `PORT=8001`
- Or stop conflicting service: `docker ps` → `docker stop <container>`

### "Database connection failed"
- Default uses in-memory storage (fine for pilot)
- For persistent storage, set DATABASE_URL
- Supported: PostgreSQL, MySQL, SQLite

### "High hosting costs"
- Review your usage in platform dashboard
- Consider adding caching (Redis)
- Optimize API call frequency
- Contact sales for Enterprise tier (unlimited hosted)

---

## 📞 Support

**Pilot Tier (Self-Hosted):**
- GitHub Issues: https://github.com/herbievelezjr/Mythara_Archive/issues
- Community Discord: [Coming Soon]
- Email: Mythara.Engine@yahoo.com (best effort)

**Enterprise Tier:**
- 24/7 Priority Support
- Dedicated Slack channel
- Phone support
- Custom SLA

---

## 📝 Terms & Conditions

- One pilot license per business domain
- Self-hosted deployment only (you pay hosting costs)
- No refunds after Docker image access granted
- Valid for 12 months from purchase
- Does not include hosted API service
- Upgrade to Enterprise for managed hosting

---

**Questions?** Email Mythara.Engine@yahoo.com

**Ready to upgrade?** Contact sales for Enterprise tier ($25K+/year) with fully managed hosting.

---

© 2025 Herbert Velez Jr. All rights reserved.
