# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Test script to demonstrate RAG-powered email assistant with sales psychology

NOTE: all people, titles, and companies in the fixtures below are fictional
stand-ins for testing — never treat them as real prospects or customers.
"""

import os
from email_assistant import EmailAssistant

# Set OpenAI API key (replace with your actual key)
# os.environ['OPENAI_API_KEY'] = 'sk-proj-YOUR-KEY-HERE'

def test_interested_reply():
    """Test response to interested prospect"""
    print("="*80)
    print("TEST 1: INTERESTED PROSPECT")
    print("="*80)
    
    email_data = {
        'subject': 'Re: AI Agent Override Accountability for Model Risk',
        'body': """Hi Herbert,

This looks interesting. We've been struggling with our model risk committee 
requiring audit trails for every AI override. Our compliance team keeps asking 
us to prove why agents approved certain high-risk loans.

I'd like to learn more.

Sarah Chen
VP Model Risk, Example Bank (fictional fixture)"""
    }
    
    ea = EmailAssistant()
    intent, confidence = ea.categorize_intent(
        email_data["body"], email_data["subject"]
    )
    print(f"\n📊 DETECTED INTENT: {intent}")
    
    draft = ea.generate_draft_response(email_data, intent)
    print(f"\n📧 DRAFT RESPONSE:\n\n{draft}")
    print("\n" + "="*80 + "\n")

def test_question_reply():
    """Test response to technical question"""
    print("="*80)
    print("TEST 2: TECHNICAL QUESTION")
    print("="*80)
    
    email_data = {
        'subject': 'Re: Mythara for Healthcare AI',
        'body': """Herbert,

How does your system handle HIPAA compliance? We need to ensure all 
AI decision logs are tamper-evident and auditable.

Also, can it integrate with our existing Epic EHR system?

Dr. James Park
CMIO, Example Health System (fictional fixture)"""
    }
    
    ea = EmailAssistant()
    intent, confidence = ea.categorize_intent(
        email_data["body"], email_data["subject"]
    )
    print(f"\n📊 DETECTED INTENT: {intent}")
    
    draft = ea.generate_draft_response(email_data, intent)
    print(f"\n📧 DRAFT RESPONSE:\n\n{draft}")
    print("\n" + "="*80 + "\n")

def test_not_interested_reply():
    """Test response to not interested"""
    print("="*80)
    print("TEST 3: NOT INTERESTED")
    print("="*80)
    
    email_data = {
        'subject': 'Re: AI Governance Platform',
        'body': """Hi Herbert,

Thanks for reaching out. We're not looking at new vendors right now. 
We just implemented a different solution last quarter.

Best,
Mike"""
    }
    
    ea = EmailAssistant()
    intent, confidence = ea.categorize_intent(
        email_data["body"], email_data["subject"]
    )
    print(f"\n📊 DETECTED INTENT: {intent}")
    
    draft = ea.generate_draft_response(email_data, intent)
    print(f"\n📧 DRAFT RESPONSE:\n\n{draft}")
    print("\n" + "="*80 + "\n")

def test_rag_search():
    """Test knowledge base search directly"""
    print("="*80)
    print("TEST 4: RAG KNOWLEDGE BASE SEARCH")
    print("="*80)
    
    from build_knowledge_base import KnowledgeBaseBuilder
    from pathlib import Path
    
    archive_root = Path(__file__).parent.parent
    kb = KnowledgeBaseBuilder(archive_root)
    
    queries = [
        "How does agent override accountability work?",
        "What are the security features?",
        "How does Mythara handle compliance?"
    ]
    
    for query in queries:
        print(f"\n🔍 QUERY: {query}")
        results = kb.search(query, n_results=2)
        print(f"📚 FOUND {len(results)} CHUNKS:")
        for i, chunk in enumerate(results, 1):
            print(f"\n  {i}. From: {chunk['filepath']}")
            print(f"     Text: {chunk['text'][:150]}...")
            print(f"     Distance: {chunk['distance']:.3f}")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    print("\n🚀 MYTHARA EMAIL ASSISTANT - RAG + SALES PSYCHOLOGY TEST\n")
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Install with:")
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set via environment
        print("Running RAG search test (doesn't need OpenAI)...\n")
        test_rag_search()
    else:
        print("✅ OpenAI API key detected\n")
        test_interested_reply()
        test_question_reply()
        test_not_interested_reply()
        test_rag_search()
