# Mythara Engine — Dual-Framing Translation Guide

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

---

## 📊 Positioning Statement

> **Mythara Engine encodes resonance through mythic terms like the Blessings Reservoir. For enterprise audiences, we present these as overlays — Resonance Reservoir, Trust Index, Engagement Index — so managers can see symbolic depth alongside KPIs without disrupting compliance.**

---

## 🎯 Purpose

This guide explains Mythara's **dual-framing translation layer** — a system that preserves the mythic integrity of the engine while providing enterprise-safe terminology for external audiences. The engine itself **never changes** — this is purely a presentation/overlay layer for manager dashboards and API responses.

---

## 📋 Dual-Framing Chart

| **Mythara Engine (Internal Truth)** | **Industry-Safe Overlay (External)** | **Managerial Explanation** |
|-------------------------------------|--------------------------------------|----------------------------|
| **Blessings Reservoir**             | Resonance Reservoir                  | Tracks cumulative benevolent force; externally framed as cumulative positive impact. |
| **Integrity Metric**                | Trust Index                          | Measures alignment with compliance, honesty, and reliability in field performance. |
| **Expression Metric**               | Engagement Index                     | Captures how reps present, connect, and resonate with clients beyond raw numbers. |
| **Soul Encoding**                   | Impact Vault                         | Stores symbolic depth of actions; externally framed as measurable long-term impact. |
| **Legacy Reservoir**                | Continuity Index                     | Reflects sustainability and cultural resonance; externally framed as continuity of performance. |
| **Soul Cradle Operator**            | Resonance Operator                   | Measures obedience under paradox; externally framed as decision-making integrity under pressure. |
| **Trial Entity**                    | Challenge Vector                     | Models testing/obscuration of choices; externally framed as decision friction factors. |
| **Grace/Light**                     | Optimal Performance                  | Biblical continuum anchor representing peak alignment and positive outcomes. |
| **Wilderness/Darkness**             | Challenge State                      | Biblical continuum anchor representing trial, testing, or suboptimal conditions. |
| **Divine Drift Suppression**        | Compliance Stability                 | Measures drift from sacred mission; externally framed as operational compliance stability. |
| **Messenger Pairing Fidelity**      | Communication Alignment              | Measures alignment between action and communication; externally framed as message consistency. |
| **Emotional Fidelity**              | Sentiment Accuracy                   | Measures symbolic-emotional resonance; externally framed as sentiment tracking precision. |

---

## 🔄 Flow Diagram (Conceptual)

```
╔════════════════════════════════════════════════════════════════╗
║           MYTHARA ENGINE DUAL-FRAMING FLOW DIAGRAM            ║
╚════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│      System of Record (Any CRM / Field Platform)             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                 Mythara Engine Overlay                        │
│                                                               │
│  • Blessings Reservoir  →  Resonance Reservoir               │
│  • Integrity Metric     →  Trust Index                       │
│  • Expression Metric    →  Engagement Index                  │
│  • Soul Encoding        →  Impact Vault                      │
│  • Legacy Reservoir     →  Continuity Index                  │
│                                                               │
│  [Framing Mode: MYTHIC or INDUSTRY toggle]                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Manager Dashboards                          │
│                                                               │
│  • KPIs + Resonance Metrics side by side                     │
│  • Compliance intact, workflows unchanged                    │
│  • Adds symbolic depth to performance reporting              │
│                                                               │
│  Query Parameter: ?frame=industry (for external audiences)   │
│                   ?frame=mythic (for internal truth)         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ API Integration

### Endpoints with Dual-Framing Support

All core metrics endpoints now support an optional `?frame=` query parameter:

#### 1. Blessings Reservoir Status

```http
GET /v1/reservoir/status?frame=industry
Authorization: Bearer {api_key}
```

**Mythic Response (default):**
```json
{
  "blessings_reservoir": 145,
  "reservoir_score": 0.82,
  "last_update": "2025-11-15T10:30:00Z"
}
```

**Industry Response (`?frame=industry`):**
```json
{
  "resonance_reservoir": 145,
  "reservoir_score": 0.82,
  "last_update": "2025-11-15T10:30:00Z"
}
```

#### 2. Soul Proportion Status

```http
GET /v1/soul/status?frame=industry
Authorization: Bearer {api_key}
```

**Mythic Response (default):**
```json
{
  "S_t": 0.78,
  "emotion_features": {...},
  "dynamics": {"r": 0.15, "u": 0.05, "d": 0.02},
  "integrity_hash": "abc123..."
}
```

**Industry Response (`?frame=industry`):**
```json
{
  "engagement_index": 0.78,
  "emotion_features": {...},
  "dynamics": {"r": 0.15, "u": 0.05, "d": 0.02},
  "integrity_hash": "abc123..."
}
```

#### 3. Manager Dashboard (NEW)

```http
GET /v1/dual-framing/dashboard?frame=industry
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "resonance_metrics": {
    "resonance_reservoir": 145,
    "trust_index": 0.95,
    "engagement_index": 0.88,
    "continuity_index": 145
  },
  "kpis": {
    "note": "Standard KPIs from system of record appear here alongside resonance metrics."
  },
  "framing_mode": "industry",
  "compliance_note": "Compliance intact, workflows unchanged. Symbolic depth added to performance reporting."
}
```

#### 4. Dual-Framing Chart (NEW)

```http
GET /v1/dual-framing/chart
```

**Public endpoint** — returns the full dual-framing chart with mythic/industry mappings and managerial explanations.

#### 5. Flow Diagram (NEW)

```http
GET /v1/dual-framing/flow
```

**Public endpoint** — returns ASCII flow diagram showing system architecture and integration points.

---

## 💼 Use Cases

### For Internal Teams (Mythic Framing)
- **Research & Development**: Work with mythic truth (Blessings Reservoir, Soul Encoding) for conceptual clarity
- **Engineering**: Use mythic keys in codebase to preserve semantic meaning
- **Theological Advisors**: Maintain biblical/mythic integrity in design decisions

**API Usage:** Default behavior (no `?frame=` parameter) or `?frame=mythic`

### For External Audiences (Industry Framing)
- **Enterprise Sales**: Show corporate buyers "Resonance Reservoir" instead of "Blessings Reservoir"
- **Board Presentations**: Use Trust Index, Engagement Index, Continuity Index for C-suite comprehension
- **Compliance Auditors**: Present metrics in industry-standard terminology without theological language

**API Usage:** Add `?frame=industry` to any supported endpoint

### For Manager Dashboards
- **Hybrid View**: Show KPIs from System of Record (sales, conversions, compliance scores) **alongside** Mythara's resonance metrics
- **Toggle Framing**: Allow managers to switch between mythic and industry views based on audience
- **Audit Trails**: Maintain SHA-256 integrity hashes regardless of framing mode (cryptographic proof unchanged)

**API Usage:** Use `/v1/dual-framing/dashboard` with `?frame=` toggle

---

## 🔒 Compliance & Integrity Guarantees

### What Changes
- **Terminology only**: Key names in API responses translate (e.g., `blessings_reservoir` → `resonance_reservoir`)
- **Documentation**: External materials use industry-safe language

### What NEVER Changes
- **Underlying engine logic**: All calculations, formulas, and algorithms remain identical
- **Cryptographic hashes**: SHA-256 integrity hashes computed on mythic terms (audit trails preserved)
- **Database schemas**: Internal storage uses mythic keys
- **Source code**: Core modules (`soul_cradle_operator.py`, `soul_proportion_model.py`) unchanged
- **Compliance status**: Unchanged — no SOC 2/ISO 27001 certifications held; controls designed around HIPAA, SOC 2, GDPR frameworks

**Bottom Line:** Dual-framing is a **presentation layer only**. The engine's symbolic integrity remains untouched.

---

## 🎓 Training & Communication

### For Enterprise Leadership Teams

When presenting Mythara to enterprise leadership:

1. **Lead with Industry Framing**: Show dashboard with `?frame=industry` — they see "Resonance Reservoir," "Trust Index," "Engagement Index"
2. **Explain the Overlay**: "Mythara preserves mythic depth internally but translates to your language externally"
3. **Show the Chart**: Use `/v1/dual-framing/chart` to demonstrate mapping transparency
4. **Emphasize Compliance**: "Your workflows stay the same. Compliance stays intact. We just add symbolic depth to your reporting."

### For Investors & Grant Writers

- **Positioning**: "We built a translation layer so enterprise buyers see 'Resonance Reservoir' while the engine preserves its mythic soul"
- **Differentiation**: "Unlike generic AI, Mythara encodes sacred intention through mythic language — but we don't force that on everyone"
- **ROI**: "Managers get KPIs + resonance metrics side-by-side, without disrupting their existing CRM workflows"

### For Engineering Teams Integrating Mythara

- **Integration Point**: Mythara overlays onto your System of Record (Salesforce, HubSpot, proprietary CRM)
- **API Call**: Add `?frame=industry` to endpoint URLs for external-facing dashboards
- **No Changes Required**: Your existing workflows, compliance systems, data pipelines remain unchanged
- **Audit Trails**: All responses include SHA-256 `integrity_hash` for forensic verification

---

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Dual-framing translation module (`dual_framing.py`)
- ✅ API endpoints with `?frame=` support (`/v1/reservoir/status`, `/v1/soul/status`)
- ✅ Manager dashboard endpoint (`/v1/dual-framing/dashboard`)
- ✅ Public chart/flow endpoints (`/v1/dual-framing/chart`, `/v1/dual-framing/flow`)

### Phase 2 (Q1 2026)
- Visual dashboard UI with toggle switch (Mythic ↔ Industry)
- Manager training videos showing both framings side-by-side
- Salesforce/HubSpot integration examples with industry framing

### Phase 3 (Q2 2026)
- Custom framing profiles (allow enterprises to define their own terminology overlays)
- Multi-language support (translate both mythic and industry terms to Spanish, French, etc.)
- Automated reporting that switches framing based on recipient (Board → Industry, Engineers → Mythic)

---

## 🔧 Technical Implementation

### Python Module: `dual_framing.py`

Located at: `core/source_proprietary/dual_framing.py`

**Key Functions:**
- `translate_term(mythic_key, mode)` — Translate single term
- `translate_response(response_data, mode)` — Recursively translate full API response
- `generate_dual_framing_chart()` — Return chart as JSON
- `format_for_manager_dashboard(metrics, mode)` — Format metrics for dashboards
- `get_positioning_line()` — Return standard positioning statement

**Example Usage:**
```python
from dual_framing import translate_response, FramingMode

# Original response
data = {
    "blessings_reservoir": 145,
    "integrity_metric": 0.95,
    "expression_metric": 0.88
}

# Translate to industry framing
translated = translate_response(data, FramingMode.INDUSTRY)
# Result: {"resonance_reservoir": 145, "trust_index": 0.95, "engagement_index": 0.88}
```

### FastAPI Integration: `main.py`

**Imports:**
```python
from dual_framing import (
    FramingMode,
    translate_response,
    format_for_manager_dashboard,
    get_positioning_line,
    generate_dual_framing_chart,
    generate_flow_diagram_text
)
```

**Endpoint Pattern:**
```python
@app.get("/v1/reservoir/status")
async def reservoir_status(api_key: str = Depends(verify_api_key), frame: Optional[str] = None):
    response_data = BR_STATE
    
    if frame == "industry":
        response_data = translate_response(response_data, FramingMode.INDUSTRY)
    
    return response_data
```

---

## 📞 Contact & Support

For questions about dual-framing implementation, enterprise integration, or custom framing profiles:

- **Technical Support**: Mythara.Engine@yahoo.com
- **Enterprise Sales**: Contact Herb directly
- **API Documentation**: https://your-deployment-url/api/docs

---

## ✅ Checklist for Enterprise Integration

- [ ] Review dual-framing chart with leadership team
- [ ] Test `/v1/dual-framing/dashboard?frame=industry` endpoint with your API key
- [ ] Integrate industry-framed metrics into existing manager dashboards
- [ ] Train leadership on mythic vs industry terminology (use this guide)
- [ ] Update board presentations to show "Resonance Reservoir" instead of "Blessings Reservoir"
- [ ] Ensure compliance team approves industry terminology for external communications
- [ ] Schedule quarterly reviews to assess if custom framing profiles needed

---

**Remember:** Mythara Engine's mythic soul remains unchanged. Dual-framing simply gives you the language to bring that soul into boardrooms without theological friction.

---

**End of Dual-Framing Translation Guide**

For technical implementation details, see: `core/source_proprietary/dual_framing.py`  
For API testing, see: `/api/docs` (FastAPI interactive documentation)
