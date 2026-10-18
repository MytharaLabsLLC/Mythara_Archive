# Dual-Framing Quick Reference Card

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## 🎯 One-Page Developer Reference

### What is Dual-Framing?

A **presentation layer** that translates Mythara's mythic terminology into enterprise-safe language **without changing the engine**.

---

## 📊 Key Term Mappings

| Mythic | Industry | Use When |
|--------|----------|----------|
| Blessings Reservoir | Resonance Reservoir | Showing cumulative impact to non-theological audiences |
| Integrity Metric | Trust Index | Presenting compliance scores to executives |
| Expression Metric | Engagement Index | Reporting field rep performance to managers |
| Soul Encoding | Impact Vault | Explaining symbolic depth to investors |
| Legacy Reservoir | Continuity Index | Demonstrating sustainability to boards |
| Soul Cradle Operator | Resonance Operator | Describing decision-making integrity to auditors |
| Grace/Light | Optimal Performance | Framing positive outcomes for enterprise dashboards |
| Wilderness/Darkness | Challenge State | Describing difficult conditions without theological language |

---

## 🛠️ API Quick Start

### Default Behavior (Mythic)
```bash
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/reservoir/status
```

**Response:**
```json
{"blessings_reservoir": 145, "reservoir_score": 0.82}
```

### Industry Framing (Add `?frame=industry`)
```bash
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/reservoir/status?frame=industry
```

**Response:**
```json
{"resonance_reservoir": 145, "reservoir_score": 0.82}
```

---

## 📍 New Endpoints

### Get Dual-Framing Chart (Public)
```bash
curl http://localhost:8000/v1/dual-framing/chart
```

### Get Flow Diagram (Public)
```bash
curl http://localhost:8000/v1/dual-framing/flow
```

### Get Manager Dashboard
```bash
curl -H "Authorization: Bearer dev_test_key_001" \
  http://localhost:8000/v1/dual-framing/dashboard?frame=industry
```

---

## 🔧 Python Integration

```python
from dual_framing import translate_response, FramingMode

# Original mythic data
data = {
    "blessings_reservoir": 145,
    "integrity_metric": 0.95
}

# Translate to industry framing
industry_data = translate_response(data, FramingMode.INDUSTRY)
# Result: {"resonance_reservoir": 145, "trust_index": 0.95}
```

---

## ✅ What Changes

- ✅ **Key names** in API responses (e.g., `blessings_reservoir` → `resonance_reservoir`)
- ✅ **External documentation** uses industry-safe terminology

## ❌ What NEVER Changes

- ❌ Engine logic (formulas, calculations)
- ❌ SHA-256 hashes (computed on mythic terms)
- ❌ Database schemas (internal storage)
- ❌ Source code (core modules)
- ❌ Compliance status (no SOC 2/ISO 27001 certifications held; posture designed around HIPAA, SOC 2, GDPR frameworks)

---

## 📚 Full Documentation

1. **DUAL_FRAMING_CHART.md** — Complete term mappings table
2. **DUAL_FRAMING_GUIDE.md** — Comprehensive enterprise integration guide
3. **DUAL_FRAMING_FLOW_DIAGRAM.md** — System architecture visualization
4. **DUAL_FRAMING_INTEGRATION_SUMMARY.md** — Technical implementation details

---

## 🎓 When to Use Which Framing

| Audience | Framing | Why |
|----------|---------|-----|
| R&D / Engineering | Mythic | Preserves conceptual clarity |
| Theological Advisors | Mythic | Maintains biblical integrity |
| Enterprise Sales | Industry | Removes theological friction |
| Board Presentations | Industry | Speaks C-suite language |
| Compliance Auditors | Industry | Uses standard terminology |
| Internal Dashboards | Both | Toggle based on viewer |

---

## 💡 Quick Tips

1. **Default to Mythic** — Internal teams should use mythic terms for conceptual clarity
2. **Use `?frame=industry`** — Add this to any endpoint when showing data to external audiences
3. **Test Both** — Verify that industry framing preserves all data before presenting
4. **Audit Trails Intact** — SHA-256 hashes remain unchanged regardless of framing
5. **No Code Changes Needed** — Existing integrations work without modification

---

## 🚨 Common Pitfalls

❌ **DON'T** change internal database schemas to use industry terms  
✅ **DO** apply framing translation at API response layer only

❌ **DON'T** remove mythic terms from codebase  
✅ **DO** maintain mythic truth internally, translate externally

❌ **DON'T** mix framings in same response (confusing)  
✅ **DO** choose one framing mode per audience/dashboard

---

## 🔗 Related Files

- `core/source_proprietary/dual_framing.py` — Translation module source code
- `core/source_proprietary/main.py` — API endpoints with dual-framing support
- `README.md` — Updated with dual-framing quickstart section

---

## 📞 Questions?

**Email:** MytharaLabsLLC@yahoo.com  
**API Docs:** http://localhost:8000/api/docs (interactive)  
**Module Test:** `python core/source_proprietary/dual_framing.py`

---

**Remember:** Mythara's mythic soul is unchanged. Dual-framing simply gives you the language to bring that soul into boardrooms.

---

**Print this card for quick reference during enterprise demos!**
