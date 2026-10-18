#!/usr/bin/env python3
"""
Mythara Engine - Monitoring & Observability
Prometheus metrics, health checks, and performance monitoring.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Response
from typing import Dict, Any
import time
import psutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ===================== PROMETHEUS METRICS =====================

# Request counters
http_requests_total = Counter(
    "mythara_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

# Clause invocation metrics
clause_invocations_total = Counter(
    "mythara_clause_invocations_total",
    "Total clause invocations",
    ["clause_id", "messenger"],
)

clause_invocation_duration = Histogram(
    "mythara_clause_invocation_duration_seconds",
    "Clause invocation duration",
    ["clause_id"],
)

# Soul Cradle paradox metrics
paradoxes_created_total = Counter(
    "mythara_paradoxes_created_total", "Total paradoxes created", ["system_type"]
)

paradox_risk_score = Histogram(
    "mythara_paradox_risk_score",
    "Paradox terminal risk scores",
    buckets=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
)

indifference_alerts_total = Counter(
    "mythara_indifference_alerts_total",
    "Total indifference trajectory alerts",
    ["severity"],
)

systemic_overload_events = Counter(
    "mythara_systemic_overload_events_total",
    "Total systemic overload events",
    ["dept_id"],
)

# Blessings Reservoir metrics
blessings_total = Gauge("mythara_blessings_total", "Total blessings in reservoir")

reservoir_score = Gauge("mythara_reservoir_score", "Blessings Reservoir score (0-1)")

overflow_events_total = Counter(
    "mythara_overflow_events_total", "Total blessings overflow events"
)

# WebSocket metrics
websocket_connections = Gauge(
    "mythara_websocket_connections", "Active WebSocket connections", ["org_id"]
)

websocket_messages_total = Counter(
    "mythara_websocket_messages_total",
    "Total WebSocket messages sent",
    ["message_type"],
)

# Database metrics
database_queries_total = Counter(
    "mythara_database_queries_total", "Total database queries", ["operation", "table"]
)

# Database connection pool metrics
db_pool_size = Gauge("mythara_db_pool_size", "Database connection pool size")

db_pool_checked_out = Gauge(
    "mythara_db_pool_checked_out", "Number of checked out database connections"
)

db_pool_overflow = Gauge(
    "mythara_db_pool_overflow", "Number of overflow database connections"
)

db_pool_available = Gauge(
    "mythara_db_pool_available", "Number of available database connections"
)

database_query_duration = Histogram(
    "mythara_database_query_duration_seconds", "Database query duration"
)

# Redis metrics
redis_operations_total = Counter(
    "mythara_redis_operations_total", "Total Redis operations", ["operation"]
)

redis_errors_total = Counter("mythara_redis_errors_total", "Total Redis errors")

# Rate limiting metrics
rate_limit_hits_total = Counter(
    "mythara_rate_limit_hits_total", "Total rate limit violations", ["identifier_type"]
)

# System info
mythara_info = Info("mythara", "Mythara Engine information")

# Set system info
mythara_info.info({"version": "1.0.0", "environment": "production"})

# ===================== PERFORMANCE MONITORING =====================


class PerformanceMonitor:
    """
    Monitor system performance and resource usage.
    """

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get current system metrics.

        Returns:
            System metrics dict
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            # Network stats
            net_io = psutil.net_io_counters()

            return {
                "cpu": {"percent": cpu_percent, "count": cpu_count},
                "memory": {
                    "total_mb": memory.total / (1024**2),
                    "available_mb": memory.available / (1024**2),
                    "used_mb": memory.used / (1024**2),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent_mb": net_io.bytes_sent / (1024**2),
                    "bytes_recv_mb": net_io.bytes_recv / (1024**2),
                },
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}

    @staticmethod
    def get_process_metrics() -> Dict[str, Any]:
        """
        Get current process metrics.

        Returns:
            Process metrics dict
        """
        try:
            process = psutil.Process()

            return {
                "memory_mb": process.memory_info().rss / (1024**2),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
            }
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            return {}


# ===================== HEALTH CHECK =====================


class HealthChecker:
    """
    Comprehensive health check for all system components.
    """

    def __init__(self):
        self.start_time = time.time()

    async def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Health check results
        """
        checks = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - self.start_time),
            "checks": {},
        }

        # API check
        checks["checks"]["api"] = {"status": "healthy", "message": "API is responding"}

        # Redis check
        checks["checks"]["redis"] = await self._check_redis()

        # Database check
        checks["checks"]["database"] = await self._check_database()

        # System resources check
        checks["checks"]["system"] = self._check_system_resources()

        # Overall status
        unhealthy = [
            name
            for name, check in checks["checks"].items()
            if check["status"] != "healthy"
        ]

        if unhealthy:
            checks["status"] = (
                "unhealthy"
                if "redis" in unhealthy or "database" in unhealthy
                else "degraded"
            )
            checks["unhealthy_components"] = unhealthy

        return checks

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connection."""
        try:
            from redis_cache import cache

            return cache.health_check()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def _check_database(self) -> Dict[str, Any]:
        """Check database connection."""
        try:
            from database import SessionLocal

            db = SessionLocal()
            try:
                # Test query
                db.execute("SELECT 1")
                return {"status": "healthy", "message": "Database connection OK"}
            finally:
                db.close()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            metrics = PerformanceMonitor.get_system_metrics()

            # Warning thresholds
            cpu_warn = 80
            memory_warn = 85
            disk_warn = 90

            warnings = []

            if metrics["cpu"]["percent"] > cpu_warn:
                warnings.append(f"CPU usage high: {metrics['cpu']['percent']}%")

            if metrics["memory"]["percent"] > memory_warn:
                warnings.append(f"Memory usage high: {metrics['memory']['percent']}%")

            if metrics["disk"]["percent"] > disk_warn:
                warnings.append(f"Disk usage high: {metrics['disk']['percent']}%")

            if warnings:
                return {"status": "degraded", "warnings": warnings, "metrics": metrics}

            return {"status": "healthy", "metrics": metrics}

        except Exception as e:
            return {"status": "unknown", "error": str(e)}


# Global health checker
health_checker = HealthChecker()


# ===================== METRICS ENDPOINTS =====================


async def get_metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus-formatted metrics
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def get_health() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return await health_checker.check_all()


async def get_system_stats() -> Dict[str, Any]:
    """
    System statistics endpoint.

    Returns:
        System and process metrics
    """
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": PerformanceMonitor.get_system_metrics(),
        "process": PerformanceMonitor.get_process_metrics(),
        "uptime_seconds": int(time.time() - health_checker.start_time),
    }


# ===================== METRIC RECORDING HELPERS =====================


def record_http_request(method: str, endpoint: str, status_code: int):
    """Record HTTP request metric."""
    http_requests_total.labels(
        method=method, endpoint=endpoint, status_code=status_code
    ).inc()


def record_clause_invocation(clause_id: str, messenger: str, duration: float):
    """Record clause invocation metric."""
    clause_invocations_total.labels(clause_id=clause_id, messenger=messenger).inc()
    clause_invocation_duration.labels(clause_id=clause_id).observe(duration)


def record_paradox_creation(system_type: str, risk_score: float):
    """Record paradox creation metric."""
    paradoxes_created_total.labels(system_type=system_type).inc()
    paradox_risk_score.observe(risk_score)


def record_indifference_alert(severity: str):
    """Record indifference trajectory alert."""
    indifference_alerts_total.labels(severity=severity).inc()


def record_systemic_overload(dept_id: str):
    """Record systemic overload event."""
    systemic_overload_events.labels(dept_id=dept_id).inc()


def update_blessings_metrics(total: int, score: float):
    """Update blessings reservoir metrics."""
    blessings_total.set(total)
    reservoir_score.set(score)


def record_overflow_event():
    """Record blessings overflow event."""
    overflow_events_total.inc()


def update_websocket_connections(org_id: str, count: int):
    """Update WebSocket connection count."""
    websocket_connections.labels(org_id=org_id).set(count)


def record_websocket_message(message_type: str):
    """Record WebSocket message sent."""
    websocket_messages_total.labels(message_type=message_type).inc()


def record_database_query(operation: str, table: str, duration: float):
    """Record database query."""
    database_queries_total.labels(operation=operation, table=table).inc()
    database_query_duration.observe(duration)


def record_redis_operation(operation: str):
    """Record Redis operation."""
    redis_operations_total.labels(operation=operation).inc()


def record_redis_error():
    """Record Redis error."""
    redis_errors_total.inc()


def update_db_pool_metrics(
    pool_size: int, checked_out: int, overflow: int, available: int
):
    """Update database connection pool metrics."""
    db_pool_size.set(pool_size)
    db_pool_checked_out.set(checked_out)
    db_pool_overflow.set(overflow)
    db_pool_available.set(available)


def record_rate_limit_hit(identifier_type: str):
    """Record rate limit violation."""
    rate_limit_hits_total.labels(identifier_type=identifier_type).inc()
