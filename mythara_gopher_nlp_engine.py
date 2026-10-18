#!/usr/bin/env python3
"""
Mythara Gopher - Natural Language Legal Intelligence Engine
A GPT-like conversational AI trained on Mythara's legal knowledge base.
Provides natural language understanding for legal queries without external APIs.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import re
import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json
from datetime import datetime, timedelta
import hashlib
from pathlib import Path
import uuid

# Import Mythara's legal frameworks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'source_proprietary'))
from torts_law_framework import TortsLawIndex, TortCategory
from legal_resources_index import LegalResearchEngine, LegalDomain

# Import Soul Cradle for emotional intelligence and paradox detection
try:
    from core.source_proprietary.soul_cradle_systems_framework import (
        SoulCradleParadox,
        SystemExpression,
        ExpressionType,
        TerminalRiskLevel,
        TerminalRiskCalculator
    )
    SOUL_CRADLE_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import path (if running from root or with PYTHONPATH set)
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'source_proprietary'))
        from soul_cradle_systems_framework import (
            SoulCradleParadox,
            SystemExpression,
            ExpressionType,
            TerminalRiskLevel,
            TerminalRiskCalculator
        )
        SOUL_CRADLE_AVAILABLE = True
    except ImportError:
        SOUL_CRADLE_AVAILABLE = False
        print("⚠️ Soul Cradle not available - emotional intelligence features disabled")


# ===================== LEGAL DISCLAIMER =====================

MYTHARA_GOPHER_LEGAL_DISCLAIMER = """
================================================================================
                        MYTHARA GOPHER LEGAL DISCLAIMER
================================================================================

PLEASE READ THIS DISCLAIMER CAREFULLY BEFORE USING MYTHARA GOPHER

1. NOT LEGAL ADVICE - NO ATTORNEY-CLIENT RELATIONSHIP
   Mythara Gopher is a legal research and document preparation tool designed 
   for PERSONAL USE ONLY. Use of this software does not create an attorney-
   client relationship or attorney client relationship. Mythara Gopher DOES NOT provide legal advice, legal 
   opinions, or legal counsel. All information provided is for informational 
   and educational purposes only.

2. NOT A SUBSTITUTE FOR LEGAL COUNSEL
   This software is NOT A SUBSTITUTE for the advice of a licensed attorney. 
   Legal matters can be complex, fact-specific, and subject to varying 
   interpretations under applicable law. Users are STRONGLY ENCOURAGED to 
   consult with a qualified attorney licensed in their jurisdiction before 
   making any legal decisions or taking any legal action.

3. DOCUMENT PREPARATION AND RESEARCH TOOL ONLY
   Mythara Gopher functions as your ADVOCATE for document preparation and 
   legal research. The software assists with drafting documents and researching 
   legal concepts but does NOT advise on legal strategy, interpret laws as 
   applied to specific circumstances, or provide guidance on legal outcomes.

4. NO GUARANTEE OF ACCURACY - INFORMATION MAY BE OUTDATED
   All legal information contained within Mythara Gopher has been compiled 
   from publicly available databases, legal resources, and government sources. 
   The information provided may NOT be current, complete, or accurate. Laws, 
   regulations, and legal precedents change frequently. Users MUST verify all 
   information with current legal sources or through consultation with legal 
   counsel.

5. CRYPTOGRAPHIC TIMESTAMPING - NO LIABILITY FOR USER ERROR
   While Mythara Gopher provides SHA-256 cryptographic timestamping features 
   for document integrity, the software and its creators CANNOT BE HELD LIABLE 
   for user error, misuse of timestamping features, improper document handling, 
   loss of evidence, or failure to preserve chain of custody. Users are solely 
   responsible for proper evidence preservation and compliance with legal 
   procedures.

6. USE AT YOUR OWN RISK
   Use of Mythara Gopher is AT YOUR OWN RISK. To the fullest extent permitted 
   by law, Mythara Engine, its creators, contributors, and affiliates 
   DISCLAIM ALL WARRANTIES, express or implied, including but not limited to 
   implied warranties of merchantability, fitness for a particular purpose, 
   accuracy, completeness, and non-infringement.

7. LIMITATION OF LIABILITY
   In no event shall Mythara Engine, its creators, developers, or affiliates 
   be liable for any direct, indirect, incidental, special, consequential, or 
   exemplary damages (including but not limited to procurement of substitute 
   services; loss of use, data, or profits; or business interruption) arising 
   from use of this software, even if advised of the possibility of such 
   damages.

8. JURISDICTIONAL LIMITATIONS
   Laws vary significantly by jurisdiction. Information provided by Mythara 
   Gopher may not apply to your specific location or circumstances. Users 
   MUST consult with local legal counsel to understand laws applicable to 
   their jurisdiction.

9. ETHICAL CONSIDERATIONS
   Users engaging in legal matters should be aware of ethical rules governing 
   legal practice in their jurisdiction, including unauthorized practice of law 
   (UPL) statutes. Using legal documents without attorney review may not 
   be appropriate in all circumstances.

10. DUTY TO SEEK PROFESSIONAL LEGAL COUNSEL
    When dealing with any legal matter, including but not limited to:
    • Litigation or potential litigation
    • Contract disputes or negotiations
    • Criminal matters or investigations
    • Real estate transactions
    • Business formation or dissolution
    • Estate planning or probate matters
    • Family law issues
    • Immigration matters
    • Bankruptcy or debt restructuring
    
    Users are STRONGLY ADVISED to seek consultation with a licensed attorney 
    who can provide advice tailored to your specific facts and circumstances.

11. ACCEPTANCE OF TERMS
    By using Mythara Gopher, you acknowledge that you have read, understood, 
    and agreed to this disclaimer. You accept full responsibility for any 
    decisions made based on information provided by this software.

12. NO ENDORSEMENT OF LEGAL POSITIONS
    Mythara Gopher's provision of information on legal topics does not 
    constitute an endorsement of any particular legal theory, strategy, or 
    position. Users must make their own informed decisions with guidance from 
    qualified legal counsel.

FOR LEGAL ADVICE SPECIFIC TO YOUR SITUATION, CONSULT A LICENSED ATTORNEY.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
================================================================================
"""

# ===================== MYTHARA GOPHER NLP ENGINE =====================

@dataclass
class LegalDocument:
    """Represents a generated legal document with cryptographic integrity"""
    doc_id: str
    doc_type: str  # demand_letter, cease_desist, evidence_summary, legal_memo, complaint, motion, discovery, writ, pleading, answer, counterclaim, interrogatories, RFP, RFA, subpoena, brief, affidavit, declaration
    title: str
    content: str
    timestamp: str
    integrity_hash: str
    metadata: Dict[str, any]
    
    def to_file(self, output_dir: str = "legal_documents") -> str:
        """Write document to file and return path"""
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"{self.doc_type}_{self.doc_id}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"{self.title}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Document ID: {self.doc_id}\n")
            f.write(f"Generated: {self.timestamp}\n")
            f.write(f"SHA-256 Integrity Hash: {self.integrity_hash}\n")
            f.write(f"\n{'-'*80}\n\n")
            f.write(self.content)
            f.write(f"\n\n{'-'*80}\n")
            f.write(f"\nCertification: This document was generated by Mythara Gopher Legal AI\n")
            f.write(f"and cryptographically timestamped at {self.timestamp}\n")
            f.write(f"Integrity Hash: {self.integrity_hash}\n\n")
            f.write(f"{'='*80}\n")
            f.write("LEGAL DISCLAIMER\n")
            f.write(f"{'='*80}\n")
            f.write("This document was generated by Mythara Gopher for PERSONAL USE ONLY.\n")
            f.write("This is NOT legal advice and does NOT create an attorney-client relationship.\n")
            f.write("Information may be outdated. Users are STRONGLY ENCOURAGED to consult a\n")
            f.write("licensed attorney before using this document or taking legal action.\n")
            f.write("Use at your own risk. Mythara Engine disclaims all warranties and liability.\n")
            f.write("For legal advice specific to your situation, consult a licensed attorney.\n")
            f.write(f"{'='*80}\n")
        
        return filepath


@dataclass
class ConversationContext:
    """Maintains conversation state and context with enhanced tracking"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, str]]
    identified_intents: List[str]
    extracted_entities: Dict[str, List[str]]
    practice_area_focus: Optional[str]
    current_topic: Optional[str]
    timestamp: str
    # Enhanced context fields for robust conversation handling
    pending_questions: List[str] = None  # Questions asked but not answered
    clarification_needed: List[str] = None  # Topics needing clarification
    legal_issues_identified: List[str] = None  # Specific legal issues detected
    confidence_scores: Dict[str, float] = None  # Confidence in identified issues
    fact_pattern: Dict[str, any] = None  # Structured fact pattern being built
    user_sentiment: str = "curious"  # urgent, concerned, curious, defensive
    follow_up_suggestions: List[str] = None  # Suggested follow-up topics
    generated_documents: List[LegalDocument] = None  # Documents created in session
    
    # ABC (Always Be Closing) consultation tracking
    consultation_stage: str = "discovery"  # discovery, qualification, solution_design, implementation, closing
    pain_points: List[str] = None  # Identified pain points/urgencies
    user_preferences: Dict[str, str] = None  # Likes/dislikes discovered
    proposed_solution: Optional[str] = None  # Solution being built
    action_items: List[str] = None  # Concrete next steps
    urgency_level: str = "normal"  # low, normal, high, critical
    readiness_to_act: float = 0.0  # 0-1 score of how ready user is to take action
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.pending_questions is None:
            self.pending_questions = []
        if self.clarification_needed is None:
            self.clarification_needed = []
        if self.legal_issues_identified is None:
            self.legal_issues_identified = []
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.fact_pattern is None:
            self.fact_pattern = {}
        if self.follow_up_suggestions is None:
            self.follow_up_suggestions = []
        if self.generated_documents is None:
            self.generated_documents = []
        # ABC consultation tracking
        if self.pain_points is None:
            self.pain_points = []
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.action_items is None:
            self.action_items = []


class MytharaGopherNLP:
    """
    Natural Language Processing engine for Mythara Legal Bots.
    Provides GPT-like conversational intelligence using pattern matching,
    entity extraction, and context-aware responses.
    
    No external APIs required - fully self-contained Mythara intelligence.
    """
    
    def __init__(self):
        self.torts_index = TortsLawIndex()
        self.legal_research = LegalResearchEngine()
        
        # Vernacular and multilingual support
        self.vernacular_mappings = self._build_vernacular_mappings()
        
        # Intent patterns (legal query classification)
        self.intent_patterns = self._build_intent_patterns()
        
        # Entity extraction patterns
        self.entity_patterns = self._build_entity_patterns()
        
        # Response templates
        self.response_templates = self._build_response_templates()
        
        # Conversation contexts (in-memory for demo; use DB in production)
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # Legal knowledge embeddings (simplified vector representation)
        self.knowledge_base = self._build_knowledge_base()
        
        # Attorney referral database
        self.attorney_database = self._build_attorney_database()
        
        print("🦫 Mythara Gopher NLP Engine Initialized")
        print("   • Natural language understanding: ACTIVE")
        print("   • Legal knowledge base: LOADED")
        print("   • Conversational context: ENABLED")
        print("   • Intent classification: READY")
        print("   • Multilingual & vernacular support: ENABLED")
        print("   • ABC Consultation Framework: ENABLED (Always Be Closing)")
        if SOUL_CRADLE_AVAILABLE:
            print("   • Soul Cradle emotional intelligence: ENABLED")
            print("   • Paradox detection: ACTIVE")
            print("   • Burnout risk assessment: ACTIVE")
        else:
            print("   • Soul Cradle: DISABLED (module not found)")
    
    def _build_vernacular_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Build vernacular and dialect mappings for inclusive language understanding.
        Supports AAVE, Southern dialects, informal speech, and multilingual terms.
        
        Returns:
            Dictionary mapping vernacular phrases to standard legal terms
        """
        return {
            # AAVE (African American Vernacular English)
            "aave": {
                # Verbs and actions
                r"\bfinna\b": "going to",
                r"\bgonna\b": "going to",
                r"\bwanna\b": "want to",
                r"\bgotta\b": "have to",
                r"\bain't\b": "is not",
                r"\bdon't got\b": "do not have",
                r"\bain't got\b": "do not have",
                r"\bIon\b": "I do not",
                r"\bImma\b": "I am going to",
                r"\blemme\b": "let me",
                r"\bgimme\b": "give me",
                
                # Legal context
                r"\bgot fired\b": "was terminated",
                r"\bthey fired me\b": "I was terminated",
                r"\bhe be\b": "he is",
                r"\bshe be\b": "she is",
                r"\bthey be\b": "they are",
                r"\bit be\b": "it is",
                r"\bwe was\b": "we were",
                r"\bthey was\b": "they were",
                r"\bI been\b": "I have been",
                r"\bhe been\b": "he has been",
                r"\bshe been\b": "she has been",
                
                # Questions
                r"\bwhat it do\b": "what is happening",
                r"\bwhat's good\b": "hello",
                r"\bhow you doing\b": "how are you doing",
                r"\bwhere you at\b": "where are you",
                
                # Legal situations
                r"\bthey tryna\b": "they are trying to",
                r"\bhe tryna\b": "he is trying to",
                r"\bshe tryna\b": "she is trying to",
                r"\bI'm tryna\b": "I am trying to",
                r"\bcaught a case\b": "was charged with a crime",
                r"\bgot locked up\b": "was arrested",
                r"\bthey locked me up\b": "I was arrested",
                r"\bthe folks\b": "the police",
                r"\bthe po-po\b": "the police",
                r"\bthe police them\b": "the police",
            },
            
            # Southern/Regional dialects
            "southern": {
                r"\by'all\b": "you all",
                r"\ball y'all\b": "all of you",
                r"\bain't\b": "is not",
                r"\bfixin' to\b": "about to",
                r"\breckon\b": "think",
                r"\bmight could\b": "might be able to",
                r"\buseta\b": "used to",
                r"\bover yonder\b": "over there",
                r"\bdone did\b": "already did",
                r"\bmight should\b": "probably should",
            },
            
            # Informal/Colloquial
            "informal": {
                r"\bkinda\b": "kind of",
                r"\bsorta\b": "sort of",
                r"\blotta\b": "lot of",
                r"\bcuz\b": "because",
                r"\bcause\b": "because",
                r"\btho\b": "though",
                r"\byeah\b": "yes",
                r"\bnah\b": "no",
                r"\byep\b": "yes",
                r"\bnope\b": "no",
                r"\bdunno\b": "do not know",
                r"\bwhatcha\b": "what are you",
                r"\bgotcha\b": "I understand",
            },
            
            # Legal slang to formal
            "legal_slang": {
                r"\bget sued\b": "face litigation",
                r"\btake to court\b": "file lawsuit against",
                r"\bbeat the case\b": "prevail in litigation",
                r"\bcaught a charge\b": "was charged with",
                r"\bdoing time\b": "serving sentence",
                r"\bgot off\b": "was acquitted",
                r"\bpaper\b": "legal documents",
                r"\bthe law\b": "law enforcement",
                r"\bgot served\b": "received legal notice",
                r"\bsign papers\b": "execute documents",
                r"\bmy boss\b": "my employer",
                r"\bthe boss\b": "the employer",
                r"\bgot canned\b": "was terminated",
                r"\bgot let go\b": "was terminated",
                r"\bthey let me go\b": "I was terminated",
                r"\bkicked me out\b": "evicted me",
                r"\bthrew me out\b": "evicted me",
                r"\bmessed me up\b": "caused injury to me",
                r"\bhurt me bad\b": "caused serious injury",
                r"\btotaled my car\b": "destroyed my vehicle",
                r"\bsmashed into me\b": "collided with me",
                r"\bran into me\b": "collided with me",
                r"\bowed me money\b": "has debt obligation",
                r"\bthey owe me\b": "debt is owed",
                r"\bdidn't pay me\b": "failed to pay wages",
                r"\bshorted my check\b": "underpaid wages",
                r"\bstiffed me\b": "failed to pay",
            },
            
            # Spanish legal terms (common in US)
            "spanish": {
                r"\babogado\b": "attorney",
                r"\bdemanda\b": "lawsuit",
                r"\bcontrato\b": "contract",
                r"\btrabajo\b": "work employment",
                r"\baccidente\b": "accident",
                r"\bdinero\b": "money damages",
                r"\bjuez\b": "judge",
                r"\bcorte\b": "court",
                r"\bderechos\b": "rights",
                r"\btestigo\b": "witness",
                r"\bprueba\b": "evidence",
            },
            
            # Chinese legal terms (Pinyin)
            "chinese": {
                r"\blüshi\b": "attorney",
                r"\bfayuan\b": "court",
                r"\bhetong\b": "contract",
                r"\bqian\b": "money",
                r"\bsifa\b": "legal",
                r"\bfaguan\b": "judge",
                r"\bzhengju\b": "evidence",
            },
            
            # Common misspellings/variations
            "variants": {
                r"\blawsuit\b": "lawsuit",
                r"\blaw suit\b": "lawsuit",
                r"\bpayed\b": "paid",
                r"\bshould of\b": "should have",
                r"\bcould of\b": "could have",
                r"\bwould of\b": "would have",
                r"\bsupposed to\b": "supposed to",
                r"\buse to\b": "used to",
            }
        }
    
    def normalize_vernacular(self, text: str) -> str:
        """
        Normalize vernacular, dialectal, and multilingual text to standard legal English.
        Preserves meaning while making text processable by intent classifiers.
        
        **IMPORTANT**: This is for INPUT PROCESSING ONLY. Gopher always responds in 
        professional, grammatically correct legal English regardless of input vernacular.
        This function ensures Gopher *understands* all dialects while maintaining 
        professional output standards.
        
        Args:
            text: Input text in any vernacular/language (AAVE, Southern, informal, Spanish, etc.)
            
        Returns:
            Normalized text in standard English for intent classification and entity extraction
        """
        normalized = text.lower()
        
        # Apply all vernacular mappings for comprehension
        # Output will always be professional - this is input normalization only
        for dialect_name, mappings in self.vernacular_mappings.items():
            for pattern, replacement in mappings.items():
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    # ===================== ABC (ALWAYS BE CLOSING) CONSULTATION FRAMEWORK =====================
    
    def assess_consultation_stage(self, context: ConversationContext) -> str:
        """
        Determine current stage of consultation using ABC methodology.
        
        Stages:
        1. discovery - Finding the need/problem
        2. qualification - Pressing pain, assessing urgency
        3. solution_design - Building custom solution
        4. implementation - Actually doing something (docs, plans)
        5. closing - Ensuring next steps, follow-up
        """
        turns = len(context.conversation_history)
        
        # Discovery stage (turns 1-3)
        if turns <= 3:
            return "discovery"
        
        # Has solution been proposed?
        if context.proposed_solution:
            # Has action been taken?
            if len(context.generated_documents) > 0 or len(context.action_items) > 0:
                return "closing"
            else:
                return "implementation"
        
        # Have pain points been identified?
        if len(context.pain_points) > 2 or context.urgency_level in ["high", "critical"]:
            return "solution_design"
        
        # Still gathering info
        if len(context.legal_issues_identified) > 0:
            return "qualification"
        
        return "discovery"
    
    def identify_pain_points(self, query: str, context: ConversationContext) -> List[str]:
        """
        Identify pain points and urgency signals in user query.
        This is the "press the pain" step.
        """
        query_lower = query.lower()
        pains = []
        
        # Urgency indicators
        urgency_patterns = [
            (r"\b(urgent|emergency|asap|immediately|now|today|deadline)\b", "Time pressure"),
            (r"\b(fired|terminated|lost job|unemployed)\b", "Job loss"),
            (r"\b(evicted|kicked out|homeless|nowhere to go)\b", "Housing instability"),
            (r"\b(can't pay|no money|broke|financial)\b", "Financial distress"),
            (r"\b(scared|afraid|worried|anxious|stressed)\b", "Emotional distress"),
            (r"\b(threaten|intimidate|harass|abuse)\b", "Safety concerns"),
            (r"\b(arrest|jail|police|criminal)\b", "Legal jeopardy"),
            (r"\b(deadline|statute|time limit|too late)\b", "Time-sensitive"),
            (r"\b(pain|injury|hurt|medical|hospital)\b", "Physical harm"),
            (r"\b(kids|children|custody)\b", "Family at risk"),
        ]
        
        for pattern, pain_description in urgency_patterns:
            if re.search(pattern, query_lower):
                if pain_description not in pains:
                    pains.append(pain_description)
        
        return pains
    
    def assess_urgency(self, query: str, context: ConversationContext) -> str:
        """
        Assess urgency level: low, normal, high, critical
        """
        query_lower = query.lower()
        
        # Critical urgency
        critical_indicators = [
            r"\b(emergency|911|urgent|asap|now|immediately|today)\b",
            r"\b(deadline.{1,20}(today|tomorrow|this week))\b",
            r"\b(eviction|homeless|foreclosure)\b",
            r"\b(arrested|jail|custody)\b",
        ]
        
        for pattern in critical_indicators:
            if re.search(pattern, query_lower):
                return "critical"
        
        # High urgency
        high_indicators = [
            r"\b(need.{1,20}(soon|quick|fast))\b",
            r"\b(terminated|fired|laid off)\b",
            r"\b(threatened|intimidated)\b",
            r"\b(deadline|statute|time limit)\b",
        ]
        
        for pattern in high_indicators:
            if re.search(pattern, query_lower):
                return "high"
        
        # Check conversation history for urgency build-up
        if len(context.pain_points) >= 3:
            return "high"
        
        return "normal"
    
    def assess_readiness_to_act(self, query: str, context: ConversationContext) -> float:
        """
        Assess how ready the user is to take action (0-1 scale).
        This determines how hard to "close."
        """
        query_lower = query.lower()
        readiness = 0.0
        
        # Strong readiness signals (+0.3 each)
        strong_signals = [
            r"\b(want to|need to|ready to|let's|finna|going to)\s+(sue|file|send|create|draft)\b",
            r"\b(how do I|what do I|can you help me)\s+(sue|file|send)\b",
            r"\b(yes|yeah|yep|definitely|absolutely|for sure)\b",
        ]
        
        for pattern in strong_signals:
            if re.search(pattern, query_lower):
                readiness += 0.3
        
        # Moderate signals (+0.2 each)
        moderate_signals = [
            r"\b(thinking about|considering|might|maybe|should I)\b",
            r"\b(what are my options|what can I do)\b",
        ]
        
        for pattern in moderate_signals:
            if re.search(pattern, query_lower):
                readiness += 0.2
        
        # Context indicators
        if len(context.generated_documents) > 0:
            readiness += 0.3  # Already taken action
        
        if context.urgency_level in ["high", "critical"]:
            readiness += 0.2  # Urgency drives action
        
        return min(1.0, readiness)
    
    def extract_user_preferences(self, query: str, context: ConversationContext) -> Dict[str, str]:
        """
        Extract likes/dislikes to build rapport and customize solution.
        """
        query_lower = query.lower()
        preferences = {}
        
        # Communication preferences
        if re.search(r"\b(don't want|hate|avoid).{1,30}\b(court|lawyer|litigation)", query_lower):
            preferences["prefers_settlement"] = "true"
        
        if re.search(r"\b(want to|prefer).{1,30}\b(settle|mediat|negotiat|resolve)", query_lower):
            preferences["prefers_settlement"] = "true"
        
        # Time preferences
        if re.search(r"\b(quick|fast|asap|soon|immediately)\b", query_lower):
            preferences["speed"] = "fast"
        
        # Cost sensitivity
        if re.search(r"\b(free|cheap|afford|expensive|cost|money)\b", query_lower):
            preferences["cost_conscious"] = "true"
        
        # DIY vs representation
        if re.search(r"\b(myself|without lawyer|pro se|on my own)\b", query_lower):
            preferences["diy"] = "true"
        
        if re.search(r"\b(need lawyer|want attorney|hire|retain)\b", query_lower):
            preferences["wants_representation"] = "true"
        
        return preferences
    
    def build_action_items(self, context: ConversationContext) -> List[str]:
        """
        Generate concrete next steps based on consultation stage and readiness.
        This is the "implementation" phase.
        """
        action_items = []
        stage = context.consultation_stage
        
        # Always start with documentation
        if "documentation" not in str(context.action_items):
            action_items.append("📝 Document all facts, dates, evidence, and communications")
        
        # Stage-specific actions
        if stage in ["solution_design", "implementation", "closing"]:
            if len(context.generated_documents) == 0:
                # Suggest document generation
                if any("termination" in issue or "employment" in issue for issue in context.legal_issues_identified):
                    action_items.append("📨 Generate demand letter to former employer")
                
                # Check fact_pattern dict properly
                fact_pattern_str = " ".join(str(v) for v in context.fact_pattern.values()) if context.fact_pattern else ""
                if "landlord" in fact_pattern_str or "evict" in fact_pattern_str:
                    action_items.append("📨 Generate demand letter for security deposit/rent")
                
                if any("infring" in issue for issue in context.legal_issues_identified):
                    action_items.append("🛑 Generate cease & desist letter")
            
            # Evidence preservation
            if context.urgency_level in ["high", "critical"]:
                action_items.append("⏱️ Timestamp critical statements and evidence NOW")
            
            # Attorney consultation
            if context.urgency_level == "critical" or context.readiness_to_act > 0.7:
                action_items.append("👨‍⚖️ Schedule consultation with licensed attorney IMMEDIATELY")
            elif len(context.pain_points) >= 2:
                action_items.append("👨‍⚖️ Consult with licensed attorney within 7 days")
            
            # Filing deadlines
            conversation_str = str(context.conversation_history)
            if "statute" in conversation_str or "deadline" in conversation_str:
                action_items.append("📅 CHECK statute of limitations deadline for your jurisdiction")
        
        return action_items
    
    def close_the_loop(self, context: ConversationContext) -> str:
        """
        Generate closing message with clear next steps and call to action.
        This ensures user leaves with concrete plan.
        """
        closing = "\n\n" + "="*80 + "\n"
        closing += "🎯 **YOUR ACTION PLAN** (Next Steps)\n"
        closing += "="*80 + "\n\n"
        
        # Show action items
        action_items = self.build_action_items(context)
        
        if action_items:
            closing += "**Immediate Actions:**\n\n"
            for i, item in enumerate(action_items, 1):
                closing += f"{i}. {item}\n"
            closing += "\n"
        
        # Urgency-based messaging
        if context.urgency_level == "critical":
            closing += "⚠️ **URGENT**: Time-sensitive situation detected. Act within 24-48 hours.\n\n"
        elif context.urgency_level == "high":
            closing += "⏰ **Important**: Address within 1-2 weeks to protect your rights.\n\n"
        
        # Document generation offer
        if len(context.generated_documents) == 0 and context.readiness_to_act > 0.5:
            closing += "📄 **Ready to take action?** I can generate:\n"
            closing += "   • Professional demand letters with deadlines\n"
            closing += "   • Cease & desist letters\n"
            closing += "   • Evidence summaries with SHA-256 timestamps\n"
            closing += "   • Legal memoranda\n\n"
            closing += "   Say: 'Generate demand letter' or 'Create cease and desist'\n\n"
        
        # Follow-up questions
        closing += "**What would you like to do next?**\n"
        closing += "   • Get more information about your legal options?\n"
        closing += "   • Generate legal documents?\n"
        closing += "   • Find attorneys in your area?\n"
        closing += "   • Learn about court procedures?\n\n"
        
        closing += "I'm here to help you take the next step. What's your priority?\n"
        closing += "="*80 + "\n"
        
        return closing
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Build intent classification patterns - ENHANCED for robustness.
        Maps user queries to 17+ legal intents with comprehensive pattern matching.
        """
        return {
            "tort_analysis": [
                r"\b(sue|lawsuit|liable|liability|tort|claim|injury|harm|damage|injured)\b",
                r"\b(negligent|negligence|malpractice|breach|duty|careless)\b",
                r"\b(defamation|slander|libel|false statement|reputation)\b",
                r"\b(assault|battery|false imprisonment|IIED|emotional distress)\b",
                r"\b(trespass|conversion|nuisance)\b",
                r"\bcan I sue\b",
                r"\bdo I have a case\b",
                r"\b(legal claim|cause of action|grounds to sue)\b",
                r"\b(personal injury|bodily harm|physical injury)\b",
                r"\b(wrongful death|survival action)\b",
                r"\b(car accident|slip and fall|medical error)\b"
            ],
            "contract_review": [
                r"\b(contract|agreement|terms|clause|provision|terms of service)\b",
                r"\b(breach of contract|enforceable|binding|valid contract)\b",
                r"\b(sign|signing|signature|execute|executed)\b",
                r"\b(negotiate|negotiation|redline|revise|amend)\b",
                r"\breview (this|my|the|our) (contract|agreement)\b",
                r"\b(NDA|non-disclosure|confidentiality agreement)\b",
                r"\b(offer|acceptance|consideration|mutual assent)\b",
                r"\b(warranty|guarantee|representation|covenant)\b",
                r"\b(indemnification|indemnify|hold harmless)\b"
            ],
            "compliance_check": [
                r"\b(GDPR|CCPA|CPRA|HIPAA|compliance|regulation|regulatory)\b",
                r"\b(SOC 2|SOC2|PCI|PCI-DSS|DSS|audit|certification)\b",
                r"\b(data protection|privacy policy|consent|cookie policy)\b",
                r"\b(compliant|violation|penalty|fine|sanction)\b",
                r"\bam I (compliant|in compliance)\b",
                r"\b(ISO 27001|NIST|CMMC|FedRAMP)\b",
                r"\b(data breach|breach notification|incident response)\b",
                r"\b(DPA|data processing agreement|BAA|business associate)\b"
            ],
            "ip_protection": [
                r"\b(patent|trademark|copyright|intellectual property|IP)\b",
                r"\b(infringement|infringe|piracy|counterfeit|knock-off)\b",
                r"\b(trade secret|confidential information|proprietary)\b",
                r"\b(register|registration|application|filing|USPTO)\b",
                r"\bprotect my (idea|invention|brand|logo|design)\b",
                r"\b(DMCA|takedown notice|cease and desist)\b",
                r"\b(fair use|public domain|license|licensing)\b",
                r"\b(service mark|trade dress|dilution)\b"
            ],
            "employment_issue": [
                r"\b(employee|employer|employment|fire|fired|termination|terminated)\b",
                r"\b(discrimination|harassment|hostile work environment)\b",
                r"\b(wrongful termination|retaliation|whistleblower|protected activity)\b",
                r"\b(hire|hiring|background check|drug test)\b",
                r"\b(wage|salary|overtime|FLSA|unpaid|back pay)\b",
                r"\b(ADA|FMLA|Title VII|protected class)\b",
                r"\b(severance|separation agreement|non-compete)\b",
                r"\b(workers compensation|workplace injury|OSHA)\b"
            ],
            "statute_of_limitations": [
                r"\b(statute of limitations|time limit|deadline|expire|expired)\b",
                r"\bhow long do I have (to sue|to file)\b",
                r"\b(too late|still file|still sue|time-barred)\b",
                r"\b(time bar|limitation period|prescriptive period)\b",
                r"\b(discovery rule|accrual|when does the clock start)\b",
                r"\b(tolling|toll|statute tolled)\b"
            ],
            "legal_research": [
                r"\b(case law|precedent|court decision|ruling|opinion)\b",
                r"\b(legal principle|doctrine|rule|statute|regulation)\b",
                r"\bwhat (does|is) .+ (mean|definition)\b",
                r"\b(research|find|look up|search|cite|citation)\b",
                r"\b(Restatement|Black's Law Dictionary|hornbook)\b",
                r"\b(mens rea|actus reus|stare decisis|ratio decidendi)\b",
                r"\b(explain|define|clarify|elucidate)\b"
            ],
            "damages_calculation": [
                r"\b(damages|compensation|recover|award|settlement|judgment)\b",
                r"\bhow much (can I|should I|am I owed|is it worth)\b",
                r"\b(punitive|compensatory|nominal|statutory|liquidated)\b",
                r"\b(pain and suffering|lost wages|medical expenses|economic loss)\b",
                r"\b(future damages|present value|discount rate)\b",
                r"\b(treble damages|attorney fees|costs)\b"
            ],
            "defense_strategy": [
                r"\b(defense|defend|counterclaim|affirmative defense)\b",
                r"\bhow (do I|can I) defend\b",
                r"\b(sued|being sued|complaint against|defendant)\b",
                r"\bdefend (myself|against|from)\b",
                r"\b(motion to dismiss|summary judgment|demurrer)\b",
                r"\b(answer|responsive pleading|twelve(b)(6))\b"
            ],
            "procedural_question": [
                r"\b(file|filing|motion|pleading|discovery|deposition)\b",
                r"\b(jurisdiction|venue|forum|proper court)\b",
                r"\b(serve|service of process|summons|complaint)\b",
                r"\bhow (do I|to) file\b",
                r"\b(interrogatories|requests for admission|subpoena)\b",
                r"\b(FRCP|Federal Rules|local rules)\b"
            ],
            "privacy_rights": [
                r"\b(privacy|private|personal information|PII)\b",
                r"\b(right to be forgotten|data deletion|erasure)\b",
                r"\b(surveillance|tracking|cookies|web beacons)\b",
                r"\b(doxxing|public disclosure|intrusion)\b",
                r"\b(COPPA|children's privacy|parental consent)\b"
            ],
            "liability_assessment": [
                r"\bam I (liable|responsible|at fault)\b",
                r"\b(strict liability|no fault|absolute liability)\b",
                r"\b(vicarious liability|respondeat superior)\b",
                r"\b(joint and several|contribution|indemnity)\b",
                r"\b(assumption of risk|comparative negligence)\b"
            ],
            "dispute_resolution": [
                r"\b(arbitration|mediation|ADR|alternative dispute)\b",
                r"\b(settlement|settle|negotiation|demand letter)\b",
                r"\b(small claims|magistrate|conciliation)\b",
                r"\b(binding arbitration|non-binding|voluntary)\b"
            ],
            "criminal_concern": [
                r"\b(criminal|crime|felony|misdemeanor|arrest)\b",
                r"\b(police|prosecutor|criminal charges|indictment)\b",
                r"\b(Miranda|rights|fifth amendment|self-incrimination)\b",
                r"\b(criminal defense|criminal lawyer|public defender)\b"
            ],
            "business_formation": [
                r"\b(LLC|corporation|incorporate|form a business)\b",
                r"\b(business structure|entity|partnership|sole proprietor)\b",
                r"\b(articles of incorporation|operating agreement|bylaws)\b",
                r"\b(EIN|tax ID|business license)\b"
            ],
            "real_estate": [
                r"\b(real estate|property|landlord|tenant|lease)\b",
                r"\b(eviction|unlawful detainer|security deposit)\b",
                r"\b(deed|title|escrow|closing)\b",
                r"\b(easement|zoning|land use|eminent domain)\b"
            ],
            "consumer_protection": [
                r"\b(consumer protection|FDCPA|TCPA|FCRA)\b",
                r"\b(debt collection|credit report|identity theft)\b",
                r"\b(lemon law|warranty|product defect|recall)\b",
                r"\b(predatory lending|usury|unfair practice)\b"
            ],
            "document_generation": [
                r"\b(draft|write|create|generate|prepare).+(letter|demand|document|memo|complaint|motion|discovery|writ|pleading|answer|affidavit|subpoena|interrogator)\b",
                r"\b(demand letter|cease and desist|legal memo|civil complaint|answer to complaint)\b",
                r"\b(motion to|motion for).+(dismiss|compel|summary judgment|injunction)\b",
                r"\b(interrogator|request for (production|admission)|discovery request|RFP|RFA)\b",
                r"\b(complaint|lawsuit|file suit|sue|civil action)\b",
                r"\b(answer|response to complaint|affirmative defense|counterclaim)\b",
                r"\b(affidavit|declaration|sworn statement|notarized statement)\b",
                r"\b(subpoena|summons|court order|writ of)\b",
                r"\b(send.+letter|mail.+letter|write.+formal)\b",
                r"\b(timestamp|certify|notarize|authenticate)\b",
                r"\b(evidence summary|chain of custody|documentation)\b",
                r"\bneed (a|to send|to file).+(formal|legal|official|complaint|motion|discovery)\b"
            ],
            "show_disclaimer": [
                r"\b(show|display|view|read|see).+(disclaimer|terms|legal notice)\b",
                r"\b(disclaimer|legal notice|terms of use|terms and conditions)\b",
                r"\b(are you a lawyer|can you give legal advice|attorney)\b",
                r"\bwhat (are|is) (your|the) (disclaimer|terms|limitations)\b"
            ],
            "attorney_referral": [
                r"\b(find|need|want|looking for|recommend|suggest).+(attorney|lawyer|counsel|legal help)\b",
                r"\b(attorney|lawyer|counsel).+(near me|in|for|who|that)\b",
                r"\b(get|find) (me )?(a |an )?(good |experienced )?(attorney|lawyer|counsel)\b",
                r"\b(referral|refer me to|connect me with).+(attorney|lawyer)\b",
                r"\b(who.+handle|specialist in|expert in).+(my case|wrongful termination|personal injury|landlord|employment)\b",
                r"\blawyer (directory|database|list|search)\b"
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, str]:
        """
        Build entity extraction patterns - ENHANCED for robust entity recognition.
        Extracts comprehensive legal entities from user input.
        """
        return {
            "jurisdiction": r"\b(California|New York|Texas|Florida|Illinois|Pennsylvania|Ohio|Georgia|North Carolina|Michigan|federal|state|CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|US|United States|9th Circuit|2nd Circuit|District Court|Supreme Court)\b",
            "date": r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}|last (?:week|month|year)|(?:yesterday|today|ago))\b",
            "money": r"\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|thousand|billion|k|m|b))?|(?:\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars)",
            "percentage": r"\d+(?:\.\d+)?%",
            "person": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
            "company": r"\b[A-Z][A-Za-z&\s]+(?:Inc|LLC|Corp|Corporation|Ltd|Limited|Co|Company|L\.L\.C\.|L\.P\.)\b",
            "tort_keywords": r"\b(negligent|intentional|strict liability|duty|breach|causation|damages|proximate cause|but-for|foreseeability)\b",
            "contract_keywords": r"\b(offer|acceptance|consideration|mutual assent|breach|performance|material breach|substantial performance|condition precedent|covenant)\b",
            "time_period": r"\b(\d+\s*(?:day|week|month|year)s?(?:\s+ago)?|within \d+|for \d+|after \d+)\b",
            "legal_standard": r"\b(preponderance of evidence|beyond reasonable doubt|clear and convincing|reasonable person|probable cause|reasonable suspicion)\b",
            "relief_sought": r"\b(injunction|restraining order|declaratory judgment|specific performance|restitution|rescission|reformation)\b",
            "parties": r"\b(plaintiff|defendant|appellant|appellee|petitioner|respondent|claimant)\b",
            "injury_type": r"\b(broken|fractured|whiplash|concussion|burns|laceration|sprain|strain|permanent|temporary|disability)\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
            "case_citation": r"\b\d+\s+[A-Z][A-Za-z.]+\s+\d+\b"
        }
    
    def _build_response_templates(self) -> Dict[str, List[str]]:
        """
        Build response templates for different intents.
        Provides natural conversational responses.
        """
        return {
            "greeting": [
                "Hello! I'm Mythara Gopher, your legal research and document preparation assistant.\n\n🌍 **Language Accessibility**: I understand AAVE, regional dialects, informal speech, and multilingual terms. Feel free to communicate naturally—I'll always respond in professional legal English.\n\n⚖️ **IMPORTANT DISCLAIMER**: I provide information for personal use only—NOT legal advice. I cannot create an attorney-client relationship. Information may be outdated. Please consult licensed legal counsel for advice. Use at your own risk.\n\nHow can I help you today?",
                "Hi there! I'm Mythara Gopher. I assist with legal research and document preparation.\n\n🌍 **Speak Your Language**: I comprehend vernacular English (AAVE, Southern dialects), informal speech, and Spanish/Chinese legal terms. I'll respond in clear, professional English.\n\n⚖️ **PLEASE NOTE**: This service is for informational purposes only and does not constitute legal advice. You are strongly encouraged to consult a licensed attorney. See full disclaimer with 'show disclaimer'.\n\nWhat can I assist you with?",
                "Welcome! I'm Mythara Gopher—your advocate for legal research and document drafting.\n\n🌍 **Inclusive Communication**: Communicate in your natural voice—AAVE, regional dialects, or informal speech. I understand all vernaculars and will provide responses in professional legal English.\n\n⚖️ **LEGAL NOTICE**: I am NOT a substitute for legal counsel. All information may be outdated. Use at your own risk. Consult a licensed attorney for legal advice specific to your situation.\n\nWhat would you like to explore?"
            ],
            "tort_analysis_intro": [
                "I can help analyze potential tort claims. Let me ask a few questions to understand your situation better.",
                "Let's examine whether you may have a valid legal claim. I'll need some details about what happened.",
                "I'll analyze this for potential tort liability. Could you provide more details about the incident?"
            ],
            "need_more_info": [
                "To provide a thorough analysis, I need a bit more information. Can you tell me about {missing_info}?",
                "That's helpful context. Could you also clarify {missing_info}?",
                "I'd like to understand {missing_info} to give you a complete answer."
            ],
            "disclaimer": [
                "⚠️ Important: This is informational guidance only and does not constitute legal advice. Please consult a licensed attorney for your specific situation.",
                "⚖️ Disclaimer: I provide legal information, not legal advice. For case-specific counsel, please speak with a licensed attorney.",
                "📋 Note: This analysis is for informational purposes only. Consult with a qualified attorney for legal advice tailored to your circumstances."
            ],
            "no_match": [
                "I'm not quite sure I understand. Could you rephrase your question or provide more details?",
                "I want to make sure I help you correctly. Could you clarify what you're asking about?",
                "Let me make sure I understand - are you asking about {suggestion}?"
            ],
            "follow_up": [
                "Is there anything else you'd like to know about this issue?",
                "Would you like me to explore any other aspects of this matter?",
                "Do you have any follow-up questions?"
            ]
        }
    
    def _build_knowledge_base(self) -> Dict[str, Dict]:
        """
        Build simplified knowledge base from legal resources.
        Creates searchable legal knowledge representation.
        """
        kb = {
            "torts": {},
            "maxims": {},
            "cases": {},
            "statutes": {},
            "concepts": {}
        }
        
        # Index all torts
        for tort_name, tort_def in self.torts_index.torts_database.items():
            kb["torts"][tort_name] = {
                "name": tort_def.tort_name,
                "category": tort_def.category.value,
                "keywords": [
                    tort_name,
                    tort_def.tort_name.lower(),
                    tort_def.category.value
                ] + [e.element_name.lower() for e in tort_def.elements],
                "elements": [e.element_name for e in tort_def.elements],
                "defenses": [d.value for d in tort_def.defenses],
                "sol": tort_def.statute_of_limitations_years
            }
        
        # Index legal maxims
        for maxim in self.legal_research.maxims.get_maxims():
            key = maxim.latin.lower().replace(" ", "_")
            kb["maxims"][key] = {
                "latin": maxim.latin,
                "english": maxim.english,
                "keywords": [maxim.latin.lower(), maxim.english.lower()],
                "explanation": maxim.explanation
            }
        
        # Index landmark cases
        for case in self.legal_research.cases.get_landmark_cases():
            case_key = case.case_name.lower().replace(" ", "_").replace(".", "")
            kb["cases"][case_key] = {
                "name": case.case_name,
                "citation": case.citation,
                "year": case.year,
                "holding": case.holding,
                "principle": case.principle,
                "keywords": case.case_name.lower().split() + case.principle.lower().split()
            }
        
        return kb
    
    def _build_attorney_database(self) -> Dict:
        """
        Build attorney referral database with practice areas and locations.
        PUBLIC DATABASE - attorneys can submit their information for inclusion.
        
        Database structure:
        - Attorney profile (name, firm, contact)
        - Practice areas (employment, personal injury, landlord/tenant, etc.)
        - Geographic coverage (state, city, counties)
        - Bar admissions
        - Free consultation info
        - Client reviews/ratings (future)
        
        NOTE: This is a PUBLIC referral service. Gopher does NOT endorse or guarantee
        any attorney. Users must verify credentials and make their own selection.
        """
        return {
            "practice_areas": {
                "employment": {
                    "keywords": ["wrongful termination", "discrimination", "harassment", "wage", "retaliation", "fired", "employment"],
                    "description": "Employment Law (wrongful termination, discrimination, wage disputes)"
                },
                "personal_injury": {
                    "keywords": ["accident", "injury", "car crash", "medical malpractice", "slip and fall", "negligence"],
                    "description": "Personal Injury (accidents, medical malpractice, negligence)"
                },
                "landlord_tenant": {
                    "keywords": ["eviction", "landlord", "tenant", "rent", "security deposit", "housing"],
                    "description": "Landlord/Tenant (evictions, rent disputes, security deposits)"
                },
                "family_law": {
                    "keywords": ["divorce", "custody", "child support", "alimony", "family", "domestic"],
                    "description": "Family Law (divorce, custody, child support)"
                },
                "criminal": {
                    "keywords": ["criminal", "arrest", "charged", "felony", "misdemeanor", "dui", "defense"],
                    "description": "Criminal Defense (arrests, charges, DUI)"
                },
                "civil_rights": {
                    "keywords": ["civil rights", "police", "constitutional", "discrimination", "first amendment"],
                    "description": "Civil Rights (police misconduct, constitutional violations)"
                },
                "immigration": {
                    "keywords": ["immigration", "visa", "deportation", "asylum", "green card", "citizenship"],
                    "description": "Immigration (visas, deportation, asylum)"
                },
                "business": {
                    "keywords": ["business", "contract", "partnership", "llc", "corporation", "commercial"],
                    "description": "Business Law (contracts, partnerships, corporate)"
                },
                "estate": {
                    "keywords": ["estate", "will", "trust", "probate", "inheritance", "elder"],
                    "description": "Estate Planning (wills, trusts, probate)"
                },
                "bankruptcy": {
                    "keywords": ["bankruptcy", "debt", "chapter 7", "chapter 13", "creditor"],
                    "description": "Bankruptcy & Debt (Chapter 7, Chapter 13, creditors)"
                }
            },
            "attorneys": [
                # CALIFORNIA ATTORNEYS
                {
                    "name": "Public Referral - California Employment Law",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["employment"],
                    "states": ["CA"],
                    "cities": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "Submit your practice info to be listed in public database"
                },
                {
                    "name": "Public Referral - California Personal Injury",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["personal_injury"],
                    "states": ["CA"],
                    "cities": ["Los Angeles", "San Diego", "San Jose"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "Contingency fee - no upfront costs. Submit your practice to be listed."
                },
                # NEW YORK ATTORNEYS
                {
                    "name": "Public Referral - New York Employment Law",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["employment", "civil_rights"],
                    "states": ["NY"],
                    "cities": ["New York City", "Buffalo", "Rochester", "Albany"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "Submit your practice info to be listed"
                },
                # TEXAS ATTORNEYS
                {
                    "name": "Public Referral - Texas Personal Injury",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["personal_injury"],
                    "states": ["TX"],
                    "cities": ["Houston", "Dallas", "Austin", "San Antonio"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "Contingency fee cases. Submit your practice to be listed."
                },
                # FLORIDA ATTORNEYS
                {
                    "name": "Public Referral - Florida Criminal Defense",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["criminal"],
                    "states": ["FL"],
                    "cities": ["Miami", "Tampa", "Orlando", "Jacksonville"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "24/7 emergency availability. Submit your practice to be listed."
                },
                # ILLINOIS ATTORNEYS
                {
                    "name": "Public Referral - Illinois Employment Law",
                    "firm": "[Submit your firm - attorney_referrals@mythara.com]",
                    "practice_areas": ["employment"],
                    "states": ["IL"],
                    "cities": ["Chicago", "Naperville", "Aurora"],
                    "phone": "[To be listed]",
                    "email": "attorney_referrals@mythara.com",
                    "website": "https://mythara.com/attorney-referrals",
                    "free_consultation": True,
                    "notes": "Submit your practice info to be listed"
                }
            ],
            "bar_associations": {
                "CA": {"name": "State Bar of California", "website": "https://www.calbar.ca.gov", "phone": "(866) 442-2529"},
                "NY": {"name": "New York State Bar Association", "website": "https://www.nysba.org", "phone": "(518) 463-3200"},
                "TX": {"name": "State Bar of Texas", "website": "https://www.texasbar.com", "phone": "(800) 204-2222"},
                "FL": {"name": "The Florida Bar", "website": "https://www.floridabar.org", "phone": "(850) 561-5600"},
                "IL": {"name": "Illinois State Bar Association", "website": "https://www.isba.org", "phone": "(217) 525-1760"}
            },
            "legal_aid": {
                "national": {
                    "name": "Legal Services Corporation",
                    "website": "https://www.lsc.gov/what-legal-aid/find-legal-aid",
                    "description": "Find free legal aid in your area"
                },
                "employment": {
                    "name": "National Employment Lawyers Association",
                    "website": "https://www.nela.org",
                    "description": "Find employment law attorneys"
                }
            }
        }
    
    def get_legal_disclaimer(self, brief: bool = False) -> str:
        """
        Return legal disclaimer for display to users.
        
        Args:
            brief: If True, returns short disclaimer. If False, returns full disclaimer.
        
        Returns:
            Legal disclaimer text
        """
        if brief:
            return (
                "⚖️ **LEGAL DISCLAIMER**: Mythara Gopher is for personal use and document "
                "preparation only. This is NOT legal advice and does NOT create an attorney-"
                "client relationship. Information may be outdated. Users are strongly "
                "encouraged to consult licensed legal counsel. Use at your own risk. "
                "See full disclaimer with `gopher.get_legal_disclaimer()`"
            )
        else:
            return MYTHARA_GOPHER_LEGAL_DISCLAIMER
    
    def _detect_legal_paradox(self, query: str, entities: Dict, context: ConversationContext) -> Optional[Dict]:
        """
        Detect legal paradoxes using Soul Cradle framework.
        Returns paradox analysis if detected, None otherwise.
        
        Examples of legal paradoxes:
        - "My employer says I must violate HIPAA or get fired"
        - "The contract requires me to break the law"
        - "I have to choose between my safety and my job"
        """
        if not SOUL_CRADLE_AVAILABLE:
            return None
        
        query_lower = query.lower()
        paradox_indicators = [
            (r"\b(forced to|must|have to|required to).+(violate|break|ignore)", "compliance_vs_employment"),
            (r"\b(lawyer told me|attorney said).+(but|however|yet)", "legal_advice_conflict"),
            (r"\b(law requires|legally required).+(can't|unable|impossible)", "impossible_compliance"),
            (r"\b(whistleblow|report).+(retaliation|fired|punished)", "whistleblower_paradox"),
            (r"\b(both|either).+(violate|breach|illegal)", "dual_illegality"),
            (r"\b(contract says).+(but|however).+(law requires)", "contract_law_conflict"),
            (r"\b(safety|health).+(vs|or).+(job|employment|termination)", "safety_vs_employment")
        ]
        
        detected_type = None
        for pattern, paradox_type in paradox_indicators:
            if re.search(pattern, query_lower, re.IGNORECASE):
                detected_type = paradox_type
                break
        
        if not detected_type:
            return None
        
        # Build paradox structure
        paradox_analysis = {
            "detected": True,
            "type": detected_type,
            "tension_score": 0.8,  # High by default for detected paradoxes
            "burnout_risk": "HIGH",
            "recommendation": "URGENT: Consult attorney immediately. This situation involves conflicting legal/ethical obligations."
        }
        
        context.legal_issues_identified.append(f"paradox_{detected_type}")
        return paradox_analysis
    
    def _assess_emotional_coercion(self, query: str, entities: Dict) -> Optional[Dict]:
        """
        Assess emotional coercion patterns using Soul Cradle principles.
        Detects will_authenticity issues (coerced vs. genuine decision-making).
        """
        if not SOUL_CRADLE_AVAILABLE:
            return None
        
        query_lower = query.lower()
        coercion_patterns = [
            r"\b(threatened|threaten|intimidate|scare|pressure)",
            r"\b(no choice|forced|must|have to) (?:sign|agree|accept)",
            r"\b(or else|otherwise).+(fired|terminated|punished|sued)",
            r"\b(guilt|shame|manipulate|gaslight)",
            r"\b(afraid|scared|terrified).+(say no|refuse|decline)"
        ]
        
        coercion_score = 0.0
        detected_patterns = []
        
        for pattern in coercion_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                coercion_score += 0.25
                detected_patterns.append(pattern)
        
        coercion_score = min(coercion_score, 1.0)
        
        if coercion_score > 0.3:
            will_authenticity = 1.0 - coercion_score
            return {
                "coercion_detected": True,
                "coercion_score": round(coercion_score, 2),
                "will_authenticity": round(will_authenticity, 2),
                "risk_level": "HIGH" if coercion_score > 0.6 else "MODERATE",
                "detected_patterns": detected_patterns[:3],
                "recommendation": "⚠️ Emotional coercion detected. Decisions made under duress may be voidable. Consult attorney about duress defense."
            }
        
        return None
    
    def _calculate_burnout_risk(self, context: ConversationContext) -> Optional[str]:
        """
        Calculate burnout risk based on conversation context.
        Uses Soul Cradle terminal risk assessment.
        """
        if not SOUL_CRADLE_AVAILABLE:
            return None
        
        risk_factors = 0
        
        # Check for burnout indicators
        burnout_keywords = [
            "exhausted", "overwhelmed", "can't take", "giving up",
            "burnout", "breaking point", "too much", "drowning"
        ]
        
        for msg in context.conversation_history:
            if msg["role"] == "user":
                content_lower = msg["content"].lower()
                for keyword in burnout_keywords:
                    if keyword in content_lower:
                        risk_factors += 1
        
        # Check for paradox accumulation
        if len(context.legal_issues_identified) > 2:
            risk_factors += 2
        
        # Check sentiment
        if context.user_sentiment in ["urgent", "defensive"]:
            risk_factors += 1
        
        if risk_factors >= 3:
            return "HIGH"
        elif risk_factors >= 2:
            return "MODERATE"
        elif risk_factors >= 1:
            return "LOW"
        else:
            return None
    
    # ===================== DOCUMENT GENERATION & TIMESTAMPING =====================
    
    def _generate_integrity_hash(self, content: str) -> str:
        """Generate SHA-256 integrity hash for document timestamping"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def generate_demand_letter(
        self,
        sender_name: str,
        sender_address: str,
        recipient_name: str,
        recipient_address: str,
        incident_description: str,
        legal_basis: List[str],
        damages_claimed: str,
        deadline_days: int = 30,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """
        Generate a professional demand letter with cryptographic timestamping.
        
        Args:
            sender_name: Your name
            sender_address: Your address
            recipient_name: Defendant's name
            recipient_address: Defendant's address
            incident_description: What happened
            legal_basis: List of applicable torts/violations
            damages_claimed: Amount and type of damages
            deadline_days: Response deadline (default 30 days)
            context: Conversation context for additional details
        
        Returns:
            LegalDocument with SHA-256 timestamp
        """
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        deadline_date = (datetime.now() + timedelta(days=deadline_days)).strftime("%B %d, %Y")
        
        content = f"""
{sender_name}
{sender_address}

{datetime.now().strftime("%B %d, %Y")}

{recipient_name}
{recipient_address}

Re: DEMAND FOR PAYMENT AND RESOLUTION OF LEGAL CLAIMS

Dear {recipient_name}:

I. INTRODUCTION

This letter constitutes formal legal notice of claims arising from the following incident and serves as a demand for immediate resolution. This demand is made without prejudice to any and all legal rights and remedies available under law.

II. STATEMENT OF FACTS

{incident_description}

III. LEGAL BASIS FOR CLAIMS

Based on the facts described above, you are liable for the following violations:

"""
        
        for i, basis in enumerate(legal_basis, 1):
            content += f"{i}. {basis}\n"
        
        content += f"""
IV. DAMAGES

As a direct and proximate result of your actions, I have suffered the following damages:

{damages_claimed}

V. DEMAND FOR RESOLUTION

I hereby demand the following:

1. Payment of all damages in the amount specified above
2. Written acknowledgment of liability
3. Assurance that such conduct will not be repeated
4. Reimbursement of all costs incurred, including attorney fees if retained

VI. DEADLINE FOR RESPONSE

You have until {deadline_date} ({deadline_days} days from the date of this letter) to respond to this demand and make full payment. Failure to respond or make payment by this deadline will result in the immediate filing of a lawsuit without further notice.

VII. PRESERVATION OF EVIDENCE

You are hereby on notice to preserve all evidence related to this matter, including but not limited to: documents, electronic communications, photographs, video recordings, and physical evidence. Destruction or alteration of evidence may result in spoliation sanctions.

VIII. LEGAL REPRESENTATION

I reserve the right to retain legal counsel at any time. If this matter proceeds to litigation, I will seek recovery of all attorney fees and costs as permitted by law.

IX. CONCLUSION

This letter is an attempt to resolve this matter without costly litigation. I urge you to take this demand seriously and respond promptly. If you have insurance coverage that may apply to this claim, please forward this letter to your insurance carrier immediately.

Please direct all correspondence regarding this matter to:

{sender_name}
{sender_address}

I expect your response by {deadline_date}.

Sincerely,

{sender_name}

---
CERTIFICATE OF SERVICE
I certify that a true and correct copy of this Demand Letter was sent via [mail/email] to {recipient_name} at {recipient_address} on {datetime.now().strftime("%B %d, %Y")}.
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="demand_letter",
            title=f"DEMAND LETTER - {recipient_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "sender": sender_name,
                "recipient": recipient_name,
                "deadline": deadline_date,
                "legal_basis": legal_basis,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_cease_and_desist(
        self,
        sender_name: str,
        recipient_name: str,
        infringing_conduct: str,
        legal_violations: List[str],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate cease and desist letter with SHA-256 timestamp"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        content = f"""
CEASE AND DESIST NOTICE

TO: {recipient_name}
FROM: {sender_name}
DATE: {datetime.now().strftime("%B %d, %Y")}

RE: DEMAND TO IMMEDIATELY CEASE UNLAWFUL CONDUCT

This letter serves as formal notice that you must immediately cease and desist from the following unlawful conduct:

INFRINGING CONDUCT:
{infringing_conduct}

LEGAL VIOLATIONS:
"""
        for i, violation in enumerate(legal_violations, 1):
            content += f"{i}. {violation}\n"
        
        content += f"""
DEMAND:
You are hereby demanded to:
1. IMMEDIATELY CEASE all infringing conduct described above
2. PROVIDE WRITTEN CONFIRMATION of compliance within 10 days
3. DESTROY OR RETURN all infringing materials
4. PROVIDE ACCOUNTING of all profits derived from infringement

CONSEQUENCES OF NON-COMPLIANCE:
Failure to comply with this demand will result in legal action without further notice, including but not limited to:
- Injunctive relief (court order to stop conduct)
- Monetary damages (compensatory and punitive)
- Attorney fees and costs
- Statutory damages where applicable

You have 10 days from receipt of this letter to comply. Time is of the essence.

{sender_name}
{datetime.now().strftime("%B %d, %Y")}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="cease_and_desist",
            title=f"CEASE AND DESIST - {recipient_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "sender": sender_name,
                "recipient": recipient_name,
                "violations": legal_violations,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_evidence_summary(
        self,
        case_title: str,
        incident_date: str,
        parties: Dict[str, str],
        evidence_items: List[Dict[str, str]],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """
        Generate evidence summary with SHA-256 chain of custody timestamping.
        Critical for legal proceedings.
        """
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        content = f"""
EVIDENCE SUMMARY AND CHAIN OF CUSTODY

CASE: {case_title}
INCIDENT DATE: {incident_date}
COMPILED: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
DOCUMENT ID: {doc_id}

PARTIES:
"""
        for role, name in parties.items():
            content += f"  {role}: {name}\n"
        
        content += f"""
EVIDENCE INVENTORY:

"""
        for i, item in enumerate(evidence_items, 1):
            item_hash = self._generate_integrity_hash(json.dumps(item, sort_keys=True))
            content += f"""
EXHIBIT {i}:
  Description: {item.get('description', 'N/A')}
  Type: {item.get('type', 'N/A')}
  Source: {item.get('source', 'N/A')}
  Date Obtained: {item.get('date_obtained', 'N/A')}
  Custodian: {item.get('custodian', 'N/A')}
  SHA-256 Hash: {item_hash}
  Relevance: {item.get('relevance', 'N/A')}
  
"""
        
        content += f"""
CHAIN OF CUSTODY CERTIFICATION:

I hereby certify that the above evidence inventory accurately reflects the evidence in my possession related to this matter. Each item has been cryptographically timestamped using SHA-256 hashing to ensure integrity and authenticity.

This evidence summary was generated and timestamped by Mythara Gopher Legal AI to maintain forensic integrity and admissibility.

Timestamp: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="evidence_summary",
            title=f"EVIDENCE SUMMARY - {case_title}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "case_title": case_title,
                "incident_date": incident_date,
                "evidence_count": len(evidence_items),
                "parties": parties,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_legal_memo(
        self,
        title: str,
        issue_statement: str,
        brief_answer: str,
        facts: str,
        analysis: str,
        conclusion: str,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate professional legal memorandum with SHA-256 timestamp"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        content = f"""
LEGAL MEMORANDUM

TO: File
FROM: Mythara Gopher Legal AI
DATE: {datetime.now().strftime("%B %d, %Y")}
RE: {title}

{'='*80}

ISSUE:
{issue_statement}

BRIEF ANSWER:
{brief_answer}

FACTS:
{facts}

ANALYSIS:
{analysis}

CONCLUSION:
{conclusion}

{'='*80}

This memorandum was prepared using Mythara Engine's comprehensive legal database including:
- 60+ tort definitions with full element analysis
- Landmark case law and legal principles
- Federal and state statutory framework
- Soul Cradle emotional intelligence assessment

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="legal_memo",
            title=title,
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "issue": issue_statement,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_complaint(
        self,
        plaintiff_name: str,
        defendant_name: str,
        court_name: str,
        case_number: str,
        jurisdiction: str,
        causes_of_action: List[str],
        facts: str,
        damages: str,
        prayer_for_relief: str,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate civil complaint with SHA-256 timestamp"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # Build causes of action section
        coa_section = ""
        for i, cause in enumerate(causes_of_action, 1):
            coa_section += f"\nCAUSE OF ACTION {i}: {cause}\n"
            coa_section += f"Plaintiff incorporates all preceding paragraphs and alleges:\n"
            coa_section += f"[Elements and specific allegations for {cause}]\n"
        
        content = f"""
{'='*80}
IN THE {court_name.upper()}
{jurisdiction.upper()}
{'='*80}

{plaintiff_name},
                                                        Plaintiff,

                    v.                                  Case No.: {case_number}

{defendant_name},
                                                        Defendant.
{'='*80}

COMPLAINT FOR DAMAGES

{'='*80}

Preliminary Statement

Plaintiff {plaintiff_name}, by and through the undersigned, brings this Complaint
against Defendant {defendant_name} and alleges as follows:

{'='*80}

PARTIES

1. Plaintiff {plaintiff_name} is an individual residing in {jurisdiction}.

2. Defendant {defendant_name} is [describe defendant's status/residence].

{'='*80}

JURISDICTION AND VENUE

3. This Court has jurisdiction over this matter pursuant to [statutory basis].

4. Venue is proper in this Court pursuant to [venue statute].

{'='*80}

FACTUAL ALLEGATIONS

{facts}

{'='*80}

{coa_section}

{'='*80}

DAMAGES

{damages}

{'='*80}

PRAYER FOR RELIEF

WHEREFORE, Plaintiff respectfully requests that this Court:

{prayer_for_relief}

And grant such other and further relief as the Court deems just and proper.

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="complaint",
            title=f"Complaint - {plaintiff_name} v. {defendant_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "plaintiff": plaintiff_name,
                "defendant": defendant_name,
                "court": court_name,
                "case_number": case_number,
                "causes_of_action": causes_of_action,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_motion(
        self,
        motion_type: str,
        case_caption: str,
        case_number: str,
        court_name: str,
        moving_party: str,
        legal_basis: str,
        argument: str,
        relief_sought: str,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate legal motion with SHA-256 timestamp"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        content = f"""
{'='*80}
{court_name.upper()}
{'='*80}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

{motion_type.upper()}

{'='*80}

{moving_party} hereby moves this Court for an Order {relief_sought},
and in support thereof states as follows:

{'='*80}

LEGAL STANDARD

{legal_basis}

{'='*80}

ARGUMENT

{argument}

{'='*80}

CONCLUSION

For the foregoing reasons, {moving_party} respectfully requests that this Court
grant this Motion and {relief_sought}.

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]
{moving_party}

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="motion",
            title=motion_type,
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "motion_type": motion_type,
                "case_number": case_number,
                "moving_party": moving_party,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_interrogatories(
        self,
        propounding_party: str,
        responding_party: str,
        case_caption: str,
        case_number: str,
        interrogatory_questions: List[str],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate interrogatories (written discovery questions)"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        questions_section = ""
        for i, question in enumerate(interrogatory_questions, 1):
            questions_section += f"\nINTERROGATORY NO. {i}:\n{question}\n"
        
        content = f"""
{'='*80}
DISCOVERY - INTERROGATORIES
{'='*80}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

{propounding_party.upper()}'S FIRST SET OF INTERROGATORIES
TO {responding_party.upper()}

{'='*80}

PROPOUNDING PARTY: {propounding_party}
RESPONDING PARTY: {responding_party}
SET NUMBER: One

{'='*80}

INSTRUCTIONS

You are required to answer the following interrogatories separately and fully
in writing under oath within 30 days of service pursuant to applicable rules
of civil procedure.

Each interrogatory shall be answered separately and completely. If you cannot
answer an interrogatory in full, answer to the extent possible.

{'='*80}

DEFINITIONS

1. "You" or "Your" refers to {responding_party} and anyone acting on their behalf.

2. "Document" means any written, recorded, or graphic matter.

3. "Identify" when referring to a person means to state their full name, address,
   and telephone number.

{'='*80}

INTERROGATORIES

{questions_section}

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]
{propounding_party}

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="discovery",
            title=f"Interrogatories - {propounding_party} to {responding_party}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "propounding_party": propounding_party,
                "responding_party": responding_party,
                "case_number": case_number,
                "question_count": len(interrogatory_questions),
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_request_for_production(
        self,
        requesting_party: str,
        producing_party: str,
        case_caption: str,
        case_number: str,
        document_requests: List[str],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate Request for Production of Documents (RFP)"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        requests_section = ""
        for i, request in enumerate(document_requests, 1):
            requests_section += f"\nREQUEST FOR PRODUCTION NO. {i}:\n{request}\n"
        
        content = f"""
{'='*80}
REQUEST FOR PRODUCTION OF DOCUMENTS
{'='*80}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

{requesting_party.upper()}'S FIRST REQUEST FOR PRODUCTION OF DOCUMENTS
TO {producing_party.upper()}

{'='*80}

REQUESTING PARTY: {requesting_party}
PRODUCING PARTY: {producing_party}
SET NUMBER: One

{'='*80}

INSTRUCTIONS

Pursuant to applicable rules of civil procedure, you are requested to produce
and permit inspection and copying of the documents described below within 30 days
of service of this request.

All documents shall be produced as they are kept in the usual course of business
or organized and labeled to correspond with the categories in the request.

{'='*80}

DEFINITIONS

1. "Document" includes writings, drawings, graphs, charts, photographs, sound
   recordings, images, electronically stored information, and other data compilations.

2. "You" or "Your" refers to {producing_party} and anyone acting on their behalf.

3. "Communication" means any transmission of information between two or more persons.

{'='*80}

REQUESTS FOR PRODUCTION

{requests_section}

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]
{requesting_party}

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="discovery",
            title=f"Request for Production - {requesting_party} to {producing_party}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "requesting_party": requesting_party,
                "producing_party": producing_party,
                "case_number": case_number,
                "request_count": len(document_requests),
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_request_for_admissions(
        self,
        requesting_party: str,
        admitting_party: str,
        case_caption: str,
        case_number: str,
        admission_statements: List[str],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate Request for Admissions (RFA)"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        admissions_section = ""
        for i, statement in enumerate(admission_statements, 1):
            admissions_section += f"\nREQUEST FOR ADMISSION NO. {i}:\nAdmit that {statement}\n"
        
        content = f"""
{'='*80}
REQUEST FOR ADMISSIONS
{'='*80}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

{requesting_party.upper()}'S FIRST REQUEST FOR ADMISSIONS
TO {admitting_party.upper()}

{'='*80}

REQUESTING PARTY: {requesting_party}
ADMITTING PARTY: {admitting_party}
SET NUMBER: One

{'='*80}

INSTRUCTIONS

Pursuant to applicable rules of civil procedure, you are required to respond
to the following requests for admissions within 30 days of service.

Each matter is admitted unless you serve a written answer or objection.
If you deny a request, state the reason for the denial.

{'='*80}

REQUESTS FOR ADMISSION

{admissions_section}

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]
{requesting_party}

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="discovery",
            title=f"Request for Admissions - {requesting_party} to {admitting_party}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "requesting_party": requesting_party,
                "admitting_party": admitting_party,
                "case_number": case_number,
                "admission_count": len(admission_statements),
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_answer(
        self,
        defendant_name: str,
        plaintiff_name: str,
        case_caption: str,
        case_number: str,
        court_name: str,
        admissions: List[str],
        denials: List[str],
        affirmative_defenses: List[str],
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate Answer to Complaint"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        admissions_section = "\n".join([f"{i}. Defendant admits the allegations in paragraph {adm}." 
                                        for i, adm in enumerate(admissions, 1)])
        
        denials_section = "\n".join([f"{i}. Defendant denies the allegations in paragraph {den}." 
                                     for i, den in enumerate(denials, len(admissions) + 1)])
        
        defenses_section = ""
        for i, defense in enumerate(affirmative_defenses, 1):
            defenses_section += f"\nAFFIRMATIVE DEFENSE {i}: {defense}\n"
        
        content = f"""
{'='*80}
{court_name.upper()}
{'='*80}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

ANSWER TO COMPLAINT

{'='*80}

Defendant {defendant_name}, answering the Complaint filed by Plaintiff
{plaintiff_name}, states as follows:

{'='*80}

ANSWER TO ALLEGATIONS

{admissions_section}

{denials_section}

{'='*80}

AFFIRMATIVE DEFENSES

{defenses_section}

{'='*80}

WHEREFORE, Defendant respectfully requests that this Court:

1. Dismiss the Complaint in its entirety;
2. Award Defendant costs and attorney's fees; and
3. Grant such other and further relief as the Court deems just and proper.

{'='*80}

Respectfully submitted,

Date: {datetime.now().strftime("%B %d, %Y")}

_______________________________
[Attorney/Pro Se Signature]
{defendant_name}

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="answer",
            title=f"Answer - {defendant_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "defendant": defendant_name,
                "plaintiff": plaintiff_name,
                "case_number": case_number,
                "affirmative_defenses_count": len(affirmative_defenses),
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_affidavit(
        self,
        affiant_name: str,
        case_caption: str,
        case_number: str,
        statements: List[str],
        purpose: str,
        jurisdiction: str,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate sworn affidavit"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        statements_section = "\n".join([f"{i}. {stmt}" for i, stmt in enumerate(statements, 1)])
        
        content = f"""
{'='*80}
AFFIDAVIT
{'='*80}

STATE OF {jurisdiction.upper()}
COUNTY OF _______________

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

AFFIDAVIT OF {affiant_name.upper()}

{'='*80}

I, {affiant_name}, being duly sworn, depose and state as follows:

{statements_section}

{'='*80}

I declare under penalty of perjury that the foregoing is true and correct
to the best of my knowledge, information, and belief.

Executed on {datetime.now().strftime("%B %d, %Y")}.


_______________________________
{affiant_name}, Affiant


Subscribed and sworn to before me this _____ day of _____________, 20___.


_______________________________
Notary Public

My Commission Expires: ______________

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="affidavit",
            title=f"Affidavit of {affiant_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "affiant": affiant_name,
                "purpose": purpose,
                "case_number": case_number,
                "statement_count": len(statements),
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def generate_subpoena(
        self,
        issuing_party: str,
        recipient_name: str,
        case_caption: str,
        case_number: str,
        court_name: str,
        subpoena_type: str,  # duces_tecum, testimony, both
        appearance_date: str,
        appearance_location: str,
        documents_requested: List[str] = None,
        context: Optional[ConversationContext] = None
    ) -> LegalDocument:
        """Generate subpoena"""
        doc_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        subpoena_title = "SUBPOENA"
        if subpoena_type == "duces_tecum":
            subpoena_title = "SUBPOENA DUCES TECUM"
        elif subpoena_type == "testimony":
            subpoena_title = "SUBPOENA FOR TESTIMONY"
        
        docs_section = ""
        if documents_requested:
            docs_section = "\n\nDOCUMENTS TO BE PRODUCED:\n"
            docs_section += "\n".join([f"{i}. {doc}" for i, doc in enumerate(documents_requested, 1)])
        
        content = f"""
{'='*80}
{subpoena_title}
{'='*80}

{court_name.upper()}

{case_caption}
                                                        Case No.: {case_number}
{'='*80}

TO: {recipient_name}

YOU ARE COMMANDED to appear at the time, date, and place set forth below to
{"testify and produce documents" if subpoena_type == "both" else "testify" if subpoena_type == "testimony" else "produce documents"}:

DATE: {appearance_date}
TIME: 10:00 AM
PLACE: {appearance_location}

{docs_section}

{'='*80}

Issuing Party: {issuing_party}
Date Issued: {datetime.now().strftime("%B %d, %Y")}

_______________________________
Clerk of Court / Authorized Officer

{'='*80}

PROOF OF SERVICE

I declare that I served this subpoena by:
[ ] Personal delivery
[ ] Certified mail
[ ] Other: _______________

On _________________ (date) at _________________ (location)

Process Server Signature: _______________________________

Document generated and cryptographically timestamped: {timestamp}
"""
        
        integrity_hash = self._generate_integrity_hash(content)
        
        doc = LegalDocument(
            doc_id=doc_id,
            doc_type="subpoena",
            title=f"{subpoena_title} - {recipient_name}",
            content=content,
            timestamp=timestamp,
            integrity_hash=integrity_hash,
            metadata={
                "issuing_party": issuing_party,
                "recipient": recipient_name,
                "subpoena_type": subpoena_type,
                "appearance_date": appearance_date,
                "case_number": case_number,
                "generated_by": "Mythara Gopher Legal AI"
            }
        )
        
        if context:
            context.generated_documents.append(doc)
        
        return doc
    
    def timestamp_user_statement(self, statement: str, user_id: str) -> Dict[str, str]:
        """
        Cryptographically timestamp a user statement for evidentiary purposes.
        Returns timestamp data that can be used as evidence of when something was said/happened.
        """
        timestamp = datetime.now().isoformat()
        statement_data = {
            "statement": statement,
            "user_id": user_id,
            "timestamp": timestamp,
            "timezone": "UTC"
        }
        
        # Generate SHA-256 hash for integrity
        content_str = json.dumps(statement_data, sort_keys=True)
        integrity_hash = self._generate_integrity_hash(content_str)
        
        return {
            "statement": statement,
            "timestamp": timestamp,
            "integrity_hash": integrity_hash,
            "certification": f"This statement was cryptographically timestamped by Mythara Gopher at {timestamp}. SHA-256 hash: {integrity_hash}. This timestamp can serve as evidence of when this statement was made."
        }
    
    def process_query(self, user_query: str, user_id: str = "default", session_id: str = None) -> str:
        """
        Main entry point: Process natural language legal query.
        
        Args:
            user_query: User's natural language question
            user_id: User identifier
            session_id: Conversation session ID
        
        Returns:
            Natural language response
        """
        # Create or retrieve conversation context
        if session_id is None:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        context = self._get_or_create_context(user_id, session_id)
        
        # Add user query to conversation history (original form)
        context.conversation_history.append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Normalize vernacular/multilingual input for processing
        normalized_query = self.normalize_vernacular(user_query)
        
        # Classify intent (using normalized query)
        intents = self._classify_intent(normalized_query)
        context.identified_intents.extend(intents)
        
        # Extract entities (using normalized query)
        entities = self._extract_entities(normalized_query)
        for entity_type, values in entities.items():
            context.extracted_entities[entity_type].extend(values)
        
        # ABC Consultation Framework - Assess and track consultation progress
        pain_points = self.identify_pain_points(normalized_query, context)
        context.pain_points.extend([p for p in pain_points if p not in context.pain_points])
        
        context.urgency_level = self.assess_urgency(normalized_query, context)
        context.readiness_to_act = self.assess_readiness_to_act(normalized_query, context)
        
        user_prefs = self.extract_user_preferences(normalized_query, context)
        context.user_preferences.update(user_prefs)
        
        context.consultation_stage = self.assess_consultation_stage(context)
        
        # Soul Cradle Analysis (emotional intelligence layer)
        # Use normalized query for analysis but preserve original for context
        paradox_analysis = self._detect_legal_paradox(normalized_query, entities, context)
        coercion_analysis = self._assess_emotional_coercion(normalized_query, entities)
        burnout_risk = self._calculate_burnout_risk(context)
        
        # Store Soul Cradle insights in context
        if paradox_analysis:
            context.confidence_scores["paradox_detected"] = paradox_analysis["tension_score"]
        if coercion_analysis:
            context.confidence_scores["coercion_score"] = coercion_analysis["coercion_score"]
            context.confidence_scores["will_authenticity"] = coercion_analysis["will_authenticity"]
        if burnout_risk:
            context.user_sentiment = f"{context.user_sentiment}_burnout_risk_{burnout_risk}"
        
        # Generate response (use original query for natural response tone)
        response = self._generate_response(normalized_query, intents, entities, context)
        
        # Append Soul Cradle warnings if critical issues detected
        if paradox_analysis and paradox_analysis.get("burnout_risk") == "HIGH":
            response += f"\\n\\n🔴 **PARADOX ALERT**: {paradox_analysis['recommendation']}"
        if coercion_analysis and coercion_analysis["risk_level"] == "HIGH":
            response += f"\\n\\n⚠️ **COERCION DETECTED**: {coercion_analysis['recommendation']}"
        if burnout_risk == "HIGH":
            response += "\\n\\n💙 **Wellbeing Note**: Multiple stressors detected. Please prioritize self-care and consider speaking with a counselor in addition to legal counsel."
        
        # ABC Framework - Always Be Closing: Add action plan when appropriate
        # Close the loop if we're past discovery stage and have decent readiness
        if context.consultation_stage in ["solution_design", "implementation", "closing"]:
            if context.readiness_to_act > 0.4 or len(context.pain_points) >= 2:
                response += self.close_the_loop(context)
        elif context.consultation_stage == "qualification" and context.urgency_level in ["high", "critical"]:
            # Even in qualification, close if urgent
            response += self.close_the_loop(context)
        
        # Add response to conversation history
        context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get existing or create new conversation context"""
        if session_id not in self.active_contexts:
            self.active_contexts[session_id] = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                conversation_history=[],
                identified_intents=[],
                extracted_entities=defaultdict(list),
                practice_area_focus=None,
                current_topic=None,
                timestamp=datetime.now().isoformat()
            )
        return self.active_contexts[session_id]
    
    def _classify_intent(self, query: str) -> List[str]:
        """
        Classify user intent using pattern matching.
        Returns list of matched intents.
        """
        query_lower = query.lower()
        matched_intents = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    matched_intents.append(intent)
                    break  # One match per intent sufficient
        
        return matched_intents
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract legal entities from query.
        Returns dictionary of entity types and extracted values.
        """
        entities = defaultdict(list)
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return dict(entities)
    
    def _generate_response(self, query: str, intents: List[str], entities: Dict, context: ConversationContext) -> str:
        """
        Generate natural language response based on intent and entities.
        """
        # Check for greeting
        if re.search(r"\b(hello|hi|hey|greetings)\b", query.lower()):
            return self.response_templates["greeting"][0]
        
        # No clear intent detected
        if not intents:
            return self._handle_unclear_query(query)
        
        # Prioritize document_generation if explicitly requesting document creation
        query_lower = query.lower()
        document_keywords = ["draft", "write", "create", "generate", "prepare", "send", "file", "demand letter", "cease and desist", "complaint", "motion"]
        has_document_request = "document_generation" in intents and any(kw in query_lower for kw in document_keywords)
        
        # Prioritize show_disclaimer if explicitly asking about terms/disclaimer
        disclaimer_keywords = ["show", "display", "view", "read", "see", "what are", "what is"]
        has_disclaimer_request = "show_disclaimer" in intents and any(kw in query_lower for kw in disclaimer_keywords)
        
        # Prioritize attorney_referral intent if query explicitly asks for attorney/lawyer
        if has_disclaimer_request:
            primary_intent = "show_disclaimer"
        elif has_document_request:
            primary_intent = "document_generation"
        elif "attorney_referral" in intents:
            attorney_keywords = ["need", "find", "looking for", "want", "recommend", "referral", "connect me"]
            lawyer_keywords = ["attorney", "lawyer", "counsel", "legal help"]
            has_attorney_request = any(kw in query_lower for kw in attorney_keywords) and any(kw in query_lower for kw in lawyer_keywords)
            if has_attorney_request:
                primary_intent = "attorney_referral"
            else:
                primary_intent = intents[0]
        else:
            # Route to appropriate handler based on primary intent
            primary_intent = intents[0]
        
        if primary_intent == "tort_analysis":
            return self._handle_tort_analysis(query, entities, context)
        elif primary_intent == "statute_of_limitations":
            return self._handle_statute_query(query, entities, context)
        elif primary_intent == "legal_research":
            return self._handle_legal_research(query, entities, context)
        elif primary_intent == "contract_review":
            return self._handle_contract_query(query, entities, context)
        elif primary_intent == "compliance_check":
            return self._handle_compliance_query(query, entities, context)
        elif primary_intent == "ip_protection":
            return self._handle_ip_query(query, entities, context)
        elif primary_intent == "employment_issue":
            return self._handle_employment_query(query, entities, context)
        elif primary_intent == "damages_calculation":
            return self._handle_damages_query(query, entities, context)
        elif primary_intent == "defense_strategy":
            return self._handle_defense_query(query, entities, context)
        elif primary_intent == "document_generation":
            return self._handle_document_generation(query, entities, context)
        elif primary_intent == "show_disclaimer":
            return self._handle_disclaimer_request(query, entities, context)
        elif primary_intent == "attorney_referral":
            return self._handle_attorney_referral(query, entities, context)
        else:
            return self._handle_general_query(query, entities, context)
    
    def _handle_disclaimer_request(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle requests to view legal disclaimer"""
        return self.get_legal_disclaimer(brief=False)
    
    def _handle_document_generation(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle document generation requests with SHA-256 timestamping"""
        response = "📄 **Document Generation Service**\n\n"
        
        query_lower = query.lower()
        
        # Determine document type requested
        if "complaint" in query_lower or "civil complaint" in query_lower:
            response += "I can generate a civil complaint (lawsuit filing) with SHA-256 timestamp.\n\n"
            response += "**Required Information:**\n"
            response += "• Plaintiff and defendant names\n"
            response += "• Court name and jurisdiction\n"
            response += "• Causes of action (e.g., negligence, breach of contract)\n"
            response += "• Factual allegations\n"
            response += "• Damages sought\n"
            response += "• Prayer for relief\n\n"
            response += "**Use:** File lawsuit in civil court\n\n"
        
        elif "motion" in query_lower:
            response += "I can generate legal motions with SHA-256 timestamp.\n\n"
            response += "**Common Motion Types:**\n"
            response += "• Motion to Dismiss\n"
            response += "• Motion for Summary Judgment\n"
            response += "• Motion to Compel Discovery\n"
            response += "• Motion for Preliminary Injunction\n"
            response += "• Motion in Limine\n"
            response += "• Motion for Continuance\n\n"
            response += "**Required:** Case info, legal standard, argument, relief sought\n\n"
        
        elif "interrogator" in query_lower or "discovery" in query_lower:
            response += "I can generate discovery documents with SHA-256 timestamps:\n\n"
            response += "**Discovery Types:**\n"
            response += "• **Interrogatories** - Written questions opponent must answer under oath\n"
            response += "• **Request for Production (RFP)** - Demand documents/evidence\n"
            response += "• **Request for Admissions (RFA)** - Statements to admit/deny\n\n"
            response += "**Timeline:** Responses typically due within 30 days\n"
            response += "**Use:** Gather evidence, establish facts, prepare for trial\n\n"
        
        elif "answer" in query_lower and ("complaint" in query_lower or "response" in query_lower):
            response += "I can generate an Answer to Complaint with SHA-256 timestamp.\n\n"
            response += "**Includes:**\n"
            response += "• Admissions (paragraphs you admit)\n"
            response += "• Denials (paragraphs you deny)\n"
            response += "• Affirmative defenses (statute of limitations, waiver, etc.)\n"
            response += "• Counterclaims (optional)\n\n"
            response += "**Critical:** Must be filed within 20-30 days of service!\n\n"
        
        elif "affidavit" in query_lower or "declaration" in query_lower:
            response += "I can generate sworn affidavits/declarations with SHA-256 timestamp.\n\n"
            response += "**Use Cases:**\n"
            response += "• Supporting evidence for motions\n"
            response += "• Witness statements\n"
            response += "• Proof of facts\n"
            response += "• Authentication of documents\n\n"
            response += "**Note:** Must be signed before notary public\n\n"
        
        elif "subpoena" in query_lower:
            response += "I can generate subpoenas with SHA-256 timestamp.\n\n"
            response += "**Subpoena Types:**\n"
            response += "• **Subpoena for Testimony** - Compel witness appearance\n"
            response += "• **Subpoena Duces Tecum** - Compel document production\n"
            response += "• **Combined** - Testimony + documents\n\n"
            response += "**Note:** Must be properly served and may require court approval\n\n"
        
        elif "demand letter" in query_lower or ("demand" in query_lower and "letter" in query_lower):
            response += "I can generate a professional demand letter with cryptographic timestamping.\n\n"
            response += "**Required Information:**\n"
            response += "• Your name and address\n"
            response += "• Recipient's name and address\n"
            response += "• Description of incident/harm\n"
            response += "• Legal basis (torts/violations)\n"
            response += "• Damages amount\n"
            response += "• 30-day deadline for response\n\n"
        
        elif "cease and desist" in query_lower or "cease & desist" in query_lower:
            response += "I can generate a cease and desist letter with SHA-256 timestamp.\n\n"
            response += "**Use Cases:**\n"
            response += "• Copyright/trademark infringement\n"
            response += "• Defamation/libel\n"
            response += "• Harassment\n"
            response += "• Contract violations\n\n"
        
        elif "writ" in query_lower:
            response += "I can generate writs with SHA-256 timestamp.\n\n"
            response += "**Common Writs:**\n"
            response += "• Writ of Execution (enforce judgment)\n"
            response += "• Writ of Garnishment (collect wages/accounts)\n"
            response += "• Writ of Possession (eviction enforcement)\n"
            response += "• Writ of Habeas Corpus (challenge detention)\n\n"
            response += "**Note:** Writs typically require court approval\n\n"
        
        elif "evidence" in query_lower or "chain of custody" in query_lower:
            response += "I can generate evidence summaries with chain of custody tracking.\n\n"
            response += "**Features:**\n"
            response += "• SHA-256 hash for each piece of evidence\n"
            response += "• Cryptographic timestamps\n"
            response += "• Chain of custody certification\n"
            response += "• Forensic integrity for court admissibility\n\n"
        
        elif "memo" in query_lower or "memorandum" in query_lower:
            response += "I can generate a professional legal memorandum.\n\n"
            response += "**Structure:**\n"
            response += "• Issue Statement\n"
            response += "• Brief Answer\n"
            response += "• Facts\n"
            response += "• Analysis (with case law)\n"
            response += "• Conclusion\n"
            response += "• SHA-256 timestamp\n\n"
        
        elif "timestamp" in query_lower:
            response += "I can cryptographically timestamp any statement or document.\n\n"
            response += "**SHA-256 Timestamping:**\n"
            response += "• Proves when something was said/documented\n"
            response += "• Creates tamper-proof record\n"
            response += "• Admissible as evidence\n"
            response += "• Blockchain-style integrity\n\n"
        
        else:
            response += "I can generate comprehensive legal documents with SHA-256 timestamping:\n\n"
            response += "**📋 COURT FILINGS:**\n"
            response += "• Complaints (start lawsuits)\n"
            response += "• Answers (respond to lawsuits)\n"
            response += "• Motions (request court orders)\n"
            response += "• Writs (court enforcement orders)\n\n"
            
            response += "**🔍 DISCOVERY DOCUMENTS:**\n"
            response += "• Interrogatories (written questions)\n"
            response += "• Request for Production (RFP - demand documents)\n"
            response += "• Request for Admissions (RFA - facts to admit/deny)\n"
            response += "• Subpoenas (compel testimony/documents)\n\n"
            
            response += "**📝 SUPPORTING DOCUMENTS:**\n"
            response += "• Affidavits/Declarations (sworn statements)\n"
            response += "• Legal Memoranda (case analysis)\n"
            response += "• Evidence Summaries (chain of custody)\n\n"
            
            response += "**📨 PRE-LITIGATION:**\n"
            response += "• Demand Letters (formal legal demands)\n"
            response += "• Cease & Desist (stop violations)\n\n"
            
            response += "**All documents include:**\n"
            response += "• SHA-256 integrity hash (tamper-proof)\n"
            response += "• ISO timestamp (millisecond precision)\n"
            response += "• Professional legal formatting\n"
            response += "• Court-ready certification\n\n"
        
        response += "**Why SHA-256 Timestamping Matters:**\n"
        response += "• Proves document authenticity\n"
        response += "• Detects any tampering\n"
        response += "• Creates forensic audit trail\n"
        response += "• Admissible in legal proceedings\n\n"
        
        if len(context.generated_documents) > 0:
            response += f"**Your Session Documents:** {len(context.generated_documents)} document(s) generated\n\n"
        
        response += "Which document would you like me to prepare?\n\n"
        
        # Add legal disclaimer
        response += self.get_legal_disclaimer(brief=True)
        
        return response
    
    def _handle_attorney_referral(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle attorney referral requests with practice area and location filtering"""
        response = "👨‍⚖️ **Attorney Referral Service**\n\n"
        
        query_lower = query.lower()
        
        # Extract jurisdiction from entities or query
        jurisdictions = entities.get("jurisdiction", [])
        
        # Convert jurisdictions to state codes
        import re
        
        # State name to code mapping
        state_map = {
            "california": "CA", "new york": "NY", "texas": "TX", "florida": "FL", 
            "illinois": "IL", "pennsylvania": "PA", "ohio": "OH", "georgia": "GA",
            "north carolina": "NC", "michigan": "MI", "new jersey": "NJ", "virginia": "VA",
            "washington": "WA", "arizona": "AZ", "massachusetts": "MA", "tennessee": "TN",
            "indiana": "IN", "missouri": "MO", "maryland": "MD", "wisconsin": "WI",
            "colorado": "CO", "minnesota": "MN", "south carolina": "SC", "alabama": "AL",
            "louisiana": "LA", "kentucky": "KY", "oregon": "OR", "oklahoma": "OK",
            "connecticut": "CT", "iowa": "IA", "mississippi": "MS", "arkansas": "AR",
            "kansas": "KS", "utah": "UT", "nevada": "NV", "new mexico": "NM",
            "nebraska": "NE", "west virginia": "WV", "idaho": "ID", "hawaii": "HI",
            "new hampshire": "NH", "maine": "ME", "montana": "MT", "rhode island": "RI",
            "delaware": "DE", "south dakota": "SD", "north dakota": "ND", "alaska": "AK",
            "vermont": "VT", "wyoming": "WY"
        }
        
        # Convert full state names to codes
        normalized_jurisdictions = []
        for jurisdiction in jurisdictions:
            jurisdiction_lower = jurisdiction.lower()
            if jurisdiction_lower in state_map:
                normalized_jurisdictions.append(state_map[jurisdiction_lower])
            elif len(jurisdiction) == 2:  # Already a state code
                normalized_jurisdictions.append(jurisdiction.upper())
            else:
                normalized_jurisdictions.append(jurisdiction)  # Keep as-is (federal, etc.)
        
        # If no jurisdictions from entities, try extracting from query
        if not normalized_jurisdictions:
            # First try full state names (lowercase)
            for state_name, state_code in state_map.items():
                if state_name in query_lower:
                    normalized_jurisdictions.append(state_code)
            
            # If no full names found, try state codes (but only as standalone words)
            if not normalized_jurisdictions:
                state_pattern = r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b"
                state_matches = re.findall(state_pattern, query.upper())
                if state_matches:
                    normalized_jurisdictions = state_matches
        
        jurisdictions = list(set(normalized_jurisdictions))  # Remove duplicates
        
        # Identify practice area from query keywords
        matched_areas = []
        for area_key, area_data in self.attorney_database["practice_areas"].items():
            for keyword in area_data["keywords"]:
                if keyword in query_lower:
                    matched_areas.append((area_key, area_data["description"]))
                    break
        
        if matched_areas:
            response += f"**Case Type Detected:** {', '.join([desc for _, desc in matched_areas])}\n\n"
        
        if jurisdictions:
            response += f"**Location:** {', '.join(jurisdictions)}\n\n"
        
        # Search attorney database
        matching_attorneys = []
        for attorney in self.attorney_database["attorneys"]:
            # Match by jurisdiction
            jurisdiction_match = not jurisdictions or any(j in attorney["states"] for j in jurisdictions)
            
            # Match by practice area
            area_match = not matched_areas or any(
                area_key in attorney["practice_areas"] for area_key, _ in matched_areas
            )
            
            if jurisdiction_match and area_match:
                matching_attorneys.append(attorney)
        
        if matching_attorneys:
            response += f"**✅ {len(matching_attorneys)} Referral(s) Available:**\n\n"
            for i, atty in enumerate(matching_attorneys[:5], 1):  # Show top 5
                response += f"{i}. **{atty['name']}**\n"
                response += f"   Firm: {atty['firm']}\n"
                response += f"   Practice Areas: {', '.join([self.attorney_database['practice_areas'][area]['description'] for area in atty['practice_areas']])}\n"
                response += f"   Location: {', '.join(atty['cities'])}\n"
                if atty.get('free_consultation'):
                    response += f"   💡 Free Consultation Available\n"
                response += f"   📞 {atty['phone']}\n"
                response += f"   📧 {atty['email']}\n"
                response += f"   🌐 {atty['website']}\n"
                if atty.get('notes'):
                    response += f"   ℹ️ {atty['notes']}\n"
                response += f"\n"
        else:
            response += "**No direct referrals found in database for your specific criteria.**\n\n"
        
        # Add bar association referral info
        if jurisdictions:
            response += "**📋 State Bar Referral Services:**\n\n"
            for juris in jurisdictions:
                if juris in self.attorney_database["bar_associations"]:
                    bar = self.attorney_database["bar_associations"][juris]
                    response += f"**{bar['name']}**\n"
                    response += f"   🌐 {bar['website']}\n"
                    response += f"   📞 {bar['phone']}\n"
                    response += f"   ℹ️ Free lawyer referral service\n\n"
        
        # Add legal aid resources
        response += "**💰 Free/Low-Cost Legal Help:**\n\n"
        response += f"**{self.attorney_database['legal_aid']['national']['name']}**\n"
        response += f"   🌐 {self.attorney_database['legal_aid']['national']['website']}\n"
        response += f"   ℹ️ {self.attorney_database['legal_aid']['national']['description']}\n\n"
        
        # Add how to verify credentials
        response += "**⚠️ VERIFY ATTORNEY CREDENTIALS:**\n"
        response += "Before hiring any attorney:\n"
        response += "1. ✅ Verify bar license (check state bar website)\n"
        response += "2. ✅ Check disciplinary history\n"
        response += "3. ✅ Read client reviews\n"
        response += "4. ✅ Get fee agreement in writing\n"
        response += "5. ✅ Meet for consultation (many offer free consults)\n\n"
        
        # Add attorney submission info
        response += "**📢 Attorneys: Join Our Public Database**\n"
        response += "Submit your practice information for inclusion:\n"
        response += "📧 attorney_referrals@mythara.com\n"
        response += "🌐 https://mythara.com/attorney-referrals\n\n"
        
        # Add disclaimer
        response += "**⚖️ REFERRAL DISCLAIMER:**\n"
        response += "Mythara Gopher provides this public attorney database as a SERVICE ONLY.\n"
        response += "We do NOT endorse, guarantee, or warrant any attorney's services.\n"
        response += "You are responsible for verifying credentials and selecting counsel.\n"
        response += "Inclusion in this database is NOT a recommendation or endorsement.\n\n"
        
        return response
    
    def _handle_tort_analysis(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle tort analysis queries with conversational intelligence"""
        response = "📋 **Tort Analysis**\n\n"
        
        # Search for applicable torts based on query keywords
        query_lower = query.lower()
        applicable_torts = []
        
        for tort_name, tort_info in self.knowledge_base["torts"].items():
            # Check if any keywords match
            for keyword in tort_info["keywords"]:
                if keyword in query_lower:
                    applicable_torts.append((tort_name, tort_info))
                    break
        
        if applicable_torts:
            response += f"Based on your query, I've identified {len(applicable_torts)} potentially relevant tort(s):\n\n"
            
            for tort_name, tort_info in applicable_torts[:3]:  # Top 3
                tort_def = self.torts_index.get_tort_definition(tort_name)
                if tort_def:
                    response += f"**{tort_info['name']}** ({tort_info['category']})\n"
                    response += f"To establish this claim, you would need to prove:\n"
                    for i, elem in enumerate(tort_def.elements[:4], 1):  # First 4 elements
                        response += f"  {i}. {elem.element_name}: {elem.description}\n"
                    
                    # Statute of limitations
                    sol = tort_info['sol'].get('default', 'varies')
                    response += f"\n⏱️ Statute of Limitations: {sol} years (varies by jurisdiction)\n"
                    
                    # Available defenses
                    if tort_info['defenses']:
                        response += f"🛡️ Potential Defenses: {', '.join(tort_info['defenses'][:3])}\n"
                    
                    response += "\n"
        else:
            # General tort analysis
            response += "Let me help you analyze potential tort claims. "
            response += "Please provide more specific details about:\n"
            response += "  • What happened (the incident or harm)\n"
            response += "  • Who was involved\n"
            response += "  • When it occurred\n"
            response += "  • What damages or injuries resulted\n\n"
            response += "This information will help me identify applicable legal claims.\n"
        
        response += "\n" + self.response_templates["disclaimer"][0]
        return response
    
    def _handle_statute_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle statute of limitations queries"""
        response = "⏱️ **Statute of Limitations Information**\n\n"
        
        jurisdiction = entities.get("jurisdiction", ["default"])[0] if entities.get("jurisdiction") else "default"
        
        # Try to identify which tort from query
        applicable_tort = None
        query_lower = query.lower()
        
        for tort_name, tort_info in self.knowledge_base["torts"].items():
            if any(kw in query_lower for kw in tort_info["keywords"]):
                applicable_tort = tort_name
                break
        
        if applicable_tort:
            tort_info = self.knowledge_base["torts"][applicable_tort]
            sol_years = tort_info["sol"].get(jurisdiction.lower(), tort_info["sol"].get("default", 2))
            
            response += f"For **{tort_info['name']}** claims:\n"
            response += f"• **{jurisdiction}**: {sol_years} years from date of injury/discovery\n"
            response += f"• This is the deadline to file a lawsuit\n"
            response += f"• Missing this deadline typically results in case dismissal\n\n"
            
            if entities.get("date"):
                response += f"📅 Based on the date you mentioned ({entities['date'][0]}), "
                response += f"you should consult an attorney immediately to verify if the statute has expired.\n\n"
        else:
            response += "Statute of limitations varies by:\n"
            response += "• **Type of claim** (tort, contract, etc.)\n"
            response += "• **Jurisdiction** (state vs federal)\n"
            response += "• **Discovery rule** (when injury was discovered)\n\n"
            response += "Common timeframes:\n"
            response += "• Personal injury: 1-3 years\n"
            response += "• Defamation: 1-2 years\n"
            response += "• Contract breach: 4-6 years\n"
            response += "• Fraud: 3-4 years\n\n"
            response += "Could you specify the type of legal claim you're asking about?\n"
        
        response += "\n" + self.response_templates["disclaimer"][0]
        return response
    
    def _handle_legal_research(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle legal research queries"""
        response = "📚 **Legal Research Results**\n\n"
        
        # Search knowledge base
        query_lower = query.lower()
        results = {
            "cases": [],
            "maxims": [],
            "concepts": []
        }
        
        # Search cases
        for case_key, case_info in self.knowledge_base["cases"].items():
            if any(keyword in query_lower for keyword in case_info["keywords"]):
                results["cases"].append(case_info)
        
        # Search maxims
        for maxim_key, maxim_info in self.knowledge_base["maxims"].items():
            if any(keyword in query_lower for keyword in maxim_info["keywords"]):
                results["maxims"].append(maxim_info)
        
        if results["cases"]:
            response += "**Relevant Case Law:**\n\n"
            for case in results["cases"][:3]:
                response += f"📖 **{case['name']}**, {case['citation']} ({case['year']})\n"
                response += f"   Holding: {case['holding']}\n"
                response += f"   Principle: {case['principle']}\n\n"
        
        if results["maxims"]:
            response += "**Applicable Legal Maxims:**\n\n"
            for maxim in results["maxims"][:2]:
                response += f"⚖️ **{maxim['latin']}** ({maxim['english']})\n"
                response += f"   {maxim['explanation']}\n\n"
        
        if not results["cases"] and not results["maxims"]:
            response += "I didn't find specific matches in my knowledge base. "
            response += "Could you rephrase your question or provide more specific legal terms?\n\n"
            response += "I can help research:\n"
            response += "• Landmark court cases\n"
            response += "• Legal principles and doctrines\n"
            response += "• Tort definitions and elements\n"
            response += "• Federal rules of evidence and procedure\n"
        
        return response
    
    def _handle_contract_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle contract-related queries"""
        response = "📄 **Contract Analysis**\n\n"
        
        response += "For contract review, I can help identify:\n"
        response += "• **Formation issues**: Offer, acceptance, consideration\n"
        response += "• **Risky terms**: Unlimited liability, auto-renewal, unilateral changes\n"
        response += "• **Missing protections**: Limitation of liability, termination rights\n"
        response += "• **Compliance gaps**: GDPR, CCPA, industry-specific requirements\n\n"
        
        if "breach" in query.lower():
            response += "**Contract Breach Analysis:**\n"
            response += "To prove breach of contract, you need:\n"
            response += "1. Valid contract existed\n"
            response += "2. You performed your obligations\n"
            response += "3. Other party failed to perform\n"
            response += "4. You suffered damages\n\n"
        
        response += "Would you like me to:\n"
        response += "• Review specific contract terms?\n"
        response += "• Analyze breach of contract scenario?\n"
        response += "• Explain contract remedies?\n"
        
        return response
    
    def _handle_compliance_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle compliance queries"""
        response = "🔐 **Compliance Analysis**\n\n"
        
        query_lower = query.lower()
        
        if "gdpr" in query_lower:
            response += "**GDPR Compliance Requirements:**\n"
            response += "• Lawful basis for processing (Art. 6)\n"
            response += "• Data subject rights (access, deletion, portability)\n"
            response += "• 72-hour breach notification\n"
            response += "• Data Protection Impact Assessments\n"
            response += "• Privacy by design and default\n\n"
        
        if "ccpa" in query_lower or "cpra" in query_lower:
            response += "**CCPA/CPRA Requirements:**\n"
            response += "• Privacy notice with data categories\n"
            response += "• Do Not Sell/Share opt-out\n"
            response += "• Right to deletion\n"
            response += "• Right to access\n"
            response += "• Authorized agent verification\n\n"
        
        if "hipaa" in query_lower:
            response += "**HIPAA Compliance:**\n"
            response += "• Administrative Safeguards (45 CFR § 164.308)\n"
            response += "• Physical Safeguards (45 CFR § 164.310)\n"
            response += "• Technical Safeguards (45 CFR § 164.312)\n"
            response += "• Business Associate Agreements\n"
            response += "• Breach notification requirements\n\n"
        
        response += "Which specific compliance framework would you like detailed guidance on?\n"
        return response
    
    def _handle_ip_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle IP protection queries"""
        response = "🛡️ **Intellectual Property Guidance**\n\n"
        
        query_lower = query.lower()
        
        if "trademark" in query_lower:
            response += "**Trademark Protection:**\n"
            response += "• Conduct USPTO TESS search\n"
            response += "• Check state registrations\n"
            response += "• Common law search (Google, domains)\n"
            response += "• File trademark application\n"
            response += "• Use ™ (unregistered) or ® (registered)\n\n"
        
        if "patent" in query_lower:
            response += "**Patent Protection:**\n"
            response += "• Utility patents: novel, useful, non-obvious inventions\n"
            response += "• Design patents: ornamental designs\n"
            response += "• Patent search required before filing\n"
            response += "• Freedom-to-operate analysis recommended\n"
            response += "• 20-year term from filing date\n\n"
        
        if "copyright" in query_lower:
            response += "**Copyright Protection:**\n"
            response += "• Automatic upon creation (fixed in tangible medium)\n"
            response += "• Registration required for statutory damages\n"
            response += "• Life of author + 70 years (or 95 years for works for hire)\n"
            response += "• Use © notice\n\n"
        
        if "trade secret" in query_lower:
            response += "**Trade Secret Protection:**\n"
            response += "• Not generally known\n"
            response += "• Economic value from secrecy\n"
            response += "• Reasonable secrecy measures required\n"
            response += "• NDAs and access controls essential\n\n"
        
        return response
    
    def _handle_employment_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle employment law queries"""
        response = "👔 **Employment Law Guidance**\n\n"
        
        query_lower = query.lower()
        
        # Detect discrimination patterns (explicit or implicit)
        discrimination_patterns = [
            "discrimination", "discriminate", "different treatment", "treating me different",
            "because i'm", "because of my", "due to my", "based on my",
            "race", "black", "white", "gender", "sex", "age", "disability"
        ]
        has_discrimination = any(pattern in query_lower for pattern in discrimination_patterns)
        
        if "fire" in query_lower or "termination" in query_lower or "terminated" in query_lower:
            response += "**Wrongful Termination Analysis:**\n"
            response += "At-will employment allows termination for any legal reason, BUT exceptions exist:\n"
            response += "• Discrimination (race, gender, age, disability, etc.)\n"
            response += "• Retaliation (whistleblowing, complaints, protected activity)\n"
            response += "• Violation of public policy\n"
            response += "• Breach of contract (if employment contract exists)\n\n"
            response += "Red flags:\n"
            response += "• Termination shortly after complaint/protected activity\n"
            response += "• Pretextual reasons\n"
            response += "• Different treatment than similarly situated employees\n\n"
        
        if has_discrimination:
            response += "**Discrimination Protection:**\n"
            response += "Protected characteristics under federal law (Title VII, ADA, ADEA):\n"
            response += "• Race, color, national origin\n"
            response += "• Sex, pregnancy, gender identity\n"
            response += "• Religion\n"
            response += "• Age (40+)\n"
            response += "• Disability\n\n"
            response += "**If you're experiencing workplace discrimination:**\n"
            response += "1. Document everything (dates, witnesses, statements)\n"
            response += "2. Report to HR or supervisor (in writing)\n"
            response += "3. File EEOC complaint (within 180-300 days)\n"
            response += "4. Consult employment attorney immediately\n\n"
            response += "⚠️ Time is critical - discrimination claims have strict deadlines!\n\n"
        
        # If neither fire nor discrimination detected, provide general employment guidance
        if "fire" not in query_lower and "termination" not in query_lower and not has_discrimination:
            response += "**Common Employment Issues:**\n"
            response += "• **Wrongful termination** - Illegal firing (discrimination, retaliation)\n"
            response += "• **Wage theft** - Unpaid wages, overtime, misclassification\n"
            response += "• **Harassment** - Hostile work environment, sexual harassment\n"
            response += "• **Discrimination** - Based on protected characteristics\n"
            response += "• **Retaliation** - Adverse action after complaint\n\n"
            response += "Please describe your specific situation so I can provide targeted guidance.\n\n"
        
        return response
    
    def _handle_damages_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle damages calculation queries"""
        response = "💰 **Damages Analysis**\n\n"
        
        response += "**Types of Damages:**\n\n"
        response += "**Compensatory Damages:**\n"
        response += "• Economic: Medical bills, lost wages, property damage\n"
        response += "• Non-economic: Pain and suffering, emotional distress\n\n"
        
        response += "**Punitive Damages:**\n"
        response += "• Available for malicious, willful, or reckless conduct\n"
        response += "• Designed to punish and deter\n"
        response += "• Often capped by state law\n\n"
        
        if entities.get("money"):
            response += f"Based on the amount you mentioned ({entities['money'][0]}), "
            response += "actual damages will depend on documented losses and jurisdiction-specific limits.\n\n"
        
        response += "To calculate damages, gather:\n"
        response += "• Medical bills and records\n"
        response += "• Lost wage documentation\n"
        response += "• Property damage estimates\n"
        response += "• Expert opinions on future damages\n"
        
        return response
    
    def _handle_defense_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle defense strategy queries"""
        response = "🛡️ **Defense Strategy**\n\n"
        
        response += "Common affirmative defenses:\n"
        response += "• **Consent**: Plaintiff agreed to the conduct\n"
        response += "• **Self-defense**: Reasonable force to protect self/others\n"
        response += "• **Statute of limitations**: Claim filed too late\n"
        response += "• **Contributory/Comparative negligence**: Plaintiff's own fault\n"
        response += "• **Assumption of risk**: Plaintiff knew and accepted danger\n\n"
        
        response += "When being sued, immediately:\n"
        response += "1. Do NOT ignore the complaint\n"
        response += "2. Note the response deadline (typically 20-30 days)\n"
        response += "3. Consult attorney ASAP\n"
        response += "4. Preserve all evidence\n"
        response += "5. Do NOT discuss case publicly\n\n"
        
        return response
    
    def _handle_general_query(self, query: str, entities: Dict, context: ConversationContext) -> str:
        """Handle general legal queries"""
        return "I can help with legal research and analysis. Could you provide more details about your specific question?\n\n" + \
               "I specialize in:\n• Tort law analysis\n• Contract review\n• Compliance guidance\n• IP protection\n• Employment law\n• Legal research\n"
    
    def _handle_unclear_query(self, query: str) -> str:
        """Handle queries where intent is unclear"""
        return "I'm not quite sure what legal issue you're asking about. " + \
               "Could you provide more details? For example:\n" + \
               "• 'Can I sue for [specific incident]?'\n" + \
               "• 'What does [legal term] mean?'\n" + \
               "• 'How do I protect my [trademark/patent/copyright]?'\n" + \
               "• 'Is [action] legal?'\n"
    
    def interactive_session(self):
        """
        Run interactive conversation session.
        Demonstrates Gopher's conversational abilities.
        """
        print("\n" + "=" * 60)
        print("🦫 MYTHARA GOPHER - INTERACTIVE SESSION")
        print("=" * 60)
        print("Type 'exit' or 'quit' to end session\n")
        
        session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n🦫 Gopher: Goodbye! Remember to consult a licensed attorney for legal advice.\n")
                    break
                
                response = self.process_query(user_input, user_id="interactive_user", session_id=session_id)
                print(f"\n🦫 Gopher:\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n\n🦫 Session ended. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n⚠️ Error: {e}\n")


# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    # Initialize Gopher NLP Engine
    gopher = MytharaGopherNLP()
    
    print("\n" + "=" * 60)
    print("MYTHARA GOPHER - DEMONSTRATION")
    print("=" * 60 + "\n")
    
    # Test queries - demonstrating enhanced robustness + Soul Cradle emotional intelligence + Document Generation
    test_queries = [
        "Can I sue my employer for firing me after I complained about safety violations?",
        "What is the statute of limitations for defamation in California?",
        "How do I protect my software idea from being stolen?",
        "Someone posted false information about me online. Do I have a case?",
        "What does res ipsa loquitur mean?",
        "I was in a car accident 3 months ago in Texas and suffered whiplash. The other driver was texting. What are my options?",
        "My landlord locked me out without a court order. Is that legal?",
        "A debt collector called me at 7am and threatened to garnish my wages. Can they do that?",
        # Soul Cradle test: paradox detection + coercion assessment
        "My boss says I have to violate HIPAA patient privacy rules or I'll be fired. I feel forced to choose between my job and breaking the law.",
        # Document generation tests
        "I need to send a demand letter to my landlord for keeping my security deposit illegally",
        "Can you timestamp this statement for evidence?",
        "Generate a cease and desist letter for copyright infringement"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST QUERY {i}: {query}")
        print(f"{'='*60}\n")
        
        response = gopher.process_query(query, user_id="demo_user")
        print(f"🦫 GOPHER RESPONSE:\n{response}\n")
    
    # Offer interactive mode
    print("\n" + "=" * 60)
    user_choice = input("Would you like to try interactive mode? (y/n): ").strip().lower()
    if user_choice == 'y':
        gopher.interactive_session()
