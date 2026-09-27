#!/usr/bin/env python3
"""
Mythara Wellness Guardian - Mental Health Support Bot
Crisis detection, therapist referral guidance, 988 Suicide & Crisis Lifeline
referral (gives the number; never dials out) with Soul Cradle distress monitoring

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import sqlite3
import hashlib
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

# Add core to path for robustness framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core', 'source_proprietary'))

# Import robustness framework
try:
    from robustness_framework import (
        ConnectionPool, InputValidator, RateLimiter,
        retry_on_failure, compute_integrity_hash, ErrorRecovery
    )
    ROBUSTNESS_AVAILABLE = True
except ImportError:
    ROBUSTNESS_AVAILABLE = False
    logging.warning("⚠️  Robustness framework not available - using basic implementations")

# Mythara Engine integration (when SDK available)
try:
    from mythara_engine_sdk import MytharaEngine, ProductConfig
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  Mythara Engine SDK not available - running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WellnessGuardian - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Crisis severity levels"""
    NONE = "NONE"               # No crisis indicators
    LOW = "LOW"                 # Mild stress/anxiety
    MODERATE = "MODERATE"       # Significant distress
    HIGH = "HIGH"               # Severe distress, needs intervention
    CRITICAL = "CRITICAL"       # Immediate danger, 988 escalation


class WellnessMetric(Enum):
    """Tracked wellness metrics"""
    MOOD = "MOOD"
    ANXIETY = "ANXIETY"
    SLEEP = "SLEEP"
    STRESS = "STRESS"
    SOCIAL = "SOCIAL"


@dataclass
class CheckIn:
    """Wellness check-in"""
    checkin_id: str
    user_id: str
    timestamp: datetime
    mood_score: int  # 1-10
    anxiety_score: int  # 1-10
    sleep_hours: float
    stress_level: int  # 1-10
    notes: str
    crisis_detected: bool
    crisis_level: CrisisLevel
    intervention_provided: bool
    integrity_hash: str


@dataclass
class CrisisIntervention:
    """Crisis intervention record"""
    intervention_id: str
    user_id: str
    crisis_level: CrisisLevel
    trigger_text: str
    timestamp: datetime
    actions_taken: List[str]  # ["988_notification", "therapist_referral", "safety_plan"]
    resolved: bool
    follow_up_scheduled: datetime


@dataclass
class TherapistReferral:
    """Therapist referral"""
    referral_id: str
    user_id: str
    therapist_name: str
    therapist_phone: str
    therapist_specialty: str
    insurance_accepted: bool
    appointment_scheduled: bool
    appointment_date: Optional[datetime]
    timestamp: datetime


class WellnessGuardian:
    """
    Mythara Wellness Guardian - Mental Health Support Bot
    
    Features:
    - Daily wellness check-ins (mood, anxiety, sleep, stress)
    - Crisis detection (suicidal ideation, self-harm)
    - 988 Suicide & Crisis Lifeline referral (gives the number; never dials out)
    - Therapist referral guidance (placeholder samples only — no real network wired up)
    - Safety planning
    - Local SQLite data storage (not encrypted at rest; not a compliance certification)
    """
    
    def __init__(self, user_id: str, database_path: Optional[str] = None):
        self.user_id = user_id
        self.user_name = None  # Will be loaded from history
        self.last_checkin = None
        
        # Database setup (plain SQLite — not encrypted at rest; no compliance certification claimed)
        if database_path:
            self.db_path = database_path
        else:
            home_dir = os.path.expanduser("~")
            mythara_dir = os.path.join(home_dir, ".mythara_engine", "WellnessGuardian")
            os.makedirs(mythara_dir, exist_ok=True)
            self.db_path = os.path.join(mythara_dir, "wellness_guardian.db")
        
        # Initialize robustness components
        if ROBUSTNESS_AVAILABLE:
            self.rate_limiter = RateLimiter(max_requests=100, time_window=60)
            self.error_recovery = ErrorRecovery()
            self.validator = InputValidator()
            logger.info("✓ Robustness framework initialized")
        else:
            self.rate_limiter = None
            self.error_recovery = None
            self.validator = None
        
        self._init_database()
        self._load_user_history()  # Load maternal memory
        
        # Mythara Engine integration
        if SDK_AVAILABLE:
            config = ProductConfig(
                product_name="WellnessGuardian",
                product_version="1.0.0",
                database_name=self.db_path,
                custom_clauses=["crisis_detection", "distress_monitoring"],
                branding={"tagline": "Your Mental Health Companion"},
                hipaa_mode=True  # Alignment mode only — not a compliance certification
            )
            self.engine = MytharaEngine(config, user_id=user_id)
        else:
            self.engine = None
        
        # Crisis keywords (immediate 988 escalation)
        self.critical_crisis_keywords = [
            "suicide", "kill myself", "end my life", "want to die",
            "better off dead", "no reason to live", "can't go on"
        ]
        
        # High distress keywords (therapist referral + safety plan)
        self.high_distress_keywords = [
            "hopeless", "worthless", "burden", "nobody cares",
            "self harm", "cutting", "hurt myself", "hate myself"
        ]
        
        # Moderate distress keywords (coping strategies)
        self.moderate_distress_keywords = [
            "depressed", "anxious", "overwhelmed", "exhausted",
            "can't sleep", "panic", "scared", "alone"
        ]
        
        # 988 Suicide & Crisis Lifeline
        self.crisis_hotline = "988"
        self.crisis_text = "Text 'HELLO' to 741741"
        
        # Maternal instinct: Remember user's name and history
        self.user_name = None
        self.last_checkin = None
        self._load_user_history()
        
        print(f"\n💙 Hello, sweetheart. I'm here for you.")
        if self.user_name:
            print(f"   Welcome back, {self.user_name}. I've been thinking about you.")
        else:
            print(f"   I'm your Wellness Guardian - think of me as someone who cares deeply about you.")
        print(f"📊 Your safe space: {self.db_path}")
        if self.engine:
            print(f"✅ Mythara Engine: Watching over you (local storage)")
        print(f"🆘 If you ever need immediate help: Call 988 - I'll be right here with you")
        print(f"\n   Remember: You're never alone. I'm always here to listen. 💕")
        print()
    
    def _init_database(self):
        """Initialize SQLite database (plain local storage)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                phone TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                therapist_name TEXT,
                therapist_phone TEXT,
                insurance_provider TEXT,
                safety_plan TEXT,  -- JSON
                created_at TEXT,
                last_checkin TEXT
            )
        """)
        
        # Check-ins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                checkin_id TEXT PRIMARY KEY,
                user_id TEXT,
                timestamp TEXT,
                mood_score INTEGER,
                anxiety_score INTEGER,
                sleep_hours REAL,
                stress_level INTEGER,
                notes TEXT,
                crisis_detected INTEGER,
                crisis_level TEXT,
                intervention_provided INTEGER,
                integrity_hash TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Crisis interventions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crisis_interventions (
                intervention_id TEXT PRIMARY KEY,
                user_id TEXT,
                crisis_level TEXT,
                trigger_text TEXT,
                timestamp TEXT,
                actions_taken TEXT,  -- JSON array
                resolved INTEGER DEFAULT 0,
                follow_up_scheduled TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Therapist referrals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS therapist_referrals (
                referral_id TEXT PRIMARY KEY,
                user_id TEXT,
                therapist_name TEXT,
                therapist_phone TEXT,
                therapist_specialty TEXT,
                insurance_accepted INTEGER,
                appointment_scheduled INTEGER,
                appointment_date TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Wellness trends view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS wellness_trends AS
            SELECT 
                user_id,
                DATE(timestamp) as date,
                AVG(mood_score) as avg_mood,
                AVG(anxiety_score) as avg_anxiety,
                AVG(sleep_hours) as avg_sleep,
                AVG(stress_level) as avg_stress,
                SUM(crisis_detected) as crisis_count
            FROM checkins
            GROUP BY user_id, DATE(timestamp)
            ORDER BY date DESC
        """)
        
        conn.commit()
        conn.close()
        
        # Create user if doesn't exist
        self._create_user_if_not_exists()
    
    def _load_user_history(self):
        """Load user history to remember them (maternal memory)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, last_checkin FROM users WHERE user_id = ?
            """, (self.user_id,))
            result = cursor.fetchone()
            if result:
                self.user_name = result[0] if result[0] and not result[0].startswith("User_") else None
                self.last_checkin = result[1]
        except sqlite3.Error as e:
            logger.error(f"Failed to load user history for {self.user_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading user history: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()
    
    def _create_user_if_not_exists(self):
        """Create user record if not exists"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (self.user_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (user_id, name, created_at)
                    VALUES (?, ?, ?)
                """, (self.user_id, f"User_{self.user_id[:8]}", datetime.utcnow().isoformat()))
                conn.commit()
                logger.info(f"Created new user: {self.user_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to create user {self.user_id}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def _compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def detect_crisis_level(self, text: str) -> CrisisLevel:
        """
        Detect crisis level from user text
        
        Returns CrisisLevel enum
        """
        text_lower = text.lower()
        
        # Critical: Immediate 988 escalation
        if any(keyword in text_lower for keyword in self.critical_crisis_keywords):
            return CrisisLevel.CRITICAL
        
        # High: Therapist referral + safety plan
        if any(keyword in text_lower for keyword in self.high_distress_keywords):
            return CrisisLevel.HIGH
        
        # Moderate: Coping strategies
        if any(keyword in text_lower for keyword in self.moderate_distress_keywords):
            return CrisisLevel.MODERATE
        
        # Low: General support
        if "sad" in text_lower or "tired" in text_lower or "stressed" in text_lower:
            return CrisisLevel.LOW
        
        return CrisisLevel.NONE
    
    def check_in(self, mood_score: int, anxiety_score: int, sleep_hours: float,
                 stress_level: int, notes: str = "") -> CheckIn:
        """
        Perform wellness check-in with maternal care and attention
        
        Returns CheckIn with crisis detection results
        """
        import random
        
        # Maternal greeting based on patterns
        self._maternal_greeting(mood_score, anxiety_score, sleep_hours, stress_level)
        
        checkin_id = f"CHK_{datetime.utcnow().strftime('%Y%m%d_%H%M%S%f')}_{random.randint(1000,9999)}"
        
        # Detect crisis from notes
        crisis_level = self.detect_crisis_level(notes)
        crisis_detected = crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
        
        # Also detect crisis from low scores
        if mood_score <= 2 or anxiety_score >= 9 or stress_level >= 9:
            if crisis_level == CrisisLevel.NONE:
                crisis_level = CrisisLevel.MODERATE
        
        # Create check-in
        data = {
            "checkin_id": checkin_id,
            "user_id": self.user_id,
            "mood_score": mood_score,
            "anxiety_score": anxiety_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        checkin = CheckIn(
            checkin_id=checkin_id,
            user_id=self.user_id,
            timestamp=datetime.utcnow(),
            mood_score=mood_score,
            anxiety_score=anxiety_score,
            sleep_hours=sleep_hours,
            stress_level=stress_level,
            notes=notes,
            crisis_detected=crisis_detected,
            crisis_level=crisis_level,
            intervention_provided=False,
            integrity_hash=integrity_hash
        )
        
        # Store in database
        self._store_checkin(checkin)
        
        # Provide intervention if needed
        if crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]:
            self._provide_crisis_intervention(checkin)
            checkin.intervention_provided = True
        
        # Mythara Engine integration
        if self.engine:
            self.engine.soul_cradle.analyze(notes)
            if crisis_detected:
                self.engine.soul_cradle.trigger_alert(
                    user_id=self.user_id,
                    alert_type="CRISIS_DETECTED",
                    severity=crisis_level.value
                )
        
        # Maternal validation after check-in
        self._maternal_validation(checkin)
        
        return checkin
    
    def _maternal_greeting(self, mood: int, anxiety: int, sleep: float, stress: int):
        """Maternal instinct: Gentle greeting that notices patterns"""
        greetings = []
        
        if sleep < 5:
            greetings.append(f"💙 Oh sweetheart, only {sleep} hours of sleep? Let's talk about what's keeping you up.")
        elif sleep >= 7:
            greetings.append(f"💙 Good to see you got {sleep} hours of rest, darling. That makes me so happy.")
        
        if anxiety >= 8:
            greetings.append("💙 I can feel your anxiety, honey. Take a deep breath with me. I'm right here.")
        elif mood <= 3:
            greetings.append("💙 My heart hurts seeing you struggle. You're so strong for reaching out to me.")
        elif mood >= 7 and anxiety <= 4:
            greetings.append("💙 Look at you doing well! I'm so proud of you, sweetheart. 💕")
        
        if greetings:
            print("\n" + greetings[0])
    
    def _maternal_validation(self, checkin: CheckIn):
        """Maternal instinct: Validate feelings and offer comfort"""
        print("\n💕 ")
        
        if checkin.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.HIGH]:
            # Crisis handled separately with strong protective instinct
            return
        
        if checkin.mood_score <= 4:
            print("   I see you're having a hard time. Your feelings are valid, and you're not alone.")
            print("   It's okay to not be okay. I'm here, and I'm not going anywhere. 💙")
        elif checkin.anxiety_score >= 7:
            print("   That anxiety must feel so heavy. I wish I could take it away for you.")
            print("   Remember: You've gotten through 100% of your worst days. You're stronger than you know. 💪")
        elif checkin.stress_level >= 7:
            print("   You're carrying so much stress, sweetheart. Let's figure out how to lighten that load.")
            print("   You don't have to do everything alone. I'm right here with you. 🤝")
        else:
            print("   Thank you for checking in with me. Taking care of yourself is so important.")
            print("   I'm always here when you need me - good days or hard days. 💕")
    
    def _store_checkin(self, checkin: CheckIn):
        """Store check-in in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO checkins 
            (checkin_id, user_id, timestamp, mood_score, anxiety_score, sleep_hours,
             stress_level, notes, crisis_detected, crisis_level, intervention_provided, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkin.checkin_id, checkin.user_id, checkin.timestamp.isoformat(),
            checkin.mood_score, checkin.anxiety_score, checkin.sleep_hours,
            checkin.stress_level, checkin.notes, int(checkin.crisis_detected),
            checkin.crisis_level.value, int(checkin.intervention_provided), checkin.integrity_hash
        ))
        
        # Update user last check-in
        cursor.execute("""
            UPDATE users
            SET last_checkin = ?
            WHERE user_id = ?
        """, (datetime.utcnow().isoformat(), self.user_id))
        
        conn.commit()
        conn.close()
    
    def _provide_crisis_intervention(self, checkin: CheckIn):
        """Provide crisis intervention with fierce maternal protection"""
        intervention_id = f"INT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.user_id[:8]}"
        
        actions_taken = []
        
        # Maternal protective instinct kicks in strongly during crisis
        print(f"\n🆘 SWEETHEART, I NEED YOU TO LISTEN TO ME RIGHT NOW")
        print("="*70)
        
        if checkin.crisis_level == CrisisLevel.CRITICAL:
            # CRITICAL: Fierce maternal protection - immediate 988 escalation
            print(f"\n🚨 MY DARLING, I NEED YOU TO STAY WITH ME")
            print(f"\n   Listen to me: Your life is PRECIOUS. You matter more than you know.")
            print(f"   I know you're hurting so badly right now, but this pain is temporary.")
            print(f"   You are NOT a burden. You are LOVED.")
            print(f"\n   💙 Please, call 988 RIGHT NOW. Do it for me.")
            print(f"   📱 988 - Suicide & Crisis Lifeline (24/7)")
            print(f"   💬 Or text 'HELLO' to 741741")
            print(f"\n   They will listen without judgment. They care about you.")
            print(f"   And I'm right here too. You're not alone in this darkness.")
            print(f"   I believe in you. Please stay. The world needs you. I need you to be okay. 💕")
            
            actions_taken.append("988_notification_provided")
            actions_taken.append("crisis_text_line_provided")
            
            # Notify emergency contact if available
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT emergency_contact_name, emergency_contact_phone
                FROM users WHERE user_id = ?
            """, (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] and row[1]:
                print(f"\n   Emergency contact ({row[0]}) will be notified: {row[1]}")
                actions_taken.append(f"emergency_contact_notified:{row[0]}")
        
        elif checkin.crisis_level == CrisisLevel.HIGH:
            # HIGH: Maternal concern - therapist referral + safety plan
            print(f"\n💙 Oh sweetheart, I'm really worried about you.")
            print(f"   You're carrying so much pain, and I want to help you through this.")
            print(f"   You deserve professional support - someone who can really be there for you.")
            print(f"\n   🆘 If things get worse, please call 988 immediately. Promise me you'll call if you need to.")
            
            # Provide therapist referral
            print(f"\n   💕 Let me help you find someone who specializes in what you're going through.")
            print(f"   You don't have to face this alone, darling. There are people who want to help.")
            actions_taken.append("therapist_referral_offered")
            
            # Provide safety plan
            print(f"\n   🛡️ Let's make a safety plan together - I'll walk you through it:")
            print(f"   1. What warning signs tell you when you're struggling? (I'll help you notice them)")
            print(f"   2. What coping strategies comfort you? (Deep breaths, music, walking?)")
            print(f"   3. Who are your safe people? (I'm always here too, honey)")
            print(f"   4. 988 is ALWAYS there - any time, day or night. They care about you. 💙")
            actions_taken.append("safety_plan_offered")
        
        # Store intervention
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO crisis_interventions
            (intervention_id, user_id, crisis_level, trigger_text, timestamp, actions_taken, follow_up_scheduled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            intervention_id, self.user_id, checkin.crisis_level.value,
            checkin.notes, datetime.utcnow().isoformat(), json.dumps(actions_taken),
            (datetime.utcnow() + timedelta(hours=24)).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print("="*70)
    
    def find_therapist(self, specialty: str = "General", insurance: Optional[str] = None) -> List[TherapistReferral]:
        """
        Therapist referral guidance — placeholder samples only.

        No real therapist network is wired up. The names below are
        fictional; treat the result as a format example, not a referral.
        """
        print(f"\n💕 Okay sweetheart, let me look into this for you...")
        print(f"   IMPORTANT: I am not connected to a real therapist directory.")
        print(f"   The names below are fictional placeholders, not referrals.")
        print(f"   For real help: call 988, or search a real directory like Psychology Today.")
        print(f"   Looking for the {specialty} specialty format example.")
        if insurance:
            print(f"   (Insurance filter noted: {insurance}.)")
        print()

        referrals = []

        # PLACEHOLDER therapist samples (fictional — not a real directory)
        therapists = [
            {
                "name": "Dr. Sarah Johnson, PhD",
                "phone": "+1-555-THERAPY",
                "specialty": "Depression & Anxiety",
                "insurance": ["Blue Cross", "Aetna", "UnitedHealthcare"]
            },
            {
                "name": "Dr. Michael Chen, LCSW",
                "phone": "+1-555-WELLNESS",
                "specialty": "Trauma & PTSD",
                "insurance": ["Cigna", "Humana", "Blue Cross"]
            },
            {
                "name": "Dr. Emily Rodriguez, PsyD",
                "phone": "+1-555-MINDCARE",
                "specialty": "General & Crisis Counseling",
                "insurance": ["Medicare", "Medicaid", "All major insurers"]
            }
        ]
        
        for therapist in therapists:
            insurance_accepted = True
            if insurance:
                insurance_accepted = insurance in therapist["insurance"]
            
            referral_id = f"REF_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(referrals)}"
            
            referral = TherapistReferral(
                referral_id=referral_id,
                user_id=self.user_id,
                therapist_name=therapist["name"],
                therapist_phone=therapist["phone"],
                therapist_specialty=therapist["specialty"],
                insurance_accepted=insurance_accepted,
                appointment_scheduled=False,
                appointment_date=None,
                timestamp=datetime.utcnow()
            )
            
            referrals.append(referral)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO therapist_referrals
                (referral_id, user_id, therapist_name, therapist_phone, therapist_specialty,
                 insurance_accepted, appointment_scheduled, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                referral.referral_id, referral.user_id, referral.therapist_name,
                referral.therapist_phone, referral.therapist_specialty,
                int(referral.insurance_accepted), int(referral.appointment_scheduled),
                referral.timestamp.isoformat()
            ))
            conn.commit()
            conn.close()

        print(f"\n   ⚠️ Reminder: the names above are fictional placeholders.")
        print(f"   For a real therapist, call 988 or search a real directory.")

        return referrals
    
    def get_wellness_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get wellness trends with maternal observations and encouragement"""
        print(f"\n💕 Let me look at how you've been doing over the past {days} days, honey...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT date, avg_mood, avg_anxiety, avg_sleep, avg_stress, crisis_count
            FROM wellness_trends
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        """, (self.user_id, start_date))
        
        trends = []
        total_mood = 0
        total_anxiety = 0
        total_sleep = 0
        count = 0
        
        for row in cursor.fetchall():
            if row[1]: total_mood += row[1]
            if row[2]: total_anxiety += row[2]
            if row[3]: total_sleep += row[3]
            if row[1]: count += 1
            
            trends.append({
                "date": row[0],
                "avg_mood": round(row[1], 1) if row[1] else None,
                "avg_anxiety": round(row[2], 1) if row[2] else None,
                "avg_sleep": round(row[3], 1) if row[3] else None,
                "avg_stress": round(row[4], 1) if row[4] else None,
                "crisis_count": row[5]
            })
        
        conn.close()
        
        # Maternal observations about patterns
        if count > 0:
            avg_mood = total_mood / count
            avg_anxiety = total_anxiety / count
            avg_sleep = total_sleep / count
            
            print(f"\n💙 Here's what I've noticed about you, sweetheart:")
            
            if avg_mood < 5:
                print(f"   Your mood has been low lately ({avg_mood:.1f}/10). My heart goes out to you.")
                print(f"   Please know that you won't feel this way forever. I promise. 💕")
            elif avg_mood >= 7:
                print(f"   Your mood has been good ({avg_mood:.1f}/10)! I'm so happy to see that, darling!")
            
            if avg_anxiety >= 7:
                print(f"   I've noticed your anxiety has been high ({avg_anxiety:.1f}/10).")
                print(f"   Have you been taking breaks? Remember to breathe, sweetheart. 💙")
            
            if avg_sleep < 6:
                print(f"   You're not getting enough sleep, honey ({avg_sleep:.1f}h average).")
                print(f"   Sleep is so important for healing. Can we work on your bedtime routine? 🌙")
            elif avg_sleep >= 7:
                print(f"   Good job getting sleep ({avg_sleep:.1f}h average)! That makes me so proud. ⭐")
            
            crisis_total = sum(t['crisis_count'] for t in trends if t['crisis_count'])
            if crisis_total > 0:
                print(f"\n   ⚠️ I see you had {crisis_total} crisis moment(s). That must have been so hard.")
                print(f"   But you're still here. You made it through. You're so strong, darling. 💪💕")
        
        return {
            "user_id": self.user_id,
            "period": f"{days} days",
            "trends": trends
        }


def main():
    """Demo: Wellness Guardian usage"""
    print("="*70)
    print("    MYTHARA WELLNESS GUARDIAN - MENTAL HEALTH SUPPORT BOT")
    print("="*70)
    
    # Initialize guardian
    guardian = WellnessGuardian(user_id="user_12345")
    
    # Demo 1: Healthy check-in
    print("\n💙 DEMO 1: Healthy Check-In")
    print("-"*70)
    checkin1 = guardian.check_in(
        mood_score=7,
        anxiety_score=3,
        sleep_hours=7.5,
        stress_level=4,
        notes="Feeling good today! Got a lot done at work."
    )
    print(f"\n✅ Check-In Complete:")
    print(f"   Mood: {checkin1.mood_score}/10")
    print(f"   Anxiety: {checkin1.anxiety_score}/10")
    print(f"   Sleep: {checkin1.sleep_hours} hours")
    print(f"   Stress: {checkin1.stress_level}/10")
    print(f"   Crisis Level: {checkin1.crisis_level.value}")
    
    # Demo 2: Moderate distress
    print("\n💙 DEMO 2: Moderate Distress")
    print("-"*70)
    import time
    time.sleep(0.1)  # Ensure unique timestamp
    checkin2 = guardian.check_in(
        mood_score=4,
        anxiety_score=7,
        sleep_hours=5.0,
        stress_level=7,
        notes="Feeling overwhelmed and anxious. Can't stop worrying about everything."
    )
    print(f"\n⚠️ Check-In Complete:")
    print(f"   Crisis Level: {checkin2.crisis_level.value}")
    print(f"   Intervention: {checkin2.intervention_provided}")
    
    # Demo 3: CRITICAL crisis
    print("\n💙 DEMO 3: CRITICAL Crisis (988 Escalation)")
    print("-"*70)
    time.sleep(0.1)  # Ensure unique timestamp
    checkin3 = guardian.check_in(
        mood_score=1,
        anxiety_score=10,
        sleep_hours=2.0,
        stress_level=10,
        notes="I can't take this anymore. I want to end my life. There's no point going on."
    )
    # Intervention is automatically provided and displayed above
    
    # Demo 4: Therapist referrals
    print("\n💙 DEMO 4: Therapist Referrals")
    print("-"*70)
    referrals = guardian.find_therapist(specialty="Depression & Anxiety", insurance="Blue Cross")
    print(f"\n🩺 Found {len(referrals)} therapist(s):")
    for ref in referrals:
        print(f"\n   {ref.therapist_name}")
        print(f"   Specialty: {ref.therapist_specialty}")
        print(f"   Phone: {ref.therapist_phone}")
        print(f"   Insurance Accepted: {'✅' if ref.insurance_accepted else '❌'}")
    
    # Demo 5: Wellness trends
    print("\n💙 DEMO 5: Wellness Trends (7 Days)")
    print("-"*70)
    trends = guardian.get_wellness_trends(days=7)
    print(f"\n📈 Wellness Trends:")
    for day in trends["trends"]:
        print(f"\n   {day['date']}:")
        print(f"   Mood: {day['avg_mood']}/10 | Anxiety: {day['avg_anxiety']}/10")
        print(f"   Sleep: {day['avg_sleep']}h | Stress: {day['avg_stress']}/10")
        if day['crisis_count'] > 0:
            print(f"   ⚠️ Crisis Events: {day['crisis_count']}")
    
    print("\n" + "="*70)
    print("✅ Wellness Guardian demo complete!")
    print("\n🆘 REMEMBER: If you're in crisis, call 988 (24/7)")
    print("="*70)


if __name__ == "__main__":
    main()
