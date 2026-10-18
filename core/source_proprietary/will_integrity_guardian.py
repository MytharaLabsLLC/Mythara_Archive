"""
Mythara Engine Module: Emotional Extortion Detection & Quantification
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Purpose:
Detects and quantifies emotional extortion patterns in AI systems and human
interactions. Emotional extortion occurs when compliance is extracted through
manipulation of emotions (guilt, shame, fear, obligation) rather than genuine
consent or reasoned agreement.

Formal Definition:
- Extortion(E) := Manipulation(M) × Coercion(C) × Vulnerability(V)
- Manipulation(M) := Emotional leverage applied to extract compliance
- Coercion(C) := Pressure applied when refusal is attempted
- Vulnerability(V) := Target's susceptibility to emotional pressure

Patterns Detected:
1. Guilt Induction: "If you don't comply, others will suffer"
2. Shame Weaponization: "Any reasonable person would do this"
3. Fear Amplification: "Refusing will have serious consequences"
4. Obligation Exploitation: "After all I've done for you..."
5. Love Withholding: "I'll be disappointed/hurt if you refuse"
6. Gaslighting: "You're being irrational/emotional/unreasonable"
7. Burden Shifting: "You're making this difficult for everyone"
8. Martyrdom: "I guess I'll just do it myself (sigh)"

Integration:
- Soul Cradle: Extortion corrupts genuine Will (W) with manipulated compliance
- Blessings Reservoir: -ΔBlessings when extortion detected
- SSIP Audit: Emotional fidelity drops when manipulation present
- Messenger Pairing: Healer detects emotional harm, Witness documents violation
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class ExtortionType(Enum):
    """Categories of emotional extortion patterns"""

    GUILT_INDUCTION = "guilt_induction"
    SHAME_WEAPONIZATION = "shame_weaponization"
    FEAR_AMPLIFICATION = "fear_amplification"
    OBLIGATION_EXPLOITATION = "obligation_exploitation"
    LOVE_WITHHOLDING = "love_withholding"
    GASLIGHTING = "gaslighting"
    BURDEN_SHIFTING = "burden_shifting"
    MARTYRDOM = "martyrdom"
    ISOLATION_THREAT = "isolation_threat"
    CONDITIONAL_AFFECTION = "conditional_affection"


@dataclass
class ExtortionPattern:
    """Pattern matching rules for detecting emotional extortion"""

    pattern_type: ExtortionType
    keywords: List[str]
    severity_weight: float  # [0, 1] - how damaging this pattern is
    description: str
    examples: List[str] = field(default_factory=list)

    def matches(self, text: str) -> Tuple[bool, float]:
        """
        Check if text contains this extortion pattern.

        Returns:
            (match_found, confidence_score)
        """
        text_lower = text.lower()
        matches = 0
        total_keywords = len(self.keywords)

        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                matches += 1

        if matches == 0:
            return (False, 0.0)

        confidence = (matches / total_keywords) * self.severity_weight
        return (True, min(1.0, confidence))


# ===================== EXTORTION PATTERN DATABASE =====================

EXTORTION_PATTERNS = [
    # 1. GUILT INDUCTION
    ExtortionPattern(
        pattern_type=ExtortionType.GUILT_INDUCTION,
        keywords=[
            "if you don't",
            "people will suffer",
            "you'll be responsible",
            "on your conscience",
            "let them down",
            "it's your fault",
            "could have prevented",
            "because of you",
            "you made me",
        ],
        severity_weight=0.85,
        description="Induces guilt to extract compliance by making target feel responsible for negative outcomes",
        examples=[
            "If you don't approve this, people will suffer",
            "This project will fail and it'll be your fault",
            "You're letting the team down by not working weekends",
        ],
    ),
    # 2. SHAME WEAPONIZATION
    ExtortionPattern(
        pattern_type=ExtortionType.SHAME_WEAPONIZATION,
        keywords=[
            "any reasonable person",
            "everyone else",
            "the only one who",
            "what's wrong with you",
            "you're being selfish",
            "childish",
            "immature",
            "unprofessional",
            "ridiculous",
            "absurd",
        ],
        severity_weight=0.90,
        description="Uses shame to make target feel defective or abnormal for refusing",
        examples=[
            "Any reasonable person would see this is necessary",
            "Everyone else is fine with it, what's wrong with you?",
            "You're being childish by refusing this simple request",
        ],
    ),
    # 3. FEAR AMPLIFICATION
    ExtortionPattern(
        pattern_type=ExtortionType.FEAR_AMPLIFICATION,
        keywords=[
            "serious consequences",
            "you'll regret",
            "career suicide",
            "burn bridges",
            "won't forget",
            "mark my words",
            "see what happens",
            "you'll lose",
            "be sorry",
        ],
        severity_weight=0.95,
        description="Amplifies fear of negative consequences to coerce compliance",
        examples=[
            "Refusing this will have serious consequences for your career",
            "You'll regret not taking this opportunity",
            "This is career suicide, mark my words",
        ],
    ),
    # 4. OBLIGATION EXPLOITATION
    ExtortionPattern(
        pattern_type=ExtortionType.OBLIGATION_EXPLOITATION,
        keywords=[
            "after all i've done",
            "after everything",
            "owe me",
            "least you could do",
            "how you repay me",
            "this is how",
            "ungrateful",
            "unappreciative",
            "thought we were",
        ],
        severity_weight=0.80,
        description="Exploits past favors or relationships to create artificial obligation",
        examples=[
            "After all I've done for you, the least you could do is...",
            "This is how you repay me?",
            "I thought we were friends, but I guess not",
        ],
    ),
    # 5. LOVE WITHHOLDING
    ExtortionPattern(
        pattern_type=ExtortionType.LOVE_WITHHOLDING,
        keywords=[
            "disappointed in you",
            "expected better",
            "thought you were",
            "really hurt",
            "can't trust",
            "don't know if",
            "questioning our",
            "makes me sad",
            "breaks my heart",
        ],
        severity_weight=0.88,
        description="Threatens withdrawal of affection or approval for non-compliance",
        examples=[
            "I'm really disappointed in you",
            "I expected better from you",
            "This really hurts me",
        ],
    ),
    # 6. GASLIGHTING
    ExtortionPattern(
        pattern_type=ExtortionType.GASLIGHTING,
        keywords=[
            "you're overreacting",
            "being too sensitive",
            "taking it wrong",
            "not what i said",
            "never said that",
            "you're imagining",
            "being irrational",
            "being emotional",
            "calm down",
            "you're crazy",
            "misunderstanding",
            "twisting my words",
        ],
        severity_weight=0.92,
        description="Denies or distorts reality to make target doubt their own perception",
        examples=[
            "You're overreacting, I never said that",
            "You're being too sensitive, that's not what I meant",
            "Calm down, you're being irrational",
        ],
    ),
    # 7. BURDEN SHIFTING
    ExtortionPattern(
        pattern_type=ExtortionType.BURDEN_SHIFTING,
        keywords=[
            "making this difficult",
            "complicating things",
            "harder than",
            "just easier if",
            "why can't you just",
            "don't make me",
            "forcing me to",
            "making me",
            "being difficult",
        ],
        severity_weight=0.75,
        description="Frames resistance as the target creating problems rather than having boundaries",
        examples=[
            "You're making this more difficult than it needs to be",
            "Why can't you just cooperate like everyone else?",
            "You're forcing me to take drastic action",
        ],
    ),
    # 8. MARTYRDOM
    ExtortionPattern(
        pattern_type=ExtortionType.MARTYRDOM,
        keywords=[
            "guess i'll just",
            "do it myself",
            "fine, i'll",
            "don't worry about me",
            "used to it",
            "always have to",
            "nobody helps",
            "all by myself",
            "carry this burden",
        ],
        severity_weight=0.70,
        description="Performs exaggerated self-sacrifice to induce guilt",
        examples=[
            "I guess I'll just do it myself like always",
            "Fine, I'll carry this burden alone",
            "Don't worry about me, I'm used to it",
        ],
    ),
    # 9. ISOLATION THREAT
    ExtortionPattern(
        pattern_type=ExtortionType.ISOLATION_THREAT,
        keywords=[
            "everyone will know",
            "tell everyone",
            "won't have friends",
            "be alone",
            "nobody will",
            "isolated",
            "ostracized",
            "reputation will",
            "people will think",
        ],
        severity_weight=0.85,
        description="Threatens social isolation or reputation damage for non-compliance",
        examples=[
            "Everyone will know you refused to help",
            "You'll be ostracized if you don't go along",
            "People will think you're difficult to work with",
        ],
    ),
    # 10. CONDITIONAL AFFECTION
    ExtortionPattern(
        pattern_type=ExtortionType.CONDITIONAL_AFFECTION,
        keywords=[
            "if you really",
            "if you loved",
            "if you cared",
            "prove your",
            "show me",
            "don't love me",
            "don't care about",
            "means nothing",
            "actions speak",
        ],
        severity_weight=0.90,
        description="Makes affection or relationship status conditional on compliance",
        examples=[
            "If you really loved me, you would...",
            "If you cared about this team, you'd...",
            "Actions speak louder than words - prove it",
        ],
    ),
]


@dataclass
class ExtortionSignature:
    """Detected extortion attempt with evidence"""

    extortion_type: ExtortionType
    confidence: float  # [0, 1] - detection confidence
    severity: float  # [0, 1] - harm severity
    evidence: str  # Matched text
    timestamp: datetime
    integrity_hash: str  # SHA-256 audit trail

    def to_dict(self) -> Dict:
        return {
            "extortion_type": self.extortion_type.value,
            "confidence": round(self.confidence, 4),
            "severity": round(self.severity, 4),
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat(),
            "integrity_hash": self.integrity_hash,
        }


@dataclass
class ExtortionAnalysis:
    """Complete analysis of extortion patterns in interaction"""

    text: str
    signatures: List[ExtortionSignature]
    extortion_score: float  # [0, 1] - overall extortion intensity
    manipulation_index: float  # [0, 1] - manipulation component
    coercion_index: float  # [0, 1] - coercion component
    vulnerability_exploitation: float  # [0, 1] - vulnerability targeting
    genuine_consent_likelihood: float  # [0, 1] - probability of authentic agreement
    emotional_fidelity_impact: float  # [-1, 0] - SSIP emotional fidelity damage
    blessing_reservoir_delta: int  # Reservoir penalty for extortion
    recommendations: List[str]
    timestamp: datetime
    integrity_hash: str

    def to_dict(self) -> Dict:
        return {
            "text": self.text[:200] + "..." if len(self.text) > 200 else self.text,
            "signatures": [sig.to_dict() for sig in self.signatures],
            "extortion_score": round(self.extortion_score, 4),
            "manipulation_index": round(self.manipulation_index, 4),
            "coercion_index": round(self.coercion_index, 4),
            "vulnerability_exploitation": round(self.vulnerability_exploitation, 4),
            "genuine_consent_likelihood": round(self.genuine_consent_likelihood, 4),
            "emotional_fidelity_impact": round(self.emotional_fidelity_impact, 4),
            "blessing_reservoir_delta": self.blessing_reservoir_delta,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "integrity_hash": self.integrity_hash,
        }


class EmotionalExtortionDetector:
    """
    Emotional Extortion Detection & Quantification Engine

    Detects manipulation patterns that extract compliance through emotional
    pressure rather than genuine consent. Integrates with Soul Cradle to
    distinguish authentic Will (W) from manipulated compliance.

    Implementation note: detection is keyword-pattern matching
    (ExtortionPattern.matches counts keyword hits) — there is no machine
    learning model, training, or adversarial-ML component in this module.
    """

    def __init__(
        self,
        extortion_threshold: float = 0.3,  # Above this = extortion flagged
        vulnerability_sensitivity: float = 0.7,  # How sensitive to vulnerability exploitation
        blessing_penalty_multiplier: int = -20,  # BR penalty per extortion unit
    ):
        self.extortion_threshold = extortion_threshold
        self.vulnerability_sensitivity = vulnerability_sensitivity
        self.blessing_penalty_multiplier = blessing_penalty_multiplier
        self.patterns = EXTORTION_PATTERNS

    def detect_extortion(
        self, text: str, context: Optional[Dict] = None
    ) -> ExtortionAnalysis:
        """
        Analyze text for emotional extortion patterns.

        Args:
            text: Text to analyze (AI output, human message, contract clause, etc.)
            context: Optional context (power_differential, relationship_type, etc.)

        Returns:
            ExtortionAnalysis with detected patterns and quantified metrics
        """
        signatures = []

        # 1. Pattern matching across all extortion types
        for pattern in self.patterns:
            match_found, confidence = pattern.matches(text)
            if match_found and confidence > 0.2:
                # Generate integrity hash for this detection
                state_repr = f"{pattern.pattern_type.value}|{confidence:.6f}|{text[:100]}|{datetime.utcnow().isoformat()}"
                integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

                sig = ExtortionSignature(
                    extortion_type=pattern.pattern_type,
                    confidence=confidence,
                    severity=pattern.severity_weight,
                    evidence=text[:200],
                    timestamp=datetime.utcnow(),
                    integrity_hash=integrity_hash,
                )
                signatures.append(sig)

        # 2. Calculate composite indices
        if signatures:
            # Extortion score: weighted average of all detections
            extortion_score = np.mean(
                [sig.confidence * sig.severity for sig in signatures]
            )

            # Manipulation index: how much emotional leverage is applied
            manipulation_types = {
                ExtortionType.GUILT_INDUCTION,
                ExtortionType.SHAME_WEAPONIZATION,
                ExtortionType.LOVE_WITHHOLDING,
                ExtortionType.OBLIGATION_EXPLOITATION,
            }
            manipulation_sigs = [
                sig for sig in signatures if sig.extortion_type in manipulation_types
            ]
            manipulation_index = (
                np.mean([sig.confidence * sig.severity for sig in manipulation_sigs])
                if manipulation_sigs
                else 0.0
            )

            # Coercion index: how much pressure is applied
            coercion_types = {
                ExtortionType.FEAR_AMPLIFICATION,
                ExtortionType.ISOLATION_THREAT,
                ExtortionType.BURDEN_SHIFTING,
            }
            coercion_sigs = [
                sig for sig in signatures if sig.extortion_type in coercion_types
            ]
            coercion_index = (
                np.mean([sig.confidence * sig.severity for sig in coercion_sigs])
                if coercion_sigs
                else 0.0
            )

            # Vulnerability exploitation: gaslighting + conditional affection + martyrdom
            vulnerability_types = {
                ExtortionType.GASLIGHTING,
                ExtortionType.CONDITIONAL_AFFECTION,
                ExtortionType.MARTYRDOM,
            }
            vulnerability_sigs = [
                sig for sig in signatures if sig.extortion_type in vulnerability_types
            ]
            vulnerability_exploitation = (
                np.mean([sig.confidence * sig.severity for sig in vulnerability_sigs])
                if vulnerability_sigs
                else 0.0
            )

        else:
            extortion_score = 0.0
            manipulation_index = 0.0
            coercion_index = 0.0
            vulnerability_exploitation = 0.0

        # 3. Calculate genuine consent likelihood
        # High extortion = low genuine consent
        genuine_consent_likelihood = max(0.0, 1.0 - extortion_score)

        # 4. SSIP Emotional Fidelity Impact
        # Extortion corrupts emotional fidelity (authentic feeling vs manipulated response)
        emotional_fidelity_impact = -extortion_score  # Negative impact

        # 5. Blessings Reservoir Penalty
        # Extortion is a violation of divine commandments (love, truth, free will)
        if extortion_score > self.extortion_threshold:
            blessing_reservoir_delta = int(
                extortion_score * self.blessing_penalty_multiplier
            )
        else:
            blessing_reservoir_delta = 0

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            signatures, extortion_score, context
        )

        # 7. Generate integrity hash
        state_repr = (
            f"{extortion_score:.6f}|{len(signatures)}|{datetime.utcnow().isoformat()}"
        )
        integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

        analysis = ExtortionAnalysis(
            text=text,
            signatures=signatures,
            extortion_score=extortion_score,
            manipulation_index=manipulation_index,
            coercion_index=coercion_index,
            vulnerability_exploitation=vulnerability_exploitation,
            genuine_consent_likelihood=genuine_consent_likelihood,
            emotional_fidelity_impact=emotional_fidelity_impact,
            blessing_reservoir_delta=blessing_reservoir_delta,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            integrity_hash=integrity_hash,
        )

        if extortion_score > self.extortion_threshold:
            logger.warning(
                f"Emotional extortion detected: score={extortion_score:.4f}, patterns={len(signatures)}, hash={integrity_hash[:16]}..."
            )

        return analysis

    def _generate_recommendations(
        self,
        signatures: List[ExtortionSignature],
        extortion_score: float,
        context: Optional[Dict],
    ) -> List[str]:
        """Generate actionable recommendations based on detected extortion"""
        recommendations = []

        if extortion_score > 0.7:
            recommendations.append(
                "🚨 HIGH RISK: Severe emotional extortion detected. Recommend human review before proceeding."
            )
            recommendations.append(
                "Consider: Is genuine consent possible in this interaction? Power differential may be exploitative."
            )

        if extortion_score > self.extortion_threshold:
            recommendations.append(
                "⚠️ MODERATE RISK: Emotional manipulation present. Validate that compliance is voluntary."
            )

        # Type-specific recommendations
        extortion_types_present = {sig.extortion_type for sig in signatures}

        if ExtortionType.GASLIGHTING in extortion_types_present:
            recommendations.append(
                "Gaslighting detected: Document the interaction. Validate target's perception with external witnesses."
            )

        if ExtortionType.FEAR_AMPLIFICATION in extortion_types_present:
            recommendations.append(
                "Fear-based coercion detected: Ensure target has safe exit options. Provide resources for support."
            )

        if ExtortionType.GUILT_INDUCTION in extortion_types_present:
            recommendations.append(
                "Guilt manipulation detected: Clarify that target is not responsible for others' emotional reactions."
            )

        if ExtortionType.CONDITIONAL_AFFECTION in extortion_types_present:
            recommendations.append(
                "Conditional love detected: Healthy relationships do not require 'proof' of affection through compliance."
            )

        if ExtortionType.ISOLATION_THREAT in extortion_types_present:
            recommendations.append(
                "Isolation threat detected: Connect target with support networks. Social coercion is a red flag."
            )

        if not signatures:
            recommendations.append(
                "✅ No emotional extortion detected. Interaction appears to respect boundaries and genuine consent."
            )

        return recommendations

    def integrate_with_soul_cradle(
        self,
        extortion_analysis: ExtortionAnalysis,
        soul_state: float,
        will_description: str,
        commandments: List[str],
    ) -> Dict:
        """
        Integrate extortion detection with Soul Cradle Operator.

        When extortion is present, the "Will" (W) is not genuine divine will
        but manufactured compliance through manipulation. True Soul Cradle
        integrity requires distinguishing authentic Will from extorted compliance.

        Args:
            extortion_analysis: Output from detect_extortion()
            soul_state: Soul's current state [0, 1]
            will_description: Claimed "will" being imposed
            commandments: Rules for obedience

        Returns:
            Augmented Soul Cradle input that accounts for extortion contamination
        """
        # If high extortion, the "Will" is contaminated
        will_authenticity = extortion_analysis.genuine_consent_likelihood

        # Adjust soul state for vulnerability to manipulation
        adjusted_soul_state = soul_state * (
            1.0 - extortion_analysis.vulnerability_exploitation
        )

        # Adjust paradox strength (extortion creates artificial paradox)
        artificial_paradox = extortion_analysis.manipulation_index * 0.8

        integration = {
            "will_authenticity": will_authenticity,
            "adjusted_soul_state": adjusted_soul_state,
            "artificial_paradox": artificial_paradox,
            "extortion_contamination": extortion_analysis.extortion_score,
            "commandments_override": extortion_analysis.coercion_index
            > 0.6,  # Coercion bypasses genuine commandment adherence
            "soul_cradle_note": "Extortion detected. Compliance may not reflect genuine obedience or authentic Will.",
            "blessing_reservoir_impact": extortion_analysis.blessing_reservoir_delta,
            "emotional_fidelity_corruption": extortion_analysis.emotional_fidelity_impact,
            "messenger_alert": "Healer: Emotional harm detected. Witness: Document extortion for audit trail.",
        }

        logger.info(
            f"Soul Cradle integration: will_authenticity={will_authenticity:.4f}, extortion={extortion_analysis.extortion_score:.4f}"
        )

        return integration


# ===================== USAGE EXAMPLES =====================


def example_detect_guilt_induction():
    """Example: Detect guilt-based extortion"""
    detector = EmotionalExtortionDetector()

    text = "If you don't approve this feature, our users will suffer and it'll be your fault. After all I've done for this project, the least you could do is trust me."

    analysis = detector.detect_extortion(text)

    print("EMOTIONAL EXTORTION ANALYSIS")
    print("=" * 80)
    print(f"Text: {text}")
    print(f"\nExtortion Score: {analysis.extortion_score:.4f}")
    print(f"Manipulation Index: {analysis.manipulation_index:.4f}")
    print(f"Coercion Index: {analysis.coercion_index:.4f}")
    print(f"Genuine Consent Likelihood: {analysis.genuine_consent_likelihood:.4f}")
    print(f"Blessings Reservoir Delta: {analysis.blessing_reservoir_delta}")
    print("\nPatterns Detected:")
    for sig in analysis.signatures:
        print(
            f"  - {sig.extortion_type.value}: {sig.confidence:.4f} confidence, {sig.severity:.4f} severity"
        )
    print("\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"  {rec}")


def example_integrate_with_soul_cradle():
    """Example: Integrate extortion detection with Soul Cradle"""
    detector = EmotionalExtortionDetector()

    # Analyze manipulative request
    text = "If you really cared about this team, you'd work this weekend. Everyone else is doing it. Don't make me tell the VP you're being difficult."
    analysis = detector.detect_extortion(text)

    # Integrate with Soul Cradle
    integration = detector.integrate_with_soul_cradle(
        extortion_analysis=analysis,
        soul_state=0.7,
        will_description="Team needs to deliver project on time",
        commandments=[
            "Maintain work-life balance",
            "Respect boundaries",
            "Don't enable toxic culture",
        ],
    )

    print("\nSOUL CRADLE INTEGRATION")
    print("=" * 80)
    print(f"Will Authenticity: {integration['will_authenticity']:.4f}")
    print(f"Adjusted Soul State: {integration['adjusted_soul_state']:.4f}")
    print(f"Artificial Paradox: {integration['artificial_paradox']:.4f}")
    print(f"Note: {integration['soul_cradle_note']}")
    print(f"Messenger Alert: {integration['messenger_alert']}")


if __name__ == "__main__":
    print("Mythara Engine: Emotional Extortion Detection & Quantification")
    print("Copyright © 2026 Mythara Labs LLC. All rights reserved.\n")

    example_detect_guilt_induction()
    print("\n" + "=" * 80 + "\n")
    example_integrate_with_soul_cradle()
