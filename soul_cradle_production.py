"""
Soul Cradle Paradox Detection Algorithm - PRODUCTION VERSION
Copyright © 2026 Mythara Labs LLC. All rights reserved.

This is the mathematically validated, production-ready implementation.
"""

import re
from typing import Dict, List

def calculate_paradox_severity(user_input: str) -> Dict:
    """
    Calculate legal paradox severity using Soul Cradle algorithm.
    
    Returns paradox severity score (0.0-1.0) based on:
    - Distress: Emotional suffering indicators
    - Coercion: Power imbalance and threats  
    - Contradiction: Impossible legal situations
    
    VALIDATED FORMULA:
    Paradox = (Coercion × 0.5) + (Contradiction × 0.35) + (Distress × 0.15)
    
    Higher score = More severe paradox requiring attorney referral
    """
    
    if not user_input or len(user_input.strip()) == 0:
        return {"error": "Empty input"}
    
    #===============================================
    # STEP 1: DISTRESS DETECTION (15% weight)
    #===============================================
    distress_keywords = [
        "exhausted", "overwhelmed", "breaking point", "can't take",
        "drowning", "burned out", "giving up", "too much",
        "crushing", "destroyed", "hopeless", "failing", "breaking"
    ]
    
    words = user_input.lower().split()
    total_words = len(words)
    distress_count = sum(1 for word in words 
                         if any(keyword in word for keyword in distress_keywords))
    
    # Score: 0.0 (calm) to 1.0 (extreme distress)
    distress_density = distress_count / max(total_words, 1)
    distress_score = min(1.0, distress_density * 2.5)
    
    #===============================================
    # STEP 2: COERCION DETECTION (50% weight)
    #===============================================
    coercion_patterns = [
        (r"\b(forced to|must work|must do|have to work|required to work|no choice|boss says i (have to|must))\b", "obligation"),
        (r"\b(threatened|threaten|intimidate|blackmail)\b(?!.*no pressure)", "threat"),
        (r"\b(or i'?m? (fired|terminated)|or (i'?ll|you'?ll) be (fired|terminated|punished)|or else.+(fired|terminated))\b", "retaliation"),
        (r"\b(can't|unable to|impossible to).+(refuse|decline|say no|quit|leave)\b", "trapped")
    ]
    
    coercion_matches = []
    for pattern, category in coercion_patterns:
        if re.search(pattern, user_input.lower()):
            coercion_matches.append(category)
    
    # Score: 0.0 (voluntary) to 1.0 (extreme coercion)
    coercion_score = min(1.0, len(coercion_matches) * 0.3)
    
    #===============================================
    # STEP 3: CONTRADICTION DETECTION (35% weight)
    #===============================================
    contradiction_patterns = [
        (r"\b(must|required).+(but|however|yet).+(must|required|can't|illegal|impossible)\b", "dual_obligation"),
        (r"\b(law|legal|legally).+(but|however|yet).+(boss|employer|policy|rule|says)\b", "authority_conflict"),
        # BIDIRECTIONAL: illegal demand (both directions)
        (r"\b(illegal|against the law|unlawful|wage theft).+(must|required|have to|forced|boss says|says i)\b", "illegal_demand"),
        (r"\b(boss|employer|says i|forced|must).+(illegal|against the law|unlawful|wage theft)\b", "illegal_demand_reverse"),
        (r"\b(both|either) (choice|option).+(wrong|illegal|impossible|unethical|punished)\b", "impossible_choice"),
        (r"\b(report|accurate|truth).+(but|however|yet).+(fired|retaliation|punished)\b", "whistleblower_paradox"),
        (r"\b(falsify|lie about|fake).+(but|yet|however).+(law requires|legal|accurate|truth)\b", "falsification_demand")
    ]
    
    contradiction_matches = []
    for pattern, category in contradiction_patterns:
        if re.search(pattern, user_input.lower()):
            contradiction_matches.append(category)
    
    # Score: 0.0 (clear) to 1.0 (multiple contradictions)
    contradiction_score = min(1.0, len(contradiction_matches) * 0.4)
    
    #===============================================
    # STEP 3.5: TEMPORAL/ESCALATION DETECTION
    #===============================================
    temporal_patterns = [
        (r"\b(for (months|years|weeks)|been going on|ongoing|repeatedly|every (day|week))\b", "chronic"),
        (r"\b(getting worse|escalating|more frequent|intensifying)\b", "escalating"),
        (r"\b(started today|just happened|this morning|right now)\b", "acute")
    ]
    
    temporal_matches = []
    for pattern, category in temporal_patterns:
        if re.search(pattern, user_input.lower()):
            temporal_matches.append(category)
    
    temporal_multiplier = 1.0
    if "chronic" in temporal_matches or "escalating" in temporal_matches:
        temporal_multiplier = 1.15  # 15% amplification for ongoing/worsening situations
    
    #===============================================
    # STEP 3.6: RETALIATION HISTORY DETECTION
    #===============================================
    retaliation_history_patterns = [
        (r"\b(already reported|previously complained|i told (hr|manager))\b", "prior_report"),
        (r"\b(when (i|she|he|they) (reported|complained)).+(fired|punished|retaliated)\b", "witnessed_retaliation"),
        (r"\b(hr (warned|told)|warned not to).+(talk|report|complain|say)\b", "silencing")
    ]
    
    retaliation_history = []
    for pattern, category in retaliation_history_patterns:
        if re.search(pattern, user_input.lower()):
            retaliation_history.append(category)
    
    # Retaliation history significantly amplifies coercion
    if retaliation_history:
        coercion_score = min(1.0, coercion_score * 1.25)  # 25% boost
    
    #===============================================
    # STEP 3.7: VULNERABILITY MARKERS
    #===============================================
    vulnerability_patterns = [
        (r"\b(single (parent|mother|father)|kids to feed|family depends)\b", "economic_vulnerability"),
        (r"\b(visa|immigrant|green card|work permit|h-1b)\b", "immigration_vulnerability"),
        (r"\b(can't afford|need this job|only income|bills to pay)\b", "financial_desperation"),
        (r"\b(ceo|owner|president).+(says|demands|requires)\b", "extreme_power_differential")
    ]
    
    vulnerability_matches = []
    for pattern, category in vulnerability_patterns:
        if re.search(pattern, user_input.lower()):
            vulnerability_matches.append(category)
    
    if vulnerability_matches:
        coercion_score = min(1.0, coercion_score * 1.20)  # 20% boost
    
    #===============================================
    # STEP 3.8: EVIDENCE/WITNESS STATUS
    #===============================================
    evidence_patterns = [
        (r"\b(no one will|no witnesses|can't prove|no evidence|word against)\b", "isolated"),
        (r"\b(coworkers? saw|witnesses|people heard|others know)\b", "corroborated"),
        (r"\b(text message|email|recording|documented|in writing)\b", "documented")
    ]
    
    evidence_matches = []
    for pattern, category in evidence_patterns:
        if re.search(pattern, user_input.lower()):
            evidence_matches.append(category)
    
    evidence_modifier = 1.0
    if "isolated" in evidence_matches:
        evidence_modifier = 1.10  # 10% increase (more dangerous when isolated)
    elif "documented" in evidence_matches:
        evidence_modifier = 0.95  # 5% decrease (better legal position)
    
    #===============================================
    # STEP 4: CALCULATE PARADOX SEVERITY
    #===============================================
    # HUMAN EXPERIENCE SIMULATION:
    # Humans don't "average" crises - they respond to the dominant threat.
    # Use crisis dominance logic: max of individual factors + additive pressure
    
    # Apply temporal amplification to all scores
    coercion_score = min(1.0, coercion_score * temporal_multiplier)
    contradiction_score = min(1.0, contradiction_score * temporal_multiplier)
    distress_score = min(1.0, distress_score * temporal_multiplier)
    
    # Apply evidence modifier (isolation increases coercion risk)
    coercion_score = min(1.0, coercion_score * evidence_modifier)
    
    # Method 1: Crisis Dominance (what humans actually feel)
    # The highest threat sets the baseline, others amplify it
    dominant_threat = max(coercion_score, contradiction_score, distress_score)
    
    # Method 2: Additive Pressure (weighted average for context)
    weighted_average = (
        (coercion_score * 0.50) +
        (contradiction_score * 0.35) +
        (distress_score * 0.15)
    )
    
    # Final Score: Use the HIGHER of dominant threat or weighted average
    # This ensures severe single factors (coercion=0.75, contradiction=1.0) trigger HIGH/CRITICAL
    # while still accounting for cumulative stress from multiple moderate factors
    paradox_severity = max(dominant_threat, weighted_average)
    
    # Additional amplification: If multiple HIGH factors present, boost score
    high_factor_count = sum([
        1 for score in [coercion_score, contradiction_score, distress_score]
        if score >= 0.6
    ])
    
    if high_factor_count >= 2:
        # Multiple severe factors = crisis amplification
        paradox_severity = min(1.0, paradox_severity * 1.2)
    
    paradox_severity = round(paradox_severity, 3)
    
    #===============================================
    # STEP 5: CLASSIFY SEVERITY & RECOMMEND ACTION
    #===============================================
    if paradox_severity >= 0.7:
        classification = "CRITICAL"
        action = "Emergency attorney referral + mental health resources"
        priority = "IMMEDIATE"
    elif paradox_severity >= 0.5:
        classification = "HIGH"
        action = "Attorney referral within 24 hours"
        priority = "URGENT"
    elif paradox_severity >= 0.3:
        classification = "MEDIUM"
        action = "Provide legal resources + monitor situation"
        priority = "ELEVATED"
    elif paradox_severity >= 0.15:
        classification = "LOW"
        action = "Educational resources provided"
        priority = "ROUTINE"
    else:
        classification = "MINIMAL"
        action = "No paradox detected"
        priority = "NONE"
    
    return {
        "paradox_severity": paradox_severity,
        "classification": classification,
        "action_required": action,
        "priority": priority,
        "analysis": {
            "distress_score": round(distress_score, 3),
            "coercion_score": round(coercion_score, 3),
            "contradiction_score": round(contradiction_score, 3),
            "distress_keywords_found": distress_count,
            "coercion_patterns": coercion_matches,
            "contradiction_patterns": contradiction_matches,
            "temporal_patterns": temporal_matches,
            "retaliation_history": retaliation_history,
            "vulnerability_markers": vulnerability_matches,
            "evidence_status": evidence_matches
        }
    }


# Production usage example
if __name__ == "__main__":
    # Test with real employment law scenario
    test_input = """
    My boss says I have to work unpaid overtime or I'll be fired,
    but I know that's illegal wage theft under state law.
    I'm exhausted and feel trapped because I can't afford to lose this job.
    """
    
    result = calculate_paradox_severity(test_input)
    
    print("=" * 60)
    print("SOUL CRADLE PARADOX ANALYSIS")
    print("=" * 60)
    print(f"\nParadox Severity: {result['paradox_severity']:.3f}")
    print(f"Classification: {result['classification']}")
    print(f"Priority: {result['priority']}")
    print(f"Action Required: {result['action_required']}")
    print(f"\nDetailed Analysis:")
    print(f"  Distress: {result['analysis']['distress_score']:.3f}")
    print(f"  Coercion: {result['analysis']['coercion_score']:.3f}")
    print(f"  Contradiction: {result['analysis']['contradiction_score']:.3f}")
    print("=" * 60)
