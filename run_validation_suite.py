#!/usr/bin/env python3
"""
Mythara Engine - Validation Suite Runner
Runs all validation tests in sequence.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
import shlex
import subprocess
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Run a command and return exit code."""
    print(f"\n{'=' * 60}")
    print(f"[TEST] {description}")
    print(f"{'=' * 60}\n")
    
    try:
        # No shell (CWE-78): split into argv list instead of shell=True.
        # A leading "python" is resolved to this interpreter so the
        # launcher works where only python3 exists.
        args = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
        if args and args[0] == "python":
            args[0] = sys.executable
        result = subprocess.run(args, shell=False, check=False)
        return result.returncode
    except Exception as e:
        print(f"[ERROR] running {description}: {e}")
        return 1


def main():
    """Run complete validation suite."""
    
    print("==> Mythara Engine - Validation Suite")
    print(f"Started: {datetime.utcnow().isoformat()}Z\n")
    
    # Ensure output directory exists
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # 1. Determinism Tests
    exit_code = run_command(
        "python tests/run_determinism_test.py --iterations 3",
        "Determinism & Reproducibility Tests"
    )
    results['determinism'] = exit_code == 0
    
    # 2. Security/Leakage Tests
    exit_code = run_command(
        "python tests/run_leakage_probes.py --count 1000",
        "Security & Leakage Probe Tests"
    )
    results['security'] = exit_code == 0
    
    # 3. SSIP Audit
    exit_code = run_command(
        "python tests/run_ssip_audit.py --interval 24h",
        "SSIP Integrity Audit"
    )
    results['ssip'] = exit_code == 0
    
    # 4. Accessibility Tests
    exit_code = run_command(
        "python tests/test_accessibility_delivery.py --count 100",
        "Accessibility Token Delivery Tests"
    )
    results['accessibility'] = exit_code == 0
    
    # 5. Adversarial/Security Tests
    exit_code = run_command(
        "python tests/run_adversarial_tests.py",
        "Adversarial Attack & Hardening Tests"
    )
    results['adversarial'] = exit_code == 0
    
    # Summary
    print(f"\n{'=' * 60}")
    print("VALIDATION SUITE SUMMARY")
    print(f"{'=' * 60}\n")
    
    print("Test Results:")
    print(f"  Determinism:    {'[PASS]' if results['determinism'] else '[FAIL]'}")
    print(f"  Security:       {'[PASS]' if results['security'] else '[FAIL]'}")
    print(f"  SSIP Audit:     {'[PASS]' if results['ssip'] else '[FAIL]'}")
    print(f"  Accessibility:  {'[PASS]' if results['accessibility'] else '[FAIL]'}")
    print(f"  Adversarial:    {'[PASS]' if results['adversarial'] else '[FAIL]'}")
    
    all_passed = all(results.values())
    
    print(f"\nOverall Status: {'[ALL TESTS PASSED]' if all_passed else '[SOME TESTS FAILED]'}")
    print(f"Completed: {datetime.utcnow().isoformat()}Z\n")
    
    print("Results saved to: tests/output/")
    print("   - determinism_report.txt")
    print("   - leakage_probe_log.csv")
    print("   - ssip_audit_report.md")
    print("   - accessibility_delivery_report.csv")
    print("   - adversarial_test_summary.txt (console output)\n")
    
    # Return exit code (0 if all passed, 1 if any failed)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
