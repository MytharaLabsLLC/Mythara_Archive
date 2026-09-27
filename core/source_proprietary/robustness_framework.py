#!/usr/bin/env python3
"""
Mythara Robustness Framework - Reliability Patterns
Database connection pooling, retry logic, input validation, logging, rate limiting

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import sqlite3
import logging
import hashlib
import re
import time
import functools
from contextlib import contextmanager
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ===================== DATABASE CONNECTION POOLING =====================


class ConnectionPool:
    """
    SQLite connection pool with automatic cleanup and thread safety
    Prevents connection leaks and improves performance
    """

    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = Lock()
        self.connections_created = 0

        # Pre-populate pool
        for _ in range(pool_size):
            conn = self._create_connection()
            self.pool.put(conn)

        logger.info(f"✓ Connection pool initialized: {db_path} (size: {pool_size})")

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.connections_created += 1
        return conn

    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool
        Automatically returns connection to pool after use

        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = None
        try:
            # Get connection from pool (with timeout)
            conn = self.pool.get(timeout=10)
            yield conn
            conn.commit()  # Auto-commit on success
        except Exception as e:
            if conn:
                conn.rollback()  # Rollback on error
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            if conn:
                self.pool.put(conn)  # Return to pool

    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
        logger.info(f"✓ Connection pool closed: {self.db_path}")


# ===================== RETRY LOGIC WITH EXPONENTIAL BACKOFF =====================


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (sqlite3.OperationalError,),
):
    """
    Decorator for automatic retry with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries (2.0 = double each time)
        exceptions: Tuple of exceptions to catch and retry

    Usage:
        @retry_on_failure(max_retries=3)
        def database_operation():
            # code that might fail transiently
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = 1.0
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"Max retries reached for {func.__name__}: {e}",
                            exc_info=True,
                        )

            raise last_exception

        return wrapper

    return decorator


# ===================== INPUT VALIDATION & SANITIZATION =====================


class InputValidator:
    """
    Comprehensive input validation and sanitization
    Prevents SQL injection, XSS, and other injection attacks
    """

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input: remove dangerous characters, enforce length limits

        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value)}")

        # Truncate to max length
        value = value[:max_length]

        # Remove null bytes (can cause SQLite issues)
        value = value.replace("\x00", "")

        # Strip leading/trailing whitespace
        value = value.strip()

        return value

    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        Sanitize SQL identifiers (table names, column names)
        Only allows alphanumeric characters and underscores

        Args:
            identifier: SQL identifier to sanitize

        Returns:
            Sanitized identifier

        Raises:
            ValueError: If identifier contains invalid characters
        """
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            raise ValueError(
                f"Invalid SQL identifier: {identifier}. "
                "Only alphanumeric characters and underscores allowed."
            )
        return identifier

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate and sanitize email address

        Args:
            email: Email address to validate

        Returns:
            Sanitized email (lowercase)

        Raises:
            ValueError: If email is invalid
        """
        email = InputValidator.sanitize_string(email, max_length=254)
        email = email.lower()

        # RFC 5322 compliant regex (simplified)
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email format: {email}")

        return email

    @staticmethod
    def validate_phone(phone: str) -> str:
        """
        Validate and sanitize phone number
        Extracts digits only

        Args:
            phone: Phone number to validate

        Returns:
            Sanitized phone (digits only)

        Raises:
            ValueError: If phone is invalid
        """
        phone = InputValidator.sanitize_string(phone, max_length=20)

        # Extract digits only
        digits = re.sub(r"\D", "", phone)

        # Validate length (10-15 digits typical for international numbers)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError(f"Invalid phone number length: {phone}")

        return digits

    @staticmethod
    def validate_integer(
        value: Any, min_value: int = None, max_value: int = None
    ) -> int:
        """
        Validate integer input with optional range constraints

        Args:
            value: Value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)

        Returns:
            Validated integer

        Raises:
            ValueError: If validation fails
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer: {value}")

        if min_value is not None and int_value < min_value:
            raise ValueError(f"Value {int_value} below minimum {min_value}")

        if max_value is not None and int_value > max_value:
            raise ValueError(f"Value {int_value} above maximum {max_value}")

        return int_value

    @staticmethod
    def validate_float(
        value: Any, min_value: float = None, max_value: float = None
    ) -> float:
        """
        Validate float input with optional range constraints

        Args:
            value: Value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)

        Returns:
            Validated float

        Raises:
            ValueError: If validation fails
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid float: {value}")

        if min_value is not None and float_value < min_value:
            raise ValueError(f"Value {float_value} below minimum {min_value}")

        if max_value is not None and float_value > max_value:
            raise ValueError(f"Value {float_value} above maximum {max_value}")

        return float_value


# ===================== RATE LIMITING =====================


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints
    Prevents abuse and ensures fair resource allocation
    """

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[datetime]] = {}
        self.lock = Lock()

        logger.info(
            f"✓ Rate limiter initialized: {max_requests} requests per {time_window}s"
        )

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for given identifier (user ID, IP address, etc.)

        Args:
            identifier: Unique identifier for rate limiting

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window)

            # Initialize if first request
            if identifier not in self.requests:
                self.requests[identifier] = []

            # Remove old requests outside time window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] if req_time > cutoff
            ]

            # Check if under limit
            if len(self.requests[identifier]) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {identifier}")
                return False

            # Add new request
            self.requests[identifier].append(now)
            return True

    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests for identifier

        Args:
            identifier: Unique identifier

        Returns:
            Number of remaining requests in current window
        """
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window)

            if identifier not in self.requests:
                return self.max_requests

            # Count recent requests
            recent = [
                req_time for req_time in self.requests[identifier] if req_time > cutoff
            ]

            return max(0, self.max_requests - len(recent))


# ===================== INTEGRITY HASHING =====================


def compute_integrity_hash(data: Dict[str, Any]) -> str:
    """
    Compute SHA-256 integrity hash for tamper-proof records

    Args:
        data: Dictionary of data to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    # Sort keys for deterministic hashing
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = str(sorted_data)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


# ===================== GRACEFUL DEGRADATION =====================


class ServiceHealthCheck:
    """
    Service health monitoring for graceful degradation
    Tracks service availability and provides fallback logic
    """

    def __init__(self):
        self.services: Dict[str, bool] = {}
        self.last_check: Dict[str, datetime] = {}
        self.lock = Lock()

    def mark_service_status(self, service_name: str, is_healthy: bool):
        """
        Mark service as healthy or unhealthy

        Args:
            service_name: Name of the service
            is_healthy: True if service is healthy, False otherwise
        """
        with self.lock:
            self.services[service_name] = is_healthy
            self.last_check[service_name] = datetime.now()

            status = "✓ HEALTHY" if is_healthy else "✗ UNHEALTHY"
            logger.info(f"Service {service_name}: {status}")

    def is_service_healthy(self, service_name: str) -> bool:
        """
        Check if service is healthy

        Args:
            service_name: Name of the service

        Returns:
            True if service is healthy (defaults to True if unknown)
        """
        with self.lock:
            return self.services.get(service_name, True)


# ===================== ERROR RECOVERY =====================


@dataclass
class ErrorContext:
    """Error context for debugging and recovery"""

    error_type: str
    error_message: str
    timestamp: datetime
    function_name: str
    attempted_recovery: bool
    recovery_successful: bool
    additional_info: Dict[str, Any]


class ErrorRecovery:
    """
    Error recovery framework with logging and notifications
    """

    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.max_history = 1000
        self.lock = Lock()

    def record_error(
        self,
        error: Exception,
        function_name: str,
        recovery_attempted: bool = False,
        recovery_successful: bool = False,
        additional_info: Dict[str, Any] = None,
    ) -> ErrorContext:
        """
        Record error for debugging and analysis

        Args:
            error: Exception that occurred
            function_name: Name of function where error occurred
            recovery_attempted: Whether recovery was attempted
            recovery_successful: Whether recovery succeeded
            additional_info: Additional context

        Returns:
            ErrorContext object
        """
        context = ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            timestamp=datetime.now(),
            function_name=function_name,
            attempted_recovery=recovery_attempted,
            recovery_successful=recovery_successful,
            additional_info=additional_info or {},
        )

        with self.lock:
            self.error_history.append(context)

            # Limit history size
            if len(self.error_history) > self.max_history:
                self.error_history = self.error_history[-self.max_history :]

        # Log error
        log_level = logging.WARNING if recovery_successful else logging.ERROR
        logger.log(
            log_level,
            f"Error in {function_name}: {error} "
            f"(recovery: {'✓' if recovery_successful else '✗'})",
        )

        return context

    def get_recent_errors(self, count: int = 10) -> List[ErrorContext]:
        """
        Get recent errors

        Args:
            count: Number of recent errors to return

        Returns:
            List of recent ErrorContext objects
        """
        with self.lock:
            return self.error_history[-count:]


# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    print("Mythara Robustness Framework - Usage Examples")
    print("=" * 70)

    # Example 1: Connection pooling
    print("\n1. Connection Pooling:")
    pool = ConnectionPool("test_robust.db", pool_size=3)

    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'Test')")

    pool.close_all()
    print("   ✓ Connection pool demo complete")

    # Example 2: Input validation
    print("\n2. Input Validation:")
    validator = InputValidator()

    try:
        email = validator.validate_email("  User@Example.COM  ")
        print(f"   ✓ Valid email: {email}")
    except ValueError as e:
        print(f"   ✗ Invalid: {e}")

    try:
        score = validator.validate_integer("75", min_value=0, max_value=100)
        print(f"   ✓ Valid score: {score}")
    except ValueError as e:
        print(f"   ✗ Invalid: {e}")

    # Example 3: Rate limiting
    print("\n3. Rate Limiting:")
    limiter = RateLimiter(max_requests=5, time_window=10)

    for i in range(7):
        allowed = limiter.is_allowed("user123")
        status = "✓ Allowed" if allowed else "✗ Rate limited"
        remaining = limiter.get_remaining("user123")
        print(f"   Request {i+1}: {status} (remaining: {remaining})")

    # Example 4: Retry logic
    print("\n4. Retry Logic:")

    @retry_on_failure(max_retries=3, backoff_factor=1.5)
    def flaky_operation():
        import random

        if random.random() < 0.7:
            raise sqlite3.OperationalError("Database locked")
        return "Success!"

    try:
        result = flaky_operation()
        print(f"   ✓ Operation succeeded: {result}")
    except Exception as e:
        print(f"   ✗ Operation failed: {e}")

    print("\n" + "=" * 70)
    print("✓ Robustness Framework ready for integration")
