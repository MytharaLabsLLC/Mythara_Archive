# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Send execution. The safety gates live in safety.py; this module moves bytes.

Two senders:
  DryRunSender (default) — writes .eml files under state/dryrun/ and logs
      DRY_RUN entries. Sends nothing. This is the mode the machine runs in
      until Herb places the Yahoo app password (see YahooSMTPSender).
  YahooSMTPSender — real sends via Yahoo SMTP as mythara.engine@yahoo.com,
      using a 0600 app-password file that Herb creates once. If the file
      is missing it raises SenderBlocked with the exact fix, instead of
      failing cryptically or, worse, half-working. The password is never
      logged, printed, or committed.
  GmailSender — legacy Gmail API path (kept as fallback). BLOCKED until
      Herb runs Gmail OAuth once (see README).

Every attempt — sent, dry-run, or blocked — is appended to the send ledger
(state/send_log.jsonl) with a body hash that matches the witness-log entry
for post-send audit.
"""

import base64
import hashlib
import json
import time
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional

from . import config
from . import safety

def _unsubscribe_headers(msg) -> None:
    """One-click unsubscribe (RFC 2369 mailto). Clicking it emails
    mythara.engine@yahoo.com with subject "unsubscribe", which triage.py
    classifies as unsubscribe -> suppressed forever, sequence stops."""
    msg["List-Unsubscribe"] = (
        f"<mailto:{config.YAHOO_FROM_ADDR}?subject=unsubscribe>"
    )


class SenderBlocked(Exception):
    """The send path is not available. Carries the exact unblock step."""


class BaseSender:
    name = "base"

    def send(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        raise NotImplementedError

    def _log(
        self,
        to: str,
        subject: str,
        body: str,
        status: str,
        detail: str = "",
        message_id: str = "",
    ) -> Dict[str, Any]:
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "sender": self.name,
            "to": to,
            "subject": subject,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "status": status,  # SENT | DRY_RUN | BLOCKED
            "detail": detail,
            "message_id": message_id,
        }
        config.SEND_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(config.SEND_LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        return entry


class DryRunSender(BaseSender):
    """Default. Writes .eml files, sends nothing."""

    name = "dryrun"

    def __init__(self, out_dir: Optional[Path] = None):
        self.out_dir = out_dir or (config.STATE_DIR / "dryrun")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def send(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        safe_to = "".join(c if c.isalnum() else "_" for c in to)[:40]
        path = self.out_dir / f"{stamp}-{safe_to}.eml"
        msg = MIMEText(body, "plain", "utf-8")
        msg["To"] = to
        msg["Subject"] = subject
        msg["From"] = f"Herbert Velez Jr. <{config.YAHOO_FROM_ADDR}>"
        _unsubscribe_headers(msg)
        path.write_text(msg.as_string(), encoding="utf-8")
        return self._log(to, subject, body, "DRY_RUN", f"wrote {path.name}")


class YahooSMTPSender(BaseSender):
    """Real sends via Yahoo SMTP. BLOCKED until the app-password file exists.

    Auth: smtp.mail.yahoo.com:587 + STARTTLS, username = the Yahoo address,
    password = the 16-char app password Herb generated at Yahoo Account
    Security -> App passwords. The file holds one line (the password only),
    mode 0600, and is gitignored. It is read at send time and never logged.
    """

    name = "yahoo"
    SMTP_HOST = "smtp.mail.yahoo.com"
    SMTP_PORT = 587

    def _password_or_raise(self) -> str:
        key_file = config.YAHOO_KEY_FILE
        if not key_file.exists():
            raise SenderBlocked(
                "BLOCKED: no Yahoo app password on this machine. Herb must "
                f"save the {config.YAHOO_FROM_ADDR} app password to "
                f"{key_file} (one line, no trailing spaces, chmod 600). "
                "Generate it at Yahoo Account Security -> App passwords. "
                "Nothing was sent."
            )
        return key_file.read_text(encoding="utf-8").strip()

    def send(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        import smtplib

        password = self._password_or_raise()
        msg = MIMEText(body, "plain", "utf-8")
        msg["To"] = to
        msg["Subject"] = subject
        msg["From"] = f"Herbert Velez Jr. <{config.YAHOO_FROM_ADDR}>"
        _unsubscribe_headers(msg)
        try:
            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT, timeout=30) as s:
                s.starttls()
                s.login(config.YAHOO_FROM_ADDR, password)
                s.sendmail(config.YAHOO_FROM_ADDR, [to], msg.as_string())
        except smtplib.SMTPAuthenticationError as exc:
            raise SenderBlocked(
                "Yahoo rejected the SMTP login — the app password is wrong, "
                "expired, or 2-step verification changed. Regenerate it at "
                "Yahoo Account Security -> App passwords and update "
                f"{config.YAHOO_KEY_FILE}. Nothing was sent."
            ) from exc
        finally:
            password = ""  # do not linger in memory
        return self._log(to, subject, body, "SENT", detail="yahoo-smtp")


class GmailSender(BaseSender):
    """Real sends. BLOCKED until Herb runs Gmail OAuth once (see README)."""

    name = "gmail"
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]  # covers send

    def __init__(self):
        self._service = None

    def _service_or_raise(self):
        if self._service is not None:
            return self._service
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise SenderBlocked(
                "google API client libraries not installed. Run: "
                "pip install google-api-python-client google-auth-oauthlib google-auth"
            ) from exc
        commercial = Path(__file__).resolve().parent.parent
        token_path = commercial / "gmail_token.json"
        creds_path = commercial / "gmail_credentials.json"
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(token_path), self.SCOPES
            )
        if creds and creds.valid:
            pass
        elif creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif creds_path.exists():
            # First run needs Herb in a browser; the scheduler must never
            # hit this path unattended — fail loudly instead.
            raise SenderBlocked(
                "Gmail OAuth client secrets exist but no token yet. "
                "BLOCKED: Herb must run the one-time browser OAuth flow "
                "(see README.md 'Gmail OAuth setup'), then re-run."
            )
        else:
            raise SenderBlocked(
                "BLOCKED: no Gmail credentials on this machine. "
                "Herb must place gmail_credentials.json (Google Cloud OAuth "
                "client) in Commercial/ and complete the one-time browser "
                "OAuth flow (see README.md 'Gmail OAuth setup'). "
                "Nothing was sent."
            )
        with open(token_path, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())
        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def send(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        service = self._service_or_raise()  # raises SenderBlocked, never half-sends
        msg = MIMEText(body, "plain", "utf-8")
        msg["To"] = to
        msg["Subject"] = subject
        msg["From"] = f"Herbert Velez Jr. <{config.YAHOO_FROM_ADDR}>"
        _unsubscribe_headers(msg)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        result = (
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
        )
        return self._log(
            to, subject, body, "SENT", message_id=result.get("id", "")
        )


def get_sender(mode: Optional[str] = None) -> BaseSender:
    mode = mode or config.SENDER_MODE
    if mode == "yahoo":
        return YahooSMTPSender()
    if mode == "gmail":
        return GmailSender()
    return DryRunSender()


_last_send_path = config.STATE_DIR / "last_send_ts.txt"


def pace() -> None:
    """Enforce minimum spacing between sends (reputation protection)."""
    if _last_send_path.exists():
        try:
            last = float(_last_send_path.read_text(encoding="utf-8").strip())
            wait = config.MIN_SECONDS_BETWEEN_SENDS - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
        except (OSError, ValueError):
            pass
    _last_send_path.write_text(str(time.time()), encoding="utf-8")
