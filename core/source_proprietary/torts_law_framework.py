#!/usr/bin/env python3
"""
Mythara Engine - Comprehensive Torts Law Framework
Public domain legal knowledge integrated into covenant integrity system.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

# ===================== TORTS LAW TAXONOMY =====================


class TortCategory(Enum):
    """Primary categories of torts"""

    INTENTIONAL = "intentional"
    NEGLIGENCE = "negligence"
    STRICT_LIABILITY = "strict_liability"
    DEFAMATION = "defamation"
    PRIVACY = "privacy"
    ECONOMIC = "economic"
    PROPERTY = "property"
    DIGNITARY = "dignitary"
    NUISANCE = "nuisance"
    EMPLOYMENT = "employment"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    INTELLECTUAL_PROPERTY = "intellectual_property"


class IntentionalTort(Enum):
    """Intentional torts against persons and property"""

    # Against Persons
    BATTERY = "battery"
    ASSAULT = "assault"
    FALSE_IMPRISONMENT = "false_imprisonment"
    INTENTIONAL_INFLICTION_EMOTIONAL_DISTRESS = "iied"

    # Against Property
    TRESPASS_TO_LAND = "trespass_land"
    TRESPASS_TO_CHATTELS = "trespass_chattels"
    CONVERSION = "conversion"

    # Against Dignity
    DEFAMATION_LIBEL = "libel"
    DEFAMATION_SLANDER = "slander"
    INVASION_OF_PRIVACY = "privacy_invasion"
    FRAUD = "fraud"
    MISREPRESENTATION = "misrepresentation"

    # Legal Process Torts
    MALICIOUS_PROSECUTION = "malicious_prosecution"
    ABUSE_OF_PROCESS = "abuse_of_process"
    WRONGFUL_CIVIL_PROCEEDINGS = "wrongful_civil_proceedings"


class NegligenceTort(Enum):
    """Negligence-based torts"""

    ORDINARY_NEGLIGENCE = "ordinary_negligence"
    GROSS_NEGLIGENCE = "gross_negligence"
    NEGLIGENCE_PER_SE = "negligence_per_se"
    RES_IPSA_LOQUITUR = "res_ipsa"
    MEDICAL_MALPRACTICE = "medical_malpractice"
    LEGAL_MALPRACTICE = "legal_malpractice"
    PROFESSIONAL_NEGLIGENCE = "professional_negligence"
    PREMISES_LIABILITY = "premises_liability"
    NEGLIGENT_INFLICTION_EMOTIONAL_DISTRESS = "nied"
    WRONGFUL_DEATH = "wrongful_death"
    SURVIVAL_ACTION = "survival_action"

    # Employment
    NEGLIGENT_HIRING = "negligent_hiring"
    NEGLIGENT_SUPERVISION = "negligent_supervision"
    NEGLIGENT_RETENTION = "negligent_retention"

    # Security & Data
    NEGLIGENT_SECURITY = "negligent_security"
    DATA_BREACH_NEGLIGENCE = "data_breach_negligence"
    CYBERSECURITY_NEGLIGENCE = "cybersecurity_negligence"


class StrictLiabilityTort(Enum):
    """Strict liability torts"""

    ABNORMALLY_DANGEROUS_ACTIVITIES = "abnormally_dangerous"
    PRODUCTS_LIABILITY_DEFECT = "products_defect"
    PRODUCTS_LIABILITY_FAILURE_TO_WARN = "products_warning"
    PRODUCTS_LIABILITY_DESIGN_DEFECT = "products_design"
    ANIMAL_LIABILITY = "animal_liability"
    ULTRAHAZARDOUS_ACTIVITY = "ultrahazardous"


class PrivacyTort(Enum):
    """Privacy invasion torts (4 categories from Restatement)"""

    INTRUSION_UPON_SECLUSION = "intrusion_seclusion"
    PUBLIC_DISCLOSURE_PRIVATE_FACTS = "public_disclosure"
    FALSE_LIGHT = "false_light"
    APPROPRIATION_NAME_LIKENESS = "appropriation"


class NuisanceTort(Enum):
    """Nuisance torts"""

    PRIVATE_NUISANCE = "private_nuisance"
    PUBLIC_NUISANCE = "public_nuisance"
    ATTRACTIVE_NUISANCE = "attractive_nuisance"


class EmploymentTort(Enum):
    """Employment-related torts"""

    WRONGFUL_TERMINATION = "wrongful_termination"
    RETALIATION = "retaliation"
    DISCRIMINATION = "discrimination"
    SEXUAL_HARASSMENT = "sexual_harassment"
    HOSTILE_WORK_ENVIRONMENT = "hostile_work_environment"
    BLACKLISTING = "blacklisting"
    INTERFERENCE_WITH_EMPLOYMENT = "interference_employment"


class HealthcareTort(Enum):
    """Healthcare-specific torts"""

    MEDICAL_MALPRACTICE = "medical_malpractice"
    LACK_OF_INFORMED_CONSENT = "lack_informed_consent"
    MEDICAL_BATTERY = "medical_battery"
    ABANDONMENT = "patient_abandonment"
    HIPAA_VIOLATION = "hipaa_violation"
    WRONGFUL_BIRTH = "wrongful_birth"
    WRONGFUL_LIFE = "wrongful_life"


class TechnologyTort(Enum):
    """Technology and digital torts"""

    DATA_BREACH = "data_breach"
    CYBERSECURITY_NEGLIGENCE = "cybersecurity_negligence"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RANSOMWARE_NEGLIGENCE = "ransomware_negligence"
    AI_ALGORITHM_HARM = "ai_algorithm_harm"
    PLATFORM_NEGLIGENCE = "platform_negligence"
    DOXXING = "doxxing"
    CYBERBULLYING = "cyberbullying"
    ONLINE_DEFAMATION = "online_defamation"


class IntellectualPropertyTort(Enum):
    """IP-related torts"""

    PATENT_INFRINGEMENT = "patent_infringement"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADE_SECRET_MISAPPROPRIATION = "trade_secret_misappropriation"
    UNFAIR_COMPETITION = "unfair_competition_ip"
    DILUTION = "trademark_dilution"
    PASSING_OFF = "passing_off"


class EconomicTort(Enum):
    """Economic and business torts"""

    FRAUD = "fraud"
    FRAUDULENT_MISREPRESENTATION = "fraudulent_misrep"
    NEGLIGENT_MISREPRESENTATION = "negligent_misrep"
    INTERFERENCE_WITH_CONTRACT = "contract_interference"
    INTERFERENCE_WITH_PROSPECTIVE_ADVANTAGE = "prospective_advantage"
    UNFAIR_COMPETITION = "unfair_competition"
    TRADE_LIBEL = "trade_libel"
    INJURIOUS_FALSEHOOD = "injurious_falsehood"
    CONSPIRACY = "conspiracy"
    WRONGFUL_TERMINATION = "wrongful_termination"
    BREACH_OF_FIDUCIARY_DUTY = "breach_fiduciary_duty"
    TORTIOUS_INTERFERENCE_BUSINESS = "tortious_interference_business"


class DefenseType(Enum):
    """Common tort defenses"""

    # Privilege Defenses
    CONSENT = "consent"
    SELF_DEFENSE = "self_defense"
    DEFENSE_OF_OTHERS = "defense_others"
    DEFENSE_OF_PROPERTY = "defense_property"
    NECESSITY = "necessity"
    DISCIPLINE = "discipline"
    ARREST = "arrest"
    TRUTH = "truth"  # Defamation
    OPINION = "opinion"  # Defamation
    ABSOLUTE_PRIVILEGE = "absolute_privilege"  # Judicial, legislative
    QUALIFIED_PRIVILEGE = "qualified_privilege"  # Good faith

    # Negligence Defenses
    CONTRIBUTORY_NEGLIGENCE = "contributory_negligence"
    COMPARATIVE_NEGLIGENCE = "comparative_negligence"
    ASSUMPTION_OF_RISK = "assumption_risk"
    LAST_CLEAR_CHANCE = "last_clear_chance"

    # Immunities
    GOVERNMENTAL_IMMUNITY = "governmental_immunity"
    CHARITABLE_IMMUNITY = "charitable_immunity"
    SPOUSAL_IMMUNITY = "spousal_immunity"
    PARENTAL_IMMUNITY = "parental_immunity"
    JUDICIAL_IMMUNITY = "judicial_immunity"
    LEGISLATIVE_IMMUNITY = "legislative_immunity"
    DIPLOMATIC_IMMUNITY = "diplomatic_immunity"

    # Business & Economic
    ECONOMIC_LOSS_RULE = "economic_loss_rule"
    BUSINESS_JUDGMENT_RULE = "business_judgment_rule"
    GOOD_FAITH_COMPETITION = "good_faith_competition"
    AT_WILL_EMPLOYMENT = "at_will_employment"
    LEGITIMATE_BUSINESS_REASON = "legitimate_business_reason"

    # Technology & Privacy
    SECTION_230_IMMUNITY = "section_230"  # CDA immunity
    DMCA_SAFE_HARBOR = "dmca_safe_harbor"
    CONSENT_TO_MONITORING = "consent_monitoring"
    NO_DUTY_TO_MONITOR = "no_duty_to_monitor"
    NEWSWORTHINESS = "newsworthiness"

    # Healthcare
    EMERGENCY_DOCTRINE = "emergency_doctrine"
    GOOD_SAMARITAN = "good_samaritan"
    THERAPEUTIC_PRIVILEGE = "therapeutic_privilege"

    # Property & Nuisance
    COMING_TO_NUISANCE = "coming_to_nuisance"

    # IP & Trade Secrets
    INDEPENDENT_DERIVATION = "independent_derivation"
    REVERSE_ENGINEERING = "reverse_engineering"
    PUBLIC_DOMAIN = "public_domain"

    # Malicious Prosecution
    PROBABLE_CAUSE = "probable_cause"
    ADVICE_OF_COUNSEL = "advice_of_counsel"
    REASONABLE_INVESTIGATION = "reasonable_investigation"

    # Other
    STATUTE_OF_LIMITATIONS = "statute_limitations"
    STATUTE_OF_REPOSE = "statute_repose"
    SUPERSEDING_CAUSE = "superseding_cause"
    PREEMPTION = "preemption"  # Federal preempts state
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    ILLEGALITY = "illegality"  # Plaintiff engaged in illegal activity


# ===================== LEGAL ELEMENTS FRAMEWORK =====================


@dataclass
class TortElement:
    """Individual element of a tort claim"""

    element_name: str
    description: str
    required: bool
    proof_standard: str  # "preponderance", "clear_and_convincing", "beyond_reasonable"
    typical_evidence: List[str]


@dataclass
class TortDefinition:
    """Complete definition of a specific tort"""

    tort_name: str
    category: TortCategory
    subcategory: Enum
    elements: List[TortElement]
    defenses: List[DefenseType]
    damages_available: List[str]
    statute_of_limitations_years: Dict[str, int]  # jurisdiction: years
    notes: str
    landmark_cases: List[str]
    restatement_sections: List[str]


# ===================== COMPREHENSIVE TORTS INDEX =====================


class TortsLawIndex:
    """
    Comprehensive index of torts law principles.
    Built from public domain legal knowledge (Restatements, common law).
    """

    def __init__(self):
        self.torts_database = self._build_torts_database()

    def _build_torts_database(self) -> Dict[str, TortDefinition]:
        """Build comprehensive torts database"""
        database = {}

        # ===================== BATTERY =====================
        database["battery"] = TortDefinition(
            tort_name="Battery",
            category=TortCategory.INTENTIONAL,
            subcategory=IntentionalTort.BATTERY,
            elements=[
                TortElement(
                    element_name="Intent",
                    description="Defendant intended to cause harmful or offensive contact",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "witness testimony",
                        "defendant statements",
                        "circumstantial evidence",
                    ],
                ),
                TortElement(
                    element_name="Harmful or Offensive Contact",
                    description="Contact was harmful or offensive to reasonable person",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "photographs",
                        "victim testimony",
                    ],
                ),
                TortElement(
                    element_name="Causation",
                    description="Defendant's conduct caused the contact",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["physical evidence", "video", "expert testimony"],
                ),
                TortElement(
                    element_name="Lack of Consent",
                    description="Plaintiff did not consent to the contact",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["victim testimony", "absence of consent forms"],
                ),
            ],
            defenses=[
                DefenseType.CONSENT,
                DefenseType.SELF_DEFENSE,
                DefenseType.DEFENSE_OF_OTHERS,
                DefenseType.DEFENSE_OF_PROPERTY,
                DefenseType.NECESSITY,
                DefenseType.DISCIPLINE,
            ],
            damages_available=[
                "compensatory damages",
                "nominal damages",
                "punitive damages (if malicious)",
                "pain and suffering",
                "medical expenses",
                "lost wages",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 1,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Battery requires intent to cause contact, not intent to harm. Transferred intent applies.",
            landmark_cases=[
                "Vosburg v. Putney, 80 Wis. 523 (1891)",
                "Cole v. Turner, 90 Eng. Rep. 958 (1704)",
                "Fisher v. Carousel Motor Hotel, 424 S.W.2d 627 (Tex. 1967)",
            ],
            restatement_sections=["Restatement (Second) of Torts § 13", "§ 18", "§ 19"],
        )

        # ===================== ASSAULT =====================
        database["assault"] = TortDefinition(
            tort_name="Assault",
            category=TortCategory.INTENTIONAL,
            subcategory=IntentionalTort.ASSAULT,
            elements=[
                TortElement(
                    element_name="Intent",
                    description="Defendant intended to cause apprehension of harmful/offensive contact",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "threatening statements",
                        "gestures",
                        "witness testimony",
                    ],
                ),
                TortElement(
                    element_name="Reasonable Apprehension",
                    description="Plaintiff reasonably believed contact was imminent",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "victim testimony",
                        "circumstances",
                        "defendant proximity",
                    ],
                ),
                TortElement(
                    element_name="Imminent Contact",
                    description="Threatened contact appeared imminent, not future",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["timeline", "distance", "weapon accessibility"],
                ),
                TortElement(
                    element_name="Apparent Ability",
                    description="Defendant had apparent ability to carry out threat",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "physical capability",
                        "weapon presence",
                        "positioning",
                    ],
                ),
            ],
            defenses=[
                DefenseType.CONSENT,
                DefenseType.SELF_DEFENSE,
                DefenseType.DEFENSE_OF_OTHERS,
            ],
            damages_available=[
                "compensatory damages",
                "nominal damages",
                "punitive damages",
                "emotional distress damages",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 1,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Words alone generally insufficient; requires overt act. No actual contact needed.",
            landmark_cases=[
                "I de S et ux. v. W de S, Y.B. Lib. Ass. folio 99, placitum 60 (1348)",
                "Western Union Telegraph Co. v. Hill, 25 Ala. App. 540 (1933)",
            ],
            restatement_sections=["Restatement (Second) of Torts § 21", "§ 22", "§ 23"],
        )

        # ===================== FALSE IMPRISONMENT =====================
        database["false_imprisonment"] = TortDefinition(
            tort_name="False Imprisonment",
            category=TortCategory.INTENTIONAL,
            subcategory=IntentionalTort.FALSE_IMPRISONMENT,
            elements=[
                TortElement(
                    element_name="Intent to Confine",
                    description="Defendant intended to confine or restrain plaintiff",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "defendant actions",
                        "statements",
                        "physical barriers",
                    ],
                ),
                TortElement(
                    element_name="Actual Confinement",
                    description="Plaintiff was actually confined or restrained",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "physical barriers",
                        "force",
                        "threats",
                        "time confined",
                    ],
                ),
                TortElement(
                    element_name="Consciousness of Confinement",
                    description="Plaintiff was aware of confinement or harmed by it",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "victim testimony",
                        "attempts to escape",
                        "harm suffered",
                    ],
                ),
                TortElement(
                    element_name="No Reasonable Means of Escape",
                    description="No safe or reasonable way to escape known to plaintiff",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "physical layout",
                        "blocked exits",
                        "threats if escaped",
                    ],
                ),
            ],
            defenses=[DefenseType.CONSENT, DefenseType.ARREST, DefenseType.NECESSITY],
            damages_available=[
                "compensatory damages",
                "nominal damages",
                "punitive damages",
                "emotional distress",
                "loss of time",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 1,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Confinement can be by physical barriers, force, threats, or assertion of legal authority.",
            landmark_cases=[
                "Bird v. Jones, 7 Q.B. 742 (1845)",
                "Parvi v. City of Kingston, 41 N.Y.2d 553 (1977)",
                "Enright v. Groves, 39 Colo. App. 39 (1977)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 35",
                "§ 36",
                "§ 40A",
            ],
        )

        # ===================== IIED =====================
        database["iied"] = TortDefinition(
            tort_name="Intentional Infliction of Emotional Distress (IIED)",
            category=TortCategory.INTENTIONAL,
            subcategory=IntentionalTort.INTENTIONAL_INFLICTION_EMOTIONAL_DISTRESS,
            elements=[
                TortElement(
                    element_name="Extreme and Outrageous Conduct",
                    description="Conduct exceeds all bounds of decency tolerated by society",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "conduct details",
                        "context",
                        "expert testimony",
                        "community standards",
                    ],
                ),
                TortElement(
                    element_name="Intent or Recklessness",
                    description="Defendant intended to cause distress or acted recklessly",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "statements",
                        "pattern of behavior",
                        "knowledge of vulnerability",
                    ],
                ),
                TortElement(
                    element_name="Causation",
                    description="Defendant's conduct caused the emotional distress",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "temporal relationship",
                        "medical records",
                        "expert testimony",
                    ],
                ),
                TortElement(
                    element_name="Severe Emotional Distress",
                    description="Plaintiff suffered severe emotional distress",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "psychological evaluations",
                        "testimony",
                        "physical manifestations",
                    ],
                ),
            ],
            defenses=[DefenseType.CONSENT, DefenseType.STATUTE_OF_LIMITATIONS],
            damages_available=[
                "emotional distress damages",
                "medical expenses for treatment",
                "punitive damages (if malicious)",
                "physical manifestation damages",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 1,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Very high bar; conduct must be truly outrageous. Mere insults insufficient.",
            landmark_cases=[
                "State Rubbish Collectors Ass'n v. Siliznoff, 38 Cal. 2d 330 (1952)",
                "Harris v. Jones, 281 Md. 560 (1977)",
                "Hustler Magazine v. Falwell, 485 U.S. 46 (1988)",
            ],
            restatement_sections=["Restatement (Second) of Torts § 46"],
        )

        # ===================== DEFAMATION =====================
        database["defamation"] = TortDefinition(
            tort_name="Defamation (Libel/Slander)",
            category=TortCategory.DEFAMATION,
            subcategory=IntentionalTort.DEFAMATION_LIBEL,
            elements=[
                TortElement(
                    element_name="Defamatory Statement",
                    description="Statement that harms reputation in community",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["statement itself", "publication", "context"],
                ),
                TortElement(
                    element_name="False Statement of Fact",
                    description="Statement is false and presented as fact (not opinion)",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "factual records",
                        "expert testimony",
                        "contradictory evidence",
                    ],
                ),
                TortElement(
                    element_name="Publication to Third Party",
                    description="Statement communicated to at least one other person",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["witnesses", "media", "documents", "recordings"],
                ),
                TortElement(
                    element_name="Fault (Public Figures: Actual Malice)",
                    description="Negligence or actual malice depending on plaintiff status",
                    required=True,
                    proof_standard="clear_and_convincing",  # for actual malice
                    typical_evidence=[
                        "knowledge of falsity",
                        "reckless disregard",
                        "investigation records",
                    ],
                ),
                TortElement(
                    element_name="Damages or Per Se",
                    description="Actual damages or statement is defamatory per se",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "financial loss",
                        "reputation harm",
                        "per se category",
                    ],
                ),
            ],
            defenses=[DefenseType.CONSENT, DefenseType.STATUTE_OF_LIMITATIONS],
            damages_available=[
                "actual damages (economic loss)",
                "presumed damages (if per se)",
                "punitive damages (if actual malice)",
                "emotional distress",
                "reputational harm",
            ],
            statute_of_limitations_years={
                "federal": 1,
                "california": 1,
                "new_york": 1,
                "texas": 1,
                "florida": 2,
                "default": 1,
            },
            notes="First Amendment protections apply. Truth is absolute defense. Opinion vs fact critical.",
            landmark_cases=[
                "New York Times Co. v. Sullivan, 376 U.S. 254 (1964)",
                "Gertz v. Robert Welch, Inc., 418 U.S. 323 (1974)",
                "Milkovich v. Lorain Journal Co., 497 U.S. 1 (1990)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 558",
                "§ 559",
                "§ 568",
                "§ 580A",
                "§ 580B",
            ],
        )

        # ===================== NEGLIGENCE =====================
        database["negligence"] = TortDefinition(
            tort_name="Negligence",
            category=TortCategory.NEGLIGENCE,
            subcategory=NegligenceTort.ORDINARY_NEGLIGENCE,
            elements=[
                TortElement(
                    element_name="Duty of Care",
                    description="Defendant owed plaintiff a duty of reasonable care",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "relationship",
                        "foreseeability",
                        "policy considerations",
                    ],
                ),
                TortElement(
                    element_name="Breach of Duty",
                    description="Defendant breached duty by failing to exercise reasonable care",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "expert testimony",
                        "standards of care",
                        "conduct comparison",
                    ],
                ),
                TortElement(
                    element_name="Actual Causation",
                    description="But-for causation: injury would not have occurred but for breach",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "timeline",
                        "expert testimony",
                        "substantial factor test",
                    ],
                ),
                TortElement(
                    element_name="Proximate Causation",
                    description="Harm was foreseeable consequence of breach",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["foreseeability analysis", "scope of risk"],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered actual damages",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "bills",
                        "economic loss",
                        "expert testimony",
                    ],
                ),
            ],
            defenses=[
                DefenseType.CONTRIBUTORY_NEGLIGENCE,
                DefenseType.COMPARATIVE_NEGLIGENCE,
                DefenseType.ASSUMPTION_OF_RISK,
                DefenseType.STATUTE_OF_LIMITATIONS,
                DefenseType.SUPERSEDING_CAUSE,
            ],
            damages_available=[
                "economic damages (medical, lost wages)",
                "non-economic damages (pain, suffering)",
                "property damage",
                "loss of consortium",
                "future damages",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 3,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Reasonable person standard. Foreseeability central to duty and proximate cause.",
            landmark_cases=[
                "Palsgraf v. Long Island R.R. Co., 248 N.Y. 339 (1928)",
                "Rowland v. Christian, 69 Cal. 2d 108 (1968)",
                "Summers v. Tice, 33 Cal. 2d 80 (1948)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 281",
                "§ 282",
                "§ 283",
                "§ 430",
                "§ 431",
            ],
        )

        # ===================== PRODUCTS LIABILITY =====================
        database["products_liability"] = TortDefinition(
            tort_name="Products Liability - Strict Liability",
            category=TortCategory.STRICT_LIABILITY,
            subcategory=StrictLiabilityTort.PRODUCTS_LIABILITY_DEFECT,
            elements=[
                TortElement(
                    element_name="Defective Product",
                    description="Product has manufacturing, design, or warning defect",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "product examination",
                        "expert testimony",
                        "testing",
                        "similar incidents",
                    ],
                ),
                TortElement(
                    element_name="Existed When Left Defendant",
                    description="Defect existed when product left defendant's control",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "manufacturing records",
                        "timeline",
                        "distribution chain",
                    ],
                ),
                TortElement(
                    element_name="Reached User Without Substantial Change",
                    description="Product reached user without substantial alteration",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "product history",
                        "maintenance records",
                        "modifications",
                    ],
                ),
                TortElement(
                    element_name="Proximate Cause",
                    description="Defect proximately caused plaintiff's injuries",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "expert causation testimony",
                        "incident report",
                    ],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered actual physical harm or property damage",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "property damage photos",
                        "economic loss",
                    ],
                ),
            ],
            defenses=[
                DefenseType.ASSUMPTION_OF_RISK,
                DefenseType.COMPARATIVE_NEGLIGENCE,
                DefenseType.STATUTE_OF_LIMITATIONS,
            ],
            damages_available=[
                "compensatory damages",
                "medical expenses",
                "lost wages",
                "pain and suffering",
                "punitive damages (if egregious)",
                "property damage",
            ],
            statute_of_limitations_years={
                "federal": 2,
                "california": 2,
                "new_york": 3,
                "texas": 2,
                "florida": 4,
                "default": 2,
            },
            notes="Applies to commercial sellers. Three types: manufacturing defect, design defect, failure to warn.",
            landmark_cases=[
                "Greenman v. Yuba Power Products, 59 Cal. 2d 57 (1963)",
                "MacPherson v. Buick Motor Co., 217 N.Y. 382 (1916)",
                "Escola v. Coca Cola Bottling Co., 24 Cal. 2d 453 (1944)",
            ],
            restatement_sections=[
                "Restatement (Third) of Torts: Products Liability § 1",
                "§ 2",
                "§ 3",
            ],
        )

        # ===================== FRAUD/MISREPRESENTATION =====================
        database["fraud"] = TortDefinition(
            tort_name="Fraud / Fraudulent Misrepresentation",
            category=TortCategory.ECONOMIC,
            subcategory=EconomicTort.FRAUDULENT_MISREPRESENTATION,
            elements=[
                TortElement(
                    element_name="False Representation",
                    description="Defendant made false representation of material fact",
                    required=True,
                    proof_standard="clear_and_convincing",
                    typical_evidence=[
                        "statements",
                        "documents",
                        "communications",
                        "expert testimony",
                    ],
                ),
                TortElement(
                    element_name="Knowledge of Falsity (Scienter)",
                    description="Defendant knew statement was false or acted with reckless disregard",
                    required=True,
                    proof_standard="clear_and_convincing",
                    typical_evidence=[
                        "internal documents",
                        "prior knowledge",
                        "investigation",
                    ],
                ),
                TortElement(
                    element_name="Intent to Induce Reliance",
                    description="Defendant intended plaintiff to rely on statement",
                    required=True,
                    proof_standard="clear_and_convincing",
                    typical_evidence=["context", "targeting", "relationship"],
                ),
                TortElement(
                    element_name="Justifiable Reliance",
                    description="Plaintiff justifiably relied on the false statement",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "actions taken",
                        "due diligence",
                        "expertise level",
                    ],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered pecuniary loss from reliance",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "financial records",
                        "contracts",
                        "economic loss calculations",
                    ],
                ),
            ],
            defenses=[DefenseType.STATUTE_OF_LIMITATIONS, DefenseType.CONSENT],
            damages_available=[
                "actual damages (out-of-pocket loss)",
                "benefit-of-bargain damages",
                "consequential damages",
                "punitive damages",
                "attorney fees (if statutory fraud)",
            ],
            statute_of_limitations_years={
                "federal": 3,
                "california": 3,
                "new_york": 6,
                "texas": 4,
                "florida": 4,
                "default": 3,
            },
            notes="Higher burden of proof (clear and convincing). Reliance must be reasonable.",
            landmark_cases=[
                "Derry v. Peek, 14 App. Cas. 337 (1889)",
                "Pasley v. Freeman, 3 T.R. 51 (1789)",
                "Alliance Mortgage Co. v. Rothwell, 10 Cal. 4th 1226 (1995)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 525",
                "§ 526",
                "§ 531",
                "§ 537",
            ],
        )

        # ===================== PRIVACY TORTS =====================
        database["intrusion_upon_seclusion"] = TortDefinition(
            tort_name="Intrusion Upon Seclusion",
            category=TortCategory.PRIVACY,
            subcategory=PrivacyTort.INTRUSION_UPON_SECLUSION,
            elements=[
                TortElement(
                    element_name="Intentional Intrusion",
                    description="Defendant intentionally intruded upon plaintiff's solitude or private affairs",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "surveillance records",
                        "unauthorized access logs",
                        "witness testimony",
                    ],
                ),
                TortElement(
                    element_name="Highly Offensive to Reasonable Person",
                    description="Intrusion would be highly offensive to reasonable person",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "expert testimony",
                        "community standards",
                        "nature of intrusion",
                    ],
                ),
                TortElement(
                    element_name="Private Matter",
                    description="Intrusion was into something private",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "nature of information",
                        "expectation of privacy",
                        "location",
                    ],
                ),
            ],
            defenses=[DefenseType.CONSENT, DefenseType.CONSENT_TO_MONITORING],
            damages_available=[
                "emotional distress",
                "nominal damages",
                "punitive damages",
            ],
            statute_of_limitations_years={"default": 2, "california": 2, "new_york": 1},
            notes="No publication required; intrusion itself is tort. Examples: wiretapping, peeping, unauthorized medical examination.",
            landmark_cases=[
                "Hamberger v. Eastman, 106 N.H. 107 (1964)",
                "Nader v. General Motors Corp., 25 N.Y.2d 560 (1970)",
            ],
            restatement_sections=["Restatement (Second) of Torts § 652B"],
        )

        database["public_disclosure"] = TortDefinition(
            tort_name="Public Disclosure of Private Facts",
            category=TortCategory.PRIVACY,
            subcategory=PrivacyTort.PUBLIC_DISCLOSURE_PRIVATE_FACTS,
            elements=[
                TortElement(
                    element_name="Public Disclosure",
                    description="Defendant publicly disclosed information",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["publication", "media coverage", "audience size"],
                ),
                TortElement(
                    element_name="Private Fact",
                    description="Information was private, not public record",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["nature of information", "prior confidentiality"],
                ),
                TortElement(
                    element_name="Highly Offensive",
                    description="Disclosure highly offensive to reasonable person",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["community standards", "nature of information"],
                ),
                TortElement(
                    element_name="Not Newsworthy",
                    description="Information not of legitimate public concern",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["newsworthiness analysis", "public interest"],
                ),
            ],
            defenses=[DefenseType.CONSENT, DefenseType.NEWSWORTHINESS],
            damages_available=[
                "emotional distress",
                "reputational harm",
                "punitive damages",
            ],
            statute_of_limitations_years={"default": 2, "california": 2},
            notes="Truth is NOT a defense. Newsworthiness is major defense. First Amendment limits this tort.",
            landmark_cases=[
                "Cox Broadcasting Corp. v. Cohn, 420 U.S. 469 (1975)",
                "Sidis v. F-R Publishing Corp., 113 F.2d 806 (2d Cir. 1940)",
            ],
            restatement_sections=["Restatement (Second) of Torts § 652D"],
        )

        # ===================== NUISANCE =====================
        database["private_nuisance"] = TortDefinition(
            tort_name="Private Nuisance",
            category=TortCategory.NUISANCE,
            subcategory=NuisanceTort.PRIVATE_NUISANCE,
            elements=[
                TortElement(
                    element_name="Substantial Interference",
                    description="Defendant's activity substantially interfered with use and enjoyment of land",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "property value decline",
                        "inability to use property",
                        "frequency of interference",
                    ],
                ),
                TortElement(
                    element_name="Unreasonable Interference",
                    description="Interference was unreasonable (harm > utility)",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "balancing test",
                        "character of neighborhood",
                        "social value",
                    ],
                ),
                TortElement(
                    element_name="Plaintiff Property Interest",
                    description="Plaintiff has property interest (owner, tenant, etc.)",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["deed", "lease", "possessory interest"],
                ),
            ],
            defenses=[
                DefenseType.COMING_TO_NUISANCE,
                DefenseType.REGULATORY_COMPLIANCE,
            ],
            damages_available=[
                "property damage",
                "diminution in value",
                "injunctive relief",
            ],
            statute_of_limitations_years={"default": 3, "california": 3, "new_york": 3},
            notes="Balancing test: gravity of harm vs. utility of conduct. Injunction or damages available.",
            landmark_cases=[
                "Boomer v. Atlantic Cement Co., 26 N.Y.2d 219 (1970)",
                "Spur Industries v. Del E. Webb Dev. Co., 108 Ariz. 178 (1972)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 822",
                "§ 826",
                "§ 829",
            ],
        )

        # ===================== EMPLOYMENT TORTS =====================
        database["wrongful_termination"] = TortDefinition(
            tort_name="Wrongful Termination in Violation of Public Policy",
            category=TortCategory.EMPLOYMENT,
            subcategory=EmploymentTort.WRONGFUL_TERMINATION,
            elements=[
                TortElement(
                    element_name="Termination",
                    description="Employer terminated employee",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "termination letter",
                        "final paycheck",
                        "exit interview",
                    ],
                ),
                TortElement(
                    element_name="Violation of Public Policy",
                    description="Termination violated clear public policy",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "statute",
                        "constitutional provision",
                        "whistleblower protection",
                    ],
                ),
                TortElement(
                    element_name="Causation",
                    description="Public policy violation motivated termination",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "timing",
                        "employer statements",
                        "pretextual reasons",
                    ],
                ),
            ],
            defenses=[
                DefenseType.AT_WILL_EMPLOYMENT,
                DefenseType.LEGITIMATE_BUSINESS_REASON,
            ],
            damages_available=[
                "lost wages",
                "emotional distress",
                "punitive damages",
                "reinstatement",
            ],
            statute_of_limitations_years={"default": 2, "california": 2, "new_york": 3},
            notes="Exception to at-will employment. Public policy must be clearly established. Applies to refusal to violate law, whistleblowing, jury duty, etc.",
            landmark_cases=[
                "Tameny v. Atlantic Richfield Co., 27 Cal. 3d 167 (1980)",
                "Petermann v. International Brotherhood of Teamsters, 174 Cal. App. 2d 184 (1959)",
            ],
            restatement_sections=["Restatement (Third) of Employment Law § 4.01"],
        )

        database["negligent_hiring"] = TortDefinition(
            tort_name="Negligent Hiring",
            category=TortCategory.EMPLOYMENT,
            subcategory=EmploymentTort.WRONGFUL_TERMINATION,
            elements=[
                TortElement(
                    element_name="Employment Relationship",
                    description="Defendant employed the tortfeasor",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["employment records", "W-2", "payroll"],
                ),
                TortElement(
                    element_name="Incompetence or Unfitness",
                    description="Employee was incompetent or unfit for position",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "criminal record",
                        "prior incidents",
                        "lack of qualifications",
                    ],
                ),
                TortElement(
                    element_name="Employer Knew or Should Have Known",
                    description="Employer knew or should have known of unfitness",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "background check failure",
                        "warning signs",
                        "industry standards",
                    ],
                ),
                TortElement(
                    element_name="Causation and Harm",
                    description="Unfitness caused plaintiff's injuries",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "incident report",
                        "medical records",
                        "nexus to job",
                    ],
                ),
            ],
            defenses=[
                DefenseType.REASONABLE_INVESTIGATION,
                DefenseType.SUPERSEDING_CAUSE,
            ],
            damages_available=[
                "compensatory damages",
                "emotional distress",
                "punitive damages",
            ],
            statute_of_limitations_years={"default": 2, "california": 2},
            notes="Employer liable for failing to exercise reasonable care in hiring. Often alleged with negligent supervision/retention.",
            landmark_cases=[
                "Ponticas v. K.M.S. Investments, 331 N.W.2d 907 (Minn. 1983)",
                "Malorney v. B&L Motor Freight, Inc., 146 Ill. App. 3d 265 (1986)",
            ],
            restatement_sections=["Restatement (Second) of Agency § 213"],
        )

        # ===================== HEALTHCARE TORTS =====================
        database["lack_informed_consent"] = TortDefinition(
            tort_name="Lack of Informed Consent",
            category=TortCategory.HEALTHCARE,
            subcategory=HealthcareTort.LACK_OF_INFORMED_CONSENT,
            elements=[
                TortElement(
                    element_name="Medical Procedure",
                    description="Healthcare provider performed medical procedure",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical records",
                        "procedure notes",
                        "billing codes",
                    ],
                ),
                TortElement(
                    element_name="Lack of Informed Consent",
                    description="Patient did not give informed consent",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "absence of consent form",
                        "inadequate disclosure",
                    ],
                ),
                TortElement(
                    element_name="Undisclosed Risk Materialized",
                    description="Risk that should have been disclosed occurred",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "medical literature",
                        "expert testimony on disclosure standards",
                    ],
                ),
                TortElement(
                    element_name="Causation",
                    description="Reasonable patient would have declined if properly informed",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "patient testimony",
                        "reasonable person standard",
                    ],
                ),
            ],
            defenses=[
                DefenseType.EMERGENCY_DOCTRINE,
                DefenseType.THERAPEUTIC_PRIVILEGE,
            ],
            damages_available=["medical expenses", "pain and suffering", "lost wages"],
            statute_of_limitations_years={
                "default": 2,
                "california": 1,
                "new_york": 2.5,
            },
            notes="Must disclose nature, risks, alternatives, consequences. Either reasonable physician or reasonable patient standard depending on jurisdiction.",
            landmark_cases=[
                "Canterbury v. Spence, 464 F.2d 772 (D.C. Cir. 1972)",
                "Cobbs v. Grant, 8 Cal. 3d 229 (1972)",
            ],
            restatement_sections=[
                "Restatement (Third) of Torts: Liability for Physical and Emotional Harm § 15"
            ],
        )

        # ===================== TECHNOLOGY TORTS =====================
        database["data_breach_negligence"] = TortDefinition(
            tort_name="Data Breach Negligence",
            category=TortCategory.TECHNOLOGY,
            subcategory=TechnologyTort.DATA_BREACH,
            elements=[
                TortElement(
                    element_name="Duty to Protect Data",
                    description="Defendant owed duty to protect plaintiff's personal data",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "privacy policy",
                        "terms of service",
                        "industry standards",
                        "statutes",
                    ],
                ),
                TortElement(
                    element_name="Breach of Duty",
                    description="Defendant failed to implement reasonable security measures",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "expert testimony",
                        "cybersecurity standards",
                        "FTC guidelines",
                    ],
                ),
                TortElement(
                    element_name="Data Breach Occurred",
                    description="Unauthorized access, disclosure, or acquisition of data",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "breach notice",
                        "forensic report",
                        "dark web monitoring",
                    ],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered actual harm (identity theft, fraud, etc.)",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "fraudulent charges",
                        "credit monitoring costs",
                        "time spent remediation",
                    ],
                ),
            ],
            defenses=[DefenseType.REGULATORY_COMPLIANCE, DefenseType.SUPERSEDING_CAUSE],
            damages_available=[
                "actual damages",
                "credit monitoring costs",
                "time value",
                "statutory damages if applicable",
            ],
            statute_of_limitations_years={"default": 2, "california": 2, "new_york": 3},
            notes="Standing requires concrete harm, not just increased risk. State data breach statutes may provide additional remedies.",
            landmark_cases=[
                "In re Target Corp. Data Breach Litig., 66 F. Supp. 3d 1154 (D. Minn. 2014)",
                "Spokeo, Inc. v. Robins, 578 U.S. 330 (2016)",
            ],
            restatement_sections=["Emerging area; no Restatement section yet"],
        )

        database["platform_negligence"] = TortDefinition(
            tort_name="Platform Negligence / Failure to Moderate",
            category=TortCategory.TECHNOLOGY,
            subcategory=TechnologyTort.PLATFORM_NEGLIGENCE,
            elements=[
                TortElement(
                    element_name="Platform Control",
                    description="Defendant operated online platform or service",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "terms of service",
                        "user agreement",
                        "platform ownership",
                    ],
                ),
                TortElement(
                    element_name="Duty to Moderate",
                    description="Platform undertook duty to moderate content or protect users",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "community guidelines",
                        "safety promises",
                        "moderation policies",
                    ],
                ),
                TortElement(
                    element_name="Breach of Duty",
                    description="Platform failed to exercise reasonable care in moderation",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "failed reports",
                        "inadequate response",
                        "pattern of abuse",
                    ],
                ),
                TortElement(
                    element_name="Harm",
                    description="Plaintiff suffered harm from third-party content/conduct",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "harassment evidence",
                        "threats",
                        "emotional distress",
                        "physical harm",
                    ],
                ),
            ],
            defenses=[DefenseType.SECTION_230_IMMUNITY, DefenseType.NO_DUTY_TO_MONITOR],
            damages_available=[
                "emotional distress",
                "reputational harm",
                "medical expenses",
                "lost wages",
            ],
            statute_of_limitations_years={"default": 2},
            notes="Section 230 of CDA provides broad immunity for platforms. Exceptions: federal criminal law, IP, state law if platform is 'information content provider.'",
            landmark_cases=[
                "Zeran v. America Online, Inc., 129 F.3d 327 (4th Cir. 1997)",
                "Fair Housing Council v. Roommates.com, 521 F.3d 1157 (9th Cir. 2008)",
            ],
            restatement_sections=["47 U.S.C. § 230 (Communications Decency Act)"],
        )

        # ===================== INTELLECTUAL PROPERTY TORTS =====================
        database["trade_secret_misappropriation"] = TortDefinition(
            tort_name="Trade Secret Misappropriation",
            category=TortCategory.INTELLECTUAL_PROPERTY,
            subcategory=IntellectualPropertyTort.TRADE_SECRET_MISAPPROPRIATION,
            elements=[
                TortElement(
                    element_name="Trade Secret Exists",
                    description="Information qualifies as trade secret under UTSA/DTSA",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "secrecy measures",
                        "economic value",
                        "not generally known",
                    ],
                ),
                TortElement(
                    element_name="Misappropriation",
                    description="Defendant acquired, disclosed, or used trade secret improperly",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "acquisition circumstances",
                        "breach of confidence",
                        "improper means",
                    ],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered economic harm",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "lost profits",
                        "unjust enrichment",
                        "reasonable royalty",
                    ],
                ),
            ],
            defenses=[
                DefenseType.INDEPENDENT_DERIVATION,
                DefenseType.REVERSE_ENGINEERING,
                DefenseType.PUBLIC_DOMAIN,
            ],
            damages_available=[
                "actual damages",
                "unjust enrichment",
                "reasonable royalty",
                "punitive damages if willful",
                "injunctive relief",
            ],
            statute_of_limitations_years={
                "default": 3,
                "federal_dtsa": 3,
                "california": 3,
            },
            notes="Uniform Trade Secrets Act adopted by most states. Federal Defend Trade Secrets Act (2016) provides federal cause of action.",
            landmark_cases=[
                "E.I. duPont deNemours & Co. v. Christopher, 431 F.2d 1012 (5th Cir. 1970)",
                "PepsiCo, Inc. v. Redmond, 54 F.3d 1262 (7th Cir. 1995)",
            ],
            restatement_sections=[
                "Uniform Trade Secrets Act § 1-3",
                "18 U.S.C. § 1836 (DTSA)",
            ],
        )

        # ===================== MALICIOUS PROSECUTION =====================
        database["malicious_prosecution"] = TortDefinition(
            tort_name="Malicious Prosecution",
            category=TortCategory.INTENTIONAL,
            subcategory=IntentionalTort.MALICIOUS_PROSECUTION,
            elements=[
                TortElement(
                    element_name="Prior Proceeding",
                    description="Defendant initiated prior criminal or civil proceeding",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=["complaint", "criminal charge", "court records"],
                ),
                TortElement(
                    element_name="Favorable Termination",
                    description="Prior proceeding terminated in plaintiff's favor",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "dismissal order",
                        "acquittal",
                        "judgment for plaintiff",
                    ],
                ),
                TortElement(
                    element_name="Lack of Probable Cause",
                    description="Defendant lacked probable cause to initiate proceeding",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "absence of evidence",
                        "fabricated claims",
                        "legal analysis",
                    ],
                ),
                TortElement(
                    element_name="Malice",
                    description="Defendant acted with malice or improper purpose",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "ulterior motive",
                        "harassment",
                        "personal vendetta",
                    ],
                ),
                TortElement(
                    element_name="Damages",
                    description="Plaintiff suffered damages from proceeding",
                    required=True,
                    proof_standard="preponderance",
                    typical_evidence=[
                        "legal fees",
                        "reputational harm",
                        "emotional distress",
                        "lost income",
                    ],
                ),
            ],
            defenses=[
                DefenseType.PROBABLE_CAUSE,
                DefenseType.ADVICE_OF_COUNSEL,
                DefenseType.ABSOLUTE_PRIVILEGE,
            ],
            damages_available=[
                "compensatory damages",
                "legal fees",
                "emotional distress",
                "reputational harm",
                "punitive damages",
            ],
            statute_of_limitations_years={"default": 2, "california": 2, "new_york": 1},
            notes="High bar to meet. Absolute privilege for prosecutors. Favorable termination must be 'on the merits' in some jurisdictions.",
            landmark_cases=[
                "Heck v. Humphrey, 512 U.S. 477 (1994)",
                "Sheldon Appel Co. v. Albert & Oliker, 47 Cal. 3d 863 (1989)",
            ],
            restatement_sections=[
                "Restatement (Second) of Torts § 653",
                "§ 654",
                "§ 674",
            ],
        )

        return database

    def get_tort_definition(self, tort_name: str) -> Optional[TortDefinition]:
        """Retrieve complete tort definition"""
        return self.torts_database.get(tort_name.lower())

    def search_torts_by_category(self, category: TortCategory) -> List[TortDefinition]:
        """Find all torts in a specific category"""
        return [
            tort for tort in self.torts_database.values() if tort.category == category
        ]

    def find_applicable_torts(self, fact_pattern: Dict[str, any]) -> List[str]:
        """
        Analyze fact pattern and identify potentially applicable torts.

        Args:
            fact_pattern: Dictionary with keys like 'intentional', 'physical_harm',
                         'property_damage', 'economic_loss', 'reputation_harm', etc.

        Returns:
            List of tort names that may apply
        """
        applicable = []

        # Intentional physical harm
        if fact_pattern.get("intentional") and fact_pattern.get("physical_contact"):
            applicable.extend(["battery", "assault"])

        # Confinement
        if fact_pattern.get("intentional") and fact_pattern.get("confined"):
            applicable.append("false_imprisonment")

        # Emotional distress
        if fact_pattern.get("emotional_distress"):
            if fact_pattern.get("intentional") and fact_pattern.get(
                "outrageous_conduct"
            ):
                applicable.append("iied")
            elif fact_pattern.get("negligent"):
                applicable.append("negligence")  # for NIED

        # Reputation harm
        if fact_pattern.get("reputation_harm") and fact_pattern.get("false_statement"):
            applicable.append("defamation")

        # Negligence
        if fact_pattern.get("negligent") and fact_pattern.get("duty_of_care"):
            applicable.append("negligence")

        # Products
        if fact_pattern.get("defective_product"):
            applicable.append("products_liability")

        # Economic/fraud
        if fact_pattern.get("false_representation") and fact_pattern.get(
            "economic_loss"
        ):
            applicable.append("fraud")

        return applicable

    def get_statute_of_limitations(
        self, tort_name: str, jurisdiction: str = "default"
    ) -> Optional[int]:
        """Get statute of limitations for tort in specific jurisdiction"""
        tort_def = self.get_tort_definition(tort_name)
        if tort_def:
            return tort_def.statute_of_limitations_years.get(
                jurisdiction.lower(),
                tort_def.statute_of_limitations_years.get("default"),
            )
        return None

    def check_elements_met(
        self, tort_name: str, elements_present: Set[str]
    ) -> Dict[str, any]:
        """
        Check if all required elements of a tort are satisfied.

        Args:
            tort_name: Name of the tort
            elements_present: Set of element names that are satisfied

        Returns:
            Dictionary with analysis results
        """
        tort_def = self.get_tort_definition(tort_name)
        if not tort_def:
            return {"error": "Tort not found"}

        required_elements = [e for e in tort_def.elements if e.required]
        met_elements = []
        missing_elements = []

        for element in required_elements:
            if element.element_name.lower() in [e.lower() for e in elements_present]:
                met_elements.append(element.element_name)
            else:
                missing_elements.append(element.element_name)

        prima_facie_case = len(missing_elements) == 0

        return {
            "tort_name": tort_def.tort_name,
            "prima_facie_case_established": prima_facie_case,
            "required_elements_count": len(required_elements),
            "met_elements": met_elements,
            "missing_elements": missing_elements,
            "percentage_complete": (
                (len(met_elements) / len(required_elements) * 100)
                if required_elements
                else 0
            ),
        }


# ===================== MYTHARA INTEGRATION =====================


class TortsCovenantIntegrity:
    """
    Integrate torts law with Mythara's covenant integrity framework.
    Maps legal violations to covenant breaches.
    """

    def __init__(self):
        self.torts_index = TortsLawIndex()

    def assess_covenant_breach_legal_exposure(
        self, action: str, context: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Assess whether a covenant breach creates tort liability.

        Example: User "abuse" prevention → False imprisonment risk?
                 Emotional manipulation detection → Defamation risk?
        """

        # Map Mythara actions to potential torts
        risk_mapping = {
            "account_termination": ["false_imprisonment", "breach_of_contract"],
            "reputation_scoring": ["defamation", "invasion_of_privacy"],
            "emotional_assessment": ["invasion_of_privacy", "iied"],
            "data_retention": ["invasion_of_privacy"],
            "communication_blocking": ["interference_with_contract"],
        }

        potential_torts = risk_mapping.get(action, [])

        analysis = {
            "action": action,
            "potential_tort_exposure": [],
            "risk_level": "low",
            "recommended_safeguards": [],
        }

        for tort_name in potential_torts:
            tort_def = self.torts_index.get_tort_definition(tort_name)
            if tort_def:
                analysis["potential_tort_exposure"].append(
                    {
                        "tort": tort_def.tort_name,
                        "category": tort_def.category.value,
                        "elements_to_avoid": [
                            e.element_name for e in tort_def.elements[:2]
                        ],
                        "available_defenses": [d.value for d in tort_def.defenses],
                    }
                )

        # Assess risk level
        if len(analysis["potential_tort_exposure"]) > 2:
            analysis["risk_level"] = "high"
        elif len(analysis["potential_tort_exposure"]) > 0:
            analysis["risk_level"] = "medium"

        # Generate safeguards
        if "defamation" in potential_torts:
            analysis["recommended_safeguards"].append(
                "Verify factual accuracy before publishing reputation scores"
            )
            analysis["recommended_safeguards"].append(
                "Allow user dispute/correction process"
            )

        if "false_imprisonment" in potential_torts:
            analysis["recommended_safeguards"].append(
                "Ensure termination doesn't prevent access to user's own data"
            )
            analysis["recommended_safeguards"].append("Provide clear exit mechanisms")

        if "invasion_of_privacy" in potential_torts:
            analysis["recommended_safeguards"].append(
                "Obtain explicit consent for emotional/behavioral tracking"
            )
            analysis["recommended_safeguards"].append(
                "Allow opt-out of profiling features"
            )

        return analysis

    def generate_liability_report(self, mythara_action: str) -> str:
        """Generate human-readable liability report for Mythara action"""
        analysis = self.assess_covenant_breach_legal_exposure(mythara_action, {})

        report = f"# Tort Liability Analysis: {mythara_action}\n\n"
        report += f"**Risk Level:** {analysis['risk_level'].upper()}\n\n"

        if analysis["potential_tort_exposure"]:
            report += "## Potential Tort Claims\n\n"
            for tort_info in analysis["potential_tort_exposure"]:
                report += f"### {tort_info['tort']} ({tort_info['category']})\n"
                report += "**Key Elements to Avoid:**\n"
                for element in tort_info["elements_to_avoid"]:
                    report += f"- {element}\n"
                report += "\n**Available Defenses:**\n"
                for defense in tort_info["available_defenses"]:
                    report += f"- {defense.replace('_', ' ').title()}\n"
                report += "\n"

        if analysis["recommended_safeguards"]:
            report += "## Recommended Safeguards\n\n"
            for i, safeguard in enumerate(analysis["recommended_safeguards"], 1):
                report += f"{i}. {safeguard}\n"

        return report


# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    # Initialize torts index
    torts = TortsLawIndex()

    # Example 1: Get battery definition
    battery = torts.get_tort_definition("battery")
    print(f"=== {battery.tort_name} ===")
    print(f"Category: {battery.category.value}")
    print("\nElements:")
    for element in battery.elements:
        print(f"  - {element.element_name}: {element.description}")
    print("\nLandmark Cases:")
    for case in battery.landmark_cases:
        print(f"  - {case}")

    # Example 2: Find applicable torts
    print("\n\n=== Tort Analysis ===")
    fact_pattern = {
        "intentional": True,
        "physical_contact": True,
        "emotional_distress": True,
    }
    applicable_torts = torts.find_applicable_torts(fact_pattern)
    print(f"Applicable torts: {applicable_torts}")

    # Example 3: Check elements
    print("\n\n=== Elements Check ===")
    elements_check = torts.check_elements_met(
        "battery", {"Intent", "Harmful or Offensive Contact", "Causation"}
    )
    print(f"Prima facie case: {elements_check['prima_facie_case_established']}")
    print(f"Missing elements: {elements_check['missing_elements']}")

    # Example 4: Mythara integration
    print("\n\n=== Mythara Covenant Integrity Analysis ===")
    covenant_integrity = TortsCovenantIntegrity()
    report = covenant_integrity.generate_liability_report("account_termination")
    print(report)
