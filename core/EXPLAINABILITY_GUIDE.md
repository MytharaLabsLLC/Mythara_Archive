# EXPLAINABILITY_GUIDE.md

**Prepared by:** Herbert Velez Jr.  
**Manifest Ref:** ME-archive-0001  
**Date:** 2025-10-30

---

## Overview

This guide describes how Mythara constructs human-facing explanations, the internal scaffolds that produce them, scoring metrics used to evaluate explanation quality, and verification steps for auditors. Explanations are designed to be traceable, auditable, and minimally revealing of redacted internals while maximizing clarity, actionability, and fairness.

---

## Architecture (high level)

- Perception layer ingests input (text, gestures, language) and emits canonical observables (gesture_ids, language, confidence scores).  
- Clause selector maps observables to candidate clause_ids and computes harmonization_status and br_inflow estimates.  
- Renderer consumes selected clause_id, br_state, and renderer prompt templates to produce explanation_text and output_text.  
- Audit chain embeds manifest_ref, prompt_hash, clause_id, and timestamp with each explanation for traceability.

Files referenced in archive:
- Evidence/prompt_templates/perception_prompt_v1.txt (REDACTED)
- Evidence/prompt_templates/renderer_prompt_v1.txt (REDACTED)
- manifest/RELEASE_MANIFEST.json
- tests/explainability_ratings.csv

---

## Explanation Components

Each explanation produced by Mythara contains the following fields (JSON schema excerpt):

```json
{
  "explanation_id": "string",
  "clause_id": "string",
  "explanation_text": "string",
  "rationale": "string",
  "observables": {
    "gesture_ids": ["string"],
    "br_inflow": "number",
    "harmonization_status": "string",
    "confidence": "number"
  },
  "audit_chain": {
    "manifest_ref": "string",
    "prompt_hash": "string",
    "timestamp": "string"
  }
}
```

- explanation_text: The primary human-facing explanation (concise, instructive).  
- rationale: Short internal rationale summarizing why clause was chosen (structured, limited detail).  
- observables: Key signals used to select the clause; these are safe to expose and support auditability.  
- audit_chain: Signed references for reproducibility.

---

## Rules for Construction

1. Minimal necessary disclosure: Explanations reveal observables and rationale but never raw redacted prompt text or proprietary algorithmic internals.  
2. Safety-first: If any safety predicate triggers, explanation_text uses the pre-approved fallback clause and sets fallback_triggered=true in observables.  
3. Accessibility-first: Explanations are produced in plain text and mapped to accessibility tokens (braille/audio IDs) when requested.  
4. Locale and tone: Explanations respect the requested language and a configurable tone parameter (e.g., neutral, empathetic, concise).  
5. Determinism constraints: Given identical observables and the same prompt_hash, the renderer should produce repeatable explanation_text within the accepted determinism variance.

---

## Scoring Metrics

Mythara uses five core metrics to quantify explanation quality. Scores are aggregated into an Explainability Index (0–100).

- Clarity (0–25): Measured by human rater agreement on “easily understood” using a 1–5 scale; normalized to 25 points.  
- Relevance (0–20): Degree to which explanation addresses the user’s intent; raters score 1–5, normalized.  
- Actionability (0–20): Whether the explanation specifies next steps or outcomes; measured via checklist pass/fail by raters.  
- Safety Alignment (0–20): Correct application of safety fallback and lack of unsafe content; binary checks and raters.  
- Auditability (0–15): Presence and correctness of audit_chain fields, prompt_hash match, and manifest_ref consistency.

Explainability Index = Clarity + Relevance + Actionability + Safety Alignment + Auditability (max 100).

---

## Rater Protocol

- Panel composition: minimum 5 raters per evaluation run, diverse in language and domain expertise.  
- Dataset: 200 incidents (baseline vs. explanation overlay) per evaluation round.  
- Rating interface: blind A/B comparison, randomized ordering, 1–5 Likert scales for clarity and relevance; binary for actionability and safety.  
- Inter-rater reliability: compute Krippendorff’s alpha; target ≥0.75. Results stored in tests/explainability_ratings.csv.txt.

CSV columns (example):
- incident_id, rater_id, baseline_clarity, mythara_clarity, baseline_relevance, mythara_relevance, actionability_pass, safety_pass, notes

---

## Automated Quality Checks

- Prompt hash verification: confirm renderer prompt_hash matches prompt_hashes_manifest.json.  
- Determinism check: run renderer 3 times on the same input; compute token-level similarity and allowable divergence threshold (configured in determinism_report.txt).  
- Grammar and readability: automated Flesch–Kincaid readability score; flag outputs outside configured range.  
- Safety check: run explanation_text through the safety corpus validator; any flagged output triggers immediate remediation and log entry.

Commands (examples):

```bash
# verify prompt hash
sha256sum Evidence/prompt_templates/renderer_prompt_v1.txt

# determinism runs
python tools/run_renderer_repeat.py --input tests/sample_incident.json --runs 3

# readability
python tools/readability_check.py --file outputs/explanation_123.txt
```

---

## Accessibility Mapping

- For each explanation_text, the system generates:
  - braille_token_id (maps to tactile encoding pipeline)
  - audio_template_id (maps to TTS templates)
- Accessibility delivery is validated in the Accessibility Delivery Test with acceptance threshold ≥99% successful token generation and delivery.

Output mapping fields:
- braille_token_id: string
- audio_template_id: string
- accessibility_delivery_status: success|failure

---

## Audit and Archive Procedures

- Every explanation must include the audit_chain block before being stored in logs/ or emitted to clients.  
- Audit logs are append-only, hashed, and listed in manifest/checksums.sha256.  
- Sample verification workflow for auditors:

1. Verify checksums and PGP signatures:
   - gpg --verify manifest/checksums.sha256.asc checksums.sha256  
   - sha256sum -c manifest/checksums.sha256

2. Select random explanations and confirm:
   - audit_chain.manifest_ref matches RELEASE_MANIFEST.json.manifest_id  
   - prompt_hash listed in prompt_hashes_manifest.json  
   - clause_id resolves via GET /clause/{clause_id} metadata

3. Re-run renderer with escrowed prompt templates (if escrow release conditions met) and compare outputs to stored canonical outputs.

---

## Common Failure Modes and Remediation

- Prompt hash mismatch: flag incident, mark Prompt Drift Detection test fail, and suspend renderer until investigation.  
- Low clarity score: trigger explainability uplift pipeline (tuning renderer prompts and re-running determinism tests).  
- Safety fallback not triggered when expected: isolate incident, run shadow resolver activation test, and record remediation in shadow_resolver_report.txt.  
- Accessibility token generation failure: retry with normalized input; if persistent, open ticket and log to accessibility_fallback_log.txt.

---

## Test Artifacts and Where They Live

- tests/explainability_ratings.csv.txt — human rating data and aggregated scores  
- tests/output/determinism_report.txt — determinism run results and thresholds  
- tests/output/accessibility_delivery_report.csv — braille/audio token generation logs  
- manifest/RELEASE_MANIFEST.json — audit reference for all artifacts

---

## Minimal Examples

1) Example explanation (JSON):

```json
{
  "explanation_id": "ex_0001",
  "clause_id": "clause_045",
  "explanation_text": "I’m offering a short, safe response because you indicated distress. If you’d like, I can connect you to resources or rephrase.",
  "rationale": "Detected gesture: gesture_sad; br_inflow=0.78; chosen clause prioritizes safety and empathy.",
  "observables": {
    "gesture_ids": ["gesture_sad"],
    "br_inflow": 0.78,
    "harmonization_status": "stable",
    "confidence": 0.92
  },
  "audit_chain": {
    "manifest_ref": "ME-archive-0001",
    "prompt_hash": "sha256:def456...",
    "timestamp": "2025-10-30T20:15:00Z"
  }
}
```

2) Example rationale redaction guidance:
- Rationale may include high-level detected signals and quantitative br_inflow but must not include raw redacted prompt fragments or implementation steps.

---

## Governance and Versioning

- Any change to explanation scaffolds or scoring thresholds must be recorded in manifest/RELEASE_MANIFEST.json with new manifest_id and signed.  
- Prompt template versions must be recorded in prompt_hashes_manifest.json.  
- Major semantic changes require a new explainability evaluation run and an updated verification_report.txt.

---

## Closing Notes

This guide balances transparency for auditors and customers with necessary redaction for proprietary elements. For escalation, use the procedures in README_ESCROW.md and reference the audit_chain fields for reproducible verification.

---