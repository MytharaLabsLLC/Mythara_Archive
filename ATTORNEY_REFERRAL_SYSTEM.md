# Attorney Referral System

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

---

## Overview

Mythara Gopher's Attorney Referral System connects users with qualified legal counsel based on:
- **Case type** (practice area)
- **Geographic location** (state)

The system maintains a **public database** of attorneys who have submitted their practice information for inclusion. 

⚠️ **IMPORTANT**: Mythara Gopher does NOT endorse or guarantee any attorney. Users must verify credentials independently.

---

## How to Use (For Users)

### Natural Language Queries

Simply ask Gopher for an attorney in natural language:

```
"I need an employment lawyer in California"
"Find me a personal injury attorney in New York"
"Looking for a criminal defense lawyer in Florida"
"I was wrongfully terminated in Los Angeles, need legal help"
"Can you recommend an immigration lawyer?"
"I need a lawyer for a car accident in Texas"
```

### What You'll Get

1. **Matched Attorneys**: Up to 5 attorneys matching your criteria
   - Name and firm
   - Practice areas
   - Location (cities covered)
   - Free consultation availability
   - Contact information (phone, email, website)
   
2. **State Bar Referral Services**: Official bar association referral links

3. **Legal Aid Resources**: Free/low-cost legal help for qualifying individuals

4. **Credential Verification Checklist**: How to verify attorney credentials

---

## Practice Areas Covered

| Practice Area | Keywords |
|--------------|----------|
| **Employment Law** | wrongful termination, discrimination, harassment, wage disputes, retaliation |
| **Personal Injury** | accidents, car crash, medical malpractice, slip and fall, negligence |
| **Landlord/Tenant** | eviction, rent disputes, security deposits, housing |
| **Family Law** | divorce, custody, child support, alimony |
| **Criminal Defense** | arrests, charges, DUI, felony, misdemeanor |
| **Civil Rights** | police misconduct, constitutional violations, discrimination |
| **Immigration** | visas, deportation, asylum, green card, citizenship |
| **Business Law** | contracts, partnerships, LLC, corporate |
| **Estate Planning** | wills, trusts, probate, inheritance |
| **Bankruptcy & Debt** | Chapter 7, Chapter 13, creditors |

---

## Geographic Coverage

*(Prototype design doc: the attorney database currently holds no entries — the states below are planned coverage, not live referral coverage.)*

Planned states:
- **CA** - California
- **NY** - New York
- **TX** - Texas
- **FL** - Florida
- **IL** - Illinois

**Expanding**: Database will grow to cover all 50 states as attorneys submit their information.

---

## For Attorneys: Join the Database

### How to Submit Your Practice

**Email**: attorney_referrals@mythara.com  
**Website**: https://mythara.com/attorney-referrals

### Information Required

1. **Attorney/Firm Name**
2. **Practice Areas** (select from list above)
3. **States** where you are licensed
4. **Cities/Counties** you serve
5. **Contact Information**:
   - Phone number
   - Email address
   - Website
6. **Free Consultation** availability (yes/no)
7. **Bar Admission Numbers** (for verification)

### Verification Process

Before inclusion:
- ✅ Bar license verification (active and in good standing)
- ✅ Disciplinary history check (must have clean record)
- ✅ Contact information validation

### No Fees

**This is a FREE public service.** No fees to be listed. No commissions or referral fees charged.

### Disclaimer

- Inclusion is NOT an endorsement by Mythara
- Users are responsible for their own due diligence
- Mythara does not guarantee any attorney's services
- Mythara is not liable for any attorney-client relationships

---

## Credential Verification (For Users)

Before hiring ANY attorney from our database (or anywhere else):

1. ✅ **Verify Bar License**: Check state bar website to confirm active license
2. ✅ **Check Disciplinary History**: Look for any past misconduct or sanctions
3. ✅ **Read Client Reviews**: Search Google, Yelp, Avvo, or other review sites
4. ✅ **Get Fee Agreement in Writing**: Understand costs upfront
5. ✅ **Meet for Consultation**: Many attorneys offer free consultations

### State Bar Verification Links

- **California**: https://www.calbar.ca.gov
- **New York**: https://www.nysba.org
- **Texas**: https://www.texasbar.com
- **Florida**: https://www.floridabar.org
- **Illinois**: https://www.isba.org

---

## Technical Implementation

### Database Structure

```python
{
    "practice_areas": {
        "employment": {
            "keywords": ["wrongful termination", "discrimination", ...],
            "description": "Employment Law (wrongful termination, discrimination, wage disputes)"
        },
        # ... 9 more practice areas
    },
    "attorneys": [
        {
            "name": "Attorney Name",
            "firm": "Firm Name",
            "practice_areas": ["employment", "civil_rights"],
            "states": ["CA", "NY"],
            "cities": ["Los Angeles", "San Francisco"],
            "phone": "(555) 123-4567",
            "email": "attorney@example.com",
            "website": "https://www.example.com",
            "free_consultation": True,
            "notes": "Additional information"
        }
    ],
    "bar_associations": {
        "CA": {"name": "State Bar of California", "website": "...", "phone": "..."}
    },
    "legal_aid": {
        "national": {"name": "Legal Services Corporation", "website": "...", ...}
    }
}
```

### Intent Pattern

```python
"attorney_referral": [
    r"\b(find|need|want|looking for|recommend|suggest).+(attorney|lawyer|counsel|legal help)\b",
    r"\b(attorney|lawyer|counsel).+(near me|in|for|who|that)\b",
    r"\b(get|find) (me )?(a |an )?(good |experienced )?(attorney|lawyer|counsel)\b",
    r"\b(referral|refer me to|connect me with).+(attorney|lawyer)\b",
    r"\b(who.+handle|specialist in|expert in).+(my case|wrongful termination|personal injury|landlord|employment)\b",
    r"\blawyer (directory|database|list|search)\b"
]
```

### Handler Method

```python
def _handle_attorney_referral(self, query: str, entities: Dict, context: ConversationContext) -> str:
    # 1. Extract jurisdiction (state codes: CA, NY, TX, etc.)
    # 2. Identify practice area from keywords
    # 3. Filter attorney database by jurisdiction AND practice area
    # 4. Display matching attorneys (top 5)
    # 5. Show state bar referral services
    # 6. Provide legal aid resources
    # 7. Include credential verification checklist
    # 8. Add attorney submission info
    # 9. Display referral disclaimer
```

---

## Examples

*(All example responses below are illustrative only — the attorney database currently holds no entries, so these responses do not reflect real listings.)*

### Example 1: Employment Law in California

**Query**: "I need an employment lawyer in California"

**Response**:
```
👨‍⚖️ **Attorney Referral Service**

**Case Type Detected:** Employment Law (wrongful termination, discrimination, wage disputes)

**Location:** CA

**✅ 1 Referral(s) Available:**

1. **Public Referral - California Employment Law**
   Firm: [Submit your firm - attorney_referrals@mythara.com]
   Practice Areas: Employment Law
   Location: Los Angeles, San Francisco, San Diego, Sacramento
   💡 Free Consultation Available
   📞 [To be listed]
   📧 attorney_referrals@mythara.com
   🌐 https://mythara.com/attorney-referrals
   ℹ️ Submit your practice info to be listed in public database

**📋 State Bar Referral Services:**

**State Bar of California**
   🌐 https://www.calbar.ca.gov
   📞 (866) 442-2529
   ℹ️ Free lawyer referral service

**💰 Free/Low-Cost Legal Help:**

**Legal Services Corporation**
   🌐 https://www.lsc.gov/what-legal-aid/find-legal-aid
   ℹ️ Find free legal aid in your area

**⚠️ VERIFY ATTORNEY CREDENTIALS:**
Before hiring any attorney:
1. ✅ Verify bar license (check state bar website)
2. ✅ Check disciplinary history
3. ✅ Read client reviews
4. ✅ Get fee agreement in writing
5. ✅ Meet for consultation (many offer free consults)

**📢 Attorneys: Join Our Public Database**
Submit your practice information for inclusion:
📧 attorney_referrals@mythara.com
🌐 https://mythara.com/attorney-referrals

**⚖️ REFERRAL DISCLAIMER:**
Mythara Gopher provides this public attorney database as a SERVICE ONLY.
We do NOT endorse, guarantee, or warrant any attorney's services.
You are responsible for verifying credentials and selecting counsel.
Inclusion in this database is NOT a recommendation or endorsement.
```

### Example 2: Immigration Law (No Location Specified)

**Query**: "Can you recommend an immigration lawyer?"

**Response**:
```
👨‍⚖️ **Attorney Referral Service**

**Case Type Detected:** Immigration (visas, deportation, asylum)

**No direct referrals found in database for your specific criteria.**

**💰 Free/Low-Cost Legal Help:**

**Legal Services Corporation**
   🌐 https://www.lsc.gov/what-legal-aid/find-legal-aid
   ℹ️ Find free legal aid in your area

[... credential verification checklist ...]
[... attorney submission info ...]
[... referral disclaimer ...]
```

---

## Roadmap

### Phase 1 (Current)
- ✅ Database structure implemented
- ✅ Intent pattern recognition
- ✅ Practice area matching
- ✅ Geographic filtering
- ✅ State bar association referrals
- ✅ Legal aid resources
- ✅ Credential verification checklist

### Phase 2 (Next)
- Populate database with real attorney submissions
- Create attorney submission form
- Expand to all 50 states
- Add city-specific matching
- Implement attorney profiles with bios

### Phase 3 (Future)
- Client review system
- Attorney ratings
- Specialty certifications
- Language capabilities
- Accessibility features (ASL, wheelchair access)
- Payment plan options

---

## Legal Disclaimers

### For Users

**NO ENDORSEMENT**: Mythara Gopher does NOT endorse, recommend, or guarantee any attorney listed in the database.

**USER RESPONSIBILITY**: You are solely responsible for:
- Verifying attorney credentials
- Evaluating attorney qualifications
- Making your own selection decision
- Any attorney-client relationship you enter

**NO LIABILITY**: Mythara is not liable for any attorney's services, fees, conduct, or outcomes.

**NOT LEGAL ADVICE**: The referral service provides information only, NOT legal advice.

### For Attorneys

**NO GUARANTEE**: Inclusion in the database does NOT guarantee referrals.

**ACCURATE INFORMATION**: You are responsible for providing accurate, up-to-date information.

**BAR COMPLIANCE**: You must maintain active bar license and good standing.

**NO FEES**: This is a free service. No referral fees or commissions are charged or paid.

**REMOVAL**: Mythara reserves the right to remove any attorney from the database at any time, with or without cause.

---

## Contact

**General Inquiries**: info@mythara.com  
**Attorney Submissions**: attorney_referrals@mythara.com  
**Technical Support**: support@mythara.com  
**Website**: https://mythara.com/attorney-referrals

---

## Changelog

**v1.0.0** (2025-01-XX)
- Initial release
- 10 practice areas
- 5 states covered (CA, NY, TX, FL, IL)
- State bar association referrals
- Legal aid resources
- Credential verification checklist
