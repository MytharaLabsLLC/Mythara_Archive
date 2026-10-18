#!/usr/bin/env python3
"""
Mythara Engine - Soul Engine Dashboard Queries
Organizational analytics for systemic overload, indifference detection, and risk aggregation.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import statistics
import logging

from soul_cradle_systems_framework import (
    SoulCradleParadox,
    TerminalRiskCalculator,
)

logger = logging.getLogger(__name__)


class SoulEngineDashboard:
    """
    Analytics and aggregation queries for Soul Engine B2B dashboard.

    Features:
    - Department-level risk aggregation
    - Systemic overload detection
    - Indifference trajectory detection (violence prevention)
    - Organizational health metrics
    """

    def __init__(self):
        self.risk_calculator = TerminalRiskCalculator()

    # ===================== DEPARTMENT ANALYTICS =====================

    def get_department_risk_profile(
        self, paradoxes: List[SoulCradleParadox], dept_id: str
    ) -> Dict[str, Any]:
        """
        Calculate risk profile for entire department.

        Args:
            paradoxes: All paradoxes in the department
            dept_id: Department ID

        Returns:
            Department risk profile with averages, at-risk users, systemic overload
        """
        if not paradoxes:
            return {
                "dept_id": dept_id,
                "total_users": 0,
                "average_baseline_stress": 0.0,
                "average_acute_risk": 0.0,
                "average_total_risk": 0.0,
                "systemic_overload": False,
                "users_at_risk": [],
            }

        # Group paradoxes by user
        user_paradoxes: Dict[str, List[SoulCradleParadox]] = {}
        for p in paradoxes:
            if p.user_id not in user_paradoxes:
                user_paradoxes[p.user_id] = []
            user_paradoxes[p.user_id].append(p)

        # Calculate per-user risk scores
        user_risks: List[Dict[str, Any]] = []

        for user_id, user_p in user_paradoxes.items():
            # Calculate baseline stress (constant environmental stress)
            baseline_stress = self._calculate_baseline_stress(user_p)

            # Calculate acute risk from recent paradoxes
            result = self.risk_calculator.calculate_terminal_risk(
                paradoxes=user_p, baseline_stress=baseline_stress
            )

            user_risks.append(
                {
                    "user_id": user_id,
                    "baseline_stress": baseline_stress,
                    "acute_risk": result["acute_risk"],
                    "total_risk": result["terminal_risk"],
                    "paradox_count": len(user_p),
                    "systemic_overload": result["systemic_overload"],
                }
            )

        # Aggregate department metrics
        avg_baseline = statistics.mean([u["baseline_stress"] for u in user_risks])
        avg_acute = statistics.mean([u["acute_risk"] for u in user_risks])
        avg_total = statistics.mean([u["total_risk"] for u in user_risks])

        # Detect systemic overload (>50% of department in overload)
        overload_count = sum(1 for u in user_risks if u["systemic_overload"])
        systemic_overload = (overload_count / len(user_risks)) > 0.5

        # Identify high-risk users
        users_at_risk = [
            u for u in user_risks if u["total_risk"] > 0.6  # HIGH or CRITICAL
        ]
        users_at_risk.sort(key=lambda u: u["total_risk"], reverse=True)

        return {
            "dept_id": dept_id,
            "total_users": len(user_paradoxes),
            "average_baseline_stress": round(avg_baseline, 3),
            "average_acute_risk": round(avg_acute, 3),
            "average_total_risk": round(avg_total, 3),
            "systemic_overload": systemic_overload,
            "systemic_overload_count": overload_count,
            "users_at_risk": users_at_risk,
            "risk_distribution": self._calculate_risk_distribution(user_risks),
        }

    def _calculate_baseline_stress(self, paradoxes: List[SoulCradleParadox]) -> float:
        """
        Calculate baseline environmental stress from paradox patterns.

        High baseline stress indicators:
        - Frequent organizational/policy paradoxes
        - High average unresolved scores
        - Low witness scores (unsupported environment)
        """
        if not paradoxes:
            return 0.0

        # Average unresolved score (higher = more stressful environment)
        avg_unresolved = statistics.mean(
            [p.unresolved_state.unresolved_score for p in paradoxes]
        )

        # Average witness score (lower = less support)
        avg_witness = (
            statistics.mean(
                [
                    (
                        p.resolution.witness_a + p.resolution.witness_b
                        if p.resolution
                        else 0.0
                    )
                    for p in paradoxes
                ]
            )
            / 2.0
        )

        # Paradox frequency (more frequent = higher baseline stress)
        if len(paradoxes) > 1:
            timestamps = sorted([p.timestamp for p in paradoxes])
            avg_days_between = sum(
                [
                    (timestamps[i] - timestamps[i - 1]).days
                    for i in range(1, len(timestamps))
                ]
            ) / (len(timestamps) - 1)

            frequency_factor = max(0.0, 1.0 - (avg_days_between / 30.0))
        else:
            frequency_factor = 0.0

        # Combine factors
        baseline = (
            avg_unresolved * 0.4 + (1.0 - avg_witness) * 0.4 + frequency_factor * 0.2
        )

        return min(1.0, max(0.0, baseline))

    def _calculate_risk_distribution(
        self, user_risks: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of users across risk levels."""
        distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}

        for user in user_risks:
            risk = user["total_risk"]
            if risk < 0.4:
                distribution["LOW"] += 1
            elif risk < 0.6:
                distribution["MODERATE"] += 1
            elif risk < 0.8:
                distribution["HIGH"] += 1
            else:
                distribution["CRITICAL"] += 1

        return distribution

    # ===================== INDIFFERENCE DETECTION (VIOLENCE PREVENTION) =====================

    def detect_indifference_trajectory(
        self, user_id: str, paradoxes: List[SoulCradleParadox], lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Detect indifference trajectory - pre-violence signature.

        Mathematical signature:
        - Tension scores DECREASING while paradoxes remain unresolved
        - T: 0.9 → 0.5 → 0.2 (soul withdrawal)
        - U remains high (paradoxes not resolved)
        - Emotional energy → 0 (E_null approaching)

        This is the 7-30 day warning window before violence or suicide.

        Args:
            user_id: User ID to analyze
            paradoxes: User's paradox history
            lookback_days: Days to analyze (default 90)

        Returns:
            Detection result with severity, trajectory, recommendations
        """
        # Filter to recent paradoxes
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent_paradoxes = [p for p in paradoxes if p.timestamp >= cutoff]

        if len(recent_paradoxes) < 5:
            return {
                "user_id": user_id,
                "indifference_detected": False,
                "insufficient_data": True,
                "message": "Need at least 5 paradoxes in 90-day window",
            }

        # Sort by timestamp
        recent_paradoxes.sort(key=lambda p: p.timestamp)

        # Calculate tension trajectory (averaging T_a and T_b)
        tension_scores = [
            (p.system_a.tension + p.system_b.tension) / 2.0 for p in recent_paradoxes
        ]

        # Calculate unresolved trajectory
        unresolved_scores = [
            p.unresolved_state.unresolved_score for p in recent_paradoxes
        ]

        # Detect indifference pattern:
        # 1. Tension is DECREASING (linear regression slope < 0)
        # 2. Unresolved remains HIGH (average > 0.6)
        # 3. Recent tension scores significantly lower than early ones

        tension_slope = self._calculate_slope(tension_scores)
        avg_unresolved = statistics.mean(unresolved_scores)

        # Compare first 1/3 vs last 1/3 of tension scores
        first_third = tension_scores[: len(tension_scores) // 3]
        last_third = tension_scores[-len(tension_scores) // 3 :]

        tension_drop = statistics.mean(first_third) - statistics.mean(last_third)
        tension_drop_pct = tension_drop / max(statistics.mean(first_third), 0.01)

        # CRITICAL indicators
        indifference_detected = (
            tension_slope < -0.005  # Tension decreasing
            and avg_unresolved > 0.6  # Paradoxes unresolved
            and tension_drop > 0.2  # Significant drop (>0.2 on 0-1 scale)
        )

        severity = "NONE"
        if indifference_detected:
            if tension_drop > 0.5 and avg_unresolved > 0.8:
                severity = "TERMINAL"  # 🚨 7-14 day window
            elif tension_drop > 0.3:
                severity = "CRITICAL"  # 14-30 day window
            else:
                severity = "WARNING"  # Early detection

        # Estimate emotional energy (E = T when paradoxes unresolved)
        emotional_energy = statistics.mean(last_third)

        # Estimate days until critical (based on tension drop rate)
        if tension_slope < 0 and emotional_energy > 0:
            days_until_zero = emotional_energy / abs(tension_slope)
            days_until_critical = max(1, int(days_until_zero * 0.5))  # 50% threshold
        else:
            days_until_critical = None

        result = {
            "user_id": user_id,
            "indifference_detected": indifference_detected,
            "severity": severity,
            "tension_trajectory": [round(t, 3) for t in tension_scores],
            "tension_slope": round(tension_slope, 5),
            "tension_drop": round(tension_drop, 3),
            "tension_drop_pct": round(tension_drop_pct * 100, 1),
            "avg_unresolved": round(avg_unresolved, 3),
            "emotional_energy": round(emotional_energy, 3),
            "days_until_critical": days_until_critical,
            "paradox_count": len(recent_paradoxes),
            "analysis_window_days": lookback_days,
        }

        # Add recommendations based on severity
        if severity == "TERMINAL":
            result["recommendations"] = [
                "🚨 72-HOUR WATCH PROTOCOL",
                "Crisis counselor within 2 hours",
                "Psychiatric evaluation within 6 hours",
                "24/7 supervision until stabilized",
                "Remove weapon/medication access",
                "Consider psychiatric hold",
                "Notify emergency contacts immediately",
            ]
            result["protocol"] = "EMERGENCY_RESPONSE"

        elif severity == "CRITICAL":
            result["recommendations"] = [
                "⚠️ URGENT INTERVENTION REQUIRED",
                "Crisis counselor meeting within 24 hours",
                "Threat assessment by trained professional",
                "Daily check-ins for 30 days",
                "Parent/guardian notification",
                "Create safety plan",
                "Monitor daily for further deterioration",
            ]
            result["protocol"] = "URGENT_INTERVENTION"

        elif severity == "WARNING":
            result["recommendations"] = [
                "Counselor check-in within 1 week",
                "Weekly monitoring for trajectory change",
                "Increase social support (peer groups)",
                "Address environmental stressors",
                "Document progression for trend analysis",
            ]
            result["protocol"] = "PREVENTIVE_SUPPORT"

        return result

    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate linear regression slope."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    # ===================== ORGANIZATIONAL HEALTH METRICS =====================

    def get_organization_health(
        self, org_id: str, all_paradoxes: List[SoulCradleParadox]
    ) -> Dict[str, Any]:
        """
        Calculate organization-wide health metrics.

        Args:
            org_id: Organization ID
            all_paradoxes: All paradoxes in the organization

        Returns:
            Organization health report
        """
        # Group by department
        dept_paradoxes: Dict[str, List[SoulCradleParadox]] = {}
        for p in all_paradoxes:
            # Extract dept_id from user_id or paradox metadata
            dept_id = self._extract_dept_id(p)
            if dept_id not in dept_paradoxes:
                dept_paradoxes[dept_id] = []
            dept_paradoxes[dept_id].append(p)

        # Calculate per-department profiles
        dept_profiles = []
        for dept_id, paradoxes in dept_paradoxes.items():
            profile = self.get_department_risk_profile(paradoxes, dept_id)
            dept_profiles.append(profile)

        # Organization-level metrics
        total_users = sum(p["total_users"] for p in dept_profiles)
        avg_org_baseline = statistics.mean(
            [p["average_baseline_stress"] for p in dept_profiles]
        )
        avg_org_acute = statistics.mean(
            [p["average_acute_risk"] for p in dept_profiles]
        )

        # Count departments in systemic overload
        depts_in_overload = sum(1 for p in dept_profiles if p["systemic_overload"])

        # Aggregate risk distribution
        org_distribution = {
            "LOW": sum(p["risk_distribution"]["LOW"] for p in dept_profiles),
            "MODERATE": sum(p["risk_distribution"]["MODERATE"] for p in dept_profiles),
            "HIGH": sum(p["risk_distribution"]["HIGH"] for p in dept_profiles),
            "CRITICAL": sum(p["risk_distribution"]["CRITICAL"] for p in dept_profiles),
        }

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(
            avg_org_baseline, avg_org_acute, org_distribution, total_users
        )

        return {
            "org_id": org_id,
            "health_score": health_score,
            "total_users": total_users,
            "total_departments": len(dept_profiles),
            "departments_in_overload": depts_in_overload,
            "average_baseline_stress": round(avg_org_baseline, 3),
            "average_acute_risk": round(avg_org_acute, 3),
            "risk_distribution": org_distribution,
            "department_profiles": dept_profiles,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _extract_dept_id(self, paradox: SoulCradleParadox) -> str:
        """Extract department ID from paradox (placeholder - implement based on schema)."""
        # This should extract from EntityRegistry or paradox metadata
        # For now, return "UNKNOWN"
        return "UNKNOWN"

    def _calculate_health_score(
        self,
        baseline: float,
        acute: float,
        distribution: Dict[str, int],
        total_users: int,
    ) -> int:
        """
        Calculate organizational health score (0-100).

        100 = Excellent (low baseline, low acute, most users in LOW risk)
        0 = Crisis (high baseline, high acute, most users in CRITICAL)
        """
        if total_users == 0:
            return 100

        # Baseline stress penalty (0-30 points)
        baseline_penalty = int(baseline * 30)

        # Acute risk penalty (0-30 points)
        acute_penalty = int(acute * 30)

        # Risk distribution penalty (0-40 points)
        critical_pct = distribution["CRITICAL"] / total_users
        high_pct = distribution["HIGH"] / total_users

        distribution_penalty = int(critical_pct * 40 + high_pct * 20)

        health_score = 100 - baseline_penalty - acute_penalty - distribution_penalty

        return max(0, min(100, health_score))


# ===================== CONVENIENCE FUNCTIONS =====================


def get_department_analytics(
    dept_id: str, paradoxes: List[SoulCradleParadox]
) -> Dict[str, Any]:
    """Get department risk profile."""
    dashboard = SoulEngineDashboard()
    return dashboard.get_department_risk_profile(paradoxes, dept_id)


def detect_indifference(
    user_id: str, paradoxes: List[SoulCradleParadox]
) -> Dict[str, Any]:
    """Detect indifference trajectory for violence prevention."""
    dashboard = SoulEngineDashboard()
    return dashboard.detect_indifference_trajectory(user_id, paradoxes)


def get_org_health(org_id: str, paradoxes: List[SoulCradleParadox]) -> Dict[str, Any]:
    """Get organization health metrics."""
    dashboard = SoulEngineDashboard()
    return dashboard.get_organization_health(org_id, paradoxes)
