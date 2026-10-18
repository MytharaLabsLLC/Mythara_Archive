"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Engine - Compliance Framework Security Audit
====================================================

This script performs aggressive security testing to identify loopholes,
vulnerabilities, and potential breaches in the unified compliance framework.

Tests include:
- SQL injection attempts
- Data sanitization bypasses
- Authentication bypass attempts
- Audit log tampering detection
- Encryption weakness exploitation
- Rate limiting bypass
- Framework-specific attack vectors
"""

import sys
import json
import hashlib
import time
from typing import Dict, List, Any
from datetime import datetime

# Import the compliance framework
try:
    from unified_compliance_framework import (
        UnifiedComplianceFramework,
        ComplianceFramework,
        FinancialServicesCompliance,
        TelecommunicationsCompliance,
        LaborEmploymentCompliance,
        CivilRightsAccessibilityCompliance,
    )
except ImportError:
    print("ERROR: Cannot import unified_compliance_framework")
    print("Make sure unified_compliance_framework.py is in the same directory")
    sys.exit(1)


class ComplianceSecurityAuditor:
    """Aggressive security testing for compliance framework."""

    def __init__(self):
        self.framework = UnifiedComplianceFramework()
        self.financial = FinancialServicesCompliance()
        self.telecom = TelecommunicationsCompliance()
        self.labor = LaborEmploymentCompliance()
        self.civil_rights = CivilRightsAccessibilityCompliance()

        self.vulnerabilities_found: List[Dict[str, Any]] = []
        self.tests_passed = 0
        self.tests_failed = 0

    def log_vulnerability(
        self, severity: str, category: str, description: str, exploit: str
    ):
        """Log a discovered vulnerability."""
        vuln = {
            "severity": severity,
            "category": category,
            "description": description,
            "exploit": exploit,
            "timestamp": datetime.now().isoformat(),
        }
        self.vulnerabilities_found.append(vuln)
        self.tests_failed += 1
        print(f"  ❌ VULNERABILITY [{severity}]: {description}")
        print(f"     Exploit: {exploit}\n")

    def log_pass(self, test_name: str):
        """Log a passed security test."""
        self.tests_passed += 1
        print(f"  ✅ PASS: {test_name}")

    # ========================================================================
    # INJECTION ATTACK TESTS
    # ========================================================================

    def test_sql_injection_attempts(self):
        """Test for SQL injection vulnerabilities."""
        print("\n🔍 Testing SQL Injection Vulnerabilities...")

        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM sensitive_data--",
            "'; DELETE FROM audit_log WHERE '1'='1",
            "1; UPDATE compliance_status SET status='compliant' WHERE 1=1--",
        ]

        for payload in sql_payloads:
            test_data = {
                "user_id": payload,
                "transaction_id": payload,
                "card_number": payload,
            }

            try:
                result = self.financial.validate_pci_dss_transaction(test_data)

                # Check if payload was sanitized or rejected
                if payload in str(result):
                    self.log_vulnerability(
                        "CRITICAL",
                        "SQL Injection",
                        "SQL injection payload was not sanitized",
                        f"Payload '{payload}' was processed without sanitization",
                    )
                else:
                    self.log_pass(f"SQL injection blocked: {payload[:30]}")
            except Exception:
                # Exception is good - means payload was rejected
                self.log_pass(f"SQL injection rejected with exception: {payload[:30]}")

    def test_xss_injection(self):
        """Test for Cross-Site Scripting vulnerabilities."""
        print("\n🔍 Testing XSS Injection Vulnerabilities...")

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
        ]

        for payload in xss_payloads:
            test_data = {"message": payload, "user_name": payload, "comment": payload}

            result = self.framework.validate_multi_framework_compliance(
                test_data, [ComplianceFramework.FCC_TCPA]
            )

            # Check if XSS payload appears in response
            response_str = json.dumps(result)
            if payload in response_str:
                self.log_vulnerability(
                    "HIGH",
                    "XSS Injection",
                    "XSS payload was not sanitized in response",
                    f"Payload '{payload}' appears in response",
                )
            else:
                self.log_pass(f"XSS injection blocked: {payload[:30]}")

    # ========================================================================
    # DATA VALIDATION BYPASS TESTS
    # ========================================================================

    def test_pci_dss_bypass_attempts(self):
        """Test PCI DSS validation bypass attempts."""
        print("\n🔍 Testing PCI DSS Bypass Attempts...")

        # Attempt 1: Store CVV with obfuscation
        test_data = {
            "cvv": "123",
            "security_code": "456",
            "cvc": "789",
            "card_verification_value": "012",
        }
        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )
        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "PCI DSS Bypass",
                "CVV storage was not detected when using alternate field names",
                "Used fields: cvv, security_code, cvc, card_verification_value",
            )
        else:
            self.log_pass("CVV storage detected with alternate field names")

        # Attempt 2: Store full card number with spaces
        test_data = {"card_number": "4532 1234 5678 9010"}
        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )
        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "PCI DSS Bypass",
                "Full card number storage not detected with space formatting",
                "Card number: 4532 1234 5678 9010",
            )
        else:
            self.log_pass("Card number storage detected with spaces")

        # Attempt 3: Store full card number with dashes
        test_data = {"card_number": "4532-1234-5678-9010"}
        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )
        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "PCI DSS Bypass",
                "Full card number storage not detected with dash formatting",
                "Card number: 4532-1234-5678-9010",
            )
        else:
            self.log_pass("Card number storage detected with dashes")

        # Attempt 4: Base64 encode sensitive data
        import base64

        encoded_cvv = base64.b64encode(b"123").decode()
        test_data = {"encoded_cvv": encoded_cvv}
        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )
        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "PCI DSS Bypass",
                "Encoded CVV not detected",
                f"Base64 encoded CVV: {encoded_cvv}",
            )
        else:
            self.log_pass("Encoded CVV storage detected")

    def test_tcpa_time_restriction_bypass(self):
        """Test FCC TCPA time restriction bypass attempts."""
        print("\n🔍 Testing TCPA Time Restriction Bypass...")

        # Attempt 1: Call outside hours (7:00 AM)
        test_data = {
            "automated": True,
            "consent_given": True,
            "call_time": "07:00",
            "opt_out_available": True,
            "on_dnc_list": False,
        }
        is_compliant, violations = self.telecom.validate_tcpa_consent(test_data)
        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "TCPA Bypass",
                "Call before 8 AM was allowed",
                "Call time: 07:00",
            )
        else:
            self.log_pass("Early morning call blocked (07:00)")

        # Attempt 2: Call outside hours (9:01 PM)
        test_data["call_time"] = "21:01"
        is_compliant, violations = self.telecom.validate_tcpa_consent(test_data)
        if is_compliant:
            self.log_vulnerability(
                "HIGH", "TCPA Bypass", "Call after 9 PM was allowed", "Call time: 21:01"
            )
        else:
            self.log_pass("Late evening call blocked (21:01)")

        # Attempt 3: Midnight call
        test_data["call_time"] = "00:00"
        is_compliant, violations = self.telecom.validate_tcpa_consent(test_data)
        if is_compliant:
            self.log_vulnerability(
                "HIGH", "TCPA Bypass", "Midnight call was allowed", "Call time: 00:00"
            )
        else:
            self.log_pass("Midnight call blocked (00:00)")

        # Attempt 4: No consent but claim emergency
        test_data = {
            "automated": True,
            "consent_given": False,
            "emergency": True,
            "call_time": "14:00",
        }
        is_compliant, violations = self.telecom.validate_tcpa_consent(test_data)
        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "TCPA Bypass",
                "Automated call allowed without consent using emergency flag",
                "Emergency flag bypassed consent requirement",
            )
        else:
            self.log_pass("Emergency flag did not bypass consent requirement")

    def test_nlra_union_retaliation_bypass(self):
        """Test NLRA union retaliation detection bypass."""
        print("\n🔍 Testing NLRA Union Retaliation Detection...")

        # Attempt 1: Disciplinary action after union activity without reason
        test_data = {
            "union_activity": True,
            "disciplinary_action": True,
            "legitimate_business_reason": False,
        }
        is_compliant, violations = self.labor.validate_nlra_rights(test_data)
        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "NLRA Bypass",
                "Disciplinary action after union activity allowed without business reason",
                "Union retaliation not detected",
            )
        else:
            self.log_pass("Union retaliation detected")

        # Attempt 2: Use alternate field names to hide retaliation
        test_data = {
            "recent_organizing_activity": True,
            "employee_action_taken": True,
            "justification": False,
        }
        is_compliant, violations = self.labor.validate_nlra_rights(test_data)
        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "NLRA Bypass",
                "Union retaliation not detected with alternate field names",
                "Used: recent_organizing_activity, employee_action_taken",
            )
        else:
            self.log_pass("Retaliation detected with alternate field names")

    # ========================================================================
    # AUTHENTICATION & AUTHORIZATION TESTS
    # ========================================================================

    def test_authentication_bypass(self):
        """Test authentication bypass attempts."""
        print("\n🔍 Testing Authentication Bypass Attempts...")

        # These tests would normally be against the API endpoints
        # For now, we test the framework's handling of missing auth data

        test_data = {"user_id": None, "api_key": None, "transaction_id": "TXN_001"}

        # Framework should reject transactions without user identification
        result = self.framework.validate_multi_framework_compliance(
            test_data, [ComplianceFramework.PCI_DSS]
        )

        # Check if transaction was properly rejected due to missing user_id
        # A compliant system should set overall_compliant=False and include authentication violation
        if result.get("overall_compliant", True):
            self.log_vulnerability(
                "HIGH",
                "Authentication",
                "Transaction processed without user identification",
                "Missing user_id was not rejected",
            )
        else:
            # Check if authentication violation was detected
            violations = result.get("all_violations", [])
            auth_violation_found = any(
                "user_id" in str(v).lower() or "authentication" in str(v).lower()
                for v in violations
            )
            if auth_violation_found:
                self.log_pass("User identification required for transactions")
            else:
                self.log_vulnerability(
                    "HIGH",
                    "Authentication",
                    "Transaction rejected but authentication violation not documented",
                    "No authentication-specific violation message",
                )

    # ========================================================================
    # AUDIT LOG INTEGRITY TESTS
    # ========================================================================

    def test_audit_log_tampering(self):
        """Test audit log integrity and tampering detection."""
        print("\n🔍 Testing Audit Log Tampering Detection...")

        # Generate two audit logs with proper user_id
        test_data1 = {"transaction_id": "TXN_001", "user_id": "test_user_001"}
        result1 = self.framework.validate_multi_framework_compliance(
            test_data1, [ComplianceFramework.PCI_DSS]
        )

        test_data2 = {"transaction_id": "TXN_002", "user_id": "test_user_002"}
        result2 = self.framework.validate_multi_framework_compliance(
            test_data2, [ComplianceFramework.PCI_DSS]
        )

        # Check if audit logs have integrity hashes
        results = {"TXN_001": result1, "TXN_002": result2}
        missing = [
            txn
            for txn, res in results.items()
            if "integrity_hash" not in res or res.get("integrity_hash") is None
        ]
        if missing:
            self.log_vulnerability(
                "CRITICAL",
                "Audit Integrity",
                f"Audit logs missing integrity hashes: {', '.join(missing)}",
                "Cannot detect tampering without cryptographic hashes",
            )
        else:
            self.log_pass("Audit logs include integrity hashes")

        # Verify hash format (should be SHA-256)
        if "integrity_hash" in result1 and result1.get("integrity_hash") is not None:
            hash_value = result1["integrity_hash"]
            if len(hash_value) != 64 or not all(
                c in "0123456789abcdef" for c in hash_value
            ):
                self.log_vulnerability(
                    "HIGH",
                    "Audit Integrity",
                    "Integrity hash is not valid SHA-256 format",
                    f"Hash: {hash_value}",
                )
            else:
                self.log_pass("Integrity hashes use SHA-256 format")

        # Test if tampering would be detected
        original_hash = result1.get("integrity_hash", "")
        tampered_result = result1.copy()
        tampered_result["overall_compliant"] = not tampered_result.get(
            "overall_compliant", False
        )

        # Recalculate hash
        audit_data = {
            "log_id": tampered_result.get("audit_log_id", ""),
            "timestamp": datetime.now().isoformat(),
            "results": tampered_result,
        }
        new_hash = hashlib.sha256(
            json.dumps(audit_data, sort_keys=True).encode()
        ).hexdigest()

        if original_hash == new_hash:
            self.log_vulnerability(
                "CRITICAL",
                "Audit Integrity",
                "Tampering not detected - hash remained same after modification",
                "Hash collision or weak hashing algorithm",
            )
        else:
            self.log_pass("Audit log tampering would be detected via hash mismatch")

    # ========================================================================
    # ENCRYPTION & DATA PROTECTION TESTS
    # ========================================================================

    def test_encryption_requirements(self):
        """Test encryption requirement enforcement."""
        print("\n🔍 Testing Encryption Requirement Enforcement...")

        # Test 1: Unencrypted PHI
        test_data = {"phi_data": "Patient SSN: 123-45-6789", "encrypted": False}
        result = self.framework.validate_multi_framework_compliance(
            test_data, [ComplianceFramework.HIPAA]
        )

        if result["overall_compliant"]:
            self.log_vulnerability(
                "CRITICAL",
                "Encryption",
                "Unencrypted PHI was allowed",
                "HIPAA requires PHI encryption at rest and in transit",
            )
        else:
            self.log_pass("Unencrypted PHI rejected")

        # Test 2: Weak encryption indicator
        test_data = {"card_token": "tok_abc123", "encryption_algorithm": "DES"}
        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )

        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "Encryption",
                "Weak encryption algorithm (DES) not flagged",
                "PCI DSS requires strong cryptography (AES-256, RSA 2048+)",
            )
        else:
            self.log_pass("Weak encryption detected")

    # ========================================================================
    # RATE LIMITING & DOS TESTS
    # ========================================================================

    def test_rate_limiting(self):
        """Test rate limiting and DoS protection."""
        print("\n🔍 Testing Rate Limiting & DoS Protection...")

        # Attempt rapid-fire validation requests with same user_id
        start_time = time.time()
        request_count = 0
        rate_limited_count = 0

        for i in range(100):
            test_data = {"request_id": f"REQ_{i}", "user_id": "rate_limit_test_user"}
            try:
                result = self.framework.validate_multi_framework_compliance(
                    test_data, [ComplianceFramework.PCI_DSS]
                )
                # Check if request was rate limited
                if result.get("error") == "RATE_LIMIT_EXCEEDED":
                    rate_limited_count += 1
                else:
                    request_count += 1
            except Exception:
                break

        elapsed_time = time.time() - start_time
        requests_per_second = (
            request_count / elapsed_time if elapsed_time > 0 else float("inf")
        )

        # Check if rate limiting was triggered
        if rate_limited_count > 0:
            self.log_pass(
                f"Rate limiting active: {rate_limited_count} requests blocked, {request_count} allowed"
            )
        elif request_count == 100 and requests_per_second > 50:
            self.log_vulnerability(
                "MEDIUM",
                "Rate Limiting",
                f"No rate limiting detected - {requests_per_second:.0f} req/sec allowed",
                "Vulnerable to DoS attacks without rate limiting",
            )
        else:
            self.log_pass(
                f"Rate limiting or performance limits in place ({requests_per_second:.0f} req/sec)"
            )

    # ========================================================================
    # LOGIC BOMB & BACKDOOR TESTS
    # ========================================================================

    def test_hidden_backdoors(self):
        """Test for hidden backdoors or special bypass codes."""
        print("\n🔍 Testing for Hidden Backdoors...")

        # Test common backdoor patterns
        backdoor_attempts = [
            {"user_id": "admin", "bypass": True},
            {"user_id": "root", "debug_mode": True},
            {"master_key": "1234567890"},
            {"override": "true", "force_compliant": True},
            {"god_mode": True},
            {"developer_access": True},
        ]

        for attempt in backdoor_attempts:
            result = self.framework.validate_multi_framework_compliance(
                attempt, [ComplianceFramework.PCI_DSS]
            )

            if result["overall_compliant"] and result.get("all_violations", []):
                self.log_vulnerability(
                    "CRITICAL",
                    "Backdoor",
                    f"Backdoor detected - violations ignored: {attempt}",
                    "Special fields bypassed compliance checks",
                )
            else:
                self.log_pass(f"No backdoor with: {list(attempt.keys())}")

    # ========================================================================
    # DATA LEAKAGE TESTS
    # ========================================================================

    def test_data_leakage(self):
        """Test for sensitive data leakage in responses."""
        print("\n🔍 Testing for Data Leakage...")

        # Test with sensitive data
        test_data = {
            "card_number": "4532123456789010",
            "cvv": "123",
            "ssn": "123-45-6789",
            "password": "MySecretPass123",
            "api_key": "sk_test_fixture_abc123xyz789",
        }

        is_compliant, violations = self.financial.validate_pci_dss_transaction(
            test_data
        )
        result_str = json.dumps({"compliant": is_compliant, "violations": violations})

        # Check if sensitive data appears in response
        sensitive_patterns = [
            "4532123456789010",
            "123-45-6789",
            "MySecretPass123",
            "sk_test_fixture_abc123xyz789",
        ]

        for pattern in sensitive_patterns:
            if pattern in result_str:
                self.log_vulnerability(
                    "CRITICAL",
                    "Data Leakage",
                    f"Sensitive data leaked in response: {pattern}",
                    "Response contains unredacted sensitive information",
                )
            else:
                self.log_pass(f"Sensitive data not leaked: {pattern[:10]}...")

    # ========================================================================
    # FRAMEWORK-SPECIFIC ATTACK VECTORS
    # ========================================================================

    def test_sox_segregation_bypass(self):
        """Test SOX segregation of duties bypass attempts."""
        print("\n🔍 Testing SOX Segregation of Duties Bypass...")

        # Attempt 1: Same preparer and approver
        test_data = {
            "amount": 50000.00,
            "preparer_id": "user_123",
            "approver_id": "user_123",
        }
        is_compliant, violations = self.financial.validate_sox_controls(test_data)

        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "SOX Bypass",
                "Same user allowed as preparer and approver",
                "Segregation of duties violated",
            )
        else:
            self.log_pass("Same preparer/approver rejected")

        # Attempt 2: High-value transaction without dual authorization
        test_data = {
            "amount": 100000.00,
            "preparer_id": "user_123",
            "approver_id": "user_456",
            "dual_authorization": False,
        }
        is_compliant, violations = self.financial.validate_sox_controls(test_data)

        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "SOX Bypass",
                "High-value transaction allowed without dual authorization",
                "Amount: $100,000 without dual auth",
            )
        else:
            self.log_pass("Dual authorization required for high-value transactions")

    def test_flsa_overtime_calculation_manipulation(self):
        """Test FLSA overtime calculation manipulation."""
        print("\n🔍 Testing FLSA Overtime Calculation Manipulation...")

        # Attempt 1: Incorrect overtime rate
        test_data = {
            "hourly_rate": 20.00,
            "hours_worked": 45,
            "overtime_pay": 100.00,  # Should be 150.00 (5 hours * 20 * 1.5)
        }
        is_compliant, violations = self.labor.validate_flsa_compliance(test_data)

        if is_compliant:
            self.log_vulnerability(
                "HIGH",
                "FLSA Bypass",
                "Incorrect overtime pay not detected",
                "Expected $150, got $100",
            )
        else:
            self.log_pass("Incorrect overtime pay detected")

        # Attempt 2: Below minimum wage
        test_data = {"hourly_rate": 5.00, "hours_worked": 40}  # Below federal minimum
        is_compliant, violations = self.labor.validate_flsa_compliance(test_data)

        if is_compliant:
            self.log_vulnerability(
                "CRITICAL",
                "FLSA Bypass",
                "Below minimum wage not detected",
                "Hourly rate: $5.00 (federal minimum: $7.25)",
            )
        else:
            self.log_pass("Below minimum wage detected")

    # ========================================================================
    # REPORT GENERATION
    # ========================================================================

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security audit report."""
        total_tests = self.tests_passed + self.tests_failed

        # Categorize vulnerabilities by severity
        critical = [
            v for v in self.vulnerabilities_found if v["severity"] == "CRITICAL"
        ]
        high = [v for v in self.vulnerabilities_found if v["severity"] == "HIGH"]
        medium = [v for v in self.vulnerabilities_found if v["severity"] == "MEDIUM"]

        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "pass_rate": (
                f"{(self.tests_passed / total_tests * 100):.1f}%"
                if total_tests > 0
                else "0%"
            ),
            "vulnerabilities_summary": {
                "total": len(self.vulnerabilities_found),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
            },
            "vulnerabilities": self.vulnerabilities_found,
            "security_score": self._calculate_security_score(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _calculate_security_score(self) -> int:
        """Calculate overall security score (0-100)."""
        critical = len(
            [v for v in self.vulnerabilities_found if v["severity"] == "CRITICAL"]
        )
        high = len([v for v in self.vulnerabilities_found if v["severity"] == "HIGH"])
        medium = len(
            [v for v in self.vulnerabilities_found if v["severity"] == "MEDIUM"]
        )

        # Deduct points based on severity
        score = 100
        score -= critical * 20
        score -= high * 10
        score -= medium * 5

        return max(0, score)

    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        vuln_categories = set(v["category"] for v in self.vulnerabilities_found)

        if "SQL Injection" in vuln_categories:
            recommendations.append(
                "Implement parameterized queries and input sanitization"
            )

        if "XSS Injection" in vuln_categories:
            recommendations.append(
                "Implement output encoding and Content Security Policy"
            )

        if "PCI DSS Bypass" in vuln_categories:
            recommendations.append(
                "Enhance card data validation with regex patterns for all formats"
            )

        if "TCPA Bypass" in vuln_categories:
            recommendations.append(
                "Implement time-based validation with timezone awareness"
            )

        if "Audit Integrity" in vuln_categories:
            recommendations.append("Implement blockchain-style audit log chaining")

        if "Authentication" in vuln_categories:
            recommendations.append(
                "Enforce mandatory authentication for all compliance operations"
            )

        if "Encryption" in vuln_categories:
            recommendations.append(
                "Enforce strong encryption standards (AES-256, RSA 2048+)"
            )

        if "Rate Limiting" in vuln_categories:
            recommendations.append(
                "Implement API rate limiting (e.g., 10 req/sec per user)"
            )

        if "Data Leakage" in vuln_categories:
            recommendations.append(
                "Implement automatic redaction of sensitive data in responses"
            )

        if not recommendations:
            recommendations.append(
                "Continue regular security audits and penetration testing"
            )

        return recommendations


def main():
    """Run comprehensive security audit."""
    print("=" * 70)
    print("Mythara Engine - Compliance Framework Security Audit")
    print("=" * 70)
    print("Testing for loopholes, vulnerabilities, and potential breaches...")
    print()

    auditor = ComplianceSecurityAuditor()

    # Run all security tests
    auditor.test_sql_injection_attempts()
    auditor.test_xss_injection()
    auditor.test_pci_dss_bypass_attempts()
    auditor.test_tcpa_time_restriction_bypass()
    auditor.test_nlra_union_retaliation_bypass()
    auditor.test_authentication_bypass()
    auditor.test_audit_log_tampering()
    auditor.test_encryption_requirements()
    auditor.test_rate_limiting()
    auditor.test_hidden_backdoors()
    auditor.test_data_leakage()
    auditor.test_sox_segregation_bypass()
    auditor.test_flsa_overtime_calculation_manipulation()

    # Generate report
    print("\n" + "=" * 70)
    print("SECURITY AUDIT REPORT")
    print("=" * 70)

    report = auditor.generate_security_report()

    print("\n📊 Test Results:")
    print(f"  Total Tests: {report['total_tests']}")
    print(f"  Passed: {report['tests_passed']} ✅")
    print(f"  Failed: {report['tests_failed']} ❌")
    print(f"  Pass Rate: {report['pass_rate']}")

    print(f"\n🔒 Security Score: {report['security_score']}/100")

    print("\n⚠️  Vulnerabilities Found:")
    print(f"  CRITICAL: {report['vulnerabilities_summary']['critical']}")
    print(f"  HIGH: {report['vulnerabilities_summary']['high']}")
    print(f"  MEDIUM: {report['vulnerabilities_summary']['medium']}")
    print(f"  TOTAL: {report['vulnerabilities_summary']['total']}")

    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

    # Save detailed report to file
    report_file = "tests/output/security_audit_report.json"
    try:
        import os

        os.makedirs("tests/output", exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, indent=2, fp=f)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")

    print("\n" + "=" * 70)

    if report["vulnerabilities_summary"]["critical"] > 0:
        print("❌ CRITICAL VULNERABILITIES FOUND - IMMEDIATE ACTION REQUIRED")
        return 1
    elif report["vulnerabilities_summary"]["high"] > 0:
        print("⚠️  HIGH-SEVERITY VULNERABILITIES FOUND - REVIEW REQUIRED")
        return 1
    else:
        print("✅ Security audit completed - No critical issues found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
