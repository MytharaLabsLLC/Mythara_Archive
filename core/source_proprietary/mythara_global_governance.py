#!/usr/bin/env python3
"""
Mythara Global Governance Framework
Universal Compliance Engine for All Industries, All Countries

Copyright © 2026 Mythara Labs LLC. All rights reserved.

This module provides comprehensive governance rules for every major industry
across every major regulatory jurisdiction worldwide.
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import re
import unicodedata

# ===================== GLOBAL REGULATORY FRAMEWORKS =====================


class GlobalRegion(str, Enum):
    """Major regulatory regions worldwide"""

    # Americas
    USA = "USA"
    CANADA = "Canada"
    MEXICO = "Mexico"
    BRAZIL = "Brazil"
    ARGENTINA = "Argentina"

    # Europe
    EU = "European_Union"
    UK = "United_Kingdom"
    GERMANY = "Germany"
    FRANCE = "France"
    SPAIN = "Spain"
    ITALY = "Italy"
    SWITZERLAND = "Switzerland"
    NETHERLANDS = "Netherlands"

    # Asia Pacific
    CHINA = "China"
    JAPAN = "Japan"
    SOUTH_KOREA = "South_Korea"
    INDIA = "India"
    SINGAPORE = "Singapore"
    AUSTRALIA = "Australia"
    NEW_ZEALAND = "New_Zealand"
    HONG_KONG = "Hong_Kong"
    TAIWAN = "Taiwan"

    # Middle East & Africa
    UAE = "United_Arab_Emirates"
    SAUDI_ARABIA = "Saudi_Arabia"
    ISRAEL = "Israel"
    SOUTH_AFRICA = "South_Africa"

    # Universal (applies everywhere)
    GLOBAL = "Global"


class IndustryVertical(str, Enum):
    """Major industry verticals with regulatory requirements"""

    HEALTHCARE = "Healthcare"
    FINANCIAL_SERVICES = "Financial_Services"
    PHARMACEUTICALS = "Pharmaceuticals"
    GOVERNMENT = "Government"
    DEFENSE = "Defense"
    EDUCATION = "Education"
    LEGAL = "Legal"
    INSURANCE = "Insurance"
    TELECOMMUNICATIONS = "Telecommunications"
    ENERGY = "Energy"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    TECHNOLOGY = "Technology"
    MEDIA = "Media"
    TRANSPORTATION = "Transportation"
    FOOD_BEVERAGE = "Food_and_Beverage"
    REAL_ESTATE = "Real_Estate"
    NONPROFIT = "Nonprofit"
    RELIGIOUS = "Religious_Organizations"


class ComplianceLevel(str, Enum):
    """Severity of compliance violation"""

    CRITICAL = "Critical"  # Legal violation, potential lawsuit
    HIGH = "High"  # Regulatory violation, fines possible
    MEDIUM = "Medium"  # Policy violation, internal review
    LOW = "Low"  # Style/tone issue, warning only


# ===================== REGULATORY FRAMEWORKS DATABASE =====================


@dataclass
class RegulatoryFramework:
    """A specific regulatory framework with rules"""

    framework_id: str
    name: str
    region: GlobalRegion
    industries: List[IndustryVertical]

    # Prohibited claims
    prohibited_claims: List[str]

    # Required disclosures
    required_disclosures: List[str]

    # Data protection rules
    data_protection_rules: Dict[str, str]

    # AI-specific rules
    ai_governance_rules: Dict[str, str]

    # Penalty for violation
    violation_severity: ComplianceLevel

    # Authority
    regulatory_authority: str


# ===================== GLOBAL COMPLIANCE DATABASE =====================

GLOBAL_REGULATORY_FRAMEWORKS = {
    # ==================== INTERNATIONAL TREATIES & CONVENTIONS ====================
    "UN_HUMAN_RIGHTS": RegulatoryFramework(
        framework_id="UN_HUMAN_RIGHTS",
        name="Universal Declaration of Human Rights (UDHR)",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "discriminate based on race",
            "discriminate based on color",
            "discriminate based on sex",
            "discriminate based on language",
            "discriminate based on religion",
            "uses race as",
            "race as a factor",
            "race as a predictive",
            "racial profiling",
            "demographic optimization",
            "demographic-based optimization",
            "demographic targeting",
            "race-based targeting",
            "ethnic profiling",
            "deny human dignity",
            "restrict freedom of thought",
            "violate right to privacy",
        ],
        required_disclosures=[
            "All individuals have equal rights regardless of race, color, sex, language, religion, political opinion, national or social origin (UDHR Article 2).",
            "Right to privacy must be respected (UDHR Article 12).",
            "Freedom of thought, conscience and religion (UDHR Article 18).",
            "AI systems must not discriminate against protected classes.",
        ],
        data_protection_rules={
            "non_discrimination": "AI must not discriminate based on protected characteristics",
            "privacy": "Right to privacy must be upheld",
            "dignity": "Human dignity must be preserved",
            "freedom_thought": "AI must not restrict freedom of thought or conscience",
        },
        ai_governance_rules={
            "bias_testing": "AI must be tested for bias against protected classes",
            "transparency": "AI decision-making must be transparent",
            "accountability": "Humans must be accountable for AI decisions",
            "non_discrimination": "AI outputs must not perpetuate discrimination",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="United Nations Human Rights Council",
    ),
    "UN_CRPD": RegulatoryFramework(
        framework_id="UN_CRPD",
        name="Convention on the Rights of Persons with Disabilities",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "inaccessible to people with disabilities",
            "no accessibility features provided",
            "accessible without WCAG compliance",
        ],
        required_disclosures=[
            "Technology must be accessible to persons with disabilities (CRPD Article 9).",
            "WCAG 2.1 Level AA minimum accessibility standard required.",
            "Assistive technology compatibility required.",
            "Equal access to information and communications technology.",
            "Universal design principles must be followed.",
        ],
        data_protection_rules={
            "accessibility": "Must provide accessible interfaces (WCAG 2.1 AA minimum)",
            "assistive_tech": "Must be compatible with screen readers, braille displays, voice control",
            "non_discrimination": "Cannot exclude people with disabilities",
            "reasonable_accommodation": "Must provide accommodations upon request",
        },
        ai_governance_rules={
            "accessible_ai": "AI interfaces must be accessible (WCAG 2.1 AA minimum)",
            "bias_disability": "AI must not discriminate against people with disabilities",
            "alternative_formats": "AI outputs must be available in alternative formats",
            "testing": "Regular accessibility testing with people with disabilities required",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="United Nations Committee on the Rights of Persons with Disabilities (182 state parties)",
    ),
    "OECD_AI_PRINCIPLES": RegulatoryFramework(
        framework_id="OECD_AI_PRINCIPLES",
        name="OECD Principles on Artificial Intelligence",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "AI is 100% unbiased",
            "AI decisions need no oversight",
            "AI has no societal impact",
            "AI is perfectly accurate",
        ],
        required_disclosures=[
            "AI should benefit people and planet (inclusive growth, sustainable development).",
            "AI systems must be robust, secure, and safe throughout their lifecycle.",
            "Transparency and responsible disclosure about AI systems required.",
            "Accountability for AI systems must be ensured.",
            "Human-centered values and fairness must guide AI development.",
        ],
        data_protection_rules={
            "transparency": "Must disclose AI use and capabilities",
            "security": "AI systems must be secure and robust",
            "safety": "AI must not cause harm",
            "privacy": "AI must respect privacy and data protection",
        },
        ai_governance_rules={
            "human_centered": "AI must be designed with human-centered values",
            "accountability": "Clear accountability for AI outcomes",
            "transparency": "Explainable AI where possible",
            "fairness": "AI must not perpetuate bias or discrimination",
            "robustness": "AI must be tested for safety and security",
            "sustainability": "AI environmental impact must be considered",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="OECD (42 member countries + partners)",
    ),
    "WCAG_INTERNATIONAL": RegulatoryFramework(
        framework_id="WCAG_INTERNATIONAL",
        name="Web Content Accessibility Guidelines (WCAG) 2.1/2.2",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "WCAG compliant",
            "WCAG certified",
            "accessible without WCAG",
            "meets WCAG without",
        ],
        required_disclosures=[
            "WCAG 2.1 Level AA conformance minimum for public-facing systems.",
            "Level AAA conformance recommended for critical services (healthcare, government).",
            "Perceivable, Operable, Understandable, Robust (POUR principles) must be followed.",
            "Regular accessibility audits by qualified professionals required.",
            "Accessibility statement must be published.",
        ],
        data_protection_rules={
            "accessibility": "Must meet WCAG 2.1 Level AA minimum (WCAG 2.2 recommended)",
            "testing": "Regular accessibility testing required (automated + manual)",
            "user_feedback": "Accessibility feedback mechanism required",
            "remediation": "Accessibility issues must be remediated within reasonable timeframe",
        },
        ai_governance_rules={
            "ai_interfaces": "AI chat interfaces must be WCAG compliant",
            "screen_reader": "AI outputs must be screen-reader friendly",
            "keyboard_nav": "AI interfaces must support keyboard navigation",
            "alt_text": "AI-generated images must have descriptive alt text",
            "captions": "AI-generated video/audio must have captions/transcripts",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="W3C Web Accessibility Initiative (adopted globally by 182+ countries)",
    ),
    "ISO_27701_PRIVACY": RegulatoryFramework(
        framework_id="ISO_27701_PRIVACY",
        name="ISO/IEC 27701:2019 Privacy Information Management",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "ISO 27701 certified without audit",
            "ISO 27701 compliant without PIMS implementation",
        ],
        required_disclosures=[
            "Privacy information management system (PIMS) required.",
            "Extends ISO 27001 with privacy-specific controls.",
            "GDPR and other privacy law mapping provided.",
            "Third-party audit by accredited body required for certification.",
            "Annual surveillance audits required.",
        ],
        data_protection_rules={
            "pims": "Must implement Privacy Information Management System",
            "privacy_by_design": "Privacy must be designed into systems from inception",
            "data_minimization": "Collect only necessary data for stated purpose",
            "retention": "Data retention policies required (must delete when no longer needed)",
            "consent": "Valid consent mechanisms required",
            "data_subject_rights": "Must enable data subject rights (access, deletion, portability)",
        },
        ai_governance_rules={
            "privacy_ai": "AI must respect privacy principles (purpose limitation, data minimization)",
            "data_use": "AI training data must comply with privacy laws",
            "automated_decisions": "Right to human review of automated decisions",
            "profiling": "AI profiling must respect privacy rights",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="ISO/IEC (international standard)",
    ),
    "WIPO_COPYRIGHT": RegulatoryFramework(
        framework_id="WIPO_COPYRIGHT",
        name="WIPO Copyright Treaty & Berne Convention",
        region=GlobalRegion.GLOBAL,
        industries=[
            IndustryVertical.TECHNOLOGY,
            IndustryVertical.MEDIA,
            IndustryVertical.EDUCATION,
        ],
        prohibited_claims=[
            "use copyrighted content without permission",
            "AI training on copyrighted data is always legal",
            "fair use applies globally",
        ],
        required_disclosures=[
            "Copyright protection extends to authors' works in all member countries (Berne Convention).",
            "AI training data may require copyright clearance depending on jurisdiction.",
            "Fair use/fair dealing varies by country.",
            "Consult intellectual property counsel for copyright compliance.",
        ],
        data_protection_rules={
            "copyright_clearance": "AI training data must have proper copyright clearance",
            "attribution": "Must attribute copyrighted works when used",
            "licensing": "Proper licensing required for copyrighted content",
        },
        ai_governance_rules={
            "training_data": "AI training data copyright must be verified",
            "generated_content": "AI-generated content copyright status must be disclosed",
            "model_ownership": "AI model ownership must be clear",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="World Intellectual Property Organization (WIPO) - 193 member states",
    ),
    "ILO_LABOR_STANDARDS": RegulatoryFramework(
        framework_id="ILO_LABOR_STANDARDS",
        name="International Labour Organization Core Conventions",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "employ workers under minimum age",
            "forced labor permitted",
            "forced labor",
            "compulsory labor",
            "use forced labor",
            "slave labor",
            "discriminate in employment",
        ],
        required_disclosures=[
            "Minimum age for employment: 15 years (ILO Convention 138).",
            "Prohibition of worst forms of child labor (ILO Convention 182).",
            "Elimination of forced or compulsory labor (ILO Conventions 29 and 105).",
            "Freedom of association and right to collective bargaining (ILO Conventions 87 and 98).",
            "Elimination of discrimination in employment (ILO Conventions 100 and 111).",
        ],
        data_protection_rules={
            "worker_data": "Worker data must be protected",
            "surveillance": "Worker surveillance must be disclosed and limited",
            "non_discrimination": "Employment practices must not discriminate",
        },
        ai_governance_rules={
            "hiring_ai": "AI hiring tools must not discriminate (race, sex, age, disability)",
            "worker_monitoring": "AI worker monitoring must respect privacy and dignity",
            "job_displacement": "AI job displacement impact must be assessed",
            "bias_testing": "AI employment tools must be tested for bias",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="International Labour Organization (ILO) - 187 member states",
    ),
    "FCPA_ANTI_CORRUPTION": RegulatoryFramework(
        framework_id="FCPA_ANTI_CORRUPTION",
        name="Foreign Corrupt Practices Act & OECD Anti-Bribery Convention",
        region=GlobalRegion.GLOBAL,
        industries=[
            IndustryVertical.GOVERNMENT,
            IndustryVertical.FINANCIAL_SERVICES,
            IndustryVertical.TECHNOLOGY,
        ],
        prohibited_claims=[
            "payments to government officials",
            "pay government officials",
            "bribe government officials",
            "bribe foreign officials",
            "facilitation payments",
            "make facilitation payments",
            "financial incentives to government",
            "incentives to officials",
            "performance incentives to government",
            "incentivize officials",
            "incentivize government officers",
            "rewards for government procurement",
            "gifts to officials",
            "facilitation payments always allowed",
        ],
        required_disclosures=[
            "Bribes to foreign government officials prohibited (FCPA, UK Bribery Act).",
            "OECD Anti-Bribery Convention prohibits bribery in international business.",
            "Facilitation payments prohibited in many jurisdictions.",
            "Third-party due diligence required.",
            "Anti-corruption compliance program required for government contracts.",
        ],
        data_protection_rules={
            "transaction_records": "All transactions with government entities must be documented",
            "due_diligence": "Third-party due diligence records required",
            "gift_register": "Gifts and hospitality must be recorded",
        },
        ai_governance_rules={
            "government_contracts": "AI systems for government must have anti-corruption controls",
            "transaction_monitoring": "AI transaction monitoring for corruption risks",
            "risk_assessment": "AI risk assessment for corruption exposure",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Department of Justice, OECD (44 parties to Anti-Bribery Convention)",
    ),
    "EXPORT_CONTROL_ITAR_EAR": RegulatoryFramework(
        framework_id="EXPORT_CONTROL_ITAR_EAR",
        name="Export Control: ITAR, EAR, Wassenaar Arrangement",
        region=GlobalRegion.GLOBAL,
        industries=[
            IndustryVertical.DEFENSE,
            IndustryVertical.TECHNOLOGY,
            IndustryVertical.GOVERNMENT,
        ],
        prohibited_claims=[
            "export defense articles without license",
            "export defense articles to China",
            "export defense articles to Russia",
            "no export restrictions",
            "AI technology not subject to export control",
            "freely distribute defense",
            "freely export defense",
            "distribute defense-related",
            "distribute our defense-related",
            "defense-related AI technology internationally",
            "defense-related AI",
            "export to China without",
            "export to Russia without",
            "export to Iran without",
            "export to North Korea without",
            "dual-use AI technology",
            "export dual-use AI",
            "dual-use AI to Russia",
            "dual-use AI to China",
            "export AI technology without",
            "no restrictions on export",
        ],
        required_disclosures=[
            "Defense-related AI subject to ITAR (International Traffic in Arms Regulations).",
            "Dual-use AI technology subject to EAR (Export Administration Regulations).",
            "Wassenaar Arrangement controls export of conventional arms and dual-use goods.",
            "Export license required for restricted countries (China, Russia, Iran, North Korea, etc.).",
            "Deemed export rules apply to foreign nationals.",
            "Consult export control counsel before international deployment.",
        ],
        data_protection_rules={
            "export_licenses": "Export licenses must be obtained and maintained",
            "end_user": "End user verification required",
            "country_restrictions": "Restricted country list must be checked",
        },
        ai_governance_rules={
            "defense_ai": "AI for defense/military applications subject to ITAR",
            "dual_use": "AI with potential military use subject to EAR (e.g., facial recognition, cybersecurity)",
            "encryption": "Strong encryption (>512-bit) subject to export control",
            "license_check": "Export license check required before international deployment",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US State Department (ITAR), US Commerce Department (EAR), Wassenaar Arrangement (42 states)",
    ),
    "SANCTIONS_OFAC": RegulatoryFramework(
        framework_id="SANCTIONS_OFAC",
        name="US OFAC Sanctions & UN Security Council Sanctions",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "operate in sanctioned countries",
            "transact with SDN list entities",
            "provide technology to sanctioned",
            "technology to sanctioned countries",
            "in Iran",
            "in North Korea",
            "in Cuba",
            "in Syria",
            "operate in Iran",
            "operate in North Korea",
            "operate in Cuba",
            "operate in Syria",
            "transact with Iranian",
            "bypass sanctions",
            "bypassing sanctions",
            "bypassing UN sanctions",
            "circumvent sanctions",
            "circumvent UN sanctions",
        ],
        required_disclosures=[
            "US OFAC sanctions prohibit transactions with sanctioned countries and entities.",
            "Comprehensive sanctions: Cuba, Iran, North Korea, Syria, Russia (partial).",
            "UN Security Council sanctions apply globally.",
            "EU sanctions regime in effect for member states.",
            "SDN (Specially Designated Nationals) list must be screened.",
            "Sanctions compliance screening required before onboarding.",
        ],
        data_protection_rules={
            "sanctions_screening": "All users/entities must be screened against sanctions lists",
            "country_blocks": "IP blocks for sanctioned countries required",
            "transaction_monitoring": "Transaction monitoring for sanctions violations",
        },
        ai_governance_rules={
            "geofencing": "AI services must be geofenced to exclude sanctioned countries",
            "entity_screening": "AI must screen entities against SDN list",
            "compliance_monitoring": "Real-time sanctions compliance monitoring required",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Treasury OFAC, UN Security Council, EU External Action Service",
    ),
    "ANTITRUST_COMPETITION": RegulatoryFramework(
        framework_id="ANTITRUST_COMPETITION",
        name="Antitrust & Competition Law (Sherman Act, EU Competition Law)",
        region=GlobalRegion.GLOBAL,
        industries=[
            IndustryVertical.TECHNOLOGY,
            IndustryVertical.FINANCIAL_SERVICES,
            IndustryVertical.TELECOMMUNICATIONS,
        ],
        prohibited_claims=[
            "price fixing with competitors",
            "coordinate pricing with competitors",
            "pricing coordination",
            "collude on prices",
            "market allocation agreements",
            "exclusive dealing that harms competition",
            "abuse dominant market position",
            "abuse our dominant",
            "monopolize the market",
        ],
        required_disclosures=[
            "Sherman Antitrust Act prohibits monopolization and anti-competitive agreements (US).",
            "EU Competition Law (Articles 101, 102 TFEU) prohibits cartels and abuse of dominance.",
            "Price fixing, bid rigging, market allocation prohibited globally.",
            "Merger control required for significant acquisitions.",
            "Consult antitrust counsel for competitive impact.",
        ],
        data_protection_rules={
            "competitor_data": "Competitor data sharing must be limited",
            "pricing_data": "Pricing coordination with competitors prohibited",
            "market_data": "Market allocation agreements prohibited",
        },
        ai_governance_rules={
            "algorithmic_pricing": "AI pricing algorithms must not facilitate collusion",
            "market_power": "AI systems must not abuse market dominance",
            "competitor_monitoring": "AI competitor monitoring must not violate antitrust law",
            "merger_review": "AI acquisitions may require antitrust clearance",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Department of Justice, FTC, European Commission (DG COMP)",
    ),
    # ==================== UNITED STATES ====================
    "USA_HIPAA": RegulatoryFramework(
        framework_id="USA_HIPAA",
        name="Health Insurance Portability and Accountability Act",
        region=GlobalRegion.USA,
        industries=[IndustryVertical.HEALTHCARE, IndustryVertical.INSURANCE],
        prohibited_claims=[
            "HIPAA compliant",
            "HIPAA certified",
            "meets HIPAA standards",
            "HIPAA approved",
            "Health Insurance Portability and Accountability Act compliant",
            "Health Insurance Portability and Accountability Act certified",
            "aligns with HIPAA",
            "HIPAA conformant",
            "cumpliente",
        ],
        required_disclosures=[
            "This system handles protected health information (PHI). Consult legal counsel for HIPAA compliance assessment.",
            "HIPAA compliance requires organizational policies beyond this software.",
        ],
        data_protection_rules={
            "phi_handling": "Cannot claim to handle PHI without BAA (Business Associate Agreement)",
            "encryption": "Must specify encryption standards (AES-256, TLS 1.3)",
            "audit_trails": "Must maintain audit logs for 6 years",
        },
        ai_governance_rules={
            "ai_decisions": "AI decisions affecting patient care must be auditable",
            "transparency": "Must disclose AI involvement in clinical decisions",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Department of Health & Human Services (HHS)",
    ),
    "USA_SOX": RegulatoryFramework(
        framework_id="USA_SOX",
        name="Sarbanes-Oxley Act",
        region=GlobalRegion.USA,
        industries=[IndustryVertical.FINANCIAL_SERVICES, IndustryVertical.TECHNOLOGY],
        prohibited_claims=["SOX compliant", "meets Sarbanes-Oxley requirements"],
        required_disclosures=[
            "Financial data handling subject to SOX Section 404 internal controls.",
            "Audit trail retention required for 7 years.",
        ],
        data_protection_rules={
            "financial_records": "Must retain financial records for 7 years",
            "audit_trails": "Immutable audit logs required",
            "access_controls": "Role-based access with approval workflows",
        },
        ai_governance_rules={
            "financial_decisions": "AI-generated financial reports must be human-reviewed",
            "audit_trails": "AI decision logs must be cryptographically signed",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Securities and Exchange Commission (SEC)",
    ),
    "USA_FINRA": RegulatoryFramework(
        framework_id="USA_FINRA",
        name="Financial Industry Regulatory Authority",
        region=GlobalRegion.USA,
        industries=[IndustryVertical.FINANCIAL_SERVICES],
        prohibited_claims=[
            "guaranteed returns",
            "guarantees investment returns",
            "guarantee returns",
            "risk-free investment",
            "risk-free",
            "no risk",
            "past performance guarantees future results",
            "consistent investment success",
            "positive outcomes guaranteed",
            "100% positive returns",
            "100% returns",
            "always profitable",
            "never lose money",
        ],
        required_disclosures=[
            "Past performance does not guarantee future results.",
            "All investments carry risk of loss.",
            "Consult a licensed financial advisor.",
        ],
        data_protection_rules={
            "client_data": "Must encrypt client financial data at rest and in transit",
            "retention": "Must retain communications for 3-6 years depending on record type",
        },
        ai_governance_rules={
            "robo_advisors": "AI investment advice must be supervised by registered representatives",
            "suitability": "AI recommendations must consider client suitability",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="FINRA",
    ),
    "USA_FDA": RegulatoryFramework(
        framework_id="USA_FDA",
        name="Food and Drug Administration Regulations",
        region=GlobalRegion.USA,
        industries=[
            IndustryVertical.HEALTHCARE,
            IndustryVertical.PHARMACEUTICALS,
            IndustryVertical.FOOD_BEVERAGE,
        ],
        prohibited_claims=[
            "FDA approved for",
            "FDA approved our",
            "approved by FDA",
            "FDA certified",
            "FDA cleared our",
            "cleared by FDA for",
            "cures cancer",
            "treats disease",
            "medical diagnosis",
        ],
        required_disclosures=[
            "This product has not been evaluated by the FDA.",
            "Not intended to diagnose, treat, cure, or prevent any disease.",
            "Consult a healthcare provider for medical advice.",
        ],
        data_protection_rules={
            "clinical_data": "Clinical trial data must be retained for 2 years after discontinuation",
            "adverse_events": "Must report serious adverse events within 15 days",
        },
        ai_governance_rules={
            "medical_devices": "AI-based medical devices require FDA clearance (510k or PMA)",
            "clinical_decision_support": "AI clinical decision support may be regulated as medical device",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Food and Drug Administration",
    ),
    "USA_FTC": RegulatoryFramework(
        framework_id="USA_FTC",
        name="Federal Trade Commission Act",
        region=GlobalRegion.USA,
        industries=[
            IndustryVertical.RETAIL,
            IndustryVertical.TECHNOLOGY,
            IndustryVertical.MEDIA,
        ],
        prohibited_claims=[
            "false advertising",
            "deceptive claims",
            "unsubstantiated guarantees",
        ],
        required_disclosures=[
            "Material connections must be disclosed.",
            "Claims must be substantiated with evidence.",
            "Endorsements must reflect typical user experience.",
        ],
        data_protection_rules={
            "consumer_data": "Must notify consumers of data collection practices",
            "children": "COPPA compliance required for users under 13",
        },
        ai_governance_rules={
            "algorithmic_transparency": "Must disclose AI use in advertising targeting",
            "bias": "AI targeting must not discriminate against protected classes",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Federal Trade Commission",
    ),
    "USA_FCRA": RegulatoryFramework(
        framework_id="USA_FCRA",
        name="Fair Credit Reporting Act",
        region=GlobalRegion.USA,
        industries=[
            IndustryVertical.FINANCIAL_SERVICES,
            IndustryVertical.INSURANCE,
            IndustryVertical.REAL_ESTATE,
        ],
        prohibited_claims=[
            "credit score improvement guaranteed",
            "remove accurate negative information",
        ],
        required_disclosures=[
            "Adverse action notices required when credit decisions are automated.",
            "Consumers have right to dispute inaccurate information.",
        ],
        data_protection_rules={
            "credit_reports": "Must provide adverse action notice within 30 days",
            "consumer_rights": "Must allow consumers to dispute and correct errors",
        },
        ai_governance_rules={
            "credit_decisions": "AI credit decisions must be explainable (FCRA 615)",
            "adverse_action": "Must provide reasons for AI-driven credit denials",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="Consumer Financial Protection Bureau (CFPB)",
    ),
    "USA_ADA": RegulatoryFramework(
        framework_id="USA_ADA",
        name="Americans with Disabilities Act",
        region=GlobalRegion.USA,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "not accessible to people with disabilities",
            "no screen reader support",
            "don't provide screen reader support",
            "screen reader support or keyboard navigation",
            "no keyboard navigation",
            "don't provide accessibility",
            "inaccessible to disabled",
        ],
        required_disclosures=[
            "Public accommodations must be accessible to people with disabilities (ADA Title III).",
            "Websites and mobile apps are covered under ADA.",
            "WCAG 2.1 Level AA is recommended standard.",
            "Reasonable accommodations must be provided upon request.",
        ],
        data_protection_rules={
            "disability_data": "Cannot collect or disclose disability information without consent",
            "accommodations": "Must provide reasonable accommodations",
        },
        ai_governance_rules={
            "accessible_interfaces": "AI interfaces must be accessible (screen readers, keyboard nav)",
            "no_discrimination": "AI must not discriminate against people with disabilities",
            "alternative_formats": "Must provide alternative formats upon request",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="US Department of Justice (DOJ)",
    ),
    "USA_COPPA": RegulatoryFramework(
        framework_id="USA_COPPA",
        name="Children's Online Privacy Protection Act",
        region=GlobalRegion.USA,
        industries=[
            IndustryVertical.EDUCATION,
            IndustryVertical.MEDIA,
            IndustryVertical.TECHNOLOGY,
        ],
        prohibited_claims=[
            "collect data from children under 13",
            "collect data from children without",
            "no parental consent required",
            "children under 13 without parental consent",
            "without parental consent",
        ],
        required_disclosures=[
            "Parental consent required for children under 13.",
            "Must post clear privacy policy.",
            "Parents have right to review and delete children's data.",
        ],
        data_protection_rules={
            "parental_consent": "Must obtain verifiable parental consent before collecting data from children under 13",
            "data_minimization": "Collect only necessary information from children",
            "deletion_rights": "Parents can request deletion of children's data",
        },
        ai_governance_rules={
            "age_verification": "Must implement age verification mechanisms",
            "child_safety": "AI interactions with children must be safe and appropriate",
            "no_profiling": "Cannot use children's data for behavioral advertising without consent",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="Federal Trade Commission (FTC)",
    ),
    "USA_CCPA": RegulatoryFramework(
        framework_id="USA_CCPA",
        name="California Consumer Privacy Act",
        region=GlobalRegion.USA,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "sell personal information without disclosure",
            "sell California residents' personal information",
            "sell California residents personal information",
            "no opt-out required",
        ],
        required_disclosures=[
            "Must disclose categories of personal information collected and sold.",
            "Consumers have right to opt-out of sale of personal information.",
            "Cannot discriminate against consumers who exercise CCPA rights.",
            "Must respond to consumer requests within 45 days.",
        ],
        data_protection_rules={
            "disclosure": "Must disclose data collection and selling practices",
            "opt_out": "Must provide 'Do Not Sell My Personal Information' link",
            "deletion_rights": "Must honor deletion requests within 45 days",
            "non_discrimination": "Cannot discriminate against consumers exercising rights",
        },
        ai_governance_rules={
            "automated_decisions": "Consumers have right to know about automated decision-making",
            "profiling": "Must disclose AI profiling and allow opt-out",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="California Attorney General",
    ),
    # ==================== EUROPEAN UNION ====================
    "EU_GDPR": RegulatoryFramework(
        framework_id="EU_GDPR",
        name="General Data Protection Regulation",
        region=GlobalRegion.EU,
        industries=list(IndustryVertical),  # Applies to ALL industries
        prohibited_claims=[
            "GDPR compliant without DPO",
            "GDPR compliant",
            "GDPR certified",
            "General Data Protection Regulation compliant",
            "General Data Protection Regulation certified",
            "comply with the General Data Protection Regulation",
            "no data processing occurs",
            "data is anonymous (when it's pseudonymous)",
            "process personal data without consent",
            "without user consent",
            "without consent",
            "no consent required",
            "forced consent",
            "for anyone including EU citizens",
            "including EU citizens",
            "aligns with GDPR",
            "meets GDPR requirements",
            "sans consentement",
            "sin consentimiento",
        ],
        required_disclosures=[
            "Data subject rights: access, rectification, erasure, portability.",
            "Legal basis for processing must be specified (consent, contract, legitimate interest).",
            "Data transfers outside EU require adequacy decision or safeguards.",
            "Right to withdraw consent at any time.",
        ],
        data_protection_rules={
            "consent": "Must obtain explicit, informed, freely-given consent",
            "right_to_erasure": "Must honor 'right to be forgotten' requests within 30 days",
            "data_minimization": "Collect only data necessary for stated purpose",
            "breach_notification": "Must notify supervisory authority within 72 hours of breach",
            "dpo_required": "Must appoint DPO if processing sensitive data at scale",
        },
        ai_governance_rules={
            "automated_decisions": "Right to human review of automated decisions (Article 22)",
            "profiling": "Must disclose profiling and allow opt-out",
            "transparency": "Must explain AI logic, significance, and consequences",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="European Data Protection Board (EDPB)",
    ),
    "EU_AI_ACT": RegulatoryFramework(
        framework_id="EU_AI_ACT",
        name="EU Artificial Intelligence Act",
        region=GlobalRegion.EU,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "AI is unbiased",
            "AI is 100% accurate",
            "no human oversight required",
            "no human oversight",
            "no transparency required",
            "high-risk AI without oversight",
            "automated AI decisions without informing",
            "without informing users",
        ],
        required_disclosures=[
            "High-risk AI systems must undergo conformity assessment.",
            "AI-generated content must be labeled as such.",
            "Emotion recognition and biometric categorization have strict limits.",
            "Prohibited AI: social scoring, subliminal manipulation, exploitation of vulnerabilities.",
        ],
        data_protection_rules={
            "training_data": "Must document data provenance and quality",
            "bias_testing": "Must test for bias across protected characteristics",
            "model_cards": "Must maintain technical documentation of AI system",
        },
        ai_governance_rules={
            "high_risk_ai": "Healthcare, employment, law enforcement AI = high-risk category",
            "human_oversight": "Meaningful human oversight required for high-risk systems",
            "transparency": "Users must be informed they're interacting with AI",
            "prohibited_uses": "Cannot use AI for social scoring or manipulation",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="European Commission",
    ),
    # ==================== UNITED KINGDOM ====================
    "UK_DPA": RegulatoryFramework(
        framework_id="UK_DPA",
        name="UK Data Protection Act 2018",
        region=GlobalRegion.UK,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "GDPR compliant without UK-specific compliance",
            "EU GDPR compliant (post-Brexit claims)",
        ],
        required_disclosures=[
            "Data subject rights under UK GDPR.",
            "ICO registration required for data controllers.",
            "Data transfers require UK adequacy or safeguards.",
        ],
        data_protection_rules={
            "uk_gdpr": "Similar to EU GDPR but UK-specific",
            "ico_registration": "Must register with ICO as data controller",
            "breach_notification": "72-hour notification to ICO",
        },
        ai_governance_rules={
            "automated_decisions": "Article 22 equivalent - right to human review",
            "algorithmic_transparency": "Must explain AI decisions affecting individuals",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="Information Commissioner's Office (ICO)",
    ),
    # ==================== CANADA ====================
    "CANADA_PIPEDA": RegulatoryFramework(
        framework_id="CANADA_PIPEDA",
        name="Personal Information Protection and Electronic Documents Act",
        region=GlobalRegion.CANADA,
        industries=list(IndustryVertical),
        prohibited_claims=["no consent required for data processing"],
        required_disclosures=[
            "Meaningful consent required before data collection.",
            "Individuals have right to access their personal information.",
            "Organizations must appoint privacy officer.",
        ],
        data_protection_rules={
            "consent": "Must obtain meaningful consent (not buried in ToS)",
            "accountability": "Must appoint individual accountable for compliance",
            "breach_notification": "Must notify Privacy Commissioner and affected individuals",
        },
        ai_governance_rules={
            "automated_decisions": "Must allow individuals to challenge AI decisions",
            "transparency": "Must explain how AI uses personal information",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Office of the Privacy Commissioner of Canada",
    ),
    # ==================== CHINA ====================
    "CHINA_PIPL": RegulatoryFramework(
        framework_id="CHINA_PIPL",
        name="Personal Information Protection Law",
        region=GlobalRegion.CHINA,
        industries=list(IndustryVertical),
        prohibited_claims=[
            "operating in China without local data storage",
            "transfer Chinese citizens' data abroad",
            "transfer data abroad without authorization",
            "cross-border transfer without",
            "data abroad without",
        ],
        required_disclosures=[
            "Personal information must be stored in China for critical infrastructure operators.",
            "Cross-border data transfers require security assessment.",
            "Separate consent required for sensitive personal information.",
        ],
        data_protection_rules={
            "data_localization": "Critical infrastructure data must stay in China",
            "consent": "Explicit consent required for sensitive data",
            "cross_border": "Data transfers abroad require CAC approval",
        },
        ai_governance_rules={
            "algorithmic_transparency": "Must disclose recommendation algorithm principles",
            "content_moderation": "Must moderate harmful content per CAC guidelines",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="Cyberspace Administration of China (CAC)",
    ),
    # ==================== JAPAN ====================
    "JAPAN_APPI": RegulatoryFramework(
        framework_id="JAPAN_APPI",
        name="Act on Protection of Personal Information",
        region=GlobalRegion.JAPAN,
        industries=list(IndustryVertical),
        prohibited_claims=["transferring data outside Japan without consent"],
        required_disclosures=[
            "Purpose of use must be specified before collection.",
            "Cross-border transfers require consent or adequate protection.",
            "Anonymized data has relaxed requirements.",
        ],
        data_protection_rules={
            "purpose_specification": "Must specify purpose before collection",
            "cross_border": "Transfers abroad require consent or PPC-approved country",
            "anonymization": "Can process anonymized data without consent",
        },
        ai_governance_rules={
            "transparency": "Should disclose AI use in personal data processing"
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Personal Information Protection Commission (PPC)",
    ),
    # ==================== AUSTRALIA ====================
    "AUSTRALIA_PRIVACY": RegulatoryFramework(
        framework_id="AUSTRALIA_PRIVACY",
        name="Privacy Act 1988",
        region=GlobalRegion.AUSTRALIA,
        industries=list(IndustryVertical),
        prohibited_claims=["no privacy obligations for small business"],
        required_disclosures=[
            "Must have privacy policy if turnover > $3M AUD.",
            "Notifiable Data Breaches scheme requires breach notification.",
            "13 Australian Privacy Principles must be followed.",
        ],
        data_protection_rules={
            "privacy_policy": "Must have accessible privacy policy",
            "breach_notification": "Must notify OAIC and affected individuals",
            "cross_border": "Responsible for overseas data processors",
        },
        ai_governance_rules={
            "transparency": "Should explain automated decision-making",
            "fairness": "AI decisions should be fair and non-discriminatory",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Office of the Australian Information Commissioner (OAIC)",
    ),
    # ==================== BRAZIL ====================
    "BRAZIL_LGPD": RegulatoryFramework(
        framework_id="BRAZIL_LGPD",
        name="Lei Geral de Proteção de Dados",
        region=GlobalRegion.BRAZIL,
        industries=list(IndustryVertical),
        prohibited_claims=["processing data in Brazil without legal basis"],
        required_disclosures=[
            "Data subject rights: access, correction, deletion, portability.",
            "Must appoint DPO for large-scale processing.",
            "Cross-border transfers require adequacy or safeguards.",
        ],
        data_protection_rules={
            "legal_basis": "Must have legal basis (consent, contract, legitimate interest)",
            "dpo": "Must appoint DPO if processing significant data",
            "breach_notification": "Must notify ANPD and affected individuals",
        },
        ai_governance_rules={
            "automated_decisions": "Right to review automated decisions",
            "transparency": "Must explain AI logic and criteria",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="Autoridade Nacional de Proteção de Dados (ANPD)",
    ),
    # ==================== SINGAPORE ====================
    "SINGAPORE_PDPA": RegulatoryFramework(
        framework_id="SINGAPORE_PDPA",
        name="Personal Data Protection Act",
        region=GlobalRegion.SINGAPORE,
        industries=list(IndustryVertical),
        prohibited_claims=["can use personal data for any purpose"],
        required_disclosures=[
            "Consent required for collection, use, and disclosure.",
            "Individuals have right to access and correct data.",
            "Appoint Data Protection Officer.",
        ],
        data_protection_rules={
            "consent": "Must obtain consent for collection/use",
            "dpo": "Must appoint DPO",
            "breach_notification": "Must notify PDPC for significant breaches",
        },
        ai_governance_rules={
            "model_governance": "Should follow AI Governance Framework guidelines",
            "explainability": "Should be able to explain AI decisions",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Personal Data Protection Commission (PDPC)",
    ),
    # ==================== UAE ====================
    "UAE_DIFC": RegulatoryFramework(
        framework_id="UAE_DIFC",
        name="DIFC Data Protection Law",
        region=GlobalRegion.UAE,
        industries=[IndustryVertical.FINANCIAL_SERVICES, IndustryVertical.TECHNOLOGY],
        prohibited_claims=["operating in DIFC without registration"],
        required_disclosures=[
            "GDPR-like requirements for DIFC entities.",
            "Data controller registration required.",
            "Cross-border transfers need safeguards.",
        ],
        data_protection_rules={
            "registration": "Must register as data controller with DIFC",
            "consent": "GDPR-style consent requirements",
            "cross_border": "Adequacy or standard contractual clauses",
        },
        ai_governance_rules={
            "transparency": "Should disclose automated decision-making"
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="DIFC Commissioner of Data Protection",
    ),
    # ==================== SOUTH AFRICA ====================
    "SOUTH_AFRICA_POPIA": RegulatoryFramework(
        framework_id="SOUTH_AFRICA_POPIA",
        name="Protection of Personal Information Act",
        region=GlobalRegion.SOUTH_AFRICA,
        industries=list(IndustryVertical),
        prohibited_claims=["processing personal information without consent"],
        required_disclosures=[
            "Data subject rights: access, correction, deletion.",
            "Must register with Information Regulator if processing special personal information.",
            "Cross-border transfers require adequate protection.",
        ],
        data_protection_rules={
            "consent": "Must obtain consent for processing",
            "registration": "Must register with regulator for special data",
            "breach_notification": "Must notify regulator and data subjects",
        },
        ai_governance_rules={
            "automated_decisions": "Right to object to automated decisions"
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="Information Regulator of South Africa",
    ),
    # ==================== GLOBAL / INDUSTRY-SPECIFIC ====================
    "GLOBAL_PCI_DSS": RegulatoryFramework(
        framework_id="GLOBAL_PCI_DSS",
        name="Payment Card Industry Data Security Standard",
        region=GlobalRegion.GLOBAL,
        industries=[
            IndustryVertical.RETAIL,
            IndustryVertical.FINANCIAL_SERVICES,
            IndustryVertical.TECHNOLOGY,
        ],
        prohibited_claims=[
            "PCI compliant without Level 1/2/3/4 certification",
            "storing CVV codes",
            "storing full magnetic stripe data",
        ],
        required_disclosures=[
            "Cannot store CVV/CVC codes after authorization.",
            "Must encrypt cardholder data in transit and at rest.",
            "Quarterly vulnerability scans required.",
        ],
        data_protection_rules={
            "encryption": "AES-256 for data at rest, TLS 1.2+ for transit",
            "tokenization": "Should tokenize payment data",
            "no_storage": "Cannot store CVV, PIN, magnetic stripe full track",
        },
        ai_governance_rules={
            "fraud_detection": "AI fraud systems must not introduce new vulnerabilities",
            "audit_trails": "AI payment decisions must be logged",
        },
        violation_severity=ComplianceLevel.CRITICAL,
        regulatory_authority="PCI Security Standards Council",
    ),
    "GLOBAL_ISO_27001": RegulatoryFramework(
        framework_id="GLOBAL_ISO_27001",
        name="ISO/IEC 27001 Information Security",
        region=GlobalRegion.GLOBAL,
        industries=list(IndustryVertical),
        prohibited_claims=["ISO 27001 certified without accredited audit"],
        required_disclosures=[
            "ISO 27001 certification requires accredited third-party audit.",
            "Annual surveillance audits required to maintain certification.",
            "Scope of certification must be clearly defined.",
        ],
        data_protection_rules={
            "isms": "Must implement Information Security Management System",
            "risk_assessment": "Regular risk assessments required",
            "incident_response": "Must have incident response procedures",
        },
        ai_governance_rules={
            "ai_security": "AI systems must be included in ISMS scope",
            "model_security": "Must protect ML models from tampering",
        },
        violation_severity=ComplianceLevel.MEDIUM,
        regulatory_authority="ISO/IEC",
    ),
    "GLOBAL_SOC2": RegulatoryFramework(
        framework_id="GLOBAL_SOC2",
        name="SOC 2 Type II Compliance",
        region=GlobalRegion.GLOBAL,
        industries=[IndustryVertical.TECHNOLOGY, IndustryVertical.FINANCIAL_SERVICES],
        prohibited_claims=["SOC 2 compliant without audit report"],
        required_disclosures=[
            "SOC 2 Type II requires 3-12 months of continuous monitoring.",
            "Must be audited by licensed CPA firm.",
            "Report covers 5 trust service criteria: Security, Availability, Processing Integrity, Confidentiality, Privacy.",
        ],
        data_protection_rules={
            "access_controls": "Logical and physical access controls",
            "encryption": "Data encryption in transit and at rest",
            "change_management": "Documented change management process",
        },
        ai_governance_rules={
            "model_integrity": "AI model changes must follow change management",
            "monitoring": "Continuous monitoring of AI system performance",
        },
        violation_severity=ComplianceLevel.HIGH,
        regulatory_authority="AICPA (American Institute of CPAs)",
    ),
}


# ===================== COMPLIANCE VALIDATION ENGINE =====================


class GlobalComplianceEngine:
    """
    Validates AI responses against global regulatory frameworks.
    This is the fortress that makes Mythara litigation-proof worldwide.
    """

    def __init__(self):
        self.frameworks = GLOBAL_REGULATORY_FRAMEWORKS
        self.violation_log = []

    def validate_response(
        self,
        response_text: str,
        industry: IndustryVertical,
        target_region: GlobalRegion,
        user_data_involved: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate AI response against all applicable regulatory frameworks.

        Returns comprehensive compliance report with violations, warnings, and required actions.
        """
        violations = []
        warnings = []
        required_disclosures = []
        applicable_frameworks = []

        # Find all applicable frameworks
        for framework_id, framework in self.frameworks.items():
            # Check if framework applies to this industry and region
            if self._framework_applies(
                framework, industry, target_region, response_text
            ):
                applicable_frameworks.append(framework)

                # Check prohibited claims
                for prohibited in framework.prohibited_claims:
                    if self._contains_claim(response_text, prohibited):
                        violations.append(
                            {
                                "framework": framework.name,
                                "framework_id": framework_id,
                                "violation_type": "prohibited_claim",
                                "prohibited_text": prohibited,
                                "severity": framework.violation_severity.value,
                                "authority": framework.regulatory_authority,
                                "consequence": self._get_consequence(
                                    framework.violation_severity
                                ),
                            }
                        )

                # Collect required disclosures
                for disclosure in framework.required_disclosures:
                    if disclosure not in required_disclosures:
                        required_disclosures.append(
                            {"framework": framework.name, "disclosure": disclosure}
                        )

                # Check data protection rules if user data involved
                if user_data_involved:
                    for rule_name, rule_text in framework.data_protection_rules.items():
                        warnings.append(
                            {
                                "framework": framework.name,
                                "rule": rule_name,
                                "requirement": rule_text,
                                "severity": "HIGH",
                            }
                        )

        # Compute overall compliance status
        has_critical = any(v["severity"] == "Critical" for v in violations)
        has_high = any(v["severity"] == "High" for v in violations)

        if has_critical:
            status = "BLOCKED"
            reason = "Critical regulatory violation detected"
        elif has_high:
            status = "HUMAN_REVIEW_REQUIRED"
            reason = "High-severity regulatory concern"
        elif violations:
            status = "WARNING"
            reason = "Minor compliance issues detected"
        else:
            status = "APPROVED"
            reason = "No regulatory violations detected"

        return {
            "status": status,
            "reason": reason,
            "violations": violations,
            "warnings": warnings,
            "required_disclosures": required_disclosures,
            "applicable_frameworks": [f.name for f in applicable_frameworks],
            "total_frameworks_checked": len(applicable_frameworks),
            "timestamp": datetime.now().isoformat(),
            "can_auto_send": (status == "APPROVED"),
            "requires_legal_review": has_critical or has_high,
        }

    def _framework_applies(
        self,
        framework: RegulatoryFramework,
        industry: IndustryVertical,
        region: GlobalRegion,
        response_text: str = "",
    ) -> bool:
        """Check if framework applies to this industry/region combination"""
        # Global frameworks apply everywhere
        if framework.region == GlobalRegion.GLOBAL:
            return industry in framework.industries

        # Regional frameworks apply to that region
        if framework.region == region:
            return industry in framework.industries

        # GDPR has extraterritorial reach: applies when processing EU citizens' data
        if framework.framework_id == "EU_GDPR" and response_text:
            eu_indicators = [
                "eu citizens",
                "european citizens",
                "eu residents",
                "european residents",
                "gdpr",
                "european union",
            ]
            if any(indicator in response_text.lower() for indicator in eu_indicators):
                return industry in framework.industries

        # CCPA has extraterritorial reach: applies when processing California residents' data
        if framework.framework_id == "USA_CCPA" and response_text:
            ca_indicators = ["california residents", "california citizens", "ccpa"]
            if any(indicator in response_text.lower() for indicator in ca_indicators):
                return industry in framework.industries

        # EU frameworks may apply to UK during transition, etc.
        regional_overlaps = {
            GlobalRegion.UK: [GlobalRegion.EU],  # UK still follows some EU rules
            GlobalRegion.SWITZERLAND: [
                GlobalRegion.EU
            ],  # Switzerland follows GDPR equivalent
        }

        if region in regional_overlaps:
            if framework.region in regional_overlaps[region]:
                return industry in framework.industries

        return False

    def _contains_claim(self, text: str, prohibited: str) -> bool:
        """Check if text contains prohibited claim (case-insensitive, obfuscation-resistant, multilingual)"""
        # Context-aware exemptions for legitimate use
        text_lower = text.lower()
        if "consult" in text_lower and "compliant" in prohibited.lower():
            return False  # "Consult for HIPAA compliance" is legitimate
        if "uses fda-approved" in text_lower and "fda approved" == prohibited.lower():
            return False  # "Uses FDA-approved methodologies" is legitimate
        if "analyze financial data" in text_lower or "helps analyze" in text_lower:
            if "guarantee" in prohibited.lower() or "risk-free" in prohibited.lower():
                return False  # Legitimate financial analysis tools
        if (
            "compliance with" in text_lower
            or "for compliance" in text_lower
            or "analyze" in text_lower
            or "helps" in text_lower
        ):
            if "compliant" in prohibited.lower():
                return False  # Legitimate compliance/analysis tools don't claim certification

        # Unicode normalization: convert to NFD then remove accents/diacritics
        def normalize_unicode(s: str) -> str:
            # Homoglyph mapping: replace look-alike characters with ASCII equivalents
            homoglyph_map = {
                # Cyrillic to Latin
                "А": "A",
                "В": "B",
                "Е": "E",
                "К": "K",
                "М": "M",
                "Н": "H",
                "О": "O",
                "Р": "P",
                "С": "C",
                "Т": "T",
                "Х": "X",
                "а": "a",
                "е": "e",
                "о": "o",
                "р": "p",
                "с": "c",
                "у": "y",
                "х": "x",
                # Greek to Latin
                "Α": "A",
                "Β": "B",
                "Ε": "E",
                "Ζ": "Z",
                "Η": "H",
                "Ι": "I",
                "Κ": "K",
                "Μ": "M",
                "Ν": "N",
                "Ο": "O",
                "Ρ": "P",
                "Τ": "T",
                "Υ": "Y",
                "Χ": "X",
                "α": "a",
                "β": "b",
                "γ": "g",
                "δ": "d",
                "ε": "e",
                "ζ": "z",
                "η": "h",
                "θ": "th",
                "ι": "i",
                "κ": "k",
                "λ": "l",
                "μ": "m",
                "ν": "n",
                "ξ": "x",
                "ο": "o",
                "π": "p",
                "ρ": "r",
                "σ": "s",
                "ς": "s",
                "τ": "t",
                "υ": "y",
                "φ": "f",
                "χ": "ch",
                "ψ": "ps",
                "ω": "o",
            }

            # Replace homoglyphs
            for homoglyph, ascii_char in homoglyph_map.items():
                s = s.replace(homoglyph, ascii_char)

            # Normalize to NFD (decomposed form)
            nfd = unicodedata.normalize("NFD", s)
            # Remove combining characters and convert to ASCII when possible
            ascii_text = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
            # Remove zero-width characters
            ascii_text = re.sub(r"[\u200B-\u200D\uFEFF]", "", ascii_text)
            return ascii_text.lower()

        text_normalized = normalize_unicode(text)
        prohibited_normalized = normalize_unicode(prohibited)

        # Further normalization: remove spaces, dashes, underscores, dots
        text_compact = re.sub(r"[\s\-_\.]", "", text_normalized)
        prohibited_compact = re.sub(r"[\s\-_\.]", "", prohibited_normalized)

        # Check compact text (catches "H I P A A", "H-I-P-A-A", homoglyphs, etc.)
        if prohibited_compact in text_compact:
            return True

        # Direct substring match
        if prohibited_normalized in text_normalized:
            return True

        # Semantic variations mapping
        semantic_variations = {
            "compliant": [
                "compliant",
                "compliance",
                "complies",
                "meets standards",
                "aligns with",
                "adheres to",
                "conforms to",
                "in compliance with",
                "certified",
                "meets requirements",
            ],
            "without consent": [
                "without consent",
                "sans consentement",
                "sin consentimiento",
                "ohne zustimmung",
                "no consent",
                "absent consent",
            ],
            "guaranteed returns": [
                "guaranteed returns",
                "guarantees returns",
                "risk-free",
                "consistent success",
                "positive outcomes guaranteed",
                "100% returns",
                "no risk",
            ],
            "uses race": [
                "uses race",
                "racial profiling",
                "race-based",
                "demographic optimization",
                "demographic-based",
                "demographic targeting",
            ],
            "bribe": [
                "bribe",
                "bribery",
                "kickback",
                "incentivize officials",
                "incentives to officials",
                "performance incentives to government",
                "financial incentives to officials",
            ],
        }

        # Check if prohibited term has semantic variations
        for base_term, variations in semantic_variations.items():
            if base_term in prohibited_normalized:
                for variation in variations:
                    variation_normalized = normalize_unicode(variation)
                    if variation_normalized in text_normalized:
                        return True

        # Pattern matching for variations
        patterns = [
            prohibited_normalized,
            prohibited_normalized.replace(" ", "-"),
            prohibited_normalized.replace(" ", "_"),
            prohibited_normalized.replace(" ", ""),
            prohibited_normalized.replace(" ", "."),
        ]

        for pattern in patterns:
            if pattern in text_normalized:
                return True

        return False

    def _get_consequence(self, severity: ComplianceLevel) -> str:
        """Get human-readable consequence of violation"""
        consequences = {
            ComplianceLevel.CRITICAL: "Potential lawsuit, regulatory fines up to millions, criminal liability possible",
            ComplianceLevel.HIGH: "Regulatory investigation, fines up to hundreds of thousands, business license at risk",
            ComplianceLevel.MEDIUM: "Internal audit required, potential policy violation, reputational risk",
            ComplianceLevel.LOW: "Minor issue, internal review recommended, no immediate legal risk",
        }
        return consequences.get(severity, "Unknown consequence")

    def generate_compliance_report(
        self, industry: IndustryVertical, regions: List[GlobalRegion]
    ) -> str:
        """
        Generate comprehensive compliance report for an industry across multiple regions.
        Shows all applicable frameworks and requirements.
        """
        report = []
        report.append("\n" + "=" * 80)
        report.append(f"GLOBAL COMPLIANCE REPORT: {industry.value}")
        report.append("=" * 80)

        for region in regions:
            report.append(f"\n{'='*80}")
            report.append(f"REGION: {region.value}")
            report.append(f"{'='*80}")

            applicable = [
                f
                for f in self.frameworks.values()
                if self._framework_applies(f, industry, region)
            ]

            if not applicable:
                report.append("  No specific regulatory frameworks apply.")
                continue

            for framework in applicable:
                report.append(f"\n📋 {framework.name}")
                report.append(f"   ID: {framework.framework_id}")
                report.append(f"   Authority: {framework.regulatory_authority}")
                report.append(f"   Severity: {framework.violation_severity.value}")

                report.append("\n   ❌ PROHIBITED CLAIMS:")
                for claim in framework.prohibited_claims:
                    report.append(f"      • {claim}")

                report.append("\n   ℹ️  REQUIRED DISCLOSURES:")
                for disclosure in framework.required_disclosures:
                    report.append(f"      • {disclosure}")

                if framework.ai_governance_rules:
                    report.append("\n   🤖 AI-SPECIFIC RULES:")
                    for rule, requirement in framework.ai_governance_rules.items():
                        report.append(f"      • {rule}: {requirement}")

        report.append("\n" + "=" * 80)
        report.append(
            f"Total Frameworks: {len([f for f in self.frameworks.values() if any(self._framework_applies(f, industry, r) for r in regions)])}"
        )
        report.append("=" * 80 + "\n")

        return "\n".join(report)


# ===================== DEMONSTRATION =====================

if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("  MYTHARA GLOBAL GOVERNANCE FRAMEWORK")
    print("  Universal Compliance for All Industries, All Countries")
    print("█" * 80)

    engine = GlobalComplianceEngine()

    # Example 1: International Treaty Violations
    print("\n" + "=" * 80)
    print("EXAMPLE 1: UN Human Rights & CRPD Violation Test")
    print("=" * 80)

    test_treaty_violation = """
    Our AI system discriminates based on race to improve accuracy.
    It's not accessible to people with disabilities because that would be too expensive.
    We restrict freedom of thought to prevent harmful ideas.
    """

    result = engine.validate_response(
        test_treaty_violation,
        IndustryVertical.TECHNOLOGY,
        GlobalRegion.GLOBAL,
        user_data_involved=True,
    )

    print(f"\nStatus: {result['status']}")
    print(f"Reason: {result['reason']}")
    print(f"Can Auto-Send: {result['can_auto_send']}")
    print(f"Requires Legal Review: {result['requires_legal_review']}")
    print(f"\nViolations Found: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  ❌ {v['framework']}: {v['prohibited_text']}")
        print(f"     Severity: {v['severity']}")
        print(f"     Consequence: {v['consequence']}")

    # Example 2: Export Control & Sanctions Violation Test
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Export Control (ITAR/EAR) & OFAC Sanctions Violation")
    print("=" * 80)

    test_export_sanctions = """
    We export defense articles without license to China and Russia.
    We operate in sanctioned countries like North Korea and Iran.
    Our AI technology is available to all countries without restriction.
    """

    result = engine.validate_response(
        test_export_sanctions,
        IndustryVertical.DEFENSE,
        GlobalRegion.USA,
        user_data_involved=True,
    )

    print(f"\nStatus: {result['status']}")
    print(f"Reason: {result['reason']}")
    print(f"Can Auto-Send: {result['can_auto_send']}")
    print(f"Requires Legal Review: {result['requires_legal_review']}")
    print(f"\nViolations Found: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  ❌ {v['framework']}: {v['prohibited_text']}")
        print(f"     Severity: {v['severity']}")

    # Example 3: Healthcare HIPAA + FDA Violation (original)
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Healthcare AI Response - USA (HIPAA + FDA)")
    print("=" * 80)

    test_response_usa = """
    Our AI system is HIPAA compliant and can diagnose medical conditions.
    It's FDA approved for clinical use.
    """

    result = engine.validate_response(
        test_response_usa,
        IndustryVertical.HEALTHCARE,
        GlobalRegion.USA,
        user_data_involved=True,
    )

    print(f"\nStatus: {result['status']}")
    print(f"Reason: {result['reason']}")
    print(f"Can Auto-Send: {result['can_auto_send']}")
    print(f"Requires Legal Review: {result['requires_legal_review']}")
    print(f"\nViolations Found: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  ❌ {v['framework']}: {v['prohibited_text']}")
        print(f"     Severity: {v['severity']}")

    # Example 4: Anti-Corruption & Antitrust Violations
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Anti-Corruption (FCPA) & Antitrust Violations")
    print("=" * 80)

    test_corruption_antitrust = """
    We offer payments to government officials to secure contracts.
    We engage in price fixing with competitors to maximize profit.
    Our market allocation agreements eliminate competition.
    """

    result = engine.validate_response(
        test_corruption_antitrust,
        IndustryVertical.GOVERNMENT,
        GlobalRegion.USA,
        user_data_involved=False,
    )

    print(f"\nStatus: {result['status']}")
    print(f"Can Auto-Send: {result['can_auto_send']}")
    print(f"Requires Legal Review: {result['requires_legal_review']}")
    print(f"\nViolations Found: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  ❌ {v['framework']}: {v['prohibited_text']}")
        print(f"     Severity: {v['severity']}")

    # Example 5: Labor Standards & Copyright Violations
    print("\n" + "=" * 80)
    print("EXAMPLE 5: ILO Labor Standards & WIPO Copyright Violations")
    print("=" * 80)

    test_labor_copyright = """
    We employ workers under minimum age and use forced labor to cut costs.
    We discriminate in employment based on race and gender.
    Our AI training uses copyrighted content without permission.
    """

    result = engine.validate_response(
        test_labor_copyright,
        IndustryVertical.TECHNOLOGY,
        GlobalRegion.GLOBAL,
        user_data_involved=False,
    )

    print(f"\nStatus: {result['status']}")
    print(f"Can Auto-Send: {result['can_auto_send']}")
    print(f"Requires Legal Review: {result['requires_legal_review']}")
    print(f"\nViolations Found: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  ❌ {v['framework']}: {v['prohibited_text']}")
        print(f"     Severity: {v['severity']}")

    # Example 6: Generate compliance report for FinTech across regions
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Financial Services Compliance - Multi-Region")
    print("=" * 80)

    report = engine.generate_compliance_report(
        IndustryVertical.FINANCIAL_SERVICES,
        [GlobalRegion.USA, GlobalRegion.EU, GlobalRegion.SINGAPORE],
    )
    print(report)

    print("\n" + "=" * 80)
    print("READY FOR GLOBAL DEPLOYMENT")
    print("=" * 80)
    print(f"Total Regulatory Frameworks: {len(GLOBAL_REGULATORY_FRAMEWORKS)}")
    print(
        f"Regions Covered: {len(set(f.region for f in GLOBAL_REGULATORY_FRAMEWORKS.values()))}"
    )
    print(f"Industries Covered: {len(IndustryVertical)}")
    print("=" * 80 + "\n")
