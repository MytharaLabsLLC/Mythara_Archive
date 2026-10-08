#!/usr/bin/env python3
"""Witnessed journal — local product surface for the emotional chain.

A small stdlib-only HTTP server (no dependencies) backed by the real
soul_cradle.emotional_chain and soul_cradle.assessors modules. Serves a
PWA journal UI and a JSON API.

v1 scope, stated plainly:
  - Binds to 127.0.0.1 only. Single local user. /api/* requires an API
    key (JOURNAL_API_KEY env, "Authorization: Bearer <key>"); without
    the key the API answers 401 — fail closed.
  - TLS 1.2+ when JOURNAL_TLS_CERT and JOURNAL_TLS_KEY are set.
    Plaintext only with JOURNAL_ALLOW_PLAINTEXT_LOCAL=1 (dev); without
    either, the server refuses to start.
  - chain_data.json is Fernet-encrypted at rest when DRMYTHARA_DATA_KEY
    is set; plaintext otherwise (dev only, with a loud warning).
  - This is a working prototype, NOT production: real users need
    per-user auth, off-site backups, and terms of service. None of that
    exists yet.
  - Entity: Mythara Labs LLC, a Colorado domestic limited liability company
    (filed with the Colorado Secretary of State on October 4, 2026;
    ID #20268239831; member-managed).
    (Source of truth: COMPLIANCE_STATUS.md.)

Run:
    python3 journal_app/server.py
Then open http://127.0.0.1:8137
"""

import json
import os
import hmac
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from soul_cradle.emotional_chain import EmotionalChain, EmotionalRecord  # noqa: E402
from drmythara_security import DataKey, EncryptedFile  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_FILE = os.path.join(BASE_DIR, "chain_data.json")
PORT = 8137

chain = EmotionalChain(operator="journal-app-v1")

_PLAINTEXT_WARNED = False


def _warn_plaintext():
    global _PLAINTEXT_WARNED
    if not _PLAINTEXT_WARNED:
        _PLAINTEXT_WARNED = True
        print("⚠️  journal_app: no DRMYTHARA_DATA_KEY — chain_data.json is "
              "PLAINTEXT (dev only). Set the key for real use.")


def _save():
    fernet = DataKey.resolve(strict=False)
    payload = json.dumps([r.to_dict() for r in chain.chain]).encode("utf-8")
    tmp = DATA_FILE + ".tmp"
    if fernet is None:
        _warn_plaintext()
        with open(tmp, "wb") as f:
            f.write(payload)
        os.chmod(tmp, 0o600)
    else:
        EncryptedFile.write(tmp, payload, fernet)
    os.replace(tmp, DATA_FILE)


def _load():
    if not os.path.exists(DATA_FILE):
        return
    fernet = DataKey.resolve(strict=False)
    raw_bytes = open(DATA_FILE, "rb").read()
    looks_encrypted = raw_bytes[:6] == b"gAAAAA"  # Fernet token magic
    if fernet is not None and looks_encrypted:
        # Wrong key / tampered file → EncryptedFile.read raises (fail closed).
        raw = json.loads(EncryptedFile.read(DATA_FILE, fernet).decode("utf-8"))
    elif looks_encrypted:
        raise SystemExit(
            "chain_data.json is encrypted but DRMYTHARA_DATA_KEY is not set. "
            "Refusing to start.")
    else:
        if fernet is not None:
            print("ℹ️  journal_app: chain_data.json is legacy plaintext; "
                  "it will be encrypted on the next save.")
        else:
            _warn_plaintext()
        raw = json.loads(raw_bytes.decode("utf-8"))
    chain.chain = [EmotionalRecord(**d) for d in raw]
    for r in chain.chain:
        if r.record_id != "genesis":
            chain._prior_intensity[r.subject_id] = r.intensity


_load()

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "WitnessedJournal/1"

    def _json(self, obj, status=200):
        body = json.dumps(obj, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    # -- API ----------------------------------------------------------
    def _api_authorized(self) -> bool:
        """Single-operator API key. Fail closed: no key configured, or a
        wrong key, means 401 on every /api/* route."""
        key = os.environ.get("JOURNAL_API_KEY", "")
        if not key:
            return False
        return hmac.compare_digest(
            self.headers.get("Authorization", ""), f"Bearer {key}")

    def _require_api_key(self) -> bool:
        if self._api_authorized():
            return True
        self._json({"error": "API key required. Set JOURNAL_API_KEY and send "
                             "'Authorization: Bearer <key>'."}, 401)
        return False

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/") and not self._require_api_key():
            return
        if parsed.path == "/api/records":
            try:
                body = self._read_json()
                subject = (body.get("subject_id") or "").strip()
                emotion = (body.get("emotion") or "").strip()
                context = (body.get("context") or "").strip()
                intensity = float(body.get("intensity", 0.5))
                reporter = (body.get("reporter_id") or "").strip() or None
                if not subject or not emotion or not context:
                    return self._json(
                        {"error": "subject_id, emotion, and context are required"}, 400
                    )
                if not (0.0 <= intensity <= 1.0):
                    return self._json({"error": "intensity must be 0.0–1.0"}, 400)
                rec = chain.record(subject, emotion, intensity, context, reporter)
                _save()
                return self._json({
                    "record_id": rec.record_id,
                    "panel_verdict": rec.panel_verdict,
                    "verified": rec.verified,
                    "coercion_markers": rec.coercion_markers,
                    "flagged_by": [j["assessor_id"] for j in rec.judgments
                                   if j["verdict"] == "flagged"],
                    "record_hash": rec.record_hash,
                })
            except (ValueError, TypeError) as e:
                return self._json({"error": f"bad request: {e}"}, 400)
        return self._json({"error": "not found"}, 404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(parsed.query)
        subject = (q.get("subject", [""])[0] or "").strip()

        if parsed.path.startswith("/api/") and not self._require_api_key():
            return

        if parsed.path == "/api/history":
            if not subject:
                return self._json({"error": "subject query param required"}, 400)
            return self._json({"subject": subject, "records": chain.history(subject)})

        if parsed.path == "/api/analysis":
            if not subject:
                return self._json({"error": "subject query param required"}, 400)
            return self._json(chain.analyze_patterns(subject))

        if parsed.path == "/api/verify":
            ok, details = chain.verify()
            return self._json({"ok": ok, "records": details["records"],
                               "failures": details["failures"]})

        if parsed.path == "/api/export":
            # Full verification report: every record with seals, evidence
            # bases, and witness judgments — the chain-of-custody export.
            if not subject:
                return self._json({"error": "subject query param required"}, 400)
            ok, details = chain.verify()
            records = [r.to_dict() for r in chain.chain
                       if r.record_id == "genesis" or r.subject_id == subject]
            body = json.dumps({
                "exported_by": "witnessed-journal v1",
                "contract": ("This export proves the records below are unaltered. "
                             "It does not prove they are true, and it never "
                             "verifies what anyone felt."),
                "chain_valid": ok,
                "verification": details,
                "genesis_attestations": chain.chain[0].evidence_bases,
                "records": records,
            }, default=str, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Disposition",
                             f'attachment; filename="witnessed-record-{subject}.json"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # -- static ----------------------------------------------------
        path = parsed.path
        if path == "/":
            path = "/index.html"
        fs_path = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip("/")))
        if not fs_path.startswith(STATIC_DIR) or not os.path.isfile(fs_path):
            return self._json({"error": "not found"}, 404)
        ext = os.path.splitext(fs_path)[1]
        with open(fs_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    import ssl

    cert = os.environ.get("JOURNAL_TLS_CERT", "")
    keyf = os.environ.get("JOURNAL_TLS_KEY", "")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    if cert and keyf:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # TLS 1.2+, never plaintext
        ctx.load_cert_chain(cert, keyf)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        print(f"Witnessed journal on https://127.0.0.1:{PORT}  "
              f"(TLS 1.2+, local only)")
    elif os.environ.get("JOURNAL_ALLOW_PLAINTEXT_LOCAL", "") == "1":
        print(f"⚠️  Witnessed journal on http://127.0.0.1:{PORT}  "
              f"(PLAINTEXT dev only — no real data)")
    else:
        print("Refusing to serve without TLS.")
        print("Set JOURNAL_TLS_CERT and JOURNAL_TLS_KEY, or set "
              "JOURNAL_ALLOW_PLAINTEXT_LOCAL=1 for local dev.")
        raise SystemExit(2)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye.")
