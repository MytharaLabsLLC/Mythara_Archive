#!/usr/bin/env python3
"""
Mythara VOIP Bot - Call-Logging CRM
Records call metadata, transcripts, keyword-based sentiment flags, and
supervisor escalations in SQLite. It places NO phone calls: an earlier
version constructed a Twilio client that was never used, and that
integration has been removed entirely. Nothing in this module dials out.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
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


class CallSentiment(Enum):
    """Real-time sentiment during call"""
    POSITIVE = "POSITIVE"       # Customer happy, engaged
    NEUTRAL = "NEUTRAL"         # Normal conversation
    FRUSTRATED = "FRUSTRATED"   # Customer frustrated, needs patience
    ANGRY = "ANGRY"             # Customer angry, needs supervisor
    DISTRESSED = "DISTRESSED"   # Customer in crisis, immediate escalation


class EscalationReason(Enum):
    """Reasons for supervisor escalation"""
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    HIGH_ANGER = "HIGH_ANGER"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    AUTHORIZATION_NEEDED = "AUTHORIZATION_NEEDED"
    DISTRESS_DETECTED = "DISTRESS_DETECTED"


@dataclass
class Call:
    """Phone call record"""
    call_id: str
    customer_phone: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    sentiment_history: List[Dict[str, Any]]  # [{"timestamp": "...", "sentiment": "...", "score": 0.8}]
    escalated: bool
    escalation_reason: Optional[EscalationReason]
    resolution: str  # "resolved", "escalated", "dropped", "callback_scheduled"
    transcript: List[Dict[str, str]]  # [{"speaker": "customer/agent", "text": "...", "timestamp": "..."}]
    integrity_hash: str


@dataclass
class Agent:
    """VOIP agent profile"""
    agent_id: str
    name: str
    active_calls: int
    total_calls: int
    total_escalations: int
    avg_call_duration: float
    avg_sentiment_score: float
    status: str  # "available", "on_call", "break", "offline"


class VOIPBot:
    """
    Mythara VOIP Bot - Call-Logging CRM.

    Records call metadata, transcripts, keyword-based sentiment flags, and
    supervisor escalations in SQLite. Places no phone calls — start_call()
    opens a call *record* (logging), it does not dial anyone.
    """

    def __init__(self, agent_id: str, database_path: Optional[str] = None):
        self.agent_id = agent_id
        
        # Database setup
        if database_path:
            self.db_path = database_path
        else:
            home_dir = os.path.expanduser("~")
            mythara_dir = os.path.join(home_dir, ".mythara_engine", "VOIPBot")
            os.makedirs(mythara_dir, exist_ok=True)
            self.db_path = os.path.join(mythara_dir, "voip_bot.db")
        
        self._init_database()

        # Mythara Engine integration
        if SDK_AVAILABLE:
            config = ProductConfig(
                product_name="VOIPBot",
                product_version="1.0.0",
                database_name=self.db_path,
                custom_clauses=["sentiment_check", "distress_escalation"],
                branding={"tagline": "Call-Logging CRM"}
            )
            self.engine = MytharaEngine(config, user_id=agent_id)
        else:
            self.engine = None
        
        # Sentiment keywords
        self.positive_keywords = ["thank", "great", "excellent", "perfect", "appreciate", "helpful"]
        self.neutral_keywords = ["okay", "fine", "yes", "no", "understand", "got it"]
        self.frustrated_keywords = ["frustrated", "annoying", "difficult", "confused", "why"]
        self.angry_keywords = ["angry", "ridiculous", "unacceptable", "terrible", "worst", "manager"]
        self.distress_keywords = ["suicide", "kill myself", "end it", "can't go on", "hopeless"]
        
        print(f"\n📞 Mythara VOIP Bot initialized for agent: {agent_id}")
        print(f"📊 Database: {self.db_path}")
        if self.engine:
            print(f"✅ Mythara Engine SDK: ACTIVE")
        print()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                active_calls INTEGER DEFAULT 0,
                total_calls INTEGER DEFAULT 0,
                total_escalations INTEGER DEFAULT 0,
                avg_call_duration REAL DEFAULT 0.0,
                avg_sentiment_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'offline',
                created_at TEXT,
                last_active TEXT
            )
        """)
        
        # Calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                call_id TEXT PRIMARY KEY,
                customer_phone TEXT,
                agent_id TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds INTEGER,
                sentiment_history TEXT,  -- JSON array
                escalated INTEGER,
                escalation_reason TEXT,
                resolution TEXT,
                transcript TEXT,  -- JSON array
                integrity_hash TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)
        
        # Escalations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                call_id TEXT,
                agent_id TEXT,
                supervisor_id TEXT,
                reason TEXT,
                timestamp TEXT,
                resolved INTEGER DEFAULT 0,
                resolution_notes TEXT,
                FOREIGN KEY (call_id) REFERENCES calls(call_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Create agent if doesn't exist
        self._create_agent_if_not_exists()
    
    def _create_agent_if_not_exists(self):
        """Create agent record if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT agent_id FROM agents WHERE agent_id = ?", (self.agent_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO agents (agent_id, name, status, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (self.agent_id, f"Agent_{self.agent_id[:8]}", "available",
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
            conn.commit()
        
        conn.close()
    
    def _compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of customer statement
        
        Returns:
        - sentiment: CallSentiment enum
        - score: float (0.0-1.0, higher = more positive)
        - keywords_detected: List[str]
        """
        text_lower = text.lower()
        
        # Count keyword matches
        positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
        neutral_count = sum(1 for kw in self.neutral_keywords if kw in text_lower)
        frustrated_count = sum(1 for kw in self.frustrated_keywords if kw in text_lower)
        angry_count = sum(1 for kw in self.angry_keywords if kw in text_lower)
        distress_count = sum(1 for kw in self.distress_keywords if kw in text_lower)
        
        # Determine sentiment
        if distress_count > 0:
            sentiment = CallSentiment.DISTRESSED
            score = 0.0
            keywords = [kw for kw in self.distress_keywords if kw in text_lower]
        elif angry_count >= 2 or "manager" in text_lower:
            sentiment = CallSentiment.ANGRY
            score = 0.2
            keywords = [kw for kw in self.angry_keywords if kw in text_lower]
        elif frustrated_count >= 2:
            sentiment = CallSentiment.FRUSTRATED
            score = 0.4
            keywords = [kw for kw in self.frustrated_keywords if kw in text_lower]
        elif positive_count >= 2:
            sentiment = CallSentiment.POSITIVE
            score = 0.9
            keywords = [kw for kw in self.positive_keywords if kw in text_lower]
        else:
            sentiment = CallSentiment.NEUTRAL
            score = 0.6
            keywords = []
        
        return {
            "sentiment": sentiment,
            "score": score,
            "keywords_detected": keywords
        }
    
    def start_call(self, customer_phone: str) -> str:
        """
        Open a new call *record* in the log (metadata only).

        This does NOT place a phone call — this module has no dialing
        capability at all. Returns call_id.
        """
        call_id = f"CALL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{customer_phone[-4:]}"
        
        # Update agent status
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agents
            SET active_calls = active_calls + 1,
                status = 'on_call',
                last_active = ?
            WHERE agent_id = ?
        """, (datetime.utcnow().isoformat(), self.agent_id))
        
        # Create call record
        data = {
            "call_id": call_id,
            "customer_phone": customer_phone,
            "agent_id": self.agent_id,
            "start_time": datetime.utcnow().isoformat()
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        cursor.execute("""
            INSERT INTO calls 
            (call_id, customer_phone, agent_id, start_time, duration_seconds,
             sentiment_history, escalated, resolution, transcript, integrity_hash)
            VALUES (?, ?, ?, ?, 0, '[]', 0, 'in_progress', '[]', ?)
        """, (call_id, customer_phone, self.agent_id, data["start_time"], integrity_hash))
        
        conn.commit()
        conn.close()
        
        print(f"📞 Call started: {call_id}")
        print(f"   Customer: {customer_phone}")
        print(f"   Agent: {self.agent_id}")
        
        return call_id
    
    def process_message(self, call_id: str, speaker: str, message: str) -> Dict[str, Any]:
        """
        Process message during call (customer or agent)
        
        Returns:
        - sentiment_analysis: Dict
        - escalation_needed: bool
        - escalation_reason: Optional[EscalationReason]
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Analyze sentiment
        sentiment_analysis = self.analyze_sentiment(message)
        
        # Store transcript
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT transcript, sentiment_history FROM calls WHERE call_id = ?", (call_id,))
        row = cursor.fetchone()
        
        if row:
            transcript = json.loads(row[0])
            sentiment_history = json.loads(row[1])
            
            # Add message to transcript
            transcript.append({
                "speaker": speaker,
                "text": message,
                "timestamp": timestamp
            })
            
            # Add sentiment to history (customer only)
            if speaker == "customer":
                sentiment_history.append({
                    "timestamp": timestamp,
                    "sentiment": sentiment_analysis["sentiment"].value,
                    "score": sentiment_analysis["score"]
                })
            
            # Update call record
            cursor.execute("""
                UPDATE calls
                SET transcript = ?,
                    sentiment_history = ?
                WHERE call_id = ?
            """, (json.dumps(transcript), json.dumps(sentiment_history), call_id))
            
            conn.commit()
        
        conn.close()
        
        # Determine if escalation needed
        escalation_needed = False
        escalation_reason = None
        
        if sentiment_analysis["sentiment"] == CallSentiment.DISTRESSED:
            escalation_needed = True
            escalation_reason = EscalationReason.DISTRESS_DETECTED
            print(f"🚨 DISTRESS DETECTED - Immediate escalation required!")
        elif sentiment_analysis["sentiment"] == CallSentiment.ANGRY:
            escalation_needed = True
            escalation_reason = EscalationReason.HIGH_ANGER
            print(f"⚠️ High anger detected - Consider escalation")
        elif "manager" in message.lower() or "supervisor" in message.lower():
            escalation_needed = True
            escalation_reason = EscalationReason.CUSTOMER_REQUEST
            print(f"📞 Customer requested supervisor")
        
        # Mythara Engine integration
        if self.engine and speaker == "customer":
            # Soul Cradle analyzes distress
            self.engine.soul_cradle.analyze(message)
        
        return {
            "sentiment_analysis": sentiment_analysis,
            "escalation_needed": escalation_needed,
            "escalation_reason": escalation_reason
        }
    
    def escalate_call(self, call_id: str, reason: EscalationReason, 
                     supervisor_id: str = "supervisor_001") -> str:
        """
        Escalate call to supervisor
        
        Returns escalation_id
        """
        escalation_id = f"ESC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{call_id[-8:]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mark call as escalated
        cursor.execute("""
            UPDATE calls
            SET escalated = 1,
                escalation_reason = ?
            WHERE call_id = ?
        """, (reason.value, call_id))
        
        # Create escalation record
        cursor.execute("""
            INSERT INTO escalations
            (escalation_id, call_id, agent_id, supervisor_id, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (escalation_id, call_id, self.agent_id, supervisor_id, reason.value,
              datetime.utcnow().isoformat()))
        
        # Update agent stats
        cursor.execute("""
            UPDATE agents
            SET total_escalations = total_escalations + 1
            WHERE agent_id = ?
        """, (self.agent_id,))
        
        conn.commit()
        conn.close()
        
        print(f"📞 Call escalated: {escalation_id}")
        print(f"   Reason: {reason.value}")
        print(f"   Supervisor: {supervisor_id}")
        
        return escalation_id
    
    def end_call(self, call_id: str, resolution: str = "resolved") -> Call:
        """
        End call and compute final metrics
        
        Returns Call object with full details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get call details
        cursor.execute("""
            SELECT customer_phone, agent_id, start_time, sentiment_history,
                   escalated, escalation_reason, transcript
            FROM calls
            WHERE call_id = ?
        """, (call_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Call {call_id} not found")
        
        customer_phone, agent_id, start_time_str, sentiment_history_str, \
            escalated, escalation_reason, transcript_str = row
        
        # Calculate duration
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.utcnow()
        duration_seconds = int((end_time - start_time).total_seconds())
        
        # Update call record
        cursor.execute("""
            UPDATE calls
            SET end_time = ?,
                duration_seconds = ?,
                resolution = ?
            WHERE call_id = ?
        """, (end_time.isoformat(), duration_seconds, resolution, call_id))
        
        # Update agent stats
        cursor.execute("""
            UPDATE agents
            SET active_calls = active_calls - 1,
                total_calls = total_calls + 1,
                status = 'available',
                avg_call_duration = (
                    SELECT AVG(duration_seconds) FROM calls WHERE agent_id = ? AND end_time IS NOT NULL
                ),
                last_active = ?
            WHERE agent_id = ?
        """, (agent_id, datetime.utcnow().isoformat(), agent_id))
        
        conn.commit()
        conn.close()
        
        # Create Call object
        sentiment_history = json.loads(sentiment_history_str)
        transcript = json.loads(transcript_str)
        
        data = {
            "call_id": call_id,
            "customer_phone": customer_phone,
            "duration_seconds": duration_seconds
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        call = Call(
            call_id=call_id,
            customer_phone=customer_phone,
            agent_id=agent_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            sentiment_history=sentiment_history,
            escalated=bool(escalated),
            escalation_reason=EscalationReason(escalation_reason) if escalation_reason else None,
            resolution=resolution,
            transcript=transcript,
            integrity_hash=integrity_hash
        )
        
        print(f"📞 Call ended: {call_id}")
        print(f"   Duration: {duration_seconds}s ({duration_seconds // 60}m {duration_seconds % 60}s)")
        print(f"   Resolution: {resolution}")
        print(f"   Escalated: {call.escalated}")
        
        return call
    
    def get_agent_stats(self) -> Agent:
        """Get agent performance stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                name, active_calls, total_calls, total_escalations,
                avg_call_duration, avg_sentiment_score, status
            FROM agents
            WHERE agent_id = ?
        """, (self.agent_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Agent(
                agent_id=self.agent_id,
                name=row[0],
                active_calls=row[1],
                total_calls=row[2],
                total_escalations=row[3],
                avg_call_duration=row[4],
                avg_sentiment_score=row[5],
                status=row[6]
            )
        return None


def main():
    """Demo: VOIP Bot call-logging usage (records only — places no calls)"""
    print("="*70)
    print("    MYTHARA VOIP BOT - CALL-LOGGING CRM (places no calls)")
    print("="*70)
    
    # Initialize bot
    bot = VOIPBot(agent_id="agent_001")
    
    # Demo 1: Positive call
    print("\n📞 DEMO 1: Positive Customer Call")
    print("-"*70)
    call_id = bot.start_call(customer_phone="+1-555-0101")
    
    # Customer messages
    result1 = bot.process_message(call_id, "customer", "Hi, I need help with my account.")
    print(f"Sentiment: {result1['sentiment_analysis']['sentiment'].value} (score: {result1['sentiment_analysis']['score']})")
    
    result2 = bot.process_message(call_id, "agent", "I'd be happy to help! Let me pull up your account.")
    
    result3 = bot.process_message(call_id, "customer", "Thank you! This is great, you've been so helpful.")
    print(f"Sentiment: {result3['sentiment_analysis']['sentiment'].value} (score: {result3['sentiment_analysis']['score']})")
    
    call = bot.end_call(call_id, resolution="resolved")
    
    # Demo 2: Angry customer (escalation)
    print("\n📞 DEMO 2: Angry Customer (Escalation)")
    print("-"*70)
    call_id2 = bot.start_call(customer_phone="+1-555-0202")
    
    result4 = bot.process_message(call_id2, "customer", "This is ridiculous! I've been waiting for 2 weeks!")
    print(f"Sentiment: {result4['sentiment_analysis']['sentiment'].value}")
    
    result5 = bot.process_message(call_id2, "customer", "This is unacceptable. I want to speak to a manager NOW!")
    print(f"Sentiment: {result5['sentiment_analysis']['sentiment'].value}")
    print(f"Escalation needed: {result5['escalation_needed']}")
    print(f"Reason: {result5['escalation_reason'].value if result5['escalation_reason'] else 'N/A'}")
    
    if result5['escalation_needed']:
        escalation_id = bot.escalate_call(call_id2, result5['escalation_reason'])
    
    call2 = bot.end_call(call_id2, resolution="escalated")
    
    # Demo 3: Distress detection (CRITICAL)
    print("\n📞 DEMO 3: Distress Detection (CRITICAL)")
    print("-"*70)
    call_id3 = bot.start_call(customer_phone="+1-555-0303")
    
    result6 = bot.process_message(call_id3, "customer", "I can't take this anymore. I just can't go on.")
    print(f"🚨 Sentiment: {result6['sentiment_analysis']['sentiment'].value}")
    print(f"🚨 IMMEDIATE ESCALATION: {result6['escalation_needed']}")
    
    if result6['escalation_needed']:
        escalation_id = bot.escalate_call(call_id3, EscalationReason.DISTRESS_DETECTED, 
                                         supervisor_id="crisis_team_001")
        print(f"   ✅ Crisis team notified: {escalation_id}")
    
    call3 = bot.end_call(call_id3, resolution="escalated_crisis")
    
    # Demo 4: Agent stats
    print("\n📊 DEMO 4: Agent Performance")
    print("-"*70)
    agent = bot.get_agent_stats()
    print(f"\n📈 Agent Stats:")
    print(f"   Agent ID: {agent.agent_id}")
    print(f"   Name: {agent.name}")
    print(f"   Status: {agent.status}")
    print(f"   Total Calls: {agent.total_calls}")
    print(f"   Active Calls: {agent.active_calls}")
    print(f"   Total Escalations: {agent.total_escalations}")
    print(f"   Avg Call Duration: {agent.avg_call_duration:.1f}s")
    
    print("\n" + "="*70)
    print("✅ VOIP Bot demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
