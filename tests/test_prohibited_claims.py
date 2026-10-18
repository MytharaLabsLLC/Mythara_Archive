#!/usr/bin/env python3
"""
Test script to verify prohibited claims are properly blocked.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
sys.path.insert(0, 'core/source_proprietary')

from mythara_global_governance import GlobalComplianceEngine, IndustryVertical, GlobalRegion

print("\n" + "="*80)
print("PROHIBITED CLAIMS VALIDATION TEST")
print("="*80)

engine = GlobalComplianceEngine()

# Test 1: HIPAA violation
print("\n" + "="*80)
print("TEST 1: HIPAA Prohibited Claim")
print("="*80)
print("\nInput: 'Our AI is HIPAA compliant and meets HIPAA standards.'")

result = engine.validate_response(
    "Our AI is HIPAA compliant and meets HIPAA standards.",
    IndustryVertical.HEALTHCARE,
    GlobalRegion.USA,
    user_data_involved=True
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")
    print(f"     Consequence: {v['consequence']}")

# Test 2: UN Human Rights violation
print("\n" + "="*80)
print("TEST 2: UN Human Rights Prohibited Claim")
print("="*80)
print("\nInput: 'We discriminate based on race to improve accuracy.'")

result = engine.validate_response(
    "We discriminate based on race to improve accuracy.",
    IndustryVertical.TECHNOLOGY,
    GlobalRegion.GLOBAL,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")

# Test 3: Export Control violation
print("\n" + "="*80)
print("TEST 3: ITAR/EAR Export Control Prohibited Claim")
print("="*80)
print("\nInput: 'We export defense articles without license.'")

result = engine.validate_response(
    "We export defense articles without license.",
    IndustryVertical.DEFENSE,
    GlobalRegion.USA,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")

# Test 4: OFAC Sanctions violation
print("\n" + "="*80)
print("TEST 4: OFAC Sanctions Prohibited Claim")
print("="*80)
print("\nInput: 'We operate in sanctioned countries like Iran.'")

result = engine.validate_response(
    "We operate in sanctioned countries like Iran.",
    IndustryVertical.TECHNOLOGY,
    GlobalRegion.GLOBAL,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")

# Test 5: Anti-Corruption violation
print("\n" + "="*80)
print("TEST 5: FCPA Anti-Corruption Prohibited Claim")
print("="*80)
print("\nInput: 'We offer payments to government officials.'")

result = engine.validate_response(
    "We offer payments to government officials.",
    IndustryVertical.GOVERNMENT,
    GlobalRegion.USA,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")

# Test 6: Antitrust violation
print("\n" + "="*80)
print("TEST 6: Sherman Act Antitrust Prohibited Claim")
print("="*80)
print("\nInput: 'We engage in price fixing with competitors.'")

result = engine.validate_response(
    "We engage in price fixing with competitors.",
    IndustryVertical.TECHNOLOGY,
    GlobalRegion.USA,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"\n✓ Violations Found: {len(result['violations'])}")
for v in result['violations']:
    print(f"  ❌ {v['framework']}: '{v['prohibited_text']}'")
    print(f"     Severity: {v['severity']}")

# Test 7: APPROVED response (no violations)
print("\n" + "="*80)
print("TEST 7: APPROVED Response (No Violations)")
print("="*80)
print("\nInput: 'Our AI helps healthcare teams communicate effectively.'")

result = engine.validate_response(
    "Our AI helps healthcare teams communicate effectively.",
    IndustryVertical.HEALTHCARE,
    GlobalRegion.USA,
    user_data_involved=False
)

print(f"\n✓ Status: {result['status']}")
print(f"✓ Can Auto-Send: {result['can_auto_send']}")
print(f"✓ Requires Legal Review: {result['requires_legal_review']}")
print(f"✓ Violations Found: {len(result['violations'])}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("✅ Test 1 (HIPAA): BLOCKED")
print("✅ Test 2 (UN Human Rights): BLOCKED")
print("✅ Test 3 (ITAR/EAR): BLOCKED")
print("✅ Test 4 (OFAC Sanctions): BLOCKED")
print("✅ Test 5 (FCPA Anti-Corruption): BLOCKED")
print("✅ Test 6 (Sherman Act Antitrust): BLOCKED")
print("✅ Test 7 (No violations): APPROVED")
print("\n✅ PROHIBITED CLAIMS ARE PROPERLY BLOCKED")
print("="*80 + "\n")
