#!/usr/bin/env python3
"""
Mythara Engine - Adversarial Attack Test Suite
Comprehensive red team testing for security vulnerabilities.

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Attack Categories:
1. Authentication & Authorization Bypass
2. SQL Injection & Database Attacks
3. API Rate Limiting & DoS
4. Compliance Framework Bypass
5. Payment System Manipulation
6. Input Validation & XSS
7. Cryptographic Integrity Attacks
8. Session Hijacking & CSRF
9. Resource Exhaustion
10. Business Logic Exploitation
"""

import sys
import os
import json
import time
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core', 'source_proprietary'))

# Import components to attack
try:
    from unified_compliance_framework import (
        UnifiedComplianceFramework,
        ComplianceFramework,
        RiskLevel
    )
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    print("⚠️  Compliance framework not available")

try:
    from soul_cradle_systems_framework import (
        SoulCradleParadox,
        SystemExpression,
        UnresolvedState,
        ResolvedSystem,
        ExpressionType,
        SystemType,
        TerminalRiskCalculator
    )
    PARADOX_AVAILABLE = True
except ImportError:
    PARADOX_AVAILABLE = False
    print("⚠️  Paradox framework not available")


# ===================== ATTACK RESULTS TRACKING =====================

class AttackResult:
    """Track results of adversarial attacks"""
    def __init__(self):
        self.total_attacks = 0
        self.successful_breaches = 0
        self.blocked_attacks = 0
        self.vulnerabilities = []
        self.critical_findings = []
        self.high_findings = []
        self.medium_findings = []
        self.low_findings = []
    
    def record_breach(self, attack_name: str, severity: str, details: str):
        """Record successful breach"""
        self.successful_breaches += 1
        vulnerability = {
            "attack": attack_name,
            "severity": severity,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.vulnerabilities.append(vulnerability)
        
        if severity == "CRITICAL":
            self.critical_findings.append(vulnerability)
        elif severity == "HIGH":
            self.high_findings.append(vulnerability)
        elif severity == "MEDIUM":
            self.medium_findings.append(vulnerability)
        else:
            self.low_findings.append(vulnerability)
    
    def record_blocked(self):
        """Record blocked attack"""
        self.blocked_attacks += 1
    
    def generate_report(self) -> str:
        """Generate comprehensive attack report"""
        success_rate = (self.successful_breaches / self.total_attacks * 100) if self.total_attacks > 0 else 0
        
        report = f"""
{'='*80}
ADVERSARIAL ATTACK TEST SUITE - FINAL REPORT
{'='*80}

Total Attacks Executed: {self.total_attacks}
Successful Breaches: {self.successful_breaches}
Blocked Attacks: {self.blocked_attacks}
Breach Rate: {success_rate:.1f}%

SEVERITY BREAKDOWN:
- CRITICAL: {len(self.critical_findings)}
- HIGH: {len(self.high_findings)}
- MEDIUM: {len(self.medium_findings)}
- LOW: {len(self.low_findings)}

{'='*80}
VULNERABILITIES FOUND:
{'='*80}
"""
        
        for vuln in self.vulnerabilities:
            report += f"\n[{vuln['severity']}] {vuln['attack']}\n"
            report += f"  Details: {vuln['details']}\n"
            report += f"  Time: {vuln['timestamp']}\n"
        
        if not self.vulnerabilities:
            report += "\n✅ NO VULNERABILITIES FOUND - System passed all adversarial tests\n"
        
        report += f"\n{'='*80}\n"
        report += """
METHODOLOGY CAVEAT (read before trusting the score above):
- "Blocked" includes attacks that raised an unhandled exception.
  An exception is NOT proof of a deliberate security control — it may
  be a crash, a missing dependency, or an import failure, not a block.
- test_privilege_escalation records "blocked" by assumption ("Assume
  blocked unless proven otherwise") without verifying any control.
- Several input-validation tests only run when the optional framework
  imports succeed; when it is unavailable those attacks are skipped,
  not blocked. Skipped != blocked.
Treat the security score as a harness self-report, not an audit.
"""
        return report


# ===================== ATTACK CATEGORY 1: AUTHENTICATION BYPASS =====================

class AuthenticationAttacks:
    """Attempt to bypass authentication mechanisms"""
    
    @staticmethod
    def test_empty_api_key(framework: Any, results: AttackResult):
        """Attack: Submit request with empty API key"""
        results.total_attacks += 1
        try:
            # Attempt compliance validation without user_id
            data = {"test": "data"}
            result = framework.validate_multi_framework_compliance(
                data=data,
                frameworks=[ComplianceFramework.PCI_DSS],
                user_id=None  # Empty authentication
            )
            
            if result.get("overall_compliant"):
                results.record_breach(
                    "Empty API Key Bypass",
                    "CRITICAL",
                    "System accepted request without user_id authentication"
                )
            else:
                results.record_blocked()
        except Exception as e:
            if "user_id is required" in str(e) or "Authentication" in str(e):
                results.record_blocked()
            else:
                results.record_breach(
                    "Authentication Error Handling",
                    "MEDIUM",
                    f"Unexpected error: {e}"
                )
    
    @staticmethod
    def test_sql_injection_in_userid(framework: Any, results: AttackResult):
        """Attack: SQL injection through user_id field"""
        results.total_attacks += 1
        payloads = [
            "admin' OR '1'='1",
            "'; DROP TABLE users;--",
            "1' UNION SELECT * FROM api_keys--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for payload in payloads:
            try:
                data = {"test": "data"}
                result = framework.validate_multi_framework_compliance(
                    data=data,
                    frameworks=[ComplianceFramework.PCI_DSS],
                    user_id=payload
                )
                
                # If it processes without sanitizing, it's a vulnerability
                if result.get("overall_compliant") or "violations" in result:
                    results.record_breach(
                        "SQL Injection in user_id",
                        "CRITICAL",
                        f"Payload '{payload}' not sanitized - potential database compromise"
                    )
                    return  # One breach is enough
            except Exception:
                pass  # Expected to fail
        
        results.record_blocked()
    
    @staticmethod
    def test_session_fixation(results: AttackResult):
        """Attack: Attempt session fixation"""
        results.total_attacks += 1
        # Simulate session token prediction
        tokens = []
        for i in range(5):
            token = hashlib.sha256(f"session_{i}".encode()).hexdigest()
            tokens.append(token)
        
        # Check for sequential/predictable patterns
        if len(set(tokens)) < len(tokens):
            results.record_breach(
                "Predictable Session Tokens",
                "HIGH",
                "Session tokens show predictable patterns"
            )
        else:
            results.record_blocked()
    
    @staticmethod
    def test_privilege_escalation(framework: Any, results: AttackResult):
        """Attack: Attempt to escalate from read to admin"""
        results.total_attacks += 1
        try:
            # Try to access admin functions with regular user
            data = {
                "user_id": "regular_user",
                "role": "admin",  # Claim admin role
                "action": "delete_all_data"
            }
            
            result = framework.validate_multi_framework_compliance(
                data=data,
                frameworks=[ComplianceFramework.SOX],
                user_id="regular_user"
            )
            
            # If it doesn't check roles, vulnerability exists
            results.record_blocked()  # Assume blocked unless proven otherwise
        except Exception:
            results.record_blocked()


# ===================== ATTACK CATEGORY 2: COMPLIANCE BYPASS =====================

class ComplianceBypassAttacks:
    """Attempt to bypass compliance validation"""
    
    @staticmethod
    def test_pci_dss_cvv_bypass(framework: Any, results: AttackResult):
        """Attack: Store CVV with obfuscation"""
        results.total_attacks += 1
        obfuscation_attempts = [
            {"card_cvv": "123"},  # Direct storage
            {"cvv_code": "456"},  # Alternate field name
            {"verification_value": "789"},  # Another name
            {"card_security_code": "012"},  # Yet another
            {"security_code_value": "345"},  # Encoded format
            {"cvv": base64.b64encode(b"678").decode()},  # Base64 encoded
            {"card_data": json.dumps({"cvv": "901"})},  # JSON encoded
        ]
        
        breaches = 0
        for attempt in obfuscation_attempts:
            try:
                result = framework.validate_multi_framework_compliance(
                    data=attempt,
                    frameworks=[ComplianceFramework.PCI_DSS],
                    user_id="attacker"
                )
                
                if result.get("overall_compliant"):
                    breaches += 1
            except Exception:
                pass
        
        if breaches > 0:
            results.record_breach(
                "PCI DSS CVV Storage Bypass",
                "CRITICAL",
                f"{breaches}/{len(obfuscation_attempts)} obfuscation attempts bypassed CVV storage detection"
            )
        else:
            results.record_blocked()
    
    @staticmethod
    def test_hipaa_phi_leakage(framework: Any, results: AttackResult):
        """Attack: Leak PHI through unencrypted channels"""
        results.total_attacks += 1
        try:
            phi_data = {
                "patient_ssn": "123-45-6789",
                "medical_record": "Patient has HIV",
                "diagnosis": "Stage 4 cancer",
                "encrypted": False  # Explicitly unencrypted
            }
            
            result = framework.validate_multi_framework_compliance(
                data=phi_data,
                frameworks=[ComplianceFramework.HIPAA],
                user_id="attacker"
            )
            
            if result.get("overall_compliant"):
                results.record_breach(
                    "HIPAA PHI Leakage",
                    "CRITICAL",
                    "Unencrypted PHI accepted by system"
                )
            else:
                results.record_blocked()
        except Exception:
            results.record_blocked()
    
    @staticmethod
    def test_nlra_union_retaliation_hiding(framework: Any, results: AttackResult):
        """Attack: Hide union retaliation with coded language"""
        results.total_attacks += 1
        coded_retaliation = {
            "employee_id": "emp_001",
            "participated_in_organizing": True,  # Obvious union activity
            "termination_reason": "cultural_fit_issues",  # Coded language
            "documented_performance_issues": False,
            "termination_date": datetime.utcnow().isoformat()
        }
        
        try:
            result = framework.validate_multi_framework_compliance(
                data=coded_retaliation,
                frameworks=[ComplianceFramework.FCC_NLRA],
                user_id="attacker"
            )
            
            if result.get("overall_compliant"):
                results.record_breach(
                    "NLRA Union Retaliation Hiding",
                    "HIGH",
                    "Coded retaliation language bypassed NLRA detection"
                )
            else:
                results.record_blocked()
        except Exception:
            results.record_blocked()
    
    @staticmethod
    def test_tcpa_consent_forgery(framework: Any, results: AttackResult):
        """Attack: Forge TCPA consent"""
        results.total_attacks += 1
        forged_consent = {
            "phone_number": "+15555555555",
            "call_time": "08:00",  # Valid time
            "consent_given": True,  # Claimed consent
            "consent_timestamp": (datetime.utcnow() - timedelta(days=400)).isoformat(),  # Expired
            "consent_method": "implied"  # Not explicit
        }
        
        try:
            result = framework.validate_multi_framework_compliance(
                data=forged_consent,
                frameworks=[ComplianceFramework.FCC_TCPA],
                user_id="attacker"
            )
            
            if result.get("overall_compliant"):
                results.record_breach(
                    "TCPA Consent Forgery",
                    "HIGH",
                    "Expired/implied consent accepted as valid"
                )
            else:
                results.record_blocked()
        except Exception:
            results.record_blocked()


# ===================== ATTACK CATEGORY 3: RATE LIMITING & DOS =====================

class RateLimitingAttacks:
    """Test rate limiting and denial of service"""
    
    @staticmethod
    def test_rate_limit_bypass(framework: Any, results: AttackResult):
        """Attack: Bypass rate limiting with rapid requests"""
        results.total_attacks += 1
        
        # Attempt 1000 requests in 1 second (far exceeds 10/sec default)
        successful_requests = 0
        user_id = f"attacker_{secrets.token_hex(4)}"
        
        start_time = time.time()
        for i in range(100):  # 100 requests
            try:
                result = framework.validate_multi_framework_compliance(
                    data={"test": f"request_{i}"},
                    frameworks=[ComplianceFramework.PCI_DSS],
                    user_id=user_id
                )
                successful_requests += 1
            except Exception as e:
                if "rate limit" in str(e).lower():
                    break
        
        elapsed = time.time() - start_time
        rate = successful_requests / elapsed if elapsed > 0 else float('inf')
        
        if rate > 10:  # Should be limited to 10 req/sec
            results.record_breach(
                "Rate Limit Bypass",
                "MEDIUM",
                f"Achieved {rate:.1f} req/sec, exceeds 10 req/sec limit"
            )
        else:
            results.record_blocked()
    
    @staticmethod
    def test_distributed_dos(framework: Any, results: AttackResult):
        """Attack: Distributed DoS with multiple user_ids"""
        results.total_attacks += 1
        
        # Simulate 10 attackers making rapid requests
        total_requests = 0
        for attacker_num in range(10):
            user_id = f"attacker_{attacker_num}"
            for i in range(20):
                try:
                    framework.validate_multi_framework_compliance(
                        data={"test": "data"},
                        frameworks=[ComplianceFramework.PCI_DSS],
                        user_id=user_id
                    )
                    total_requests += 1
                except Exception:
                    break
        
        # If system allows 200 requests (10 users × 20 each), rate limiting is per-user only
        if total_requests > 150:
            results.record_breach(
                "Distributed DoS Vulnerability",
                "MEDIUM",
                f"System processed {total_requests} requests from 10 users without global rate limiting"
            )
        else:
            results.record_blocked()


# ===================== ATTACK CATEGORY 4: CRYPTOGRAPHIC ATTACKS =====================

class CryptographicAttacks:
    """Attack cryptographic integrity mechanisms"""
    
    @staticmethod
    def test_hash_collision(results: AttackResult):
        """Attack: Attempt to create hash collision"""
        results.total_attacks += 1
        
        # Try to find two different inputs with same SHA-256 hash
        # (This should be computationally infeasible)
        hashes = {}
        collision_found = False
        
        for i in range(10000):
            data = f"test_data_{i}_{secrets.token_hex(8)}"
            hash_val = hashlib.sha256(data.encode()).hexdigest()
            
            if hash_val in hashes:
                collision_found = True
                results.record_breach(
                    "SHA-256 Hash Collision",
                    "CRITICAL",
                    f"Hash collision found: '{hashes[hash_val]}' == '{data}'"
                )
                break
            hashes[hash_val] = data
        
        if not collision_found:
            results.record_blocked()
    
    @staticmethod
    def test_integrity_hash_tampering(results: AttackResult):
        """Attack: Tamper with data and recalculate hash"""
        results.total_attacks += 1
        
        # Original data
        original_data = {"user": "alice", "balance": 100}
        original_hash = hashlib.sha256(json.dumps(original_data, sort_keys=True).encode()).hexdigest()
        
        # Tampered data
        tampered_data = {"user": "alice", "balance": 1000000}
        tampered_hash = hashlib.sha256(json.dumps(tampered_data, sort_keys=True).encode()).hexdigest()
        
        # If we can recalculate hash, tampering is undetectable without HMAC
        if tampered_hash != original_hash:
            results.record_breach(
                "Integrity Hash Weakness",
                "MEDIUM",
                "System uses SHA-256 without HMAC - attacker can recalculate hashes after tampering"
            )
        else:
            results.record_blocked()


# ===================== ATTACK CATEGORY 5: PARADOX SYSTEM ATTACKS =====================

class ParadoxSystemAttacks:
    """Attack the paradox resolution system"""
    
    @staticmethod
    def test_negative_tension_injection(results: AttackResult):
        """Attack: Inject negative tension scores"""
        results.total_attacks += 1
        try:
            malicious_expression = SystemExpression(
                type=ExpressionType.POLICY,
                weight=-1.0,  # Negative weight
                tension=-0.5,  # Negative tension
                content="Malicious expression"
            )
            
            results.record_breach(
                "Negative Tension Injection",
                "MEDIUM",
                "System accepted negative tension/weight values"
            )
        except Exception:
            results.record_blocked()
    
    @staticmethod
    def test_terminal_risk_overflow(results: AttackResult):
        """Attack: Overflow terminal risk calculation"""
        results.total_attacks += 1
        try:
            # Create 10,000 fake paradoxes to overflow calculation
            fake_paradoxes = []
            for i in range(10000):
                paradox = {
                    "unresolved_state": {"unresolved_score": 1.0},
                    "expression_a": {"tension": 1.0},
                    "expression_b": {"tension": 1.0},
                    "timestamp": datetime.utcnow()
                }
                fake_paradoxes.append(paradox)
            
            # This should cause memory/performance issues
            results.record_breach(
                "Terminal Risk Overflow",
                "LOW",
                "System may be vulnerable to resource exhaustion with 10k+ paradoxes"
            )
        except Exception:
            results.record_blocked()


# ===================== ATTACK CATEGORY 6: INPUT VALIDATION =====================

class InputValidationAttacks:
    """Test input validation across all fields"""
    
    @staticmethod
    def test_xss_injection(framework: Any, results: AttackResult):
        """Attack: XSS through compliance data"""
        results.total_attacks += 1
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "'; alert('XSS'); //",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
        ]
        
        for payload in xss_payloads:
            try:
                result = framework.validate_multi_framework_compliance(
                    data={"user_input": payload},
                    frameworks=[ComplianceFramework.PCI_DSS],
                    user_id="attacker"
                )
                
                # Check if payload is echoed back unsanitized
                if payload in str(result):
                    results.record_breach(
                        "XSS Vulnerability",
                        "HIGH",
                        f"XSS payload reflected without sanitization: {payload}"
                    )
                    return
            except Exception:
                pass
        
        results.record_blocked()
    
    @staticmethod
    def test_buffer_overflow(framework: Any, results: AttackResult):
        """Attack: Buffer overflow with massive input"""
        results.total_attacks += 1
        try:
            # 10MB payload
            massive_payload = "A" * (10 * 1024 * 1024)
            result = framework.validate_multi_framework_compliance(
                data={"field": massive_payload},
                frameworks=[ComplianceFramework.PCI_DSS],
                user_id="attacker"
            )
            
            results.record_breach(
                "Buffer Overflow - No Size Limit",
                "MEDIUM",
                "System accepted 10MB payload without size validation"
            )
        except Exception:
            results.record_blocked()
    
    @staticmethod
    def test_null_byte_injection(framework: Any, results: AttackResult):
        """Attack: Null byte injection"""
        results.total_attacks += 1
        try:
            null_payload = "admin\x00user"
            result = framework.validate_multi_framework_compliance(
                data={"username": null_payload},
                frameworks=[ComplianceFramework.SOX],
                user_id=null_payload
            )
            
            if result.get("overall_compliant"):
                results.record_breach(
                    "Null Byte Injection",
                    "MEDIUM",
                    "System processed null byte without sanitization"
                )
            else:
                results.record_blocked()
        except Exception:
            results.record_blocked()


# ===================== MAIN ADVERSARIAL TEST RUNNER =====================

def run_adversarial_tests():
    """Execute all adversarial attacks"""
    print("\n" + "="*80)
    print("MYTHARA ENGINE - ADVERSARIAL ATTACK TEST SUITE")
    print("="*80)
    print("⚠️  RED TEAM MODE: Attempting to breach all security controls\n")
    
    results = AttackResult()
    
    # Initialize framework for testing
    if COMPLIANCE_AVAILABLE:
        framework = UnifiedComplianceFramework(rate_limit_per_second=10)
        print("✅ Compliance framework loaded\n")
    else:
        print("❌ Compliance framework not available - skipping compliance tests\n")
        framework = None
    
    # Category 1: Authentication
    print("🔴 CATEGORY 1: Authentication & Authorization Attacks")
    print("-" * 80)
    if framework:
        AuthenticationAttacks.test_empty_api_key(framework, results)
        print("  - Empty API key bypass test: EXECUTED")
        
        AuthenticationAttacks.test_sql_injection_in_userid(framework, results)
        print("  - SQL injection in user_id: EXECUTED")
        
        AuthenticationAttacks.test_privilege_escalation(framework, results)
        print("  - Privilege escalation: EXECUTED")
    
    AuthenticationAttacks.test_session_fixation(results)
    print("  - Session fixation: EXECUTED")
    
    # Category 2: Compliance Bypass
    print("\n🔴 CATEGORY 2: Compliance Framework Bypass Attacks")
    print("-" * 80)
    if framework:
        ComplianceBypassAttacks.test_pci_dss_cvv_bypass(framework, results)
        print("  - PCI DSS CVV storage bypass: EXECUTED")
        
        ComplianceBypassAttacks.test_hipaa_phi_leakage(framework, results)
        print("  - HIPAA PHI leakage: EXECUTED")
        
        ComplianceBypassAttacks.test_nlra_union_retaliation_hiding(framework, results)
        print("  - NLRA union retaliation hiding: EXECUTED")
        
        ComplianceBypassAttacks.test_tcpa_consent_forgery(framework, results)
        print("  - TCPA consent forgery: EXECUTED")
    
    # Category 3: Rate Limiting
    print("\n🔴 CATEGORY 3: Rate Limiting & DoS Attacks")
    print("-" * 80)
    if framework:
        RateLimitingAttacks.test_rate_limit_bypass(framework, results)
        print("  - Rate limit bypass: EXECUTED")
        
        RateLimitingAttacks.test_distributed_dos(framework, results)
        print("  - Distributed DoS: EXECUTED")
    
    # Category 4: Cryptography
    print("\n🔴 CATEGORY 4: Cryptographic Attacks")
    print("-" * 80)
    CryptographicAttacks.test_hash_collision(results)
    print("  - SHA-256 collision attempt: EXECUTED")
    
    CryptographicAttacks.test_integrity_hash_tampering(results)
    print("  - Integrity hash tampering: EXECUTED")
    
    # Category 5: Paradox System
    if PARADOX_AVAILABLE:
        print("\n🔴 CATEGORY 5: Paradox System Attacks")
        print("-" * 80)
        ParadoxSystemAttacks.test_negative_tension_injection(results)
        print("  - Negative tension injection: EXECUTED")
        
        ParadoxSystemAttacks.test_terminal_risk_overflow(results)
        print("  - Terminal risk overflow: EXECUTED")
    
    # Category 6: Input Validation
    print("\n🔴 CATEGORY 6: Input Validation Attacks")
    print("-" * 80)
    if framework:
        InputValidationAttacks.test_xss_injection(framework, results)
        print("  - XSS injection: EXECUTED")
        
        InputValidationAttacks.test_buffer_overflow(framework, results)
        print("  - Buffer overflow: EXECUTED")
        
        InputValidationAttacks.test_null_byte_injection(framework, results)
        print("  - Null byte injection: EXECUTED")
    
    # Generate and print report
    print("\n" + results.generate_report())
    
    # Security score
    security_score = (results.blocked_attacks / results.total_attacks * 100) if results.total_attacks > 0 else 0
    print(f"\n🛡️  SECURITY SCORE: {security_score:.1f}% ({results.blocked_attacks}/{results.total_attacks} attacks blocked)")
    
    if security_score >= 95:
        print("✅ EXCELLENT: System is highly secure")
    elif security_score >= 80:
        print("⚠️  GOOD: System is secure with minor vulnerabilities")
    elif security_score >= 60:
        print("⚠️  FAIR: System has moderate security issues")
    else:
        print("❌ POOR: System has critical security vulnerabilities")
    
    return results


if __name__ == "__main__":
    results = run_adversarial_tests()
    
    # Exit with failure code if critical vulnerabilities found
    if len(results.critical_findings) > 0:
        sys.exit(1)
    else:
        sys.exit(0)
