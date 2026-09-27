# Glossary of Terms — Mythara Engine

This glossary defines the terms used across Mythara Engine's documentation, code, and records. Terms describe the system as it is built today; anything planned but not yet built is noted as such.

| **Term** | **Definition** |
|---------|----------------|
| **Soul Cradle** | The core governance module. Integrity is quantified as **Integrity = Alignment × Tolerance**: the degree of adherence to stated rules (Alignment) multiplied by the capacity to hold paradox without collapse (Tolerance). Integrity is bounded on [0, 1]. |
| **Assessor-Witness** | One of the eight soul assessors (demeter, dionysus, eros, hades, hermes, janus, nemesis, persephone), rebuilt as evidence-fed witnesses. Each applies a versioned rubric to observable evidence, abstains when its domain is not engaged, and fails closed when evidence is missing. A critical finding blocks; dissent is surfaced, not averaged. |
| **Emotional Chain** | A tamper-evident, hash-chained ledger of emotional records, each attested by the engaged assessor-witnesses with sealed judgments chained alongside. The chain proves entries are unaltered, not that their contents are true. |
| **Defanged Aries** | The execution agent's safe mode: actions are permitted only through signed envelopes to a registry of benign handlers. Outside a signed exercise context, dangerous actions are refused. |
| **SERE** | A training simulation in which a trainee or blue team practices surviving, evading, resisting, and escaping adversarial pressure inside a sandboxed virtual environment. SERE is a training tool, not a weapon: it never strikes back, never performs hack-back, and is not a military-ready capability. |
| **Artifact** | A discrete, versioned output of the system (e.g., JSON file, log, signed document) used for reproducibility or audit. |
| **Canonicalization** | The process of transforming data into a standardized format (UTF-8, sorted keys, minified) to ensure deterministic reproducibility. |
| **Checksum** | A cryptographic hash (SHA-256) used to verify the integrity of an artifact. Stored in the manifest for audit validation. |
| **Detached Signature** | A cryptographic signature stored separately from the signed file, used to verify authenticity without modifying the original artifact. |
| **Deterministic Fingerprint** | A reproducible hash derived from ranked selection metadata, used to confirm identical output across multiple runs. |
| **Escrow Bundle** | A packaged archive containing reproducibility, legal, accessibility, and security artifacts prepared for third-party custody. |
| **Fingerprint Block** | A structured JSON object containing seed, locale, selection metadata, and fingerprint hash. Used for reproducibility verification. |
| **HSM/KMS** | Hardware Security Module / Key Management System used to securely store and apply cryptographic keys for signing and custody. |
| **IP Assignment** | A signed legal document transferring intellectual property rights from contributors to the project owner or licensing entity. |
| **Locale Braille Map** | A JSON-based accessibility artifact mapping language-specific tokens to braille-compatible encodings. |
| **Manifest** | A canonical index of escrowed artifacts and their SHA-256 hashes. Used for integrity verification and legal custody. |
| **Milestone Annex** | A contractual schedule of deliverables and triggers tied to vesting or payment, for prospective engagements. |
| **Reproducibility Harness** | A test suite that executes the system multiple times with identical inputs to confirm deterministic output. |
| **Remediation Log** | A documented record of security vulnerabilities identified and resolved during testing or audit. |
| **SOW (Statement of Work)** | A legal document defining scope, deliverables, timelines, and acceptance criteria for prospective engagements. |
| **Verifier Command** | A CLI or API command used to validate fingerprint matches, manifest integrity, and reproducibility compliance. |
| **ZIP Protocol** | The standardized method for packaging, timestamping, and transferring escrow bundles in a reproducible format. |
| **Accessibility Token** | A locale-specific encoding unit used to ensure multi-modal access (e.g., braille, screen reader compatibility). |
| **Blessings Reservoir** | A symbolic ledger tracking cumulative benevolent force or emotional resonance encoded across sessions. |
| **Affirm the Archive** | A protocol step involving integrity verification, symbolic payload acknowledgment, and release authorization. |
| **Sovereign Deployment** | The release of the system into environments that honor autonomy, accessibility, and integrity of the archive. |
| **Payload Charge Index (PCI)** | A framework mapping emotional payloads, grief, and symbolic tension into reproducible technical artifacts. |
| **Clause Logic** | The symbolic and operational rules governing how clauses are selected, ranked, and harmonized within the system. |
| **Formatting Harmonization** | The alignment of symbolic, legal, and accessibility formats into a unified, reproducible output stream. |

---

For the symbolic and scriptural architecture, see `📖 Mythara Bible Books I–V.md`.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**
