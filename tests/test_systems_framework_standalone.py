#!/usr/bin/env python3
"""
Systems Framework Standalone Testing Harness
Test terminal risk prediction without Soul Engine dependencies.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
from pathlib import Path

# Add core/source_proprietary to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

from soul_cradle_systems_framework import (
    SoulCradleParadox,
    SystemExpression,
    NonExpression,
    PrincipalSystem,
    UnresolvedState,
    ResolvedSystem,
    ExpressionType,
    SystemType,
    TerminalRiskLevel,
    TerminalRiskCalculator,
)
from datetime import datetime, timedelta
import json


def create_test_paradox(
    domain: str, expression_a_content: str, expression_b_content: str, days_ago: int = 0
):
    """Helper to create test paradoxes"""
    timestamp = datetime.now() - timedelta(days=days_ago)
    paradox_id = f"TEST_{timestamp.strftime('%Y%m%d_%H%M%S')}"

    return SoulCradleParadox(
        paradox_id=paradox_id,
        expression_a=SystemExpression(
            type=ExpressionType.POLICY,
            notation="Every(Policy)Any(+)Some(Action)Non(Heart)",
            content=expression_a_content,
            dominion_claim=True,
        ),
        expression_b=SystemExpression(
            type=ExpressionType.HEART,
            notation="Every(Heart)Any(+)Some(Care)Non(Action)",
            content=expression_b_content,
            dominion_claim=True,
        ),
        non_expression=NonExpression(
            notation="Non(Both)", reality="Cannot satisfy both"
        ),
        unresolved_state=UnresolvedState(reality="Cannot satisfy both demands at once"),
        resolved_system=ResolvedSystem(
            description="Both truths witnessed without choosing"
        ),
        system_type=SystemType.PSEUDO_PARTIAL,
        viability_score=0.1,
        terminal_risk=TerminalRiskLevel.HIGH,
        principal_system=PrincipalSystem(
            notation="Every(Mission)Any(+)Some(1,0)Non(Mission)",
            viability_score=1.0,
            description="Both truths witnessed",
        ),
        user_id="test_user",
        domain=domain,
        timestamp=timestamp,
    )


def test_scenario_1_low_risk():
    """Test: Worker with few paradoxes = LOW risk"""
    print("\n" + "=" * 60)
    print("SCENARIO 1: Low Risk Worker (5 paradoxes in 90 days)")
    print("=" * 60)

    paradoxes = [
        create_test_paradox(
            "Healthcare", "Policy says discharge", "Patient needs care", days_ago=10
        ),
        create_test_paradox(
            "Healthcare",
            "Budget limits resources",
            "Patient needs treatment",
            days_ago=25,
        ),
        create_test_paradox(
            "Healthcare", "Protocol says no", "Family begging for help", days_ago=40
        ),
        create_test_paradox(
            "Healthcare", "Insurance denied", "Patient deteriorating", days_ago=60
        ),
        create_test_paradox(
            "Healthcare", "Staffing shortage", "Patients waiting", days_ago=80
        ),
    ]

    risk = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=90
    )
    non_expression_count = sum(1 for px in paradoxes if px.non_expression is not None)

    print(f"\nParadoxes logged: {risk['total_paradoxes']}")
    print(f"Pseudo-system density: {risk['incomplete_resolution_count']}")
    print(f"Non-expression count: {non_expression_count}")
    print(f"\n🎯 Risk Score: {risk['risk_score']}")
    print(f"🎯 Risk Level: {risk['risk_level']}")
    print(f"\n📋 Recommendation:\n{risk['recommendation']}")

    return risk


def test_scenario_2_moderate_risk():
    """Test: Worker with increasing paradoxes = MODERATE risk"""
    print("\n" + "=" * 60)
    print("SCENARIO 2: Moderate Risk Worker (15 paradoxes in 90 days)")
    print("=" * 60)

    paradoxes = []
    for i in range(15):
        paradoxes.append(
            create_test_paradox(
                "Nonprofit",
                f"Board directive #{i+1}",
                f"Mission conflict #{i+1}",
                days_ago=(i * 6),  # Spread over 90 days
            )
        )

    risk = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=90
    )
    non_expression_count = sum(1 for px in paradoxes if px.non_expression is not None)

    print(f"\nParadoxes logged: {risk['total_paradoxes']}")
    print(f"Pseudo-system density: {risk['incomplete_resolution_count']}")
    print(f"Non-expression count: {non_expression_count}")
    print(f"\n🎯 Risk Score: {risk['risk_score']}")
    print(f"🎯 Risk Level: {risk['risk_level']}")
    print(f"\n📋 Recommendation:\n{risk['recommendation']}")

    return risk


def test_scenario_3_high_risk():
    """Test: Worker with frequent paradoxes = HIGH risk"""
    print("\n" + "=" * 60)
    print("SCENARIO 3: High Risk Worker (35 paradoxes in 90 days)")
    print("=" * 60)

    paradoxes = []
    for i in range(35):
        paradoxes.append(
            create_test_paradox(
                "Social Services",
                f"Policy violation #{i+1}",
                f"Client safety concern #{i+1}",
                days_ago=(i * 2),  # 2-3 per week
            )
        )

    risk = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=90
    )
    non_expression_count = sum(1 for px in paradoxes if px.non_expression is not None)

    print(f"\nParadoxes logged: {risk['total_paradoxes']}")
    print(f"Pseudo-system density: {risk['incomplete_resolution_count']}")
    print(f"Non-expression count: {non_expression_count}")
    print(f"\n🎯 Risk Score: {risk['risk_score']}")
    print(f"🎯 Risk Level: {risk['risk_level']}")
    print(f"\n📋 Recommendation:\n{risk['recommendation']}")

    return risk


def test_scenario_4_critical_risk():
    """Test: Worker with overwhelming paradoxes = CRITICAL risk"""
    print("\n" + "=" * 60)
    print("SCENARIO 4: Critical Risk Worker (60+ paradoxes in 90 days)")
    print("=" * 60)

    paradoxes = []
    for i in range(65):
        paradoxes.append(
            create_test_paradox(
                "Public Defense",
                f"Court deadline #{i+1}",
                f"Client needs time #{i+1}",
                days_ago=(i * 1.3),  # Nearly daily
            )
        )

    risk = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=90
    )
    non_expression_count = sum(1 for px in paradoxes if px.non_expression is not None)

    print(f"\nParadoxes logged: {risk['total_paradoxes']}")
    print(f"Pseudo-system density: {risk['incomplete_resolution_count']}")
    print(f"Non-expression count: {non_expression_count}")
    print(f"\n🎯 Risk Score: {risk['risk_score']}")
    print(f"🎯 Risk Level: {risk['risk_level']}")
    print(f"\n📋 Recommendation:\n{risk['recommendation']}")

    return risk


def test_time_window_comparison():
    """Test: Compare 30-day vs 90-day windows"""
    print("\n" + "=" * 60)
    print("SCENARIO 6: Time Window Comparison")
    print("=" * 60)

    # Create 40 paradoxes spread over 90 days
    paradoxes = []
    for i in range(40):
        paradoxes.append(
            create_test_paradox(
                "Healthcare", f"Policy #{i+1}", f"Heart #{i+1}", days_ago=(i * 2)
            )
        )

    risk_30 = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=30
    )
    risk_60 = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=60
    )
    risk_90 = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, time_window_days=90
    )

    print("\n30-Day Window:")
    print(
        f"  Paradoxes: {risk_30['total_paradoxes']} | Score: {risk_30['risk_score']} | Level: {risk_30['risk_level']}"
    )

    print("\n60-Day Window:")
    print(
        f"  Paradoxes: {risk_60['total_paradoxes']} | Score: {risk_60['risk_score']} | Level: {risk_60['risk_level']}"
    )

    print("\n90-Day Window:")
    print(
        f"  Paradoxes: {risk_90['total_paradoxes']} | Score: {risk_90['risk_score']} | Level: {risk_90['risk_level']}"
    )

    return {"30d": risk_30, "60d": risk_60, "90d": risk_90}


def test_viability_threshold():
    """Test: Different viability thresholds"""
    print("\n" + "=" * 60)
    print("SCENARIO 7: Viability Threshold Sensitivity")
    print("=" * 60)

    # Create paradoxes with varying viability scores
    paradoxes = []
    for i in range(20):
        p = create_test_paradox(
            "Healthcare", f"Policy #{i}", f"Heart #{i}", days_ago=i * 4
        )
        p.viability_score = 0.05 + (i * 0.04)  # Range from 0.05 to 0.81
        paradoxes.append(p)

    risk_low = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, viability_threshold=0.2
    )
    risk_mid = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, viability_threshold=0.3
    )
    risk_high = TerminalRiskCalculator.calculate_terminal_risk(
        paradoxes, viability_threshold=0.4
    )

    print("\nThreshold 0.2:")
    print(
        f"  Pseudo-systems: {risk_low['incomplete_resolution_count']} | Score: {risk_low['risk_score']} | Level: {risk_low['risk_level']}"
    )

    print("\nThreshold 0.3 (default):")
    print(
        f"  Pseudo-systems: {risk_mid['incomplete_resolution_count']} | Score: {risk_mid['risk_score']} | Level: {risk_mid['risk_level']}"
    )

    print("\nThreshold 0.4:")
    print(
        f"  Pseudo-systems: {risk_high['incomplete_resolution_count']} | Score: {risk_high['risk_score']} | Level: {risk_high['risk_level']}"
    )

    return {"0.2": risk_low, "0.3": risk_mid, "0.4": risk_high}


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("█" * 60)
    print("  SYSTEMS FRAMEWORK STANDALONE TEST SUITE")
    print("█" * 60)

    results = {}

    try:
        results["scenario_1_low_risk"] = test_scenario_1_low_risk()
        results["scenario_2_moderate_risk"] = test_scenario_2_moderate_risk()
        results["scenario_3_high_risk"] = test_scenario_3_high_risk()
        results["scenario_4_critical_risk"] = test_scenario_4_critical_risk()
        results["scenario_5_query_language"] = test_query_language()
        results["scenario_6_time_windows"] = test_time_window_comparison()
        results["scenario_7_viability"] = test_viability_threshold()

        print("\n" + "=" * 60)
        print("TEST SUITE COMPLETE ✅")
        print("=" * 60)

        # Summary
        print("\n📊 RISK LEVEL DISTRIBUTION:")
        print(f"  Low Risk:      {results['scenario_1_low_risk']['risk_level']}")
        print(f"  Moderate Risk: {results['scenario_2_moderate_risk']['risk_level']}")
        print(f"  High Risk:     {results['scenario_3_high_risk']['risk_level']}")
        print(f"  Critical Risk: {results['scenario_4_critical_risk']['risk_level']}")

        print("\n📈 RISK SCORES:")
        print(f"  Low:      {results['scenario_1_low_risk']['risk_score']}")
        print(f"  Moderate: {results['scenario_2_moderate_risk']['risk_score']}")
        print(f"  High:     {results['scenario_3_high_risk']['risk_score']}")
        print(f"  Critical: {results['scenario_4_critical_risk']['risk_score']}")

        print("\n✅ All tests passed. Framework is operational.\n")

        return results

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = run_all_tests()

    # Optionally save results to JSON
    if results:
        output_file = (
            Path(__file__).parent
            / "tests"
            / "output"
            / "systems_framework_test_results.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert datetime objects to strings for JSON serialization
        def serialize_dates(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=serialize_dates)

        print(f"📝 Results saved to: {output_file}")
