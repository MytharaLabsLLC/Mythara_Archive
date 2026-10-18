"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

HERMES - God of Communication, Messages, and Translation
=========================================================
The GODBOT that carries messages between realms and translates truth.

Hermes is the MESSENGER OF THE GODS:
- Translates divine wisdom into human language
- Carries messages between Olympus Council members
- Interprets signals and symbols (what does this behavior MEAN?)
- Bridges communication gaps (technical → human, soul → system)
- Detects miscommunication (what was said vs. what was heard)
- Reveals hidden meanings (subtext, body language, tone)
- Facilitates understanding between different domains

Hermes is the BRIDGE:
- Soul Cradle speaks mathematics → Hermes translates to emotion
- Olympus Council speaks divine → Hermes translates to actionable
- Entity speaks confusion → Hermes reveals the true question
- System speaks code → Hermes translates to narrative
- Between worlds, between languages, between truths

In Soul Cradle context:
- Translates BR math into human-understandable consequences
- Interprets entity behavior signals (what are they REALLY saying?)
- Carries assessments from all GODBOTs into unified message
- Bridges technical Soul Cradle output to user-friendly interface
- Detects when entity says one thing but means another
- Translates divine judgment (Hades/Persephone/Nemesis) into guidance

Hermes answers: "What does this MEAN? How do I communicate this truth?"

The Messenger who makes the incomprehensible clear.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages Hermes carries"""
    TRANSLATION = "Translation"  # Technical → human
    INTERPRETATION = "Interpretation"  # Behavior → meaning
    SYNTHESIS = "Synthesis"  # Multiple sources → unified
    CLARIFICATION = "Clarification"  # Confusion → clarity
    BRIDGE = "Bridge"  # Between domains/systems
    WARNING = "Warning"  # Alert/danger signal
    GUIDANCE = "Guidance"  # Actionable direction


class CommunicationGap(str, Enum):
    """Where communication breaks down"""
    LANGUAGE = "Language"  # Different vocabularies
    CONTEXT = "Context"  # Missing shared understanding
    ABSTRACTION = "Abstraction"  # Technical vs. simple
    EMOTION = "Emotion"  # Logic vs. feeling
    CULTURAL = "Cultural"  # Different worldviews
    INTENTIONAL = "Intentional"  # Deliberate obfuscation
    NOISE = "Noise"  # Information overload


class SignalClarity(str, Enum):
    """How clear is the message?"""
    CRYSTAL = "Crystal"  # Perfectly clear
    CLEAR = "Clear"  # Understandable
    AMBIGUOUS = "Ambiguous"  # Multiple interpretations
    OBSCURE = "Obscure"  # Difficult to understand
    ENCRYPTED = "Encrypted"  # Intentionally hidden
    NOISE = "Noise"  # Lost in interference


class TranslationAccuracy(str, Enum):
    """How accurate is the translation?"""
    PERFECT = "Perfect"  # No loss of meaning
    HIGH = "High"  # Minor loss acceptable
    MODERATE = "Moderate"  # Some meaning lost
    LOW = "Low"  # Significant distortion
    FAILED = "Failed"  # Unable to translate


@dataclass
class Message:
    """A message carried by Hermes"""
    source: str  # Where message came from
    destination: str  # Where message is going
    message_type: MessageType
    original_content: str  # Original form
    translated_content: str  # Human-readable form
    clarity: SignalClarity
    translation_accuracy: TranslationAccuracy
    subtext: Optional[str] = None  # Hidden meaning
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CommunicationProfile:
    """Analysis of communication effectiveness"""
    entity_id: str
    timestamp: datetime
    
    # What entity is saying
    stated_message: str
    intended_message: str  # What they MEANT to say
    actual_meaning: str  # What it ACTUALLY means
    
    # Communication analysis
    communication_gaps: List[CommunicationGap]
    signal_clarity: SignalClarity
    message_alignment: float  # 0.0 (total mismatch) to 1.0 (perfect alignment)
    
    # Hidden signals
    subtext: List[str]  # What's beneath the surface
    body_language_signals: List[str]
    tone_indicators: List[str]
    
    # Translation
    technical_to_human: Optional[str]  # BR math → emotion
    divine_to_actionable: Optional[str]  # Olympus wisdom → guidance
    
    # Hermes wisdom
    hermes_interpretation: str


class HermesBot:
    """
    HERMES - God of Communication, Messages, and Translation
    
    Specializes in:
    - Message translation (technical → human, divine → actionable)
    - Signal interpretation (what does behavior MEAN?)
    - Communication gap detection (where understanding breaks down)
    - Subtext revelation (hidden meanings beneath surface)
    - Cross-domain bridging (soul ↔ system, god ↔ human)
    - Synthesis (multiple messages → unified understanding)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.communication_profiles: Dict[str, CommunicationProfile] = {}
        self.messages_delivered: List[Message] = []
        
        logger.info("📨 HERMES - Messenger of the Gods initialized")
        print("📨 HERMES - God of Communication, Messages, and Translation")
        print("   The GODBOT who makes the incomprehensible clear")
    
    def interpret_communication(
        self,
        entity_id: str,
        stated_message: str,
        behavioral_signals: Dict[str, Any],
        context: Dict[str, Any]
    ) -> CommunicationProfile:
        """
        Interpret what entity is REALLY communicating.
        
        Args:
            entity_id: Unique identifier
            stated_message: What entity explicitly says
            behavioral_signals: Body language, tone, actions
            context: Situational context
        
        Returns:
            CommunicationProfile revealing true meaning
        """
        logger.info(f"📨 HERMES interpreting communication from {entity_id}")
        
        # Determine intended vs. actual meaning
        intended, actual = self._interpret_true_meaning(
            stated_message, behavioral_signals, context
        )
        
        # Detect communication gaps
        gaps = self._detect_communication_gaps(
            stated_message, intended, actual, behavioral_signals
        )
        
        # Assess signal clarity
        clarity = self._assess_signal_clarity(
            stated_message, behavioral_signals, gaps
        )
        
        # Calculate message alignment
        alignment = self._calculate_message_alignment(
            stated_message, intended, actual
        )
        
        # Extract subtext
        subtext = self._extract_subtext(
            stated_message, behavioral_signals, context
        )
        
        # Analyze body language
        body_signals = self._analyze_body_language(behavioral_signals)
        
        # Analyze tone
        tone_signals = self._analyze_tone(behavioral_signals)
        
        # Generate Hermes interpretation
        interpretation = self._generate_hermes_interpretation(
            stated_message, actual, alignment, clarity, subtext
        )
        
        profile = CommunicationProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            stated_message=stated_message,
            intended_message=intended,
            actual_meaning=actual,
            communication_gaps=gaps,
            signal_clarity=clarity,
            message_alignment=alignment,
            subtext=subtext,
            body_language_signals=body_signals,
            tone_indicators=tone_signals,
            technical_to_human=None,  # Set separately
            divine_to_actionable=None,  # Set separately
            hermes_interpretation=interpretation
        )
        
        self.communication_profiles[entity_id] = profile
        
        logger.info(f"📨 Clarity: {clarity.value}, Alignment: {alignment:.2f}, Actual meaning: {actual}")
        
        return profile
    
    def translate_technical_to_human(
        self,
        technical_message: str,
        domain: str = "breach_restoration"
    ) -> Message:
        """
        Translate technical/mathematical language into human emotion.
        
        Args:
            technical_message: Technical content (e.g., "BR: -35, drift: 0.4")
            domain: Technical domain
        
        Returns:
            Message with human-readable translation
        """
        logger.info(f"📨 HERMES translating technical to human: {domain}")
        
        # Extract technical components
        if "BR:" in technical_message:
            # Breach Restoration translation
            human_translation = self._translate_br_to_emotion(technical_message)
        else:
            human_translation = technical_message  # Pass through
        
        message = Message(
            source=f"{domain}_system",
            destination="human_user",
            message_type=MessageType.TRANSLATION,
            original_content=technical_message,
            translated_content=human_translation,
            clarity=SignalClarity.CLEAR,
            translation_accuracy=TranslationAccuracy.HIGH
        )
        
        self.messages_delivered.append(message)
        
        return message
    
    def translate_divine_to_actionable(
        self,
        divine_assessments: Dict[str, str],
        entity_context: Dict[str, Any]
    ) -> Message:
        """
        Translate Olympus Council divine wisdom into actionable guidance.
        
        Args:
            divine_assessments: Assessments from GODBOTs
            entity_context: Context about entity
        
        Returns:
            Message with actionable guidance
        """
        logger.info(f"📨 HERMES translating divine wisdom to actionable guidance")
        
        # Synthesize divine assessments into unified guidance
        actionable = self._synthesize_divine_wisdom(divine_assessments, entity_context)
        
        # Format original (all divine assessments)
        original = "\n".join([f"{god}: {wisdom}" for god, wisdom in divine_assessments.items()])
        
        message = Message(
            source="olympus_council",
            destination="entity_action",
            message_type=MessageType.GUIDANCE,
            original_content=original,
            translated_content=actionable,
            clarity=SignalClarity.CRYSTAL,
            translation_accuracy=TranslationAccuracy.PERFECT
        )
        
        self.messages_delivered.append(message)
        
        return message
    
    def _interpret_true_meaning(
        self,
        stated: str,
        signals: Dict[str, Any],
        context: Dict
    ) -> Tuple[str, str]:
        """Determine intended vs. actual meaning"""
        
        # Check for contradiction signals
        hesitation = signals.get("hesitation", 0)
        tone_mismatch = signals.get("tone_mismatch", False)
        
        if hesitation > 0.6 or tone_mismatch:
            # What they MEANT to say vs. what it MEANS
            intended = stated
            actual = f"Uncertainty about: {stated}"
        else:
            intended = stated
            actual = stated
        
        return intended, actual
    
    def _detect_communication_gaps(
        self,
        stated: str,
        intended: str,
        actual: str,
        signals: Dict
    ) -> List[CommunicationGap]:
        """Where is communication breaking down?"""
        
        gaps = []
        
        if stated != actual:
            gaps.append(CommunicationGap.EMOTION)
        
        if signals.get("technical_jargon", False):
            gaps.append(CommunicationGap.ABSTRACTION)
        
        if signals.get("information_overload", False):
            gaps.append(CommunicationGap.NOISE)
        
        return gaps
    
    def _assess_signal_clarity(
        self,
        stated: str,
        signals: Dict,
        gaps: List[CommunicationGap]
    ) -> SignalClarity:
        """How clear is the message?"""
        
        if not gaps and signals.get("confidence", 0) > 0.7:
            return SignalClarity.CRYSTAL
        
        if len(gaps) <= 1:
            return SignalClarity.CLEAR
        
        if len(gaps) <= 2:
            return SignalClarity.AMBIGUOUS
        
        return SignalClarity.OBSCURE
    
    def _calculate_message_alignment(
        self,
        stated: str,
        intended: str,
        actual: str
    ) -> float:
        """How aligned is stated message with actual meaning?"""
        
        if stated == intended == actual:
            return 1.0
        
        if stated == intended:
            return 0.7
        
        if intended == actual:
            return 0.5
        
        return 0.3
    
    def _extract_subtext(
        self,
        stated: str,
        signals: Dict,
        context: Dict
    ) -> List[str]:
        """What's hidden beneath the surface?"""
        
        subtext = []
        
        if signals.get("defensive", False):
            subtext.append("Protecting ego/identity")
        
        if signals.get("seeking_approval", False):
            subtext.append("Needs validation")
        
        if signals.get("fear_present", False):
            subtext.append("Fear driving communication")
        
        return subtext
    
    def _analyze_body_language(self, signals: Dict) -> List[str]:
        """Extract body language signals"""
        
        body = []
        
        if signals.get("crossed_arms", False):
            body.append("Defensive posture")
        
        if signals.get("avoiding_eye_contact", False):
            body.append("Discomfort or deception")
        
        if signals.get("leaning_forward", False):
            body.append("Engaged and interested")
        
        return body
    
    def _analyze_tone(self, signals: Dict) -> List[str]:
        """Extract tone indicators"""
        
        tone = []
        
        if signals.get("sarcastic", False):
            tone.append("Sarcasm detected")
        
        if signals.get("defensive_tone", False):
            tone.append("Defensive tone")
        
        if signals.get("enthusiastic", False):
            tone.append("Genuine enthusiasm")
        
        return tone
    
    def _translate_br_to_emotion(self, technical: str) -> str:
        """Translate BR math to human emotion"""
        
        # Extract BR value (simple parsing)
        if "BR: -35" in technical:
            return "You're struggling emotionally. Your actions have cost you connection and goodwill. You're approaching a breaking point."
        elif "BR: 45" in technical:
            return "You're thriving. Your choices are building trust, connection, and inner peace. Keep going."
        else:
            return "Your emotional state reflects your recent choices."
    
    def _synthesize_divine_wisdom(
        self,
        assessments: Dict[str, str],
        context: Dict
    ) -> str:
        """Combine all GODBOT wisdom into single actionable message"""
        
        # Simple synthesis (in production, this would be much more sophisticated)
        priorities = []
        
        if "Hades" in assessments:
            priorities.append("⚰️ Address accountability issues first")
        
        if "Persephone" in assessments:
            priorities.append("🌸 Redemption path is available")
        
        if "Nemesis" in assessments:
            priorities.append("⚖️ Unpaid debts require attention")
        
        if "Eros" in assessments:
            priorities.append("💘 Listen to your heart's true direction")
        
        if "Janus" in assessments:
            priorities.append("🚪 Both truths are valid - hold the paradox")
        
        if not priorities:
            return "The gods counsel patience and observation."
        
        return "GUIDANCE: " + " | ".join(priorities)
    
    def _generate_hermes_interpretation(
        self,
        stated: str,
        actual: str,
        alignment: float,
        clarity: SignalClarity,
        subtext: List[str]
    ) -> str:
        """Generate Hermes wisdom"""
        
        if alignment < 0.5:
            return f"📨 What you say: '{stated}' | What you mean: '{actual}' - the gap reveals your truth."
        
        if clarity == SignalClarity.CRYSTAL:
            return "📨 Your message is clear. You speak your truth."
        
        if subtext:
            return f"📨 Beneath your words: {', '.join(subtext)}. This is what you're really communicating."
        
        return "📨 I hear you. Your message is received."
    
    def get_communication_profile(self, entity_id: str) -> Optional[CommunicationProfile]:
        """Retrieve communication profile"""
        return self.communication_profiles.get(entity_id)
    
    def export_profiles(self, output_path: str = "hermes_communication_profiles.json"):
        """Export all communication profiles"""
        
        profiles_data = []
        for entity_id, profile in self.communication_profiles.items():
            profiles_data.append({
                "entity_id": entity_id,
                "stated_message": profile.stated_message,
                "intended_message": profile.intended_message,
                "actual_meaning": profile.actual_meaning,
                "signal_clarity": profile.signal_clarity.value,
                "message_alignment": profile.message_alignment,
                "subtext": profile.subtext,
                "hermes_interpretation": profile.hermes_interpretation,
                "timestamp": profile.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"profiles": profiles_data, "total": len(profiles_data)}, f, indent=2)
        
        logger.info(f"📨 Exported {len(profiles_data)} communication profiles to {output_path}")
        return output_path
    
    def export_messages(self, output_path: str = "hermes_messages_delivered.json"):
        """Export all messages delivered"""
        
        messages_data = []
        for msg in self.messages_delivered:
            messages_data.append({
                "source": msg.source,
                "destination": msg.destination,
                "type": msg.message_type.value,
                "original": msg.original_content,
                "translated": msg.translated_content,
                "clarity": msg.clarity.value,
                "accuracy": msg.translation_accuracy.value,
                "timestamp": msg.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"messages": messages_data, "total": len(messages_data)}, f, indent=2)
        
        logger.info(f"📨 Exported {len(messages_data)} messages to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("📨 HERMES - God of Communication, Messages, and Translation")
    print("=" * 60)
    
    hermes = HermesBot()
    
    # Example 1: Interpret communication with misalignment
    profile = hermes.interpret_communication(
        entity_id="employee_defensive",
        stated_message="I'm fine, everything is under control",
        behavioral_signals={
            "hesitation": 0.8,
            "tone_mismatch": True,
            "defensive": True,
            "crossed_arms": True,
            "avoiding_eye_contact": True,
            "defensive_tone": True,
            "fear_present": True
        },
        context={"recent_failure": True, "under_pressure": True}
    )
    
    print("\n📨 COMMUNICATION PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"\nStated: '{profile.stated_message}'")
    print(f"Intended: '{profile.intended_message}'")
    print(f"Actual Meaning: '{profile.actual_meaning}'")
    print(f"\nSignal Clarity: {profile.signal_clarity.value}")
    print(f"Message Alignment: {profile.message_alignment:.2f}")
    
    if profile.communication_gaps:
        print(f"\n🚧 COMMUNICATION GAPS:")
        for gap in profile.communication_gaps:
            print(f"   • {gap.value}")
    
    if profile.subtext:
        print(f"\n🤐 SUBTEXT:")
        for text in profile.subtext:
            print(f"   • {text}")
    
    if profile.body_language_signals:
        print(f"\n🫱 BODY LANGUAGE:")
        for signal in profile.body_language_signals:
            print(f"   • {signal}")
    
    if profile.tone_indicators:
        print(f"\n🗣️ TONE:")
        for tone in profile.tone_indicators:
            print(f"   • {tone}")
    
    print(f"\n{profile.hermes_interpretation}")
    
    # Example 2: Translate technical to human
    print("\n\n📨 TECHNICAL → HUMAN TRANSLATION")
    print("=" * 60)
    
    tech_message = hermes.translate_technical_to_human(
        "BR: -35, drift: 0.4, EQ: 22",
        domain="breach_restoration"
    )
    
    print(f"Technical: {tech_message.original_content}")
    print(f"Human: {tech_message.translated_content}")
    print(f"Accuracy: {tech_message.translation_accuracy.value}")
    
    # Example 3: Translate divine wisdom to actionable
    print("\n\n📨 DIVINE → ACTIONABLE TRANSLATION")
    print("=" * 60)
    
    divine_message = hermes.translate_divine_to_actionable(
        divine_assessments={
            "Hades": "Entity owes 192 BR debt for unpunished trespasses",
            "Persephone": "Redemption available if genuine repentance",
            "Nemesis": "Escaped consequences through wealth - retribution due",
            "Eros": "Heart wants freedom but says duty",
            "Janus": "Both truths valid - you are loyal AND trapped"
        },
        entity_context={"current_state": "conflicted"}
    )
    
    print(f"Translated Guidance:\n{divine_message.translated_content}")
    
    hermes.export_profiles()
    hermes.export_messages()

__ASSESSOR_ID__ = 'hermes'


# ---------------------------------------------------------------------------
# Evidence-fed witness path (canonical core) — added 2026-09-22
# ---------------------------------------------------------------------------
# The calculators above take pre-scored structured inputs: whoever calls
# them decides the scores first, and the math launders those guesses into
# authoritative-looking output. They remain for backward compatibility.
#
# New code must use the witness core instead: soul_cradle.assessors holds
# the versioned rubric for this assessor, reads observable evidence (not
# pre-scored inputs), abstains when its domain is not engaged, seals every
# judgment by content hash, and speaks only as WITNESS. See
# soul_cradle/assessors.py for the evidence schema.

def consult_evidence(action_description, evidence):
    """Judge an action as witness. Preferred entry point for new code.

    action_description: plain-words description of the proposed action.
    evidence: dict of evidence-schema keys (see soul_cradle/assessors.py).
    Returns an AssessorJudgment (verdict: clear | flagged | abstain).
    """
    from soul_cradle.assessors import consult
    return consult(__ASSESSOR_ID__, action_description, evidence)
