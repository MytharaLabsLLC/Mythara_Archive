#!/usr/bin/env python3
"""
Q.U.I.C.K.F.I.X. Bot - Quick Universal Intelligent Code Knowledge Fixer
Part of the A.M.I.R. Cybersecurity Suite

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Q.U.I.C.K.F.I.X. (Quick Universal Intelligent Code Knowledge Fixer) can:
- Auto-detect vulnerabilities in code
- Generate intelligent patches using available resources
- Apply fixes without breaking existing functionality
- Create innovative solutions when standard tools aren't available
- Document everything it does
"""

import os
import sys
import re
import ast
import json
import hashlib
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - QUICKFIX - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Vulnerability:
    """A detected vulnerability"""
    file_path: str
    line_number: int
    vulnerability_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    vulnerable_code: str
    suggested_fix: str
    cwe_id: Optional[str] = None


@dataclass
class QuickFix:
    """A Q.U.I.C.K.F.I.X.-style intelligent patch"""
    vulnerability: Vulnerability
    fix_applied: bool
    fix_method: str
    backup_created: bool
    backup_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    dry_run: bool = False  # True = preview only, no files touched


class QuickFixBot:
    """
    Q.U.I.C.K.F.I.X. Bot - Quick Universal Intelligent Code Knowledge Fixer
    Part of the A.M.I.R. Cybersecurity Suite
    
    "Intelligent vulnerability fixing with available resources."
    """
    
    def __init__(self, target_directory: str = "."):
        self.target_directory = os.path.abspath(target_directory)
        self.vulnerabilities: List[Vulnerability] = []
        self.fixes: List[QuickFix] = []
        self.tools_available = self._check_available_tools()
        
        logger.info("⚡ Q.U.I.C.K.F.I.X. Bot initialized")
        logger.info(f"📂 Target directory: {self.target_directory}")
        logger.info(f"🛠️  Available tools: {', '.join(self.tools_available)}")
    
    def _check_available_tools(self) -> List[str]:
        """Check what tools we have to work with"""
        tools = ["python", "regex", "ast_parser"]
        
        # Check for optional tools
        try:
            import black
            tools.append("black")
        except ImportError:
            pass
        
        try:
            import pylint
            tools.append("pylint")
        except ImportError:
            pass
        
        return tools
    
    def scan_for_vulnerabilities(self, file_pattern: str = "*.py") -> List[Vulnerability]:
        """
        Scan for common security vulnerabilities
        
        QUICKFIX's approach: Use what we have - regex, AST parsing, pattern matching
        """
        logger.info("🔍 Scanning for vulnerabilities...")
        
        python_files = []
        for root, dirs, files in os.walk(self.target_directory):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        logger.info(f"📝 Found {len(python_files)} Python files to scan")
        
        for file_path in python_files:
            self._scan_file(file_path)
        
        logger.info(f"⚠️  Found {len(self.vulnerabilities)} vulnerabilities")
        return self.vulnerabilities
    
    def _scan_file(self, file_path: str):
        """Scan a single file for vulnerabilities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for common vulnerabilities
            self._check_sql_injection(file_path, content, lines)
            self._check_hardcoded_secrets(file_path, content, lines)
            self._check_weak_crypto(file_path, content, lines)
            self._check_insecure_deserialization(file_path, content, lines)
            self._check_command_injection(file_path, content, lines)
            self._check_path_traversal(file_path, content, lines)
            
        except Exception as e:
            logger.warning(f"⚠️  Could not scan {file_path}: {e}")
    
    def _check_sql_injection(self, file_path: str, content: str, lines: List[str]):
        """Check for SQL injection vulnerabilities"""
        # Pattern: String concatenation or f-strings in SQL queries
        sql_patterns = [
            (r'execute\s*\(\s*["\'].*?%s.*?["\'].*?%', 'String formatting in SQL'),
            (r'execute\s*\(\s*f["\']', 'F-string in SQL query'),
            (r'execute\s*\(\s*["\'].*?\+', 'String concatenation in SQL'),
            (r'cursor\.execute\s*\(\s*["\'].*?\.format\(', '.format() in SQL'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.vulnerabilities.append(Vulnerability(
                        file_path=file_path,
                        line_number=i,
                        vulnerability_type="SQL Injection",
                        severity="CRITICAL",
                        description=f"Potential SQL injection: {desc}",
                        vulnerable_code=line.strip(),
                        suggested_fix="Use parameterized queries with placeholders (?)",
                        cwe_id="CWE-89"
                    ))
    
    def _check_hardcoded_secrets(self, file_path: str, content: str, lines: List[str]):
        """Check for hardcoded secrets"""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded token'),
            (r'AWS_SECRET_ACCESS_KEY\s*=', 'AWS secret key'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments and common false positives
            if line.strip().startswith('#') or 'example' in line.lower() or 'dummy' in line.lower():
                continue
            
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.vulnerabilities.append(Vulnerability(
                        file_path=file_path,
                        line_number=i,
                        vulnerability_type="Hardcoded Secret",
                        severity="HIGH",
                        description=f"Potential {desc}",
                        vulnerable_code=line.strip(),
                        suggested_fix="Use environment variables or secrets manager",
                        cwe_id="CWE-798"
                    ))
    
    def _check_weak_crypto(self, file_path: str, content: str, lines: List[str]):
        """Check for weak cryptography"""
        weak_crypto = [
            (r'hashlib\.md5\(', 'MD5 is cryptographically broken'),
            (r'hashlib\.sha1\(', 'SHA1 is weak for security'),
            (r'DES\.new\(', 'DES is insecure'),
            (r'Random\.random\(', 'random() is not cryptographically secure'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in weak_crypto:
                if re.search(pattern, line):
                    # Check if it's being used for security (not just checksums)
                    context_lines = lines[max(0, i-3):min(len(lines), i+2)]
                    context = ' '.join(context_lines).lower()
                    
                    if any(word in context for word in ['password', 'secret', 'token', 'auth', 'encrypt', 'secure']):
                        self.vulnerabilities.append(Vulnerability(
                            file_path=file_path,
                            line_number=i,
                            vulnerability_type="Weak Cryptography",
                            severity="HIGH",
                            description=desc,
                            vulnerable_code=line.strip(),
                            suggested_fix="Use SHA256, SHA512, or bcrypt for security purposes",
                            cwe_id="CWE-327"
                        ))
    
    def _check_insecure_deserialization(self, file_path: str, content: str, lines: List[str]):
        """Check for insecure deserialization"""
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
        if 'pickle.loads(' in content or 'pickle.load(' in content:
            # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
            # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
            for i, line in enumerate(lines, 1):
                # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
                if 'pickle.load' in line:
                    self.vulnerabilities.append(Vulnerability(
                        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
                        file_path=file_path,
                        line_number=i,
                        # QUICKFIX WARNING: pickle.loads() can execute arbitrary code (CWE-502)
                        vulnerability_type="Insecure Deserialization",
                        severity="HIGH",
                        description="pickle.loads() can execute arbitrary code",
                        vulnerable_code=line.strip(),
                        suggested_fix="Use json.loads() or validate pickle data source",
                        cwe_id="CWE-502"
                    ))
    
    def _check_command_injection(self, file_path: str, content: str, lines: List[str]):
        """Check for command injection vulnerabilities"""
        dangerous_patterns = [
            (r'os\.system\s*\([^)]*\+', 'os.system with string concatenation'),
            (r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True', 'subprocess with shell=True'),
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX WARNING: File path constructed from user input (CWE-22)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            # QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)
            (r'eval\s*\(', 'eval() can execute arbitrary code'),
            (r'exec\s*\(', 'exec() can execute arbitrary code'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, line):
                    self.vulnerabilities.append(Vulnerability(
                        file_path=file_path,
                        # QUICKFIX WARNING: File path constructed from user input (CWE-22)
                        line_number=i,
                        vulnerability_type="Command Injection",
                        severity="CRITICAL",
                        description=desc,
                        vulnerable_code=line.strip(),
                        suggested_fix="Use subprocess with list arguments, avoid shell=True",
                        cwe_id="CWE-78"
                    ))
    # QUICKFIX WARNING: File path constructed from user input (CWE-22)
    
    def _check_path_traversal(self, file_path: str, content: str, lines: List[str]):
        """Check for path traversal vulnerabilities"""
        if 'open(' in content and ('user' in content.lower() or 'input' in content.lower()):
            for i, line in enumerate(lines, 1):
                if 'open(' in line and '+' in line:
                    self.vulnerabilities.append(Vulnerability(
                        file_path=file_path,
                        line_number=i,
                        vulnerability_type="Path Traversal",
                        severity="MEDIUM",
                        description="File path constructed from user input",
                        vulnerable_code=line.strip(),
                        suggested_fix="Validate and sanitize file paths, use os.path.abspath()",
                        cwe_id="CWE-22"
                    ))
    
    def fix_all_vulnerabilities(self, severity_threshold: str = "MEDIUM",
                                dry_run: bool = True) -> List[QuickFix]:
        """
        Fix all vulnerabilities QUICKFIX style.

        Args:
            severity_threshold: Only fix vulnerabilities at this level or higher
            dry_run: When True (default), compute fixes but write NOTHING.
                Set dry_run=False to apply for real. Real applies always
                create a verified backup first — a write without a backup
                is refused.
        """
        logger.info("🔧 QUICKFIX is getting to work...")
        
        severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        threshold_level = severity_order.get(severity_threshold, 1)

        # Group by file; within a file sort bottom-up so inserted lines never
        # invalidate the line numbers of fixes above them.
        sorted_vulns = sorted(
            [v for v in self.vulnerabilities if severity_order.get(v.severity, 0) >= threshold_level],
            key=lambda v: (v.file_path, -v.line_number)
        )

        self.fixes = []
        current_file = None
        file_group: List[Vulnerability] = []
        for vuln in sorted_vulns + [None]:  # sentinel flushes the last group
            path = vuln.file_path if vuln else None
            if path != current_file:
                if file_group:
                    self.fixes.extend(
                        self._apply_file_fixes(current_file, file_group, dry_run=dry_run))
                file_group = []
                current_file = path
            if vuln:
                file_group.append(vuln)

        applied = len([f for f in self.fixes if f.fix_applied])
        if dry_run:
            logger.info(f"🔍 DRY RUN: {len(self.fixes)} fixes previewed, 0 files written")
        else:
            logger.info(f"✅ QUICKFIX fixed {applied} vulnerabilities")
        return self.fixes

    def _apply_file_fixes(self, file_path: str, vulns: List[Vulnerability],
                           dry_run: bool = True) -> List[QuickFix]:
        """Apply every fix for one file.

        One backup per file (verified byte-identical before any write), fixes
        applied bottom-up so inserted lines never invalidate the line numbers
        of fixes above them, then a single write. A transform that cannot be
        done safely degrades to a warning comment and fix_applied=False —
        never a silently broken rewrite.
        """
        results: List[QuickFix] = []

        def refused(method: str, backup_path: Optional[str],
                    backup_ok: bool) -> List[QuickFix]:
            return [QuickFix(v, False, method, backup_ok, backup_path,
                             dry_run=dry_run) for v in vulns]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_text = f.read()
        except OSError as e:
            logger.error(f"❌ Could not read {file_path}: {e}")
            return refused(f"Failed: could not read file: {e}", None, False)

        lines = original_text.split('\n')

        # Pre-pass: a single `import os` at the top if any secret fix needs
        # it. Done once, before line fixes, so line numbers stay valid.
        shift = 0
        if (any(v.vulnerability_type == "Hardcoded Secret" for v in vulns)
                and not re.search(r'^\s*import\s+os\b', original_text, re.M)):
            lines.insert(0, 'import os')
            shift = 1

        # Bottom-up: vulns arrive sorted by descending line number.
        ok_by_vuln = {}
        for vuln in vulns:
            line_idx = vuln.line_number - 1 + shift
            if not (0 <= line_idx < len(lines)):
                ok_by_vuln[id(vuln)] = False
                continue
            try:
                ok_by_vuln[id(vuln)] = self._fix_one(lines, vuln, line_idx)
            except Exception as e:
                logger.error(f"❌ Transform failed for {vuln.vulnerability_type} "
                             f"at {file_path}:{vuln.line_number}: {e}")
                self._add_security_warning(lines, vuln, line_idx)
                ok_by_vuln[id(vuln)] = False

        if dry_run:
            for v in vulns:
                ok = ok_by_vuln.get(id(v), False)
                results.append(QuickFix(
                    v, False,
                    "dry-run preview: transform applies cleanly; no files written"
                    if ok else
                    "dry-run preview: pattern needs manual review; no files written",
                    False, dry_run=True))
            return results

        # REAL apply: exactly one backup, verified byte-identical, then write.
        backup_path = self._create_backup(file_path)
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_text = f.read()
        except OSError as e:
            logger.error(f"🛑 REFUSED: backup unreadable for {file_path}: {e}")
            return refused("REFUSED: backup unreadable", backup_path, False)
        if backup_text != original_text:
            logger.error(f"🛑 REFUSED: backup mismatch for {file_path} — not writing")
            return refused("REFUSED: backup could not be verified byte-identical",
                           backup_path, True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        for v in vulns:
            ok = ok_by_vuln.get(id(v), False)
            results.append(QuickFix(
                v, ok,
                "Q.U.I.C.K.F.I.X. automatic patch (backup verified)" if ok else
                "warning comment only — pattern needs manual review",
                True, backup_path))
        return results

    def _fix_one(self, lines: List[str], vuln: Vulnerability, line_idx: int) -> bool:
        """Dispatch one transform. Returns True only if the code was really fixed."""
        t = vuln.vulnerability_type
        if t == "SQL Injection":
            return self._fix_sql_injection(lines, vuln, line_idx)
        elif t == "Hardcoded Secret":
            return self._fix_hardcoded_secret(lines, vuln, line_idx)
        elif t == "Weak Cryptography":
            return self._fix_weak_crypto(lines, vuln, line_idx)
        elif t == "Command Injection":
            return self._fix_command_injection(lines, vuln, line_idx)
        else:
            self._add_security_warning(lines, vuln, line_idx)
            return False
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the file.

        The filename carries microsecond timestamps so multiple fixes to the
        same file never collide. The file is created with exclusive ('x')
        mode: if a backup somehow already exists at that path, this raises
        instead of silently overwriting a prior backup.
        """
        backup_dir = os.path.join(self.target_directory, '.QUICKFIX_backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        backup_filename = f"{os.path.basename(file_path)}.{timestamp}.{file_hash}.backup"
        backup_path = os.path.join(backup_dir, backup_filename)

        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'x', encoding='utf-8') as dst:
                dst.write(src.read())

        return backup_path
    
    def _fix_sql_injection(self, lines: List[str], vuln: Vulnerability, line_idx: int) -> bool:
        """Convert .format()-built SQL to a real parameterized query.

        cursor.execute("... '{}'".format(name))
          -> cursor.execute("... ?", (name))
        Anything that isn't this exact shape gets a warning comment and
        returns False — a wrong "fix" is worse than no fix.
        """
        line = lines[line_idx]
        indent = len(line) - len(line.lstrip())

        m = re.search(r'\.format\(([^()]*)\)', line)
        if m:
            args = m.group(1).strip()
            if args:
                fixed = line[:m.start()] + line[m.end():]
                fixed = re.sub(r'\{\w*\}', '?', fixed)
                fixed = fixed.replace("'?'", "?").replace('"?"', '?')
                stripped = fixed.rstrip()
                if stripped.endswith(')'):
                    fixed = stripped[:-1].rstrip() + ", (%s))" % args
                    comment = (' ' * indent +
                               '# QUICKFIX FIX: Converted to parameterized query to prevent SQL injection (CWE-89)')
                    lines[line_idx] = comment + '\n' + fixed
                    return True

        self._add_security_warning(lines, vuln, line_idx)
        return False

    def _fix_hardcoded_secret(self, lines: List[str], vuln: Vulnerability, line_idx: int) -> bool:
        """Replace a hardcoded secret with an environment-variable lookup.

        (`import os` is handled once per file by the caller pre-pass.)
        """
        line = lines[line_idx]

        match = re.search(r'(\w+)\s*=\s*["\']', line)
        if match:
            var_name = match.group(1)
            indent = len(line) - len(line.lstrip())

            comment = ' ' * indent + '# QUICKFIX FIX: Moved to environment variable (CWE-798)'
            fixed_line = (' ' * indent +
                          f'{var_name} = os.getenv("{var_name.upper()}", "")  # Set via environment')

            lines[line_idx] = comment + '\n' + fixed_line
            return True

        self._add_security_warning(lines, vuln, line_idx)
        return False

    def _fix_weak_crypto(self, lines: List[str], vuln: Vulnerability, line_idx: int) -> bool:
        """Upgrade MD5/SHA1 to SHA256."""
        line = lines[line_idx]

        fixed_line = line.replace('hashlib.md5(', 'hashlib.sha256(')
        fixed_line = fixed_line.replace('hashlib.sha1(', 'hashlib.sha256(')

        if fixed_line == line:
            self._add_security_warning(lines, vuln, line_idx)
            return False

        indent = len(line) - len(line.lstrip())
        comment = ' ' * indent + '# QUICKFIX FIX: Upgraded to SHA256 for security (CWE-327)'

        lines[line_idx] = comment + '\n' + fixed_line
        return True

    def _fix_command_injection(self, lines: List[str], vuln: Vulnerability, line_idx: int) -> bool:
        """Flip shell=True to shell=False only when the command is already a
        list (e.g. subprocess.run(["ls", d], shell=True)) — there the flip is
        behavior-preserving. A string command would break, so it gets a
        warning comment and manual review instead."""
        line = lines[line_idx]
        indent = len(line) - len(line.lstrip())
        comment = ' ' * indent + '# QUICKFIX FIX: Removed shell=True to prevent command injection (CWE-78)'

        if 'shell=True' in line and re.search(r'\(\s*\[', line):
            fixed_line = line.replace('shell=True', 'shell=False')
            lines[line_idx] = comment + '\n' + fixed_line
            return True

        self._add_security_warning(lines, vuln, line_idx)
        return False

    def _add_security_warning(self, lines: List[str], vuln: Vulnerability, line_idx: int):
        """Add a security warning comment (no code change)."""
        line = lines[line_idx]

        indent = len(line) - len(line.lstrip())
        comment = ' ' * indent + f'# QUICKFIX WARNING: {vuln.description} ({vuln.cwe_id})'

        lines.insert(line_idx, comment)
    
    def generate_report(self) -> str:
        """Generate a comprehensive QUICKFIX report"""
        report = f"""
{'='*80}
🔧 QUICKFIX BOT SECURITY REPORT
{'='*80}

Mission: Secure the codebase with available resources
Target: {self.target_directory}
Timestamp: {datetime.utcnow().isoformat()}

VULNERABILITIES DETECTED:
{'='*80}
Total: {len(self.vulnerabilities)}
CRITICAL: {len([v for v in self.vulnerabilities if v.severity == 'CRITICAL'])}
HIGH: {len([v for v in self.vulnerabilities if v.severity == 'HIGH'])}
MEDIUM: {len([v for v in self.vulnerabilities if v.severity == 'MEDIUM'])}
LOW: {len([v for v in self.vulnerabilities if v.severity == 'LOW'])}

FIXES APPLIED:
{'='*80}
Total Fixes Attempted: {len(self.fixes)}
Successful: {len([f for f in self.fixes if f.fix_applied])}
Failed: {len([f for f in self.fixes if not f.fix_applied])}
Backups Created: {len([f for f in self.fixes if f.backup_created])}

DETAILED FINDINGS:
{'='*80}
"""
        
        for i, vuln in enumerate(self.vulnerabilities, 1):
            report += f"""
[{i}] {vuln.severity} - {vuln.vulnerability_type}
File: {os.path.relpath(vuln.file_path, self.target_directory)}
Line: {vuln.line_number}
CWE: {vuln.cwe_id or 'N/A'}
Description: {vuln.description}
Code: {vuln.vulnerable_code}
Fix: {vuln.suggested_fix}
{'-'*80}
"""
        
        report += f"""
{'='*80}
QUICKFIX's Notes:
{'-'*80}
- All fixes have been backed up to .QUICKFIX_backups/
- Review changes before committing
- Test thoroughly after applying fixes
- "I love it when a plan comes together!" - QUICKFIX

Tools Used: {', '.join(self.tools_available)}
{'='*80}
"""
        
        return report
    
    def save_report(self, filename: str = "QUICKFIX_security_report.txt"):
        """Save the report to a file"""
        report = self.generate_report()
        report_path = os.path.join(self.target_directory, filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Report saved to: {report_path}")
        return report_path


def main():
    """QUICKFIX Bot main function"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    🔧 QUICKFIX BOT 🔧                     ║
║        "Never leave home without duct tape and code"      ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize QUICKFIX
    target = os.getcwd()
    QUICKFIX = QuickFixBot(target)
    
    # Scan for vulnerabilities
    print("\n🔍 Phase 1: Reconnaissance")
    vulnerabilities = QUICKFIX.scan_for_vulnerabilities()
    
    if not vulnerabilities:
        print("✅ No vulnerabilities detected! System is secure.")
        return 0
    
    # Show findings
    print(f"\n⚠️  Found {len(vulnerabilities)} vulnerabilities:")
    for v in vulnerabilities[:10]:  # Show first 10
        print(f"  - {v.severity}: {v.vulnerability_type} in {os.path.basename(v.file_path)}:{v.line_number}")
    
    if len(vulnerabilities) > 10:
        print(f"  ... and {len(vulnerabilities) - 10} more")
    
    # Ask to fix — dry run first, always
    print("\n🔧 Phase 2: Preview Fixes (DRY RUN — nothing will be written)")
    fixes = QUICKFIX.fix_all_vulnerabilities(severity_threshold="MEDIUM", dry_run=True)
    previewed = len([f for f in fixes if f.dry_run])
    print(f"🔍 {previewed} fixes previewed, 0 files written.")

    print("\nApply fixes for real? (backups are created and verified first) (y/n)")
    response = input("> ").strip().lower()

    if response == 'y':
        fixes = QUICKFIX.fix_all_vulnerabilities(severity_threshold="MEDIUM", dry_run=False)
        applied = len([f for f in fixes if f.fix_applied])
        refused = len([f for f in fixes if not f.fix_applied and not f.dry_run])
        print(f"✅ Applied {applied} fixes ({refused} refused/failed)")
    else:
        print("⏭️  Skipped — no files were modified.")
    
    # Generate report
    print("\n📄 Phase 3: Documentation")
    report_path = QUICKFIX.save_report()
    print(f"Report saved to: {report_path}")
    
    # Show summary
    print("\n" + "="*60)
    print("🎯 QUICKFIX Mission Complete!")
    print("="*60)
    print(QUICKFIX.generate_report())
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
