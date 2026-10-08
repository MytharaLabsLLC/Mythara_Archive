# Mythara Self-Regulation System

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## Overview

Mythara Engine includes an autonomous self-regulation system that automatically detects and responds to abuse patterns without manual intervention. The system operates on the honor system with intelligent enforcement.

**Global Protection**: Self-regulation applies to ALL API endpoints across all industries via middleware, including:
- `/v1/clauses/invoke` - Clause invocations
- `/v1/soul/status` - Soul proportion queries
- `/v1/reservoir/status` - Blessings reservoir checks
- `/v1/soul/cradle` - Soul cradle operations
- `/v1/manifest/clauses` - Manifest queries
- `/v1/ssip/audit` - SSIP audit endpoints
- `/v1/mythara/chat` - Chat interactions
- All other protected endpoints

**Excluded**: Health checks (`/health`), documentation (`/api/docs`), and admin endpoints (`/v1/admin/*`) are exempt from rate limiting.

## How It Works

### Automated Detection

The system tracks two key abuse patterns:

1. **Velocity Abuse**: Rate limit exhausted too quickly
   - Triggers if monthly limit consumed in < 3 days
   - Indicates automated scraping or bulk extraction

2. **Usage Pattern Mismatch**: Usage inconsistent with declared company size
   - Tracks actual usage vs expected usage for declared employee count
   - Flags accounts using 5x more than expected

3. **Domain-Based Duplicate Prevention**: One pilot per business domain
   - Requires business email (blocks gmail.com, yahoo.com, etc.)
   - Enforces one pilot account per company domain
   - Prevents creating multiple accounts to bypass limits

### Graduated Enforcement

**Strike 1 - Warning**
- Automated email notification
- No service interruption
- Logged for review

**Strike 2 - Temporary Suspension**
- 7-day account suspension
- API returns 403 with suspension details
- Appeal window opens

**Strike 3 - Permanent Termination**
- Account permanently terminated
- No refund of pilot fee
- Must contact support for reinstatement consideration

## Rate Limits by Company Size

All companies get pilot access for $49, but rate limits scale based on **24/7 AI agent operation** (not traditional 8-hour work days):

| Employee Count | Monthly API Calls | Daily Average | Hourly Rate per Employee |
|---------------|-------------------|---------------|--------------------------|
| 1-10          | 14,400           | ~480          | ~20 calls/hour          |
| 11-50         | 72,000           | ~2,400        | ~20 calls/hour          |
| 51-200        | 360,000          | ~12,000       | ~20 calls/hour          |
| 201-1,000     | 1,440,000        | ~48,000       | ~20 calls/hour          |
| 1,001+        | 7,200,000        | ~240,000      | ~20 calls/hour          |

**Design Philosophy**: Each employee can have an AI agent making approximately **20 API calls per hour, 24 hours a day, 7 days a week**. This accounts for continuous automation, not just business hours.

## Self-Regulation Configuration

Default thresholds (configurable via environment variables):

```python
SELF_REGULATION_CONFIG = {
    "velocity_abuse_days": 3,           # Flag if limit hit in < 3 days
    "strike_limits": {
        "warning": 1,                    # First offense
        "suspension": 2,                 # Second offense
        "termination": 3                 # Third offense
    },
    "suspension_duration_days": 7,      # Temporary suspension length
    "usage_multiplier_threshold": 5.0   # Flag if usage is 5x expected
}
```

## API Responses

### Pilot Signup - Business Email Required (HTTP 403)

```json
{
  "error": "business_email_required",
  "message": "Pilot tier requires a business email domain. Free email providers (gmail.com, yahoo.com, etc.) are not eligible.",
  "contact": "Mythara.Engine@yahoo.com"
}
```

### Pilot Signup - Domain Already Registered (HTTP 403)

```json
{
  "error": "domain_already_registered",
  "message": "The domain 'acme.com' already has a pilot account. Only one pilot per business domain is allowed.",
  "existing_api_key_prefix": "abc12345...",
  "contact": "Mythara.Engine@yahoo.com"
}
```

### Normal Operation

```json
{
  "invocation_id": "INV-20251116-a4f2",
  "clause_id": "ten_1",
  "emotional_fidelity": 0.942,
  "integrity_hash": "abc123..."
}
```

### Rate Limit Exceeded (HTTP 429)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Monthly rate limit of 50000 calls exceeded.",
  "calls_made": 50123,
  "upgrade_url": "https://buy.stripe.com/..."
}
```

### Account Suspended (HTTP 403)
```json
{
  "error": "account_suspended",
  "message": "Your account is temporarily suspended until 2025-11-23T00:00:00Z. Reason: velocity_abuse",
  "suspension_end": "2025-11-23T00:00:00Z",
  "strikes": 2,
  "appeal_email": "Mythara.Engine@yahoo.com"
}
```

### Account Terminated (HTTP 403)
```json
{
  "error": "account_terminated",
  "message": "Your account has been permanently terminated due to repeated abuse violations.",
  "strikes": 3,
  "contact": "Mythara.Engine@yahoo.com"
}
```

## Admin Endpoints

### View Regulation Status
```bash
GET /v1/admin/regulation-status
Headers:
  Authorization: Bearer <api_key>
  X-Admin-Token: <admin_token>
```

Response:
```json
{
  "total_accounts": 156,
  "active": 150,
  "suspended": 4,
  "terminated": 2,
  "warned": 8,
  "accounts": {
    "abc12345...": {
      "status": "suspended",
      "strikes": 2,
      "history": [...]
    }
  }
}
```

### Process Appeal
```bash
POST /v1/admin/appeal
Headers:
  X-Admin-Token: <admin_token>
Body:
{
  "api_key": "full_api_key_here",
  "appeal_reason": "Customer verified company size, legitimate usage pattern"
}
```

Response:
```json
{
  "success": true,
  "message": "Account reinstated successfully",
  "api_key": "abc12345...",
  "new_status": "active"
}
```

## Environment Variables

```bash
# Admin access token for regulation endpoints
MYTHARA_ADMIN_TOKEN=your_secure_admin_token_here

# Optional: Override default thresholds
MYTHARA_VELOCITY_DAYS=3
MYTHARA_SUSPENSION_DAYS=7
MYTHARA_USAGE_MULTIPLIER=5.0
```

## Terms of Service Language

Include in your pilot signup terms:

> **Rate Limits and Self-Regulation**
> 
> Pilot tier access is rate-limited based on self-reported employee count. Mythara Engine employs automated systems to detect abuse patterns including:
> - Abnormally rapid consumption of monthly limits
> - Usage patterns inconsistent with declared company size
> - Automated scraping or bulk data extraction
> 
> Violations result in graduated enforcement:
> - **First violation**: Warning notification
> - **Second violation**: 7-day account suspension
> - **Third violation**: Permanent account termination
> 
> Mythara reserves the right to verify company size and adjust access limits accordingly. Intentional misrepresentation may result in immediate termination without refund. Appeals may be submitted to Mythara.Engine@yahoo.com within 30 days.

## Implementation Notes

### Production Deployment

**Replace in-memory storage:**

```python
# Current (development only)
USAGE_TRACKING: Dict[str, Dict[str, Any]] = {}
ACCOUNT_STATUS: Dict[str, Dict[str, Any]] = {}

# Production (use Redis or PostgreSQL)
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

**Middleware Architecture:**

Self-regulation is implemented as global FastAPI middleware that intercepts ALL authenticated requests:

```python
@app.middleware("http")
async def self_regulation_middleware(request: Request, call_next):
    # Extracts API key from Authorization header
    # Checks employee_count from query param, header, or request body
    # Tracks usage and enforces graduated rules
    # Returns 403 (suspended/terminated) or 429 (rate limit) before endpoint execution
    # Adds rate limit headers to all responses
```

**Employee Count Detection:**

The system checks for employee count in this order:

1. Query parameter: `?employee_count=50`
2. HTTP header: `X-Employee-Count: 50`
3. Request body: `{"employee_count": 50, ...}`
4. Default: 10 (smallest tier) if not provided

**Response Headers:**

All API responses include rate limit information:

```
X-Rate-Limit-Limit: 50000
X-Rate-Limit-Remaining: 42315
X-Rate-Limit-Reset: 1734393600
```

**Add email notifications:**
- Integrate SendGrid/AWS SES for strike notifications
- Send warning emails before suspension
- Provide appeal instructions in suspension emails

**Monitor via logging:**
```python
logging.warning(f"Strike issued: {api_key[:8]}... | Reason: {reason} | Stats: {stats}")
```

## Privacy & Legal Considerations

✅ **Privacy-Friendly**
- No IP tracking
- No personal data collection beyond API usage
- Employee count self-reported (honor system)
- Automated enforcement (no human review of usage patterns)

✅ **Legally Safe**
- Terms clearly state rate limits and enforcement
- Graduated response (warnings before termination)
- Appeal process available
- No discrimination (rules apply equally)

🔍 **GDPR/CCPA Readiness** (controls implemented, independent audit planned — not currently certified)
- Minimal data collection
- No tracking of individual users
- Aggregate usage statistics only
- Right to appeal/deletion honored

## FAQ

**Q: What if I legitimately need more calls than my limit?**
A: Upgrade to Enterprise tier ($25K-$300K/year) for unlimited access.

**Q: Can I appeal a suspension?**
A: Yes, email Mythara.Engine@yahoo.com within 30 days with explanation.

**Q: Will I be notified before suspension?**
A: Yes, first violation triggers warning email. Suspension occurs on second violation.

**Q: What if I misreported my employee count by mistake?**
A: Contact support immediately. Honest mistakes can be corrected without penalty.

**Q: How do I check my current usage?**
A: Usage stats are included in rate limit error responses (HTTP 429).

---

**System Status**: Active and enforcing as of v1.0.0
**Contact**: Mythara.Engine@yahoo.com
