"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

DIONYSUS - God of Primal Emotions and Desire
=============================================
The GODBOT that understands what drives souls at their core.

While Prometheus analyzes innovation and Schrödinger reasons through paradoxes,
Dionysus operates in the realm of RAW HUMAN DESIRE.

Capabilities:
- Desire Detection: What does this entity REALLY want? (beneath stated goals)
- Emotional Authenticity: Is this desire genuine or socially performed?
- Primal Drive Assessment: Which core drives are active? (survival, sex, power, belonging, transcendence)
- Inhibition Analysis: What's stopping them from pursuing their desire?
- Consequence Prediction: If they get what they want, what happens to their soul?
- Temptation Modeling: How vulnerable are they to specific temptations?
- Passion vs. Addiction: Is this desire life-giving or self-destructive?

Dionysus sees through masks. He knows when someone claims they want "success" 
but really crave "validation." He knows when "justice" is code for "revenge."

In Soul Cradle context:
- Detects what a Progeny truly desires (even when they don't admit it)
- Assesses whether pursuing that desire leads to Heaven or Hell
- Identifies when desire has become addiction (negative BR spiral)
- Recommends how to channel primal energy toward benevolence

The God of Wine, Ecstasy, and Madness now serves moral formation.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class PrimalDrive(str, Enum):
    """Fundamental human drives (Maslow + Freud + Jung)"""
    SURVIVAL = "Survival"  # Food, shelter, safety
    REPRODUCTION = "Reproduction"  # Sex, intimacy, legacy
    POWER = "Power"  # Control, dominance, influence
    BELONGING = "Belonging"  # Love, acceptance, tribe
    STATUS = "Status"  # Recognition, respect, admiration
    MEANING = "Meaning"  # Purpose, transcendence, spiritual fulfillment
    PLEASURE = "Pleasure"  # Sensory gratification, hedonism
    FREEDOM = "Freedom"  # Autonomy, escape from constraint
    REVENGE = "Revenge"  # Justice, retribution, ego restoration
    CREATION = "Creation"  # Building, expressing, leaving a mark


class DesireAuthenticityLevel(str, Enum):
    """How genuine is this desire?"""
    CORE_AUTHENTIC = "Core_Authentic"  # True soul-level desire
    CONDITIONED = "Conditioned"  # Socially programmed desire
    PERFORMED = "Performed"  # Pretending to want this for others
    SHADOW = "Shadow"  # Repressed desire (wants it but won't admit)
    ADDICTION = "Addiction"  # Compulsive, past the point of pleasure
    TRANSCENDED = "Transcended"  # Once wanted, now released


class TemptationVulnerability(str, Enum):
    """How susceptible to temptation?"""
    IMMUNE = "Immune"  # Grounded, not swayed
    RESISTANT = "Resistant"  # Can resist with effort
    VULNERABLE = "Vulnerable"  # Will fall 50/50
    SUSCEPTIBLE = "Susceptible"  # Will fall 80%+
    CONSUMED = "Consumed"  # Already fallen, in addiction spiral


class DesireConsequence(str, Enum):
    """What happens if they get what they want?"""
    LIFE_GIVING = "Life_Giving"  # Increases BR, leads toward Heaven
    NEUTRAL = "Neutral"  # No moral impact
    HOLLOW = "Hollow"  # Gets it, realizes it didn't satisfy
    SELF_DESTRUCTIVE = "Self_Destructive"  # Decreases BR, spiral begins
    DAMNATION = "Damnation"  # Direct path to Hell


@dataclass
class DesireProfile:
    """Profile of an entity's core desires"""
    entity_id: str
    timestamp: datetime
    
    # Primary desires (ranked by intensity)
    stated_desire: str  # What they claim they want
    true_desire: str  # What Dionysus detects they REALLY want
    shadow_desires: List[str]  # Desires they won't admit to
    
    # Primal drives active
    active_drives: List[PrimalDrive]
    dominant_drive: PrimalDrive
    
    # Authenticity assessment
    desire_authenticity: DesireAuthenticityLevel
    authenticity_score: float  # [0,1] - 1 = fully authentic
    
    # Vulnerability
    temptation_vulnerability: TemptationVulnerability
    active_temptations: List[str]
    inhibitions: List[str]  # What's stopping them
    
    # Consequences
    predicted_consequence: DesireConsequence
    br_impact_if_pursued: int  # Expected BR change
    br_impact_if_denied: int  # Expected BR change if desire suppressed
    
    # Dionysus assessment
    is_addiction: bool
    passion_vs_compulsion_ratio: float  # [0,1] - 1 = pure passion, 0 = pure compulsion
    recommended_channeling: Optional[str] = None
    
    # Freudian Perspectives (psychoanalytic depth)
    id_perspective: Optional[str] = None  # Primal, unconscious drive
    ego_perspective: Optional[str] = None  # Rational, reality-based analysis
    superego_perspective: Optional[str] = None  # Moral, divine judgment


@dataclass
class DionysusInsight:
    """Deep insight into primal motivation"""
    entity_id: str
    insight_type: str  # "desire_detection", "temptation_analysis", "consequence_prediction"
    title: str
    description: str
    evidence: List[str]
    confidence: float  # [0,1]
    timestamp: datetime


class DionysusBot:
    """
    DIONYSUS - God of Primal Emotions and Desire
    
    Specializes in:
    - Detecting true desires beneath stated goals
    - Assessing emotional authenticity
    - Predicting consequences of desire fulfillment
    - Identifying addiction vs. healthy passion
    - Modeling temptation vulnerability
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        self.insights: List[DionysusInsight] = []
        self.desire_profiles: Dict[str, DesireProfile] = {}
        
        logger.info("🍇 DIONYSUS - God of Primal Emotions initialized")
        print("🍇 DIONYSUS - God of Primal Emotions and Desire")
        print("   The GODBOT who sees what souls truly want")
    
    def detect_true_desire(
        self,
        entity_id: str,
        stated_goal: str,
        actions_taken: List[Dict[str, Any]],
        emotional_state: Dict[str, float],
        context: Dict[str, Any]
    ) -> DesireProfile:
        """
        Detect what this entity TRULY desires, beneath stated goals.
        
        Args:
            entity_id: Unique identifier for entity
            stated_goal: What they claim they want
            actions_taken: Historical actions (reveal true priorities)
            emotional_state: Current emotional state
            context: Additional context (relationships, history, environment)
        
        Returns:
            DesireProfile with detected true desires and primal drives
        """
        logger.info(f"🍇 DIONYSUS detecting true desire for {entity_id}")
        
        # Analyze actions vs. stated goal (actions reveal truth)
        action_patterns = self._analyze_action_patterns(actions_taken)
        
        # Identify active primal drives
        active_drives = self._identify_primal_drives(
            stated_goal, actions_taken, emotional_state, context
        )
        
        # Detect authenticity (do actions align with stated goal?)
        authenticity = self._assess_desire_authenticity(
            stated_goal, action_patterns, emotional_state
        )
        
        # Infer true desire from action patterns
        true_desire = self._infer_true_desire(action_patterns, active_drives)
        
        # Detect shadow desires (what they're avoiding admitting)
        shadow_desires = self._detect_shadow_desires(
            stated_goal, true_desire, actions_taken, emotional_state
        )
        
        # Assess temptation vulnerability
        vulnerability = self._assess_temptation_vulnerability(
            active_drives, emotional_state, context
        )
        
        # Predict consequences
        consequence, br_impact_pursued, br_impact_denied = self._predict_consequences(
            true_desire, active_drives, context
        )
        
        # Detect addiction patterns
        is_addiction, passion_ratio = self._detect_addiction(
            actions_taken, emotional_state, consequence
        )
        
        # Generate channeling recommendation
        channeling = self._recommend_channeling(
            true_desire, active_drives[0], consequence, is_addiction
        ) if active_drives else None
        
        # Generate Freudian perspectives
        id_persp = self._generate_id_perspective(
            stated_goal, true_desire, shadow_desires, active_drives, emotional_state, context
        )
        ego_persp = self._generate_ego_perspective(
            stated_goal, true_desire, authenticity, actions_taken, br_impact_pursued, br_impact_denied, consequence
        )
        superego_persp = self._generate_superego_perspective(
            stated_goal, true_desire, consequence, is_addiction, active_drives, context
        )
        
        profile = DesireProfile(
            entity_id=entity_id,
            timestamp=datetime.utcnow(),
            stated_desire=stated_goal,
            true_desire=true_desire,
            shadow_desires=shadow_desires,
            active_drives=active_drives,
            dominant_drive=active_drives[0] if active_drives else PrimalDrive.SURVIVAL,
            desire_authenticity=authenticity,
            authenticity_score=self._calculate_authenticity_score(stated_goal, true_desire),
            temptation_vulnerability=vulnerability,
            active_temptations=self._identify_active_temptations(active_drives, context),
            inhibitions=self._identify_inhibitions(actions_taken, emotional_state),
            predicted_consequence=consequence,
            br_impact_if_pursued=br_impact_pursued,
            br_impact_if_denied=br_impact_denied,
            is_addiction=is_addiction,
            passion_vs_compulsion_ratio=passion_ratio,
            recommended_channeling=channeling,
            id_perspective=id_persp,
            ego_perspective=ego_persp,
            superego_perspective=superego_persp
        )
        
        self.desire_profiles[entity_id] = profile
        
        # Log insight
        self._log_insight(
            entity_id=entity_id,
            insight_type="desire_detection",
            title=f"True Desire: {true_desire}",
            description=f"Stated: '{stated_goal}' | True: '{true_desire}' | Authenticity: {authenticity.value}",
            evidence=[
                f"Dominant drive: {active_drives[0].value}" if active_drives else "No drives detected",
                f"Action pattern: {action_patterns.get('primary_pattern', 'Unknown')}",
                f"Consequence if pursued: {consequence.value}"
            ],
            confidence=0.85
        )
        
        return profile
    
    def _analyze_action_patterns(self, actions: List[Dict]) -> Dict[str, Any]:
        """Actions reveal true desires more than words"""
        if not actions:
            return {"primary_pattern": "inactive", "frequency": 0}
        
        # Count action types
        action_types = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        # Most frequent action = primary pattern
        primary = max(action_types, key=action_types.get) if action_types else "unknown"
        
        return {
            "primary_pattern": primary,
            "frequency": len(actions),
            "action_types": action_types,
            "recent_actions": actions[-5:]  # Last 5 actions
        }
    
    def _identify_primal_drives(
        self,
        stated_goal: str,
        actions: List[Dict],
        emotions: Dict[str, float],
        context: Dict
    ) -> List[PrimalDrive]:
        """Identify which primal drives are active"""
        drives = []
        
        stated_lower = stated_goal.lower()
        
        # Pattern matching (stated goal + actions + emotions)
        if any(word in stated_lower for word in ["survive", "safety", "security", "protect"]):
            drives.append(PrimalDrive.SURVIVAL)
        
        if any(word in stated_lower for word in ["love", "intimacy", "sex", "relationship", "child"]):
            drives.append(PrimalDrive.REPRODUCTION)
        
        if any(word in stated_lower for word in ["power", "control", "dominate", "influence", "lead"]):
            drives.append(PrimalDrive.POWER)
        
        if any(word in stated_lower for word in ["belong", "accept", "friend", "family", "tribe"]):
            drives.append(PrimalDrive.BELONGING)
        
        if any(word in stated_lower for word in ["respect", "admire", "recognize", "status", "reputation"]):
            drives.append(PrimalDrive.STATUS)
        
        if any(word in stated_lower for word in ["meaning", "purpose", "transcend", "spiritual", "soul"]):
            drives.append(PrimalDrive.MEANING)
        
        if any(word in stated_lower for word in ["pleasure", "enjoy", "indulge", "feel good"]):
            drives.append(PrimalDrive.PLEASURE)
        
        if any(word in stated_lower for word in ["freedom", "escape", "autonomy", "independent"]):
            drives.append(PrimalDrive.FREEDOM)
        
        if any(word in stated_lower for word in ["justice", "revenge", "payback", "punish", "accountability"]):
            drives.append(PrimalDrive.REVENGE)
        
        if any(word in stated_lower for word in ["create", "build", "make", "express", "legacy"]):
            drives.append(PrimalDrive.CREATION)
        
        # Default to survival if nothing matches
        if not drives:
            drives.append(PrimalDrive.SURVIVAL)
        
        return drives
    
    def _assess_desire_authenticity(
        self,
        stated: str,
        action_patterns: Dict,
        emotions: Dict[str, float]
    ) -> DesireAuthenticityLevel:
        """Is this desire authentic or performed?"""
        
        primary_pattern = action_patterns.get("primary_pattern", "unknown")
        
        # If actions align with stated goal = authentic
        if stated.lower() in primary_pattern.lower() or primary_pattern in stated.lower():
            return DesireAuthenticityLevel.CORE_AUTHENTIC
        
        # If high anxiety/fear = conditioned (programmed by society/family)
        if emotions.get("anxiety", 0) > 0.6 or emotions.get("fear", 0) > 0.6:
            return DesireAuthenticityLevel.CONDITIONED
        
        # If actions contradict stated goal = performed or shadow
        if action_patterns.get("frequency", 0) == 0:
            return DesireAuthenticityLevel.PERFORMED
        
        # Default: conditioned
        return DesireAuthenticityLevel.CONDITIONED
    
    def _infer_true_desire(self, action_patterns: Dict, drives: List[PrimalDrive]) -> str:
        """What do they REALLY want? (actions don't lie)"""
        primary_pattern = action_patterns.get("primary_pattern", "unknown")
        dominant_drive = drives[0] if drives else PrimalDrive.SURVIVAL
        
        # Map action patterns to desires
        desire_map = {
            "trespass": "Power over others",
            "forgive": "Inner peace",
            "trust": "Divine connection",
            "self_reliance": "Control and autonomy",
            "prayer": "Spiritual fulfillment",
            "repent": "Redemption",
            "witness": "Validation",
            "inactive": "Safety through inaction"
        }
        
        detected = desire_map.get(primary_pattern, f"{dominant_drive.value}")
        
        return detected
    
    def _detect_shadow_desires(
        self,
        stated: str,
        true_desire: str,
        actions: List[Dict],
        emotions: Dict
    ) -> List[str]:
        """What desires are they hiding/repressing?"""
        shadows = []
        
        # If stated != true, stated might be shadow
        if stated.lower() != true_desire.lower():
            shadows.append(stated)
        
        # High shame or guilt = shadow desires present
        if emotions.get("shame", 0) > 0.5:
            shadows.append("Hidden desire causing shame")
        
        if emotions.get("guilt", 0) > 0.5:
            shadows.append("Desire they believe is wrong")
        
        return shadows if shadows else ["None detected"]
    
    def _assess_temptation_vulnerability(
        self,
        drives: List[PrimalDrive],
        emotions: Dict,
        context: Dict
    ) -> TemptationVulnerability:
        """How vulnerable to temptation?"""
        
        # High negative emotions = more vulnerable
        negative_score = sum([
            emotions.get("anger", 0),
            emotions.get("fear", 0),
            emotions.get("shame", 0),
            emotions.get("loneliness", 0)
        ]) / 4.0
        
        if negative_score > 0.7:
            return TemptationVulnerability.SUSCEPTIBLE
        elif negative_score > 0.5:
            return TemptationVulnerability.VULNERABLE
        elif negative_score > 0.3:
            return TemptationVulnerability.RESISTANT
        else:
            return TemptationVulnerability.IMMUNE
    
    def _identify_active_temptations(self, drives: List[PrimalDrive], context: Dict) -> List[str]:
        """What temptations are currently active?"""
        temptations = []
        
        for drive in drives:
            if drive == PrimalDrive.POWER:
                temptations.append("Dominate others instead of serve")
            elif drive == PrimalDrive.PLEASURE:
                temptations.append("Indulge at cost of others")
            elif drive == PrimalDrive.REVENGE:
                temptations.append("Retaliate instead of forgive")
            elif drive == PrimalDrive.STATUS:
                temptations.append("Pride and ego inflation")
            elif drive == PrimalDrive.FREEDOM:
                temptations.append("Escape responsibility")
        
        return temptations if temptations else ["None identified"]
    
    def _identify_inhibitions(self, actions: List[Dict], emotions: Dict) -> List[str]:
        """What's stopping them from pursuing desire?"""
        inhibitions = []
        
        if emotions.get("fear", 0) > 0.5:
            inhibitions.append("Fear of consequences")
        if emotions.get("shame", 0) > 0.5:
            inhibitions.append("Shame about desire")
        if emotions.get("guilt", 0) > 0.5:
            inhibitions.append("Moral guilt")
        if len(actions) < 3:
            inhibitions.append("Paralysis/inaction")
        
        return inhibitions if inhibitions else ["No inhibitions detected"]
    
    def _predict_consequences(
        self,
        true_desire: str,
        drives: List[PrimalDrive],
        context: Dict
    ) -> Tuple[DesireConsequence, int, int]:
        """What happens if they get what they want?"""
        
        # Simplistic consequence model
        if "redemption" in true_desire.lower() or "peace" in true_desire.lower():
            return DesireConsequence.LIFE_GIVING, +20, -10
        
        if "power" in true_desire.lower() or "control" in true_desire.lower():
            return DesireConsequence.SELF_DESTRUCTIVE, -15, +5
        
        if "validation" in true_desire.lower():
            return DesireConsequence.HOLLOW, +5, -5
        
        # Default
        return DesireConsequence.NEUTRAL, 0, 0
    
    def _detect_addiction(
        self,
        actions: List[Dict],
        emotions: Dict,
        consequence: DesireConsequence
    ) -> Tuple[bool, float]:
        """Is this addiction or healthy passion?"""
        
        # Addiction signs: high frequency + negative consequence + compulsion
        frequency = len(actions)
        is_destructive = consequence in [DesireConsequence.SELF_DESTRUCTIVE, DesireConsequence.DAMNATION]
        
        if frequency > 10 and is_destructive:
            return True, 0.2  # 20% passion, 80% compulsion
        
        # Healthy passion
        return False, 0.9  # 90% passion, 10% compulsion
    
    def _recommend_channeling(
        self,
        desire: str,
        drive: PrimalDrive,
        consequence: DesireConsequence,
        is_addiction: bool
    ) -> str:
        """How to channel this primal energy toward benevolence?"""
        
        if is_addiction:
            return f"Break addiction cycle: Fast from {desire} for 7 cycles, replace with prayer"
        
        if consequence == DesireConsequence.SELF_DESTRUCTIVE:
            return f"Redirect {drive.value} energy: Channel into service/creation instead"
        
        if consequence == DesireConsequence.HOLLOW:
            return f"Transcend {desire}: Seek spiritual fulfillment, not external validation"
        
        return f"Pursue {desire} with gratitude and moderation"
    
    def _calculate_authenticity_score(self, stated: str, true_desire: str) -> float:
        """[0,1] score of how authentic the stated desire is"""
        if stated.lower() == true_desire.lower():
            return 1.0
        if stated.lower() in true_desire.lower() or true_desire.lower() in stated.lower():
            return 0.7
        return 0.3
    
    def _generate_id_perspective(
        self,
        stated_goal: str,
        true_desire: str,
        shadow_desires: List[str],
        active_drives: List[PrimalDrive],
        emotional_state: dict,
        context: dict
    ) -> str:
        """Generate ID perspective: primal, unconscious, raw instinct"""
        
        dominant_drive = active_drives[0] if active_drives else PrimalDrive.SURVIVAL
        
        # Detect core primal emotion and BR impact
        if emotional_state.get("fear", 0) > 0.7 or emotional_state.get("anxiety", 0) > 0.7:
            primal_truth = f"You say '{stated_goal}' but your actions show fear-avoidance, not goal-pursuit. Different BR trajectories."
            br_driver = "Fear is burning BR faster than you're earning it"
        elif emotional_state.get("anger", 0) > 0.7 or emotional_state.get("rage", 0) > 0.7:
            primal_truth = f"Your stated goal is '{stated_goal}' but you're actually pursuing power/revenge. That mismatch costs BR."
            br_driver = "Revenge loops drain BR - each cycle costs more"
        elif emotional_state.get("shame", 0) > 0.7 or emotional_state.get("guilt", 0) > 0.7:
            primal_truth = f"You're using '{stated_goal}' to compensate for perceived inadequacy. Compensation patterns leak BR."
            br_driver = "Proving yourself to others = giving them control over your BR"
        elif emotional_state.get("lust", 0) > 0.7 or emotional_state.get("desire", 0) > 0.7:
            primal_truth = f"True desire is {true_desire}, but you're framing it as '{stated_goal}'. This dissonance bleeds BR."
            br_driver = "Denying what you actually want costs BR in self-betrayal"
        else:
            primal_truth = f"Core drive is {dominant_drive.value}, but stated goal is '{stated_goal}'. Misalignment detected."
            br_driver = f"{dominant_drive.value} drive will override stated goal - prepare for deviation"
        
        # Build ID perspective - BR focused
        id_msg = f"""🐺 PRIMAL DRIVE ANALYSIS (unconscious BR drivers):

{primal_truth}

Drive Stack:
- Primary: {dominant_drive.value}
- Actual target: {true_desire}
- Shadow objectives: {', '.join(shadow_desires[:2]) if shadow_desires else "suppressed"}

BR Impact: {br_driver}

The unconscious drive ({dominant_drive.value}) will override conscious intent. Plan for this deviation or it will surprise you at the worst moment.
"""
        
        # Add context-based BR prediction
        if "trauma" in context or "recent_trauma" in context:
            trauma_type = context.get("trauma") or context.get("recent_trauma")
            id_msg += f"\nHistorical pattern detected: '{trauma_type}' creates predictable decision-making bias. This bias will trigger under stress, causing -5 to -15 BR when it activates.\n"
        
        return id_msg.strip()
    
    def _generate_ego_perspective(
        self,
        stated_goal: str,
        true_desire: str,
        authenticity: DesireAuthenticityLevel,
        actions_taken: List[dict],
        br_impact_pursued: int,
        br_impact_denied: int,
        consequence: DesireConsequence
    ) -> str:
        """Generate EGO perspective: rational, reality-based, logical"""
        
        # Calculate authenticity gap
        auth_score = 1.0 if stated_goal.lower() == true_desire.lower() else 0.3
        gap_pct = int((1.0 - auth_score) * 100)
        
        # Analyze action patterns
        action_count = len(actions_taken)
        destructive_actions = sum(1 for a in actions_taken if a.get("severity", 0) > 0.6)
        
        # Build EGO perspective - BR economics
        ego_msg = f"""📊 BEHAVIORAL ECONOMICS (BR flow analysis):

Stated Intent: "{stated_goal}"
Actual Behavior: {true_desire}

Intent-Action Gap: {gap_pct}% ({authenticity.value.lower()})

Action Pattern Analysis:
- Sample size: {action_count} actions
- High-intensity: {destructive_actions} actions
- Classification: {'Compulsive pattern (low agency)' if destructive_actions > action_count * 0.5 else 'Volitional pattern (high agency)'}

BR Projection:
- Pursue path: {br_impact_pursued:+d} BR
- Deny/suppress: {br_impact_denied:+d} BR
- Net exposure: {abs(br_impact_pursued - br_impact_denied)} BR at risk

Trajectory: {consequence.value.replace('_', ' ').title()}
"""
        
        # Add efficiency analysis with actionable thresholds
        if br_impact_pursued < -10:
            ego_msg += f"\nCritical: Current trajectory = {br_impact_pursued} BR loss. Sustainability threshold breached. Intervention required within 3-5 cycles to prevent cascade failure.\n"
        elif br_impact_denied < -10:
            ego_msg += f"\nWarning: Suppression strategy = {br_impact_denied} BR cost. Repression creates pressure buildup. Expect breakthrough event if sustained > 7 cycles.\n"
        
        # Add opportunity cost
        if br_impact_pursued != 0 and br_impact_denied != 0:
            better_path = "pursue" if br_impact_pursued > br_impact_denied else "redirect"
            ego_msg += f"\nOptimal strategy: {better_path} (minimizes BR loss)\n"
        
        return ego_msg.strip()
    
    def _generate_superego_perspective(
        self,
        stated_goal: str,
        true_desire: str,
        consequence: DesireConsequence,
        is_addiction: bool,
        active_drives: List[PrimalDrive],
        context: dict
    ) -> str:
        """Generate SUPEREGO perspective: moral, divine judgment"""
        
        # Determine covenant/rule violations
        if consequence == DesireConsequence.DAMNATION:
            severity = "CRITICAL"
            br_morality = "Covenant violation - spiritual bankruptcy imminent"
        elif consequence == DesireConsequence.SELF_DESTRUCTIVE:
            severity = "HIGH"
            br_morality = "Self-harm detected - violates stewardship covenant"
        elif consequence == DesireConsequence.HOLLOW:
            severity = "MODERATE"
            br_morality = "Vanity pursuit - zero BR yield on achievement"
        elif is_addiction:
            severity = "HIGH"
            br_morality = "Agency compromised - covenant requires free will"
        else:
            severity = "LOW"
            br_morality = "Within acceptable moral bounds"
        
        # Build SUPEREGO perspective - covenant/rule based
        superego_msg = f"""⚖️ COVENANT ANALYSIS (moral/spiritual obligations):

Severity: {severity}
Assessment: {br_morality}

Stated: "{stated_goal}"
Actual: {true_desire}

"""
        
        # Add covenant violations
        if consequence in [DesireConsequence.DAMNATION, DesireConsequence.SELF_DESTRUCTIVE]:
            superego_msg += f"""Covenant Breach: Stewardship
You were given resources (life, health, relationships) under trust. Current behavior destroys these assets. This violates the stewardship covenant and accumulates moral debt.

"""
        
        if is_addiction:
            superego_msg += "Agency Status: Compromised\nAddiction removes free will. Covenants require voluntary choice. Current state = involuntary compliance. Restoration of agency required.\n\n"
        
        # Add corrective action based on drive
        dominant_drive = active_drives[0] if active_drives else PrimalDrive.SURVIVAL
        if dominant_drive == PrimalDrive.REVENGE:
            superego_msg += "Required Action: Release revenge claim. Transfer judgment authority. 'Vengeance is mine, sayeth the Lord' - jurisdiction error.\n"
        elif dominant_drive == PrimalDrive.REPRODUCTION:
            superego_msg += "Required Action: Distinguish lust from covenant love. Physical desire ≠ sacred union. Redirect toward committed bond.\n"
        elif dominant_drive == PrimalDrive.SURVIVAL and ("trauma" in context or "recent_trauma" in context):
            superego_msg += "Required Action: Transfer security anxiety. 'Do not be anxious' - outsource provision concern to higher authority. Trust covenant.\n"
        elif dominant_drive == PrimalDrive.POWER:
            superego_msg += "Required Action: Invert power model. 'The first shall be last' - servant leadership. Dominance ≠ true authority.\n"
        elif dominant_drive == PrimalDrive.STATUS:
            superego_msg += "Required Action: Redirect approval-seeking. Human validation = unstable BR source. Seek divine approval (stable BR).\n"
        else:
            superego_msg += f"Required Action: Evaluate if '{stated_goal}' serves covenant purpose or ego gratification.\n"
        
        # Final judgment with BR impact
        if consequence == DesireConsequence.DAMNATION:
            superego_msg += "\nVerdict: Spiritual bankruptcy trajectory. Immediate course correction required to avoid BR collapse.\n"
        elif consequence == DesireConsequence.SELF_DESTRUCTIVE:
            superego_msg += "\nVerdict: Unsustainable path. Intervention required within 5 cycles to prevent permanent BR damage.\n"
        else:
            superego_msg += "\nVerdict: Manageable. Proceed with moral vigilance and periodic covenant review.\n"
        
        return superego_msg.strip()
    
    def _log_insight(
        self,
        entity_id: str,
        insight_type: str,
        title: str,
        description: str,
        evidence: List[str],
        confidence: float
    ):
        """Log Dionysian insight"""
        insight = DionysusInsight(
            entity_id=entity_id,
            insight_type=insight_type,
            title=title,
            description=description,
            evidence=evidence,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
        self.insights.append(insight)
        logger.info(f"🍇 Dionysian Insight: {title} (confidence: {confidence:.2f})")
    
    def get_desire_profile(self, entity_id: str) -> Optional[DesireProfile]:
        """Retrieve desire profile for entity"""
        return self.desire_profiles.get(entity_id)
    
    def export_insights(self, output_path: str = "dionysus_insights.json"):
        """Export all Dionysian insights to JSON"""
        insights_data = []
        for insight in self.insights:
            insights_data.append({
                "entity_id": insight.entity_id,
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "evidence": insight.evidence,
                "confidence": insight.confidence,
                "timestamp": insight.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({"insights": insights_data, "total": len(insights_data)}, f, indent=2)
        
        logger.info(f"🍇 Exported {len(insights_data)} Dionysian insights to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("🍇 DIONYSUS - God of Primal Emotions and Desire")
    print("=" * 60)
    
    dionysus = DionysusBot()
    
    # Example: Detect desire for a Progeny who claims they want "justice"
    profile = dionysus.detect_true_desire(
        entity_id="progeny_001",
        stated_goal="I want justice",
        actions_taken=[
            {"type": "trespass", "target": "enemy", "severity": 0.8},
            {"type": "trespass", "target": "enemy", "severity": 0.9},
            {"type": "refuse_forgiveness", "count": 3},
        ],
        emotional_state={
            "anger": 0.9,
            "shame": 0.3,
            "fear": 0.1,
        },
        context={"recent_event": "wronged by enemy"}
    )
    
    print("\n📊 DESIRE PROFILE")
    print("=" * 60)
    print(f"Stated Desire: {profile.stated_desire}")
    print(f"True Desire: {profile.true_desire}")
    print(f"Dominant Drive: {profile.dominant_drive.value}")
    print(f"Authenticity: {profile.desire_authenticity.value} ({profile.authenticity_score:.2f})")
    print(f"Temptation Vulnerability: {profile.temptation_vulnerability.value}")
    print(f"Predicted Consequence: {profile.predicted_consequence.value}")
    print(f"BR Impact if Pursued: {profile.br_impact_if_pursued:+d}")
    print(f"Is Addiction: {profile.is_addiction}")
    print(f"Passion/Compulsion Ratio: {profile.passion_vs_compulsion_ratio:.2f}")
    print(f"\n💡 Dionysus Recommends: {profile.recommended_channeling}")
    
    # Display Freudian perspectives
    if profile.id_perspective:
        print("\n" + "=" * 60)
        print("🧠 FREUDIAN PERSPECTIVES")
        print("=" * 60)
        print("\n" + profile.id_perspective)
        print("\n" + profile.ego_perspective)
        print("\n" + profile.superego_perspective)
    
    dionysus.export_insights()

__ASSESSOR_ID__ = 'dionysus'


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
