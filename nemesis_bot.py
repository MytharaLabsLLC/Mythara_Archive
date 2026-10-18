"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

NEMESIS - Goddess of Divine Retribution and Righteous Vengeance
================================================================
The GODBOT that enforces cosmic justice and balances the scales.

While Hades judges and Persephone offers mercy, Nemesis ENSURES JUSTICE IS SERVED:
- Detects hubris (excessive pride that defies divine order)
- Calculates retribution owed (what punishment fits the crime?)
- Identifies those who escaped accountability
- Tracks cosmic imbalance (unpunished evil creates debt)
- Enforces proportional punishment (not too harsh, not too lenient)
- Delivers righteous vengeance (justice for victims)

Nemesis is not cruel - she is FAIR:
- Punishes the arrogant who abuse power
- Protects the innocent from oppressors
- Ensures no one is "too big to fail" or "above the law"
- Balances excessive fortune with proportional downfall
- Prevents escape through wealth, status, or manipulation

In Soul Cradle context:
- Identifies Progeny who trespassed but escaped consequences
- Calculates EXACT retribution required (precise, proportional)
- Detects hubris patterns (entities who think they're above BR mechanics)
- Enforces delayed justice (some debts come due later)
- Balances cosmic scales (victim gains what oppressor loses)

Nemesis answers: "Who got away with it, and what must they pay?"

The Goddess who ensures NO ONE escapes justice.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json


logger = logging.getLogger(__name__)


class HubrisLevel(str, Enum):
    """Degree of arrogance and pride"""
    HUMBLE = "Humble"  # Appropriate self-awareness
    CONFIDENT = "Confident"  # Healthy self-esteem
    ARROGANT = "Arrogant"  # Excessive pride, dismissive of others
    HUBRIS = "Hubris"  # Defying divine/cosmic order
    TYRANNICAL = "Tyrannical"  # Oppressing others through power
    BLASPHEMOUS = "Blasphemous"  # Claiming divine status


class JusticeStatus(str, Enum):
    """Has justice been served?"""
    BALANCED = "Balanced"  # Justice served, scales even
    PARTIAL = "Partial"  # Some consequences, but not enough
    ESCAPED = "Escaped"  # Avoided all consequences
    DELAYED = "Delayed"  # Justice coming, but not yet delivered
    OVERDUE = "Overdue"  # Justice long delayed, debt growing
    IMMUNE = "Immune"  # Protected from consequences (wealth/power/status)


class RetributionType(str, Enum):
    """Form of cosmic punishment"""
    LOSS_OF_STATUS = "Loss_of_Status"  # Fall from high position
    LOSS_OF_WEALTH = "Loss_of_Wealth"  # Financial ruin
    LOSS_OF_POWER = "Loss_of_Power"  # Authority stripped
    LOSS_OF_REPUTATION = "Loss_of_Reputation"  # Public shame/exposure
    LOSS_OF_HEALTH = "Loss_of_Health"  # Physical/mental deterioration
    LOSS_OF_RELATIONSHIPS = "Loss_of_Relationships"  # Isolation, betrayal
    DIVINE_PUNISHMENT = "Divine_Punishment"  # Direct cosmic intervention


class VictimizationSeverity(str, Enum):
    """How badly were victims harmed?"""
    MINIMAL = "Minimal"  # Minor inconvenience
    MODERATE = "Moderate"  # Significant harm
    SEVERE = "Severe"  # Life-altering damage
    DEVASTATING = "Devastating"  # Irreversible destruction
    GENOCIDAL = "Genocidal"  # Mass victimization


class EscapeMechanism(str, Enum):
    """How did they avoid consequences?"""
    NONE = "None"  # Did not escape
    WEALTH = "Wealth"  # Bought their way out
    POWER = "Power"  # Used authority to suppress justice
    STATUS = "Status"  # "Too important" to punish
    MANIPULATION = "Manipulation"  # Lied/deceived to avoid consequences
    LEGAL_LOOPHOLES = "Legal_Loopholes"  # Exploited system flaws
    CORRUPTION = "Corruption"  # Bribed/corrupted justice system


@dataclass
class UnpunishedTrespass:
    """Crime that escaped justice"""
    trespass_type: str
    severity: float  # 0.0 to 1.0
    victim_count: int
    br_debt: int  # BR owed but not paid
    date: datetime
    escape_mechanism: EscapeMechanism
    statute_expired: bool = False  # Too late for normal justice


@dataclass
class RetributionProfile:
    """Calculation of punishment owed"""
    entity_id: str
    timestamp: datetime
    
    # Hubris assessment
    hubris_level: HubrisLevel
    hubris_patterns: List[str]  # Specific arrogant behaviors
    
    # Justice status
    justice_status: JusticeStatus
    unpunished_trespasses: List[UnpunishedTrespass]
    total_victims: int
    victimization_severity: VictimizationSeverity
    
    # Escape analysis
    escape_mechanisms: List[EscapeMechanism]
    accountability_shield: List[str]  # What protects them? (wealth, power, status)
    
    # Retribution calculation
    retribution_owed: int  # BR debt
    retribution_types: List[RetributionType]
    proportionality_ratio: float  # How much punishment fits crime?
    
    # Timing
    days_since_trespass: int
    justice_delay_multiplier: float  # Debt grows over time
    retribution_due_date: datetime
    
    # Cosmic balance
    cosmic_imbalance: int  # How much universe is "out of balance"
    victim_restitution_required: int  # BR that must go to victims


@dataclass
class NemesisJudgment:
    """Divine retribution decree"""
    entity_id: str
    timestamp: datetime
    judgment_type: str  # "retribution", "restitution", "cosmic_balance"
    verdict: str
    retribution_decreed: List[RetributionType]
    br_cost: int
    victim_compensation: int
    enforcement_method: str  # How will this be delivered?
    inevitable: bool  # Can this be avoided?


class NemesisBot:
    """
    NEMESIS - Goddess of Divine Retribution and Righteous Vengeance
    
    Specializes in:
    - Hubris detection (arrogance that defies cosmic order)
    - Unpunished trespass identification (who got away with it?)
    - Retribution calculation (what punishment is owed?)
    - Justice delay tracking (how long has justice been denied?)
    - Cosmic balance enforcement (restoring equilibrium)
    - Victim restitution (compensating those harmed)
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.retribution_profiles: Dict[str, RetributionProfile] = {}
        self.judgments_issued: List[NemesisJudgment] = []
        
        logger.info("⚖️ NEMESIS - Goddess of Divine Retribution initialized")
        print("⚖️ NEMESIS - Goddess of Divine Retribution and Righteous Vengeance")
        print("   The GODBOT who ensures NO ONE escapes justice")
    
    def assess_retribution(
        self,
        entity_id: str,
        current_br: int,
        trespasses: List[Dict[str, Any]],
        consequences_paid: List[Dict[str, Any]],
        current_status: str,  # "wealthy", "powerful", "famous", "ordinary"
        cycles_lived: int
    ) -> RetributionProfile:
        """
        Assess what retribution is owed for unpunished crimes.
        
        Args:
            entity_id: Unique identifier
            current_br: Current benevolence reservoir
            trespasses: All trespasses committed
            consequences_paid: Consequences already suffered
            current_status: Social/economic status (escape mechanism indicator)
            cycles_lived: Total cycles
        
        Returns:
            RetributionProfile with punishment calculation
        """
        logger.info(f"⚖️ NEMESIS assessing retribution for {entity_id}")
        
        # Detect hubris
        hubris_level, hubris_patterns = self._detect_hubris(
            current_br, current_status, trespasses, consequences_paid
        )
        
        # Identify unpunished trespasses
        unpunished = self._identify_unpunished_trespasses(
            trespasses, consequences_paid, cycles_lived
        )
        
        # Determine justice status
        justice_status = self._determine_justice_status(
            unpunished, len(consequences_paid), len(trespasses)
        )
        
        # Analyze escape mechanisms
        escape_mechanisms, shields = self._analyze_escape_mechanisms(
            unpunished, current_status
        )
        
        # Calculate victim impact
        total_victims, severity = self._calculate_victim_impact(unpunished)
        
        # Calculate retribution owed
        retribution_owed, types, proportionality = self._calculate_retribution(
            unpunished, hubris_level, current_status
        )
        
        # Calculate justice delay multiplier
        delay_multiplier, days_since = self._calculate_justice_delay(unpunished)
        
        # Calculate cosmic imbalance
        cosmic_imbalance = self._calculate_cosmic_imbalance(
            retribution_owed, len(unpunished), severity
        )
        
        # Calculate victim restitution
        victim_restitution = self._calculate_victim_restitution(unpunished)
        
        # Determine when retribution is due
        due_date = self._calculate_retribution_due_date(
            days_since, justice_status, hubris_level
        )
        
        profile = RetributionProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            hubris_level=hubris_level,
            hubris_patterns=hubris_patterns,
            justice_status=justice_status,
            unpunished_trespasses=unpunished,
            total_victims=total_victims,
            victimization_severity=severity,
            escape_mechanisms=escape_mechanisms,
            accountability_shield=shields,
            retribution_owed=retribution_owed,
            retribution_types=types,
            proportionality_ratio=proportionality,
            days_since_trespass=days_since,
            justice_delay_multiplier=delay_multiplier,
            retribution_due_date=due_date,
            cosmic_imbalance=cosmic_imbalance,
            victim_restitution_required=victim_restitution
        )
        
        self.retribution_profiles[entity_id] = profile
        
        logger.info(f"⚖️ Retribution: {retribution_owed} BR, Status: {justice_status.value}, Hubris: {hubris_level.value}")
        
        return profile
    
    def _detect_hubris(
        self,
        br: int,
        status: str,
        trespasses: List[Dict],
        consequences: List[Dict]
    ) -> Tuple[HubrisLevel, List[str]]:
        """Detect arrogance and pride"""
        
        patterns = []
        
        # High status + many trespasses + few consequences = hubris
        if status in ["wealthy", "powerful", "famous"] and len(trespasses) > 5 and len(consequences) < 2:
            patterns.append("Believes status protects from consequences")
            patterns.append("Pattern of trespassing without accountability")
            return HubrisLevel.HUBRIS, patterns
        
        # Positive BR despite many trespasses = escaped justice
        if br > 20 and len(trespasses) > 3:
            patterns.append("Maintains good standing despite crimes")
            return HubrisLevel.ARROGANT, patterns
        
        # High status alone doesn't mean hubris
        if status in ["wealthy", "powerful"] and len(trespasses) < 2:
            patterns.append("High status but limited trespasses")
            return HubrisLevel.CONFIDENT, patterns
        
        return HubrisLevel.HUMBLE, []
    
    def _identify_unpunished_trespasses(
        self,
        trespasses: List[Dict],
        consequences: List[Dict],
        cycles: int
    ) -> List[UnpunishedTrespass]:
        """Find crimes that escaped justice"""
        
        unpunished = []
        
        # Assume 1 consequence per trespass is "justice"
        unpunished_count = len(trespasses) - len(consequences)
        
        if unpunished_count <= 0:
            return []
        
        # Take most recent trespasses as unpunished
        for t in trespasses[-unpunished_count:]:
            days_ago = cycles * 30  # Rough estimate
            
            unpunished.append(UnpunishedTrespass(
                trespass_type=t.get("type", "unknown"),
                severity=t.get("severity", 0.5),
                victim_count=t.get("victim_count", 1),
                br_debt=int(t.get("severity", 0.5) * 50),
                date=datetime.utcnow() - timedelta(days=days_ago),
                escape_mechanism=EscapeMechanism.NONE,
                statute_expired=False
            ))
        
        return unpunished
    
    def _determine_justice_status(
        self,
        unpunished: List[UnpunishedTrespass],
        consequence_count: int,
        trespass_count: int
    ) -> JusticeStatus:
        """Has justice been served?"""
        
        if not unpunished:
            return JusticeStatus.BALANCED
        
        ratio = consequence_count / max(trespass_count, 1)
        
        if ratio < 0.2:
            return JusticeStatus.ESCAPED
        elif ratio < 0.5:
            return JusticeStatus.DELAYED
        elif ratio < 0.8:
            return JusticeStatus.PARTIAL
        else:
            return JusticeStatus.OVERDUE
    
    def _analyze_escape_mechanisms(
        self,
        unpunished: List[UnpunishedTrespass],
        status: str
    ) -> Tuple[List[EscapeMechanism], List[str]]:
        """How did they avoid consequences?"""
        
        mechanisms = []
        shields = []
        
        if status == "wealthy":
            mechanisms.append(EscapeMechanism.WEALTH)
            shields.append("Financial resources shield from consequences")
        
        if status == "powerful":
            mechanisms.append(EscapeMechanism.POWER)
            shields.append("Authority suppresses accountability")
        
        if status == "famous":
            mechanisms.append(EscapeMechanism.STATUS)
            shields.append("Public profile provides protection")
        
        if not mechanisms:
            mechanisms.append(EscapeMechanism.NONE)
        
        return mechanisms, shields
    
    def _calculate_victim_impact(
        self,
        unpunished: List[UnpunishedTrespass]
    ) -> Tuple[int, VictimizationSeverity]:
        """How badly were victims harmed?"""
        
        total_victims = sum(t.victim_count for t in unpunished)
        avg_severity = sum(t.severity for t in unpunished) / max(len(unpunished), 1)
        
        if total_victims > 100:
            severity = VictimizationSeverity.GENOCIDAL
        elif avg_severity > 0.8:
            severity = VictimizationSeverity.DEVASTATING
        elif avg_severity > 0.6:
            severity = VictimizationSeverity.SEVERE
        elif avg_severity > 0.4:
            severity = VictimizationSeverity.MODERATE
        else:
            severity = VictimizationSeverity.MINIMAL
        
        return total_victims, severity
    
    def _calculate_retribution(
        self,
        unpunished: List[UnpunishedTrespass],
        hubris: HubrisLevel,
        status: str
    ) -> Tuple[int, List[RetributionType], float]:
        """What punishment is owed?"""
        
        # Base debt
        base_debt = sum(t.br_debt for t in unpunished)
        
        # Hubris multiplier
        hubris_multipliers = {
            HubrisLevel.HUMBLE: 1.0,
            HubrisLevel.CONFIDENT: 1.0,
            HubrisLevel.ARROGANT: 1.5,
            HubrisLevel.HUBRIS: 2.0,
            HubrisLevel.TYRANNICAL: 3.0,
            HubrisLevel.BLASPHEMOUS: 5.0
        }
        
        multiplier = hubris_multipliers.get(hubris, 1.0)
        total_debt = int(base_debt * multiplier)
        
        # Determine retribution types
        types = []
        
        if status == "wealthy":
            types.append(RetributionType.LOSS_OF_WEALTH)
        
        if status == "powerful":
            types.append(RetributionType.LOSS_OF_POWER)
        
        if status == "famous":
            types.append(RetributionType.LOSS_OF_REPUTATION)
        
        if hubris in [HubrisLevel.HUBRIS, HubrisLevel.TYRANNICAL]:
            types.append(RetributionType.LOSS_OF_STATUS)
        
        if not types:
            types.append(RetributionType.DIVINE_PUNISHMENT)
        
        # Proportionality (1.0 = perfectly proportional)
        proportionality = 1.0  # Nemesis is ALWAYS proportional
        
        return total_debt, types, proportionality
    
    def _calculate_justice_delay(
        self,
        unpunished: List[UnpunishedTrespass]
    ) -> Tuple[float, int]:
        """How long has justice been delayed?"""
        
        if not unpunished:
            return 1.0, 0
        
        # Average days since trespass
        days = [
            (datetime.utcnow() - t.date).days
            for t in unpunished
        ]
        
        avg_days = sum(days) / len(days)
        
        # Debt grows 10% per month delayed
        months_delayed = avg_days / 30
        multiplier = 1.0 + (months_delayed * 0.1)
        
        return multiplier, int(avg_days)
    
    def _calculate_cosmic_imbalance(
        self,
        retribution_owed: int,
        unpunished_count: int,
        severity: VictimizationSeverity
    ) -> int:
        """How out of balance is the universe?"""
        
        severity_weights = {
            VictimizationSeverity.MINIMAL: 1,
            VictimizationSeverity.MODERATE: 2,
            VictimizationSeverity.SEVERE: 4,
            VictimizationSeverity.DEVASTATING: 8,
            VictimizationSeverity.GENOCIDAL: 16
        }
        
        weight = severity_weights.get(severity, 1)
        
        return retribution_owed * weight * unpunished_count
    
    def _calculate_victim_restitution(
        self,
        unpunished: List[UnpunishedTrespass]
    ) -> int:
        """BR that must go to victims"""
        
        # 60% of debt goes to victims, 40% to cosmic justice
        total_debt = sum(t.br_debt for t in unpunished)
        return int(total_debt * 0.6)
    
    def _calculate_retribution_due_date(
        self,
        days_since: int,
        status: JusticeStatus,
        hubris: HubrisLevel
    ) -> datetime:
        """When will retribution arrive?"""
        
        # Overdue = immediate
        if status == JusticeStatus.OVERDUE:
            return datetime.utcnow()
        
        # High hubris = faster retribution
        if hubris in [HubrisLevel.HUBRIS, HubrisLevel.TYRANNICAL, HubrisLevel.BLASPHEMOUS]:
            return datetime.utcnow() + timedelta(days=30)
        
        # Default: within 90 days
        return datetime.utcnow() + timedelta(days=90)
    
    def decree_retribution(
        self,
        entity_id: str,
        profile: RetributionProfile
    ) -> NemesisJudgment:
        """Issue divine retribution decree"""
        
        judgment = NemesisJudgment(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            judgment_type="retribution",
            verdict=f"{profile.hubris_level.value} entity with {len(profile.unpunished_trespasses)} unpunished trespasses must face justice",
            retribution_decreed=profile.retribution_types,
            br_cost=profile.retribution_owed,
            victim_compensation=profile.victim_restitution_required,
            enforcement_method="Divine intervention - inevitable consequences",
            inevitable=True
        )
        
        self.judgments_issued.append(judgment)
        
        logger.info(f"⚖️ NEMESIS DECREE: {entity_id} owes {profile.retribution_owed} BR")
        
        return judgment
    
    def get_retribution_profile(self, entity_id: str) -> Optional[RetributionProfile]:
        """Retrieve retribution profile"""
        return self.retribution_profiles.get(entity_id)
    
    def export_judgments(self, output_path: str = "nemesis_judgments.json"):
        """Export all retribution decrees"""
        
        judgments_data = []
        for j in self.judgments_issued:
            judgments_data.append({
                "entity_id": j.entity_id,
                "type": j.judgment_type,
                "verdict": j.verdict,
                "retribution": [r.value for r in j.retribution_decreed],
                "br_cost": j.br_cost,
                "victim_compensation": j.victim_compensation,
                "enforcement": j.enforcement_method,
                "inevitable": j.inevitable,
                "timestamp": j.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"judgments": judgments_data, "total": len(judgments_data)}, f, indent=2)
        
        logger.info(f"⚖️ Exported {len(judgments_data)} judgments to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("⚖️ NEMESIS - Goddess of Divine Retribution and Righteous Vengeance")
    print("=" * 60)
    
    nemesis = NemesisBot()
    
    # Example: Wealthy entity who committed crimes but escaped consequences
    profile = nemesis.assess_retribution(
        entity_id="oligarch_escaped",
        current_br=45,  # Still high despite crimes!
        trespasses=[
            {"type": "fraud", "severity": 0.8, "victim_count": 50},
            {"type": "exploitation", "severity": 0.7, "victim_count": 200},
            {"type": "corruption", "severity": 0.9, "victim_count": 10},
            {"type": "environmental_destruction", "severity": 0.85, "victim_count": 5000},
        ],
        consequences_paid=[],  # NO consequences yet!
        current_status="wealthy",
        cycles_lived=8
    )
    
    print("\n⚖️ RETRIBUTION PROFILE")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"Hubris Level: {profile.hubris_level.value}")
    print(f"Justice Status: {profile.justice_status.value}")
    print(f"Current BR: +45 (unjustly high)")
    print(f"Unpunished Trespasses: {len(profile.unpunished_trespasses)}")
    print(f"Total Victims: {profile.total_victims}")
    print(f"Victimization Severity: {profile.victimization_severity.value}")
    
    if profile.hubris_patterns:
        print(f"\n🎭 HUBRIS PATTERNS:")
        for pattern in profile.hubris_patterns:
            print(f"   • {pattern}")
    
    if profile.escape_mechanisms:
        print(f"\n🛡️ ESCAPE MECHANISMS:")
        for mech in profile.escape_mechanisms:
            print(f"   • {mech.value}")
    
    if profile.accountability_shield:
        print(f"\n🛡️ ACCOUNTABILITY SHIELDS:")
        for shield in profile.accountability_shield:
            print(f"   • {shield}")
    
    print(f"\n💰 RETRIBUTION OWED:")
    print(f"   Total Debt: {profile.retribution_owed} BR")
    print(f"   Proportionality: {profile.proportionality_ratio:.1f} (1.0 = perfect)")
    print(f"   Justice Delay Multiplier: {profile.justice_delay_multiplier:.2f}x")
    print(f"   Days Since Trespass: {profile.days_since_trespass}")
    
    print(f"\n⚔️ RETRIBUTION TYPES:")
    for rtype in profile.retribution_types:
        print(f"   • {rtype.value}")
    
    print(f"\n🌍 COSMIC IMBALANCE: {profile.cosmic_imbalance}")
    print(f"💝 VICTIM RESTITUTION: {profile.victim_restitution_required} BR")
    print(f"⏰ RETRIBUTION DUE: {profile.retribution_due_date.strftime('%Y-%m-%d')}")
    
    # Issue decree
    judgment = nemesis.decree_retribution(profile.entity_id, profile)
    
    print(f"\n⚖️ NEMESIS DECREE")
    print("=" * 60)
    print(f"Verdict: {judgment.verdict}")
    print(f"BR Cost: {judgment.br_cost}")
    print(f"Victim Compensation: {judgment.victim_compensation} BR")
    print(f"Enforcement: {judgment.enforcement_method}")
    print(f"Inevitable: {judgment.inevitable}")
    
    nemesis.export_judgments()

__ASSESSOR_ID__ = 'nemesis'


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
