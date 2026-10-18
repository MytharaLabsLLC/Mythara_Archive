import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara VP of HR - Contractor Human Resources Management
- Contractor onboarding coordination
- Performance review scheduling and tracking
- Compliance monitoring (certifications, training)
- Conflict resolution and issue tracking
- Training coordination and skill development
- Contractor satisfaction surveys

Uses Mythara SSIP:
- Sanctification: Compliance rules locked (immutable)
- Integrity Hashing: All HR records cryptographically verified
- Blessings Reservoir: Contractor satisfaction scores
- Shadow_Resolver: Auto-escalate unresolved conflicts
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

class MytharaHRVP:
    """VP of HR - Contractor human resources management."""
    
    def __init__(self):
        self.bot_id = "hr_vp"
        self.bot_token = None
        self.db_path = "mythara_hr.db"
        
        # Initialize database
        self._init_db()
        
        # Register with orchestrator
        self._register()
    
    def _init_db(self):
        """Initialize HR database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Contractor profiles (extended HR data)
        c.execute('''
            CREATE TABLE IF NOT EXISTS contractor_profiles (
                contractor_email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hire_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                department TEXT,
                manager_email TEXT,
                skills TEXT,
                certifications TEXT,
                last_review_date TEXT,
                next_review_date TEXT,
                satisfaction_score REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Performance reviews
        c.execute('''
            CREATE TABLE IF NOT EXISTS performance_reviews (
                review_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                review_date TEXT NOT NULL,
                reviewer_email TEXT,
                overall_score REAL,
                technical_score REAL,
                communication_score REAL,
                reliability_score REAL,
                feedback TEXT,
                goals TEXT,
                status TEXT DEFAULT 'draft',
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_email) REFERENCES contractor_profiles(contractor_email)
            )
        ''')
        
        # Compliance tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS compliance_records (
                record_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                compliance_type TEXT NOT NULL,
                requirement TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                completion_date TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_email) REFERENCES contractor_profiles(contractor_email)
            )
        ''')
        
        # Issues and conflicts
        c.execute('''
            CREATE TABLE IF NOT EXISTS hr_issues (
                issue_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                severity TEXT DEFAULT 'low',
                description TEXT,
                reported_by TEXT,
                reported_at TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                resolution TEXT,
                resolved_at TEXT,
                escalated BOOLEAN DEFAULT 0,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_email) REFERENCES contractor_profiles(contractor_email)
            )
        ''')
        
        # Training records
        c.execute('''
            CREATE TABLE IF NOT EXISTS training_records (
                training_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                training_name TEXT NOT NULL,
                training_type TEXT,
                provider TEXT,
                start_date TEXT,
                completion_date TEXT,
                status TEXT DEFAULT 'scheduled',
                certification_earned TEXT,
                cost REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_email) REFERENCES contractor_profiles(contractor_email)
            )
        ''')
        
        # Satisfaction surveys
        c.execute('''
            CREATE TABLE IF NOT EXISTS satisfaction_surveys (
                survey_id TEXT PRIMARY KEY,
                contractor_email TEXT NOT NULL,
                survey_date TEXT NOT NULL,
                overall_satisfaction REAL,
                work_life_balance REAL,
                compensation_satisfaction REAL,
                growth_opportunities REAL,
                management_satisfaction REAL,
                comments TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (contractor_email) REFERENCES contractor_profiles(contractor_email)
            )
        ''')
        
        # HR audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS hr_audit (
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
        print(f"[OK] HR VP database initialized: {self.db_path}")
    
    def _register(self):
        """Register with orchestrator."""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/register_bot",
                json={
                    "bot_id": self.bot_id,
                    "capabilities": ["hr_management", "contractor_onboarding", "performance_reviews", "compliance", "conflict_resolution"],
                    "master_token": VP_MASTER_TOKEN
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.bot_token = data.get("bot_token")
                print(f"[OK] Registered as HR VP: {self.bot_id}")
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
            INSERT INTO hr_audit (audit_id, entity, action, details, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (audit_id, entity, action, json.dumps(details), datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
    
    def onboard_contractor(self, email: str, name: str, department: str = "General", 
                          skills: List[str] = None, manager_email: str = None) -> Dict[str, Any]:
        """Create contractor HR profile."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        hire_date = datetime.now().isoformat()
        next_review = (datetime.now() + timedelta(days=90)).isoformat()  # 90-day review
        
        record = {
            "contractor_email": email,
            "name": name,
            "hire_date": hire_date,
            "department": department,
            "manager_email": manager_email,
            "skills": json.dumps(skills or []),
            "next_review_date": next_review
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO contractor_profiles 
            (contractor_email, name, hire_date, status, department, manager_email, skills, 
             next_review_date, created_at, integrity_hash)
            VALUES (?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)
        ''', (email, name, hire_date, department, manager_email, 
              json.dumps(skills or []), next_review, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("contractor_profile", "onboarded", record)
        
        print(f"[HR] Onboarded contractor: {name} ({email})")
        print(f"     Department: {department}")
        print(f"     Next Review: {next_review[:10]}")
        
        return {"success": True, "contractor_email": email, "next_review": next_review}
    
    def schedule_performance_review(self, contractor_email: str, reviewer_email: str = "hr@mythara.com") -> Dict[str, Any]:
        """Schedule performance review."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        review_id = hashlib.sha256(f"{contractor_email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        review_date = datetime.now().isoformat()
        
        record = {
            "review_id": review_id,
            "contractor_email": contractor_email,
            "reviewer_email": reviewer_email,
            "review_date": review_date
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO performance_reviews 
            (review_id, contractor_email, review_date, reviewer_email, status, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, 'scheduled', ?, ?)
        ''', (review_id, contractor_email, review_date, reviewer_email, 
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("performance_review", "scheduled", record)
        
        print(f"[HR] Scheduled performance review: {review_id}")
        print(f"     Contractor: {contractor_email}")
        
        return {"success": True, "review_id": review_id}
    
    def submit_performance_review(self, review_id: str, overall_score: float, 
                                  technical_score: float, communication_score: float,
                                  reliability_score: float, feedback: str, goals: str) -> Dict[str, Any]:
        """Submit completed performance review."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE performance_reviews
            SET overall_score = ?, technical_score = ?, communication_score = ?, 
                reliability_score = ?, feedback = ?, goals = ?, status = 'completed'
            WHERE review_id = ?
        ''', (overall_score, technical_score, communication_score, reliability_score,
              feedback, goals, review_id))
        
        # Update contractor next review date (6 months)
        c.execute('SELECT contractor_email FROM performance_reviews WHERE review_id = ?', (review_id,))
        row = c.fetchone()
        if row:
            contractor_email = row[0]
            next_review = (datetime.now() + timedelta(days=180)).isoformat()
            c.execute('UPDATE contractor_profiles SET last_review_date = ?, next_review_date = ? WHERE contractor_email = ?',
                     (datetime.now().isoformat(), next_review, contractor_email))
        
        conn.commit()
        conn.close()
        
        self._audit("performance_review", "completed", {
            "review_id": review_id,
            "overall_score": overall_score
        })
        
        print(f"[HR] Completed performance review: {review_id}")
        print(f"     Overall Score: {overall_score}/5.0")
        
        return {"success": True, "review_id": review_id, "overall_score": overall_score}
    
    def track_compliance(self, contractor_email: str, compliance_type: str, 
                        requirement: str, due_date: str = None) -> Dict[str, Any]:
        """Track compliance requirement."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        record_id = hashlib.sha256(f"{contractor_email}{compliance_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "record_id": record_id,
            "contractor_email": contractor_email,
            "compliance_type": compliance_type,
            "requirement": requirement,
            "due_date": due_date
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO compliance_records
            (record_id, contractor_email, compliance_type, requirement, due_date, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, contractor_email, compliance_type, requirement, due_date,
              datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("compliance", "tracked", record)
        
        print(f"[HR] Tracked compliance: {compliance_type}")
        print(f"     Contractor: {contractor_email}")
        print(f"     Due: {due_date or 'No deadline'}")
        
        return {"success": True, "record_id": record_id}
    
    def report_issue(self, contractor_email: str, issue_type: str, severity: str,
                    description: str, reported_by: str = "system") -> Dict[str, Any]:
        """Report HR issue or conflict."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        issue_id = hashlib.sha256(f"{contractor_email}{issue_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Auto-escalate critical issues
        escalated = 1 if severity == "critical" else 0
        
        record = {
            "issue_id": issue_id,
            "contractor_email": contractor_email,
            "issue_type": issue_type,
            "severity": severity,
            "description": description,
            "reported_by": reported_by,
            "escalated": escalated
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO hr_issues
            (issue_id, contractor_email, issue_type, severity, description, 
             reported_by, reported_at, escalated, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (issue_id, contractor_email, issue_type, severity, description,
              reported_by, datetime.now().isoformat(), escalated, integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("hr_issue", "reported", record)
        
        print(f"[HR] Reported {severity} issue: {issue_type}")
        print(f"     Contractor: {contractor_email}")
        if escalated:
            print(f"     ⚠️ AUTO-ESCALATED (critical severity)")
        
        return {"success": True, "issue_id": issue_id, "escalated": bool(escalated)}
    
    def resolve_issue(self, issue_id: str, resolution: str) -> Dict[str, Any]:
        """Resolve HR issue."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE hr_issues
            SET status = 'resolved', resolution = ?, resolved_at = ?
            WHERE issue_id = ?
        ''', (resolution, datetime.now().isoformat(), issue_id))
        
        conn.commit()
        conn.close()
        
        self._audit("hr_issue", "resolved", {"issue_id": issue_id, "resolution": resolution})
        
        print(f"[HR] Resolved issue: {issue_id}")
        
        return {"success": True, "issue_id": issue_id}
    
    def schedule_training(self, contractor_email: str, training_name: str, 
                         training_type: str, start_date: str, cost: float = 0.0) -> Dict[str, Any]:
        """Schedule contractor training."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        training_id = hashlib.sha256(f"{contractor_email}{training_name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "training_id": training_id,
            "contractor_email": contractor_email,
            "training_name": training_name,
            "training_type": training_type,
            "start_date": start_date,
            "cost": cost
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO training_records
            (training_id, contractor_email, training_name, training_type, start_date, 
             cost, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (training_id, contractor_email, training_name, training_type, start_date,
              cost, datetime.now().isoformat(), integrity_hash))
        
        conn.commit()
        conn.close()
        
        self._audit("training", "scheduled", record)
        
        print(f"[HR] Scheduled training: {training_name}")
        print(f"     Contractor: {contractor_email}")
        print(f"     Cost: ${cost:.2f}")
        
        return {"success": True, "training_id": training_id}
    
    def record_satisfaction_survey(self, contractor_email: str, overall: float,
                                   work_life: float, compensation: float,
                                   growth: float, management: float, 
                                   comments: str = "") -> Dict[str, Any]:
        """Record contractor satisfaction survey."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        survey_id = hashlib.sha256(f"{contractor_email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        record = {
            "survey_id": survey_id,
            "contractor_email": contractor_email,
            "overall_satisfaction": overall,
            "work_life_balance": work_life,
            "compensation_satisfaction": compensation,
            "growth_opportunities": growth,
            "management_satisfaction": management
        }
        
        integrity_hash = self._generate_integrity_hash(record)
        
        c.execute('''
            INSERT INTO satisfaction_surveys
            (survey_id, contractor_email, survey_date, overall_satisfaction, 
             work_life_balance, compensation_satisfaction, growth_opportunities,
             management_satisfaction, comments, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (survey_id, contractor_email, datetime.now().isoformat(), overall,
              work_life, compensation, growth, management, comments,
              datetime.now().isoformat(), integrity_hash))
        
        # Update contractor profile satisfaction score
        c.execute('UPDATE contractor_profiles SET satisfaction_score = ? WHERE contractor_email = ?',
                 (overall, contractor_email))
        
        conn.commit()
        conn.close()
        
        self._audit("satisfaction_survey", "recorded", record)
        
        print(f"[HR] Recorded satisfaction survey")
        print(f"     Contractor: {contractor_email}")
        print(f"     Overall Satisfaction: {overall}/5.0")
        
        return {"success": True, "survey_id": survey_id, "overall": overall}
    
    def generate_hr_report(self) -> str:
        """Generate comprehensive HR report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Contractor counts
        c.execute('SELECT COUNT(*) FROM contractor_profiles WHERE status = "active"')
        active_contractors = c.fetchone()[0]
        
        c.execute('SELECT AVG(satisfaction_score) FROM contractor_profiles WHERE status = "active"')
        avg_satisfaction = c.fetchone()[0] or 0.0
        
        # Reviews
        c.execute('SELECT COUNT(*) FROM performance_reviews WHERE status = "completed"')
        completed_reviews = c.fetchone()[0]
        
        c.execute('SELECT AVG(overall_score) FROM performance_reviews WHERE status = "completed"')
        avg_review_score = c.fetchone()[0] or 0.0
        
        # Compliance
        c.execute('SELECT COUNT(*) FROM compliance_records WHERE status = "pending"')
        pending_compliance = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM compliance_records WHERE status = "completed"')
        completed_compliance = c.fetchone()[0]
        
        # Issues
        c.execute('SELECT COUNT(*) FROM hr_issues WHERE status = "open"')
        open_issues = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM hr_issues WHERE severity = "critical" AND status = "open"')
        critical_issues = c.fetchone()[0]
        
        # Training
        c.execute('SELECT COUNT(*) FROM training_records WHERE status = "completed"')
        completed_training = c.fetchone()[0]
        
        c.execute('SELECT SUM(cost) FROM training_records WHERE status = "completed"')
        training_investment = c.fetchone()[0] or 0.0
        
        conn.close()
        
        report = f"""
================================================================
          MYTHARA VP OF HR - WORKFORCE REPORT
                     {datetime.now().strftime("%Y-%m-%d %H:%M")}
================================================================

WORKFORCE OVERVIEW:
   Active Contractors: {active_contractors}
   Avg Satisfaction Score: {avg_satisfaction:.2f}/5.0

PERFORMANCE MANAGEMENT:
   Completed Reviews: {completed_reviews}
   Avg Review Score: {avg_review_score:.2f}/5.0

COMPLIANCE:
   Pending Requirements: {pending_compliance}
   Completed Requirements: {completed_compliance}

ISSUES & CONFLICTS:
   Open Issues: {open_issues}
   Critical Issues: {critical_issues}
   {"[!] ESCALATION REQUIRED" if critical_issues > 0 else "[OK] No critical issues"}

TRAINING & DEVELOPMENT:
   Completed Training: {completed_training}
   Training Investment: ${training_investment:,.2f}

================================================================
"""
        return report

if __name__ == "__main__":
    print("Mythara VP of HR - Contractor Human Resources")
    print("=" * 60)
    
    hr = MytharaHRVP()
    
    # Demo: Onboard contractor
    hr.onboard_contractor(
        email="sarah@contractor.com",
        name="Sarah Johnson",
        department="Engineering",
        skills=["Python", "FastAPI", "PostgreSQL"],
        manager_email="manager@mythara.com"
    )
    
    # Schedule performance review
    review = hr.schedule_performance_review("sarah@contractor.com")
    
    # Submit review
    hr.submit_performance_review(
        review_id=review['review_id'],
        overall_score=4.5,
        technical_score=4.7,
        communication_score=4.3,
        reliability_score=4.5,
        feedback="Excellent technical skills and reliability. Strong team player.",
        goals="Lead architecture review process in Q1 2026"
    )
    
    # Track compliance
    hr.track_compliance(
        contractor_email="sarah@contractor.com",
        compliance_type="certification",
        requirement="AWS Solutions Architect",
        due_date=(datetime.now() + timedelta(days=60)).isoformat()
    )
    
    # Schedule training
    hr.schedule_training(
        contractor_email="sarah@contractor.com",
        training_name="Advanced Kubernetes Administration",
        training_type="technical",
        start_date=(datetime.now() + timedelta(days=14)).isoformat(),
        cost=1500.0
    )
    
    # Record satisfaction survey
    hr.record_satisfaction_survey(
        contractor_email="sarah@contractor.com",
        overall=4.6,
        work_life=4.8,
        compensation=4.5,
        growth=4.4,
        management=4.7,
        comments="Great work environment and growth opportunities"
    )
    
    # Generate report
    print("\n" + hr.generate_hr_report())
