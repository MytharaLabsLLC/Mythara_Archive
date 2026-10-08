import os
import sys
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
DrMythara Bot - Healthcare Compliance Specialist (user-facing wrapper).

Thin demo face. The canonical health-reasoning core lives in
soul_cradle/health.py — rule tables, consult_health(), screen_health(),
and the standing-matrix adapter. This wrapper owns the SQLite audit
trail, the self-assessment checklist flows, and orchestrator
registration. It owns no rules: every rule it references comes from the
core.

- HIPAA self-assessment checklists (NOT audits)
- FDA 21 CFR Part 11 readiness checklists (NOT validations)
- Medical AI governance checklists

NOT A MEDICAL PROFESSIONAL. DOES NOT PROVIDE MEDICAL ADVICE.
COMPLIANCE GUIDANCE ONLY.

PLAIN-LANGUAGE PROMISE (read before using the checklist functions):
  * Every "audit" / "validation" / "assessment" function below is a
    SELF-ASSESSMENT CHECKLIST, not an audit. It evaluates ONLY the
    answers the caller supplies and derives every finding from those
    inputs. Nothing is simulated, scanned, or pre-filled — the old
    simulated flows with canned findings were removed.
  * Answers are keyed by control id (the rule "check" fields in
    soul_cradle/health.py). Call bot.checklist_controls(domain) to list
    the exact questions and their control ids.
  * Answer values: True (control in place) / False (not in place) /
    "unknown" (no answer). Unanswered controls are reported as UNKNOWN —
    never assumed pass or fail. Unrecognized values are treated as
    unknown, never guessed.
  * Output is always labeled "self-assessment checklist, not an audit"
    and never implies certification, compliance achievement, audit
    completeness, or a regulatory determination.
  * The database is encrypted at rest (Fernet) and every compliance
    function requires sign-in. The current posture is documented in
    COMPLIANCE_STATUS.md — "built with compliance in mind; readiness,
    never certified."
"""

# Repo-root bootstrap so the wrapper can reach the Soul Cradle core.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sqlite3
import hashlib
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import requests

from soul_cradle.health import (
    RULE_TABLES,
    consult_health,
    screen_health,
    verify_judgment,
    rule_inventory,
)

try:
    from soul_cradle.bot_witness import (
        witness_action,
        checklist_evidence,
        WitnessUnavailable,
    )
except ImportError:  # pragma: no cover — direct-script fallback
    from pathlib import Path as _WitnessPath

    sys.path.insert(0, str(_WitnessPath(__file__).resolve().parent.parent))
    from soul_cradle.bot_witness import (
        witness_action,
        checklist_evidence,
        WitnessUnavailable,
    )

try:
    from drmythara_security import (
        EncryptedSQLite,
        DataKey,
        MissingDataKeyError,
        SecurityError as DrMytharaSecurityError,
        AuthenticationError as DrMytharaAuthenticationError,
        AccountLockedError as DrMytharaAccountLockedError,
        SessionError as DrMytharaSessionError,
        AccessDeniedError as DrMytharaAccessDeniedError,
        BackupError as DrMytharaBackupError,
        PasswordHasher,
        UserStore,
        SessionManager,
        BreakGlass,
        AuditReview,
        BackupManager,
        assert_subject_allowed,
    )
    from drmythara_persona import MytharaVoice, check_claim as _check_claim
    from drmythara_llm import MytharaChat, ChatConfig, SYSTEM_PROMPT
    from drmythara_vitals import (
        VitalReading,
        VitalsStore,
        WellnessEngine,
        WellnessReport,
        Observation,
        screen_symptoms,
        WELLNESS_DISCLAIMER,
    )
    from drmythara_council import CareCouncil, CouncilResult
    from drmythara_ledger import (
        VitalsLedger,
        export_doctor_summary as _export_doctor_summary,
        VITAL_READING,
        WELLNESS_REPORT,
        COUNCIL_DELIBERATION,
        SYMPTOM_SCREEN,
        CHAT_NOTE,
    )
    _SECURITY_AVAILABLE = True
except ImportError:  # pragma: no cover — direct-script fallback
    from pathlib import Path as _SecPath

    sys.path.insert(0, str(_SecPath(__file__).resolve().parent))
    from drmythara_security import (
        EncryptedSQLite,
        DataKey,
        MissingDataKeyError,
        SecurityError as DrMytharaSecurityError,
        AuthenticationError as DrMytharaAuthenticationError,
        AccountLockedError as DrMytharaAccountLockedError,
        SessionError as DrMytharaSessionError,
        AccessDeniedError as DrMytharaAccessDeniedError,
        BackupError as DrMytharaBackupError,
        PasswordHasher,
        UserStore,
        SessionManager,
        BreakGlass,
        AuditReview,
        BackupManager,
        assert_subject_allowed,
    )
    from drmythara_persona import MytharaVoice, check_claim as _check_claim
    from drmythara_llm import MytharaChat, ChatConfig, SYSTEM_PROMPT
    from drmythara_vitals import (
        VitalReading,
        VitalsStore,
        WellnessEngine,
        WellnessReport,
        Observation,
        screen_symptoms,
        WELLNESS_DISCLAIMER,
    )
    from drmythara_council import CareCouncil, CouncilResult
    from drmythara_ledger import (
        VitalsLedger,
        export_doctor_summary as _export_doctor_summary,
        VITAL_READING,
        WELLNESS_REPORT,
        COUNCIL_DELIBERATION,
        SYMPTOM_SCREEN,
        CHAT_NOTE,
    )
    _SECURITY_AVAILABLE = True

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

DISCLAIMER = (
    "NOT A MEDICAL PROFESSIONAL. DOES NOT PROVIDE MEDICAL ADVICE. "
    "COMPLIANCE GUIDANCE ONLY."
)

CHECKLIST_LABEL = (
    "SELF-ASSESSMENT CHECKLIST — NOT AN AUDIT. Results reflect only "
    "caller-supplied answers; this is not an audit, not a certification, "
    "not a determination of compliance, and not a complete assessment."
)

# Rule-table -> legacy nested group label (shape compatibility for rule views)
_TABLE_GROUPS = {
    "hipaa_technical": "technical_safeguards",
    "hipaa_administrative": "administrative_safeguards",
    "hipaa_physical": "physical_safeguards",
}

# Checklist domain -> canonical rule-table names consulted
CHECKLIST_TABLES = {
    "hipaa": ["hipaa_technical", "hipaa_administrative", "hipaa_physical"],
    "fda_cfr11": ["fda_records", "fda_signatures"],
    "ai_governance": ["ai_governance"],
}

# Rule table -> audit-trail group label
_TABLE_GROUP = {
    "hipaa_technical": "technical",
    "hipaa_administrative": "administrative",
    "hipaa_physical": "physical",
    "fda_records": "records",
    "fda_signatures": "signatures",
    "ai_governance": "governance",
}

# Answer normalization: truthy tokens, falsy tokens. Anything else (or
# missing) -> unknown. Never guessed.
_TRUE_TOKENS = {
    "true", "yes", "y", "1", "pass", "passed", "implemented", "satisfied",
    "compliant", "complete", "done", "in_place", "in place",
}
_FALSE_TOKENS = {
    "false", "no", "n", "0", "fail", "failed", "not_implemented",
    "not implemented", "unsatisfied", "non_compliant", "noncompliant",
    "incomplete", "missing", "absent",
}

# Reference data (identifier categories, not checkable rules)
PHI_CATEGORIES = [
    "names", "addresses", "dates", "phone_numbers", "fax_numbers", "email_addresses",
    "ssn", "medical_record_numbers", "health_plan_numbers", "account_numbers",
    "certificate_numbers", "vehicle_identifiers", "device_identifiers", "urls",
    "ip_addresses", "biometric_identifiers", "photos", "unique_identifying_numbers",
]

AI_GOVERNANCE_REFERENCE = {
    "risk_categories": {
        "low_risk": "Non-diagnostic informational AI (e.g., appointment scheduling)",
        "moderate_risk": "Clinical decision support without autonomous action",
        "high_risk": "Diagnostic AI requiring FDA clearance",
        "critical_risk": "Autonomous treatment AI (rare, heavily regulated)",
    },
    "fda_device_classes": {
        "class_i": "Low risk, general controls",
        "class_ii": "Moderate risk, special controls + 510(k) clearance",
        "class_iii": "High risk, PMA (Pre-Market Approval) required",
    },
}


def _nested_rule_view() -> Dict[str, Any]:
    """Rebuild the legacy nested rule shape from the canonical core tables."""
    view: Dict[str, Any] = {}
    for table_name, group in _TABLE_GROUPS.items():
        table = RULE_TABLES[table_name]
        group_view = view.setdefault(group, {})
        for rule in table.rules:
            group_view.setdefault(rule.category, []).append(rule.check)
    view["phi_categories"] = list(PHI_CATEGORIES)
    return view


def prompt_answer(check_id: str, requirement: str):
    """Example `ask` callable for interactive checklist use (stdin).

    Pass as ask=prompt_answer to audit_hipaa_compliance() /
    validate_fda_cfr11_compliance() / assess_medical_ai_governance() to be
    prompted for each control not present in `answers`.
    """
    return input(f"[{check_id}] {requirement}\n  Implemented? (yes/no/unknown): ")


def _requires_auth(method):
    """Method decorator: no signed-in session, no ePHI function.

    Raises DrMytharaSessionError ("Not signed in…") when called without
    login(). Applied to every method that reads or writes protected data.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._current_session()  # raises when not signed in
        return method(self, *args, **kwargs)
    return wrapper


class DrMytharaBot:
    """DrMythara Bot - Healthcare compliance specialist (user-facing wrapper)."""

    def __init__(
        self,
        *,
        data_key: Optional[str] = None,
        dev_mode: bool = False,
        db_path: Optional[str] = None,
        persona: bool = True,
    ):
        """Create the bot.

        data_key: Fernet key for at-rest encryption. Defaults to the
            DRMYTHARA_DATA_KEY environment variable. Missing key raises
            MissingDataKeyError unless dev_mode=True.
        dev_mode: run WITHOUT encryption (loud warnings). Dev and tests
            only — never point at real data.
        db_path: database file location (default mythara_drmythara.db
            in the current directory).
        persona: attach Mythara's voice layer (default on).
        """
        self.bot_id = "drmythara_bot"
        self.bot_token = None
        self.db_path = db_path or "mythara_drmythara.db"
        self.dev_mode = dev_mode

        # At-rest encryption key: provisioned secret config only, never
        # ephemeral. Fail closed on ePHI paths.
        self._fernet = DataKey.resolve(data_key, strict=not dev_mode)
        if self._fernet is None:
            print(
                "⚠️  DrMythara running in DEV MODE: database is NOT encrypted. "
                "Set DRMYTHARA_DATA_KEY for real use."
            )

        # Rule views are projections of the canonical core — not copies.
        self.hipaa_rules = _nested_rule_view()
        self.ai_governance = dict(AI_GOVERNANCE_REFERENCE)

        # Auth + sessions + audit trail
        self.sessions = SessionManager()
        self._session_token: Optional[str] = None
        self._breakglass: Optional[BreakGlass] = None  # lazy: needs secret

        # Mythara's voice (the "I Am Mythara" character).
        self.voice = MytharaVoice() if persona else None
        self._chat: Optional["MytharaChat"] = None  # lazy: needs LLM config

        # Initialize database (encrypted)
        self._init_db()

        # Register with orchestrator
        self._register()

    # -- database (encrypted at rest) ------------------------------------

    def _db(self):
        """Context manager yielding a sqlite3 connection to the encrypted
        database. Commits on clean exit."""
        return EncryptedSQLite(self.db_path, self._fernet)

    # -- canonical core passthroughs -------------------------------------

    def consult(self, topic: str, evidence: Dict[str, Any]):
        """Health-reasoning consult. Delegates to soul_cradle.health.

        Returns a HealthJudgment: verdict in {"clear","flagged",
        "outside_scope"}, findings, rule_versions, integrity_hash.
        """
        return consult_health(topic, evidence)

    def screen(self, action_description: str, evidence: Optional[Dict[str, Any]] = None):
        """Membrane hook passthrough: screen_health() from the core."""
        return screen_health(action_description, evidence)

    def rule_versions(self) -> Dict[str, Dict[str, str]]:
        """Every rule table with version, effective date, and source."""
        return rule_inventory()

    # -- audit trail ------------------------------------------------------

    def _init_db(self):
        """Initialize the DrMythara database (encrypted at rest).

        Creates the checklist tables plus the security tables (users,
        chained security events, review sign-offs).
        """
        with self._db() as conn:
            self._create_tables(conn)

    def _create_tables(self, conn):
        """Create all tables: checklist audit trail + security tables."""
        c = conn.cursor()

        # HIPAA compliance audits
        c.execute('''
            CREATE TABLE IF NOT EXISTS hipaa_audits (
                audit_id TEXT PRIMARY KEY,
                organization_name TEXT NOT NULL,
                audit_date TEXT NOT NULL,
                audit_type TEXT CHECK(audit_type IN ('initial', 'annual', 'incident', 'ad_hoc')),
                scope TEXT,
                technical_score INT DEFAULT 0,
                administrative_score INT DEFAULT 0,
                physical_score INT DEFAULT 0,
                overall_score INT DEFAULT 0,
                findings TEXT,
                critical_issues INT DEFAULT 0,
                high_issues INT DEFAULT 0,
                medium_issues INT DEFAULT 0,
                low_issues INT DEFAULT 0,
                remediation_plan TEXT,
                status TEXT DEFAULT 'in_progress',
                completed_at TEXT,
                integrity_hash TEXT
            )
        ''')

        # FDA 21 CFR Part 11 validations
        c.execute('''
            CREATE TABLE IF NOT EXISTS fda_validations (
                validation_id TEXT PRIMARY KEY,
                system_name TEXT NOT NULL,
                validation_date TEXT NOT NULL,
                validation_type TEXT CHECK(validation_type IN ('initial', 'periodic', 'change_control', 'revalidation')),
                electronic_records_compliant BOOLEAN DEFAULT 0,
                electronic_signatures_compliant BOOLEAN DEFAULT 0,
                audit_trail_compliant BOOLEAN DEFAULT 0,
                overall_compliant BOOLEAN DEFAULT 0,
                findings TEXT,
                gaps TEXT,
                remediation_actions TEXT,
                status TEXT DEFAULT 'in_progress',
                completed_at TEXT,
                integrity_hash TEXT
            )
        ''')

        # Medical AI governance assessments
        c.execute('''
            CREATE TABLE IF NOT EXISTS ai_governance_assessments (
                assessment_id TEXT PRIMARY KEY,
                ai_system_name TEXT NOT NULL,
                assessment_date TEXT NOT NULL,
                risk_category TEXT CHECK(risk_category IN ('low_risk', 'moderate_risk', 'high_risk', 'critical_risk')),
                fda_device_class TEXT CHECK(fda_device_class IN ('class_i', 'class_ii', 'class_iii', 'not_device')),
                requires_fda_clearance BOOLEAN DEFAULT 0,
                clinical_validation_complete BOOLEAN DEFAULT 0,
                bias_testing_complete BOOLEAN DEFAULT 0,
                drift_monitoring_enabled BOOLEAN DEFAULT 0,
                overall_governance_score INT DEFAULT 0,
                findings TEXT,
                recommendations TEXT,
                status TEXT DEFAULT 'in_progress',
                completed_at TEXT,
                integrity_hash TEXT
            )
        ''')

        # PHI exposure incidents
        c.execute('''
            CREATE TABLE IF NOT EXISTS phi_incidents (
                incident_id TEXT PRIMARY KEY,
                detected_at TEXT NOT NULL,
                incident_type TEXT CHECK(incident_type IN ('unauthorized_access', 'data_breach', 'improper_disposal', 'lost_device', 'ransomware', 'phishing', 'insider_threat')),
                severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
                affected_records INT DEFAULT 0,
                affected_phi_categories TEXT,
                breach_notification_required BOOLEAN DEFAULT 0,
                ocr_notified BOOLEAN DEFAULT 0,
                patients_notified BOOLEAN DEFAULT 0,
                root_cause TEXT,
                remediation_actions TEXT,
                status TEXT DEFAULT 'investigating',
                resolved_at TEXT,
                integrity_hash TEXT
            )
        ''')

        # Compliance reports
        c.execute('''
            CREATE TABLE IF NOT EXISTS compliance_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT CHECK(report_type IN ('hipaa', 'fda_cfr11', 'ai_governance', 'combined')),
                generated_at TEXT NOT NULL,
                reporting_period_start TEXT NOT NULL,
                reporting_period_end TEXT NOT NULL,
                overall_compliance_score INT DEFAULT 0,
                total_audits INT DEFAULT 0,
                critical_findings INT DEFAULT 0,
                recommendations TEXT,
                executive_summary TEXT,
                integrity_hash TEXT
            )
        ''')

        # Security tables: users, hash-chained security events, reviews.
        UserStore(conn)
        AuditReview(conn)

        # Wellness tables: vitals readings + hash-chained health ledger.
        VitalsStore(conn)
        VitalsLedger(conn)

        print(f"[OK] DrMythara Bot database initialized: {self.db_path}"
              + ("" if self._fernet else " (DEV MODE — unencrypted)"))

    def _register(self):
        """Register with Mythara Orchestrator."""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/register_bot",
                json={
                    "vp_token": VP_MASTER_TOKEN,
                    "bot_id": self.bot_id,
                    "bot_name": "DrMythara Healthcare Compliance Bot"
                },
                timeout=5
            )
            if response.status_code == 200:
                self.bot_token = response.json()['bot_token']
                print(f"[OK] Registered with orchestrator: {self.bot_id}")
        except Exception as e:
            print(f"[WARN] Could not connect to orchestrator: {e}")

    def _generate_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for audit trail."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

    # -- authentication & sessions --------------------------------------

    def _current_session(self) -> Dict[str, Any]:
        """Return the current session or raise (used by _requires_auth)."""
        if not self._session_token:
            raise DrMytharaSessionError("Not signed in. Call login() first.")
        return self.sessions.validate(self._session_token)

    def _audit(self, conn, actor: str, action: str,
               subject: Optional[str] = None,
               detail: Optional[str] = None,
               emergency: bool = False) -> None:
        AuditReview(conn).log_event(actor, action, subject=subject,
                                    detail=detail, emergency=emergency)

    def create_user(self, user_id: str, password: str,
                    role: str = "clinician") -> Dict[str, str]:
        """Create a user account.

        First-user bootstrap: when no users exist yet, the first account
        is created without a session (it becomes admin) and the event is
        logged. Afterwards, only a signed-in admin can create users.
        """
        with self._db() as conn:
            store = UserStore(conn)
            if store.user_count() == 0:
                rec = store.create_user(user_id, password, role="admin")
                self._audit(conn, user_id, "first_admin_created",
                            detail="bootstrap: first user becomes admin")
                return rec
            sess = self._current_session()
            if sess["role"] != "admin":
                raise DrMytharaAccessDeniedError(
                    "Only an admin can create users.")
            rec = store.create_user(user_id, password, role)
            self._audit(conn, sess["user_id"], "user_created",
                        detail=f"created {user_id} with role {role}",
                        emergency=sess["emergency"])
            return rec

    def login(self, user_id: str, password: str) -> Dict[str, str]:
        """Sign in. Returns a session token plus the user record.

        Passwords are verified with PBKDF2-HMAC-SHA256 (per-user salt).
        Five wrong tries lock the account for 15 minutes. Failures are
        logged without revealing whether the user ID exists.
        """
        with self._db() as conn:
            store = UserStore(conn)
            try:
                user = store.authenticate(user_id, password)
            except (DrMytharaAuthenticationError,
                    DrMytharaAccountLockedError) as exc:
                self._audit(conn, user_id or "unknown", "login_failed",
                            detail=type(exc).__name__)
                raise
            token = self.sessions.create_session(user["user_id"],
                                                 user["role"])
            self._session_token = token
            self._audit(conn, user["user_id"], "login")
            return {"token": token, **user}

    def logout(self) -> None:
        """End the current session."""
        if not self._session_token:
            return
        try:
            actor = self.sessions.validate(self._session_token)["user_id"]
        except DrMytharaSessionError:
            actor = "unknown"
        self.sessions.revoke(self._session_token)
        self._session_token = None
        with self._db() as conn:
            self._audit(conn, actor, "logout")

    # -- break-glass emergency access ------------------------------------

    def _get_breakglass(self) -> BreakGlass:
        if self._breakglass is None:
            # Raises SecurityError until DRMYTHARA_BREAKGLASS_SECRET is set.
            self._breakglass = BreakGlass()
        return self._breakglass

    def break_glass_request(self, operator_id: str, reason: str) -> Dict[str, str]:
        """Issue a 30-minute emergency token. Does NOT need a session —
        that is the point: it exists for when normal sign-in is impossible.

        The reason is required and the issuance is written to the
        security log flagged for review. Rotate the break-glass secret
        after any use.
        """
        issued = self._get_breakglass().issue_token(operator_id, reason)
        with self._db() as conn:
            self._audit(conn, operator_id, "break_glass_issued",
                        detail=f"reason: {reason}", emergency=True)
        return issued

    def login_break_glass(self, token: str) -> Dict[str, str]:
        """Sign in with an emergency token. The session is admin-scoped,
        lasts 30 minutes, and every action under it is flagged emergency
        in the audit log."""
        rec = self._get_breakglass().validate_token(token)
        sess_token = self.sessions.create_session(
            rec["operator_id"], "admin", emergency=True,
            ttl=timedelta(minutes=30))
        self._session_token = sess_token
        with self._db() as conn:
            self._audit(conn, rec["operator_id"], "break_glass_login",
                        detail=f"reason: {rec['reason']}", emergency=True)
        return {"token": sess_token, "user_id": rec["operator_id"],
                "role": "admin", "emergency": True}

    # -- PHI incidents (subject-scoped) -----------------------------------

    @_requires_auth
    def record_phi_incident(self, *, incident_type: str, severity: str,
                            subject_id: Optional[str] = None,
                            affected_records: int = 0,
                            affected_phi_categories: Optional[List[str]] = None,
                            root_cause: str = "",
                            remediation_actions: str = "") -> Dict[str, str]:
        """Record a PHI incident. Written to the encrypted database and
        the security log. breach_notification_required is an initial
        triage flag, not a legal determination."""
        sess = self._current_session()
        incident_id = (
            f"PHI-{datetime.now().strftime('%Y%m%d')}-{os.urandom(4).hex().upper()}"
        )
        breach_flag = severity in ("high", "critical") and affected_records > 0
        row = {
            "incident_id": incident_id,
            "detected_at": datetime.now().isoformat(),
            "incident_type": incident_type,
            "severity": severity,
            "affected_records": affected_records,
            "affected_phi_categories": json.dumps(affected_phi_categories or []),
            "breach_notification_required": int(breach_flag),
            "ocr_notified": 0,
            "patients_notified": 0,
            "root_cause": root_cause,
            "remediation_actions": remediation_actions,
            "status": "investigating",
            "resolved_at": None,
            "integrity_hash": "",
            "subject_id": subject_id,
        }
        row["integrity_hash"] = self._generate_integrity_hash(
            {k: v for k, v in row.items() if k != "integrity_hash"})
        with self._db() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(phi_incidents)")]
            if "subject_id" not in cols:
                conn.execute("ALTER TABLE phi_incidents ADD COLUMN subject_id TEXT")
            conn.execute(
                """INSERT INTO phi_incidents
                   (incident_id, detected_at, incident_type, severity,
                    affected_records, affected_phi_categories,
                    breach_notification_required, ocr_notified, patients_notified,
                    root_cause, remediation_actions, status, resolved_at,
                    integrity_hash, subject_id)
                   VALUES (:incident_id, :detected_at, :incident_type, :severity,
                    :affected_records, :affected_phi_categories,
                    :breach_notification_required, :ocr_notified, :patients_notified,
                    :root_cause, :remediation_actions, :status, :resolved_at,
                    :integrity_hash, :subject_id)""", row)
            self._audit(conn, sess["user_id"], "phi_incident_recorded",
                        subject=subject_id,
                        detail=f"{incident_id} severity={severity}",
                        emergency=sess["emergency"])
        return {"incident_id": incident_id,
                "breach_notification_required": breach_flag,
                "status": "investigating"}

    @_requires_auth
    def list_phi_incidents(
            self, subject_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List PHI incidents. Minimum-necessary: non-admins see only
        their own subject's incidents; admins may filter or see all.
        Every read is logged."""
        sess = self._current_session()
        if sess["role"] == "admin":
            requested = subject_id  # None = all
        else:
            requested = subject_id or sess["user_id"]
            assert_subject_allowed(sess["user_id"], requested)
        with self._db() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(phi_incidents)")]
            if "subject_id" not in cols:
                conn.execute("ALTER TABLE phi_incidents ADD COLUMN subject_id TEXT")
            if requested:
                rows = conn.execute(
                    "SELECT * FROM phi_incidents WHERE subject_id = ? "
                    "ORDER BY detected_at DESC", (requested,)).fetchall()
                names = [d[1] for d in conn.execute(
                    "PRAGMA table_info(phi_incidents)")]
            else:
                rows = conn.execute(
                    "SELECT * FROM phi_incidents ORDER BY detected_at DESC"
                ).fetchall()
                names = [d[1] for d in conn.execute(
                    "PRAGMA table_info(phi_incidents)")]
            self._audit(conn, sess["user_id"], "phi_incidents_listed",
                        subject=requested, detail=f"{len(rows)} rows",
                        emergency=sess["emergency"])
            result = [dict(zip(names, r)) for r in rows]
        return result

    # -- backups & restore tests ------------------------------------------

    @_requires_auth
    def backup_now(self, label: str = "drmythara") -> Dict[str, str]:
        """Write an encrypted backup of the database. Logged."""
        sess = self._current_session()
        if self._fernet is None:
            raise DrMytharaBackupError(
                "Backups need a data key — dev mode has none.")
        backup_dir = os.path.join(
            os.path.dirname(os.path.abspath(self.db_path)), "backups")
        result = BackupManager(backup_dir).backup(
            self.db_path, self._fernet, label)
        with self._db() as conn:
            self._audit(conn, sess["user_id"], "backup",
                        detail=f"{result['backup']} sha256={result['sha256'][:16]}…",
                        emergency=sess["emergency"])
        return result

    @_requires_auth
    def test_restore_now(self, label: str = "drmythara") -> Dict[str, Any]:
        """Run a full restore drill (backup → restore → verify) and log
        the result. Raises BackupError on any failure."""
        sess = self._current_session()
        if self._fernet is None:
            raise DrMytharaBackupError(
                "Restore tests need a data key — dev mode has none.")

        def _verify(path: str) -> None:
            with EncryptedSQLite(path, self._fernet) as conn:
                conn.execute("SELECT COUNT(*) FROM hipaa_audits").fetchone()

        report = BackupManager(
            os.path.dirname(os.path.abspath(self.db_path))
        ).test_restore(self.db_path, self._fernet, label,
                       verify_opens=_verify)
        with self._db() as conn:
            self._audit(conn, sess["user_id"], "restore_test",
                        detail=f"ok={report['ok']} sha256={report['restored_sha256'][:16]}…",
                        emergency=sess["emergency"])
        return report

    # -- audit review sign-off ---------------------------------------------

    @_requires_auth
    def pending_review(self) -> Dict[str, Any]:
        """Security events since the last review, plus chain health."""
        with self._db() as conn:
            return AuditReview(conn).review_status()

    @_requires_auth
    def sign_off_review(self, note: str = "") -> Dict[str, Any]:
        """Review all pending security events and record the sign-off,
        hash-chained. The sign-off itself is logged."""
        sess = self._current_session()
        with self._db() as conn:
            audit = AuditReview(conn)
            result = audit.sign_off(sess["user_id"], note)
            self._audit(conn, sess["user_id"], "review_sign_off",
                        detail=f"reviewed {result['events_reviewed']} events",
                        emergency=sess["emergency"])
        return result

    # -- Mythara's voice ----------------------------------------------------

    def greet(self) -> str:
        """The character's introduction (the "I Am Mythara" monologue)."""
        if self.voice is None:
            return "DrMythara compliance assistant ready."
        return self.voice.greet()

    def introduce(self) -> str:
        """The wellness companion's greeting: honest disclosure first,
        warm clinical frame. This is how she meets someone — the "Dr"
        is her character name, not a credential."""
        if self.voice is None:
            return "DrMythara wellness companion ready."
        return self.voice.intro()

    # -- wellness companion -------------------------------------------------
    # Vitals + heuristic wellness, voiced clinically, recorded in the
    # hash-chained ledger. Every method needs sign-in; non-admins are
    # scoped to their own subject (minimum-necessary).

    @staticmethod
    def _resolve_subject(sess: Dict[str, Any],
                         subject_id: Optional[str]) -> str:
        """Minimum-necessary: non-admins act only on their own subject."""
        if sess["role"] == "admin":
            return subject_id or sess["user_id"]
        subject = subject_id or sess["user_id"]
        assert_subject_allowed(sess["user_id"], subject)
        return subject

    @staticmethod
    def _obs_to_dict(obs: "Observation") -> Dict[str, Any]:
        return {
            "rule_id": obs.rule_id,
            "severity": obs.severity,
            "title": obs.title,
            "saw": obs.saw,
            "why_it_matters": obs.why_it_matters,
            "consider": obs.consider,
            "reasoning": list(obs.reasoning or []),
            "values": dict(obs.values or {}),
        }

    @_requires_auth
    def record_vitals(self, vital_type: str, value: float, *,
                      subject_id: Optional[str] = None,
                      unit: str = "",
                      secondary: Optional[float] = None,
                      note: str = "",
                      source: str = "manual",
                      taken_at: Optional[str] = None) -> Dict[str, Any]:
        """Record one vitals reading, voiced back in her clinical voice.

        The reading is stored in the encrypted database and chained
        into the health ledger. Implausible values are rejected as
        likely entry errors (see drmythara_vitals._sanity_check).
        """
        sess = self._current_session()
        subject = self._resolve_subject(sess, subject_id)
        reading = VitalReading(
            subject_id=subject, vital_type=vital_type, value=value,
            unit=unit, secondary=secondary, note=note, source=source,
            taken_at=taken_at)
        with self._db() as conn:
            store = VitalsStore(conn)
            ledger = VitalsLedger(conn)
            reading_id = store.record(reading)
            ledger.record(subject, VITAL_READING, {
                "reading_id": reading_id,
                "vital_type": vital_type,
                "value": value,
                "secondary": secondary,
                "unit": unit,
                "taken_at": reading.taken_at,
                "source": source,
                "note": note,
            })
            self._audit(conn, sess["user_id"], "vital_recorded",
                        subject=subject,
                        detail=f"{vital_type} reading {reading_id}",
                        emergency=sess["emergency"])
        spoken = self.voice.narrate(
            f"Recorded: {vital_type} {value:g}"
            f"{'/' + str(secondary) if secondary else ''}"
            f" {unit} for you.".strip()) if self.voice else "Recorded."
        return {"reading_id": reading_id, "spoken": spoken,
                "subject_id": subject}

    @_requires_auth
    def wellness_check(self, subject_id: Optional[str] = None
                       ) -> Dict[str, Any]:
        """Run the full wellness flow: heuristic engine, care council,
        hash-chained record — spoken in her clinical voice.

        Escalations are voiced first and directly; the council's note
        is attached (its deliberation never gates urgent care).
        """
        sess = self._current_session()
        subject = self._resolve_subject(sess, subject_id)
        with self._db() as conn:
            store = VitalsStore(conn)
            ledger = VitalsLedger(conn)
            report = WellnessEngine().evaluate(subject, store)
            council_result = CareCouncil().deliberate(report)
            ledger.record(subject, WELLNESS_REPORT, {
                "generated_at": report.generated_at,
                "rules_evaluated": report.rules_evaluated,
                "observations": [self._obs_to_dict(o)
                                 for o in report.observations],
            })
            ledger.record(subject, COUNCIL_DELIBERATION, {
                "verdict": council_result.verdict,
                "observations_count": len(report.observations),
                "dissent": council_result.dissent,
                "judgment_hashes": [j.get("integrity_hash")
                                    for j in council_result.judgments],
            })
            self._audit(conn, sess["user_id"], "wellness_check",
                        subject=subject,
                        detail=(f"{len(report.observations)} observations, "
                                f"council={council_result.verdict}"),
                        emergency=sess["emergency"])
        spoken = self.voice.narrate_wellness(report)
        spoken += "\n\n" + council_result.note
        return {
            "spoken": spoken,
            "observations": [self._obs_to_dict(o)
                             for o in report.observations],
            "council_verdict": council_result.verdict,
            "council_note": council_result.note,
            "subject_id": subject,
        }

    @_requires_auth
    def symptom_prescreen(self, text: str,
                          subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Screen free text for emergency symptoms — locally, instantly.

        On match: direct escalation in her voice, chained to the
        ledger. Otherwise a calm, honest all-clear (not a diagnosis).
        Runs before any LLM call; the model is never the safety net.
        """
        sess = self._current_session()
        subject = self._resolve_subject(sess, subject_id)
        found = screen_symptoms(text or "")
        with self._db() as conn:
            ledger = VitalsLedger(conn)
            if found is not None:
                ledger.record(subject, SYMPTOM_SCREEN, {
                    "matched": found.values.get("matched", []),
                    "title": found.title,
                    "escalated": True,
                })
                self._audit(conn, sess["user_id"], "symptom_escalation",
                            subject=subject,
                            detail=f"matched={found.values.get('matched', [])}",
                            emergency=sess["emergency"])
                spoken = self.voice.escalate_care(
                    f"{found.title}. {found.saw}")
                return {"escalated": True, "spoken": spoken,
                        "subject_id": subject}
            ledger.record(subject, SYMPTOM_SCREEN, {
                "matched": [], "escalated": False})
            self._audit(conn, sess["user_id"], "symptom_screen_clear",
                        subject=subject, emergency=sess["emergency"])
            spoken = self.voice.narrate(
                "I listened for emergency patterns in what you described "
                "and did not find any. If anything changes or you feel "
                "worse, tell me right away — and trust your own sense of "
                "urgency over any screening.")
            return {"escalated": False, "spoken": spoken,
                    "subject_id": subject}

    @_requires_auth
    def export_doctor_summary(self, subject_id: Optional[str] = None) -> str:
        """The "bring to your doctor" summary — plain language, chained
        record behind it, honest disclaimer attached."""
        sess = self._current_session()
        subject = self._resolve_subject(sess, subject_id)
        with self._db() as conn:
            store = VitalsStore(conn)
            ledger = VitalsLedger(conn)
            summary = _export_doctor_summary(subject, ledger, store)
            self._audit(conn, sess["user_id"], "doctor_summary_exported",
                        subject=subject, emergency=sess["emergency"])
        return summary

    @_requires_auth
    def chat(self, message: str) -> Dict[str, Any]:
        """Conversational chat with Mythara (sign-in required).

        The message goes through the LLM backend configured by
        DRMYTHARA_LLM_PROVIDER (default "anthropic") with Mythara's
        system prompt. ePHI protection: without DRMYTHARA_BAA_SIGNED=1,
        messages with detected identifiers are refused, never sent to
        an external provider. The model's reply is screened for
        forbidden compliance claims.

        Only metadata is logged (provider, flags) — never message text.
        """
        sess = self._current_session()

        # Safety first, locally: emergency symptoms never wait for the
        # model. The LLM is conversational, never the safety net.
        screened = screen_symptoms(message or "")
        if screened is not None:
            with self._db() as conn:
                VitalsLedger(conn).record(
                    self._resolve_subject(sess, None), SYMPTOM_SCREEN, {
                        "matched": screened.values.get("matched", []),
                        "title": screened.title,
                        "escalated": True,
                        "via": "chat",
                    })
                self._audit(conn, sess["user_id"], "symptom_escalation",
                            subject=sess["user_id"],
                            detail="via chat: "
                            f"{screened.values.get('matched', [])}",
                            emergency=sess["emergency"])
            return {
                "reply": self.voice.escalate_care(
                    f"{screened.title}. {screened.saw}"),
                "provider": "local-screen",
                "sent_to_provider": False,
                "phi_detected": False,
                "claim_flagged": False,
                "escalated": True,
            }

        if self._chat is None:
            self._chat = MytharaChat()  # config from environment
        reply = self._chat.ask(message)
        with self._db() as conn:
            self._audit(conn, sess["user_id"], "llm_chat",
                        detail=(f"provider={reply.provider} "
                                f"sent={reply.sent_to_provider} "
                                f"phi={reply.phi_detected} "
                                f"claim_flagged={reply.claim_flagged}"),
                        emergency=sess["emergency"])
        return {
            "reply": reply.text,
            "provider": reply.provider,
            "sent_to_provider": reply.sent_to_provider,
            "phi_detected": reply.phi_detected,
            "claim_flagged": reply.claim_flagged,
            "escalated": False,
        }

    def narrate(self, result: Dict[str, Any]) -> str:
        """Render a checklist result in Mythara's voice.

        The voice layer self-checks every output: it can speak of the
        safeguards that genuinely exist (tamper-evident records, faithful
        logging) but can never assert certification or compliance.
        """
        if self.voice is None:
            return json.dumps(result, indent=2, default=str)[:2000]
        summary = {
            "domain": str(result.get("organization") or result.get("system_name")
                          or result.get("ai_system_name") or "this review"),
            "total_controls": int(result.get("controls_answered", 0)
                                  + result.get("controls_unanswered", 0)),
            "status_counts": {
                "compliant": int(result.get("controls_passed", 0)),
                "partial": 0,
                "non_compliant": int(result.get("controls_failed", 0)),
                "unknown": int(result.get("controls_unanswered", 0)),
            },
        }
        spoken = self.voice.narrate_summary(summary)
        return f"{spoken}\n\n{self.voice.closing()}"

    # -- honest checklist engine (self-assessment; nothing is simulated) ---

    def _witness_checklist(self, domain: str, summary: Dict[str, int]) -> None:
        """Record a checklist completion with the Soul Cradle panel.

        Record-only: a self-assessment checklist is never blocked, but its
        completion is witnessed and chained. Warn-and-proceed on outage.
        """
        try:
            evidence, bases = checklist_evidence(
                domain=domain,
                controls_total=summary["total_controls"],
                controls_failed=summary["failed"],
                controls_unknown=summary["unanswered"],
                declared_intent="report the checklist answers honestly; unanswered stay UNKNOWN",
            )
            witness_action(
                bot_id="drmythara",
                action=f"complete {domain} self-assessment checklist",
                evidence=evidence,
                evidence_bases=bases,
                enforce=False,
            )
        except WitnessUnavailable as exc:
            print(f"[DRMYTHARA] WITNESS UNAVAILABLE — {exc}; proceeding.")

    @staticmethod
    def _normalize_answer(raw: Any) -> Optional[bool]:
        """Normalize a caller-supplied answer -> True | False | None(unknown).

        Unrecognized or missing values become unknown. Never guessed.
        """
        if raw is None:
            return None
        if isinstance(raw, bool):
            return raw
        token = str(raw).strip().lower()
        if token in _TRUE_TOKENS:
            return True
        if token in _FALSE_TOKENS:
            return False
        return None

    @staticmethod
    def _json_safe(raw: Any) -> Any:
        """Keep stored answers JSON-serializable."""
        if raw is None or isinstance(raw, (bool, int, float, str)):
            return raw
        return str(raw)

    def checklist_controls(self, domain: str = "hipaa") -> List[Dict[str, Any]]:
        """List the control questions for a checklist domain.

        Returns [{table, rule_id, check, requirement, category, severity,
        guidance}]. The "check" value is the key your `answers` dict must
        supply. Every rule comes from the canonical core tables.
        """
        if domain not in CHECKLIST_TABLES:
            raise ValueError(
                f"Unknown checklist domain: {domain!r}. "
                f"Choose from {sorted(CHECKLIST_TABLES)}"
            )
        controls = []
        for table_name in CHECKLIST_TABLES[domain]:
            table = RULE_TABLES[table_name]
            for rule in table.rules:
                controls.append({
                    "table": table_name,
                    "rule_id": rule.rule_id,
                    "check": rule.check,
                    "requirement": rule.requirement,
                    "category": rule.category,
                    "severity": rule.severity,
                    "guidance": rule.guidance,
                })
        return controls

    def _run_checklist(
        self,
        tables,
        answers: Optional[Dict[str, Any]] = None,
        ask: Optional[Callable[[str, str], Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Evaluate caller-supplied answers against the canonical rules.

        Every control result derives from the caller's input. Returns
        per-control dicts with status in {"pass", "fail", "unknown"}.
        """
        answers = answers or {}
        table_names = [tables] if isinstance(tables, str) else list(tables)
        results = []
        for table_name in table_names:
            table = RULE_TABLES[table_name]
            for rule in table.rules:
                raw = answers.get(rule.check)
                if raw is None and ask is not None:
                    raw = ask(rule.check, rule.requirement)
                verdict = self._normalize_answer(raw)
                status = (
                    "pass" if verdict is True
                    else "fail" if verdict is False
                    else "unknown"
                )
                results.append({
                    "table": table_name,
                    "rule_id": rule.rule_id,
                    "check": rule.check,
                    "requirement": rule.requirement,
                    "category": rule.category,
                    "severity": rule.severity,
                    "guidance": rule.guidance,
                    "answer": self._json_safe(raw),
                    "status": status,
                })
        return results

    @staticmethod
    def _checklist_summary(results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Score from answered controls only; unanswered are reported, not scored."""
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        unknown = sum(1 for r in results if r["status"] == "unknown")
        answered = passed + failed
        score = round(passed / answered * 100) if answered else 0
        return {
            "total_controls": len(results),
            "answered": answered,
            "unanswered": unknown,
            "passed": passed,
            "failed": failed,
            "score": score,
        }

    @staticmethod
    def _findings_from_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build findings ONLY from the caller's answers. No canned findings.

        Failed controls become findings carrying the rule's own severity,
        requirement, and remediation guidance from the canonical core.
        Unanswered controls become "unknown" advisories — never assumed
        pass or fail.
        """
        findings = []
        for r in results:
            if r["status"] == "fail":
                findings.append({
                    "rule_id": r["rule_id"],
                    "severity": r["severity"],
                    "finding": (
                        "Control NOT satisfied per caller-supplied answer: "
                        f"{r['requirement']}"
                    ),
                    "recommendation": r["guidance"],
                })
            elif r["status"] == "unknown":
                findings.append({
                    "rule_id": r["rule_id"],
                    "severity": "advisory",
                    "finding": (
                        "No answer supplied — status UNKNOWN (not assumed "
                        f"pass or fail): {r['requirement']}"
                    ),
                    "recommendation": (
                        "Answer this control to complete the checklist; "
                        "unanswered controls cannot be cleared."
                    ),
                })
        return findings

    # -- checklist flows (self-assessment; the core does the real reasoning)

    @_requires_auth
    def audit_hipaa_compliance(
        self,
        organization: str,
        answers: Optional[Dict[str, Any]] = None,
        ask: Optional[Callable[[str, str], Any]] = None,
        scope: str = "full",
    ) -> Dict[str, Any]:
        """HIPAA self-assessment checklist (NOT an audit).

        Evaluates ONLY the answers you supply. Nothing is simulated and no
        finding is pre-written: every result derives from `answers`.

        Args:
            organization: Name of the organization being assessed.
            answers: dict of control_id -> True/False/"unknown". Control
                ids are the rule "check" fields; see checklist_controls().
                Omitted controls are reported as UNKNOWN.
            ask: optional callable(check_id, requirement) -> answer, used
                for controls missing from `answers` (interactive prompting;
                pass prompt_answer for a stdin prompt).
            scope: 'full', 'technical', 'administrative', or 'physical'.

        Returns:
            Checklist results labeled as self-assessment, with per-control
            pass/fail/unknown, findings derived from the answers, and the
            disclaimer. NOT a medical professional; NOT an audit.
        """
        scope_map = {
            "full": CHECKLIST_TABLES["hipaa"],
            "technical": ["hipaa_technical"],
            "administrative": ["hipaa_administrative"],
            "physical": ["hipaa_physical"],
        }
        if scope not in scope_map:
            raise ValueError(f"Unknown scope: {scope!r}. Choose from {sorted(scope_map)}")
        tables = scope_map[scope]

        audit_id = hashlib.sha256(
            f"{organization}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        results = self._run_checklist(tables, answers, ask)
        summary = self._checklist_summary(results)
        findings = self._findings_from_results(results)

        # Per-group scores for the audit-trail columns (answered controls only)
        group_scores = {}
        for table_name in tables:
            group = _TABLE_GROUP[table_name]
            group_results = [r for r in results if r["table"] == table_name]
            group_scores[group] = self._checklist_summary(group_results)["score"]

        technical_score = group_scores.get("technical", 0)
        administrative_score = group_scores.get("administrative", 0)
        physical_score = group_scores.get("physical", 0)

        critical_issues = sum(1 for r in results if r["status"] == "fail" and r["severity"] == "critical")
        high_issues = sum(1 for r in results if r["status"] == "fail" and r["severity"] == "high")
        medium_issues = sum(1 for r in results if r["status"] == "fail" and r["severity"] == "medium")
        low_issues = sum(1 for r in results if r["status"] == "fail" and r["severity"] == "low")

        findings_payload = {
            "label": CHECKLIST_LABEL,
            "disclaimer": DISCLAIMER,
            "controls": results,
            "findings": findings,
        }

        audit_data = {
            "audit_id": audit_id,
            "organization_name": organization,
            "audit_date": datetime.now().isoformat(),
            "audit_type": "ad_hoc",
            "scope": scope,
            "technical_score": technical_score,
            "administrative_score": administrative_score,
            "physical_score": physical_score,
            "overall_score": summary["score"],
            "findings": json.dumps(findings_payload),
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        audit_data["integrity_hash"] = self._generate_integrity_hash(audit_data)

        # Save to database
        with self._db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO hipaa_audits VALUES
                         (:audit_id, :organization_name, :audit_date, :audit_type, :scope,
                          :technical_score, :administrative_score, :physical_score, :overall_score,
                          :findings, :critical_issues, :high_issues, :medium_issues, :low_issues,
                          NULL, :status, :completed_at, :integrity_hash)''', audit_data)

        if summary["failed"] or summary["unanswered"]:
            recommendation = (
                f"Address the {summary['failed']} failed control(s) and answer the "
                f"{summary['unanswered']} unanswered control(s), then re-run. This "
                "checklist alone is not a determination of compliance."
            )
        else:
            recommendation = (
                "All controls answered and satisfied. Self-assessment only — "
                "not an audit, not a certification, not a compliance determination."
            )

        self._witness_checklist("hipaa", summary)

        return {
            "label": CHECKLIST_LABEL,
            "disclaimer": DISCLAIMER,
            "audit_id": audit_id,
            "organization": organization,
            "scope": scope,
            "overall_score": summary["score"],
            "technical_score": technical_score,
            "administrative_score": administrative_score,
            "physical_score": physical_score,
            "controls_answered": summary["answered"],
            "controls_unanswered": summary["unanswered"],
            "controls_passed": summary["passed"],
            "controls_failed": summary["failed"],
            "findings": findings,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "recommendation": recommendation,
        }

    @_requires_auth
    def validate_fda_cfr11_compliance(
        self,
        system_name: str,
        answers: Optional[Dict[str, Any]] = None,
        ask: Optional[Callable[[str, str], Any]] = None,
    ) -> Dict[str, Any]:
        """FDA 21 CFR Part 11 readiness checklist (NOT a validation).

        Same honesty contract as audit_hipaa_compliance(): evaluates ONLY
        caller-supplied answers keyed by control id (see
        checklist_controls("fda_cfr11")). A group reads compliant only when
        every control in it was answered and passed; any unanswered control
        yields None (unknown), never an assumed pass.
        """
        validation_id = hashlib.sha256(
            f"{system_name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        results = self._run_checklist(CHECKLIST_TABLES["fda_cfr11"], answers, ask)
        summary = self._checklist_summary(results)
        findings = self._findings_from_results(results)

        def _group_flag(table_name: str, check_id: Optional[str] = None) -> Optional[bool]:
            group = [r for r in results if r["table"] == table_name]
            if check_id is not None:
                group = [r for r in group if r["check"] == check_id]
            if any(r["status"] == "fail" for r in group):
                return False
            if group and all(r["status"] == "pass" for r in group):
                return True
            return None  # unanswered somewhere — unknown, not assumed

        records_compliant = _group_flag("fda_records")
        signatures_compliant = _group_flag("fda_signatures")
        audit_trail_compliant = _group_flag("fda_records", "audit_trail")

        flags = [records_compliant, signatures_compliant, audit_trail_compliant]
        if all(f is True for f in flags):
            overall_compliant: Optional[bool] = True
        elif any(f is False for f in flags):
            overall_compliant = False
        else:
            overall_compliant = None

        gaps = [
            f"{f['finding']} Remediation: {f['recommendation']}"
            for f in findings if f["severity"] != "advisory"
        ]

        findings_payload = {
            "label": CHECKLIST_LABEL,
            "disclaimer": DISCLAIMER,
            "controls": results,
            "findings": findings,
        }

        validation_data = {
            "validation_id": validation_id,
            "system_name": system_name,
            "validation_date": datetime.now().isoformat(),
            "validation_type": "periodic",  # self-assessment checklist run
            "electronic_records_compliant": records_compliant,
            "electronic_signatures_compliant": signatures_compliant,
            "audit_trail_compliant": audit_trail_compliant,
            "overall_compliant": overall_compliant,
            "findings": json.dumps(findings_payload),
            "gaps": json.dumps(gaps),
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        validation_data["integrity_hash"] = self._generate_integrity_hash(validation_data)

        # Save to database
        with self._db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO fda_validations VALUES
                         (:validation_id, :system_name, :validation_date, :validation_type,
                          :electronic_records_compliant, :electronic_signatures_compliant,
                          :audit_trail_compliant, :overall_compliant, :findings, :gaps,
                          NULL, :status, :completed_at, :integrity_hash)''', validation_data)

        if overall_compliant is True:
            recommendation = (
                "All answered controls satisfied. Readiness checklist only — "
                "not a validation, not a certification, not a compliance determination."
            )
        elif overall_compliant is False:
            recommendation = "Address the gaps before using the system in production."
        else:
            recommendation = (
                "Cannot determine readiness: some controls are unanswered. "
                "Answer every control, then re-run."
            )

        self._witness_checklist("fda_cfr11", summary)

        return {
            "label": CHECKLIST_LABEL,
            "disclaimer": DISCLAIMER,
            "validation_id": validation_id,
            "system_name": system_name,
            "overall_compliant": overall_compliant,
            "electronic_records_compliant": records_compliant,
            "electronic_signatures_compliant": signatures_compliant,
            "audit_trail_compliant": audit_trail_compliant,
            "controls_answered": summary["answered"],
            "controls_unanswered": summary["unanswered"],
            "gaps": gaps,
            "recommendation": recommendation,
        }

    @_requires_auth
    def assess_medical_ai_governance(
        self,
        ai_system: str,
        use_case: str,
        answers: Optional[Dict[str, Any]] = None,
        ask: Optional[Callable[[str, str], Any]] = None,
        risk_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Medical-AI governance checklist (NOT a regulatory assessment).

        Governance findings derive ONLY from caller-supplied answers keyed
        by control id (see checklist_controls("ai_governance")). The risk
        category is a rough keyword screening of the use case unless the
        caller supplies one — it is an estimate, not a clinical or
        regulatory determination.
        """
        assessment_id = hashlib.sha256(
            f"{ai_system}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        results = self._run_checklist(CHECKLIST_TABLES["ai_governance"], answers, ask)
        summary = self._checklist_summary(results)
        findings = self._findings_from_results(results)

        allowed_categories = ("low_risk", "moderate_risk", "high_risk", "critical_risk")
        if risk_category is None:
            risk_basis = "keyword_heuristic_estimate"
            lowered = use_case.lower()
            risk_category = "moderate_risk"
            if "autonomous" in lowered:
                risk_category = "critical_risk"
            elif "diagnostic" in lowered or "treatment" in lowered:
                risk_category = "high_risk"
            elif "scheduling" in lowered or "reminder" in lowered:
                risk_category = "low_risk"
        else:
            risk_basis = "caller_supplied"
        if risk_category not in allowed_categories:
            raise ValueError(
                f"Unknown risk_category: {risk_category!r}. "
                f"Choose from {allowed_categories}"
            )

        # Device-class screening estimate — confirm with FDA classification.
        fda_class = "not_device"
        requires_clearance = False
        if risk_category in ("high_risk", "critical_risk"):
            fda_class = "class_ii"
            requires_clearance = True
        elif risk_category == "moderate_risk":
            fda_class = "class_i"

        def _rule_flag(check_id: str) -> Optional[bool]:
            match = [r for r in results if r["check"] == check_id]
            if not match:
                return None
            status = match[0]["status"]
            return True if status == "pass" else (False if status == "fail" else None)

        recommendations = [
            f"{f['finding']} Remediation: {f['recommendation']}"
            for f in findings
        ]

        assessment_data = {
            "assessment_id": assessment_id,
            "ai_system_name": ai_system,
            "assessment_date": datetime.now().isoformat(),
            "risk_category": risk_category,
            "fda_device_class": fda_class,
            "requires_fda_clearance": requires_clearance,
            "clinical_validation_complete": _rule_flag("clinical_validation"),
            "bias_testing_complete": _rule_flag("bias_testing"),
            "drift_monitoring_enabled": _rule_flag("drift_monitoring"),
            "overall_governance_score": summary["score"],
            "findings": json.dumps({
                "label": CHECKLIST_LABEL,
                "disclaimer": DISCLAIMER,
                "controls": results,
                "findings": findings,
            }),
            "recommendations": json.dumps(recommendations),
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        }
        assessment_data["integrity_hash"] = self._generate_integrity_hash(assessment_data)

        # Save to database
        with self._db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO ai_governance_assessments VALUES
                         (:assessment_id, :ai_system_name, :assessment_date, :risk_category,
                          :fda_device_class, :requires_fda_clearance, :clinical_validation_complete,
                          :bias_testing_complete, :drift_monitoring_enabled, :overall_governance_score,
                          :findings, :recommendations, :status, :completed_at, :integrity_hash)''', assessment_data)

        self._witness_checklist("ai_governance", summary)

        return {
            "label": CHECKLIST_LABEL,
            "disclaimer": DISCLAIMER,
            "assessment_id": assessment_id,
            "ai_system": ai_system,
            "risk_category": risk_category,
            "risk_basis": risk_basis,
            "risk_note": (
                "Risk category is a rough screening estimate "
                f"({risk_basis.replace('_', ' ')}), not a clinical or "
                "regulatory determination."
            ),
            "fda_device_class": fda_class,
            "fda_device_class_note": "Estimated device class — confirm with FDA classification.",
            "requires_fda_clearance": requires_clearance,
            "governance_score": summary["score"],
            "controls_answered": summary["answered"],
            "controls_unanswered": summary["unanswered"],
            "findings": findings,
            "recommendations": recommendations,
        }

    @_requires_auth
    def generate_compliance_report(self) -> str:
        """Generate a summary of recorded self-assessment checklists.

        Aggregates the checklist audit trail. These are self-reported
        checklist runs — not audits, not certifications.
        """
        with self._db() as conn:
            c = conn.cursor()

            # Get recent checklist runs
            c.execute('''SELECT COUNT(*), AVG(overall_score), SUM(critical_issues), SUM(high_issues)
                         FROM hipaa_audits
                         WHERE audit_date >= date('now', '-30 days')''')
            hipaa_stats = c.fetchone()

            # Get recent validations
            c.execute('''SELECT COUNT(*),
                         SUM(CASE WHEN overall_compliant = 1 THEN 1 ELSE 0 END)
                         FROM fda_validations
                         WHERE validation_date >= date('now', '-30 days')''')
            fda_stats = c.fetchone()

            # Get recent AI assessments
            c.execute('''SELECT COUNT(*), AVG(overall_governance_score),
                         SUM(CASE WHEN requires_fda_clearance = 1 THEN 1 ELSE 0 END)
                         FROM ai_governance_assessments
                         WHERE assessment_date >= date('now', '-30 days')''')
            ai_stats = c.fetchone()

            # Get recent PHI incidents
            c.execute('''SELECT COUNT(*), SUM(affected_records)
                         FROM phi_incidents
                         WHERE detected_at >= date('now', '-30 days')''')
            incident_stats = c.fetchone()


        report = f"""
{'='*80}
    DRMYTHARA BOT - HEALTHCARE SELF-ASSESSMENT CHECKLIST SUMMARY
                 {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*80}

NOT A MEDICAL PROFESSIONAL. DOES NOT PROVIDE MEDICAL ADVICE.
COMPLIANCE GUIDANCE ONLY.

{CHECKLIST_LABEL}

HIPAA SELF-ASSESSMENT CHECKLISTS (Last 30 Days):
   Total Checklist Runs: {hipaa_stats[0] or 0}
   Avg Score (answered controls only): {hipaa_stats[1] or 0:.1f}%
   Critical Issues: {hipaa_stats[2] or 0}
   High Issues: {hipaa_stats[3] or 0}

FDA 21 CFR PART 11 READINESS CHECKLISTS (Last 30 Days):
   Total Checklist Runs: {fda_stats[0] or 0}
   Systems Fully Satisfied: {fda_stats[1] or 0}

MEDICAL AI GOVERNANCE CHECKLISTS (Last 30 Days):
   AI Systems Assessed: {ai_stats[0] or 0}
   Avg Governance Score: {ai_stats[1] or 0:.1f}%
   Systems Flagged as Possibly Requiring FDA Clearance: {ai_stats[2] or 0}

PHI SECURITY INCIDENTS (Last 30 Days):
   Total Incidents: {incident_stats[0] or 0}
   Affected Records: {incident_stats[1] or 0}
   {'[!] BREACH NOTIFICATION REQUIRED' if incident_stats[1] and incident_stats[1] > 500 else '[OK] No breach notification threshold reached'}

RECOMMENDATIONS:
   {'[!] Address critical HIPAA findings immediately' if hipaa_stats[2] and hipaa_stats[2] > 0 else '✓ No critical HIPAA issues'}
   {'[!] Complete FDA 21 CFR Part 11 gap remediation' if fda_stats[0] and fda_stats[1] and fda_stats[1] < fda_stats[0] else '✓ No FDA 21 CFR Part 11 gaps found (readiness checklist — not a validation)'}
   {'[!] Confirm FDA classification for flagged AI systems' if ai_stats[2] and ai_stats[2] > 0 else '✓ AI systems appropriately screened'}

{'='*80}
"""
        return report


if __name__ == "__main__":
    """Demo / self-check entry point.

    Two modes:
      DRMYTHARA_DEV=1 → throwaway demo: temp database, plaintext, demo
        login, Mythara's voice on. Nothing touches real data.
      default (strict) → needs DRMYTHARA_DATA_KEY plus DRMYTHARA_USER /
        DRMYTHARA_PASSWORD. Fails closed with setup instructions.
    """
    import tempfile

    print("DrMythara — healthcare compliance readiness, in Mythara's voice.")
    print(DISCLAIMER)
    print(CHECKLIST_LABEL)

    dev = os.environ.get("DRMYTHARA_DEV", "") == "1"
    if dev:
        tmpdir = tempfile.mkdtemp(prefix="drmythara-demo-")
        bot = DrMytharaBot(dev_mode=True,
                           db_path=os.path.join(tmpdir, "demo.db"))
        print("⚠️  DEV DEMO: throwaway plaintext database at", tmpdir)
        bot.create_user("demo", "demo-password-1234", role="admin")
        bot.login("demo", "demo-password-1234")
        # Dev chat uses the local stub (no network, no model).
        os.environ.setdefault("DRMYTHARA_LLM_PROVIDER", "stub")
    else:
        user = os.environ.get("DRMYTHARA_USER", "")
        password = os.environ.get("DRMYTHARA_PASSWORD", "")
        if not user or not password:
            print("Missing DRMYTHARA_USER / DRMYTHARA_PASSWORD.")
            print("Set them, plus DRMYTHARA_DATA_KEY, or run with "
                  "DRMYTHARA_DEV=1 for the throwaway demo.")
            raise SystemExit(2)
        try:
            bot = DrMytharaBot()
        except MissingDataKeyError as exc:
            print(exc)
            raise SystemExit(2)
        try:
            bot.login(user, password)
        except DrMytharaAuthenticationError:
            # First-run bootstrap: no users yet → create from env creds.
            with bot._db() as _c:
                from drmythara_security import UserStore as _US
                empty = _US(_c).user_count() == 0
            if empty:
                bot.create_user(user, password, role="admin")
                bot.login(user, password)
                print(f"First user {user!r} created (admin, bootstrap).")
            else:
                print("Sign-in failed.")
                raise SystemExit(2)

    print()
    print(bot.greet())
    print()

    # Canonical core consult (real reasoning — public, no sign-in needed)
    judgment = bot.consult("hipaa", {"unique_user_id": True, "encryption": True})
    print(f"[CORE CONSULT] verdict={judgment.verdict} findings={len(judgment.findings)} "
          f"rules={judgment.rule_versions}")
    print(f"[CORE CONSULT] hash verifies: {verify_judgment(judgment)}")

    # HIPAA self-assessment checklist with caller-supplied answers.
    # Every finding derives from THESE inputs — change an answer and the
    # finding changes with it.
    print(bot.voice.checklist_opening("mental health") if bot.voice else "")
    hipaa_answers = {c["check"]: True for c in bot.checklist_controls("hipaa")}
    hipaa_answers["auto_logoff"] = False  # the one failing control (caller's input)
    audit_result = bot.audit_hipaa_compliance(
        "Example Healthcare Org", answers=hipaa_answers, scope="full"
    )
    print(f"\n[HIPAA CHECKLIST] Score: {audit_result['overall_score']}% "
          f"({audit_result['controls_answered']} answered, "
          f"{audit_result['controls_unanswered']} unanswered)")
    for f in audit_result["findings"]:
        print(f"   - [{f['severity']}] {f['finding']}")

    # Mythara speaks the result — in her voice, within honest bounds.
    print()
    print(bot.narrate(audit_result))

    # Conversational chat (dev: local stub; prod: configured provider).
    chat_reply = bot.chat("Hello Mythara — what do you protect?")
    print()
    print("[CHAT]", chat_reply["reply"])
    print(f"(provider={chat_reply['provider']} "
          f"sent={chat_reply['sent_to_provider']})")

    # Generate report
    report = bot.generate_compliance_report()
    print(report)

    print("\nDrMythara run complete.")
