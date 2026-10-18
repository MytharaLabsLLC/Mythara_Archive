#!/usr/bin/env python3
"""Tests for Unified Compliance Framework (current API).

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import pytest

from unified_compliance_framework import UnifiedComplianceFramework, ComplianceFramework


@pytest.fixture(scope="module")
def ucf():
    return UnifiedComplianceFramework()


def test_framework_enumeration():
    assert len(list(ComplianceFramework)) == 10


def test_generate_compliance_report(ucf):
    report = ucf.generate_compliance_report()
    assert report["frameworks_supported"] == 10
    assert set(report["compliance_frameworks"]) == {"financial", "privacy", "security"}
    total = sum(len(v) for v in report["compliance_frameworks"].values())
    assert total == 10


def test_validation_requires_authentication(ucf):
    result = ucf.validate_multi_framework_compliance(
        {"card_token": "tok_abc123"}, [ComplianceFramework.PCI_DSS]
    )
    assert result["error"] == "AUTHENTICATION_REQUIRED"


def test_pci_dss_validation(ucf):
    result = ucf.validate_multi_framework_compliance(
        {"card_token": "tok_abc123", "amount": 100.00, "encrypted": True},
        [ComplianceFramework.PCI_DSS],
        user_id="pci_tester",
    )
    assert result["status"] == "COMPLIANT"
    assert result["frameworks"]["PCI_DSS"]["compliant"] is True
    assert "signature" in result


def test_multi_framework_validation(ucf):
    result = ucf.validate_multi_framework_compliance(
        {"field": "value"},
        [ComplianceFramework.GDPR, ComplianceFramework.SOC2],
        user_id="multi_tester",
    )
    assert result["status"] == "COMPLIANT"
    assert set(result["frameworks"]) == {"GDPR", "SOC2"}


def test_audit_logs_recorded(ucf):
    logs = ucf.get_audit_logs(user_id="pci_tester")
    assert len(logs) > 0
    assert all(entry["user_id"] == "pci_tester" for entry in logs)
