#!/usr/bin/env python3
"""
Mythara Engine - Structured Logging
Production-grade logging with correlation IDs and structured output.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Context variable for correlation ID (thread-safe)
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Compatible with ELK, Splunk, Datadog, and other log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        corr_id = correlation_id.get()
        if corr_id:
            log_data["correlation_id"] = corr_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class StructuredLogger:
    """
    Wrapper for structured logging with correlation IDs and custom fields.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup structured logging handlers."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _log(self, level: int, message: str, **kwargs):
        """Internal log method with extra fields."""
        extra_fields = {k: v for k, v in kwargs.items() if v is not None}
        self.logger.log(level, message, extra={"extra_fields": extra_fields})

    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional extra fields."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with optional extra fields."""
        self._log(logging.CRITICAL, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields."""
        self._log(logging.DEBUG, message, **kwargs)


def set_correlation_id(corr_id: Optional[str] = None):
    """
    Set correlation ID for current context.
    If None, generates a new UUID.
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id.get()


def clear_correlation_id():
    """Clear correlation ID from context."""
    correlation_id.set(None)


# Example usage for request tracking
def log_request(
    logger: StructuredLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
):
    """
    Log HTTP request with structured data.

    Example:
        log_request(logger, "POST", "/v1/clauses/invoke", 200, 45.3, "user_123")
    """
    logger.info(
        f"{method} {path} - {status_code}",
        http_method=method,
        http_path=path,
        http_status=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
    )


def log_error_with_context(
    logger: StructuredLogger, error: Exception, context: Dict[str, Any]
):
    """
    Log error with additional context.

    Example:
        log_error_with_context(logger, e, {"api_key": "key_123", "clause_id": "Legacy_Seed"})
    """
    logger.error(
        f"Error: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        **context,
    )


# Create default logger instance
get_logger = StructuredLogger
