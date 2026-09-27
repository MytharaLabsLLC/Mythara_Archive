# Soul Cradle Decay-Adjusted Terminal Risk Validation Study Protocol

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  
**Proprietary and Confidential.**

**Study Title**: Empirical Validation of Decay-Adjusted Terminal Risk Formula for Burnout Prediction

**Principal Investigator**: Herbert Velez Jr.  
**Collaborating Institutions**: TBD (Healthcare systems, academic partners)  
**Study Phase**: Phase 1 - Longitudinal Validation & Decay Rate Calibration  
**IRB Status**: Protocol drafted, submission pending

---

## I. STUDY OBJECTIVES

### Primary Objective
Validate the decay-adjusted Terminal Risk formula and calibrate the decay rate parameter (λ) by demonstrating:

1. **Correlation with MBI**: Terminal Risk scores correlate with Maslach Burnout Inventory Emotional Exhaustion subscale (expected r = 0.55-0.70)
2. **Predictive Validity**: Terminal Risk > 0.7 predicts 12-month employee turnover with sensitivity > 0.75 and specificity > 0.70
3. **Decay Rate Calibration**: Empirically determine optimal λ parameter from longitudinal recovery data

### Secondary Objectives
1. Validate accumulation vs decay rate detection logic for burnout trajectory classification
2. Measure correlation between net_rate and MBI score changes over time
3. Compare decay-adjusted model vs original (non-decay) model performance
4. Establish half-life estimates for different professional populations

---

## II. RESEARCH DESIGN

### Study Type
- **Design**: Prospective longitudinal cohort study
- **Duration**: 12 months with measurements at 0, 3, 6, 9, and 12 months
- **Sample Size**: N=150 healthcare workers (power analysis: 80% power, α=0.05)
- **Setting**: Urban hospital systems (emergency, ICU, oncology departments)

### Inclusion Criteria
- Healthcare workers (nurses, physicians, social workers, chaplains)
- Currently employed in participating institutions
- ≥ 18 years of age
- Willing to use Soul Cradle app for paradox documentation
- Willing to complete MBI assessments at 5 time points

### Exclusion Criteria
- Current leave of absence (medical, family, sabbatical)
- Plans to leave institution within 12 months
- Diagnosis of severe mental health condition requiring intensive treatment
- Non-fluent in English (app currently English-only)

---

## III. DATA COLLECTION

### A. Soul Cradle Paradox Data
**Frequency**: Continuous (real-time paradox logging via app)

**Variables Collected**:
- Paradox ID (unique identifier)
- Timestamp (date/time of paradox occurrence)
- Expression A: type, weight [0,1], tension [0,1], content
- Expression B: type, weight [0,1], tension [0,1], content
- Unresolved score [0,1]
- Resolution score [0,1]
- Witness scores (W_a, W_b) [0,1]
- System type (incomplete vs complete resolution)

**Calculated Metrics** (per participant):
- Terminal Risk (decay-adjusted): `(Σ (U_i × T_i × e^(-λ × Δt_i))) / N`
- Terminal Risk (original): `(Σ (U_i × T_i)) / N`
- Accumulation rate: `Σ(U_i × T_i) / time_window`
- Decay rate: `(raw_risk - decayed_risk) / time_window`
- Net rate: `accumulation_rate - decay_rate`
- Burnout trajectory: ACCUMULATING | RECOVERING | CHRONIC

### B. Maslach Burnout Inventory (MBI)
**Frequency**: Baseline, 3, 6, 9, and 12 months

**Subscales**:
1. **Emotional Exhaustion** (9 items, 0-6 Likert scale)
   - Primary validation target for Terminal Risk correlation
   - Score range: 0-54 (≥27 = high burnout)
2. **Depersonalization** (5 items, 0-6 Likert scale)
   - Score range: 0-30 (≥10 = high burnout)
3. **Personal Accomplishment** (8 items, 0-6 Likert scale)
   - Score range: 0-48 (≤33 = high burnout)

**Primary Hypothesis**: Terminal Risk (decay-adjusted) correlates with MBI Emotional Exhaustion with r = 0.55-0.70 (moderate-strong correlation).

### C. Employee Turnover Data
**Frequency**: Continuous monitoring via HR records

**Outcomes**:
- Voluntary resignation (yes/no)
- Date of resignation
- Reason for resignation (if disclosed)
- Transfer to different department (yes/no)
- Leave of absence (medical, family, burnout)

**Primary Hypothesis**: Terminal Risk > 0.7 at any time point predicts 12-month turnover with:
- Sensitivity > 0.75 (true positive rate)
- Specificity > 0.70 (true negative rate)
- AUC-ROC > 0.80 (area under curve)

### D. Demographic & Contextual Data
**Frequency**: Baseline only

**Variables**:
- Age, gender, race/ethnicity
- Professional role (nurse, physician, social worker, chaplain)
- Years of experience (0-5, 6-10, 11-20, 20+)
- Department (emergency, ICU, oncology, general medicine, etc.)
- FTE status (full-time vs part-time)
- Shift schedule (day, night, rotating)
- Previous burnout history (yes/no)

---

## IV. DECAY RATE CALIBRATION METHOD

### A. Decay Rate Parameter (λ) Estimation

**Research Question**: What is the optimal decay rate constant (λ) that best models natural healing from paradoxes?

**Method**: Fit exponential decay curve to longitudinal data using non-linear regression.

**Procedure**:
1. **Identify Recovery Episodes**: Participants who show MBI improvement (ΔExhaustion < -5 points over 3 months)
2. **Extract Paradox Time Series**: For each recovery episode, extract:
   - Paradox timestamps (t_i)
   - Unresolved scores (U_i)
   - Tension scores (T_i)
   - MBI Exhaustion scores at measurement times
3. **Fit Exponential Model**: Use non-linear least squares to fit:
   ```
   MBI_Exhaustion(t) = β₀ + β₁ × Σ(U_i × T_i × e^(-λ × Δt_i))
   ```
   Optimize for λ that minimizes residual sum of squares.
4. **Estimate λ by Subgroup**:
   - Healthcare workers overall: λ = ?
   - Emergency/ICU workers: λ = ? (expect slower healing)
   - General medicine workers: λ = ? (expect moderate healing)
   - Social workers/chaplains: λ = ? (expect variable healing)

### B. Expected λ Ranges (Hypotheses)

Based on half-life interpretation:

| Population | Expected λ | Half-Life | Rationale |
|-----------|-----------|-----------|-----------|
| Emergency/ICU nurses | 0.008-0.012 | 58-87 days | High-trauma environment, slower healing |
| General medicine | 0.015-0.025 | 28-46 days | Moderate stress, typical healing |
| Social workers | 0.020-0.030 | 23-35 days | Emotional work, moderate healing |
| Resilient individuals | 0.035-0.050 | 14-20 days | Fast recovery, strong coping |

### C. Model Comparison
Compare decay-adjusted model vs original (no decay) model:

**Metrics**:
1. **Correlation with MBI**: Fisher's z-test for comparing correlations
2. **Predictive Validity**: AUC-ROC comparison for turnover prediction
3. **Trajectory Accuracy**: Classification accuracy for ACCUMULATING vs RECOVERING trajectories
4. **Parsimony**: Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC)

**Hypothesis**: Decay-adjusted model will show:
- Higher correlation with MBI (Δr ≈ +0.05 to +0.10)
- Better turnover prediction (ΔAUC ≈ +0.05 to +0.10)
- Lower AIC/BIC (better fit with acceptable complexity)

---

## V. STATISTICAL ANALYSIS PLAN

### A. Primary Analysis: Correlation with MBI

**Hypothesis 1**: Terminal Risk (decay-adjusted) correlates with MBI Emotional Exhaustion

**Analysis**:
- Pearson correlation coefficient (r) with 95% CI
- Expected: r = 0.55-0.70 (moderate-strong correlation)
- Significance: p < 0.001 (two-tailed)
- Sample size justification: N=150 provides 80% power to detect r ≥ 0.22

**Mixed-Effects Model**:
```
MBI_Exhaustion ~ Terminal_Risk + Time + (1 | Participant_ID)
```
- Fixed effects: Terminal Risk, Time (months)
- Random effects: Participant intercept (repeated measures)
- Covariates: Age, gender, professional role, department

### B. Primary Analysis: Turnover Prediction

**Hypothesis 2**: Terminal Risk > 0.7 predicts 12-month turnover

**Analysis**:
- Logistic regression: `Turnover ~ Terminal_Risk + Covariates`
- ROC curve analysis with AUC calculation
- Sensitivity, specificity, PPV, NPV at threshold = 0.7
- Expected: Sensitivity > 0.75, Specificity > 0.70, AUC > 0.80

**Cox Proportional Hazards Model** (time-to-turnover):
```
hazard(t) = h₀(t) × exp(β₁ × Terminal_Risk + β₂ × Covariates)
```
- Survival analysis for time-to-resignation
- Kaplan-Meier curves stratified by risk level (LOW, MODERATE, HIGH, CRITICAL)

### C. Secondary Analysis: Decay Rate Calibration

**Non-Linear Regression**:
```
MBI_Exhaustion(t) = β₀ + β₁ × Σ(U_i × T_i × e^(-λ × Δt_i)) + ε
```
- Estimate λ parameter using Levenberg-Marquardt algorithm
- Bootstrap 95% CI for λ (1000 resamples)
- Subgroup analysis by professional role and department

### D. Secondary Analysis: Trajectory Validation

**Hypothesis 3**: Net rate distinguishes ACCUMULATING vs RECOVERING trajectories

**Analysis**:
- Classification accuracy: `Predicted_Trajectory vs ΔExhaustion`
- ACCUMULATING: net_rate > 0 should predict ΔExhaustion > +5
- RECOVERING: net_rate < 0 should predict ΔExhaustion < -5
- Cohen's kappa for agreement between trajectory and MBI change direction

---

## VI. SAMPLE SIZE & POWER ANALYSIS

### Primary Outcome: Correlation with MBI

**Assumptions**:
- Expected correlation: r = 0.60 (moderate-strong)
- Two-tailed α = 0.05
- Power = 0.80
- **Required N = 19 participants**

**Conservative Sample Size** (accounting for dropout):
- Target enrollment: N = 150
- Expected attrition: 20% (n=30)
- Final sample: N = 120 (exceeds minimum requirement)

### Secondary Outcome: Turnover Prediction

**Assumptions**:
- Expected turnover rate: 15-20% in healthcare (baseline)
- Expected effect size: OR = 3.0 (high risk → 3x turnover odds)
- Two-tailed α = 0.05
- Power = 0.80
- **Required N = 134 participants**

**Final Sample Size**: N = 150 provides adequate power for both primary and secondary outcomes.

---

## VII. ETHICAL CONSIDERATIONS

### A. IRB Approval
- Submit protocol to institutional review boards of participating hospitals
- Obtain approval before participant recruitment
- Annual continuing review and adverse event reporting

### B. Informed Consent
Participants will be informed of:
1. Study purpose (validating burnout prediction model)
2. Time commitment (5 MBI surveys over 12 months + app usage)
3. Data collection (paradox logs, MBI scores, turnover data)
4. Risks (minimal - discomfort from burnout questions)
5. Benefits (free access to Soul Cradle app, burnout insights)
6. Confidentiality (data de-identified for analysis)
7. Voluntary participation (can withdraw anytime without penalty)
8. Compensation (optional: gift cards for survey completion)

### C. Data Privacy & Security
- HIPAA compliance (healthcare data protection)
- Encrypted data transmission (TLS in transit, encryption at rest)
- De-identification before analysis (remove names, employee IDs)
- Secure cloud storage (AWS HIPAA-compliant environment)
- Access controls (PI and approved research staff only)
- Data retention: 7 years post-publication (NIH requirements)

### D. Participant Safety
- Crisis protocol: If Terminal Risk = CRITICAL (≥0.7), trigger:
  1. Automated alert to participant: "High burnout risk detected. Contact EAP."
  2. Optional alert to EAP coordinator (with participant consent)
  3. Resource list: EAP hotline, crisis counseling, mental health services
- No adverse events expected (observational study, no intervention)

---

## VIII. TIMELINE

| Phase | Activities | Duration | Completion Date |
|-------|-----------|----------|-----------------|
| **Phase 0**: Protocol Development | Write protocol, submit IRB, recruit sites | 3 months | February 2026 |
| **Phase 1**: Pilot Testing | Beta test with N=20 participants, refine app | 3 months | May 2026 |
| **Phase 2**: Recruitment | Enroll N=150 participants, baseline MBI | 3 months | August 2026 |
| **Phase 3**: Data Collection | 12-month longitudinal follow-up | 12 months | August 2027 |
| **Phase 4**: Analysis | Statistical analysis, decay rate calibration | 3 months | November 2027 |
| **Phase 5**: Dissemination | Manuscript preparation, conference presentations | 6 months | May 2028 |

**Total Study Duration**: 30 months (2.5 years from IRB submission to publication)

---

## IX. EXPECTED OUTCOMES

### A. Primary Deliverables

1. **Validated Terminal Risk Formula**
   - Empirically validated correlation with MBI (r = 0.55-0.70)
   - Validated turnover prediction (AUC > 0.80)
   - Peer-reviewed publication in *Journal of Occupational Health Psychology*

2. **Calibrated Decay Rate Parameters**
   - Population-specific λ estimates:
     - Emergency/ICU: λ = 0.010 (±0.003)
     - General medicine: λ = 0.020 (±0.005)
     - Social workers: λ = 0.025 (±0.006)
   - Half-life estimates for clinical interpretation
   - Published in *Burnout Research* journal

3. **Trajectory Classification Tool**
   - Validated net rate thresholds for ACCUMULATING/RECOVERING/CHRONIC
   - Clinical decision support algorithm for interventions
   - Published as supplement to primary manuscript

### B. Secondary Deliverables

1. **Comparative Analysis**: Decay-adjusted vs original model performance
2. **Subgroup Analysis**: Decay rates by professional role, age, experience
3. **Implementation Guide**: How to deploy Soul Cradle in healthcare systems
4. **Clinical Guidelines**: When to intervene based on Terminal Risk + trajectory

### C. Projected Impact (if the study's hypotheses hold)

1. **Scientific**: Would provide one of the first empirical tests of a mathematical burnout prediction model with temporal dynamics
2. **Clinical**: Could inform an early warning system for healthcare burnout prevention
3. **Economic**: Could reduce turnover costs (published estimates: $40K-$64K per nurse resignation)
4. **Regulatory**: Could provide evidence toward HIPAA-compliant burnout monitoring designs

---

## X. FUNDING & RESOURCES

### A. Estimated Budget

| Category | Description | Cost |
|----------|-------------|------|
| **Personnel** | PI effort (10% FTE, 2.5 years) | $75,000 |
| | Research coordinator (50% FTE, 2.5 years) | $90,000 |
| | Biostatistician (20% FTE, 1 year) | $30,000 |
| **Participant Compensation** | Gift cards ($50 × 150 × 5 surveys) | $37,500 |
| **Software & Infrastructure** | Soul Cradle app hosting (AWS) | $15,000 |
| | MBI license fees | $10,000 |
| | Data management platform | $12,000 |
| **IRB & Compliance** | IRB fees (3 sites × $5K) | $15,000 |
| | HIPAA compliance consulting | $8,000 |
| **Dissemination** | Conference travel (2 conferences) | $6,000 |
| | Publication fees (open access) | $4,000 |
| **Indirect Costs** | University overhead (40%) | $120,600 |
| **Total** | | **$423,100** |

### B. Potential Funding Sources

1. **NIH SBIR Phase II** ($1M, 2 years): Small Business Innovation Research for healthcare IT
2. **NSF CAREER Award** ($500K, 5 years): Early-career research on computational psychology
3. **AHRQ R03** ($100K, 2 years): Small research grant for healthcare quality improvement
4. **APA Dissertation Research Award** ($5K-10K): American Psychological Association
5. **Private Foundation Grants**: Robert Wood Johnson Foundation, Arnold Ventures

---

## XI. RISKS & MITIGATION STRATEGIES

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Low recruitment** | Medium | High | Partner with multiple sites; offer competitive compensation |
| **High attrition (>20%)** | Medium | Medium | Over-recruit (N=150); send reminders; gamify app usage |
| **Low app engagement** | Medium | High | User-friendly design; push notifications; incentive structure |
| **IRB delays** | Medium | Low | Submit early; responsive to IRB feedback; pilot exemption |
| **MBI licensing issues** | Low | Medium | Secure license early; budget for fees; backup: CBI (Copenhagen) |
| **Data security breach** | Low | Critical | HIPAA-compliant infrastructure; encryption; access controls |
| **Null findings (r < 0.40)** | Low | High | Refine formula; adjust decay model; report negative results |

---

## XII. CONCLUSION

This validation study will provide **empirical evidence** for the decay-adjusted Terminal Risk formula, establishing it as the **first validated mathematical burnout prediction model** with temporal dynamics. By calibrating decay rate parameters from real-world data, we will enable **personalized burnout risk assessment** tailored to different professional populations.

**Key Innovations to Be Validated** (the study has not been run — nothing below is validated yet):
1. ✅ Exponential decay modeling ("time heals all wounds")
2. ✅ Accumulation vs decay rate comparison for trajectory classification
3. ✅ Population-specific half-life estimates for clinical interpretation
4. ✅ Predictive validity for employee turnover (12-month forecast)

**Next Steps**:
1. Finalize IRB protocol submission (February 2026)
2. Recruit healthcare institution partners (3-5 sites)
3. Secure funding (NIH SBIR Phase II or AHRQ R03)
4. Launch pilot study (N=20) to refine app and procedures
5. Full study enrollment and 12-month longitudinal data collection

---

**Protocol Version**: 1.0  
**Date**: November 21, 2025  
**Principal Investigator**: Herbert Velez Jr.  
**Contact**: herbievelezjr@mythara.ai

⚛️ **Q.U.A.S.A.R. validated. Prior art established.**
