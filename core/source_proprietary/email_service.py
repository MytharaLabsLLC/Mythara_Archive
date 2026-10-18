#!/usr/bin/env python3
"""
Mythara Engine - Email Service
SendGrid integration for automated API key delivery and alerts.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional, Dict, Any
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# SendGrid API key from environment
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Mythara.Engine@yahoo.com")
FROM_NAME = os.getenv("FROM_NAME", "Mythara Engine")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "Mythara.Engine@yahoo.com")


def send_email(
    to_email: str, subject: str, body_html: str, body_text: str
) -> Dict[str, Any]:
    """
    Send email via SendGrid.
    Returns status dict with success/error info.
    """
    if not SENDGRID_API_KEY:
        logger.error("SENDGRID_API_KEY not configured - email not sent")
        return {"success": False, "error": "SendGrid not configured"}

    try:
        message = Mail(
            from_email=Email(FROM_EMAIL, FROM_NAME),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", body_text),
            html_content=Content("text/html", body_html),
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(
            f"Email sent to {to_email}: {subject} (status {response.status_code})"
        )
        return {"success": True, "status_code": response.status_code}

    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return {"success": False, "error": str(e)}


def send_strike_warning(
    to_email: str,
    api_key: str,
    company_name: str,
    strike_count: int,
    reason: str,
    suspended_until: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Send strike notification to API key holder for self-regulation violation.
    """
    if strike_count == 1:
        subject = f"⚠️ Strike #1 Warning - {company_name}"
        action = "This is a warning. Please adjust your usage patterns."
    elif strike_count == 2:
        subject = f"🚫 Strike #2: 7-Day Suspension - {company_name}"
        action = f"Your account is suspended until {suspended_until.strftime('%Y-%m-%d %H:%M UTC')}. API calls will be rejected during this period."
    else:
        subject = f"❌ Strike #3: Account Terminated - {company_name}"
        action = "Your account has been permanently terminated. Contact support if you believe this is an error."

    body_html = f"""
    <html>
    <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1>Self-Regulation Strike #{strike_count}</h1>
        <p><strong>Company:</strong> {company_name}</p>
        <p><strong>Reason:</strong> {reason}</p>
        <p><strong>Action Taken:</strong> {action}</p>
        
        <h2>What Happened?</h2>
        <p>Our self-regulation system detected abuse patterns in your API usage:</p>
        <ul>
            <li>Velocity abuse: Exhausted call limit in less than 24 hours</li>
            <li>Usage mismatch: Actual usage 3x+ higher than expected for your employee count</li>
        </ul>
        
        <h2>Graduated Enforcement</h2>
        <ul>
            <li><strong>Strike 1:</strong> Warning (current: {strike_count})</li>
            <li><strong>Strike 2:</strong> 7-day suspension</li>
            <li><strong>Strike 3:</strong> Permanent termination</li>
        </ul>
        
        <p>Support: {SUPPORT_EMAIL}</p>
    </body>
    </html>
    """

    body_text = f"""
Self-Regulation Strike #{strike_count}

Company: {company_name}
Reason: {reason}
Action Taken: {action}

WHAT HAPPENED?
Our self-regulation system detected abuse patterns in your API usage:
- Velocity abuse: Exhausted call limit in less than 24 hours
- Usage mismatch: Actual usage 3x+ higher than expected for your employee count

GRADUATED ENFORCEMENT
- Strike 1: Warning (current: {strike_count})
- Strike 2: 7-day suspension
- Strike 3: Permanent termination

Support: {SUPPORT_EMAIL}
    """

    return send_email(to_email, subject, body_html, body_text)
