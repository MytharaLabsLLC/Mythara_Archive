# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Reply triage.

Reads the inbox where replies actually land and routes them:

  interested / question -> ESCALATE to the operator (these are the money —
                         a human reply goes out as Herb; the machine never
                         pretends to hold a conversation)
  not_interested        -> polite close, sequence stops, no further mail
  unsubscribe / complaint -> suppress forever, sequence stops
  bounced               -> suppress, sequence stops
  autoresponder / noise  -> ignore, sequence continues

Classification is heuristic + explicit. Anything ambiguous escalates to
the operator rather than being auto-closed — losing a hot lead to a
misclassified "not interested" is worse than one extra escalation.

Inbox source: Yahoo IMAP (replies to mythara.engine@yahoo.com land in the
Yahoo mailbox — reading anywhere else means shouting into the void).
The legacy Gmail API path is kept as a fallback. Without either, triage
reports the inbox unreadable and the sequences keep their conservative
behavior (no reply assumed). The learning loop only scores observed
outcomes.
"""

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from . import config, prospects, safety, sequences

# --- classification ---------------------------------------------------------

INTERESTED = (
    "interested", "let's talk", "lets talk", "book a call", "schedule",
    "tell me more", "sounds good", "how much", "pricing", "pilot",
    "send over", "call next week", "works for me",
)
QUESTION = ("?", "how does", "what does", "do you", "can you", "what's the")
NOT_INTERESTED = (
    "not interested", "no thanks", "no thank you", "pass", "remove me",
    "don't contact", "not a fit", "no budget", "already have",
)
UNSUBSCRIBE = ("unsubscribe", "stop emailing", "opt out", "opt-out", "stop")
BOUNCE_HINTS = ("undeliverable", "delivery failure", "mailbox unavailable",
                "address not found", "bounce")
AUTORESPONDER_HINTS = ("out of office", "auto-reply", "autoreply",
                       "on vacation", "will respond when")


def classify_reply(subject: str, body: str) -> str:
    """Return one of: interested, question, not_interested, unsubscribe,
    bounced, autoresponder, unknown."""
    text = f"{subject}\n{body}".lower()
    if any(h in text for h in UNSUBSCRIBE):
        return "unsubscribe"
    if any(h in text for h in BOUNCE_HINTS):
        return "bounced"
    if any(h in text for h in AUTORESPONDER_HINTS):
        return "autoresponder"
    if any(h in text for h in NOT_INTERESTED):
        return "not_interested"
    if any(h in text for h in INTERESTED):
        return "interested"
    if "?" in body or any(h in text for h in QUESTION):
        return "question"
    return "unknown"


def route_classification(
    pid: str, classification: str, raw_subject: str = "", raw_snippet: str = ""
) -> Dict[str, Any]:
    """Apply a classification: update prospect, learning, escalation.

    Returns what was done. Hot leads ALWAYS escalate to Herb.
    """
    from . import learning

    d = prospects.get(pid)
    if not d:
        return {"ok": False, "reason": "unknown prospect"}
    variant = d["touches"][-1]["variant"] if d.get("touches") else "direct"

    if classification in ("interested", "question"):
        prospects.update(pid, status=prospects.STATUS_INTERESTED)
        learning.record_outcome(variant, classification)
        path = safety.escalate(
            f"HOT REPLY — {d['name']} <{d['email']}>",
            f"classification: {classification}\n"
            f"company: {d['company']} | role: {d['role']}\n"
            f"subject: {raw_subject}\nsnippet: {raw_snippet[:500]}\n\n"
            f"Operator: this one needs a human reply, written as Herb. "
            f"The machine stops here — it never pretends to hold a conversation.",
        )
        return {"ok": True, "action": "escalated_to_herb", "file": path}

    if classification == "not_interested":
        sequences.stop_sequence(pid, "not_interested")
        learning.record_outcome(variant, "not_interested")
        return {"ok": True, "action": "sequence_stopped"}

    if classification in ("unsubscribe", "bounced"):
        sequences.stop_sequence(pid, classification)
        learning.record_outcome(
            variant, "unsubscribe" if classification == "unsubscribe" else "bounced"
        )
        return {"ok": True, "action": f"suppressed_{classification}"}

    if classification == "autoresponder":
        return {"ok": True, "action": "ignored_autoresponder"}

    # unknown: escalate rather than misroute. Silence is not consent.
    path = safety.escalate(
        f"UNCLASSIFIED REPLY — {d['name']} <{d['email']}>",
        f"subject: {raw_subject}\nsnippet: {raw_snippet[:500]}\n\n"
        "The classifier could not route this. The operator decides.",
    )
    return {"ok": True, "action": "escalated_unknown", "file": path}


def yahoo_inbox_readable() -> bool:
    """True when the Yahoo app-password file exists, which is all IMAP
    login needs. Same file the SMTP sender uses — one secret, one place."""
    return config.YAHOO_KEY_FILE.exists()


def fetch_recent_replies_yahoo(days: int = 7) -> List[Dict[str, Any]]:
    """Pull recent inbox mail via Yahoo IMAP — this is where replies to
    mythara.engine@yahoo.com actually land. Returns [] when the key file is
    missing or on any IMAP failure (triage must never kill the pipeline).

    Each item: {'from': email, 'subject': ..., 'snippet': ..., 'thread_id': ...}
    """
    import imaplib
    import email as email_lib
    from email.header import decode_header

    password = ""
    try:
        key_file = config.YAHOO_KEY_FILE
        if not key_file.exists():
            return []
        password = key_file.read_text(encoding="utf-8").strip()
        if not password:
            return []

        def _decode(value) -> str:
            if not value:
                return ""
            parts = []
            for chunk, charset in decode_header(value):
                if isinstance(chunk, bytes):
                    parts.append(chunk.decode(charset or "utf-8", errors="replace"))
                else:
                    parts.append(chunk)
            return "".join(parts)

        since = (date.today() - timedelta(days=days)).strftime("%d-%b-%Y")
        out: List[Dict[str, Any]] = []
        with imaplib.IMAP4_SSL(config.YAHOO_IMAP_HOST, config.YAHOO_IMAP_PORT) as m:
            m.login(config.YAHOO_FROM_ADDR, password)
            m.select("INBOX", readonly=True)
            typ, data = m.search(None, f'(SINCE "{since}")')
            if typ != "OK" or not data or not data[0]:
                return []
            for mid in data[0].split()[-50:]:
                typ, msg_data = m.fetch(mid, "(RFC822)")
                if typ != "OK" or not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0][1]
                if not isinstance(raw, bytes):
                    continue
                msg = email_lib.message_from_bytes(raw)
                from_raw = _decode(msg.get("From", ""))
                mbox = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", from_raw)
                from_addr = (mbox.group(0).lower() if mbox else from_raw.lower())
                if from_addr == config.YAHOO_FROM_ADDR.lower():
                    continue  # our own sent mail, not a reply
                subject = _decode(msg.get("Subject", ""))
                snippet = ""
                try:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if payload:
                                    snippet = payload.decode(
                                        part.get_content_charset() or "utf-8",
                                        errors="replace",
                                    )[:500]
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            snippet = payload.decode("utf-8", errors="replace")[:500]
                        elif isinstance(msg.get_payload(), str):
                            snippet = msg.get_payload()[:500]
                except Exception:
                    snippet = ""
                out.append({
                    "from": from_addr,
                    "subject": subject,
                    "snippet": " ".join(snippet.split()),
                    "thread_id": mid.decode("utf-8", errors="replace"),
                })
        return out
    except Exception:
        return []
    finally:
        password = ""  # do not linger in memory


def fetch_recent_replies(service=None, days: int = 7) -> List[Dict[str, Any]]:
    """Pull recent inbox threads via the Gmail API. Returns [] when Gmail
    is unavailable (triage then reports BLOCKED; sequences stay conservative).

    Each item: {'from': email, 'subject': ..., 'snippet': ..., 'thread_id': ...}
    """
    if service is None:
        return []
    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", q="newer_than:{}d -in:sent".format(days), maxResults=50)
            .execute()
        )
    except Exception:
        return []
    out = []
    for m in results.get("messages", []):
        try:
            full = (
                service.users()
                .messages()
                .get(userId="me", id=m["id"], format="metadata",
                     metadataHeaders=["From", "Subject"])
                .execute()
            )
        except Exception:
            continue
        headers = {h["name"].lower(): h["value"]
                   for h in full.get("payload", {}).get("headers", [])}
        from_addr = headers.get("from", "")
        mbox = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", from_addr)
        out.append({
            "from": mbox.group(0).lower() if mbox else from_addr.lower(),
            "subject": headers.get("subject", ""),
            "snippet": full.get("snippet", ""),
            "thread_id": full.get("threadId", ""),
        })
    return out


def match_to_prospect(from_email: str) -> Optional[str]:
    """Find the prospect id for a reply sender's email."""
    from_email = from_email.strip().lower()
    for pid, d in prospects._load_all().items():
        if d["email"] == from_email:
            return pid
    return None
