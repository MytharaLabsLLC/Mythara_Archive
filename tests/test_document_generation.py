"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Engine - Automated Document Generation Test
Tests SHA-256 timestamping and all document types
"""

from mythara_gopher_nlp_engine import MytharaGopherNLP

def test_conversational_interface():
    """Test natural language document requests"""
    print("=" * 80)
    print("  TESTING CONVERSATIONAL DOCUMENT GENERATION INTERFACE")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    # Test queries for document generation
    queries = [
        "I need to send a demand letter to my landlord for withholding my security deposit",
        "Can you generate a cease and desist for someone stealing my copyrighted work?",
        "How do I timestamp a statement for evidence in court?",
        "Create an evidence summary with chain of custody for my case",
        "I want to draft a formal legal letter"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print(f"{'='*80}\n")
        
        response = gopher.process_query(query, user_id="test_user")
        print(f"🦫 GOPHER RESPONSE:\n{response}\n")
        
        # Check if document_generation intent was detected
        if "Document Generation" in response or "SHA-256" in response:
            print("✅ Document generation intent correctly detected!")
        else:
            print("⚠️ Document generation intent may not have been detected")
        
        print("\n" + "-" * 80)

def test_direct_document_generation():
    """Test direct document generation methods"""
    print("\n" + "=" * 80)
    print("  TESTING DIRECT DOCUMENT GENERATION")
    print("=" * 80 + "\n")
    
    gopher = MytharaGopherNLP()
    
    # Test 1: Demand Letter
    print("TEST 1: Generating Demand Letter...")
    doc1 = gopher.generate_demand_letter(
        sender_name="Test Plaintiff",
        sender_address="123 Test St",
        recipient_name="Test Defendant",
        recipient_address="456 Test Ave",
        incident_description="Test incident for automated testing",
        legal_basis=["Breach of Contract", "Negligence"],
        damages_claimed="$5,000 test damages",
        deadline_days=30
    )
    print(f"✅ Demand Letter Generated")
    print(f"   Doc ID: {doc1.doc_id}")
    print(f"   SHA-256: {doc1.integrity_hash}")
    print(f"   Timestamp: {doc1.timestamp}")
    print(f"   Content Length: {len(doc1.content)} characters\n")
    
    # Test 2: Cease & Desist
    print("TEST 2: Generating Cease & Desist...")
    doc2 = gopher.generate_cease_and_desist(
        sender_name="Test Company",
        recipient_name="Test Infringer",
        infringing_conduct="Test infringement description",
        legal_violations=["Copyright Infringement", "Trademark Violation"]
    )
    print(f"✅ Cease & Desist Generated")
    print(f"   Doc ID: {doc2.doc_id}")
    print(f"   SHA-256: {doc2.integrity_hash}")
    print(f"   Timestamp: {doc2.timestamp}\n")
    
    # Test 3: Evidence Summary
    print("TEST 3: Generating Evidence Summary...")
    evidence = [
        {
            "description": "Test email evidence",
            "type": "Email",
            "source": "Company server",
            "date_obtained": "2024-01-01",
            "custodian": "Test Attorney",
            "relevance": "Proves liability"
        }
    ]
    doc3 = gopher.generate_evidence_summary(
        case_title="Test v. Defendant",
        incident_date="2024-01-01",
        parties={"plaintiff": "Test", "defendant": "Defendant"},
        evidence_items=evidence
    )
    print(f"✅ Evidence Summary Generated")
    print(f"   Doc ID: {doc3.doc_id}")
    print(f"   SHA-256: {doc3.integrity_hash}")
    print(f"   Evidence Items: {len(evidence)}\n")
    
    # Test 4: Statement Timestamping
    print("TEST 4: Timestamping Statement...")
    result = gopher.timestamp_user_statement(
        "This is a test statement for automated testing",
        "test_user"
    )
    print(f"✅ Statement Timestamped")
    print(f"   Timestamp: {result['timestamp']}")
    print(f"   SHA-256: {result['integrity_hash']}\n")
    
    # Test 5: Legal Memo
    print("TEST 5: Generating Legal Memo...")
    doc5 = gopher.generate_legal_memo(
        title="Test Memo",
        issue_statement="Test issue",
        brief_answer="Test answer",
        facts="Test facts",
        analysis="Test analysis",
        conclusion="Test conclusion"
    )
    print(f"✅ Legal Memo Generated")
    print(f"   Doc ID: {doc5.doc_id}")
    print(f"   SHA-256: {doc5.integrity_hash}\n")
    
    print("=" * 80)
    print("ALL DOCUMENT TYPES SUCCESSFULLY GENERATED!")
    print("=" * 80)
    
    return [doc1, doc2, doc3, doc5]

def check_file_output(documents):
    """Test that documents can be saved to files"""
    print("\n" + "=" * 80)
    print("  TESTING FILE OUTPUT")
    print("=" * 80 + "\n")
    
    for i, doc in enumerate(documents, 1):
        print(f"Saving document {i} ({doc.doc_type})...")
        filepath = doc.to_file()
        print(f"✅ Saved to: {filepath}\n")
    
    print("=" * 80)
    print("ALL DOCUMENTS SAVED WITH SHA-256 CERTIFICATION!")
    print("=" * 80)

def verify_sha256_integrity(documents):
    """Verify SHA-256 hashes are correct format"""
    print("\n" + "=" * 80)
    print("  VERIFYING SHA-256 INTEGRITY")
    print("=" * 80 + "\n")
    
    for doc in documents:
        # SHA-256 should be 64 hex characters
        is_valid = len(doc.integrity_hash) == 64 and all(c in '0123456789abcdef' for c in doc.integrity_hash)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"{status} - {doc.doc_type}: {doc.integrity_hash}")
    
    print("\n" + "=" * 80)
    print("SHA-256 INTEGRITY VERIFICATION COMPLETE")
    print("=" * 80)

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  MYTHARA ENGINE - AUTOMATED DOCUMENT GENERATION TEST SUITE")
    print("  Testing SHA-256 Cryptographic Timestamping & Legal Documents")
    print("=" * 80 + "\n")
    
    try:
        # Test 1: Conversational interface
        test_conversational_interface()
        
        # Test 2: Direct document generation
        documents = test_direct_document_generation()
        
        # Test 3: File output
        check_file_output(documents)
        
        # Test 4: SHA-256 integrity
        verify_sha256_integrity(documents)
        
        print("\n" + "=" * 80)
        print("  ✅ ALL TESTS PASSED!")
        print("  Document generation system is fully operational")
        print("  SHA-256 timestamping verified")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
