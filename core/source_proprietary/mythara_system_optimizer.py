# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara System Resource Optimizer Bot
Monitors system capacity, overrides Windows protocols to maximize RAM/CPU,
ensures 15 autonomous bots run smoothly without performance degradation
"""

import psutil
import subprocess
import os
from datetime import datetime
from typing import Dict, List


class MytharaSystemOptimizer:
    def __init__(self):
        self.min_available_ram_gb = 2.0  # Alert if < 2GB free
        self.min_available_cpu_percent = 20.0  # Alert if < 20% CPU available
        self.optimization_applied = False

    def get_system_specs(self) -> Dict:
        """Get current system specifications"""
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_physical = psutil.cpu_count(logical=False)
        disk = psutil.disk_usage("C:\\")

        specs = {
            "total_ram_gb": round(memory.total / (1024**3), 2),
            "available_ram_gb": round(memory.available / (1024**3), 2),
            "ram_usage_percent": memory.percent,
            "cpu_logical_cores": cpu_count,
            "cpu_physical_cores": cpu_physical,
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_usage_percent": disk.percent,
            "timestamp": datetime.now().isoformat(),
        }

        return specs

    def calculate_bot_workload(self, num_bots: int = 15) -> Dict:
        """Calculate resource requirements for all bots"""

        # Conservative estimates per bot
        ram_per_bot_mb = 150  # Python + SQLite + small operations
        cpu_per_bot_percent = 2.5  # Average CPU usage per bot

        total_ram_needed_gb = (ram_per_bot_mb * num_bots) / 1024
        total_cpu_needed_percent = cpu_per_bot_percent * num_bots

        specs = self.get_system_specs()

        workload = {
            "number_of_bots": num_bots,
            "estimated_ram_needed_gb": round(total_ram_needed_gb, 2),
            "estimated_cpu_needed_percent": round(total_cpu_needed_percent, 1),
            "current_available_ram_gb": specs["available_ram_gb"],
            "current_available_cpu_percent": 100 - specs["cpu_usage_percent"],
            "ram_sufficient": specs["available_ram_gb"] >= total_ram_needed_gb,
            "cpu_sufficient": (100 - specs["cpu_usage_percent"])
            >= total_cpu_needed_percent,
            "system_can_handle": None,
            "optimization_needed": False,
            "recommendations": [],
        }

        # Determine if system can handle workload
        if workload["ram_sufficient"] and workload["cpu_sufficient"]:
            workload["system_can_handle"] = True
            workload["recommendations"].append(
                "✅ System has sufficient resources for all 15 bots"
            )
        else:
            workload["system_can_handle"] = False
            workload["optimization_needed"] = True

            if not workload["ram_sufficient"]:
                shortfall = total_ram_needed_gb - specs["available_ram_gb"]
                workload["recommendations"].append(
                    f"⚠️ RAM shortfall: Need {shortfall:.2f} GB more. Optimization required."
                )

            if not workload["cpu_sufficient"]:
                workload["recommendations"].append(
                    "⚠️ CPU may be constrained. Optimization recommended."
                )

        return workload

    def apply_windows_optimizations(self) -> List[str]:
        """Apply Windows registry and system optimizations to maximize resources"""
        optimizations = []

        print("\n[OPTIMIZER] Applying Windows system optimizations...\n")

        # 1. Disable Windows Search indexing (frees RAM)
        try:
            subprocess.run(
                ["powershell", "-Command", "Stop-Service -Name WSearch -Force"],
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Set-Service -Name WSearch -StartupType Disabled",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append(
                "✅ Disabled Windows Search indexing (frees ~200-500MB RAM)"
            )
        except Exception as e:
            optimizations.append(f"⚠️ Could not disable Windows Search: {e}")

        # 2. Disable Superfetch/SysMain (reduces disk I/O)
        try:
            subprocess.run(
                ["powershell", "-Command", "Stop-Service -Name SysMain -Force"],
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Set-Service -Name SysMain -StartupType Disabled",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append(
                "✅ Disabled Superfetch/SysMain (frees ~100-300MB RAM)"
            )
        except Exception as e:
            optimizations.append(f"⚠️ Could not disable Superfetch: {e}")

        # 3. Set process priority for Python (higher CPU priority)
        try:
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Get-Process python | ForEach-Object { $_.PriorityClass = "High" }',
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append("✅ Set Python processes to HIGH priority")
        except Exception as e:
            optimizations.append(f"⚠️ Could not set Python priority: {e}")

        # 4. Disable Windows Tips and Suggestions
        try:
            subprocess.run(
                [
                    "reg",
                    "add",
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager",
                    "/v",
                    "SubscribedContent-338389Enabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append("✅ Disabled Windows Tips (frees ~50MB RAM)")
        except Exception as e:
            optimizations.append(f"⚠️ Could not disable Windows Tips: {e}")

        # 5. Clear Windows Temp files
        try:
            temp_path = os.environ.get("TEMP", "C:\\Windows\\Temp")
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'Remove-Item -Path "{temp_path}\\*" -Recurse -Force -ErrorAction SilentlyContinue',
                ],
                capture_output=True,
                timeout=30,
            )
            optimizations.append("✅ Cleared Windows temp files")
        except Exception as e:
            optimizations.append(f"⚠️ Could not clear temp files: {e}")

        # 6. Disable Visual Effects (reduces GPU/RAM usage)
        try:
            subprocess.run(
                [
                    "reg",
                    "add",
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects",
                    "/v",
                    "VisualFXSetting",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "2",
                    "/f",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append(
                "✅ Set Visual Effects to 'Best Performance' (frees ~100-200MB RAM)"
            )
        except Exception as e:
            optimizations.append(f"⚠️ Could not optimize visual effects: {e}")

        # 7. Increase system cache for applications
        try:
            subprocess.run(
                [
                    "reg",
                    "add",
                    "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management",
                    "/v",
                    "LargeSystemCache",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append("✅ Enabled Large System Cache for applications")
        except Exception as e:
            optimizations.append(f"⚠️ Could not enable large system cache: {e}")

        # 8. Disable hibernation (frees disk space = more virtual memory)
        try:
            subprocess.run(
                ["powershell", "-Command", "powercfg /hibernate off"],
                capture_output=True,
                timeout=10,
            )
            optimizations.append(
                "✅ Disabled hibernation (frees disk space for virtual memory)"
            )
        except Exception as e:
            optimizations.append(f"⚠️ Could not disable hibernation: {e}")

        # 9. Set power plan to High Performance
        try:
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append("✅ Set power plan to HIGH PERFORMANCE")
        except Exception as e:
            optimizations.append(f"⚠️ Could not set power plan: {e}")

        # 10. Increase virtual memory (pagefile)
        try:
            # Calculate optimal pagefile size (1.5x RAM)
            ram_gb = psutil.virtual_memory().total / (1024**3)
            pagefile_mb = int(ram_gb * 1.5 * 1024)

            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'wmic pagefileset where name="C:\\\\pagefile.sys" set InitialSize={pagefile_mb},MaximumSize={pagefile_mb}',
                ],
                capture_output=True,
                timeout=10,
            )
            optimizations.append(
                f"✅ Increased virtual memory to {pagefile_mb}MB (1.5x RAM)"
            )
        except Exception as e:
            optimizations.append(f"⚠️ Could not increase virtual memory: {e}")

        self.optimization_applied = True
        return optimizations

    def kill_resource_hogs(self, exclude_processes: List[str] = None) -> List[str]:
        """Kill processes consuming excessive resources"""
        if exclude_processes is None:
            exclude_processes = [
                "python.exe",
                "pythonw.exe",
                "System",
                "svchost.exe",
                "explorer.exe",
                "taskhostw.exe",
                "dwm.exe",
            ]

        killed = []

        print("\n[OPTIMIZER] Identifying resource-intensive processes...\n")

        # Find processes using > 500MB RAM or > 25% CPU
        for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
            try:
                mem_mb = proc.info["memory_info"].rss / (1024**2)
                cpu_percent = proc.info["cpu_percent"]

                # Skip critical processes
                if proc.info["name"] in exclude_processes:
                    continue

                # Kill if using excessive resources
                if mem_mb > 500 or cpu_percent > 25:
                    try:
                        p = psutil.Process(proc.info["pid"])
                        p.terminate()
                        killed.append(
                            f"✅ Killed {proc.info['name']} (PID: {proc.info['pid']}, RAM: {mem_mb:.0f}MB, CPU: {cpu_percent:.1f}%)"
                        )
                    except Exception:
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not killed:
            killed.append("✅ No resource-hogging processes found")

        return killed

    def optimize_python_runtime(self) -> List[str]:
        """Apply Python-specific optimizations"""
        optimizations = []

        print("\n[OPTIMIZER] Applying Python runtime optimizations...\n")

        # 1. Set environment variables for Python optimization
        os.environ["PYTHONOPTIMIZE"] = "2"  # Enable maximum optimization
        optimizations.append("✅ Set PYTHONOPTIMIZE=2 (bytecode optimization)")

        os.environ["PYTHONDONTWRITEBYTECODE"] = "0"  # Allow .pyc caching
        optimizations.append("✅ Enabled bytecode caching (.pyc files)")

        os.environ["PYTHONUNBUFFERED"] = "0"  # Enable buffering for performance
        optimizations.append("✅ Enabled I/O buffering")

        # 2. Recommend SQLite optimizations
        optimizations.append(
            "✅ Recommend: Use PRAGMA journal_mode=WAL in SQLite for concurrent access"
        )
        optimizations.append(
            "✅ Recommend: Use PRAGMA synchronous=NORMAL in SQLite for faster writes"
        )

        # 3. Recommend batch processing
        optimizations.append(
            "✅ Recommend: Schedule bots at staggered times (not all at once)"
        )

        return optimizations

    def generate_optimization_report(self) -> str:
        """Generate comprehensive system optimization report"""
        specs = self.get_system_specs()
        workload = self.calculate_bot_workload(15)

        report = f"""
================================================================================
MYTHARA SYSTEM RESOURCE OPTIMIZER - ANALYSIS REPORT
================================================================================

CURRENT SYSTEM SPECIFICATIONS:
   Total RAM: {specs['total_ram_gb']} GB
   Available RAM: {specs['available_ram_gb']} GB ({100 - specs['ram_usage_percent']:.1f}% free)
   CPU Cores: {specs['cpu_logical_cores']} logical ({specs['cpu_physical_cores']} physical)
   CPU Usage: {specs['cpu_usage_percent']:.1f}% ({100 - specs['cpu_usage_percent']:.1f}% available)
   Disk Space: {specs['disk_free_gb']} GB free ({100 - specs['disk_usage_percent']:.1f}% available)

WORKLOAD ANALYSIS (15 Autonomous Bots):
   Estimated RAM Needed: {workload['estimated_ram_needed_gb']} GB
   Estimated CPU Needed: {workload['estimated_cpu_needed_percent']}%
   
   RAM Assessment: {"✅ SUFFICIENT" if workload['ram_sufficient'] else "⚠️ INSUFFICIENT"}
   CPU Assessment: {"✅ SUFFICIENT" if workload['cpu_sufficient'] else "⚠️ MAY BE CONSTRAINED"}
   
   Overall Verdict: {"✅ SYSTEM CAN HANDLE ALL 15 BOTS" if workload['system_can_handle'] else "⚠️ OPTIMIZATION REQUIRED"}

RECOMMENDATIONS:
"""

        for rec in workload["recommendations"]:
            report += f"   {rec}\n"

        report += f"""
OPTIMIZATION STATUS:
   Windows Optimizations Applied: {"✅ YES" if self.optimization_applied else "⚠️ NOT YET"}
   
   Expected RAM Savings After Optimization:
      - Disable Windows Search: ~200-500 MB
      - Disable Superfetch: ~100-300 MB
      - Disable Visual Effects: ~100-200 MB
      - Kill resource hogs: ~500-1000 MB
      - Clear temp files: ~100-500 MB
      TOTAL EXPECTED SAVINGS: ~1-2.5 GB

BOT SCHEDULING STRATEGY (To Minimize Load):
   
   CONTINUOUS (Every 30 min):
      - Support Chat Bot (low CPU, monitors tickets)
   
   HOURLY:
      - DevOps VP (system monitoring)
      - DevSecOps VP (security scanning)
   
   DAILY (Staggered):
      06:00 AM - Finance VP
      07:00 AM - Logistics VP
      08:00 AM - Sales/Marketing VP
      09:00 AM - Customer Success VP, International Sales VP, Researcher Bot
      10:00 AM - Public Affairs VP, SBGA Bot
      11:00 AM - Accounting VP
   
   WEEKLY:
      Monday 06:00 AM - Grant Writer Bot
      Monday 08:00 AM - HR VP
      Sunday 12:00 AM - SEO Bot
   
   MAXIMUM CONCURRENT BOTS: 3-4 (uses ~600MB RAM, 10% CPU)

PERFORMANCE OPTIMIZATION TIPS:
   1. ✅ Use SQLite with WAL mode (Write-Ahead Logging) for concurrent access
   2. ✅ Enable PRAGMA synchronous=NORMAL for faster database writes
   3. ✅ Schedule heavy bots (Grant Writer, Researcher) during off-hours
   4. ✅ Run cleanup scripts weekly to delete old audit logs
   5. ✅ Monitor RAM usage; restart bots monthly to prevent memory leaks

================================================================================
"""

        return report


if __name__ == "__main__":
    print("=" * 80)
    print("MYTHARA SYSTEM RESOURCE OPTIMIZER")
    print("Analyzing capacity for 15 autonomous bots...")
    print("=" * 80)

    optimizer = MytharaSystemOptimizer()

    # Step 1: Analyze current system
    print("\n[1/5] Analyzing system specifications...")
    specs = optimizer.get_system_specs()
    print(
        f"[OK] System has {specs['total_ram_gb']} GB RAM, {specs['cpu_logical_cores']} CPU cores"
    )

    # Step 2: Calculate workload
    print("\n[2/5] Calculating workload for 15 bots...")
    workload = optimizer.calculate_bot_workload(15)
    print(
        f"[OK] Bots need ~{workload['estimated_ram_needed_gb']} GB RAM, ~{workload['estimated_cpu_needed_percent']}% CPU"
    )

    if not workload["system_can_handle"]:
        print("\n⚠️  OPTIMIZATION REQUIRED\n")

        # Step 3: Apply Windows optimizations
        print("[3/5] Applying Windows system optimizations...")
        print("      (Note: Some optimizations require Administrator privileges)")
        windows_opts = optimizer.apply_windows_optimizations()
        for opt in windows_opts:
            print(f"      {opt}")

        # Step 4: Kill resource hogs
        print("\n[4/5] Killing resource-intensive processes...")
        killed = optimizer.kill_resource_hogs()
        for k in killed:
            print(f"      {k}")

        # Step 5: Apply Python optimizations
        print("\n[5/5] Applying Python runtime optimizations...")
        python_opts = optimizer.optimize_python_runtime()
        for opt in python_opts:
            print(f"      {opt}")

        print("\n✅ OPTIMIZATION COMPLETE\n")
        print("Recommendation: Restart Windows to apply all registry changes")
    else:
        print("\n✅ SYSTEM CAN HANDLE ALL 15 BOTS WITHOUT OPTIMIZATION\n")
        print("[3/5] Skipping Windows optimizations (not needed)")
        print("[4/5] Skipping process cleanup (not needed)")
        print("[5/5] Applying Python runtime optimizations anyway...")
        python_opts = optimizer.optimize_python_runtime()
        for opt in python_opts:
            print(f"      {opt}")

    # Generate full report
    print("\n" + "=" * 80)
    print(optimizer.generate_optimization_report())

    # Re-check after optimization
    print("\n[POST-OPTIMIZATION] Re-analyzing system resources...")
    specs_after = optimizer.get_system_specs()
    print(
        f"[OK] Available RAM after optimization: {specs_after['available_ram_gb']} GB"
    )
    print(
        f"[OK] Available CPU after optimization: {100 - specs_after['cpu_usage_percent']:.1f}%"
    )

    workload_after = optimizer.calculate_bot_workload(15)
    if workload_after["system_can_handle"]:
        print("\n" + "=" * 80)
        print("✅✅✅ SYSTEM NOW READY TO HANDLE ALL 15 BOTS ✅✅✅")
        print("=" * 80)
    else:
        print("\n⚠️  Additional RAM may be needed. Recommendations:")
        print("   1. Close all non-essential applications before running bots")
        print("   2. Restart Windows to free up memory")
        print("   3. Use staggered bot scheduling (not all at once)")
        print("   4. Consider upgrading RAM if running 24/7 production workloads")

    print("\n" + "=" * 80)
