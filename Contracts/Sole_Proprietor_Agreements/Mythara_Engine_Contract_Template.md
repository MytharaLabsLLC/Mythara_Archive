# Mythara Engine — Master Software Licensing Agreement

> **⚠ DRAFT TEMPLATE — NEVER EXECUTED — NOT LEGAL ADVICE**
>
> This is an **unsigned template only**. No licenses have been sold, no
> revenue earned, and no agreement on these terms has ever been signed.
> Pricing tiers, fees, SLAs, and all commercial terms below are template
> placeholders, not offered or agreed terms. **Do not sign or rely on this
> document without review by a licensed attorney.** Entity references use
> Mythara Labs LLC (proposed Colorado domestic LLC; Articles of Organization filing attempted
> with the Colorado Secretary of State on September 27, 2026 — not confirmed;
> not yet a formed entity); until formation completes, the
> licensor is Herbert Velez Jr., individual.

**Agreement ID:** ME-MSLA-TEMPLATE-001  
**Effective Date:** [INSERT DATE]  
**Licensor:** Herbert Velez Jr.  
**Licensee:** [COMPANY NAME]

---

## 1. Definitions

**1.1 "Software"** means the Mythara Engine inference orchestration system, including all source code, documentation, manifests, validation suites, and related materials as defined in the RELEASE_MANIFEST.json file (Manifest ID: ME-archive-0001).

**1.2 "License Tier"** means the specific license type selected by Licensee: Development, Enterprise, or Sovereign, as defined in Section 3.

**1.3 "Deployment Environment"** means the infrastructure (cloud, on-premises, or air-gapped) where Licensee operates the Software.

**1.4 "Escrow Agent"** means the third-party service provider holding source code and proprietary materials for conditional release per Section 8.

**1.5 "Manifest Reference"** means the cryptographically signed identifier (ME-archive-0001) used for version tracking and audit compliance.

---

## 2. Grant of License

**2.1 License Grant**

Subject to the terms of this Agreement and payment of applicable fees, Licensor grants Licensee a non-exclusive, non-transferable, revocable license to:

(a) Install and operate the Software in Licensee's Deployment Environment  
(b) Access documentation and validation suites included in the Software package  
(c) Use the Software for internal business purposes consistent with the selected License Tier

**2.2 Restrictions**

Licensee shall NOT:

(a) Distribute, sublicense, or transfer the Software to third parties  
(b) Reverse engineer, decompile, or disassemble the Software (except as permitted under Sovereign License with escrow release)  
(c) Remove or modify copyright notices, PGP signatures, or manifest references  
(d) Use the Software for purposes outside the scope of the selected License Tier  
(e) Exceed usage limits specified in Section 3 without upgrading to a higher License Tier

---

## 3. License Tiers and Pricing

### 3.1 Development License

**Use Case:** Internal testing, proof-of-concept, non-production environments

**Permitted Uses:**
- Development and staging environments only
- Up to 10,000 API requests per month
- Maximum 2 concurrent deployments

**Restrictions:**
- NO production deployment
- NO customer-facing applications
- NO revenue-generating use

**Pricing:** $2,500/year  
**Support:** Email support, 5 business day SLA

---

### 3.2 Enterprise License

**Use Case:** Production deployment for commercial applications

**Permitted Uses:**
- Production environments
- Up to 100,000 API requests per month
- Maximum 5 concurrent deployments
- Single business unit or subsidiary

**Restrictions:**
- NO multi-tenant SaaS resale
- NO white-label redistribution

**Pricing:** $25,000/year  
**Support:** Priority email support, 48-hour SLA, quarterly review calls

**Overage Fees:** $0.30 per 1,000 requests above 100K/month limit

---

### 3.3 Sovereign License

**Use Case:** Government, defense, air-gapped deployments, source code access

**Permitted Uses:**
- Unlimited API requests
- Unlimited concurrent deployments (within Licensee's organization)
- Air-gapped and classified environments
- Source code access via escrow release (Section 8)
- White-label integration rights (with attribution)

**Restrictions:**
- Geographic or entity-specific (defined in Exhibit A)
- Source code modifications require disclosure to Licensor

**Pricing:** $150,000/year (base) + $50,000 escrow setup fee (one-time)  
**Support:** 24-hour SLA, on-site integration assistance (up to 40 hours/year), dedicated Slack channel

---

## 4. Payment Terms

**4.1 Fees**

Licensee shall pay the annual license fee for the selected License Tier within 30 days of the Effective Date.

**4.2 Renewal**

This Agreement automatically renews annually unless either party provides 60 days' written notice of non-renewal. Renewal fees are subject to annual increases not exceeding 5%.

**4.3 Payment Methods**

Licensee may remit payment via:

- **Wire Transfer / ACH:** Bank details provided in invoice
- **Cash App:** $MytharaEngine
- **Cryptocurrency:** BTC / ETH / USDC (wallet addresses provided upon request)
- **Check:** Payable to "Herbert Velez Jr., Sole Proprietor"

Cryptocurrency payments are converted to USD at the exchange rate on the date of payment confirmation.

**4.4 Late Payment**

Late payments incur a 1.5% monthly interest charge. Licensor may suspend access to the Software if payment is more than 30 days overdue.

**4.5 Taxes**

All fees are exclusive of taxes. Licensee is responsible for all sales, use, VAT, and other applicable taxes.

---

## 5. Delivery and Verification

**5.1 Delivery**

Licensor shall deliver the Software package via:
- Private GitHub repository access, OR
- Secure encrypted file transfer

Delivery includes:
- Software binaries and/or container images
- PGP-signed manifests (RELEASE_MANIFEST.json, checksums.sha256)
- Documentation (README, INSTALL, API_SPEC_PUBLIC)
- Validation suite and test results

**5.2 Verification**

Licensee shall verify package integrity using:

```bash
gpg --import forensic_public_key.asc
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
cd manifest && sha256sum -c checksums.sha256
```

**PGP Fingerprint:** `571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C`

Licensee has 14 days from delivery to report verification failures.

---

## 6. Support and Maintenance

**6.1 Support Scope**

Licensor shall provide technical support consistent with the License Tier:
- Bug fixes and patches
- Security updates
- Documentation clarifications
- Integration assistance (Sovereign License only)

**6.2 Exclusions**

Support does NOT include:
- Custom feature development
- Third-party software issues
- Infrastructure configuration (except Sovereign License)
- Issues caused by Licensee modifications

**6.3 Support Channels**

Primary contact: mytharalabs@yahoo.com  
PGP-encrypted communications encouraged for sensitive issues.

---

## 7. Warranties and Disclaimers

**7.1 Limited Warranty**

Licensor warrants that:
(a) The Software will substantially conform to the documentation  
(b) Licensor has the right to license the Software  
(c) The Software does not infringe third-party intellectual property rights (to Licensor's knowledge)

**7.2 Warranty Period**

90 days from delivery date.

**7.3 Remedy**

Licensor's sole obligation for warranty breach is to correct defects or, if correction is not commercially reasonable, refund fees paid in the prior 12 months.

**7.4 DISCLAIMER**

EXCEPT AS EXPRESSLY STATED IN SECTION 7.1, THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

---

## 8. Escrow (Sovereign License Only)

**8.1 Escrow Deposit**

For Sovereign Licenses, Licensor shall deposit source code, proprietary algorithms, and build scripts with an approved Escrow Agent (Iron Mountain or a mutually agreed provider).

**8.2 Release Conditions**

Source code is released to Licensee upon:
(a) Licensor bankruptcy or cessation of business  
(b) Licensor failure to provide critical security patches for 90+ days  
(c) Licensor material breach of this Agreement (after 30-day cure period)

**8.3 Verification Rights**

Licensee may request annual escrow verification audits to confirm deposit completeness.

**8.4 Post-Release Rights**

Upon escrow release, Licensee may:
- Modify source code for internal use
- Maintain and patch the Software
- NOT redistribute or sublicense modified versions

---

## 9. Confidentiality

**9.1 Confidential Information**

Each party agrees to protect the other's Confidential Information using the same care applied to its own confidential materials (minimum: reasonable care).

Confidential Information includes:
- Software source code (if disclosed)
- Proprietary algorithms and architectures
- Pricing and financial terms
- Performance metrics and validation results

**9.2 Exclusions**

Confidential Information does NOT include information that:
(a) Is publicly available (other than through breach)  
(b) Licensee independently developed  
(c) Was rightfully received from a third party

**9.3 Term**

Confidentiality obligations survive termination for 5 years.

---

## 10. Intellectual Property

**10.1 Ownership**

Licensor retains all right, title, and interest in the Software, including all intellectual property rights. This Agreement grants only the limited license specified in Section 2.

**10.2 Feedback**

Licensee may provide suggestions, bug reports, or enhancement requests ("Feedback"). Licensor may use Feedback without obligation or compensation to Licensee.

**10.3 Licensee Data**

Licensee retains all rights to data processed by the Software. Licensor does NOT access or collect Licensee data.

---

## 11. Limitation of Liability

**11.1 Consequential Damages Waiver**

IN NO EVENT SHALL LICENSOR BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS, LOST DATA, OR BUSINESS INTERRUPTION, EVEN IF ADVISED OF THE POSSIBILITY.

**11.2 Liability Cap**

LICENSOR'S TOTAL LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED THE FEES PAID BY LICENSEE IN THE 12 MONTHS PRECEDING THE CLAIM.

**11.3 Exceptions**

Liability limits do NOT apply to:
- Licensee's breach of confidentiality (Section 9)
- Licensee's unauthorized distribution or sublicensing
- Gross negligence or willful misconduct

---

## 12. Term and Termination

**12.1 Term**

This Agreement begins on the Effective Date and continues for one year, with automatic annual renewal (Section 4.2).

**12.2 Termination for Cause**

Either party may terminate if the other party:
(a) Materially breaches this Agreement and fails to cure within 30 days of written notice  
(b) Becomes insolvent or subject to bankruptcy proceedings

**12.3 Termination for Convenience**

Licensee may terminate with 60 days' written notice. No refund of prepaid fees.

**12.4 Effect of Termination**

Upon termination:
(a) Licensee shall cease using the Software and delete all copies  
(b) Unpaid fees become immediately due  
(c) Sections 7 (Disclaimers), 9 (Confidentiality), 10 (IP), 11 (Liability), and 13 (General) survive

**12.5 Escrow Survival**

For Sovereign Licenses, escrow deposit remains accessible per Section 8.2 release conditions.

---

## 13. General Provisions

**13.1 Governing Law**

This Agreement is governed by the laws of the State of Colorado, USA, without regard to conflict of law principles. *(Template placeholder — confirm governing law with counsel at execution.)*

**13.2 Dispute Resolution**

Disputes shall be resolved through:
1. Good faith negotiation (30 days)
2. Mediation (JAMS or AAA rules)
3. Binding arbitration (if mediation fails)

**13.3 Assignment**

Licensee may NOT assign this Agreement without Licensor's written consent. Licensor may assign to an affiliate or successor.

**13.4 Force Majeure**

Neither party is liable for delays caused by circumstances beyond reasonable control (natural disasters, war, pandemics, government actions).

**13.5 Entire Agreement**

This Agreement, including referenced exhibits, constitutes the entire agreement and supersedes all prior negotiations.

**13.6 Amendments**

Amendments require written agreement signed by both parties.

**13.7 Severability**

If any provision is unenforceable, the remainder of the Agreement continues in effect.

**13.8 Notices**

Notices must be in writing to:

**Licensor:**  
Herbert Velez Jr., Sole Proprietor  
Email: mytharalabs@yahoo.com  
PGP: 571F FB4C CCFA DCF A44A  63F6 D968 C2D5 DBE2 486C

**Licensee:**  
[INSERT COMPANY ADDRESS]  
[INSERT EMAIL]

---

## Signature Block

**LICENSOR:**

Herbert Velez Jr., Sole Proprietor

Signature: ___________________________  
Date: ___________________________

---

**LICENSEE:**

[COMPANY NAME]

Authorized Representative: ___________________________  
Title: ___________________________  
Signature: ___________________________  
Date: ___________________________

---

## Exhibit A: Deployment Scope (Sovereign License Only)

**Geographic Restrictions:** [INSERT: e.g., "United States only" or "EU member states"]

**Permitted Entities:** [INSERT: e.g., "Licensee and wholly-owned subsidiaries" or "US Department of Defense and contractors"]

**Deployment Environments:** [INSERT: e.g., "SIPRNet, NIPRNet, on-premises data centers"]

**Source Code Access:** ☐ Full source ☐ Partial (specify: _____________)

**Modification Rights:** ☐ Permitted with disclosure ☐ Prohibited

---

**END OF AGREEMENT**

---

*This template is for reference purposes. Consult legal counsel before execution. Not a substitute for professional legal advice.*
