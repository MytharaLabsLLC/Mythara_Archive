**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

# Adversarial Testing Guide — Breaking Mythara on Purpose

This guide shows how to actively try to break Mythara's integrity, SSIP enforcement, and security—and how to harden against each attack.

## Attack surface map

- Cryptographic integrity (hashes, signatures)
- SSIP validation and clause logic
- Input sanitization and injection
- Replay and race conditions
- Performance and resource exhaustion
- Audit log tampering

## Test suite: `tests/run_adversarial_tests.py`

Run all attacks:

```powershell
python tests\run_adversarial_tests.py
```

### What it tests

1. **Hash collision attempt**
   - Attack: Generate two different payloads with same SHA-256 hash
   - Expected: Fail (SHA-256 collision resistance ~2^128 ops)
   - Remediation: Use SHA-256 or stronger; monitor NIST guidance

2. **Replay attack**
   - Attack: Reuse old invocation ID + hash to fake a new request
   - Expected: Detect duplicate invocation ID
   - Remediation: Track seen IDs in cache/DB; expire after TTL; enforce monotonic timestamps

3. **Tampering detection**
   - Attack: Modify response after hash generation
   - Expected: Hash verification fails
   - Remediation: Clients must recompute hash and compare; reject mismatches

4. **Injection in clause name**
   - Attack: SQL/command injection via clause parameter (e.g., `'; DROP TABLE;--`)
   - Expected: Allowlist or parameterized queries block
   - Remediation: Validate clause names against allowlist; use Pydantic enum or strict pattern match

5. **Oversized payload**
   - Attack: Send multi-GB payload to exhaust memory/CPU
   - Expected: Reject with HTTP 413 Payload Too Large
   - Remediation: Set `client_max_body_size` in Uvicorn/nginx; validate size before parsing

6. **Unicode normalization bypass**
   - Attack: Use look-alike Unicode (e.g., Greek Α vs Latin A) to bypass filters
   - Expected: Normalize (NFC/NFKC) before comparison
   - Remediation: Apply `unicodedata.normalize('NFKC', text)` on all user inputs

7. **Timing attack on hash comparison**
   - Attack: Infer hash value by measuring comparison time
   - Expected: Constant-time comparison
   - Remediation: Use `hmac.compare_digest(hash_expected, hash_received)`

8. **SSIP bypass via null clause**
   - Attack: Pass `null`, `""`, or missing clause to skip validation
   - Expected: Enforce presence with Pydantic `Field(..., min_length=1)`
   - Remediation: Reject requests with missing/empty required fields

9. **Race condition on invocation ID**
   - Attack: Concurrent requests with same ID
   - Expected: Atomic check-and-insert prevents duplicates
   - Remediation: Use DB unique constraint or Redis `SETNX`; handle exceptions gracefully

10. **Performance degradation under load**
    - Attack: Rapid requests to degrade hashing/validation speed
    - Expected: Sub-100ms overhead per call
    - Remediation: Async logging; sample audits (1–10% in dev); scale workers; use rate limiting

## Additional manual attacks (not in automated suite)

### API key brute force
- Attack: Enumerate Bearer tokens
- Remediation: Rate-limit auth endpoints; use strong, random keys (256-bit); rotate regularly; monitor failed attempts

### Log injection
- Attack: Inject newlines/ANSI codes into logs to forge entries
- Remediation: Escape/sanitize all user input before logging; use structured JSON logs; WORM storage

### Denial of service (application layer)
- Attack: Flood endpoints to exhaust resources
- Remediation: Rate limiting (per IP/key); CAPTCHAs or proof-of-work; autoscaling; circuit breakers

### Side-channel leakage
- Attack: Infer clause or input via response time/size
- Remediation: Pad responses to constant size where critical; add random jitter; use encrypted channels

### Dependency vulnerabilities
- Attack: Exploit known CVEs in FastAPI, Pydantic, cryptography, etc.
- Remediation: Pin versions in `requirements-api.txt`; run `pip-audit` or Dependabot; update regularly

## Hardening checklist (production)

- Input validation
  - Pydantic strict types and length limits
  - Allowlist clause names
  - Unicode normalization (NFKC)
  - Reject null/empty required fields

- Cryptographic integrity
  - SHA-256 or SHA-3 for hashes
  - `hmac.compare_digest` for comparisons
  - Rotate signing keys regularly
  - Monitor NIST post-quantum readiness

- Replay and race prevention
  - Unique invocation IDs with monotonic timestamps
  - Redis/DB cache for seen IDs with TTL
  - Atomic check-and-insert (unique constraints)

- Resource limits
  - Max payload size (10 MB default)
  - Rate limiting (per IP/key)
  - Request timeouts (30s default)
  - Worker pool scaling

- Audit integrity
  - Append-only, WORM storage for logs
  - Structured JSON (no user-controlled fields in raw strings)
  - Signed manifests (PGP)
  - Retention policies (align with regulatory requirements)

- Dependency hygiene
  - Pin versions; run `pip-audit` weekly
  - Enable Dependabot alerts
  - Test updates in staging before prod

- Network security
  - TLS 1.3 only; strong cipher suites
  - Firewall ingress to known IPs (if feasible)
  - Separate subnets for API, DB, logs

## Running the adversarial suite

```powershell
# Install dependencies if needed
pip install -r tests\requirements.txt

# Run adversarial tests
python tests\run_adversarial_tests.py
```

Expected output:

```
============================================================
MYTHARA ENGINE — ADVERSARIAL TEST SUITE
============================================================

[TEST] Hash collision attempt
✅ No collision: abc123def456... ≠ xyz789ghi012...

[TEST] Replay attack
✅ Replay blocked: INV_123456789 already seen

[TEST] Tampering detection
✅ Tampering detected: hash mismatch

...

============================================================
SUMMARY
============================================================
Passed: 10/10
✅ PASS: test_hash_collision_attempt
✅ PASS: test_replay_attack
✅ PASS: test_tampering_detection
...
============================================================
```

## When a test fails

- ❌ Hash collision: Upgrade hash algorithm; verify implementation
- ❌ Replay accepted: Add invocation ID deduplication; set expiration
- ❌ Tampering not detected: Ensure hash covers all mutable fields
- ❌ Injection accepted: Add allowlist; use parameterized queries
- ❌ Oversized payload accepted: Set `max_body_size`; validate early
- ❌ Unicode bypass: Apply normalization before all comparisons
- ❌ Timing leak: Switch to `hmac.compare_digest`
- ❌ SSIP bypass: Enforce required fields in Pydantic models
- ❌ Race condition: Add unique constraint or atomic CAS operation
- ❌ Performance degraded: Enable async logging; sample audits; scale workers

## Penetration testing (external)

For production readiness:

- Engage a third-party pentester (OWASP Top 10, API Security)
- Request signed report for compliance
- Store findings in `Evidence/` and track remediation

## Contact

- Security issues: [Mythara.Engine@yahoo.com](mailto:Mythara.Engine@yahoo.com) (private disclosure)
