"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Gopher - Legal Disclaimer Test
Verifies disclaimer integration across all features
"""

import sys
import io

# Fix Windows console encoding
# Windows-console UTF-8 fix: only rewrap a REAL console stdout.
# Under pytest sys.stdout is a capture object; rewrapping it closes
# pytest's capture buffer when the wrapper is garbage-collected.
if type(sys.stdout) is io.TextIOWrapper:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from mythara_gopher_nlp_engine import MytharaGopherNLP, MYTHARA_GOPHER_LEGAL_DISCLAIMER

def test_disclaimer_constant():
    """Test that disclaimer constant exists and has content"""
    print("=" * 80)
    print("TEST 1: Disclaimer Constant")
    print("=" * 80)
    
    assert len(MYTHARA_GOPHER_LEGAL_DISCLAIMER) > 500, "Disclaimer should be comprehensive"
    assert "NOT LEGAL ADVICE" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert ("attorney-client relationship" in MYTHARA_GOPHER_LEGAL_DISCLAIMER or 
            "attorney client relationship" in MYTHARA_GOPHER_LEGAL_DISCLAIMER), "Should mention attorney-client relationship"
    assert "NOT A SUBSTITUTE" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert "SHA-256" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert "USE AT YOUR OWN RISK" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert "publicly available databases" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert "may NOT be current" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    assert "consult a licensed attorney" in MYTHARA_GOPHER_LEGAL_DISCLAIMER.lower()
    assert "Herbert Velez Jr" in MYTHARA_GOPHER_LEGAL_DISCLAIMER
    
    print("✅ Disclaimer constant contains all required elements")
    print(f"   Length: {len(MYTHARA_GOPHER_LEGAL_DISCLAIMER)} characters\n")

def test_get_legal_disclaimer_method():
    """Test the get_legal_disclaimer method"""
    print("=" * 80)
    print("TEST 2: get_legal_disclaimer() Method")
    print("=" * 80)
    
    gopher = MytharaGopherNLP()
    
    # Test full disclaimer
    full_disclaimer = gopher.get_legal_disclaimer(brief=False)
    assert len(full_disclaimer) > 500
    assert "NOT LEGAL ADVICE" in full_disclaimer
    print("✅ Full disclaimer retrieval works")
    
    # Test brief disclaimer
    brief_disclaimer = gopher.get_legal_disclaimer(brief=True)
    assert len(brief_disclaimer) < 500
    assert "LEGAL DISCLAIMER" in brief_disclaimer
    assert "NOT legal advice" in brief_disclaimer
    assert "attorney-client relationship" in brief_disclaimer
    print("✅ Brief disclaimer retrieval works")
    print(f"   Brief length: {len(brief_disclaimer)} characters")
    print(f"   Full length: {len(full_disclaimer)} characters\n")

def test_greeting_includes_disclaimer():
    """Test that greeting includes disclaimer"""
    print("=" * 80)
    print("TEST 3: Greeting Includes Disclaimer")
    print("=" * 80)
    
    gopher = MytharaGopherNLP()
    
    # Test greeting queries
    greeting_queries = ["hello", "hi", "hey there"]
    
    for query in greeting_queries:
        response = gopher.process_query(query, user_id="test_user")
        assert "DISCLAIMER" in response or "LEGAL NOTICE" in response or "PLEASE NOTE" in response
        assert "NOT legal advice" in response or "not constitute legal advice" in response
        assert "consult" in response.lower()
        
    print(f"✅ All {len(greeting_queries)} greeting variations include disclaimer\n")

def test_document_generation_includes_disclaimer():
    """Test that document generation responses include disclaimer"""
    print("=" * 80)
    print("TEST 4: Document Generation Includes Disclaimer")
    print("=" * 80)
    
    gopher = MytharaGopherNLP()
    
    # Test document generation query
    query = "I need to send a demand letter"
    response = gopher.process_query(query, user_id="test_user")
    
    assert "LEGAL DISCLAIMER" in response
    assert "personal use" in response.lower()
    assert "NOT legal advice" in response
    
    print("✅ Document generation response includes disclaimer\n")

def test_show_disclaimer_intent():
    """Test that users can request to see disclaimer"""
    print("=" * 80)
    print("TEST 5: Show Disclaimer Intent")
    print("=" * 80)
    
    gopher = MytharaGopherNLP()
    
    # Test disclaimer request queries
    queries = [
        "show disclaimer",
        "what are your terms",
        "are you a lawyer",
        "can you give legal advice"
    ]
    
    for query in queries:
        response = gopher.process_query(query, user_id="test_user")
        # Should trigger disclaimer display
        assert len(response) > 500, f"Query '{query}' should show full disclaimer"
        assert "NOT LEGAL ADVICE" in response
        
    print(f"✅ All {len(queries)} disclaimer request variations work\n")

def test_generated_document_files_include_disclaimer():
    """Test that generated document files include disclaimer"""
    print("=" * 80)
    print("TEST 6: Generated Files Include Disclaimer")
    print("=" * 80)
    
    gopher = MytharaGopherNLP()
    
    # Generate a test document
    doc = gopher.generate_demand_letter(
        sender_name="Test User",
        sender_address="123 Test St",
        recipient_name="Test Recipient",
        recipient_address="456 Test Ave",
        incident_description="Test incident",
        legal_basis=["Test Tort"],
        damages_claimed="$1,000",
        deadline_days=30
    )
    
    # Save to file
    filepath = doc.to_file(output_dir="test_legal_documents")
    
    # Read file and check for disclaimer
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "LEGAL DISCLAIMER" in content
    assert "PERSONAL USE ONLY" in content
    assert "NOT legal advice" in content
    assert "does NOT create an attorney-client relationship" in content
    assert "consult a licensed attorney" in content
    assert "Use at your own risk" in content
    
    print(f"✅ Generated document file includes disclaimer")
    print(f"   File: {filepath}\n")
    
    # Cleanup
    import os
    import shutil
    if os.path.exists("test_legal_documents"):
        shutil.rmtree("test_legal_documents")
        print("✅ Test files cleaned up\n")

def test_disclaimer_key_terms():
    """Verify all required legal terms are present"""
    print("=" * 80)
    print("TEST 7: Required Legal Terms Present")
    print("=" * 80)
    
    required_terms = [
        "NOT LEGAL ADVICE",
        "attorney-client relationship",
        "NOT A SUBSTITUTE",
        "consult",
        "licensed attorney",
        "PERSONAL USE ONLY",
        "document preparation",
        "research",
        "NOT advise",
        "advocate",
        "publicly available databases",
        "NOT be current",
        "outdated",
        "SHA-256",
        "cryptographic timestamping",
        "user error",
        "USE AT YOUR OWN RISK",
        "DISCLAIM ALL WARRANTIES",
        "LIABILITY",
        "jurisdictional",
        "ethical",
        "unauthorized practice of law"
    ]
    
    disclaimer = MYTHARA_GOPHER_LEGAL_DISCLAIMER.lower()
    
    missing_terms = []
    for term in required_terms:
        if term.lower() not in disclaimer:
            missing_terms.append(term)
    
    if missing_terms:
        print(f"❌ Missing required terms: {missing_terms}")
        assert False, f"Disclaimer missing required terms: {missing_terms}"
    else:
        print(f"✅ All {len(required_terms)} required legal terms present\n")

def display_full_disclaimer():
    """Display the full disclaimer for manual review"""
    print("=" * 80)
    print("FULL DISCLAIMER TEXT FOR REVIEW")
    print("=" * 80)
    print(MYTHARA_GOPHER_LEGAL_DISCLAIMER)
    print("=" * 80 + "\n")

def main():
    """Run all disclaimer tests"""
    print("\n" + "=" * 80)
    print("MYTHARA GOPHER - LEGAL DISCLAIMER TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_disclaimer_constant()
        test_get_legal_disclaimer_method()
        test_greeting_includes_disclaimer()
        test_document_generation_includes_disclaimer()
        test_show_disclaimer_intent()
        test_generated_document_files_include_disclaimer()
        test_disclaimer_key_terms()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("Legal disclaimer is properly integrated across all features")
        print("=" * 80 + "\n")
        
        # Offer to display full disclaimer
        print("Would you like to see the full disclaimer text? (y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            display_full_disclaimer()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
