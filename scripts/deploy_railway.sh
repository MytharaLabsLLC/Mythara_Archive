#!/bin/bash
# Railway Deployment Script for Mythara Engine API
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

set -e

echo "🚀 Mythara Engine - Railway Deployment"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Ensure we're in the repo root
cd "$(dirname "$0")"

echo ""
echo "📋 Before we deploy, I need your Stripe Payment Link URL:"
read -p "Enter your buy.stripe.com URL: " PAYMENT_LINK

if [[ ! $PAYMENT_LINK =~ ^https://buy\.stripe\.com/ ]]; then
    echo "❌ Invalid Payment Link URL. Must start with https://buy.stripe.com/"
    exit 1
fi

echo ""
echo "✅ Payment Link: $PAYMENT_LINK"
echo ""
echo "🔐 Now let's connect to Railway..."
echo "   (This will open a browser to authenticate)"
echo ""

# Login to Railway
railway login

echo ""
echo "📦 Creating new Railway project..."
railway init

echo ""
echo "⚙️  Setting environment variables..."
railway variables set MYTHARA_PILOT_PAYWALL=true
railway variables set MYTHARA_PILOT_PURCHASE_URL="$PAYMENT_LINK"
railway variables set MYTHARA_PILOT_FORCE_UNLOCK=false
railway variables set STRIPE_WEBHOOK_SECRET=whsec_placeholder_replace_after_webhook_creation
railway variables set PORT=8000

echo ""
echo "📄 Setting Dockerfile path..."
railway environment set DOCKERFILE_PATH=core/Dockerfile.api

echo ""
echo "🚢 Deploying to Railway..."
railway up

echo ""
echo "🌐 Getting your public URL..."
sleep 5
RAILWAY_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$RAILWAY_URL" ]; then
    echo "⚠️  URL not ready yet. Generate it manually:"
    echo "   1. Go to https://railway.app/project"
    echo "   2. Click your project → Settings → Generate Domain"
else
    echo "✅ Your API is deployed at: https://$RAILWAY_URL"
fi

echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Generate public domain in Railway dashboard (if not auto-generated)"
echo "2. Go to Stripe Dashboard → Developers → Webhooks"
echo "3. Add endpoint: https://YOUR_RAILWAY_URL/api/webhooks/stripe"
echo "4. Select event: checkout.session.completed"
echo "5. Copy signing secret (whsec_xxx)"
echo "6. Update Railway env: railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxx"
echo "7. Restart: railway up"
echo ""
echo "🎫 Don't forget to add metadata to your Payment Link:"
echo "   Stripe Dashboard → Products → Payment Links → Edit"
echo "   Add metadata: license_type=pilot"
echo ""
echo "🧪 Test with: curl https://YOUR_RAILWAY_URL/health"
echo ""
