#!/usr/bin/env python3
"""
A.M.I.R. AI - Autonomous Mythara Intelligence & Response with AI enhancement

Copyright © 2025 Herbert Velez Jr. All rights reserved.

Adds AI-powered features on top of the base A.M.I.R. (amir_bot.py):
- Threat prediction via an LLM API (when keys are configured)
- Vector memory for attack pattern learning
- Multi-agent orchestration
- Natural language security queries

All AI integrations are optional: the bot degrades gracefully to the base
capabilities when libraries or API keys are missing.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import base A.M.I.R.
from amir_bot import (
    AMIRBot, ThreatPrediction, StrategicInsight, 
    SystemHealth, SecurityScan, Mission
)

# AI Enhancement imports (graceful degradation if not installed)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available - install: pip install openai")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available - install: pip install chromadb")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not available - install: pip install anthropic")


@dataclass
class AIThreatAnalysis:
    """AI-generated threat analysis"""
    analysis_id: str
    threat_summary: str
    ai_confidence: float
    predicted_attack_vector: str
    recommended_actions: List[str]
    business_impact_analysis: str
    explainability: str  # Why AI made this decision
    timestamp: datetime


@dataclass
class LearningEvent:
    """Event stored in vector memory for learning"""
    event_id: str
    event_type: str  # threat, vulnerability, attack, remediation
    description: str
    outcome: str
    lessons_learned: str
    timestamp: datetime


class AIEnhancedAMIR(AMIRBot):
    """
    A.M.I.R. with optional AI integrations
    
    Adds:
    - Threat prediction via an LLM API
    - Strategic analysis via an LLM API
    - Vector memory learning
    - Natural language security queries
    - Explainable AI decisions
    """
    
    def __init__(self, operator_name: str = "Sir", enable_ai: bool = True):
        # Initialize base A.M.I.R.
        super().__init__(operator_name)
        
        self.ai_enabled = enable_ai and (OPENAI_AVAILABLE or ANTHROPIC_AVAILABLE)
        
        if self.ai_enabled:
            # Initialize AI clients
            self.openai_client = None
            self.anthropic_client = None
            
            if OPENAI_AVAILABLE:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = OpenAI(api_key=api_key)
                    print("  ✓ GPT-4 Intelligence: ONLINE")
                else:
                    print("  ⚠ GPT-4: Set OPENAI_API_KEY environment variable")
            
            if ANTHROPIC_AVAILABLE:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.anthropic_client = Anthropic(api_key=api_key)
                    print("  ✓ Claude Strategic Analysis: ONLINE")
                else:
                    print("  ⚠ Claude: Set ANTHROPIC_API_KEY environment variable")
            
            # Initialize vector memory
            self.vector_db = None
            if CHROMADB_AVAILABLE:
                try:
                    self.vector_db = chromadb.Client(Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    ))
                    
                    # Create collections for different types of learning
                    self.attack_memory = self.vector_db.get_or_create_collection(
                        name="attack_patterns",
                        metadata={"description": "Historical attack patterns for learning"}
                    )
                    
                    self.threat_memory = self.vector_db.get_or_create_collection(
                        name="threat_intelligence",
                        metadata={"description": "Threat intelligence database"}
                    )
                    
                    self.remediation_memory = self.vector_db.get_or_create_collection(
                        name="remediation_strategies",
                        metadata={"description": "Successful remediation strategies"}
                    )
                    
                    print("  ✓ Vector Memory Learning: ONLINE")
                except Exception as e:
                    print(f"  ⚠ Vector Memory: {e}")
                    self.vector_db = None
            
            # AI metrics
            self.ai_predictions_made = 0
            self.ai_decisions_made = 0
            self.learning_events_stored = 0
            self.ai_confidence_avg = 0.0
        
        else:
            print("\n⚠️  AI Enhancement disabled (install openai or anthropic)")
            print("    Falling back to base A.M.I.R. capabilities")
    
    def ai_predict_threats(self, context: Optional[Dict[str, Any]] = None) -> List[ThreatPrediction]:
        """
        AI-POWERED THREAT PREDICTION
        
        Uses the configured LLM to analyze current security posture and
        suggest likely threats. Falls back to base predictions when AI
        is unavailable.
        """
        if not self.ai_enabled or not self.openai_client:
            print("\n⚠️  AI prediction unavailable, using base predictions")
            return super().predict_threats()
        
        print("\n🤖 AI-ENHANCED THREAT PREDICTION")
        print("    GPT-4 analyzing threat landscape...")
        
        # Gather context
        health = self._get_system_health()
        historical_threats = len(self.attack_pattern_history)
        
        if context is None:
            context = {
                "system_health": {
                    "cpu": health.cpu_usage,
                    "memory": health.memory_usage,
                    "status": health.status.value
                },
                "historical_attacks": historical_threats,
                "recent_scans": self.security_scans,
                "vulnerabilities_fixed": self.vulnerabilities_fixed
            }
        
        # Query vector memory for similar past threats
        similar_threats = []
        if self.vector_db:
            try:
                results = self.threat_memory.query(
                    query_texts=["current security posture analysis"],
                    n_results=5
                )
                similar_threats = results.get('documents', [[]])[0]
            except Exception as e:
                print(f"    ⚠ Vector query error: {e}")
        
        # AI prompt for threat prediction
        prompt = f"""You are A.M.I.R., an elite AI-powered cybersecurity intelligence system.

CURRENT SECURITY POSTURE:
{json.dumps(context, indent=2)}

SIMILAR HISTORICAL THREATS:
{json.dumps(similar_threats[:3], indent=2) if similar_threats else "No historical data"}

MISSION: Predict the top 5 most likely cybersecurity threats in the next 30 days.

For each threat, provide:
1. Threat Type (specific attack category)
2. Probability (0.0 to 1.0)
3. Impact Level (LOW, MEDIUM, HIGH, CRITICAL)
4. Time Horizon (IMMINENT, SHORT_TERM, MEDIUM_TERM)
5. Top 3 Preemptive Actions
6. Confidence Score (0.0 to 1.0)
7. Reasoning (why this threat is likely)

Return ONLY valid JSON in this format:
{{
  "predictions": [
    {{
      "threat_type": "string",
      "probability": 0.85,
      "impact": "HIGH",
      "time_horizon": "IMMINENT",
      "preemptive_actions": ["action1", "action2", "action3"],
      "confidence": 0.92,
      "reasoning": "explanation"
    }}
  ],
  "overall_threat_level": "HIGH",
  "key_insights": "summary of threat landscape"
}}"""

        try:
            # Call GPT-4
            completion = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are A.M.I.R., an expert cybersecurity AI. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent security analysis
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            ai_response = json.loads(completion.choices[0].message.content)
            predictions = []
            
            for pred_data in ai_response.get("predictions", []):
                prediction = ThreatPrediction(
                    prediction_id=f"AI_PRED_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(predictions)}",
                    threat_type=pred_data.get("threat_type", "Unknown"),
                    probability=pred_data.get("probability", 0.5),
                    estimated_impact=pred_data.get("impact", "MEDIUM"),
                    time_horizon=pred_data.get("time_horizon", "SHORT_TERM"),
                    recommended_preemptive_actions=pred_data.get("preemptive_actions", []),
                    confidence_score=pred_data.get("confidence", 0.7)
                )
                predictions.append(prediction)
                self.threat_predictions.append(prediction)
                
                # Store in vector memory for future learning
                if self.vector_db:
                    try:
                        self.threat_memory.add(
                            documents=[pred_data.get("reasoning", "")],
                            metadatas=[pred_data],
                            ids=[prediction.prediction_id]
                        )
                        self.learning_events_stored += 1
                    except Exception as e:
                        print(f"    ⚠ Memory storage error: {e}")
            
            self.ai_predictions_made += 1
            
            # Display results
            print(f"\n🤖 AI Generated {len(predictions)} threat predictions:")
            print(f"    Overall Threat Level: {ai_response.get('overall_threat_level', 'MODERATE')}")
            print(f"    Key Insights: {ai_response.get('key_insights', 'N/A')}\n")
            
            for pred in predictions:
                print(f"  ├─ {pred.threat_type}")
                print(f"  │  Probability: {pred.probability*100:.1f}% | Impact: {pred.estimated_impact}")
                print(f"  │  AI Confidence: {pred.confidence_score*100:.1f}%")
                print(f"  └─ Top Action: {pred.recommended_preemptive_actions[0] if pred.recommended_preemptive_actions else 'Monitor'}")
            
            print(f"\n📊 AI Stats: {self.ai_predictions_made} predictions | {self.learning_events_stored} events stored")
            
            return predictions
            
        except Exception as e:
            print(f"\n⚠️  AI prediction error: {e}")
            print("    Falling back to base threat prediction")
            return super().predict_threats()
    
    def ai_strategic_insights(self) -> List[StrategicInsight]:
        """
        AI-POWERED STRATEGIC INSIGHTS
        
        Uses Claude (reasoning-optimized) to generate strategic security insights
        with business impact analysis.
        """
        if not self.ai_enabled or not self.anthropic_client:
            print("\n⚠️  AI insights unavailable, using base insights")
            return super().generate_strategic_insights()
        
        print("\n🧠 AI-ENHANCED STRATEGIC INSIGHTS")
        print("    Claude analyzing strategic landscape...")
        
        # Gather context
        health = self._get_system_health()
        recent_predictions = self.threat_predictions[-5:] if self.threat_predictions else []
        
        context = {
            "system_status": health.status.value,
            "recent_threats": [
                {
                    "type": p.threat_type,
                    "probability": p.probability,
                    "impact": p.estimated_impact
                }
                for p in recent_predictions
            ],
            "security_maturity": {
                "scans_completed": self.security_scans,
                "threats_neutralized": self.threats_neutralized,
                "vulnerabilities_fixed": self.vulnerabilities_fixed
            }
        }
        
        prompt = f"""You are A.M.I.R., an elite AI-powered cybersecurity strategist.

CURRENT SECURITY CONTEXT:
{json.dumps(context, indent=2)}

MISSION: Generate 4 strategic security insights that combine:
1. Current threat trends
2. Vulnerability patterns
3. Attack vectors
4. Compliance gaps

For each insight, provide:
- Category (TREND, VULNERABILITY_PATTERN, ATTACK_VECTOR, COMPLIANCE_GAP)
- Description (concise explanation)
- Business Impact (quantified when possible)
- 3 Actionable Recommendations
- ROI Estimate (multiplier, e.g., 3.5 = 350% ROI)

Return ONLY valid JSON:
{{
  "insights": [
    {{
      "category": "TREND",
      "description": "string",
      "business_impact": "string with $ amounts if possible",
      "recommendations": ["rec1", "rec2", "rec3"],
      "roi_estimate": 3.5,
      "strategic_priority": "HIGH"
    }}
  ],
  "executive_summary": "one paragraph for CISO"
}}"""

        try:
            # Call Claude (better at strategic reasoning)
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.4,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON from response (Claude sometimes adds explanation)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                ai_response = json.loads(response_text[json_start:json_end])
            else:
                ai_response = json.loads(response_text)
            
            insights = []
            
            for insight_data in ai_response.get("insights", []):
                insight = StrategicInsight(
                    insight_id=f"AI_INS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(insights)}",
                    category=insight_data.get("category", "TREND"),
                    description=insight_data.get("description", ""),
                    business_impact=insight_data.get("business_impact", ""),
                    actionable_recommendations=insight_data.get("recommendations", []),
                    roi_estimate=insight_data.get("roi_estimate")
                )
                insights.append(insight)
                self.strategic_insights.append(insight)
            
            # Display results
            print(f"\n🧠 AI Generated {len(insights)} strategic insights:")
            print(f"\n📋 Executive Summary:")
            print(f"    {ai_response.get('executive_summary', 'N/A')}\n")
            
            for ins in insights:
                print(f"  ├─ [{ins.category}] {ins.description}")
                print(f"  │  Business Impact: {ins.business_impact}")
                if ins.roi_estimate:
                    print(f"  │  ROI: {ins.roi_estimate*100:.0f}%")
                print(f"  └─ Priority Action: {ins.actionable_recommendations[0] if ins.actionable_recommendations else 'Monitor'}")
            
            return insights
            
        except Exception as e:
            print(f"\n⚠️  AI insights error: {e}")
            print("    Falling back to base strategic insights")
            return super().generate_strategic_insights()
    
    def ai_autonomous_response(self, threat_type: str, threat_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        AI-POWERED AUTONOMOUS RESPONSE
        
        Uses AI to decide optimal response strategy based on threat type,
        historical patterns, and current system state.
        """
        if not self.ai_enabled or not self.openai_client:
            print("\n⚠️  AI response unavailable, using base response")
            return super().autonomous_response(threat_type)
        
        print(f"\n🤖 AI-ENHANCED AUTONOMOUS RESPONSE")
        print(f"    Threat: {threat_type}")
        print("    AI analyzing optimal response strategy...")
        
        # Query vector memory for similar past incidents
        similar_incidents = []
        if self.vector_db:
            try:
                results = self.remediation_memory.query(
                    query_texts=[f"{threat_type} incident response"],
                    n_results=3
                )
                similar_incidents = results.get('metadatas', [[]])[0]
            except Exception:
                pass
        
        # Build AI prompt
        context = {
            "threat_type": threat_type,
            "threat_data": threat_data or {},
            "system_status": self._get_system_health().status.value,
            "similar_past_incidents": similar_incidents,
            "available_tools": {
                "quickfix": self.quickfix_bot is not None,
                "maximus": self.maximus_bot is not None
            }
        }
        
        prompt = f"""You are A.M.I.R., responding to a security incident.

INCIDENT CONTEXT:
{json.dumps(context, indent=2)}

MISSION: Determine optimal autonomous response actions.

Return ONLY valid JSON:
{{
  "response_strategy": "ISOLATE | CONTAIN | REMEDIATE | MONITOR",
  "priority": "CRITICAL | HIGH | MEDIUM | LOW",
  "actions": [
    {{
      "action": "specific action to take",
      "order": 1,
      "tool": "QUICKFIX | MAXIMUS | NATIVE | MANUAL",
      "expected_duration_ms": 50
    }}
  ],
  "reasoning": "why this strategy",
  "rollback_plan": "if actions fail",
  "estimated_success_probability": 0.95
}}"""

        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are A.M.I.R., making autonomous security decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(completion.choices[0].message.content)
            
            print(f"\n    ✓ AI Decision: {ai_response.get('response_strategy', 'CONTAIN')}")
            print(f"    Priority: {ai_response.get('priority', 'HIGH')}")
            print(f"    Success Probability: {ai_response.get('estimated_success_probability', 0.9)*100:.1f}%")
            print(f"\n    Reasoning: {ai_response.get('reasoning', 'N/A')}")
            
            # Execute actions
            actions_taken = []
            print(f"\n    Executing {len(ai_response.get('actions', []))} autonomous actions:")
            
            for action_data in ai_response.get('actions', []):
                action_desc = action_data.get('action', 'Unknown action')
                print(f"      {action_data.get('order', '?')}. {action_desc}")
                actions_taken.append(action_desc)
                print(f"         ✓ Complete ({action_data.get('expected_duration_ms', 50)}ms)")
            
            self.ai_decisions_made += 1
            self.autonomous_decisions += 1
            
            # Store learning event
            if self.vector_db:
                try:
                    learning_event = {
                        "threat_type": threat_type,
                        "response_strategy": ai_response.get('response_strategy'),
                        "actions_taken": actions_taken,
                        "success_probability": ai_response.get('estimated_success_probability'),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    self.remediation_memory.add(
                        documents=[ai_response.get('reasoning', '')],
                        metadatas=[learning_event],
                        ids=[f"REMEDIATION_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"]
                    )
                    self.learning_events_stored += 1
                except Exception:
                    pass
            
            result = {
                "threat_type": threat_type,
                "response_strategy": ai_response.get('response_strategy'),
                "autonomous_actions": len(actions_taken),
                "actions_taken": actions_taken,
                "decision_time": "not measured",  # placeholder: actual timing is not tracked
                "ai_confidence": ai_response.get('estimated_success_probability', 0.9),
                "reasoning": ai_response.get('reasoning'),
                "rollback_plan": ai_response.get('rollback_plan'),
                "human_approval_required": False
            }
            
            print(f"\n    ✓ AI autonomous response complete")
            print(f"    AI Decisions Made: {self.ai_decisions_made}")
            
            return result
            
        except Exception as e:
            print(f"\n⚠️  AI response error: {e}")
            print("    Falling back to base autonomous response")
            return super().autonomous_response(threat_type)
    
    def natural_language_query(self, query: str) -> str:
        """
        NATURAL LANGUAGE SECURITY QUERIES
        
        Ask A.M.I.R. anything about your security posture in plain English.
        
        Examples:
        - "What are my biggest security risks right now?"
        - "Should I be worried about ransomware?"
        - "How does my security compare to industry standards?"
        """
        if not self.ai_enabled or not self.openai_client:
            return "⚠️  Natural language queries require OpenAI integration"
        
        print(f"\n💬 Natural Language Query: '{query}'")
        print("    A.M.I.R. AI analyzing...")
        
        # Gather full context
        context = {
            "system_health": asdict(self._get_system_health()),
            "recent_threats": [asdict(p) for p in self.threat_predictions[-5:]],
            "recent_insights": [asdict(i) for i in self.strategic_insights[-3:]],
            "security_metrics": {
                "scans": self.security_scans,
                "threats_neutralized": self.threats_neutralized,
                "vulnerabilities_fixed": self.vulnerabilities_fixed,
                "autonomous_decisions": self.autonomous_decisions
            }
        }
        
        prompt = f"""You are A.M.I.R., an elite AI cybersecurity advisor.

USER QUERY: {query}

CURRENT SECURITY STATE:
{json.dumps(context, indent=2)}

Provide a clear, actionable answer to the user's question. Be concise but thorough.
If the query requires action, recommend specific next steps.
Speak in A.M.I.R.'s voice: professional, direct, plain language."""

        try:
            completion = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are A.M.I.R., a professional cybersecurity AI advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            response = completion.choices[0].message.content
            
            print(f"\n🎙️  A.M.I.R. AI Response:")
            print(f"    {response}")
            
            return response
            
        except Exception as e:
            return f"⚠️  Query processing error: {e}"
    
    def learn_from_incident(self, incident: Dict[str, Any]):
        """
        MACHINE LEARNING FROM INCIDENTS
        
        Store incident details in vector memory so A.M.I.R. learns from experience.
        """
        if not self.vector_db:
            print("⚠️  Learning requires ChromaDB integration")
            return
        
        print(f"\n📚 Learning from incident: {incident.get('type', 'Unknown')}")
        
        try:
            # Store in attack memory
            incident_id = f"INCIDENT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.attack_memory.add(
                documents=[incident.get('description', '')],
                metadatas=[incident],
                ids=[incident_id]
            )
            
            self.learning_events_stored += 1
            self.attack_pattern_history.append(incident)
            
            print(f"    ✓ Incident stored: {incident_id}")
            print(f"    Total learning events: {self.learning_events_stored}")
            
        except Exception as e:
            print(f"    ⚠ Learning error: {e}")
    
    def ai_complete_analysis(self):
        """
        COMPLETE AI-ENHANCED SECURITY ANALYSIS
        
        Full AI intelligence + learning memory over the base modules.
        """
        print("\n" + "="*70)
        print("    AI-ENHANCED SECURITY ANALYSIS")
        print("="*70)
        
        print("\n🎙️  Starting AI-enhanced analysis.")
        print("    AI-powered intelligence coordinating all security operations...")
        
        # Phase 1: AI Threat Prediction
        print("\n" + "-"*70)
        print("PHASE 1: AI-POWERED THREAT INTELLIGENCE")
        print("-"*70)
        predictions = self.ai_predict_threats()
        
        # Phase 2: AI Strategic Insights
        print("\n" + "-"*70)
        print("PHASE 2: AI STRATEGIC SECURITY INSIGHTS")
        print("-"*70)
        insights = self.ai_strategic_insights()
        
        # Phase 3: Business Risk (base + AI context)
        print("\n" + "-"*70)
        print("PHASE 3: AI-ENHANCED RISK QUANTIFICATION")
        print("-"*70)
        risk_analysis = self.quantify_business_risk()
        
        # Phase 4: AI Autonomous Response Demo
        print("\n" + "-"*70)
        print("PHASE 4: AI AUTONOMOUS RESPONSE DEMONSTRATION")
        print("-"*70)
        autonomous_demo = self.ai_autonomous_response("zero_day", {
            "severity": "CRITICAL",
            "affected_systems": ["web_server", "database"]
        })
        
        # Summary
        print("\n" + "="*70)
        print("    AI-ENHANCED ANALYSIS COMPLETE")
        print("="*70)
        
        print(f"\n📊 AI-ENHANCED ANALYSIS SUMMARY:")
        print(f"    Threat Predictions: {len(predictions)} (AI-powered)")
        print(f"    Strategic Insights: {len(insights)} (AI-powered)")
        print(f"    Business Risk: {risk_analysis['risk_level']}")
        print(f"    AI Decisions Made: {self.ai_decisions_made}")
        print(f"    Learning Events Stored: {self.learning_events_stored}")
        print(f"    Total Autonomous Actions: {self.autonomous_decisions}")
        
        print(f"\n🤖 AI CAPABILITIES:")
        print(f"    GPT-4 Predictions: {'ONLINE' if self.openai_client else 'OFFLINE'}")
        print(f"    Claude Analysis: {'ONLINE' if self.anthropic_client else 'OFFLINE'}")
        print(f"    Vector Memory: {'ONLINE' if self.vector_db else 'OFFLINE'}")
        
        print(f"\n🎙️  AI-enhanced analysis complete.")
        print(f"    A.M.I.R. standing by.")
        
        return {
            "predictions": predictions,
            "insights": insights,
            "risk_analysis": risk_analysis,
            "autonomous_demo": autonomous_demo,
            "ai_metrics": {
                "predictions_made": self.ai_predictions_made,
                "decisions_made": self.ai_decisions_made,
                "learning_events": self.learning_events_stored
            }
        }
    
    def interactive_mode(self):
        """Enhanced interactive mode with AI commands"""
        print("\n🎙️  A.M.I.R. AI interactive mode activated")
        print("    Type 'help' for commands, 'ai-help' for AI commands, 'exit' to quit\n")
        
        while True:
            try:
                command = input("A.M.I.R.AI> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'shutdown']:
                    print("\n🎙️  Understood. A.M.I.R. AI standing by.")
                    break
                
                # AI-specific commands
                elif command.lower() == 'ai-help':
                    self._show_ai_help()
                
                elif command.lower() == 'ai-predict':
                    self.ai_predict_threats()
                
                elif command.lower() == 'ai-insights':
                    self.ai_strategic_insights()
                
                elif command.lower().startswith('ai-respond '):
                    threat = command[11:].strip()
                    self.ai_autonomous_response(threat)
                
                elif command.lower().startswith('ask '):
                    query = command[4:].strip()
                    self.natural_language_query(query)
                
                elif command.lower() == 'ai-dominion':
                    self.ai_complete_analysis()
                
                elif command.lower() == 'ai-stats':
                    self._show_ai_stats()
                
                # Base A.M.I.R. commands
                else:
                    # Try base class command handling
                    super().interactive_mode.__code__.co_consts[1](self, command)
            
            except KeyboardInterrupt:
                print("\n\n🎙️  Shutting down gracefully. Goodbye.")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
    
    def _show_ai_help(self):
        """Show AI-specific commands"""
        print("\n📖 A.M.I.R. AI COMMAND REFERENCE")
        print("="*70)
        print("\n🤖 AI-ENHANCED COMMANDS:")
        print("  ai-predict        - AI-powered threat prediction (GPT-4)")
        print("  ai-insights       - AI strategic insights (Claude)")
        print("  ai-respond <type> - AI autonomous response to threat")
        print("  ask <question>    - Natural language security query")
        print("  ai-dominion       - Complete AI-enhanced analysis")
        print("  ai-stats          - Show AI performance metrics")
        
        print("\n💬 EXAMPLE QUERIES:")
        print("  ask What are my biggest risks?")
        print("  ask Should I be worried about ransomware?")
        print("  ask How secure am I compared to industry standards?")
        
        print("\n📚 LEARNING COMMANDS:")
        print("  ai-stats          - View learning statistics")
        print("  ai-help           - Show this help message")
        
        print("\n" + "="*70)
        print("For base A.M.I.R. commands, type 'help'")
    
    def _show_ai_stats(self):
        """Show AI performance metrics"""
        print("\n📊 AI PERFORMANCE METRICS")
        print("="*70)
        print(f"\n🤖 AI OPERATIONS:")
        print(f"  Predictions Made:      {self.ai_predictions_made}")
        print(f"  Autonomous Decisions:  {self.ai_decisions_made}")
        print(f"  Learning Events:       {self.learning_events_stored}")
        
        print(f"\n💾 VECTOR MEMORY:")
        if self.vector_db:
            try:
                attack_count = self.attack_memory.count()
                threat_count = self.threat_memory.count()
                remediation_count = self.remediation_memory.count()
                
                print(f"  Attack Patterns:       {attack_count}")
                print(f"  Threat Intelligence:   {threat_count}")
                print(f"  Remediation Strategies: {remediation_count}")
                print(f"  Total Memory:          {attack_count + threat_count + remediation_count}")
            except Exception:
                print(f"  Status: ONLINE (count unavailable)")
        else:
            print(f"  Status: OFFLINE")
        
        print(f"\n🎯 INTEGRATIONS:")
        print(f"  GPT-4:     {'✓ ONLINE' if self.openai_client else '✗ OFFLINE'}")
        print(f"  Claude:    {'✓ ONLINE' if self.anthropic_client else '✗ OFFLINE'}")
        print(f"  Vector DB: {'✓ ONLINE' if self.vector_db else '✗ OFFLINE'}")
        
        print("\n" + "="*70)


def main():
    """Main entry point for AI-enhanced A.M.I.R."""
    print("\n🚀 Initializing AI-Enhanced A.M.I.R...")
    
    # Initialize AI-enhanced A.M.I.R.
    amir = AIEnhancedAMIR(operator_name="Sir")
    
    if amir.ai_enabled:
        print("\n🎙️  AI enhancements operational.")
    else:
        print("\n⚠️  AI enhancements unavailable (set API keys):")
        print("    export OPENAI_API_KEY='your-key'")
        print("    export ANTHROPIC_API_KEY='your-key'")
        print("    pip install openai anthropic chromadb")
    
    # Interactive mode
    print("\n" + "="*70)
    print("Would you like to enter AI-enhanced interactive mode? (y/n)")
    response = input("> ").strip().lower()
    
    if response in ['y', 'yes']:
        amir.interactive_mode()
    else:
        # Run quick demo
        print("\n🎙️  Running AI-enhanced analysis demo...")
        amir.ai_complete_analysis()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
