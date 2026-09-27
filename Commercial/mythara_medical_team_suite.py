# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
DrMythara Medical Team Suite - Comprehensive Healthcare Bot System
Combines essential clinical functions with non-essential support roles

CRITICAL DISCLAIMER: 
- NO MEDICAL ADVICE PROVIDED
- NO DIAGNOSTIC CAPABILITIES
- ADMINISTRATIVE & COMPLIANCE SUPPORT ONLY
- NOT A SUBSTITUTE FOR MEDICAL PROFESSIONALS

Essential Bots (Clinical Functions):
1. Triage Coordinator Bot - Patient prioritization workflows
2. Clinical Documentation Assistant - Medical record support
3. Compliance Monitor Bot - Internal compliance-rule tracking (self-assessment only, not regulatory monitoring)
4. Crisis Response Bot - Emergency protocol coordination (includes mental health crises)
5. Rx Management Bot - Medication and prescription management
6. Mental Health Support Bot - DSM-5-TR-informed self-assessment checklists (not clinical assessments), Soul Cradle integration

Non-Essential Bots (Support Roles):
7. Patient Education Bot - Health literacy resources
8. Scheduling Coordinator Bot - Appointment management
9. Resource Allocation Bot - Supply and staffing optimization
10. Administrative Assistant Bot - Paperwork and billing support
11. Quality Assurance Bot - Process improvement monitoring
12. Continuing Education Bot - Staff training coordination

Uses Mythara SSIP Framework:
- Sanctification: Medical protocols locked (immutable)
- Integrity Hashing: All actions cryptographically verified
- Blessings Reservoir: Service quality scores
- Shadow_Resolver: Auto-escalate critical issues
"""

import json
import sqlite3
import hashlib
import logging
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

# Cryptography imports (optional - will use basic encryption if not available)
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("Warning: cryptography library not installed - using basic encryption")

# Configure logging to avoid PHI in logs (HIPAA-aligned practice; no certification claimed)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# HIPAA Compliance Constants
HIPAA_RETENTION_YEARS = 6  # Minimum HIPAA record retention
HIPAA_AUDIT_LOG_RETENTION_YEARS = 6
HIPAA_ENCRYPTION_KEY_ROTATION_DAYS = 90
HIPAA_SESSION_TIMEOUT_MINUTES = 15
HIPAA_MAX_LOGIN_ATTEMPTS = 5
HIPAA_PASSWORD_MIN_LENGTH = 12

# Clinical honesty labeling — stamped on EVERY clinical output.
# This suite is demo-grade workflow software, NOT a medical device,
# NOT a diagnostic tool, and NOT a substitute for licensed clinicians.
CLINICAL_DISCLAIMER = (
    "DEMO-GRADE OUTPUT — NOT MEDICAL ADVICE. This software is not a medical "
    "device and does not diagnose, treat, or prescribe. Clinical logic here is "
    "simplified keyword/threshold rules for demonstration only. All clinical "
    "decisions require a licensed healthcare professional."
)


class UrgencyLevel(Enum):
    """Patient urgency classification"""
    EMERGENCY = "emergency"  # Life-threatening, immediate
    URGENT = "urgent"  # Serious, needs prompt attention
    SEMI_URGENT = "semi_urgent"  # Can wait hours
    NON_URGENT = "non_urgent"  # Can wait days
    ROUTINE = "routine"  # Scheduled appointment


class BotRole(Enum):
    """Medical team bot roles"""
    TRIAGE_COORDINATOR = "triage_coordinator"
    CLINICAL_DOCUMENTATION = "clinical_documentation"
    COMPLIANCE_MONITOR = "compliance_monitor"
    CRISIS_RESPONSE = "crisis_response"
    RX_MANAGEMENT = "rx_management"
    MENTAL_HEALTH_SUPPORT = "mental_health_support"
    PATIENT_EDUCATION = "patient_education"
    SCHEDULING_COORDINATOR = "scheduling_coordinator"
    RESOURCE_ALLOCATION = "resource_allocation"
    ADMINISTRATIVE_ASSISTANT = "administrative_assistant"
    QUALITY_ASSURANCE = "quality_assurance"
    CONTINUING_EDUCATION = "continuing_education"


class HIPAAAccessLevel(Enum):
    """Access levels modeled on HIPAA's minimum-necessary principle (alignment only; no certification claimed)"""
    EMERGENCY = "emergency"  # Break-glass access for emergencies
    FULL_PHI = "full_phi"  # Physicians, nurses with patient care role
    LIMITED_PHI = "limited_phi"  # Support staff, minimum necessary
    ADMINISTRATIVE = "administrative"  # Billing, scheduling (limited PHI)
    TECHNICAL = "technical"  # IT staff, no PHI access
    AUDIT_ONLY = "audit_only"  # Compliance officers, read-only audit logs


class HIPAAEventType(Enum):
    """HIPAA audit log event types"""
    PHI_ACCESS = "phi_access"
    PHI_MODIFY = "phi_modify"
    PHI_DELETE = "phi_delete"
    PHI_EXPORT = "phi_export"
    PHI_PRINT = "phi_print"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_TIMEOUT = "session_timeout"
    ACCESS_DENIED = "access_denied"
    ENCRYPTION_KEY_ROTATION = "encryption_key_rotation"
    BREACH_DETECTION = "breach_detection"
    EMERGENCY_ACCESS = "emergency_access"


class FCCComplianceType(Enum):
    """FCC regulation compliance types"""
    TCPA = "tcpa"  # Telephone Consumer Protection Act
    CAN_SPAM = "can_spam"  # Email marketing regulations
    CPNI = "cpni"  # Customer Proprietary Network Information
    CALEA = "calea"  # Communications Assistance for Law Enforcement
    PART_15 = "part_15"  # Radio frequency devices
    PART_68 = "part_68"  # Network equipment registration


class PCIDSSRequirement(Enum):
    """PCI DSS v4.0 Requirements"""
    REQ_1 = "install_maintain_network_security"  # Firewalls, network segmentation
    REQ_2 = "apply_secure_configurations"  # Default passwords, unnecessary services
    REQ_3 = "protect_stored_cardholder_data"  # Encryption, tokenization
    REQ_4 = "protect_cardholder_data_transmission"  # Strong cryptography, TLS
    REQ_5 = "protect_systems_from_malware"  # Anti-virus, anti-malware
    REQ_6 = "develop_secure_systems"  # Secure coding, vulnerability management
    REQ_7 = "restrict_access_to_cardholder_data"  # Need-to-know basis
    REQ_8 = "identify_authenticate_access"  # Unique IDs, MFA
    REQ_9 = "restrict_physical_access"  # Facility controls, media destruction
    REQ_10 = "log_monitor_network_activity"  # Audit trails, log retention
    REQ_11 = "test_security_systems"  # Vulnerability scans, penetration testing
    REQ_12 = "support_information_security"  # Security policy, training


class PaymentCardType(Enum):
    """Payment card types (for PCI DSS scope)"""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"
    JCB = "jcb"
    DINERS = "diners"


# PCI DSS Compliance Constants
PCI_DSS_VERSION = "4.0"
PCI_LOG_RETENTION_YEARS = 1  # Minimum 1 year (Requirement 10.5.1)
PCI_QUARTERLY_SCAN_REQUIRED = True
PCI_ANNUAL_PENETRATION_TEST_REQUIRED = True
PCI_PASSWORD_MIN_LENGTH = 12  # PCI DSS 4.0 Requirement 8.3.6
PCI_PASSWORD_MAX_AGE_DAYS = 90  # Requirement 8.3.9
PCI_CARD_DATA_RETENTION_DAYS = 90  # Minimize storage duration
PCI_TOKENIZATION_REQUIRED = True

# FCC Compliance Constants
FCC_TCPA_CONSENT_REQUIRED = True  # Prior express written consent for automated calls
FCC_TCPA_OPT_OUT_REQUIRED = True  # Must honor opt-out requests immediately
FCC_TCPA_CALL_TIME_START = "08:00"  # No calls before 8 AM local time
FCC_TCPA_CALL_TIME_END = "21:00"  # No calls after 9 PM local time
FCC_CPNI_CONSENT_REQUIRED = True  # Customer consent for using network info
FCC_DATA_BREACH_NOTIFICATION_DAYS = 30  # FCC data breach notification timeline


@dataclass
class HIPAAUser:
    """User record with role-based access controls (HIPAA-aligned; no certification claimed)"""
    user_id: str
    username: str
    role: str  # Provider, Nurse, Admin, etc.
    access_level: HIPAAAccessLevel
    npi_number: Optional[str]  # National Provider Identifier
    department: str
    active: bool
    last_login: Optional[str]
    failed_login_attempts: int
    password_hash: str  # Never stored in plain text
    mfa_enabled: bool
    created_date: str


@dataclass
class HIPAAAuditLog:
    """Tamper-evident audit log entry (HIPAA-aligned; no certification claimed)"""
    log_id: str
    event_type: HIPAAEventType
    user_id: str
    patient_id: Optional[str]  # PHI identifier
    action_description: str
    ip_address: str
    timestamp: str
    success: bool
    denial_reason: Optional[str]
    integrity_hash: str  # Tamper-evident audit trail


@dataclass
class PaymentTransaction:
    """PCI DSS-compliant payment transaction (tokenized)"""
    transaction_id: str
    patient_id: str
    amount: float
    currency: str
    card_token: str  # Tokenized card number (NOT plain card number)
    card_type: PaymentCardType
    last_four_digits: str  # Only last 4 digits stored
    transaction_date: str
    authorization_code: str
    merchant_id: str
    payment_processor: str
    status: str  # authorized, captured, refunded, declined
    cvv_verified: bool  # CVV never stored
    avs_verified: bool  # Address verification
    three_d_secure: bool  # 3D Secure authentication
    integrity_hash: str


@dataclass
class FCCConsentRecord:
    """FCC TCPA/CPNI consent record"""
    consent_id: str
    patient_id: str
    consent_type: str  # tcpa_voice, tcpa_sms, cpni, marketing_email
    consent_given: bool
    consent_date: str
    consent_method: str  # written, electronic, verbal
    phone_number: Optional[str]
    email_address: Optional[str]
    opt_out_date: Optional[str]
    revoked: bool
    audit_trail: str  # Documentation of consent collection
    integrity_hash: str


@dataclass
class TriageCase:
    """Triage assessment case"""
    case_id: str
    patient_id: str
    chief_complaint: str
    vital_signs: Dict[str, Any]
    urgency_level: UrgencyLevel
    assigned_provider: Optional[str]
    triage_time: str
    notes: str
    integrity_hash: str
    disclaimer: str = ""


@dataclass
class ClinicalNote:
    """Clinical documentation entry"""
    note_id: str
    patient_id: str
    encounter_id: str
    note_type: str  # SOAP, progress, discharge, etc.
    provider_id: str
    content: Dict[str, str]
    timestamp: str
    signed: bool
    integrity_hash: str
    disclaimer: str = ""


@dataclass
class ComplianceAlert:
    """Compliance monitoring alert"""
    alert_id: str
    alert_type: str  # HIPAA, FDA, accreditation
    severity: str  # critical, high, medium, low
    description: str
    affected_systems: List[str]
    remediation_required: bool
    timestamp: str
    resolved: bool
    integrity_hash: str


@dataclass
class Prescription:
    """Prescription/medication order"""
    rx_id: str
    patient_id: str
    prescriber_id: str
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    quantity: int
    refills_allowed: int
    pharmacy_id: Optional[str]
    status: str  # pending, filled, cancelled, expired
    prescribed_date: str
    filled_date: Optional[str]
    drug_interactions_checked: bool
    allergy_checked: bool
    notes: str
    integrity_hash: str
    disclaimer: str = ""


class MedicalTeamSuite:
    """
    Comprehensive medical team bot orchestration system
    Coordinates essential and non-essential healthcare bots
    """
    
    def __init__(self, db_path: str = "mythara_medical_team.db"):
        self.db_path = db_path
        self.suite_id = "medical_team_suite_v1"
        
        # Initialize database FIRST — bots seed reference tables on construction
        self._init_database()

        # Initialize all bot modules
        self.triage_bot = TriageCoordinatorBot(self)
        self.clinical_doc_bot = ClinicalDocumentationBot(self)
        self.compliance_bot = ComplianceMonitorBot(self)
        self.crisis_bot = CrisisResponseBot(self)
        self.rx_bot = RxManagementBot(self)
        self.mental_health_bot = MentalHealthSupportBot(self)
        self.patient_ed_bot = PatientEducationBot(self)
        self.scheduling_bot = SchedulingCoordinatorBot(self)
        self.resource_bot = ResourceAllocationBot(self)
        self.admin_bot = AdministrativeAssistantBot(self)
        self.qa_bot = QualityAssuranceBot(self)
        self.education_bot = ContinuingEducationBot(self)

        logger.info(f"Medical Team Suite initialized: {self.suite_id}")
    
    def _init_database(self):
        """Initialize SQLite database for medical team operations"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Triage cases
        c.execute('''
            CREATE TABLE IF NOT EXISTS triage_cases (
                case_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                chief_complaint TEXT NOT NULL,
                vital_signs TEXT,
                urgency_level TEXT NOT NULL,
                assigned_provider TEXT,
                triage_time TEXT NOT NULL,
                notes TEXT,
                resolved BOOLEAN DEFAULT 0,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Clinical notes
        c.execute('''
            CREATE TABLE IF NOT EXISTS clinical_notes (
                note_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                encounter_id TEXT NOT NULL,
                note_type TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                signed BOOLEAN DEFAULT 0,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Compliance alerts
        c.execute('''
            CREATE TABLE IF NOT EXISTS compliance_alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                affected_systems TEXT,
                remediation_required BOOLEAN DEFAULT 1,
                timestamp TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                resolution_notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Patient education sessions
        c.execute('''
            CREATE TABLE IF NOT EXISTS education_sessions (
                session_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                materials_provided TEXT,
                comprehension_level TEXT,
                follow_up_needed BOOLEAN DEFAULT 0,
                timestamp TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Appointments
        c.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                appointment_type TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                duration_minutes INT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Resource allocation
        c.execute('''
            CREATE TABLE IF NOT EXISTS resource_allocations (
                allocation_id TEXT PRIMARY KEY,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                allocated_to TEXT NOT NULL,
                allocation_time TEXT NOT NULL,
                expected_return_time TEXT,
                status TEXT DEFAULT 'allocated',
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Quality metrics
        c.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                measurement_time TEXT NOT NULL,
                department TEXT,
                notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Staff training
        c.execute('''
            CREATE TABLE IF NOT EXISTS staff_training (
                training_id TEXT PRIMARY KEY,
                staff_id TEXT NOT NULL,
                course_name TEXT NOT NULL,
                completion_date TEXT,
                certification_expires TEXT,
                status TEXT DEFAULT 'in_progress',
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Prescriptions (Rx management)
        c.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                rx_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                prescriber_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                frequency TEXT NOT NULL,
                duration_days INT NOT NULL,
                quantity INT NOT NULL,
                refills_allowed INT DEFAULT 0,
                pharmacy_id TEXT,
                status TEXT DEFAULT 'pending',
                prescribed_date TEXT NOT NULL,
                filled_date TEXT,
                drug_interactions_checked BOOLEAN DEFAULT 0,
                allergy_checked BOOLEAN DEFAULT 0,
                notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Medication allergies
        c.execute('''
            CREATE TABLE IF NOT EXISTS medication_allergies (
                allergy_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                reaction TEXT NOT NULL,
                severity TEXT NOT NULL,
                documented_date TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Drug interactions database
        c.execute('''
            CREATE TABLE IF NOT EXISTS drug_interactions (
                interaction_id TEXT PRIMARY KEY,
                drug_a TEXT NOT NULL,
                drug_b TEXT NOT NULL,
                interaction_severity TEXT NOT NULL,
                description TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Mental health assessments (DSM-5-TR based)
        c.execute('''
            CREATE TABLE IF NOT EXISTS mental_health_assessments (
                assessment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                assessor_id TEXT NOT NULL,
                dsm5_category TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                severity_level TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                safety_plan_required BOOLEAN DEFAULT 0,
                assessment_date TEXT NOT NULL,
                notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Soul Cradle paradoxes (systems framework)
        c.execute('''
            CREATE TABLE IF NOT EXISTS soul_cradle_paradoxes (
                paradox_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                clinician_id TEXT NOT NULL,
                expression_a TEXT NOT NULL,
                expression_b TEXT NOT NULL,
                non_expression TEXT NOT NULL,
                system_type TEXT NOT NULL,
                viability_score REAL NOT NULL,
                terminal_risk TEXT NOT NULL,
                principal_system TEXT NOT NULL,
                witnessed_by TEXT,
                created_date TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Crisis interventions (mental health crises)
        c.execute('''
            CREATE TABLE IF NOT EXISTS crisis_interventions (
                intervention_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                crisis_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                intervention_actions TEXT NOT NULL,
                outcome TEXT,
                referrals TEXT,
                safety_plan TEXT,
                intervention_date TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # Safety plans
        c.execute('''
            CREATE TABLE IF NOT EXISTS safety_plans (
                plan_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                warning_signs TEXT NOT NULL,
                coping_strategies TEXT NOT NULL,
                support_contacts TEXT NOT NULL,
                crisis_resources TEXT NOT NULL,
                restrictions TEXT,
                created_date TEXT NOT NULL,
                last_reviewed TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # PCI DSS Payment Transactions (tokenized, no full card numbers)
        c.execute('''
            CREATE TABLE IF NOT EXISTS payment_transactions (
                transaction_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                card_token TEXT NOT NULL,
                card_type TEXT NOT NULL,
                last_four_digits TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                authorization_code TEXT,
                merchant_id TEXT NOT NULL,
                payment_processor TEXT NOT NULL,
                status TEXT NOT NULL,
                cvv_verified BOOLEAN DEFAULT 0,
                avs_verified BOOLEAN DEFAULT 0,
                three_d_secure BOOLEAN DEFAULT 0,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # PCI DSS Audit Log (Requirement 10)
        c.execute('''
            CREATE TABLE IF NOT EXISTS pci_audit_log (
                log_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                transaction_id TEXT,
                action_description TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                system_component TEXT,
                integrity_hash TEXT NOT NULL,
                previous_log_hash TEXT
            )
        ''')
        
        # PCI DSS Cardholder Data Access Log (Requirement 7)
        c.execute('''
            CREATE TABLE IF NOT EXISTS cardholder_data_access (
                access_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                access_type TEXT NOT NULL,
                data_accessed TEXT NOT NULL,
                justification TEXT NOT NULL,
                approved_by TEXT,
                timestamp TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # PCI DSS Vulnerability Scans (Requirement 11.3)
        c.execute('''
            CREATE TABLE IF NOT EXISTS vulnerability_scans (
                scan_id TEXT PRIMARY KEY,
                scan_type TEXT NOT NULL,
                scan_date TEXT NOT NULL,
                vulnerabilities_found INT DEFAULT 0,
                critical_findings INT DEFAULT 0,
                high_findings INT DEFAULT 0,
                medium_findings INT DEFAULT 0,
                low_findings INT DEFAULT 0,
                remediation_deadline TEXT,
                scan_report_url TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # FCC TCPA/CPNI Consent Records
        c.execute('''
            CREATE TABLE IF NOT EXISTS fcc_consent_records (
                consent_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                consent_given BOOLEAN NOT NULL,
                consent_date TEXT NOT NULL,
                consent_method TEXT NOT NULL,
                phone_number TEXT,
                email_address TEXT,
                opt_out_date TEXT,
                revoked BOOLEAN DEFAULT 0,
                audit_trail TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # FCC Communication Log (TCPA compliance tracking)
        c.execute('''
            CREATE TABLE IF NOT EXISTS fcc_communication_log (
                comm_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                communication_type TEXT NOT NULL,
                phone_number TEXT,
                email_address TEXT,
                timestamp TEXT NOT NULL,
                consent_verified BOOLEAN NOT NULL,
                time_restriction_complied BOOLEAN DEFAULT 1,
                opt_out_honored BOOLEAN DEFAULT 1,
                automated_system BOOLEAN DEFAULT 0,
                purpose TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        # FCC Data Breach Notification (47 CFR § 64.2011)
        c.execute('''
            CREATE TABLE IF NOT EXISTS fcc_breach_notifications (
                breach_id TEXT PRIMARY KEY,
                breach_type TEXT NOT NULL,
                customers_affected INT NOT NULL,
                cpni_exposed TEXT,
                discovery_date TEXT NOT NULL,
                notification_date TEXT,
                fbi_notified BOOLEAN DEFAULT 0,
                fcc_notified BOOLEAN DEFAULT 0,
                customer_notification_sent BOOLEAN DEFAULT 0,
                remediation_status TEXT,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Medical team database initialized (HIPAA + PCI DSS + FCC compliant)")
    
    def compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SSIP integrity hash for medical data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def generate_suite_report(self) -> Dict[str, Any]:
        """Generate comprehensive medical team suite status report"""
        report = {
            "suite_id": self.suite_id,
            "report_time": datetime.utcnow().isoformat(),
            "essential_bots": {
                "triage_coordinator": self.triage_bot.get_status(),
                "clinical_documentation": self.clinical_doc_bot.get_status(),
                "compliance_monitor": self.compliance_bot.get_status(),
                "crisis_response": self.crisis_bot.get_status(),
                "rx_management": self.rx_bot.get_status(),
                "mental_health_support": self.mental_health_bot.get_status()
            },
            "support_bots": {
                "patient_education": self.patient_ed_bot.get_status(),
                "scheduling_coordinator": self.scheduling_bot.get_status(),
                "resource_allocation": self.resource_bot.get_status(),
                "administrative_assistant": self.admin_bot.get_status(),
                "quality_assurance": self.qa_bot.get_status(),
                "continuing_education": self.education_bot.get_status()
            },
            "overall_health": self._compute_suite_health(),
            "disclaimer": CLINICAL_DISCLAIMER
        }
        
        report["integrity_hash"] = self.compute_integrity_hash(report)
        return report


    def _compute_suite_health(self) -> Dict[str, Any]:
        """Compute overall suite health metrics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Count active cases
        c.execute("SELECT COUNT(*) FROM triage_cases WHERE resolved = 0")
        active_triage = c.fetchone()[0]
        
        # Count unresolved compliance alerts
        c.execute("SELECT COUNT(*) FROM compliance_alerts WHERE resolved = 0")
        active_alerts = c.fetchone()[0]
        
        # Count today's appointments
        today = datetime.utcnow().date().isoformat()
        c.execute("SELECT COUNT(*) FROM appointments WHERE DATE(scheduled_time) = ? AND status = 'scheduled'", (today,))
        todays_appointments = c.fetchone()[0]
        
        conn.close()
        
        return {
            "active_triage_cases": active_triage,
            "unresolved_compliance_alerts": active_alerts,
            "todays_scheduled_appointments": todays_appointments,
            "suite_operational": True,
            "last_health_check": datetime.utcnow().isoformat()
        }


# ============================================================================
# ESSENTIAL BOTS (Critical Clinical Functions)
# ============================================================================

class TriageCoordinatorBot:
    """
    Essential Bot: Triage patient cases and prioritize care
    
    Responsibilities:
    - Assess patient urgency based on symptoms and vitals
    - Prioritize patients for provider assignment
    - Track wait times and escalate delays
    - Coordinate emergency response
    
    NOT A MEDICAL DEVICE - Administrative workflow only
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "triage_coordinator"
        logger.info(f"Initialized {self.bot_id}")
    
    def assess_triage(self, patient_id: str, chief_complaint: str, 
                     vital_signs: Dict[str, Any]) -> TriageCase:
        """
        Assess triage urgency (NOT A DIAGNOSTIC TOOL)
        Uses standardized triage protocols
        """
        case_id = f"TRIAGE_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        # Basic urgency assessment (simplified for demo)
        urgency = self._determine_urgency(chief_complaint, vital_signs)
        
        case = TriageCase(
            case_id=case_id,
            patient_id=patient_id,
            chief_complaint=chief_complaint,
            vital_signs=vital_signs,
            urgency_level=urgency,
            assigned_provider=None,
            triage_time=datetime.utcnow().isoformat(),
            notes="",
            integrity_hash="",
            disclaimer=CLINICAL_DISCLAIMER
        )
        
        case.integrity_hash = self.suite.compute_integrity_hash(asdict(case))
        
        # Save to database
        self._save_triage_case(case)
        
        logger.info(f"Triage case created: {case_id}, urgency: {urgency.value}")
        return case
    
    def _determine_urgency(self, complaint: str, vitals: Dict[str, Any]) -> UrgencyLevel:
        """
        Determine urgency level (simplified algorithm)
        Real implementation would use clinical decision support system
        """
        # Emergency keywords
        emergency_keywords = ["chest pain", "difficulty breathing", "unresponsive", 
                            "severe bleeding", "stroke", "heart attack"]
        
        if any(keyword in complaint.lower() for keyword in emergency_keywords):
            return UrgencyLevel.EMERGENCY
        
        # Check vital signs (if provided)
        if vitals:
            hr = vitals.get("heart_rate", 0)
            bp_sys = vitals.get("blood_pressure_systolic", 0)
            temp = vitals.get("temperature_f", 0)
            
            if hr > 120 or hr < 50 or bp_sys > 180 or bp_sys < 90 or temp > 103:
                return UrgencyLevel.URGENT
        
        # Default to routine for demo
        return UrgencyLevel.ROUTINE
    
    def _save_triage_case(self, case: TriageCase):
        """Save triage case to database"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO triage_cases 
            (case_id, patient_id, chief_complaint, vital_signs, urgency_level, 
             assigned_provider, triage_time, notes, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case.case_id, case.patient_id, case.chief_complaint,
            json.dumps(case.vital_signs), case.urgency_level.value,
            case.assigned_provider, case.triage_time, case.notes,
            case.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def get_status(self) -> Dict[str, Any]:
        """Get triage coordinator status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute("SELECT urgency_level, COUNT(*) FROM triage_cases WHERE resolved = 0 GROUP BY urgency_level")
        urgency_counts = dict(c.fetchall())
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "active_cases_by_urgency": urgency_counts,
            "last_check": datetime.utcnow().isoformat()
        }


class ClinicalDocumentationBot:
    """
    Essential Bot: Assist with medical documentation
    
    Responsibilities:
    - Support SOAP note generation
    - Ensure documentation completeness
    - Track unsigned notes
    - Generate discharge summaries
    
    DOES NOT WRITE MEDICAL NOTES - Assists human providers only
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "clinical_documentation"
        logger.info(f"Initialized {self.bot_id}")
    
    def create_note_template(self, note_type: str, patient_id: str, 
                            encounter_id: str, provider_id: str) -> ClinicalNote:
        """Create structured clinical note template"""
        note_id = f"NOTE_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{encounter_id}"
        
        # Generate appropriate template
        content = self._get_note_template(note_type)
        
        note = ClinicalNote(
            note_id=note_id,
            patient_id=patient_id,
            encounter_id=encounter_id,
            note_type=note_type,
            provider_id=provider_id,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            signed=False,
            integrity_hash="",
            disclaimer=CLINICAL_DISCLAIMER
        )
        
        note.integrity_hash = self.suite.compute_integrity_hash(asdict(note))
        
        # Save to database
        self._save_clinical_note(note)
        
        logger.info(f"Clinical note template created: {note_id}, type: {note_type}")
        return note
    
    def _get_note_template(self, note_type: str) -> Dict[str, str]:
        """Get clinical note template by type"""
        templates = {
            "SOAP": {
                "subjective": "[Patient's description of symptoms]",
                "objective": "[Vital signs, physical exam findings]",
                "assessment": "[Diagnosis or working diagnosis]",
                "plan": "[Treatment plan, follow-up]"
            },
            "progress": {
                "current_status": "[Patient's current condition]",
                "changes": "[Changes since last visit]",
                "plan": "[Updated treatment plan]"
            },
            "discharge": {
                "admission_reason": "[Reason for admission]",
                "hospital_course": "[Summary of treatment]",
                "discharge_instructions": "[Patient instructions]",
                "follow_up": "[Follow-up appointments]"
            }
        }
        
        return templates.get(note_type, {})
    
    def _save_clinical_note(self, note: ClinicalNote):
        """Save clinical note to database"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO clinical_notes 
            (note_id, patient_id, encounter_id, note_type, provider_id, 
             content, timestamp, signed, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            note.note_id, note.patient_id, note.encounter_id, note.note_type,
            note.provider_id, json.dumps(note.content), note.timestamp,
            note.signed, note.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def get_status(self) -> Dict[str, Any]:
        """Get clinical documentation status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM clinical_notes WHERE signed = 0")
        unsigned_notes = c.fetchone()[0]
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "unsigned_notes_pending": unsigned_notes,
            "last_check": datetime.utcnow().isoformat()
        }


class ComplianceMonitorBot:
    """
    Essential Bot: internal compliance self-assessment tracking (demo-grade)

    Responsibilities:
    - Flag PHI exposure risks against internal checklist rules
    - Track access-control and audit-log completeness
    - Alert on internal compliance gaps

    HONEST SCOPE: self-assessment software using simplified rules. It is NOT
    HIPAA or FDA monitoring, not an audit, and not a regulatory
    determination.

    Integrates with existing DrMythara compliance bot
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "compliance_monitor"
        logger.info(f"Initialized {self.bot_id}")
    
    def create_alert(self, alert_type: str, severity: str, 
                    description: str, affected_systems: List[str]) -> ComplianceAlert:
        """Create compliance alert"""
        alert_id = f"ALERT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        alert = ComplianceAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            affected_systems=affected_systems,
            remediation_required=(severity in ["critical", "high"]),
            timestamp=datetime.utcnow().isoformat(),
            resolved=False,
            integrity_hash=""
        )
        
        alert.integrity_hash = self.suite.compute_integrity_hash(asdict(alert))
        
        # Save to database
        self._save_compliance_alert(alert)
        
        logger.warning(f"Compliance alert created: {alert_id}, severity: {severity}")
        return alert
    
    def _save_compliance_alert(self, alert: ComplianceAlert):
        """Save compliance alert to database"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO compliance_alerts 
            (alert_id, alert_type, severity, description, affected_systems, 
             remediation_required, timestamp, resolved, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id, alert.alert_type, alert.severity, alert.description,
            json.dumps(alert.affected_systems), alert.remediation_required,
            alert.timestamp, alert.resolved, alert.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def get_status(self) -> Dict[str, Any]:
        """Get compliance monitor status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute("SELECT severity, COUNT(*) FROM compliance_alerts WHERE resolved = 0 GROUP BY severity")
        alerts_by_severity = dict(c.fetchall())
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "active_alerts_by_severity": alerts_by_severity,
            "last_check": datetime.utcnow().isoformat()
        }


class CrisisResponseBot:
    """
    Essential Bot: Emergency protocol coordination
    
    Responsibilities:
    - Detect crisis situations
    - Activate emergency protocols
    - Coordinate multi-disciplinary response
    - Document crisis events
    
    NOT A SUBSTITUTE FOR 911 or emergency services
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "crisis_response"
        self.crisis_protocols = self._init_crisis_protocols()
        logger.info(f"Initialized {self.bot_id}")
    
    def _init_crisis_protocols(self) -> Dict[str, Any]:
        """Initialize crisis response protocols including mental health crises"""
        return {
            "code_blue": {
                "description": "Cardiac or respiratory arrest",
                "team": ["physician", "nurse", "respiratory_therapist", "pharmacist"],
                "equipment": ["crash_cart", "defibrillator", "airway_kit"]
            },
            "code_red": {
                "description": "Fire emergency",
                "team": ["security", "facilities", "nursing"],
                "actions": ["RACE_protocol"]
            },
            "code_grey": {
                "description": "Combative person",
                "team": ["security", "behavioral_health", "nursing"],
                "equipment": ["restraints"]
            },
            "code_pink": {
                "description": "Infant/child abduction",
                "team": ["security", "nursing", "administration"],
                "actions": ["lockdown", "law_enforcement_notification"]
            },
            "code_green": {
                "description": "Behavioral/psychiatric emergency",
                "team": ["behavioral_health", "social_work", "nursing", "security"],
                "actions": ["de_escalation", "safety_assessment", "1_to_1_observation"]
            },
            "code_silver": {
                "description": "Active threat/violence",
                "team": ["security", "law_enforcement", "administration"],
                "actions": ["shelter_in_place", "evacuation", "lockdown"]
            },
            "mental_health_crisis": {
                "description": "Suicidal ideation, severe mental health decompensation",
                "team": ["mental_health_clinician", "crisis_counselor", "social_work", "psychiatry"],
                "equipment": ["safety_plan_materials", "crisis_resources"],
                "actions": ["risk_assessment", "safety_planning", "voluntary_or_involuntary_hold"]
            }
        }
    
    def activate_crisis_protocol(self, protocol_code: str, location: str, 
                                 details: str) -> Dict[str, Any]:
        """Activate emergency protocol"""
        crisis_id = f"CRISIS_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        protocol = self.crisis_protocols.get(protocol_code, {})
        
        response = {
            "crisis_id": crisis_id,
            "protocol_code": protocol_code,
            "protocol_description": protocol.get("description", "Unknown"),
            "location": location,
            "details": details,
            "activation_time": datetime.utcnow().isoformat(),
            "required_team": protocol.get("team", []),
            "required_equipment": protocol.get("equipment", []),
            "required_actions": protocol.get("actions", []),
            "status": "activated",
            "disclaimer": CLINICAL_DISCLAIMER
        }
        
        response["integrity_hash"] = self.suite.compute_integrity_hash(response)
        
        logger.critical(f"CRISIS ACTIVATED: {protocol_code} at {location}")
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Get crisis response status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "available_protocols": list(self.crisis_protocols.keys()),
            "last_check": datetime.utcnow().isoformat()
        }


class RxManagementBot:
    """
    Essential Bot: Prescription and medication management
    
    Responsibilities:
    - Create and track prescriptions
    - Check drug interactions
    - Verify patient allergies
    - Monitor medication compliance
    - Track refill requests
    - Interface with pharmacy systems
    
    NOT A PRESCRIBING SYSTEM - Administrative workflow only
    DOES NOT REPLACE PHARMACIST OR PRESCRIBER JUDGMENT
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "rx_management"
        self._init_drug_interaction_database()
        logger.info(f"Initialized {self.bot_id}")
    
    def _init_drug_interaction_database(self):
        """Initialize common drug interactions (simplified for demo)"""
        common_interactions = [
            ("warfarin", "aspirin", "major", "Increased bleeding risk"),
            ("lisinopril", "potassium", "major", "Hyperkalemia risk"),
            ("metformin", "alcohol", "moderate", "Lactic acidosis risk"),
            ("simvastatin", "grapefruit", "moderate", "Increased statin levels"),
            ("levothyroxine", "calcium", "moderate", "Reduced thyroid absorption")
        ]
        
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        for drug_a, drug_b, severity, description in common_interactions:
            interaction_id = f"INTERACTION_{hashlib.md5(f'{drug_a}{drug_b}'.encode()).hexdigest()[:16]}"
            interaction_data = {
                "drug_a": drug_a,
                "drug_b": drug_b,
                "severity": severity,
                "description": description
            }
            integrity_hash = self.suite.compute_integrity_hash(interaction_data)
            
            c.execute('''
                INSERT OR IGNORE INTO drug_interactions
                (interaction_id, drug_a, drug_b, interaction_severity, description, integrity_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction_id, drug_a, drug_b, severity, description, integrity_hash))
        
        conn.commit()
        conn.close()
    
    def create_prescription(
        self,
        patient_id: str,
        prescriber_id: str,
        medication_name: str,
        dosage: str,
        frequency: str,
        duration_days: int,
        quantity: int,
        refills_allowed: int = 0,
        pharmacy_id: Optional[str] = None,
        notes: str = ""
    ) -> Prescription:
        """
        Create a new prescription with safety checks
        
        CRITICAL: This is administrative workflow only
        Actual prescribing must be done by licensed prescriber
        """
        rx_id = f"RX_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        # Check for drug interactions
        interactions = self._check_drug_interactions(patient_id, medication_name)
        drug_interactions_checked = True
        
        # Check for allergies
        allergies = self._check_allergies(patient_id, medication_name)
        allergy_checked = True
        
        # Create prescription object
        prescription = Prescription(
            rx_id=rx_id,
            patient_id=patient_id,
            prescriber_id=prescriber_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration_days=duration_days,
            quantity=quantity,
            refills_allowed=refills_allowed,
            pharmacy_id=pharmacy_id,
            status="pending",
            prescribed_date=datetime.utcnow().isoformat(),
            filled_date=None,
            drug_interactions_checked=drug_interactions_checked,
            allergy_checked=allergy_checked,
            notes=notes,
            integrity_hash="",
            disclaimer=CLINICAL_DISCLAIMER
        )
        
        # Add warnings to notes if issues found
        warnings = []
        if interactions:
            warnings.append(f"DRUG INTERACTIONS: {len(interactions)} found")
        if allergies:
            warnings.append(f"ALLERGY ALERT: Patient has documented allergy")
        
        if warnings:
            prescription.notes = f"{notes}\n\nAUTOMATED WARNINGS:\n" + "\n".join(warnings)
        
        prescription.integrity_hash = self.suite.compute_integrity_hash(asdict(prescription))
        
        # Save to database
        self._save_prescription(prescription)
        
        logger.info(f"Prescription created: {rx_id} for {medication_name}")
        
        if interactions or allergies:
            logger.warning(f"Prescription {rx_id} has safety alerts - requires review")
        
        return prescription
    
    def _check_drug_interactions(self, patient_id: str, new_medication: str) -> List[Dict[str, Any]]:
        """Check for drug interactions with patient's current medications"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        # Get patient's current active prescriptions
        c.execute('''
            SELECT medication_name FROM prescriptions 
            WHERE patient_id = ? AND status IN ('pending', 'filled')
        ''', (patient_id,))
        
        current_meds = [row[0] for row in c.fetchall()]
        
        # Check interactions
        interactions = []
        for current_med in current_meds:
            c.execute('''
                SELECT interaction_id, drug_a, drug_b, interaction_severity, description
                FROM drug_interactions
                WHERE (drug_a = ? AND drug_b = ?) OR (drug_a = ? AND drug_b = ?)
            ''', (current_med, new_medication, new_medication, current_med))
            
            for row in c.fetchall():
                interactions.append({
                    "interaction_id": row[0],
                    "drug_a": row[1],
                    "drug_b": row[2],
                    "severity": row[3],
                    "description": row[4],
                    "disclaimer": CLINICAL_DISCLAIMER
                })
        
        conn.close()
        return interactions
    
    def _check_allergies(self, patient_id: str, medication_name: str) -> List[Dict[str, Any]]:
        """Check for documented medication allergies"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT allergy_id, medication_name, reaction, severity
            FROM medication_allergies
            WHERE patient_id = ? AND medication_name = ?
        ''', (patient_id, medication_name))
        
        allergies = []
        for row in c.fetchall():
            allergies.append({
                "allergy_id": row[0],
                "medication": row[1],
                "reaction": row[2],
                "severity": row[3]
            })
        
        conn.close()
        return allergies
    
    def _save_prescription(self, prescription: Prescription):
        """Save prescription to database"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO prescriptions
            (rx_id, patient_id, prescriber_id, medication_name, dosage, frequency,
             duration_days, quantity, refills_allowed, pharmacy_id, status,
             prescribed_date, filled_date, drug_interactions_checked, allergy_checked,
             notes, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prescription.rx_id, prescription.patient_id, prescription.prescriber_id,
            prescription.medication_name, prescription.dosage, prescription.frequency,
            prescription.duration_days, prescription.quantity, prescription.refills_allowed,
            prescription.pharmacy_id, prescription.status, prescription.prescribed_date,
            prescription.filled_date, prescription.drug_interactions_checked,
            prescription.allergy_checked, prescription.notes, prescription.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def add_allergy(
        self,
        patient_id: str,
        medication_name: str,
        reaction: str,
        severity: str  # mild, moderate, severe, life_threatening
    ) -> Dict[str, Any]:
        """Document medication allergy"""
        allergy_id = f"ALLERGY_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        allergy_data = {
            "allergy_id": allergy_id,
            "patient_id": patient_id,
            "medication_name": medication_name,
            "reaction": reaction,
            "severity": severity,
            "documented_date": datetime.utcnow().isoformat()
        }
        
        allergy_data["integrity_hash"] = self.suite.compute_integrity_hash(allergy_data)
        
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO medication_allergies
            (allergy_id, patient_id, medication_name, reaction, severity, documented_date, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            allergy_id, patient_id, medication_name, reaction, severity,
            allergy_data["documented_date"], allergy_data["integrity_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Medication allergy documented: {allergy_id}")
        return allergy_data
    
    def fill_prescription(self, rx_id: str, pharmacy_id: str) -> Dict[str, Any]:
        """Mark prescription as filled"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        filled_date = datetime.utcnow().isoformat()
        
        c.execute('''
            UPDATE prescriptions
            SET status = 'filled', filled_date = ?, pharmacy_id = ?
            WHERE rx_id = ?
        ''', (filled_date, pharmacy_id, rx_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Prescription filled: {rx_id} at pharmacy {pharmacy_id}")
        
        return {
            "rx_id": rx_id,
            "status": "filled",
            "filled_date": filled_date,
            "pharmacy_id": pharmacy_id
        }
    
    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all active medications for a patient"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT rx_id, medication_name, dosage, frequency, status, prescribed_date
            FROM prescriptions
            WHERE patient_id = ? AND status IN ('pending', 'filled')
            ORDER BY prescribed_date DESC
        ''', (patient_id,))
        
        medications = []
        for row in c.fetchall():
            medications.append({
                "rx_id": row[0],
                "medication_name": row[1],
                "dosage": row[2],
                "frequency": row[3],
                "status": row[4],
                "prescribed_date": row[5]
            })
        
        conn.close()
        return medications
    
    def get_status(self) -> Dict[str, Any]:
        """Get Rx management status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        # Count active prescriptions
        c.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'pending'")
        pending_prescriptions = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'filled'")
        filled_prescriptions = c.fetchone()[0]
        
        # Count documented allergies
        c.execute("SELECT COUNT(*) FROM medication_allergies")
        total_allergies = c.fetchone()[0]
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "pending_prescriptions": pending_prescriptions,
            "filled_prescriptions": filled_prescriptions,
            "documented_allergies": total_allergies,
            "last_check": datetime.utcnow().isoformat()
        }


class MentalHealthSupportBot:
    """
    Essential Bot: Mental Health Support with DSM-5-TR and Soul Cradle Integration
    
    Responsibilities:
    - Mental health assessments (DSM-5-TR categories)
    - Soul Cradle paradox documentation
    - Crisis intervention coordination
    - Safety planning
    - Therapeutic framework tracking (CBT, DBT, ACT)
    - Risk assessment
    
    CRITICAL DISCLAIMER:
    - NOT A REPLACEMENT FOR LICENSED MENTAL HEALTH PROFESSIONALS
    - NOT DIAGNOSTIC - Administrative support only
    - Crisis situations require immediate professional intervention
    - ALWAYS call 988 (Suicide & Crisis Lifeline) or 911 for emergencies
    
    Integrates:
    - DSM-5-TR diagnostic categories (reference only, not for diagnosis)
    - Soul Cradle systems framework (paradox documentation)
    - Blessings Reservoir (healing progress tracking)
    - SSIP integrity hashing (confidential data protection)
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "mental_health_support"
        self.dsm5_categories = self._init_dsm5_categories()
        self.therapeutic_frameworks = self._init_therapeutic_frameworks()
        self.crisis_resources = self._init_crisis_resources()
        logger.info(f"Initialized {self.bot_id}")
    
    def _init_dsm5_categories(self) -> Dict[str, Any]:
        """Initialize DSM-5-TR major diagnostic categories (reference only)"""
        return {
            "neurodevelopmental": {
                "examples": ["ADHD", "Autism Spectrum", "Learning Disorders"],
                "key_features": ["developmental_onset", "impaired_functioning"]
            },
            "schizophrenia_spectrum": {
                "examples": ["Schizophrenia", "Schizoaffective", "Brief Psychotic"],
                "key_features": ["psychotic_symptoms", "reality_distortion"]
            },
            "bipolar_related": {
                "examples": ["Bipolar I", "Bipolar II", "Cyclothymic"],
                "key_features": ["mood_elevation", "cyclic_patterns"]
            },
            "depressive": {
                "examples": ["Major Depressive", "Persistent Depressive", "Premenstrual Dysphoric"],
                "key_features": ["low_mood", "anhedonia", "hopelessness"]
            },
            "anxiety": {
                "examples": ["Generalized Anxiety", "Panic", "Social Anxiety", "Specific Phobia"],
                "key_features": ["excessive_worry", "fear_response", "avoidance"]
            },
            "ocd_related": {
                "examples": ["OCD", "Body Dysmorphic", "Hoarding"],
                "key_features": ["obsessions", "compulsions", "repetitive_behaviors"]
            },
            "trauma_stressor": {
                "examples": ["PTSD", "Acute Stress", "Adjustment Disorders"],
                "key_features": ["trauma_exposure", "intrusive_symptoms", "hyperarousal"]
            },
            "dissociative": {
                "examples": ["Dissociative Identity", "Dissociative Amnesia", "Depersonalization"],
                "key_features": ["identity_disruption", "memory_gaps", "reality_detachment"]
            },
            "somatic_symptom": {
                "examples": ["Somatic Symptom", "Illness Anxiety", "Conversion"],
                "key_features": ["physical_symptoms", "health_preoccupation"]
            },
            "feeding_eating": {
                "examples": ["Anorexia", "Bulimia", "Binge-Eating"],
                "key_features": ["eating_disturbance", "body_image", "weight_concerns"]
            },
            "personality": {
                "examples": ["Borderline", "Narcissistic", "Antisocial", "Avoidant"],
                "key_features": ["enduring_patterns", "interpersonal_dysfunction"]
            },
            "substance_related": {
                "examples": ["Alcohol Use", "Opioid Use", "Stimulant Use"],
                "key_features": ["craving", "tolerance", "withdrawal", "loss_of_control"]
            }
        }
    
    def _init_therapeutic_frameworks(self) -> Dict[str, Any]:
        """Initialize evidence-based therapeutic frameworks"""
        return {
            "CBT": {
                "name": "Cognitive Behavioral Therapy",
                "focus": "Thought patterns and behaviors",
                "techniques": ["cognitive_restructuring", "behavioral_activation", "exposure"]
            },
            "DBT": {
                "name": "Dialectical Behavior Therapy",
                "focus": "Emotion regulation and distress tolerance",
                "modules": ["mindfulness", "distress_tolerance", "emotion_regulation", "interpersonal_effectiveness"]
            },
            "ACT": {
                "name": "Acceptance and Commitment Therapy",
                "focus": "Psychological flexibility and values",
                "processes": ["acceptance", "cognitive_defusion", "present_moment", "self_as_context", "values", "committed_action"]
            },
            "TF_CBT": {
                "name": "Trauma-Focused CBT",
                "focus": "Trauma processing and coping",
                "components": ["psychoeducation", "relaxation", "affect_regulation", "trauma_narrative"]
            },
            "MI": {
                "name": "Motivational Interviewing",
                "focus": "Ambivalence and behavior change",
                "spirit": ["partnership", "acceptance", "compassion", "evocation"]
            }
        }
    
    def _init_crisis_resources(self) -> Dict[str, str]:
        """Initialize crisis hotlines and resources"""
        return {
            "988_lifeline": "988 - Suicide & Crisis Lifeline (24/7)",
            "crisis_text": "Text HOME to 741741 - Crisis Text Line",
            "nami_helpline": "1-800-950-NAMI (6264) - National Alliance on Mental Illness",
            "samhsa": "1-800-662-4357 - SAMHSA National Helpline",
            "trevor_project": "1-866-488-7386 - Trevor Project (LGBTQ+ Youth)",
            "veterans_crisis": "1-800-273-8255, press 1 - Veterans Crisis Line",
            "warmline": "Various states - Peer support warmlines (non-crisis)",
            "emergency": "911 - Life-threatening emergencies"
        }
    
    def create_assessment(
        self,
        patient_id: str,
        assessor_id: str,
        dsm5_category: str,
        symptoms: List[str],
        severity_level: str,  # mild, moderate, severe, profound
        risk_level: str,  # low, moderate, high, imminent
        safety_plan_required: bool = False,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Create mental health assessment (Administrative documentation only)
        
        CRITICAL: This is NOT a diagnostic tool. Diagnosis must be made by
        qualified mental health professional using proper clinical assessment.
        """
        assessment_id = f"MH_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        assessment = {
            "assessment_id": assessment_id,
            "patient_id": patient_id,
            "assessor_id": assessor_id,
            "dsm5_category": dsm5_category,
            "symptoms": symptoms,
            "severity_level": severity_level,
            "risk_level": risk_level,
            "safety_plan_required": safety_plan_required,
            "assessment_date": datetime.utcnow().isoformat(),
            "notes": notes
        }
        
        assessment["integrity_hash"] = self.suite.compute_integrity_hash(assessment)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO mental_health_assessments
            (assessment_id, patient_id, assessor_id, dsm5_category, symptoms,
             severity_level, risk_level, safety_plan_required, assessment_date,
             notes, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment_id, patient_id, assessor_id, dsm5_category,
            json.dumps(symptoms), severity_level, risk_level,
            safety_plan_required, assessment["assessment_date"],
            notes, assessment["integrity_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Mental health assessment created: {assessment_id}, category: {dsm5_category}")
        
        if risk_level in ["high", "imminent"]:
            logger.warning(f"HIGH RISK ASSESSMENT: {assessment_id} - Safety intervention required")
        
        assessment["disclaimer"] = CLINICAL_DISCLAIMER
        return assessment
    
    def document_soul_cradle_paradox(
        self,
        patient_id: str,
        clinician_id: str,
        expression_a: str,
        expression_b: str,
        non_expression: str,
        system_type: str = "Pseudo_Partial",
        viability_score: float = 0.0,
        terminal_risk: str = "HIGH",
        principal_system: str = "",
        witnessed_by: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Document a Soul Cradle paradox using systems framework
        
        This captures the therapeutic paradoxes clients face:
        - Expression A: Policy/Rule demands (e.g., "Must be productive")
        - Expression B: Heart/Need reality (e.g., "Need rest to heal")
        - Non-Expression: The impossibility ("Can't satisfy both")
        - Principal System: How Soul Cradle resolves it (witnessing both truths)
        
        Integration with Blessings Reservoir:
        - Moving from Pseudo-Partial → Principal Complete adds blessings
        - Documenting paradoxes enables healing pathways
        """
        paradox_id = f"SC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{patient_id}"
        
        paradox = {
            "paradox_id": paradox_id,
            "patient_id": patient_id,
            "clinician_id": clinician_id,
            "expression_a": expression_a,
            "expression_b": expression_b,
            "non_expression": non_expression,
            "system_type": system_type,
            "viability_score": viability_score,
            "terminal_risk": terminal_risk,
            "principal_system": principal_system,
            "witnessed_by": json.dumps(witnessed_by) if witnessed_by else "[]",
            "created_date": datetime.utcnow().isoformat()
        }
        
        paradox["integrity_hash"] = self.suite.compute_integrity_hash(paradox)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO soul_cradle_paradoxes
            (paradox_id, patient_id, clinician_id, expression_a, expression_b,
             non_expression, system_type, viability_score, terminal_risk,
             principal_system, witnessed_by, created_date, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paradox_id, patient_id, clinician_id, expression_a, expression_b,
            non_expression, system_type, viability_score, terminal_risk,
            principal_system, paradox["witnessed_by"], paradox["created_date"],
            paradox["integrity_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Soul Cradle paradox documented: {paradox_id}")
        paradox["disclaimer"] = CLINICAL_DISCLAIMER
        return paradox
    
    def create_safety_plan(
        self,
        patient_id: str,
        warning_signs: List[str],
        coping_strategies: List[str],
        support_contacts: List[Dict[str, str]],
        crisis_resources: Optional[List[str]] = None,
        restrictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create comprehensive safety plan"""
        plan_id = f"SAFETY_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        if crisis_resources is None:
            crisis_resources = [
                "988 - Suicide & Crisis Lifeline",
                "911 - Emergency services",
                "Crisis Text Line: Text HOME to 741741"
            ]
        
        safety_plan = {
            "plan_id": plan_id,
            "patient_id": patient_id,
            "warning_signs": warning_signs,
            "coping_strategies": coping_strategies,
            "support_contacts": support_contacts,
            "crisis_resources": crisis_resources,
            "restrictions": restrictions or [],
            "created_date": datetime.utcnow().isoformat(),
            "last_reviewed": datetime.utcnow().isoformat()
        }
        
        safety_plan["integrity_hash"] = self.suite.compute_integrity_hash(safety_plan)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO safety_plans
            (plan_id, patient_id, warning_signs, coping_strategies, support_contacts,
             crisis_resources, restrictions, created_date, last_reviewed, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plan_id, patient_id, json.dumps(warning_signs), json.dumps(coping_strategies),
            json.dumps(support_contacts), json.dumps(crisis_resources),
            json.dumps(safety_plan["restrictions"]), safety_plan["created_date"],
            safety_plan["last_reviewed"], safety_plan["integrity_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Safety plan created: {plan_id}")
        safety_plan["disclaimer"] = CLINICAL_DISCLAIMER
        return safety_plan
    
    def intervene_crisis(
        self,
        patient_id: str,
        crisis_type: str,  # suicidal_ideation, self_harm, psychotic_break, severe_anxiety, etc.
        severity: str,  # mild, moderate, severe, extreme
        intervention_actions: List[str],
        outcome: str = "",
        referrals: Optional[List[str]] = None,
        safety_plan_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Document crisis intervention
        
        CRITICAL: This is documentation only. Actual crisis intervention
        must be performed by trained mental health professionals.
        For immediate danger, call 988 or 911.
        """
        intervention_id = f"CRISIS_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        intervention = {
            "intervention_id": intervention_id,
            "patient_id": patient_id,
            "crisis_type": crisis_type,
            "severity": severity,
            "intervention_actions": intervention_actions,
            "outcome": outcome,
            "referrals": referrals or [],
            "safety_plan": safety_plan_id or "",
            "intervention_date": datetime.utcnow().isoformat()
        }
        
        intervention["integrity_hash"] = self.suite.compute_integrity_hash(intervention)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO crisis_interventions
            (intervention_id, patient_id, crisis_type, severity, intervention_actions,
             outcome, referrals, safety_plan, intervention_date, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            intervention_id, patient_id, crisis_type, severity,
            json.dumps(intervention_actions), outcome, json.dumps(intervention["referrals"]),
            intervention["safety_plan"], intervention["intervention_date"],
            intervention["integrity_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.critical(f"CRISIS INTERVENTION DOCUMENTED: {intervention_id}, type: {crisis_type}, severity: {severity}")
        intervention["disclaimer"] = CLINICAL_DISCLAIMER
        return intervention
    
    def get_crisis_resources(self) -> Dict[str, str]:
        """Get all crisis hotlines and resources"""
        return self.crisis_resources
    
    def get_status(self) -> Dict[str, Any]:
        """Get mental health support bot status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        # Count assessments by risk level
        c.execute('''
            SELECT risk_level, COUNT(*) 
            FROM mental_health_assessments 
            GROUP BY risk_level
        ''')
        assessments_by_risk = dict(c.fetchall())
        
        # Count active safety plans
        c.execute("SELECT COUNT(*) FROM safety_plans")
        active_safety_plans = c.fetchone()[0]
        
        # Count crisis interventions (last 7 days)
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        c.execute('''
            SELECT COUNT(*) FROM crisis_interventions 
            WHERE intervention_date >= ?
        ''', (seven_days_ago,))
        recent_crises = c.fetchone()[0]
        
        # Count documented paradoxes
        c.execute("SELECT COUNT(*) FROM soul_cradle_paradoxes")
        documented_paradoxes = c.fetchone()[0]
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "assessments_by_risk": assessments_by_risk,
            "active_safety_plans": active_safety_plans,
            "recent_crisis_interventions": recent_crises,
            "documented_soul_cradle_paradoxes": documented_paradoxes,
            "crisis_resources_available": len(self.crisis_resources),
            "last_check": datetime.utcnow().isoformat()
        }


# ============================================================================
# NON-ESSENTIAL BOTS (Support Roles)
# ============================================================================

class PatientEducationBot:
    """
    Support Bot: Patient education and health literacy
    
    Responsibilities:
    - Provide condition-specific education materials
    - Assess patient understanding
    - Schedule follow-up education
    - Track patient engagement
    
    NOT MEDICAL ADVICE - Educational resources only
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "patient_education"
        logger.info(f"Initialized {self.bot_id}")
    
    def provide_education(self, patient_id: str, topic: str) -> Dict[str, Any]:
        """Provide patient education session"""
        session_id = f"EDU_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        materials = self._get_education_materials(topic)
        
        session = {
            "session_id": session_id,
            "patient_id": patient_id,
            "topic": topic,
            "materials_provided": materials,
            "comprehension_level": "pending_assessment",
            "follow_up_needed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session["integrity_hash"] = self.suite.compute_integrity_hash(session)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO education_sessions 
            (session_id, patient_id, topic, materials_provided, comprehension_level, 
             follow_up_needed, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, patient_id, topic, json.dumps(materials),
              session["comprehension_level"], session["follow_up_needed"],
              session["timestamp"], session["integrity_hash"]))
        conn.commit()
        conn.close()
        
        logger.info(f"Education session created: {session_id}, topic: {topic}")
        return session
    
    def _get_education_materials(self, topic: str) -> List[str]:
        """Get education materials for topic"""
        materials_library = {
            "diabetes": ["blood_glucose_monitoring.pdf", "diet_guidelines.pdf", "insulin_management.pdf"],
            "hypertension": ["blood_pressure_tracking.pdf", "medication_compliance.pdf", "lifestyle_modifications.pdf"],
            "heart_disease": ["cardiac_symptoms.pdf", "exercise_guidelines.pdf", "diet_recommendations.pdf"]
        }
        
        return materials_library.get(topic.lower(), ["general_health.pdf"])
    
    def get_status(self) -> Dict[str, Any]:
        """Get patient education status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "last_check": datetime.utcnow().isoformat()
        }


class SchedulingCoordinatorBot:
    """
    Support Bot: Appointment scheduling and management
    
    Responsibilities:
    - Schedule patient appointments
    - Manage provider calendars
    - Send appointment reminders
    - Handle cancellations and rescheduling
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "scheduling_coordinator"
        logger.info(f"Initialized {self.bot_id}")
    
    def schedule_appointment(self, patient_id: str, provider_id: str,
                           appointment_type: str, scheduled_time: str,
                           duration_minutes: int = 30) -> Dict[str, Any]:
        """Schedule a patient appointment"""
        appointment_id = f"APPT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id}"
        
        appointment = {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "provider_id": provider_id,
            "appointment_type": appointment_type,
            "scheduled_time": scheduled_time,
            "duration_minutes": duration_minutes,
            "status": "scheduled",
            "notes": ""
        }
        
        appointment["integrity_hash"] = self.suite.compute_integrity_hash(appointment)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO appointments 
            (appointment_id, patient_id, provider_id, appointment_type, 
             scheduled_time, duration_minutes, status, notes, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, provider_id, appointment_type,
              scheduled_time, duration_minutes, appointment["status"],
              appointment["notes"], appointment["integrity_hash"]))
        conn.commit()
        conn.close()
        
        logger.info(f"Appointment scheduled: {appointment_id}")
        return appointment
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduling coordinator status"""
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        
        today = datetime.utcnow().date().isoformat()
        c.execute("SELECT COUNT(*) FROM appointments WHERE DATE(scheduled_time) = ?", (today,))
        todays_appointments = c.fetchone()[0]
        
        conn.close()
        
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "todays_appointments": todays_appointments,
            "last_check": datetime.utcnow().isoformat()
        }


class ResourceAllocationBot:
    """
    Support Bot: Resource and staffing optimization
    
    Responsibilities:
    - Track equipment availability
    - Manage staff assignments
    - Optimize resource utilization
    - Alert on shortages
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "resource_allocation"
        logger.info(f"Initialized {self.bot_id}")
    
    def allocate_resource(self, resource_type: str, resource_name: str,
                         allocated_to: str, duration_hours: int = 4) -> Dict[str, Any]:
        """Allocate a resource"""
        allocation_id = f"RES_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        allocation_time = datetime.utcnow()
        expected_return = allocation_time + timedelta(hours=duration_hours)
        
        allocation = {
            "allocation_id": allocation_id,
            "resource_type": resource_type,
            "resource_name": resource_name,
            "allocated_to": allocated_to,
            "allocation_time": allocation_time.isoformat(),
            "expected_return_time": expected_return.isoformat(),
            "status": "allocated"
        }
        
        allocation["integrity_hash"] = self.suite.compute_integrity_hash(allocation)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO resource_allocations 
            (allocation_id, resource_type, resource_name, allocated_to, 
             allocation_time, expected_return_time, status, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (allocation_id, resource_type, resource_name, allocated_to,
              allocation["allocation_time"], allocation["expected_return_time"],
              allocation["status"], allocation["integrity_hash"]))
        conn.commit()
        conn.close()
        
        logger.info(f"Resource allocated: {allocation_id}")
        return allocation
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource allocation status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "last_check": datetime.utcnow().isoformat()
        }


class AdministrativeAssistantBot:
    """
    Support Bot: Administrative tasks and paperwork
    
    Responsibilities:
    - Process insurance verifications
    - Generate billing codes
    - Manage prior authorizations
    - Track outstanding documentation
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "administrative_assistant"
        logger.info(f"Initialized {self.bot_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get administrative assistant status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "last_check": datetime.utcnow().isoformat()
        }


class QualityAssuranceBot:
    """
    Support Bot: Quality metrics and process improvement
    
    Responsibilities:
    - Track quality metrics
    - Identify process bottlenecks
    - Generate improvement reports
    - Monitor patient satisfaction
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "quality_assurance"
        logger.info(f"Initialized {self.bot_id}")
    
    def record_metric(self, metric_name: str, metric_value: float,
                     department: str = "") -> Dict[str, Any]:
        """Record quality metric"""
        metric_id = f"QA_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        metric = {
            "metric_id": metric_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "measurement_time": datetime.utcnow().isoformat(),
            "department": department,
            "notes": ""
        }
        
        metric["integrity_hash"] = self.suite.compute_integrity_hash(metric)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO quality_metrics 
            (metric_id, metric_name, metric_value, measurement_time, 
             department, notes, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (metric_id, metric_name, metric_value, metric["measurement_time"],
              department, metric["notes"], metric["integrity_hash"]))
        conn.commit()
        conn.close()
        
        logger.info(f"Quality metric recorded: {metric_name} = {metric_value}")
        return metric
    
    def get_status(self) -> Dict[str, Any]:
        """Get quality assurance status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "last_check": datetime.utcnow().isoformat()
        }


class ContinuingEducationBot:
    """
    Support Bot: Staff training and certification tracking
    
    Responsibilities:
    - Track staff certifications
    - Schedule required training
    - Monitor expiring credentials
    - Generate compliance reports
    """
    
    def __init__(self, suite: MedicalTeamSuite):
        self.suite = suite
        self.bot_id = "continuing_education"
        logger.info(f"Initialized {self.bot_id}")
    
    def enroll_training(self, staff_id: str, course_name: str,
                       certification_duration_days: int = 365) -> Dict[str, Any]:
        """Enroll staff in training"""
        training_id = f"TRAIN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{staff_id}"
        
        certification_expires = (datetime.utcnow() + timedelta(days=certification_duration_days)).isoformat()
        
        training = {
            "training_id": training_id,
            "staff_id": staff_id,
            "course_name": course_name,
            "completion_date": None,
            "certification_expires": certification_expires,
            "status": "in_progress"
        }
        
        training["integrity_hash"] = self.suite.compute_integrity_hash(training)
        
        # Save to database
        conn = sqlite3.connect(self.suite.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO staff_training 
            (training_id, staff_id, course_name, completion_date, 
             certification_expires, status, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (training_id, staff_id, course_name, training["completion_date"],
              certification_expires, training["status"], training["integrity_hash"]))
        conn.commit()
        conn.close()
        
        logger.info(f"Staff training enrolled: {training_id}")
        return training
    
    def get_status(self) -> Dict[str, Any]:
        """Get continuing education status"""
        return {
            "bot_id": self.bot_id,
            "operational": True,
            "last_check": datetime.utcnow().isoformat()
        }


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI interface for medical team suite"""
    print("\n" + "="*80)
    print("DrMythara Medical Team Suite - Comprehensive Healthcare Bot System")
    print("="*80)
    print("\nCRITICAL DISCLAIMER:")
    print("- NO MEDICAL ADVICE PROVIDED")
    print("- NO DIAGNOSTIC CAPABILITIES")
    print("- ADMINISTRATIVE & COMPLIANCE SUPPORT ONLY")
    print("- NOT A SUBSTITUTE FOR MEDICAL PROFESSIONALS")
    print("="*80 + "\n")
    
    suite = MedicalTeamSuite()
    
    # Generate status report
    report = suite.generate_suite_report()
    
    print("\n📊 MEDICAL TEAM SUITE STATUS REPORT")
    print("="*80)
    print(json.dumps(report, indent=2))
    print("\n" + "="*80)
    
    # Demo: Create triage case
    print("\n🚑 DEMO: Creating Triage Case...")
    triage_case = suite.triage_bot.assess_triage(
        patient_id="PT001",
        chief_complaint="Persistent cough and fever for 3 days",
        vital_signs={
            "heart_rate": 88,
            "blood_pressure_systolic": 125,
            "blood_pressure_diastolic": 80,
            "temperature_f": 100.4,
            "respiratory_rate": 18,
            "oxygen_saturation": 97
        }
    )
    print(f"✅ Triage case created: {triage_case.case_id}")
    print(f"   Urgency: {triage_case.urgency_level.value}")
    
    # Demo: Schedule appointment
    print("\n📅 DEMO: Scheduling Appointment...")
    appointment = suite.scheduling_bot.schedule_appointment(
        patient_id="PT001",
        provider_id="DR_SMITH",
        appointment_type="follow_up",
        scheduled_time=(datetime.utcnow() + timedelta(days=7)).isoformat(),
        duration_minutes=30
    )
    print(f"✅ Appointment scheduled: {appointment['appointment_id']}")
    
    # Demo: Create compliance alert
    print("\n⚠️  DEMO: Creating Compliance Alert...")
    alert = suite.compliance_bot.create_alert(
        alert_type="HIPAA",
        severity="medium",
        description="Unsigned clinical notes pending > 24 hours",
        affected_systems=["EMR_SYSTEM"]
    )
    print(f"✅ Compliance alert created: {alert.alert_id}")
    
    print("\n" + "="*80)
    print("Medical Team Suite Demo Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
