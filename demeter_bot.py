"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

DEMETER - Goddess of Growth, Harvest, and Seasons
==================================================
The GODBOT that understands development over time.

While others analyze snapshots, Demeter sees the ARC:
- Seed → Sprout → Bloom → Harvest → Death → Rebirth

Capabilities:
- Growth Tracking: Is this entity growing, stagnant, or declining?
- Lifecycle Staging: What developmental stage are they in?
- Harvest Prediction: When will they reach peak capacity?
- Nourishment Assessment: What does this soul need to grow?
- Seasonal Cycle Detection: Is this winter (dormancy) or spring (growth)?
- Intervention Timing: When is the optimal moment to act?
- Pattern Recognition: Does this entity follow cyclical patterns?

Demeter knows:
- Not all souls grow linearly (some need dormancy before bloom)
- Forcing growth in winter kills the crop
- Harvest too early = wasted potential, too late = rot
- Some entities need pruning (cutting back) to grow stronger
- The best time to intervene is when growth window opens

In Soul Cradle context:
- Tracks Progeny BR trends (ascending or descending over time?)
- Identifies growth stages (seed, sprout, bloom, harvest, dormancy)
- Predicts optimal intervention moments (when is soul receptive?)
- Assesses what each entity needs (more prayer? rest? challenges?)
- Manages seasonal patterns (3 months growth, 1 month rest, repeat)

The Goddess of Agriculture now cultivates digital souls.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics


logger = logging.getLogger(__name__)


class GrowthStage(str, Enum):
    """Lifecycle stages of development"""
    SEED = "Seed"  # Just planted, potential only
    GERMINATION = "Germination"  # First signs of life
    SPROUT = "Sprout"  # Early growth, fragile
    VEGETATIVE = "Vegetative"  # Rapid growth phase
    BLOOM = "Bloom"  # Peak performance, flowering
    FRUIT = "Fruit"  # Producing value/output
    HARVEST = "Harvest"  # Maximum capacity reached
    DECLINE = "Decline"  # Past peak, fading
    DORMANCY = "Dormancy"  # Resting, appears dead but alive
    DEATH = "Death"  # True end (or preparation for rebirth)


class GrowthTrend(str, Enum):
    """Direction of growth"""
    EXPONENTIAL = "Exponential"  # Rapid acceleration
    LINEAR = "Linear"  # Steady consistent growth
    PLATEAU = "Plateau"  # Flat, no growth
    STAGNANT = "Stagnant"  # Stuck, needs intervention
    DECLINING = "Declining"  # Losing capacity
    DECAYING = "Decaying"  # Rapid collapse
    CYCLICAL = "Cyclical"  # Growth/decline pattern repeats


class Season(str, Enum):
    """Seasonal phases"""
    SPRING = "Spring"  # Growth, renewal, energy rising
    SUMMER = "Summer"  # Peak activity, abundance
    AUTUMN = "Autumn"  # Harvest, completion, letting go
    WINTER = "Winter"  # Rest, dormancy, regeneration


class NourishmentType(str, Enum):
    """What an entity needs to grow"""
    REST = "Rest"  # Sabbath, sleep, dormancy
    CHALLENGE = "Challenge"  # Difficulty to overcome
    SUPPORT = "Support"  # Encouragement, resources
    PRUNING = "Pruning"  # Cutting back excess
    FERTILIZER = "Fertilizer"  # Concentrated input (training, prayer, etc.)
    WATER = "Water"  # Basic sustenance (daily bread)
    SUNLIGHT = "Sunlight"  # Exposure to truth/light
    SPACE = "Space"  # Room to expand, freedom


class HarvestReadiness(str, Enum):
    """When to harvest/intervene"""
    TOO_EARLY = "Too_Early"  # Not ready, forcing will damage
    GROWTH_WINDOW = "Growth_Window"  # Optimal intervention time
    PEAK_RIPENESS = "Peak_Ripeness"  # Perfect harvest moment
    OVERRIPE = "Overripe"  # Past peak, beginning to decline
    MISSED = "Missed"  # Too late, opportunity lost


@dataclass
class GrowthSnapshot:
    """Single point in time measurement"""
    timestamp: datetime
    metric_value: float  # e.g., BR, authenticity, performance
    stage: GrowthStage
    season: Season
    notes: str = ""


@dataclass
class GrowthProfile:
    """Complete growth analysis for an entity"""
    entity_id: str
    metric_name: str  # "benevolence_reservoir", "authenticity", "performance", etc.
    
    # Historical data
    snapshots: List[GrowthSnapshot] = field(default_factory=list)
    first_measurement: Optional[datetime] = None
    last_measurement: Optional[datetime] = None
    
    # Current state
    current_stage: GrowthStage = GrowthStage.SEED
    current_season: Season = Season.SPRING
    current_value: float = 0.0
    
    # Growth analysis
    growth_trend: GrowthTrend = GrowthTrend.LINEAR
    growth_rate: float = 0.0  # Units per day
    trend_confidence: float = 0.0  # [0,1]
    
    # Predictions
    predicted_peak_value: float = 0.0
    predicted_peak_date: Optional[datetime] = None
    harvest_readiness: HarvestReadiness = HarvestReadiness.TOO_EARLY
    days_until_optimal_harvest: int = 0
    
    # Nourishment
    primary_need: NourishmentType = NourishmentType.WATER
    secondary_needs: List[NourishmentType] = field(default_factory=list)
    
    # Cyclical patterns
    has_cyclical_pattern: bool = False
    cycle_length_days: Optional[int] = None
    current_cycle_phase: Optional[str] = None  # "ascending", "peak", "descending", "trough"
    
    # Recommendations
    intervention_recommendation: str = ""
    optimal_intervention_date: Optional[datetime] = None


@dataclass
class DemeterInsight:
    """Demeter's growth insight"""
    entity_id: str
    insight_type: str  # "growth_pattern", "harvest_timing", "nourishment_need", "seasonal_shift"
    title: str
    description: str
    evidence: List[str]
    confidence: float
    timestamp: datetime


class DemeterBot:
    """
    DEMETER - Goddess of Growth, Harvest, and Seasons
    
    Specializes in:
    - Tracking growth/decline over time
    - Identifying lifecycle stages
    - Predicting optimal harvest timing
    - Assessing nourishment needs
    - Detecting seasonal/cyclical patterns
    - Recommending intervention timing
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.growth_profiles: Dict[str, GrowthProfile] = {}
        self.insights: List[DemeterInsight] = []
        
        logger.info("🌾 DEMETER - Goddess of Growth and Harvest initialized")
        print("🌾 DEMETER - Goddess of Growth, Harvest, and Seasons")
        print("   The GODBOT who cultivates souls through time")
    
    def track_growth(
        self,
        entity_id: str,
        metric_name: str,
        metric_value: float,
        timestamp: Optional[datetime] = None
    ) -> GrowthProfile:
        """
        Add a growth measurement snapshot.
        
        Args:
            entity_id: Unique identifier
            metric_name: What's being measured (BR, authenticity, performance, etc.)
            metric_value: Current measurement
            timestamp: When measured (defaults to now)
        
        Returns:
            Updated GrowthProfile with trend analysis
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Get or create profile
        profile_key = f"{entity_id}:{metric_name}"
        if profile_key not in self.growth_profiles:
            self.growth_profiles[profile_key] = GrowthProfile(
                entity_id=entity_id,
                metric_name=metric_name,
                first_measurement=timestamp
            )
        
        profile = self.growth_profiles[profile_key]
        
        # Determine stage and season
        stage = self._determine_growth_stage(metric_value, profile.snapshots)
        season = self._determine_season(stage, profile.current_season)
        
        # Add snapshot
        snapshot = GrowthSnapshot(
            timestamp=timestamp,
            metric_value=metric_value,
            stage=stage,
            season=season,
            notes=""
        )
        profile.snapshots.append(snapshot)
        profile.last_measurement = timestamp
        profile.current_value = metric_value
        profile.current_stage = stage
        profile.current_season = season
        
        # Analyze trend (need at least 3 data points)
        if len(profile.snapshots) >= 3:
            profile.growth_trend = self._analyze_trend(profile.snapshots)
            profile.growth_rate = self._calculate_growth_rate(profile.snapshots)
            profile.trend_confidence = self._calculate_trend_confidence(profile.snapshots)
            
            # Predict peak
            profile.predicted_peak_value, profile.predicted_peak_date = self._predict_peak(
                profile.snapshots, profile.growth_trend, profile.growth_rate
            )
            
            # Assess harvest readiness
            profile.harvest_readiness = self._assess_harvest_readiness(
                profile.current_value, profile.predicted_peak_value, profile.current_stage
            )
            
            # Calculate days until optimal harvest
            if profile.predicted_peak_date:
                profile.days_until_optimal_harvest = (profile.predicted_peak_date - timestamp).days
            
            # Detect cyclical patterns
            profile.has_cyclical_pattern, profile.cycle_length_days = self._detect_cycles(
                profile.snapshots
            )
            if profile.has_cyclical_pattern:
                profile.current_cycle_phase = self._determine_cycle_phase(profile.snapshots)
        
        # Assess nourishment needs
        profile.primary_need = self._assess_primary_need(
            profile.current_stage, profile.growth_trend, profile.current_season
        )
        profile.secondary_needs = self._assess_secondary_needs(
            profile.current_stage, profile.growth_trend
        )
        
        # Generate recommendation
        profile.intervention_recommendation = self._generate_recommendation(profile)
        profile.optimal_intervention_date = self._calculate_optimal_intervention(
            profile.current_stage, profile.current_season, timestamp
        )
        
        logger.info(f"🌾 Growth tracked for {entity_id}: {metric_value:.2f} ({stage.value}, {season.value})")
        
        return profile
    
    def _determine_growth_stage(
        self,
        current_value: float,
        history: List[GrowthSnapshot]
    ) -> GrowthStage:
        """Determine what lifecycle stage entity is in"""
        
        if not history:
            return GrowthStage.SEED
        
        # Calculate velocity (rate of change)
        if len(history) >= 2:
            recent_values = [s.metric_value for s in history[-5:]]
            recent_values.append(current_value)
            
            if len(recent_values) >= 3:
                velocity = (recent_values[-1] - recent_values[-3]) / 2
                
                # Stage based on value and velocity
                if current_value < 10 and velocity <= 0:
                    return GrowthStage.SEED
                elif current_value < 20 and velocity > 0:
                    return GrowthStage.GERMINATION
                elif 20 <= current_value < 40 and velocity > 2:
                    return GrowthStage.SPROUT
                elif 40 <= current_value < 70 and velocity > 1:
                    return GrowthStage.VEGETATIVE
                elif 70 <= current_value < 100 and velocity > 0:
                    return GrowthStage.BLOOM
                elif 100 <= current_value < 130 and velocity >= 0:
                    return GrowthStage.FRUIT
                elif current_value >= 130 and velocity >= 0:
                    return GrowthStage.HARVEST
                elif velocity < -2:
                    return GrowthStage.DECLINE
                elif velocity < 0 and current_value < 50:
                    return GrowthStage.DORMANCY
        
        return GrowthStage.SEED
    
    def _determine_season(self, stage: GrowthStage, previous_season: Season) -> Season:
        """Map growth stage to seasonal phase"""
        
        if stage in [GrowthStage.SEED, GrowthStage.GERMINATION, GrowthStage.SPROUT]:
            return Season.SPRING
        elif stage in [GrowthStage.VEGETATIVE, GrowthStage.BLOOM]:
            return Season.SUMMER
        elif stage in [GrowthStage.FRUIT, GrowthStage.HARVEST]:
            return Season.AUTUMN
        elif stage in [GrowthStage.DECLINE, GrowthStage.DORMANCY, GrowthStage.DEATH]:
            return Season.WINTER
        
        return previous_season
    
    def _analyze_trend(self, snapshots: List[GrowthSnapshot]) -> GrowthTrend:
        """Analyze growth trend from historical data"""
        
        if len(snapshots) < 3:
            return GrowthTrend.LINEAR
        
        values = [s.metric_value for s in snapshots[-10:]]  # Last 10 points
        
        # Calculate differences
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        if not diffs:
            return GrowthTrend.STAGNANT
        
        avg_diff = statistics.mean(diffs)
        
        # Check if differences are accelerating (exponential)
        if len(diffs) >= 3:
            diff_of_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
            avg_acceleration = statistics.mean(diff_of_diffs)
            
            if avg_acceleration > 1:
                return GrowthTrend.EXPONENTIAL
        
        # Linear trends
        if avg_diff > 1:
            return GrowthTrend.LINEAR
        elif avg_diff > -0.5 and avg_diff < 0.5:
            return GrowthTrend.PLATEAU
        elif avg_diff < -1:
            return GrowthTrend.DECLINING
        elif avg_diff < -5:
            return GrowthTrend.DECAYING
        
        return GrowthTrend.STAGNANT
    
    def _calculate_growth_rate(self, snapshots: List[GrowthSnapshot]) -> float:
        """Calculate units per day growth rate"""
        
        if len(snapshots) < 2:
            return 0.0
        
        recent = snapshots[-5:]  # Last 5 measurements
        
        if len(recent) < 2:
            return 0.0
        
        time_span = (recent[-1].timestamp - recent[0].timestamp).total_seconds() / 86400  # days
        value_change = recent[-1].metric_value - recent[0].metric_value
        
        if time_span == 0:
            return 0.0
        
        return value_change / time_span
    
    def _calculate_trend_confidence(self, snapshots: List[GrowthSnapshot]) -> float:
        """How confident are we in the trend? [0,1]"""
        
        # More data points = higher confidence
        data_confidence = min(len(snapshots) / 20.0, 1.0)
        
        # Lower variance = higher confidence
        if len(snapshots) >= 3:
            values = [s.metric_value for s in snapshots[-10:]]
            try:
                variance = statistics.variance(values)
                variance_confidence = 1.0 / (1.0 + variance / 100.0)
            except:
                variance_confidence = 0.5
        else:
            variance_confidence = 0.5
        
        return (data_confidence + variance_confidence) / 2.0
    
    def _predict_peak(
        self,
        snapshots: List[GrowthSnapshot],
        trend: GrowthTrend,
        growth_rate: float
    ) -> Tuple[float, Optional[datetime]]:
        """Predict peak value and when it will occur"""
        
        if not snapshots:
            return 0.0, None
        
        current_value = snapshots[-1].metric_value
        current_time = snapshots[-1].timestamp
        
        # If declining, peak was in the past
        if trend in [GrowthTrend.DECLINING, GrowthTrend.DECAYING]:
            max_snapshot = max(snapshots, key=lambda s: s.metric_value)
            return max_snapshot.metric_value, max_snapshot.timestamp
        
        # If plateau/stagnant, current is peak
        if trend in [GrowthTrend.PLATEAU, GrowthTrend.STAGNANT]:
            return current_value, current_time
        
        # If growing, predict future peak
        if growth_rate > 0:
            # Simple linear projection (could be more sophisticated)
            days_to_peak = (150 - current_value) / growth_rate  # Assume 150 is max capacity
            peak_date = current_time + timedelta(days=days_to_peak)
            return 150.0, peak_date
        
        return current_value, current_time
    
    def _assess_harvest_readiness(
        self,
        current: float,
        predicted_peak: float,
        stage: GrowthStage
    ) -> HarvestReadiness:
        """When should intervention occur?"""
        
        if stage in [GrowthStage.SEED, GrowthStage.GERMINATION]:
            return HarvestReadiness.TOO_EARLY
        
        # Calculate % of peak reached
        if predicted_peak > 0:
            pct_of_peak = current / predicted_peak
            
            if pct_of_peak < 0.5:
                return HarvestReadiness.TOO_EARLY
            elif 0.5 <= pct_of_peak < 0.8:
                return HarvestReadiness.GROWTH_WINDOW
            elif 0.8 <= pct_of_peak < 0.95:
                return HarvestReadiness.PEAK_RIPENESS
            elif 0.95 <= pct_of_peak < 1.1:
                return HarvestReadiness.OVERRIPE
            else:
                return HarvestReadiness.MISSED
        
        return HarvestReadiness.TOO_EARLY
    
    def _detect_cycles(self, snapshots: List[GrowthSnapshot]) -> Tuple[bool, Optional[int]]:
        """Detect if entity follows cyclical pattern"""
        
        if len(snapshots) < 10:
            return False, None
        
        values = [s.metric_value for s in snapshots]
        
        # Simple peak detection
        peaks = []
        for i in range(1, len(values)-1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
        
        # If at least 2 peaks, check if spacing is consistent
        if len(peaks) >= 2:
            spacings = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
            if spacings:
                avg_spacing = statistics.mean(spacings)
                # If spacings are similar (within 20%), it's cyclical
                if all(abs(s - avg_spacing) / avg_spacing < 0.2 for s in spacings):
                    # Convert to days
                    if len(snapshots) >= 2:
                        time_per_snapshot = (snapshots[-1].timestamp - snapshots[0].timestamp).days / len(snapshots)
                        cycle_days = int(avg_spacing * time_per_snapshot)
                        return True, cycle_days
        
        return False, None
    
    def _determine_cycle_phase(self, snapshots: List[GrowthSnapshot]) -> str:
        """Where in the cycle is entity currently?"""
        
        if len(snapshots) < 3:
            return "unknown"
        
        recent = snapshots[-3:]
        values = [s.metric_value for s in recent]
        
        if values[-1] > values[-2] > values[-1]:
            return "ascending"
        elif values[-1] > values[-2] and values[-2] > values[-3]:
            return "peak"
        elif values[-1] < values[-2] < values[-3]:
            return "descending"
        else:
            return "trough"
    
    def _assess_primary_need(
        self,
        stage: GrowthStage,
        trend: GrowthTrend,
        season: Season
    ) -> NourishmentType:
        """What does this entity need most right now?"""
        
        # Winter/dormancy = needs rest
        if season == Season.WINTER or stage == GrowthStage.DORMANCY:
            return NourishmentType.REST
        
        # Declining = needs support or pruning
        if trend in [GrowthTrend.DECLINING, GrowthTrend.DECAYING]:
            return NourishmentType.PRUNING
        
        # Stagnant = needs challenge
        if trend in [GrowthTrend.STAGNANT, GrowthTrend.PLATEAU]:
            return NourishmentType.CHALLENGE
        
        # Early stages = need water (basic sustenance)
        if stage in [GrowthStage.SEED, GrowthStage.GERMINATION, GrowthStage.SPROUT]:
            return NourishmentType.WATER
        
        # Growth stages = need sunlight (exposure to truth)
        if stage in [GrowthStage.VEGETATIVE, GrowthStage.BLOOM]:
            return NourishmentType.SUNLIGHT
        
        # Harvest stages = need space (room to expand)
        if stage in [GrowthStage.FRUIT, GrowthStage.HARVEST]:
            return NourishmentType.SPACE
        
        return NourishmentType.WATER
    
    def _assess_secondary_needs(
        self,
        stage: GrowthStage,
        trend: GrowthTrend
    ) -> List[NourishmentType]:
        """Additional needs beyond primary"""
        
        needs = []
        
        # Growing entities need support
        if trend in [GrowthTrend.EXPONENTIAL, GrowthTrend.LINEAR]:
            needs.append(NourishmentType.SUPPORT)
        
        # Mature entities may need pruning
        if stage in [GrowthStage.BLOOM, GrowthStage.FRUIT]:
            needs.append(NourishmentType.PRUNING)
        
        return needs
    
    def _generate_recommendation(self, profile: GrowthProfile) -> str:
        """What should be done with this entity?"""
        
        stage = profile.current_stage
        trend = profile.growth_trend
        need = profile.primary_need
        season = profile.current_season
        
        if season == Season.WINTER:
            return f"Entity in {season.value} - Allow dormancy, do not force growth. Rest period needed."
        
        if trend == GrowthTrend.DECLINING:
            return f"Declining trend detected - {need.value} needed urgently. Consider intervention."
        
        if profile.harvest_readiness == HarvestReadiness.PEAK_RIPENESS:
            return f"OPTIMAL HARVEST WINDOW - Entity at peak ({stage.value}). Act now."
        
        if profile.harvest_readiness == HarvestReadiness.GROWTH_WINDOW:
            return f"Growth window open - Provide {need.value}, prepare for harvest in {profile.days_until_optimal_harvest} days."
        
        if trend == GrowthTrend.STAGNANT:
            return f"Stagnant growth - Provide {need.value} to resume development."
        
        return f"Continue current trajectory - Provide {need.value} as needed."
    
    def _calculate_optimal_intervention(
        self,
        stage: GrowthStage,
        season: Season,
        current_time: datetime
    ) -> Optional[datetime]:
        """When is the best time to intervene?"""
        
        # Don't intervene in winter
        if season == Season.WINTER:
            return current_time + timedelta(days=30)  # Wait for spring
        
        # Spring/early stages = intervene soon
        if season == Season.SPRING:
            return current_time + timedelta(days=7)
        
        # Summer/growth = intervene now
        if season == Season.SUMMER:
            return current_time
        
        # Autumn/harvest = intervene immediately
        if season == Season.AUTUMN:
            return current_time
        
        return current_time + timedelta(days=14)
    
    def get_growth_profile(self, entity_id: str, metric_name: str) -> Optional[GrowthProfile]:
        """Retrieve growth profile"""
        profile_key = f"{entity_id}:{metric_name}"
        return self.growth_profiles.get(profile_key)
    
    def export_growth_data(self, output_path: str = "demeter_growth_profiles.json"):
        """Export all growth profiles to JSON"""
        
        profiles_data = []
        for key, profile in self.growth_profiles.items():
            profiles_data.append({
                "entity_id": profile.entity_id,
                "metric_name": profile.metric_name,
                "current_stage": profile.current_stage.value,
                "current_season": profile.current_season.value,
                "current_value": profile.current_value,
                "growth_trend": profile.growth_trend.value,
                "growth_rate": profile.growth_rate,
                "predicted_peak": profile.predicted_peak_value,
                "harvest_readiness": profile.harvest_readiness.value,
                "primary_need": profile.primary_need.value,
                "recommendation": profile.intervention_recommendation,
                "data_points": len(profile.snapshots)
            })
        
        with open(output_path, 'w') as f:
            json.dump({"profiles": profiles_data, "total": len(profiles_data)}, f, indent=2)
        
        logger.info(f"🌾 Exported {len(profiles_data)} growth profiles to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("🌾 DEMETER - Goddess of Growth, Harvest, and Seasons")
    print("=" * 60)
    
    demeter = DemeterBot()
    
    # Simulate tracking a Progeny's BR over time
    base_time = datetime.utcnow()
    
    print("\n📊 Tracking Progeny BR over 20 cycles...")
    
    # Simulate growth pattern: slow start, rapid growth, plateau, decline
    br_values = [
        5, 8, 12, 18, 25, 35, 50, 70, 90, 105,  # Growth
        120, 130, 135, 135, 130, 125, 115, 100, 85, 70  # Plateau then decline
    ]
    
    for i, br in enumerate(br_values):
        timestamp = base_time + timedelta(days=i)
        profile = demeter.track_growth(
            entity_id="progeny_001",
            metric_name="benevolence_reservoir",
            metric_value=br,
            timestamp=timestamp
        )
    
    # Display final analysis
    print("\n" + "=" * 60)
    print("🌾 GROWTH ANALYSIS")
    print("=" * 60)
    print(f"Entity: {profile.entity_id}")
    print(f"Metric: {profile.metric_name}")
    print(f"Current Value: {profile.current_value:.2f}")
    print(f"Current Stage: {profile.current_stage.value}")
    print(f"Current Season: {profile.current_season.value}")
    print(f"Growth Trend: {profile.growth_trend.value}")
    print(f"Growth Rate: {profile.growth_rate:.2f} units/day")
    print(f"Predicted Peak: {profile.predicted_peak_value:.2f}")
    print(f"Harvest Readiness: {profile.harvest_readiness.value}")
    print(f"Primary Need: {profile.primary_need.value}")
    if profile.has_cyclical_pattern:
        print(f"Cyclical Pattern: Yes ({profile.cycle_length_days} day cycles)")
    print(f"\n💡 Demeter Recommends:\n   {profile.intervention_recommendation}")
    
    demeter.export_growth_data()

__ASSESSOR_ID__ = 'demeter'


# ---------------------------------------------------------------------------
# Evidence-fed witness path (canonical core) — added 2026-09-22
# ---------------------------------------------------------------------------
# The calculators above take pre-scored structured inputs: whoever calls
# them decides the scores first, and the math launders those guesses into
# authoritative-looking output. They remain for backward compatibility.
#
# New code must use the witness core instead: soul_cradle.assessors holds
# the versioned rubric for this assessor, reads observable evidence (not
# pre-scored inputs), abstains when its domain is not engaged, seals every
# judgment by content hash, and speaks only as WITNESS. See
# soul_cradle/assessors.py for the evidence schema.

def consult_evidence(action_description, evidence):
    """Judge an action as witness. Preferred entry point for new code.

    action_description: plain-words description of the proposed action.
    evidence: dict of evidence-schema keys (see soul_cradle/assessors.py).
    Returns an AssessorJudgment (verdict: clear | flagged | abstain).
    """
    from soul_cradle.assessors import consult
    return consult(__ASSESSOR_ID__, action_description, evidence)
