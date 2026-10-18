#!/usr/bin/env python3
"""
Mythara Engine - Rate Limiting Middleware
Prevent abuse and DDoS attacks with per-user and per-org rate limiting.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple, Optional
import time
import logging

logger = logging.getLogger(__name__)

# Try to import Redis for distributed rate limiting
try:
    from redis_cache import cache as redis_cache

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning(
        "Redis not available for rate limiting - using in-memory (not recommended for production)"
    )


# Process-wide in-memory rate-limit counters (development fallback only).
# Shared across middleware instances; tests reset it between cases.
_IN_MEMORY_STORE: Dict[str, Tuple[int, float]] = {}


def reset_in_memory_store() -> None:
    """Clear in-memory rate-limit counters (test isolation)."""
    _IN_MEMORY_STORE.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with multiple tiers:
    - IP-based: Prevent DDoS from single IP
    - API key-based: Per-user limits
    - Organization-based: Per-org limits
    - Endpoint-specific: Different limits per endpoint type
    """

    def __init__(self, app, default_limit: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI app instance
            default_limit: Default requests per window
            window_seconds: Time window in seconds
        """
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds

        # In-memory fallback (not distributed - for development only).
        # Module-level so it is shared across middleware instances in this
        # process and resettable by tests (see reset_in_memory_store).
        self._memory_store = _IN_MEMORY_STORE

        # Endpoint-specific rate limits
        self.endpoint_limits = {
            "/v1/clauses/invoke": (50, 60),  # 50 req/min for clause invocation
            "/v1/soul/cradle": (30, 60),  # 30 req/min for paradox creation
            "/v1/soul/indifference": (10, 60),  # 10 req/min for indifference detection
            "/health": (
                1000,
                60,
            ),  # 1000 req/min for health checks (load balancers need high limit)
            "/api/docs": (100, 60),  # 100 req/min for docs (interactive documentation)
            "/openapi.json": (100, 60),  # 100 req/min for OpenAPI spec
            "/api/redoc": (100, 60),  # 100 req/min for ReDoc
        }

        # Public endpoint limits (unauthenticated per-IP - DDoS protection)
        # These are STRICTER limits applied per IP address for public endpoints
        self.public_endpoint_ip_limits = {
            "/health": (
                100,
                60,
            ),  # 100 req/min per IP (down from 1000 for DDoS protection)
            "/api/docs": (20, 60),  # 20 req/min per IP (reasonable for docs browsing)
            "/openapi.json": (10, 60),  # 10 req/min per IP (spec rarely changes)
            "/api/redoc": (20, 60),  # 20 req/min per IP (docs browsing)
            "/": (50, 60),  # 50 req/min per IP (root endpoint)
        }

        # Tier-based limits (override for paid tiers)
        self.tier_limits = {
            "free": (100, 60),  # 100 req/min
            "pilot": (500, 60),  # 500 req/min
            "enterprise": (5000, 60),  # 5000 req/min
            "sovereign": (10000, 60),  # 10000 req/min (unlimited)
        }

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limits.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response or 429 Too Many Requests
        """
        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract identifiers for rate limiting
        ip_address = self._get_client_ip(request)
        api_key = self._extract_api_key(request)
        org_id = self._extract_org_id(request)
        path = request.url.path

        # Determine rate limit based on endpoint and tier
        max_requests, window = self._get_rate_limit(path, api_key)

        # For public endpoints without auth, apply STRICTER per-IP limits (DDoS protection)
        if not api_key and path in self.public_endpoint_ip_limits:
            ip_limit, ip_window = self.public_endpoint_ip_limits[path]
            ip_allowed, ip_remaining = self._check_limit(
                f"public_ip:{path}:{ip_address}", ip_limit, ip_window
            )

            if not ip_allowed:
                logger.warning(
                    f"🚫 Public endpoint rate limit exceeded for IP {ip_address} on {path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for unauthenticated requests. Try again in {ip_window} seconds.",
                    headers={
                        "Retry-After": str(ip_window),
                        "X-RateLimit-Limit": str(ip_limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )
        else:
            # Check IP-based rate limit (global DDoS protection for authenticated requests)
            ip_allowed, ip_remaining = self._check_limit(
                f"ip:{ip_address}",
                max_requests * 2,  # IPs get 2x limit (multiple users behind NAT)
                window,
            )

            if not ip_allowed:
                logger.warning(f"🚫 Rate limit exceeded for IP: {ip_address}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {window} seconds.",
                    headers={"Retry-After": str(window)},
                )

        # Check API key-based rate limit
        if api_key:
            key_allowed, key_remaining = self._check_limit(
                f"key:{api_key}", max_requests, window
            )

            if not key_allowed:
                logger.warning(f"🚫 Rate limit exceeded for API key: {api_key[:16]}...")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {window} seconds.",
                    headers={"Retry-After": str(window)},
                )

            # Add rate limit headers to response
            remaining = key_remaining

        # Check organization-based rate limit (if applicable)
        if org_id:
            org_limit = max_requests * 10  # Orgs get 10x per-user limit

            org_allowed, org_remaining = self._check_limit(
                f"org:{org_id}", org_limit, window
            )

            if not org_allowed:
                logger.warning(f"🚫 Rate limit exceeded for organization: {org_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Organization rate limit exceeded. Try again in {window} seconds.",
                    headers={"Retry-After": str(window)},
                )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        if api_key:
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)

        return response

    def _check_limit(
        self, identifier: str, max_requests: int, window: int
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded.

        Args:
            identifier: Unique identifier (ip:X.X.X.X, key:sk_xxx, org:ORG_xxx)
            max_requests: Max requests allowed
            window: Time window in seconds

        Returns:
            (is_allowed, requests_remaining)
        """
        # Use Redis if available (distributed rate limiting)
        if REDIS_AVAILABLE and redis_cache.client is not None:
            try:
                return redis_cache.check_rate_limit(identifier, max_requests, window)
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}, falling back to memory")

        # In-memory fallback (NOT distributed - development only)
        current_time = time.time()

        if identifier in self._memory_store:
            count, timestamp = self._memory_store[identifier]

            # Reset if window expired
            if current_time - timestamp > window:
                self._memory_store[identifier] = (1, current_time)
                return True, max_requests - 1

            # Check limit
            if count >= max_requests:
                return False, 0

            # Increment counter
            self._memory_store[identifier] = (count + 1, timestamp)
            return True, max_requests - count - 1

        # First request
        self._memory_store[identifier] = (1, current_time)
        return True, max_requests - 1

    def _get_rate_limit(self, path: str, api_key: Optional[str]) -> Tuple[int, int]:
        """
        Get rate limit for specific endpoint and tier.

        Args:
            path: Request path
            api_key: API key (determines tier)

        Returns:
            (max_requests, window_seconds)
        """
        # Check endpoint-specific limits first
        for endpoint, (limit, window) in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit, window

        # Determine tier from API key
        tier = self._get_api_key_tier(api_key)

        if tier in self.tier_limits:
            return self.tier_limits[tier]

        # Default limit
        return self.default_limit, self.window_seconds

    def _get_api_key_tier(self, api_key: Optional[str]) -> str:
        """
        Determine API key tier (free, pilot, enterprise, sovereign).

        Args:
            api_key: API key

        Returns:
            Tier name
        """
        if not api_key:
            return "free"

        # Extract tier from API key prefix.
        # NOTE: the legacy "sk_pilot_" prefix is intentionally NOT honored —
        # pilot keys were exposed and must not grant any tier.
        if api_key.startswith("sk_sovereign_"):
            return "sovereign"
        elif api_key.startswith("sk_enterprise_"):
            return "enterprise"
        else:
            return "free"

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address (handles proxies).

        Args:
            request: HTTP request

        Returns:
            IP address
        """
        # Check X-Forwarded-For header (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"

    def _extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extract API key from Authorization header.

        Args:
            request: HTTP request

        Returns:
            API key or None
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        # Bearer token format
        if auth_header.startswith("Bearer "):
            return auth_header[7:]

        return None

    def _extract_org_id(self, request: Request) -> Optional[str]:
        """
        Extract organization ID from request (header or API key metadata).

        Args:
            request: HTTP request

        Returns:
            Organization ID or None
        """
        # Check X-Organization-ID header
        org_id = request.headers.get("X-Organization-ID")
        if org_id:
            return org_id

        # TODO: Look up org_id from API key in database
        # For now, return None
        return None


# ===================== DECORATOR FOR FUNCTION-LEVEL RATE LIMITING =====================


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Decorator for function-level rate limiting.

    Usage:
        @rate_limit(max_requests=5, window_seconds=60)
        async def my_endpoint():
            ...

    Args:
        max_requests: Max requests allowed
        window_seconds: Time window in seconds
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request = kwargs.get("request") or (
                args[0] if args and isinstance(args[0], Request) else None
            )

            if not request:
                # No request object, skip rate limiting
                return await func(*args, **kwargs)

            # Get identifier
            api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
            identifier = f"func:{func.__name__}:{api_key or request.client.host}"

            # Check rate limit
            middleware = RateLimitMiddleware(None)
            allowed, remaining = middleware._check_limit(
                identifier, max_requests, window_seconds
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {func.__name__}. Try again in {window_seconds} seconds.",
                    headers={"Retry-After": str(window_seconds)},
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
