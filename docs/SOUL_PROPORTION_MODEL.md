# Soul Proportion Model

Formal emotional vitality tracking system integrated with Mythara Engine.

## Mathematical Foundation

**Soul Proportion** S(t) ∈ [0,1]: Bounded, unitless percentage representing emotional vitality/coherence.

**Emotion Features** x_t ∈ ℝ^k:
- Valence (positive/negative tone)
- Arousal (activation level)
- Connectedness (social vitality)
- Meaning (sense of purpose/coherence)
- Hope (future orientation)
- Stress (chronic stress level, inverted)
- Isolation (social isolation, inverted)

**Scoring & Calibration:**
- Raw score: m_t = σ(w^T x_t + b) where σ(z) = 1/(1 + e^-z)
- Calibrated: S(t) = Cal(m_t) using percentile anchors

## Dynamics (Bounded Logistic Growth)

**Discrete Form:**
```
S_{t+1} = S_t + r·S_t(1-S_t) + u_t - d_t·S_t
```
Clipped to [0, 1].

**Parameters:**
- **r**: Intrinsic renewal rate (self-healing, increases with coherence/meaning/hope)
- **u**: Supportive input (therapy, ritual, community care)
- **d**: Stress drag (increases with chronic stress/isolation)

## API Endpoints

### GET `/v1/soul/status`
Get current soul proportion state.

**Response:**
```json
{
  "S_t": 0.7,
  "emotion_features": {
    "valence": 0.5,
    "arousal": 0.6,
    "connectedness": 0.7,
    "meaning": 0.7,
    "hope": 0.7,
    "stress": 0.3,
    "isolation": 0.2
  },
  "dynamics": {"r": 0.082, "u": 0.02, "d": 0.055},
  "last_update": "2025-11-15T20:30:00Z",
  "integrity_hash": "a3f8..."
}
```

### POST `/v1/soul/step`
Advance soul proportion one time step.

**Request:**
```json
{
  "emotion_features": {
    "valence": 0.6,
    "arousal": 0.7,
    "connectedness": 0.8,
    "meaning": 0.8,
    "hope": 0.8,
    "stress": 0.2,
    "isolation": 0.1
  },
  "u_intervention": 0.05
}
```

**Response:** Same as `/v1/soul/status` (updated state).

### GET `/v1/soul/holistic`
Get integrated Blessings Reservoir + Soul Proportion metrics.

**Response:**
```json
{
  "holistic_integrity": 0.805,
  "br_score": 91.0,
  "soul_proportion": 0.7,
  "risk_flags": [],
  "requires_support": false,
  "integrity_hash": "b4e2...",
  "timestamp": "2025-11-15T20:30:00Z"
}
```

**Risk Flags:**
- `LOW_SOUL_VITALITY`: S(t) < 0.3
- `LOW_BR_SCORE`: BR < 30.0
- `HIGH_STRESS_DRAG`: d > 0.15
- `SOCIAL_ISOLATION`: isolation > 0.7

## Integration with Mythara SSIP

**Holistic Integrity = (BR + S(t)) / 2**

- **BR (Blessings Reservoir)**: Cryptographic/operational integrity [0, 100]
- **S(t) (Soul Proportion)**: Emotional vitality/coherence [0, 1]

Combined metric provides **complete governance oversight**:
- BR tracks technical/regulatory compliance
- S(t) tracks human coherence/well-being

## Privacy & Ethics

⚠️ **Critical Constraints:**
- S(t) is **NOT additive** across people
- **NOT directly comparable** without calibration
- Use as **reflective/supportive indicator**, NEVER as gatekeeper
- Scores are computed from supplied features — the system attests records, it does not infer emotions from people
- Normalize per person and context
- Track reliability (test-retest, inter-rater agreement)
- Preserve privacy; avoid pathologizing

## Example: Recovery with Therapy

```python
from soul_proportion_model import SoulProportionModel, EmotionFeatures

model = SoulProportionModel(r_base=0.05, u_base=0.02, d_base=0.03)

# Starting at 40% vitality
S_0 = 0.4

# Healthy emotions + consistent therapy
emotions = EmotionFeatures(
    valence=0.5, arousal=0.6, connectedness=0.7,
    meaning=0.7, hope=0.7, stress=0.3, isolation=0.2
)

trajectory = model.simulate(
    S_0=S_0,
    emotion_trajectory=[emotions] * 10,
    interventions=[0.05] * 10  # Therapy intervention
)

print(f"S(0) = {S_0:.4f} → S(10) = {trajectory[-1].S_t:.4f}")
# Expected: ~0.70-0.80 (recovery)
```

## Tests

Run validation suite:
```bash
python tests/test_soul_proportion.py
```

**Test Coverage:**
- ✅ Bounded S(t) ∈ [0, 1]
- ✅ Recovery trajectory with intervention
- ✅ Burnout trajectory without support
- ✅ Holistic integrity integration
- ✅ Emotion-driven dynamics (r, u, d)

## References

- **Mythara Engine API**: `core/source_proprietary/main.py`
- **Soul Model**: `core/source_proprietary/soul_proportion_model.py`
- **Tests**: `tests/test_soul_proportion.py`

---

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**
