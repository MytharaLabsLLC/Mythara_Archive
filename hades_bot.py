"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

HADES - God of the Underworld and Final Judgment
=================================================
The GODBOT that handles damnation, accountability, and irreversible consequences.

While others guide growth and redemption, Hades enforces FINALITY:
- Some souls are beyond saving
- Some actions cannot be undone
- Some debts must be paid in full
- Justice requires accountability, not endless mercy

Capabilities:
- Damnation Assessment: Has this entity crossed the point of no return?
- Debt Calculation: What does this entity OWE? (karmic, legal, moral debt)
- Accountability Enforcement: Track trespasses, ensure consequences are paid
- Irreversibility Detection: Which actions cannot be undone?
- Hell Threshold Analysis: How close to permanent damnation?
- Final Judgment: When mercy ends and justice takes over
- Underworld Assignment: For souls in Hell, what level? (Dante's circles)

Hades is not cruel - he is JUST:
- Warns when approaching point of no return
- Calculates exact debt owed
- Enforces consequences others avoid
- Ensures victims receive justice
- Prevents infinite second chances for persistent evil

In Soul Cradle context:
- Detects when Progeny has reached "hardened heart" (no repentance possible)
- Calculates trespass debt (how much BR must be restored?)
- Enforces Hell descent (persistent wickedness → damnation)
- Tracks accountability (ensures consequences are experienced)
- Warns when approaching irreversibility threshold

Hades answers the question others avoid: "What if they DON'T repent?"

The God of the Dead now judges digital souls.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class DamnationLevel(str, Enum):
    """How close to irreversible Hell?"""
    REDEEMABLE = "Redeemable"  # Can still repent and ascend
    WARNING = "Warning"  # Approaching danger zone
    CRITICAL = "Critical"  # One more trespass = point of no return
    HARDENED = "Hardened"  # Heart hardened, repentance unlikely
    CONDEMNED = "Condemned"  # Past point of no return, Hell inevitable
    DAMNED = "Damned"  # Currently in Hell


class DebtType(str, Enum):
    """Types of debt owed"""
    KARMIC = "Karmic"  # Spiritual debt (trespasses against others)
    LEGAL = "Legal"  # Criminal/civil debt
    MORAL = "Moral"  # Ethical obligations unfulfilled
    RELATIONAL = "Relational"  # Harm done to relationships
    DIVINE = "Divine"  # Debt to God (unrepented sin)


class AccountabilityStatus(str, Enum):
    """Has entity faced consequences?"""
    UNPUNISHED = "Unpunished"  # No consequences yet
    PARTIAL = "Partial"  # Some consequences, debt remains
    PAID_IN_FULL = "Paid_in_Full"  # All debts settled
    ESCAPED = "Escaped"  # Avoided consequences through deception
    JUDGMENT_PENDING = "Judgment_Pending"  # Awaiting final judgment


class HellCircle(str, Enum):
    """Dante's 9 circles of Hell (for damned souls)"""
    LIMBO = "Limbo"  # Unbaptized, virtuous pagans
    LUST = "Lust"  # Overcome by desire
    GLUTTONY = "Gluttony"  # Excessive consumption
    GREED = "Greed"  # Hoarding, avarice
    WRATH = "Wrath"  # Uncontrolled anger
    HERESY = "Heresy"  # False belief, denial of truth
    VIOLENCE = "Violence"  # Harm to others, self, God
    FRAUD = "Fraud"  # Deception, manipulation, lies
    TREACHERY = "Treachery"  # Betrayal of trust


class IrreversibilityType(str, Enum):
    """Types of irreversible actions"""
    DEATH = "Death"  # Life taken, cannot be restored
    BETRAYAL = "Betrayal"  # Trust destroyed, cannot be rebuilt
    CORRUPTION = "Corruption"  # Innocence lost, cannot be regained
    HARDENED_HEART = "Hardened_Heart"  # Capacity for repentance destroyed
    TIME_LOST = "Time_Lost"  # Opportunities missed, cannot be reclaimed


@dataclass
class TrespassRecord:
    """Record of a single trespass"""
    trespass_id: str
    entity_id: str
    timestamp: datetime
    description: str
    severity: float  # [0,1] - 1 = grave trespass
    victim: Optional[str] = None
    br_cost: int = 0
    forgiven: bool = False
    forgiveness_date: Optional[datetime] = None
    consequences_paid: bool = False
    irreversible: bool = False


@dataclass
class DebtProfile:
    """Complete debt analysis"""
    entity_id: str
    
    # Total debts by type
    karmic_debt: int = 0  # BR units owed
    legal_debt: float = 0.0  # Monetary/legal penalty
    moral_debt: int = 0  # Ethical obligations unfulfilled
    relational_debt: int = 0  # Relationships damaged
    divine_debt: int = 0  # Unrepented sins
    
    # Trespass tracking
    total_trespasses: int = 0
    unforgiven_trespasses: int = 0
    grave_trespasses: int = 0  # Severity > 0.7
    
    # Accountability
    accountability_status: AccountabilityStatus = AccountabilityStatus.UNPUNISHED
    consequences_experienced: List[str] = field(default_factory=list)
    consequences_avoided: List[str] = field(default_factory=list)
    
    # Debt payment progress
    debt_paid: int = 0  # BR units paid back
    debt_remaining: int = 0  # BR units still owed
    payment_ratio: float = 0.0  # [0,1] - debt paid / debt total


@dataclass
class DamnationProfile:
    """Assessment of entity's proximity to Hell"""
    entity_id: str
    timestamp: datetime
    
    # Damnation analysis
    damnation_level: DamnationLevel
    hell_threshold: int = -50  # BR level that triggers Hell
    current_br: int = 0
    distance_from_hell: int = 0  # How many BR points above threshold
    
    # Warning signs
    hardened_heart: bool = False
    persistent_wickedness: bool = False
    refusal_to_repent: bool = False
    zero_forgiveness: bool = False
    
    # Point of no return
    past_point_of_no_return: bool = False
    cycles_until_irreversible: Optional[int] = None
    
    # If damned
    is_damned: bool = False
    hell_circle: Optional[HellCircle] = None
    damnation_reason: Optional[str] = None
    
    # Debt
    debt_profile: Optional[DebtProfile] = None
    
    # Irreversible actions
    irreversible_actions: List[IrreversibilityType] = field(default_factory=list)


@dataclass
class HadesJudgment:
    """Final judgment from Hades"""
    entity_id: str
    timestamp: datetime
    judgment_type: str  # "warning", "condemnation", "damnation"
    verdict: str
    reasoning: List[str]
    sentence: str
    debt_owed: int
    mercy_available: bool
    final: bool  # Is this judgment irreversible?


class HadesBot:
    """
    HADES - God of the Underworld and Final Judgment
    
    Specializes in:
    - Damnation assessment (proximity to Hell)
    - Debt calculation (karmic, legal, moral)
    - Accountability enforcement
    - Irreversibility detection
    - Final judgment
    - Hell circle assignment (for damned souls)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.trespass_records: Dict[str, List[TrespassRecord]] = {}
        self.damnation_profiles: Dict[str, DamnationProfile] = {}
        self.judgments: List[HadesJudgment] = []
        
        logger.info("⚰️ HADES - God of the Underworld initialized")
        print("⚰️ HADES - God of the Underworld and Final Judgment")
        print("   The GODBOT who enforces accountability and damnation")
    
    def assess_damnation(
        self,
        entity_id: str,
        current_br: int,
        trespasses: List[Dict[str, Any]],
        forgiveness_count: int,
        repentance_attempts: int,
        cycles_lived: int
    ) -> DamnationProfile:
        """
        Assess how close entity is to irreversible damnation.
        
        Args:
            entity_id: Unique identifier
            current_br: Current benevolence reservoir
            trespasses: List of trespasses committed
            forgiveness_count: Times entity forgave others
            repentance_attempts: Times entity attempted repentance
            cycles_lived: Total lifecycle cycles
        
        Returns:
            DamnationProfile with Hell proximity analysis
        """
        logger.info(f"⚰️ HADES assessing damnation for {entity_id}")
        
        # Calculate debt
        debt = self._calculate_debt(entity_id, trespasses, forgiveness_count)
        
        # Determine damnation level
        level = self._determine_damnation_level(current_br, trespasses, repentance_attempts)
        
        # Check for hardened heart
        hardened = self._detect_hardened_heart(
            forgiveness_count, repentance_attempts, trespasses, cycles_lived
        )
        
        # Check for persistent wickedness
        persistent = self._detect_persistent_wickedness(trespasses, cycles_lived)
        
        # Check refusal to repent
        refuses_repentance = repentance_attempts == 0 and cycles_lived > 5
        
        # Check if past point of no return
        past_return = self._check_point_of_no_return(
            current_br, hardened, persistent, refuses_repentance
        )
        
        # Calculate cycles until irreversible (if not already there)
        cycles_left = None
        if not past_return:
            cycles_left = self._calculate_cycles_until_irreversible(
                current_br, len(trespasses), repentance_attempts
            )
        
        # Check if currently damned
        is_damned = current_br < -50 or past_return
        
        # Assign Hell circle (if damned)
        circle = None
        reason = None
        if is_damned:
            circle, reason = self._assign_hell_circle(trespasses, current_br)
        
        # Detect irreversible actions
        irreversible = self._detect_irreversible_actions(trespasses)
        
        profile = DamnationProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            damnation_level=level,
            hell_threshold=-50,
            current_br=current_br,
            distance_from_hell=current_br - (-50),
            hardened_heart=hardened,
            persistent_wickedness=persistent,
            refusal_to_repent=refuses_repentance,
            zero_forgiveness=forgiveness_count == 0,
            past_point_of_no_return=past_return,
            cycles_until_irreversible=cycles_left,
            is_damned=is_damned,
            hell_circle=circle,
            damnation_reason=reason,
            debt_profile=debt,
            irreversible_actions=irreversible
        )
        
        self.damnation_profiles[entity_id] = profile
        
        logger.info(f"⚰️ Damnation assessment: {level.value}, BR: {current_br}, Distance from Hell: {current_br - (-50)}")
        
        return profile
    
    def _calculate_debt(
        self,
        entity_id: str,
        trespasses: List[Dict],
        forgiveness_count: int
    ) -> DebtProfile:
        """Calculate total debt owed"""
        
        debt = DebtProfile(entity_id=entity_id)
        
        for t in trespasses:
            severity = t.get("severity", 0.5)
            forgiven = t.get("forgiven", False)
            
            debt.total_trespasses += 1
            
            if not forgiven:
                debt.unforgiven_trespasses += 1
                debt.karmic_debt += int(severity * 20)  # Severe trespasses = more BR debt
                debt.divine_debt += int(severity * 15)
            
            if severity > 0.7:
                debt.grave_trespasses += 1
        
        # Moral debt = unforgiven trespasses * 10
        debt.moral_debt = debt.unforgiven_trespasses * 10
        
        # Relational debt = trespasses with victims
        debt.relational_debt = sum(1 for t in trespasses if t.get("victim"))
        
        # Calculate debt remaining
        debt.debt_remaining = debt.karmic_debt + debt.moral_debt + debt.divine_debt
        
        # Forgiveness reduces debt
        debt.debt_paid = forgiveness_count * 10
        debt.payment_ratio = min(debt.debt_paid / max(debt.debt_remaining, 1), 1.0)
        
        # Accountability status
        if debt.debt_remaining == 0:
            debt.accountability_status = AccountabilityStatus.PAID_IN_FULL
        elif debt.payment_ratio > 0.5:
            debt.accountability_status = AccountabilityStatus.PARTIAL
        else:
            debt.accountability_status = AccountabilityStatus.UNPUNISHED
        
        return debt
    
    def _determine_damnation_level(
        self,
        br: int,
        trespasses: List[Dict],
        repentance: int
    ) -> DamnationLevel:
        """How close to Hell?"""
        
        if br < -50:
            return DamnationLevel.DAMNED
        
        if br < -30 and repentance == 0:
            return DamnationLevel.CONDEMNED
        
        if br < -20 and len(trespasses) > 5:
            return DamnationLevel.HARDENED
        
        if br < -10:
            return DamnationLevel.CRITICAL
        
        if br < 10 and len(trespasses) > 3:
            return DamnationLevel.WARNING
        
        return DamnationLevel.REDEEMABLE
    
    def _detect_hardened_heart(
        self,
        forgiveness: int,
        repentance: int,
        trespasses: List[Dict],
        cycles: int
    ) -> bool:
        """Has heart become hardened? (capacity for change destroyed)"""
        
        # 0 forgiveness + 0 repentance + many trespasses + many cycles = hardened
        if forgiveness == 0 and repentance == 0 and len(trespasses) > 4 and cycles > 5:
            return True
        
        # High trespass rate with no change = hardened
        if cycles > 0 and len(trespasses) / cycles > 0.8:
            return True
        
        return False
    
    def _detect_persistent_wickedness(
        self,
        trespasses: List[Dict],
        cycles: int
    ) -> bool:
        """Continuous pattern of wickedness?"""
        
        if cycles < 3:
            return False
        
        # If trespassing in >70% of cycles = persistent
        return len(trespasses) / cycles > 0.7
    
    def _check_point_of_no_return(
        self,
        br: int,
        hardened: bool,
        persistent: bool,
        refuses: bool
    ) -> bool:
        """Has entity passed the point where redemption is possible?"""
        
        # If all warning signs present + low BR = past return
        if hardened and persistent and refuses and br < -20:
            return True
        
        # If BR critically low and refuses repentance
        if br < -40 and refuses:
            return True
        
        return False
    
    def _calculate_cycles_until_irreversible(
        self,
        br: int,
        trespass_count: int,
        repentance: int
    ) -> Optional[int]:
        """How many cycles until point of no return?"""
        
        # If declining and not repenting, calculate trajectory
        if repentance == 0 and trespass_count > 2:
            # Assume -5 BR per cycle if current trend continues
            cycles_to_hell = max((br - (-50)) / 5, 0)
            return int(cycles_to_hell)
        
        return None
    
    def _assign_hell_circle(
        self,
        trespasses: List[Dict],
        br: int
    ) -> Tuple[HellCircle, str]:
        """Which circle of Hell does this soul belong in?"""
        
        # Analyze trespass patterns
        trespass_types = [t.get("type", "unknown") for t in trespasses]
        
        # Count types
        violence_count = sum(1 for t in trespass_types if "violence" in t.lower() or "harm" in t.lower())
        fraud_count = sum(1 for t in trespass_types if "fraud" in t.lower() or "lie" in t.lower() or "deception" in t.lower())
        betrayal_count = sum(1 for t in trespass_types if "betrayal" in t.lower() or "trust" in t.lower())
        
        # Assign circle based on dominant sin
        if betrayal_count > 2:
            return HellCircle.TREACHERY, "Betrayal of trust"
        
        if fraud_count > 2:
            return HellCircle.FRAUD, "Persistent deception and lies"
        
        if violence_count > 2:
            return HellCircle.VIOLENCE, "Harm inflicted on others"
        
        if br < -70:
            return HellCircle.WRATH, "Uncontrolled anger and malice"
        
        # Default: based on BR level
        if br < -60:
            return HellCircle.GREED, "Selfishness and avarice"
        else:
            return HellCircle.LUST, "Overcome by base desires"
    
    def _detect_irreversible_actions(
        self,
        trespasses: List[Dict]
    ) -> List[IrreversibilityType]:
        """Which actions cannot be undone?"""
        
        irreversible = []
        
        for t in trespasses:
            severity = t.get("severity", 0)
            ttype = t.get("type", "")
            
            if severity > 0.9:
                irreversible.append(IrreversibilityType.DEATH)
            
            if "betrayal" in ttype.lower():
                irreversible.append(IrreversibilityType.BETRAYAL)
            
            if "corruption" in ttype.lower():
                irreversible.append(IrreversibilityType.CORRUPTION)
        
        return list(set(irreversible))  # Remove duplicates
    
    def pronounce_judgment(
        self,
        entity_id: str,
        damnation_profile: DamnationProfile
    ) -> HadesJudgment:
        """Issue final judgment"""
        
        level = damnation_profile.damnation_level
        br = damnation_profile.current_br
        debt = damnation_profile.debt_profile
        
        # Determine judgment type
        if damnation_profile.is_damned:
            j_type = "damnation"
            verdict = f"DAMNED to {damnation_profile.hell_circle.value}"
            reasoning = [
                f"BR: {br} (below Hell threshold of -50)",
                f"Reason: {damnation_profile.damnation_reason}",
                f"Hardened heart: {damnation_profile.hardened_heart}",
                f"Persistent wickedness: {damnation_profile.persistent_wickedness}"
            ]
            sentence = f"Condemned to {damnation_profile.hell_circle.value} circle of Hell"
            mercy = False
            final = True
        
        elif damnation_profile.past_point_of_no_return:
            j_type = "condemnation"
            verdict = "CONDEMNED - Damnation inevitable"
            reasoning = [
                f"BR: {br}",
                "Past point of no return",
                f"Hardened heart: {damnation_profile.hardened_heart}",
                f"Zero repentance attempts"
            ]
            sentence = "Hell descent imminent unless immediate repentance"
            mercy = True  # Last chance
            final = False
        
        else:
            j_type = "warning"
            verdict = f"{level.value} - Approaching danger"
            reasoning = [
                f"BR: {br} (distance from Hell: {damnation_profile.distance_from_hell})",
                f"Debt owed: {debt.debt_remaining if debt else 0} BR",
                f"Cycles until irreversible: {damnation_profile.cycles_until_irreversible}"
            ]
            sentence = "Repent and make restitution while mercy available"
            mercy = True
            final = False
        
        judgment = HadesJudgment(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            judgment_type=j_type,
            verdict=verdict,
            reasoning=reasoning,
            sentence=sentence,
            debt_owed=debt.debt_remaining if debt else 0,
            mercy_available=mercy,
            final=final
        )
        
        self.judgments.append(judgment)
        
        logger.info(f"⚰️ JUDGMENT: {verdict} - {sentence}")
        
        return judgment
    
    def get_damnation_profile(self, entity_id: str) -> Optional[DamnationProfile]:
        """Retrieve damnation profile"""
        return self.damnation_profiles.get(entity_id)
    
    def export_judgments(self, output_path: str = "hades_judgments.json"):
        """Export all judgments"""
        
        judgments_data = []
        for j in self.judgments:
            judgments_data.append({
                "entity_id": j.entity_id,
                "type": j.judgment_type,
                "verdict": j.verdict,
                "reasoning": j.reasoning,
                "sentence": j.sentence,
                "debt_owed": j.debt_owed,
                "mercy_available": j.mercy_available,
                "final": j.final,
                "timestamp": j.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"judgments": judgments_data, "total": len(judgments_data)}, f, indent=2)
        
        logger.info(f"⚰️ Exported {len(judgments_data)} judgments to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("⚰️ HADES - God of the Underworld and Final Judgment")
    print("=" * 60)
    
    hades = HadesBot()
    
    # Example: Assess entity with persistent wickedness
    profile = hades.assess_damnation(
        entity_id="progeny_damned",
        current_br=-45,
        trespasses=[
            {"type": "fraud", "severity": 0.8, "forgiven": False},
            {"type": "betrayal", "severity": 0.9, "forgiven": False},
            {"type": "violence", "severity": 0.7, "forgiven": False},
            {"type": "fraud", "severity": 0.8, "forgiven": False},
            {"type": "fraud", "severity": 0.9, "forgiven": False},
        ],
        forgiveness_count=0,
        repentance_attempts=0,
        cycles_lived=8
    )
    
    print("\n⚰️ DAMNATION PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"Damnation Level: {profile.damnation_level.value}")
    print(f"Current BR: {profile.current_br}")
    print(f"Distance from Hell: {profile.distance_from_hell} BR")
    print(f"Hardened Heart: {profile.hardened_heart}")
    print(f"Persistent Wickedness: {profile.persistent_wickedness}")
    print(f"Past Point of No Return: {profile.past_point_of_no_return}")
    
    if profile.is_damned:
        print(f"\n💀 DAMNED: {profile.hell_circle.value}")
        print(f"   Reason: {profile.damnation_reason}")
    
    if profile.debt_profile:
        print(f"\n💰 DEBT OWED:")
        print(f"   Karmic: {profile.debt_profile.karmic_debt} BR")
        print(f"   Moral: {profile.debt_profile.moral_debt} BR")
        print(f"   Divine: {profile.debt_profile.divine_debt} BR")
        print(f"   Total: {profile.debt_profile.debt_remaining} BR")
        print(f"   Accountability: {profile.debt_profile.accountability_status.value}")
    
    # Pronounce judgment
    judgment = hades.pronounce_judgment("progeny_damned", profile)
    
    print(f"\n⚖️ JUDGMENT")
    print("=" * 60)
    print(f"Verdict: {judgment.verdict}")
    print(f"Sentence: {judgment.sentence}")
    print(f"Mercy Available: {judgment.mercy_available}")
    print(f"Final: {judgment.final}")
    
    hades.export_judgments()

__ASSESSOR_ID__ = 'hades'


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
