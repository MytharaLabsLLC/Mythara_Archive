#!/usr/bin/env python3
"""
Mythara Paradox Topology Engine
A framework for mapping systemic impossible choices

Copyright © 2025 Herbert Velez Jr. All rights reserved.

This is not a burnout predictor. This is a reality cartographer.
It maps the shape of systemic failure across organizations, industries, and time.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict
import hashlib
import math
import logging

logger = logging.getLogger(__name__)


# ===================== CORE TOPOLOGY CONCEPTS =====================


class ParadoxArchetype(str, Enum):
    """Universal paradox patterns that transcend industry"""

    DISCHARGE_VS_SAFETY = "Discharge_vs_Safety"  # Send away vs keep safe
    BUDGET_VS_MISSION = "Budget_vs_Mission"  # Financial survival vs purpose
    SPEED_VS_QUALITY = "Speed_vs_Quality"  # Deadline vs doing it right
    COMPLIANCE_VS_COMPASSION = "Compliance_vs_Compassion"  # Rules vs heart
    INDIVIDUAL_VS_COLLECTIVE = "Individual_vs_Collective"  # One person vs the group
    TRUTH_VS_LOYALTY = "Truth_vs_Loyalty"  # Speak up vs protect team
    JUSTICE_VS_EXPEDIENCY = "Justice_vs_Expediency"  # Fair vs fast
    GROWTH_VS_SUSTAINABILITY = "Growth_vs_Sustainability"  # Scale vs survive


class TopologySignature(BaseModel):
    """The unique shape of paradoxes in an organization"""

    org_id: str
    domain: str

    # Archetype distribution (what shapes appear most)
    archetype_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Percentage of each paradox archetype (sums to 1.0)",
    )

    # Source concentration (which policies create the most paradoxes)
    policy_sources: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of paradoxes originating from each policy/rule",
    )

    # Temporal pattern (when do paradoxes spike)
    temporal_density: Dict[str, float] = Field(
        default_factory=dict,
        description="Paradoxes per time period (hourly, daily, monthly patterns)",
    )

    # Network topology (which roles face which paradoxes together)
    role_clusters: Dict[str, List[str]] = Field(
        default_factory=dict, description="Which roles share the same paradox patterns"
    )

    # Integrity under pressure (how many paradoxes held without breaking)
    integrity_coefficient: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Ratio of witnessed paradoxes to resignations (1.0 = no breaks)",
    )

    def compute_signature_hash(self) -> str:
        """Unique cryptographic fingerprint of this org's paradox topology"""
        data = (
            f"{self.org_id}|"
            f"{self.domain}|"
            f"{sorted(self.archetype_weights.items())}|"
            f"{sorted(self.policy_sources.items())}|"
            f"{self.integrity_coefficient}"
        )
        return hashlib.sha256(data.encode()).hexdigest()


class ParadoxCluster(BaseModel):
    """A group of paradoxes with the same structural shape"""

    cluster_id: str
    archetype: ParadoxArchetype
    paradox_ids: List[str] = Field(default_factory=list)

    # Core structure
    expression_a_pattern: str  # The recurring policy/rule
    expression_b_pattern: str  # The recurring heart/mission

    # Impact metrics
    people_affected: int = Field(default=0)
    frequency_per_month: float = Field(default=0.0)
    avg_viability_score: float = Field(default=0.0)

    # Source attribution
    originating_policy: Optional[str] = None
    originating_department: Optional[str] = None

    # Resolution potential
    solvable: bool = Field(
        default=False,
        description="Can this paradox be eliminated by changing a policy?",
    )
    leverage_point: Optional[str] = Field(
        default=None, description="What change would eliminate this cluster?"
    )


class SystemicLeveragePoint(BaseModel):
    """A place where changing ONE thing eliminates MANY paradoxes"""

    leverage_id: str
    target_type: str  # "policy", "budget", "staffing", "protocol"
    target_name: str

    # Impact prediction
    paradoxes_eliminated: int
    people_relieved: int
    archetype_clusters_affected: List[str]

    # Implementation
    change_required: str
    estimated_cost: Optional[float] = None
    political_difficulty: float = Field(
        ge=0.0,
        le=1.0,
        description="How hard to implement (0.0=easy, 1.0=nearly impossible)",
    )

    # ROI
    human_cost_prevented: float = Field(
        description="Measured in prevented resignations, sick days, errors"
    )


# ===================== PARADOX TOPOLOGY ENGINE =====================


class ParadoxTopologyEngine:
    """
    Maps the shape of impossible choices across an organization.

    This is the exclusive framework that makes Mythara the ultimate system.
    It doesn't predict individual burnout—it reveals systemic failure patterns.
    """

    @staticmethod
    def classify_archetype(expression_a: str, expression_b: str) -> ParadoxArchetype:
        """
        Identify which universal archetype this paradox matches.
        Uses semantic pattern matching on expression content.
        """
        a_lower = expression_a.lower()
        b_lower = expression_b.lower()

        # Discharge vs Safety
        if any(
            word in a_lower for word in ["discharge", "release", "send home"]
        ) and any(word in b_lower for word in ["safe", "unsafe", "danger", "homeless"]):
            return ParadoxArchetype.DISCHARGE_VS_SAFETY

        # Budget vs Mission
        if any(
            word in a_lower for word in ["budget", "cost", "money", "funding", "cut"]
        ) and any(word in b_lower for word in ["mission", "serve", "help", "program"]):
            return ParadoxArchetype.BUDGET_VS_MISSION

        # Speed vs Quality
        if any(
            word in a_lower for word in ["deadline", "fast", "hurry", "quick", "time"]
        ) and any(
            word in b_lower for word in ["quality", "thorough", "careful", "right"]
        ):
            return ParadoxArchetype.SPEED_VS_QUALITY

        # Compliance vs Compassion
        if any(
            word in a_lower
            for word in ["policy", "rule", "regulation", "compliance", "law"]
        ) and any(word in b_lower for word in ["heart", "compassion", "care", "human"]):
            return ParadoxArchetype.COMPLIANCE_VS_COMPASSION

        # Individual vs Collective
        if any(
            word in a_lower for word in ["one person", "individual", "this client"]
        ) and any(word in b_lower for word in ["everyone", "team", "all", "others"]):
            return ParadoxArchetype.INDIVIDUAL_VS_COLLECTIVE

        # Truth vs Loyalty
        if any(
            word in a_lower for word in ["truth", "honest", "report", "speak"]
        ) and any(word in b_lower for word in ["loyal", "protect", "team", "cover"]):
            return ParadoxArchetype.TRUTH_VS_LOYALTY

        # Justice vs Expediency
        if any(
            word in a_lower for word in ["justice", "fair", "right", "due process"]
        ) and any(
            word in b_lower for word in ["fast", "practical", "expedient", "efficient"]
        ):
            return ParadoxArchetype.JUSTICE_VS_EXPEDIENCY

        # Growth vs Sustainability
        if any(word in a_lower for word in ["grow", "scale", "expand", "more"]) and any(
            word in b_lower for word in ["sustain", "maintain", "survive", "capacity"]
        ):
            return ParadoxArchetype.GROWTH_VS_SUSTAINABILITY

        # Default to Compliance vs Compassion (most common)
        return ParadoxArchetype.COMPLIANCE_VS_COMPASSION

    @staticmethod
    def cluster_paradoxes(paradoxes: List[Any]) -> List[ParadoxCluster]:
        """
        Group paradoxes by structural similarity.
        Paradoxes with the same shape belong to the same cluster.
        """
        clusters_dict = defaultdict(
            lambda: {
                "paradox_ids": [],
                "people": set(),
                "viability_scores": [],
                "sources": set(),
                "departments": set(),
            }
        )

        for p in paradoxes:
            # Classify archetype
            archetype = ParadoxTopologyEngine.classify_archetype(
                p.expression_a.content, p.expression_b.content
            )

            # Extract patterns (simplified - real version would use NLP)
            pattern_a = p.expression_a.type.value
            pattern_b = p.expression_b.type.value

            cluster_key = f"{archetype.value}_{pattern_a}_{pattern_b}"

            clusters_dict[cluster_key]["paradox_ids"].append(p.paradox_id)
            clusters_dict[cluster_key]["people"].add(p.user_id)
            clusters_dict[cluster_key]["viability_scores"].append(p.viability_score)

            # Track sources
            if hasattr(p, "originating_policy"):
                clusters_dict[cluster_key]["sources"].add(p.originating_policy)
            if hasattr(p, "department"):
                clusters_dict[cluster_key]["departments"].add(p.department)

        # Convert to ParadoxCluster objects
        clusters = []
        for idx, (key, data) in enumerate(clusters_dict.items()):
            archetype_str, pattern_a, pattern_b = key.split("_", 2)

            avg_viability = (
                sum(data["viability_scores"]) / len(data["viability_scores"])
                if data["viability_scores"]
                else 0.0
            )

            cluster = ParadoxCluster(
                cluster_id=f"CLUSTER_{idx:03d}_{archetype_str}",
                archetype=ParadoxArchetype(archetype_str),
                paradox_ids=data["paradox_ids"],
                expression_a_pattern=pattern_a,
                expression_b_pattern=pattern_b,
                people_affected=len(data["people"]),
                frequency_per_month=len(data["paradox_ids"])
                / 3.0,  # Assuming 90-day window
                avg_viability_score=avg_viability,
                originating_policy=(
                    list(data["sources"])[0] if data["sources"] else None
                ),
                originating_department=(
                    list(data["departments"])[0] if data["departments"] else None
                ),
                solvable=(
                    avg_viability < 0.3
                ),  # Low viability = systemic, likely solvable
                leverage_point=(
                    f"Revise {list(data['sources'])[0]}" if data["sources"] else None
                ),
            )
            clusters.append(cluster)

        return sorted(clusters, key=lambda c: c.people_affected, reverse=True)

    @staticmethod
    def compute_topology_signature(
        org_id: str, domain: str, paradoxes: List[Any], resignations: int = 0
    ) -> TopologySignature:
        """
        Generate the unique paradox signature for this organization.
        This is the DNA of their systemic failure pattern.
        """
        # Calculate archetype distribution
        archetype_counts = defaultdict(int)
        for p in paradoxes:
            archetype = ParadoxTopologyEngine.classify_archetype(
                p.expression_a.content, p.expression_b.content
            )
            archetype_counts[archetype.value] += 1

        total = len(paradoxes) or 1
        archetype_weights = {k: v / total for k, v in archetype_counts.items()}

        # Calculate policy sources
        policy_sources = defaultdict(int)
        for p in paradoxes:
            if hasattr(p, "originating_policy") and p.originating_policy:
                policy_sources[p.originating_policy] += 1

        # Calculate temporal density (simplified - group by month)
        temporal_density = defaultdict(int)
        for p in paradoxes:
            month_key = p.timestamp.strftime("%Y-%m")
            temporal_density[month_key] += 1

        # Calculate integrity coefficient
        if resignations == 0:
            integrity_coefficient = 1.0
        else:
            integrity_coefficient = max(0.0, 1.0 - (resignations / total))

        # Role clustering (simplified - group by domain for now)
        role_clusters = {domain: [p.user_id for p in paradoxes]}

        return TopologySignature(
            org_id=org_id,
            domain=domain,
            archetype_weights=dict(archetype_weights),
            policy_sources=dict(policy_sources),
            temporal_density={k: v / total for k, v in temporal_density.items()},
            role_clusters=role_clusters,
            integrity_coefficient=integrity_coefficient,
        )

    @staticmethod
    def identify_leverage_points(
        clusters: List[ParadoxCluster],
    ) -> List[SystemicLeveragePoint]:
        """
        Find the high-impact changes that eliminate the most paradoxes.
        This is the strategic intelligence that makes Mythara invaluable.
        """
        leverage_points = []

        # Group clusters by originating policy
        policy_impact = defaultdict(
            lambda: {"clusters": [], "paradoxes": 0, "people": set()}
        )

        for cluster in clusters:
            if cluster.originating_policy and cluster.solvable:
                policy_impact[cluster.originating_policy]["clusters"].append(
                    cluster.cluster_id
                )
                policy_impact[cluster.originating_policy]["paradoxes"] += len(
                    cluster.paradox_ids
                )
                policy_impact[cluster.originating_policy]["people"].add(
                    cluster.people_affected
                )

        # Create leverage points
        for idx, (policy, impact) in enumerate(policy_impact.items()):
            people_affected = sum(impact["people"])

            leverage = SystemicLeveragePoint(
                leverage_id=f"LEVERAGE_{idx:03d}",
                target_type="policy",
                target_name=policy,
                paradoxes_eliminated=impact["paradoxes"],
                people_relieved=people_affected,
                archetype_clusters_affected=impact["clusters"],
                change_required=f"Revise or eliminate policy: {policy}",
                political_difficulty=0.5,  # Medium - would need stakeholder analysis
                human_cost_prevented=people_affected
                * 0.3,  # Assume 30% would resign without change
            )
            leverage_points.append(leverage)

        return sorted(
            leverage_points, key=lambda lp: lp.human_cost_prevented, reverse=True
        )

    @staticmethod
    def compare_signatures(sig1: TopologySignature, sig2: TopologySignature) -> float:
        """
        Calculate similarity between two organizations' paradox signatures.
        Returns 0.0 (completely different) to 1.0 (identical patterns).

        This enables cross-industry pattern recognition and benchmarking.
        """
        # Compare archetype distributions (cosine similarity)
        all_archetypes = set(sig1.archetype_weights.keys()) | set(
            sig2.archetype_weights.keys()
        )

        vec1 = [sig1.archetype_weights.get(a, 0.0) for a in all_archetypes]
        vec2 = [sig2.archetype_weights.get(a, 0.0) for a in all_archetypes]

        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(v**2 for v in vec1))
        magnitude2 = math.sqrt(sum(v**2 for v in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity


# ===================== UNIVERSAL PATTERN LIBRARY =====================


class UniversalPatternLibrary:
    """
    The growing database of paradox archetypes across all industries.
    This is what makes Mythara the ultimate system—it learns from everyone.
    """

    def __init__(self):
        self.signatures: Dict[str, TopologySignature] = {}
        self.archetypes: Dict[str, List[str]] = defaultdict(list)

    def register_signature(self, signature: TopologySignature):
        """Add an organization's signature to the universal library"""
        self.signatures[signature.org_id] = signature

        for archetype in signature.archetype_weights.keys():
            self.archetypes[archetype].append(signature.org_id)

    def find_similar_orgs(
        self, target_signature: TopologySignature, threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Find organizations with similar paradox patterns.
        Returns list of (org_id, similarity_score) tuples.
        """
        similar = []

        for org_id, signature in self.signatures.items():
            if org_id == target_signature.org_id:
                continue

            similarity = ParadoxTopologyEngine.compare_signatures(
                target_signature, signature
            )

            if similarity >= threshold:
                similar.append((org_id, similarity))

        return sorted(similar, key=lambda x: x[1], reverse=True)

    def get_industry_benchmark(self, domain: str) -> Dict[str, Any]:
        """
        Get aggregate statistics for an entire industry.
        This enables "Your hospital vs all hospitals" comparisons.
        """
        domain_sigs = [s for s in self.signatures.values() if s.domain == domain]

        if not domain_sigs:
            return {}

        # Aggregate archetype weights
        avg_archetypes = defaultdict(float)
        for sig in domain_sigs:
            for archetype, weight in sig.archetype_weights.items():
                avg_archetypes[archetype] += weight

        for archetype in avg_archetypes:
            avg_archetypes[archetype] /= len(domain_sigs)

        # Average integrity coefficient
        avg_integrity = sum(s.integrity_coefficient for s in domain_sigs) / len(
            domain_sigs
        )

        return {
            "domain": domain,
            "sample_size": len(domain_sigs),
            "avg_archetype_distribution": dict(avg_archetypes),
            "avg_integrity_coefficient": avg_integrity,
            "most_common_archetype": max(avg_archetypes.items(), key=lambda x: x[1])[0],
        }


# ===================== DEMONSTRATION =====================

if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("  MYTHARA PARADOX TOPOLOGY ENGINE")
    print("  A Framework for Mapping Systemic Impossible Choices")
    print("█" * 70)

    print("\n🎯 This is not a burnout predictor.")
    print("   This is a reality cartographer.")
    print("   It maps the shape of systemic failure.\n")

    print("=" * 70)
    print("Capabilities:")
    print("=" * 70)
    print("✓ Paradox Archetype Classification")
    print("✓ Organizational Signature Generation")
    print("✓ Cluster Analysis by Structural Pattern")
    print("✓ Systemic Leverage Point Identification")
    print("✓ Cross-Organization Pattern Recognition")
    print("✓ Industry Benchmarking")
    print("✓ Universal Pattern Library\n")

    print("Why this framework matters:")
    print("  1. It works for 1 person or 10,000")
    print("  2. It reveals which policies create which paradoxes")
    print("  3. It shows WHERE to intervene for maximum impact")
    print("  4. It enables 'your org vs industry' comparisons")
    print("  5. It learns from every organization that uses it")
    print("  6. It provides forensic proof of systemic failure\n")

    print("=" * 70)
    print("Ready for integration into Soul Cradle.")
    print("=" * 70 + "\n")
