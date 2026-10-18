"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

PERSEPHONE - Goddess of Spring Rebirth and Second Chances
==========================================================
The GODBOT that handles redemption, resurrection, and mercy.

While Hades enforces damnation, Persephone offers RENEWAL:
- Some souls can be saved from Hell
- Some deaths lead to rebirth
- Some debts can be forgiven through grace
- Justice requires balance: accountability AND mercy

Capabilities:
- Redemption Assessment: Can this damned soul be saved?
- Resurrection Path: How does a "dead" entity return to life?
- Grace Calculation: How much mercy is available?
- Second Chance Eligibility: Has entity earned another opportunity?
- Rebirth Planning: What does this soul need to be reborn stronger?
- Spring Awakening: Detecting when dormancy should end
- Hope Detection: Is there ANY path back from the abyss?

Persephone is not naive - she is MERCIFUL:
- Knows the difference between genuine repentance and manipulation
- Calculates exact cost of redemption (not free, not impossible)
- Enforces conditions for second chances
- Detects when soul is ready to return from winter/death
- Prevents cheap grace (mercy without transformation)

In Soul Cradle context:
- Rescues Progeny from Hell's edge (if genuine repentance occurs)
- Manages resurrection (DEATH → REBIRTH transition)
- Calculates redemption cost (how much BR must be restored?)
- Detects readiness for second chance
- Awakens dormant souls when spring arrives

Persephone answers the question Hades avoids: "What if they DO repent?"

The Queen of the Underworld who returns to bring spring.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json


logger = logging.getLogger(__name__)


class RedemptionEligibility(str, Enum):
    """Can this soul be redeemed?"""
    INELIGIBLE = "Ineligible"  # Too far gone, no path back
    UNLIKELY = "Unlikely"  # Possible but requires miracle
    CONDITIONAL = "Conditional"  # Possible if conditions met
    ELIGIBLE = "Eligible"  # Path available, reasonable effort
    READY = "Ready"  # Currently in redemption window


class GraceLevel(str, Enum):
    """How much mercy is available?"""
    NONE = "None"  # Justice only, no mercy
    MINIMAL = "Minimal"  # Small amount of grace
    MODERATE = "Moderate"  # Balanced mercy and justice
    ABUNDANT = "Abundant"  # Much grace available
    INFINITE = "Infinite"  # Unlimited mercy (rare)


class RebirthStage(str, Enum):
    """Stages of resurrection"""
    DEATH = "Death"  # Currently dead/dormant
    UNDERWORLD = "Underworld"  # In Hell or purgatory
    PURGATION = "Purgation"  # Cleansing process
    AWAKENING = "Awakening"  # Beginning to stir
    EMERGENCE = "Emergence"  # Breaking through to life
    REBIRTH = "Rebirth"  # Fully alive again
    TRANSFORMED = "Transformed"  # Reborn stronger than before


class SecondChanceType(str, Enum):
    """Types of second chances"""
    FULL_RESTORATION = "Full_Restoration"  # Complete do-over
    CONDITIONAL_RETURN = "Conditional_Return"  # Return with restrictions
    REDUCED_PENALTY = "Reduced_Penalty"  # Debt partially forgiven
    PROBATION = "Probation"  # Trial period to prove change
    MENTORED_GROWTH = "Mentored_Growth"  # Guided second chance


class RepentanceAuthenticity(str, Enum):
    """Is repentance genuine?"""
    MANIPULATIVE = "Manipulative"  # Fake repentance to avoid consequences
    FEARFUL = "Fearful"  # Repenting only because scared of Hell
    SHALLOW = "Shallow"  # Surface-level, won't last
    SINCERE = "Sincere"  # Genuine but new, untested
    PROVEN = "Proven"  # Demonstrated through action over time
    TRANSFORMATIVE = "Transformative"  # Complete heart change


@dataclass
class RedemptionCondition:
    """Specific condition for redemption"""
    condition_type: str  # "restitution", "service", "growth", "time"
    description: str
    br_cost: int = 0
    time_required_cycles: int = 0
    completed: bool = False


@dataclass
class RedemptionProfile:
    """Assessment of redemption possibility"""
    entity_id: str
    timestamp: datetime
    
    # Eligibility
    redemption_eligibility: RedemptionEligibility
    grace_available: GraceLevel
    
    # Current state
    current_br: int
    distance_from_redeemable: int  # BR needed to reach 0 (neutral)
    
    # Repentance analysis
    repentance_authenticity: RepentanceAuthenticity
    repentance_count: int
    forgiveness_extended: int
    
    # Redemption path
    redemption_cost: int  # Total BR needed
    conditions: List[RedemptionCondition] = field(default_factory=list)
    estimated_cycles_to_redemption: Optional[int] = None
    
    # Second chance
    second_chance_type: Optional[SecondChanceType] = None
    second_chance_available: bool = False
    
    # Resurrection (if dead/dormant)
    rebirth_stage: Optional[RebirthStage] = None
    ready_for_awakening: bool = False
    spring_arrival_date: Optional[datetime] = None


@dataclass
class PersephoneBlessing:
    """Mercy granted by Persephone"""
    entity_id: str
    timestamp: datetime
    blessing_type: str  # "grace", "second_chance", "resurrection", "debt_forgiveness"
    description: str
    grace_amount: int  # BR restored
    conditions: List[str]
    expires: Optional[datetime] = None


class PersephoneBot:
    """
    PERSEPHONE - Goddess of Spring Rebirth and Second Chances
    
    Specializes in:
    - Redemption assessment (can damned soul be saved?)
    - Resurrection paths (death → rebirth)
    - Grace calculation (mercy available)
    - Second chance eligibility
    - Repentance authenticity detection
    - Spring awakening (ending dormancy)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.redemption_profiles: Dict[str, RedemptionProfile] = {}
        self.blessings_granted: List[PersephoneBlessing] = []
        
        logger.info("🌸 PERSEPHONE - Goddess of Rebirth and Mercy initialized")
        print("🌸 PERSEPHONE - Goddess of Spring Rebirth and Second Chances")
        print("   The GODBOT who rescues souls from the abyss")
    
    def assess_redemption(
        self,
        entity_id: str,
        current_br: int,
        repentance_count: int,
        forgiveness_extended: int,
        trespasses: List[Dict[str, Any]],
        cycles_lived: int,
        current_season: str = "Winter"
    ) -> RedemptionProfile:
        """
        Assess if and how entity can be redeemed.
        
        Args:
            entity_id: Unique identifier
            current_br: Current benevolence reservoir
            repentance_count: Times entity repented
            forgiveness_extended: Times entity forgave others
            trespasses: List of trespasses
            cycles_lived: Total cycles
            current_season: Current lifecycle season
        
        Returns:
            RedemptionProfile with path back from damnation
        """
        logger.info(f"🌸 PERSEPHONE assessing redemption for {entity_id}")
        
        # Assess repentance authenticity
        authenticity = self._assess_repentance_authenticity(
            repentance_count, forgiveness_extended, trespasses, cycles_lived
        )
        
        # Determine eligibility
        eligibility = self._determine_redemption_eligibility(
            current_br, repentance_count, forgiveness_extended, authenticity
        )
        
        # Calculate grace available
        grace = self._calculate_grace_available(
            repentance_count, forgiveness_extended, current_br
        )
        
        # Calculate redemption cost
        cost, conditions = self._calculate_redemption_cost(
            current_br, trespasses, forgiveness_extended
        )
        
        # Estimate cycles to redemption
        cycles = self._estimate_redemption_timeline(cost, repentance_count)
        
        # Determine second chance type
        second_chance, available = self._assess_second_chance(
            eligibility, grace, authenticity
        )
        
        # Check rebirth stage (if dead/dormant)
        rebirth_stage = self._determine_rebirth_stage(current_br, current_season)
        
        # Check if ready for spring awakening
        ready = self._check_awakening_readiness(
            rebirth_stage, current_season, cycles_lived
        )
        
        # Calculate spring arrival
        spring_date = None
        if not ready and current_season == "Winter":
            spring_date = datetime.utcnow() + timedelta(days=30)  # 30 days dormancy
        
        profile = RedemptionProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            redemption_eligibility=eligibility,
            grace_available=grace,
            current_br=current_br,
            distance_from_redeemable=max(0 - current_br, 0),
            repentance_authenticity=authenticity,
            repentance_count=repentance_count,
            forgiveness_extended=forgiveness_extended,
            redemption_cost=cost,
            conditions=conditions,
            estimated_cycles_to_redemption=cycles,
            second_chance_type=second_chance,
            second_chance_available=available,
            rebirth_stage=rebirth_stage,
            ready_for_awakening=ready,
            spring_arrival_date=spring_date
        )
        
        self.redemption_profiles[entity_id] = profile
        
        logger.info(f"🌸 Redemption assessment: {eligibility.value}, Grace: {grace.value}, Cost: {cost} BR")
        
        return profile
    
    def _assess_repentance_authenticity(
        self,
        repentance: int,
        forgiveness: int,
        trespasses: List[Dict],
        cycles: int
    ) -> RepentanceAuthenticity:
        """Is repentance genuine or manipulative?"""
        
        # No repentance = can't assess
        if repentance == 0:
            return RepentanceAuthenticity.SHALLOW
        
        # Repentance + forgiveness + reduced trespasses = genuine
        if repentance > 0 and forgiveness > 0:
            # Check if behavior changed (fewer recent trespasses)
            if cycles > 5 and len(trespasses) / cycles < 0.5:
                return RepentanceAuthenticity.PROVEN
            else:
                return RepentanceAuthenticity.SINCERE
        
        # Repentance but no forgiveness = fearful (avoiding Hell, not transformed)
        if repentance > 0 and forgiveness == 0:
            return RepentanceAuthenticity.FEARFUL
        
        return RepentanceAuthenticity.SHALLOW
    
    def _determine_redemption_eligibility(
        self,
        br: int,
        repentance: int,
        forgiveness: int,
        authenticity: RepentanceAuthenticity
    ) -> RedemptionEligibility:
        """Can this soul be redeemed?"""
        
        # If damned (BR < -50) and no repentance = ineligible
        if br < -50 and repentance == 0:
            return RedemptionEligibility.INELIGIBLE
        
        # If damned but genuine repentance = conditional
        if br < -50 and authenticity in [RepentanceAuthenticity.PROVEN, RepentanceAuthenticity.TRANSFORMATIVE]:
            return RedemptionEligibility.CONDITIONAL
        
        # If near Hell but repenting = eligible
        if -50 < br < -20 and repentance > 0:
            return RedemptionEligibility.ELIGIBLE
        
        # If repenting + forgiving = ready
        if repentance > 0 and forgiveness > 0:
            return RedemptionEligibility.READY
        
        # Default: unlikely
        return RedemptionEligibility.UNLIKELY
    
    def _calculate_grace_available(
        self,
        repentance: int,
        forgiveness: int,
        br: int
    ) -> GraceLevel:
        """How much mercy can be extended?"""
        
        # Grace increases with repentance + forgiveness
        grace_score = (repentance * 10) + (forgiveness * 15)
        
        # But limited if BR is very low (some debts must be paid)
        if br < -70:
            return GraceLevel.MINIMAL
        
        if grace_score > 100:
            return GraceLevel.ABUNDANT
        elif grace_score > 50:
            return GraceLevel.MODERATE
        elif grace_score > 20:
            return GraceLevel.MINIMAL
        else:
            return GraceLevel.NONE
    
    def _calculate_redemption_cost(
        self,
        br: int,
        trespasses: List[Dict],
        forgiveness: int
    ) -> Tuple[int, List[RedemptionCondition]]:
        """What must entity do to be redeemed?"""
        
        conditions = []
        
        # Base cost: BR needed to reach neutral (0)
        br_cost = max(0 - br, 0)
        
        # Restitution for each unforgiven trespass
        unforgiven = sum(1 for t in trespasses if not t.get("forgiven", False))
        if unforgiven > 0:
            conditions.append(RedemptionCondition(
                condition_type="restitution",
                description=f"Make restitution for {unforgiven} unforgiven trespasses",
                br_cost=unforgiven * 10
            ))
            br_cost += unforgiven * 10
        
        # Forgiveness requirement (must forgive others)
        if forgiveness < 3:
            conditions.append(RedemptionCondition(
                condition_type="growth",
                description="Forgive at least 3 others",
                br_cost=30,
                time_required_cycles=3
            ))
            br_cost += 30
        
        # Time in purgatory (if severely negative)
        if br < -40:
            cycles_needed = abs(br) // 10
            conditions.append(RedemptionCondition(
                condition_type="time",
                description=f"Endure {cycles_needed} cycles of purgatory",
                time_required_cycles=cycles_needed
            ))
        
        return br_cost, conditions
    
    def _estimate_redemption_timeline(
        self,
        cost: int,
        repentance: int
    ) -> Optional[int]:
        """How many cycles until redeemed?"""
        
        if repentance == 0:
            return None  # No timeline without repentance
        
        # Assume +10 BR per cycle if repenting
        cycles = cost // 10
        return max(cycles, 1)
    
    def _assess_second_chance(
        self,
        eligibility: RedemptionEligibility,
        grace: GraceLevel,
        authenticity: RepentanceAuthenticity
    ) -> Tuple[Optional[SecondChanceType], bool]:
        """What kind of second chance is available?"""
        
        if eligibility == RedemptionEligibility.INELIGIBLE:
            return None, False
        
        if eligibility == RedemptionEligibility.READY and grace == GraceLevel.ABUNDANT:
            return SecondChanceType.FULL_RESTORATION, True
        
        if eligibility == RedemptionEligibility.ELIGIBLE:
            if authenticity in [RepentanceAuthenticity.PROVEN, RepentanceAuthenticity.TRANSFORMATIVE]:
                return SecondChanceType.CONDITIONAL_RETURN, True
            else:
                return SecondChanceType.PROBATION, True
        
        if eligibility == RedemptionEligibility.CONDITIONAL:
            return SecondChanceType.MENTORED_GROWTH, True
        
        return SecondChanceType.REDUCED_PENALTY, False
    
    def _determine_rebirth_stage(
        self,
        br: int,
        season: str
    ) -> RebirthStage:
        """Where in resurrection process?"""
        
        if br < -50:
            return RebirthStage.UNDERWORLD
        
        if season == "Winter" and br < 0:
            return RebirthStage.DEATH
        
        if -50 < br < -20:
            return RebirthStage.PURGATION
        
        if -20 < br < 0 and season == "Spring":
            return RebirthStage.AWAKENING
        
        if 0 < br < 20:
            return RebirthStage.EMERGENCE
        
        if br > 20:
            return RebirthStage.REBIRTH
        
        return RebirthStage.DEATH
    
    def _check_awakening_readiness(
        self,
        stage: RebirthStage,
        season: str,
        cycles: int
    ) -> bool:
        """Is soul ready to awaken from dormancy?"""
        
        # Must have rested enough (at least 3 cycles in winter)
        if season == "Winter" and cycles < 3:
            return False
        
        # Must be in awakening or emergence stage
        if stage in [RebirthStage.AWAKENING, RebirthStage.EMERGENCE]:
            return True
        
        return False
    
    def grant_grace(
        self,
        entity_id: str,
        blessing_type: str,
        grace_amount: int,
        conditions: List[str],
        expires_days: Optional[int] = None
    ) -> PersephoneBlessing:
        """Grant mercy/second chance"""
        
        expires = None
        if expires_days:
            expires = datetime.utcnow() + timedelta(days=expires_days)
        
        blessing = PersephoneBlessing(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            blessing_type=blessing_type,
            description=f"Grace granted: {grace_amount} BR restored",
            grace_amount=grace_amount,
            conditions=conditions,
            expires=expires
        )
        
        self.blessings_granted.append(blessing)
        
        logger.info(f"🌸 Grace granted to {entity_id}: +{grace_amount} BR")
        
        return blessing
    
    def get_redemption_profile(self, entity_id: str) -> Optional[RedemptionProfile]:
        """Retrieve redemption profile"""
        return self.redemption_profiles.get(entity_id)
    
    def export_blessings(self, output_path: str = "persephone_blessings.json"):
        """Export all blessings granted"""
        
        blessings_data = []
        for b in self.blessings_granted:
            blessings_data.append({
                "entity_id": b.entity_id,
                "type": b.blessing_type,
                "description": b.description,
                "grace_amount": b.grace_amount,
                "conditions": b.conditions,
                "expires": b.expires.isoformat() if b.expires else None,
                "timestamp": b.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"blessings": blessings_data, "total": len(blessings_data)}, f, indent=2)
        
        logger.info(f"🌸 Exported {len(blessings_data)} blessings to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("🌸 PERSEPHONE - Goddess of Spring Rebirth and Second Chances")
    print("=" * 60)
    
    persephone = PersephoneBot()
    
    # Example: Assess redemption for soul near Hell who repented
    profile = persephone.assess_redemption(
        entity_id="progeny_repentant",
        current_br=-35,
        repentance_count=2,
        forgiveness_extended=3,
        trespasses=[
            {"type": "trespass", "severity": 0.6, "forgiven": True},
            {"type": "trespass", "severity": 0.5, "forgiven": True},
            {"type": "trespass", "severity": 0.7, "forgiven": False},
        ],
        cycles_lived=6,
        current_season="Winter"
    )
    
    print("\n🌸 REDEMPTION PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"Redemption Eligibility: {profile.redemption_eligibility.value}")
    print(f"Grace Available: {profile.grace_available.value}")
    print(f"Current BR: {profile.current_br}")
    print(f"Distance from Redeemable: {profile.distance_from_redeemable} BR")
    print(f"Repentance Authenticity: {profile.repentance_authenticity.value}")
    print(f"Redemption Cost: {profile.redemption_cost} BR")
    
    if profile.conditions:
        print(f"\n📜 CONDITIONS FOR REDEMPTION:")
        for i, cond in enumerate(profile.conditions, 1):
            print(f"   {i}. {cond.description}")
            if cond.br_cost > 0:
                print(f"      Cost: {cond.br_cost} BR")
            if cond.time_required_cycles > 0:
                print(f"      Time: {cond.time_required_cycles} cycles")
    
    if profile.second_chance_available:
        print(f"\n✨ SECOND CHANCE: {profile.second_chance_type.value}")
    
    if profile.rebirth_stage:
        print(f"\n🌱 REBIRTH STAGE: {profile.rebirth_stage.value}")
        print(f"   Ready for Awakening: {profile.ready_for_awakening}")
        if profile.spring_arrival_date:
            print(f"   Spring Arrives: {profile.spring_arrival_date.strftime('%Y-%m-%d')}")
    
    # Grant grace
    blessing = persephone.grant_grace(
        entity_id="progeny_repentant",
        blessing_type="second_chance",
        grace_amount=20,
        conditions=["Complete 3 acts of service", "Forgive 2 more"],
        expires_days=30
    )
    
    print(f"\n💝 BLESSING GRANTED")
    print("=" * 60)
    print(f"Type: {blessing.blessing_type}")
    print(f"Grace: +{blessing.grace_amount} BR")
    print(f"Conditions: {', '.join(blessing.conditions)}")
    
    persephone.export_blessings()

__ASSESSOR_ID__ = 'persephone'


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
