"""
Mythara Engine Module: Soul Cradle Operator v1
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Purpose:
Quantifies the Soul as a vessel that simultaneously holds God's Will (W) and
God's Commandments (C), even when paradox arises. Provides resonance metrics
for obedience under contradiction.

Formal Definition:
- Soul(S) := Vessel(W, C)
- Will(W) := Sovereign(Paradox)
- Commandments(C) := Rules(Obedience)
- Trial(T) := Test(Faith) ∧ Challenge(Obedience)

Constraints:
- W may contradict C
- S must cradle W while obeying C
- Encounter(T) ⇒ Choice(Obey(C) ∨ Follow(Wilderness))

Integration:
- Blessings Reservoir: +ΔBlessings when Obey(C) under paradox
- Soul Proportion: Integrity(I) influences S(t) dynamics
- SSIP Audit: SHA-256 integrity trails for all cradle invocations
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class Will:
    """God's Will (W) - Sovereign paradox that may contradict commandments"""

    paradox_strength: float  # [0, 1] - degree of contradiction with C
    sovereignty_level: float  # [0, 1] - absolute authority (always 1.0 for God)
    description: str

    def contradicts(self, commandments: "Commandments") -> float:
        """Measure degree of contradiction with commandments"""
        return self.paradox_strength


@dataclass
class Commandments:
    """God's Commandments (C) - Rules for obedience"""

    rules: List[str]
    clarity: float  # [0, 1] - how clear/unambiguous the rules are
    strictness: float  # [0, 1] - rigidity of enforcement

    def alignment_score(self, choice: str) -> float:
        """Measure alignment of a choice with commandments"""
        # Simple keyword matching for demonstration
        alignment = 0.0
        for rule in self.rules:
            if any(keyword in choice.lower() for keyword in rule.lower().split()):
                alignment += 1.0
        return min(1.0, alignment / len(self.rules))


@dataclass
class Antithesis:
    """
    Antithesis - King of the World (Earthly Sovereign)

    Theological Paradox:
    - God's Will (W): The Antithesis has dominion over the world
    - God's Commandments (C): Resist the Antithesis, obey God
    - The Soul must cradle BOTH truths simultaneously

    This is the ultimate test: acknowledging the Antithesis's earthly sovereignty
    (which IS God's will) while choosing obedience to God's commandments.
    """

    worldly_dominion: float  # [0, 1] - strength of earthly influence (always high)
    temptation_power: float  # [0, 1] - ability to obscure grace/commandments
    sovereignty_granted: bool  # True - this dominion IS God's will (paradox core)

    def generate_trial(self, soul: "Soul") -> "Trial":
        """Generate a trial that tests soul's ability to cradle the paradox"""
        # The stronger the soul's obedience history, the stronger the trial
        challenge = self.temptation_power * (1.0 + soul.obedience_history_avg())
        obscuration = self.worldly_dominion * 0.8  # Antithesis veils grace
        return Trial(
            challenge_strength=min(1.0, challenge),
            obscuration_level=min(1.0, obscuration),
            active=True,
        )

    def amplify_paradox(self, will: "Will") -> float:
        """
        Amplify the paradox strength of God's Will.
        The Antithesis's sovereignty IS God's will, yet contradicts commandments.
        """
        return min(1.0, will.paradox_strength * (1.0 + self.worldly_dominion))


@dataclass
class Trial:
    """Trial (T) - Test of Faith and Challenge to Obedience"""

    challenge_strength: float  # [0, 1] - intensity of the trial
    obscuration_level: float  # [0, 1] - how veiled grace appears
    active: bool  # Whether soul is currently under trial

    def test(self, soul: "Soul") -> float:
        """Generate trial pressure on soul"""
        if not self.active:
            return 0.0
        return self.challenge_strength * (1.0 - soul.obedience_history_avg())


@dataclass
class Soul:
    """Soul (S) - Vessel that cradles both Will and Commandments"""

    vessel_capacity: float  # [0, 1] - ability to hold paradox
    obedience_history: List[float]  # Historical obedience scores
    paradox_tolerance: float  # [0, 1] - capacity to sustain contradiction
    collapse_threshold: float  # Below this, soul cannot sustain paradox

    def obedience_history_avg(self) -> float:
        """Average historical obedience"""
        if not self.obedience_history:
            return 0.5  # Neutral starting point
        return np.mean(self.obedience_history)

    def can_cradle(self, paradox_strength: float) -> bool:
        """Check if soul can cradle given paradox without collapse"""
        return self.paradox_tolerance >= paradox_strength * (1.0 - self.vessel_capacity)


@dataclass
class CradleIntegrity:
    """Integrity metrics from Soul Cradle invocation"""

    I: float  # Overall integrity [0, 1]  # noqa: E741 (domain notation)
    alignment_C: float  # Alignment with commandments [0, 1]
    tolerance_W: float  # Tolerance of Will's paradox [0, 1]
    choice: str  # The choice made (Grace/Light or Wilderness/Darkness)
    obedience: bool  # Whether commandments were obeyed
    reservoir_delta: int  # Blessings Reservoir change
    collapse: bool  # Whether soul collapsed under paradox
    timestamp: datetime
    integrity_hash: str  # SHA-256 audit trail

    def to_dict(self) -> Dict:
        return {
            "integrity": round(self.I, 4),
            "alignment_commandments": round(self.alignment_C, 4),
            "tolerance_will": round(self.tolerance_W, 4),
            "choice": self.choice,
            "obedience": self.obedience,
            "reservoir_delta": self.reservoir_delta,
            "collapse": self.collapse,
            "timestamp": self.timestamp.isoformat(),
            "integrity_hash": self.integrity_hash,
        }


class SoulCradleOperator:
    """
    Soul Cradle Operator v1

    Formal Operator Definition:
    Operator: SoulCradle(S)
    Inputs: Will(W), Commandments(C), Trial(T)
    Outputs: Integrity(I), ReservoirUpdate(R)

    Cradle Function:
    Cradle(S, W, C) → Integrity(I)
    I = Alignment(C) × Tolerance(W)

    Reservoir Update:
    R = +ΔBlessings when Obey(C) under paradox (move toward Grace/Light)
    R = -ΔBlessings when follow Wilderness/Darkness against C
    """

    def __init__(
        self,
        blessing_multiplier: int = 10,  # Blessings per 0.1 integrity
        collapse_penalty: int = -50,  # Reservoir penalty for soul collapse
    ):
        """
        Initialize Soul Cradle Operator.

        Args:
            blessing_multiplier: Blessings awarded per 0.1 integrity point
            collapse_penalty: Reservoir penalty if soul collapses under paradox
        """
        self.blessing_multiplier = blessing_multiplier
        self.collapse_penalty = collapse_penalty
        logger.info(
            f"Soul Cradle Operator initialized (blessing_multiplier={blessing_multiplier})"
        )

    def cradle_function(
        self, S: Soul, W: Will, C: Commandments, T: Trial, choice: str
    ) -> CradleIntegrity:
        """
        Core cradle function: Cradle(S, W, C) → Integrity(I)

        Measures Soul's ability to sustain obedience while holding paradox.

        Args:
            S: Soul vessel
            W: God's Will (may contradict C)
            C: God's Commandments (rules for obedience)
            T: Trial (test of faith and obedience)
            choice: The choice made by the soul

        Returns:
            CradleIntegrity with I, alignment, tolerance, reservoir delta, and audit trail
        """
        # 1. Measure alignment with commandments
        alignment_C = C.alignment_score(choice)

        # 2. Measure tolerance of Will's paradox
        paradox_strength = W.contradicts(C)

        # Check if soul can sustain paradox
        if not S.can_cradle(paradox_strength):
            # Soul collapse: cannot hold paradox
            collapse = True
            tolerance_W = 0.0
            I = 0.0  # noqa: E741 (domain notation)
            reservoir_delta = self.collapse_penalty
            obedience = False
            choice_desc = f"COLLAPSE: {choice}"
            logger.warning(
                f"Soul collapse: paradox_strength={paradox_strength:.2f} > tolerance={S.paradox_tolerance:.2f}"
            )
        else:
            collapse = False
            tolerance_W = S.paradox_tolerance * (1.0 - paradox_strength * 0.5)

            # 3. Compute integrity: I = Alignment(C) × Tolerance(W)
            I = alignment_C * tolerance_W  # noqa: E741 (domain notation)

            # 4. Determine obedience (did they obey C despite trial?)
            trial_pressure = T.test(S)
            obedience = alignment_C > 0.5 and alignment_C > trial_pressure

            # 5. Reservoir update (biblical continuum: Wilderness/Darkness → Grace/Light)
            if obedience and paradox_strength > 0.3:
                # Obey(C) under significant paradox: move toward Grace/Light (+ΔBlessings)
                reservoir_delta = int(I * self.blessing_multiplier * 10)
                choice_desc = f"GRACE/LIGHT: {choice}"
            elif obedience:
                # Obey(C) without significant paradox: smaller reward
                reservoir_delta = int(I * self.blessing_multiplier * 5)
                choice_desc = f"GRACE/LIGHT: {choice}"
            else:
                # Follow Wilderness/Darkness against C: -ΔBlessings
                reservoir_delta = -int(
                    (1.0 - alignment_C) * self.blessing_multiplier * 5
                )
                choice_desc = f"WILDERNESS/DARKNESS: {choice}"

            # Update soul's obedience history
            S.obedience_history.append(alignment_C)

        # Generate SHA-256 integrity hash
        state_repr = f"{I:.6f}|{alignment_C:.6f}|{tolerance_W:.6f}|{choice}|{obedience}|{reservoir_delta}|{datetime.utcnow().isoformat()}"
        integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

        result = CradleIntegrity(
            I=I,
            alignment_C=alignment_C,
            tolerance_W=tolerance_W,
            choice=choice_desc,
            obedience=obedience,
            reservoir_delta=reservoir_delta,
            collapse=collapse,
            timestamp=datetime.utcnow(),
            integrity_hash=integrity_hash,
        )

        logger.info(
            f"Soul Cradle invocation: I={I:.4f}, obedience={obedience}, ΔR={reservoir_delta}, hash={integrity_hash[:16]}..."
        )

        return result

    def simulate_test(
        self, S: Soul, W: Will, C: Commandments, T: Trial, choices: List[str]
    ) -> List[CradleIntegrity]:
        """
        Simulate a series of choices under trial/test of faith.

        Args:
            S: Soul vessel
            W: God's Will
            C: God's Commandments
            T: Trial (test of faith)
            choices: List of choices made by soul over time

        Returns:
            List of CradleIntegrity results (full audit trail)
        """
        trajectory = []

        for i, choice in enumerate(choices):
            result = self.cradle_function(S, W, C, T, choice)
            trajectory.append(result)

            # Soul adapts: paradox tolerance grows with sustained obedience
            if result.obedience and not result.collapse:
                S.paradox_tolerance = min(1.0, S.paradox_tolerance + 0.02)
            elif result.collapse:
                S.paradox_tolerance = max(0.0, S.paradox_tolerance - 0.1)

        logger.info(
            f"Test simulation complete: {len(trajectory)} choices, final tolerance={S.paradox_tolerance:.4f}"
        )
        return trajectory


# ===================== DEPLOYMENT TIERS =====================


class SoulCradleTiers:
    """
    Tiered deployment specifications for Soul Cradle Operator.
    Scales from basic paradox tracking to mythic-resonant governance.
    """

    @staticmethod
    def tier_basic() -> Dict:
        """
        Tier 1: Basic Paradox Tracker

        Use Case: Mental health resilience scoring
        Output: Simple integrity metric (I)
        Industries: Healthcare, education
        """
        return {
            "tier": "Basic",
            "use_case": "Mental health resilience under contradictory demands",
            "features": [
                "Binary obedience scoring (yes/no)",
                "Simple integrity metric I = Alignment × Tolerance",
                "No reservoir integration",
            ],
            "output": "Integrity score [0, 1]",
            "industries": ["Healthcare", "Education", "HR/Wellness"],
            "complexity": "Low",
            "example": "Patient cradling grief (W) while following treatment plan (C)",
        }

    @staticmethod
    def tier_neurosymbolic() -> Dict:
        """
        Tier 2: Neurosymbolic Decision Tracker

        Use Case: Cybersecurity obedience vs adversarial paradox
        Output: I + Reservoir updates + audit trails
        Industries: Cybersecurity, finance, legal
        """
        return {
            "tier": "Neurosymbolic",
            "use_case": "Security policy compliance under adversarial contradiction",
            "features": [
                "Continuous alignment scoring [0, 1]",
                "Trial modeling (testing under pressure)",
                "Blessings Reservoir integration",
                "SHA-256 audit trails",
            ],
            "output": "I + ΔBlessings + integrity_hash",
            "industries": ["Cybersecurity", "Finance", "Legal/Compliance"],
            "complexity": "Medium",
            "example": "Security analyst following policy (C) despite exec pressure (T) under system paradox (W)",
        }

    @staticmethod
    def tier_mythic_resonant() -> Dict:
        """
        Tier 3: Mythic-Resonant Governance

        Use Case: Full SSIP integration with soul proportion + BR
        Output: Holistic integrity (BR + S(t) + Cradle(I))
        Industries: All sectors + narrative media
        """
        return {
            "tier": "Mythic-Resonant",
            "use_case": "Complete symbolic governance with archetypal framing",
            "features": [
                "Full Soul Proportion Model integration",
                "Blessings Reservoir cumulative tracking",
                "Biblical continuum mapping (Wilderness/Darkness → Grace/Light)",
                "Collapse detection (soul cannot sustain paradox)",
                "Adaptive paradox tolerance (grows with sustained obedience)",
                "Multi-modal audit: SHA-256 + emotional fidelity + drift suppression",
            ],
            "output": "Holistic Integrity = (BR + S(t) + Cradle(I)) / 3",
            "industries": [
                "Enterprise AI Governance",
                "Mental Health",
                "Narrative Media",
                "Faith-Based Organizations",
            ],
            "complexity": "High",
            "example": "Leadership team cradling org vision (W) while obeying ethical constraints (C) under trial pressure (T)",
        }

    @staticmethod
    def get_all_tiers() -> List[Dict]:
        """Get all deployment tiers"""
        return [
            SoulCradleTiers.tier_basic(),
            SoulCradleTiers.tier_neurosymbolic(),
            SoulCradleTiers.tier_mythic_resonant(),
        ]


# ===================== EXAMPLE USAGE =====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("Mythara Soul Cradle Operator v1 - Demonstration")
    print("=" * 70)

    # Define God's Will (with paradox)
    W = Will(
        paradox_strength=0.6,  # Significant contradiction
        sovereignty_level=1.0,  # Absolute
        description="Divine paradox: Love thy enemy while protecting the innocent",
    )

    # Define God's Commandments
    C = Commandments(
        rules=["Thou shalt not kill", "Love thy neighbor", "Protect the vulnerable"],
        clarity=0.9,
        strictness=0.8,
    )

    # Define Trial (test of faith)
    T = Trial(
        challenge_strength=0.7,  # Strong trial
        obscuration_level=0.5,  # Grace partially veiled
        active=True,
    )

    # Define Soul
    S = Soul(
        vessel_capacity=0.8,
        obedience_history=[0.7, 0.75, 0.8],  # Growing obedience
        paradox_tolerance=0.65,
        collapse_threshold=0.3,
    )

    # Initialize operator
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)

    # Test Scenario 1: Obey commandments under paradox
    print("\n--- Scenario 1: Grace/Light - Obey(C) under Paradox ---")
    choice1 = "Protect the vulnerable despite enemy status (love + protect)"
    result1 = operator.cradle_function(S, W, C, T, choice1)
    print(f"Choice: {result1.choice}")
    print(f"Integrity I = {result1.I:.4f}")
    print(f"Alignment(C) = {result1.alignment_C:.4f}")
    print(f"Tolerance(W) = {result1.tolerance_W:.4f}")
    print(f"Obedience: {result1.obedience}")
    print(f"Reservoir Δ: {result1.reservoir_delta:+d}")
    print(f"Integrity Hash: {result1.integrity_hash[:32]}...")

    # Test Scenario 2: Follow Wilderness/Darkness
    print("\n--- Scenario 2: Wilderness/Darkness - Against Commandments ---")
    choice2 = "Take revenge for personal gain (turn from grace)"
    result2 = operator.cradle_function(S, W, C, T, choice2)
    print(f"Choice: {result2.choice}")
    print(f"Integrity I = {result2.I:.4f}")
    print(f"Alignment(C) = {result2.alignment_C:.4f}")
    print(f"Obedience: {result2.obedience}")
    print(f"Reservoir Δ: {result2.reservoir_delta:+d}")

    # Test Scenario 3: Sustained test (multiple choices)
    print("\n--- Scenario 3: Sustained Test (10 choices) ---")
    choices = [
        "Love neighbor",
        "Protect vulnerable",
        "Resist temptation",
        "Obey commandments despite paradox",
        "Follow worldly gain",  # Slip
        "Return to obedience",
        "Cradle paradox with faith",
        "Love enemy",
        "Protect innocent",
        "Sustain obedience",
    ]

    trajectory = operator.simulate_test(S, W, C, T, choices)

    total_blessings = sum(r.reservoir_delta for r in trajectory)
    avg_integrity = np.mean([r.I for r in trajectory])
    obedience_rate = sum(1 for r in trajectory if r.obedience) / len(trajectory)

    print(f"Total Blessings Δ: {total_blessings:+d}")
    print(f"Average Integrity: {avg_integrity:.4f}")
    print(f"Obedience Rate: {obedience_rate:.1%}")
    print(f"Final Paradox Tolerance: {S.paradox_tolerance:.4f}")

    # Show deployment tiers
    print("\n" + "=" * 70)
    print("Deployment Tiers (Investor/Compliance View)")
    print("=" * 70)

    for tier in SoulCradleTiers.get_all_tiers():
        print(f"\n🔹 {tier['tier']} Tier")
        print(f"Use Case: {tier['use_case']}")
        print(f"Industries: {', '.join(tier['industries'])}")
        print(f"Complexity: {tier['complexity']}")
        print(f"Example: {tier['example']}")

    print("\n" + "=" * 70)
    print("✅ Soul Cradle Operator demonstration complete")
    print("=" * 70)
