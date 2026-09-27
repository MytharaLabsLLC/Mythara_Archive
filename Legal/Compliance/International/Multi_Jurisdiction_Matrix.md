# Multi-Jurisdiction Regulatory Compliance Matrix

**Copyright © 2025 Herbert Velez Jr. All rights reserved. Proprietary and Confidential.**

**Product:** Mythara Engine (pre-release, unaudited)
**Version:** 1.0
**Last Updated:** November 2, 2025
**Scope:** Mapping of global accessibility, privacy, and AI/ML regulations the project should plan for

---

## Standing Disclaimer

> **No entry in this matrix is a certification, assessment, or audit.**
> Every row names a law or framework the project has *mapped* — i.e., read
> about and noted as relevant. No third-party audit (SOC 2, ISO 27001,
> HIPAA, GDPR, FedRAMP, CMMC, or any other) has been completed, sought, or
> passed. No regulator has reviewed Mythara. No legal counsel has validated
> any row. Where an earlier draft of this document used ✅ marks, they
> claimed achievements that do not exist and have been removed.

**Legend:**
- 🗺️ = Mapped — the law is understood to be relevant; nothing has been done about it
- ⚠️ = Conditional or evolving — applicability depends on use case, market, or pending regulation
- ❌ = Not assessed

---

## Quick Reference Matrix

| **Jurisdiction** | **Accessibility** | **Privacy** | **AI/ML** | **Healthcare** | **Education** | **Overall** |
|------------------|-------------------|-------------|-----------|----------------|---------------|-------------|
| **United States** | 🗺️ ADA, 508, CVAA | 🗺️ HIPAA, COPPA | 🗺️ Voluntary frameworks | ⚠️ FDA (if medical claims) | 🗺️ FERPA, IDEA | 🗺️ MAPPED — not assessed |
| **European Union** | 🗺️ EAA, WAD, EN 301 549 | 🗺️ GDPR | 🗺️ AI Act | ⚠️ MDR (if medical claims) | 🗺️ GDPR-ED | 🗺️ MAPPED — not assessed |
| **United Kingdom** | 🗺️ Equality Act | 🗺️ UK GDPR, DPA | 🗺️ Voluntary | ⚠️ MHRA (if medical claims) | 🗺️ DPA 2018 | 🗺️ MAPPED — not assessed |
| **Canada** | 🗺️ ACA, AODA | 🗺️ PIPEDA | ⚠️ AIDA (pending) | ⚠️ Health Canada (if medical claims) | 🗺️ PIPEDA | 🗺️ MAPPED — not assessed |
| **Australia** | 🗺️ DDA | 🗺️ Privacy Act | 🗺️ Voluntary | ⚠️ TGA (if medical claims) | 🗺️ Privacy Act | 🗺️ MAPPED — not assessed |
| **Japan** | 🗺️ JIS X 8341-3 | 🗺️ APPI | 🗺️ Voluntary | ⚠️ PMDA (if medical claims) | 🗺️ APPI | 🗺️ MAPPED — not assessed |
| **China** | 🗺️ GB/T standards | 🗺️ PIPL | 🗺️ Algorithm regulations | ⚠️ NMPA (if medical claims) | 🗺️ PIPL | ⚠️ PARTIAL* |
| **India** | 🗺️ RPWD Act | ⚠️ DPDP Act (rules pending) | 🗺️ Voluntary | ⚠️ CDSCO (if medical claims) | ⚠️ DPDP Act | ⚠️ EVOLVING |
| **Singapore** | 🗺️ ENGA guidelines | 🗺️ PDPA | 🗺️ Model AI Gov (voluntary) | ⚠️ HSA (if medical claims) | 🗺️ PDPA | 🗺️ MAPPED — not assessed |
| **South Korea** | 🗺️ KCAG | 🗺️ PIPA | 🗺️ Voluntary | ⚠️ MFDS (if medical claims) | 🗺️ PIPA | 🗺️ MAPPED — not assessed |

- \* = China market would require a local entity, data localization, and government approvals. No plans exist.

---

## Detailed Jurisdiction Notes

### 🇺🇸 United States

| **Law/Standard** | **Relevance** | **Status** |
|------------------|---------------|------------|
| ADA Title III | Web access as public accommodation | 🗺️ Mapped — no assessment |
| Section 508 (Revised 2017) | Federal procurement accessibility | 🗺️ Mapped — no VPAT evaluation performed |
| CVAA | Advanced communications accessibility | 🗺️ Mapped — no assessment |
| HIPAA | Only if handling protected health information | ⚠️ Conditional — no handling today |
| COPPA | Only if serving users under 13 | ⚠️ Conditional |
| CCPA/CPRA (CA) | Consumer privacy rights | 🗺️ Mapped — no assessment |
| SHIELD Act (NY) | Cybersecurity safeguards | 🗺️ Mapped — no assessment |
| FERPA / IDEA | Only in education contexts | ⚠️ Conditional |
| NIST AI Risk Management | Voluntary | 🗺️ Mapped |
| FDA 21 CFR 820 / SaMD guidance | Only if marketed as a medical device | ⚠️ Not a medical device today; no filings, no 510(k), no design controls in place |

### 🇪🇺 European Union

| **Directive/Standard** | **Relevance** | **Status** |
|------------------------|---------------|------------|
| European Accessibility Act (2019/882) | Product/service accessibility | 🗺️ Mapped — no assessment |
| Web Accessibility Directive (2016/2102) | Public-sector web accessibility | 🗺️ Mapped — no assessment |
| EN 301 549 | ICT accessibility standard | 🗺️ Mapped — no conformance report |
| GDPR | Lawful basis, data-subject rights, DPIA | 🗺️ Mapped — no DPIA conducted, no assessment |
| ePrivacy Directive | Cookies, electronic communications | 🗺️ Mapped — no implementation |
| EU AI Act | Risk classification, transparency | 🗺️ Mapped — no formal classification; note that emotion recognition for vulnerable groups can be high-risk, which is why the design attests to self-reported records and never infers emotions |
| MDR (2017/745) | Only if medical claims made | ⚠️ No medical claims today; no CE marking, no technical file, no clinical evaluation |

### 🇬🇧 United Kingdom

| **Law** | **Relevance** | **Status** |
|---------|---------------|------------|
| Equality Act 2010 | Reasonable adjustments | 🗺️ Mapped — no assessment |
| UK GDPR + Data Protection Act 2018 | Data protection | 🗺️ Mapped — no ICO registration, no assessment |
| MHRA regulations | Only if a medical device | ⚠️ Not applicable today; no UKCA marking |

### 🇨🇦 Canada

| **Law** | **Relevance** | **Status** |
|---------|---------------|------------|
| Accessible Canada Act | Accessibility planning | 🗺️ Mapped — no plan filed |
| AODA (Ontario) | Provincial accessibility | 🗺️ Mapped — no assessment |
| PIPEDA | Consent, breach notification | 🗺️ Mapped — no privacy assessment |
| AIDA (pending) | AI regulation | ⚠️ Monitoring; not enacted |

### 🇦🇺 Australia

| **Law** | **Relevance** | **Status** |
|---------|---------------|------------|
| Disability Discrimination Act 1992 | Web accessibility | 🗺️ Mapped — no assessment |
| Privacy Act 1988 | Privacy principles, breach notification | 🗺️ Mapped — no assessment |

### 🇯🇵 Japan

| **Law/Standard** | **Relevance** | **Status** |
|------------------|---------------|------------|
| JIS X 8341-3 | Web accessibility | 🗺️ Mapped — no assessment |
| APPI | Data protection, cross-border transfers | 🗺️ Mapped — no assessment |

### 🇨🇳 China

| **Law** | **Relevance** | **Status** |
|---------|---------------|------------|
| PIPL | Consent, data localization | ⚠️ Would require local deployment — no plans |
| Cybersecurity Law / Data Security Law | Data classification, critical infrastructure | ⚠️ No assessment |
| Algorithm Recommendation / Deep Synthesis regulations | Registration, content labeling | ⚠️ Conditional on operating in China |

### 🇮🇳 India

| **Law** | **Relevance** | **Status** |
|---------|---------------|------------|
| RPWD Act 2016 | Web accessibility | 🗺️ Mapped — no assessment |
| DPDP Act 2023 | Data protection | ⚠️ Rules still pending; monitoring |

### 🇸🇬 Singapore

| **Law/Guideline** | **Relevance** | **Status** |
|-------------------|---------------|------------|
| PDPA | Consent, breach notification | 🗺️ Mapped — no assessment |
| Model AI Governance Framework | Voluntary best practices | 🗺️ Mapped |

### 🇰🇷 South Korea

| **Law/Standard** | **Relevance** | **Status** |
|------------------|---------------|------------|
| KCAG | Web accessibility | 🗺️ Mapped — no assessment |
| PIPA | Consent, data protection | 🗺️ Mapped — no assessment |

---

## Industry-Specific Notes

### 🏥 Healthcare / Medical Devices

Mythara is not a medical device and makes no medical claims. If a future deployment ever made diagnostic or treatment claims, the following would apply and would require regulatory counsel and approvals *before* launch: FDA 510(k) or De Novo (US), CE marking under MDR (EU), UKCA (UK), MDEL (Canada), TGA registration (Australia), PMDA (Japan). **None of this exists today**: no filings, no technical files, no clinical evaluations, no "510(k)-ready" anything. The earlier draft's ✅ marks in this section were removed as fabricated.

### 🎓 Education

FERPA, COPPA, IDEA (US); GDPR child-consent provisions (EU); age-appropriate design (UK). 🗺️ Mapped — no assessment; parental consent flows would need to be built and reviewed by counsel before serving minors.

### 🏛️ Government / Public Sector

Section 508 (US), EN 301 549 (EU). 🗺️ Mapped — no VPAT evaluation performed, no FISMA authorization, no FedRAMP certification. The earlier draft's claims of FISMA controls and FedRAMP positioning were removed.

---

## Compliance Maintenance Schedule *(proposed, not active)*

| **Activity** | **Frequency** | **Status** |
|-------------|--------------|------------|
| Accessibility evaluation | Annual once a product ships | Not started — no product shipped |
| VPAT | Per major release | Blank template on file; nothing evaluated |
| Privacy review | Annual or when laws change | Not started |
| Penetration testing | Annual | Not performed |
| Regulatory monitoring | Continuous | By project owner |

---

## Honest Risk Assessment

| **Jurisdiction** | **Risk Level** | **Primary Concern** | **Honest Mitigation** |
|------------------|---------------|---------------------|----------------------|
| United States | 🟡 MEDIUM | ADA litigation risk *if* a public product ships without accessibility work | Do the accessibility work before shipping; get counsel |
| European Union | 🟡 MEDIUM | GDPR fines *if* personal data is mishandled | Design privacy in from the start; conduct a DPIA before launch |
| China | 🔴 HIGH | Data localization, algorithm registration | Do not operate in China without a local partner and counsel |
| India | 🟡 MEDIUM | Evolving DPDP rules | Monitor; design adaptably |
| Global | 🟡 MEDIUM | AI regulation evolving everywhere | Transparency, human oversight, honest documentation — and no emotion-inference claims |

The earlier draft rated most jurisdictions 🟢 LOW on the basis of compliance that did not exist. That was dishonest and has been corrected.

---

## Obligations of Anyone Building on Mythara

**The project provides:** this mapping, design intent documents, and an honest record of what has *not* been done.

**Anyone deploying or licensing Mythara must:**
- Conduct jurisdiction-specific legal review with licensed counsel
- Implement compliance measures in their own deployment
- Register with data protection authorities where required
- Obtain medical-device approvals *before* making any medical claim
- Never represent this matrix as evidence of compliance

**The project does NOT provide:** legal advice, compliance guarantees, liability coverage, or any certification.

---

## Document Updates

| **Version** | **Date** | **Changes** | **Author** |
|------------|---------|-------------|-----------|
| 1.0 | Nov 2, 2025 | Initial multi-jurisdiction matrix | Herbert Velez Jr. |
| 1.1 | Sep 27, 2026 | Voice-standard pass: removed fabricated conformance claims; re-mapped all entries as unassessed | Cal (voice-standard pass) |

---

**Mythara Project** (Mythara Labs LLC: formation filing attempted Sept 27, 2026 — not confirmed; entity not yet formed)
