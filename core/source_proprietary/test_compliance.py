#!/usr/bin/env python3
"""Tests for Unified Compliance Framework (lattice API).

Copyright © 2026 Mythara Labs LLC. All rights reserved.

History: this suite was written against an earlier 10-framework API
(status/frameworks/signature result shape). The implementation that
actually ships — UnifiedComplianceFramework in
universal_governance_lattice.py, re-exported by
unified_compliance_framework.py — covers 45 frameworks and returns
overall_compliant/framework_results/integrity_hash. main.py and
security_audit_compliance.py both consume the lattice shape, so these
tests were rewritten against it (2026-10-19), preserving each original
test's intent.
"""

import pytest

from unified_compliance_framework import UnifiedComplianceFramework, ComplianceFramework


@pytest.fixture(scope="module")
def ucf():
    return UnifiedComplianceFramework()


def test_framework_enumeration():
    assert len(list(ComplianceFramework)) == 45


def test_generate_compliance_report(ucf):
    report = ucf.generate_compliance_report()
    assert report["frameworks_supported"] == len(list(ComplianceFramework))
    assert set(report["compliance_frameworks"]) == {
        "financial",
        "healthcare",
        "telecommunications",
        "federal",
        "privacy",
        "industry",
        "labor",
        "civil_rights",
        "other",
    }
    total = sum(len(v) for v in report["compliance_frameworks"].values())
    assert total == 43  # named standards across the 9 families
    assert report["compliance_status"] == "OPERATIONAL"


def test_validation_requires_authentication(ucf):
    result = ucf.validate_multi_framework_compliance(
        {"card_token": "tok_abc123"}, [ComplianceFramework.PCI_DSS]
    )
    assert result["error"] == "AUTHENTICATION_REQUIRED"
    assert result["message"]  # main.py surfaces this as the HTTP detail


def test_pci_dss_validation(ucf):
    result = ucf.validate_multi_framework_compliance(
        {
            "card_token": "tok_abc123",
            "amount": 100.00,
            "encrypted": True,
            "transaction_id": "TXN_TEST_001",
        },
        [ComplianceFramework.PCI_DSS],
        user_id="pci_tester",
    )
    assert result["overall_compliant"] is True
    assert result["framework_results"]["pci_dss"]["compliant"] is True
    assert result["integrity_hash"]


def test_multi_framework_validation(ucf):
    result = ucf.validate_multi_framework_compliance(
        {
            # GDPR evidence
            "lawful_basis": "consent",
            "privacy_notice_provided": True,
            "data_subject_rights_process": True,
            # SOC 2 evidence
            "access_controls_documented": True,
            "change_management_process": True,
            "system_monitoring_enabled": True,
            "incident_response_plan": True,
        },
        [ComplianceFramework.GDPR, ComplianceFramework.SOC_2],
        user_id="multi_tester",
    )
    assert result["overall_compliant"] is True
    assert set(result["framework_results"]) == {"gdpr", "soc_2"}


def test_unimplemented_frameworks_no_longer_pass():
    # Regression (2026-10-19): 32 frameworks used to return COMPLIANT by
    # default with no validator behind them. Invariants now:
    #  - no framework reports a missing validator;
    #  - evidence-presence validators (41 of 45) fail closed on empty data;
    #  - the 4 scan-based validators (NLRA, UNION_COMPLIANCE,
    #    ACLU_STANDARDS, SECTION_508) pass on empty data BY DESIGN — they
    #    scan for prohibited conduct — and each must catch a planted
    #    violation (test_scan_validators_detect_violations).
    # Own instance with the rate limiter lifted: the production default
    # (10/sec/user) would throttle this 45-call sweep.
    ucf = UnifiedComplianceFramework(rate_limit_per_second=100000)
    scan_based = {"nlra", "union_compliance", "aclu_standards", "section_508"}
    for framework in ComplianceFramework:
        result = ucf.validate_multi_framework_compliance(
            {}, [framework], user_id="coverage_tester"
        )
        violations = result["framework_results"][framework.value]["violations"]
        assert not any("no validator implemented" in v for v in violations), framework
        if framework.value not in scan_based:
            assert result["overall_compliant"] is False, framework
            assert violations, framework


def test_scan_validators_detect_violations():
    # The four scan-based validators pass on empty data; each must fire
    # when the conduct it guards against is present.
    ucf = UnifiedComplianceFramework(rate_limit_per_second=100000)
    planted = {
        ComplianceFramework.NLRA: {"union_activity": True, "disciplinary_action": True},
        ComplianceFramework.UNION_COMPLIANCE: {"termination_action": True},
        ComplianceFramework.ACLU_STANDARDS: {"surveillance_without_warrant": True},
        ComplianceFramework.SECTION_508: {"has_images": True},
    }
    for framework, data in planted.items():
        result = ucf.validate_multi_framework_compliance(
            data, [framework], user_id="scan_tester"
        )
        assert result["overall_compliant"] is False, framework
        assert result["framework_results"][framework.value]["violations"], framework


def test_audit_logs_recorded(ucf):
    logs = ucf.get_audit_logs(user_id="pci_tester")
    assert len(logs) > 0
    assert all(entry["user_id"] == "pci_tester" for entry in logs)
