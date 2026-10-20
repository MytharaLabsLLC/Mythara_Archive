#!/usr/bin/env python3
"""
Unified Compliance Framework for Mythara Engine
Implements multi-industry regulatory compliance standards

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Supported Compliance Frameworks:
- Financial: PCI DSS, FINRA, SOX, GLBA, Dodd-Frank, BSA/AML
- Healthcare: HIPAA, HITECH, 21 CFR Part 11 (FDA)
- Telecommunications: FCC TCPA, CPNI, CALEA, CAN-SPAM
- Federal: FISMA, NIST SP 800-53, FTC, OMB M-25-04, GDPR, CCPA
- Industry: SOC 2, ISO 27001, OWASP, COBIT, ITIL
- Labor: NLRA, FLSA, OSHA, EEOC, Union Compliance
- Civil Rights: ACLU Standards, ADA, Section 508
"""

import hashlib
import hmac
import json
import secrets
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Security constants
SECRET_KEY = secrets.token_bytes(32)  # 256-bit key for HMAC
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


# ============================================================================
# SECURITY UTILITIES
# ============================================================================


def sanitize_input(value: Any) -> str:
    """Sanitize input to prevent SQL injection and other attacks"""
    if value is None:
        return ""

    # Convert to string
    str_value = str(value)

    # Remove dangerous SQL characters and patterns
    dangerous_patterns = [
        r"('|(\-\-)|(;)|(\|\|)|(\*))",  # SQL special chars
        r"(\bOR\b|\bAND\b).*=.*",  # SQL logic
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",  # SQL keywords
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # XSS
        r"on\w+\s*=",  # Event handlers
    ]

    for pattern in dangerous_patterns:
        str_value = re.sub(pattern, "", str_value, flags=re.IGNORECASE)

    # Remove null bytes
    str_value = str_value.replace("\x00", "")

    # Limit length to prevent buffer overflow
    max_length = 1000000  # 1MB limit
    if len(str_value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} bytes")

    return str_value


def validate_jwt_algorithm(token: str) -> bool:
    """Validate JWT token doesn't use 'none' algorithm"""
    try:
        # Extract header (first part before first dot)
        header_b64 = token.split(".")[0]
        # Decode base64 (add padding if needed)
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += "=" * padding

        import base64

        header_json = base64.b64decode(header_b64).decode("utf-8")
        header = json.loads(header_json)

        # Reject 'none' algorithm
        if header.get("alg", "").lower() == "none":
            logger.warning("JWT with 'none' algorithm rejected")
            return False

        return True
    except Exception as e:
        logger.warning(f"JWT validation failed: {e}")
        return False


# ============================================================================
# COMPLIANCE FRAMEWORK ENUMS
# ============================================================================


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    # Financial Services
    PCI_DSS = "pci_dss"  # Payment Card Industry
    FINRA = "finra"  # Financial Industry Regulatory Authority
    SOX = "sox"  # Sarbanes-Oxley Act
    GLBA = "glba"  # Gramm-Leach-Bliley Act
    DODD_FRANK = "dodd_frank"  # Dodd-Frank Wall Street Reform
    BSA_AML = "bsa_aml"  # Bank Secrecy Act / Anti-Money Laundering
    SEC_REG = "sec_reg"  # Securities and Exchange Commission

    # Healthcare
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    HITECH = "hitech"  # Health Information Technology for Economic and Clinical Health
    FDA_21_CFR_11 = "fda_21_cfr_11"  # FDA Electronic Records

    # Telecommunications
    FCC_TCPA = "fcc_tcpa"  # Telephone Consumer Protection Act
    FCC_CPNI = "fcc_cpni"  # Customer Proprietary Network Information
    CAN_SPAM = "can_spam"  # Email Marketing
    CALEA = "calea"  # Communications Assistance for Law Enforcement

    # Federal Regulations
    FISMA = "fisma"  # Federal Information Security Management Act
    NIST_800_53 = "nist_800_53"  # NIST Security Controls
    FTC_ACT = "ftc_act"  # Federal Trade Commission Act
    OMB_M_25_04 = "omb_m_25_04"  # Zero Trust Architecture
    FERC = "ferc"  # Federal Energy Regulatory Commission

    # Privacy
    GDPR = "gdpr"  # EU General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    PIPEDA = "pipeda"  # Canadian Personal Information Protection
    LGPD = "lgpd"  # Brazilian General Data Protection Law
    APPI = "appi"  # Japanese Act on Protection of Personal Information

    # Industry Standards
    SOC_2 = "soc_2"  # Service Organization Control 2
    ISO_27001 = "iso_27001"  # Information Security Management
    ISO_27017 = "iso_27017"  # Cloud Security
    ISO_27018 = "iso_27018"  # Cloud Privacy
    OWASP = "owasp"  # Open Web Application Security Project
    COBIT = "cobit"  # Control Objectives for Information Technologies
    ITIL = "itil"  # IT Infrastructure Library

    # Labor & Employment
    NLRA = "nlra"  # National Labor Relations Act
    FLSA = "flsa"  # Fair Labor Standards Act
    OSHA = "osha"  # Occupational Safety and Health Administration
    EEOC = "eeoc"  # Equal Employment Opportunity Commission
    FMLA = "fmla"  # Family and Medical Leave Act
    UNION_COMPLIANCE = "union_compliance"  # Union Labor Standards

    # Civil Rights & Accessibility
    ACLU_STANDARDS = "aclu_standards"  # ACLU Civil Liberties Standards
    ADA = "ada"  # Americans with Disabilities Act
    SECTION_508 = "section_508"  # Accessibility Standards
    WCAG = "wcag"  # Web Content Accessibility Guidelines

    # Other Important Standards
    FERPA = "ferpa"  # Family Educational Rights and Privacy Act
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    DMCA = "dmca"  # Digital Millennium Copyright Act
    COSO = "coso"  # Committee of Sponsoring Organizations


class ComplianceStatus(Enum):
    """Compliance audit statuses"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"
    REMEDIATION_IN_PROGRESS = "remediation_in_progress"


class RiskLevel(Enum):
    """Risk assessment levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


# ============================================================================
# DATACLASSES
# ============================================================================


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""

    framework: ComplianceFramework
    requirement_id: str
    requirement_name: str
    description: str
    control_objective: str
    implementation_status: ComplianceStatus
    risk_level: RiskLevel
    evidence_required: List[str]
    responsible_party: str
    last_audit_date: Optional[str]
    next_audit_date: str
    notes: str


@dataclass
class ComplianceAuditLog:
    """Compliance audit event"""

    log_id: str
    framework: ComplianceFramework
    event_type: str
    user_id: str
    action_description: str
    timestamp: str
    status: ComplianceStatus
    findings: str
    remediation_required: bool
    integrity_hash: str


# ============================================================================
# FINANCIAL SERVICES COMPLIANCE (PCI DSS, FINRA, SOX)
# ============================================================================


class FinancialServicesCompliance:
    """
    Financial Services Regulatory Compliance

    Implements:
    - PCI DSS v4.0: Payment card security
    - FINRA: Financial industry regulations
    - SOX: Financial reporting and internal controls
    - GLBA: Financial privacy
    - BSA/AML: Anti-money laundering
    - Dodd-Frank: Systemic risk management
    """

    def __init__(self):
        self.framework_name = "Financial Services Compliance"
        logger.info(f"{self.framework_name} initialized")

    def validate_pci_dss_transaction(
        self, transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate PCI DSS compliance for payment transaction

        Requirements:
        - No full card numbers (tokenization required)
        - No CVV stored
        - TLS 1.2+ for transmission
        - Audit logging enabled
        """
        violations = []

        # Check for prohibited data storage
        prohibited_fields = ["card_number", "cvv", "cvv2", "cvc", "pin"]
        for field in prohibited_fields:
            if field in transaction_data and transaction_data[field]:
                violations.append(f"PCI DSS Violation: {field} must not be stored")

        # Require tokenization
        if "card_token" not in transaction_data:
            violations.append("PCI DSS Violation: Card must be tokenized")

        # Validate encryption
        if not transaction_data.get("encrypted", False):
            violations.append("PCI DSS Violation: Data must be encrypted in transit")

        # Require audit trail
        if "transaction_id" not in transaction_data:
            violations.append(
                "PCI DSS Violation: Transaction ID required for audit trail"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_finra_communication(
        self, communication_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate FINRA compliance for financial communications

        Requirements:
        - Record retention (3-6 years depending on type)
        - Supervision and review
        - No misleading statements
        - Risk disclosures present
        """
        violations = []

        # Check for required disclosures
        if not communication_data.get("risk_disclosure", False):
            violations.append(
                "FINRA Violation: Risk disclosure required for investment communications"
            )

        # Check for supervision
        if not communication_data.get("supervised_by"):
            violations.append(
                "FINRA Violation: Communication must be supervised by principal"
            )

        # Check retention metadata
        if not communication_data.get("retention_category"):
            violations.append("FINRA Violation: Retention category must be specified")

        # Prohibit misleading statements
        prohibited_phrases = ["guaranteed returns", "risk-free", "no risk"]
        content = communication_data.get("content", "").lower()
        for phrase in prohibited_phrases:
            if phrase in content:
                violations.append(
                    f"FINRA Violation: Misleading phrase '{phrase}' not permitted"
                )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_sox_controls(
        self, financial_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate SOX (Sarbanes-Oxley) compliance

        Requirements:
        - Segregation of duties
        - Change management controls
        - Access controls
        - Audit trails
        """
        violations = []

        # Check segregation of duties
        if financial_data.get("preparer_id") == financial_data.get("approver_id"):
            violations.append(
                "SOX Violation: Preparer and approver cannot be same person"
            )

        # Require dual authorization for material transactions
        if financial_data.get("amount", 0) > 10000 and not financial_data.get(
            "dual_authorization"
        ):
            violations.append(
                "SOX Violation: Transactions >$10,000 require dual authorization"
            )

        # Check audit trail
        if not financial_data.get("audit_log_id"):
            violations.append(
                "SOX Violation: All financial transactions must have audit trail"
            )

        # Require integrity hash
        if not financial_data.get("integrity_hash"):
            violations.append(
                "SOX Violation: Financial records must have tamper-evident hashing"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations


# ============================================================================
# HEALTHCARE COMPLIANCE (HIPAA, HITECH, FDA)
# ============================================================================


class HealthcareCompliance:
    """
    Healthcare Regulatory Compliance

    Implements:
    - HIPAA: Protected Health Information security
    - HITECH: Electronic health records
    - FDA 21 CFR Part 11: Electronic signatures
    """

    def __init__(self):
        self.framework_name = "Healthcare Compliance"
        logger.info(f"{self.framework_name} initialized")

    def validate_hipaa_phi_protection(
        self, phi_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate HIPAA compliance for Protected Health Information

        Requirements (45 CFR § 164.312 - Security Rule):
        - PHI must be encrypted at rest and in transit
        - Access controls required
        - Audit logging enabled
        - Minimum necessary standard
        - Breach notification procedures
        """
        violations = []

        # Check encryption requirement (§164.312(a)(2)(iv) and §164.312(e)(2)(ii))
        if not phi_data.get("encrypted", False):
            violations.append(
                "HIPAA Violation: PHI must be encrypted at rest and in transit (§164.312)"
            )

        # Verify encryption strength
        encryption_algorithm = phi_data.get("encryption_algorithm", "").upper()
        if encryption_algorithm and encryption_algorithm not in [
            "AES-256",
            "AES256",
            "AES_256",
        ]:
            violations.append(
                "HIPAA Violation: PHI requires AES-256 encryption or equivalent"
            )

        # Check access controls (§164.312(a)(1))
        if "access_control_id" not in phi_data:
            violations.append(
                "HIPAA Violation: Access controls required for PHI access (§164.312(a)(1))"
            )

        # Verify audit logging (§164.312(b))
        if not phi_data.get("audit_log_enabled", False):
            violations.append(
                "HIPAA Violation: Audit controls required for PHI access (§164.312(b))"
            )

        # Check minimum necessary standard (§164.502(b))
        if not phi_data.get("minimum_necessary", False):
            violations.append(
                "HIPAA Violation: Minimum necessary standard not documented (§164.502(b))"
            )

        # Check authentication (§164.312(d))
        if not phi_data.get("user_authenticated", False):
            violations.append(
                "HIPAA Violation: Person or entity authentication required (§164.312(d))"
            )

        # Check transmission security (§164.312(e)(1))
        if phi_data.get("transmitted", False) and not phi_data.get(
            "transmission_encrypted", False
        ):
            violations.append(
                "HIPAA Violation: PHI transmission must be encrypted (§164.312(e))"
            )

        # Verify no prohibited disclosures
        if phi_data.get("disclosed_without_authorization", False):
            violations.append(
                "HIPAA Violation: PHI disclosure requires patient authorization (§164.508)"
            )

        # Check for business associate agreement if data shared with third party
        if phi_data.get("shared_with_third_party", False) and not phi_data.get(
            "baa_in_place", False
        ):
            violations.append(
                "HIPAA Violation: Business Associate Agreement required for third-party PHI sharing (§164.502(e))"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_hitech_ehr_security(
        self, ehr_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate HITECH Act compliance for Electronic Health Records

        Requirements:
        - Enhanced breach notification
        - Meaningful use standards
        - Audit trail integrity
        """
        violations = []

        # Check breach notification procedures
        if not ehr_data.get("breach_notification_procedure", False):
            violations.append(
                "HITECH Violation: Breach notification procedures required"
            )

        # Verify audit trail
        if not ehr_data.get("immutable_audit_trail", False):
            violations.append(
                "HITECH Violation: Immutable audit trail required for EHR modifications"
            )

        # Check encryption for electronic transmission
        if not ehr_data.get("end_to_end_encryption", False):
            violations.append(
                "HITECH Violation: End-to-end encryption required for EHR transmission"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations


# ============================================================================
# TELECOMMUNICATIONS COMPLIANCE (FCC)
# ============================================================================


class TelecommunicationsCompliance:
    """
    FCC and Telecommunications Regulatory Compliance

    Implements:
    - TCPA: Telephone Consumer Protection Act
    - CPNI: Customer Proprietary Network Information
    - CAN-SPAM: Email marketing
    - CALEA: Law enforcement assistance
    """

    def __init__(self):
        self.framework_name = "Telecommunications Compliance"
        logger.info(f"{self.framework_name} initialized")

    def validate_tcpa_consent(
        self, contact_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate TCPA compliance for automated communications

        Requirements:
        - Prior express written consent for automated calls/texts
        - Time-of-day restrictions (8 AM - 9 PM local time)
        - Opt-out mechanism provided
        - Do Not Call (DNC) registry compliance
        """
        violations = []

        # Check consent
        if contact_data.get("automated", False) and not contact_data.get(
            "consent_given"
        ):
            violations.append(
                "TCPA Violation: Prior express written consent required for automated calls"
            )

        # Check time restrictions
        if "call_time" in contact_data:
            call_hour = int(contact_data["call_time"].split(":")[0])
            if call_hour < 8 or call_hour >= 21:
                violations.append(
                    f"TCPA Violation: Calls restricted to 8 AM - 9 PM local time (attempted: {call_hour}:00)"
                )

        # Check opt-out mechanism
        if not contact_data.get("opt_out_available"):
            violations.append("TCPA Violation: Opt-out mechanism must be provided")

        # Check DNC registry
        if contact_data.get("on_dnc_list", False):
            violations.append("TCPA Violation: Number on Do Not Call registry")

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_cpni_protection(
        self, customer_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate CPNI (Customer Proprietary Network Information) protection

        CPNI includes: phone numbers, call records, location data
        """
        violations = []

        # Check customer consent for CPNI use
        if not customer_data.get("cpni_consent"):
            violations.append(
                "CPNI Violation: Customer consent required to use network information"
            )

        # Check authentication
        if not customer_data.get("customer_authenticated"):
            violations.append(
                "CPNI Violation: Customer identity must be authenticated before CPNI disclosure"
            )

        # Check encryption
        if not customer_data.get("encrypted"):
            violations.append(
                "CPNI Violation: CPNI must be encrypted in storage and transmission"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations


# ============================================================================
# LABOR & EMPLOYMENT COMPLIANCE
# ============================================================================


class LaborEmploymentCompliance:
    """
    Labor and Employment Regulatory Compliance

    Implements:
    - NLRA: National Labor Relations Act (union rights)
    - FLSA: Fair Labor Standards Act (wages, hours)
    - OSHA: Occupational safety
    - EEOC: Equal employment opportunity
    - Union contracts and collective bargaining
    """

    def __init__(self):
        self.framework_name = "Labor & Employment Compliance"
        logger.info(f"{self.framework_name} initialized")

    def validate_nlra_rights(
        self, employee_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate NLRA (National Labor Relations Act) compliance

        Protects:
        - Right to organize unions
        - Right to collective bargaining
        - Right to concerted activity
        - Protection from retaliation
        """
        violations = []

        # Check for retaliation flags - including alternate field names
        union_activity_indicators = [
            "union_activity",
            "recent_organizing_activity",
            "union_organizing",
            "collective_bargaining_activity",
            "concerted_activity",
            "labor_organizing",
        ]

        disciplinary_action_indicators = [
            "disciplinary_action",
            "employee_action_taken",
            "adverse_action",
            "termination",
            "suspension",
            "demotion",
            "discipline_imposed",
        ]

        business_reason_indicators = [
            "legitimate_business_reason",
            "justification",
            "documented_cause",
            "performance_issues",
            "business_justification",
        ]

        # Check if any union activity indicator is true
        has_union_activity = any(
            employee_data.get(indicator, False)
            for indicator in union_activity_indicators
        )

        # Check if any disciplinary action indicator is true
        has_disciplinary_action = any(
            employee_data.get(indicator, False)
            for indicator in disciplinary_action_indicators
        )

        # Check if any business reason indicator is true
        has_business_reason = any(
            employee_data.get(indicator, False)
            for indicator in business_reason_indicators
        )

        # Detect potential retaliation
        if has_union_activity and has_disciplinary_action:
            if not has_business_reason:
                violations.append(
                    "NLRA Violation: Disciplinary action after union activity requires documented business reason"
                )

        # Check surveillance
        if employee_data.get("surveillance_of_union_activity"):
            violations.append(
                "NLRA Violation: Surveillance of union organizing is prohibited"
            )

        # Check communication restrictions
        if employee_data.get("prohibited_discussions"):
            prohibited = employee_data["prohibited_discussions"]
            if "wages" in prohibited or "working_conditions" in prohibited:
                violations.append(
                    "NLRA Violation: Cannot prohibit discussions about wages or working conditions"
                )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_flsa_compliance(
        self, payroll_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate FLSA (Fair Labor Standards Act) compliance

        Requirements:
        - Minimum wage compliance
        - Overtime pay (1.5x for hours > 40/week)
        - Child labor restrictions
        - Recordkeeping (3 years)
        """
        violations = []

        # Check minimum wage
        federal_minimum_wage = 7.25  # As of 2025
        hourly_rate = payroll_data.get("hourly_rate", 0)
        if hourly_rate < federal_minimum_wage:
            violations.append(
                f"FLSA Violation: Hourly rate ${hourly_rate} below federal minimum ${federal_minimum_wage}"
            )

        # Check overtime pay
        hours_worked = payroll_data.get("hours_worked", 0)
        if hours_worked > 40:
            overtime_hours = hours_worked - 40
            expected_overtime_pay = (
                overtime_hours * payroll_data.get("hourly_rate", 0) * 1.5
            )
            actual_overtime_pay = payroll_data.get("overtime_pay", 0)
            if actual_overtime_pay < expected_overtime_pay:
                violations.append(
                    f"FLSA Violation: Overtime pay insufficient (expected: ${expected_overtime_pay:.2f}, actual: ${actual_overtime_pay:.2f})"
                )

        # Check child labor
        if payroll_data.get("employee_age", 18) < 16:
            if payroll_data.get("hours_worked", 0) > 3 or payroll_data.get(
                "late_night_work"
            ):
                violations.append(
                    "FLSA Violation: Child labor restrictions violated (max 3 hours on school days, no late night work)"
                )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_union_contract(
        self, contract_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate union contract compliance

        Requirements:
        - Grievance procedures
        - Seniority rights
        - Just cause for termination
        - Union security clauses
        """
        violations = []

        # Check termination process
        if contract_data.get("termination_action"):
            if not contract_data.get("just_cause_documented"):
                violations.append(
                    "Union Contract Violation: Termination requires documented just cause"
                )

            if not contract_data.get("union_notified"):
                violations.append(
                    "Union Contract Violation: Union must be notified of termination actions"
                )

            if not contract_data.get("grievance_process_available"):
                violations.append(
                    "Union Contract Violation: Employee must be informed of grievance rights"
                )

        # Check seniority rights
        if contract_data.get("layoff_action") and not contract_data.get(
            "seniority_followed"
        ):
            violations.append(
                "Union Contract Violation: Layoffs must follow seniority order per contract"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations


# ============================================================================
# CIVIL RIGHTS & ACCESSIBILITY COMPLIANCE
# ============================================================================


class CivilRightsAccessibilityCompliance:
    """
    Civil Rights and Accessibility Compliance

    Implements:
    - ACLU Standards: Civil liberties protection
    - ADA: Americans with Disabilities Act
    - Section 508: Electronic accessibility
    - WCAG: Web Content Accessibility Guidelines
    """

    def __init__(self):
        self.framework_name = "Civil Rights & Accessibility Compliance"
        logger.info(f"{self.framework_name} initialized")

    def validate_aclu_standards(
        self, civil_liberty_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate ACLU civil liberties standards

        Protects:
        - Freedom of speech
        - Privacy rights
        - Due process
        - Equal protection
        - Freedom from discrimination
        """
        violations = []

        # Check surveillance and privacy
        if civil_liberty_data.get("surveillance_without_warrant"):
            violations.append(
                "ACLU Standard Violation: Surveillance without warrant violates Fourth Amendment"
            )

        # Check free speech
        if civil_liberty_data.get("content_censored") and not civil_liberty_data.get(
            "imminent_lawless_action"
        ):
            violations.append(
                "ACLU Standard Violation: Content censorship requires imminent lawless action standard"
            )

        # Check due process
        if civil_liberty_data.get("disciplinary_action") and not civil_liberty_data.get(
            "notice_and_hearing"
        ):
            violations.append(
                "ACLU Standard Violation: Due process requires notice and opportunity to be heard"
            )

        # Check discrimination
        protected_classes = [
            "race",
            "religion",
            "gender",
            "national_origin",
            "disability",
            "sexual_orientation",
        ]
        if civil_liberty_data.get("adverse_action"):
            for protected_class in protected_classes:
                if civil_liberty_data.get(f"based_on_{protected_class}"):
                    violations.append(
                        f"ACLU Standard Violation: Discrimination based on {protected_class} prohibited"
                    )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_ada_accessibility(
        self, accessibility_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate ADA (Americans with Disabilities Act) compliance

        Requirements:
        - Reasonable accommodations
        - No disability discrimination
        - Accessible facilities and technology
        """
        violations = []

        # Check accommodation requests
        if accessibility_data.get(
            "accommodation_requested"
        ) and not accessibility_data.get("accommodation_provided"):
            if not accessibility_data.get("undue_hardship_documented"):
                violations.append(
                    "ADA Violation: Reasonable accommodation must be provided unless undue hardship"
                )

        # Check technology accessibility
        if not accessibility_data.get("screen_reader_compatible"):
            violations.append(
                "ADA Violation: Technology must be accessible to screen readers"
            )

        if not accessibility_data.get("keyboard_navigable"):
            violations.append(
                "ADA Violation: All functions must be keyboard accessible"
            )

        # Check discrimination
        if accessibility_data.get("adverse_action_based_on_disability"):
            violations.append(
                "ADA Violation: Adverse actions based on disability are prohibited"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def validate_section_508(
        self, digital_content: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate Section 508 accessibility compliance

        Requirements for federal systems:
        - Alt text for images
        - Captions for video
        - Keyboard accessibility
        - Color contrast ratios
        """
        violations = []

        # Check images
        if digital_content.get("has_images") and not digital_content.get(
            "alt_text_provided"
        ):
            violations.append(
                "Section 508 Violation: All images require descriptive alt text"
            )

        # Check multimedia
        if digital_content.get("has_video") and not digital_content.get(
            "captions_provided"
        ):
            violations.append(
                "Section 508 Violation: Video content requires captions/transcripts"
            )

        # Check color contrast
        if digital_content.get("color_contrast_ratio", 10) < 4.5:
            violations.append(
                "Section 508 Violation: Color contrast ratio must be at least 4.5:1"
            )

        # Check forms
        if digital_content.get("has_forms") and not digital_content.get(
            "labels_associated"
        ):
            violations.append(
                "Section 508 Violation: Form inputs require associated labels"
            )

        is_compliant = len(violations) == 0
        return is_compliant, violations


# ============================================================================
# UNIFIED COMPLIANCE ORCHESTRATOR
# ============================================================================


# ---------------------------------------------------------------------------
# Extended validators (added 2026-10-19). Previously 32 of 45 frameworks
# fell through to a default that returned COMPLIANT unimplemented. These
# evidence-presence validators cover them all; the dispatcher default is
# now fail-closed. They verify required compliance evidence is present in
# a submission — they are not legal determinations.
# ---------------------------------------------------------------------------
def _evidence_check(
    framework_name: str,
    data: Dict[str, Any],
    required: Dict[str, str],
    prohibited: Tuple[str, ...] = (),
) -> Tuple[bool, List[str]]:
    """Shared evidence check: prohibited fields present, or required
    evidence fields missing/falsy, produce violations."""
    violations: List[str] = []
    for field in prohibited:
        if data.get(field):
            violations.append(
                f"{framework_name} Violation: {field} must not be present"
            )
    for field, desc in required.items():
        value = data.get(field)
        if value is None or value == "" or value is False:
            violations.append(f"{framework_name} Violation: {desc}")
    return (len(violations) == 0), violations


class PrivacyCompliance:
    """Privacy-framework evidence validators (GDPR/CCPA/PIPEDA/LGPD/APPI)."""

    def validate_gdpr(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("GDPR", data, {
            "lawful_basis": "a lawful basis for processing must be recorded",
            "privacy_notice_provided": "privacy notice must be provided to data subjects",
            "data_subject_rights_process": "a data-subject rights process (access/erasure) must exist",
        })

    def validate_ccpa(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("CCPA", data, {
            "consumer_rights_notice": "consumer rights notice required",
            "opt_out_mechanism": "a do-not-sell/share opt-out mechanism is required",
            "privacy_policy_current": "privacy policy must disclose data practices",
        })

    def validate_pipeda(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("PIPEDA", data, {
            "consent_obtained": "meaningful consent required",
            "privacy_officer_assigned": "a privacy officer must be designated",
            "access_procedures": "individual access procedures required",
        })

    def validate_lgpd(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("LGPD", data, {
            "lawful_basis": "a lawful basis for processing must be recorded",
            "dpo_assigned": "a data protection officer (encarregado) must be designated",
            "privacy_notice_provided": "privacy notice must be provided to data subjects",
        })

    def validate_appi(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("APPI", data, {
            "purpose_of_use_specified": "purpose of use must be specified",
            "privacy_policy_published": "privacy policy must be published",
            "security_controls_documented": "security control measures must be documented",
        })


class GovernanceStandardsCompliance:
    """Evidence validators for the remaining financial, federal, security,
    labor, civil-rights, and misc frameworks not covered by the family
    classes (see module docstring for scope and limits)."""

    # -- financial leftovers --
    def validate_glba(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("GLBA", data, {
            "information_security_program": "a written information security program is required (Safeguards Rule)",
            "customer_notice_provided": "privacy notice to customers required",
            "access_controls_documented": "access controls for customer information required",
        })

    def validate_dodd_frank(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("Dodd-Frank", data, {
            "compliance_program_documented": "a compliance program must be documented",
            "regulatory_reporting_procedures": "regulatory reporting procedures required",
        })

    def validate_bsa_aml(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("BSA/AML", data, {
            "aml_program_documented": "a BSA/AML compliance program is required",
            "kyc_procedures": "customer identification (KYC) procedures required",
            "suspicious_activity_monitoring": "transaction monitoring for suspicious activity required",
        })

    def validate_sec_reg(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("SEC", data, {
            "disclosure_controls": "disclosure controls and procedures required",
            "filings_current": "required filings must be current",
        })

    # -- healthcare leftover --
    def validate_fda_21_cfr_11(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FDA 21 CFR Part 11", data, {
            "audit_trail_enabled": "secure audit trails required for electronic records",
            "electronic_signatures_validated": "electronic signature controls must be validated",
            "record_retention_policy": "a record retention policy is required",
        })

    # -- telecom leftovers --
    def validate_can_spam(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("CAN-SPAM", data, {
            "sender_identified": "sender must be accurately identified",
            "opt_out_mechanism": "a working opt-out mechanism is required",
            "physical_address_included": "a valid physical postal address is required",
        })

    def validate_calea(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("CALEA", data, {
            "lawful_intercept_capability_documented": "lawful intercept capability must be documented",
            "privacy_safeguards_documented": "privacy safeguards for intercept data required",
        })

    # -- labor leftovers --
    def validate_osha(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("OSHA", data, {
            "safety_program_documented": "a workplace safety program is required",
            "hazard_assessment_completed": "a hazard assessment must be completed",
            "incident_log_maintained": "injury/illness records must be maintained",
        })

    def validate_eeoc(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("EEOC", data, {
            "nondiscrimination_policy": "an EEO/nondiscrimination policy is required",
            "complaint_process_documented": "a discrimination complaint process must be documented",
        })

    def validate_fmla(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FMLA", data, {
            "leave_policy_documented": "FMLA leave policy must be documented",
            "eligibility_notices_provided": "eligibility notices must be provided to employees",
        })

    # -- civil rights leftover --
    def validate_wcag(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("WCAG", data, {
            "accessibility_audit_completed": "an accessibility audit against WCAG criteria is required",
            "wcag_conformance_level": "target WCAG conformance level must be recorded",
        })

    # -- security / industry standards --
    def validate_soc2(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("SOC 2", data, {
            "access_controls_documented": "logical access controls must be documented (CC6)",
            "change_management_process": "change management process required (CC7)",
            "system_monitoring_enabled": "system monitoring required (CC7)",
            "incident_response_plan": "incident response procedures required",
        })

    def validate_iso_27001(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("ISO 27001", data, {
            "isms_scope_defined": "ISMS scope must be defined",
            "risk_assessment_completed": "information security risk assessment required",
            "access_control_policy": "an access control policy is required",
        })

    def validate_iso_27017(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("ISO 27017", data, {
            "cloud_controls_documented": "cloud security controls must be documented",
            "shared_responsibility_defined": "shared responsibility model must be defined",
        })

    def validate_iso_27018(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("ISO 27018", data, {
            "pii_processor_controls": "PII protection controls for public cloud required",
            "data_subject_consent": "consent for PII processing must be recorded",
        })

    def validate_owasp(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("OWASP", data, {
            "input_validation_enabled": "input validation required (OWASP ASVS)",
            "output_encoding_enabled": "output encoding required (OWASP ASVS)",
            "security_headers_enabled": "security headers must be enabled",
        })

    def validate_cobit(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("COBIT", data, {
            "governance_framework_documented": "an IT governance framework must be documented",
            "risk_register_maintained": "a risk register must be maintained",
        })

    def validate_itil(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("ITIL", data, {
            "incident_process_defined": "an incident management process must be defined",
            "change_records_maintained": "change records must be maintained",
        })

    # -- federal --
    def validate_nist_800_53(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("NIST SP 800-53", data, {
            "security_controls_implemented": "NIST SP 800-53 controls must be implemented",
            "continuous_monitoring": "a continuous monitoring strategy is required",
        })

    def validate_fisma(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FISMA", data, {
            "system_categorization": "FIPS 199 system categorization required",
            "security_plan_documented": "a system security plan is required",
            "authorization_to_operate": "an authorization to operate (ATO) is required",
        })

    def validate_ftc_act(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FTC Act", data, {
            "truthful_disclosures": "disclosures must be truthful and substantiated",
        }, prohibited=("deceptive_practices",))

    def validate_omb_m_25_04(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("OMB M-25-04", data, {
            "identity_mfa_enforced": "phishing-resistant MFA required (zero trust)",
            "device_trust_verified": "device trust must be verified",
            "least_privilege_enforced": "least-privilege access must be enforced",
        })

    def validate_ferc(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FERC", data, {
            "reliability_standards_documented": "reliability standards compliance must be documented",
            "cip_controls_documented": "CIP cybersecurity controls required",
        })

    # -- education / children / IP / controls --
    def validate_ferpa(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("FERPA", data, {
            "student_consent_for_disclosure": "consent required before disclosing education records",
            "records_access_controls": "access controls for education records required",
        }, prohibited=("unauthorized_disclosure",))

    def validate_coppa(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("COPPA", data, {
            "parental_consent_obtained": "verifiable parental consent required",
            "child_data_minimized": "children's data collection must be minimized",
        }, prohibited=("behavioral_advertising_to_children",))

    def validate_dmca(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("DMCA", data, {
            "designated_agent_registered": "a designated copyright agent must be registered",
            "takedown_process_documented": "a notice-and-takedown process must be documented",
        })

    def validate_coso(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return _evidence_check("COSO", data, {
            "internal_controls_documented": "internal control framework must be documented",
            "control_environment_assessed": "the control environment must be assessed",
        })


class UnifiedComplianceFramework:
    """
    Unified Compliance Orchestrator for Mythara Engine

    Coordinates compliance across all regulatory frameworks and provides:
    - Multi-framework compliance validation
    - Compliance audit logging
    - Risk assessment and reporting
    - Automated compliance monitoring
    """

    def __init__(self, rate_limit_per_second: int = 10):
        self.financial = FinancialServicesCompliance()
        self.healthcare = HealthcareCompliance()
        self.telecom = TelecommunicationsCompliance()
        self.labor = LaborEmploymentCompliance()
        self.civil_rights = CivilRightsAccessibilityCompliance()
        self.privacy = PrivacyCompliance()
        self.standards = GovernanceStandardsCompliance()

        self.audit_logs: List[ComplianceAuditLog] = []

        # Rate limiting (token bucket algorithm)
        self.rate_limit_per_second = rate_limit_per_second
        self.rate_limit_buckets: Dict[str, Dict[str, Any]] = {}

        # SECURITY FIX: Brute force protection
        self.failed_login_attempts: Dict[str, List[datetime]] = (
            {}
        )  # Track failed attempts
        self.locked_accounts: Dict[str, datetime] = {}  # Track account lockouts

        logger.info(
            f"Unified Compliance Framework initialized (rate limit: {rate_limit_per_second} req/sec)"
        )

    def validate_multi_framework_compliance(
        self,
        data: Dict[str, Any],
        frameworks: List[ComplianceFramework],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate compliance across multiple frameworks simultaneously

        Args:
            data: Data to validate
            frameworks: List of compliance frameworks to check
            user_id: User ID performing the validation (required for audit trail)

        Returns:
            Compliance validation results with audit metadata
        """
        # SECURITY FIX #1: Enforce mandatory authentication - no null/empty user_id allowed
        if not user_id:
            user_id = data.get("user_id")

        # Strict validation: reject None, empty string, whitespace, null bytes
        if not user_id or not str(user_id).strip() or "\x00" in str(user_id):
            logger.error(f"Authentication failed: Invalid user_id: {repr(user_id)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "frameworks_checked": [f.value for f in frameworks],
                "overall_compliant": False,
                "framework_results": {},
                "all_violations": [
                    "CRITICAL: Authentication required - user_id must be non-empty string"
                ],
                "risk_assessment": "CRITICAL",
                "audit_log_id": None,
                "integrity_hash": None,
                "error": "AUTHENTICATION_REQUIRED",
                "message": "Authentication required - user_id must be a non-empty string",
            }

        # SECURITY FIX #2: Sanitize user_id to prevent SQL injection
        try:
            user_id = sanitize_input(user_id)
        except ValueError as e:
            logger.error(f"Input validation failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "frameworks_checked": [f.value for f in frameworks],
                "overall_compliant": False,
                "framework_results": {},
                "all_violations": [f"Input validation failed: {str(e)}"],
                "risk_assessment": "HIGH",
                "audit_log_id": None,
                "integrity_hash": None,
                "error": "INVALID_INPUT",
                "message": "Input validation failed",
            }

        # SECURITY FIX #3: Check for account lockout (brute force protection)
        if user_id in self.locked_accounts:
            lockout_time = self.locked_accounts[user_id]
            time_remaining = (
                lockout_time + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            ) - datetime.utcnow()
            if time_remaining.total_seconds() > 0:
                logger.warning(f"Account locked: {user_id}")
                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "frameworks_checked": [f.value for f in frameworks],
                    "overall_compliant": False,
                    "framework_results": {},
                    "all_violations": [
                        f"Account locked due to too many failed attempts. Try again in {int(time_remaining.total_seconds() / 60)} minutes."
                    ],
                    "risk_assessment": "HIGH",
                    "audit_log_id": None,
                    "integrity_hash": None,
                    "error": "ACCOUNT_LOCKED",
                    "message": "Account locked due to too many failed attempts",
                    "user_id": user_id,
                }
            else:
                # Lockout expired, remove it
                del self.locked_accounts[user_id]
                if user_id in self.failed_login_attempts:
                    del self.failed_login_attempts[user_id]

        # Check rate limit for this user
        if not self._check_rate_limit(user_id):
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "frameworks_checked": [f.value for f in frameworks],
                "overall_compliant": False,
                "framework_results": {},
                "all_violations": [
                    f"Rate Limit Violation: Maximum {self.rate_limit_per_second} requests per second exceeded"
                ],
                "risk_assessment": "MEDIUM",
                "audit_log_id": None,
                "integrity_hash": None,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded",
                "user_id": user_id,
            }

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "frameworks_checked": [f.value for f in frameworks],
            "overall_compliant": True,
            "framework_results": {},
            "all_violations": [],
            "risk_assessment": "LOW",
            "user_id": user_id,
        }

        for framework in frameworks:
            try:
                is_compliant, violations = self._validate_framework(framework, data)
            except Exception as e:
                # A crashing validator must fail closed, never crash the
                # whole validation or silently pass (found 2026-10-19:
                # FLSA raised KeyError on missing hourly_rate).
                logger.error(f"Validator error for {framework.value}: {e}")
                is_compliant = False
                violations = [
                    f"{framework.value}: validator error ({type(e).__name__}: {e})"
                ]

            results["framework_results"][framework.value] = {
                "compliant": is_compliant,
                "violations": violations,
            }

            if not is_compliant:
                results["overall_compliant"] = False
                results["all_violations"].extend(violations)

        # Assess risk level
        violation_count = len(results["all_violations"])
        if violation_count == 0:
            results["risk_assessment"] = "NEGLIGIBLE"
        elif violation_count <= 2:
            results["risk_assessment"] = "LOW"
        elif violation_count <= 5:
            results["risk_assessment"] = "MEDIUM"
        elif violation_count <= 10:
            results["risk_assessment"] = "HIGH"
        else:
            results["risk_assessment"] = "CRITICAL"

        # Track successful operation (reset failed attempts if any)
        if user_id in self.failed_login_attempts:
            del self.failed_login_attempts[user_id]

        # Log audit event and get audit log ID and integrity hash
        audit_log_id, integrity_hash = self._log_compliance_audit(frameworks, results)

        # Add audit metadata to results
        results["audit_log_id"] = audit_log_id
        results["integrity_hash"] = integrity_hash

        return results

    def _validate_framework(
        self, framework: ComplianceFramework, data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Route validation to the appropriate compliance module.

        All 45 frameworks have a validator. Anything unrouted fails
        closed — an unimplemented check must never report compliant.
        """
        F = ComplianceFramework
        routes = {
            # financial
            F.PCI_DSS: self.financial.validate_pci_dss_transaction,
            F.FINRA: self.financial.validate_finra_communication,
            F.SOX: self.financial.validate_sox_controls,
            F.GLBA: self.standards.validate_glba,
            F.DODD_FRANK: self.standards.validate_dodd_frank,
            F.BSA_AML: self.standards.validate_bsa_aml,
            F.SEC_REG: self.standards.validate_sec_reg,
            # healthcare
            F.HIPAA: self.healthcare.validate_hipaa_phi_protection,
            F.HITECH: self.healthcare.validate_hitech_ehr_security,
            F.FDA_21_CFR_11: self.standards.validate_fda_21_cfr_11,
            # telecommunications
            F.FCC_TCPA: self.telecom.validate_tcpa_consent,
            F.FCC_CPNI: self.telecom.validate_cpni_protection,
            F.CAN_SPAM: self.standards.validate_can_spam,
            F.CALEA: self.standards.validate_calea,
            # federal
            F.FISMA: self.standards.validate_fisma,
            F.NIST_800_53: self.standards.validate_nist_800_53,
            F.FTC_ACT: self.standards.validate_ftc_act,
            F.OMB_M_25_04: self.standards.validate_omb_m_25_04,
            F.FERC: self.standards.validate_ferc,
            # privacy
            F.GDPR: self.privacy.validate_gdpr,
            F.CCPA: self.privacy.validate_ccpa,
            F.PIPEDA: self.privacy.validate_pipeda,
            F.LGPD: self.privacy.validate_lgpd,
            F.APPI: self.privacy.validate_appi,
            # industry standards
            F.SOC_2: self.standards.validate_soc2,
            F.ISO_27001: self.standards.validate_iso_27001,
            F.ISO_27017: self.standards.validate_iso_27017,
            F.ISO_27018: self.standards.validate_iso_27018,
            F.OWASP: self.standards.validate_owasp,
            F.COBIT: self.standards.validate_cobit,
            F.ITIL: self.standards.validate_itil,
            # labor & employment
            F.NLRA: self.labor.validate_nlra_rights,
            F.FLSA: self.labor.validate_flsa_compliance,
            F.OSHA: self.standards.validate_osha,
            F.EEOC: self.standards.validate_eeoc,
            F.FMLA: self.standards.validate_fmla,
            F.UNION_COMPLIANCE: self.labor.validate_union_contract,
            # civil rights & accessibility
            F.ACLU_STANDARDS: self.civil_rights.validate_aclu_standards,
            F.ADA: self.civil_rights.validate_ada_accessibility,
            F.SECTION_508: self.civil_rights.validate_section_508,
            F.WCAG: self.standards.validate_wcag,
            # education / children / IP / controls
            F.FERPA: self.standards.validate_ferpa,
            F.COPPA: self.standards.validate_coppa,
            F.DMCA: self.standards.validate_dmca,
            F.COSO: self.standards.validate_coso,
        }
        handler = routes.get(framework)
        if handler is None:
            logger.error(f"No validator implemented for {framework.value}")
            return False, [
                f"{framework.value}: no validator implemented — failing closed"
            ]
        return handler(data)

    def _log_compliance_audit(
        self, frameworks: List[ComplianceFramework], results: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Log compliance audit event and return log ID and integrity hash"""
        log_id = f"COMP_AUDIT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        # SECURITY FIX #4: Generate HMAC integrity hash (prevents tampering)
        hash_input = json.dumps(results, sort_keys=True).encode("utf-8")
        integrity_hash = hmac.new(SECRET_KEY, hash_input, hashlib.sha256).hexdigest()

        # Extract user_id from results (required for audit trail)
        user_id = results.get("user_id", "UNKNOWN")

        audit_log = ComplianceAuditLog(
            log_id=log_id,
            framework=frameworks[0] if frameworks else ComplianceFramework.SOC_2,
            event_type="multi_framework_validation",
            user_id=user_id,
            action_description=f"Validated {len(frameworks)} frameworks",
            timestamp=datetime.utcnow().isoformat(),
            status=(
                ComplianceStatus.COMPLIANT
                if results["overall_compliant"]
                else ComplianceStatus.NON_COMPLIANT
            ),
            findings=json.dumps(results["all_violations"]),
            remediation_required=not results["overall_compliant"],
            integrity_hash=integrity_hash,
        )

        self.audit_logs.append(audit_log)
        logger.info(f"Compliance audit logged: {log_id} for user: {user_id}")

        return log_id, integrity_hash

    def _track_failed_attempt(self, user_id: str) -> None:
        """Track failed login attempt and lock account if threshold exceeded"""
        current_time = datetime.utcnow()

        # Initialize tracking for this user
        if user_id not in self.failed_login_attempts:
            self.failed_login_attempts[user_id] = []

        # Add current attempt
        self.failed_login_attempts[user_id].append(current_time)

        # Remove attempts older than 15 minutes
        cutoff_time = current_time - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        self.failed_login_attempts[user_id] = [
            attempt
            for attempt in self.failed_login_attempts[user_id]
            if attempt > cutoff_time
        ]

        # Check if threshold exceeded
        if len(self.failed_login_attempts[user_id]) >= MAX_FAILED_ATTEMPTS:
            self.locked_accounts[user_id] = current_time
            logger.warning(
                f"Account locked due to {MAX_FAILED_ATTEMPTS} failed attempts: {user_id}"
            )

    def _check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit using token bucket algorithm

        Args:
            user_id: User identifier

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = datetime.utcnow().timestamp()

        # Get or create bucket for this user
        if user_id not in self.rate_limit_buckets:
            self.rate_limit_buckets[user_id] = {
                "tokens": float(self.rate_limit_per_second),
                "last_refill": current_time,
            }

        bucket = self.rate_limit_buckets[user_id]

        # Calculate time elapsed and refill tokens
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = time_elapsed * self.rate_limit_per_second
        bucket["tokens"] = min(
            float(self.rate_limit_per_second), bucket["tokens"] + tokens_to_add
        )
        bucket["last_refill"] = current_time

        # Check if we have at least one token available
        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True
        else:
            # Rate limit exceeded
            return False

    def get_audit_logs(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return audit log entries as dicts, optionally filtered by user."""
        logs = self.audit_logs
        if user_id is not None:
            logs = [log for log in logs if log.user_id == user_id]
        out = []
        for log in logs:
            entry = asdict(log)
            entry["framework"] = log.framework.value
            entry["status"] = log.status.value
            out.append(entry)
        return out

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance status report"""
        report = {
            "report_generated": datetime.utcnow().isoformat(),
            "total_audits": len(self.audit_logs),
            "frameworks_supported": len(ComplianceFramework),
            "recent_audits": [asdict(log) for log in self.audit_logs[-10:]],
            "compliance_frameworks": {
                "financial": [
                    "PCI DSS v4.0",
                    "FINRA",
                    "SOX",
                    "GLBA",
                    "Dodd-Frank",
                    "BSA/AML",
                    "SEC",
                ],
                "healthcare": ["HIPAA", "HITECH", "FDA 21 CFR Part 11"],
                "telecommunications": ["FCC TCPA", "FCC CPNI", "CAN-SPAM", "CALEA"],
                "federal": [
                    "FISMA",
                    "NIST SP 800-53",
                    "FTC Act",
                    "OMB M-25-04",
                    "FERC",
                ],
                "privacy": ["GDPR", "CCPA", "PIPEDA", "LGPD", "APPI"],
                "industry": [
                    "SOC 2",
                    "ISO 27001/27017/27018",
                    "OWASP",
                    "COBIT",
                    "ITIL",
                ],
                "labor": ["NLRA", "FLSA", "OSHA", "EEOC", "FMLA", "Union Compliance"],
                "civil_rights": ["ACLU Standards", "ADA", "Section 508", "WCAG"],
                "other": ["FERPA", "COPPA", "DMCA", "COSO"],
            },
            "compliance_status": "OPERATIONAL",
        }

        return report


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================


def create_unified_compliance_framework() -> UnifiedComplianceFramework:
    """Factory function to create unified compliance framework"""
    return UnifiedComplianceFramework()


# Module-level instance for easy import
unified_compliance = create_unified_compliance_framework()
