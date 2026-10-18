#!/usr/bin/env python3
"""
Mythara Engine - Database Layer
PostgreSQL persistence for API usage tracking, audit logs, and email queue.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment (Railway provides DATABASE_URL automatically)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mythara_pilots.db")

# Fix for Railway's postgres:// URLs (SQLAlchemy needs postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_timeout=30,  # Timeout waiting for connection from pool (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    echo=False,  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UsageTracking(Base):
    """
    API call usage tracking per API key.
    Separate table allows efficient queries without loading full key data.
    """

    __tablename__ = "usage_tracking"

    api_key = Column(String, primary_key=True, index=True)
    call_count = Column(Integer, default=0, nullable=False)
    total_limit = Column(Integer, nullable=False)
    last_call = Column(DateTime, nullable=True)

    # Abuse detection metrics
    first_call_date = Column(DateTime, nullable=True)
    velocity_abuse_detected = Column(Boolean, default=False)
    usage_mismatch_detected = Column(Boolean, default=False)

    # Alert tracking
    sent_80_percent_alert = Column(Boolean, default=False)
    sent_24hr_expiration_alert = Column(Boolean, default=False)

    # Self-regulation enforcement
    strike_count = Column(Integer, default=0)
    suspended_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    termination_reason = Column(String, nullable=True)


class AuditLog(Base):
    """
    Immutable audit log for compliance and forensics.
    Tracks all critical actions: API calls, strikes, terminations.
    """

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    api_key = Column(String, index=True, nullable=True)
    action = Column(String, nullable=False)  # e.g., "api_call", "strike_issued"
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)


class EmailQueue(Base):
    """
    Outbound email queue for async delivery.
    Ensures emails are sent even if SendGrid is temporarily down.
    """

    __tablename__ = "email_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    body_html = Column(String, nullable=False)
    body_text = Column(String, nullable=False)
    template_type = Column(
        String, nullable=False
    )  # e.g., "api_key_delivery", "80_percent_alert"
    api_key = Column(String, nullable=True, index=True)

    # Delivery tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, sent, failed


# Database helper functions
def get_db() -> Session:
    """
    Dependency for FastAPI endpoints to get database session.
    Ensures proper connection cleanup after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database schema - creates all tables if they don't exist.
    Call this on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_usage_tracking(db: Session, api_key: str) -> Optional[UsageTracking]:
    """Get usage tracking for API key."""
    return db.query(UsageTracking).filter(UsageTracking.api_key == api_key).first()


def issue_strike(db: Session, api_key: str, reason: str) -> int:
    """
    Issue strike to API key for self-regulation violation.
    Graduated enforcement: 1 = warning, 2 = 7-day suspension, 3 = termination.
    Returns the new strike count.
    """
    usage = get_usage_tracking(db, api_key)
    if not usage:
        raise ValueError(f"Usage record not found: {api_key}")

    usage.strike_count += 1

    if usage.strike_count == 2:
        # Second strike = 7-day suspension
        usage.suspended_until = datetime.utcnow() + timedelta(days=7)
    elif usage.strike_count >= 3:
        # Third strike = termination
        usage.is_active = False
        usage.termination_reason = reason

    db.commit()

    # Audit log
    audit = AuditLog(
        api_key=api_key,
        action="strike_issued",
        details={
            "reason": reason,
            "strike_count": usage.strike_count,
            "suspended_until": (
                usage.suspended_until.isoformat() if usage.suspended_until else None
            ),
            "terminated": usage.strike_count >= 3,
        },
    )
    db.add(audit)
    db.commit()

    logger.warning(
        f"Strike issued to {api_key[:8]}...: {reason} (strike {usage.strike_count})"
    )
    return usage.strike_count


def log_audit(
    db: Session,
    action: str,
    api_key: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Log audit event for compliance tracking.
    Immutable record of all system actions.
    """
    audit = AuditLog(
        api_key=api_key,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit)
    db.commit()


def queue_email(
    db: Session,
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str,
    template_type: str,
    api_key: Optional[str] = None,
) -> EmailQueue:
    """
    Queue email for async delivery.
    Ensures email is sent even if SendGrid is temporarily down.
    """
    email = EmailQueue(
        to_email=to_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        template_type=template_type,
        api_key=api_key,
        status="pending",
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    logger.info(f"Email queued: {template_type} to {to_email}")
    return email


def get_api_rate_limit_for_employee_count(employee_count: int) -> int:
    """
    Return 7-day total API call limit based on employee count.
    Matches API_RATE_LIMITS_BY_EMPLOYEE_COUNT in main.py.
    """
    if employee_count <= 10:
        return 1_000
    elif employee_count <= 50:
        return 5_000
    elif employee_count <= 200:
        return 15_000
    elif employee_count <= 1_000:
        return 30_000
    else:
        return 50_000
