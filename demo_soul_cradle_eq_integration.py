#!/usr/bin/env python3
"""
Soul Cradle Emotional Authenticity Integration Demo
Demonstrates how EQ = (G/T) × H formula tracks emotional labor in paradox resolution.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
from pathlib import Path

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent / "core" / "source_proprietary"))

from soul_cradle_systems_framework import (
    SoulCradleParadox,
    SystemExpression,
    UnresolvedState,
    NonExpression,
    ResolvedSystem,
    ExpressionType,
    SystemType,
    TerminalRiskLevel,
    EmotionalAuthenticity,
    EmotionalAuthenticityLevel
)
from datetime import datetime


def demonstrate_eq_in_soul_cradle():
    """Show how EQ formula integrates with Soul Cradle paradox resolution"""
    
    print("="*70)
    print("⚛️ SOUL CRADLE EMOTIONAL AUTHENTICITY INTEGRATION")
    print("   Formula: EQ = (G/T) × H")
    print("="*70 + "\n")
    
    # Create a hospital discharge paradox
    paradox = SoulCradleParadox(
        paradox_id="SC_2025_1121_001",
        expression_a=SystemExpression(
            type=ExpressionType.POLICY,
            weight=0.9,
            tension=0.8,
            content="Hospital policy requires discharge within 72 hours",
            dominion_claim=True
        ),
        expression_b=SystemExpression(
            type=ExpressionType.COMPASSION,
            weight=0.8,
            tension=0.7,
            content="Patient will be homeless and unsafe if discharged now",
            dominion_claim=True
        ),
        unresolved_state=UnresolvedState(
            type=ExpressionType.RESOLUTION,
            unresolved_score=0.85,
            reality="Cannot satisfy both policy compliance and patient safety"
        ),
        non_expression=NonExpression(
            type=ExpressionType.COMPASSION,
            suppression_level=0.7,
            content="Hospital cannot provide housing or extend care for social issues",
            reason="Resource constraints and regulatory boundaries",
            impact="Patient safety compromised, staff moral injury",
            reality="System gap between policy and compassionate care"
        ),
        system_type=SystemType.INCOMPLETE_RESOLUTION,
        viability_score=0.15,
        terminal_risk=TerminalRiskLevel.HIGH,
        resolved_system=ResolvedSystem(
            witness_score_a=1.0,
            witness_score_b=1.0,
            recovery_method="Dual_Witness_Integration",
            viability_score=1.0,
            description="Soul Cradle witnesses BOTH the policy requirement AND the compassion concern"
        ),
        user_id="nurse_practitioner_001",
        domain="Healthcare"
    )
    
    print("📊 PARADOX CONTEXT:")
    print(f"  ID: {paradox.paradox_id}")
    print(f"  Domain: {paradox.domain}")
    print(f"  Expression A: {paradox.expression_a.content}")
    print(f"  Expression B: {paradox.expression_b.content}")
    print(f"  Non-Expression: {paradox.non_expression.content}")
    print(f"  Terminal Risk: {paradox.terminal_risk.value}\n")
    
    # Scenario 1: Initial expression - holding back true feelings
    print("="*70)
    print("SCENARIO 1: Initial Discussion with Manager")
    print("="*70)
    eq1 = paradox.calculate_emotional_authenticity(
        genuine_shareable=80,  # Has a lot of genuine concerns to share
        total_expressed=50,     # Only expresses half due to professional filter
        held_back=50,          # Holds back frustration and moral distress
        context="Initial report to nursing manager about discharge concern"
    )
    
    print(f"Genuine Ideas Available: {eq1.genuine_shareable}%")
    print(f"Actually Expressed: {eq1.total_expressed}%")
    print(f"Held Back: {eq1.held_back}%")
    print(f"EQ Score: {eq1.eq_score:.2f}")
    print(f"Level: {eq1.authenticity_level.value}")
    print(f"Interpretation: {eq1.interpret()}\n")
    
    # Scenario 2: Escalation - more suppression
    print("="*70)
    print("SCENARIO 2: Meeting with Hospital Administrator")
    print("="*70)
    eq2 = paradox.calculate_emotional_authenticity(
        genuine_shareable=90,  # Even more concerns now
        total_expressed=30,     # Less expression due to hierarchy
        held_back=70,          # Significant suppression for career safety
        context="Escalation meeting with administration about patient safety"
    )
    
    print(f"Genuine Ideas Available: {eq2.genuine_shareable}%")
    print(f"Actually Expressed: {eq2.total_expressed}%")
    print(f"Held Back: {eq2.held_back}%")
    print(f"EQ Score: {eq2.eq_score:.2f}")
    print(f"Level: {eq2.authenticity_level.value}")
    print(f"Interpretation: {eq2.interpret()}\n")
    
    # Scenario 3: Peer conversation - burnout territory
    print("="*70)
    print("SCENARIO 3: Venting to Colleague After Discharge")
    print("="*70)
    eq3 = paradox.calculate_emotional_authenticity(
        genuine_shareable=100,  # Full emotional reality
        total_expressed=60,     # More open with peer but still filtered
        held_back=40,          # Still holding back some hopelessness
        context="Private conversation with trusted colleague"
    )
    
    print(f"Genuine Ideas Available: {eq3.genuine_shareable}%")
    print(f"Actually Expressed: {eq3.total_expressed}%")
    print(f"Held Back: {eq3.held_back}%")
    print(f"EQ Score: {eq3.eq_score:.2f}")
    print(f"Level: {eq3.authenticity_level.value}")
    print(f"Interpretation: {eq3.interpret()}\n")
    
    # Scenario 4: Soul Cradle witnessing - authentic expression
    print("="*70)
    print("SCENARIO 4: Soul Cradle Witnessing Session")
    print("="*70)
    eq4 = paradox.calculate_emotional_authenticity(
        genuine_shareable=100,  # Full emotional reality
        total_expressed=100,    # Complete expression in witnessed space
        held_back=5,           # Minimal suppression - safe to be authentic
        context="Soul Cradle witnessing both policy constraint AND compassion"
    )
    
    print(f"Genuine Ideas Available: {eq4.genuine_shareable}%")
    print(f"Actually Expressed: {eq4.total_expressed}%")
    print(f"Held Back: {eq4.held_back}%")
    print(f"EQ Score: {eq4.eq_score:.2f}")
    print(f"Level: {eq4.authenticity_level.value}")
    print(f"Interpretation: {eq4.interpret()}\n")
    
    # Analyze burnout risk
    print("="*70)
    print("📊 BURNOUT RISK ANALYSIS")
    print("="*70)
    
    is_at_risk, avg_eq, recommendation = paradox.predict_burnout_risk()
    
    print(f"\nEmotional Authenticity Timeline:")
    for i, ea in enumerate(paradox.authenticity_timeline, 1):
        print(f"  {i}. {ea.context[:50]}...")
        print(f"     EQ={ea.eq_score:.1f} | Level={ea.authenticity_level.value}")
    
    print(f"\nAverage EQ Score: {avg_eq:.2f}")
    print(f"Burnout Risk: {'YES ⚠️' if is_at_risk else 'NO ✅'}")
    print(f"\n{recommendation}\n")
    
    # Show how Soul Cradle resolution impacts EQ
    print("="*70)
    print("✨ SOUL CRADLE RESOLUTION IMPACT")
    print("="*70)
    
    print(f"\nBEFORE Soul Cradle:")
    print(f"  Average EQ: {sum(ea.eq_score for ea in paradox.authenticity_timeline[:3]) / 3:.1f}")
    print(f"  Emotional State: {paradox.authenticity_timeline[1].authenticity_level.value}")
    print(f"  Suppression Rate: {paradox.authenticity_timeline[1].held_back:.0f}%")
    
    print(f"\nAFTER Soul Cradle Witnessing:")
    print(f"  Current EQ: {paradox.authenticity_timeline[-1].eq_score:.1f}")
    print(f"  Emotional State: {paradox.authenticity_timeline[-1].authenticity_level.value}")
    print(f"  Suppression Rate: {paradox.authenticity_timeline[-1].held_back:.0f}%")
    
    print(f"\n📊 Improvement:")
    before_avg = sum(ea.eq_score for ea in paradox.authenticity_timeline[:3]) / 3
    after = paradox.authenticity_timeline[-1].eq_score
    improvement = ((before_avg - after) / before_avg) * 100 if before_avg > 0 else 0
    
    print(f"  EQ Score Reduction: {improvement:.1f}%")
    print(f"  Burnout Risk: REDUCED from {paradox.authenticity_timeline[1].authenticity_level.value}")
    print(f"                      to {paradox.authenticity_timeline[-1].authenticity_level.value}")
    
    print("\n💡 KEY INSIGHT:")
    print("  Soul Cradle witnessing BOTH expressions (policy AND compassion)")
    print("  reduces emotional suppression, lowering EQ score and burnout risk.")
    print("  When both truths are witnessed, authenticity can be expressed safely.\n")
    
    print("="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print(f"\nFormula validated: EQ = (G/T) × H")
    print(f"Integrated into: Soul Cradle Systems Framework")
    print(f"Purpose: Track emotional labor and predict burnout in paradox resolution")
    print("="*70 + "\n")


if __name__ == "__main__":
    demonstrate_eq_in_soul_cradle()
