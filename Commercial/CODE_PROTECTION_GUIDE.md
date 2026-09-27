# Protecting Proprietary SSIP Code

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

> **Notes on this document.** All pricing in the licensing tiers below is *proposed*, not established — no licenses have been sold at these or any figures. Domains and addresses used in code examples (`api.mythara.com`, `sales@mythara.com`) are placeholders, not live services. Customer IDs in examples (`acme_bank_001`) are fictional.

---

## 🔒 HOW TO KEEP CODE HIDDEN

You have **5 options** to protect the proprietary SSIP governance logic:

---

## ✅ OPTION 1: PyArmor (RECOMMENDED)

**Best for:** Sharing code with customers while keeping it unreadable

```powershell
# Install PyArmor
py -3.11 -m pip install pyarmor

# Obfuscate the proprietary file
pyarmor gen sales_bot_ssip_governance.py

# This creates obfuscated version in dist/
# Deploy only the obfuscated files (unreadable even with decompilers)
```

**Result:**
- ✅ Customers can import and run it
- ❌ Customers CANNOT read the source
- ❌ Competitors CANNOT reverse engineer
- ✅ You can still update it

**Cost:** Free (community version) or $69/year (pro)

---

## ✅ OPTION 2: Cython Compilation (.pyd)

**Best for:** Maximum protection (compiles to machine code)

```powershell
# Install Cython
py -3.11 -m pip install cython

# Create setup.py
```

```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "sales_bot_ssip_governance.py",
        compiler_directives={'language_level': "3"}
    )
)
```

```powershell
# Compile to .pyd (Windows) or .so (Linux)
py -3.11 setup.py build_ext --inplace

# Deploy only the .pyd file (completely unreadable - it's compiled C)
```

**Result:**
- ✅ 100% unreadable (binary file)
- ❌ Customers CANNOT reverse engineer
- ✅ Fast execution (compiled C speed)
- ⚠️ Must compile for each OS (Windows .pyd vs Linux .so)

---

## ✅ OPTION 3: API-Only (No Code Shared)

**Best for:** Maximum security + recurring revenue

**You host the code on your server:**

```python
# server.py (you run this)
from fastapi import FastAPI, Header
from sales_bot_ssip_governance import SalesGovernanceEngine

app = FastAPI()

@app.post("/process-email")
async def process(email_data: dict, api_key: str = Header(...)):
    # Verify API key (customer subscription)
    if not validate_api_key(api_key):
        return {"error": "Invalid API key"}
    
    # Run proprietary logic on YOUR server
    engine = SalesGovernanceEngine()
    result = engine.process_email(email_data)
    
    # Return only results (not code)
    return result
```

**Customer uses it:**

```python
import requests

response = requests.post(
    "https://api.mythara.com/sales-bot/process",
    headers={"Authorization": "Bearer sk-mythara-abc123"},
    json={"subject": "...", "body": "..."}
)

result = response.json()
```

**Result:**
- ✅ Code NEVER leaves your server
- ✅ Customers pay per API call (recurring revenue)
- ✅ You can update anytime (no redeployment)
- ⚠️ Customers need internet connection
- ⚠️ You handle hosting/scaling

**Pricing model:**
- $500/month = 1,000 API calls
- $2,500/month = 10,000 calls
- $5,000/month = unlimited

---

## ✅ OPTION 4: License Key Protection

**Best for:** Preventing unauthorized use

```python
# sales_bot_ssip_governance.py (add at top)

import hashlib
from pathlib import Path

def _verify_license():
    """Verify valid Mythara license before running"""
    license_file = Path("mythara_license.key")
    
    if not license_file.exists():
        raise Exception(
            "No Mythara license found.\n"
            "Contact sales@mythara.com for licensing.\n"
            "Unauthorized use is prohibited."
        )
    
    license_key = license_file.read_text().strip()
    
    # Verify license signature (proprietary crypto)
    # This checks: customer_id + expiration + signature
    if not _validate_license_signature(license_key):
        raise Exception("Invalid or expired Mythara license")
    
    print(f"✅ Mythara license valid: {_get_customer_name(license_key)}")

# Run at module import
_verify_license()
```

**Generate license for customer:**

```python
# You run this to generate customer license
customer_id = "acme_bank_001"
expiration = "2026-12-31"
signature = _sign_license(customer_id, expiration, SECRET_KEY)

license_key = f"{customer_id}|{expiration}|{signature}"
# Send to customer: acme_bank_001|2026-12-31|a8f3e9c2...
```

**Result:**
- ✅ Code won't run without valid license
- ✅ You control expiration dates
- ✅ Can revoke licenses remotely
- ⚠️ Determined hackers might bypass (combine with obfuscation)

---

## ✅ OPTION 5: Just Don't Share It

**Best for:** Demos and your own use

Simply **DON'T include it** in customer deliverables:

**What you share:**
- ✅ `email_assistant.py` (your implementation, can be readable)
- ✅ `build_knowledge_base.py` (RAG system, can be readable)
- ✅ `bot_audit_log.jsonl` (transparency)
- ✅ Documentation

**What you keep:**
- ❌ `sales_bot_ssip_governance.py` (proprietary SSIP engine)
- ❌ Clause enforcement logic
- ❌ Blessings reservoir algorithm
- ❌ Integrity hashing implementation

**On sales calls:**

> "The email bot you see is governed by Mythara's SSIP engine.
> I can show you the audit trail and governance decisions,
> but the clause enforcement algorithm is proprietary.
> 
> For your use case (AI credit decisions), you'd license the
> same governance engine with your custom clauses."

---

## 🎯 RECOMMENDED STRATEGY

**For YOUR sales bot (internal use):**
- Keep source private (Option 5)
- Show only audit logs to prospects
- Use as demo ("this is Mythara governing our AI")

**For CUSTOMER deployments:**
- **Banking/Healthcare (high security):** API-only (Option 3)
  - You host, they call API
  - $2,500-$5,000/month recurring
  
- **Tech companies (moderate security):** PyArmor (Option 1)
  - They deploy on-prem
  - Code is obfuscated but functional
  - $2,500 one-time + $500/month support
  
- **Startups (lower security):** License key (Option 4)
  - They get source but needs license
  - $500-$2,500 one-time

**For GITHUB (if you open-source anything):**
- Open-source: Email assistant, RAG system, basic templates
- Proprietary: SSIP governance engine (commercial license only)
- Dual licensing: "Community edition" (basic) + "Enterprise edition" (full SSIP)

---

## 📦 WHAT TO DO RIGHT NOW

### Step 1: Protect `sales_bot_ssip_governance.py`

```powershell
# Quick obfuscation with PyArmor
py -3.11 -m pip install pyarmor
pyarmor gen sales_bot_ssip_governance.py

# Obfuscated version in: dist/sales_bot_ssip_governance.py
```

### Step 2: Add to .gitignore

```
# .gitignore (if using Git)
sales_bot_ssip_governance.py
bot_blessings.json
bot_audit_log.jsonl
mythara_license.key
```

### Step 3: Create public interface

Use `sales_bot_public_interface.py` (already created):
- Customers import this (not the raw governance file)
- Shows WHAT decisions were made (transparency)
- Hides HOW decisions are made (proprietary)

### Step 4: Demo statement

On sales calls:

> "I'm showing you the audit trail and governance stats.
> The clause enforcement engine itself is proprietary Mythara SSIP.
> Think of it like showing you AWS CloudWatch logs—you see the results,
> but the infrastructure is our proprietary technology.
> 
> For your pilot, you'd license the same engine with your custom clauses
> (credit limits, approval authority, etc.)."

---

## 💰 LICENSING TIERS

### **Tier 1: Demo/Proof-of-Concept** - FREE
- Show audit logs
- Explain how it works
- No code shared

### **Tier 2: Pilot** - $500
- 30-day trial
- Limited to 100 emails/month
- Obfuscated code OR API access
- License expires after 30 days

### **Tier 3: Production** - $2,500/month
- Unlimited emails
- On-prem deployment (obfuscated)
- OR API access (you host)
- Annual contract

### **Tier 4: Enterprise** - $5,000-$25,000/month
- Custom clauses
- Source code access (with NDA)
- Dedicated support
- Multi-year contract

---

## ✅ YOUR CODE IS NOW PROTECTED

- ✅ `sales_bot_ssip_governance.py` can be obfuscated (PyArmor)
- ✅ `sales_bot_public_interface.py` is your customer-facing API
- ✅ Demos show results, not implementation
- ✅ You control licensing and expiration
- ✅ Competitors can't steal the SSIP logic

**The proprietary magic stays yours. 🔒**
