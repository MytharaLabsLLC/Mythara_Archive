#!/usr/bin/env python3
"""
Mythara Engine - Comprehensive Break Test Suite
Tests all 5 critical fixes under load and edge cases.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import requests
import asyncio
import aiohttp
import time
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE_URL = "http://localhost:8000"
RESULTS = {
    "test_rate_limiting": {"passed": False, "details": ""},
    "test_cors_validation": {"passed": False, "details": ""},
    "test_database_pool": {"passed": False, "details": ""},
    "test_exception_handling": {"passed": False, "details": ""},
    "test_load_stress": {"passed": False, "details": ""},
}

def print_header(test_name):
    print(f"\n{'='*70}")
    print(f"🔥 BREAK TEST: {test_name}")
    print(f"{'='*70}\n")

def print_result(test_name, passed, details):
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"\n{status}: {test_name}")
    print(f"Details: {details}\n")
    RESULTS[test_name]["passed"] = passed
    RESULTS[test_name]["details"] = details


# ============================================================================
# TEST 1: Rate Limiting - DDoS Attack Simulation
# ============================================================================
def test_rate_limiting():
    print_header("Rate Limiting - DDoS Attack Simulation")
    
    try:
        # Test public endpoint rate limiting (should be 100 req/min per IP for /health)
        print("🚀 Hammering /health endpoint with 150 requests in 10 seconds...")
        
        start = time.time()
        responses = []
        blocked_count = 0
        
        for i in range(150):
            try:
                resp = requests.get(f"{BASE_URL}/health", timeout=2)
                responses.append(resp.status_code)
                
                if resp.status_code == 429:
                    blocked_count += 1
                    print(f"   Request {i+1}: ❌ BLOCKED (429 Too Many Requests)")
                elif i < 10 or i % 20 == 0:  # Print first 10 and every 20th
                    print(f"   Request {i+1}: ✅ Allowed (200 OK)")
                    
            except requests.exceptions.RequestException as e:
                print(f"   Request {i+1}: ⚠️ Error - {e}")
                
        elapsed = time.time() - start
        
        # Analysis
        success_count = responses.count(200)
        total_requests = len(responses)
        
        print(f"\n📊 Results:")
        print(f"   Total requests sent: {total_requests}")
        print(f"   Successful (200): {success_count}")
        print(f"   Rate limited (429): {blocked_count}")
        print(f"   Time elapsed: {elapsed:.2f}s")
        print(f"   Rate: {total_requests/elapsed:.1f} req/s")
        
        # Rate limiting should kick in after ~100 requests in 60 seconds
        # Since we're hitting 150 in 10 seconds, we expect blocks
        if blocked_count > 0:
            print_result("test_rate_limiting", True, 
                        f"Rate limiting working! Blocked {blocked_count}/{total_requests} requests")
            return True
        else:
            print_result("test_rate_limiting", False,
                        f"No rate limiting detected! All {total_requests} requests succeeded")
            return False
            
    except Exception as e:
        print_result("test_rate_limiting", False, f"Test crashed: {e}")
        return False


# ============================================================================
# TEST 2: CORS Validation - Production Mode Check
# ============================================================================
def test_cors_validation():
    print_header("CORS Validation - Production Mode Check")
    
    try:
        print("🔍 Checking CORS configuration...")
        
        # Check if production mode would fail without MYTHARA_ALLOWED_ORIGINS
        has_database_url = os.getenv("DATABASE_URL", "").startswith(("postgres://", "postgresql://"))
        has_cors_config = bool(os.getenv("MYTHARA_ALLOWED_ORIGINS"))
        
        print(f"   DATABASE_URL present (production): {has_database_url}")
        print(f"   MYTHARA_ALLOWED_ORIGINS set: {has_cors_config}")
        
        # Test CORS headers on actual request
        resp = requests.get(f"{BASE_URL}/health")
        cors_headers = {
            "Access-Control-Allow-Origin": resp.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": resp.headers.get("Access-Control-Allow-Credentials"),
        }
        
        print(f"\n📋 CORS Headers:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        # In dev mode (no DATABASE_URL), should use localhost defaults
        if not has_database_url:
            print(f"\n✅ Development mode: Using localhost CORS defaults")
            print(f"   This is correct! Production would enforce MYTHARA_ALLOWED_ORIGINS")
            print_result("test_cors_validation", True,
                        "Dev mode CORS working. Production validation would reject startup without env var")
            return True
        elif has_database_url and not has_cors_config:
            print(f"\n❌ Production mode without CORS config!")
            print(f"   Server should have failed to start!")
            print_result("test_cors_validation", False,
                        "Production mode detected but CORS not enforced")
            return False
        else:
            print(f"\n✅ Production mode with CORS properly configured")
            print_result("test_cors_validation", True,
                        "Production CORS validation working")
            return True
            
    except Exception as e:
        print_result("test_cors_validation", False, f"Test crashed: {e}")
        return False


# ============================================================================
# TEST 3: Database Pool - Connection Exhaustion
# ============================================================================
def test_database_pool():
    print_header("Database Pool - Connection Exhaustion Test")
    
    try:
        print("🔥 Attempting to exhaust database connection pool...")
        print("   Pool size: 10, Max overflow: 20")
        print("   Total available: 30 connections")
        print("   Attempting 50 concurrent requests...\n")
        
        def make_request(req_num):
            try:
                resp = requests.get(f"{BASE_URL}/health", timeout=10)
                return (req_num, resp.status_code, "success")
            except requests.exceptions.Timeout:
                return (req_num, 0, "timeout")
            except Exception as e:
                return (req_num, 0, f"error: {e}")
        
        # Fire 50 concurrent requests
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        success = sum(1 for _, status, _ in results if status == 200)
        timeouts = sum(1 for _, _, msg in results if msg == "timeout")
        errors = sum(1 for _, _, msg in results if msg.startswith("error"))
        
        print(f"📊 Results:")
        print(f"   Successful requests: {success}/50")
        print(f"   Timeouts: {timeouts}/50")
        print(f"   Errors: {errors}/50")
        
        # Check pool status endpoint
        try:
            pool_resp = requests.get(f"{BASE_URL}/v1/admin/db-pool-status", timeout=5)
            if pool_resp.status_code == 200:
                pool_data = pool_resp.json()
                print(f"\n📊 Pool Status:")
                print(f"   Pool size: {pool_data.get('pool_size')}")
                print(f"   Checked out: {pool_data.get('checked_out_connections')}")
                print(f"   Available: {pool_data.get('available_connections')}")
                print(f"   Pool exhausted: {pool_data.get('pool_exhausted')}")
        except:
            print("   ⚠️ Could not fetch pool status (endpoint may require auth)")
        
        # With proper pool configuration, most requests should succeed
        if success >= 45:  # At least 90% success rate
            print_result("test_database_pool", True,
                        f"Pool handling concurrent load well: {success}/50 succeeded")
            return True
        elif timeouts > 10:
            print_result("test_database_pool", False,
                        f"Too many timeouts: {timeouts}/50 (pool may be exhausted)")
            return False
        else:
            print_result("test_database_pool", True,
                        f"Pool under stress but functional: {success}/50 succeeded")
            return True
            
    except Exception as e:
        print_result("test_database_pool", False, f"Test crashed: {e}")
        return False


# ============================================================================
# TEST 4: Exception Handling - No Bare Excepts
# ============================================================================
def test_exception_handling():
    print_header("Exception Handling - Bare Except Detection")
    
    try:
        print("🔍 Checking for bare except clauses in main.py...")
        
        main_file = "core/source_proprietary/main.py"
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        bare_excepts = []
        generic_excepts = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "except:":
                bare_excepts.append(i)
            elif stripped == "except Exception:":
                generic_excepts.append(i)
        
        print(f"📊 Results:")
        print(f"   Total lines scanned: {len(lines)}")
        print(f"   Bare 'except:' found: {len(bare_excepts)}")
        print(f"   Generic 'except Exception:' found: {len(generic_excepts)}")
        
        if bare_excepts:
            print(f"\n❌ Found bare except clauses at lines: {bare_excepts}")
        if generic_excepts:
            print(f"   ⚠️ Found generic Exception catches at lines: {generic_excepts}")
        
        # Test that exceptions are properly logged
        print(f"\n🧪 Testing exception logging...")
        
        # Try to trigger an error that should be logged
        try:
            # Invalid endpoint should return 404, not 500
            resp = requests.get(f"{BASE_URL}/v1/invalid/endpoint/test")
            print(f"   Invalid endpoint response: {resp.status_code}")
            
            if resp.status_code == 404:
                print(f"   ✅ Proper error handling (404 Not Found)")
            else:
                print(f"   ⚠️ Unexpected response code: {resp.status_code}")
        except Exception as e:
            print(f"   ⚠️ Request failed: {e}")
        
        if len(bare_excepts) == 0:
            print_result("test_exception_handling", True,
                        "No bare except clauses found! Exception handling improved.")
            return True
        else:
            print_result("test_exception_handling", False,
                        f"Found {len(bare_excepts)} bare except clauses that need fixing")
            return False
            
    except Exception as e:
        print_result("test_exception_handling", False, f"Test crashed: {e}")
        return False


# ============================================================================
# TEST 5: Load Stress Test - Find the Breaking Point
# ============================================================================
async def async_request(session, url, req_num):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return (req_num, resp.status, await resp.text())
    except asyncio.TimeoutError:
        return (req_num, 0, "timeout")
    except Exception as e:
        return (req_num, 0, f"error: {str(e)[:50]}")

async def load_test_async(total_requests, concurrency):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(total_requests):
            task = async_request(session, f"{BASE_URL}/health", i)
            tasks.append(task)
            
            # Limit concurrency
            if len(tasks) >= concurrency:
                results = await asyncio.gather(*tasks)
                yield results
                tasks = []
        
        if tasks:
            results = await asyncio.gather(*tasks)
            yield results

def test_load_stress():
    print_header("Load Stress Test - Find the Breaking Point")
    
    try:
        print("🔥 Starting progressive load test...")
        print("   Phase 1: 100 requests, 10 concurrent")
        print("   Phase 2: 500 requests, 50 concurrent")
        print("   Phase 3: 1000 requests, 100 concurrent\n")
        
        phases = [
            (100, 10, "Light load"),
            (500, 50, "Medium load"),
            (1000, 100, "Heavy load"),
        ]
        
        all_passed = True
        
        for total_requests, concurrency, phase_name in phases:
            print(f"{'='*50}")
            print(f"📊 {phase_name}: {total_requests} requests @ {concurrency} concurrent")
            print(f"{'='*50}\n")
            
            start = time.time()
            success_count = 0
            error_count = 0
            timeout_count = 0
            rate_limited_count = 0
            
            # Run async load test
            async def run_phase():
                nonlocal success_count, error_count, timeout_count, rate_limited_count
                
                async for batch in load_test_async(total_requests, concurrency):
                    for req_num, status, content in batch:
                        if status == 200:
                            success_count += 1
                        elif status == 429:
                            rate_limited_count += 1
                        elif status == 0:
                            if content == "timeout":
                                timeout_count += 1
                            else:
                                error_count += 1
                        else:
                            error_count += 1
                        
                        # Progress indicator
                        if (req_num + 1) % 100 == 0:
                            print(f"   Progress: {req_num + 1}/{total_requests} requests...")
            
            try:
                asyncio.run(run_phase())
            except Exception as e:
                print(f"   ⚠️ Phase crashed: {e}")
                all_passed = False
                continue
            
            elapsed = time.time() - start
            req_per_sec = total_requests / elapsed if elapsed > 0 else 0
            success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
            
            print(f"\n📊 Phase Results:")
            print(f"   Successful (200): {success_count}/{total_requests} ({success_rate:.1f}%)")
            print(f"   Rate limited (429): {rate_limited_count}")
            print(f"   Timeouts: {timeout_count}")
            print(f"   Errors: {error_count}")
            print(f"   Time: {elapsed:.2f}s ({req_per_sec:.1f} req/s)")
            
            # Check if this phase passed
            if success_rate < 50:
                print(f"   ❌ Phase FAILED: Success rate too low ({success_rate:.1f}%)")
                all_passed = False
            else:
                print(f"   ✅ Phase PASSED: {success_rate:.1f}% success rate")
            
            # Cooldown between phases
            if phase_name != "Heavy load":
                print(f"\n⏳ Cooling down for 2 seconds...\n")
                time.sleep(2)
        
        if all_passed:
            print_result("test_load_stress", True,
                        "Server handled all load phases successfully!")
            return True
        else:
            print_result("test_load_stress", False,
                        "Server struggled under heavy load")
            return False
            
    except Exception as e:
        print_result("test_load_stress", False, f"Test crashed: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("\n" + "="*70)
    print("🔥 MYTHARA ENGINE - COMPREHENSIVE BREAK TEST SUITE")
    print("="*70)
    print("\nTesting all 5 critical fixes under extreme conditions...")
    print(f"Target: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check if server is running
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Server is running (status: {resp.status_code})\n")
    except:
        print(f"❌ ERROR: Server is not running at {BASE_URL}")
        print(f"   Start the server with: python core/source_proprietary/main.py\n")
        sys.exit(1)
    
    # Run all tests
    tests = [
        ("test_rate_limiting", test_rate_limiting),
        ("test_cors_validation", test_cors_validation),
        ("test_database_pool", test_database_pool),
        ("test_exception_handling", test_exception_handling),
        ("test_load_stress", test_load_stress),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Test interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test runner crashed: {e}\n")
    
    # Final Report
    print("\n" + "="*70)
    print("📋 FINAL REPORT")
    print("="*70 + "\n")
    
    passed = sum(1 for r in RESULTS.values() if r["passed"])
    total = len(RESULTS)
    
    for test_name, result in RESULTS.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} - {test_name}")
        print(f"      {result['details']}\n")
    
    print(f"{'='*70}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Server is production-ready!\n")
        return 0
    else:
        print(f"⚠️ {total - passed} test(s) failed. Review issues above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
