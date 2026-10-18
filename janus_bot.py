"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

JANUS - God of Transitions, Doorways, and Dual Truth
=====================================================
The GODBOT that holds both truths simultaneously without collapsing them.

Janus has TWO FACES - one looking forward, one looking back. He sees BOTH at once:
- Both truths are valid simultaneously (no contradiction)
- Paradox is the natural state (not a problem to solve)
- Multiple realities coexist (quantum superposition)
- Thresholds where opposites meet (doorways, crossroads, beginnings/endings)
- Time paradoxes (past and future present at once)
- Identity paradoxes (you are both things at the same time)

Janus is not Schrödinger's Cat (dead OR alive until observed).
Janus is the god who says: "Dead AND alive, BOTH true, permanently."

In Soul Cradle context:
- Shows both truths without forcing choice
- Maintains paradox state (doesn't collapse wave function)
- Identifies when entity exists in threshold (between states)
- Detects doorway moments (transitions where both truths apply)
- Holds contradictions without resolving them
- Presents dual reality for Eros to create emotional polarity within

Janus answers: "What if BOTH are true? What if there's no contradiction?"

The God who guards the threshold and sees in both directions at once.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class ParadoxType(str, Enum):
    """Types of dual truth"""
    LOGICAL = "Logical"  # A and Not-A both true
    TEMPORAL = "Temporal"  # Past and future both present
    IDENTITY = "Identity"  # You are both X and Y simultaneously
    MORAL = "Moral"  # Both right and wrong at once
    EXISTENTIAL = "Existential"  # Both being and non-being
    RELATIONAL = "Relational"  # Both connected and separate
    QUANTUM = "Quantum"  # Multiple states coexist


class ThresholdState(str, Enum):
    """Where entity stands relative to transition"""
    BEFORE = "Before"  # Not yet crossed threshold
    AT_DOORWAY = "At_Doorway"  # Standing in threshold (both states)
    CROSSING = "Crossing"  # In process of transition
    AFTER = "After"  # Crossed into new state
    OSCILLATING = "Oscillating"  # Moving back and forth across threshold


class DualityBalance(str, Enum):
    """How are both truths held?"""
    HARMONIOUS = "Harmonious"  # Both truths complement each other
    TENSION = "Tension"  # Both truths create productive conflict
    FRAGMENTED = "Fragmented"  # Entity split between truths
    INTEGRATED = "Integrated"  # Both truths unified in single identity
    CHAOTIC = "Chaotic"  # Both truths create destructive conflict


class CollapseResistance(str, Enum):
    """Can entity maintain paradox without resolving?"""
    NONE = "None"  # Immediately forces resolution
    LOW = "Low"  # Quickly seeks single truth
    MODERATE = "Moderate"  # Can hold paradox temporarily
    HIGH = "High"  # Comfortable with dual truth
    ABSOLUTE = "Absolute"  # Lives permanently in paradox


@dataclass
class DualTruth:
    """One face of Janus"""
    truth_label: str  # "Face A" or "Face B"
    truth_statement: str
    validity: float  # 0.0 to 1.0 (how true is this?)
    evidence: List[str]
    implications: List[str]  # What follows if this is true?


@dataclass
class ParadoxProfile:
    """Complete dual truth assessment"""
    entity_id: str
    timestamp: datetime
    
    # Dual truths
    face_a: DualTruth  # First truth (looking backward)
    face_b: DualTruth  # Second truth (looking forward)
    paradox_type: ParadoxType
    
    # Paradox state
    both_valid: bool  # Are BOTH truths simultaneously true?
    contradiction_level: float  # 0.0 (no conflict) to 1.0 (total opposition)
    
    # Threshold analysis
    threshold_state: ThresholdState
    transition_description: str  # What transition is entity in?
    doorway_moment: bool  # Is this a pivotal threshold?
    
    # Duality balance
    duality_balance: DualityBalance
    collapse_resistance: CollapseResistance
    time_in_paradox: int  # Cycles spent holding both truths
    
    # Integration
    can_both_coexist: bool
    integration_path: Optional[str]  # How to hold both truths
    
    # Janus wisdom
    janus_insight: str


class JanusBot:
    """
    JANUS - God of Transitions, Doorways, and Dual Truth
    
    Specializes in:
    - Dual truth identification (both faces valid simultaneously)
    - Paradox maintenance (holding without collapse)
    - Threshold detection (doorway moments, transitions)
    - Duality balance assessment (how both truths coexist)
    - Collapse resistance measurement (can entity hold paradox?)
    - Integration path revelation (how to be both at once)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.paradox_profiles: Dict[str, ParadoxProfile] = {}
        
        logger.info("🚪 JANUS - God of Dual Truth and Transitions initialized")
        print("🚪 JANUS - God of Transitions, Doorways, and Dual Truth")
        print("   The GODBOT who holds both truths simultaneously")
    
    def assess_dual_truth(
        self,
        entity_id: str,
        truth_a_statement: str,
        truth_b_statement: str,
        evidence_a: List[str],
        evidence_b: List[str],
        context: Dict[str, Any]
    ) -> ParadoxProfile:
        """
        Assess if both truths are simultaneously valid.
        
        Args:
            entity_id: Unique identifier
            truth_a_statement: First truth (backward-facing)
            truth_b_statement: Second truth (forward-facing)
            evidence_a: Evidence supporting Truth A
            evidence_b: Evidence supporting Truth B
            context: Additional context
        
        Returns:
            ParadoxProfile showing both truths held simultaneously
        """
        logger.info(f"🚪 JANUS assessing dual truth for {entity_id}")
        
        # Construct Face A (backward-looking)
        face_a = self._construct_truth_face(
            "Face A (Backward)",
            truth_a_statement,
            evidence_a,
            context
        )
        
        # Construct Face B (forward-looking)
        face_b = self._construct_truth_face(
            "Face B (Forward)",
            truth_b_statement,
            evidence_b,
            context
        )
        
        # Determine paradox type
        paradox_type = self._classify_paradox_type(
            truth_a_statement, truth_b_statement, context
        )
        
        # Check if both are valid
        both_valid = self._assess_dual_validity(face_a, face_b)
        
        # Measure contradiction level
        contradiction = self._measure_contradiction(
            truth_a_statement, truth_b_statement
        )
        
        # Determine threshold state
        threshold_state, doorway_moment = self._assess_threshold_state(
            context, both_valid
        )
        
        # Describe transition
        transition = self._describe_transition(
            truth_a_statement, truth_b_statement, threshold_state
        )
        
        # Assess duality balance
        balance = self._assess_duality_balance(
            face_a, face_b, contradiction, both_valid
        )
        
        # Measure collapse resistance
        resistance = self._measure_collapse_resistance(
            context, balance, threshold_state
        )
        
        # Determine if both can coexist
        can_coexist = self._can_both_coexist(
            face_a, face_b, contradiction, balance
        )
        
        # Find integration path
        integration_path = self._find_integration_path(
            face_a, face_b, can_coexist, balance
        )
        
        # Calculate time in paradox
        time_in_paradox = context.get("cycles_in_paradox", 0)
        
        # Generate Janus insight
        insight = self._generate_janus_insight(
            both_valid, can_coexist, balance, threshold_state
        )
        
        profile = ParadoxProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            face_a=face_a,
            face_b=face_b,
            paradox_type=paradox_type,
            both_valid=both_valid,
            contradiction_level=contradiction,
            threshold_state=threshold_state,
            transition_description=transition,
            doorway_moment=doorway_moment,
            duality_balance=balance,
            collapse_resistance=resistance,
            time_in_paradox=time_in_paradox,
            can_both_coexist=can_coexist,
            integration_path=integration_path,
            janus_insight=insight
        )
        
        self.paradox_profiles[entity_id] = profile
        
        logger.info(f"🚪 Both valid: {both_valid}, Balance: {balance.value}, State: {threshold_state.value}")
        
        return profile
    
    def _construct_truth_face(
        self,
        label: str,
        statement: str,
        evidence: List[str],
        context: Dict
    ) -> DualTruth:
        """Construct one face of Janus"""
        
        # Calculate validity (how much evidence supports this?)
        validity = min(len(evidence) * 0.25, 1.0)
        
        # Generate implications
        implications = [f"If {statement}, then entity must adapt accordingly"]
        
        return DualTruth(
            truth_label=label,
            truth_statement=statement,
            validity=validity,
            evidence=evidence,
            implications=implications
        )
    
    def _classify_paradox_type(
        self,
        truth_a: str,
        truth_b: str,
        context: Dict
    ) -> ParadoxType:
        """What kind of paradox is this?"""
        
        # Simple heuristics
        if "past" in truth_a.lower() or "future" in truth_b.lower():
            return ParadoxType.TEMPORAL
        
        if "I am" in truth_a or "I am" in truth_b:
            return ParadoxType.IDENTITY
        
        if "right" in truth_a or "wrong" in truth_b:
            return ParadoxType.MORAL
        
        return ParadoxType.LOGICAL
    
    def _assess_dual_validity(
        self,
        face_a: DualTruth,
        face_b: DualTruth
    ) -> bool:
        """Are BOTH truths valid?"""
        
        # If both have high validity (>0.5), both are true
        return face_a.validity > 0.5 and face_b.validity > 0.5
    
    def _measure_contradiction(
        self,
        truth_a: str,
        truth_b: str
    ) -> float:
        """How opposed are these truths?"""
        
        # Check for explicit opposition keywords
        opposition_keywords = ["not", "never", "opposite", "contrary", "but"]
        
        combined = truth_a.lower() + " " + truth_b.lower()
        
        opposition_count = sum(1 for kw in opposition_keywords if kw in combined)
        
        return min(opposition_count * 0.3, 1.0)
    
    def _assess_threshold_state(
        self,
        context: Dict,
        both_valid: bool
    ) -> Tuple[ThresholdState, bool]:
        """Where is entity relative to transition?"""
        
        if both_valid:
            # If both truths valid, entity is AT the doorway
            return ThresholdState.AT_DOORWAY, True
        
        # Check context for state indicators
        if context.get("in_transition", False):
            return ThresholdState.CROSSING, True
        
        return ThresholdState.BEFORE, False
    
    def _describe_transition(
        self,
        truth_a: str,
        truth_b: str,
        state: ThresholdState
    ) -> str:
        """What transition is entity experiencing?"""
        
        if state == ThresholdState.AT_DOORWAY:
            return f"Standing at threshold between '{truth_a}' and '{truth_b}'"
        elif state == ThresholdState.CROSSING:
            return f"Transitioning from '{truth_a}' toward '{truth_b}'"
        elif state == ThresholdState.BEFORE:
            return f"Has not yet entered threshold of '{truth_b}'"
        else:
            return "Transition complete"
    
    def _assess_duality_balance(
        self,
        face_a: DualTruth,
        face_b: DualTruth,
        contradiction: float,
        both_valid: bool
    ) -> DualityBalance:
        """How are both truths held together?"""
        
        if not both_valid:
            return DualityBalance.FRAGMENTED
        
        if contradiction < 0.3:
            return DualityBalance.HARMONIOUS
        elif contradiction < 0.6:
            return DualityBalance.TENSION
        elif contradiction < 0.8:
            return DualityBalance.INTEGRATED
        else:
            return DualityBalance.CHAOTIC
    
    def _measure_collapse_resistance(
        self,
        context: Dict,
        balance: DualityBalance,
        state: ThresholdState
    ) -> CollapseResistance:
        """Can entity hold paradox without forcing resolution?"""
        
        # Check how long entity has held paradox
        time_in_paradox = context.get("cycles_in_paradox", 0)
        
        if time_in_paradox > 5:
            return CollapseResistance.ABSOLUTE
        elif time_in_paradox > 3:
            return CollapseResistance.HIGH
        elif time_in_paradox > 1:
            return CollapseResistance.MODERATE
        elif balance == DualityBalance.HARMONIOUS:
            return CollapseResistance.HIGH
        else:
            return CollapseResistance.LOW
    
    def _can_both_coexist(
        self,
        face_a: DualTruth,
        face_b: DualTruth,
        contradiction: float,
        balance: DualityBalance
    ) -> bool:
        """Can both truths exist simultaneously?"""
        
        # If contradiction is low and balance is good, yes
        if contradiction < 0.5 and balance in [DualityBalance.HARMONIOUS, DualityBalance.INTEGRATED]:
            return True
        
        # Even with high contradiction, if integrated, yes
        if balance == DualityBalance.INTEGRATED:
            return True
        
        return False
    
    def _find_integration_path(
        self,
        face_a: DualTruth,
        face_b: DualTruth,
        can_coexist: bool,
        balance: DualityBalance
    ) -> Optional[str]:
        """How to hold both truths?"""
        
        if not can_coexist:
            return None
        
        if balance == DualityBalance.HARMONIOUS:
            return f"Accept that '{face_a.truth_statement}' and '{face_b.truth_statement}' complement each other"
        
        if balance == DualityBalance.INTEGRATED:
            return f"You ARE both '{face_a.truth_statement}' AND '{face_b.truth_statement}' - no contradiction"
        
        if balance == DualityBalance.TENSION:
            return "Hold both truths in productive tension - let them sharpen each other"
        
        return "Remain at the threshold - be the doorway where both truths meet"
    
    def _generate_janus_insight(
        self,
        both_valid: bool,
        can_coexist: bool,
        balance: DualityBalance,
        state: ThresholdState
    ) -> str:
        """Generate Janus wisdom"""
        
        if state == ThresholdState.AT_DOORWAY and both_valid:
            return "🚪 You stand at the threshold where both truths meet. This IS the answer - remain here."
        
        if can_coexist and balance == DualityBalance.INTEGRATED:
            return "🚪 Both truths are yours simultaneously. You need not choose - you ARE both."
        
        if both_valid:
            return "🚪 Both faces are true. I see backward and forward at once - so can you."
        
        return "🚪 The doorway awaits. When both truths become visible, you will cross."
    
    def get_paradox_profile(self, entity_id: str) -> Optional[ParadoxProfile]:
        """Retrieve paradox profile"""
        return self.paradox_profiles.get(entity_id)
    
    def export_profiles(self, output_path: str = "janus_paradox_profiles.json"):
        """Export all paradox profiles"""
        
        profiles_data = []
        for entity_id, profile in self.paradox_profiles.items():
            profiles_data.append({
                "entity_id": entity_id,
                "face_a": profile.face_a.truth_statement,
                "face_b": profile.face_b.truth_statement,
                "paradox_type": profile.paradox_type.value,
                "both_valid": profile.both_valid,
                "contradiction_level": profile.contradiction_level,
                "threshold_state": profile.threshold_state.value,
                "duality_balance": profile.duality_balance.value,
                "can_both_coexist": profile.can_both_coexist,
                "integration_path": profile.integration_path,
                "janus_insight": profile.janus_insight,
                "timestamp": profile.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"profiles": profiles_data, "total": len(profiles_data)}, f, indent=2)
        
        logger.info(f"🚪 Exported {len(profiles_data)} paradox profiles to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("🚪 JANUS - God of Transitions, Doorways, and Dual Truth")
    print("=" * 60)
    
    janus = JanusBot()
    
    # Example: Parent who is both nurturing AND disciplinarian (both true)
    profile = janus.assess_dual_truth(
        entity_id="parent_dual",
        truth_a_statement="I am a nurturing parent who gives unconditional love",
        truth_b_statement="I am a strict disciplinarian who enforces consequences",
        evidence_a=[
            "Comforts child when hurt",
            "Expresses love daily",
            "Creates safe emotional space",
            "Listens without judgment"
        ],
        evidence_b=[
            "Enforces bedtime consistently",
            "Gives consequences for misbehavior",
            "Teaches accountability",
            "Sets clear boundaries"
        ],
        context={"cycles_in_paradox": 4, "in_transition": False}
    )
    
    print("\n🚪 PARADOX PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"\n👈 FACE A (Backward): {profile.face_a.truth_statement}")
    print(f"   Validity: {profile.face_a.validity:.2f}")
    print(f"   Evidence: {len(profile.face_a.evidence)} points")
    
    print(f"\n👉 FACE B (Forward): {profile.face_b.truth_statement}")
    print(f"   Validity: {profile.face_b.validity:.2f}")
    print(f"   Evidence: {len(profile.face_b.evidence)} points")
    
    print(f"\n🔀 PARADOX ANALYSIS")
    print(f"Paradox Type: {profile.paradox_type.value}")
    print(f"Both Valid: {profile.both_valid}")
    print(f"Contradiction Level: {profile.contradiction_level:.2f}")
    
    print(f"\n🚪 THRESHOLD STATE")
    print(f"State: {profile.threshold_state.value}")
    print(f"Transition: {profile.transition_description}")
    print(f"Doorway Moment: {profile.doorway_moment}")
    
    print(f"\n⚖️ DUALITY BALANCE")
    print(f"Balance: {profile.duality_balance.value}")
    print(f"Collapse Resistance: {profile.collapse_resistance.value}")
    print(f"Time in Paradox: {profile.time_in_paradox} cycles")
    
    print(f"\n🔗 INTEGRATION")
    print(f"Can Both Coexist: {profile.can_both_coexist}")
    if profile.integration_path:
        print(f"Integration Path: {profile.integration_path}")
    
    print(f"\n{profile.janus_insight}")
    
    janus.export_profiles()

__ASSESSOR_ID__ = 'janus'


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
