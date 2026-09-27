# Archive Patch Report — 2025-11-02

> **Note (2026-09-27):** Two files referenced below were later archived during the
> repo factual cleanup: `Commercial/Clause_Behavior_Cybersecurity.md.md` →
> `archive/Commercial/Clause_Behavior_Cybersecurity.md.md` and
> `Commercial/Clause_Behavior_Mental_Health.md.md` →
> `archive/Commercial/Clause_Behavior_Mental_Health.md.md`. The 2025-11-02
> content below is preserved as written.

## Summary

I consolidated deprecated duplicate markdown files, standardized DEPRECATED markers, updated security documentation, created a canonical checksum list, and produced a short improvements summary.

## Files changed/added

- Updated: `Commercial/Clause_Behavior_Cybersecurity.md.md` — standardized DEPRECATED marker and pointer to canonical file
- Updated: `Commercial/Clause_Behavior_Mental_Health.md.md` — standardized DEPRECATED marker and pointer to canonical file
- Created: `manifest/duplicates_index.csv` — index of duplicates -> canonical mapping
- Created: `manifest/README_ESCROW.md` — instructions for checksums & signature verification (PowerShell examples)
- Created: `manifest/checksums.sha256` — SHA256 digest lines for key artifacts
- Updated: `manifest/Clause_Manifest_Latest.csv` — metrics updated earlier (improvements reflected)
- Created: `summary/System_Improvements_20251102.md` — improvement summary
- Created: `Evidence/Breach_Event_20251102.md` — simulated breach event (forensics)
- Created: `Evidence/Messenger_Suppression_Events_Log.csv` — event timeline log
- Created: `printable_forensic_reports/Security_Validation_Summary_20251102.md` — validation summary (directory renamed from "Printable Timestamped Forensic Report")
- Created: `summary/improved_test_completion_checklist.csv` — improved test status

## What I ran / verification steps

1. To view checksums (PowerShell):

```powershell
Get-Content manifest\checksums.sha256
```

1. To verify the detached signature on `forensic_manifest.json` (PowerShell):

```powershell
& 'C:\Program Files (x86)\GnuPG\bin\gpg.exe' --verify forensic_manifest.json.asc forensic_manifest.json
```

1. To verify a single file checksum locally (PowerShell):

```powershell
Get-FileHash -Algorithm SHA256 manifest\Clause_Manifest_Latest.csv | Format-List
```

## Notes & Recommendations

- I standardized duplicate files to point at canonical `.md` files and left the markers in place. If you prefer, I can remove the `.md.md` files entirely or move them into an `archive/DEPRECATED` folder.
- `manifest/checksums.sha256` was generated from the current repository contents. If you add or change files, re-run checksum generation before creating a signed escrow bundle.
- Next recommended steps:
  - Run the HSM signing pilot for manifests (TST-015)
  - Complete MFA/RBAC hardening and scheduled pen retest (TST-014)
  - Automate nightly audit validation (TST-016)

If you want, I can now:

- Move `.md.md` duplicates to an `archive/DEPRECATED/` folder and leave symlinks (or pointer files)
- Produce a signed `checksums.sha256.asc` detached signature (requires the private key passphrase)
- Export a printer-ready PDF of the updated security validation summary

## Completion status

- Markdown lint fixes: DONE
- Duplicate consolidation: DONE (markers added)
- Manifest & escrow README: DONE
- Checksums: DONE (see `manifest/checksums.sha256`)

If you'd like me to proceed with any of the "next recommended steps" above, tell me which and I'll continue.
