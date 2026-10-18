"""
Mythara Engine - Legal Resources Index
Comprehensive legal knowledge base for covenant integrity system.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

# ===================== LEGAL PRINCIPLES TAXONOMY =====================


class LegalDomain(Enum):
    """Major domains of law"""

    TORTS = "torts"
    CONTRACTS = "contracts"
    CONSTITUTIONAL = "constitutional"
    CRIMINAL = "criminal"
    PROPERTY = "property"
    EVIDENCE = "evidence"
    PROCEDURE = "procedure"
    ADMINISTRATIVE = "administrative"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    PRIVACY = "privacy"


class EvidenceRule(Enum):
    """Federal Rules of Evidence (public domain)"""

    # Relevance
    RELEVANCE_401 = "Evidence is relevant if it makes fact more/less probable"
    RELEVANCE_403 = "Court may exclude if prejudicial effect outweighs probative value"

    # Hearsay
    HEARSAY_801 = "Hearsay is out-of-court statement offered for truth"
    HEARSAY_802 = "Hearsay generally inadmissible unless exception applies"
    HEARSAY_803_PRESENT_SENSE = "Present sense impression exception"
    HEARSAY_803_EXCITED_UTTERANCE = "Excited utterance exception"
    HEARSAY_803_BUSINESS_RECORDS = "Business records exception"
    HEARSAY_804_FORMER_TESTIMONY = "Former testimony when declarant unavailable"
    HEARSAY_807_RESIDUAL = "Residual exception for trustworthy statements"

    # Privileges
    PRIVILEGE_501 = "Privileges governed by common law"
    ATTORNEY_CLIENT = "Attorney-client privilege protects confidential communications"
    SPOUSAL = "Spousal testimonial privilege and confidential communications"

    # Expert Testimony
    EXPERT_702 = "Expert may testify if knowledge helps trier of fact"
    EXPERT_703 = (
        "Expert may base opinion on inadmissible facts if reasonably relied upon"
    )
    DAUBERT_STANDARD = "Expert testimony must be reliable and relevant"

    # Authentication
    AUTHENTICATION_901 = "Evidence must be authenticated before admission"
    SELF_AUTHENTICATION_902 = "Certain documents self-authenticating"


class ConstitutionalPrinciple(Enum):
    """Key constitutional principles (US Constitution - public domain)"""

    # First Amendment
    FREE_SPEECH = "Congress shall make no law abridging freedom of speech"
    FREE_PRESS = "Freedom of the press protected"
    FREE_EXERCISE = "Free exercise of religion"
    ESTABLISHMENT = "No establishment of religion"

    # Fourth Amendment
    SEARCH_SEIZURE = "Protection against unreasonable search and seizure"
    WARRANT_REQUIREMENT = "Warrants require probable cause"

    # Fifth Amendment
    SELF_INCRIMINATION = "No person compelled to be witness against himself"
    DOUBLE_JEOPARDY = "No person tried twice for same offense"
    DUE_PROCESS_FEDERAL = (
        "No deprivation of life, liberty, property without due process"
    )
    TAKINGS = "Private property shall not be taken without just compensation"

    # Fourteenth Amendment
    DUE_PROCESS_STATE = "States shall not deprive due process"
    EQUAL_PROTECTION = "No state shall deny equal protection of laws"

    # Commerce Clause
    COMMERCE_CLAUSE = "Congress may regulate interstate commerce"
    DORMANT_COMMERCE = "States may not discriminate against interstate commerce"


class ContractDoctrine(Enum):
    """Key contract law principles"""

    # Formation
    OFFER = "Manifestation of willingness to enter bargain"
    ACCEPTANCE = "Manifestation of assent to terms of offer"
    CONSIDERATION = "Bargained-for exchange of legal value"
    MUTUAL_ASSENT = "Meeting of the minds required"

    # Defenses to Formation
    STATUTE_OF_FRAUDS = "Certain contracts must be in writing"
    CAPACITY = "Parties must have legal capacity to contract"
    DURESS = "Contract voidable if procured by improper threat"
    UNDUE_INFLUENCE = "Contract voidable if unfair persuasion"
    MISTAKE = "Mutual mistake may void contract"
    MISREPRESENTATION = "False statement of material fact may void"

    # Performance and Breach
    PERFECT_TENDER = "Seller must deliver goods conforming in every respect (UCC)"
    SUBSTANTIAL_PERFORMANCE = "Nearly complete performance excuses minor defects"
    MATERIAL_BREACH = "Significant breach excuses other party's performance"
    ANTICIPATORY_REPUDIATION = "Clear statement of non-performance before due"

    # Remedies
    EXPECTATION_DAMAGES = "Put plaintiff in position if contract performed"
    RELIANCE_DAMAGES = "Reimburse costs incurred in reliance"
    RESTITUTION = "Return benefit conferred to prevent unjust enrichment"
    SPECIFIC_PERFORMANCE = "Court orders actual performance (rare)"
    LIQUIDATED_DAMAGES = "Pre-agreed damages if reasonable"

    # Third Parties
    THIRD_PARTY_BENEFICIARY = "Non-party may enforce if intended beneficiary"
    ASSIGNMENT = "Transfer of contractual rights"
    DELEGATION = "Transfer of contractual duties"


# ===================== LEGAL MAXIMS & PRINCIPLES =====================


@dataclass
class LegalMaxim:
    """Traditional legal maxim or principle"""

    latin: str
    english: str
    domain: LegalDomain
    explanation: str
    application: str


class LegalMaximsIndex:
    """Collection of fundamental legal maxims"""

    @staticmethod
    def get_maxims() -> List[LegalMaxim]:
        return [
            LegalMaxim(
                latin="Actus reus non facit reum nisi mens sit rea",
                english="The act is not guilty unless the mind is guilty",
                domain=LegalDomain.CRIMINAL,
                explanation="Criminal liability requires both wrongful act and criminal intent",
                application="Defense: acted without intent or knowledge",
            ),
            LegalMaxim(
                latin="Caveat emptor",
                english="Let the buyer beware",
                domain=LegalDomain.CONTRACTS,
                explanation="Buyer bears risk unless seller makes express warranties",
                application="Limits implied warranties; buyer must inspect",
            ),
            LegalMaxim(
                latin="Res ipsa loquitur",
                english="The thing speaks for itself",
                domain=LegalDomain.TORTS,
                explanation="Negligence inferred when accident wouldn't normally occur without negligence",
                application="Barrel falls from warehouse; surgical instrument left in patient",
            ),
            LegalMaxim(
                latin="Volenti non fit injuria",
                english="To one who consents, no harm is done",
                domain=LegalDomain.TORTS,
                explanation="Assumption of risk defense; plaintiff consented to danger",
                application="Contact sports; dangerous recreational activities",
            ),
            LegalMaxim(
                latin="De minimis non curat lex",
                english="The law does not concern itself with trifles",
                domain=LegalDomain.PROCEDURE,
                explanation="Courts won't hear cases involving trivial matters",
                application="Dismissal for lack of substantial controversy",
            ),
            LegalMaxim(
                latin="Nemo dat quod non habet",
                english="No one can give what they do not have",
                domain=LegalDomain.PROPERTY,
                explanation="Cannot transfer better title than you possess",
                application="Stolen goods; fraudulent transfers",
            ),
            LegalMaxim(
                latin="Uberrima fides",
                english="Utmost good faith",
                domain=LegalDomain.CONTRACTS,
                explanation="Parties must deal with utmost honesty (insurance contracts)",
                application="Insurance applicant must disclose all material facts",
            ),
            LegalMaxim(
                latin="Stare decisis",
                english="To stand by things decided",
                domain=LegalDomain.PROCEDURE,
                explanation="Courts follow precedent from prior decisions",
                application="Predictability; consistency in law",
            ),
            LegalMaxim(
                latin="Qui facit per alium facit per se",
                english="He who acts through another acts himself",
                domain=LegalDomain.TORTS,
                explanation="Principal liable for agent's acts within scope of authority",
                application="Respondeat superior; vicarious liability",
            ),
            LegalMaxim(
                latin="Ex post facto",
                english="From a thing done afterward",
                domain=LegalDomain.CONSTITUTIONAL,
                explanation="Retroactive criminal laws prohibited",
                application="Cannot punish acts legal when committed",
            ),
            LegalMaxim(
                latin="Habeas corpus",
                english="You shall have the body",
                domain=LegalDomain.CONSTITUTIONAL,
                explanation="Writ requiring government to justify detention",
                application="Challenge unlawful imprisonment",
            ),
            LegalMaxim(
                latin="Lex loci",
                english="Law of the place",
                domain=LegalDomain.PROCEDURE,
                explanation="Law of jurisdiction where event occurred applies",
                application="Choice of law; conflicts of law",
            ),
            LegalMaxim(
                latin="Prima facie",
                english="At first sight / on its face",
                domain=LegalDomain.EVIDENCE,
                explanation="Evidence sufficient to establish fact unless rebutted",
                application="Prima facie case shifts burden to defendant",
            ),
            LegalMaxim(
                latin="Quantum meruit",
                english="As much as he deserved",
                domain=LegalDomain.CONTRACTS,
                explanation="Reasonable value of services rendered",
                application="Recovery when no contract but unjust enrichment",
            ),
            LegalMaxim(
                latin="Respondeat superior",
                english="Let the superior answer",
                domain=LegalDomain.TORTS,
                explanation="Employer liable for employee's torts in scope of employment",
                application="Vicarious liability; master-servant relationship",
            ),
        ]


# ===================== CASE LAW PRINCIPLES =====================


@dataclass
class LandmarkCase:
    """Major case establishing legal principle"""

    case_name: str
    citation: str
    year: int
    court: str
    domain: LegalDomain
    holding: str
    principle: str
    modern_application: str


class LandmarkCasesIndex:
    """Index of major precedent-setting cases (public domain)"""

    @staticmethod
    def get_landmark_cases() -> List[LandmarkCase]:
        return [
            # Constitutional Law
            LandmarkCase(
                case_name="Marbury v. Madison",
                citation="5 U.S. 137",
                year=1803,
                court="U.S. Supreme Court",
                domain=LegalDomain.CONSTITUTIONAL,
                holding="Supreme Court has power to review acts of Congress",
                principle="Judicial review",
                modern_application="Foundation of constitutional judicial review",
            ),
            LandmarkCase(
                case_name="Brown v. Board of Education",
                citation="347 U.S. 483",
                year=1954,
                court="U.S. Supreme Court",
                domain=LegalDomain.CONSTITUTIONAL,
                holding="Separate educational facilities inherently unequal",
                principle="Equal protection; racial segregation unconstitutional",
                modern_application="Foundation of civil rights law; strict scrutiny for racial classifications",
            ),
            LandmarkCase(
                case_name="Miranda v. Arizona",
                citation="384 U.S. 436",
                year=1966,
                court="U.S. Supreme Court",
                domain=LegalDomain.CONSTITUTIONAL,
                holding="Suspects must be informed of rights before custodial interrogation",
                principle="Fifth Amendment self-incrimination protection",
                modern_application="Miranda warnings required for police interrogations",
            ),
            LandmarkCase(
                case_name="New York Times Co. v. Sullivan",
                citation="376 U.S. 254",
                year=1964,
                court="U.S. Supreme Court",
                domain=LegalDomain.CONSTITUTIONAL,
                holding="Public officials must prove actual malice in defamation suits",
                principle="First Amendment protects criticism of public officials",
                modern_application="Actual malice standard for public figure defamation",
            ),
            # Torts
            LandmarkCase(
                case_name="Palsgraf v. Long Island R.R. Co.",
                citation="248 N.Y. 339",
                year=1928,
                court="New York Court of Appeals",
                domain=LegalDomain.TORTS,
                holding="Duty of care limited to foreseeable plaintiffs",
                principle="Proximate cause; foreseeability determines duty",
                modern_application="Landmark case on duty and proximate causation in negligence",
            ),
            LandmarkCase(
                case_name="Greenman v. Yuba Power Products",
                citation="59 Cal. 2d 57",
                year=1963,
                court="California Supreme Court",
                domain=LegalDomain.TORTS,
                holding="Manufacturer strictly liable for defective products",
                principle="Strict products liability",
                modern_application="Foundation of modern products liability law",
            ),
            LandmarkCase(
                case_name="Escola v. Coca Cola Bottling Co.",
                citation="24 Cal. 2d 453",
                year=1944,
                court="California Supreme Court",
                domain=LegalDomain.TORTS,
                holding="Res ipsa loquitur applies to exploding bottles",
                principle="Inference of negligence from circumstantial evidence",
                modern_application="Traynor concurrence laid groundwork for strict products liability",
            ),
            # Contracts
            LandmarkCase(
                case_name="Hadley v. Baxendale",
                citation="156 Eng. Rep. 145",
                year=1854,
                court="Court of Exchequer (England)",
                domain=LegalDomain.CONTRACTS,
                holding="Consequential damages limited to foreseeable at time of contract",
                principle="Foreseeability limits consequential damages",
                modern_application="Foundation of contract damages law; limits recovery",
            ),
            LandmarkCase(
                case_name="Lucy v. Zehmer",
                citation="196 Va. 493",
                year=1954,
                court="Virginia Supreme Court",
                domain=LegalDomain.CONTRACTS,
                holding="Contract formed based on objective manifestation, not subjective intent",
                principle="Objective theory of contracts",
                modern_application="Intent judged by reasonable person standard",
            ),
            LandmarkCase(
                case_name="Hawkins v. McGee",
                citation="84 N.H. 114",
                year=1929,
                court="New Hampshire Supreme Court",
                domain=LegalDomain.CONTRACTS,
                holding="Doctor's promise of 'perfect hand' created express warranty",
                principle="Expectation damages for breach of warranty",
                modern_application="Basis for medical malpractice warranty claims",
            ),
            # Property
            LandmarkCase(
                case_name="Pierson v. Post",
                citation="3 Cai. R. 175 (N.Y. Sup. Ct. 1805)",
                year=1805,
                court="New York Supreme Court",
                domain=LegalDomain.PROPERTY,
                holding="Property acquired by capture, not mere pursuit",
                principle="Rule of capture",
                modern_application="Foundation of property acquisition law",
            ),
            LandmarkCase(
                case_name="Kelo v. City of New London",
                citation="545 U.S. 469",
                year=2005,
                court="U.S. Supreme Court",
                domain=LegalDomain.PROPERTY,
                holding="Economic development qualifies as 'public use' for takings",
                principle="Broad interpretation of eminent domain",
                modern_application="Controversial expansion of takings power",
            ),
            # Criminal Law
            LandmarkCase(
                case_name="Gideon v. Wainwright",
                citation="372 U.S. 335",
                year=1963,
                court="U.S. Supreme Court",
                domain=LegalDomain.CRIMINAL,
                holding="Right to counsel in criminal prosecutions",
                principle="Sixth Amendment right to counsel",
                modern_application="States must provide counsel to indigent defendants",
            ),
        ]


# ===================== RESTATEMENTS INDEX =====================


@dataclass
class RestatementSection:
    """Section from ALI Restatement (principles are public domain)"""

    restatement: str
    section: str
    title: str
    principle: str
    comments: List[str]


class RestatementsIndex:
    """Key principles from Restatements of Law (ALI)"""

    @staticmethod
    def get_restatement_sections() -> List[RestatementSection]:
        return [
            RestatementSection(
                restatement="Restatement (Second) of Torts",
                section="§ 13",
                title="Battery: Harmful Contact",
                principle="Actor is subject to liability for battery if: (a) he acts intending to cause harmful or offensive contact, and (b) harmful contact results",
                comments=[
                    "Intent required is intent to cause contact, not intent to harm",
                    "Transferred intent applies",
                    "Contact need only be offensive, not harmful",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Torts",
                section="§ 46",
                title="Intentional Infliction of Emotional Distress",
                principle="One who by extreme and outrageous conduct intentionally or recklessly causes severe emotional distress is liable",
                comments=[
                    "Conduct must exceed all bounds of decency",
                    "Mere insults insufficient",
                    "Liability even without physical harm",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Torts",
                section="§ 282",
                title="Negligence Defined",
                principle="Negligence is conduct which falls below the standard established by law for protection of others",
                comments=[
                    "Reasonable person standard",
                    "Objective test, not subjective",
                    "Standard of care varies by circumstance",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Torts",
                section="§ 402A",
                title="Strict Liability - Products",
                principle="Seller engaged in business of selling product in defective condition unreasonably dangerous is strictly liable",
                comments=[
                    "Applies to commercial sellers only",
                    "No privity requirement",
                    "Defect must exist when left seller's control",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Contracts",
                section="§ 1",
                title="Contract Defined",
                principle="Contract is promise or set of promises for breach of which law gives remedy",
                comments=[
                    "Enforceable promise is key",
                    "Remedy distinguishes from moral obligation",
                    "Can be express or implied",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Contracts",
                section="§ 71",
                title="Consideration",
                principle="Performance or return promise must be bargained for to constitute consideration",
                comments=[
                    "Bargained-for exchange required",
                    "Past consideration insufficient",
                    "Adequacy not reviewed by courts",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Second) of Contracts",
                section="§ 90",
                title="Promissory Estoppel",
                principle="Promise reasonably inducing reliance is binding if injustice avoided only by enforcement",
                comments=[
                    "Consideration substitute",
                    "Reliance must be reasonable",
                    "Remedy may be limited",
                ],
            ),
            RestatementSection(
                restatement="Restatement (Third) of Torts: Products Liability",
                section="§ 2",
                title="Categories of Product Defect",
                principle="Three types: manufacturing defect, design defect, inadequate warnings",
                comments=[
                    "Manufacturing: departs from intended design",
                    "Design: foreseeable risks could have been reduced",
                    "Warning: insufficient instructions or warnings",
                ],
            ),
        ]


# ===================== FEDERAL RULES INDEX =====================


@dataclass
class FederalRule:
    """Federal procedural or evidence rule"""

    rule_system: str  # "FRCP", "FRE", "FRCrP"
    rule_number: str
    title: str
    summary: str
    key_points: List[str]


class FederalRulesIndex:
    """Index of Federal Rules (public domain)"""

    @staticmethod
    def get_federal_rules() -> List[FederalRule]:
        return [
            # Federal Rules of Civil Procedure
            FederalRule(
                rule_system="FRCP",
                rule_number="Rule 8",
                title="General Rules of Pleading",
                summary="Complaint must contain short and plain statement showing entitlement to relief",
                key_points=[
                    "Notice pleading standard",
                    "Plausibility standard post-Twombly/Iqbal",
                    "Must include jurisdictional statement",
                ],
            ),
            FederalRule(
                rule_system="FRCP",
                rule_number="Rule 12(b)(6)",
                title="Motion to Dismiss - Failure to State Claim",
                summary="Defendant may move to dismiss for failure to state claim upon which relief can be granted",
                key_points=[
                    "Tests legal sufficiency of complaint",
                    "Facts taken in light most favorable to plaintiff",
                    "Plausibility standard, not probability",
                ],
            ),
            FederalRule(
                rule_system="FRCP",
                rule_number="Rule 26",
                title="Duty to Disclose; General Provisions Governing Discovery",
                summary="Parties must disclose certain information without awaiting discovery request",
                key_points=[
                    "Initial disclosures required",
                    "Expert witness disclosures",
                    "Proportionality limits discovery",
                ],
            ),
            FederalRule(
                rule_system="FRCP",
                rule_number="Rule 56",
                title="Summary Judgment",
                summary="Court shall grant summary judgment if no genuine dispute of material fact",
                key_points=[
                    "Moving party bears burden initially",
                    "Non-moving party must show genuine issue",
                    "View evidence in light favorable to non-movant",
                ],
            ),
            # Federal Rules of Evidence
            FederalRule(
                rule_system="FRE",
                rule_number="Rule 401",
                title="Test for Relevant Evidence",
                summary="Evidence is relevant if it makes fact more or less probable and is of consequence",
                key_points=[
                    "Low bar for relevance",
                    "Probative value test",
                    "Materiality required",
                ],
            ),
            FederalRule(
                rule_system="FRE",
                rule_number="Rule 403",
                title="Excluding Relevant Evidence",
                summary="Court may exclude relevant evidence if prejudicial effect substantially outweighs probative value",
                key_points=[
                    "Balancing test",
                    "Prejudice, confusion, or waste of time",
                    "Discretionary with court",
                ],
            ),
            FederalRule(
                rule_system="FRE",
                rule_number="Rule 801",
                title="Definitions - Hearsay",
                summary="Hearsay is out-of-court statement offered to prove truth of matter asserted",
                key_points=[
                    "Three components: statement, out of court, truth of matter",
                    "Non-hearsay exceptions in (d)",
                    "Prior statements and admissions",
                ],
            ),
            FederalRule(
                rule_system="FRE",
                rule_number="Rule 802",
                title="The Rule Against Hearsay",
                summary="Hearsay is inadmissible unless exception applies",
                key_points=[
                    "General exclusion",
                    "Numerous exceptions in 803-807",
                    "Declarant availability matters for some",
                ],
            ),
            FederalRule(
                rule_system="FRE",
                rule_number="Rule 702",
                title="Testimony by Expert Witnesses",
                summary="Expert may testify if scientific, technical knowledge will help trier of fact",
                key_points=[
                    "Daubert reliability standard",
                    "Qualifications required",
                    "Opinion must be relevant and reliable",
                ],
            ),
        ]


# ===================== LEGAL RESEARCH TOOLS =====================


class LegalResearchEngine:
    """
    Comprehensive legal research capability for Mythara Engine.
    All resources derived from public domain sources.
    """

    def __init__(self):
        self.maxims = LegalMaximsIndex()
        self.cases = LandmarkCasesIndex()
        self.restatements = RestatementsIndex()
        self.rules = FederalRulesIndex()

    def search_by_domain(self, domain: LegalDomain) -> Dict[str, List]:
        """Search all resources by legal domain"""
        results = {
            "maxims": [m for m in self.maxims.get_maxims() if m.domain == domain],
            "landmark_cases": [
                c for c in self.cases.get_landmark_cases() if c.domain == domain
            ],
            "restatements": [
                r
                for r in self.restatements.get_restatement_sections()
                if domain.value.lower() in r.restatement.lower()
            ],
            "federal_rules": [],  # Domain-specific filtering for rules
        }
        return results

    def search_by_keyword(self, keyword: str) -> Dict[str, List]:
        """Full-text search across all resources"""
        keyword_lower = keyword.lower()
        results = {
            "maxims": [],
            "landmark_cases": [],
            "restatements": [],
            "federal_rules": [],
        }

        # Search maxims
        for maxim in self.maxims.get_maxims():
            if (
                keyword_lower in maxim.english.lower()
                or keyword_lower in maxim.explanation.lower()
                or keyword_lower in maxim.application.lower()
            ):
                results["maxims"].append(maxim)

        # Search cases
        for case in self.cases.get_landmark_cases():
            if (
                keyword_lower in case.case_name.lower()
                or keyword_lower in case.holding.lower()
                or keyword_lower in case.principle.lower()
            ):
                results["landmark_cases"].append(case)

        # Search restatements
        for restatement in self.restatements.get_restatement_sections():
            if (
                keyword_lower in restatement.title.lower()
                or keyword_lower in restatement.principle.lower()
            ):
                results["restatements"].append(restatement)

        # Search rules
        for rule in self.rules.get_federal_rules():
            if (
                keyword_lower in rule.title.lower()
                or keyword_lower in rule.summary.lower()
            ):
                results["federal_rules"].append(rule)

        return results

    def get_legal_principle_by_citation(self, citation: str) -> Optional[Dict]:
        """Look up specific legal principle by citation"""
        # Search cases
        for case in self.cases.get_landmark_cases():
            if citation in case.citation:
                return {"type": "case", "data": case}

        # Search restatements
        for restatement in self.restatements.get_restatement_sections():
            if citation in f"{restatement.restatement} {restatement.section}":
                return {"type": "restatement", "data": restatement}

        # Search rules
        for rule in self.rules.get_federal_rules():
            if citation in rule.rule_number:
                return {"type": "federal_rule", "data": rule}

        return None

    def generate_legal_memo(self, issue: str, relevant_keywords: List[str]) -> str:
        """Generate legal memorandum based on research"""
        memo = "# LEGAL MEMORANDUM\n\n"
        memo += f"**Issue:** {issue}\n\n"
        memo += "---\n\n"

        # Gather all relevant materials
        all_results = {
            "maxims": [],
            "landmark_cases": [],
            "restatements": [],
            "federal_rules": [],
        }
        for keyword in relevant_keywords:
            keyword_results = self.search_by_keyword(keyword)
            for key in all_results:
                all_results[key].extend(keyword_results[key])

        # Remove duplicates
        for key in all_results:
            all_results[key] = list(
                {id(item): item for item in all_results[key]}.values()
            )

        # Build memo sections
        if all_results["landmark_cases"]:
            memo += "## Applicable Case Law\n\n"
            for case in all_results["landmark_cases"][:5]:  # Limit to 5 most relevant
                memo += f"### {case.case_name}, {case.citation} ({case.year})\n"
                memo += f"**Holding:** {case.holding}\n\n"
                memo += f"**Principle:** {case.principle}\n\n"
                memo += f"**Modern Application:** {case.modern_application}\n\n"

        if all_results["restatements"]:
            memo += "## Restatement Principles\n\n"
            for restatement in all_results["restatements"][:5]:
                memo += f"### {restatement.restatement} {restatement.section}\n"
                memo += f"**Title:** {restatement.title}\n\n"
                memo += f"**Principle:** {restatement.principle}\n\n"
                if restatement.comments:
                    memo += "**Key Comments:**\n"
                    for comment in restatement.comments:
                        memo += f"- {comment}\n"
                    memo += "\n"

        if all_results["maxims"]:
            memo += "## Applicable Legal Maxims\n\n"
            for maxim in all_results["maxims"][:3]:
                memo += f"### {maxim.latin} ({maxim.english})\n"
                memo += f"**Explanation:** {maxim.explanation}\n\n"
                memo += f"**Application:** {maxim.application}\n\n"

        if all_results["federal_rules"]:
            memo += "## Relevant Federal Rules\n\n"
            for rule in all_results["federal_rules"][:5]:
                memo += f"### {rule.rule_system} {rule.rule_number}: {rule.title}\n"
                memo += f"**Summary:** {rule.summary}\n\n"
                memo += "**Key Points:**\n"
                for point in rule.key_points:
                    memo += f"- {point}\n"
                memo += "\n"

        memo += "---\n\n"
        memo += "**Note:** This memorandum is based on public domain legal principles. "
        memo += "Consult licensed attorney for case-specific advice.\n"

        return memo


# ===================== EXPORT FUNCTIONALITY =====================


def export_legal_resources_json(filepath: str):
    """Export all legal resources to JSON for external use"""
    engine = LegalResearchEngine()

    export_data = {
        "maxims": [
            {
                "latin": m.latin,
                "english": m.english,
                "domain": m.domain.value,
                "explanation": m.explanation,
                "application": m.application,
            }
            for m in engine.maxims.get_maxims()
        ],
        "landmark_cases": [
            {
                "case_name": c.case_name,
                "citation": c.citation,
                "year": c.year,
                "court": c.court,
                "domain": c.domain.value,
                "holding": c.holding,
                "principle": c.principle,
                "modern_application": c.modern_application,
            }
            for c in engine.cases.get_landmark_cases()
        ],
        "restatements": [
            {
                "restatement": r.restatement,
                "section": r.section,
                "title": r.title,
                "principle": r.principle,
                "comments": r.comments,
            }
            for r in engine.restatements.get_restatement_sections()
        ],
        "federal_rules": [
            {
                "rule_system": r.rule_system,
                "rule_number": r.rule_number,
                "title": r.title,
                "summary": r.summary,
                "key_points": r.key_points,
            }
            for r in engine.rules.get_federal_rules()
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    research = LegalResearchEngine()

    # Example 1: Search by domain
    print("=== TORTS LAW RESOURCES ===")
    torts_resources = research.search_by_domain(LegalDomain.TORTS)
    print(f"Found {len(torts_resources['maxims'])} maxims")
    print(f"Found {len(torts_resources['landmark_cases'])} landmark cases")

    # Example 2: Keyword search
    print("\n\n=== SEARCH: 'negligence' ===")
    negligence_results = research.search_by_keyword("negligence")
    for case in negligence_results["landmark_cases"]:
        print(f"- {case.case_name}: {case.principle}")

    # Example 3: Generate legal memo
    print("\n\n=== LEGAL MEMORANDUM ===")
    memo = research.generate_legal_memo(
        issue="Whether platform termination of user account creates tort liability",
        relevant_keywords=["contract", "breach", "damages", "interference"],
    )
    print(memo)

    # Example 4: Export to JSON
    export_legal_resources_json("legal_resources_index.json")
    print("\n\nExported legal resources to legal_resources_index.json")
