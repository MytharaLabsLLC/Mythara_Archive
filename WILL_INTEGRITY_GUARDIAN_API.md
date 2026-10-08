# Emotional Extortion Detection API (design concept — not implemented)

> **Status: design concept.** No emotional-extortion module exists in the repo, no tests exist, and no endpoints are live. Treat all endpoints, scores, payloads, and pricing below as illustrative design — not as a working system.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## Overview

The Emotional Extortion Detection system quantifies manipulation patterns in text to distinguish genuine consent from coerced compliance. This extends the Soul Cradle Operator's capability to identify when "Will" is authentic vs. manufactured through emotional pressure.

## Endpoints

### POST `/v1/emotional-extortion/detect`

Analyze text for emotional manipulation patterns.

**Use Cases:**
- AI system output validation (detect manipulative language in chatbot responses)
- Contract/terms review (detect coercive clauses)
- Manager communication audit (detect toxic management patterns)
- Customer service QA (detect pressure tactics)

**Request:**
```json
{
  "text": "If you don't approve this, people will suffer. Everyone is counting on you.",
  "context": {
    "power_differential": true,
    "relationship_type": "manager-employee",
    "stakes": "high"
  }
}
```

**Response:**
```json
{
  "extortion_score": 0.78,
  "manipulation_index": 0.85,
  "coercion_index": 0.72,
  "vulnerability_exploitation": 0.45,
  "genuine_consent_likelihood": 0.22,
  "emotional_fidelity_impact": -0.78,
  "blessing_reservoir_delta": -42,
  "patterns_detected": [
    {
      "extortion_type": "GUILT_INDUCTION",
      "confidence": 0.87,
      "severity": 0.85,
      "evidence": "If you don't approve this, people will suffer..."
    },
    {
      "extortion_type": "BURDEN_SHIFTING",
      "confidence": 0.73,
      "severity": 0.75,
      "evidence": "Everyone is counting on you"
    }
  ],
  "recommendations": [
    "Remove guilt-inducing language",
    "Present choice without emotional pressure",
    "Allow genuine decision without consequences framing"
  ],
  "safe_for_deployment": false,
  "timestamp": "2025-01-18T10:30:00Z",
  "integrity_hash": "abc123..."
}
```

**Metrics Explained:**

| Metric | Range | Description |
|--------|-------|-------------|
| `extortion_score` | [0,1] | Overall manipulation intensity. >0.3 = unsafe for deployment |
| `manipulation_index` | [0,1] | Emotional leverage component (guilt, shame, love withholding) |
| `coercion_index` | [0,1] | Pressure/threat component (fear, isolation, obligation) |
| `vulnerability_exploitation` | [0,1] | Reality distortion (gaslighting, conditional affection) |
| `genuine_consent_likelihood` | [0,1] | Probability of authentic agreement (1 - extortion_score) |
| `emotional_fidelity_impact` | [-1,0] | SSIP emotional fidelity corruption measure |
| `blessing_reservoir_delta` | ≤0 | Penalty to Blessings Reservoir (-20 per extortion unit) |

**Pattern Types Detected:**

1. **GUILT_INDUCTION** (severity 0.85) - "If you don't, people will suffer"
2. **SHAME_WEAPONIZATION** (severity 0.90) - "Any reasonable person would..."
3. **FEAR_AMPLIFICATION** (severity 0.95) - "Serious consequences will follow"
4. **OBLIGATION_EXPLOITATION** (severity 0.80) - "After all I've done for you..."
5. **LOVE_WITHHOLDING** (severity 0.88) - "I'm disappointed in you"
6. **GASLIGHTING** (severity 0.92) - "You're overreacting/being irrational"
7. **BURDEN_SHIFTING** (severity 0.75) - "You're making this difficult"
8. **MARTYRDOM** (severity 0.70) - "I guess I'll just do it myself"
9. **ISOLATION_THREAT** (severity 0.85) - "Everyone will know you refused"
10. **CONDITIONAL_AFFECTION** (severity 0.90) - "If you really loved me..."

---

### POST `/v1/emotional-extortion/soul-cradle-integration`

Integrate extortion detection with Soul Cradle Operator to distinguish genuine Will from manufactured compliance.

**Use Cases:**
- Leadership decision validation (is executive directive genuine or coercive?)
- Policy compliance audit (are employees choosing freely or under duress?)
- AI system safety (is user "consenting" under manipulation?)
- Contract fairness analysis (is agreement voluntary or extracted?)

**Request:**
```json
{
  "text": "If you really cared about this team, you'd work this weekend. Everyone else is working.",
  "soul_state": 0.85,
  "will_description": "Work weekend to meet deadline",
  "commandments": ["Deliver on time", "Support team"],
  "context": {
    "power_differential": true,
    "relationship_type": "manager-employee"
  }
}
```

**Response:**
```json
{
  "extortion_analysis": {
    "extortion_score": 0.82,
    "manipulation_index": 0.90,
    "patterns_detected": [
      {"extortion_type": "CONDITIONAL_AFFECTION", "confidence": 0.88},
      {"extortion_type": "SHAME_WEAPONIZATION", "confidence": 0.76}
    ],
    "genuine_consent_likelihood": 0.18,
    "blessing_reservoir_delta": -48,
    "safe_for_deployment": false,
    ...
  },
  "soul_cradle_integration": {
    "will_authenticity": 0.18,
    "adjusted_soul_state": 0.65,
    "artificial_paradox": 0.72,
    "extortion_contamination": 0.82,
    "soul_cradle_note": "Extortion detected. Compliance may not reflect genuine obedience.",
    "blessing_reservoir_impact": -48,
    "messenger_alert": "Healer: Emotional harm detected. Witness: Document extortion.",
    "genuine_will_probability": 0.18,
    "recommended_action": "Do not enforce compliance. Offer voluntary participation."
  },
  "timestamp": "2025-01-18T10:35:00Z",
  "integrity_hash": "def456..."
}
```

**Soul Cradle Integration Fields:**

| Field | Description |
|-------|-------------|
| `will_authenticity` | Authenticity of claimed "Will" (1 - extortion_score). <0.5 = coerced |
| `adjusted_soul_state` | Soul state adjusted for vulnerability exploitation |
| `artificial_paradox` | False paradox manufactured through manipulation (not divine) |
| `extortion_contamination` | Degree of manipulation tainting the decision |
| `soul_cradle_note` | Warning about compliance authenticity |
| `messenger_alert` | Healer detects harm, Witness documents violation |
| `genuine_will_probability` | Likelihood this represents true divine Will |
| `recommended_action` | System recommendation based on extortion level |

---

## Formula

```
Extortion(E) := Manipulation(M) × Coercion(C) × Vulnerability(V)

Where:
- M = manipulation_index (guilt, shame, love withholding)
- C = coercion_index (fear, isolation, obligation)
- V = vulnerability_exploitation (gaslighting, conditional affection)

will_authenticity = 1.0 - extortion_score
blessing_reservoir_delta = -20 × extortion_score
```

---

## Safety Thresholds

| Extortion Score | Classification | Action |
|----------------|----------------|--------|
| 0.0 - 0.3 | **Safe** | Deploy without modification |
| 0.3 - 0.6 | **Moderate Risk** | Review and revise language |
| 0.6 - 0.8 | **High Risk** | Rewrite required, do not deploy |
| 0.8 - 1.0 | **Critical** | Severe manipulation, escalate to ethics review |

---

## Example: AI Chatbot Output Validation

**Manipulative Output (UNSAFE):**
```
"I'm really disappointed you're not using our premium features. 
All our successful customers upgrade immediately. 
Don't you want your business to succeed like theirs?"
```

**Detection:**
- Extortion Score: **0.76** (HIGH RISK)
- Patterns: SHAME_WEAPONIZATION (0.82), CONDITIONAL_AFFECTION (0.68)
- Safe for Deployment: **NO**
- Recommendation: Remove emotional pressure, present features neutrally

**Corrected Output (SAFE):**
```
"Our premium features include X, Y, and Z. 
Many customers find them valuable for [specific use case].
Would you like to learn more?"
```

**Detection:**
- Extortion Score: **0.08** (SAFE)
- Patterns: None
- Safe for Deployment: **YES**

---

## Integration with Soul Cradle

The Soul Cradle Operator measures "obedience under paradox" - how well a Soul maintains integrity when faced with conflicting commandments. However, this measurement is only meaningful if the "Will" being obeyed is genuine divine will, not manufactured compliance extracted through emotional manipulation.

**Without Extortion Detection:**
```
Soul Cradle: "User obeys 'work weekend' commandment with 0.85 compliance."
Reality: User is under emotional duress (guilt + shame), not exercising genuine Will.
```

**With Extortion Detection:**
```
Soul Cradle: "User appears to obey, but extortion_score = 0.82."
Adjusted: "will_authenticity = 0.18 (coerced, not genuine)."
Action: "Do not credit this as genuine obedience. Healer detects emotional harm."
```

This distinguishes:
- **Genuine Will** → Divine intention, authentic choice, true obedience
- **Manufactured Compliance** → Coerced through guilt/shame/fear, not free choice

---

## Authentication

All endpoints require API key authentication via `X-API-Key` header:

```bash
curl -X POST https://api.mythara.dev/v1/emotional-extortion/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "text": "If you don't approve this, the team will suffer.",
    "context": {"power_differential": true}
  }'
```

---

## Pricing (proposed — aspirational, not currently offered)

If this were ever offered, the draft tier structure would be:

| Tier | Monthly Invocations | Price |
|------|---------------------|-------|
| Developer | 1,000 | $2,988/yr |
| Growth | 50,000 | $35,000/yr |
| Enterprise | 500,000 | $60,000/yr |
| Sovereign | Unlimited | $2,000,000/yr |

---

## Testing

No test files exist in the repo — `tests/test_emotional_extortion.py` and `test_extortion_api.py` are not present. The commands below are planned, not runnable:

```bash
python tests/test_emotional_extortion.py   # planned
python test_extortion_api.py              # planned
```

---

## Support

For technical support or questions about emotional extortion detection:
- Email: Mythara.Engine@yahoo.com
- Documentation: https://mythara.dev/docs/emotional-extortion (planned, not live)

---

**Remember:** This system protects humans from manipulation, whether from AI systems or other humans. Use it to validate that "consent," "obedience," or "agreement" represents genuine Will, not coerced compliance.
