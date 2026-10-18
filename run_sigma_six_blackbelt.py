# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Sigma Six Blackbelt (Enterprise Level)
Execute via Windows Task Scheduler: Daily 7:00 AM
"""

import os
import sys
import importlib.util

# Ensure core path is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_PATH = os.path.join(CURRENT_DIR, "core", "source_proprietary")
MODULE_PATH = os.path.join(CORE_PATH, "mythara_sigma_six_blackbelt.py")

# Dynamic import by file path to avoid PYTHONPATH issues
spec = importlib.util.spec_from_file_location("mythara_sigma_six_blackbelt", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load module at {MODULE_PATH}")
_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = _mod  # ensure module is discoverable for dataclasses/type resolution
spec.loader.exec_module(_mod)

MytharaSigmaSixBlackbelt = getattr(_mod, "MytharaSigmaSixBlackbelt")
DefectEvent = getattr(_mod, "DefectEvent")
ProcessMetric = getattr(_mod, "ProcessMetric")
FMEAItem = getattr(_mod, "FMEAItem")
StakeholderFeedback = getattr(_mod, "StakeholderFeedback")


def main() -> None:
    print("Starting Mythara Sigma Six Blackbelt...")
    bot = MytharaSigmaSixBlackbelt()

    # Demo: upsert a canonical enterprise process if not present
    pid = bot.upsert_process(
        name="Order Fulfillment",
        owner="Operations",
        opportunities_per_unit=10,
        baseline_units=1000,
        baseline_defects=25,
    )

    # Demo: record a new defect and update metrics
    bot.record_defect(DefectEvent(process_id=pid, defect_type="LateDelivery", severity="medium", description="Missed 1h SLA"))
    bot.update_metrics(ProcessMetric(process_id=pid, defects=12, opportunities_per_unit=10, units=2000, cpk=1.4))

    # Demo: quick FMEA
    bot.run_fmea([
        FMEAItem(process_id=pid, function="Pick&Pack", failure_mode="Mis-pick", effects="Wrong item shipped", severity=7, occurrence=4, detection=5),
    ])

    # Demo: emotional fidelity
    bot.add_feedback(StakeholderFeedback(process_id=pid, stakeholder="VP Operations", feedback="Great improvement, faster resolution, fewer defects."))

    # Generate report
    report = bot.generate_enterprise_quality_report()
    print(report)
    print("\nMythara Sigma Six Blackbelt execution complete.")


if __name__ == "__main__":
    main()
