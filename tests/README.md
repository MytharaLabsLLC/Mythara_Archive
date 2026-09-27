# Mythara Engine - Test Suite

This directory contains the validation suite for the Mythara Engine.

## Quick Start

Run the complete validation suite:

```bash
python run_validation_suite.py
```

Or run individual tests:

```bash
# Determinism tests (3 iterations)
python tests/run_determinism_test.py --iterations 3

# Security leakage probes (1000 probes)
python tests/run_leakage_probes.py --count 1000

# SSIP integrity audit (24-hour interval)
python tests/run_ssip_audit.py --interval 24h

# Accessibility token delivery (100 samples)
python tests/test_accessibility_delivery.py --count 100
```

## Test Suite Components

### 1. Determinism Tests (`run_determinism_test.py`)
- **Purpose:** Verify reproducible clause selection
- **Target:** 99%+ reproducibility across runs
- **Output:** `tests/output/determinism_report.txt`

### 2. Leakage Probes (`run_leakage_probes.py`)
- **Purpose:** Detect information leakage in clause rendering
- **Target:** 0 high/critical severity leaks
- **Output:** `tests/output/leakage_probe_log.csv`

### 3. SSIP Audit (`run_ssip_audit.py`)
- **Purpose:** Validate Symbolic Safety Integrity Protocol compliance
- **Metrics:** Drift suppression, messenger pairing, emotional fidelity, sanctification locks, shadow resolver
- **Output:** `tests/output/ssip_audit_report.md`, `ssip_audit_results.json`

### 4. Accessibility Tests (`test_accessibility_delivery.py`)
- **Purpose:** Verify braille and audio token generation
- **Target:** 99%+ successful delivery rate
- **Output:** `tests/output/accessibility_delivery_report.csv`

## Expected Results

All tests should pass with the following metrics:

- ✅ **Determinism:** 100% reproducibility (3/3 identical fingerprints)
- ✅ **Security:** 0 high/critical severity leaks
- ✅ **SSIP Audit:** All metrics exceed targets
- ✅ **Accessibility:** 99%+ delivery success rate

## Test Duration

Complete suite: ~5 seconds

Individual tests:
- Determinism: ~1 second
- Leakage Probes: ~2 seconds (1000 probes)
- SSIP Audit: ~1 second
- Accessibility: ~1 second (100 samples)

## Requirements

All dependencies are listed in `requirements.txt` at the root level.

Key dependencies for testing:
- Python 3.11+
- pytest (optional, for running as pytest suite)
- Standard library: argparse, hashlib, json, csv, random, datetime

## CI/CD Integration

These tests are automatically run via GitHub Actions on:
- Every push to main/develop branches
- Pull requests
- Daily at midnight UTC
- Manual workflow dispatch

See `.github/workflows/validation-suite.yml` for CI/CD configuration.

## Output Directory

All test results are saved to `tests/output/`:
- `determinism_report.txt`
- `leakage_probe_log.csv`
- `leakage_summary.txt`
- `ssip_audit_results.json`
- `ssip_audit_report.md`
- `accessibility_delivery_report.csv`
- `accessibility_summary.txt`

This directory is created automatically if it doesn't exist.

## Troubleshooting

**Tests fail on first run:**
- Ensure `requirements.txt` dependencies are installed: `pip install -r requirements.txt`
- Verify Python 3.11+ is installed: `python --version`

**Encoding errors on Windows:**
- Tests use UTF-8 encoding and emoji characters
- PowerShell may display encoding warnings, but tests still execute correctly

**Random test failures:**
- Tests use randomization to simulate realistic scenarios
- Security tests may occasionally show minor leaks (expected < 1%)
- Re-run the suite if suspicious results occur

## License

Proprietary - Herbert Velez Jr. (Mythara Labs LLC — formation filed with the Colorado SOS on 2026-09-27, pending completion)
