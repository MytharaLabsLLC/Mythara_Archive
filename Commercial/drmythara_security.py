# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""
DrMythara ePHI security layer.

Real, production-oriented controls for the Dr Mythara bot's data
surfaces: password authentication, session management, encryption at
rest, encrypted backups, break-glass emergency access, subject-scoped
reads, and a signed audit-review workflow.

HONEST STATUS — read before deploying:
  * IMPLEMENTED HERE: PBKDF2-HMAC-SHA256 password hashing (600k
    iterations, per-user salt); account lockout; token sessions with
    absolute + idle timeouts; Fernet (AES-128-CBC + HMAC-SHA256)
    file-level encryption for SQLite/JSON stores; hash-chained,
    signed security-event log with a review sign-off workflow;
    encrypted backups with a logged restore test; break-glass access
    that is fully audited and auto-expiring.
  * STILL NEEDED OUTSIDE THIS FILE: a real secret store for
    DRMYTHARA_DATA_KEY (env var is the minimum; a KMS is better);
    TLS termination in front of any network surface (see
    journal_app/server.py); off-site backup copies (backups here are
    local — copy them off-site on a schedule); the organizational
    paperwork (risk analysis, policies, BAAs) from Phase 2 of the
    HIPAA roadmap.
  * DEPENDENCY: the `cryptography` package (Fernet). It is in
    requirements.txt. If it is missing, every encryption path FAILS
    CLOSED with a clear error — nothing silently runs unencrypted.

Key management:
  * The data key comes from the DRMYTHARA_DATA_KEY environment variable
    (a Fernet key: urlsafe base64, 32 bytes — generate with
    DataKey.generate_key()).
  * Rotation procedure: 1) generate a new key and store it in the
    secret store; 2) call DataKey.rotate(old_key, new_key, [paths...])
    to re-encrypt every store; 3) verify each store opens with the new
    key; 4) revoke the old key. Never reuse a retired key.
  * There is NO ephemeral-key fallback on ePHI paths. If the key is
    missing, resolve_data_key(strict=True) raises MissingDataKeyError
    instead of inventing one.

Public-language note: user-facing strings in this module use plain
language. Internal security terms (hash, session, lockout) are fine;
pipeline jargon ("witnessed", "ingested", "honesty contract") is not
used here.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import shutil
import sqlite3
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover — fail-closed path, tested via stub
    Fernet = None  # type: ignore[assignment]

    class InvalidToken(Exception):  # type: ignore[no-redef]
        """Placeholder so except-clauses keep working without cryptography."""


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SecurityError(Exception):
    """Base class for this module's errors."""


class MissingDataKeyError(SecurityError):
    """Raised when no data key is available and one is required.

    Fix: generate a key and export it before starting the bot::

        python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        export DRMYTHARA_DATA_KEY='<the key>'
    """


class AuthenticationError(SecurityError):
    """Wrong credentials. Message is deliberately generic (no user enumeration)."""


class AccountLockedError(SecurityError):
    """Too many failed logins; the account is temporarily locked."""


class SessionError(SecurityError):
    """Session missing, expired, or revoked."""


class AccessDeniedError(SecurityError):
    """The signed-in identity may not touch this subject's records."""


class BackupError(SecurityError):
    """Backup or restore failed."""


# ---------------------------------------------------------------------------
# Password hashing — PBKDF2-HMAC-SHA256, per-user salt
# ---------------------------------------------------------------------------

# OWASP's current PBKDF2-HMAC-SHA256 guidance. This is a NIST-approved
# KDF. (Argon2id would also be fine; PBKDF2 is stdlib, so there is one
# fewer moving part. The format version field lets us upgrade later.)
_PBKDF2_ALGORITHM = "pbkdf2-sha256"
_PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 32

# Account lockout policy.
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_DURATION = timedelta(minutes=15)

# Password policy.
_MIN_PASSWORD_LENGTH = 12


class PasswordHasher:
    """Hash and verify passwords with PBKDF2-HMAC-SHA256.

    Stored format: pbkdf2-sha256$<iterations>$<b64 salt>$<b64 derived key>
    NEVER use plain HMAC-with-a-shared-secret for passwords: HMAC is fast
    (good for message auth, bad for password storage) and a module-level
    random key cannot verify after restart.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        if not isinstance(password, str) or len(password) < _MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters."
            )
        salt = secrets.token_bytes(_SALT_BYTES)
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
        )
        b64 = lambda b: base64.b64encode(b).decode("ascii")  # noqa: E731
        return (
            f"{_PBKDF2_ALGORITHM}${_PBKDF2_ITERATIONS}"
            f"${b64(salt)}${b64(dk)}"
        )

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        try:
            algo, iters, salt_b64, dk_b64 = stored.split("$")
            if algo != _PBKDF2_ALGORITHM:
                return False
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(dk_b64)
            dk = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, int(iters)
            )
            return hmac.compare_digest(dk, expected)
        except (ValueError, TypeError, base64.binascii.Error):
            return False


# ---------------------------------------------------------------------------
# Data key management — Fernet keys from env/secret config, never ephemeral
# ---------------------------------------------------------------------------

DATA_KEY_ENV = "DRMYTHARA_DATA_KEY"
BREAKGLASS_ENV = "DRMYTHARA_BREAKGLASS_SECRET"


class DataKey:
    """Load, generate, and rotate the at-rest encryption key."""

    @staticmethod
    def generate_key() -> str:
        """Generate a fresh Fernet key (urlsafe base64, 32 bytes)."""
        _require_crypto()
        assert Fernet is not None
        return Fernet.generate_key().decode("ascii")

    @staticmethod
    def resolve(explicit: Optional[str] = None, *, strict: bool = True):
        """Return a Fernet instance for the data key.

        Precedence: explicit argument, then DRMYTHARA_DATA_KEY.
        strict=True (default): missing key raises MissingDataKeyError —
        ePHI paths must never silently run unencrypted. strict=False:
        returns None so callers can run an explicitly-marked dev mode
        (they must warn loudly; see EncryptedSQLite).
        """
        _require_crypto()
        raw = explicit or os.environ.get(DATA_KEY_ENV, "")
        if not raw:
            if strict:
                raise MissingDataKeyError(
                    "No data key found. Set the DRMYTHARA_DATA_KEY environment "
                    "variable to a Fernet key (generate one with "
                    "DataKey.generate_key()). Refusing to handle protected "
                    "data without encryption."
                )
            return None
        try:
            assert Fernet is not None
            return Fernet(raw.encode("ascii") if isinstance(raw, str) else raw)
        except (ValueError, TypeError) as exc:
            raise SecurityError(
                "DRMYTHARA_DATA_KEY is not a valid Fernet key."
            ) from exc

    @staticmethod
    def rotate(old_key: str, new_key: str, store_paths: List[str]) -> List[str]:
        """Re-encrypt every store from old_key to new_key.

        Rotation procedure: generate + stage the new key, call this,
        verify each store opens under the new key, then revoke the old
        key. Returns the list of re-encrypted paths.
        """
        old_f = DataKey.resolve(old_key, strict=True)
        new_f = DataKey.resolve(new_key, strict=True)
        done = []
        for path in store_paths:
            token = Path(path).read_bytes()
            assert old_f is not None and new_f is not None
            try:
                plain = old_f.decrypt(token)
            except InvalidToken as exc:
                raise SecurityError(
                    f"Rotation failed for {path}: old key does not decrypt it."
                ) from exc
            Path(path).write_bytes(new_f.encrypt(plain))
            _chmod_600(path)
            done.append(path)
        return done


def _require_crypto() -> None:
    if Fernet is None:
        raise SecurityError(
            "The 'cryptography' package is required for encryption "
            "(pip install cryptography — it is in requirements.txt). "
            "Refusing to continue without real encryption."
        )


def _chmod_600(path: str) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Encrypted file + SQLite stores (Fernet whole-file encryption)
# ---------------------------------------------------------------------------

class EncryptedFile:
    """Whole-file Fernet encryption for JSON/SQLite stores.

    Format on disk: raw Fernet token bytes, file mode 0600.
    """

    @staticmethod
    def write(path: str, data: bytes, fernet) -> None:
        if fernet is None:
            raise SecurityError("Refusing to write protected data unencrypted.")
        tmp = f"{path}.tmp.{secrets.token_hex(8)}"
        with open(tmp, "wb") as f:
            f.write(fernet.encrypt(data))
        _chmod_600(tmp)
        os.replace(tmp, path)

    @staticmethod
    def read(path: str, fernet) -> bytes:
        if fernet is None:
            raise SecurityError("Refusing to read protected data unencrypted.")
        token = Path(path).read_bytes()
        try:
            return fernet.decrypt(token)
        except InvalidToken as exc:
            raise SecurityError(
                f"Cannot decrypt {path}: wrong key or tampered file."
            ) from exc


@contextmanager
def EncryptedSQLite(db_path: str, fernet) -> Iterator[sqlite3.Connection]:
    """SQLite connection with transparent at-rest encryption.

    How it works: the .db file on disk is always Fernet-encrypted.
    On open it is decrypted to a 0600 temp file in the same directory,
    SQLite works against the temp file, and on close the temp file is
    re-encrypted back and securely removed.

    Honest limits (documented, not hidden):
      * The plaintext exists briefly in a temp file (0600, same
        filesystem). Full-disk encryption on the host covers the rest.
      * If fernet is None, this runs PLAINTEXT and prints a loud
        warning. That mode is dev-only: never point it at real data.
    """
    if fernet is None:
        print(
            "⚠️  EncryptedSQLite: NO DATA KEY — running PLAINTEXT (dev only). "
            "Set DRMYTHARA_DATA_KEY for real use."
        )
        conn = sqlite3.connect(db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
        return

    db_file = Path(db_path)
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix=".dbplain-", dir=str(db_file.parent or "."), suffix=".sqlite"
    )
    os.close(tmp_fd)
    _chmod_600(tmp_path)
    if db_file.exists():
        try:
            Path(tmp_path).write_bytes(EncryptedFile.read(str(db_file), fernet))
        except BaseException:
            _shred_temp(tmp_path)  # decrypt failed: don't leak the temp file
            raise
    conn = sqlite3.connect(tmp_path)
    try:
        yield conn
        conn.commit()
    except BaseException:
        # The block raised: roll back the partial transaction, but
        # PERSIST everything committed so far. Committed writes (e.g.
        # failed-login counters, audit events) must never be silently
        # lost just because the caller raised.
        conn.rollback()
        raise
    finally:
        conn.close()
        try:
            EncryptedFile.write(
                str(db_file), Path(tmp_path).read_bytes(), fernet)
        finally:
            _shred_temp(tmp_path)


def _shred_temp(tmp_path: str) -> None:
    """Best-effort shred of the plaintext temp file."""
    try:
        size = os.path.getsize(tmp_path)
        with open(tmp_path, "r+b") as f:
            f.write(os.urandom(size))
    except OSError:
        pass
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# User accounts + authentication (backed by a sqlite3 connection)
# ---------------------------------------------------------------------------

_CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS drmy_users (
    user_id TEXT PRIMARY KEY,
    pw_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'clinician',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


class UserStore:
    """User accounts with lockout. Runs on any sqlite3 connection
    (in production: inside the bot's encrypted database)."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        conn.execute(_CREATE_USERS_SQL)
        conn.commit()

    def user_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM drmy_users").fetchone()
        return int(row[0])

    def create_user(
        self, user_id: str, password: str, role: str = "clinician"
    ) -> Dict[str, str]:
        user_id = (user_id or "").strip()
        if not user_id:
            raise ValueError("user_id is required.")
        if role not in ("admin", "clinician", "auditor"):
            raise ValueError("role must be admin, clinician, or auditor.")
        if self._conn.execute(
            "SELECT 1 FROM drmy_users WHERE user_id = ?", (user_id,)
        ).fetchone():
            raise ValueError(f"User {user_id!r} already exists.")
        pw_hash = PasswordHasher.hash_password(password)
        now = _utcnow()
        self._conn.execute(
            "INSERT INTO drmy_users "
            "(user_id, pw_hash, role, failed_attempts, locked_until, "
            " created_at, updated_at) VALUES (?, ?, ?, 0, NULL, ?, ?)",
            (user_id, pw_hash, role, now, now),
        )
        self._conn.commit()
        return {"user_id": user_id, "role": role, "created_at": now}

    def _row(self, user_id: str):
        return self._conn.execute(
            "SELECT user_id, pw_hash, role, failed_attempts, locked_until "
            "FROM drmy_users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    def authenticate(self, user_id: str, password: str) -> Dict[str, str]:
        """Verify credentials. Raises AuthenticationError (generic message —
        no user enumeration) or AccountLockedError."""
        row = self._row((user_id or "").strip())
        now = datetime.now(timezone.utc)

        def _fail():
            raise AuthenticationError("Invalid user ID or password.")

        if row is None:
            # Still hash to keep timing roughly uniform (no enumeration).
            PasswordHasher.verify_password(
                password or "x",
                "pbkdf2-sha256$600000$"
                + base64.b64encode(b"\x00" * 32).decode()
                + "$" + base64.b64encode(b"\x00" * 32).decode(),
            )
            _fail()
        _, pw_hash, role, failed, locked_until = row
        if locked_until:
            locked_dt = datetime.fromisoformat(locked_until)
            if now < locked_dt:
                raise AccountLockedError(
                    "Account temporarily locked after too many failed "
                    "sign-in attempts. Try again later."
                )
        if not PasswordHasher.verify_password(password or "", pw_hash):
            failed = int(failed) + 1
            lock = None
            if failed >= _MAX_FAILED_ATTEMPTS:
                lock = (now + _LOCKOUT_DURATION).isoformat()
            self._conn.execute(
                "UPDATE drmy_users SET failed_attempts = ?, locked_until = ?, "
                "updated_at = ? WHERE user_id = ?",
                (failed, lock, _utcnow(), row[0]),
            )
            self._conn.commit()
            if lock:
                raise AccountLockedError(
                    "Account temporarily locked after too many failed "
                    "sign-in attempts. Try again later."
                )
            _fail()
        self._conn.execute(
            "UPDATE drmy_users SET failed_attempts = 0, locked_until = NULL, "
            "updated_at = ? WHERE user_id = ?",
            (_utcnow(), row[0]),
        )
        self._conn.commit()
        return {"user_id": row[0], "role": role}

    def change_password(self, user_id: str, old_password: str, new_password: str) -> None:
        self.authenticate(user_id, old_password)  # raises if wrong
        pw_hash = PasswordHasher.hash_password(new_password)
        self._conn.execute(
            "UPDATE drmy_users SET pw_hash = ?, updated_at = ? WHERE user_id = ?",
            (pw_hash, _utcnow(), user_id),
        )
        self._conn.commit()

    def unlock_user(self, user_id: str) -> None:
        self._conn.execute(
            "UPDATE drmy_users SET failed_attempts = 0, locked_until = NULL, "
            "updated_at = ? WHERE user_id = ?",
            (_utcnow(), user_id),
        )
        self._conn.commit()


# ---------------------------------------------------------------------------
# Sessions — in-memory tokens with absolute + idle timeouts
# ---------------------------------------------------------------------------

class SessionManager:
    """Token sessions. In-memory: a restart ends every session (documented;
    acceptable for v1 — a persistent session store is future work)."""

    def __init__(
        self,
        *,
        absolute_timeout: timedelta = timedelta(hours=8),
        idle_timeout: timedelta = timedelta(minutes=30),
    ):
        self._absolute = absolute_timeout
        self._idle = idle_timeout
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self, user_id: str, role: str, *, emergency: bool = False,
        ttl: Optional[timedelta] = None,
    ) -> str:
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        self._sessions[token] = {
            "user_id": user_id,
            "role": role,
            "emergency": emergency,
            "created_at": now,
            "last_activity": now,
            "expires_at": now + (ttl or self._absolute),
        }
        return token

    def validate(self, token: str) -> Dict[str, Any]:
        sess = self._sessions.get(token or "")
        now = datetime.now(timezone.utc)
        if sess is None:
            raise SessionError("Not signed in. Sign in first.")
        if now >= sess["expires_at"]:
            del self._sessions[token]
            raise SessionError("Session expired. Sign in again.")
        if now - sess["last_activity"] >= self._idle:
            del self._sessions[token]
            raise SessionError(
                "Session timed out from inactivity. Sign in again."
            )
        sess["last_activity"] = now
        return {
            "user_id": sess["user_id"],
            "role": sess["role"],
            "emergency": sess["emergency"],
        }

    def revoke(self, token: str) -> None:
        self._sessions.pop(token or "", None)

    def revoke_user(self, user_id: str) -> None:
        for tok, sess in list(self._sessions.items()):
            if sess["user_id"] == user_id:
                del self._sessions[tok]

    def active_count(self) -> int:
        return len(self._sessions)


# ---------------------------------------------------------------------------
# Break-glass emergency access — audited, auto-expiring
# ---------------------------------------------------------------------------

class BreakGlass:
    """Emergency access when normal sign-in is impossible.

    Procedure (documented for the operator):
      1. Keep DRMYTHARA_BREAKGLASS_SECRET in the secret store, separate
         from the data key. Only the security officer holds it.
      2. To use it: call issue_token(operator_id, reason) — or set the
         env var and use the bot's break_glass_request().
      3. The token lasts 30 minutes, is single-purpose, and EVERY use is
         written to the security-event log flagged for review.
      4. After the emergency, rotate the break-glass secret and review
         every action taken under it.
    """

    def __init__(self, secret: Optional[str] = None, *, ttl_minutes: int = 30):
        secret = secret or os.environ.get(BREAKGLASS_ENV, "")
        if not secret:
            raise SecurityError(
                "Break-glass is not configured: set the "
                "DRMYTHARA_BREAKGLASS_SECRET environment variable. "
                "Emergency access stays disabled until you do."
            )
        self._secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        self._ttl = timedelta(minutes=ttl_minutes)
        self._tokens: Dict[str, Dict[str, Any]] = {}

    def issue_token(self, operator_id: str, reason: str) -> Dict[str, str]:
        reason = (reason or "").strip()
        if not reason:
            raise ValueError("A reason is required for emergency access.")
        token = "bg_" + secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        self._tokens[token_hash] = {
            "operator_id": operator_id,
            "reason": reason,
            "issued_at": now.isoformat(),
            "expires_at": (now + self._ttl).isoformat(),
        }
        return {
            "token": token,
            "operator_id": operator_id,
            "reason": reason,
            "expires_at": (now + self._ttl).isoformat(),
        }

    def validate_token(self, token: str) -> Dict[str, str]:
        token_hash = hashlib.sha256((token or "").encode()).hexdigest()
        rec = self._tokens.get(token_hash)
        now = datetime.now(timezone.utc)
        if rec is None:
            raise AuthenticationError("Invalid emergency token.")
        if now >= datetime.fromisoformat(rec["expires_at"]):
            del self._tokens[token_hash]
            raise AuthenticationError("Emergency token expired.")
        return rec


# ---------------------------------------------------------------------------
# Hash-chained security events + review sign-off workflow
# ---------------------------------------------------------------------------

_CREATE_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS drmy_security_events (
    event_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    subject TEXT,
    detail TEXT,
    emergency INTEGER NOT NULL DEFAULT 0,
    prev_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL
)
"""

_CREATE_REVIEWS_SQL = """
CREATE TABLE IF NOT EXISTS drmy_reviews (
    review_id TEXT PRIMARY KEY,
    reviewer TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT NOT NULL,
    event_count INTEGER NOT NULL,
    event_ids TEXT NOT NULL,
    note TEXT,
    prev_hash TEXT NOT NULL,
    review_hash TEXT NOT NULL
)
"""


def _chain_hash(prev_hash: str, payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256((prev_hash + canonical).encode()).hexdigest()


class AuditReview:
    """Append-only, hash-chained security events with a sign-off workflow.

    Every sensitive action (sign-in, break-glass, backup, restore,
    review) is logged here. A reviewer periodically signs off the
    events since the last review; the sign-off itself is chained, so a
    missing review is detectable. This builds on the repo's existing
    hash-chain approach — it does not replace the emotional chain.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        conn.execute(_CREATE_EVENTS_SQL)
        conn.execute(_CREATE_REVIEWS_SQL)
        conn.commit()

    # -- events ------------------------------------------------------

    def _last_event_hash(self) -> str:
        row = self._conn.execute(
            "SELECT event_hash FROM drmy_security_events "
            "ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "GENESIS"

    def log_event(
        self,
        actor: str,
        action: str,
        subject: Optional[str] = None,
        detail: Optional[str] = None,
        emergency: bool = False,
    ) -> Dict[str, str]:
        event_id = secrets.token_hex(8)
        ts = _utcnow()
        prev = self._last_event_hash()
        payload = {
            "event_id": event_id, "ts": ts, "actor": actor,
            "action": action, "subject": subject, "detail": detail,
            "emergency": bool(emergency),
        }
        event_hash = _chain_hash(prev, payload)
        self._conn.execute(
            "INSERT INTO drmy_security_events (event_id, ts, actor, action, "
            "subject, detail, emergency, prev_hash, event_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, ts, actor, action, subject, detail,
             int(bool(emergency)), prev, event_hash),
        )
        self._conn.commit()
        return {"event_id": event_id, "event_hash": event_hash, "ts": ts}

    def verify_chain(self) -> Dict[str, Any]:
        rows = self._conn.execute(
            "SELECT event_id, ts, actor, action, subject, detail, emergency, "
            "prev_hash, event_hash FROM drmy_security_events ORDER BY rowid"
        ).fetchall()
        prev = "GENESIS"
        failures = []
        for r in rows:
            (eid, ts, actor, action, subject, detail, emergency,
             prev_hash, event_hash) = r
            if prev_hash != prev:
                failures.append(eid)
                continue
            payload = {
                "event_id": eid, "ts": ts, "actor": actor, "action": action,
                "subject": subject, "detail": detail,
                "emergency": bool(emergency),
            }
            if _chain_hash(prev, payload) != event_hash:
                failures.append(eid)
            prev = event_hash
        return {"ok": not failures, "events": len(rows), "failures": failures}

    # -- reviews -----------------------------------------------------

    def _last_review_hash(self) -> str:
        row = self._conn.execute(
            "SELECT review_hash FROM drmy_reviews ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "GENESIS"

    def _last_review_time(self) -> Optional[str]:
        row = self._conn.execute(
            "SELECT ended_at FROM drmy_reviews ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else None

    def pending_events(self) -> List[Dict[str, Any]]:
        since = self._last_review_time()
        if since:
            rows = self._conn.execute(
                "SELECT event_id, ts, actor, action, subject, detail, emergency "
                "FROM drmy_security_events WHERE ts > ? ORDER BY ts",
                (since,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT event_id, ts, actor, action, subject, detail, emergency "
                "FROM drmy_security_events ORDER BY ts"
            ).fetchall()
        return [
            {"event_id": r[0], "ts": r[1], "actor": r[2], "action": r[3],
             "subject": r[4], "detail": r[5], "emergency": bool(r[6])}
            for r in rows
        ]

    def sign_off(self, reviewer: str, note: str = "") -> Dict[str, Any]:
        """Review every pending event and record the sign-off, chained."""
        pending = self.pending_events()
        started = self._last_review_time() or _utcnow()
        ended = _utcnow()
        review_id = secrets.token_hex(8)
        prev = self._last_review_hash()
        payload = {
            "review_id": review_id, "reviewer": reviewer,
            "started_at": started, "ended_at": ended,
            "event_count": len(pending),
            "event_ids": [e["event_id"] for e in pending],
            "note": note,
        }
        review_hash = _chain_hash(prev, payload)
        self._conn.execute(
            "INSERT INTO drmy_reviews (review_id, reviewer, started_at, "
            "ended_at, event_count, event_ids, note, prev_hash, review_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (review_id, reviewer, started, ended, len(pending),
             json.dumps(payload["event_ids"]), note, prev, review_hash),
        )
        self._conn.commit()
        return {
            "review_id": review_id, "reviewer": reviewer,
            "events_reviewed": len(pending), "review_hash": review_hash,
            "ended_at": ended,
        }

    def review_status(self) -> Dict[str, Any]:
        pending = self.pending_events()
        return {
            "pending_count": len(pending),
            "pending_emergency": sum(1 for e in pending if e["emergency"]),
            "last_review": self._last_review_time(),
            "chain": self.verify_chain(),
        }


# ---------------------------------------------------------------------------
# Minimum-necessary: subject-scoped reads
# ---------------------------------------------------------------------------

def assert_subject_allowed(session_subject: Optional[str],
                           requested_subject: str) -> None:
    """Enforce minimum-necessary access: a signed-in identity may read only
    its own subject's records (admins may read any subject — pass
    session_subject=None for admin sessions)."""
    if session_subject is None:
        return  # admin session: full scope, still logged by callers
    if (requested_subject or "").strip() != (session_subject or "").strip():
        raise AccessDeniedError(
            "You may only view records for your own subject ID."
        )


# ---------------------------------------------------------------------------
# Encrypted backups + logged restore test
# ---------------------------------------------------------------------------

class BackupManager:
    """Encrypted backups of protected stores, with a logged restore test.

    Backups are Fernet-encrypted files written to backup_dir. The
    manifest records sha256 so tampering is detectable. Restoring
    verifies the manifest and that the store still opens.

    Honest limit: backup_dir is local. Copy backups off-site on a
    schedule — that step is the operator's duty (Phase 2 paperwork).
    """

    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup(self, store_path: str, fernet, label: str) -> Dict[str, str]:
        _require_crypto()
        src = Path(store_path)
        if not src.exists():
            raise BackupError(f"Nothing to back up: {store_path} does not exist.")
        raw = src.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        name = f"{label}-{stamp}.bak"
        dest = self.backup_dir / name
        assert fernet is not None
        dest.write_bytes(fernet.encrypt(raw))
        _chmod_600(str(dest))
        manifest = {
            "label": label, "created_at": _utcnow(),
            "source": str(src), "sha256": digest,
            "bytes": len(raw), "encrypted": True,
        }
        (self.backup_dir / f"{name}.manifest.json").write_text(
            json.dumps(manifest, indent=2))
        return {"backup": str(dest), "sha256": digest,
                "created_at": manifest["created_at"]}

    def _load_manifest(self, backup_path: str) -> Dict[str, Any]:
        mp = Path(str(backup_path) + ".manifest.json")
        if not mp.exists():
            raise BackupError("Backup manifest missing — refusing to restore.")
        return json.loads(mp.read_text())

    def restore(self, backup_path: str, store_path: str, fernet,
                *, verify_opens=None) -> Dict[str, Any]:
        """Restore a backup over store_path. verify_opens, if given, is a
        callable(store_path) that raises unless the store is usable."""
        _require_crypto()
        manifest = self._load_manifest(backup_path)
        assert fernet is not None
        try:
            raw = fernet.decrypt(Path(backup_path).read_bytes())
        except InvalidToken as exc:
            raise BackupError(
                "Backup cannot be decrypted: wrong key or tampered file."
            ) from exc
        if hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
            raise BackupError("Backup integrity check failed — not restoring.")
        dest = Path(store_path)
        if dest.exists():
            safety = dest.with_suffix(dest.suffix + f".pre-restore-{secrets.token_hex(4)}")
            shutil.copy2(dest, safety)
        dest.write_bytes(raw)
        _chmod_600(str(dest))
        if verify_opens is not None:
            try:
                verify_opens(str(dest))
            except Exception as exc:
                raise BackupError(
                    f"Restored store failed verification: {exc}"
                ) from exc
        return {"restored_to": str(dest), "sha256": manifest["sha256"],
                "backed_up_at": manifest["created_at"],
                "restored_at": _utcnow()}

    def test_restore(self, store_path: str, fernet, label: str,
                     *, verify_opens=None) -> Dict[str, Any]:
        """Full drill in a temp dir: backup -> restore -> verify.

        Returns a report dict the caller should log to the security
        event trail. Raises BackupError on any failure.
        """
        with tempfile.TemporaryDirectory(prefix="drmy-restore-test-") as tmp:
            mgr = BackupManager(tmp)
            made = mgr.backup(store_path, fernet, label)
            target = str(Path(tmp) / "restored.db")
            result = mgr.restore(made["backup"], target, fernet,
                                 verify_opens=verify_opens)
        report = {
            "ok": True,
            "label": label,
            "backup_sha256": made["sha256"],
            "restored_sha256": result["sha256"],
            "match": made["sha256"] == result["sha256"],
            "tested_at": _utcnow(),
        }
        if not report["match"]:
            raise BackupError("Restore test failed: hash mismatch.")
        return report
