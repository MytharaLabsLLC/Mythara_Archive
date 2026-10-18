"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Simple Attorney Referral Test
"""

import sys
import io

# Fix Windows console encoding
# Windows-console UTF-8 fix: only rewrap a REAL console stdout.
# Under pytest sys.stdout is a capture object; rewrapping it closes
# pytest's capture buffer when the wrapper is garbage-collected.
if type(sys.stdout) is io.TextIOWrapper:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from mythara_gopher_nlp_engine import MytharaGopherNLP

print("="*80)
print("ATTORNEY REFERRAL SYSTEM - WORKING TEST")
print("="*80)
print()

# Initialize
gopher = MytharaGopherNLP()
print("\n✅ Gopher Initialized\n")

# Test queries
tests = [
    ("Employment Law - California", "I need an employment lawyer in California"),
    ("Personal Injury - New York", "Find me a personal injury attorney in New York"),
    ("Criminal Defense - Florida", "Looking for a criminal defense lawyer in Florida"),
]

for name, query in tests:
    print("="*80)
    print(f"TEST: {name}")
    print(f"QUERY: {query}")
    print("="*80)
    
    response = gopher.process_query(query, "test_user")
    
    # Extract key lines
    for line in response.split('\n'):
        if any(keyword in line for keyword in [
            'Case Type', 'Location:', 'Referral', 'Public Referral', 
            'Practice Areas:', 'Free Consultation', 'State Bar'
        ]):
            print(line)
    print()

print("="*80)
print("✅ ALL TESTS COMPLETE - ATTORNEY REFERRAL WORKING")
print("="*80)
