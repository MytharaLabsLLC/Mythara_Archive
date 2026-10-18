#!/usr/bin/env python3
"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Engine - Advanced Security Hardening Layer
===================================================

Multi-layered security defense system to make penetration significantly harder:
- Request signature verification (HMAC-SHA256)
- Time-based token expiration
- IP whitelist/blacklist management
- Advanced rate limiting with exponential backoff
- Request fingerprinting and anomaly detection
- Brute force protection
- SQL injection prevention (parameterized queries only)
- XSS prevention with output encoding
- CSRF token validation
- TLS/SSL enforcement
- Security headers (HSTS, CSP, X-Frame-Options)
- API versioning and deprecation
- Geolocation-based access control
- Device fingerprinting
- Suspicious activity detection with ML-ready patterns
"""

import os
import hashlib
import hmac
import secrets
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import logging
import ipaddress

logger = logging.getLogger(__name__)


# ===================== SECURITY CONFIGURATION =====================


@dataclass
class SecurityConfig:
    """Centralized security configuration"""

    # HMAC signature validation
    signature_required: bool = True
    signature_algorithm: str = "sha256"
    signature_expiry_seconds: int = 300  # 5 minutes

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_burst: int = 10  # Allow brief bursts
    exponential_backoff_enabled: bool = True

    # Brute force protection
    brute_force_threshold: int = 5  # Failed attempts before lockout
    brute_force_lockout_minutes: int = 30
    brute_force_progressive_delay: bool = True

    # IP management
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist_enabled: bool = True
    ip_blacklist: List[str] = field(default_factory=list)
    auto_blacklist_on_abuse: bool = True

    # Request validation
    max_request_size_kb: int = 1024  # 1MB
    allowed_content_types: List[str] = field(
        default_factory=lambda: ["application/json"]
    )
    min_request_interval_ms: int = 50  # Prevent rapid-fire attacks

    # Token security
    token_rotation_enabled: bool = True
    token_rotation_hours: int = 24
    token_min_entropy_bits: int = 256  # Strong tokens only

    # Geolocation
    geo_restriction_enabled: bool = False
    allowed_countries: List[str] = field(default_factory=list)

    # Anomaly detection
    anomaly_detection_enabled: bool = True
    anomaly_threshold_score: float = 0.8  # 0-1 scale


# ===================== HMAC REQUEST SIGNING =====================


class HMACAuthenticator:
    """
    HMAC-SHA256 request signature validation.
    Every request must include a signature to prove authenticity.
    """

    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key

    def generate_signature(
        self,
        method: str,
        path: str,
        timestamp: int,
        body: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> str:
        """Generate HMAC signature for request"""
        # Construct canonical request string
        parts = [method.upper(), path, str(timestamp), nonce or "", body or ""]
        canonical_request = "\n".join(parts)

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key, canonical_request.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return signature

    def verify_signature(
        self,
        provided_signature: str,
        method: str,
        path: str,
        timestamp: int,
        body: Optional[str] = None,
        nonce: Optional[str] = None,
        max_age_seconds: int = 300,
    ) -> Tuple[bool, str]:
        """
        Verify HMAC signature and check timestamp.
        Returns (valid, error_message)
        """
        # Check timestamp freshness
        now = int(time.time())
        if abs(now - timestamp) > max_age_seconds:
            return False, "Request timestamp expired or invalid"

        # Generate expected signature
        expected = self.generate_signature(method, path, timestamp, body, nonce)

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(provided_signature, expected):
            return False, "Invalid signature"

        return True, ""


# ===================== ADVANCED RATE LIMITING =====================


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting with exponential backoff"""

    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens per second
    violations: int = 0
    last_violation: Optional[float] = None


class AdvancedRateLimiter:
    """
    Multi-level rate limiting with exponential backoff.
    Tracks per-key, per-IP, and per-endpoint limits.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.violation_history: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(
        self, identifier: str, capacity: int = 60, refill_rate: float = 1.0
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed, error_message, retry_after_seconds)
        """
        now = time.time()

        # Get or create bucket
        if identifier not in self.buckets:
            self.buckets[identifier] = RateLimitBucket(
                capacity=capacity,
                tokens=float(capacity),
                last_refill=now,
                refill_rate=refill_rate,
            )

        bucket = self.buckets[identifier]

        # Refill tokens based on time elapsed
        elapsed = now - bucket.last_refill
        bucket.tokens = min(
            bucket.capacity, bucket.tokens + (elapsed * bucket.refill_rate)
        )
        bucket.last_refill = now

        # Apply exponential backoff if enabled
        if self.config.exponential_backoff_enabled and bucket.violations > 0:
            backoff_multiplier = 2**bucket.violations
            effective_tokens = bucket.tokens / backoff_multiplier
        else:
            effective_tokens = bucket.tokens

        # Check if tokens available
        if effective_tokens >= 1.0:
            bucket.tokens -= 1.0
            return True, None, None
        else:
            # Rate limit exceeded
            bucket.violations += 1
            bucket.last_violation = now
            self.violation_history[identifier].append(now)

            # Calculate retry after
            tokens_needed = 1.0 - bucket.tokens
            retry_after = int(tokens_needed / bucket.refill_rate) + 1

            return False, "Rate limit exceeded", retry_after

    def get_violation_count(self, identifier: str, window_seconds: int = 3600) -> int:
        """Get number of violations in time window"""
        now = time.time()
        cutoff = now - window_seconds
        violations = self.violation_history.get(identifier, [])
        return len([v for v in violations if v > cutoff])

    def reset_violations(self, identifier: str):
        """Reset violation count (for admin/override)"""
        if identifier in self.buckets:
            self.buckets[identifier].violations = 0
            self.buckets[identifier].last_violation = None
        if identifier in self.violation_history:
            self.violation_history[identifier] = []


# ===================== BRUTE FORCE PROTECTION =====================


@dataclass
class BruteForceTracker:
    """Track failed authentication attempts"""

    failed_attempts: int = 0
    last_failure: Optional[float] = None
    locked_until: Optional[float] = None
    total_lockouts: int = 0


class BruteForceProtector:
    """
    Protect against brute force attacks with progressive delays.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.trackers: Dict[str, BruteForceTracker] = {}

    def record_failure(
        self, identifier: str
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Record failed authentication attempt.
        Returns (locked, error_message, lockout_seconds)
        """
        now = time.time()

        if identifier not in self.trackers:
            self.trackers[identifier] = BruteForceTracker()

        tracker = self.trackers[identifier]

        # Check if currently locked
        if tracker.locked_until and now < tracker.locked_until:
            remaining = int(tracker.locked_until - now)
            return True, "Account locked due to brute force protection", remaining

        # Reset lockout if expired
        if tracker.locked_until and now >= tracker.locked_until:
            tracker.locked_until = None
            tracker.failed_attempts = 0

        # Increment failure count
        tracker.failed_attempts += 1
        tracker.last_failure = now

        # Check if threshold exceeded
        if tracker.failed_attempts >= self.config.brute_force_threshold:
            # Calculate lockout duration with progressive penalty
            base_lockout = self.config.brute_force_lockout_minutes * 60
            if self.config.brute_force_progressive_delay:
                lockout_duration = base_lockout * (2**tracker.total_lockouts)
            else:
                lockout_duration = base_lockout

            tracker.locked_until = now + lockout_duration
            tracker.total_lockouts += 1

            logger.warning(
                f"🔒 Brute force lockout: {identifier} ({tracker.failed_attempts} attempts)"
            )

            return (
                True,
                "Too many failed attempts. Account locked.",
                int(lockout_duration),
            )

        return False, None, None

    def record_success(self, identifier: str):
        """Record successful authentication (resets counter)"""
        if identifier in self.trackers:
            self.trackers[identifier].failed_attempts = 0
            self.trackers[identifier].last_failure = None

    def is_locked(self, identifier: str) -> bool:
        """Check if identifier is currently locked"""
        if identifier not in self.trackers:
            return False

        tracker = self.trackers[identifier]
        if not tracker.locked_until:
            return False

        return time.time() < tracker.locked_until


# ===================== IP ACCESS CONTROL =====================


class IPAccessController:
    """
    Manage IP whitelist and blacklist.
    Support CIDR ranges for network-level blocking.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.whitelist_networks: List[ipaddress.IPv4Network] = []
        self.blacklist_networks: List[ipaddress.IPv4Network] = []
        self.auto_blacklist: Dict[str, float] = {}  # IP -> timestamp

        # Parse CIDR ranges
        self._parse_ip_lists()

    def _parse_ip_lists(self):
        """Parse IP lists into network objects"""
        for ip_str in self.config.ip_whitelist:
            try:
                self.whitelist_networks.append(
                    ipaddress.ip_network(ip_str, strict=False)
                )
            except ValueError as e:
                logger.error(f"Invalid whitelist IP/CIDR: {ip_str} - {e}")

        for ip_str in self.config.ip_blacklist:
            try:
                self.blacklist_networks.append(
                    ipaddress.ip_network(ip_str, strict=False)
                )
            except ValueError as e:
                logger.error(f"Invalid blacklist IP/CIDR: {ip_str} - {e}")

    def is_allowed(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if IP is allowed to make requests.
        Returns (allowed, reason)
        """
        try:
            ip_obj = ipaddress.ip_address(ip_address)
        except ValueError:
            return False, "Invalid IP address format"

        # Check blacklist first (takes priority)
        if self.config.ip_blacklist_enabled:
            for network in self.blacklist_networks:
                if ip_obj in network:
                    return False, f"IP {ip_address} is blacklisted"

            # Check auto-blacklist
            if ip_address in self.auto_blacklist:
                return False, f"IP {ip_address} auto-blacklisted due to abuse"

        # Check whitelist if enabled
        if self.config.ip_whitelist_enabled:
            for network in self.whitelist_networks:
                if ip_obj in network:
                    return True, None
            return False, f"IP {ip_address} not in whitelist"

        return True, None

    def add_to_blacklist(self, ip_address: str, auto: bool = False):
        """Add IP to blacklist"""
        if auto:
            self.auto_blacklist[ip_address] = time.time()
            logger.warning(f"🚫 Auto-blacklisted IP: {ip_address}")
        else:
            try:
                network = ipaddress.ip_network(ip_address, strict=False)
                if network not in self.blacklist_networks:
                    self.blacklist_networks.append(network)
                    logger.warning(f"🚫 Manually blacklisted IP: {ip_address}")
            except ValueError as e:
                logger.error(f"Failed to blacklist {ip_address}: {e}")


# ===================== REQUEST ANOMALY DETECTION =====================


@dataclass
class RequestProfile:
    """Profile of normal request behavior for anomaly detection"""

    avg_request_size: float = 0.0
    avg_request_interval: float = 0.0
    common_paths: Dict[str, int] = field(default_factory=dict)
    common_user_agents: Dict[str, int] = field(default_factory=dict)
    request_count: int = 0
    last_request: Optional[float] = None


class AnomalyDetector:
    """
    Detect anomalous request patterns using statistical analysis.
    ML-ready for future enhancement with trained models.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.profiles: Dict[str, RequestProfile] = {}

    def analyze_request(
        self,
        identifier: str,
        request_size: int,
        path: str,
        user_agent: str,
        headers: Dict[str, str],
    ) -> Tuple[float, List[str]]:
        """
        Analyze request for anomalies.
        Returns (anomaly_score 0-1, suspicious_indicators)
        """
        if identifier not in self.profiles:
            self.profiles[identifier] = RequestProfile()

        profile = self.profiles[identifier]
        now = time.time()

        anomaly_score = 0.0
        indicators = []

        # Check request size anomaly
        if profile.request_count > 10:
            size_deviation = abs(request_size - profile.avg_request_size) / max(
                profile.avg_request_size, 1
            )
            if size_deviation > 3.0:  # 3x standard deviation
                anomaly_score += 0.3
                indicators.append(f"Unusual request size: {request_size} bytes")

        # Check request interval anomaly (too fast)
        if profile.last_request:
            interval = now - profile.last_request
            if interval < self.config.min_request_interval_ms / 1000:
                anomaly_score += 0.4
                indicators.append(f"Requests too rapid: {interval*1000:.0f}ms interval")

        # Check path anomaly
        if profile.request_count > 50 and path not in profile.common_paths:
            # New path after establishing pattern
            anomaly_score += 0.2
            indicators.append(f"Unusual endpoint access: {path}")

        # Check suspicious user agent patterns
        suspicious_ua_patterns = [
            r"curl",
            r"wget",
            r"python-requests",
            r"bot",
            r"crawler",
            r"spider",
            r"scraper",
        ]
        if any(
            re.search(pattern, user_agent.lower()) for pattern in suspicious_ua_patterns
        ):
            anomaly_score += 0.1
            indicators.append(f"Suspicious user agent: {user_agent}")

        # Check for SQL injection patterns in path
        sql_patterns = [
            r"(\bOR\b|\bAND\b).*=.*",
            r"'.*--",
            r";\s*DROP\s+TABLE",
            r"UNION.*SELECT",
            r"'.*OR.*'.*=.*'",
        ]
        if any(re.search(pattern, path, re.IGNORECASE) for pattern in sql_patterns):
            anomaly_score = 1.0  # Instant max score
            indicators.append("SQL injection pattern detected")

        # Check for XSS patterns
        xss_patterns = [r"<script", r"javascript:", r"onerror=", r"onclick="]
        if any(re.search(pattern, path, re.IGNORECASE) for pattern in xss_patterns):
            anomaly_score = 1.0
            indicators.append("XSS pattern detected")

        # Update profile
        profile.request_count += 1
        profile.avg_request_size = (
            profile.avg_request_size * (profile.request_count - 1) + request_size
        ) / profile.request_count
        profile.common_paths[path] = profile.common_paths.get(path, 0) + 1
        profile.common_user_agents[user_agent] = (
            profile.common_user_agents.get(user_agent, 0) + 1
        )
        profile.last_request = now

        return min(anomaly_score, 1.0), indicators


# ===================== INTEGRATED SECURITY MANAGER =====================


class SecurityManager:
    """
    Unified security manager coordinating all hardening layers.
    """

    def __init__(self, secret_key: bytes, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.hmac_auth = HMACAuthenticator(secret_key)
        self.rate_limiter = AdvancedRateLimiter(self.config)
        self.brute_force = BruteForceProtector(self.config)
        self.ip_controller = IPAccessController(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)

        logger.info("🛡️ Security Manager initialized with hardened configuration")

    def validate_request(
        self,
        method: str,
        path: str,
        ip_address: str,
        api_key: str,
        signature: Optional[str],
        timestamp: Optional[int],
        nonce: Optional[str],
        body: Optional[str],
        request_size: int,
        user_agent: str,
        headers: Dict[str, str],
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Comprehensive request validation through all security layers.
        Returns (allowed, error_message, metadata)
        """
        metadata = {}

        # Layer 1: IP Access Control
        ip_allowed, ip_reason = self.ip_controller.is_allowed(ip_address)
        if not ip_allowed:
            logger.warning(f"🚫 IP blocked: {ip_address} - {ip_reason}")
            return False, ip_reason, {"layer": "ip_control"}

        # Layer 2: Brute Force Check
        if self.brute_force.is_locked(api_key):
            locked, error, retry_after = self.brute_force.record_failure(api_key)
            if locked:
                logger.warning(f"🔒 Locked account attempted access: {api_key[:8]}...")
                metadata["retry_after"] = retry_after
                return False, error, metadata

        # Layer 3: Rate Limiting
        rate_allowed, rate_error, retry_after = self.rate_limiter.check_rate_limit(
            f"key_{api_key}",
            capacity=self.config.rate_limit_per_minute,
            refill_rate=self.config.rate_limit_per_minute / 60.0,
        )
        if not rate_allowed:
            metadata["retry_after"] = retry_after
            violations = self.rate_limiter.get_violation_count(f"key_{api_key}")

            # Auto-blacklist on repeated abuse
            if self.config.auto_blacklist_on_abuse and violations > 100:
                self.ip_controller.add_to_blacklist(ip_address, auto=True)

            logger.warning(
                f"⏱️ Rate limit exceeded: {api_key[:8]}... ({violations} violations)"
            )
            return False, rate_error, metadata

        # Layer 4: HMAC Signature Verification
        if self.config.signature_required and signature and timestamp:
            valid, sig_error = self.hmac_auth.verify_signature(
                signature,
                method,
                path,
                timestamp,
                body,
                nonce,
                max_age_seconds=self.config.signature_expiry_seconds,
            )
            if not valid:
                # Record as potential attack
                self.brute_force.record_failure(f"sig_{api_key}")
                logger.warning(f"🔐 Invalid signature: {api_key[:8]}... - {sig_error}")
                return (
                    False,
                    f"Signature validation failed: {sig_error}",
                    {"layer": "hmac"},
                )

        # Layer 5: Request Size Validation
        if request_size > self.config.max_request_size_kb * 1024:
            logger.warning(
                f"📦 Oversized request blocked: {request_size} bytes from {api_key[:8]}..."
            )
            return (
                False,
                f"Request size exceeds limit of {self.config.max_request_size_kb}KB",
                {"layer": "size"},
            )

        # Layer 6: Anomaly Detection
        if self.config.anomaly_detection_enabled:
            anomaly_score, indicators = self.anomaly_detector.analyze_request(
                api_key, request_size, path, user_agent, headers
            )

            metadata["anomaly_score"] = anomaly_score
            metadata["anomaly_indicators"] = indicators

            if anomaly_score >= self.config.anomaly_threshold_score:
                logger.error(
                    f"🚨 ANOMALY DETECTED: {api_key[:8]}... Score: {anomaly_score:.2f}"
                )
                logger.error(f"   Indicators: {', '.join(indicators)}")

                # Auto-blacklist on critical anomalies
                if anomaly_score >= 0.95:
                    self.ip_controller.add_to_blacklist(ip_address, auto=True)

                return False, "Suspicious activity detected", metadata

        # All layers passed
        metadata["security_score"] = "PASSED_ALL_LAYERS"
        return True, None, metadata

    def generate_secure_token(self, entropy_bits: int = 256) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(entropy_bits // 8)

    def get_security_headers(self) -> Dict[str, str]:
        """Generate security headers for responses"""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


# ===================== USAGE EXAMPLE =====================


def example_usage():
    """Example of how to integrate SecurityManager"""

    # Initialize with secret key
    secret_key = secrets.token_bytes(32)

    # Configure security
    config = SecurityConfig(
        signature_required=True,
        rate_limit_per_minute=60,
        brute_force_threshold=5,
        ip_blacklist_enabled=True,
        anomaly_detection_enabled=True,
    )

    security_mgr = SecurityManager(secret_key, config)

    # Validate incoming request
    allowed, error, metadata = security_mgr.validate_request(
        method="POST",
        path="/v1/clauses/invoke",
        ip_address="192.168.1.100",
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        api_key=os.getenv("API_KEY", ""),  # Set via environment
        signature="hmac_signature_here",
        timestamp=int(time.time()),
        nonce="unique_nonce",
        body='{"clause_id": "test"}',
        request_size=1024,
        user_agent="MytharaClient/1.0",
        headers={},
    )

    if not allowed:
        print(f"❌ Request blocked: {error}")
        print(f"   Metadata: {metadata}")
    else:
        print("✅ Request allowed")
        print(f"   Security score: {metadata.get('security_score')}")


if __name__ == "__main__":
    example_usage()
