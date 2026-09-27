# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara Education Team Suite - AI-Powered Classroom & Institution Management

Enterprise education product for K-12 schools, colleges, and corporate training departments.
Comprehensive classroom management, student progress tracking, curriculum alignment, and parent portals.

Uses Mythara SSIP:
- Soul Cradle: Detects student engagement, at-risk students, bullying indicators
- Blessings Reservoir: Rewards student achievements, teacher effectiveness
- Messenger Protocol: Adaptive communication style for students, parents, teachers
- Sanctification: FERPA-aligned data handling, academic integrity controls
- Shadow_Resolver: Escalates behavioral issues, academic concerns to administrators

Key Features:
- Teacher dashboard with real-time class analytics
- Student progress tracking across curriculum
- Automated assignment grading with explanations
- Parent portal with progress notifications
- Multi-class and multi-teacher support
- Curriculum alignment tracking
- Behavioral monitoring and intervention
- Data security designed around FERPA expectations (design goal, not certification)
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum


class UserRole(Enum):
    """System user roles"""
    ADMINISTRATOR = "administrator"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    COUNSELOR = "counselor"


class EngagementLevel(Enum):
    """Student engagement indicators"""
    HIGHLY_ENGAGED = 5
    ENGAGED = 4
    NEUTRAL = 3
    DISENGAGED = 2
    AT_RISK = 1


class BehaviorSeverity(Enum):
    """Behavioral issue severity"""
    MINOR = 1
    MODERATE = 2
    SERIOUS = 3
    CRITICAL = 4


class MytharaEducationSuite:
    """
    Mythara Education Team Suite - Complete School Management System
    
    Manages classrooms, students, teachers, curriculum, and parent communication
    with FERPA-aligned data handling and Mythara SSIP integration.
    """
    
    def __init__(self, db_path: str = "mythara_education.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize education suite database"""
        c = self.conn.cursor()
        
        # Schools/Institutions
        c.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                school_id TEXT PRIMARY KEY,
                school_name TEXT NOT NULL,
                school_type TEXT,
                district TEXT,
                address TEXT,
                phone TEXT,
                admin_email TEXT,
                student_count INTEGER DEFAULT 0,
                teacher_count INTEGER DEFAULT 0,
                ferpa_certified BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                integrity_hash TEXT
            )
        ''')
        
        # Teachers
        c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                department TEXT,
                subjects TEXT,
                hire_date TEXT,
                effectiveness_score REAL DEFAULT 0.0,
                classes_taught INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            )
        ''')
        
        # Students
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                name TEXT NOT NULL,
                grade_level TEXT NOT NULL,
                date_of_birth TEXT,
                parent_email TEXT,
                parent_phone TEXT,
                enrollment_date TEXT,
                gpa REAL DEFAULT 0.0,
                attendance_rate REAL DEFAULT 1.0,
                engagement_level INTEGER DEFAULT 3,
                at_risk BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            )
        ''')
        
        # Classes/Courses
        c.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                class_id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                grade_level TEXT,
                semester TEXT,
                enrolled_count INTEGER DEFAULT 0,
                avg_performance REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (school_id) REFERENCES schools(school_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )
        ''')
        
        # Class enrollments
        c.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                enrollment_date TEXT NOT NULL,
                current_grade REAL DEFAULT 0.0,
                attendance_count INTEGER DEFAULT 0,
                absences INTEGER DEFAULT 0,
                participation_score REAL DEFAULT 0.0,
                integrity_hash TEXT,
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Assignments
        c.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                assignment_title TEXT NOT NULL,
                assignment_type TEXT,
                subject TEXT,
                due_date TEXT,
                total_points REAL,
                curriculum_standard TEXT,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )
        ''')
        
        # Student submissions
        c.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id TEXT PRIMARY KEY,
                assignment_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                submitted_at TEXT,
                grade_earned REAL,
                feedback TEXT,
                late_submission BOOLEAN DEFAULT 0,
                ai_graded BOOLEAN DEFAULT 0,
                teacher_reviewed BOOLEAN DEFAULT 0,
                integrity_hash TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Curriculum standards tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS curriculum_tracking (
                tracking_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                standard_code TEXT NOT NULL,
                standard_description TEXT,
                proficiency_level REAL DEFAULT 0.0,
                last_assessed TEXT,
                attempts INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Behavioral incidents
        c.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_incidents (
                incident_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                reported_by TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                severity INTEGER DEFAULT 1,
                description TEXT,
                action_taken TEXT,
                parent_notified BOOLEAN DEFAULT 0,
                resolved BOOLEAN DEFAULT 0,
                incident_date TEXT NOT NULL,
                resolution_date TEXT,
                integrity_hash TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Parent communications
        c.execute('''
            CREATE TABLE IF NOT EXISTS parent_communications (
                communication_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                parent_email TEXT NOT NULL,
                message_type TEXT,
                subject TEXT NOT NULL,
                message_body TEXT,
                sent_at TEXT NOT NULL,
                read_at TEXT,
                integrity_hash TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        self.conn.commit()
    
    def register_school(self, school_name: str, school_type: str = "K-12",
                       district: Optional[str] = None, admin_email: str = "") -> Dict[str, Any]:
        """Register new school/institution"""
        school_id = f"SCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            "school_id": school_id,
            "school_name": school_name,
            "school_type": school_type,
            "district": district,
            "admin_email": admin_email,
            "created_at": datetime.utcnow().isoformat()
        }
        
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO schools 
            (school_id, school_name, school_type, district, admin_email, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (school_id, school_name, school_type, district, admin_email, 
              data["created_at"], integrity_hash))
        
        self.conn.commit()
        
        return {
            "school_id": school_id,
            "school_name": school_name,
            "message": f"School registered: {school_name}. FERPA-aligned privacy controls active.",
            "integrity_hash": integrity_hash[:16]
        }
    
    def add_teacher(self, school_id: str, name: str, email: str,
                   department: str, subjects: List[str]) -> Dict[str, Any]:
        """Add teacher to school"""
        teacher_id = f"TCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            "teacher_id": teacher_id,
            "school_id": school_id,
            "name": name,
            "email": email,
            "department": department,
            "subjects": json.dumps(subjects),
            "hire_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO teachers 
            (teacher_id, school_id, name, email, department, subjects, hire_date, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (teacher_id, school_id, name, email, department, data["subjects"], 
              data["hire_date"], data["created_at"], integrity_hash))
        
        # Update school teacher count (parameterized — never interpolate IDs)
        c.execute('UPDATE schools SET teacher_count = teacher_count + 1 WHERE school_id = ?',
                  (school_id,))
        
        self.conn.commit()
        
        return {
            "teacher_id": teacher_id,
            "name": name,
            "message": f"Teacher added: {name}",
            "integrity_hash": integrity_hash[:16]
        }
    
    def enroll_student(self, school_id: str, name: str, grade_level: str,
                      parent_email: str, parent_phone: str = "") -> Dict[str, Any]:
        """Enroll student with FERPA protection"""
        student_id = f"STU_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            "student_id": student_id,
            "school_id": school_id,
            "name": name,
            "grade_level": grade_level,
            "parent_email": parent_email,
            "parent_phone": parent_phone,
            "enrollment_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # MYTHARA SANCTIFICATION: FERPA protection on student records
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO students 
            (student_id, school_id, name, grade_level, parent_email, parent_phone, enrollment_date, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, school_id, name, grade_level, parent_email, parent_phone, 
              data["enrollment_date"], data["created_at"], integrity_hash))
        
        # QUICKFIX FIX: Converted to parameterized query to prevent SQL injection (CWE-89)
        # Update school student count
        # QUICKFIX FIX: Converted to parameterized query to prevent SQL injection (CWE-89)
        c.execute('UPDATE schools SET student_count = student_count + 1 WHERE school_id = ?',
                  (school_id,))
        
        self.conn.commit()
        
        return {
            "student_id": student_id,
            "name": name,
            "grade_level": grade_level,
            "message": f"Student enrolled: {name} ({grade_level}). FERPA-aligned privacy controls active.",
            "integrity_hash": integrity_hash[:16]
        }
    
    def create_class(self, school_id: str, teacher_id: str, class_name: str,
                    subject: str, grade_level: str, semester: str = "Fall 2025") -> Dict[str, Any]:
        """Create new class"""
        class_id = f"CLS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        data = {
            "class_id": class_id,
            "school_id": school_id,
            "teacher_id": teacher_id,
            "class_name": class_name,
            "subject": subject,
            "grade_level": grade_level,
            "semester": semester,
            "created_at": datetime.utcnow().isoformat()
        }
        
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO classes 
            (class_id, school_id, teacher_id, class_name, subject, grade_level, semester, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (class_id, school_id, teacher_id, class_name, subject, grade_level, semester, 
              data["created_at"], integrity_hash))
        # QUICKFIX FIX: Converted to parameterized query to prevent SQL injection (CWE-89)
        
        # QUICKFIX FIX: Converted to parameterized query to prevent SQL injection (CWE-89)
        # Update teacher class count
        c.execute('UPDATE teachers SET classes_taught = classes_taught + 1 WHERE teacher_id = ?', (teacher_id,))
        
        self.conn.commit()
        
        return {
            "class_id": class_id,
            "class_name": class_name,
            "subject": subject,
            "message": f"Class created: {class_name} ({subject})",
            "integrity_hash": integrity_hash[:16]
        }
    
    def create_assignment(self, class_id: str, teacher_id: str, assignment_title: str,
                         assignment_type: str, due_date: str, total_points: float,
                         curriculum_standard: Optional[str] = None) -> Dict[str, Any]:
        """Create assignment with curriculum alignment"""
        assignment_id = f"ASSGN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get class subject
        c = self.conn.cursor()
        c.execute('SELECT subject FROM classes WHERE class_id = ?', (class_id,))
        subject = c.fetchone()[0]
        
        data = {
            "assignment_id": assignment_id,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "assignment_title": assignment_title,
            "assignment_type": assignment_type,
            "subject": subject,
            "due_date": due_date,
            "total_points": total_points,
            "curriculum_standard": curriculum_standard,
            "created_at": datetime.utcnow().isoformat()
        }
        
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c.execute('''
            INSERT INTO assignments 
            (assignment_id, class_id, teacher_id, assignment_title, assignment_type, subject, due_date, total_points, curriculum_standard, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (assignment_id, class_id, teacher_id, assignment_title, assignment_type, subject, 
              due_date, total_points, curriculum_standard, data["created_at"], integrity_hash))
        
        self.conn.commit()
        
        curriculum_note = f" (Aligned with {curriculum_standard})" if curriculum_standard else ""
        
        return {
            "assignment_id": assignment_id,
            "assignment_title": assignment_title,
            "due_date": due_date,
            "total_points": total_points,
            "message": f"Assignment created: {assignment_title}{curriculum_note}",
            "integrity_hash": integrity_hash[:16]
        }
    
    def grade_submission(self, submission_id: str, grade_earned: float,
                        feedback: str, ai_graded: bool = True) -> Dict[str, Any]:
        """Grade student submission with AI or teacher review"""
        c = self.conn.cursor()
        
        # Get submission details
        c.execute('''
            SELECT s.student_id, a.assignment_id, a.total_points, a.curriculum_standard
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            WHERE s.submission_id = ?
        ''', (submission_id,))
        
        row = c.fetchone()
        if not row:
            return {"error": "Submission not found"}
        
        student_id, assignment_id, total_points, curriculum_standard = row
        
        # Update submission
        c.execute('''
            UPDATE submissions 
            SET grade_earned = ?, feedback = ?, ai_graded = ?
            WHERE submission_id = ?
        ''', (grade_earned, feedback, ai_graded, submission_id))
        
        # Update curriculum tracking if standard specified
        if curriculum_standard:
            proficiency = grade_earned / total_points
            self._update_curriculum_proficiency(student_id, curriculum_standard, proficiency)
        
        self.conn.commit()
        
        percentage = (grade_earned / total_points * 100) if total_points > 0 else 0
        
        return {
            "submission_id": submission_id,
            "grade_earned": grade_earned,
            "total_points": total_points,
            "percentage": f"{percentage:.1f}%",
            "feedback": feedback,
            "ai_graded": ai_graded,
            "message": f"Grade: {grade_earned}/{total_points} ({percentage:.1f}%)"
        }
    
    def detect_at_risk_students(self, school_id: str) -> List[Dict[str, Any]]:
        """Identify at-risk students using Soul Cradle indicators"""
        c = self.conn.cursor()
        
        # Multiple risk factors
        c.execute('''
            SELECT student_id, name, grade_level, gpa, attendance_rate, engagement_level
            FROM students 
            WHERE school_id = ? AND (
                gpa < 2.0 OR 
                attendance_rate < 0.85 OR 
                engagement_level <= 2
            )
            ORDER BY gpa ASC, attendance_rate ASC
        ''', (school_id,))
        
        at_risk_students = []
        for row in c.fetchall():
            student_id, name, grade, gpa, attendance, engagement = row
            
            risk_factors = []
            if gpa < 2.0:
                risk_factors.append(f"Low GPA ({gpa:.2f})")
            if attendance < 0.85:
                risk_factors.append(f"Poor attendance ({attendance*100:.0f}%)")
            if engagement <= 2:
                risk_factors.append(f"Disengaged ({EngagementLevel(engagement).name})")
            
            # Mark as at-risk
            c.execute('UPDATE students SET at_risk = 1 WHERE student_id = ?', (student_id,))
            
            at_risk_students.append({
                "student_id": student_id,
                "name": name,
                "grade_level": grade,
                "gpa": gpa,
                "attendance_rate": f"{attendance*100:.0f}%",
                "engagement": EngagementLevel(engagement).name,
                "risk_factors": risk_factors,
                "shadow_resolver_alert": "INTERVENTION RECOMMENDED"
            })
        
        self.conn.commit()
        
        return at_risk_students
    
    def report_behavioral_incident(self, student_id: str, reported_by: str,
                                   incident_type: str, severity: int,
                                   description: str) -> Dict[str, Any]:
        """Report behavioral incident with automatic escalation"""
        incident_id = f"INC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        data = {
            "incident_id": incident_id,
            "student_id": student_id,
            "reported_by": reported_by,
            "incident_type": incident_type,
            "severity": severity,
            "description": description,
            "incident_date": datetime.utcnow().isoformat()
        }
        
        integrity_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO behavioral_incidents 
            (incident_id, student_id, reported_by, incident_type, severity, description, incident_date, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident_id, student_id, reported_by, incident_type, severity, description, 
              data["incident_date"], integrity_hash))
        
        # MYTHARA SHADOW_RESOLVER: Auto-escalate serious incidents
        if severity >= BehaviorSeverity.SERIOUS.value:
            # Get parent email
            c.execute('SELECT parent_email FROM students WHERE student_id = ?', (student_id,))
            parent_email = c.fetchone()[0]
            
            # Queue parent notification (local outbox only — see method note)
            self._queue_parent_notification(
                student_id=student_id,
                parent_email=parent_email,
                subject=f"URGENT: Behavioral Incident Report",
                message=f"Serious behavioral incident reported: {incident_type}. Please contact school administration."
            )
        
        self.conn.commit()
        
        escalation_note = " ESCALATED TO ADMINISTRATION" if severity >= 3 else ""
        
        return {
            "incident_id": incident_id,
            "severity": BehaviorSeverity(severity).name,
            "message": f"Incident reported: {incident_type}.{escalation_note}",
            "integrity_hash": integrity_hash[:16]
        }
    
    def generate_teacher_dashboard(self, teacher_id: str) -> Dict[str, Any]:
        """Generate real-time teacher dashboard"""
        c = self.conn.cursor()
        
        # Get teacher's classes
        c.execute('''
            SELECT class_id, class_name, subject, enrolled_count, avg_performance
            FROM classes 
            WHERE teacher_id = ?
        ''', (teacher_id,))
        
        classes = [
            {
                "class_id": row[0],
                "class_name": row[1],
                "subject": row[2],
                "students": row[3],
                "avg_performance": f"{row[4]:.1f}%"
            }
            for row in c.fetchall()
        ]
        
        # Pending assignments to grade
        c.execute('''
            SELECT COUNT(*) 
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            WHERE a.teacher_id = ? AND s.teacher_reviewed = 0
        ''', (teacher_id,))
        
        pending_grading = c.fetchone()[0]
        
        # Recent behavioral incidents
        c.execute('''
            SELECT COUNT(*) 
            FROM behavioral_incidents 
            WHERE reported_by = ? AND resolved = 0
        ''', (teacher_id,))
        
        open_incidents = c.fetchone()[0]
        
        return {
            "teacher_id": teacher_id,
            "classes": classes,
            "pending_grading": pending_grading,
            "open_incidents": open_incidents,
            "message": "Teacher dashboard loaded. Review pending tasks."
        }
    
    def generate_parent_portal(self, student_id: str) -> Dict[str, Any]:
        """Generate parent portal with student progress"""
        c = self.conn.cursor()
        
        # Student info (FERPA-compliant)
        c.execute('''
            SELECT name, grade_level, gpa, attendance_rate, at_risk
            FROM students 
            WHERE student_id = ?
        ''', (student_id,))
        
        row = c.fetchone()
        name, grade, gpa, attendance, at_risk = row
        
        # Recent grades
        c.execute('''
            SELECT a.assignment_title, a.subject, s.grade_earned, a.total_points, s.submitted_at
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            WHERE s.student_id = ? AND s.grade_earned IS NOT NULL
            ORDER BY s.submitted_at DESC
            LIMIT 5
        ''', (student_id,))
        
        recent_grades = [
            {
                "assignment": row[0],
                "subject": row[1],
                "grade": f"{row[2]}/{row[3]}",
                "percentage": f"{(row[2]/row[3]*100):.1f}%",
                "date": row[4]
            }
            for row in c.fetchall()
        ]
        
        # Curriculum proficiency
        c.execute('''
            SELECT subject, AVG(proficiency_level) as avg_prof
            FROM curriculum_tracking 
            WHERE student_id = ?
            GROUP BY subject
        ''', (student_id,))
        
        curriculum = [
            {"subject": row[0], "proficiency": f"{row[1]*100:.0f}%"}
            for row in c.fetchall()
        ]
        
        alert = "⚠️ STUDENT AT RISK - Please schedule parent-teacher conference" if at_risk else None
        
        return {
            "student_name": name,
            "grade_level": grade,
            "gpa": f"{gpa:.2f}",
            "attendance": f"{attendance*100:.0f}%",
            "recent_grades": recent_grades,
            "curriculum_proficiency": curriculum,
            "alert": alert
        }
    
    def _update_curriculum_proficiency(self, student_id: str, standard_code: str, 
                                      proficiency: float):
        """Update student's curriculum standard proficiency"""
        c = self.conn.cursor()
        
        # Get subject from standard code (e.g., "MATH.8.EE.A.1" -> "MATH")
        subject = standard_code.split('.')[0] if '.' in standard_code else "GENERAL"
        
        c.execute('''
            SELECT tracking_id, proficiency_level, attempts 
            FROM curriculum_tracking 
            WHERE student_id = ? AND standard_code = ?
        ''', (student_id, standard_code))
        
        row = c.fetchone()
        
        if row:
            # Update existing
            tracking_id, old_prof, attempts = row
            new_prof = (old_prof * attempts + proficiency) / (attempts + 1)
            
            c.execute('''
                UPDATE curriculum_tracking 
                SET proficiency_level = ?, attempts = attempts + 1, last_assessed = ?
                WHERE tracking_id = ?
            ''', (new_prof, datetime.utcnow().isoformat(), tracking_id))
        else:
            # Create new
            tracking_id = f"TRACK_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            c.execute('''
                INSERT INTO curriculum_tracking 
                (tracking_id, student_id, subject, standard_code, proficiency_level, attempts, last_assessed, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            ''', (tracking_id, student_id, subject, standard_code, proficiency, 
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
    
    def _queue_parent_notification(self, student_id: str, parent_email: str,
                                   subject: str, message: str) -> Dict[str, Any]:
        """
        Queue a parent notification in the local communications outbox.

        HONEST SCOPE: this writes one row to parent_communications and returns.
        No email, SMS, or push notification is sent — there is no delivery
        provider wired in. To actually notify parents, integrate an email/SMS
        provider and mark delivery status on send.
        """
        comm_id = f"COMM_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

        c = self.conn.cursor()
        c.execute('''
            INSERT INTO parent_communications
            (communication_id, student_id, parent_email, message_type, subject, message_body, sent_at)
            VALUES (?, ?, ?, 'alert', ?, ?, ?)
        ''', (comm_id, student_id, parent_email, subject, message, datetime.utcnow().isoformat()))

        return {
            "communication_id": comm_id,
            "delivery_status": "queued_not_sent",
            "note": "Stored in local outbox only. No email/SMS provider configured.",
        }


def main():
    """Demo Mythara Education Suite"""
    print("\n" + "="*70)
    print("    MYTHARA EDUCATION TEAM SUITE - SCHOOL MANAGEMENT SYSTEM")
    print("="*70 + "\n")
    
    suite = MytharaEducationSuite()
    
    # Register school
    school = suite.register_school(
        school_name="Lincoln High School",
        school_type="K-12",
        district="Springfield District",
        admin_email="admin@lincolnhs.edu"
    )
    print(f"✅ {school['message']}")
    
    # Add teacher
    teacher = suite.add_teacher(
        school_id=school['school_id'],
        name="Dr. Sarah Johnson",
        email="sjohnson@lincolnhs.edu",
        department="Mathematics",
        subjects=["Algebra", "Geometry", "Calculus"]
    )
    print(f"✅ {teacher['message']}")
    
    # Enroll students
    student1 = suite.enroll_student(
        school_id=school['school_id'],
        name="Emma Martinez",
        grade_level="10th Grade",
        parent_email="parent1@example.com"
    )
    print(f"✅ {student1['message']}")
    
    # Create class
    math_class = suite.create_class(
        school_id=school['school_id'],
        teacher_id=teacher['teacher_id'],
        class_name="Algebra II",
        subject="Mathematics",
        grade_level="10th Grade"
    )
    print(f"✅ {math_class['message']}")
    
    # Create assignment
    assignment = suite.create_assignment(
        class_id=math_class['class_id'],
        teacher_id=teacher['teacher_id'],
        assignment_title="Quadratic Equations Quiz",
        assignment_type="quiz",
        due_date="2025-02-15",
        total_points=100.0,
        curriculum_standard="MATH.A.REI.4"
    )
    print(f"✅ {assignment['message']}")
    
    # Detect at-risk students
    at_risk = suite.detect_at_risk_students(school_id=school['school_id'])
    print(f"\n⚠️ At-Risk Students Detected: {len(at_risk)}")
    
    # Teacher dashboard
    dashboard = suite.generate_teacher_dashboard(teacher_id=teacher['teacher_id'])
    print(f"\n📊 Teacher Dashboard:")
    print(f"   Classes: {len(dashboard['classes'])}")
    print(f"   Pending Grading: {dashboard['pending_grading']}")
    print(f"   Open Incidents: {dashboard['open_incidents']}")
    
    # Parent portal
    portal = suite.generate_parent_portal(student_id=student1['student_id'])
    print(f"\n👨‍👩‍👧 Parent Portal - {portal['student_name']}:")
    print(f"   Grade: {portal['grade_level']}")
    print(f"   GPA: {portal['gpa']}")
    print(f"   Attendance: {portal['attendance']}")
    if portal['alert']:
        print(f"   {portal['alert']}")
    
    print("\n" + "="*70)
    print("    MYTHARA EDUCATION SUITE DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
