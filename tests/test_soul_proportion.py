"""
Tests for Soul Proportion Model
Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

from soul_proportion_model import (
    SoulProportionModel,
    EmotionFeatures,
    integrate_with_blessings_reservoir
)


def test_soul_proportion_bounded():
    """Test that S(t) remains bounded in [0, 1]"""
    model = SoulProportionModel()
    
    # Test with extreme inputs
    emotions_high = EmotionFeatures(
        valence=1.0, arousal=1.0, connectedness=1.0, meaning=1.0,
        hope=1.0, stress=0.0, isolation=0.0
    )
    
    S_t = 0.95
    state = model.step(S_t, emotions_high, u_intervention=0.1)
    
    assert 0.0 <= state.S_t <= 1.0, f"S(t) out of bounds: {state.S_t}"
    print(f"✅ Bounded test passed: S(t) = {state.S_t:.4f}")


def test_soul_proportion_recovery():
    """Test recovery trajectory with supportive intervention"""
    model = SoulProportionModel(r_base=0.05, u_base=0.02, d_base=0.02)
    
    # Start at low vitality
    S_0 = 0.3
    
    # Healthy emotion features + therapy
    emotions = EmotionFeatures(
        valence=0.5, arousal=0.6, connectedness=0.7, meaning=0.7,
        hope=0.7, stress=0.2, isolation=0.1
    )
    
    trajectory = model.simulate(
        S_0=S_0,
        emotion_trajectory=[emotions] * 10,
        interventions=[0.05] * 10  # Consistent therapy
    )
    
    # Should show upward trend
    assert trajectory[-1].S_t > S_0, "No recovery observed"
    print(f"✅ Recovery test passed: {S_0:.4f} → {trajectory[-1].S_t:.4f}")


def test_soul_proportion_burnout():
    """Test burnout trajectory without intervention"""
    model = SoulProportionModel(r_base=0.05, u_base=0.0, d_base=0.03)
    
    # Start healthy
    S_0 = 0.7
    
    # High stress, low support
    emotions = EmotionFeatures(
        valence=-0.3, arousal=0.9, connectedness=0.2, meaning=0.2,
        hope=0.1, stress=0.9, isolation=0.8
    )
    
    trajectory = model.simulate(
        S_0=S_0,
        emotion_trajectory=[emotions] * 10,
        interventions=[0.0] * 10
    )
    
    # Should show downward trend
    assert trajectory[-1].S_t < S_0, "No burnout observed"
    print(f"✅ Burnout test passed: {S_0:.4f} → {trajectory[-1].S_t:.4f}")


def test_holistic_integrity():
    """Test integration with Blessings Reservoir"""
    model = SoulProportionModel()
    
    emotions = EmotionFeatures(
        valence=0.5, arousal=0.6, connectedness=0.7, meaning=0.7,
        hope=0.7, stress=0.3, isolation=0.2
    )
    
    state = model.step(0.7, emotions)
    br_score = 85.0
    
    integrated = integrate_with_blessings_reservoir(state, br_score)
    
    assert 0.0 <= integrated["holistic_integrity"] <= 1.0
    assert "br_score" in integrated
    assert "soul_proportion" in integrated
    assert "risk_flags" in integrated
    assert "integrity_hash" in integrated
    
    print(f"✅ Holistic integrity test passed: {integrated['holistic_integrity']:.4f}")


def test_dynamics_emotion_driven():
    """Test that r, u, d respond to emotion features"""
    model = SoulProportionModel(r_base=0.05, u_base=0.02, d_base=0.03)
    
    # High meaning/hope should boost r
    emotions_high = EmotionFeatures(
        valence=0.8, arousal=0.5, connectedness=0.9, meaning=0.9,
        hope=0.9, stress=0.1, isolation=0.1
    )
    r_high, u_high, d_high = model.compute_dynamics(emotions_high)
    
    # Low meaning/hope, high stress should increase d
    emotions_low = EmotionFeatures(
        valence=-0.2, arousal=0.8, connectedness=0.2, meaning=0.2,
        hope=0.1, stress=0.9, isolation=0.9
    )
    r_low, u_low, d_low = model.compute_dynamics(emotions_low)
    
    assert r_high > r_low, "r should increase with meaning/hope"
    assert d_low > d_high, "d should increase with stress/isolation"
    
    print(f"✅ Dynamics test passed: r_high={r_high:.4f} > r_low={r_low:.4f}, d_low={d_low:.4f} > d_high={d_high:.4f}")


if __name__ == "__main__":
    print("=" * 60)
    print("Soul Proportion Model - Test Suite")
    print("=" * 60)
    
    test_soul_proportion_bounded()
    test_soul_proportion_recovery()
    test_soul_proportion_burnout()
    test_holistic_integrity()
    test_dynamics_emotion_driven()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed")
    print("=" * 60)
