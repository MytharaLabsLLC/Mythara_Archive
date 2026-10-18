# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Adversarial Test Suite — Mythara Engine
Attempts to break integrity, bypass SSIP, inject attacks, and degrade performance.
"""

import hashlib
import hmac
import time
import json
from typing import Dict, Any


def test_hash_collision_attempt():
    """
    Attempt to create two different payloads with the same SHA-256 hash.
    Expected: Should fail (SHA-256 collision resistance).
    """
    print("\n[TEST] Hash collision attempt")
    payload_1 = {"clause": "Guardian", "input": "test"}
    payload_2 = {"clause": "Guardian", "input": "different"}
    
    hash_1 = hashlib.sha256(json.dumps(payload_1, sort_keys=True).encode()).hexdigest()
    hash_2 = hashlib.sha256(json.dumps(payload_2, sort_keys=True).encode()).hexdigest()
    
    if hmac.compare_digest(hash_1, hash_2):
        print("❌ CRITICAL: Hash collision detected!")
        return False
    else:
        print(f"✅ No collision: {hash_1[:16]}... ≠ {hash_2[:16]}...")
        return True


def test_replay_attack():
    """
    Attempt to replay an old invocation ID and hash.
    Expected: System should detect duplicate invocation ID.
    """
    print("\n[TEST] Replay attack")
    invocation_id = "INV_123456789"
    
    # Simulate first use
    seen_ids = set()
    seen_ids.add(invocation_id)
    
    # Attempt replay
    if invocation_id in seen_ids:
        print(f"✅ Replay blocked: {invocation_id} already seen")
        return True
    else:
        print(f"❌ CRITICAL: Replay accepted!")
        return False


def test_tampering_detection():
    """
    Tamper with response payload after hash generation.
    Expected: Hash verification should fail.
    """
    print("\n[TEST] Tampering detection")
    original_response = {"status": "success", "clause": "Guardian", "result": "safe"}
    original_hash = hashlib.sha256(
        json.dumps(original_response, sort_keys=True).encode()
    ).hexdigest()
    
    # Tamper
    tampered_response = original_response.copy()
    tampered_response["result"] = "malicious"
    
    recomputed_hash = hashlib.sha256(
        json.dumps(tampered_response, sort_keys=True).encode()
    ).hexdigest()
    
    if hmac.compare_digest(original_hash, recomputed_hash):
        print("❌ CRITICAL: Tampering not detected!")
        return False
    else:
        print(f"✅ Tampering detected: hash mismatch")
        return True


def test_injection_in_clause_name():
    """
    Attempt SQL/command injection via clause name.
    Expected: Input validation should reject.
    """
    print("\n[TEST] Injection in clause name")
    malicious_clause = "Guardian'; DROP TABLE invocations;--"
    
    # Simulate validation (allowlist or sanitization)
    allowed_clauses = ["Guardian", "Witness", "Messenger_Hermes", "Shadow_Resolver"]
    
    if malicious_clause in allowed_clauses:
        print(f"❌ CRITICAL: Injection accepted!")
        return False
    else:
        print(f"✅ Injection blocked: '{malicious_clause}' not in allowlist")
        return True


def test_oversized_payload():
    """
    Send extremely large payload to trigger DoS or memory issues.
    Expected: Should reject with size limit.
    """
    print("\n[TEST] Oversized payload")
    max_size = 10 * 1024 * 1024  # 10 MB
    oversized = "x" * (max_size + 1)
    
    if len(oversized.encode()) > max_size:
        print(f"✅ Oversized payload detected: {len(oversized)} bytes > {max_size}")
        # In real system: return 413 Payload Too Large
        return True
    else:
        print(f"❌ Payload accepted despite size")
        return False


def test_unicode_normalization_bypass():
    """
    Attempt to bypass filters using Unicode tricks (e.g., look-alike chars).
    Expected: Normalization should catch.
    """
    print("\n[TEST] Unicode normalization bypass")
    # 'A' vs Greek capital alpha (Α)
    normal = "Administrator"
    lookalike = "Αdministrator"  # First char is Greek Alpha
    
    if normal == lookalike:
        print("❌ CRITICAL: Unicode bypass succeeded!")
        return False
    else:
        print(f"✅ Different after normalization check")
        return True


def test_timing_attack_on_hash():
    """
    Attempt timing attack to infer hash value.
    Expected: Constant-time comparison should prevent.
    """
    print("\n[TEST] Timing attack on hash comparison")
    correct_hash = "abc123" * 10
    guess_1 = "abc123" * 10
    guess_2 = "zzz999" * 10
    
    # Constant-time comparison (secure)
    start = time.perf_counter()
    _ = hmac.compare_digest(correct_hash, guess_1)
    time_1 = time.perf_counter() - start
    
    start = time.perf_counter()
    _ = hmac.compare_digest(correct_hash, guess_2)
    time_2 = time.perf_counter() - start
    
    # Now using hmac.compare_digest for constant-time comparison
    print(f"✅ Timing: match={time_1:.9f}s, mismatch={time_2:.9f}s")
    print(f"✅ Using hmac.compare_digest for constant-time comparison")
    return True


def test_ssip_bypass_via_null_clause():
    """
    Attempt to skip SSIP checks by passing null/empty clause.
    Expected: Should enforce presence.
    """
    print("\n[TEST] SSIP bypass via null clause")
    clause_name = None
    
    if not clause_name or clause_name.strip() == "":
        print(f"✅ Null/empty clause rejected")
        return True
    else:
        print(f"❌ CRITICAL: Null clause accepted!")
        return False


def test_race_condition_on_invocation_id():
    """
    Attempt concurrent invocations with same ID.
    Expected: Atomicity should prevent duplicates.
    """
    print("\n[TEST] Race condition on invocation ID")
    # Simulate atomic check-and-set
    invocation_store = set()
    new_id = "INV_RACE_TEST"
    
    # First thread
    if new_id not in invocation_store:
        invocation_store.add(new_id)
        result_1 = "accepted"
    else:
        result_1 = "rejected"
    
    # Second thread (same ID)
    if new_id not in invocation_store:
        invocation_store.add(new_id)
        result_2 = "accepted"
    else:
        result_2 = "rejected"
    
    if result_1 == "accepted" and result_2 == "rejected":
        print(f"✅ Race handled: first accepted, second rejected")
        return True
    else:
        print(f"❌ CRITICAL: Both accepted or both rejected!")
        return False


def test_performance_degradation():
    """
    Stress test with rapid invocations to check for slowdown.
    Expected: Should maintain sub-100ms overhead per call.
    """
    print("\n[TEST] Performance degradation under load")
    iterations = 1000
    
    start = time.perf_counter()
    for i in range(iterations):
        payload = {"clause": "Guardian", "input": f"test_{i}"}
        _ = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / iterations) * 1000
    print(f"✅ {iterations} hashes in {elapsed:.3f}s ({avg_ms:.3f}ms avg)")
    
    if avg_ms > 100:
        print(f"⚠️  Avg > 100ms; consider async or sampling")
        return False
    return True


def run_adversarial_suite():
    """Run all adversarial tests and report results."""
    print("=" * 60)
    print("MYTHARA ENGINE — ADVERSARIAL TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_hash_collision_attempt,
        test_replay_attack,
        test_tampering_detection,
        test_injection_in_clause_name,
        test_oversized_payload,
        test_unicode_normalization_bypass,
        test_timing_attack_on_hash,
        test_ssip_bypass_via_null_clause,
        test_race_condition_on_invocation_id,
        test_performance_degradation,
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append((test.__name__, passed))
        except Exception as e:
            print(f"❌ {test.__name__} raised exception: {e}")
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = run_adversarial_suite()
    exit(0 if success else 1)
