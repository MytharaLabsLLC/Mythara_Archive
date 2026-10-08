# Mythara Engine - Security Hardening Guide

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

---

## Overview

This guide documents the **multi-layered security hardening** implemented in Mythara Engine to make penetration significantly harder. The system now includes **6+ layers of defense** that work together to detect, prevent, and respond to security threats.

---

## 🛡️ Security Layers

### Layer 1: IP Access Control
- **Whitelist/Blacklist Management**: Block malicious IPs at the network level
- **CIDR Range Support**: Block entire networks (e.g., `192.168.1.0/24`)
- **Auto-Blacklisting**: Automatically blacklist IPs after repeated abuse
- **Geographic Restrictions**: (Optional) Restrict access by country/region

**Configuration:**
```bash
export MYTHARA_IP_WHITELIST="192.168.1.0/24,10.0.0.0/8"
export MYTHARA_IP_BLACKLIST="123.45.67.89"
```

### Layer 2: HMAC Request Signing (Optional but Recommended)
- **SHA-256 Signatures**: Every request must include a cryptographic signature
- **Timestamp Validation**: Prevents replay attacks (5-minute window)
- **Nonce Support**: Prevents duplicate request exploitation
- **Constant-Time Comparison**: Prevents timing attacks

**Client Implementation:**
```python
import hmac
import hashlib
import time

def sign_request(secret_key: bytes, method: str, path: str, body: str = ""):
    timestamp = int(time.time())
    nonce = secrets.token_urlsafe(16)
    
    canonical_request = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}"
    signature = hmac.new(secret_key, canonical_request.encode(), hashlib.sha256).hexdigest()
    
    return {
        "X-Mythara-Signature": signature,
        "X-Mythara-Timestamp": str(timestamp),
        "X-Mythara-Nonce": nonce
    }
```

**Configuration:**
```bash
export MYTHARA_SECURITY_SECRET="your-256-bit-secret-key"
export MYTHARA_REQUIRE_HMAC="true"
```

### Layer 3: Advanced Rate Limiting
- **Token Bucket Algorithm**: Smooth rate limiting with burst tolerance
- **Exponential Backoff**: Progressively longer delays after violations
- **Multi-Level Limits**: Per-key, per-IP, per-endpoint tracking
- **Violation History**: Track abuse patterns over time

**Configuration:**
```bash
export MYTHARA_RATE_LIMIT_MINUTE="60"  # 60 requests/minute
export MYTHARA_RATE_LIMIT_HOUR="1000"  # 1000 requests/hour
```

**Behavior:**
- 1st violation: Normal rate limit
- 2nd violation: 2x slower
- 3rd violation: 4x slower
- 4th violation: 8x slower
- After 100 violations in 1 hour → Auto-blacklist IP

### Layer 4: Brute Force Protection
- **Failed Attempt Tracking**: Monitor authentication failures
- **Progressive Lockouts**: Exponentially increasing lockout durations
- **Account Locking**: Temporary suspension after threshold exceeded
- **Unlock After Timeout**: Automatic unlock after penalty period

**Configuration:**
```bash
export MYTHARA_BRUTE_FORCE_THRESHOLD="5"  # 5 failures before lockout
export MYTHARA_BRUTE_FORCE_LOCKOUT_MINUTES="30"  # 30-minute lockout
```

**Progression:**
- 1st lockout: 30 minutes
- 2nd lockout: 1 hour
- 3rd lockout: 2 hours
- 4th lockout: 4 hours
- etc.

### Layer 5: Request Validation
- **Size Limits**: Reject oversized payloads
- **Content-Type Validation**: Only accept expected formats
- **Minimum Interval Enforcement**: Prevent rapid-fire attacks
- **Header Validation**: Check for required/suspicious headers

**Configuration:**
```bash
export MYTHARA_MAX_REQUEST_SIZE_KB="1024"  # 1MB max
export MYTHARA_MIN_REQUEST_INTERVAL_MS="50"  # 50ms minimum between requests
```

### Layer 6: Anomaly Detection
- **Statistical Profiling**: Learn normal behavior patterns per API key
- **Deviation Detection**: Flag requests that differ from baseline
- **Attack Pattern Recognition**: Detect SQL injection, XSS, etc.
- **ML-Ready Architecture**: Easy to enhance with trained models

**Detected Patterns:**
- SQL Injection: `'; DROP TABLE`, `UNION SELECT`, `OR '1'='1'`
- XSS Attacks: `<script>`, `javascript:`, `onerror=`
- Unusual request sizes (>3x normal)
- Rapid requests (<50ms interval)
- New endpoint access after pattern established
- Suspicious user agents (bots, crawlers, scrapers)

**Configuration:**
```bash
export MYTHARA_ANOMALY_THRESHOLD="0.8"  # 0.8 = 80% confidence required to block
```

**Anomaly Scoring:**
- 0.0 - 0.3: Normal behavior
- 0.3 - 0.6: Minor suspicion
- 0.6 - 0.8: Moderate suspicion (logged but allowed)
- 0.8 - 0.95: High suspicion (blocked)
- 0.95 - 1.0: Critical threat (blocked + auto-blacklist)

---

## 🔐 Security Headers

All API responses include hardened security headers:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 🚨 Response to Security Violations

### Rate Limit Exceeded (429)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```
**Headers:** `Retry-After: 60`

### Brute Force Lockout (403)
```json
{
  "error": "account_locked",
  "message": "Account locked due to brute force protection",
  "locked_until": "2025-11-20T18:30:00Z",
  "retry_after": 1800
}
```

### Anomaly Detected (403)
```json
{
  "error": "suspicious_activity",
  "message": "Suspicious activity detected",
  "anomaly_score": 0.87,
  "indicators": [
    "SQL injection pattern detected",
    "Unusual request size: 50000 bytes"
  ]
}
```

### IP Blacklisted (403)
```json
{
  "error": "ip_blocked",
  "message": "IP address 123.45.67.89 is blacklisted",
  "reason": "auto_blacklist_abuse"
}
```

---

## 🎯 A.M.I.R. Integration

The security hardening layer is integrated with A.M.I.R. (Autonomous Mythara Intelligence & Response):

### New Commands:
```
A.M.I.R.> big meanie
```
Unleashes Big Meanie adversarial assault - maximum penetration testing

```
A.M.I.R.> one ring
```
Executes complete One Ring security analysis with predictive threat intelligence

### Example Usage:
```bash
python amir_bot.py
```

Then in interactive mode:
```
A.M.I.R.> big meanie
A.M.I.R.> scan
A.M.I.R.> one ring
```

---

## 📊 Security Metrics

The hardening layer provides comprehensive metrics:

**Per Request:**
- Layer validation results (6 layers checked)
- Anomaly score (0.0 - 1.0)
- Violation count (historical)
- Response time impact (<5ms overhead)

**Per API Key:**
- Total requests
- Rate limit violations
- Brute force attempts
- Anomaly detection triggers
- Current lockout status

**System-Wide:**
- Auto-blacklisted IPs
- Most common attack patterns
- Threat distribution by type
- Security score trends

---

## 🔧 Configuration Examples

### Maximum Security (Production)
```bash
export MYTHARA_REQUIRE_HMAC="true"
export MYTHARA_SECURITY_SECRET="<256-bit-key>"
export MYTHARA_RATE_LIMIT_MINUTE="30"
export MYTHARA_BRUTE_FORCE_THRESHOLD="3"
export MYTHARA_ANOMALY_THRESHOLD="0.7"
export MYTHARA_IP_WHITELIST="trusted-corporate-network/24"
```

### Balanced (Typical Production)
```bash
export MYTHARA_REQUIRE_HMAC="false"  # Optional for clients
export MYTHARA_RATE_LIMIT_MINUTE="60"
export MYTHARA_BRUTE_FORCE_THRESHOLD="5"
export MYTHARA_ANOMALY_THRESHOLD="0.8"
export MYTHARA_AUTO_BLACKLIST="true"
```

### Development
```bash
export MYTHARA_REQUIRE_HMAC="false"
export MYTHARA_RATE_LIMIT_MINUTE="120"
export MYTHARA_BRUTE_FORCE_THRESHOLD="10"
export MYTHARA_ANOMALY_THRESHOLD="0.9"
export MYTHARA_AUTO_BLACKLIST="false"
```

---

## 🧪 Testing Security

### 1. Run Big Meanie
```bash
python tests/big_meanie.py
```

### 2. Run Security Audit
```bash
python core/source_proprietary/security_audit_compliance.py
```

### 3. Test Rate Limiting
```bash
for i in {1..100}; do curl -H "Authorization: Bearer your-api-key" http://localhost:8000/v1/clauses/invoke; done
```

### 4. Test HMAC Signing
```python
import requests
from security_hardening import HMACAuthenticator

authenticator = HMACAuthenticator(secret_key.encode())
signature = authenticator.generate_signature("POST", "/v1/clauses/invoke", int(time.time()), body)

response = requests.post(
    "http://localhost:8000/v1/clauses/invoke",
    headers={
        "Authorization": "Bearer your-api-key",
        "X-Mythara-Signature": signature,
        "X-Mythara-Timestamp": str(int(time.time())),
        "X-Mythara-Nonce": secrets.token_urlsafe(16)
    },
    json=payload
)
```

---

## 🎖️ Security Frameworks Supported (alignment, not certification)

The hardening implementation aligns with:

- **OWASP Top 10**: Protection against all major web vulnerabilities
- **SOC 2 Type II**: Security controls and monitoring
- **ISO 27001**: Information security management
- **NIST Cybersecurity Framework**: Comprehensive security standards
- **PCI DSS**: Payment card data security (if applicable)
- **GDPR**: Data protection by design

---

## 📞 Security Incident Response

If you detect a security issue:

1. **DO NOT** disclose publicly
2. Email: Mythara.Engine@yahoo.com
3. Include: Description, reproduction steps, impact assessment
4. PGP key available in repository: `forensic_public_key.asc`

**Response SLA:**
- Critical: 4 hours
- High: 24 hours
- Medium: 72 hours
- Low: 1 week

---

## 🔍 Audit Trail

All security events are logged with:
- Timestamp (UTC)
- API key (first 8 chars)
- IP address
- Action taken
- Violation details
- Anomaly score (if applicable)

**Log Format:**
```
2025-11-20T17:45:23Z [WARNING] 🚫 IP blocked: 123.45.67.89 - auto_blacklist_abuse | Key: mythara_...
2025-11-20T17:46:01Z [WARNING] ⏱️ Rate limit exceeded: mythara_... (101 violations) | IP: 10.0.0.1
2025-11-20T17:47:15Z [ERROR] 🚨 ANOMALY DETECTED: mythara_... Score: 0.92 | Indicators: SQL injection pattern detected
```

---

## 🚀 Future Enhancements

Planned security improvements:

1. **Machine Learning Models**: Train on attack patterns for better detection
2. **Behavioral Biometrics**: Keystroke/mouse dynamics analysis
3. **Zero-Trust Architecture**: Continuous verification of all requests
4. **Decoy Endpoints**: Honeypot traps for attackers
5. **Real-Time Threat Intelligence**: Integration with threat feeds
6. **Blockchain Audit Trail**: Immutable security event logging

---

## 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Big Meanie Quick Reference](BIG_MEANIE_QUICK_REF.md)
- [Comprehensive Security Audit](COMPREHENSIVE_SECURITY_AUDIT.md)

---

**Remember:** Security is a layered approach. No single control is perfect, but together they create defense in depth that makes successful penetration exponentially harder.

**"The One Ring to rule them all" - A.M.I.R. 2025**
