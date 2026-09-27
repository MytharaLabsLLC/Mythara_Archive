#!/usr/bin/env python3
"""Witnessed journal — local product surface for the emotional chain.

A small stdlib-only HTTP server (no dependencies) backed by the real
soul_cradle.emotional_chain and soul_cradle.assessors modules. Serves a
PWA journal UI and a JSON API.

v1 scope, stated plainly:
  - Binds to 127.0.0.1 only. Single local user. No auth, no TLS.
  - This is a working prototype, NOT production: real users need auth,
    TLS, backups, and terms of service. None of that exists yet.
  - Entity: Mythara Labs LLC — a Colorado domestic limited liability
    company; Articles of Organization filed with the Colorado Secretary
    of State on September 27, 2026, pending completion; member-managed;
    sole member and organizer: Herbert Velez Jr.

Run:
    python3 journal_app/server.py
Then open http://127.0.0.1:8137
"""

import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soul_cradle.emotional_chain import EmotionalChain, EmotionalRecord  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_FILE = os.path.join(BASE_DIR, "chain_data.json")
PORT = 8137

chain = EmotionalChain(operator="journal-app-v1")


def _save():
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump([r.to_dict() for r in chain.chain], f)
    os.replace(tmp, DATA_FILE)


def _load():
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE) as f:
        raw = json.load(f)
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
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
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
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Witnessed journal on http://127.0.0.1:{PORT}  (local only, v1 prototype)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye.")
