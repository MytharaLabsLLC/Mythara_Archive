#!/usr/bin/env python3
"""
Mythara Engine - Health Check Monitor
Monitoring script for production deployments.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List
import requests

class HealthMonitor:
    """
    Health check monitor for Mythara Engine API.
    Performs periodic health checks and reports status.
    """
    
    def __init__(self, api_url: str, check_interval: int = 60):
        """
        Initialize health monitor.
        
        Args:
            api_url: Base URL of API (e.g., https://api.yourdomain.com)
            check_interval: Seconds between checks (default: 60)
        """
        self.api_url = api_url.rstrip('/')
        self.check_interval = check_interval
        self.results: List[Dict] = []
    
    def check_health(self) -> Dict:
        """
        Perform single health check.
        
        Returns:
            {
                "timestamp": str,
                "status": "healthy" | "unhealthy",
                "response_time_ms": float,
                "status_code": int,
                "version": str,
                "error": str | None
            }
        """
        start = time.time()
        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "unknown",
            "response_time_ms": 0,
            "status_code": 0,
            "version": None,
            "error": None
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=10
            )
            
            end = time.time()
            result["response_time_ms"] = round((end - start) * 1000, 2)
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                data = response.json()
                result["status"] = data.get("status", "unknown")
                result["version"] = data.get("version")
            else:
                result["status"] = "unhealthy"
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["status"] = "unhealthy"
            result["error"] = "Timeout after 10 seconds"
        except requests.exceptions.ConnectionError:
            result["status"] = "unhealthy"
            result["error"] = "Connection failed"
        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)
        
        return result
    
    def check_endpoint(self, endpoint: str, api_key: str = None) -> Dict:
        """
        Check specific API endpoint.
        
        Args:
            endpoint: Endpoint path (e.g., /v1/reservoir/status)
            api_key: API key for authentication
            
        Returns:
            Check result dictionary
        """
        start = time.time()
        result = {
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "unknown",
            "response_time_ms": 0,
            "status_code": 0,
            "error": None
        }
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            response = requests.get(
                f"{self.api_url}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            end = time.time()
            result["response_time_ms"] = round((end - start) * 1000, 2)
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = "healthy"
            else:
                result["status"] = "unhealthy"
                result["error"] = f"HTTP {response.status_code}"
                
        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)
        
        return result
    
    def monitor(self, duration_minutes: int = None):
        """
        Run continuous monitoring.
        
        Args:
            duration_minutes: Duration to monitor (None = indefinite)
        """
        print(f"🔍 Starting health monitor for {self.api_url}")
        print(f"⏱️  Check interval: {self.check_interval}s")
        if duration_minutes:
            print(f"⏳ Duration: {duration_minutes} minutes")
        else:
            print("⏳ Duration: Continuous (Ctrl+C to stop)")
        print()
        
        start_time = time.time()
        check_count = 0
        healthy_count = 0
        
        try:
            while True:
                check_count += 1
                result = self.check_health()
                self.results.append(result)
                
                if result["status"] == "healthy":
                    healthy_count += 1
                    print(f"✅ [{result['timestamp']}] Healthy "
                          f"({result['response_time_ms']}ms) "
                          f"v{result['version']}")
                else:
                    print(f"❌ [{result['timestamp']}] Unhealthy - {result['error']}")
                
                # Calculate uptime
                uptime_pct = (healthy_count / check_count) * 100
                print(f"   Uptime: {uptime_pct:.2f}% ({healthy_count}/{check_count} checks)")
                print()
                
                # Check if duration exceeded
                if duration_minutes:
                    elapsed = (time.time() - start_time) / 60
                    if elapsed >= duration_minutes:
                        break
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        
        self.print_summary(check_count, healthy_count)
    
    def print_summary(self, total: int, healthy: int):
        """Print monitoring summary."""
        print("\n" + "=" * 60)
        print("MONITORING SUMMARY")
        print("=" * 60)
        
        uptime_pct = (healthy / total) * 100 if total > 0 else 0
        
        print(f"Total checks:    {total}")
        print(f"Healthy:         {healthy}")
        print(f"Unhealthy:       {total - healthy}")
        print(f"Uptime:          {uptime_pct:.2f}%")
        
        if self.results:
            response_times = [r["response_time_ms"] for r in self.results 
                            if r["response_time_ms"] > 0]
            if response_times:
                print(f"\nResponse times:")
                print(f"  Min:     {min(response_times):.2f}ms")
                print(f"  Max:     {max(response_times):.2f}ms")
                print(f"  Average: {sum(response_times)/len(response_times):.2f}ms")
        
        # Write results to file
        output_file = "health_monitor_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📝 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Mythara Engine API health"
    )
    parser.add_argument(
        'api_url',
        help='Base URL of API (e.g., https://api.yourdomain.com)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        help='Monitoring duration in minutes (default: continuous)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Perform single check and exit'
    )
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(args.api_url, args.interval)
    
    if args.once:
        result = monitor.check_health()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == "healthy" else 1)
    else:
        monitor.monitor(args.duration)


if __name__ == "__main__":
    main()
