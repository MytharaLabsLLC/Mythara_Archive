# Mythara Engine — Pilot (Container Run Guide)
# Copyright © 2025 Herbert Velez Jr.

This guide covers running the Mythara Engine pilot via a prebuilt container image. No source code distribution is included in the pilot package.

## Prerequisites
- Docker 20+
- A pilot API key (Bearer token) issued to your organization
- A private image pull link (provided separately by Herbert Velez Jr.)

## 1) Pull the private image
We will provide a private registry URL and temporary pull token. Example format (placeholder):

```
docker login <private-registry>
docker pull <private-registry>/mythara/engine:pilot-2025-11
```

## 2) Run the container
Set your API key and optional license settings via environment variables.

```
docker run --rm -p 8000:8000 \
  -e MYTHARA_LICENSE_MODE=trial \
  -e MYTHARA_LICENSE_TRIAL_DAYS=30 \
  -e MYTHARA_PURCHASE_URL=https://mythara.ai/enterprise \
  -e MYTHARA_INFLATION_RATE_ANNUAL=0.03 \
  -e MYTHARA_PRICE_BASE_YEAR=2025 \
  -e MYTHARA_PRICE_MULTIPLIER=1.0 \
  -e MYTHARA_DB_URL="postgresql://user:pass@localhost:5432/mythara" \
  -e MYTHARA_REDIS_URL="redis://localhost:6379/0" \
  <private-registry>/mythara/engine:pilot-2025-11
```

Once running:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 3) Authenticate and test
Use your pilot API key as a Bearer token.

```
curl -s http://localhost:8000/v1/license/status \
  -H "Authorization: Bearer <your_pilot_key>" | jq
```

Trial responses include headers:
- `X-Mythara-License-Edition`
- `X-Mythara-License-Status`
- `X-Mythara-License-Days-Remaining`
- `X-Mythara-Enterprise-Price-USD`

Example invocation:
```
curl -s -X POST http://localhost:8000/v1/clauses/invoke \
  -H "Authorization: Bearer <your_pilot_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "clause_id": "Legacy_Seed",
    "messenger": "M-001",
    "payload": {"emotion": "grief", "intensity": 0.87},
    "consent_token": "user_consent_xyz"
  }' | jq
```

## 4) Trial expiry and upgrades
- After 30 days, protected endpoints return HTTP 402 with an upgrade link and current price.
- Enterprise/Sovereign keys remain ACTIVE (no trial limits). Contact us to swap keys when you’re ready.

## Notes
- Do not attempt to reverse engineer the container or extract internal components. The pilot is for evaluation only under the Pilot License Policy.
- For air‑gapped deployments or Sovereign tier, we provide an isolated image and audit role enablement.

Questions? Mythara.Engine@yahoo.com
