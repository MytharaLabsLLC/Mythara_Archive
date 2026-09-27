# Mythara Gopher - Quick Document Reference

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

## Quick Command Reference

### Generate Complaint (Start Lawsuit)
```python
doc = gopher.generate_complaint(
    plaintiff_name="Your Name",
    defendant_name="Defendant Name",
    court_name="Superior Court",
    case_number="CV-2025-1234",
    jurisdiction="State/County",
    causes_of_action=["Negligence", "Breach of Contract"],
    facts="What happened...",
    damages="$X in damages",
    prayer_for_relief="A. Award damages; B. Award costs..."
)
```

### Generate Motion
```python
doc = gopher.generate_motion(
    motion_type="Motion to Compel",
    case_caption="Plaintiff v. Defendant",
    case_number="CV-2025-1234",
    court_name="Superior Court",
    moving_party="Plaintiff",
    legal_basis="Legal standard...",
    argument="Why you should win...",
    relief_sought="what you want court to do"
)
```

### Generate Interrogatories (Questions)
```python
doc = gopher.generate_interrogatories(
    propounding_party="Plaintiff",
    responding_party="Defendant",
    case_caption="Plaintiff v. Defendant",
    case_number="CV-2025-1234",
    interrogatory_questions=[
        "Question 1?",
        "Question 2?",
        "Question 3?"
    ]
)
```

### Generate Request for Production (Documents)
```python
doc = gopher.generate_request_for_production(
    requesting_party="Plaintiff",
    producing_party="Defendant",
    case_caption="Plaintiff v. Defendant",
    case_number="CV-2025-1234",
    document_requests=[
        "All contracts...",
        "All emails...",
        "All records..."
    ]
)
```

### Generate Request for Admissions
```python
doc = gopher.generate_request_for_admissions(
    requesting_party="Plaintiff",
    admitting_party="Defendant",
    case_caption="Plaintiff v. Defendant",
    case_number="CV-2025-1234",
    admission_statements=[
        "the contract was signed on X date",
        "you breached the contract",
        "damages exceed $10,000"
    ]
)
```

### Generate Answer (Respond to Lawsuit)
```python
doc = gopher.generate_answer(
    defendant_name="Your Name",
    plaintiff_name="Person Who Sued You",
    case_caption="Smith v. Jones",
    case_number="CV-2025-1234",
    court_name="Superior Court",
    admissions=["1", "2"],      # Admit paragraphs 1, 2
    denials=["3", "4", "5"],    # Deny paragraphs 3, 4, 5
    affirmative_defenses=[
        "Statute of Limitations",
        "Failure to State a Claim"
    ]
)
```

### Generate Affidavit (Sworn Statement)
```python
doc = gopher.generate_affidavit(
    affiant_name="Your Name",
    case_caption="Case Caption",
    case_number="CV-2025-1234",
    statements=[
        "I am over 18 and competent",
        "I witnessed the incident",
        "Specific fact 1",
        "Specific fact 2"
    ],
    purpose="Support Motion for Summary Judgment",
    jurisdiction="California"
)
```

### Generate Subpoena
```python
doc = gopher.generate_subpoena(
    issuing_party="Plaintiff",
    recipient_name="Witness/Organization Name",
    case_caption="Case Caption",
    case_number="CV-2025-1234",
    court_name="Superior Court",
    subpoena_type="duces_tecum",  # or "testimony" or "both"
    appearance_date="January 15, 2026",
    appearance_location="Court address",
    documents_requested=[
        "Document 1",
        "Document 2"
    ]
)
```

## Save Document to File
```python
# Generate any document
doc = gopher.generate_complaint(...)

# Save to file (creates legal_documents/ folder)
filepath = doc.to_file()

# Save to custom location
filepath = doc.to_file(output_dir="my_case_files")

# Document includes SHA-256 hash and timestamp automatically
```

## Interactive Mode
```python
from mythara_gopher_nlp_engine import MytharaGopherNLP

gopher = MytharaGopherNLP()

# Ask Gopher naturally
response = gopher.process_query(
    "I need to file a complaint for wrongful termination",
    user_id="user123"
)
print(response)

# Gopher guides you through document generation
```

## Document Types Summary

| Document | Purpose | Timeline |
|----------|---------|----------|
| **Complaint** | Start lawsuit | File to begin case |
| **Answer** | Respond to lawsuit | 20-30 days after service |
| **Motion** | Request court order | As needed during case |
| **Interrogatories** | Ask written questions | Response due in 30 days |
| **RFP** | Demand documents | Response due in 30 days |
| **RFA** | Request admissions | Response due in 30 days |
| **Subpoena** | Compel testimony/docs | As needed for trial/depo |
| **Affidavit** | Sworn statement | Attach to motions |
| **Demand Letter** | Pre-lawsuit demand | 30-day deadline to respond |
| **Cease & Desist** | Stop violations | As needed |

## Key Features

✅ **SHA-256 Timestamping** - All documents cryptographically timestamped  
✅ **Tamper-Evident** - Integrity hash detects any modifications  
✅ **Professional legal formatting**  
✅ **Forensic Audit Trail** - Hash-chained integrity trail  
✅ **Timestamped Records** - SHA-256 timestamps support the evidentiary trail (admissibility is determined by the court)  

## Common Workflows

### Lawsuit Workflow
1. **Demand Letter** → Give opponent chance to settle
2. **Complaint** → File lawsuit if no settlement
3. **Discovery** → Interrogatories, RFP, RFA
4. **Motions** → Motion for summary judgment, etc.
5. **Trial** → Affidavits, subpoenas for witnesses

### Responding to Lawsuit
1. **Answer** → Must file within 20-30 days!
2. **Discovery Responses** → Answer interrogatories, produce documents
3. **Counter Discovery** → Send your own interrogatories/RFP
4. **Motions** → Motion to dismiss, summary judgment

### Discovery Strategy
1. **Interrogatories** → Get basic facts, identify witnesses
2. **RFP** → Get copies of key documents
3. **RFA** → Establish undisputed facts
4. **Subpoenas** → Get documents from third parties
5. **Depositions** → Question witnesses under oath

## Pro Tips

💡 **Always Verify Deadlines** - Different jurisdictions have different timelines  
💡 **Proofread Everything** - Check names, dates, case numbers  
💡 **Keep Copies** - Save all documents with SHA-256 hashes  
💡 **Serve Properly** - Follow service of process rules  
💡 **Consult Attorney** - Before filing anything in court  

## Legal Disclaimer

⚠️ These documents are for **PERSONAL USE ONLY**  
⚠️ This is **NOT LEGAL ADVICE**  
⚠️ Does **NOT** create attorney-client relationship  
⚠️ **CONSULT ATTORNEY** before filing any documents  
⚠️ Information may be outdated - verify with attorney  

## Demo & Documentation

**Run Comprehensive Demo:**
```bash
python demo_comprehensive_documents.py
```

**Full Documentation:**
See `COMPREHENSIVE_DOCUMENT_GENERATION.md` for detailed examples and best practices.

---

**Remember:** Gopher is a document preparation tool. Always consult a licensed attorney before taking legal action!
