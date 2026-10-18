#!/usr/bin/env python3
"""
S.E.R.E. - Survive, Evade, Resist, Escape
Part of the A.M.I.R. Cybersecurity Suite

Copyright © 2026 Mythara Labs LLC. All rights reserved.

S.E.R.E. doctrine (enforced in code):
  - Sandbox-only. The specimen is NEVER executed on the host.
  - Detect: the operator names an explicit specimen path. SERE invents
    nothing — no random threats, no fake source IPs.
  - Pull the specimen into an isolated sandbox directory and analyze the
    contained COPY only.
  - Quarantine: move the original into a quarantine directory, verify it is
    gone from its original location, keep chain of custody.
  - Produce a forensic profile: hashes, sizes, timestamps, permissions,
    type indicators, embedded indicators.
  - No hack-back, ever. No firewall changes, no IP blocking, no remote
    retaliation. Egress stays sealed by design: SERE makes zero network
    calls and takes zero network actions.
  - No fabricated numbers. Integrity is verified by hash comparison, not
    asserted. A failed step is reported FAILED, never "100%".

Every action is appended to a tamper-evident hash-chained JSONL event log.
"""

import hashlib
import json
import logging
import math
import os
import re
import shutil
import stat
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Indicators extracted from a specimen are just that — indicators found in
# the bytes. They are never presented as attribution.
URL_RE = re.compile(rb'https?://[^\s\'"<>]{4,120}')
IPV4_RE = re.compile(rb'\b(?:\d{1,3}\.){3}\d{1,3}\b')


class SpecimenStatus(Enum):
    DETECTED = "DETECTED"
    CONTAINED = "CONTAINED"
    QUARANTINED = "QUARANTINED"
    FAILED = "FAILED"


@dataclass
class ForensicProfile:
    """Measured facts about a specimen. Every field is observed, none inferred."""
    path: str
    sha256: str
    md5: str
    size_bytes: int
    mode: str
    mtime: str
    file_type: str
    entropy: float
    indicators: Dict[str, List[str]] = field(default_factory=dict)
    archive_members: Optional[List[str]] = None


@dataclass
class Event:
    seq: int
    timestamp: str
    action: str
    detail: str
    prev_hash: str
    event_hash: str = ""


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _file_type(path: str) -> str:
    """Magic-byte identification. Unknown is reported as unknown."""
    with open(path, 'rb') as f:
        magic = f.read(8)
    if magic.startswith(b'\x7fELF'):
        return "ELF executable"
    if magic.startswith(b'MZ'):
        return "PE executable (MZ)"
    if magic.startswith(b'PK\x03\x04'):
        return "ZIP archive"
    if magic.startswith(b'\x1f\x8b'):
        return "gzip archive"
    if magic.startswith(b'#!'):
        return "script (shebang)"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return "text"
    except (UnicodeDecodeError, OSError):
        return "unknown binary"


class SEREBot:
    """
    S.E.R.E. — sandbox-only specimen handling.

    Usage:
        bot = SEREBot(workdir="/path/to/case")
        specimen = bot.detect("/path/to/suspicious/file")
        bot.contain(specimen)      # copy into sandbox
        profile = bot.analyze(specimen)   # static forensics on the COPY
        bot.quarantine(specimen)   # move the original into quarantine
    """

    def __init__(self, workdir: str = ".sere_case"):
        self.workdir = os.path.abspath(workdir)
        self.sandbox_dir = os.path.join(self.workdir, "sandbox")
        self.quarantine_dir = os.path.join(self.workdir, "quarantine")
        self.log_path = os.path.join(self.workdir, "sere_events.jsonl")
        for d in (self.sandbox_dir, self.quarantine_dir):
            os.makedirs(d, exist_ok=True)
            os.chmod(d, 0o700)
        self._seq = self._load_seq()
        logger.info("S.E.R.E. initialized | workdir=%s (sandbox-only, no network actions)",
                    self.workdir)

    # ------------------------------------------------------------------
    # Tamper-evident event log (hash chain)
    # ------------------------------------------------------------------
    def _load_seq(self) -> int:
        if not os.path.exists(self.log_path):
            return 0
        seq = 0
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    seq = max(seq, json.loads(line).get("seq", 0))
        return seq

    def _last_hash(self) -> str:
        if not os.path.exists(self.log_path):
            return "GENESIS"
        last = "GENESIS"
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line).get("event_hash", last)
        return last

    def _log(self, action: str, detail: str) -> Event:
        self._seq += 1
        prev = self._last_hash()
        body = {"seq": self._seq,
                "timestamp": datetime.utcnow().isoformat(),
                "action": action, "detail": detail, "prev_hash": prev}
        event_hash = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode()).hexdigest()
        body["event_hash"] = event_hash
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(body) + "\n")
        return Event(**body)

    def verify_log(self) -> bool:
        """Verify the hash chain. Returns True only if every link checks out."""
        prev = "GENESIS"
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    e = json.loads(line)
                    if e.get("prev_hash") != prev:
                        return False
                    check = {k: e[k] for k in ("seq", "timestamp", "action", "detail", "prev_hash")}
                    if hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest() != e.get("event_hash"):
                        return False
                    prev = e["event_hash"]
        except (OSError, json.JSONDecodeError, KeyError):
            return False
        return True

    # ------------------------------------------------------------------
    # SURVIVE: detect — the operator names the specimen; SERE verifies it
    # ------------------------------------------------------------------
    def detect(self, specimen_path: str) -> Dict[str, Any]:
        """Register a specimen for handling. The path must be explicit and real."""
        self._log("DETECT_ATTEMPT", f"operator named specimen: {specimen_path}")
        if not specimen_path or not os.path.isfile(specimen_path):
            self._log("DETECT_FAILED", f"not a real file: {specimen_path}")
            return {"status": SpecimenStatus.FAILED.value,
                    "reason": f"specimen is not a real file: {specimen_path}"}
        real = os.path.realpath(specimen_path)
        self._log("DETECTED", f"specimen confirmed at {real}")
        return {"status": SpecimenStatus.DETECTED.value, "path": real}

    # ------------------------------------------------------------------
    # EVADE (the specimen's evasion ends here): contain into the sandbox
    # ------------------------------------------------------------------
    def contain(self, specimen: Dict[str, Any]) -> Dict[str, Any]:
        """Copy the specimen into the isolated sandbox directory."""
        src = specimen.get("path")
        if not src or not os.path.isfile(src):
            self._log("CONTAIN_FAILED", f"no valid specimen path: {src}")
            return {"status": SpecimenStatus.FAILED.value,
                    "reason": "no valid specimen to contain"}
        digest = _sha256_file(src)[:16]
        dest = os.path.join(self.sandbox_dir, f"specimen_{digest}.bin")
        shutil.copy2(src, dest)
        os.chmod(dest, 0o400)  # read-only inside the sandbox
        if _sha256_file(dest) != _sha256_file(src):
            self._log("CONTAIN_FAILED", "sandbox copy hash mismatch")
            return {"status": SpecimenStatus.FAILED.value,
                    "reason": "sandbox copy failed hash verification"}
        self._log("CONTAINED",
                  f"{src} -> {dest} (sha256 {_sha256_file(dest)[:16]}..., verified)")
        specimen["sandbox_copy"] = dest
        return {"status": SpecimenStatus.CONTAINED.value, "sandbox_copy": dest}

    # ------------------------------------------------------------------
    # RESIST: static forensics on the SANDBOX COPY only — never executed
    # ------------------------------------------------------------------
    def analyze(self, specimen: Dict[str, Any]) -> Dict[str, Any]:
        """Build the forensic profile from the contained copy. No execution."""
        target = specimen.get("sandbox_copy") or specimen.get("path")
        if not target or not os.path.isfile(target):
            self._log("ANALYZE_FAILED", f"no contained copy: {target}")
            return {"status": SpecimenStatus.FAILED.value,
                    "reason": "no contained copy to analyze"}
        self._log("ANALYZE_START", f"static forensics on contained copy {target} (no execution)")
        st = os.stat(target)
        with open(target, 'rb') as f:
            head = f.read(1048576)  # first MB is enough for indicators/entropy

        indicators: Dict[str, List[str]] = {}
        urls = sorted(set(m.decode('utf-8', 'replace') for m in URL_RE.findall(head)))[:20]
        ips = sorted(set(m.decode('utf-8', 'replace') for m in IPV4_RE.findall(head)))[:20]
        if urls:
            indicators["embedded_urls"] = urls
        if ips:
            indicators["embedded_ipv4"] = ips

        ftype = _file_type(target)
        members = None
        if ftype == "ZIP archive":
            try:
                with zipfile.ZipFile(target) as z:
                    members = z.namelist()[:50]  # listed, never extracted
            except zipfile.BadZipFile:
                members = []

        profile = ForensicProfile(
            path=target,
            sha256=_sha256_file(target),
            md5=_md5_file(target),
            size_bytes=st.st_size,
            mode=oct(stat.S_IMODE(st.st_mode)),
            mtime=datetime.utcfromtimestamp(st.st_mtime).isoformat(),
            file_type=ftype,
            entropy=round(_entropy(head), 2),
            indicators=indicators,
            archive_members=members,
        )
        self._log("ANALYZED",
                  f"profile: {profile.file_type}, {profile.size_bytes} bytes, "
                  f"sha256 {profile.sha256[:16]}..., entropy {profile.entropy}")
        return {"status": "PROFILED", "profile": profile}

    # ------------------------------------------------------------------
    # ESCAPE (sealed): quarantine the original, verify removal
    # ------------------------------------------------------------------
    def quarantine(self, specimen: Dict[str, Any]) -> Dict[str, Any]:
        """Move the original into quarantine and verify it is gone."""
        src = specimen.get("path")
        if not src or not os.path.isfile(src):
            self._log("QUARANTINE_FAILED", f"original not present (already moved?): {src}")
            return {"status": SpecimenStatus.FAILED.value,
                    "reason": "original specimen not present at quarantine time"}
        pre_hash = _sha256_file(src)
        dest = os.path.join(self.quarantine_dir, os.path.basename(src) + ".quarantined")
        shutil.move(src, dest)
        os.chmod(dest, 0o400)
        removed = not os.path.exists(src)
        intact = _sha256_file(dest) == pre_hash
        if removed and intact:
            self._log("QUARANTINED",
                      f"{src} -> {dest}; original location verified empty; hash intact")
            return {"status": SpecimenStatus.QUARANTINED.value,
                    "quarantine_path": dest, "hash_intact": True}
        self._log("QUARANTINE_FAILED",
                  f"removed={removed} intact={intact} for {src}")
        return {"status": SpecimenStatus.FAILED.value,
                "reason": f"quarantine incomplete (removed={removed}, intact={intact})"}

    # ------------------------------------------------------------------
    # Doctrine enforcement: egress stays sealed by design
    # ------------------------------------------------------------------
    def seal_egress(self) -> Dict[str, Any]:
        """SERE takes no network actions — no firewall edits, no IP blocks,
        no callbacks, no retaliation. This records that posture per case."""
        self._log("EGRESS_SEALED",
                  "no network actions taken or authorized: no firewall changes, "
                  "no IP blocking, no C2 callbacks, no hack-back")
        return {"egress": "sealed", "network_actions_taken": 0,
                "note": "SERE makes zero network calls by design"}

    def case_report(self) -> Dict[str, Any]:
        report = {
            "workdir": self.workdir,
            "events": self._seq,
            "log_intact": self.verify_log(),
            "log_path": self.log_path,
        }
        self._log("CASE_REPORT", f"log_intact={report['log_intact']}")
        return report


def main():
    """CLI: python sere_bot.py <specimen_path> [workdir]"""
    if len(sys.argv) < 2:
        print("Usage: python sere_bot.py <specimen_path> [workdir]")
        print("SERE doctrine: sandbox-only. The specimen is never executed.")
        return 2
    workdir = sys.argv[2] if len(sys.argv) > 2 else ".sere_case"
    bot = SEREBot(workdir)

    specimen = bot.detect(sys.argv[1])
    if specimen["status"] != SpecimenStatus.DETECTED.value:
        print(f"DETECT FAILED: {specimen['reason']}")
        return 1
    contained = bot.contain(specimen)
    if contained["status"] != SpecimenStatus.CONTAINED.value:
        print(f"CONTAIN FAILED: {contained['reason']}")
        return 1
    analysis = bot.analyze(specimen)
    profile = analysis.get("profile")
    if profile:
        print("\n— FORENSIC PROFILE (measured) —")
        print(f"  sha256: {profile.sha256}")
        print(f"  size:   {profile.size_bytes} bytes | type: {profile.file_type}")
        print(f"  entropy: {profile.entropy} | mode: {profile.mode}")
        if profile.indicators:
            for k, v in profile.indicators.items():
                print(f"  {k}: {v}")
    quarantined = bot.quarantine(specimen)
    bot.seal_egress()
    report = bot.case_report()
    print(f"\nQuarantine: {quarantined['status']}")
    print(f"Event log intact: {report['log_intact']} ({report['events']} events)")
    return 0 if quarantined["status"] == SpecimenStatus.QUARANTINED.value else 1


if __name__ == "__main__":
    sys.exit(main())
