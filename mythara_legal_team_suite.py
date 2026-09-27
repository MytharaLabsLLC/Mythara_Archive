#!/usr/bin/env python3
"""
Mythara Legal Team Suite - Comprehensive Legal Bot Architecture
Multi-area legal support bot architecture.

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

# Import the comprehensive torts framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'source_proprietary'))
from torts_law_framework import TortsLawIndex, TortsCovenantIntegrity, TortCategory
from legal_resources_index import LegalResearchEngine, LegalDomain


class LegalPracticeArea(Enum):
    """Major legal practice areas"""
    CORPORATE = "corporate"
    EMPLOYMENT = "employment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    REAL_ESTATE = "real_estate"
    LITIGATION = "litigation"
    COMPLIANCE = "compliance"
    CONTRACTS = "contracts"
    PRIVACY = "privacy"


class MytharaLegalTeamSuite:
    """
    Comprehensive legal team suite with 12 specialized legal bots.
    
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
        
        # Initialize all legal bots
        self.torts_analyzer = TortsAnalyzerBot(self.torts_index)
        self.contract_reviewer = ContractReviewBot(self.legal_research)
        self.compliance_monitor = ComplianceMonitorBot(self.legal_research)
        self.ip_guardian = IPGuardianBot(self.torts_index, self.legal_research)
        self.employment_counsel = EmploymentCounselBot(self.torts_index)
        self.privacy_sentinel = PrivacySentinelBot(self.torts_index)
        self.litigation_strategist = LitigationStrategistBot(self.torts_index, self.legal_research)
        self.healthcare_compliance = HealthcareComplianceBot(self.torts_index)
        self.corporate_governance = CorporateGovernanceBot(self.legal_research)
        self.real_estate_advisor = RealEstateAdvisorBot(self.torts_index)
        self.technology_counsel = TechnologyCounselBot(self.torts_index)
        self.regulatory_navigator = RegulatoryNavigatorBot(self.legal_research)
        
        print("🏛️ Mythara Legal Team Suite Initialized")
        print("=" * 60)
        print("12 Specialized Legal Bots Active:")
        print("  1. Torts Analyzer")
        print("  2. Contract Reviewer")
        print("  3. Compliance Monitor")
        print("  4. IP Guardian")
        print("  5. Employment Counsel")
        print("  6. Privacy Sentinel")
        print("  7. Litigation Strategist")
        print("  8. Healthcare Compliance")
        print("  9. Corporate Governance")
        print(" 10. Real Estate Advisor")
        print(" 11. Technology Counsel")
        print(" 12. Regulatory Navigator")
        print("=" * 60)
        print("⚠️  NOT A SUBSTITUTE FOR LICENSED ATTORNEY")
        print("=" * 60)


# ===================== BOT 1: TORTS ANALYZER =====================

class TortsAnalyzerBot:
    """
    Analyzes fact patterns for potential tort claims and defenses.
    Provides comprehensive tort law guidance across all categories.
    """
    
    def __init__(self, torts_index: TortsLawIndex):
        self.torts_index = torts_index
        self.name = "Torts Analyzer Bot"
    
    def analyze_fact_pattern(self, facts: Dict[str, any]) -> Dict[str, any]:
        """
        Analyze facts and identify applicable torts.
        
        Args:
            facts: Dictionary with keys like 'intentional', 'physical_contact',
                   'property_damage', 'economic_loss', etc.
        
        Returns:
            Analysis with applicable torts, elements, and defenses
        """
        applicable_torts = self.torts_index.find_applicable_torts(facts)
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "fact_summary": facts,
            "applicable_torts": [],
            "strongest_claims": [],
            "potential_defenses": [],
            "recommended_actions": []
        }
        
        for tort_name in applicable_torts:
            tort_def = self.torts_index.get_tort_definition(tort_name)
            if tort_def:
                tort_analysis = {
                    "tort_name": tort_def.tort_name,
                    "category": tort_def.category.value,
                    "elements": [
                        {
                            "name": elem.element_name,
                            "description": elem.description,
                            "proof_standard": elem.proof_standard
                        }
                        for elem in tort_def.elements
                    ],
                    "potential_defenses": [d.value for d in tort_def.defenses],
                    "statute_of_limitations": tort_def.statute_of_limitations_years.get("default", "varies"),
                    "landmark_cases": tort_def.landmark_cases[:2]  # Top 2
                }
                analysis["applicable_torts"].append(tort_analysis)
        
        # Rank claims by strength
        if len(analysis["applicable_torts"]) > 0:
            analysis["strongest_claims"] = [t["tort_name"] for t in analysis["applicable_torts"][:3]]
        
        # Generate recommendations
        if applicable_torts:
            analysis["recommended_actions"].append("Consult licensed attorney for case evaluation")
            analysis["recommended_actions"].append("Gather evidence for each element")
            analysis["recommended_actions"].append("Verify statute of limitations has not expired")
            analysis["recommended_actions"].append("Consider alternative dispute resolution")
        
        return analysis
    
    def check_statute_of_limitations(self, tort_name: str, incident_date: str, jurisdiction: str = "default") -> Dict[str, any]:
        """Check if statute of limitations has expired"""
        from datetime import datetime
        
        sol_years = self.torts_index.get_statute_of_limitations(tort_name, jurisdiction)
        if not sol_years:
            return {"error": "Tort not found"}
        
        incident = datetime.fromisoformat(incident_date)
        current = datetime.now()
        years_elapsed = (current - incident).days / 365.25
        
        expired = years_elapsed > sol_years
        time_remaining = max(0, sol_years - years_elapsed)
        
        return {
            "tort": tort_name,
            "jurisdiction": jurisdiction,
            "statute_years": sol_years,
            "incident_date": incident_date,
            "years_elapsed": round(years_elapsed, 2),
            "expired": expired,
            "years_remaining": round(time_remaining, 2),
            "urgency": "IMMEDIATE" if time_remaining < 0.25 else "HIGH" if time_remaining < 1 else "MODERATE"
        }


# ===================== BOT 2: CONTRACT REVIEWER =====================

class ContractReviewBot:
    """
    Reviews contracts for legal risks, unfavorable terms, and compliance issues.
    Provides redline suggestions and negotiation guidance.
    """
    
    def __init__(self, legal_research: LegalResearchEngine):
        self.legal_research = legal_research
        self.name = "Contract Review Bot"
    
    def review_contract_terms(self, contract_type: str, terms: List[str]) -> Dict[str, any]:
        """
        Review contract terms for legal risks.
        
        Args:
            contract_type: Type of contract (employment, SaaS, NDA, etc.)
            terms: List of contract clauses to review
        
        Returns:
            Risk analysis with recommendations
        """
        review = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "contract_type": contract_type,
            "high_risk_terms": [],
            "recommended_changes": [],
            "favorable_terms": [],
            "compliance_issues": []
        }
        
        # Common red flags
        red_flags = [
            "unlimited liability",
            "no limitation of liability",
            "automatic renewal",
            "perpetual license",
            "non-compete",
            "assignment without consent",
            "unilateral modification",
            "no termination right",
            "forum selection",
            "mandatory arbitration",
            "class action waiver"
        ]
        
        for term in terms:
            term_lower = term.lower()
            for red_flag in red_flags:
                if red_flag in term_lower:
                    review["high_risk_terms"].append({
                        "term": term,
                        "risk": red_flag,
                        "severity": "HIGH",
                        "recommendation": f"Negotiate {red_flag} clause or seek cap/limitation"
                    })
        
        # Contract-specific checks
        if contract_type.lower() == "saas":
            review["recommended_changes"].append("Add SLA with uptime guarantees")
            review["recommended_changes"].append("Include data portability clause")
            review["recommended_changes"].append("Verify GDPR/CCPA compliance provisions")
        
        if contract_type.lower() == "employment":
            review["recommended_changes"].append("Review non-compete scope and duration")
            review["recommended_changes"].append("Ensure IP assignment is limited to scope of work")
            review["recommended_changes"].append("Verify at-will employment disclaimers")
        
        return review
    
    def generate_redline_suggestions(self, problematic_clause: str) -> Dict[str, str]:
        """Generate suggested redline for problematic clause"""
        return {
            "original": problematic_clause,
            "suggested_revision": "CONSULT ATTORNEY for specific redline",
            "rationale": "Legal counsel should review based on client's specific risk tolerance",
            "negotiation_leverage": "Depends on parties' relative bargaining power"
        }


# ===================== BOT 3: COMPLIANCE MONITOR =====================

class ComplianceMonitorBot:
    """
    Monitors regulatory compliance across multiple domains.
    Tracks GDPR, CCPA, HIPAA, SOC 2, and industry-specific regulations.
    """
    
    def __init__(self, legal_research: LegalResearchEngine):
        self.legal_research = legal_research
        self.name = "Compliance Monitor Bot"
        self.frameworks = ["GDPR", "CCPA", "HIPAA", "SOC2", "PCI-DSS", "COPPA", "FERPA"]
    
    def assess_compliance(self, organization_type: str, data_types: List[str], jurisdictions: List[str]) -> Dict[str, any]:
        """
        Assess compliance requirements.
        
        Args:
            organization_type: Type of org (healthcare, fintech, SaaS, etc.)
            data_types: Types of data handled (PHI, PII, financial, etc.)
            jurisdictions: Geographic jurisdictions (US, EU, CA, etc.)
        
        Returns:
            Compliance assessment with requirements
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "organization_type": organization_type,
            "applicable_frameworks": [],
            "required_controls": [],
            "documentation_requirements": [],
            "risk_level": "LOW"
        }
        
        # Determine applicable frameworks
        if "PHI" in data_types or organization_type.lower() == "healthcare":
            assessment["applicable_frameworks"].append({
                "framework": "HIPAA",
                "requirements": [
                    "Administrative Safeguards (45 CFR § 164.308)",
                    "Physical Safeguards (45 CFR § 164.310)",
                    "Technical Safeguards (45 CFR § 164.312)",
                    "Business Associate Agreements",
                    "Breach Notification (45 CFR § 164.400)"
                ]
            })
            assessment["risk_level"] = "HIGH"
        
        if "EU" in jurisdictions or "GDPR" in data_types:
            assessment["applicable_frameworks"].append({
                "framework": "GDPR",
                "requirements": [
                    "Lawful basis for processing (Art. 6)",
                    "Data subject rights (Art. 15-22)",
                    "Data Protection Impact Assessment (Art. 35)",
                    "Data Processing Agreements (Art. 28)",
                    "72-hour breach notification (Art. 33)"
                ]
            })
            assessment["risk_level"] = "HIGH"
        
        if "CA" in jurisdictions or "California" in jurisdictions:
            assessment["applicable_frameworks"].append({
                "framework": "CCPA/CPRA",
                "requirements": [
                    "Privacy notice with data categories",
                    "Do Not Sell/Share opt-out",
                    "Right to deletion",
                    "Right to access",
                    "Authorized agent verification"
                ]
            })
        
        if "financial" in data_types or "credit card" in data_types:
            assessment["applicable_frameworks"].append({
                "framework": "PCI-DSS",
                "requirements": [
                    "Requirement 1: Install and maintain network security controls",
                    "Requirement 2: Apply secure configurations",
                    "Requirement 3: Protect stored account data",
                    "Requirement 8: Identify users and authenticate access",
                    "Requirement 10: Log and monitor all access"
                ]
            })
        
        # Required controls
        assessment["required_controls"] = [
            "Encryption at rest and in transit",
            "Access controls with role-based permissions",
            "Audit logging with tamper-evident logs",
            "Incident response plan",
            "Regular security assessments",
            "Vendor security reviews"
        ]
        
        # Documentation
        assessment["documentation_requirements"] = [
            "Privacy Policy",
            "Terms of Service",
            "Data Processing Agreements",
            "Security policies and procedures",
            "Breach response plan",
            "Records of processing activities"
        ]
        
        return assessment


# ===================== BOT 4: IP GUARDIAN =====================

class IPGuardianBot:
    """
    Protects intellectual property rights.
    Handles patents, trademarks, copyrights, and trade secrets.
    """
    
    def __init__(self, torts_index: TortsLawIndex, legal_research: LegalResearchEngine):
        self.torts_index = torts_index
        self.legal_research = legal_research
        self.name = "IP Guardian Bot"
    
    def assess_infringement_risk(self, ip_type: str, use_case: str) -> Dict[str, any]:
        """
        Assess potential IP infringement risks.
        
        Args:
            ip_type: Type of IP (patent, trademark, copyright, trade_secret)
            use_case: Description of intended use
        
        Returns:
            Risk assessment with clearance recommendations
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "ip_type": ip_type,
            "use_case": use_case,
            "infringement_risks": [],
            "clearance_steps": [],
            "defensive_strategies": []
        }
        
        if ip_type.lower() == "patent":
            assessment["infringement_risks"].append("Utility patent infringement (35 U.S.C. § 271)")
            assessment["clearance_steps"] = [
                "Conduct patent search (USPTO, Google Patents)",
                "Freedom-to-operate (FTO) opinion from patent attorney",
                "Identify blocking patents",
                "Consider design-around options",
                "Evaluate invalidity/non-infringement arguments"
            ]
            assessment["defensive_strategies"] = [
                "File own patent applications",
                "Prior art search for invalidity defenses",
                "License negotiations if blocking patent found"
            ]
        
        elif ip_type.lower() == "trademark":
            assessment["infringement_risks"].append("Trademark infringement and dilution")
            assessment["clearance_steps"] = [
                "USPTO TESS database search",
                "State trademark database search",
                "Common law trademark search (Google, domain names)",
                "Likelihood of confusion analysis (DuPont factors)",
                "Clearance opinion from trademark attorney"
            ]
            assessment["defensive_strategies"] = [
                "File trademark application promptly",
                "Use ™ symbol (® after registration)",
                "Consistent use in commerce",
                "Monitor for infringement"
            ]
        
        elif ip_type.lower() == "copyright":
            assessment["infringement_risks"].append("Copyright infringement (17 U.S.C. § 501)")
            assessment["clearance_steps"] = [
                "Verify work is original or licensed",
                "Check public domain status",
                "Evaluate fair use factors (17 U.S.C. § 107)",
                "Obtain licenses where needed"
            ]
            assessment["defensive_strategies"] = [
                "Register copyrights with US Copyright Office",
                "Use © notice",
                "Include license terms in distribution",
                "DMCA takedown procedures for online use"
            ]
        
        elif ip_type.lower() == "trade_secret":
            trade_secret_tort = self.torts_index.get_tort_definition("trade_secret_misappropriation")
            if trade_secret_tort:
                assessment["infringement_risks"].append("Trade secret misappropriation (UTSA/DTSA)")
                assessment["clearance_steps"] = [
                    "Verify secrecy measures in place",
                    "Confirm information not generally known",
                    "Document economic value",
                    "Review employee/vendor NDAs"
                ]
                assessment["defensive_strategies"] = [
                    "Implement robust confidentiality agreements",
                    "Physical and digital access controls",
                    "Employee training on trade secret protection",
                    "Departure procedures for departing employees",
                    "Mark documents as confidential/proprietary"
                ]
        
        return assessment
    
    def generate_ip_protection_checklist(self, business_type: str) -> List[str]:
        """Generate IP protection checklist for business"""
        checklist = [
            "✓ Conduct IP audit of all company assets",
            "✓ File trademark applications for brand names/logos",
            "✓ Copyright registration for key creative works",
            "✓ Patent search for innovative technology",
            "✓ Employee IP assignment agreements",
            "✓ Vendor/contractor IP clauses",
            "✓ Trade secret identification and protection",
            "✓ Open source license compliance review",
            "✓ Domain name portfolio protection",
            "✓ Social media handle registration"
        ]
        
        if business_type.lower() in ["saas", "software", "technology"]:
            checklist.extend([
                "✓ Software copyright notices in code",
                "✓ API terms of service with IP protections",
                "✓ DMCA agent registration",
                "✓ License compliance tooling (FOSS)"
            ])
        
        return checklist


# ===================== BOT 5: EMPLOYMENT COUNSEL =====================

class EmploymentCounselBot:
    """
    Provides employment law guidance.
    Covers hiring, termination, discrimination, harassment, and wage-hour.
    """
    
    def __init__(self, torts_index: TortsLawIndex):
        self.torts_index = torts_index
        self.name = "Employment Counsel Bot"
    
    def assess_termination_risk(self, employee_info: Dict[str, any], termination_reason: str) -> Dict[str, any]:
        """
        Assess legal risk of employee termination.
        
        Args:
            employee_info: Employee details (tenure, protected class, complaints, etc.)
            termination_reason: Stated reason for termination
        
        Returns:
            Risk assessment with recommendations
        """
        risk_assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "overall_risk": "LOW",
            "potential_claims": [],
            "risk_factors": [],
            "recommended_steps": [],
            "documentation_required": []
        }
        
        # Check wrongful termination risk
        wrongful_term = self.torts_index.get_tort_definition("wrongful_termination")
        if wrongful_term:
            risk_assessment["potential_claims"].append({
                "claim": "Wrongful Termination in Violation of Public Policy",
                "elements": [e.element_name for e in wrongful_term.elements],
                "statute_of_limitations": wrongful_term.statute_of_limitations_years.get("default")
            })
        
        # Risk factors
        if employee_info.get("recent_complaint"):
            risk_assessment["risk_factors"].append("Recent complaint filed (retaliation risk)")
            risk_assessment["overall_risk"] = "HIGH"
        
        if employee_info.get("protected_class"):
            risk_assessment["risk_factors"].append("Protected class member (discrimination risk)")
            risk_assessment["overall_risk"] = "MEDIUM" if risk_assessment["overall_risk"] == "LOW" else "HIGH"
        
        if employee_info.get("tenure_years", 0) > 5:
            risk_assessment["risk_factors"].append("Long tenure employee (higher damages exposure)")
        
        if "performance" not in termination_reason.lower():
            risk_assessment["risk_factors"].append("Non-performance termination (requires stronger justification)")
        
        # Recommended steps
        risk_assessment["recommended_steps"] = [
            "Document performance issues with specific examples",
            "Review personnel file for completeness",
            "Ensure progressive discipline was followed",
            "Verify no protected activity preceded termination",
            "Prepare severance agreement with release",
            "Conduct exit interview",
            "Consult employment attorney before finalizing"
        ]
        
        # Documentation
        risk_assessment["documentation_required"] = [
            "Performance reviews",
            "Disciplinary warnings",
            "Termination memo with business justification",
            "Final paycheck calculation",
            "COBRA notice",
            "Separation agreement (if applicable)"
        ]
        
        return risk_assessment
    
    def generate_hiring_checklist(self) -> List[str]:
        """Generate compliant hiring process checklist"""
        return [
            "✓ Job description with essential functions",
            "✓ Neutral job posting (no discriminatory language)",
            "✓ Structured interview questions",
            "✓ Background check with FCRA disclosures",
            "✓ Reference checks",
            "✓ Offer letter (not employment contract unless intended)",
            "✓ At-will employment acknowledgment",
            "✓ I-9 verification",
            "✓ W-4 and state tax forms",
            "✓ Employee handbook acknowledgment",
            "✓ IP assignment agreement",
            "✓ Confidentiality/NDA",
            "✓ Arbitration agreement (if applicable)",
            "✓ Benefits enrollment"
        ]


# ===================== BOT 6: PRIVACY SENTINEL =====================

class PrivacySentinelBot:
    """
    Monitors privacy compliance and data protection.
    Handles GDPR, CCPA, data breaches, and privacy torts.
    """
    
    def __init__(self, torts_index: TortsLawIndex):
        self.torts_index = torts_index
        self.name = "Privacy Sentinel Bot"
    
    def assess_privacy_tort_risk(self, activity: str, data_types: List[str]) -> Dict[str, any]:
        """
        Assess privacy tort exposure from business activity.
        
        Args:
            activity: Description of data processing activity
            data_types: Types of personal data involved
        
        Returns:
            Privacy tort risk assessment
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "activity": activity,
            "applicable_privacy_torts": [],
            "risk_level": "LOW",
            "mitigation_strategies": []
        }
        
        # Check intrusion upon seclusion
        intrusion_tort = self.torts_index.get_tort_definition("intrusion_upon_seclusion")
        if intrusion_tort and ("surveillance" in activity.lower() or "monitoring" in activity.lower()):
            assessment["applicable_privacy_torts"].append({
                "tort": "Intrusion Upon Seclusion",
                "risk": "MEDIUM",
                "elements": [e.element_name for e in intrusion_tort.elements],
                "defenses": [d.value for d in intrusion_tort.defenses]
            })
            assessment["risk_level"] = "MEDIUM"
        
        # Check public disclosure of private facts
        disclosure_tort = self.torts_index.get_tort_definition("public_disclosure")
        if disclosure_tort and ("publish" in activity.lower() or "disclose" in activity.lower()):
            assessment["applicable_privacy_torts"].append({
                "tort": "Public Disclosure of Private Facts",
                "risk": "HIGH",
                "elements": [e.element_name for e in disclosure_tort.elements],
                "defenses": [d.value for d in disclosure_tort.defenses]
            })
            assessment["risk_level"] = "HIGH"
        
        # Mitigation strategies
        assessment["mitigation_strategies"] = [
            "Obtain explicit consent for data collection",
            "Provide clear privacy notice",
            "Implement data minimization principles",
            "Offer opt-out mechanisms",
            "Encrypt sensitive data",
            "Regular privacy impact assessments",
            "Incident response plan for breaches"
        ]
        
        return assessment


# ===================== Additional Bots =====================
# NOTE: Every method below returns deterministic rule/keyword analysis over
# caller-supplied facts. Nothing here is legal advice. Outputs carry the
# not-a-lawyer disclaimer; consult a licensed attorney for real matters.

class LitigationStrategistBot:
    """
    Litigation strategy and case management.
    Scores case strength from observable case factors; generates phase timelines.
    """
    def __init__(self, torts_index, legal_research):
        self.torts_index = torts_index
        self.legal_research = legal_research
        self.name = "Litigation Strategist Bot"

    def assess_case_strength(self, case_facts: Dict[str, any]) -> Dict[str, any]:
        """
        Score case strength from caller-supplied factors (0-100 per factor).
        Factors: evidence_strength, witness_support, damages_documented,
                 defendant_resources, applicable_law_favorable, defenses_known.
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "overall_score": 0,
            "strength_level": "WEAK",
            "factor_scores": {},
            "risks": [],
            "recommended_next_steps": [],
            "disclaimer": "Informational only — not legal advice. Consult a licensed litigator."
        }

        weights = {
            "evidence_strength": 0.30,
            "witness_support": 0.15,
            "damages_documented": 0.20,
            "defendant_resources": 0.10,
            "applicable_law_favorable": 0.15,
            "defenses_known": 0.10,
        }
        total = 0.0
        for factor, weight in weights.items():
            score = max(0, min(100, int(case_facts.get(factor, 0))))
            assessment["factor_scores"][factor] = score
            total += score * weight
        assessment["overall_score"] = round(total, 1)

        if total >= 75:
            assessment["strength_level"] = "STRONG"
        elif total >= 50:
            assessment["strength_level"] = "MODERATE"
        elif total >= 30:
            assessment["strength_level"] = "WEAK"

        if case_facts.get("evidence_strength", 0) < 40:
            assessment["risks"].append("Weak evidence base — discovery burden will be high")
        if case_facts.get("defenses_known", 0) > 60:
            assessment["risks"].append("Strong known defenses — expect dispositive motions")
        if case_facts.get("defendant_resources", 0) > 70:
            assessment["risks"].append("Well-resourced opponent — litigation will be expensive and long")
        if case_facts.get("damages_documented", 0) < 40:
            assessment["risks"].append("Damages poorly documented — recovery may not justify cost")

        assessment["recommended_next_steps"] = [
            "Preserve all evidence (litigation hold letter)",
            "Engage licensed litigation counsel for case evaluation",
            "Send demand letter before filing where appropriate",
            "Evaluate ADR (mediation/arbitration) vs. trial economics",
            "Calendar statute of limitations immediately",
        ]
        return assessment

    def generate_litigation_timeline(self, case_type: str = "civil") -> List[Dict[str, str]]:
        """Deterministic phase timeline for a civil litigation matter."""
        phases = [
            {"phase": "Pre-suit", "duration": "1-3 months",
             "actions": "Demand letter, evidence preservation, counsel engagement"},
            {"phase": "Pleadings", "duration": "2-4 months",
             "actions": "Complaint filed, answer/motion to dismiss, counterclaims"},
            {"phase": "Discovery", "duration": "6-12 months",
             "actions": "Document requests, depositions, interrogatories, experts retained"},
            {"phase": "Dispositive motions", "duration": "2-4 months",
             "actions": "Summary judgment briefing and argument"},
            {"phase": "ADR / settlement", "duration": "1-3 months",
             "actions": "Mediation, settlement conferences"},
            {"phase": "Trial", "duration": "1-4 weeks",
             "actions": "Jury/bench trial, verdict"},
            {"phase": "Post-trial / appeal", "duration": "6-18 months",
             "actions": "Post-trial motions, notice of appeal"},
        ]
        return [{"case_type": case_type, **p} for p in phases]


class HealthcareComplianceBot:
    """
    HIPAA, FDA, and healthcare-specific compliance.
    Checklist-based safeguard analysis over caller-supplied practices.
    """
    def __init__(self, torts_index):
        self.torts_index = torts_index
        self.name = "Healthcare Compliance Bot"
        self.phi_categories = [
            "names", "addresses", "dates", "phone_numbers", "fax_numbers",
            "email_addresses", "ssn", "medical_record_numbers", "health_plan_ids",
            "account_numbers", "certificate_numbers", "vehicle_ids", "device_ids",
            "web_urls", "ip_addresses", "biometric_ids", "photos", "other_ids",
        ]
        self.safeguards = {
            "administrative": ["risk_analysis", "workforce_training", "access_management",
                               "incident_response_plan", "business_associate_agreements"],
            "physical": ["facility_access_controls", "workstation_security",
                         "device_media_controls"],
            "technical": ["access_controls", "audit_controls", "integrity_controls",
                          "transmission_security", "encryption"],
        }

    def assess_hipaa_risk(self, practices: Dict[str, any]) -> Dict[str, any]:
        """
        Score HIPAA posture from caller-supplied practice flags.
        practices: {"implemented_safeguards": [...], "phi_categories_handled": [...],
                    "has_baa": bool, "breach_history": int}
        """
        implemented = set(practices.get("implemented_safeguards", []))
        all_safeguards = [s for group in self.safeguards.values() for s in group]
        missing = [s for s in all_safeguards if s not in implemented]

        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "safeguards_implemented": len(implemented),
            "safeguards_total": len(all_safeguards),
            "missing_safeguards": missing,
            "phi_categories_handled": practices.get("phi_categories_handled", []),
            "overall_risk": "LOW",
            "findings": [],
            "recommended_steps": [],
            "disclaimer": "Informational only — not legal advice. HIPAA compliance requires "
                          "qualified counsel and a formal risk analysis.",
        }

        coverage = len(implemented) / len(all_safeguards) if all_safeguards else 0
        if coverage < 0.5:
            assessment["overall_risk"] = "HIGH"
        elif coverage < 0.8:
            assessment["overall_risk"] = "MEDIUM"

        if not practices.get("has_baa"):
            assessment["findings"].append("No Business Associate Agreements in place")
            assessment["overall_risk"] = "HIGH"
        if practices.get("breach_history", 0) > 0:
            assessment["findings"].append(
                f"{practices['breach_history']} prior breach(es) — breach notification rule review required")
        if "encryption" not in implemented:
            assessment["findings"].append("Encryption not implemented (addressable but expected)")
        if "risk_analysis" not in implemented:
            assessment["findings"].append("No documented risk analysis — required by the Security Rule")

        assessment["recommended_steps"] = [
            "Complete a formal HIPAA risk analysis with documentation",
            "Execute BAAs with every business associate",
            "Implement missing safeguards, starting with encryption and access controls",
            "Train workforce and document training",
            "Establish breach notification procedures",
            "Engage healthcare compliance counsel",
        ]
        return assessment

    def generate_hipaa_checklist(self) -> List[str]:
        """Safeguard checklist grouped by HIPAA Security Rule categories."""
        checklist = []
        for group, items in self.safeguards.items():
            checklist.append(f"[{group.upper()}]")
            checklist.extend(f"  - {item}" for item in items)
        checklist.append("18 PHI identifier categories inventoried: " + ", ".join(self.phi_categories))
        return checklist


class CorporateGovernanceBot:
    """
    Corporate formation, governance, M&A.
    Rule-based entity comparison and formation checklists.
    """
    def __init__(self, legal_research):
        self.legal_research = legal_research
        self.name = "Corporate Governance Bot"
        self.entity_profiles = {
            "LLC": {"liability": "limited", "tax": "pass-through (default)",
                    "formality": "low", "investors": "members (VC-unfriendly)",
                    "best_for": ["small business", "real estate", "family business"]},
            "C-Corp": {"liability": "limited", "tax": "double taxation",
                       "formality": "high", "investors": "shares (VC-standard)",
                       "best_for": ["startups seeking VC", "going public", "employee stock options"]},
            "S-Corp": {"liability": "limited", "tax": "pass-through (restrictions)",
                       "formality": "medium", "investors": "100 US individuals max",
                       "best_for": ["profitable small business", "owner-operators"]},
            "Sole Proprietorship": {"liability": "unlimited", "tax": "personal",
                                    "formality": "none", "investors": "n/a",
                                    "best_for": ["testing an idea", "freelancers"]},
        }

    def recommend_entity(self, factors: Dict[str, any]) -> Dict[str, any]:
        """
        Score entity fit from caller-supplied factors.
        factors: {"seeking_vc": bool, "owners": int, "profitable": bool,
                  "wants_low_formality": bool, "non_us_owners": bool}
        """
        scores = {entity: 0 for entity in self.entity_profiles}
        if factors.get("seeking_vc"):
            scores["C-Corp"] += 3
        if factors.get("owners", 1) > 1:
            scores["LLC"] += 1
            scores["C-Corp"] += 1
        if factors.get("profitable") and not factors.get("seeking_vc"):
            scores["S-Corp"] += 2
            scores["LLC"] += 1
        if factors.get("wants_low_formality"):
            scores["LLC"] += 2
            scores["Sole Proprietorship"] += 1
        if factors.get("non_us_owners"):
            scores["S-Corp"] -= 3  # S-corp bars nonresident alien owners
            scores["C-Corp"] += 1
            scores["LLC"] += 1
        if factors.get("owners", 1) == 1 and not factors.get("seeking_vc"):
            scores["LLC"] += 1

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "ranked_entities": [
                {"entity": e, "score": s, "profile": self.entity_profiles[e]}
                for e, s in ranked
            ],
            "top_recommendation": ranked[0][0],
            "disclaimer": "Informational only — not legal or tax advice. Entity choice has "
                          "tax consequences; consult licensed attorney and CPA.",
        }

    def generate_formation_checklist(self, entity_type: str = "LLC") -> List[str]:
        """Deterministic formation checklist."""
        return [
            f"Choose and clear the {entity_type} name (state business registry search)",
            "Designate a registered agent with in-state address",
            f"File formation documents (Articles of Organization/Incorporation) with the state",
            "Obtain EIN from the IRS",
            "Draft governing document (Operating Agreement / Bylaws + shareholder agreement)",
            "Issue ownership interests and record in ledger",
            "Open business bank account",
            "File beneficial ownership reports as required",
            "Obtain business licenses and permits",
            "Set up accounting, tax calendar, and annual report reminders",
            "Consult attorney and CPA before operating",
        ]


class RealEstateAdvisorBot:
    """
    Real estate transactions and property law.
    Keyword-based risk flagging over caller-supplied transaction terms.
    """
    def __init__(self, torts_index):
        self.torts_index = torts_index
        self.name = "Real Estate Advisor Bot"
        self.risk_keywords = {
            "no inspection contingency": ("Missing inspection contingency", "HIGH"),
            "as-is": ("As-is sale — limited recourse for defects", "MEDIUM"),
            "no title insurance": ("No title insurance commitment", "HIGH"),
            "balloon payment": ("Balloon payment structure", "MEDIUM"),
            "adjustable rate": ("Adjustable/variable rate exposure", "MEDIUM"),
            "prepayment penalty": ("Prepayment penalty clause", "LOW"),
            "no financing contingency": ("No financing contingency — deposit at risk", "HIGH"),
            "hoa": ("HOA restrictions, dues, and special assessments", "MEDIUM"),
            "flood zone": ("Flood zone — insurance and disclosure issues", "MEDIUM"),
            "easement": ("Easement burdening the property", "LOW"),
            "lien": ("Existing lien on title", "HIGH"),
        }

    def assess_transaction_risk(self, transaction: Dict[str, any]) -> Dict[str, any]:
        """
        Flag risks from caller-supplied transaction text.
        transaction: {"description": str, "property_type": str, "price": number}
        """
        description = transaction.get("description", "").lower()
        flags = []
        for keyword, (label, severity) in self.risk_keywords.items():
            if keyword in description:
                flags.append({"trigger": keyword, "issue": label, "severity": severity})

        high = sum(1 for f in flags if f["severity"] == "HIGH")
        overall = "HIGH" if high >= 2 else ("MEDIUM" if flags else "LOW")
        return {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "property_type": transaction.get("property_type", "unknown"),
            "overall_risk": overall,
            "flags": flags,
            "recommended_steps": [
                "Obtain title commitment and title insurance",
                "Complete professional inspection within contingency period",
                "Review HOA docs, CC&Rs, and special assessments",
                "Verify zoning, permits, and floodplain status",
                "Have a licensed real estate attorney review the purchase agreement",
            ],
            "disclaimer": "Informational only — not legal advice. Real estate law is "
                          "state-specific; consult a licensed attorney.",
        }

    def generate_closing_checklist(self) -> List[str]:
        """Deterministic closing checklist."""
        return [
            "Executed purchase agreement with all addenda",
            "Earnest money deposited with escrow",
            "Title search completed; title commitment reviewed",
            "Inspection completed; repair addendum negotiated",
            "Appraisal completed (if financed)",
            "Loan commitment / proof of funds verified",
            "HOA/condo resale package reviewed",
            "Closing disclosure reviewed 3 days before closing",
            "Final walkthrough completed",
            "Funds wired to verified escrow account (verify wiring instructions by phone)",
            "Deed recorded; title policy issued",
        ]


class TechnologyCounselBot:
    """
    Technology transactions, licensing, SaaS.
    Keyword-based review of SaaS/license terms in the ContractReviewBot style.
    """
    def __init__(self, torts_index):
        self.torts_index = torts_index
        self.name = "Technology Counsel Bot"
        self.risk_keywords = {
            "perpetual license": ("Perpetual license grant — scope creep risk", "MEDIUM"),
            "irrevocable": ("Irrevocable rights grant", "MEDIUM"),
            "assign": ("Broad assignment of IP to vendor", "HIGH"),
            "own all data": ("Vendor claims ownership of customer data", "HIGH"),
            "no sla": ("No service-level commitments", "MEDIUM"),
            "no uptime": ("No uptime guarantee", "MEDIUM"),
            "unilateral modification": ("Vendor may change terms unilaterally", "HIGH"),
            "auto-renew": ("Automatic renewal without notice", "MEDIUM"),
            "no termination for convenience": ("No termination-for-convenience right", "MEDIUM"),
            "indemnify vendor": ("One-sided indemnification of vendor", "MEDIUM"),
            "limitation of liability": ("Check liability caps and carve-outs", "LOW"),
            "no audit right": ("No audit rights over vendor security/usage", "LOW"),
            "subprocessors": ("Subprocessor usage — review DPA obligations", "MEDIUM"),
            "data residency": ("Data residency / cross-border transfer terms", "MEDIUM"),
        }

    def review_saas_terms(self, terms: List[str]) -> Dict[str, any]:
        """Flag risky SaaS/license terms via keyword matching."""
        findings = []
        for term in terms:
            lowered = term.lower()
            for keyword, (label, severity) in self.risk_keywords.items():
                if keyword in lowered:
                    findings.append({
                        "term": term, "trigger": keyword,
                        "issue": label, "severity": severity,
                    })
        high = sum(1 for f in findings if f["severity"] == "HIGH")
        return {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "terms_reviewed": len(terms),
            "findings": findings,
            "overall_risk": "HIGH" if high >= 2 else ("MEDIUM" if findings else "LOW"),
            "recommended_steps": [
                "Negotiate data ownership and return/deletion on termination",
                "Require SLA with credits and uptime commitment",
                "Add mutual indemnification and balanced liability caps",
                "Require DPA covering subprocessors and breach notification",
                "Secure termination-for-convenience and renewal notice rights",
                "Have technology counsel review before signing",
            ],
            "disclaimer": "Informational only — not legal advice. Consult licensed technology counsel.",
        }

    def generate_licensing_checklist(self) -> List[str]:
        """Deterministic software licensing checklist."""
        return [
            "License scope defined (users, seats, territory, term)",
            "IP ownership and assignment terms reviewed",
            "Open-source components inventoried and license-compatible",
            "SLA / uptime / support tiers specified",
            "Data protection addendum (DPA) executed",
            "Security requirements and audit rights included",
            "Termination, wind-down, and data-return provisions",
            "Fee structure, renewal caps, and price protections",
            "Indemnification (IP infringement) and insurance",
            "Limitation of liability with appropriate carve-outs",
        ]


class RegulatoryNavigatorBot:
    """
    Regulatory compliance and government relations.
    Maps industry + activities to likely regulators via deterministic tables.
    """
    def __init__(self, legal_research):
        self.legal_research = legal_research
        self.name = "Regulatory Navigator Bot"
        self.industry_regulators = {
            "banking": ["OCC / FDIC / Federal Reserve (federal)", "State banking department",
                        "CFPB (consumer finance)", "FinCEN (BSA/AML)"],
            "healthcare": ["HHS / OCR (HIPAA)", "FDA (drugs/devices)", "CMS (Medicare/Medicaid)",
                           "State medical board"],
            "fintech": ["State money-transmitter licensing (state-by-state)", "FinCEN (MSB)",
                        "CFPB", "SEC (if securities involved)"],
            "telecom": ["FCC", "State PUC"],
            "energy": ["FERC", "State PUC", "EPA"],
            "food": ["FDA", "USDA", "State health department"],
            "transportation": ["DOT / FMCSA", "FAA (aviation)"],
            "education": ["Dept. of Education", "State education agency"],
            "ai": ["FTC (unfair/deceptive practices)", "NIST AI RMF (voluntary framework)",
                   "EU AI Act (if operating in EU)", "State AI laws (evolving)"],
            "crypto": ["SEC", "CFTC", "FinCEN", "State money-transmitter regimes"],
        }
        self.activity_triggers = {
            "consumer data": "State privacy laws (e.g., CCPA/CPRA) + FTC",
            "employees": "DOL, OSHA, EEOC, state labor agencies",
            "public company": "SEC reporting obligations",
            "government contracts": "FAR compliance, agency-specific rules",
            "environmental impact": "EPA, state environmental agencies",
            "import": "CBP, tariffs, trade compliance (BIS/OFAC)",
        }

    def identify_regulators(self, industry: str, activities: List[str]) -> Dict[str, any]:
        """Map industry and activities to likely regulators."""
        industry_key = industry.lower()
        regulators = list(self.industry_regulators.get(industry_key, []))
        activity_hits = []
        for activity in activities:
            for trigger, reg in self.activity_triggers.items():
                if trigger in activity.lower():
                    activity_hits.append({"activity": activity, "regulator": reg})
                    if reg not in regulators:
                        regulators.append(reg)
        if not regulators:
            regulators = ["Industry regulator not in table — research required"]
        return {
            "timestamp": datetime.now().isoformat(),
            "bot": self.name,
            "industry": industry,
            "likely_regulators": regulators,
            "activity_triggers": activity_hits,
            "recommended_steps": [
                "Confirm regulator list with licensed regulatory counsel",
                "Inventory required licenses, registrations, and filings",
                "Build a compliance calendar with renewal deadlines",
                "Designate a compliance owner and escalation path",
                "Monitor rulemaking in each regulator's docket",
            ],
            "disclaimer": "Informational only — not legal advice. Regulatory scope is "
                          "fact- and jurisdiction-specific.",
        }

    def generate_compliance_calendar(self) -> List[Dict[str, str]]:
        """Generic annual compliance calendar template."""
        return [
            {"period": "Q1", "task": "Annual reports / franchise tax filings (state)"},
            {"period": "Q1", "task": "Review and renew business licenses"},
            {"period": "Q2", "task": "Mid-year policy review (privacy, security, HR)"},
            {"period": "Q3", "task": "License renewal check; training refresh"},
            {"period": "Q4", "task": "Year-end compliance audit and calendar build for next year"},
            {"period": "Ongoing", "task": "Track regulator dockets for rule changes"},
        ]


# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MYTHARA LEGAL TEAM SUITE - DEMONSTRATION")
    print("=" * 60 + "\n")
    
    # Initialize suite
    legal_suite = MytharaLegalTeamSuite()
    
    print("\n" + "=" * 60)
    print("DEMO 1: TORTS ANALYSIS")
    print("=" * 60 + "\n")
    
    # Analyze tort scenario
    fact_pattern = {
        'intentional': True,
        'physical_contact': True,
        'emotional_distress': True,
        'employer_action': True
    }
    
    torts_analysis = legal_suite.torts_analyzer.analyze_fact_pattern(fact_pattern)
    print(f"Applicable Torts Found: {len(torts_analysis['applicable_torts'])}")
    for tort in torts_analysis['applicable_torts']:
        print(f"\n📋 {tort['tort_name']} ({tort['category']})")
        print(f"   Elements: {len(tort['elements'])}")
        print(f"   Statute of Limitations: {tort['statute_of_limitations']} years")
    
    print("\n" + "=" * 60)
    print("DEMO 2: CONTRACT REVIEW")
    print("=" * 60 + "\n")
    
    # Review contract
    contract_terms = [
        "Unlimited liability for any damages",
        "Automatic renewal without notice",
        "Unilateral modification rights reserved",
        "No termination right for customer"
    ]
    
    contract_review = legal_suite.contract_reviewer.review_contract_terms("SaaS", contract_terms)
    print(f"High Risk Terms Identified: {len(contract_review['high_risk_terms'])}")
    for risk_term in contract_review['high_risk_terms']:
        print(f"\n⚠️  {risk_term['risk'].upper()}")
        print(f"   Severity: {risk_term['severity']}")
        print(f"   Recommendation: {risk_term['recommendation']}")
    
    print("\n" + "=" * 60)
    print("DEMO 3: COMPLIANCE ASSESSMENT")
    print("=" * 60 + "\n")
    
    # Assess compliance
    compliance = legal_suite.compliance_monitor.assess_compliance(
        organization_type="SaaS",
        data_types=["PII", "financial"],
        jurisdictions=["US", "EU", "CA"]
    )
    
    print(f"Risk Level: {compliance['risk_level']}")
    print(f"\nApplicable Frameworks: {len(compliance['applicable_frameworks'])}")
    for framework in compliance['applicable_frameworks']:
        print(f"\n🔐 {framework['framework']}")
        print(f"   Requirements: {len(framework['requirements'])}")
        for req in framework['requirements'][:2]:
            print(f"   - {req}")
    
    print("\n" + "=" * 60)
    print("DEMO 4: IP PROTECTION")
    print("=" * 60 + "\n")
    
    # IP assessment
    ip_risk = legal_suite.ip_guardian.assess_infringement_risk(
        ip_type="trademark",
        use_case="New SaaS product brand name"
    )
    
    print("Clearance Steps:")
    for step in ip_risk['clearance_steps']:
        print(f"  ✓ {step}")
    
    print("\n" + "=" * 60)
    print("DEMO 5: EMPLOYMENT RISK")
    print("=" * 60 + "\n")
    
    # Termination risk
    employee = {
        "tenure_years": 7,
        "protected_class": True,
        "recent_complaint": True
    }
    
    termination_risk = legal_suite.employment_counsel.assess_termination_risk(
        employee_info=employee,
        termination_reason="Performance issues"
    )
    
    print(f"Overall Risk: {termination_risk['overall_risk']}")
    print(f"\nRisk Factors:")
    for factor in termination_risk['risk_factors']:
        print(f"  ⚠️  {factor}")
    
    print("\n" + "=" * 60)
    print("⚖️  DISCLAIMER: NOT LEGAL ADVICE")
    print("=" * 60)
    print("This suite provides informational guidance only.")
    print("Consult licensed attorney for specific legal matters.")
    print("=" * 60 + "\n")
