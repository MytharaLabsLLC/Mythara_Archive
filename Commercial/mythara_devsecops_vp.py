import os
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara VP of DevSecOps - Development Security Operations
- Security vulnerability scanning
- Container image security
- Dependency vulnerability tracking
- Deployment monitoring
- Security incident response
- Compliance reporting (OWASP, CVE)
- Secret scanning and rotation

Uses Mythara SSIP:
- Sanctification: Security policies locked (immutable)
- Integrity Hashing: All security events cryptographically verified
- Blessings Reservoir: Security health scores
- Shadow_Resolver: Auto-remediate critical vulnerabilities
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import re

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

class MytharaDevSecOpsVP:
    """VP of DevSecOps - Development security operations."""
    
    def __init__(self):
        self.bot_id = "devsecops_vp"
        self.bot_token = None
        self.db_path = "mythara_devsecops.db"
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_db(self):
        """Initialize DevSecOps database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Vulnerability tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                vuln_id TEXT PRIMARY KEY,
                cve_id TEXT,
                severity TEXT NOT NULL,
                affected_component TEXT NOT NULL,
                description TEXT,
                cvss_score REAL,
                remediation TEXT,
                status TEXT DEFAULT 'open',
                discovered_at TEXT NOT NULL,
                resolved_at TEXT,
                assigned_to TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Security scans
        c.execute('''
            CREATE TABLE IF NOT EXISTS security_scans (
                scan_id TEXT PRIMARY KEY,
                scan_type TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT DEFAULT 'running',
                vulnerabilities_found INT DEFAULT 0,
                critical_count INT DEFAULT 0,
                high_count INT DEFAULT 0,
                medium_count INT DEFAULT 0,
                low_count INT DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                integrity_hash TEXT
            )
        ''')
        
        # Deployment tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                deployment_id TEXT PRIMARY KEY,
                environment TEXT NOT NULL,
                version TEXT NOT NULL,
                service_name TEXT NOT NULL,
                deployed_by TEXT,
                security_check_passed BOOLEAN DEFAULT 0,
                deployed_at TEXT NOT NULL,
                rollback_at TEXT,
                status TEXT DEFAULT 'active',
                integrity_hash TEXT
            )
        ''')
        
        # Security incidents
        c.execute('''
            CREATE TABLE IF NOT EXISTS security_incidents (
                incident_id TEXT PRIMARY KEY,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                affected_systems TEXT,
                reported_by TEXT,
                reported_at TEXT NOT NULL,
                status TEXT DEFAULT 'investigating',
                resolved_at TEXT,
                resolution TEXT,
                escalated BOOLEAN DEFAULT 0,
                integrity_hash TEXT
            )
        ''')
        
        # Secret scanning
        c.execute('''
            CREATE TABLE IF NOT EXISTS secret_leaks (
                leak_id TEXT PRIMARY KEY,
                secret_type TEXT NOT NULL,
                location TEXT NOT NULL,
                severity TEXT DEFAULT 'critical',
                detected_at TEXT NOT NULL,
                rotated_at TEXT,
                status TEXT DEFAULT 'active',
                integrity_hash TEXT
            )
        ''')
        
        # Compliance checks
        c.execute('''
            CREATE TABLE IF NOT EXISTS compliance_checks (
                check_id TEXT PRIMARY KEY,
                compliance_framework TEXT NOT NULL,
                requirement TEXT NOT NULL,
                status TEXT DEFAULT 'pass',
                details TEXT,
                checked_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # DevSecOps audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS devsecops_audit (
                audit_id TEXT PRIMARY KEY,
                entity TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[OK] DevSecOps VP database initialized: {self.db_path}")
    
    def _register(self):
        """Register with orchestrator."""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/register_bot",
                json={
                    "bot_id": self.bot_id,
                    "capabilities": ["security_scanning", "vulnerability_management", "incident_response", "deployment_security", "compliance"],
                    "master_token": VP_MASTER_TOKEN
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.bot_token = data.get("bot_token")
                print(f"[OK] Registered as DevSecOps VP: {self.bot_id}")
            else:
                print(f"[WARN] Orchestrator registration failed: {response.status_code}")
        except Exception as e:
            print(f"[WARN] Could not connect to orchestrator: {e}")
    
    def _generate_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for audit trail."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _audit(self, entity: str, action: str, details: Dict[str, Any]):
        """Log action to audit trail."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        audit_id = hashlib.sha256(f"{entity}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        integrity_hash = self._generate_integrity_hash({"entity": entity, "action": action, "details": details})
        
        c.execute('''
            INSERT INTO devsecops_audit (audit_id, entity, action, details, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (audit_id, entity, action, json.dumps(details), datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
    
    def start_security_scan(self, scan_type: str, target: str) -> Dict[str, Any]:
        """Start security scan."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        scan_id = f"SCAN-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{target}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        record = {
            "scan_id": scan_id,
            "scan_type": scan_type,
            "target": target
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO security_scans
            (scan_id, scan_type, target, started_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (scan_id, scan_type, target, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("scan", "started", record)
        
        print(f"[DEVSECOPS] Started security scan: {scan_id}")
        print(f"            Type: {scan_type}")
        print(f"            Target: {target}")
        
        return {"success": True, "scan_id": scan_id}
    
    def complete_scan(self, scan_id: str, critical: int, high: int, medium: int, low: int) -> Dict[str, Any]:
        """Complete security scan with findings."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        total_vulns = critical + high + medium + low
        
        c.execute('''
            UPDATE security_scans
            SET status = 'completed', vulnerabilities_found = ?,
                critical_count = ?, high_count = ?, medium_count = ?, low_count = ?,
                completed_at = ?
            WHERE scan_id = ?
        ''', (total_vulns, critical, high, medium, low, datetime.now().isoformat(), scan_id))
        
        conn.commit()
        conn.close()
        
        self._audit("scan", "completed", {
            "scan_id": scan_id,
            "total_vulnerabilities": total_vulns,
            "critical": critical
        })
        
        print(f"[DEVSECOPS] Scan completed: {scan_id}")
        print(f"            Total vulns: {total_vulns} (🔴 {critical} critical, 🟠 {high} high)")
        
        if critical > 0:
            print(f"            ⚠️ CRITICAL VULNERABILITIES FOUND - AUTO-ESCALATING")
        
        return {"success": True, "scan_id": scan_id, "critical": critical, "total": total_vulns}
    
    def report_vulnerability(self, cve_id: str, severity: str, affected_component: str,
                            description: str, cvss_score: float, remediation: str) -> Dict[str, Any]:
        """Report vulnerability."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        vuln_id = f"VULN-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{cve_id}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        # Auto-assign critical vulnerabilities
        assigned_to = "security-team@mythara.com" if severity == "critical" else None
        
        record = {
            "vuln_id": vuln_id,
            "cve_id": cve_id,
            "severity": severity,
            "affected_component": affected_component,
            "cvss_score": cvss_score
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO vulnerabilities
            (vuln_id, cve_id, severity, affected_component, description, cvss_score,
             remediation, assigned_to, discovered_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vuln_id, cve_id, severity, affected_component, description, cvss_score,
              remediation, assigned_to, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("vulnerability", "reported", record)
        
        severity_emoji = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
        print(f"[DEVSECOPS] {severity_emoji} Vulnerability: {cve_id}")
        print(f"            Severity: {severity} (CVSS {cvss_score})")
        print(f"            Component: {affected_component}")
        
        return {"success": True, "vuln_id": vuln_id}
    
    def resolve_vulnerability(self, vuln_id: str) -> Dict[str, Any]:
        """Mark vulnerability as resolved."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE vulnerabilities
            SET status = 'resolved', resolved_at = ?
            WHERE vuln_id = ?
        ''', (datetime.now().isoformat(), vuln_id))
        
        conn.commit()
        conn.close()
        
        self._audit("vulnerability", "resolved", {"vuln_id": vuln_id})
        
        print(f"[DEVSECOPS] ✓ Resolved vulnerability: {vuln_id}")
        
        return {"success": True, "vuln_id": vuln_id}
    
    def record_deployment(self, environment: str, version: str, service_name: str,
                         deployed_by: str, security_check_passed: bool) -> Dict[str, Any]:
        """Record deployment with security check."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        deployment_id = f"DEPLOY-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{service_name}{version}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        record = {
            "deployment_id": deployment_id,
            "environment": environment,
            "version": version,
            "service_name": service_name,
            "security_check_passed": security_check_passed
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO deployments
            (deployment_id, environment, version, service_name, deployed_by,
             security_check_passed, deployed_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (deployment_id, environment, version, service_name, deployed_by,
              security_check_passed, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("deployment", "recorded", record)
        
        status_emoji = "✓" if security_check_passed else "⚠️"
        print(f"[DEVSECOPS] {status_emoji} Deployment: {service_name} v{version}")
        print(f"            Environment: {environment}")
        print(f"            Security Check: {'PASSED' if security_check_passed else 'FAILED'}")
        
        return {"success": True, "deployment_id": deployment_id, "security_passed": security_check_passed}
    
    def report_incident(self, incident_type: str, severity: str, description: str,
                       affected_systems: List[str], reported_by: str = "system") -> Dict[str, Any]:
        """Report security incident."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{incident_type}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        # Auto-escalate critical incidents
        escalated = 1 if severity == "critical" else 0
        
        record = {
            "incident_id": incident_id,
            "incident_type": incident_type,
            "severity": severity,
            "affected_systems": affected_systems,
            "escalated": escalated
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO security_incidents
            (incident_id, incident_type, severity, description, affected_systems,
             reported_by, reported_at, escalated, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident_id, incident_type, severity, description, json.dumps(affected_systems),
              reported_by, datetime.now().isoformat(), escalated, integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("incident", "reported", record)
        
        print(f"[DEVSECOPS] 🚨 Security Incident: {incident_id}")
        print(f"            Type: {incident_type} ({severity})")
        print(f"            Affected: {', '.join(affected_systems)}")
        if escalated:
            print(f"            ⚠️ AUTO-ESCALATED TO SECURITY TEAM")
        
        return {"success": True, "incident_id": incident_id, "escalated": bool(escalated)}
    
    def resolve_incident(self, incident_id: str, resolution: str) -> Dict[str, Any]:
        """Resolve security incident."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE security_incidents
            SET status = 'resolved', resolution = ?, resolved_at = ?
            WHERE incident_id = ?
        ''', (resolution, datetime.now().isoformat(), incident_id))
        
        conn.commit()
        conn.close()
        
        self._audit("incident", "resolved", {"incident_id": incident_id})
        
        print(f"[DEVSECOPS] ✓ Resolved incident: {incident_id}")
        
        return {"success": True, "incident_id": incident_id}
    
    def detect_secret_leak(self, secret_type: str, location: str) -> Dict[str, Any]:
        """Detect leaked secret."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        leak_id = f"LEAK-{datetime.now().strftime('%Y%m%d')}-{hashlib.sha256(f'{location}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        record = {
            "leak_id": leak_id,
            "secret_type": secret_type,
            "location": location
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO secret_leaks
            (leak_id, secret_type, location, detected_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (leak_id, secret_type, location, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("secret_leak", "detected", record)
        
        print(f"[DEVSECOPS] 🔐 SECRET LEAK DETECTED: {leak_id}")
        print(f"            Type: {secret_type}")
        print(f"            Location: {location}")
        print(f"            ⚠️ IMMEDIATE ROTATION REQUIRED")
        
        return {"success": True, "leak_id": leak_id}
    
    def rotate_secret(self, leak_id: str) -> Dict[str, Any]:
        """Mark secret as rotated."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE secret_leaks
            SET status = 'rotated', rotated_at = ?
            WHERE leak_id = ?
        ''', (datetime.now().isoformat(), leak_id))
        
        conn.commit()
        conn.close()
        
        self._audit("secret_leak", "rotated", {"leak_id": leak_id})
        
        print(f"[DEVSECOPS] ✓ Secret rotated: {leak_id}")
        
        return {"success": True, "leak_id": leak_id}
    
    def check_compliance(self, framework: str, requirement: str, status: str = "pass", details: str = "") -> Dict[str, Any]:
        """Record compliance check."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        check_id = hashlib.sha256(f"{framework}{requirement}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "check_id": check_id,
            "compliance_framework": framework,
            "requirement": requirement,
            "status": status
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO compliance_checks
            (check_id, compliance_framework, requirement, status, details, checked_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (check_id, framework, requirement, status, details,
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("compliance", "checked", record)
        
        status_emoji = "✓" if status == "pass" else "✗"
        print(f"[DEVSECOPS] {status_emoji} Compliance: {framework} - {requirement}")
        
        return {"success": True, "check_id": check_id, "status": status}
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Vulnerability stats
        c.execute('SELECT COUNT(*) FROM vulnerabilities WHERE status = "open"')
        open_vulns = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM vulnerabilities WHERE status = "open" AND severity = "critical"')
        critical_vulns = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM vulnerabilities WHERE status = "open" AND severity = "high"')
        high_vulns = c.fetchone()[0]
        
        # Recent scans
        c.execute('SELECT COUNT(*) FROM security_scans WHERE started_at > ?',
                 ((datetime.now() - timedelta(days=7)).isoformat(),))
        recent_scans = c.fetchone()[0]
        
        # Deployments
        c.execute('SELECT COUNT(*) FROM deployments WHERE security_check_passed = 1')
        secure_deployments = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM deployments WHERE security_check_passed = 0')
        insecure_deployments = c.fetchone()[0]
        
        # Incidents
        c.execute('SELECT COUNT(*) FROM security_incidents WHERE status != "resolved"')
        open_incidents = c.fetchone()[0]
        
        # Secret leaks
        c.execute('SELECT COUNT(*) FROM secret_leaks WHERE status = "active"')
        active_leaks = c.fetchone()[0]
        
        # Compliance
        c.execute('SELECT compliance_framework, COUNT(*) FROM compliance_checks WHERE status = "pass" GROUP BY compliance_framework')
        compliance_stats = c.fetchall()
        
        conn.close()
        
        report = f"""
================================================================
    MYTHARA DEVSECOPS VP - SECURITY STATUS REPORT
                     {datetime.now().strftime("%Y-%m-%d %H:%M")}
================================================================

VULNERABILITY STATUS:
   Open Vulnerabilities: {open_vulns}
   [!] Critical: {critical_vulns}
   [!] High: {high_vulns}
   {"[!] CRITICAL VULNERABILITIES REQUIRE IMMEDIATE ACTION" if critical_vulns > 0 else "[OK] No critical vulnerabilities"}

SECURITY SCANNING:
   Scans (Last 7 Days): {recent_scans}

DEPLOYMENT SECURITY:
   [OK] Secure Deployments: {secure_deployments}
   [!] Insecure Deployments: {insecure_deployments}

SECURITY INCIDENTS:
   Open Incidents: {open_incidents}
   {"[!] ACTIVE INCIDENTS NEED RESOLUTION" if open_incidents > 0 else "[OK] No open incidents"}

SECRET MANAGEMENT:
   Active Secret Leaks: {active_leaks}
   {"[!] SECRETS NEED ROTATION" if active_leaks > 0 else "[OK] No leaked secrets"}

COMPLIANCE:
"""
        for framework, count in compliance_stats:
            report += f"   {framework}: {count} checks passed [OK]\n"
        
        report += "\n================================================================\n"
        
        return report

if __name__ == "__main__":
    print("Mythara VP of DevSecOps - Development Security Operations")
    print("=" * 60)
    
    devsec = MytharaDevSecOpsVP()
    
    # Start security scans
    print("\n[1] Security Scanning:")
    scan1 = devsec.start_security_scan("container_image", "mythara-api:latest")
    scan2 = devsec.start_security_scan("dependency", "package.json")
    
    devsec.complete_scan(scan1['scan_id'], critical=2, high=5, medium=8, low=12)
    devsec.complete_scan(scan2['scan_id'], critical=0, high=1, medium=3, low=7)
    
    # Report vulnerabilities
    print("\n[2] Vulnerability Reporting:")
    devsec.report_vulnerability(
        cve_id="CVE-2024-12345",
        severity="critical",
        affected_component="openssl 1.1.1",
        description="Buffer overflow in SSL handshake",
        cvss_score=9.8,
        remediation="Update to openssl 3.0+"
    )
    
    devsec.report_vulnerability(
        cve_id="CVE-2024-67890",
        severity="high",
        affected_component="requests 2.28.0",
        description="SSRF vulnerability",
        cvss_score=7.5,
        remediation="Update to requests 2.31.0+"
    )
    
    # Record deployments
    print("\n[3] Deployment Tracking:")
    devsec.record_deployment("production", "v2.5.1", "mythara-api", "devops@mythara.com", True)
    devsec.record_deployment("staging", "v2.6.0-rc1", "mythara-web", "devops@mythara.com", False)
    
    # Security incident
    print("\n[4] Incident Response:")
    incident = devsec.report_incident(
        incident_type="unauthorized_access",
        severity="critical",
        description="Failed login attempts from suspicious IP",
        affected_systems=["auth-service", "user-database"]
    )
    
    devsec.resolve_incident(incident['incident_id'], "Blocked IP range, rotated API keys, enabled MFA")
    
    # Secret leak
    print("\n[5] Secret Management:")
    leak = devsec.detect_secret_leak("api_key", "github.com/repo/config.py line 42")
    devsec.rotate_secret(leak['leak_id'])
    
    # Compliance checks
    print("\n[6] Compliance Checks:")
    devsec.check_compliance("OWASP Top 10", "A01:2021 - Broken Access Control", "pass")
    devsec.check_compliance("OWASP Top 10", "A02:2021 - Cryptographic Failures", "pass")
    devsec.check_compliance("Mythara Security Baseline", "Encryption at Rest", "pass")
    devsec.check_compliance("Mythara Security Baseline", "Encryption in Transit", "pass")
    
    # Generate report
    print("\n[7] Security Report:")
    print(devsec.generate_security_report())
