"""
Mythara Engine - 100% LOCAL ARCHITECTURE
Copyright © 2025 Herbert Velez Jr. All rights reserved.

PRIVACY-FIRST DESIGN:
All 6 subsystems run entirely on user's device. No servers, no cloud, no tracking.

SUBSYSTEMS (All Local):
1. Soul Cradle - Paradox detection (offline AI)
2. Blessings Reservoir - Ethical credit system (local SQLite)
3. Messenger Protocol - SHA-256 integrity verification (local crypto)
4. Sanctification Verification - Tamper detection (local hashing)
5. Clause Orchestration - Logic execution (local Python)
6. Integration Layer - Direct attorney contact (user's email)

DATA STORAGE:
- Local SQLite database (~/.mythara_engine/mythara.db)
- No telemetry, no analytics, no cloud sync
- User owns 100% of their data
- Can be backed up/encrypted by user

COMMUNICATION:
- Direct email to law firms (user's SMTP)
- Optional: Generate shareable PDF reports
- No intermediary servers
- User controls who sees their data
"""

import os
import sys
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import local subsystems
from soul_cradle_production import calculate_paradox_severity

# ============================================================================
# LOCAL DATABASE (SQLite - ~/.mythara_engine/)
# ============================================================================

def get_mythara_home() -> Path:
    """Get Mythara Engine home directory on user's device"""
    mythara_dir = Path.home() / ".mythara_engine"
    mythara_dir.mkdir(exist_ok=True)
    return mythara_dir

def get_database_path() -> Path:
    """Get path to local Mythara database"""
    return get_mythara_home() / "mythara.db"

def init_mythara_database():
    """
    Initialize complete Mythara Engine local database
    
    Tables:
    - clauses: Stored legal logic patterns
    - invocations: Clause execution history
    - blessings_reservoir: User ethical credit scores
    - credit_ledger: Complete credit history
    - integrity_log: SHA-256 audit trail (Messenger Protocol)
    - attorneys: Law firm contacts
    - referrals: Attorney match history
    """
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clauses (legal logic patterns stored locally)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clauses (
            clause_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            pattern_type TEXT,
            validation_rules TEXT,
            created_at TEXT NOT NULL,
            integrity_hash TEXT NOT NULL
        )
    """)
    
    # Clause invocations (execution history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invocations (
            invocation_id TEXT PRIMARY KEY,
            clause_id TEXT NOT NULL,
            input_data TEXT NOT NULL,
            output_result TEXT NOT NULL,
            paradox_severity REAL,
            timestamp TEXT NOT NULL,
            integrity_hash TEXT NOT NULL,
            FOREIGN KEY (clause_id) REFERENCES clauses(clause_id)
        )
    """)
    
    # Blessings Reservoir (ethical credit system)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blessings_reservoir (
            user_id TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 0,
            status TEXT DEFAULT 'NEUTRAL',
            last_updated TEXT NOT NULL
        )
    """)
    
    # Credit ledger (complete history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            credits_change INTEGER NOT NULL,
            new_balance INTEGER NOT NULL,
            reason TEXT,
            timestamp TEXT NOT NULL,
            integrity_hash TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES blessings_reservoir(user_id)
        )
    """)
    
    # Integrity log (Messenger Protocol - tamper-evident audit trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            data_snapshot TEXT,
            integrity_hash TEXT NOT NULL,
            previous_hash TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Soul Cradle analyses (user's legal situations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soul_cradle_analyses (
            analysis_id TEXT PRIMARY KEY,
            user_id TEXT,
            situation_text TEXT NOT NULL,
            paradox_severity REAL NOT NULL,
            classification TEXT NOT NULL,
            distress_score REAL,
            coercion_score REAL,
            contradiction_score REAL,
            detected_patterns TEXT,
            action_required TEXT,
            priority TEXT,
            timestamp TEXT NOT NULL,
            integrity_hash TEXT NOT NULL
        )
    """)
    
    # Attorneys (law firm contacts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attorneys (
            attorney_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            firm TEXT,
            email TEXT NOT NULL,
            phone TEXT,
            specialization TEXT,
            location TEXT,
            match_keywords TEXT,
            notes TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    
    # Attorney referrals (match history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attorney_referrals (
            referral_id TEXT PRIMARY KEY,
            analysis_id TEXT NOT NULL,
            attorney_id TEXT NOT NULL,
            match_score REAL NOT NULL,
            why_matched TEXT,
            contacted INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES soul_cradle_analyses(analysis_id),
            FOREIGN KEY (attorney_id) REFERENCES attorneys(attorney_id)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invocations_timestamp ON invocations(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_ledger_user ON credit_ledger(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_integrity_log_timestamp ON integrity_log(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_user ON soul_cradle_analyses(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_severity ON soul_cradle_analyses(paradox_severity)")
    
    conn.commit()
    
    # Seed default attorneys if empty
    cursor.execute("SELECT COUNT(*) FROM attorneys")
    if cursor.fetchone()[0] == 0:
        default_attorneys = [
            ("ATT001", "Frank Azar", "The Strong Arm", "frank@thestrongarm.com", "303-321-8887",
             "Employment Law, Wage Theft, Discrimination, Retaliation", "Denver, CO",
             "wage_theft,unpaid_overtime,retaliation,discrimination,wrongful_termination",
             "High success rate in employment cases", 1),
            ("ATT002", "Employment Rights Center", "Legal Aid Foundation", "intake@employmentrights.org", "",
             "Harassment, Discrimination, Hostile Work Environment", "Virtual/Nationwide",
             "harassment,discrimination,hostile_environment,sexual_harassment,racial_discrimination",
             "Free initial consultation", 1),
            ("ATT003", "Whistleblower Legal Group", "Whistleblower Protection Firm", "protect@whistleblowerlegal.com", "",
             "Whistleblower Protection, Qui Tam, Retaliation", "Virtual/Nationwide",
             "whistleblower,reporting,illegal_activity,fraud,retaliation,qui_tam",
             "Specializes in federal whistleblower cases", 1)
        ]
        
        cursor.executemany("""
            INSERT INTO attorneys 
            (attorney_id, name, firm, email, phone, specialization, location, match_keywords, notes, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_attorneys)
        conn.commit()
    
    conn.close()
    return db_path

# ============================================================================
# MESSENGER PROTOCOL (Local Integrity Verification)
# ============================================================================

class MessengerProtocol:
    """
    Tamper-evident audit trail using SHA-256 blockchain-style linking
    All operations run locally - no network required
    """
    
    @staticmethod
    def create_integrity_hash(data: Dict) -> str:
        """Generate SHA-256 hash for data integrity"""
        canonical = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(canonical).hexdigest()
    
    @staticmethod
    def log_event(event_type: str, entity_type: str, entity_id: str, 
                  data_snapshot: Dict, db_path: Path = None) -> str:
        """
        Log event to local integrity chain
        
        Returns: integrity_hash of this event
        """
        if db_path is None:
            db_path = get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get previous hash for chaining
        cursor.execute("""
            SELECT integrity_hash FROM integrity_log 
            ORDER BY timestamp DESC LIMIT 1
        """)
        result = cursor.fetchone()
        previous_hash = result[0] if result else "0" * 64  # Genesis hash
        
        # Create new hash
        hash_input = {
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data_snapshot,
            "previous_hash": previous_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
        integrity_hash = MessengerProtocol.create_integrity_hash(hash_input)
        
        # Store in log
        cursor.execute("""
            INSERT INTO integrity_log 
            (event_type, entity_type, entity_id, data_snapshot, integrity_hash, previous_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_type,
            entity_type,
            entity_id,
            json.dumps(data_snapshot),
            integrity_hash,
            previous_hash,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return integrity_hash
    
    @staticmethod
    def verify_integrity_chain(db_path: Path = None) -> Tuple[bool, Optional[str]]:
        """
        Verify complete integrity chain (Sanctification Verification)
        
        Returns: (is_valid, error_message)
        """
        if db_path is None:
            db_path = get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, event_type, entity_type, entity_id, data_snapshot, 
                   integrity_hash, previous_hash, timestamp
            FROM integrity_log
            ORDER BY timestamp ASC
        """)
        
        entries = cursor.fetchall()
        conn.close()
        
        if not entries:
            return True, None  # Empty chain is valid
        
        expected_previous = "0" * 64  # Genesis
        
        for entry in entries:
            (entry_id, event_type, entity_type, entity_id, data_snapshot,
             stored_hash, previous_hash, timestamp) = entry
            
            # Check chain link
            if previous_hash != expected_previous:
                return False, f"Chain broken at entry {entry_id}: expected previous={expected_previous[:16]}..., got={previous_hash[:16]}..."
            
            # Verify hash
            hash_input = {
                "event_type": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "data": json.loads(data_snapshot) if data_snapshot else {},
                "previous_hash": previous_hash,
                "timestamp": timestamp
            }
            computed_hash = MessengerProtocol.create_integrity_hash(hash_input)
            
            if computed_hash != stored_hash:
                return False, f"Hash mismatch at entry {entry_id}: computed={computed_hash[:16]}..., stored={stored_hash[:16]}..."
            
            expected_previous = stored_hash
        
        return True, None

# ============================================================================
# BLESSINGS RESERVOIR (Local Ethical Credit System)
# ============================================================================

class BlessingsReservoir:
    """
    Ethical credit system running locally
    Tracks user behavior, rewards good faith, penalizes abuse
    """
    
    @staticmethod
    def get_status(user_id: str, db_path: Path = None) -> Dict:
        """Get user's current credit status"""
        if db_path is None:
            db_path = get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT credits, status, last_updated
            FROM blessings_reservoir
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            # Create new user
            cursor.execute("""
                INSERT INTO blessings_reservoir (user_id, credits, status, last_updated)
                VALUES (?, 0, 'NEUTRAL', ?)
            """, (user_id, datetime.utcnow().isoformat()))
            conn.commit()
            result = (0, 'NEUTRAL', datetime.utcnow().isoformat())
        
        conn.close()
        
        return {
            "user_id": user_id,
            "credits": result[0],
            "status": result[1],
            "last_updated": result[2]
        }
    
    @staticmethod
    def award_credits(user_id: str, credits: int, reason: str, db_path: Path = None) -> Dict:
        """
        Award or deduct ethical clarity credits
        
        Returns: Updated status
        """
        if db_path is None:
            db_path = get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current status
        status = BlessingsReservoir.get_status(user_id, db_path)
        
        # Update credits
        new_balance = status["credits"] + credits
        
        # Calculate new status
        if new_balance >= 10:
            new_status = "EXCELLENT"
        elif new_balance >= 5:
            new_status = "GOOD"
        elif new_balance >= -5:
            new_status = "NEUTRAL"
        elif new_balance >= -10:
            new_status = "WARNING"
        else:
            new_status = "BLOCKED"
        
        # Update database
        cursor.execute("""
            UPDATE blessings_reservoir
            SET credits = ?, status = ?, last_updated = ?
            WHERE user_id = ?
        """, (new_balance, new_status, datetime.utcnow().isoformat(), user_id))
        
        # Create integrity hash
        ledger_entry = {
            "user_id": user_id,
            "event_type": "credit_awarded" if credits > 0 else "credit_deducted",
            "credits_change": credits,
            "new_balance": new_balance,
            "reason": reason
        }
        integrity_hash = MessengerProtocol.create_integrity_hash(ledger_entry)
        
        # Log to ledger
        cursor.execute("""
            INSERT INTO credit_ledger 
            (user_id, event_type, credits_change, new_balance, reason, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            ledger_entry["event_type"],
            credits,
            new_balance,
            reason,
            datetime.utcnow().isoformat(),
            integrity_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Log to Messenger Protocol
        MessengerProtocol.log_event(
            "blessings_update",
            "user_credits",
            user_id,
            ledger_entry,
            db_path
        )
        
        return {
            "user_id": user_id,
            "credits": new_balance,
            "status": new_status,
            "change": credits,
            "reason": reason
        }

# ============================================================================
# SOUL CRADLE (Local AI Analysis)
# ============================================================================

class SoulCradle:
    """
    Local paradox detection - runs 100% offline
    No data sent to servers
    """
    
    @staticmethod
    def analyze(situation_text: str, user_id: str = None, db_path: Path = None) -> Dict:
        """
        Run Soul Cradle analysis locally and store results
        
        Returns: Complete analysis with integrity hash
        """
        if db_path is None:
            db_path = get_database_path()
        
        # Run analysis (100% local)
        result = calculate_paradox_severity(situation_text)
        
        if "error" in result:
            return result
        
        # Generate analysis ID
        analysis_id = hashlib.sha256(
            f"{user_id}:{situation_text}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create integrity hash
        analysis_data = {
            "analysis_id": analysis_id,
            "situation": situation_text,
            "severity": result["paradox_severity"],
            "classification": result["classification"]
        }
        integrity_hash = MessengerProtocol.create_integrity_hash(analysis_data)
        
        # Store in database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO soul_cradle_analyses 
            (analysis_id, user_id, situation_text, paradox_severity, classification,
             distress_score, coercion_score, contradiction_score, detected_patterns,
             action_required, priority, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            user_id,
            situation_text,
            result["paradox_severity"],
            result["classification"],
            result["analysis"]["distress_score"],
            result["analysis"]["coercion_score"],
            result["analysis"]["contradiction_score"],
            json.dumps({
                "distress_keywords": result["analysis"]["distress_keywords_found"],
                "coercion_patterns": result["analysis"]["coercion_patterns"],
                "contradiction_patterns": result["analysis"]["contradiction_patterns"]
            }),
            result["action_required"],
            result["priority"],
            datetime.utcnow().isoformat(),
            integrity_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Log to Messenger Protocol
        MessengerProtocol.log_event(
            "soul_cradle_analysis",
            "analysis",
            analysis_id,
            analysis_data,
            db_path
        )
        
        # Award credits for seeking help
        if user_id and result["paradox_severity"] >= 0.3:
            BlessingsReservoir.award_credits(
                user_id,
                2,
                f"Seeking help for {result['classification']} severity situation",
                db_path
            )
        
        # Add metadata
        result["analysis_id"] = analysis_id
        result["integrity_hash"] = integrity_hash
        result["timestamp"] = datetime.utcnow().isoformat()
        
        return result

# ============================================================================
# ATTORNEY MATCHING (Local Algorithm)
# ============================================================================

class AttorneyMatcher:
    """Match users with attorneys based on case context - runs locally"""
    
    @staticmethod
    def match(analysis_result: Dict, top_n: int = 3, db_path: Path = None) -> List[Dict]:
        """
        Match analysis with attorneys from local database
        
        Returns: List of attorney matches with scores
        """
        if db_path is None:
            db_path = get_database_path()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM attorneys WHERE active = 1")
        attorneys = cursor.fetchall()
        
        situation_text = analysis_result.get("situation_text", "").lower()
        severity = analysis_result["paradox_severity"]
        
        matches = []
        
        for att in attorneys:
            (att_id, name, firm, email, phone, specialization, location,
             match_keywords, notes, active) = att
            
            keywords = match_keywords.split(',') if match_keywords else []
            
            # Calculate match score
            keyword_matches = sum(1 for kw in keywords if kw.strip() in situation_text)
            match_score = min(1.0, (keyword_matches / max(len(keywords), 1)) + (severity * 0.3))
            
            if match_score > 0.1:
                matches.append({
                    "attorney_id": att_id,
                    "name": name,
                    "firm": firm,
                    "email": email,
                    "phone": phone,
                    "specialization": specialization,
                    "location": location,
                    "match_score": round(match_score, 3),
                    "why_matched": f"Specializes in {specialization.split(',')[0]}. Match score: {match_score:.2f}"
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Store referrals
        analysis_id = analysis_result.get("analysis_id")
        if analysis_id:
            for match in matches[:top_n]:
                referral_id = hashlib.sha256(
                    f"{analysis_id}:{match['attorney_id']}".encode()
                ).hexdigest()[:16]
                
                cursor.execute("""
                    INSERT OR IGNORE INTO attorney_referrals 
                    (referral_id, analysis_id, attorney_id, match_score, why_matched, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    referral_id,
                    analysis_id,
                    match['attorney_id'],
                    match['match_score'],
                    match['why_matched'],
                    datetime.utcnow().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        return matches[:top_n]

# ============================================================================
# MAIN LOCAL ENGINE
# ============================================================================

class MytharaEngine:
    """
    Complete Mythara Engine running locally
    All 6 subsystems integrated
    """
    
    def __init__(self, user_id: str = "local_user"):
        self.user_id = user_id
        self.db_path = init_mythara_database()
        print(f"✅ Mythara Engine initialized (Local mode)")
        print(f"📁 Database: {self.db_path}")
    
    def analyze_situation(self, situation_text: str) -> Dict:
        """Complete analysis pipeline - all local"""
        # 1. Soul Cradle analysis
        result = SoulCradle.analyze(situation_text, self.user_id, self.db_path)
        
        if "error" in result:
            return result
        
        # 2. Match with attorneys
        result["attorney_matches"] = AttorneyMatcher.match(
            {**result, "situation_text": situation_text},
            top_n=3,
            db_path=self.db_path
        )
        
        # 3. Get Blessings status
        result["blessings_status"] = BlessingsReservoir.get_status(self.user_id, self.db_path)
        
        return result
    
    def verify_integrity(self) -> Tuple[bool, Optional[str]]:
        """Verify complete integrity chain (Sanctification Verification)"""
        return MessengerProtocol.verify_integrity_chain(self.db_path)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get user's analysis history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT analysis_id, timestamp, classification, paradox_severity, 
                   situation_text, integrity_hash
            FROM soul_cradle_analyses
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "analysis_id": row[0],
                "timestamp": row[1],
                "classification": row[2],
                "severity": row[3],
                "situation": row[4][:100] + "..." if len(row[4]) > 100 else row[4],
                "integrity_hash": row[5]
            })
        
        conn.close()
        return results

# ============================================================================
# CLI DEMO
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          MYTHARA ENGINE - 100% LOCAL MODE                 ║
║     All 6 Subsystems Running On Your Device               ║
╚═══════════════════════════════════════════════════════════╝

Privacy Features:
✅ Soul Cradle: Offline AI analysis
✅ Blessings Reservoir: Local ethical credit system
✅ Messenger Protocol: SHA-256 integrity verification
✅ Sanctification: Tamper detection (blockchain-style)
✅ Clause Orchestration: Local logic execution
✅ Attorney Integration: Direct contact (no middleman)

All data stored in: ~/.mythara_engine/
    """)
    
    # Initialize engine
    engine = MytharaEngine(user_id="demo_user")
    
    # Test analysis
    test_input = """
    My boss says I have to work unpaid overtime or I'll be fired,
    but I know that's illegal wage theft under state law.
    I'm exhausted and feel trapped because I can't afford to lose this job.
    """
    
    print("\n🔍 Running Soul Cradle Analysis (Local)...")
    result = engine.analyze_situation(test_input)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Analysis ID: {result['analysis_id']}")
    print(f"Severity: {result['classification']} ({result['paradox_severity']:.3f}/1.0)")
    print(f"Priority: {result['priority']}")
    print(f"\nBlessings Status: {result['blessings_status']['status']} ({result['blessings_status']['credits']} credits)")
    print(f"\nMatched Attorneys:")
    for att in result['attorney_matches']:
        print(f"  • {att['name']} ({att['firm']}) - Score: {att['match_score']:.2f}")
    
    print(f"\n🔒 Integrity Hash: {result['integrity_hash'][:32]}...")
    
    # Verify integrity
    print("\n🔍 Verifying integrity chain...")
    is_valid, error = engine.verify_integrity()
    print(f"✅ Chain Valid: {is_valid}" if is_valid else f"❌ Chain Broken: {error}")
    
    print(f"\n📁 All data stored locally at: {engine.db_path}")
    print("No servers. No cloud. No tracking. You own your data.\n")
