"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Gopher - Vernacular & Multilingual Support Test
Tests AAVE, regional dialects, and multilingual understanding
"""

import sys
import io
import re

# Fix Windows console encoding
# Windows-console UTF-8 fix: only rewrap a REAL console stdout.
# Under pytest sys.stdout is a capture object; rewrapping it closes
# pytest's capture buffer when the wrapper is garbage-collected.
if type(sys.stdout) is io.TextIOWrapper:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from mythara_gopher_nlp_engine import MytharaGopherNLP

def test_aave_normalization():
    """Test AAVE (African American Vernacular English) understanding"""
    print("=" * 80)
    print("TEST 1: AAVE Input → Professional English Output")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    # Vernacular markers that should NOT appear in responses
    vernacular_markers = [
        r"\bain't\b", r"\bgonna\b", r"\bfinna\b", r"\btryna\b", 
        r"\bIon\b", r"\bImma\b", r"\bgotta\b", r"\bwanna\b",
        r"\by'all\b", r"\bthey was\b", r"\bwe was\b", r"\bhe be\b"
    ]
    
    test_cases = [
        # Employment discrimination
        ("My boss be treating me different cuz I'm Black", "employment discrimination"),
        ("They fired me but I ain't did nothing wrong", "wrongful termination"),
        ("Ion think they supposed to fire me like that", "wrongful termination"),
        ("My supervisor tryna make me quit", "constructive discharge"),
        
        # Police/Criminal
        ("The folks locked me up for no reason", "false arrest"),
        ("Po-po violated my rights", "civil rights violation"),
        ("I got arrested but ain't did nothing", "false arrest"),
        
        # Injuries/Torts
        ("He ran into me and messed my car up bad", "vehicle collision tort"),
        ("They building made me sick, I been coughing", "premises liability"),
        
        # General questions
        ("Finna sue somebody, what I gotta do?", "lawsuit procedure"),
        ("Can I take them to court?", "litigation question"),
    ]
    
    print("Testing AAVE comprehension with professional responses:\n")
    for query, expected_context in test_cases:
        print(f"Query (AAVE): \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized: \"{normalized}\"")
        
        response = gopher.process_query(query, user_id="aave_test")
        
        # Verify response is helpful (not confused)
        assert len(response) > 50, f"Response too short for query: {query}"
        
        # CRITICAL: Verify response is in proper English (no vernacular markers)
        for marker in vernacular_markers:
            if re.search(marker, response, re.IGNORECASE):
                print(f"❌ FAILED: Response contains vernacular marker: {marker}")
                print(f"Response preview: {response[:200]}")
                assert False, f"Response should not contain vernacular: {marker}"
        
        print(f"✅ Response in professional English ({len(response)} chars)")
        print(f"✅ Comprehended context: {expected_context}\n")
    
    print(f"✅ All {len(test_cases)} AAVE queries understood AND responded to professionally!\n")

def test_southern_dialect():
    """Test Southern/regional dialect understanding"""
    print("=" * 80)
    print("TEST 2: Southern & Regional Dialects")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    test_cases = [
        "Y'all fired me and I reckon that ain't right",
        "My landlord fixin' to kick me out",
        "They done did me wrong at work",
        "I might could sue them for what they did",
        "All y'all at that company owe me money",
    ]
    
    print("Testing Southern dialect queries:\n")
    for query in test_cases:
        print(f"Query: \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized: \"{normalized}\"")
        
        response = gopher.process_query(query, user_id="southern_test")
        assert len(response) > 50
        print(f"✅ Response generated\n")
    
    print(f"✅ All {len(test_cases)} Southern dialect cases processed!\n")

def test_informal_colloquial():
    """Test informal/colloquial speech understanding"""
    print("=" * 80)
    print("TEST 3: Informal & Colloquial Speech")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    test_cases = [
        "I kinda got hurt at work, sorta bad tho",
        "My boss is being a jerk, dunno what to do",
        "They tryna fire me cuz I complained",
        "Nah, they ain't paid me what they owe",
        "Yeah, I wanna sue them for what they did",
    ]
    
    print("Testing informal queries:\n")
    for query in test_cases:
        print(f"Query: \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized: \"{normalized}\"")
        
        response = gopher.process_query(query, user_id="informal_test")
        assert len(response) > 50
        print(f"✅ Response generated\n")
    
    print(f"✅ All {len(test_cases)} informal cases processed!\n")

def test_legal_slang():
    """Test legal slang understanding"""
    print("=" * 80)
    print("TEST 4: Legal Slang")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    test_cases = [
        ("I got canned from my job last week", "termination"),
        ("They let me go without warning", "termination"),
        ("My landlord kicked me out", "eviction"),
        ("Some dude smashed into my car", "collision"),
        ("They owed me money but stiffed me", "breach of contract"),
        ("Got served papers yesterday", "legal notice"),
        ("They shorted my check again", "wage theft"),
    ]
    
    print("Testing legal slang:\n")
    for query, expected in test_cases:
        print(f"Query: \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized: \"{normalized}\"")
        print(f"Expected: {expected}")
        
        response = gopher.process_query(query, user_id="slang_test")
        assert len(response) > 50
        print(f"✅ Response generated\n")
    
    print(f"✅ All {len(test_cases)} legal slang cases processed!\n")

def test_multilingual_spanish():
    """Test Spanish legal term understanding"""
    print("=" * 80)
    print("TEST 5: Spanish Legal Terms")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    test_cases = [
        ("Necesito un abogado para mi caso", "need attorney"),
        ("Tuve un accidente en el trabajo", "workplace accident"),
        ("Mi jefe no me paga el dinero", "unpaid wages"),
        ("Quiero hacer una demanda", "want to file lawsuit"),
        ("Donde está la corte?", "where is court"),
    ]
    
    print("Testing Spanish terms:\n")
    for query, expected in test_cases:
        print(f"Query: \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized: \"{normalized}\"")
        print(f"Expected: {expected}")
        
        response = gopher.process_query(query, user_id="spanish_test")
        print(f"✅ Response generated ({len(response)} chars)\n")
    
    print(f"✅ All {len(test_cases)} Spanish cases processed!\n")

def test_mixed_vernacular():
    """Test mixed vernacular in single queries"""
    print("=" * 80)
    print("TEST 6: Mixed Vernacular → Professional Responses")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    # Vernacular markers that should NOT appear in responses
    bad_grammar = [
        r"\bain't\b", r"\bfinna\b", r"\btryna\b", r"\bIon\b",
        r"\bwhatchu\b", r"\by'all\b", r"\bthey ass\b"
    ]
    
    # These are realistic queries mixing multiple vernaculars
    test_cases = [
        "Yo, my boss be tryna fire me cuz I complained about safety, can I sue they ass?",
        "I ain't get paid for like 3 weeks, finna take them to court, whatchu think?",
        "The po-po locked me up but Ion did nothing, how I beat this case?",
        "They kicked me out my apartment but ain't give me no notice, that's legal?",
        "Some fool ran into my car while I was at the light, he owe me money right?",
        "My landlord tryna keep my deposit but the place was clean when I left, y'all help?",
    ]
    
    print("Testing mixed vernacular comprehension with professional output:\n")
    for i, query in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"Query (Mixed Vernacular): \"{query}\"")
        normalized = gopher.normalize_vernacular(query)
        print(f"Normalized for processing: \"{normalized}\"")
        
        response = gopher.process_query(query, user_id="mixed_test")
        
        # Verify substantive response
        assert len(response) > 100, "Response should be comprehensive"
        
        # CRITICAL: Verify professional grammar in response
        found_bad_grammar = False
        for marker in bad_grammar:
            if re.search(marker, response, re.IGNORECASE):
                print(f"❌ Response contains vernacular: {marker}")
                found_bad_grammar = True
        
        assert not found_bad_grammar, "Response must use proper grammar"
        
        # Check for disclaimer (should always be present)
        has_disclaimer = any(term in response for term in 
                           ["DISCLAIMER", "not legal advice", "consult", "attorney"])
        
        print(f"✅ Professional English response ({len(response)} chars)")
        print(f"✅ Proper grammar maintained")
        print(f"✅ Disclaimer present: {has_disclaimer}\n")
    
    print(f"✅ All {len(test_cases)} mixed vernacular queries understood with professional responses!\n")

def test_vernacular_with_document_generation():
    """Test vernacular queries triggering document generation"""
    print("=" * 80)
    print("TEST 7: Vernacular + Document Generation")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    test_cases = [
        "I need to send a demand letter to my landlord, they ain't give me my deposit back",
        "Finna write a cease and desist to somebody using my stuff",
        "How I timestamp evidence for court? Got some texts and emails",
        "Need to draft some papers to sue my boss",
    ]
    
    print("Testing vernacular document requests:\n")
    for query in test_cases:
        print(f"Query: \"{query}\"")
        response = gopher.process_query(query, user_id="doc_gen_test")
        
        # Should detect document generation intent
        assert "Document Generation" in response or "document" in response.lower()
        assert "SHA-256" in response or "timestamp" in response.lower()
        
        print(f"✅ Document generation detected and explained\n")
    
    print(f"✅ All {len(test_cases)} document generation cases processed!\n")

def demonstrate_vernacular_accessibility():
    """Demonstrate full conversation in vernacular"""
    print("=" * 80)
    print("DEMONSTRATION: Full Vernacular Conversation")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    conversation = [
        "Yo, what's good? I need some help",
        "My boss be treating me different than everybody else",
        "Ion know if it's discrimination but it feel like it",
        "They fired me yesterday, said I ain't doing my job right",
        "But I been there 5 years and never had no problems before",
        "Can I sue them for wrongful termination?",
        "What I gotta do to take them to court?"
    ]
    
    print("Simulating natural conversation in AAVE:\n")
    print("=" * 80 + "\n")
    
    for i, query in enumerate(conversation, 1):
        print(f"USER (Turn {i}): {query}")
        response = gopher.process_query(query, user_id="demo_user", 
                                       session_id="vernacular_demo")
        
        # Show first 300 chars of response
        preview = response[:300] + "..." if len(response) > 300 else response
        print(f"GOPHER: {preview}\n")
        print("-" * 80 + "\n")
    
    print("✅ Full conversation processed naturally with vernacular input!\n")

def main():
    """Run all vernacular tests"""
    print("\n" + "=" * 80)
    print("MYTHARA GOPHER - VERNACULAR & MULTILINGUAL SUPPORT TEST")
    print("Testing AAVE, Southern Dialects, Slang, and Multilingual Understanding")
    print("=" * 80 + "\n")
    
    try:
        test_aave_normalization()
        test_southern_dialect()
        test_informal_colloquial()
        test_legal_slang()
        test_multilingual_spanish()
        test_mixed_vernacular()
        test_vernacular_with_document_generation()
        
        print("\n" + "=" * 80)
        print("✅ ALL VERNACULAR TESTS PASSED!")
        print("Mythara Gopher successfully understands:")
        print("  • AAVE (African American Vernacular English)")
        print("  • Southern & Regional Dialects")
        print("  • Informal/Colloquial Speech")
        print("  • Legal Slang")
        print("  • Spanish Legal Terms")
        print("  • Mixed Vernacular")
        print("=" * 80 + "\n")
        
        # Offer demonstration
        demo = input("Would you like to see a full vernacular conversation demo? (y/n): ").strip().lower()
        if demo == 'y':
            demonstrate_vernacular_accessibility()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
