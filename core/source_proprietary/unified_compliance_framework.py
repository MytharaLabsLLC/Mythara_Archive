# Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""Unified Compliance Framework — public import surface.

The canonical implementations live in ``universal_governance_lattice.py``.
The rest of the system (main.py, security_audit_compliance.py,
test_compliance.py, amir_bot.py, the adversarial test suites) was written
against this module name, which was missing from the tree — every import
of it failed, and security_audit_compliance.py exited at import time.

This module restores the expected surface by re-exporting the lattice's
compliance classes, so there is exactly one implementation, in the lattice.
"""

import hashlib  # noqa: F401  (imported from here by tests/big_meanie.py)
import hmac  # noqa: F401  (imported from here by tests/big_meanie.py)

from universal_governance_lattice import (  # noqa: F401
    SECRET_KEY,
    CivilRightsAccessibilityCompliance,
    ComplianceFramework,
    FinancialServicesCompliance,
    HealthcareCompliance,
    LaborEmploymentCompliance,
    TelecommunicationsCompliance,
    UnifiedComplianceFramework,
    create_unified_compliance_framework,
    validate_jwt_algorithm,
)

__all__ = [
    "SECRET_KEY",
    "CivilRightsAccessibilityCompliance",
    "ComplianceFramework",
    "FinancialServicesCompliance",
    "HealthcareCompliance",
    "LaborEmploymentCompliance",
    "TelecommunicationsCompliance",
    "UnifiedComplianceFramework",
    "create_unified_compliance_framework",
    "validate_jwt_algorithm",
]
