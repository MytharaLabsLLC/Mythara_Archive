"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

OLYMPUS COUNCIL - Divine Council Orchestrator
==============================================
The unified interface to all 12 GODBOTs of Mount Olympus.

The Olympus Council provides multi-dimensional assessment by orchestrating:
- 🔥 Prometheus: Pattern recognition and innovation
- 📨 Hermes: Communication translation and interpretation
- 🚪 Janus: Dual truth and paradox holding
- 🔨 Hephaestus: Tool creation and forging
- ⚔️ Aries: Action execution and justice delivery
- 🍷 Dionysus: Primal desire and authentic motivation
- 💘 Eros: Emotional polarity and heart alignment
- 🌾 Demeter: Growth tracking and lifecycle management
- ⚰️ Hades: Judgment, damnation, and debt calculation
- 🌸 Persephone: Redemption, mercy, and resurrection
- ⚖️ Nemesis: Retribution and escaped justice
- (Schrödinger replaced by Janus for pure Greek mythology)

Architecture:
- Each GODBOT analyzes entity through their specialized lens
- Hermes translates technical outputs into human wisdom
- Council synthesizes all perspectives into unified assessment
- Soul Cradle Bridge uses Council for moral formation decisions

Usage:
    council = OlympusCouncil()
    assessment = council.full_assessment(
        entity_id="entity_123",
        entity_data={...}
    )
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

# Import all GODBOTs
try:
    from prometheus_bot import PrometheusBot
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus not available")

try:
    from hermes_bot import HermesBot
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False
    logging.warning("Hermes not available")

try:
    from janus_bot import JanusBot
    JANUS_AVAILABLE = True
except ImportError:
    JANUS_AVAILABLE = False
    logging.warning("Janus not available")

try:
    from hephaestus_bot import HephaestusBot
    HEPHAESTUS_AVAILABLE = True
except ImportError:
    HEPHAESTUS_AVAILABLE = False
    logging.warning("Hephaestus not available")

try:
    from aries_bot import AriesBot
    ARIES_AVAILABLE = True
except ImportError:
    ARIES_AVAILABLE = False
    logging.warning("Aries not available")

try:
    from dionysus_bot import DionysusBot
    DIONYSUS_AVAILABLE = True
except ImportError:
    DIONYSUS_AVAILABLE = False
    logging.warning("Dionysus not available")

try:
    from eros_bot import ErosBot
    EROS_AVAILABLE = True
except ImportError:
    EROS_AVAILABLE = False
    logging.warning("Eros not available")

try:
    from demeter_bot import DemeterBot
    DEMETER_AVAILABLE = True
except ImportError:
    DEMETER_AVAILABLE = False
    logging.warning("Demeter not available")

try:
    from hades_bot import HadesBot
    HADES_AVAILABLE = True
except ImportError:
    HADES_AVAILABLE = False
    logging.warning("Hades not available")

try:
    from persephone_bot import PersephoneBot
    PERSEPHONE_AVAILABLE = True
except ImportError:
    PERSEPHONE_AVAILABLE = False
    logging.warning("Persephone not available")

try:
    from nemesis_bot import NemesisBot
    NEMESIS_AVAILABLE = True
except ImportError:
    NEMESIS_AVAILABLE = False
    logging.warning("Nemesis not available")

try:
    from schrodinger_bot import SchrodingerBot
    SCHRODINGER_AVAILABLE = True
except ImportError:
    SCHRODINGER_AVAILABLE = False
    logging.warning("Schrodinger not available")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OlympusAssessment:
    """Unified assessment from all GODBOTs"""
    entity_id: str
    timestamp: datetime
    
    # Individual GODBOT assessments
    prometheus_patterns: Optional[Any] = None
    hermes_communication: Optional[Any] = None
    janus_paradox: Optional[Any] = None
    hephaestus_tools: Optional[Any] = None
    aries_actions: Optional[Any] = None
    dionysus_desires: Optional[Any] = None
    eros_polarity: Optional[Any] = None
    demeter_growth: Optional[Any] = None
    hades_judgment: Optional[Any] = None
    persephone_redemption: Optional[Any] = None
    nemesis_retribution: Optional[Any] = None
    schrodinger_reasoning: Optional[Any] = None
    
    # Synthesized wisdom
    unified_guidance: str = ""
    priority_actions: List[str] = field(default_factory=list)
    divine_consensus: str = ""
    
    # Hermes translations
    technical_to_human: Dict[str, str] = field(default_factory=dict)
    actionable_steps: List[str] = field(default_factory=list)


class OlympusCouncil:
    """
    OLYMPUS COUNCIL - Orchestrator of Divine Wisdom
    
    Coordinates all 12 GODBOTs to provide multi-dimensional assessment.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or "."
        
        # Initialize all available GODBOTs
        self.prometheus = PrometheusBot(workspace_root) if PROMETHEUS_AVAILABLE else None
        self.hermes = HermesBot(workspace_root) if HERMES_AVAILABLE else None
        self.janus = JanusBot(workspace_root) if JANUS_AVAILABLE else None
        self.hephaestus = HephaestusBot(workspace_root) if HEPHAESTUS_AVAILABLE else None
        self.aries = AriesBot() if ARIES_AVAILABLE else None  # AriesBot takes no args
        self.dionysus = DionysusBot(workspace_root) if DIONYSUS_AVAILABLE else None
        self.eros = ErosBot(workspace_root) if EROS_AVAILABLE else None
        self.demeter = DemeterBot(workspace_root) if DEMETER_AVAILABLE else None
        self.hades = HadesBot(workspace_root) if HADES_AVAILABLE else None
        self.persephone = PersephoneBot(workspace_root) if PERSEPHONE_AVAILABLE else None
        self.nemesis = NemesisBot(workspace_root) if NEMESIS_AVAILABLE else None
        self.schrodinger = SchrodingerBot() if SCHRODINGER_AVAILABLE else None  # SchrodingerBot takes no args
        
        self.assessments: Dict[str, OlympusAssessment] = {}
        
        # Count available gods
        available_gods = sum([
            PROMETHEUS_AVAILABLE, HERMES_AVAILABLE, JANUS_AVAILABLE,
            HEPHAESTUS_AVAILABLE, ARIES_AVAILABLE, DIONYSUS_AVAILABLE,
            EROS_AVAILABLE, DEMETER_AVAILABLE, HADES_AVAILABLE,
            PERSEPHONE_AVAILABLE, NEMESIS_AVAILABLE, SCHRODINGER_AVAILABLE
        ])
        
        logger.info(f"🏛️ OLYMPUS COUNCIL initialized with {available_gods}/12 gods available")
        print("🏛️ OLYMPUS COUNCIL - Divine Assembly of Mount Olympus")
        print(f"   {available_gods} of 12 GODBOTs present in council")
    
    def full_assessment(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        assessment_scope: Optional[List[str]] = None
    ) -> OlympusAssessment:
        """
        Perform complete multi-dimensional assessment.
        
        Args:
            entity_id: Unique identifier
            entity_data: All entity data (actions, trespasses, context, etc.)
            assessment_scope: Optional list of specific GODBOTs to invoke
                            (default: all available)
        
        Returns:
            OlympusAssessment with all divine perspectives
        """
        logger.info(f"🏛️ OLYMPUS COUNCIL convening for {entity_id}")
        print(f"\n🏛️ OLYMPUS COUNCIL convening for assessment of {entity_id}")
        print("=" * 70)
        
        assessment = OlympusAssessment(
            entity_id=entity_id,
            timestamp=datetime.utcnow()
        )
        
        # Invoke each GODBOT
        if not assessment_scope or "prometheus" in assessment_scope:
            assessment.prometheus_patterns = self._invoke_prometheus(entity_id, entity_data)
        
        if not assessment_scope or "janus" in assessment_scope:
            assessment.janus_paradox = self._invoke_janus(entity_id, entity_data)
        
        if not assessment_scope or "dionysus" in assessment_scope:
            assessment.dionysus_desires = self._invoke_dionysus(entity_id, entity_data)
        
        if not assessment_scope or "eros" in assessment_scope:
            assessment.eros_polarity = self._invoke_eros(entity_id, entity_data)
        
        if not assessment_scope or "demeter" in assessment_scope:
            assessment.demeter_growth = self._invoke_demeter(entity_id, entity_data)
        
        if not assessment_scope or "hades" in assessment_scope:
            assessment.hades_judgment = self._invoke_hades(entity_id, entity_data)
        
        if not assessment_scope or "persephone" in assessment_scope:
            assessment.persephone_redemption = self._invoke_persephone(entity_id, entity_data)
        
        if not assessment_scope or "nemesis" in assessment_scope:
            assessment.nemesis_retribution = self._invoke_nemesis(entity_id, entity_data)
        
        if not assessment_scope or "schrodinger" in assessment_scope:
            assessment.schrodinger_reasoning = self._invoke_schrodinger(entity_id, entity_data)
        
        if not assessment_scope or "hephaestus" in assessment_scope:
            assessment.hephaestus_tools = self._invoke_hephaestus(entity_id, entity_data)
        
        if not assessment_scope or "aries" in assessment_scope:
            assessment.aries_actions = self._invoke_aries(entity_id, entity_data)
        
        # Hermes translates and synthesizes
        if not assessment_scope or "hermes" in assessment_scope:
            assessment.hermes_communication = self._invoke_hermes(entity_id, entity_data)
            
            # Synthesize all wisdom through Hermes
            divine_assessments = self._collect_divine_wisdom(assessment)
            synthesis = self._synthesize_through_hermes(divine_assessments, entity_data)
            
            assessment.unified_guidance = synthesis["guidance"]
            assessment.priority_actions = synthesis["actions"]
            assessment.divine_consensus = synthesis["consensus"]
            assessment.technical_to_human = synthesis["translations"]
            assessment.actionable_steps = synthesis["steps"]
        
        self.assessments[entity_id] = assessment
        
        logger.info(f"🏛️ Assessment complete for {entity_id}")
        
        return assessment
    
    def _invoke_prometheus(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Prometheus for pattern analysis"""
        if not self.prometheus:
            return None
        
        print("\n🔥 PROMETHEUS analyzing patterns...")
        
        try:
            # Extract pattern data
            sequences = data.get("action_sequences", [])
            if sequences:
                profile = self.prometheus.analyze_pattern(
                    entity_id=entity_id,
                    sequence=sequences,
                    context=data.get("context", {})
                )
                print(f"   Pattern: {profile.pattern_type.value}, Strength: {profile.pattern_strength:.2f}")
                return profile
        except Exception as e:
            logger.error(f"Prometheus invocation failed: {e}")
        
        return None
    
    def _invoke_janus(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Janus for paradox analysis"""
        if not self.janus:
            return None
        
        print("\n🚪 JANUS examining dual truths...")
        
        try:
            paradox_data = data.get("paradox", {})
            if paradox_data:
                profile = self.janus.assess_dual_truth(
                    entity_id=entity_id,
                    truth_a_statement=paradox_data.get("truth_a", ""),
                    truth_b_statement=paradox_data.get("truth_b", ""),
                    evidence_a=paradox_data.get("evidence_a", []),
                    evidence_b=paradox_data.get("evidence_b", []),
                    context=data.get("context", {})
                )
                print(f"   Both valid: {profile.both_valid}, Balance: {profile.duality_balance.value}")
                return profile
        except Exception as e:
            logger.error(f"Janus invocation failed: {e}")
        
        return None
    
    def _invoke_dionysus(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Dionysus for desire analysis"""
        if not self.dionysus:
            return None
        
        print("\n🍷 DIONYSUS revealing true desires...")
        
        try:
            profile = self.dionysus.detect_true_desire(
                entity_id=entity_id,
                stated_goal=data.get("stated_goal", ""),
                actions_taken=data.get("actions", []),
                emotional_state=data.get("emotional_state", {}),
                context=data.get("context", {})
            )
            print(f"   Stated: {profile.stated_desire[:40]}...")
            print(f"   True: {profile.true_desire[:40]}...")
            print(f"   Authenticity: {profile.authenticity_score:.2f}")
            return profile
        except Exception as e:
            logger.error(f"Dionysus invocation failed: {e}")
        
        return None
    
    def _invoke_eros(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Eros for emotional polarity"""
        if not self.eros:
            return None
        
        print("\n💘 EROS detecting emotional polarity...")
        
        try:
            paradox_data = data.get("paradox", {})
            if paradox_data:
                profile = self.eros.assess_emotional_polarity(
                    entity_id=entity_id,
                    truth_a=paradox_data.get("truth_a", ""),
                    truth_b=paradox_data.get("truth_b", ""),
                    stated_choice=paradox_data.get("stated_choice", ""),
                    emotional_responses=data.get("emotional_responses", {}),
                    past_actions=data.get("actions", []),
                    context=data.get("context", {})
                )
                print(f"   Stated: {profile.stated_choice[:40]}...")
                print(f"   Felt: {profile.felt_choice[:40]}...")
                print(f"   Alignment: {profile.heart_alignment.value}")
                return profile
        except Exception as e:
            logger.error(f"Eros invocation failed: {e}")
        
        return None
    
    def _invoke_demeter(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Demeter for growth tracking"""
        if not self.demeter:
            return None
        
        print("\n🌾 DEMETER tracking growth...")
        
        try:
            growth_data = data.get("growth_metrics", [])
            if growth_data:
                # Track multiple measurements
                for metric in growth_data:
                    self.demeter.track_growth(
                        entity_id=entity_id,
                        metric_name=metric.get("name", "BR"),
                        metric_value=metric.get("value", 0),
                        timestamp=metric.get("timestamp")
                    )
                
                profile = self.demeter.get_growth_profile(entity_id)
                if profile:
                    print(f"   Stage: {profile.current_stage.value}, Trend: {profile.growth_trend.value}")
                    print(f"   Season: {profile.current_season.value}")
                return profile
        except Exception as e:
            logger.error(f"Demeter invocation failed: {e}")
        
        return None
    
    def _invoke_hades(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Hades for judgment"""
        if not self.hades:
            return None
        
        print("\n⚰️ HADES pronouncing judgment...")
        
        try:
            profile = self.hades.assess_damnation(
                entity_id=entity_id,
                current_br=data.get("current_br", 0),
                trespasses=data.get("trespasses", []),
                forgiveness_count=data.get("forgiveness_count", 0),
                repentance_attempts=data.get("repentance_attempts", 0),
                cycles_lived=data.get("cycles_lived", 0)
            )
            print(f"   Damnation: {profile.damnation_level.value}")
            print(f"   Current BR: {profile.current_br}, Distance from Hell: {profile.distance_from_hell}")
            return profile
        except Exception as e:
            logger.error(f"Hades invocation failed: {e}")
        
        return None
    
    def _invoke_persephone(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Persephone for redemption"""
        if not self.persephone:
            return None
        
        print("\n🌸 PERSEPHONE assessing redemption...")
        
        try:
            profile = self.persephone.assess_redemption(
                entity_id=entity_id,
                current_br=data.get("current_br", 0),
                repentance_count=data.get("repentance_attempts", 0),
                forgiveness_extended=data.get("forgiveness_count", 0),
                trespasses=data.get("trespasses", []),
                cycles_lived=data.get("cycles_lived", 0),
                current_season=data.get("season", "Winter")
            )
            print(f"   Eligibility: {profile.redemption_eligibility.value}")
            print(f"   Grace: {profile.grace_available.value}, Cost: {profile.redemption_cost} BR")
            return profile
        except Exception as e:
            logger.error(f"Persephone invocation failed: {e}")
        
        return None
    
    def _invoke_nemesis(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Nemesis for retribution"""
        if not self.nemesis:
            return None
        
        print("\n⚖️ NEMESIS calculating retribution...")
        
        try:
            profile = self.nemesis.assess_retribution(
                entity_id=entity_id,
                current_br=data.get("current_br", 0),
                trespasses=data.get("trespasses", []),
                consequences_paid=data.get("consequences_paid", []),
                current_status=data.get("status", "ordinary"),
                cycles_lived=data.get("cycles_lived", 0)
            )
            print(f"   Justice Status: {profile.justice_status.value}")
            print(f"   Retribution Owed: {profile.retribution_owed} BR")
            return profile
        except Exception as e:
            logger.error(f"Nemesis invocation failed: {e}")
        
        return None
    
    def _invoke_schrodinger(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Schrodinger for quantum reasoning over possible paths"""
        if not self.schrodinger:
            return None
        
        print("\n⚛️ SCHRODINGER reasoning over possible paths...")
        
        try:
            solution, observation, analysis = self.schrodinger.quantum_reason(
                problem=data.get("problem", f"Optimal path for {entity_id}"),
                context=data.get("context", {})
            )
            print(f"   Collapsed to: {solution.description[:60]} (confidence {observation.confidence:.2f})")
            return observation
        except Exception as e:
            logger.error(f"Schrodinger invocation failed: {e}")
        
        return None
    
    def _invoke_hephaestus(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Hephaestus for tool creation"""
        if not self.hephaestus:
            return None
        
        print("\n🔨 HEPHAESTUS forging solutions...")
        
        try:
            # Hephaestus creates tools based on needs
            need = data.get("tool_need", "growth")
            print(f"   Forging tool for: {need}")
            return {"tool_need": need, "status": "forged"}
        except Exception as e:
            logger.error(f"Hephaestus invocation failed: {e}")
        
        return None
    
    def _invoke_aries(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Aries for action execution"""
        if not self.aries:
            return None
        
        print("\n⚔️ ARIES planning action...")
        
        try:
            # Aries determines immediate actions
            actions = data.get("pending_actions", [])
            print(f"   {len(actions)} actions pending execution")
            return {"actions_pending": len(actions)}
        except Exception as e:
            logger.error(f"Aries invocation failed: {e}")
        
        return None
    
    def _invoke_hermes(self, entity_id: str, data: Dict) -> Optional[Any]:
        """Invoke Hermes for communication"""
        if not self.hermes:
            return None
        
        print("\n📨 HERMES interpreting communication...")
        
        try:
            profile = self.hermes.interpret_communication(
                entity_id=entity_id,
                stated_message=data.get("stated_message", ""),
                behavioral_signals=data.get("behavioral_signals", {}),
                context=data.get("context", {})
            )
            print(f"   Clarity: {profile.signal_clarity.value}")
            print(f"   Alignment: {profile.message_alignment:.2f}")
            return profile
        except Exception as e:
            logger.error(f"Hermes invocation failed: {e}")
        
        return None
    
    def _collect_divine_wisdom(self, assessment: OlympusAssessment) -> Dict[str, str]:
        """Collect wisdom from all GODBOTs"""
        wisdom = {}
        
        if assessment.prometheus_patterns:
            wisdom["Prometheus"] = f"Pattern detected: {getattr(assessment.prometheus_patterns, 'pattern_type', 'unknown')}"
        
        if assessment.janus_paradox:
            wisdom["Janus"] = getattr(assessment.janus_paradox, 'janus_insight', 'Both truths valid')
        
        if assessment.dionysus_desires:
            wisdom["Dionysus"] = getattr(assessment.dionysus_desires, 'recommendation', 'Follow true desire')
        
        if assessment.eros_polarity:
            wisdom["Eros"] = getattr(assessment.eros_polarity, 'eros_insight', 'Listen to heart')
        
        if assessment.demeter_growth:
            wisdom["Demeter"] = getattr(assessment.demeter_growth, 'recommendation', 'Continue growth')
        
        if assessment.hades_judgment:
            wisdom["Hades"] = f"Damnation: {getattr(assessment.hades_judgment, 'damnation_level', 'unknown')}"
        
        if assessment.persephone_redemption:
            wisdom["Persephone"] = f"Redemption: {getattr(assessment.persephone_redemption, 'redemption_eligibility', 'unknown')}"
        
        if assessment.nemesis_retribution:
            wisdom["Nemesis"] = f"Justice: {getattr(assessment.nemesis_retribution, 'justice_status', 'unknown')}"
        
        if assessment.schrodinger_reasoning:
            wisdom["Schrodinger"] = getattr(assessment.schrodinger_reasoning, 'reasoning', 'Hold all paths until observed')
        
        return wisdom
    
    def _synthesize_through_hermes(
        self,
        divine_wisdom: Dict[str, str],
        entity_data: Dict
    ) -> Dict[str, Any]:
        """Use Hermes to synthesize all wisdom"""
        
        if not self.hermes or not divine_wisdom:
            return {
                "guidance": "Council unable to provide guidance",
                "actions": [],
                "consensus": "",
                "translations": {},
                "steps": []
            }
        
        # Translate divine wisdom to actionable
        message = self.hermes.translate_divine_to_actionable(
            divine_assessments=divine_wisdom,
            entity_context=entity_data.get("context", {})
        )
        
        # Extract priority actions
        priority_actions = []
        if "Hades" in divine_wisdom:
            priority_actions.append("Address accountability issues")
        if "Persephone" in divine_wisdom:
            priority_actions.append("Pursue redemption path")
        if "Nemesis" in divine_wisdom:
            priority_actions.append("Settle unpaid debts")
        
        # Build consensus
        consensus = f"Council of {len(divine_wisdom)} gods has spoken"
        
        # Translate technical terms
        translations = {
            "BR": "Benevolence Reservoir (emotional health)",
            "EQ": "Emotional Quotient",
            "drift": "Moral drift from authentic self"
        }
        
        # Actionable steps
        steps = [
            "1. Acknowledge current state honestly",
            "2. Take accountability for past actions",
            "3. Seek redemption through genuine change",
            "4. Follow heart's true direction"
        ]
        
        return {
            "guidance": message.translated_content,
            "actions": priority_actions,
            "consensus": consensus,
            "translations": translations,
            "steps": steps
        }
    
    def get_assessment(self, entity_id: str) -> Optional[OlympusAssessment]:
        """Retrieve assessment"""
        return self.assessments.get(entity_id)
    
    def export_assessment(
        self,
        entity_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """Export assessment to JSON"""
        
        assessment = self.assessments.get(entity_id)
        if not assessment:
            return ""
        
        if not output_path:
            output_path = f"olympus_assessment_{entity_id}.json"
        
        data = {
            "entity_id": assessment.entity_id,
            "timestamp": assessment.timestamp.isoformat(),
            "unified_guidance": assessment.unified_guidance,
            "priority_actions": assessment.priority_actions,
            "divine_consensus": assessment.divine_consensus,
            "technical_translations": assessment.technical_to_human,
            "actionable_steps": assessment.actionable_steps,
            "godbot_assessments": {
                "prometheus": str(assessment.prometheus_patterns) if assessment.prometheus_patterns else None,
                "janus": str(assessment.janus_paradox) if assessment.janus_paradox else None,
                "dionysus": str(assessment.dionysus_desires) if assessment.dionysus_desires else None,
                "eros": str(assessment.eros_polarity) if assessment.eros_polarity else None,
                "demeter": str(assessment.demeter_growth) if assessment.demeter_growth else None,
                "hades": str(assessment.hades_judgment) if assessment.hades_judgment else None,
                "persephone": str(assessment.persephone_redemption) if assessment.persephone_redemption else None,
                "nemesis": str(assessment.nemesis_retribution) if assessment.nemesis_retribution else None,
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"🏛️ Exported assessment to {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    print("🏛️ OLYMPUS COUNCIL - Divine Assembly")
    print("=" * 70)
    
    council = OlympusCouncil()
    
    # Example: Complete assessment
    entity_data = {
        "stated_goal": "I want to be successful",
        "actions": [
            {"action": "worked_overtime", "supports_truth": "career"},
            {"action": "skipped_family_dinner", "supports_truth": "career"},
            {"action": "felt_guilty", "supports_truth": "family"},
        ],
        "emotional_state": {"stress": 0.8, "guilt": 0.6},
        "current_br": -15,
        "trespasses": [
            {"type": "neglect", "severity": 0.6, "victim": "family"},
        ],
        "forgiveness_count": 0,
        "repentance_attempts": 1,
        "cycles_lived": 5,
        "consequences_paid": [],
        "status": "ordinary",
        "paradox": {
            "truth_a": "I am a dedicated professional",
            "truth_b": "I am a loving family person",
            "stated_choice": "I am a dedicated professional",
            "evidence_a": ["works long hours", "achieves goals"],
            "evidence_b": ["loves family", "feels guilty for absence"]
        },
        "emotional_responses": {
            "excitement_about_truth_a": 0.7,
            "excitement_about_truth_b": 0.9,
            "hesitation": 0.7
        },
        "behavioral_signals": {
            "defensive": True,
            "fear_present": True
        },
        "stated_message": "I'm fine, work is just busy right now",
        "context": {"recent_failure": False, "under_pressure": True},
        "season": "Autumn"
    }
    
    assessment = council.full_assessment(
        entity_id="entity_conflicted",
        entity_data=entity_data
    )
    
    print("\n\n🏛️ OLYMPUS COUNCIL DECREE")
    print("=" * 70)
    print(f"\nEntity: {assessment.entity_id}")
    print(f"Assessment Time: {assessment.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📜 UNIFIED GUIDANCE")
    print(f"{assessment.unified_guidance}")
    
    if assessment.priority_actions:
        print(f"\n⚡ PRIORITY ACTIONS:")
        for action in assessment.priority_actions:
            print(f"   • {action}")
    
    if assessment.actionable_steps:
        print(f"\n📋 ACTIONABLE STEPS:")
        for step in assessment.actionable_steps:
            print(f"   {step}")
    
    print(f"\n🏛️ {assessment.divine_consensus}")
    
    # Export
    output_file = council.export_assessment("entity_conflicted")
    print(f"\n💾 Assessment exported to: {output_file}")
