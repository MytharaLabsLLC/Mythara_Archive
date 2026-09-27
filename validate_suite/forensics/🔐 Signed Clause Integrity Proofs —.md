# 🔐 Signed Clause Integrity Proofs — Mythara Engine

This document defines the schema for clause integrity proofs and records the
proofs that have been issued. **No proofs have been issued yet** — the table
below is the template each proof must fill. A clause may be marked Verified
only after its fingerprint hash has been recorded and its signature checked
against a registered signing key.

---

## 📜 Integrity Table

| Clause Name     | Version | Messenger ID | SHA-256 Fingerprint Hash | Timestamp (UTC) | Signature Status | Notes |
|-----------------|---------|--------------|--------------------------|-----------------|------------------|-------|
| Legacy_Seed     | v1.0    | —            | —                        | —               | ⏳ Not issued    | —     |
| Blessing_Arc    | v1.0    | —            | —                        | —               | ⏳ Not issued    | —     |
| Memory_Lock     | v1.0    | —            | —                        | —               | ⏳ Not issued    | —     |
| Judgment_Sigil  | v1.0    | —            | —                        | —               | ⏳ Not issued    | —     |
| Lineage_Lock    | v1.0    | —            | —                        | —               | ⏳ Not issued    | —     |

Each row, when filled, records a full 64-character SHA-256 fingerprint, the
UTC timestamp of signing, and the verifying messenger or key identity.
Placeholder hashes are not acceptable entries.

---

## 🧠 Notes

- A fingerprint must match the clause registry before a proof is recorded
- Signatures are validated against registered keys, not assertions
- Integrity proofs, once issued, support audit review and escrow packaging

A proof that has not been issued is simply absent from the record. Absence
proves nothing, and this document claims nothing beyond what is recorded.
