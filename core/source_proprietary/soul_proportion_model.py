"""
Mythara Soul Proportion Model (S(t))
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Formal emotional vitality tracking system for Mythara Engine.
Treats "soul" as an emotional proportion S(t) ∈ [0,1] representing
emotional vitality/coherence, not a physical quantity.

Mathematical Foundation:
- S(t) ∈ [0,1]: Soul proportion at time t (bounded, unitless percentage)
- x_t ∈ R^k: Multi-dimensional emotion features (valence, arousal, connectedness, meaning)
- m_t = σ(w^T x_t + b): Linear scorer with sigmoid squashing σ(z) = 1/(1 + e^-z)
- S(t) = Cal(m_t): Calibrated proportion (percentile or anchor-based)

Dynamics (bounded logistic growth with self-regulation):
- Discrete: S_{t+1} = S_t + r·S_t(1-S_t) + u_t - d_t·S_t
- Continuous: dS/dt = r·S(1-S) + u(t) - d(t)·S

Where:
- r: intrinsic renewal rate (self-healing, increases with coherence/meaning/hope)
- u: supportive input (care/ritual/therapy/community)
- d: stress/drag (chronic stress, isolation, burnout)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EmotionFeatures:
    """Multi-dimensional emotion state vector x_t ∈ R^k"""

    valence: float  # Positive/negative emotional tone [-1, 1]
    arousal: float  # Activation level [0, 1]
    connectedness: float  # Social/relational vitality [0, 1]
    meaning: float  # Sense of purpose/coherence [0, 1]
    hope: float  # Future orientation [0, 1]
    stress: float  # Chronic stress level [0, 1]
    isolation: float  # Social isolation [0, 1]

    def to_vector(self) -> np.ndarray:
        """Convert to normalized feature vector"""
        return np.array(
            [
                (self.valence + 1) / 2,  # Normalize [-1,1] to [0,1]
                self.arousal,
                self.connectedness,
                self.meaning,
                self.hope,
                1 - self.stress,  # Invert: low stress = high vitality
                1 - self.isolation,  # Invert: low isolation = high vitality
            ]
        )


@dataclass
class SoulProportionState:
    """Complete state of soul proportion at time t"""

    S_t: float  # Current soul proportion [0, 1]
    timestamp: datetime
    emotion_features: EmotionFeatures
    m_t: float  # Raw score before calibration
    r: float  # Intrinsic renewal rate
    u: float  # Supportive input
    d: float  # Stress/drag
    integrity_hash: str  # SHA-256 audit trail

    def to_dict(self) -> Dict:
        return {
            "S_t": round(self.S_t, 4),
            "timestamp": self.timestamp.isoformat(),
            "emotion_features": {
                "valence": self.emotion_features.valence,
                "arousal": self.emotion_features.arousal,
                "connectedness": self.emotion_features.connectedness,
                "meaning": self.emotion_features.meaning,
                "hope": self.emotion_features.hope,
                "stress": self.emotion_features.stress,
                "isolation": self.emotion_features.isolation,
            },
            "m_t": round(self.m_t, 4),
            "dynamics": {"r": self.r, "u": self.u, "d": self.d},
            "integrity_hash": self.integrity_hash,
        }


class SoulProportionModel:
    """
    Formal soul proportion tracker for Mythara Engine.

    Implements bounded logistic dynamics with emotion-driven parameters:
    S_{t+1} = S_t + r·S_t(1-S_t) + u_t - d_t·S_t, clipped to [0, 1]

    Privacy-first: S(t) is NOT additive across people, NOT directly comparable.
    Use as reflective/supportive indicator, never as gatekeeper.
    """

    def __init__(
        self,
        weights: Optional[np.ndarray] = None,
        bias: float = 0.0,
        r_base: float = 0.05,  # Base intrinsic renewal (5% per step)
        u_base: float = 0.0,  # Base supportive input
        d_base: float = 0.02,  # Base stress drag (2% per step)
    ):
        """
        Initialize soul proportion model.

        Args:
            weights: Linear weights for m_t = σ(w^T x_t + b). Default: equal weighting.
            bias: Bias term for scorer.
            r_base: Base intrinsic renewal rate (self-healing).
            u_base: Base supportive input (care/ritual).
            d_base: Base stress drag.
        """
        # Default equal weighting across 7 emotion dimensions
        self.weights = (
            weights
            if weights is not None
            else np.array(
                [
                    0.15,  # valence
                    0.10,  # arousal
                    0.20,  # connectedness (high weight: social vitality critical)
                    0.25,  # meaning (high weight: purpose/coherence central)
                    0.15,  # hope
                    0.075,  # stress (inverted)
                    0.075,  # isolation (inverted)
                ]
            )
        )
        self.bias = bias
        self.r_base = r_base
        self.u_base = u_base
        self.d_base = d_base

        # Calibration anchors (percentile-based, updated from observations)
        self.calibration_anchors = {
            "p10": 0.2,  # 10th percentile
            "p50": 0.5,  # Median
            "p90": 0.8,  # 90th percentile
        }

        logger.info(
            f"Soul Proportion Model initialized: r={r_base}, u={u_base}, d={d_base}"
        )

    def sigmoid(self, z: float) -> float:
        """Sigmoid squashing function σ(z) = 1/(1 + e^-z)"""
        return 1.0 / (1.0 + np.exp(-z))

    def compute_raw_score(self, emotion_features: EmotionFeatures) -> float:
        """
        Compute raw score m_t = σ(w^T x_t + b).

        Args:
            emotion_features: Current emotion state vector.

        Returns:
            Raw score m_t ∈ [0, 1] before calibration.
        """
        x_t = emotion_features.to_vector()
        z = np.dot(self.weights, x_t) + self.bias
        m_t = self.sigmoid(z)
        return m_t

    def calibrate(self, m_t: float) -> float:
        """
        Calibrate raw score to soul proportion S(t) = Cal(m_t).

        Uses percentile anchors to normalize across contexts.
        Simple linear interpolation between anchors.

        Args:
            m_t: Raw score from sigmoid.

        Returns:
            Calibrated S(t) ∈ [0, 1].
        """
        # Simple percentile-based calibration
        if m_t < self.calibration_anchors["p10"]:
            return 0.1 * (m_t / self.calibration_anchors["p10"])
        elif m_t < self.calibration_anchors["p50"]:
            return 0.1 + 0.4 * (
                (m_t - self.calibration_anchors["p10"])
                / (self.calibration_anchors["p50"] - self.calibration_anchors["p10"])
            )
        elif m_t < self.calibration_anchors["p90"]:
            return 0.5 + 0.4 * (
                (m_t - self.calibration_anchors["p50"])
                / (self.calibration_anchors["p90"] - self.calibration_anchors["p50"])
            )
        else:
            return 0.9 + 0.1 * (
                (m_t - self.calibration_anchors["p90"])
                / (1.0 - self.calibration_anchors["p90"])
            )

    def compute_dynamics(
        self, emotion_features: EmotionFeatures
    ) -> Tuple[float, float, float]:
        """
        Compute emotion-driven dynamics parameters (r, u, d).

        Args:
            emotion_features: Current emotion state.

        Returns:
            (r, u, d) tuple:
            - r: intrinsic renewal (increases with coherence/meaning/hope)
            - u: supportive input (acute care/ritual)
            - d: stress drag (increases with chronic stress/isolation)
        """
        # r increases with meaning, hope, and connectedness
        r_emotion_boost = (
            emotion_features.meaning * 0.4
            + emotion_features.hope * 0.3
            + emotion_features.connectedness * 0.3
        ) * 0.1  # Max 10% boost
        r = self.r_base + r_emotion_boost

        # u is base supportive input (can be amplified by interventions)
        u = self.u_base

        # d increases with stress and isolation
        d_emotion_penalty = (
            emotion_features.stress * 0.5 + emotion_features.isolation * 0.5
        ) * 0.1  # Max 10% penalty
        d = self.d_base + d_emotion_penalty

        return r, u, d

    def step(
        self, S_t: float, emotion_features: EmotionFeatures, u_intervention: float = 0.0
    ) -> SoulProportionState:
        """
        Advance soul proportion by one time step.

        Implements: S_{t+1} = S_t + r·S_t(1-S_t) + u_t - d_t·S_t
        Clipped to [0, 1] to maintain bounded proportion.

        Args:
            S_t: Current soul proportion.
            emotion_features: Current emotion state.
            u_intervention: External supportive input (therapy, ritual, etc.).

        Returns:
            SoulProportionState with S_{t+1} and full audit trail.
        """
        # Compute raw score
        m_t = self.compute_raw_score(emotion_features)

        # Compute dynamics
        r, u_base, d = self.compute_dynamics(emotion_features)
        u_total = u_base + u_intervention

        # Bounded logistic dynamics
        S_next = S_t + r * S_t * (1 - S_t) + u_total - d * S_t

        # Clip to [0, 1]
        S_next = max(0.0, min(1.0, S_next))

        # Generate integrity hash (SHA-256)
        import hashlib

        state_repr = f"{S_next:.6f}|{emotion_features.to_vector()}|{r:.6f}|{u_total:.6f}|{d:.6f}|{datetime.utcnow().isoformat()}"
        integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

        state = SoulProportionState(
            S_t=S_next,
            timestamp=datetime.utcnow(),
            emotion_features=emotion_features,
            m_t=m_t,
            r=r,
            u=u_total,
            d=d,
            integrity_hash=integrity_hash,
        )

        logger.debug(
            f"Soul proportion step: S_t={S_t:.4f} → S_{{t+1}}={S_next:.4f} (r={r:.4f}, u={u_total:.4f}, d={d:.4f})"
        )

        return state

    def simulate(
        self,
        S_0: float,
        emotion_trajectory: List[EmotionFeatures],
        interventions: Optional[List[float]] = None,
    ) -> List[SoulProportionState]:
        """
        Simulate soul proportion trajectory over time.

        Args:
            S_0: Initial soul proportion.
            emotion_trajectory: Time series of emotion features.
            interventions: Time series of supportive inputs (default: zeros).

        Returns:
            List of SoulProportionState objects (full audit trail).
        """
        if interventions is None:
            interventions = [0.0] * len(emotion_trajectory)

        trajectory = []
        S_current = S_0

        for t, (emotions, u_intervention) in enumerate(
            zip(emotion_trajectory, interventions)
        ):
            state = self.step(S_current, emotions, u_intervention)
            trajectory.append(state)
            S_current = state.S_t

        logger.info(
            f"Simulation complete: {len(trajectory)} steps, S_0={S_0:.4f} → S_final={S_current:.4f}"
        )
        return trajectory


# =========================== MYTHARA INTEGRATION ===========================


def integrate_with_blessings_reservoir(
    soul_state: SoulProportionState, br_score: float
) -> Dict:
    """
    Integrate soul proportion with Mythara's Blessings Reservoir.

    Soul vitality and BR score are complementary:
    - BR tracks operational integrity (cryptographic governance)
    - S(t) tracks emotional vitality (human coherence)

    Combined metric: Holistic Integrity = (BR + S(t)) / 2

    Args:
        soul_state: Current soul proportion state.
        br_score: Current Blessings Reservoir score [0, 100].

    Returns:
        Integrated governance metrics.
    """
    # Normalize BR to [0, 1]
    br_normalized = br_score / 100.0

    # Combined holistic integrity
    holistic_integrity = (br_normalized + soul_state.S_t) / 2.0

    # Risk flags
    risk_flags = []
    if soul_state.S_t < 0.3:
        risk_flags.append("LOW_SOUL_VITALITY")
    if br_normalized < 0.3:
        risk_flags.append("LOW_BR_SCORE")
    if soul_state.d > 0.15:
        risk_flags.append("HIGH_STRESS_DRAG")
    if soul_state.emotion_features.isolation > 0.7:
        risk_flags.append("SOCIAL_ISOLATION")

    return {
        "holistic_integrity": round(holistic_integrity, 4),
        "br_score": round(br_score, 2),
        "soul_proportion": round(soul_state.S_t, 4),
        "risk_flags": risk_flags,
        "requires_support": len(risk_flags) > 0,
        "integrity_hash": soul_state.integrity_hash,
        "timestamp": soul_state.timestamp.isoformat(),
    }


# =========================== EXAMPLE USAGE ===========================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Mythara Soul Proportion Model - Simulation")
    print("=" * 60)

    # Initialize model
    model = SoulProportionModel(
        r_base=0.05,  # 5% intrinsic renewal
        u_base=0.02,  # 2% base support
        d_base=0.03,  # 3% stress drag
    )

    # Scenario 1: Gradual recovery with therapy intervention
    print("\n--- Scenario 1: Recovery with Support ---")
    S_0 = 0.4  # Starting at 40% vitality

    emotion_trajectory = [
        EmotionFeatures(
            valence=0.2,
            arousal=0.5,
            connectedness=0.4,
            meaning=0.5,
            hope=0.5,
            stress=0.6,
            isolation=0.5,
        )
        for _ in range(5)
    ] + [
        EmotionFeatures(
            valence=0.5,
            arousal=0.6,
            connectedness=0.7,
            meaning=0.7,
            hope=0.7,
            stress=0.3,
            isolation=0.2,
        )
        for _ in range(5)
    ]

    interventions = [0.0] * 5 + [0.05] * 5  # Therapy starts at t=5

    trajectory = model.simulate(S_0, emotion_trajectory, interventions)

    print(f"Initial S(0) = {S_0:.4f}")
    for i, state in enumerate(trajectory):
        print(
            f"t={i+1}: S(t)={state.S_t:.4f}, r={state.r:.4f}, u={state.u:.4f}, d={state.d:.4f}"
        )
    print(f"Final S(10) = {trajectory[-1].S_t:.4f}")

    # Scenario 2: Burnout without intervention
    print("\n--- Scenario 2: Burnout without Support ---")
    S_0 = 0.7  # Starting healthy

    emotion_trajectory_burnout = [
        EmotionFeatures(
            valence=-0.2,
            arousal=0.8,
            connectedness=0.3,
            meaning=0.3,
            hope=0.2,
            stress=0.9,
            isolation=0.8,
        )
        for _ in range(10)
    ]

    trajectory_burnout = model.simulate(S_0, emotion_trajectory_burnout)

    print(f"Initial S(0) = {S_0:.4f}")
    for i, state in enumerate(trajectory_burnout):
        print(f"t={i+1}: S(t)={state.S_t:.4f}, r={state.r:.4f}, d={state.d:.4f}")
    print(f"Final S(10) = {trajectory_burnout[-1].S_t:.4f}")

    # Integration with Blessings Reservoir
    print("\n--- Integration with Blessings Reservoir ---")
    final_state = trajectory[-1]
    br_score = 75.0  # Example BR score

    integrated = integrate_with_blessings_reservoir(final_state, br_score)
    print(f"Holistic Integrity: {integrated['holistic_integrity']:.4f}")
    print(f"BR Score: {integrated['br_score']}")
    print(f"Soul Proportion: {integrated['soul_proportion']}")
    print(f"Risk Flags: {integrated['risk_flags']}")
    print(f"Integrity Hash: {integrated['integrity_hash'][:16]}...")
