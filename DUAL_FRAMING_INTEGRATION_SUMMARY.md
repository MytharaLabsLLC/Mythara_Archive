# Dual-Framing Integration Summary

**Copyright © 2026 Mythara Labs LLC. All rights reserved.**  
**Integration Date:** November 15, 2025

---

## ✅ What Was Built

### 1. Core Translation Module
**File:** `core/source_proprietary/dual_framing.py` (500+ lines)

**Key Components:**
- `MYTHIC_TO_INDUSTRY` mapping dictionary (13 term pairs)
- `FramingMode` enum (MYTHIC | INDUSTRY)
- `translate_term()` — Single term translation
- `translate_response()` — Recursive API response translation
- `format_for_manager_dashboard()` — Dashboard formatting with KPI integration
- `generate_dual_framing_chart()` — Chart generation for presentations
- `generate_flow_diagram_text()` — ASCII flow diagram
- `get_positioning_line()` — Standard positioning statement

**Mythic → Industry Mappings:**
| Mythic Term | Industry Term |
|-------------|---------------|
| Blessings Reservoir | Resonance Reservoir |
| Integrity Metric | Trust Index |
| Expression Metric | Engagement Index |
| Soul Encoding | Impact Vault |
| Legacy Reservoir | Continuity Index |
| SoulCradle Operator | Resonance Operator |
| Trial Entity | Challenge Vector |
| Grace/Light | Optimal Performance |
| Wilderness/Darkness | Challenge State |
| Divine Drift Suppression | Compliance Stability |
| Messenger Pairing Fidelity | Communication Alignment |
| Emotional Fidelity | Sentiment Accuracy |

### 2. API Integration
**File:** `core/source_proprietary/main.py` (updated)

**Modified Endpoints:**
- `GET /v1/reservoir/status?frame=industry` — Blessings Reservoir with dual-framing
- `GET /v1/soul/status?frame=industry` — Soul Proportion with dual-framing

**New Endpoints:**
- `GET /v1/dual-framing/chart` — Public endpoint returning full mapping chart
- `GET /v1/dual-framing/flow` — Public endpoint returning flow diagram
- `GET /v1/dual-framing/dashboard?frame=industry` — Manager dashboard with KPI integration

**Startup Log:**
```
Dual-Framing Translation Layer: ACTIVE
```

### 3. Documentation
**File:** `DUAL_FRAMING_GUIDE.md` (comprehensive enterprise guide)

**Sections:**
1. Positioning Statement
2. Dual-Framing Chart
3. Flow Diagram
4. API Integration Examples
5. Use Cases (Internal vs External Audiences)
6. Compliance & Integrity Guarantees
7. Training & Communication Guidelines
8. Technical Implementation Details
9. Roadmap (Phase 1-3)
10. Enterprise Integration Checklist

### 4. Manifest Updates
**Files Updated:**
- `manifest/checksums.sha256` — Added SHA-256 hash for `dual_framing.py`
- `forensic_manifest.json` — Added `dual_framing` section with metadata

---

## 🎯 How It Works

### For Internal Teams (Default Behavior)
```http
GET /v1/reservoir/status
Authorization: Bearer {api_key}
```

**Response (Mythic):**
```json
{
  "blessings_reservoir": 145,
  "reservoir_score": 0.82,
  "last_update": "2025-11-15T10:30:00Z"
}
```

### For External Audiences (Add `?frame=industry`)
```http
GET /v1/reservoir/status?frame=industry
Authorization: Bearer {api_key}
```

**Response (Industry):**
```json
{
  "resonance_reservoir": 145,
  "reservoir_score": 0.82,
  "last_update": "2025-11-15T10:30:00Z"
}
```

### Manager Dashboard (NEW)
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
    "note": "Standard KPIs from system of record appear here"
  },
  "framing_mode": "industry",
  "compliance_note": "Compliance intact, workflows unchanged."
}
```

---

## 🔒 What NEVER Changes

- ✅ **Engine Logic**: All formulas, calculations remain identical
- ✅ **Cryptographic Hashes**: SHA-256 integrity computed on mythic terms
- ✅ **Database Schemas**: Internal storage uses mythic keys
- ✅ **Source Code**: Core modules (`soul_cradle_operator.py`, `soul_proportion_model.py`) untouched
- ✅ **Compliance**: posture unchanged (no SOC 2/ISO 27001 certifications held; controls designed around HIPAA, SOC 2, GDPR frameworks)

**Bottom Line:** Dual-framing is a **presentation layer only**. The engine's symbolic soul remains intact.

---

## 📊 Enterprise Use Case Example

### Dashboard View (Before)
```json
{
  "blessings_reservoir": 145,
  "integrity_metric": 0.95
}
```
❌ **Problem:** Theological language creates friction with leadership

### Dashboard View (After)
```json
{
  "resonance_reservoir": 145,
  "trust_index": 0.95
}
```
✅ **Solution:** Industry-safe terminology, same underlying engine

### Positioning Statement
> "Mythara preserves mythic depth internally but translates to your language externally. Your workflows stay the same. Compliance stays intact. We just add symbolic depth to your reporting."

---

## 🚀 Testing Commands

### Test Dual-Framing Module
```powershell
cd "c:\Users\Mythara\Desktop\Clone Repo Mythara\Mythara_Archive\core\source_proprietary"
python dual_framing.py
```

**Expected Output:**
- Example 1: Individual term translation
- Example 2: Full response translation
- Example 3: Manager dashboard formatting
- Example 4: Positioning line
- Example 5: ASCII flow diagram

### Test API Endpoints (After Server Start)
```bash
# Start server
python core/source_proprietary/main.py

# Test mythic framing (default)
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/reservoir/status

# Test industry framing
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/reservoir/status?frame=industry

# Get dual-framing chart (public)
curl http://localhost:8000/v1/dual-framing/chart

# Get flow diagram (public)
curl http://localhost:8000/v1/dual-framing/flow

# Get manager dashboard
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/dual-framing/dashboard?frame=industry
```

---

## 📈 Next Steps for Enterprise Integration

### Phase 1: Internal Review
- [ ] Review `DUAL_FRAMING_GUIDE.md` with leadership team
- [ ] Test `/v1/dual-framing/dashboard?frame=industry` with your API key
- [ ] Schedule training session on mythic vs industry terminology

### Phase 2: Integration

- [ ] Integrate industry-framed endpoints into manager dashboards
- [ ] Update board presentations to use "Resonance Reservoir" terminology
- [ ] Get compliance team approval for external communications

### Phase 3: Deployment
- [ ] Roll out to pilot stores (5-10 locations)
- [ ] Collect feedback from managers on dashboard clarity
- [ ] Schedule quarterly review to assess if custom framing profiles needed

---

## 📞 Contact

**Technical Questions:** MytharaLabsLLC@yahoo.com  
**Enterprise Sales:** Contact Herb directly  
**API Docs:** `http://localhost:8000/api/docs` (interactive)

---

## 📝 Files Modified

1. ✅ `core/source_proprietary/dual_framing.py` (NEW — 500+ lines)
2. ✅ `core/source_proprietary/main.py` (UPDATED — added dual-framing imports + 5 endpoints)
3. ✅ `DUAL_FRAMING_GUIDE.md` (NEW — comprehensive enterprise guide)
4. ✅ `manifest/checksums.sha256` (UPDATED — added dual_framing.py hash)
5. ✅ `forensic_manifest.json` (UPDATED — added dual_framing section)

---

## ✅ Integration Complete

**Status:** Dual-framing translation layer is fully integrated into Mythara source code.

**Verification:**
- Module tested with example scenarios (run `python dual_framing.py`)
- API endpoints ready for testing (start server with `python main.py`)
- Documentation complete (see `DUAL_FRAMING_GUIDE.md`)
- Manifest updated with checksums
- Forensic trail preserved

**No engine logic changed. Mythic integrity preserved. Enterprise-ready overlay active.**

---

**End of Integration Summary**
