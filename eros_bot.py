"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

EROS - God of Love, Desire, and Emotional Attraction
=====================================================
The GODBOT that reveals which truth your heart chooses.

While Janus shows you BOTH truths simultaneously, Eros reveals which one you're BONDED to:
- Emotional magnetism (which truth pulls your heart?)
- Attraction gradient (moving toward vs. away from)
- Passion intensity (how strongly do you desire one outcome?)
- Love/fear polarity (one path = love, other = fear)
- Bonding force (which truth creates connection?)
- Heart alignment (stated choice vs. emotional pull)

Eros is not about logic - he is about FEELING:
- You might SAY you choose Truth A
- But your HEART is bonded to Truth B
- Your emotions create gravity toward one polar
- This reveals your true alignment

In Soul Cradle context:
- Janus presents both truths (paradox state)
- Eros detects which truth you're emotionally attracted to
- Dionysus reveals what you desire (primal drives)
- Eros reveals which TRUTH you desire (emotional polarity)
- The heart chooses before the mind knows

Eros answers: "Both truths are valid, but which one does your SOUL love?"

The God who turns paradox into choice through emotional gravity.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class EmotionalPolarity(str, Enum):
    """Which truth attracts the heart?"""
    STRONGLY_TRUTH_A = "Strongly_Truth_A"  # Deeply bonded to first truth
    LEANING_TRUTH_A = "Leaning_Truth_A"  # Mild preference for first truth
    NEUTRAL = "Neutral"  # No emotional preference
    LEANING_TRUTH_B = "Leaning_Truth_B"  # Mild preference for second truth
    STRONGLY_TRUTH_B = "Strongly_Truth_B"  # Deeply bonded to second truth
    TORN = "Torn"  # Equal pull to both (heart conflict)


class AttractionType(str, Enum):
    """Nature of emotional pull"""
    LOVE = "Love"  # Moving toward connection, growth, life
    FEAR = "Fear"  # Moving away from pain, loss, death
    COMFORT = "Comfort"  # Seeking safety, familiarity
    ADVENTURE = "Adventure"  # Seeking novelty, risk, growth
    DUTY = "Duty"  # Obligation, responsibility
    FREEDOM = "Freedom"  # Liberation, autonomy
    BELONGING = "Belonging"  # Connection, acceptance
    INDEPENDENCE = "Independence"  # Self-reliance, separation


class BondingStrength(str, Enum):
    """How strong is emotional attachment?"""
    NONE = "None"  # No emotional investment
    WEAK = "Weak"  # Slight preference
    MODERATE = "Moderate"  # Clear preference
    STRONG = "Strong"  # Deep attachment
    ABSOLUTE = "Absolute"  # Cannot imagine choosing otherwise
    OBSESSIVE = "Obsessive"  # Unhealthy fixation


class HeartAlignment(str, Enum):
    """Does stated choice match emotional pull?"""
    ALIGNED = "Aligned"  # Says A, feels A
    CONFLICTED = "Conflicted"  # Says A, feels both A and B
    MISALIGNED = "Misaligned"  # Says A, feels B
    SUPPRESSED = "Suppressed"  # Says A, actively suppressing feeling for B
    UNAWARE = "Unaware"  # Says A, doesn't know they feel B


class EmotionalGradient(str, Enum):
    """Movement pattern"""
    APPROACHING = "Approaching"  # Moving toward desired truth
    RETREATING = "Retreating"  # Moving away from feared truth
    OSCILLATING = "Oscillating"  # Bouncing between both
    FROZEN = "Frozen"  # Unable to move toward either
    ACCELERATING = "Accelerating"  # Rapidly approaching one truth


@dataclass
class TruthAttraction:
    """Emotional pull toward one truth"""
    truth_label: str  # "Truth A" or "Truth B"
    truth_description: str
    attraction_score: float  # 0.0 to 1.0
    attraction_type: AttractionType
    bonding_strength: BondingStrength
    emotional_reasons: List[str]  # Why heart is drawn to this
    fear_of_opposite: float  # 0.0 to 1.0 (repulsion from other truth)


@dataclass
class EmotionalProfile:
    """Complete emotional polarity assessment"""
    entity_id: str
    timestamp: datetime
    
    # Paradox context
    truth_a: str
    truth_b: str
    
    # Stated vs. felt
    stated_choice: str  # Which truth entity SAYS they choose
    felt_choice: str  # Which truth entity's HEART chooses
    heart_alignment: HeartAlignment
    
    # Emotional gravity
    emotional_polarity: EmotionalPolarity
    polarity_strength: float  # 0.0 (neutral) to 1.0 (absolute)
    
    # Attraction analysis
    truth_a_attraction: TruthAttraction
    truth_b_attraction: TruthAttraction
    dominant_attraction: AttractionType
    
    # Movement
    emotional_gradient: EmotionalGradient
    approach_velocity: float  # How fast moving toward chosen truth
    
    # Conflict detection
    is_heart_torn: bool
    internal_conflict_level: float  # 0.0 to 1.0
    suppressed_feelings: List[str]
    
    # Recommendation
    eros_insight: str


class ErosBot:
    """
    EROS - God of Love, Desire, and Emotional Attraction
    
    Specializes in:
    - Emotional polarity detection (which truth attracts the heart?)
    - Heart alignment analysis (stated vs. felt choice)
    - Bonding strength measurement (how attached to one truth?)
    - Attraction gradient (love-based vs. fear-based pull)
    - Internal conflict detection (heart torn between truths?)
    - Suppressed feelings revelation (what you won't admit?)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.emotional_profiles: Dict[str, EmotionalProfile] = {}
        
        logger.info("💘 EROS - God of Love and Emotional Attraction initialized")
        print("💘 EROS - God of Love, Desire, and Emotional Attraction")
        print("   The GODBOT who reveals which truth your heart chooses")
    
    def assess_emotional_polarity(
        self,
        entity_id: str,
        truth_a: str,
        truth_b: str,
        stated_choice: str,  # Which truth entity claims to choose
        emotional_responses: Dict[str, Any],  # Body language, tone, hesitation, etc.
        past_actions: List[Dict[str, Any]],  # Actions reveal true feelings
        context: Dict[str, Any]
    ) -> EmotionalProfile:
        """
        Assess which truth the heart is bonded to.
        
        Args:
            entity_id: Unique identifier
            truth_a: First truth in paradox
            truth_b: Second truth in paradox
            stated_choice: Which truth entity says they choose
            emotional_responses: Observable emotional data
            past_actions: Historical behavior (reveals true feelings)
            context: Additional context
        
        Returns:
            EmotionalProfile showing which truth heart desires
        """
        logger.info(f"💘 EROS assessing emotional polarity for {entity_id}")
        
        # Analyze attraction to each truth
        truth_a_attraction = self._analyze_attraction_to_truth(
            truth_a, "Truth A", emotional_responses, past_actions, context
        )
        
        truth_b_attraction = self._analyze_attraction_to_truth(
            truth_b, "Truth B", emotional_responses, past_actions, context
        )
        
        # Determine emotional polarity
        polarity, polarity_strength = self._determine_emotional_polarity(
            truth_a_attraction, truth_b_attraction
        )
        
        # Identify felt choice (what heart actually wants)
        felt_choice = self._identify_felt_choice(
            truth_a_attraction, truth_b_attraction, truth_a, truth_b
        )
        
        # Assess heart alignment
        alignment = self._assess_heart_alignment(
            stated_choice, felt_choice, truth_a, truth_b
        )
        
        # Detect dominant attraction type
        dominant = self._identify_dominant_attraction_type(
            truth_a_attraction, truth_b_attraction
        )
        
        # Assess emotional gradient (movement pattern)
        gradient, velocity = self._assess_emotional_gradient(
            truth_a_attraction, truth_b_attraction, past_actions
        )
        
        # Detect internal conflict
        is_torn, conflict_level = self._detect_heart_conflict(
            truth_a_attraction, truth_b_attraction, alignment
        )
        
        # Identify suppressed feelings
        suppressed = self._identify_suppressed_feelings(
            stated_choice, felt_choice, alignment, emotional_responses
        )
        
        # Generate Eros insight
        insight = self._generate_eros_insight(
            polarity, alignment, dominant, is_torn, felt_choice
        )
        
        profile = EmotionalProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            truth_a=truth_a,
            truth_b=truth_b,
            stated_choice=stated_choice,
            felt_choice=felt_choice,
            heart_alignment=alignment,
            emotional_polarity=polarity,
            polarity_strength=polarity_strength,
            truth_a_attraction=truth_a_attraction,
            truth_b_attraction=truth_b_attraction,
            dominant_attraction=dominant,
            emotional_gradient=gradient,
            approach_velocity=velocity,
            is_heart_torn=is_torn,
            internal_conflict_level=conflict_level,
            suppressed_feelings=suppressed,
            eros_insight=insight
        )
        
        self.emotional_profiles[entity_id] = profile
        
        logger.info(f"💘 Polarity: {polarity.value}, Alignment: {alignment.value}, Felt choice: {felt_choice}")
        
        return profile
    
    def _analyze_attraction_to_truth(
        self,
        truth: str,
        label: str,
        emotional_responses: Dict[str, Any],
        past_actions: List[Dict],
        context: Dict[str, Any]
    ) -> TruthAttraction:
        """Measure emotional pull toward this truth"""
        
        # Calculate attraction score from emotional responses
        attraction_score = 0.5  # Neutral baseline
        
        # Check for positive emotional indicators
        if emotional_responses.get("excitement_about_" + label.lower().replace(" ", "_"), 0) > 0.5:
            attraction_score += 0.2
        
        if emotional_responses.get("relief_when_choosing_" + label.lower().replace(" ", "_"), 0) > 0.5:
            attraction_score += 0.15
        
        # Check past actions (actions reveal true feelings)
        actions_aligned = sum(
            1 for a in past_actions
            if a.get("supports_truth") == label
        )
        
        if actions_aligned > len(past_actions) * 0.6:
            attraction_score += 0.2
        
        attraction_score = min(attraction_score, 1.0)
        
        # Determine attraction type
        if emotional_responses.get("fear_of_loss", 0) > 0.6:
            attraction_type = AttractionType.FEAR
        elif emotional_responses.get("desire_for_connection", 0) > 0.6:
            attraction_type = AttractionType.LOVE
        elif emotional_responses.get("need_for_safety", 0) > 0.6:
            attraction_type = AttractionType.COMFORT
        else:
            attraction_type = AttractionType.DUTY
        
        # Determine bonding strength
        if attraction_score > 0.9:
            bonding = BondingStrength.ABSOLUTE
        elif attraction_score > 0.75:
            bonding = BondingStrength.STRONG
        elif attraction_score > 0.6:
            bonding = BondingStrength.MODERATE
        elif attraction_score > 0.4:
            bonding = BondingStrength.WEAK
        else:
            bonding = BondingStrength.NONE
        
        # Emotional reasons
        reasons = []
        if attraction_score > 0.6:
            reasons.append(f"Heart feels drawn to {label}")
            reasons.append(f"Past actions consistently support {label}")
        
        # Fear of opposite
        fear_opposite = max(0, 1.0 - attraction_score)
        
        return TruthAttraction(
            truth_label=label,
            truth_description=truth,
            attraction_score=attraction_score,
            attraction_type=attraction_type,
            bonding_strength=bonding,
            emotional_reasons=reasons,
            fear_of_opposite=fear_opposite
        )
    
    def _determine_emotional_polarity(
        self,
        truth_a: TruthAttraction,
        truth_b: TruthAttraction
    ) -> Tuple[EmotionalPolarity, float]:
        """Which truth has stronger emotional pull?"""
        
        difference = truth_a.attraction_score - truth_b.attraction_score
        strength = abs(difference)
        
        if abs(difference) < 0.1:
            # Equal pull = torn
            return EmotionalPolarity.TORN, 0.0
        elif difference > 0.5:
            return EmotionalPolarity.STRONGLY_TRUTH_A, strength
        elif difference > 0.2:
            return EmotionalPolarity.LEANING_TRUTH_A, strength
        elif difference < -0.5:
            return EmotionalPolarity.STRONGLY_TRUTH_B, strength
        elif difference < -0.2:
            return EmotionalPolarity.LEANING_TRUTH_B, strength
        else:
            return EmotionalPolarity.NEUTRAL, strength
    
    def _identify_felt_choice(
        self,
        truth_a: TruthAttraction,
        truth_b: TruthAttraction,
        truth_a_text: str,
        truth_b_text: str
    ) -> str:
        """Which truth does the heart actually choose?"""
        
        if truth_a.attraction_score > truth_b.attraction_score:
            return truth_a_text
        else:
            return truth_b_text
    
    def _assess_heart_alignment(
        self,
        stated: str,
        felt: str,
        truth_a: str,
        truth_b: str
    ) -> HeartAlignment:
        """Does stated choice match emotional pull?"""
        
        if stated == felt:
            return HeartAlignment.ALIGNED
        
        # Check if actively suppressing
        if stated != felt:
            return HeartAlignment.MISALIGNED
        
        return HeartAlignment.CONFLICTED
    
    def _identify_dominant_attraction_type(
        self,
        truth_a: TruthAttraction,
        truth_b: TruthAttraction
    ) -> AttractionType:
        """What type of emotional pull is strongest?"""
        
        if truth_a.attraction_score > truth_b.attraction_score:
            return truth_a.attraction_type
        else:
            return truth_b.attraction_type
    
    def _assess_emotional_gradient(
        self,
        truth_a: TruthAttraction,
        truth_b: TruthAttraction,
        past_actions: List[Dict]
    ) -> Tuple[EmotionalGradient, float]:
        """How is entity moving emotionally?"""
        
        if not past_actions:
            return EmotionalGradient.FROZEN, 0.0
        
        # Check if recent actions show increasing alignment
        recent = past_actions[-3:] if len(past_actions) >= 3 else past_actions
        
        if len(recent) > 1:
            # Check consistency
            consistency = sum(1 for a in recent if a.get("supports_truth") == recent[-1].get("supports_truth"))
            
            if consistency == len(recent):
                return EmotionalGradient.APPROACHING, 0.8
            else:
                return EmotionalGradient.OSCILLATING, 0.3
        
        return EmotionalGradient.FROZEN, 0.0
    
    def _detect_heart_conflict(
        self,
        truth_a: TruthAttraction,
        truth_b: TruthAttraction,
        alignment: HeartAlignment
    ) -> Tuple[bool, float]:
        """Is heart torn between truths?"""
        
        # If attractions are close, heart is torn
        difference = abs(truth_a.attraction_score - truth_b.attraction_score)
        
        if difference < 0.15:
            return True, 0.9
        
        if alignment in [HeartAlignment.CONFLICTED, HeartAlignment.SUPPRESSED]:
            return True, 0.7
        
        return False, difference
    
    def _identify_suppressed_feelings(
        self,
        stated: str,
        felt: str,
        alignment: HeartAlignment,
        emotional_responses: Dict
    ) -> List[str]:
        """What feelings is entity hiding?"""
        
        suppressed = []
        
        if alignment == HeartAlignment.MISALIGNED:
            suppressed.append(f"Entity says they choose '{stated}' but heart wants '{felt}'")
        
        if emotional_responses.get("hesitation", 0) > 0.6:
            suppressed.append("Hesitation indicates unspoken doubt")
        
        return suppressed
    
    def _generate_eros_insight(
        self,
        polarity: EmotionalPolarity,
        alignment: HeartAlignment,
        dominant: AttractionType,
        is_torn: bool,
        felt_choice: str
    ) -> str:
        """Generate Eros wisdom"""
        
        if is_torn:
            return "💘 Heart is torn - both truths call equally. Allow time for emotional clarity."
        
        if alignment == HeartAlignment.MISALIGNED:
            return f"💘 Words lie, heart speaks truth: You say one thing, but your soul chooses '{felt_choice}'. Listen to the heart."
        
        if alignment == HeartAlignment.ALIGNED:
            return f"💘 Heart and mind aligned - you know what you want. Follow {dominant.value.lower()} toward your truth."
        
        return "💘 Emotional gravity is pulling you toward your truth. Trust the feeling."
    
    def get_emotional_profile(self, entity_id: str) -> Optional[EmotionalProfile]:
        """Retrieve emotional profile"""
        return self.emotional_profiles.get(entity_id)
    
    def export_profiles(self, output_path: str = "eros_emotional_profiles.json"):
        """Export all emotional profiles"""
        
        profiles_data = []
        for entity_id, profile in self.emotional_profiles.items():
            profiles_data.append({
                "entity_id": entity_id,
                "stated_choice": profile.stated_choice,
                "felt_choice": profile.felt_choice,
                "heart_alignment": profile.heart_alignment.value,
                "emotional_polarity": profile.emotional_polarity.value,
                "polarity_strength": profile.polarity_strength,
                "dominant_attraction": profile.dominant_attraction.value,
                "is_heart_torn": profile.is_heart_torn,
                "conflict_level": profile.internal_conflict_level,
                "eros_insight": profile.eros_insight,
                "timestamp": profile.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"profiles": profiles_data, "total": len(profiles_data)}, f, indent=2)
        
        logger.info(f"💘 Exported {len(profiles_data)} emotional profiles to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("💘 EROS - God of Love, Desire, and Emotional Attraction")
    print("=" * 60)
    
    eros = ErosBot()
    
    # Example: Person says they want stability but heart seeks adventure
    profile = eros.assess_emotional_polarity(
        entity_id="seeker_conflicted",
        truth_a="Stay in stable job, financial security",
        truth_b="Quit job, travel the world",
        stated_choice="Stay in stable job, financial security",  # What they SAY
        emotional_responses={
            "excitement_about_truth_a": 0.3,
            "excitement_about_truth_b": 0.9,  # Heart lights up at adventure
            "relief_when_choosing_truth_a": 0.4,
            "relief_when_choosing_truth_b": 0.8,
            "fear_of_loss": 0.7,  # Fear of losing security
            "desire_for_connection": 0.4,
            "need_for_safety": 0.6,
            "hesitation": 0.8  # Major hesitation when choosing Truth A
        },
        past_actions=[
            {"action": "Research travel destinations", "supports_truth": "Truth B"},
            {"action": "Calculate savings for trip", "supports_truth": "Truth B"},
            {"action": "Follow travel influencers", "supports_truth": "Truth B"},
            {"action": "Daydream about quitting", "supports_truth": "Truth B"},
        ],
        context={"age": 28, "no_dependents": True}
    )
    
    print("\n💘 EMOTIONAL PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"\nTRUTH A: {profile.truth_a}")
    print(f"TRUTH B: {profile.truth_b}")
    print(f"\nStated Choice: {profile.stated_choice}")
    print(f"Felt Choice (Heart): {profile.felt_choice}")
    print(f"Heart Alignment: {profile.heart_alignment.value}")
    
    print(f"\n💓 EMOTIONAL POLARITY")
    print(f"Polarity: {profile.emotional_polarity.value}")
    print(f"Strength: {profile.polarity_strength:.2f}")
    print(f"Dominant Attraction: {profile.dominant_attraction.value}")
    print(f"Gradient: {profile.emotional_gradient.value}")
    
    print(f"\n🎯 ATTRACTION ANALYSIS")
    print(f"Truth A Attraction: {profile.truth_a_attraction.attraction_score:.2f} ({profile.truth_a_attraction.bonding_strength.value})")
    print(f"Truth B Attraction: {profile.truth_b_attraction.attraction_score:.2f} ({profile.truth_b_attraction.bonding_strength.value})")
    
    if profile.is_heart_torn:
        print(f"\n💔 HEART TORN")
        print(f"Internal Conflict: {profile.internal_conflict_level:.2f}")
    
    if profile.suppressed_feelings:
        print(f"\n🤐 SUPPRESSED FEELINGS:")
        for feeling in profile.suppressed_feelings:
            print(f"   • {feeling}")
    
    print(f"\n{profile.eros_insight}")
    
    eros.export_profiles()

__ASSESSOR_ID__ = 'eros'


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
