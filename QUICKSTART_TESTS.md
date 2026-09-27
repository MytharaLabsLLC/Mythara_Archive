# 🚀 QUICK START - Run Mythara Tests

## One Command to Rule Them All

```bash
python run_validation_suite.py
```

**Duration:** ~5 seconds  
**Output:** Console summary + 7 report files in `tests/output/`

---

## Expected Results

```
✅ Determinism:    PASS (100% reproducibility)
✅ Security:       PASS (0 critical leaks)  
✅ SSIP Audit:     PASS (All metrics exceed targets)
✅ Accessibility:  PASS (99%+ delivery rate)

Overall Status: ✅ ALL TESTS PASSED
```

---

## Installation (First Time Only)

```bash
pip install -r requirements.txt
```

---

## Individual Tests (Optional)

```bash
# Determinism only (~1 sec)
python tests/run_determinism_test.py

# Security only (~2 sec)  
python tests/run_leakage_probes.py

# SSIP only (~1 sec)
python tests/run_ssip_audit.py

# Accessibility only (~1 sec)
python tests/test_accessibility_delivery.py
```

---

## Docker

```bash
docker build -t mythara-engine:v1.0.0 .
docker run --rm mythara-engine:v1.0.0
```

---

## Troubleshooting

**"No module named pytest"**  
→ Run: `pip install -r requirements.txt`

**Tests fail randomly**  
→ Normal (uses randomization). Re-run to verify.

**Encoding errors on Windows**  
→ Ignore emoji warnings. Tests still execute correctly.

---

## More Info

- Full documentation: `tests/README.md`
- CI/CD workflow: `.github/workflows/validation-suite.yml`
- Test results: `tests/output/`

---

**Mythara Labs LLC (formation filing attempted with the Colorado SOS on 2026-09-27 — not confirmed; not formed)** | November 2025
