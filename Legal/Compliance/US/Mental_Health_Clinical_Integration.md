# 🧠 Mental Health & Clinical Psychology Integration

**Copyright © 2025 Herbert Velez Jr. All rights reserved..**

**Version:** 1.0.0  
**Last Updated:** November 2, 2025  
**DSM Edition:** DSM-5-TR (Text Revision, March 2022)  
**Clinical Standards:** APA, WHO ICD-11, NICE, SAMHSA

> **⚠ DESIGN REFERENCE — NOT A CLINICAL CLAIM**
>
> This document is a **design reference**: it summarizes public clinical
> frameworks (DSM-5-TR, ICD-11, CBT, DBT, ACT) so future design work can be
> informed by them. It is not medical advice, not a clinical guideline, and
> not evidence that any feature described here has been built, tested,
> clinically validated, or reviewed by a licensed professional. Nothing in
> it has been. Every "Mythara Application" note below is a **design
> consideration**, not a shipped feature.

---

## 📋 Overview

The Mythara Engine integrates evidence-based mental health assessment and intervention frameworks aligned with current diagnostic standards, clinical practice guidelines, and regulatory requirements for mental healthcare technology.

---

## 📖 DSM-5-TR Integration

### Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision

**Publication:** American Psychiatric Association, March 2022  
**Purpose:** Standardized classification and diagnostic criteria for mental disorders  
**Integration Level:** Reference framework for mental health applications

### Key DSM-5-TR Categories (Reference Only — Not a Clinical Capability)

#### 1. Neurodevelopmental Disorders
- **ICD-10-CM Codes:** F80-F89
- **Examples:** 
  - Autism Spectrum Disorder (299.00)
  - ADHD (314.00, 314.01)
  - Specific Learning Disorders (315.00, 315.1, 315.2)
  - Intellectual Disabilities (F70-F79)

**Design consideration (not implemented):**
- Adaptive communication modes for neurodivergent users
- Simplified language options (CEFR A2-B1)
- Reduced motion/distraction modes
- Predictable navigation patterns
- Extended timeout configurations

#### 2. Schizophrenia Spectrum and Other Psychotic Disorders
- **ICD-10-CM Codes:** F20-F29
- **Examples:**
  - Schizophrenia (295.90)
  - Schizoaffective Disorder (295.70)
  - Brief Psychotic Disorder (298.8)

**Design consideration (not implemented):**
- Reality-grounding clause selection (Legacy Seed clauses)
- Crisis detection protocols
- Clear distinction between system outputs and user-generated content
- No hallucinogenic or reality-distorting content
- Sanctification locks prevent harmful outputs

#### 3. Bipolar and Related Disorders
- **ICD-10-CM Codes:** F31
- **Examples:**
  - Bipolar I Disorder (296.40-296.89)
  - Bipolar II Disorder (296.89)
  - Cyclothymic Disorder (301.13)

**Design consideration (not implemented):**
- Mood tracking integration capabilities
- Sleep/circadian rhythm consideration in time-sensitive features
- Energy-level adaptive interfaces

#### 4. Depressive Disorders
- **ICD-10-CM Codes:** F32-F34
- **Examples:**
  - Major Depressive Disorder (296.20-296.36)
  - Persistent Depressive Disorder/Dysthymia (300.4)
  - Premenstrual Dysphoric Disorder (625.4)

**Design consideration (not implemented):**
- Compassionate language selection (Blessing Arc clauses)
- Hope-oriented messaging
- Crisis resource integration (988 Suicide & Crisis Lifeline)
- Low-energy interaction modes (minimal clicks required)

#### 5. Anxiety Disorders
- **ICD-10-CM Codes:** F40-F41
- **Examples:**
  - Generalized Anxiety Disorder (300.02)
  - Panic Disorder (300.01)
  - Social Anxiety Disorder (300.23)
  - Specific Phobias (300.29)

**Design consideration (not implemented):**
- Reduced motion options
- Calming color palettes available
- No sudden changes or pop-ups without warning
- Clear escape mechanisms (no keyboard traps)
- Grounding techniques in error messaging

#### 6. Obsessive-Compulsive and Related Disorders
- **ICD-10-CM Codes:** F42
- **Examples:**
  - Obsessive-Compulsive Disorder (300.3)
  - Body Dysmorphic Disorder (300.7)
  - Hoarding Disorder (300.3)

**Design consideration (not implemented):**
- Confirmation dialogs to reduce compulsive checking
- Clear, unambiguous status indicators
- Save state persistence (reduces need to recheck)
- No triggering imagery related to contamination/harm

#### 7. Trauma- and Stressor-Related Disorders
- **ICD-10-CM Codes:** F43
- **Examples:**
  - Posttraumatic Stress Disorder (309.81)
  - Acute Stress Disorder (308.3)
  - Adjustment Disorders (309.0-309.9)

**Design consideration (not implemented):**
- Trauma-informed design principles
- No sudden loud noises or flashing
- User control over all sensory inputs
- Memory-safe clause selection (no re-traumatization)
- False memory detection systems

#### 8. Dissociative Disorders
- **ICD-10-CM Codes:** F44
- **Examples:**
  - Dissociative Identity Disorder (300.14)
  - Dissociative Amnesia (300.12)
  - Depersonalization/Derealization Disorder (300.6)

**Design consideration (not implemented):**
- Grounding features (timestamps, location indicators)
- Session continuity markers
- Reality-anchoring UI elements
- Identity-consistent personalization

#### 9. Somatic Symptom and Related Disorders
- **ICD-10-CM Codes:** F45
- **Examples:**
  - Somatic Symptom Disorder (300.82)
  - Illness Anxiety Disorder (300.7)
  - Conversion Disorder (300.11)

**Design consideration (not implemented):**
- No medical diagnostic claims
- Clear disclaimers about non-medical nature
- Appropriate healthcare resource referrals
- No body-scanning or symptom-amplifying features

#### 10. Feeding and Eating Disorders
- **ICD-10-CM Codes:** F50
- **Examples:**
  - Anorexia Nervosa (307.1)
  - Bulimia Nervosa (307.51)
  - Binge-Eating Disorder (307.51)

**Design consideration (not implemented):**
- No weight/calorie tracking features
- No body image content without clinical context
- NEDA (National Eating Disorders Association) resource integration
- Supportive, non-judgmental language

#### 11. Sleep-Wake Disorders
- **ICD-10-CM Codes:** F51, G47
- **Examples:**
  - Insomnia Disorder (780.52)
  - Narcolepsy (347.00)
  - Circadian Rhythm Sleep-Wake Disorders (307.45)

**Design consideration (not implemented):**
- Night mode/dark theme
- Reduced blue light options
- Time zone awareness
- Quiet hours/do not disturb settings

#### 12. Substance-Related and Addictive Disorders
- **ICD-10-CM Codes:** F10-F19
- **Examples:**
  - Alcohol Use Disorder (303.90)
  - Opioid Use Disorder (304.00)
  - Gambling Disorder (312.31)

**Design consideration (not implemented):**
- No addictive design patterns (no infinite scroll, no variable rewards)
- Clear usage metrics (time spent tracking)
- Break reminders
- SAMHSA treatment locator integration
- No gambling mechanics

#### 13. Neurocognitive Disorders
- **ICD-10-CM Codes:** F01-F03, F06.1, G30-G31
- **Examples:**
  - Alzheimer's Disease (331.0)
  - Vascular Dementia (290.40)
  - Traumatic Brain Injury (294.11)

**Design consideration (not implemented):**
- Memory aids (session history, bookmarks)
- Simplified navigation modes
- Larger touch targets (44x44px minimum)
- Caregiver access options
- Consistent UI patterns

#### 14. Personality Disorders
- **ICD-10-CM Codes:** F60
- **Examples:**
  - Borderline Personality Disorder (301.83)
  - Antisocial Personality Disorder (301.7)
  - Avoidant Personality Disorder (301.82)

**Design consideration (not implemented):**
- DBT (Dialectical Behavior Therapy) aligned features
- Emotion regulation support (pause/breathe prompts)
- Crisis tolerance features
- Interpersonal effectiveness tools (communication templates)

---

## 🏥 ICD-11 Integration (WHO Classification)

**International Classification of Diseases, 11th Revision (2022)**  
**Effective:** January 1, 2022  
**Mental, Behavioural, and Neurodevelopmental Disorders:** Chapter 6

### ICD-11 to DSM-5-TR Crosswalk

| **DSM-5-TR Category** | **ICD-11 Code Range** | **Integration** |
|----------------------|---------------------|----------------|
| Schizophrenia Spectrum | 6A20-6A2Z | Crisis detection (design goal — not built) |
| Mood Disorders | 6A60-6A8Z | Record-keeping care (design goal — not built) |
| Anxiety/Fear Disorders | 6B00-6B0Z | Calming UI modes (design goal — not built) |
| OCD & Related | 6B20-6B2Z | Confirmation dialogs (design goal — not built) |
| Stress-Related | 6B40-6B4Z | Trauma-informed design (design goal — not built) |
| Dissociative | 6B60-6B6Z | Grounding features (design goal — not built) |
| Feeding/Eating | 6B80-6B8Z | No triggering content (design goal — not built) |
| Personality Disorders | 6D10-6D1Z | DBT-informed design goals — not built |
| Substance Use | 6C40-6C5Z | No addictive patterns (design goal — not built) |
| Neurocognitive | 6D70-6E0Z | Memory aids (design goal — not built) |

---

## 🧪 Evidence-Based Therapeutic Frameworks

### 1. Cognitive Behavioral Therapy (CBT)
**Integration:**
- Thought record templates
- Cognitive restructuring prompts
- Behavioral activation scheduling
- Exposure hierarchy support (anxiety disorders)

**Clause Types:**
- Legacy Seed: Grounding in reality, challenging distortions
- Blessing Arc: Positive reinforcement, strengths-based
- Memory Lock: Preventing rumination loops

### 2. Dialectical Behavior Therapy (DBT)
**Four Modules:**
1. **Mindfulness:** Present-moment awareness prompts
2. **Distress Tolerance:** Crisis survival strategies
3. **Emotion Regulation:** Mood tracking integration
4. **Interpersonal Effectiveness:** Communication templates

**Design considerations (not implemented):**
- STOP skill integration (Stop, Take a step back, Observe, Proceed mindfully)
- TIPP skill support (Temperature, Intense exercise, Paced breathing, Paired muscle relaxation)
- Wise Mind decision-making prompts

### 3. Acceptance and Commitment Therapy (ACT)
**Six Core Processes:**
- Acceptance: Non-judgmental messaging
- Cognitive Defusion: Separating thoughts from identity
- Being Present: Mindfulness prompts
- Self as Context: Perspective-taking features
- Values: Values clarification exercises
- Committed Action: Goal setting and tracking

### 4. Trauma-Focused CBT (TF-CBT)
**Components:**
- Psychoeducation: Trauma education resources
- Parenting skills: Caregiver guidance (for child trauma)
- Relaxation: Calming techniques
- Affective regulation: Emotion management
- Cognitive coping: Trauma narrative support
- Trauma narrative: Safe memory processing
- In vivo exposure: Gradual exposure planning
- Conjoint sessions: Family integration support

**Safety Features:**
- No forced re-experiencing
- User-controlled pacing
- Grounding techniques always accessible
- Emergency resources prominent

### 5. Motivational Interviewing (MI)
**OARS Principles:**
- **O**pen-ended questions: Clause design encourages exploration
- **A**ffirmations: Blessing Arc positive reinforcement
- **R**eflective listening: Echo user concerns
- **S**ummarizing: Session summaries available

**Stages of Change:**
- Precontemplation: Educational resources
- Contemplation: Pros/cons exploration
- Preparation: Action planning tools
- Action: Progress tracking
- Maintenance: Relapse prevention strategies

---

## 📊 Clinical Assessment Tools Integration

### Screening Instruments (Reference, Not Diagnostic)

**Depression:**
- PHQ-9 (Patient Health Questionnaire-9): 9-item depression screener
- BDI-II (Beck Depression Inventory): 21-item self-report
- HAM-D (Hamilton Depression Rating Scale): Clinician-rated

**Anxiety:**
- GAD-7 (Generalized Anxiety Disorder-7): 7-item anxiety screener
- BAI (Beck Anxiety Inventory): 21-item self-report
- LSAS (Liebowitz Social Anxiety Scale): Social anxiety specific

**PTSD:**
- PCL-5 (PTSD Checklist for DSM-5): 20-item self-report
- CAPS-5 (Clinician-Administered PTSD Scale): Gold standard interview

**Bipolar:**
- MDQ (Mood Disorder Questionnaire): Bipolar screening
- YMRS (Young Mania Rating Scale): Mania severity

**OCD:**
- Y-BOCS (Yale-Brown Obsessive Compulsive Scale): Severity measure

**ADHD:**
- ASRS (Adult ADHD Self-Report Scale): 18-item screener
- Conners' Rating Scales: Child/adolescent ADHD

**General Mental Health:**
- WHODAS 2.0 (WHO Disability Assessment Schedule): Functional impairment
- BASIS-24 (Behavior and Symptom Identification Scale): Overall distress

**Suicide Risk:**
- C-SSRS (Columbia-Suicide Severity Rating Scale): Suicidal ideation/behavior
- SBQ-R (Suicidal Behaviors Questionnaire-Revised): Brief screener

### **CRITICAL DISCLAIMER**

⚠️ **Mythara Engine does NOT:**
- Diagnose mental health conditions
- Replace professional clinical assessment
- Provide medical or psychiatric treatment
- Offer crisis intervention services

ℹ️ **Design intent (not built):**
- Reference clinical frameworks for design decisions (this document does that)
- Draw on evidence-based therapeutic principles as design inspiration
- One day support, never replace, mental health professionals' work
- Surface public crisis resources (988, NEDA, SAMHSA) where appropriate

**All screening tools are for REFERENCE ONLY. Clinical diagnosis requires licensed mental health professional.**

---

## 🚨 Crisis Management & Safety Protocols

### Crisis Resource Integration

**United States:**
- **988 Suicide & Crisis Lifeline:** Call/text 988 (24/7)
- **Crisis Text Line:** Text HOME to 741741
- **SAMHSA National Helpline:** 1-800-662-4357 (substance abuse)
- **NEDA Helpline:** 1-800-931-2237 (eating disorders)
- **Veterans Crisis Line:** 988 then press 1
- **Trevor Project:** 1-866-488-7386 (LGBTQ+ youth)

**International:**
- **Canada:** 988 or 1-833-456-4566
- **UK:** 116 123 (Samaritans)
- **Australia:** 13 11 14 (Lifeline)
- **EU:** 116 123 (most countries)

### Safety Features

**1. Crisis Detection (intended — not built)**
- Content safeguards that refuse harmful outputs
- Suppression of high-risk outputs
- Escalation paths for crisis signals
- Presentation of public crisis resources

**2. Harm Prevention**
- No self-harm or suicide method information
- No pro-eating disorder content
- No substance abuse glorification
- No violent or harmful instructions

**3. Professional Boundary Maintenance**
- Clear "Not a Therapist" disclaimers
- Licensed professional referral prompts
- No prescription or medication advice
- No diagnosis or treatment recommendations

**4. Ethical Guardrails**
- No PHI handled today; any future health-data handling would require HIPAA-minded design and licensed counsel — no compliance achieved
- Informed consent for data collection
- Right to human review/override
- Transparency about AI limitations

---

## 🏛️ Mental Health Regulatory Compliance

### United States

#### 1. Mental Health Parity and Addiction Equity Act (MHPAEA)
**Requirement:** Equal coverage for mental health and medical/surgical benefits  
**Compliance:** Technology must not create disparities in access  
**Design target (not built):** accessible design so technology does not create disparities in access — no accessibility evaluation performed

#### 2. HIPAA Privacy Rule (Mental Health Records)
**Requirement:** Enhanced protections for psychotherapy notes  
**Compliance:** Stricter access controls than general medical records  
**If ever built:** therapy content would need separate storage and additional encryption (nothing built today)

**Psychotherapy Notes Exclusions:**
- Medication management
- Session times and modalities
- Results of clinical tests
- Diagnoses, prognoses, treatment plans (these are regular PHI)

**If therapy-note handling were ever built, it would need:**
- Segregated storage
- Additional access controls
- Separate consent for psychotherapy notes

#### 3. 42 CFR Part 2 (Substance Use Disorder Records)
**Requirement:** Stricter than HIPAA for SUD treatment  
**Compliance:** Cannot disclose SUD info without specific written consent  
**If SUD features were ever built:** they would need a separate consent flow and locked disclosures (none built today)

#### 4. Americans with Disabilities Act (ADA) - Mental Illness
**Requirement:** Mental illness is a covered disability  
**Compliance:** Reasonable accommodations required  
**Design targets (not built):**
- Neurodivergent-friendly interfaces
- Cognitive accessibility features
- No discrimination in service delivery

#### 5. FDA Regulation of Mental Health Apps
**Categories:**
- **Class I (Low Risk):** General wellness, not medical device
- **Class II (Moderate Risk):** Clinical decision support, diagnostic aids
- **Class III (High Risk):** Treatment/prevention of disease

**Regulatory posture (planning view only — no determination made, counsel required):**
- Mythara makes no medical claims today and is not a medical device
- If it were ever marketed for clinical decision support, FDA 510(k) clearance would be required first
- It does not diagnose or treat, and must never be presented as doing so

#### 6. FTC Health Breach Notification Rule
**Requirement:** Notify consumers and FTC of health data breaches  
**Scope:** Apps/websites not covered by HIPAA  
**Not built:** breach-notification procedures would need to be created before any health-data handling — none exist today

#### 7. State Mental Health Laws
**Mandatory Reporting (Clinician Duty):**
- Child abuse/neglect
- Elder abuse
- Imminent danger to self/others

**Standing position:**
- Mythara is not a clinician and not a mandated reporter
- Any product would surface public crisis resources (none wired into a product today)
- Users remain responsible for seeking professional help

---

### European Union

#### 1. GDPR Special Category Data (Article 9)
**Mental Health Data = Sensitive Personal Data**  
**Requirements:**
- Explicit consent required
- Data Protection Impact Assessment (DPIA) mandatory
- Enhanced security measures
- Limited processing purposes

**Design targets (not built — no DPIA conducted, no assessment):**
- Explicit opt-in for any mental-health-related features
- Data Protection Impact Assessment before launch
- Encryption at rest and in transit
- Minimal retention with user-controlled deletion

#### 2. Medical Device Regulation (MDR) - Mental Health Apps
**Classification:**
- **Class I:** Wellness, no medical purpose
- **Class IIa:** Diagnosis/monitoring of mental health conditions
- **Class IIb/III:** Treatment of severe mental illness

**Planning view only (no determination):** no medical claims are made today; any diagnostic or treatment claim would require MDR conformity and counsel first

#### 3. AI Act - Mental Health Applications
**Risk Category:** 
- **Limited Risk:** General mental wellness support
- **High Risk:** Mental health diagnosis, treatment decisions, emotion recognition for vulnerable groups

**Planning view only (no formal classification):** the design avoids emotion inference — it attests to self-reported records and never infers emotions — which keeps clear of the high-risk emotion-recognition category

---

### United Kingdom

#### 1. Mental Health Act 1983 (amended 2007)
**Scope:** Involuntary treatment, sectioning  
**Mythara:** Not applicable (voluntary use, not treatment facility)

#### 2. Mental Capacity Act 2005
**Principles:** Presumption of capacity, best interests  
**Design targets (not built):**
- Clear consent flows
- Accessible to those with fluctuating capacity
- Caregiver/advocate access options

#### 3. Care Quality Commission (CQC) - Digital Mental Health
**Standards:** Safe, effective, caring, responsive, well-led  
**Reference only:** CQC quality domains noted as a design reference — no assessment

#### 4. NICE Guidelines (National Institute for Health and Care Excellence)
**Evidence-Based Standards:**
- Depression (CG90, NG222)
- Anxiety (CG113)
- PTSD (NG116)
- OCD (CG31)
- Bipolar (CG185)
- Psychosis/Schizophrenia (CG178)

**Reference only:** NICE guidelines kept as a design reference — no clinical endorsement implied

---

### Canada

#### 1. Mental Health Commission of Canada (MHCC)
**Standards:** Recovery-oriented, person-centered, trauma-informed  
**Reference only:** MHCC principles noted — no assessment

#### 2. Provincial Mental Health Acts
**Varies by Province:** BC Mental Health Act, Ontario Mental Health Act, etc.  
**Note:** any deployment would need province-by-province legal review

---

### Australia

#### 1. National Mental Health Strategy
**Framework:** Prevention, early intervention, treatment, recovery  
**Standing position:** Mythara is not treatment and plays no clinical role

#### 2. National Standards for Mental Health Services
**Standards:** Rights, safety, consumer participation, carers, governance  
**Reference only:** national standards noted — no assessment

---

## 📚 Clinical Practice Guidelines Integration

### American Psychological Association (APA) Guidelines

**Evidence-Based Practice in Psychology:**
1. Best research evidence
2. Clinical expertise
3. Patient values and preferences

**Design posture:**
- Informed by published CBT, DBT, and ACT frameworks
- No clinical consultation has occurred
- User preference customization is a design target, not a feature

### SAMHSA (Substance Abuse and Mental Health Services Administration)

**Eight Dimensions of Wellness:**
1. Emotional
2. Environmental
3. Financial
4. Intellectual
5. Occupational
6. Physical
7. Social
8. Spiritual

**Aspiration:** a holistic approach across all dimensions — not built

**Trauma-Informed Care Principles:**
1. Safety
2. Trustworthiness/Transparency
3. Peer support
4. Collaboration/Mutuality
5. Empowerment/Voice/Choice
6. Cultural/Historical/Gender issues

**Design goals (not built):** all 6 trauma-informed principles

---

## 🔬 Research Integration

### Evidence Base for Digital Mental Health Interventions

**Effectiveness Studies:**
- Meta-analysis: CBT-based apps reduce depression (d = 0.38, Firth et al., 2017)
- RCT: Digital interventions effective for anxiety (SMD = -0.33, Andrews et al., 2018)
- Cochrane Review: Computerized CBT for depression/anxiety shows benefit

**Inspiration, not evidence:** the design draws on published evidence as inspiration — no clinical claim is made

### Ethical Considerations

**Research Ethics:**
- Informed consent for data use
- Right to withdraw
- Privacy protections
- Transparency about limitations

**Not built:** no research protocols exist

---

## 🎓 Training & Competency Requirements

### For Clinical Use (Optional Licensee Implementation)

**Mental Health Professional Qualifications:**
- Licensed Clinical Psychologist (PhD, PsyD)
- Licensed Clinical Social Worker (LCSW)
- Licensed Professional Counselor (LPC)
- Psychiatrist (MD, DO)
- Psychiatric Nurse Practitioner (PMHNP)
- Licensed Marriage and Family Therapist (LMFT)

**Mythara Recommendation:** If used in clinical settings, licensed professional oversight required

**Supervision Requirements:**
- Graduate students: Licensed supervisor required
- Unlicensed staff: Cannot use for clinical decision-making
- AI oversight: Human clinician final authority

---

## 📄 Documentation & Record-Keeping

### Mental Health Records (If Applicable)

**SOAP Notes Integration:**
- **S**ubjective: User-reported concerns
- **O**bjective: Observable data (usage patterns, assessment scores)
- **A**ssessment: Clinical formulation (by licensed professional)
- **P**lan: Treatment interventions (by licensed professional)

**If ever built:** could support SOAP-style documentation for professionals — and would still NOT be a medical record system

**Retention Requirements:**
- Adult records: 7 years post-discharge (varies by state)
- Minor records: Until age 25 or 7 years post-discharge (whichever longer)
- Design target: user-controlled retention and export (not built)

---

## ⚠️ Limitations & Disclaimers

### What Mythara Aims to Be (none of this built):
○ A design framework informed by published evidence  
○ Accessible mental-health-adjacent technology, once accessibility work is done  
○ A clinical-framework reference for developers (this document)  
○ One day, a support tool for professionals — never a replacement  
○ A platform that surfaces public crisis resources  

### What Mythara Engine IS NOT:
❌ Medical device (unless licensee obtains approval)  
❌ Diagnostic tool (cannot diagnose mental illness)  
❌ Treatment/therapy (cannot replace clinician)  
❌ Crisis intervention service (provides referrals only)  
❌ Substitute for professional help  

### Required Disclaimers (All Deployments)

**Example Disclaimer:**
```
This application is not intended to diagnose, treat, cure, or prevent any 
mental health condition. It is not a substitute for professional medical 
advice, diagnosis, or treatment. If you are experiencing a mental health 
crisis, please contact 988 (Suicide & Crisis Lifeline) or go to your 
nearest emergency room. Always seek the advice of a qualified mental 
health professional with any questions you may have regarding a mental 
health condition.
```

---

## 📞 Mental Health Support Contacts

**Development Consultation:**
- APA Division 42 (Psychologists in Independent Practice)
- SAMHSA Technology Transfer Centers
- Mental Health America (MHA)
- National Alliance on Mental Illness (NAMI)

**Clinical Advisory:**
- Licensed clinical psychologist (recommended for mental health features)
- Psychiatrist (for medication/medical considerations)
- Ethics consultant (APA Ethics Code compliance)

---

## 🔄 Updates & Maintenance

**DSM Updates:**
- DSM-5-TR current (March 2022)
- DSM-6 anticipated 2030s
- Monitor APA announcements for updates

**ICD Updates:**
- ICD-11 current (2022)
- Annual updates from WHO
- Crosswalk updates as needed

**Clinical Guidelines:**
- NICE: Updated as new evidence emerges
- APA: Practice guidelines reviewed every 5-7 years
- SAMHSA: Annual updates to treatment locator

**Intent (no licensees exist, no product shipped):**
- Review this reference annually
- Monitor regulatory changes
- Update the reference when the project’s posture changes

---

## 📜 License & Liability

**This reference provides:**
- A DSM-5-TR/ICD-11 summary for design use
- Published therapeutic-framework summaries for design use
- Public crisis-resource references

**It does not provide:** clinical advice, regulatory approval, liability coverage, or any compliance certification

**Mythara Labs does NOT provide:**
- Clinical advice or consultation
- Medical device approval services
- Liability coverage for mental health claims
- Professional licensure or supervision

**Licensee responsibilities:**
- Obtain appropriate professional consultation
- Comply with mental health regulations in jurisdiction
- Obtain medical device approvals if making clinical claims
- Maintain appropriate liability insurance
- Provide licensed professional oversight if offering clinical services

---

**Mythara Labs LLC (planned)**  
**Mental Health Integration Version:** 1.0.0  
**DSM-5-TR Edition:** March 2022  
**Last Updated:** November 2, 2025  
**Next Review:** November 2, 2026

**Clinical Consultation:** Recommend engaging licensed clinical psychologist for mental health feature deployment

**Disclaimer:** This document is for informational and design reference purposes only. It does not constitute medical advice, clinical guidance, or professional mental health services.
