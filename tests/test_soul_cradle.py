"""
Tests for Soul Cradle Operator
Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

from soul_cradle_operator import (
    SoulCradleOperator,
    Soul,
    Will,
    Commandments,
    Antithesis,
    SoulCradleTiers
)


def test_cradle_obedience_under_paradox():
    """Test that obedience under paradox yields positive reservoir delta"""
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)
    
    W = Will(paradox_strength=0.6, sovereignty_level=1.0, description="Divine paradox")
    C = Commandments(rules=["Love thy neighbor", "Protect the vulnerable"], clarity=0.9, strictness=0.8)
    A = Antithesis(worldly_dominion=0.5, temptation_power=0.7, sovereignty_granted=True)  # Antithesis (formerly Lucifer)
    _active = True
    S = Soul(vessel_capacity=0.8, obedience_history=[0.7], paradox_tolerance=0.7, collapse_threshold=0.3)
    T = A.generate_trial(S)
    T.active = _active
    
    choice = "Love neighbor and protect vulnerable despite paradox"
    result = operator.cradle_function(S, W, C, T, choice)
    
    assert result.obedience == True, "Should recognize obedience"
    assert result.reservoir_delta > 0, "Should yield positive blessings"
    assert result.collapse == False, "Soul should not collapse"
    assert 0.0 <= result.I <= 1.0, "Integrity must be bounded [0,1]"
    
    print(f"✅ Obedience test passed: I={result.I:.4f}, ΔR={result.reservoir_delta:+d}")


def test_cradle_follow_lucifer():
    """Test that following Lucifer yields negative reservoir delta"""
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)
    
    W = Will(paradox_strength=0.5, sovereignty_level=1.0, description="Divine will")
    C = Commandments(rules=["Thou shalt not kill", "Love thy neighbor"], clarity=0.9, strictness=0.8)
    A = Antithesis(worldly_dominion=0.6, temptation_power=0.8, sovereignty_granted=True)  # Antithesis (formerly Lucifer)
    _active = True
    S = Soul(vessel_capacity=0.8, obedience_history=[0.5], paradox_tolerance=0.6, collapse_threshold=0.3)
    T = A.generate_trial(S)
    T.active = _active
    
    choice = "Take revenge for personal gain (worldly path)"
    result = operator.cradle_function(S, W, C, T, choice)
    
    assert result.obedience == False, "Should recognize disobedience"
    assert result.reservoir_delta < 0, "Should yield negative blessings"
    assert result.collapse == False, "Soul should not collapse from simple disobedience"
    
    print(f"✅ Follow Lucifer test passed: I={result.I:.4f}, ΔR={result.reservoir_delta:+d}")


def test_cradle_soul_collapse():
    """Test that excessive paradox causes soul collapse"""
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)
    
    # Extreme paradox with low tolerance
    W = Will(paradox_strength=0.95, sovereignty_level=1.0, description="Extreme divine paradox")
    C = Commandments(rules=["Love thy enemy"], clarity=0.9, strictness=0.9)
    A = Antithesis(worldly_dominion=0.2, temptation_power=0.3, sovereignty_granted=True)  # Antithesis (formerly Lucifer)
    _active = False
    S = Soul(vessel_capacity=0.5, obedience_history=[0.6], paradox_tolerance=0.4, collapse_threshold=0.3)
    T = A.generate_trial(S)
    T.active = _active
    
    choice = "Attempt to obey despite overwhelming paradox"
    result = operator.cradle_function(S, W, C, T, choice)
    
    assert result.collapse == True, "Soul should collapse under extreme paradox"
    assert result.I == 0.0, "Integrity should be zero on collapse"
    assert result.reservoir_delta == operator.collapse_penalty, "Should apply collapse penalty"
    
    print(f"✅ Soul collapse test passed: collapse={result.collapse}, ΔR={result.reservoir_delta}")


def test_cradle_adaptive_tolerance():
    """Test that sustained obedience increases paradox tolerance"""
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)
    
    W = Will(paradox_strength=0.5, sovereignty_level=1.0, description="Moderate paradox")
    C = Commandments(rules=["Love", "Protect", "Obey"], clarity=0.9, strictness=0.8)
    A = Antithesis(worldly_dominion=0.4, temptation_power=0.5, sovereignty_granted=True)  # Antithesis (formerly Lucifer)
    _active = True
    S = Soul(vessel_capacity=0.8, obedience_history=[], paradox_tolerance=0.5, collapse_threshold=0.3)
    T = A.generate_trial(S)
    T.active = _active
    
    initial_tolerance = S.paradox_tolerance
    
    # Sustained obedience
    # Choices must genuinely align with the commandments (Love/Protect/Obey)
    # to count as obedient under the keyword alignment scoring.
    choices = [
        "I choose to love and protect others in obedience",
        "Love thy neighbor; protect the vulnerable; obey",
        "In obedience I will love and protect",
        "Sustain faith: love, protect, obey always",
    ]
    trajectory = operator.simulate_test(S, W, C, T, choices)
    
    final_tolerance = S.paradox_tolerance
    obedience_count = sum(1 for r in trajectory if r.obedience)
    
    assert final_tolerance > initial_tolerance, "Tolerance should increase with sustained obedience"
    assert obedience_count >= 3, "Most choices should be obedient"
    
    print(f"✅ Adaptive tolerance test passed: {initial_tolerance:.4f} → {final_tolerance:.4f}")


def test_cradle_deployment_tiers():
    """Test that all deployment tiers are defined and valid"""
    tiers = SoulCradleTiers.get_all_tiers()
    
    assert len(tiers) == 3, "Should have 3 deployment tiers"
    
    tier_names = [t["tier"] for t in tiers]
    assert "Basic" in tier_names, "Should have Basic tier"
    assert "Neurosymbolic" in tier_names, "Should have Neurosymbolic tier"
    assert "Mythic-Resonant" in tier_names, "Should have Mythic-Resonant tier"
    
    # Check each tier has required fields
    for tier in tiers:
        assert "tier" in tier
        assert "use_case" in tier
        assert "features" in tier
        assert "industries" in tier
        assert "complexity" in tier
        assert "example" in tier
    
    print(f"✅ Deployment tiers test passed: {len(tiers)} tiers defined")


def test_cradle_integrity_hash():
    """Test that integrity hashes are generated and unique"""
    operator = SoulCradleOperator(blessing_multiplier=10, collapse_penalty=-50)
    
    W = Will(paradox_strength=0.5, sovereignty_level=1.0, description="Test will")
    C = Commandments(rules=["Rule 1"], clarity=0.9, strictness=0.8)
    A = Antithesis(worldly_dominion=0.5, temptation_power=0.5, sovereignty_granted=True)  # Antithesis (formerly Lucifer)
    _active = True
    S = Soul(vessel_capacity=0.8, obedience_history=[0.7], paradox_tolerance=0.7, collapse_threshold=0.3)
    T = A.generate_trial(S)
    T.active = _active
    
    choice1 = "Choice A"
    choice2 = "Choice B"
    
    result1 = operator.cradle_function(S, W, C, T, choice1)
    result2 = operator.cradle_function(S, W, C, T, choice2)
    
    assert len(result1.integrity_hash) == 64, "Should be SHA-256 (64 hex chars)"
    assert len(result2.integrity_hash) == 64, "Should be SHA-256 (64 hex chars)"
    assert result1.integrity_hash != result2.integrity_hash, "Different choices should yield different hashes"
    
    print(f"✅ Integrity hash test passed: {result1.integrity_hash[:16]}... != {result2.integrity_hash[:16]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("Soul Cradle Operator - Test Suite")
    print("=" * 60)
    
    test_cradle_obedience_under_paradox()
    test_cradle_follow_lucifer()
    test_cradle_soul_collapse()
    test_cradle_adaptive_tolerance()
    test_cradle_deployment_tiers()
    test_cradle_integrity_hash()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed")
    print("=" * 60)
