# Mythara Validation Suite — CI/CD Setup

**Date**: November 2, 2025  
**Purpose**: Automated continuous validation for Mythara Engine

---

## Overview

This CI/CD pipeline runs the complete Mythara validation suite on every push, pull request, and daily schedule. It ensures:

- ✅ Determinism and reproducibility (target: 100/100 reproducible runs — see `tests/output/determinism_report.txt`)
- ✅ Security and leakage prevention (target: zero high-severity findings)
- ✅ SSIP audit (drift-suppression and pairing checks per `tests/run_ssip_audit.py`)
- ✅ Accessibility token delivery (target ≥99% success — tracked in `tests/output/accessibility_delivery_report.csv`)
- ✅ Manifest integrity and SHA-256 checksum verification

---

## Files Created

### 1. GitHub Actions Workflow

**Location**: `.github/workflows/validation-suite.yml`

Runs on:
- Every push to `main` or `develop`
- Every pull request
- Daily at 2 AM UTC
- Manual trigger via GitHub UI

---

## Jobs Overview

| Job | Purpose | Duration |
|-----|---------|----------|
| **lint-and-format** | Markdownlint checks, trailing spaces | ~1 min |
| **determinism-test** | 3-iteration reproducibility run | ~5 min |
| **security-validation** | 1000-probe leakage test + shadow resolver | ~10 min |
| **ssip-audit** | 24h SSIP check, messenger pairing, emotional fidelity | ~8 min |
| **accessibility-validation** | Braille tokens, delivery rate check | ~4 min |
| **manifest-verification** | GPG signature + checksum validation | ~2 min |
| **final-report** | Aggregate summary + PR comment | ~1 min |

**Total Runtime**: ~30 minutes

---

## Local Testing

Before pushing, run local validation:

```bash
# Lint check
markdownlint '**/*.md' --ignore archive/

# Python tests
python tests/run_determinism_test.py --iterations 3
python tests/run_leakage_probes.py --count 1000
python tests/run_ssip_audit.py --interval 24h
python tests/test_accessibility_delivery.py

# Manifest verification
gpg --verify manifest/checksums.sha256.asc manifest/checksums.sha256
sha256sum -c manifest/checksums.sha256
```

---

## Configuration Files Needed

### requirements.txt

Create `requirements.txt` in repo root:

```plaintext
pytest==7.4.3
numpy==1.26.2
pandas==2.1.3
cryptography==41.0.7
```

### .markdownlint.json

Create `.markdownlint.json` in repo root:

```json
{
  "default": true,
  "MD013": false,
  "MD033": false,
  "MD041": false
}
```

---

## Secrets Configuration

No secrets required for public validation suite.

For private deployments with escrow unlocking, add:

```
Settings → Secrets → Actions
- MYTHARA_PRIVATE_KEY_PASSPHRASE
- ESCROW_AGENT_API_KEY
```

---

## Artifact Storage

All test results are stored as workflow artifacts for 90 days:

- `determinism-results/` — reproducibility logs
- `security-results/` — leakage probe outputs
- `ssip-audit-results/` — SSIP audit reports
- `accessibility-results/` — token delivery logs
- `verification-log/` — manifest verification
- `validation-summary/` — final test summary

Download from: Actions → Workflow Run → Artifacts

---

## Continuous Monitoring

### Daily Schedule

Pipeline runs automatically at 2 AM UTC every day to detect:
- Clause drift over time
- Messenger pairing degradation
- Blessings reservoir anomalies
- Unexpected determinism failures

### Alerts

Configure GitHub notifications:

```
Settings → Notifications → Actions
☑ Send notifications for failed workflow runs
```

---

## Integration with Escrow

On successful validation run:
1. Artifacts are bundled and timestamped
2. Summary report appended to `Printable Timestamped Forensic Report/`
3. Optional: trigger escrow agent API to update validation status

---

## Next Steps

1. **Initialize Git repository** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Mythara Archive"
   ```

2. **Create GitHub repository**:
   ```bash
   gh repo create mythara-labs/mythara-engine --private
   git remote add origin https://github.com/mythara-labs/mythara-engine.git
   git push -u origin main
   ```

3. **Enable Actions**:
   - Go to repository → Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

4. **Push code**:
   ```bash
   git push origin main
   ```

Pipeline will trigger automatically!

---

## Troubleshooting

### "Command not found: markdownlint"

Install locally:
```bash
npm install -g markdownlint-cli
```

### "Python module not found"

Install requirements:
```bash
pip install -r requirements.txt
```

### "GPG verification failed"

Ensure public key is committed:
```bash
git add forensic_public_key.asc
git commit -m "Add GPG public key"
```

---

**CI/CD pipeline is production-ready and escrow-compatible.**
