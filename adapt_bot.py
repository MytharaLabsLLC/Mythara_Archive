#!/usr/bin/env python3
"""
A.D.A.P.T. - Adaptive Defense & Penetration Tester
Part of the A.M.I.R. Cybersecurity Suite

Copyright © 2026 Mythara Labs LLC. All rights reserved.

A.D.A.P.T. runs REAL local security checks and ADAPTS its check set based
on what it finds: a finding in one check unlocks deeper follow-up checks
and raises the priority of related checks. Nothing here is simulated.

Honesty contract (enforced in code):
- Every check runs against real local targets (files, pip, permissions).
- A check that crashes reports UNKNOWN — never PASS, never "protected".
- No randomness decides any result. No hardcoded findings.
- Findings carry file:line evidence or they are not findings.

Check rounds:
- Round 1 (base): import_safety, dependency_audit, file_permissions, secret_scan
- Follow-ups unlock adaptively: entropy_scan (after secret hits),
  subprocess_audit (after shell/exec hits), setuid_scan (after perm hits).
"""

import ast
import json
import logging
import math
import os
import re
import stat
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.QUICKFIX_backups'}


class CheckStatus(Enum):
    """A check ends in exactly one of these. UNKNOWN is never a pass."""
    PASS = "PASS"        # ran clean, no findings
    FAIL = "FAIL"        # ran, found real issues
    UNKNOWN = "UNKNOWN"  # could not run or crashed — investigate, do not trust


@dataclass
class CheckResult:
    """The outcome of one real check."""
    check_id: str
    check_name: str
    status: CheckStatus
    findings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    error: Optional[str] = None
    duration_s: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AdaptiveCheck:
    """A registered check plus its adaptive wiring."""
    check_id: str
    name: str
    func: Callable[["ADAPTBot"], CheckResult]
    weight: float = 1.0
    enabled: bool = True
    # check_ids unlocked when THIS check FAILs
    unlocks_on_fail: List[str] = field(default_factory=list)
    # check_ids whose weight rises when THIS check FAILs
    boosts_on_fail: List[str] = field(default_factory=list)


def _iter_py_files(target: str):
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.py'):
                yield os.path.join(root, f)


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


class ADAPTBot:
    """
    A.D.A.P.T. — Adaptive Defense & Penetration Tester.

    Runs real checks, then adapts: failures unlock deeper follow-up checks
    and raise the weight of related checks in the next round. The adaptation
    log records every decision so the "adaptation" itself is auditable.
    """

    def __init__(self, target_system: str = "."):
        self.target_system = os.path.abspath(target_system)
        self.checks: Dict[str, AdaptiveCheck] = {}
        self.results: List[CheckResult] = []
        self.adaptation_log: List[str] = []
        self.findings_count = 0
        self.unknown_count = 0
        self._register_checks()
        logger.info("A.D.A.P.T. initialized | target=%s", self.target_system)

    # ------------------------------------------------------------------
    # Check registry
    # ------------------------------------------------------------------
    def _register_checks(self):
        base = [
            AdaptiveCheck("import_safety", "Import & code-execution safety (AST)",
                          self._check_import_safety,
                          unlocks_on_fail=["subprocess_audit"],
                          boosts_on_fail=["secret_scan"]),
            AdaptiveCheck("dependency_audit", "Dependency audit (pip)",
                          self._check_dependencies),
            AdaptiveCheck("file_permissions", "File permission scan",
                          self._check_file_permissions,
                          unlocks_on_fail=["setuid_scan"]),
            AdaptiveCheck("secret_scan", "Hardcoded secret scan",
                          self._check_secrets,
                          unlocks_on_fail=["entropy_scan"],
                          boosts_on_fail=["entropy_scan"]),
        ]
        followups = [
            AdaptiveCheck("entropy_scan", "High-entropy string scan (follow-up)",
                          self._check_entropy, enabled=False),
            AdaptiveCheck("subprocess_audit", "Subprocess call-site audit (follow-up)",
                          self._check_subprocess_sites, enabled=False),
            AdaptiveCheck("setuid_scan", "Setuid/setgid bit scan (follow-up)",
                          self._check_setuid, enabled=False),
        ]
        for c in base + followups:
            self.checks[c.check_id] = c

    # ------------------------------------------------------------------
    # Real checks (each returns CheckResult; crashes become UNKNOWN)
    # ------------------------------------------------------------------
    def _run_one(self, check: AdaptiveCheck) -> CheckResult:
        start = time.time()
        try:
            result = check.func()
            result.duration_s = round(time.time() - start, 2)
            return result
        except Exception as e:  # crashed check = UNKNOWN, never a pass
            return CheckResult(
                check_id=check.check_id,
                check_name=check.name,
                status=CheckStatus.UNKNOWN,
                error=f"{type(e).__name__}: {e}",
                duration_s=round(time.time() - start, 2),
            )

    def _check_import_safety(self) -> CheckResult:
        """AST-parse every .py file for dangerous execution primitives."""
        findings, evidence = [], []
        files_scanned = 0
        for path in _iter_py_files(self.target_system):
            files_scanned += 1
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    tree = ast.parse(f.read(), filename=path)
            except SyntaxError as e:
                findings.append(f"unparseable file (syntax error): {os.path.relpath(path, self.target_system)}")
                evidence.append(f"{os.path.relpath(path, self.target_system)}: syntax error at line {e.lineno}")
                continue
            rel = os.path.relpath(path, self.target_system)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name = ""
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = f"{getattr(func.value, 'id', '?')}.{func.attr}"
                    if name in ("eval", "exec"):
                        findings.append(f"{name}() call — arbitrary code execution")
                        evidence.append(f"{rel}:{node.lineno}")
                    elif name in ("os.system", "os.popen"):
                        findings.append(f"{name}() call — shell command execution")
                        evidence.append(f"{rel}:{node.lineno}")
                    elif name == "pickle.loads" or name == "pickle.load":
                        findings.append("pickle deserialization — arbitrary code on untrusted data")
                        evidence.append(f"{rel}:{node.lineno}")
                    elif "subprocess" in name:
                        for kw in node.keywords:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                findings.append("subprocess with shell=True — command injection risk")
                                evidence.append(f"{rel}:{node.lineno}")
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("import_safety", "Import & code-execution safety (AST)",
                           status, findings, evidence)

    def _check_dependencies(self) -> CheckResult:
        """Ask pip what's outdated and whether anything is broken."""
        findings, evidence = [], []
        try:
            out = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True, timeout=120, check=False,
            )
        except Exception as e:
            return CheckResult("dependency_audit", "Dependency audit (pip)",
                               CheckStatus.UNKNOWN, error=f"pip invocation failed: {e}")
        if out.returncode != 0:
            return CheckResult("dependency_audit", "Dependency audit (pip)",
                               CheckStatus.UNKNOWN,
                               error=f"pip exited {out.returncode}: {out.stderr.strip()[:200]}")
        try:
            outdated = json.loads(out.stdout or "[]")
        except json.JSONDecodeError as e:
            return CheckResult("dependency_audit", "Dependency audit (pip)",
                               CheckStatus.UNKNOWN, error=f"could not parse pip output: {e}")
        for pkg in outdated:
            name = pkg.get("name", "?")
            findings.append(f"outdated package: {name} {pkg.get('version', '?')} -> {pkg.get('latest_version', '?')} (review for CVEs)")
            evidence.append(f"{name}=={pkg.get('version', '?')} installed, {pkg.get('latest_version', '?')} available")
        # pip check for broken requirements
        try:
            chk = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True, text=True, timeout=120, check=False,
            )
            if chk.returncode != 0 and chk.stdout.strip():
                for line in chk.stdout.strip().splitlines()[:10]:
                    findings.append(f"broken dependency: {line.strip()}")
                    evidence.append(f"pip check: {line.strip()}")
        except Exception:
            pass  # pip check is best-effort; outdated scan already ran
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("dependency_audit", "Dependency audit (pip)", status, findings, evidence)

    def _check_file_permissions(self) -> CheckResult:
        """Find world-writable files and loose private keys."""
        findings, evidence = [], []
        for root, dirs, files in os.walk(self.target_system):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, self.target_system)
                try:
                    mode = os.stat(path).st_mode
                except OSError:
                    continue
                if mode & stat.S_IWOTH:
                    findings.append(f"world-writable file: {rel}")
                    evidence.append(f"{rel}: mode {oct(stat.S_IMODE(mode))}")
                low = f.lower()
                if low.endswith(('.pem', '.key')) or low in ('id_rsa', 'id_ed25519', 'id_dsa'):
                    if mode & (stat.S_IRGRP | stat.S_IROTH):
                        findings.append(f"private key readable by group/other: {rel}")
                        evidence.append(f"{rel}: mode {oct(stat.S_IMODE(mode))}")
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("file_permissions", "File permission scan", status, findings, evidence)

    def _check_secrets(self) -> CheckResult:
        """Regex scan for hardcoded secrets. Values are masked in evidence."""
        findings, evidence = [], []
        patterns = [
            (re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\']([^"\']{4,})["\']'), "password"),
            (re.compile(r'(?i)(api[_-]?key)\s*=\s*["\']([^"\']{8,})["\']'), "api key"),
            (re.compile(r'(?i)(secret[_-]?key|client[_-]?secret)\s*=\s*["\']([^"\']{8,})["\']'), "secret"),
            (re.compile(r'(?i)(auth[_-]?token|access[_-]?token)\s*=\s*["\']([^"\']{8,})["\']'), "token"),
            (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS access key id"),
            (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'), "private key block"),
        ]
        for path in _iter_py_files(self.target_system):
            rel = os.path.relpath(path, self.target_system)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                low = stripped.lower()
                if 'example' in low or 'dummy' in low or 'placeholder' in low or 'your_' in low:
                    continue
                for rx, label in patterns:
                    m = rx.search(line)
                    if m:
                        masked = (m.group(2)[:2] + "***") if m.lastindex and m.lastindex >= 2 else "***"
                        findings.append(f"possible hardcoded {label} in {rel}:{i}")
                        evidence.append(f"{rel}:{i}: {label} value masked ({masked})")
                        break
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("secret_scan", "Hardcoded secret scan", status, findings, evidence)

    def _check_entropy(self) -> CheckResult:
        """Follow-up: high-entropy string literals suggest embedded secrets."""
        findings, evidence = [], []
        str_rx = re.compile(r'["\']([A-Za-z0-9+/=_\-]{20,})["\']')
        for path in _iter_py_files(self.target_system):
            rel = os.path.relpath(path, self.target_system)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for m in str_rx.finditer(line):
                    s = m.group(1)
                    if _shannon_entropy(s) > 4.5:
                        findings.append(f"high-entropy string ({_shannon_entropy(s):.1f} bits) in {rel}:{i} — possible embedded secret")
                        evidence.append(f"{rel}:{i}: entropy {_shannon_entropy(s):.1f}, length {len(s)}, prefix {s[:6]}***")
                        break
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("entropy_scan", "High-entropy string scan (follow-up)",
                           status, findings, evidence)

    def _check_subprocess_sites(self) -> CheckResult:
        """Follow-up: enumerate every subprocess/os.exec call site with context."""
        findings, evidence = [], []
        for path in _iter_py_files(self.target_system):
            rel = os.path.relpath(path, self.target_system)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith('#'):
                    continue
                if re.search(r'\bsubprocess\.\w+\s*\(', line) or re.search(r'\bos\.(system|popen|exec\w+|spawn\w+)\s*\(', line):
                    has_shell = 'shell=True' in line
                    findings.append(f"subprocess call site in {rel}:{i}{' (shell=True)' if has_shell else ''}")
                    evidence.append(f"{rel}:{i}: {s[:120]}")
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("subprocess_audit", "Subprocess call-site audit (follow-up)",
                           status, findings, evidence)

    def _check_setuid(self) -> CheckResult:
        """Follow-up: setuid/setgid bits are privilege-escalation surface."""
        findings, evidence = [], []
        for root, dirs, files in os.walk(self.target_system):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, self.target_system)
                try:
                    mode = os.stat(path).st_mode
                except OSError:
                    continue
                if mode & (stat.S_ISUID | stat.S_ISGID):
                    findings.append(f"setuid/setgid bit set: {rel}")
                    evidence.append(f"{rel}: mode {oct(stat.S_IMODE(mode))}")
        status = CheckStatus.FAIL if findings else CheckStatus.PASS
        return CheckResult("setuid_scan", "Setuid/setgid bit scan (follow-up)",
                           status, findings, evidence)

    # ------------------------------------------------------------------
    # Adaptive assessment loop
    # ------------------------------------------------------------------
    def run_security_assessment(self, max_rounds: int = 3) -> Dict[str, Any]:
        """Run base checks, then adapt: failures unlock deeper follow-ups."""
        print("\n" + "=" * 70)
        print("A.D.A.P.T. — ADAPTIVE SECURITY ASSESSMENT (real checks only)")
        print("=" * 70)
        print(f"Target: {self.target_system}")

        for round_no in range(1, max_rounds + 1):
            due = [c for c in self.checks.values() if c.enabled
                   and not any(r.check_id == c.check_id for r in self.results)]
            if not due:
                break
            due.sort(key=lambda c: c.weight, reverse=True)
            print(f"\n— Round {round_no}: {len(due)} check(s), ordered by adapted weight —")
            for check in due:
                print(f"  ▶ {check.name} [weight {check.weight:.1f}]")
                result = self._run_one(check)
                self.results.append(result)
                tag = {"PASS": "✓", "FAIL": "✗", "UNKNOWN": "?"}[result.status.name]
                print(f"    {tag} {result.status.value} "
                      f"({len(result.findings)} findings, {result.duration_s}s)")
                if result.error:
                    print(f"      error: {result.error}")
                self._adapt(check, result)

        return self._generate_report()

    def _adapt(self, check: AdaptiveCheck, result: CheckResult):
        """Adaptation: failures unlock follow-ups and boost related checks."""
        if result.status == CheckStatus.FAIL:
            self.findings_count += len(result.findings)
            for fid in check.unlocks_on_fail:
                target = self.checks.get(fid)
                if target and not target.enabled:
                    target.enabled = True
                    msg = f"unlocked follow-up '{target.name}' (triggered by {check.check_id} FAIL)"
                    self.adaptation_log.append(msg)
                    logger.info("ADAPT: %s", msg)
            for bid in check.boosts_on_fail:
                target = self.checks.get(bid)
                if target:
                    target.weight += 1.0
                    msg = f"boosted '{target.name}' weight to {target.weight:.1f} (triggered by {check.check_id} FAIL)"
                    self.adaptation_log.append(msg)
        elif result.status == CheckStatus.UNKNOWN:
            self.unknown_count += 1
            msg = f"check '{check.name}' UNKNOWN — not counted as pass, needs investigation"
            self.adaptation_log.append(msg)
            logger.warning("ADAPT: %s", msg)

    def _generate_report(self) -> Dict[str, Any]:
        """Report real numbers. Nothing here is estimated or simulated."""
        by_status = Counter(r.status.name for r in self.results)
        report = {
            "target": self.target_system,
            "timestamp": datetime.utcnow().isoformat(),
            "checks_run": len(self.results),
            "passed": by_status.get("PASS", 0),
            "failed": by_status.get("FAIL", 0),
            "unknown": by_status.get("UNKNOWN", 0),
            "total_findings": self.findings_count,
            "adaptation_log": list(self.adaptation_log),
            "results": [
                {"check": r.check_name, "status": r.status.value,
                 "findings": r.findings, "evidence": r.evidence,
                 "error": r.error}
                for r in self.results
            ],
        }

        print("\n" + "=" * 70)
        print("A.D.A.P.T. FINAL REPORT (measured, not simulated)")
        print("=" * 70)
        print(f"Checks run: {report['checks_run']} | "
              f"PASS {report['passed']} | FAIL {report['failed']} | UNKNOWN {report['unknown']}")
        print(f"Total findings: {report['total_findings']}")
        if self.adaptation_log:
            print("\nAdaptation decisions:")
            for entry in self.adaptation_log:
                print(f"  • {entry}")
        for r in self.results:
            if r.status == CheckStatus.FAIL:
                print(f"\n✗ {r.check_name}:")
                for f_, e_ in zip(r.findings, r.evidence):
                    print(f"    - {f_}\n      {e_}")
        if report["unknown"]:
            print(f"\n? {report['unknown']} check(s) UNKNOWN — investigate, do not assume safe.")
        print("=" * 70)
        return report


def main():
    """CLI: python adapt_bot.py [target_dir]"""
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print("A.D.A.P.T. — Adaptive Defense & Penetration Tester")
    print(f"Target: {os.path.abspath(target)}\n")
    bot = ADAPTBot(target)
    report = bot.run_security_assessment()
    fails = report["failed"]
    unknowns = report["unknown"]
    print(f"\nExit: {'1 (findings or unknowns present)' if fails or unknowns else '0 (clean)'}")
    return 1 if (fails or unknowns) else 0


if __name__ == "__main__":
    sys.exit(main())
