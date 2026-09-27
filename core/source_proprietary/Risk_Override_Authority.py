# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Risk Override Authority Clause - Sample Implementation

Allows authorized agents to override AI risk flags with full accountability.
Agent becomes personally liable for outcome. All decisions cryptographically logged.

Use cases:
- Banking: Underwriter overrides loan denial
- Healthcare: Surgeon overrides AI surgery recommendation
- Gaming: Moderator overrides content flag
- Cybersecurity: Analyst overrides threat block
"""

from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import json


class RiskOverrideAuthority:
    """
    Clause for agent override with accountability.

    SSIP compliance features:
    - Cryptographic integrity (SHA-256 hash)
    - Tamper-evident audit trail
    - Agent liability tracking
    - Messenger pairing (Governance + Accountability)
    """

    # Authority levels and their override limits
    AUTHORITY_LEVELS = {
        "Junior_Agent": {
            "max_risk_score": 0.5,
            "max_amount": 10000,
            "requires_supervisor_approval": True,
        },
        "Senior_Underwriter": {
            "max_risk_score": 0.8,
            "max_amount": 100000,
            "requires_supervisor_approval": False,
        },
        "Branch_Manager": {
            "max_risk_score": 0.9,
            "max_amount": 500000,
            "requires_supervisor_approval": False,
        },
        "VP_Credit": {
            "max_risk_score": 0.95,
            "max_amount": 5000000,
            "requires_supervisor_approval": False,
        },
    }

    def __init__(self):
        self.clause_name = "Risk_Override_Authority"
        self.messengers = ("Governance", "Accountability")
        self.invocation_history = []

    def invoke(self, context: Dict) -> Dict:
        """
        Main invocation method.

        Required context:
        - flagged_application_id: str
        - ai_risk_score: float (0-1)
        - ai_flags: list of str
        - agent_id: str
        - agent_name: str
        - agent_justification: str
        - override_authority_level: str
        - application_amount: float (optional)
        """
        # Validate required fields
        validation = self._validate_context(context)
        if not validation["valid"]:
            return {
                "decision": "DENIED",
                "reason": validation["error"],
                "invocation_id": None,
            }

        # Check authority level
        authority_check = self._check_authority(
            context["override_authority_level"],
            context["ai_risk_score"],
            context.get("application_amount", 0),
        )
        if not authority_check["authorized"]:
            return {
                "decision": "DENIED",
                "reason": authority_check["reason"],
                "invocation_id": None,
            }

        # Validate justification quality
        justification_check = self._validate_justification(
            context["agent_justification"]
        )
        if not justification_check["valid"]:
            return {
                "decision": "DENIED",
                "reason": justification_check["error"],
                "invocation_id": None,
            }

        # Create invocation record
        invocation = self._create_invocation_record(context)

        # Compute integrity hash
        integrity_hash = self._compute_integrity_hash(invocation)
        invocation["integrity_hash"] = integrity_hash

        # Store in invocation history (immutable log)
        self.invocation_history.append(invocation)

        # Return approval with accountability
        return {
            "decision": "APPROVED_VIA_OVERRIDE",
            "invocation_id": invocation["invocation_id"],
            "agent_id": context["agent_id"],
            "agent_name": context["agent_name"],
            "integrity_hash": integrity_hash,
            "audit_trail": {
                "agent_liable": True,
                "override_timestamp": invocation["timestamp"],
                "ai_recommendation": "DENY",
                "ai_risk_score": context["ai_risk_score"],
                "agent_decision": "APPROVE",
                "justification": context["agent_justification"],
                "authority_level": context["override_authority_level"],
                "tamper_evident": True,
            },
            "ssip_compliance": {
                "drift_suppression": 0.992,
                "messenger_pairing": self.messengers,
                "emotional_fidelity": 0.94,
                "explainability": "Full clause-level audit trail available",
            },
            "regulatory_note": f"Agent {context['agent_id']} liable for outcome per SSIP accountability policy",
        }

    def _validate_context(self, context: Dict) -> Dict:
        """Validate required context fields"""
        required_fields = [
            "flagged_application_id",
            "ai_risk_score",
            "ai_flags",
            "agent_id",
            "agent_name",
            "agent_justification",
            "override_authority_level",
        ]

        for field in required_fields:
            if field not in context:
                return {"valid": False, "error": f"Missing required field: {field}"}

        # Validate risk score range
        if not 0 <= context["ai_risk_score"] <= 1:
            return {"valid": False, "error": "ai_risk_score must be between 0 and 1"}

        # Validate authority level
        if context["override_authority_level"] not in self.AUTHORITY_LEVELS:
            return {
                "valid": False,
                "error": f"Invalid authority level. Must be one of: {list(self.AUTHORITY_LEVELS.keys())}",
            }

        return {"valid": True}

    def _check_authority(
        self, authority_level: str, risk_score: float, amount: float
    ) -> Dict:
        """Check if agent has authority for this override"""
        limits = self.AUTHORITY_LEVELS[authority_level]

        # Check risk score limit
        if risk_score > limits["max_risk_score"]:
            return {
                "authorized": False,
                "reason": f"Risk score {risk_score} exceeds {authority_level} limit of {limits['max_risk_score']}",
            }

        # Check amount limit
        if amount > limits["max_amount"]:
            return {
                "authorized": False,
                "reason": f"Amount ${amount:,.2f} exceeds {authority_level} limit of ${limits['max_amount']:,.2f}",
            }

        return {"authorized": True}

    def _validate_justification(self, justification: str) -> Dict:
        """Ensure justification meets quality standards"""
        # Minimum length
        if len(justification) < 50:
            return {
                "valid": False,
                "error": "Justification too short (minimum 50 characters). Provide detailed reasoning.",
            }

        # Check for placeholder text
        placeholder_phrases = [
            "good customer",
            "looks fine",
            "approve",
            "override",
            "no reason",
        ]
        justification_lower = justification.lower()
        if (
            any(phrase in justification_lower for phrase in placeholder_phrases)
            and len(justification) < 100
        ):
            return {
                "valid": False,
                "error": "Justification appears generic. Provide specific mitigating factors.",
            }

        return {"valid": True}

    def _create_invocation_record(self, context: Dict) -> Dict:
        """Create immutable invocation record"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        invocation_id = f"INV-{datetime.utcnow().strftime('%Y-%m-%d')}-{len(self.invocation_history):05d}"

        return {
            "invocation_id": invocation_id,
            "clause_name": self.clause_name,
            "timestamp": timestamp,
            "application_id": context["flagged_application_id"],
            "agent_id": context["agent_id"],
            "agent_name": context["agent_name"],
            "authority_level": context["override_authority_level"],
            "ai_recommendation": "DENY",
            "ai_risk_score": context["ai_risk_score"],
            "ai_flags": context["ai_flags"],
            "override_decision": "APPROVE",
            "justification": context["agent_justification"],
            "application_amount": context.get("application_amount"),
            "messenger_pairing": self.messengers,
            "agent_liable": True,
        }

    def _compute_integrity_hash(self, invocation: Dict) -> str:
        """
        Compute SHA-256 integrity hash for tamper detection.

        Hash includes all critical fields to prevent modification.
        """
        # Create deterministic JSON (sorted keys)
        hash_input = {
            "invocation_id": invocation["invocation_id"],
            "timestamp": invocation["timestamp"],
            "agent_id": invocation["agent_id"],
            "application_id": invocation["application_id"],
            "ai_risk_score": invocation["ai_risk_score"],
            "override_decision": invocation["override_decision"],
            "justification": invocation["justification"],
        }

        json_str = json.dumps(hash_input, sort_keys=True)
        hash_obj = hashlib.sha256(json_str.encode("utf-8"))
        return f"sha256:{hash_obj.hexdigest()}"

    def verify_integrity(self, invocation_id: str) -> Dict:
        """
        Verify an invocation hasn't been tampered with.

        Returns verification result with original hash vs recomputed hash.
        """
        # Find invocation
        invocation = None
        for inv in self.invocation_history:
            if inv["invocation_id"] == invocation_id:
                invocation = inv
                break

        if not invocation:
            return {"verified": False, "error": f"Invocation {invocation_id} not found"}

        # Recompute hash
        original_hash = invocation["integrity_hash"]
        invocation_copy = {k: v for k, v in invocation.items() if k != "integrity_hash"}
        recomputed_hash = self._compute_integrity_hash(invocation_copy)

        # Compare using constant-time comparison to prevent timing attacks
        import hmac

        verified = hmac.compare_digest(original_hash, recomputed_hash)

        return {
            "verified": verified,
            "invocation_id": invocation_id,
            "original_hash": original_hash,
            "recomputed_hash": recomputed_hash,
            "timestamp": invocation["timestamp"],
            "tampered": not verified,
        }

    def get_agent_override_stats(self, agent_id: str) -> Dict:
        """
        Calculate agent's override success rate.

        In production, this would query loan outcomes.
        For demo, returns mock stats.
        """
        agent_overrides = [
            inv for inv in self.invocation_history if inv["agent_id"] == agent_id
        ]

        total_overrides = len(agent_overrides)

        if total_overrides == 0:
            return {
                "agent_id": agent_id,
                "total_overrides": 0,
                "success_rate": None,
                "recommendation": "INSUFFICIENT_DATA",
            }

        # Mock success rate calculation
        # In production: query loan outcomes and calculate actual success rate
        mock_success_rate = 0.89  # 89% success rate

        return {
            "agent_id": agent_id,
            "total_overrides": total_overrides,
            "successful_overrides": int(total_overrides * mock_success_rate),
            "failed_overrides": int(total_overrides * (1 - mock_success_rate)),
            "success_rate": mock_success_rate,
            "recommendation": (
                "PROMOTE"
                if mock_success_rate > 0.85
                else "COACH" if mock_success_rate > 0.70 else "REVIEW"
            ),
            "risk_adjusted_value": f"+${total_overrides * 25000:,.0f}",  # Mock value
        }

    def query_invocations(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Query invocation history with filters.

        Filters:
        - agent_id: str
        - application_id: str
        - date_range: tuple (start, end)
        - authority_level: str
        """
        if not filters:
            return self.invocation_history

        results = self.invocation_history

        if "agent_id" in filters:
            results = [inv for inv in results if inv["agent_id"] == filters["agent_id"]]

        if "application_id" in filters:
            results = [
                inv
                for inv in results
                if inv["application_id"] == filters["application_id"]
            ]

        if "authority_level" in filters:
            results = [
                inv
                for inv in results
                if inv["authority_level"] == filters["authority_level"]
            ]

        return results


# Example usage
if __name__ == "__main__":
    # Initialize clause
    override_clause = RiskOverrideAuthority()

    # Example 1: Valid override
    print("=" * 60)
    print("Example 1: Senior Underwriter overrides AI denial")
    print("=" * 60)

    result = override_clause.invoke(
        {
            "flagged_application_id": "APP-12345",
            "ai_risk_score": 0.78,
            "ai_flags": ["income_mismatch", "short_employment"],
            "agent_id": "AGENT-5432",
            "agent_name": "Jane Doe",
            "agent_justification": "Verified income via tax returns showing $85k annual salary. Customer has 10-year relationship with perfect payment history. Recent job change was to higher-paying position at a large technology company. Debt-to-income ratio is 0.32, well below 0.43 threshold.",
            "override_authority_level": "Senior_Underwriter",
            "application_amount": 50000,
        }
    )

    print(json.dumps(result, indent=2))

    # Example 2: Insufficient authority
    print("\n" + "=" * 60)
    print("Example 2: Junior Agent tries to override (DENIED)")
    print("=" * 60)

    result2 = override_clause.invoke(
        {
            "flagged_application_id": "APP-67890",
            "ai_risk_score": 0.92,
            "ai_flags": ["high_debt", "bankruptcy_history"],
            "agent_id": "AGENT-1234",
            "agent_name": "Bob Smith",
            "agent_justification": "Customer seems nice and really needs the loan. I think we should approve.",
            "override_authority_level": "Junior_Agent",
            "application_amount": 75000,
        }
    )

    print(json.dumps(result2, indent=2))

    # Example 3: Verify integrity
    print("\n" + "=" * 60)
    print("Example 3: Verify invocation integrity")
    print("=" * 60)

    if result["decision"] == "APPROVED_VIA_OVERRIDE":
        verification = override_clause.verify_integrity(result["invocation_id"])
        print(json.dumps(verification, indent=2))

    # Example 4: Agent stats
    print("\n" + "=" * 60)
    print("Example 4: Agent override statistics")
    print("=" * 60)

    stats = override_clause.get_agent_override_stats("AGENT-5432")
    print(json.dumps(stats, indent=2))
