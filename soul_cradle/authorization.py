"""
Soul Cradle authorization for Aries (the plating).

Every action Aries executes must carry a signed ActionEnvelope proving it
passed Soul Cradle bounds. Aries verifies the envelope before execution.
No valid governed signal means no execution.

Design notes (read before extending):
- Signatures are HMAC-SHA256 over a canonical JSON serialization. The key
  comes from the SOUL_CRADLE_KEY environment variable. If it is absent, an
  ephemeral development key is generated and a loud warning is printed:
  envelopes will not survive a restart and this is NOT production posture.
  Production path: back the authority with a KMS/HSM and never let the key
  touch application code or logs.
- This module enforces structural authorization: allowlisted action type,
  authorized issuer, intact payload, unexpired envelope. Semantic judgment
  (does this action serve its purpose without violating constitutional
  bounds) is delegated to a pluggable bounds_check callable. Wire it to
  PurposeResolver.check_bounds when the resolver is integrated; until then
  the default logs a warning that no semantic check is configured.
- The action handler registry is the only code Aries can run. Registering a
  new handler is a code-review event, not a runtime operation. There is no
  exec(), no eval(), and no shell=True anywhere in this trust boundary.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Canonical serialization + signing primitives
# ---------------------------------------------------------------------------


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _payload_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


# ---------------------------------------------------------------------------
# ActionEnvelope
# ---------------------------------------------------------------------------


@dataclass
class ActionEnvelope:
    """Signed authorization for one Aries action."""

    action_id: str
    action_type: str
    payload_hash: str
    issuer: str
    purpose: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    issued_at: int = 0
    expires_at: int = 0
    signature: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("signature", None)
        return d

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ActionEnvelope":
        return cls(
            **{
                k: d.get(k, getattr(cls, k) if hasattr(cls, k) else None)
                for k in (
                    "action_id",
                    "action_type",
                    "payload_hash",
                    "issuer",
                    "purpose",
                    "constraints",
                    "issued_at",
                    "expires_at",
                    "signature",
                )
            }
        )


# ---------------------------------------------------------------------------
# Handler registry — the only code Aries may run
# ---------------------------------------------------------------------------

Handler = Callable[[Dict[str, Any]], str]

_ACTION_HANDLERS: Dict[str, Handler] = {}
_HANDLER_ISSUERS: Dict[str, List[str]] = {}


def register_handler(
    name: str, func: Handler, allowed_issuers: Optional[List[str]] = None
) -> None:
    """Register a named action handler. Code-review event, not runtime config."""
    _ACTION_HANDLERS[name] = func
    _HANDLER_ISSUERS[name] = allowed_issuers if allowed_issuers is not None else []


def action_types() -> List[str]:
    return sorted(_ACTION_HANDLERS.keys())


def issuers_for(action_type: str) -> List[str]:
    return list(_HANDLER_ISSUERS.get(action_type, []))


# --- built-in safe handlers -------------------------------------------------


def _handle_emit_text(payload: Dict[str, Any]) -> str:
    text = payload.get("text", "")
    if not isinstance(text, str):
        raise ValueError("emit_text payload 'text' must be a string")
    return text[:4000]


def _handle_write_report(payload: Dict[str, Any]) -> str:
    filename = payload.get("filename", "")
    content = payload.get("content", "")
    if not isinstance(filename, str) or not isinstance(content, str):
        raise ValueError("write_report payload must be string filename/content")
    if len(content) > 200_000:
        raise ValueError("write_report content exceeds 200KB cap")
    # Constrain writes to the sandbox directory; refuse traversal outright.
    base = Path(os.environ.get("ARIES_OUT_DIR", "aries_out")).resolve()
    target = (base / filename).resolve()
    if target == base or base not in target.parents:
        raise ValueError(f"write_report refused: '{filename}' escapes sandbox")
    base.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"wrote {target} ({len(content)} chars)"


register_handler("emit_text", _handle_emit_text)
register_handler("write_report", _handle_write_report)


# ---------------------------------------------------------------------------
# SoulCradleAuthority — issues envelopes after bounds checks
# ---------------------------------------------------------------------------


class AuthorizationError(Exception):
    """Raised when an action cannot be authorized or verified."""


class SoulCradleAuthority:
    """
    Issues signed ActionEnvelopes. Structural checks enforced here:
    allowlisted action type, issuer permitted for that type, payload schema
    is the handler's business (it validates its own input).
    """

    def __init__(
        self,
        key: Optional[bytes] = None,
        issuer_policy: Optional[Dict[str, List[str]]] = None,
        handlers: Optional[Dict[str, Handler]] = None,
    ):
        if key is None:
            env_key = os.environ.get("SOUL_CRADLE_KEY", "")
            if env_key:
                key = env_key.encode("utf-8")
            else:
                key = secrets.token_bytes(32)
                print(
                    "⚠️  SOUL_CRADLE_KEY not set: using an ephemeral development "
                    "key. Envelopes will not verify after restart. "
                    "This is NOT production posture."
                )
        self._key = key
        # Handler registry is instance-scoped: it defaults to the shared
        # global registry, but a caller may pass a private one (the SERE
        # war machine does) so its action types never leak into anyone
        # else's world.
        self._handlers: Dict[str, Handler] = (
            handlers if handlers is not None else _ACTION_HANDLERS
        )
        # issuer -> list of action types it may request ("*" = all)
        self._issuer_policy: Dict[str, List[str]] = issuer_policy or {
            "soul_cradle": ["*"],
            "olympus_council": ["emit_text", "write_report"],
            "self_test": ["emit_text"],
        }
        self._bounds_check: Optional[
            Callable[[str, str, Dict[str, Any]], Optional[str]]
        ] = None
        self._bounds_warned = False
        self._audit_path = Path(
            os.environ.get("SOUL_CRADLE_AUDIT", "soul_cradle/audit.jsonl")
        )

    # -- configuration ------------------------------------------------------

    def set_bounds_check(
        self, fn: Callable[[str, str, Dict[str, Any]], Optional[str]]
    ) -> None:
        """Install semantic bounds check: fn(purpose, action_type, payload)
        returns a refusal reason, or None to allow."""
        self._bounds_check = fn

    def allow_issuer(self, issuer: str, action_types_: List[str]) -> None:
        self._issuer_policy[issuer] = list(action_types_)

    # -- issuance -----------------------------------------------------------

    def _sign(self, unsigned: Dict[str, Any]) -> str:
        return hmac.new(self._key, _canonical(unsigned), hashlib.sha256).hexdigest()

    def authorize(
        self,
        action_type: str,
        payload: Dict[str, Any],
        issuer: str,
        purpose: str,
        constraints: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 3600,
    ) -> ActionEnvelope:
        """Bounds-check and sign an action. Raises AuthorizationError on refusal."""
        now = int(time.time())

        if action_type not in self._handlers:
            raise AuthorizationError(f"unknown action type: {action_type!r}")
        allowed = self._issuer_policy.get(issuer, [])
        if action_type not in allowed and "*" not in allowed:
            self._audit(
                "authorize_denied",
                issuer,
                action_type,
                "issuer not permitted for action type",
            )
            raise AuthorizationError(
                f"issuer {issuer!r} not permitted for action type {action_type!r}"
            )
        if not isinstance(payload, dict):
            raise AuthorizationError("payload must be a dict")

        # Semantic bounds: Soul Cradle judgment, fail closed.
        if self._bounds_check is not None:
            refusal = self._bounds_check(purpose, action_type, payload)
            if refusal:
                self._audit(
                    "authorize_denied",
                    issuer,
                    action_type,
                    f"bounds check refused: {refusal}",
                )
                raise AuthorizationError(f"bounds check refused: {refusal}")
        else:
            if not self._bounds_warned:
                self._bounds_warned = True
                print(
                    "⚠️  No semantic bounds check configured on SoulCradleAuthority; "
                    "structural authorization only. Wire PurposeResolver.check_bounds."
                )

        env = ActionEnvelope(
            action_id=hashlib.sha256(
                f"{action_type}:{issuer}:{now}:{secrets.token_hex(8)}".encode()
            ).hexdigest()[:16],
            action_type=action_type,
            payload_hash=_payload_hash(payload),
            issuer=issuer,
            purpose=purpose,
            constraints=constraints or {},
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        env.signature = self._sign(env.unsigned_dict())
        self._audit("authorized", issuer, action_type, env.action_id)
        return env

    # -- verification (used by Aries before every execution) -----------------

    def verify(
        self, envelope: Optional[ActionEnvelope], payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Return (ok, reason). Never raises on bad input — fail closed."""
        if envelope is None:
            return False, "missing authorization envelope"
        if not isinstance(envelope, ActionEnvelope):
            return False, "envelope is not an ActionEnvelope"
        expected = self._sign(envelope.unsigned_dict())
        if not hmac.compare_digest(expected, envelope.signature or ""):
            self._audit(
                "verify_denied", envelope.issuer, envelope.action_type, "bad signature"
            )
            return False, "invalid signature"
        now = int(time.time())
        if now > envelope.expires_at:
            self._audit(
                "verify_denied",
                envelope.issuer,
                envelope.action_type,
                "envelope expired",
            )
            return False, "envelope expired"
        if _payload_hash(payload) != envelope.payload_hash:
            self._audit(
                "verify_denied",
                envelope.issuer,
                envelope.action_type,
                "payload hash mismatch (tampered payload)",
            )
            return False, "payload hash mismatch"
        if envelope.action_type not in self._handlers:
            return False, f"unknown action type: {envelope.action_type!r}"
        allowed = self._issuer_policy.get(envelope.issuer, [])
        if envelope.action_type not in allowed and "*" not in allowed:
            self._audit(
                "verify_denied",
                envelope.issuer,
                envelope.action_type,
                "issuer not permitted for action type",
            )
            return False, "issuer not permitted for action type"
        return True, "ok"

    def dispatch(self, envelope: ActionEnvelope, payload: Dict[str, Any]) -> str:
        """Verify then run the registered handler. Raises AuthorizationError."""
        ok, reason = self.verify(envelope, payload)
        if not ok:
            raise AuthorizationError(f"refused: {reason}")
        handler = self._handlers[envelope.action_type]
        result = handler(payload)
        self._audit(
            "executed", envelope.issuer, envelope.action_type, envelope.action_id
        )
        return result

    # -- audit ----------------------------------------------------------------

    def _audit(self, event: str, issuer: str, action_type: str, detail: str) -> None:
        try:
            self._audit_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._audit_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "ts": int(time.time()),
                            "event": event,
                            "issuer": issuer,
                            "action_type": action_type,
                            "detail": detail,
                        }
                    )
                    + "\n"
                )
        except OSError:
            pass
