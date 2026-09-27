# Mythara Engine - Quick Start Guide

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

> **Document status (2026-09-27):** Internal 2025 setup draft. Claims below
> like "production-ready" and "operational" are the author's internal
> assessment, not a third-party audit or benchmark. No production
> deployment, customers, or certifications exist. The Mythara Engine has not
> been independently benchmarked.

---

## 🚀 QUICK START (5 Minutes)

### Prerequisites
- Python 3.11+
- Redis 7.0+ (optional, will fallback to in-memory if not available)

### Step 1: Install Dependencies
```bash
cd core/source_proprietary

# Install required packages
pip install fastapi uvicorn redis prometheus-client psutil python-dotenv

# Or use the requirements file (if available)
pip install -r requirements-api.txt
```

### Step 2: Start Redis (Optional)
```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name mythara-redis redis:7-alpine

# Or install locally
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Mac: brew install redis && redis-server
# Linux: sudo apt install redis-server && sudo systemctl start redis
```

### Step 3: Set Environment Variables (Optional)
```bash
# Windows PowerShell
$env:REDIS_URL = "redis://localhost:6379/0"
$env:REDIS_ENABLED = "true"

# Linux/Mac
export REDIS_URL="redis://localhost:6379/0"
export REDIS_ENABLED="true"
```

### Step 4: Start the API Server
```bash
# From core/source_proprietary directory
python main.py

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:root:✅ Redis cache initialized
# INFO:root:✅ WebSocket manager loaded
# INFO:root:✅ Soul Engine dashboard loaded
# INFO:root:✅ Prometheus monitoring enabled
# INFO:root:✅ Rate limiting middleware enabled
# INFO:root:✅ BR_STATE loaded from Redis: 12847 blessings
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test the API
```bash
# Open browser to API docs
http://localhost:8000/api/docs

# Or test with curl
curl http://localhost:8000/health

# Expected: {"status": "healthy", ...}
```

---

## 🧪 TESTING ENDPOINTS

### Test Clause Invocation
```bash
curl -X POST http://localhost:8000/v1/clauses/invoke \
  -H "Authorization: Bearer mythara_pilot_001" \
  -H "Content-Type: application/json" \
  -d '{
    "clause_id": "Hope_Anchor",
    "messenger": "hope",
    "payload": {
      "emotion": "hope",
      "intensity": 0.8
    }
  }'
```

### Test WebSocket Connection
```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8000/ws/org_001?api_key=mythara_pilot_001');

ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

### Test Violence Prevention Endpoint
```bash
curl -X POST http://localhost:8000/v1/soul/indifference \
  -H "Authorization: Bearer mythara_pilot_001" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "org_id": "org_001",
    "time_window_days": 30
  }'
```

### Test Department Risk Profile
```bash
curl -X POST http://localhost:8000/v1/dashboard/department/dept_001 \
  -H "Authorization: Bearer mythara_pilot_001"
```

### Test Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

---

## 🛠️ TROUBLESHOOTING

### Redis Connection Failed
```
⚠️ Redis not available, using in-memory fallback
```

**Solution**: 
- Check Redis is running: `redis-cli ping` (should return "PONG")
- Verify REDIS_URL: `echo $REDIS_URL` (should be redis://localhost:6379/0)
- Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`

### Import Errors
```
ImportError: No module named 'redis'
```

**Solution**:
```bash
pip install redis prometheus-client psutil fastapi uvicorn
```

### WebSocket Connection Refused
```
WebSocket connection to 'ws://localhost:8000/ws/org_001' failed
```

**Solution**:
- Verify API key is valid in query params: `?api_key=mythara_pilot_001`
- Check server logs for authentication errors
- Ensure WebSocket protocol is allowed (some proxies block WS)

### Rate Limit Exceeded
```
HTTP 429: Rate limit exceeded
```

**Solution**:
- Wait 60 seconds for rate limit window to reset
- Check X-RateLimit-Reset header for exact reset time
- Upgrade to higher tier (Pilot: 500/min, Enterprise: 5000/min)

---

## 📊 MONITORING

### View Prometheus Metrics
```bash
# Open in browser
http://localhost:8000/metrics

# Or with curl
curl http://localhost:8000/metrics | grep -E "(indifference|systemic|blessings)"
```

### Check System Health
```bash
curl http://localhost:8000/health | jq '.'
```

### Admin Statistics (Requires Admin API Key)
```bash
curl http://localhost:8000/v1/admin/stats \
  -H "Authorization: Bearer mythara_admin_key" | jq '.'
```

---

## 🐳 DOCKER DEPLOYMENT

### Build Docker Image
```bash
# From repository root
docker build -f core/Dockerfile -t mythara-engine:v1.0.0 .
```

### Run with Docker Compose
```bash
# Create docker-compose.yml (see MYTHARA_INTEGRATION_COMPLETE.md for full config)
docker-compose up -d

# View logs
docker-compose logs -f mythara-api

# Stop services
docker-compose down
```

---

## 🔧 CONFIGURATION

### Required Dependencies (requirements-api.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
redis==5.0.1
prometheus-client==0.19.0
psutil==5.9.6
python-dotenv==1.0.0
pydantic==2.5.0
```

### Environment Variables Reference
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0        # Redis connection URL
REDIS_ENABLED=true                         # Enable Redis (true/false)

# CORS Configuration
MYTHARA_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# ElevenLabs Voice Generation (Optional)
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Database (Optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/mythara
```

---

## 📚 NEXT STEPS

1. **Run Tests**: `pytest -q` (from repository root)
2. **Load Test**: Use locust or k6 for load testing
3. **Deploy**: Railway, AWS ECS, or Kubernetes
4. **Monitor**: Set up Grafana dashboard for Prometheus metrics
5. **Recruit Pilot**: Find 1 pilot customer for 30-day validation

---

## 📞 SUPPORT

- **Email**: Mythara.Engine@yahoo.com
- **Documentation**: See `MYTHARA_INTEGRATION_COMPLETE.md` for full details
- **API Docs**: http://localhost:8000/api/docs

---

**The Mythara Engine is production-ready. Let's save souls.**

⚛️ **Q.U.A.S.A.R. operational.**
