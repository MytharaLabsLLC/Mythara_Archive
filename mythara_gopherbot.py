#!/usr/bin/env python3
"""
Mythara Gopherbot - Your Personal Legal Research Assistant
Fetches, analyzes, and delivers legal resources on demand.

Copyright © 2026 Mythara Labs LLC. All rights reserved.

"Go fetch!" - The bot that retrieves what you need, when you need it.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json

# Import legal frameworks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'source_proprietary'))
from torts_law_framework import TortsLawIndex, TortsCovenantIntegrity, TortCategory
from legal_resources_index import LegalResearchEngine, LegalDomain


class GopherTaskType(Enum):
    """Types of tasks Gopherbot can perform"""
    FETCH_TORT_DEFINITION = "fetch_tort"
    FETCH_CASE_LAW = "fetch_case"
    FETCH_STATUTE = "fetch_statute"
    ANALYZE_FACT_PATTERN = "analyze_facts"
    RESEARCH_TOPIC = "research_topic"
    COMPLIANCE_CHECK = "compliance_check"
    CONTRACT_ANALYSIS = "contract_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    GENERATE_MEMO = "generate_memo"
    DEADLINE_TRACKING = "deadline_tracking"


class GopherPriority(Enum):
    """Priority levels for Gopherbot tasks"""
    URGENT = "urgent"  # Statute of limitations, deadlines
    HIGH = "high"  # Active litigation, compliance issues
    MEDIUM = "medium"  # General research
    LOW = "low"  # Background information


class MytharaGopherbot:
    """
    🐹 Mythara Gopherbot - Your tireless legal research assistant.
    
    Capabilities:
    - Fetches tort definitions, case law, statutes
    - Analyzes fact patterns
    - Generates legal memos
    - Tracks deadlines and statutes of limitations
    - Monitors compliance requirements
    - Performs contract risk analysis
    - Delivers customized legal research
    
    **DISCLAIMER:**
    - NOT A SUBSTITUTE FOR LICENSED ATTORNEY
    - NO ATTORNEY-CLIENT RELATIONSHIP CREATED
    - INFORMATIONAL PURPOSES ONLY
    - SEEK PROFESSIONAL LEGAL COUNSEL FOR SPECIFIC MATTERS
    """
    
    def __init__(self):
        self.torts_index = TortsLawIndex()
        self.legal_research = LegalResearchEngine()
        self.covenant_integrity = TortsCovenantIntegrity()
        self.task_queue = []
        self.completed_tasks = []
        
        print("🐹 Mythara Gopherbot Initialized!")
        print("=" * 60)
        print("Your personal legal research assistant is ready.")
        print("I can fetch legal resources, analyze cases, and deliver")
        print("comprehensive research on demand.")
        print("=" * 60)
        print("⚠️  NOT A SUBSTITUTE FOR LICENSED ATTORNEY")
        print("=" * 60 + "\n")
    
    # ==================== CORE FETCH COMMANDS ====================
    
    def fetch_tort(self, tort_name: str) -> Dict[str, Any]:
        """
        Fetch complete tort definition with all elements, defenses, and case law.
        
        Usage: gopherbot.fetch_tort("battery")
        """
        task_id = self._create_task(GopherTaskType.FETCH_TORT_DEFINITION, tort_name)
        
        print(f"🐹 Fetching tort definition: {tort_name}...")
        
        tort_def = self.torts_index.get_tort_definition(tort_name)
        
        if not tort_def:
            result = {
                "task_id": task_id,
                "status": "error",
                "error": f"Tort '{tort_name}' not found in database",
                "suggestions": self._suggest_similar_torts(tort_name)
            }
        else:
            result = {
                "task_id": task_id,
                "status": "success",
                "tort_name": tort_def.tort_name,
                "category": tort_def.category.value,
                "subcategory": tort_def.subcategory.value,
                "elements": [
                    {
                        "name": elem.element_name,
                        "description": elem.description,
                        "required": elem.required,
                        "proof_standard": elem.proof_standard,
                        "typical_evidence": elem.typical_evidence
                    }
                    for elem in tort_def.elements
                ],
                "defenses": [d.value for d in tort_def.defenses],
                "damages_available": tort_def.damages_available,
                "statute_of_limitations": tort_def.statute_of_limitations_years,
                "notes": tort_def.notes,
                "landmark_cases": tort_def.landmark_cases,
                "restatement_sections": tort_def.restatement_sections,
                "timestamp": datetime.now().isoformat()
            }
        
        self._complete_task(task_id, result)
        print(f"✅ Tort definition retrieved!\n")
        return result
    
    def fetch_case(self, case_name: str) -> Dict[str, Any]:
        """
        Fetch landmark case details.
        
        Usage: gopherbot.fetch_case("Palsgraf")
        """
        task_id = self._create_task(GopherTaskType.FETCH_CASE_LAW, case_name)
        
        print(f"🐹 Fetching case law: {case_name}...")
        
        # Search landmark cases
        cases = self.legal_research.cases.get_landmark_cases()
        matching_cases = [c for c in cases if case_name.lower() in c.case_name.lower()]
        
        if not matching_cases:
            result = {
                "task_id": task_id,
                "status": "error",
                "error": f"Case '{case_name}' not found in landmark cases database"
            }
        else:
            result = {
                "task_id": task_id,
                "status": "success",
                "cases": [
                    {
                        "case_name": case.case_name,
                        "citation": case.citation,
                        "year": case.year,
                        "court": case.court,
                        "domain": case.domain.value,
                        "holding": case.holding,
                        "principle": case.principle,
                        "modern_application": case.modern_application
                    }
                    for case in matching_cases
                ],
                "timestamp": datetime.now().isoformat()
            }
        
        self._complete_task(task_id, result)
        print(f"✅ Case law retrieved!\n")
        return result
    
    def fetch_all_by_category(self, category: str) -> Dict[str, Any]:
        """
        Fetch all torts in a specific category.
        
        Usage: gopherbot.fetch_all_by_category("privacy")
        """
        print(f"🐹 Fetching all torts in category: {category}...")
        
        try:
            category_enum = TortCategory[category.upper()]
        except KeyError:
            return {
                "status": "error",
                "error": f"Category '{category}' not found",
                "available_categories": [c.value for c in TortCategory]
            }
        
        torts = self.torts_index.search_torts_by_category(category_enum)
        
        result = {
            "status": "success",
            "category": category,
            "count": len(torts),
            "torts": [
                {
                    "name": t.tort_name,
                    "subcategory": t.subcategory.value,
                    "elements_count": len(t.elements),
                    "defenses_count": len(t.defenses)
                }
                for t in torts
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Found {len(torts)} torts in {category}!\n")
        return result
    
    # ==================== ANALYSIS COMMANDS ====================
    
    def analyze_facts(self, fact_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze fact pattern and identify applicable torts.
        
        Usage: gopherbot.analyze_facts({
            'intentional': True,
            'physical_contact': True,
            'emotional_distress': True
        })
        """
        task_id = self._create_task(GopherTaskType.ANALYZE_FACT_PATTERN, str(fact_pattern))
        
        print(f"🐹 Analyzing fact pattern...")
        print(f"   Facts provided: {len(fact_pattern)} factors")
        
        applicable_torts = self.torts_index.find_applicable_torts(fact_pattern)
        
        detailed_analysis = []
        for tort_name in applicable_torts:
            tort_def = self.torts_index.get_tort_definition(tort_name)
            if tort_def:
                detailed_analysis.append({
                    "tort_name": tort_def.tort_name,
                    "category": tort_def.category.value,
                    "elements": [e.element_name for e in tort_def.elements],
                    "strength": self._assess_claim_strength(tort_def, fact_pattern),
                    "statute_of_limitations": tort_def.statute_of_limitations_years.get("default", "varies"),
                    "key_defenses": [d.value for d in tort_def.defenses[:3]]
                })
        
        # Rank by strength
        detailed_analysis.sort(key=lambda x: x["strength"], reverse=True)
        
        result = {
            "task_id": task_id,
            "status": "success",
            "fact_pattern": fact_pattern,
            "applicable_torts_count": len(applicable_torts),
            "detailed_analysis": detailed_analysis,
            "strongest_claims": [a["tort_name"] for a in detailed_analysis[:3]],
            "recommended_next_steps": [
                "Gather evidence for each element",
                "Verify statute of limitations has not expired",
                "Consider settlement alternatives",
                "Consult licensed attorney for case evaluation"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self._complete_task(task_id, result)
        print(f"✅ Analysis complete! Found {len(applicable_torts)} applicable torts.\n")
        return result
    
    def check_deadline(self, tort_name: str, incident_date: str, jurisdiction: str = "default") -> Dict[str, Any]:
        """
        Check statute of limitations deadline.
        
        Usage: gopherbot.check_deadline("battery", "2023-01-15", "california")
        """
        task_id = self._create_task(GopherTaskType.DEADLINE_TRACKING, f"{tort_name} | {incident_date}")
        
        print(f"🐹 Checking deadline for {tort_name}...")
        
        from datetime import datetime as dt
        
        sol_years = self.torts_index.get_statute_of_limitations(tort_name, jurisdiction)
        
        if not sol_years:
            result = {
                "task_id": task_id,
                "status": "error",
                "error": f"Could not find statute of limitations for '{tort_name}'"
            }
        else:
            try:
                incident = dt.fromisoformat(incident_date)
                current = dt.now()
                years_elapsed = (current - incident).days / 365.25
                
                expired = years_elapsed > sol_years
                time_remaining = max(0, sol_years - years_elapsed)
                days_remaining = int(time_remaining * 365.25)
                
                # Calculate exact deadline
                deadline = incident.replace(year=incident.year + sol_years)
                
                if time_remaining < 0.25:  # Less than 3 months
                    urgency = "🚨 IMMEDIATE ACTION REQUIRED"
                elif time_remaining < 1:
                    urgency = "⚠️ HIGH URGENCY"
                else:
                    urgency = "✓ Adequate time remaining"
                
                result = {
                    "task_id": task_id,
                    "status": "success",
                    "tort": tort_name,
                    "jurisdiction": jurisdiction,
                    "statute_years": sol_years,
                    "incident_date": incident_date,
                    "deadline_date": deadline.isoformat(),
                    "years_elapsed": round(years_elapsed, 2),
                    "days_remaining": days_remaining,
                    "expired": expired,
                    "urgency": urgency,
                    "recommendation": "IMMEDIATE LEGAL CONSULTATION" if expired or time_remaining < 0.25 else "Proceed with case preparation"
                }
            except ValueError:
                result = {
                    "task_id": task_id,
                    "status": "error",
                    "error": "Invalid date format. Use YYYY-MM-DD."
                }
        
        self._complete_task(task_id, result)
        print(f"✅ Deadline check complete!\n")
        return result
    
    # ==================== RESEARCH COMMANDS ====================
    
    def research_topic(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Comprehensive research on legal topic.
        
        Usage: gopherbot.research_topic("defamation", ["public figure", "actual malice"])
        """
        task_id = self._create_task(GopherTaskType.RESEARCH_TOPIC, f"{topic} | {', '.join(keywords)}")
        
        print(f"🐹 Researching topic: {topic}")
        print(f"   Keywords: {', '.join(keywords)}")
        
        # Gather all relevant materials
        research_results = {
            "maxims": [],
            "landmark_cases": [],
            "restatements": [],
            "federal_rules": []
        }
        
        for keyword in keywords + [topic]:
            results = self.legal_research.search_by_keyword(keyword)
            for key in research_results:
                research_results[key].extend(results[key])
        
        # Remove duplicates
        for key in research_results:
            research_results[key] = list({id(item): item for item in research_results[key]}.values())
        
        result = {
            "task_id": task_id,
            "status": "success",
            "topic": topic,
            "keywords": keywords,
            "findings": {
                "maxims_found": len(research_results["maxims"]),
                "cases_found": len(research_results["landmark_cases"]),
                "restatements_found": len(research_results["restatements"]),
                "federal_rules_found": len(research_results["federal_rules"])
            },
            "top_cases": [
                {
                    "case_name": c.case_name,
                    "citation": c.citation,
                    "principle": c.principle
                }
                for c in research_results["landmark_cases"][:3]
            ],
            "top_maxims": [
                {
                    "latin": m.latin,
                    "english": m.english,
                    "application": m.application
                }
                for m in research_results["maxims"][:3]
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self._complete_task(task_id, result)
        print(f"✅ Research complete!\n")
        return result
    
    def generate_memo(self, issue: str, keywords: List[str]) -> str:
        """
        Generate comprehensive legal memorandum.
        
        Usage: gopherbot.generate_memo("Liability for data breach", ["negligence", "cybersecurity"])
        """
        task_id = self._create_task(GopherTaskType.GENERATE_MEMO, issue)
        
        print(f"🐹 Generating legal memorandum...")
        print(f"   Issue: {issue}")
        
        memo = self.legal_research.generate_legal_memo(issue, keywords)
        
        result = {
            "task_id": task_id,
            "status": "success",
            "issue": issue,
            "memo_text": memo,
            "word_count": len(memo.split()),
            "timestamp": datetime.now().isoformat()
        }
        
        self._complete_task(task_id, result)
        print(f"✅ Memo generated! ({len(memo.split())} words)\n")
        return memo
    
    # ==================== COMPLIANCE & RISK ====================
    
    def compliance_check(self, organization_type: str, data_types: List[str], jurisdictions: List[str]) -> Dict[str, Any]:
        """
        Check compliance requirements.
        
        Usage: gopherbot.compliance_check("SaaS", ["PII", "financial"], ["US", "EU"])
        """
        task_id = self._create_task(GopherTaskType.COMPLIANCE_CHECK, organization_type)
        
        print(f"🐹 Checking compliance requirements...")
        print(f"   Organization: {organization_type}")
        print(f"   Data types: {', '.join(data_types)}")
        print(f"   Jurisdictions: {', '.join(jurisdictions)}")
        
        frameworks = []
        risk_level = "LOW"
        
        # HIPAA
        if "PHI" in data_types or organization_type.lower() == "healthcare":
            frameworks.append("HIPAA")
            risk_level = "HIGH"
        
        # GDPR
        if "EU" in jurisdictions:
            frameworks.append("GDPR")
            risk_level = "HIGH"
        
        # CCPA/CPRA
        if "CA" in jurisdictions or "California" in jurisdictions:
            frameworks.append("CCPA/CPRA")
        
        # PCI-DSS
        if "financial" in data_types or "credit card" in data_types:
            frameworks.append("PCI-DSS")
        
        # SOC 2
        if organization_type.lower() in ["saas", "software", "technology"]:
            frameworks.append("SOC 2")
        
        result = {
            "task_id": task_id,
            "status": "success",
            "organization_type": organization_type,
            "applicable_frameworks": frameworks,
            "risk_level": risk_level,
            "immediate_actions": [
                f"Review {fw} requirements" for fw in frameworks
            ],
            "documentation_needed": [
                "Privacy Policy",
                "Terms of Service",
                "Data Processing Agreements",
                "Security Policies"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self._complete_task(task_id, result)
        print(f"✅ Compliance check complete! Risk level: {risk_level}\n")
        return result
    
    def assess_platform_risk(self, activity: str) -> Dict[str, Any]:
        """
        Assess tort liability risk for platform activity.
        
        Usage: gopherbot.assess_platform_risk("account_termination")
        """
        task_id = self._create_task(GopherTaskType.RISK_ASSESSMENT, activity)
        
        print(f"🐹 Assessing risk for activity: {activity}")
        
        risk_analysis = self.covenant_integrity.assess_covenant_breach_legal_exposure(activity, {})
        
        result = {
            "task_id": task_id,
            "status": "success",
            "activity": activity,
            "risk_analysis": risk_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        self._complete_task(task_id, result)
        print(f"✅ Risk assessment complete!\n")
        return result
    
    # ==================== UTILITY COMMANDS ====================
    
    def show_queue(self) -> Dict[str, Any]:
        """Show current task queue"""
        return {
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "queue": self.task_queue
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task history"""
        return self.completed_tasks[-limit:]
    
    def export_results(self, filepath: str):
        """Export all completed tasks to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.completed_tasks, f, indent=2, ensure_ascii=False)
        print(f"✅ Results exported to {filepath}")
    
    # ==================== HELPER METHODS ====================
    
    def _create_task(self, task_type: GopherTaskType, description: str) -> str:
        """Create new task and add to queue"""
        task_id = f"GOPHER-{len(self.task_queue) + len(self.completed_tasks) + 1:04d}"
        task = {
            "task_id": task_id,
            "type": task_type.value,
            "description": description,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        self.task_queue.append(task)
        return task_id
    
    def _complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as complete and move to history"""
        for task in self.task_queue:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                task["completed"] = datetime.now().isoformat()
                task["result"] = result
                self.completed_tasks.append(task)
                self.task_queue.remove(task)
                break
    
    def _suggest_similar_torts(self, tort_name: str) -> List[str]:
        """Suggest similar tort names"""
        all_torts = list(self.torts_index.torts_database.keys())
        # Simple similarity: starts with same letter or contains substring
        suggestions = [t for t in all_torts if t[0] == tort_name[0] or tort_name[:3] in t]
        return suggestions[:5]
    
    def _assess_claim_strength(self, tort_def, facts: Dict[str, Any]) -> str:
        """Assess strength of tort claim based on facts"""
        # Simple heuristic: check how many fact indicators match tort category
        strength_score = 0
        
        if tort_def.category == TortCategory.INTENTIONAL and facts.get('intentional'):
            strength_score += 2
        if tort_def.category == TortCategory.NEGLIGENCE and facts.get('negligent'):
            strength_score += 2
        if facts.get('physical_contact') and 'battery' in tort_def.tort_name.lower():
            strength_score += 3
        if facts.get('emotional_distress') and 'emotional' in tort_def.tort_name.lower():
            strength_score += 3
        if facts.get('economic_loss') and tort_def.category == TortCategory.ECONOMIC:
            strength_score += 2
        
        if strength_score >= 5:
            return "STRONG"
        elif strength_score >= 3:
            return "MODERATE"
        else:
            return "WEAK"


# ==================== INTERACTIVE COMMANDS ====================

class GopherCommands:
    """
    Interactive command interface for Gopherbot.
    Use natural language commands to interact with the bot.
    """
    
    def __init__(self, gopherbot: MytharaGopherbot):
        self.bot = gopherbot
    
    def help(self):
        """Display available commands"""
        print("\n🐹 Mythara Gopherbot Commands:")
        print("=" * 60)
        print("FETCH COMMANDS:")
        print("  • fetch tort <name>              - Get tort definition")
        print("  • fetch case <name>              - Get case law")
        print("  • fetch category <name>          - Get all torts in category")
        print()
        print("ANALYSIS COMMANDS:")
        print("  • analyze facts                  - Analyze fact pattern")
        print("  • check deadline <tort> <date>   - Check statute of limitations")
        print()
        print("RESEARCH COMMANDS:")
        print("  • research <topic>               - Research legal topic")
        print("  • generate memo <issue>          - Generate legal memo")
        print()
        print("COMPLIANCE COMMANDS:")
        print("  • compliance check               - Check compliance requirements")
        print("  • assess risk <activity>         - Assess platform risk")
        print()
        print("UTILITY COMMANDS:")
        print("  • show queue                     - Show task queue")
        print("  • history                        - Show task history")
        print("  • export <filepath>              - Export results to JSON")
        print("=" * 60 + "\n")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🐹 MYTHARA GOPHERBOT - DEMONSTRATION")
    print("=" * 60 + "\n")
    
    # Initialize Gopherbot
    gopherbot = MytharaGopherbot()
    commands = GopherCommands(gopherbot)
    
    # Demo 1: Fetch tort definition
    print("=" * 60)
    print("DEMO 1: FETCH TORT DEFINITION")
    print("=" * 60 + "\n")
    
    battery = gopherbot.fetch_tort("battery")
    print(f"Tort: {battery['tort_name']}")
    print(f"Category: {battery['category']}")
    print(f"Elements: {len(battery['elements'])}")
    print(f"Defenses: {len(battery['defenses'])}")
    
    # Demo 2: Analyze fact pattern
    print("\n" + "=" * 60)
    print("DEMO 2: ANALYZE FACT PATTERN")
    print("=" * 60 + "\n")
    
    facts = {
        'intentional': True,
        'physical_contact': True,
        'emotional_distress': True,
        'data_breach': False
    }
    
    analysis = gopherbot.analyze_facts(facts)
    print(f"Applicable torts: {analysis['applicable_torts_count']}")
    print(f"Strongest claims: {', '.join(analysis['strongest_claims'])}")
    
    # Demo 3: Check deadline
    print("\n" + "=" * 60)
    print("DEMO 3: CHECK STATUTE OF LIMITATIONS")
    print("=" * 60 + "\n")
    
    deadline = gopherbot.check_deadline("battery", "2023-11-15", "california")
    print(f"Tort: {deadline['tort']}")
    print(f"Days remaining: {deadline['days_remaining']}")
    print(f"Urgency: {deadline['urgency']}")
    
    # Demo 4: Research topic
    print("\n" + "=" * 60)
    print("DEMO 4: RESEARCH LEGAL TOPIC")
    print("=" * 60 + "\n")
    
    research = gopherbot.research_topic("negligence", ["duty", "breach", "causation"])
    print(f"Maxims found: {research['findings']['maxims_found']}")
    print(f"Cases found: {research['findings']['cases_found']}")
    print(f"Top case: {research['top_cases'][0]['case_name'] if research['top_cases'] else 'None'}")
    
    # Demo 5: Compliance check
    print("\n" + "=" * 60)
    print("DEMO 5: COMPLIANCE CHECK")
    print("=" * 60 + "\n")
    
    compliance = gopherbot.compliance_check("SaaS", ["PII", "financial"], ["US", "EU"])
    print(f"Applicable frameworks: {', '.join(compliance['applicable_frameworks'])}")
    print(f"Risk level: {compliance['risk_level']}")
    
    # Demo 6: Show task history
    print("\n" + "=" * 60)
    print("DEMO 6: TASK HISTORY")
    print("=" * 60 + "\n")
    
    history = gopherbot.get_task_history(5)
    print(f"Completed tasks: {len(history)}")
    for task in history:
        print(f"  • {task['task_id']}: {task['type']} - {task['description'][:40]}...")
    
    # Show available commands
    print("\n")
    commands.help()
    
    print("=" * 60)
    print("⚖️  DISCLAIMER: NOT LEGAL ADVICE")
    print("=" * 60)
    print("Gopherbot provides informational guidance only.")
    print("Consult licensed attorney for specific legal matters.")
    print("=" * 60 + "\n")
