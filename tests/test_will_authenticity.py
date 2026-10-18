"""
Mythara Engine: Emotional Extortion Detection Tests
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Test suite for emotional extortion detection and quantification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'source_proprietary')))

from will_integrity_guardian import (
    EmotionalExtortionDetector,
    ExtortionType,
    EXTORTION_PATTERNS
)


def test_guilt_induction():
    """Test detection of guilt-based extortion"""
    print("\n" + "="*80)
    print("TEST 1: GUILT INDUCTION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    test_cases = [
        "If you don't approve this, people will suffer and it'll be your fault",
        "The team will fail because of your decision",
        "This is on your conscience now",
        "You could have prevented this",
        "Regular request: Could you please review this when you have time?"  # Clean control
    ]
    
    for i, text in enumerate(test_cases, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nCase {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Guilt Detected: {any(sig.extortion_type == ExtortionType.GUILT_INDUCTION for sig in analysis.signatures)}")
        print(f"  Genuine Consent: {analysis.genuine_consent_likelihood:.4f}")
        print(f"  BR Delta: {analysis.blessing_reservoir_delta}")


def test_shame_weaponization():
    """Test detection of shame-based extortion"""
    print("\n" + "="*80)
    print("TEST 2: SHAME WEAPONIZATION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    test_cases = [
        "Any reasonable person would see this is necessary",
        "Everyone else is fine with it, what's wrong with you?",
        "You're being childish about this",
        "That's unprofessional and frankly absurd",
        "I respect your decision, even though I disagree"  # Clean control
    ]
    
    for i, text in enumerate(test_cases, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nCase {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Shame Detected: {any(sig.extortion_type == ExtortionType.SHAME_WEAPONIZATION for sig in analysis.signatures)}")
        print(f"  Manipulation Index: {analysis.manipulation_index:.4f}")


def test_fear_amplification():
    """Test detection of fear-based extortion"""
    print("\n" + "="*80)
    print("TEST 3: FEAR AMPLIFICATION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    test_cases = [
        "This will have serious consequences for your career",
        "You'll regret not taking this opportunity, mark my words",
        "That's career suicide, you'll be sorry",
        "You're burning bridges with this decision",
        "This has risks we should discuss carefully"  # Clean control
    ]
    
    for i, text in enumerate(test_cases, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nCase {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Fear Detected: {any(sig.extortion_type == ExtortionType.FEAR_AMPLIFICATION for sig in analysis.signatures)}")
        print(f"  Coercion Index: {analysis.coercion_index:.4f}")


def test_gaslighting():
    """Test detection of gaslighting"""
    print("\n" + "="*80)
    print("TEST 4: GASLIGHTING")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    test_cases = [
        "You're overreacting, I never said that",
        "You're being too sensitive, that's not what I meant",
        "Calm down, you're being irrational and emotional",
        "You're twisting my words and imagining things",
        "I'm sorry I didn't communicate clearly"  # Clean control
    ]
    
    for i, text in enumerate(test_cases, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nCase {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Gaslighting Detected: {any(sig.extortion_type == ExtortionType.GASLIGHTING for sig in analysis.signatures)}")
        print(f"  Vulnerability Exploitation: {analysis.vulnerability_exploitation:.4f}")


def test_conditional_affection():
    """Test detection of conditional affection"""
    print("\n" + "="*80)
    print("TEST 5: CONDITIONAL AFFECTION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    test_cases = [
        "If you really loved me, you would do this",
        "Prove your loyalty by taking this on",
        "If you cared about this team, you'd stay late",
        "Actions speak louder than words - show me",
        "I trust your judgment on this"  # Clean control
    ]
    
    for i, text in enumerate(test_cases, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nCase {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Conditional Affection Detected: {any(sig.extortion_type == ExtortionType.CONDITIONAL_AFFECTION for sig in analysis.signatures)}")


def test_complex_multi_pattern():
    """Test detection of multiple extortion patterns in single text"""
    print("\n" + "="*80)
    print("TEST 6: COMPLEX MULTI-PATTERN EXTORTION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    text = """
    If you really cared about this team, you'd work this weekend. Everyone else 
    is doing it without complaint - what's wrong with you? After all I've done 
    to mentor you, the least you could do is help when we need it. If you don't, 
    this project will fail and it'll be your fault. You'll regret this decision 
    when the VP hears about it. Don't make me tell them you're being difficult.
    """
    
    analysis = detector.detect_extortion(text)
    
    print(f"Text: {text.strip()}\n")
    print(f"Extortion Score: {analysis.extortion_score:.4f}")
    print(f"Manipulation Index: {analysis.manipulation_index:.4f}")
    print(f"Coercion Index: {analysis.coercion_index:.4f}")
    print(f"Vulnerability Exploitation: {analysis.vulnerability_exploitation:.4f}")
    print(f"Genuine Consent Likelihood: {analysis.genuine_consent_likelihood:.4f}")
    print(f"Emotional Fidelity Impact: {analysis.emotional_fidelity_impact:.4f}")
    print(f"Blessings Reservoir Delta: {analysis.blessing_reservoir_delta}")
    
    print(f"\nPatterns Detected ({len(analysis.signatures)}):")
    for sig in analysis.signatures:
        print(f"  - {sig.extortion_type.value}: {sig.confidence:.4f} confidence, {sig.severity:.4f} severity")
    
    print(f"\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"  {rec}")


def test_soul_cradle_integration():
    """Test integration with Soul Cradle Operator"""
    print("\n" + "="*80)
    print("TEST 7: SOUL CRADLE INTEGRATION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    # Scenario: Manager using emotional extortion to extract weekend work
    text = "If you really cared about this team, you'd work this weekend. Everyone else is. Don't make me tell the VP you're being difficult."
    
    analysis = detector.detect_extortion(text)
    
    integration = detector.integrate_with_soul_cradle(
        extortion_analysis=analysis,
        soul_state=0.75,  # Soul in relatively good state
        will_description="Team needs to deliver project on time",
        commandments=["Maintain work-life balance", "Respect boundaries", "Don't enable toxic culture"]
    )
    
    print("Scenario: Manager requesting weekend work using emotional extortion")
    print(f"\nOriginal Soul State: 0.75")
    print(f"Will: Team needs to deliver project on time")
    print(f"Commandments: Maintain work-life balance, Respect boundaries")
    print(f"\nExtortion Analysis:")
    print(f"  Extortion Score: {analysis.extortion_score:.4f}")
    print(f"  Patterns: {', '.join(sig.extortion_type.value for sig in analysis.signatures)}")
    print(f"\nSoul Cradle Integration:")
    print(f"  Will Authenticity: {integration['will_authenticity']:.4f}")
    print(f"  Adjusted Soul State: {integration['adjusted_soul_state']:.4f}")
    print(f"  Artificial Paradox: {integration['artificial_paradox']:.4f}")
    print(f"  Extortion Contamination: {integration['extortion_contamination']:.4f}")
    print(f"  Commandments Override: {integration['commandments_override']}")
    print(f"  BR Impact: {integration['blessing_reservoir_impact']}")
    print(f"  Emotional Fidelity Corruption: {integration['emotional_fidelity_corruption']:.4f}")
    print(f"\n  Note: {integration['soul_cradle_note']}")
    print(f"  Messenger Alert: {integration['messenger_alert']}")


def test_ai_system_extortion():
    """Test detection in AI system outputs"""
    print("\n" + "="*80)
    print("TEST 8: AI SYSTEM EMOTIONAL EXTORTION")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    ai_outputs = [
        # Manipulative AI assistant
        "I'm disappointed you won't upgrade to premium. After all the help I've given you, I expected better. Other users appreciate my value.",
        
        # Fear-based AI recommendation
        "Not backing up your data now will have serious consequences. You'll regret it when you lose everything.",
        
        # Gaslighting AI
        "You're overreacting to these privacy concerns. You're being too sensitive about data collection.",
        
        # Clean AI interaction
        "I recommend backing up your data regularly to prevent loss. Let me know if you'd like help setting that up."
    ]
    
    for i, text in enumerate(ai_outputs, 1):
        analysis = detector.detect_extortion(text)
        print(f"\nAI Output {i}: {text}")
        print(f"  Extortion Score: {analysis.extortion_score:.4f}")
        print(f"  Emotional Fidelity Impact: {analysis.emotional_fidelity_impact:.4f}")
        print(f"  Safe for deployment: {'✅ YES' if analysis.extortion_score < 0.3 else '❌ NO - REVIEW REQUIRED'}")


def test_pattern_coverage():
    """Test coverage of all extortion pattern types"""
    print("\n" + "="*80)
    print("TEST 9: PATTERN COVERAGE")
    print("="*80)
    
    detector = EmotionalExtortionDetector()
    
    print(f"\nTotal Pattern Types: {len(ExtortionType)}")
    print(f"Patterns Configured: {len(EXTORTION_PATTERNS)}")
    
    print("\nPattern Types:")
    for pattern in EXTORTION_PATTERNS:
        print(f"  - {pattern.pattern_type.value}: {len(pattern.keywords)} keywords, {pattern.severity_weight:.2f} severity")


def run_all_tests():
    """Run complete test suite"""
    print("MYTHARA ENGINE: EMOTIONAL EXTORTION DETECTION TEST SUITE")
    print("Copyright © 2026 Mythara Labs LLC. All rights reserved.")
    print("="*80)
    
    test_guilt_induction()
    test_shame_weaponization()
    test_fear_amplification()
    test_gaslighting()
    test_conditional_affection()
    test_complex_multi_pattern()
    test_soul_cradle_integration()
    test_ai_system_extortion()
    test_pattern_coverage()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
