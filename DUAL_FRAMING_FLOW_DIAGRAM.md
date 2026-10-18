# Mythara Engine Dual-Framing Flow Diagram

**Copyright © 2026 Mythara Labs LLC. All rights reserved.**

---

## System Architecture with Dual-Framing Overlay

```
╔═════════════════════════════════════════════════════════════════════════╗
║                    MYTHARA ENGINE DUAL-FRAMING FLOW                     ║
╚═════════════════════════════════════════════════════════════════════════╝


┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│              System of Record (Any CRM / Field Platform)                │
│                                                                         │
│  Examples: Salesforce, HubSpot, Microsoft Dynamics, Custom CRM         │
│  Data: Sales metrics, compliance scores, KPIs, field rep performance   │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ API Integration
                                 │ (REST/GraphQL)
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                      MYTHARA ENGINE OVERLAY LAYER                       │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │            Dual-Framing Translation Module                        │ │
│  │         (core/source_proprietary/dual_framing.py)                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────┐      ┌──────────────────────────────┐   │
│  │    MYTHIC TRUTH          │      │   INDUSTRY-SAFE OVERLAY      │   │
│  │    (Internal)            │  →   │   (External)                 │   │
│  ├──────────────────────────┤      ├──────────────────────────────┤   │
│  │ Blessings Reservoir      │  →   │ Resonance Reservoir          │   │
│  │ Integrity Metric         │  →   │ Trust Index                  │   │
│  │ Expression Metric        │  →   │ Engagement Index             │   │
│  │ Soul Encoding            │  →   │ Impact Vault                 │   │
│  │ Legacy Reservoir         │  →   │ Continuity Index             │   │
│  │ SoulCradle Operator     │  →   │ Resonance Operator           │   │
│  │ Trial Entity             │  →   │ Challenge Vector             │   │
│  │ Grace/Light              │  →   │ Optimal Performance          │   │
│  │ Wilderness/Darkness      │  →   │ Challenge State              │   │
│  │ Divine Drift Suppression │  →   │ Compliance Stability         │   │
│  │ Messenger Pairing        │  →   │ Communication Alignment      │   │
│  │ Emotional Fidelity       │  →   │ Sentiment Accuracy           │   │
│  └──────────────────────────┘      └──────────────────────────────┘   │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  Framing Mode Toggle:                                             │ │
│  │  • ?frame=mythic  (default) — Use internal truth                  │ │
│  │  • ?frame=industry          — Use enterprise-safe overlay         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  Integrity Guarantees:                                            │ │
│  │  ✓ SHA-256 hashes computed on mythic terms (audit trail)          │ │
│  │  ✓ Engine logic unchanged (calculations identical)                │ │
│  │  ✓ Database schemas use mythic keys (internal storage)            │ │
│  │  ✓ Compliance posture unchanged (no SOC 2/ISO 27001 certs held)   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ Formatted Response
                                 │ (JSON with selected framing)
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         MANAGER DASHBOARDS                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  KPIs from System of Record        Resonance Metrics from Mythara │ │
│  │  ────────────────────────────────────────────────────────────────  │ │
│  │  • Sales Conversion: 12.5%         • Resonance Reservoir: 145    │ │
│  │  • Avg. Deal Size: $4,200          • Trust Index: 0.95           │ │
│  │  • Time to Close: 18 days          • Engagement Index: 0.88      │ │
│  │  • Customer Sat.: 4.7/5            • Continuity Index: 145       │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ✓ Compliance intact — Mythara doesn't replace existing systems       │
│  ✓ Workflows unchanged — Mythara overlays on top of current data      │
│  ✓ Symbolic depth added — Managers see resonance alongside numbers    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  Toggle View:                                                     │ │
│  │  [ Mythic Truth ]  [ Industry Overlay ] ← Manager chooses framing │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════

                          KEY INTEGRATION POINTS

═══════════════════════════════════════════════════════════════════════════

1. SYSTEM OF RECORD
   ├─ No changes required to existing CRM/field platform
   ├─ Mythara reads data via standard API integration
   └─ KPIs continue to flow as normal

2. MYTHARA ENGINE OVERLAY
   ├─ Computes symbolic metrics (Blessings Reservoir, Soul Proportion, etc.)
   ├─ Generates SHA-256 integrity hashes for audit trails
   ├─ Applies dual-framing translation based on audience
   └─ Returns formatted response with selected terminology

3. MANAGER DASHBOARDS
   ├─ Display KPIs + resonance metrics side-by-side
   ├─ Allow toggle between mythic and industry framing
   ├─ Maintain compliance (no PHI, no workflow disruption)
   └─ Provide symbolic depth without theological friction

═══════════════════════════════════════════════════════════════════════════

                           API ENDPOINT EXAMPLES

═══════════════════════════════════════════════════════════════════════════

GET /v1/reservoir/status?frame=mythic
  → { "blessings_reservoir": 145, "reservoir_score": 0.82 }

GET /v1/reservoir/status?frame=industry
  → { "resonance_reservoir": 145, "reservoir_score": 0.82 }

GET /v1/dual-framing/dashboard?frame=industry
  → {
      "resonance_metrics": { "resonance_reservoir": 145, ... },
      "kpis": { ... },
      "framing_mode": "industry"
    }

GET /v1/dual-framing/chart
  → Full mythic-to-industry mapping chart (public endpoint)

GET /v1/dual-framing/flow
  → This flow diagram as ASCII text (public endpoint)

═══════════════════════════════════════════════════════════════════════════

                              POSITIONING LINE

═══════════════════════════════════════════════════════════════════════════

"Mythara Engine encodes resonance through mythic terms like the Blessings
Reservoir. For enterprise audiences, we present these as overlays —
Resonance Reservoir, Trust Index, Engagement Index — so managers can see
symbolic depth alongside KPIs without disrupting compliance."

═══════════════════════════════════════════════════════════════════════════
```

---

## Use This Diagram For:

1. **Enterprise Sales**: Show how Mythara overlays on existing CRM systems without disrupting workflows
2. **Board Presentations**: Demonstrate enterprise-safe terminology while preserving engine integrity
3. **Investor Pitch**: Explain translation layer as competitive differentiation
4. **Engineering Teams**: Clarify integration architecture and API endpoints
5. **Compliance Auditors**: Show that underlying logic and audit trails remain unchanged

---

## Files to Reference:

- **Technical Details**: `core/source_proprietary/dual_framing.py`
- **Comprehensive Guide**: `DUAL_FRAMING_GUIDE.md`
- **Integration Summary**: `DUAL_FRAMING_INTEGRATION_SUMMARY.md`
- **API Documentation**: `http://localhost:8000/api/docs` (after starting server)

---

**Mythara Engine preserves its mythic soul while speaking the language of enterprise.**
