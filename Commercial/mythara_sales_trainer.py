#!/usr/bin/env python3
"""
Mythara Sales Trainer - AI Sales Coaching Platform
Pitch analysis, objection handling, role-play simulation with Soul Cradle confidence detection

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

# Mythara Engine integration (when SDK available)
try:
    from mythara_engine_sdk import MytharaEngine, ProductConfig
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  Mythara Engine SDK not available - running in standalone mode")


class PitchQuality(Enum):
    """Pitch confidence levels"""
    WEAK = "WEAK"           # Multiple weak phrases, low confidence
    MODERATE = "MODERATE"   # Some weak phrases, needs improvement
    STRONG = "STRONG"       # Confident language, assertive
    EXCELLENT = "EXCELLENT" # Perfect pitch, executive-level


class ObjectionType(Enum):
    """Common sales objections"""
    PRICE = "PRICE"
    TIMING = "TIMING"
    COMPETITION = "COMPETITION"
    AUTHORITY = "AUTHORITY"
    NEED = "NEED"
    TRUST = "TRUST"


@dataclass
class PitchAnalysis:
    """Analysis of sales pitch"""
    pitch_id: str
    rep_id: str
    pitch_text: str
    confidence_score: float  # 0.0-1.0
    weak_phrases: List[str]
    strong_phrases: List[str]
    quality: PitchQuality
    recommendations: List[str]
    timestamp: datetime
    credits_earned: int


@dataclass
class ObjectionResponse:
    """Objection handling response"""
    objection_id: str
    rep_id: str
    objection_type: ObjectionType
    customer_objection: str
    rep_response: str
    effectiveness_score: float  # 0.0-1.0
    recommendations: List[str]
    timestamp: datetime
    credits_earned: int


@dataclass
class RolePlaySession:
    """Role-play simulation session"""
    session_id: str
    rep_id: str
    scenario: str
    customer_profile: Dict[str, Any]
    transcript: List[Dict[str, str]]  # [{"speaker": "rep/customer", "message": "..."}]
    outcome: str  # "won", "lost", "undecided"
    performance_score: float
    timestamp: datetime
    credits_earned: int


class SalesTrainer:
    """
    Mythara Sales Trainer - AI Sales Coaching Platform
    
    Features:
    - Pitch confidence analysis (weak language detection)
    - Objection handling coaching (coercion avoidance)
    - Role-play simulation (distress = customer pushback)
    - Team leaderboards (credit-based gamification)
    """
    
    def __init__(self, rep_id: str, database_path: Optional[str] = None):
        self.rep_id = rep_id
        
        # Database setup
        if database_path:
            self.db_path = database_path
        else:
            home_dir = os.path.expanduser("~")
            mythara_dir = os.path.join(home_dir, ".mythara_engine", "SalesTrainer")
            os.makedirs(mythara_dir, exist_ok=True)
            self.db_path = os.path.join(mythara_dir, "sales_trainer.db")
        
        self._init_database()
        
        # Mythara Engine integration
        if SDK_AVAILABLE:
            config = ProductConfig(
                product_name="SalesTrainer",
                product_version="1.0.0",
                database_name=self.db_path,
                custom_clauses=["confidence_check", "objection_handler"],
                branding={"tagline": "Close More Deals with Confidence"}
            )
            self.engine = MytharaEngine(config, user_id=rep_id)
        else:
            self.engine = None
        
        # Weak language patterns (reduce confidence score)
        self.weak_phrases = [
            "i think", "maybe", "probably", "possibly", "hopefully",
            "kind of", "sort of", "i guess", "i suppose", "might",
            "perhaps", "just wondering", "if you want", "would you mind",
            "sorry to bother", "i'm not sure", "could you maybe"
        ]
        
        # Strong language patterns (increase confidence score)
        # Note: phrases implying clients/results ("our clients see",
        # "proven results") were removed — we have no customers and no measured
        # results, and the sales bot's compliance rules forbid claiming them.
        self.strong_phrases = [
            "i recommend", "you'll benefit from", "this solves",
            "guarantee", "best solution",
            "this delivers", "you need",
            "let's schedule", "here's what we'll do", "commitment"
        ]
        
        print(f"\n🎯 Mythara Sales Trainer initialized for rep: {rep_id}")
        print(f"📊 Database: {self.db_path}")
        if self.engine:
            print(f"✅ Mythara Engine SDK: ACTIVE")
        print()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reps (
                rep_id TEXT PRIMARY KEY,
                name TEXT,
                team TEXT,
                total_credits INTEGER DEFAULT 0,
                total_pitches INTEGER DEFAULT 0,
                total_objections INTEGER DEFAULT 0,
                total_roleplay_sessions INTEGER DEFAULT 0,
                avg_confidence_score REAL DEFAULT 0.0,
                created_at TEXT,
                last_active TEXT
            )
        """)
        
        # Pitches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pitches (
                pitch_id TEXT PRIMARY KEY,
                rep_id TEXT,
                pitch_text TEXT,
                confidence_score REAL,
                weak_phrases TEXT,  -- JSON array
                strong_phrases TEXT,  -- JSON array
                quality TEXT,
                recommendations TEXT,  -- JSON array
                credits_earned INTEGER,
                timestamp TEXT,
                integrity_hash TEXT,
                FOREIGN KEY (rep_id) REFERENCES reps(rep_id)
            )
        """)
        
        # Objections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objections (
                objection_id TEXT PRIMARY KEY,
                rep_id TEXT,
                objection_type TEXT,
                customer_objection TEXT,
                rep_response TEXT,
                effectiveness_score REAL,
                recommendations TEXT,  -- JSON array
                credits_earned INTEGER,
                timestamp TEXT,
                integrity_hash TEXT,
                FOREIGN KEY (rep_id) REFERENCES reps(rep_id)
            )
        """)
        
        # Role-play sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roleplay_sessions (
                session_id TEXT PRIMARY KEY,
                rep_id TEXT,
                scenario TEXT,
                customer_profile TEXT,  -- JSON
                transcript TEXT,  -- JSON array
                outcome TEXT,
                performance_score REAL,
                credits_earned INTEGER,
                timestamp TEXT,
                integrity_hash TEXT,
                FOREIGN KEY (rep_id) REFERENCES reps(rep_id)
            )
        """)
        
        # Leaderboard view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS leaderboard AS
            SELECT 
                rep_id,
                name,
                team,
                total_credits,
                total_pitches,
                avg_confidence_score,
                RANK() OVER (ORDER BY total_credits DESC) as rank
            FROM reps
            ORDER BY total_credits DESC
        """)
        
        conn.commit()
        conn.close()
        
        # Create rep if doesn't exist
        self._create_rep_if_not_exists()
    
    def _create_rep_if_not_exists(self):
        """Create rep record if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT rep_id FROM reps WHERE rep_id = ?", (self.rep_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO reps (rep_id, name, team, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (self.rep_id, f"Rep_{self.rep_id[:8]}", "Default", 
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
            conn.commit()
        
        conn.close()
    
    def _compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def analyze_pitch(self, pitch_text: str) -> PitchAnalysis:
        """
        Analyze sales pitch for confidence and language quality
        
        Returns PitchAnalysis with:
        - Confidence score (0.0-1.0)
        - Weak phrases detected
        - Strong phrases detected
        - Quality rating
        - Recommendations
        - Credits earned
        """
        pitch_id = f"PITCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.rep_id[:8]}"
        pitch_lower = pitch_text.lower()
        
        # Detect weak phrases
        weak_detected = [phrase for phrase in self.weak_phrases if phrase in pitch_lower]
        
        # Detect strong phrases
        strong_detected = [phrase for phrase in self.strong_phrases if phrase in pitch_lower]
        
        # Calculate confidence score
        base_score = 0.5
        weak_penalty = len(weak_detected) * 0.08
        strong_bonus = len(strong_detected) * 0.12
        confidence_score = max(0.0, min(1.0, base_score - weak_penalty + strong_bonus))
        
        # Determine quality
        if confidence_score >= 0.9:
            quality = PitchQuality.EXCELLENT
            credits = 20
        elif confidence_score >= 0.75:
            quality = PitchQuality.STRONG
            credits = 15
        elif confidence_score >= 0.5:
            quality = PitchQuality.MODERATE
            credits = 10
        else:
            quality = PitchQuality.WEAK
            credits = 5
        
        # Generate recommendations
        recommendations = []
        if weak_detected:
            recommendations.append(f"Remove weak phrases: {', '.join(weak_detected[:3])}")
            recommendations.append("Use assertive language: 'I recommend' instead of 'I think'")
        if len(strong_detected) < 2:
            recommendations.append("Add more confident phrases: 'here is what we will do', 'best solution'")
        if "?" in pitch_text and pitch_text.count("?") > 2:
            recommendations.append("Reduce questions - make statements instead")
        if confidence_score < 0.7:
            recommendations.append("Practice with role-play scenarios to build confidence")
        
        analysis = PitchAnalysis(
            pitch_id=pitch_id,
            rep_id=self.rep_id,
            pitch_text=pitch_text,
            confidence_score=confidence_score,
            weak_phrases=weak_detected,
            strong_phrases=strong_detected,
            quality=quality,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            credits_earned=credits
        )
        
        # Store in database
        self._store_pitch_analysis(analysis)
        
        # Award credits
        self._award_credits(credits, "Pitch analysis completed")
        
        # Mythara Engine integration
        if self.engine:
            self.engine.soul_cradle.analyze(pitch_text)
            self.engine.blessings.award_credits(self.rep_id, credits, "Pitch confidence training")
        
        return analysis
    
    def _store_pitch_analysis(self, analysis: PitchAnalysis):
        """Store pitch analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compute integrity hash
        data = {
            "pitch_id": analysis.pitch_id,
            "rep_id": analysis.rep_id,
            "confidence_score": analysis.confidence_score,
            "quality": analysis.quality.value
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        cursor.execute("""
            INSERT INTO pitches 
            (pitch_id, rep_id, pitch_text, confidence_score, weak_phrases, 
             strong_phrases, quality, recommendations, credits_earned, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis.pitch_id, analysis.rep_id, analysis.pitch_text,
            analysis.confidence_score, json.dumps(analysis.weak_phrases),
            json.dumps(analysis.strong_phrases), analysis.quality.value,
            json.dumps(analysis.recommendations), analysis.credits_earned,
            analysis.timestamp.isoformat(), integrity_hash
        ))
        
        # Update rep stats
        cursor.execute("""
            UPDATE reps 
            SET total_pitches = total_pitches + 1,
                avg_confidence_score = (
                    SELECT AVG(confidence_score) FROM pitches WHERE rep_id = ?
                ),
                last_active = ?
            WHERE rep_id = ?
        """, (self.rep_id, datetime.utcnow().isoformat(), self.rep_id))
        
        conn.commit()
        conn.close()
    
    def handle_objection(self, objection_type: ObjectionType, customer_objection: str, 
                        rep_response: str) -> ObjectionResponse:
        """
        Coach on objection handling
        
        Returns ObjectionResponse with:
        - Effectiveness score
        - Recommendations for improvement
        - Credits earned
        """
        objection_id = f"OBJ_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.rep_id[:8]}"
        
        # Analyze response effectiveness
        response_lower = rep_response.lower()
        
        # Check for coercion/manipulation (BAD)
        coercion_phrases = ["you have to", "you must", "no choice", "everyone else", "limited time"]
        coercion_detected = any(phrase in response_lower for phrase in coercion_phrases)
        
        # Check for empathy (GOOD)
        empathy_phrases = ["i understand", "i hear you", "that makes sense", "appreciate your concern"]
        empathy_detected = any(phrase in response_lower for phrase in empathy_phrases)
        
        # Check for value proposition (GOOD)
        value_phrases = ["benefit", "save", "roi", "proven", "results", "solution"]
        value_detected = any(phrase in response_lower for phrase in value_phrases)
        
        # Calculate effectiveness score
        base_score = 0.5
        if coercion_detected:
            base_score -= 0.3  # Heavy penalty for manipulation
        if empathy_detected:
            base_score += 0.2
        if value_detected:
            base_score += 0.2
        
        effectiveness_score = max(0.0, min(1.0, base_score))
        
        # Generate recommendations
        recommendations = []
        if coercion_detected:
            recommendations.append("⚠️ AVOID manipulation tactics - use empathy instead")
        if not empathy_detected:
            recommendations.append("Start with empathy: 'I understand your concern about...'")
        if not value_detected:
            recommendations.append("Emphasize value: 'Here's how this saves you...'")
        
        # Objection-specific coaching
        if objection_type == ObjectionType.PRICE:
            recommendations.append("Reframe as investment: 'For $X, you'll save $Y in 6 months'")
        elif objection_type == ObjectionType.TIMING:
            recommendations.append("Create urgency honestly: 'If we start now, you can be live before next quarter'")
        elif objection_type == ObjectionType.COMPETITION:
            recommendations.append("Differentiate: 'Unlike competitor X, we offer Y which saves you Z'")
        
        # Credits based on effectiveness
        if effectiveness_score >= 0.8:
            credits = 20
        elif effectiveness_score >= 0.6:
            credits = 15
        elif effectiveness_score >= 0.4:
            credits = 10
        else:
            credits = 5
        
        response_obj = ObjectionResponse(
            objection_id=objection_id,
            rep_id=self.rep_id,
            objection_type=objection_type,
            customer_objection=customer_objection,
            rep_response=rep_response,
            effectiveness_score=effectiveness_score,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            credits_earned=credits
        )
        
        # Store in database
        self._store_objection_response(response_obj)
        
        # Award credits
        self._award_credits(credits, f"Objection handling: {objection_type.value}")
        
        # Mythara Engine integration
        if self.engine:
            # Detect coercion with Soul Cradle
            self.engine.soul_cradle.analyze(rep_response)
            self.engine.blessings.award_credits(self.rep_id, credits, "Objection handling training")
        
        return response_obj
    
    def _store_objection_response(self, response: ObjectionResponse):
        """Store objection response in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {
            "objection_id": response.objection_id,
            "rep_id": response.rep_id,
            "effectiveness_score": response.effectiveness_score
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        cursor.execute("""
            INSERT INTO objections 
            (objection_id, rep_id, objection_type, customer_objection, rep_response,
             effectiveness_score, recommendations, credits_earned, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            response.objection_id, response.rep_id, response.objection_type.value,
            response.customer_objection, response.rep_response, response.effectiveness_score,
            json.dumps(response.recommendations), response.credits_earned,
            response.timestamp.isoformat(), integrity_hash
        ))
        
        # Update rep stats
        cursor.execute("""
            UPDATE reps 
            SET total_objections = total_objections + 1,
                last_active = ?
            WHERE rep_id = ?
        """, (datetime.utcnow().isoformat(), self.rep_id))
        
        conn.commit()
        conn.close()
    
    def _award_credits(self, credits: int, reason: str):
        """Award credits to rep"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reps 
            SET total_credits = total_credits + ?
            WHERE rep_id = ?
        """, (credits, self.rep_id))
        
        conn.commit()
        conn.close()
        
        print(f"💰 +{credits} credits: {reason}")
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top performers leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rank, rep_id, name, team, total_credits, total_pitches, avg_confidence_score
            FROM leaderboard
            LIMIT ?
        """, (top_n,))
        
        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                "rank": row[0],
                "rep_id": row[1],
                "name": row[2],
                "team": row[3],
                "total_credits": row[4],
                "total_pitches": row[5],
                "avg_confidence_score": round(row[6], 2)
            })
        
        conn.close()
        return leaderboard
    
    def get_rep_stats(self) -> Dict[str, Any]:
        """Get rep performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                total_credits, total_pitches, total_objections, 
                total_roleplay_sessions, avg_confidence_score
            FROM reps
            WHERE rep_id = ?
        """, (self.rep_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "rep_id": self.rep_id,
                "total_credits": row[0],
                "total_pitches": row[1],
                "total_objections": row[2],
                "total_roleplay_sessions": row[3],
                "avg_confidence_score": round(row[4], 2)
            }
        return {}


def main():
    """Demo: Sales Trainer usage"""
    print("="*70)
    print("    MYTHARA SALES TRAINER - AI SALES COACHING PLATFORM")
    print("="*70)
    
    # Initialize trainer
    trainer = SalesTrainer(rep_id="rep_12345")
    
    # Demo 1: Analyze weak pitch
    print("\n📊 DEMO 1: Weak Pitch Analysis")
    print("-"*70)
    weak_pitch = """
    I think our product might be able to help you. Maybe you could try it? 
    I'm not sure if it's the right fit, but hopefully it could work for you.
    If you want, we could schedule a demo. Would you mind taking a look?
    """
    analysis = trainer.analyze_pitch(weak_pitch)
    print(f"\n🎯 Pitch Analysis:")
    print(f"   Confidence Score: {analysis.confidence_score:.2f}")
    print(f"   Quality: {analysis.quality.value}")
    print(f"   Weak Phrases: {', '.join(analysis.weak_phrases[:5])}")
    print(f"   Credits Earned: {analysis.credits_earned}")
    print(f"\n💡 Recommendations:")
    for rec in analysis.recommendations:
        print(f"   • {rec}")
    
    # Demo 2: Analyze strong pitch
    print("\n📊 DEMO 2: Strong Pitch Analysis")
    print("-"*70)
    strong_pitch = """
    I recommend our Enterprise solution. This solves your scalability challenge 
    and most teams that automate this step free up hours every week. 
    Let's schedule implementation for next week. Here's what we'll do...
    """
    analysis2 = trainer.analyze_pitch(strong_pitch)
    print(f"\n🎯 Pitch Analysis:")
    print(f"   Confidence Score: {analysis2.confidence_score:.2f}")
    print(f"   Quality: {analysis2.quality.value}")
    print(f"   Strong Phrases: {', '.join(analysis2.strong_phrases)}")
    print(f"   Credits Earned: {analysis2.credits_earned}")
    
    # Demo 3: Objection handling
    print("\n📊 DEMO 3: Objection Handling")
    print("-"*70)
    objection = "Your pricing is too high compared to competitors."
    
    # Bad response (coercion)
    bad_response = "You have to buy now or you'll lose this deal. Everyone else is signing up!"
    response1 = trainer.handle_objection(
        ObjectionType.PRICE, 
        objection, 
        bad_response
    )
    print(f"\n❌ Bad Response (Coercion):")
    print(f"   Effectiveness Score: {response1.effectiveness_score:.2f}")
    print(f"   Credits: {response1.credits_earned}")
    print(f"   Recommendations:")
    for rec in response1.recommendations:
        print(f"   {rec}")
    
    # Good response (empathy + value)
    good_response = """
    I understand your concern about pricing. Let's work the numbers together:
    if this saves your team five hours a week, that's roughly 260 hours a year.
    Compare that against the price and see whether it beats your current setup.
    """
    response2 = trainer.handle_objection(
        ObjectionType.PRICE,
        objection,
        good_response
    )
    print(f"\n✅ Good Response (Empathy + Value):")
    print(f"   Effectiveness Score: {response2.effectiveness_score:.2f}")
    print(f"   Credits: {response2.credits_earned}")
    
    # Demo 4: Leaderboard
    print("\n📊 DEMO 4: Team Leaderboard")
    print("-"*70)
    leaderboard = trainer.get_leaderboard(top_n=5)
    print(f"\n🏆 Top Performers:")
    for entry in leaderboard:
        print(f"   #{entry['rank']} {entry['name']} - {entry['total_credits']} credits")
        print(f"        Pitches: {entry['total_pitches']} | Avg Confidence: {entry['avg_confidence_score']}")
    
    # Demo 5: Rep stats
    print("\n📊 DEMO 5: Rep Performance")
    print("-"*70)
    stats = trainer.get_rep_stats()
    print(f"\n📈 Your Stats:")
    print(f"   Total Credits: {stats['total_credits']}")
    print(f"   Pitches Analyzed: {stats['total_pitches']}")
    print(f"   Objections Handled: {stats['total_objections']}")
    print(f"   Avg Confidence: {stats['avg_confidence_score']}")
    
    print("\n" + "="*70)
    print("✅ Sales Trainer demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
