# Mythara Engine API

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  
**Proprietary and Confidential.**

---

## FastAPI Server Implementation

Reference implementation of the Mythara Engine API: symbolic clause invocation and SSIP orchestration over FastAPI.

### Features

✅ **7 documented core endpoints** (the server exposes additional endpoints; see `main.py`)
- `POST /v1/clauses/invoke` — Invoke symbolic clauses
- `GET /v1/reservoir/status` — Blessings Reservoir metrics
- `GET /v1/manifest/clauses` — Clause manifest with integrity hashes
- `GET /v1/ssip/audit` — SSIP compliance audit
- `GET /v1/clauses/{clause_id}` — Individual clause details
- `GET /health` — Health check
- `GET /` — Root status

✅ **Security**
- Bearer token authentication
- API key validation
- CORS middleware
- Integrity hash verification

✅ **Compliance**
- SSIP metrics tracking
- Drift suppression monitoring
- Emotional fidelity calculations
- Audit trail generation

---

## Quick Start

### 1. Install Dependencies

```bash
cd core/source_proprietary
pip install -r requirements-api.txt
```

### 2. Run Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### 3. View API Documentation

Open in browser:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Authentication

All endpoints (except `/` and `/health`) require Bearer token authentication.

### Test API Keys

```
Development: dev_test_key_001
Enterprise:  ent_prod_key_001
Sovereign:   sov_airgap_key_001
```

### Example Request

```bash
curl -X POST http://localhost:8000/v1/clauses/invoke \
  -H "Authorization: Bearer dev_test_key_001" \
  -H "Content-Type: application/json" \
  -d '{
    "clause_id": "Legacy_Seed",
    "messenger": "M-001",
    "payload": {
      "emotion": "grief",
      "intensity": 0.87,
      "context": "ancestral_memory"
    },
    "consent_token": "user_consent_xyz"
  }'
```

---

## Endpoint Details

### POST /v1/clauses/invoke

Invoke a symbolic clause with emotional payload.

**Request Body:**
```json
{
  "clause_id": "Legacy_Seed",
  "messenger": "M-001",
  "payload": {
    "emotion": "grief",
    "intensity": 0.87,
    "context": "ancestral_memory"
  },
  "consent_token": "user_consent_xyz"
}
```

**Response:**
```json
{
  "invocation_id": "INV-20251102-a3f2",
  "clause_id": "Legacy_Seed",
  "messenger": "M-001",
  "emotional_fidelity": 0.93,
  "blessings_delta": 87,
  "timestamp": "2025-11-02T19:30:00Z",
  "integrity_hash": "3f2a9c1e8b7f4a2c..."
}
```

---

### GET /v1/reservoir/status

Get Blessings Reservoir metrics.

**Response:**
```json
{
  "reservoir_score": 0.91,
  "total_blessings": 12847,
  "overflow_events": 2,
  "last_update": "2025-11-02T19:00:00Z"
}
```

---

### GET /v1/manifest/clauses

Retrieve complete clause manifest.

**Response:**
```json
{
  "manifest_version": "v1.0.0",
  "clauses": [
    {
      "clause_id": "Legacy_Seed",
      "description": "Ancestral memory harmonization clause",
      "emotional_tags": ["grief", "legacy", "ancestral"],
      "fallback_clause": "Shadow_Resolver",
      "integrity_hash": "3f2a9c..."
    }
  ],
  "total_clauses": 3
}
```

---

### GET /v1/ssip/audit

Run SSIP compliance audit.

**Response:**
```json
{
  "drift_suppression": 0.992,
  "messenger_pairing_fidelity": 0.994,
  "emotional_fidelity": 0.93,
  "sanctification_locks_active": true,
  "compliance_status": "PASS"
}
```

---

## Available Clauses

**Legacy_Seed**  
Ancestral memory harmonization  
Tags: grief, legacy, ancestral

**Hope_Anchor**  
Future-oriented resilience  
Tags: hope, resilience, forward

**Shadow_Resolver**  
Fallback safety clause  
Tags: safety, fallback, neutral

---

## Production Deployment

### Docker

```bash
# Build image
docker build -t mythara-api:1.0.0 -f ../../Dockerfile .

# Run container
docker run -p 8000:8000 mythara-api:1.0.0
```

### Environment Variables

Create `.env` file:

```bash
API_VERSION=1.0.0
LOG_LEVEL=info
CORS_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/mythara
REDIS_URL=redis://localhost:6379
```

### Production Considerations

⚠️ **Current implementation uses in-memory state** (for demo/testing)

For production:
1. Replace `BR_STATE` dict with Redis
2. Replace `CLAUSE_DB` dict with PostgreSQL
3. Use secure API key storage (database/secrets manager)
4. Enable HTTPS/TLS
5. Add rate limiting (slowapi or nginx)
6. Set up monitoring (Prometheus, DataDog)
7. Configure CORS for specific domains
8. Add request validation middleware
9. Implement audit logging to database
10. Set up backup/disaster recovery

---

## Testing

```bash
# Run automated tests
pytest

# Test with curl
curl http://localhost:8000/health

# Test authenticated endpoint
curl -H "Authorization: Bearer dev_test_key_001" \
     http://localhost:8000/v1/reservoir/status
```

---

## License

This API implementation is proprietary software owned by **Herbert Velez Jr.**

- Development License: $2,500/year
- Enterprise License: Production deployment
- Sovereign License: Air-gapped deployment

See `../../LICENSE.md` and `../../COPYRIGHT.md` for complete terms.

---

**Version:** 1.0.0  
**Last Updated:** November 2, 2025  
**Author:** Herbert Velez Jr.
