#!/usr/bin/env python3
"""
Mythara Engine - Redis Cache Layer
Persistent state management for Blessings Reservoir and Soul Cradle data.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import redis
import json
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Redis connection URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"


class RedisCache:
    """
    Redis-backed cache for Mythara Engine state management.

    Features:
    - Blessings Reservoir state persistence
    - Soul Cradle paradox history
    - API key session management
    - Rate limiting counters
    """

    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis connection with connection pooling.

        Args:
            url: Redis connection URL (defaults to REDIS_URL env var)
        """
        self.url = url or REDIS_URL
        self.enabled = REDIS_ENABLED

        if not self.enabled:
            logger.warning(
                "⚠️ Redis is DISABLED. Using in-memory fallback (data will not persist)."
            )
            self.client = None
            self._memory_store: Dict[str, Any] = {}
            return

        try:
            # Create connection pool for efficient connection reuse
            self.pool = redis.ConnectionPool.from_url(
                self.url,
                max_connections=20,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                decode_responses=True,  # Auto-decode bytes to strings
            )

            self.client = redis.Redis(connection_pool=self.pool)

            # Test connection
            self.client.ping()
            logger.info(f"✅ Redis connected: {self.url}")

        except redis.ConnectionError as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning(
                "⚠️ Falling back to in-memory storage (data will not persist)"
            )
            self.client = None
            self._memory_store: Dict[str, Any] = {}

    # ===================== GENERIC KEY-VALUE OPERATIONS =====================

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set a key-value pair with optional expiration.

        Args:
            key: Cache key
            value: Value to store (will be JSON-serialized)
            expire: Optional TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.client is None:
                self._memory_store[key] = value
                return True

            serialized = json.dumps(value, default=str)

            if expire:
                return self.client.setex(key, expire, serialized)
            else:
                return self.client.set(key, serialized)

        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.

        Args:
            key: Cache key

        Returns:
            Deserialized value or None if not found
        """
        try:
            if self.client is None:
                return self._memory_store.get(key)

            value = self.client.get(key)
            if value is None:
                return None

            return json.loads(value)

        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            if self.client is None:
                if key in self._memory_store:
                    del self._memory_store[key]
                return True

            return bool(self.client.delete(key))

        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if self.client is None:
                return key in self._memory_store

            return bool(self.client.exists(key))

        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    # ===================== BLESSINGS RESERVOIR STATE =====================

    def get_br_state(self) -> Dict[str, Any]:
        """
        Get Blessings Reservoir state.

        Returns:
            BR state dict with reservoir_score, total_blessings, overflow_events
        """
        state = self.get("mythara:br_state")

        if state is None:
            # Initialize default state
            default_state = {
                "reservoir_score": 0.82,
                "total_blessings": 42000,
                "overflow_events": 3,
                "last_update": datetime.utcnow().isoformat() + "Z",
            }
            self.set("mythara:br_state", default_state)
            return default_state

        return state

    def update_br_state(self, updates: Dict[str, Any]) -> bool:
        """
        Update Blessings Reservoir state.

        Args:
            updates: Dict of fields to update (reservoir_score, total_blessings, etc.)

        Returns:
            True if successful
        """
        current_state = self.get_br_state()
        current_state.update(updates)
        current_state["last_update"] = datetime.utcnow().isoformat() + "Z"

        return self.set("mythara:br_state", current_state)

    def increment_blessings(self, delta: int) -> int:
        """
        Increment total_blessings atomically.

        Args:
            delta: Amount to add

        Returns:
            New total_blessings value
        """
        if self.client is None:
            state = self.get_br_state()
            state["total_blessings"] += delta
            self.set("mythara:br_state", state)
            return state["total_blessings"]

        # Use Redis HINCRBY for atomic increment
        new_total = self.client.hincrby(
            "mythara:br_state_hash", "total_blessings", delta
        )

        # Update last_update timestamp
        self.client.hset(
            "mythara:br_state_hash", "last_update", datetime.utcnow().isoformat() + "Z"
        )

        return new_total

    # ===================== SOUL CRADLE PARADOX STORAGE =====================

    def store_paradox(self, user_id: str, paradox: Dict[str, Any]) -> bool:
        """
        Store a Soul Cradle paradox for a user.

        Args:
            user_id: User's unique ID
            paradox: Paradox dict with timestamp, unresolved_score, etc.

        Returns:
            True if successful
        """
        key = f"mythara:paradoxes:{user_id}"

        try:
            if self.client is None:
                if key not in self._memory_store:
                    self._memory_store[key] = []
                self._memory_store[key].append(paradox)
                return True

            # Store as list (RPUSH for append)
            self.client.rpush(key, json.dumps(paradox, default=str))

            # Set expiration (keep 90 days of paradox history)
            self.client.expire(key, 90 * 24 * 60 * 60)

            return True

        except Exception as e:
            logger.error(f"Error storing paradox: {e}")
            return False

    def get_user_paradoxes(
        self,
        user_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get paradoxes for a user.

        Args:
            user_id: User's unique ID
            limit: Maximum number of paradoxes to return (most recent)
            since: Only return paradoxes after this datetime

        Returns:
            List of paradox dicts
        """
        key = f"mythara:paradoxes:{user_id}"

        try:
            if self.client is None:
                paradoxes = self._memory_store.get(key, [])
            else:
                # Get all paradoxes from list
                raw_paradoxes = self.client.lrange(key, 0, -1)
                paradoxes = [json.loads(p) for p in raw_paradoxes]

            # Filter by timestamp if specified
            if since:
                paradoxes = [
                    p
                    for p in paradoxes
                    if datetime.fromisoformat(p["timestamp"].replace("Z", "")) >= since
                ]

            # Sort by timestamp descending (most recent first)
            paradoxes.sort(key=lambda p: p["timestamp"], reverse=True)

            # Apply limit
            if limit:
                paradoxes = paradoxes[:limit]

            return paradoxes

        except Exception as e:
            logger.error(f"Error retrieving paradoxes: {e}")
            return []

    # ===================== RATE LIMITING =====================

    def check_rate_limit(
        self, identifier: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded using sliding window.

        Args:
            identifier: User ID, IP address, or API key
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, requests_remaining)
        """
        key = f"mythara:ratelimit:{identifier}"

        try:
            if self.client is None:
                # In-memory fallback (not accurate across processes)
                current = self._memory_store.get(key, 0)
                if current >= max_requests:
                    return False, 0
                self._memory_store[key] = current + 1
                return True, max_requests - current - 1

            # Use Redis for accurate distributed rate limiting
            current = self.client.get(key)

            if current is None:
                # First request in window
                self.client.setex(key, window_seconds, 1)
                return True, max_requests - 1

            current = int(current)

            if current >= max_requests:
                return False, 0

            # Increment counter
            self.client.incr(key)
            return True, max_requests - current - 1

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, max_requests  # Fail open on error

    # ===================== SESSION MANAGEMENT =====================

    def create_session(
        self, api_key: str, metadata: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """
        Create API session with metadata.

        Args:
            api_key: API key identifier
            metadata: Session data (user_id, org_id, permissions, etc.)
            ttl: Session lifetime in seconds

        Returns:
            True if successful
        """
        key = f"mythara:session:{api_key}"
        metadata["created_at"] = datetime.utcnow().isoformat()

        return self.set(key, metadata, expire=ttl)

    def get_session(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get session metadata by API key."""
        key = f"mythara:session:{api_key}"
        return self.get(key)

    def invalidate_session(self, api_key: str) -> bool:
        """Invalidate/logout session."""
        key = f"mythara:session:{api_key}"
        return self.delete(key)

    # ===================== HEALTH CHECK =====================

    def health_check(self) -> Dict[str, Any]:
        """
        Check Redis connection health.

        Returns:
            Health status dict
        """
        if self.client is None:
            return {
                "status": "degraded",
                "message": "Using in-memory fallback",
                "connected": False,
            }

        try:
            self.client.ping()
            info = self.client.info()

            return {
                "status": "healthy",
                "connected": True,
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
            }

        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    def close(self) -> None:
        """
        Close Redis connection pool gracefully.

        Call this during application shutdown to release connections.
        """
        try:
            if self.client is not None:
                self.client.close()
                if hasattr(self, "pool"):
                    self.pool.disconnect()
                logger.info("✅ Redis connection pool closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# Global cache instance
cache = RedisCache()


# ===================== CONVENIENCE FUNCTIONS =====================


def get_br_state() -> Dict[str, Any]:
    """Get Blessings Reservoir state."""
    return cache.get_br_state()


def update_br_state(updates: Dict[str, Any]) -> bool:
    """Update BR state."""
    return cache.update_br_state(updates)


def increment_blessings(delta: int) -> int:
    """Increment blessings atomically."""
    return cache.increment_blessings(delta)


def store_paradox(user_id: str, paradox: Dict[str, Any]) -> bool:
    """Store user paradox."""
    return cache.store_paradox(user_id, paradox)


def get_user_paradoxes(
    user_id: str, limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get user's paradoxes."""
    return cache.get_user_paradoxes(user_id, limit=limit)


def check_rate_limit(
    identifier: str, max_requests: int = 100, window_seconds: int = 60
) -> tuple[bool, int]:
    """Check rate limit."""
    return cache.check_rate_limit(identifier, max_requests, window_seconds)
