# README — Escrow & Manifest Signing

This folder contains the clause manifest and artifacts required for escrow, reproducibility verification, and legal transfer.

## Key files

- `Clause_Manifest_Latest.csv` — canonical manifest listing clauses and status
- `duplicates_index.csv` — index of duplicate/deprecated files in the repo
- `../forensic_public_key.asc` — ASCII-armored public key used to verify signatures (repository root)
- `../forensic_manifest.json.asc` — ASCII-armored detached signature for `forensic_manifest.json` (repository root)

## Signing and verification (PowerShell examples)

Generate a checksum for the manifest (PowerShell):

```powershell
Get-FileHash -Algorithm SHA256 manifest\Clause_Manifest_Latest.csv | Format-List
```

Verify an ASCII-armored detached signature (adjust gpg path if needed):

```powershell
& 'C:\Program Files (x86)\GnuPG\bin\gpg.exe' --verify forensic_manifest.json.asc forensic_manifest.json
```

Export the public key (if you need to share it):

```powershell
& 'C:\Program Files (x86)\GnuPG\bin\gpg.exe' --armor --export 'Mythara.Engine@yahoo.com' > forensic_public_key.asc
```

## Notes

- Always include `forensic_public_key.asc` with any escrow transfer so recipients can verify signatures.
- Ensure `Clause_Manifest_Latest.csv` is the version referenced in any escrow package and that all checksums are recorded.
- For full escrow packaging, produce a canonical checksums file (sorted lexicographically) named `checksums.sha256` with entries like:

```text
<sha256>  relative/path/to/file
```

The `checksums.sha256` file is the canonical checksums record for the current repository artifacts. It can be regenerated and re-signed after any content change, following `SIGNING_INSTRUCTIONS.md` — note that editing any listed file invalidates its checksum and signature until that is done.
