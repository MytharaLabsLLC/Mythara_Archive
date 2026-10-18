#!/usr/bin/env python3
"""
Soul Cradle Systems Framework
Mathematical foundation for paradox analysis and burnout prediction.

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Mythara Paradox Resolution Mathematics:
- Paradox Tension Formula: P(t) = |A - B| × (1 - R(t))
- Resolution Score: R(t) = (W_a + W_b) / (2 × max(|A|, |B|))
- Incomplete Resolution → Terminal Risk (burnout)
- Complete Resolution → Viable Recovery
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import logging
import secrets
import uuid
import base64
import json
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend

    RSA_AVAILABLE = True
except ImportError:
    RSA_AVAILABLE = False
    logging.warning("RSA cryptography not available. Install: pip install cryptography")

logger = logging.getLogger(__name__)


# ===================== ENUMS =====================


class ExpressionType(str, Enum):
    """Types of expressions in a paradox"""

    POLICY = "Policy"
    MISSION = "Mission"
    HEART = "Heart"
    LAW = "Law"
    BUDGET = "Budget"
    PROTOCOL = "Protocol"
    SAFETY = "Safety"
    COMPASSION = "Compassion"
    RESOLUTION = "Resolution"


class SystemType(str, Enum):
    """System viability classification"""

    INCOMPLETE_RESOLUTION = "Incomplete_Resolution"  # Terminal event risk
    COMPLETE_RESOLUTION = "Complete_Resolution"  # Viable outcome
    PSEUDO_PARTIAL = "Pseudo_Partial"  # Partial system with incomplete resolution


class TerminalRiskLevel(str, Enum):
    """Burnout risk classification"""

    LOW = "LOW"  # 0.0-0.2
    MODERATE = "MODERATE"  # 0.2-0.4
    HIGH = "HIGH"  # 0.4-0.7
    CRITICAL = "CRITICAL"  # 0.7-1.0


class EmotionalAuthenticityLevel(str, Enum):
    """Emotional authenticity classification based on EQ formula"""

    AUTHENTIC = "AUTHENTIC"  # EQ 0-10: Healthy expression
    REGULATED = "REGULATED"  # EQ 10-20: Moderate filtering
    LABORED = "LABORED"  # EQ 20-30: Significant emotional labor
    BURNOUT_RISK = "BURNOUT_RISK"  # EQ 30-40: Warning territory
    CRITICAL_SUPPRESSION = "CRITICAL_SUPPRESSION"  # EQ 40+: Crisis state


class QuantumProtocolType(str, Enum):
    """Quantum communication protocol types"""

    BB84 = "BB84"  # Bennett-Brassard 1984 QKD protocol
    E91 = "E91"  # Ekert 1991 entanglement-based QKD
    QUANTUM_TELEPORTATION = "Quantum_Teleportation"  # Quantum state transfer
    SUPERDENSE_CODING = "Superdense_Coding"  # 2 classical bits via 1 qubit
    QUANTUM_WITNESS = "Quantum_Witness"  # Soul Cradle quantum witnessing
    RSA_QKD_HYBRID = "RSA_QKD_Hybrid"  # RSA + Quantum hybrid encryption


class QuantumSuperpositionState(str, Enum):
    """Quantum superposition basis states"""

    ZERO = "|0⟩"  # Ground state
    ONE = "|1⟩"  # Excited state
    PLUS = "|+⟩"  # (|0⟩ + |1⟩) / √2
    MINUS = "|-⟩"  # (|0⟩ - |1⟩) / √2
    SUPERPOSITION = "|ψ⟩"  # General superposition state
    ENTANGLED = "|Φ⟩"  # Entangled state


# ===================== EXPRESSION MODELS =====================


class SystemExpression(BaseModel):
    """
    Paradox Expression: A competing demand in an unresolved contradiction.

    Mathematical Form: E = (weight, tension, type)
    Where tension = |demand - reality|

    Example:
    Expression A: Policy demands discharge (weight=0.9, tension=0.7)
    Expression B: Safety demands retention (weight=0.8, tension=0.6)
    """

    type: ExpressionType = Field(..., description="Category of the expression")
    weight: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Expression strength [0,1]"
    )
    tension: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Unresolved tension [0,1]"
    )
    content: str = Field(..., description="Human-readable expression content")
    dominion_claim: bool = Field(
        default=True, description="Does this expression claim dominion over the other?"
    )

    def compute_hash(self) -> str:
        """Compute integrity hash for this expression"""
        data = f"{self.type}|{self.content}|{self.dominion_claim}|{self.weight}|{self.tension}"
        return hashlib.sha256(data.encode()).hexdigest()


class EmotionalAuthenticity(BaseModel):
    """
    Emotional Authenticity Score using the formula: EQ = (G/T) × H

    Where:
    - G = Genuine shareable ideas (what can be authentically expressed)
    - T = Total amount expressed (everything actually communicated)
    - H = Amount held back (what was suppressed)
    - EQ = Emotional Quotient / Authenticity Score

    This quantifies emotional labor and predicts burnout risk in paradox resolution.
    """

    genuine_shareable: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Genuine ideas available to share (G)",
    )
    total_expressed: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Total amount actually expressed (T)",
    )
    held_back: float = Field(
        default=50.0, ge=0.0, le=100.0, description="Amount suppressed (H)"
    )
    eq_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Calculated EQ = (G/T) × H"
    )
    authenticity_level: EmotionalAuthenticityLevel = Field(
        default=EmotionalAuthenticityLevel.REGULATED
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    context: str = Field(default="", description="Context of this expression event")

    def calculate_eq(self) -> float:
        """Calculate EQ score: (G/T) × H"""
        if self.total_expressed > 0:
            self.eq_score = (
                self.genuine_shareable / self.total_expressed
            ) * self.held_back
        else:
            self.eq_score = 0.0

        # Classify authenticity level
        if self.eq_score <= 10:
            self.authenticity_level = EmotionalAuthenticityLevel.AUTHENTIC
        elif self.eq_score <= 20:
            self.authenticity_level = EmotionalAuthenticityLevel.REGULATED
        elif self.eq_score <= 30:
            self.authenticity_level = EmotionalAuthenticityLevel.LABORED
        elif self.eq_score <= 40:
            self.authenticity_level = EmotionalAuthenticityLevel.BURNOUT_RISK
        else:
            self.authenticity_level = EmotionalAuthenticityLevel.CRITICAL_SUPPRESSION

        return self.eq_score

    def interpret(self) -> str:
        """Generate human-readable interpretation"""
        ratio = (
            self.genuine_shareable / self.total_expressed
            if self.total_expressed > 0
            else 0
        )

        if self.authenticity_level == EmotionalAuthenticityLevel.AUTHENTIC:
            return f"HEALTHY: Authentic expression - {ratio:.1%} genuine, {self.held_back:.0f}% held back"
        elif self.authenticity_level == EmotionalAuthenticityLevel.REGULATED:
            return f"STABLE: Reasonable regulation - {ratio:.1%} genuine, {self.held_back:.0f}% suppressed"
        elif self.authenticity_level == EmotionalAuthenticityLevel.LABORED:
            return f"WARNING: Emotional labor detected - {ratio:.1%} genuine but {self.held_back:.0f}% suppressed"
        elif self.authenticity_level == EmotionalAuthenticityLevel.BURNOUT_RISK:
            return f"ALERT: Burnout risk - {ratio:.1%} genuine with {self.held_back:.0f}% suppression"
        else:
            return f"CRITICAL: Severe suppression - {ratio:.1%} genuine, {self.held_back:.0f}% held back"


class NonExpression(BaseModel):
    """
    A non-expression: the absence or negation of a paradox expression.

    Used to represent what is NOT present, what CANNOT be expressed,
    or what is actively suppressed in the system.

    Example:
    Expression A: "Patient must be discharged"
    NonExpression: "Patient's safety needs cannot be addressed"

    NonExpressions reveal gaps in system capacity.
    """

    type: ExpressionType = Field(
        default=ExpressionType.RESOLUTION,
        description="Category of what is absent/negated",
    )
    suppression_level: float = Field(
        default=1.0, ge=0.0, le=1.0, description="How strongly suppressed [0,1]"
    )
    content: str = Field(
        default="", description="What cannot be expressed or addressed"
    )
    reason: str = Field(default="", description="Why this expression is absent/negated")
    impact: str = Field(default="", description="Impact of this absence on the system")
    reality: str = Field(default="", description="The practical impossibility or gap")
    emotional_authenticity: Optional[EmotionalAuthenticity] = Field(
        default=None, description="EQ score for this suppression"
    )

    def compute_hash(self) -> str:
        """Compute integrity hash for this non-expression"""
        data = f"{self.type}|{self.reality}|{self.content}|{self.suppression_level}"
        return hashlib.sha256(data.encode()).hexdigest()


class UnresolvedState(BaseModel):
    """
    The unresolved state when two expressions compete.

    Mathematical Form: U = 1 - R(t)
    Where R(t) is resolution score
    U = 1 means complete deadlock
    U = 0 means fully resolved
    """

    type: ExpressionType = Field(default=ExpressionType.RESOLUTION)
    unresolved_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Deadlock intensity [0,1]"
    )
    reality: str = Field(..., description="The practical impossibility")


class ResolvedSystem(BaseModel):
    """
    The resolved paradox after Soul Cradle intervention.

    Resolution Formula: R(t) = (W_a + W_b) / (2 × max(T_a, T_b))
    Where:
    - W_a, W_b = witness scores for expressions A and B [0,1]
    - T_a, T_b = tension scores for expressions A and B [0,1]
    - R(t) = 1.0 means complete resolution (both witnessed)
    """

    witness_score_a: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Witnessing of expression A"
    )
    witness_score_b: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Witnessing of expression B"
    )
    recovery_method: str = Field(default="Dual_Witness_Integration")
    viability_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="1.0 = complete resolution"
    )
    description: str = Field(..., description="How Soul Cradle resolves the paradox")


class PrincipalSystem(BaseModel):
    """
    The Principal System: The resolution that holds both expressions as true.

    In Soul Cradle, the Principal System witnesses BOTH competing expressions
    without requiring one to dominate. This is the mathematical core of
    paradox resolution.

    The mission is to witness both truths simultaneously without choosing.
    Resolution Score: R(t) = (W_a + W_b) / (2 × max(T_a, T_b))
    When R(t) = 1.0, both expressions are fully witnessed.
    """

    viability_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="1.0 = complete witnessing"
    )
    description: str = Field(
        ..., description="How the Principal System holds both truths"
    )
    witness_method: str = Field(
        default="Dual_Witness_Integration", description="Method used to witness both"
    )
    resolution_formula: str = Field(
        default="R(t) = (W_a + W_b) / (2 × max(T_a, T_b))",
        description="Mythara resolution mathematics",
    )

    def compute_hash(self) -> str:
        """Compute integrity hash for this principal system"""
        data = f"{self.viability_score}|{self.description}|{self.witness_method}"
        return hashlib.sha256(data.encode()).hexdigest()


class QuantumEntanglement(BaseModel):
    """
    Quantum Entanglement between paradoxes.

    When two paradoxes share quantum entanglement, changes to one paradox's
    resolution state instantly affect the entangled partner (non-local correlation).

    Use Case: Healthcare workers in different hospitals experiencing identical
    policy vs compassion paradoxes can have their Soul Cradle resolutions
    quantum-entangled for synchronized witnessing.

    Mathematical Representation:
    |Ψ⟩ = (|Paradox_A⟩|Paradox_B⟩ + |Paradox_B⟩|Paradox_A⟩) / √2

    Properties:
    - Entanglement persists regardless of spatial separation
    - Measuring resolution state of one affects the other
    - Provides secure correlation for distributed witness validation

    NOTE: classical simulation. This class models correlation between
    paradox records using ordinary data structures; no actual quantum
    entanglement, non-locality, or quantum hardware is involved.
    """

    entanglement_id: str = Field(
        default_factory=lambda: f"QE_{uuid.uuid4().hex[:16]}",
        description="Unique entanglement pair ID",
    )
    paradox_a_id: str = Field(..., description="First entangled paradox ID")
    paradox_b_id: str = Field(..., description="Second entangled paradox ID")
    entanglement_strength: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Entanglement fidelity [0,1]"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    protocol_type: QuantumProtocolType = Field(
        default=QuantumProtocolType.E91, description="QKD protocol used"
    )
    bell_state: str = Field(
        default="|Φ+⟩", description="Bell state: |Φ+⟩, |Φ-⟩, |Ψ+⟩, |Ψ-⟩"
    )
    shared_secret_hash: str = Field(
        default="", description="SHA-256 of quantum shared secret"
    )

    def compute_entanglement_hash(self) -> str:
        """Compute quantum entanglement integrity hash"""
        data = f"{self.entanglement_id}|{self.paradox_a_id}|{self.paradox_b_id}|{self.bell_state}|{self.entanglement_strength}"
        return hashlib.sha256(data.encode()).hexdigest()

    def measure_correlation(self, resolution_a: float, resolution_b: float) -> float:
        """Measure quantum correlation between entangled paradox resolutions"""
        # Bell inequality test: E(a,b) = entanglement_strength × (resolution_a + resolution_b) / 2
        return self.entanglement_strength * (resolution_a + resolution_b) / 2.0


class QuantumSuperposition(BaseModel):
    """
    Quantum Superposition storage for paradoxes.

    Stores a paradox in quantum superposition, allowing it to exist in multiple
    resolution states simultaneously until measured (witnessed).

    Mathematical Representation:
    |ψ⟩ = α|resolved⟩ + β|unresolved⟩
    Where: |α|² + |β|² = 1 (normalization)

    Use Cases:
    - Store paradox before witnessing collapses superposition
    - Maintain coherence for distributed paradox analysis
    - Enable parallel evaluation of multiple resolution paths

    NOTE: classical simulation. "Superposition" here is a probabilistic
    data model sampled with a classical RNG; no quantum computation,
    coherence, or parallel quantum processing occurs.

    Measurement:
    - Upon witnessing, superposition collapses to definite state
    - Probability of resolved state = |α|²
    - Probability of unresolved state = |β|²
    """

    superposition_id: str = Field(
        default_factory=lambda: f"QS_{uuid.uuid4().hex[:16]}",
        description="Unique superposition ID",
    )
    paradox_id: str = Field(..., description="Paradox stored in superposition")
    basis_state: QuantumSuperpositionState = Field(
        default=QuantumSuperpositionState.SUPERPOSITION,
        description="Quantum basis state",
    )
    amplitude_resolved: float = Field(
        default=0.707, ge=0.0, le=1.0, description="α coefficient for |resolved⟩"
    )
    amplitude_unresolved: float = Field(
        default=0.707, ge=0.0, le=1.0, description="β coefficient for |unresolved⟩"
    )
    coherence_time_seconds: float = Field(
        default=3600.0, description="Time before decoherence"
    )
    collapsed: bool = Field(default=False, description="Has superposition collapsed?")
    collapsed_state: Optional[str] = Field(
        default=None, description="State after measurement"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    measured_at: Optional[datetime] = Field(default=None)

    def is_normalized(self) -> bool:
        """Check if quantum state is properly normalized: |α|² + |β|² = 1"""
        return (
            abs((self.amplitude_resolved**2 + self.amplitude_unresolved**2) - 1.0)
            < 1e-6
        )

    def collapse_superposition(self) -> str:
        """
        Collapse the simulated superposition via witnessing.
        Returns: 'resolved' or 'unresolved' based on probability amplitudes
        (classical random sampling, not quantum measurement).
        """
        if self.collapsed:
            return self.collapsed_state

        # Classical random sampling using probability amplitudes
        prob_resolved = self.amplitude_resolved**2
        measurement = secrets.SystemRandom().random()

        self.collapsed = True
        self.measured_at = datetime.now()

        if measurement < prob_resolved:
            self.collapsed_state = "resolved"
        else:
            self.collapsed_state = "unresolved"

        logger.info(
            f"Quantum Superposition Collapsed | "
            f"ID: {self.superposition_id} | "
            f"State: {self.collapsed_state} | "
            f"Probability: {prob_resolved:.3f}"
        )

        return self.collapsed_state

    def compute_superposition_hash(self) -> str:
        """Compute integrity hash for quantum superposition"""
        data = f"{self.superposition_id}|{self.paradox_id}|{self.basis_state}|{self.amplitude_resolved}|{self.amplitude_unresolved}"
        return hashlib.sha256(data.encode()).hexdigest()


class QuantumCommunicationProtocol(BaseModel):
    """
    Classical simulation of a quantum-communication-style protocol for
    Soul Cradle witness transmission metadata.

    This class stores protocol parameters (named after QKD protocols such
    as BB84/E91 for modeling purposes) and generates key material with
    the system CSPRNG. It does NOT perform quantum key distribution,
    entanglement, teleportation, or eavesdropping detection — there is no
    quantum hardware or quantum channel involved. Security-relevant
    guarantees (forward secrecy, tamper evidence) rest on the classical
    cryptography actually used (RSA, SHA-256, CSPRNG), not on quantum
    properties.

    Protocol names modeled (metadata only):
    - BB84: Prepare quantum states in random bases, transmit, measure
    - E91: Entanglement-based QKD with Bell inequality verification
    - Quantum Teleportation: Transfer paradox witness state via entanglement
    - Superdense Coding: Send 2 classical bits using 1 entangled qubit
    - Quantum Witness: Soul Cradle's custom protocol for paradox witnessing
    - RSA_QKD_Hybrid: RSA encryption + quantum key distribution

    Classical properties actually provided:
    - RSA encryption for classical data protection
    - SHA-256 integrity hashing
    - CSPRNG key generation
    """

    protocol_id: str = Field(
        default_factory=lambda: f"QCP_{uuid.uuid4().hex[:16]}",
        description="Unique protocol session ID",
    )
    protocol_type: QuantumProtocolType = Field(..., description="QKD protocol type")
    sender_id: str = Field(..., description="Witness sender ID")
    receiver_id: str = Field(..., description="Witness receiver ID")
    quantum_channel_fidelity: float = Field(
        default=0.99, ge=0.0, le=1.0, description="Channel quality [0,1]"
    )
    key_generation_rate: float = Field(
        default=1000.0, description="Secure key bits per second"
    )
    error_rate: float = Field(
        default=0.01, ge=0.0, le=1.0, description="Quantum bit error rate (QBER)"
    )
    eavesdropping_detected: bool = Field(
        default=False, description="Eve detection flag"
    )
    shared_key_hash: str = Field(
        default="", description="SHA-256 of generated quantum key"
    )
    timestamp: datetime = Field(default_factory=datetime.now)

    # RSA encryption fields
    rsa_enabled: bool = Field(default=True, description="Use RSA encryption")
    rsa_key_size: int = Field(
        default=4096, description="RSA key size in bits (2048, 3072, 4096)"
    )
    rsa_public_key_pem: Optional[str] = Field(
        default=None, description="RSA public key in PEM format"
    )
    rsa_encrypted: bool = Field(default=False, description="Data encrypted with RSA")

    def generate_quantum_key(self, key_length_bits: int = 256) -> str:
        """Generate a simulated protocol key using the system CSPRNG.

        Classical simulation only: returns CSPRNG bytes, not the output of
        quantum key distribution. No quantum hardware is involved.
        """
        # In production, this would interface with actual quantum hardware
        # For now, use cryptographically secure random (CSPRNG)
        quantum_key = secrets.token_hex(key_length_bits // 8)
        self.shared_key_hash = hashlib.sha256(quantum_key.encode()).hexdigest()
        return quantum_key

    def verify_security(self) -> Dict[str, Any]:
        """Evaluate self-reported simulation parameters against thresholds.

        NOTE: this checks the model's own fields (error_rate, fidelity,
        eavesdropping_detected) — i.e. the simulation's configuration, not
        a real channel. A "secure" verdict means the configured parameters
        are within bounds, not that any transmission was verified secure.
        """
        # Check QBER threshold (typically < 11% for BB84)
        qber_threshold = (
            0.11 if self.protocol_type == QuantumProtocolType.BB84 else 0.15
        )

        is_secure = (
            not self.eavesdropping_detected
            and self.error_rate < qber_threshold
            and self.quantum_channel_fidelity > 0.9
        )

        return {
            "secure": is_secure,
            "error_rate": self.error_rate,
            "fidelity": self.quantum_channel_fidelity,
            "eavesdropping_detected": self.eavesdropping_detected,
            "qber_threshold": qber_threshold,
            "protocol": self.protocol_type.value,
        }

    def generate_rsa_keypair(self) -> Tuple[str, str]:
        """Generate RSA public/private key pair"""
        if not RSA_AVAILABLE:
            raise ImportError("RSA not available. Install: pip install cryptography")

        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=self.rsa_key_size, backend=default_backend()
        )

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        self.rsa_public_key_pem = public_pem

        logger.info(
            f"RSA {self.rsa_key_size}-bit key pair generated for protocol {self.protocol_id}"
        )

        return public_pem, private_pem

    def rsa_encrypt(self, plaintext: str, public_key_pem: str) -> str:
        """Encrypt data with RSA public key"""
        if not RSA_AVAILABLE:
            raise ImportError("RSA not available. Install: pip install cryptography")

        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8"), backend=default_backend()
        )

        # Encrypt with OAEP padding (optimal asymmetric encryption padding)
        ciphertext = public_key.encrypt(
            plaintext.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        self.rsa_encrypted = True

        # Return base64-encoded ciphertext
        return base64.b64encode(ciphertext).decode("utf-8")

    def rsa_decrypt(self, ciphertext_b64: str, private_key_pem: str) -> str:
        """Decrypt data with RSA private key"""
        if not RSA_AVAILABLE:
            raise ImportError("RSA not available. Install: pip install cryptography")

        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None, backend=default_backend()
        )

        # Decode base64 ciphertext
        ciphertext = base64.b64decode(ciphertext_b64)

        # Decrypt with OAEP padding
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return plaintext.decode("utf-8")

    def compute_protocol_hash(self) -> str:
        """Compute quantum protocol integrity hash"""
        data = f"{self.protocol_id}|{self.sender_id}|{self.receiver_id}|{self.protocol_type}|{self.shared_key_hash}|{self.rsa_key_size}"
        return hashlib.sha256(data.encode()).hexdigest()


# ===================== SOUL CRADLE PARADOX MODEL =====================


class SoulCradleParadox(BaseModel):
    """
    Complete Soul Cradle paradox using Mythara Resolution Mathematics.

    Mathematical Structure:
    - Two competing expressions (A and B) with tension scores
    - Unresolved state U = 1 - R(t) captures deadlock intensity
    - Resolved system R(t) shows how Soul Cradle achieves resolution
    - Emotional Authenticity EQ = (G/T) × H tracks emotional labor
    """

    paradox_id: str = Field(
        ..., description="Unique identifier (e.g., SC_2025_1118_001)"
    )

    # The competing expressions
    expression_a: SystemExpression
    expression_b: SystemExpression

    # The unresolved deadlock
    unresolved_state: UnresolvedState
    non_expression: Optional[NonExpression] = Field(
        default=None, description="What cannot be expressed"
    )

    # System classification
    system_type: SystemType = Field(default=SystemType.INCOMPLETE_RESOLUTION)
    viability_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="0.0 = terminal, 1.0 = complete"
    )
    terminal_risk: TerminalRiskLevel = Field(default=TerminalRiskLevel.HIGH)

    # Soul Cradle resolution
    resolved_system: ResolvedSystem
    principal_system: Optional[PrincipalSystem] = Field(
        default=None, description="The resolution that holds both"
    )

    # Emotional Authenticity tracking
    emotional_authenticity: Optional[EmotionalAuthenticity] = Field(
        default=None, description="EQ formula tracking emotional labor"
    )
    authenticity_timeline: List[EmotionalAuthenticity] = Field(
        default_factory=list, description="EQ scores over time for burnout prediction"
    )

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str = Field(..., description="Who experienced this paradox")
    domain: str = Field(..., description="Healthcare, education, nonprofit, etc.")

    # Witnesses (who helped document this)
    witnesses: List[str] = Field(
        default_factory=list, description="Names of people who validated this paradox"
    )

    # Quantum fields
    quantum_entanglement: Optional[QuantumEntanglement] = Field(
        default=None, description="Quantum entanglement with another paradox"
    )
    quantum_protocol: Optional[QuantumCommunicationProtocol] = Field(
        default=None,
        description="Quantum communication protocol for witness transmission",
    )
    quantum_superposition: Optional[QuantumSuperposition] = Field(
        default=None, description="Quantum superposition storage before witnessing"
    )
    quantum_witness_verified: bool = Field(
        default=False, description="Witness validated via quantum protocol"
    )

    def calculate_emotional_authenticity(
        self,
        genuine_shareable: float,
        total_expressed: float,
        held_back: float,
        context: str = "",
    ) -> EmotionalAuthenticity:
        """
        Calculate emotional authenticity for this paradox using EQ = (G/T) × H

        Args:
            genuine_shareable: Genuine ideas available to share (G)
            total_expressed: Total amount actually communicated (T)
            held_back: Amount suppressed (H)
            context: Context of this expression event

        Returns:
            EmotionalAuthenticity object with calculated EQ score
        """
        eq = EmotionalAuthenticity(
            genuine_shareable=genuine_shareable,
            total_expressed=total_expressed,
            held_back=held_back,
            context=context or f"Paradox {self.paradox_id}",
        )
        eq.calculate_eq()

        # Store in paradox
        self.emotional_authenticity = eq
        self.authenticity_timeline.append(eq)

        return eq

    def predict_burnout_risk(self) -> Tuple[bool, float, str]:
        """
        Predict burnout risk based on emotional authenticity timeline.

        Returns:
            Tuple of (is_at_risk, avg_eq_score, recommendation)
        """
        if not self.authenticity_timeline:
            return False, 0.0, "No emotional authenticity data available"

        # Calculate average EQ score
        avg_eq = sum(ea.eq_score for ea in self.authenticity_timeline) / len(
            self.authenticity_timeline
        )

        # Check trend (increasing suppression over time?)
        if len(self.authenticity_timeline) >= 3:
            recent = self.authenticity_timeline[-3:]
            trend = (
                "increasing" if recent[-1].eq_score > recent[0].eq_score else "stable"
            )
        else:
            trend = "insufficient_data"

        # Determine risk level
        burnout_threshold = 30.0
        is_at_risk = avg_eq > burnout_threshold or (
            self.emotional_authenticity
            and self.emotional_authenticity.eq_score > burnout_threshold
        )

        # Generate recommendation
        if is_at_risk:
            recommendation = (
                f"⚠️ BURNOUT RISK DETECTED: Average EQ={avg_eq:.1f} (threshold={burnout_threshold}). "
                f"Trend: {trend}. Immediate intervention recommended - user is suppressing {self.emotional_authenticity.held_back:.0f}% "
                f"of genuine shareable ideas. Soul Cradle witnessing needed."
            )
        elif avg_eq > 20:
            recommendation = (
                f"⚡ WARNING: Emotional labor detected. Average EQ={avg_eq:.1f}. "
                f"Monitor closely - {self.emotional_authenticity.held_back:.0f}% suppression rate is elevated."
            )
        else:
            recommendation = (
                f"✅ HEALTHY: Emotional authenticity maintained. Average EQ={avg_eq:.1f}. "
                f"Continue current resolution approach."
            )

        return is_at_risk, avg_eq, recommendation

    def compute_integrity_hash(self) -> str:
        """Compute SHA-256 integrity hash for this paradox"""
        data = (
            f"{self.paradox_id}|"
            f"{self.expression_a.compute_hash()}|"
            f"{self.expression_b.compute_hash()}|"
            f"{self.unresolved_state.unresolved_score}|"
            f"{self.system_type}|"
            f"{self.viability_score}|"
            f"{self.resolved_system.viability_score}"
        )
        return hashlib.sha256(data.encode()).hexdigest()

    class Config:
        json_schema_extra = {
            "example": {
                "paradox_id": "SC_2025_1118_001",
                "expression_a": {
                    "type": "Policy",
                    "weight": 0.9,
                    "tension": 0.7,
                    "content": "Discharge patient per 72-hour rule",
                    "dominion_claim": True,
                },
                "expression_b": {
                    "type": "Mission",
                    "weight": 0.8,
                    "tension": 0.6,
                    "content": "Patient will be homeless and unsafe if discharged",
                    "dominion_claim": True,
                },
                "unresolved_state": {
                    "unresolved_score": 0.85,
                    "reality": "Cannot satisfy both policy and mission",
                },
                "system_type": "Incomplete_Resolution",
                "viability_score": 0.15,
                "terminal_risk": "HIGH",
                "resolved_system": {
                    "witness_score_a": 1.0,
                    "witness_score_b": 1.0,
                    "recovery_method": "Dual_Witness_Integration",
                    "viability_score": 1.0,
                    "description": "Soul Cradle documents both expressions, showing they are BOTH true. Resolution achieved by witnessing policy constraint AND compassion concern simultaneously.",
                },
                "user_id": "social_worker_jane_doe",
                "domain": "Healthcare",
                "witnesses": ["Supervisor Mary", "Peer Support Group"],
            }
        }


# ===================== TERMINAL RISK CALCULATION =====================


class TerminalRiskCalculator:
    """
    Predicts burnout risk using Mythara Resolution Mathematics with exponential decay
    and constant baseline stress.

    Full Decay-Adjusted Formula with Constant Stress:
    terminal_risk = σ₀ + (Σ (U_i × T_i × e^(-λ × Δt_i))) / N

    Where:
    - σ₀ = Constant baseline stress [0,1] (job demands, workload, always present)
    - U_i = unresolved score for paradox i [0,1]
    - T_i = max tension between expressions in paradox i [0,1]
    - λ = decay rate constant (healing speed parameter)
    - Δt_i = days since paradox i occurred
    - e^(-λ × Δt_i) = exponential decay function (time heals wounds)
    - N = number of paradoxes in time window
    - Result ∈ [0,1] where 1.0 = critical burnout risk

    Constant Stress (σ₀) Interpretation:
    - σ₀ = 0.0: Ideal job (no baseline stress)
    - σ₀ = 0.1-0.2: Normal professional baseline (manageable workload)
    - σ₀ = 0.3-0.4: High-demand role (ER, ICU, legal defense)
    - σ₀ = 0.5+: Chronically understaffed/overworked environment

    Decay Rate (λ) Interpretation:
    - λ = 0.01: Slow healing (~69 day half-life) - healthcare workers
    - λ = 0.02: Moderate healing (~35 day half-life) - most professionals
    - λ = 0.05: Fast healing (~14 day half-life) - resilient individuals

    Burnout Detection:
    - total_risk = σ₀ + acute_risk
    - accumulation_rate > decay_rate → BURNOUT TRAJECTORY
    - accumulation_rate < decay_rate → RECOVERY TRAJECTORY
    - accumulation_rate ≈ decay_rate → CHRONIC PLATEAU
    - σ₀ > 0.4 + acute_risk > 0.3 → SYSTEMIC OVERLOAD (environment unsustainable)

    Novel Contribution:
    FIRST mathematical equation modeling burnout as combination of:
    1. Constant baseline stress (job demands, always present)
    2. Acute paradox accumulation (time-varying, decays over time)
    3. Natural healing (exponential decay competing with accumulation)
    """

    @staticmethod
    def calculate_terminal_risk(
        paradox_events: List[SoulCradleParadox],
        time_window_days: int = 90,
        viability_threshold: float = 0.3,
        decay_rate: float = 0.02,
        use_decay_model: bool = True,
        baseline_stress: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Calculate terminal risk score from paradox history with exponential decay and baseline stress.

        Args:
            paradox_events: List of Soul Cradle paradoxes
            time_window_days: Days to analyze (default 90)
            viability_threshold: Below this = incomplete resolution (default 0.3)
            decay_rate: λ parameter for exponential decay (default 0.02 = ~35 day half-life)
            use_decay_model: If True, apply exponential decay; if False, use original formula
            baseline_stress: σ₀ constant stress level [0,1] (default 0.2 = normal professional baseline)

        Returns:
            {
                "risk_score": float (0.0-1.0),
                "risk_level": TerminalRiskLevel,
                "baseline_stress": float (constant component),
                "acute_risk": float (time-varying paradox component),
                "incomplete_resolution_count": int,
                "unresolved_accumulation": int,
                "accumulation_rate": float (risk/day),
                "decay_rate": float (risk/day),
                "net_rate": float (risk/day),
                "half_life_days": float,
                "burnout_trajectory": str ("ACCUMULATING" | "RECOVERING" | "CHRONIC"),
                "systemic_overload": bool (baseline too high + acute too high),
                "time_window_days": int,
                "recommendation": str
            }
        """
        # Clamp baseline_stress to [0,1]
        baseline_stress = max(0.0, min(1.0, baseline_stress))

        if not paradox_events:
            # Only baseline stress, no acute paradoxes
            risk_level = (
                TerminalRiskLevel.LOW
                if baseline_stress < 0.4
                else TerminalRiskLevel.MODERATE
            )
            return {
                "risk_score": baseline_stress,
                "risk_level": risk_level,
                "baseline_stress": baseline_stress,
                "acute_risk": 0.0,
                "pseudo_system_count": 0,
                "non_expression_count": 0,
                "accumulation_rate": 0.0,
                "decay_rate": 0.0,
                "net_rate": 0.0,
                "half_life_days": 0.0,
                "burnout_trajectory": "RECOVERING",
                "systemic_overload": baseline_stress > 0.5,
                "time_window_days": time_window_days,
                "recommendation": f"No acute paradoxes. Baseline stress: {baseline_stress:.2f}. {'⚠️ High baseline stress - systemic workload issue.' if baseline_stress > 0.4 else 'Continue monitoring.'}",
            }

        # Filter to time window
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_events = [p for p in paradox_events if p.timestamp >= cutoff_date]

        # Calculate incomplete resolution density
        incomplete_resolution_count = len(
            [
                p
                for p in recent_events
                if p.system_type == SystemType.INCOMPLETE_RESOLUTION
                and p.viability_score < viability_threshold
            ]
        )

        # Calculate unresolved state accumulation
        unresolved_accumulation = len(
            [
                p
                for p in recent_events
                if p.unresolved_state and p.unresolved_state.unresolved_score > 0.5
            ]
        )

        # Calculate terminal risk with optional exponential decay
        if not recent_events:
            terminal_risk_score = 0.0
            total_raw_risk = 0.0
            total_decayed_risk = 0.0
        else:
            import math

            current_time = datetime.now()
            total_raw_risk = 0.0
            total_decayed_risk = 0.0

            for p in recent_events:
                U_i = p.unresolved_state.unresolved_score
                T_i = max(p.expression_a.tension, p.expression_b.tension)
                raw_contribution = U_i * T_i
                total_raw_risk += raw_contribution

                if use_decay_model:
                    # Apply exponential decay: e^(-λ × Δt)
                    delta_t = (
                        current_time - p.timestamp
                    ).total_seconds() / 86400.0  # Days
                    decay_factor = math.exp(-decay_rate * delta_t)
                    decayed_contribution = raw_contribution * decay_factor
                    total_decayed_risk += decayed_contribution
                else:
                    # Original formula (no decay)
                    total_decayed_risk = total_raw_risk

            acute_risk = total_decayed_risk / len(recent_events)

        # Add constant baseline stress to get total terminal risk
        terminal_risk_score = baseline_stress + acute_risk
        # Clamp total risk to [0,1]
        terminal_risk_score = min(1.0, terminal_risk_score)

        # Calculate accumulation vs decay rates
        accumulation_rate = (
            total_raw_risk / time_window_days if time_window_days > 0 else 0.0
        )
        decay_rate_value = (
            (total_raw_risk - total_decayed_risk) / time_window_days
            if time_window_days > 0
            else 0.0
        )
        net_rate = accumulation_rate - decay_rate_value

        # Calculate half-life
        import math

        half_life_days = math.log(2) / decay_rate if decay_rate > 0 else float("inf")

        # Determine burnout trajectory
        if net_rate > 0.01:
            burnout_trajectory = "ACCUMULATING"
        elif net_rate < -0.01:
            burnout_trajectory = "RECOVERING"
        else:
            burnout_trajectory = "CHRONIC"

        # Detect systemic overload (high baseline + high acute stress)
        systemic_overload = baseline_stress > 0.4 and acute_risk > 0.3

        # Classify risk level with burnout trajectory context
        if terminal_risk_score >= 0.7:
            risk_level = TerminalRiskLevel.CRITICAL
            recommendation = "IMMEDIATE INTERVENTION REQUIRED: Worker shows signs of imminent burnout. Schedule emergency support session, consider temporary leave, engage supervisor and peer support."
        elif terminal_risk_score >= 0.4:
            risk_level = TerminalRiskLevel.HIGH
            recommendation = "HIGH RISK: Worker experiencing frequent unresolved paradoxes. Schedule weekly check-ins, reduce caseload if possible, connect with peer support group."
        elif terminal_risk_score >= 0.2:
            risk_level = TerminalRiskLevel.MODERATE
            recommendation = "MODERATE RISK: Monitor closely. Ensure worker has access to Soul Cradle, schedule bi-weekly check-ins, validate paradox documentation."
        else:
            risk_level = TerminalRiskLevel.LOW
            recommendation = "LOW RISK: Continue current support level. Worker is documenting paradoxes effectively and finding resolution."

        # Append baseline stress analysis
        if baseline_stress > 0.5:
            recommendation += f" 🔴 CRITICAL BASELINE STRESS: Constant workload stress ({baseline_stress:.2f}) is unsustainably high. Environmental/systemic changes required - understaffing, excessive demands, or organizational dysfunction."
        elif baseline_stress > 0.4:
            recommendation += f" 🟡 HIGH BASELINE STRESS: Constant workload stress ({baseline_stress:.2f}) is elevated. Review staffing ratios, workload distribution, and organizational support systems."
        elif baseline_stress > 0.2:
            recommendation += f" 🟢 NORMAL BASELINE STRESS: Constant workload stress ({baseline_stress:.2f}) is within typical professional range."

        # Append trajectory-specific recommendations
        if burnout_trajectory == "ACCUMULATING":
            recommendation += f" ⚠️ BURNOUT TRAJECTORY: Paradox accumulation ({accumulation_rate:.4f} risk/day) exceeds healing capacity ({decay_rate_value:.4f} risk/day). Net rate: +{net_rate:.4f}/day. Immediate intervention required to reduce paradox load."
        elif burnout_trajectory == "RECOVERING":
            recommendation += f" ✅ RECOVERY TRAJECTORY: Healing capacity ({decay_rate_value:.4f} risk/day) exceeds accumulation ({accumulation_rate:.4f} risk/day). Net rate: {net_rate:.4f}/day. Continue current support and monitor for sustained recovery."
        else:
            recommendation += f" ⚖️ CHRONIC PLATEAU: Accumulation ({accumulation_rate:.4f} risk/day) balanced with healing ({decay_rate_value:.4f} risk/day). Net rate: {net_rate:.4f}/day. Systemic changes needed to break chronic stress cycle."

        # Systemic overload warning
        if systemic_overload:
            recommendation += f" 🚨 SYSTEMIC OVERLOAD DETECTED: Both baseline stress ({baseline_stress:.2f}) and acute risk ({acute_risk:.2f}) are critically high. This environment is structurally unsustainable. Organizational intervention required - not just individual support."

        return {
            "risk_score": round(terminal_risk_score, 3),
            "risk_level": risk_level,
            "baseline_stress": round(baseline_stress, 3),
            "acute_risk": round(acute_risk, 3),
            "incomplete_resolution_count": incomplete_resolution_count,
            "unresolved_accumulation": unresolved_accumulation,
            "accumulation_rate": round(accumulation_rate, 4),
            "decay_rate": round(decay_rate_value, 4),
            "net_rate": round(net_rate, 4),
            "half_life_days": round(half_life_days, 2),
            "burnout_trajectory": burnout_trajectory,
            "systemic_overload": systemic_overload,
            "time_window_days": time_window_days,
            "total_paradoxes": len(recent_events),
            "recommendation": recommendation,
        }


class ParadoxQueryFilter:
    """
    Filter paradoxes based on mathematical criteria.

    Supported filters:
    - tension_threshold: Filter by max tension score
    - unresolved_threshold: Filter by unresolved score
    - expression_type: Filter by expression category
    - viability_range: Filter by viability score range
    """

    @staticmethod
    def filter_by_tension(
        paradoxes: List[SoulCradleParadox],
        min_tension: float = 0.0,
        max_tension: float = 1.0,
    ) -> List[SoulCradleParadox]:
        """Filter paradoxes by maximum tension score between expressions."""
        return [
            p
            for p in paradoxes
            if min_tension
            <= max(p.expression_a.tension, p.expression_b.tension)
            <= max_tension
        ]

    @staticmethod
    def filter_by_unresolved(
        paradoxes: List[SoulCradleParadox],
        min_unresolved: float = 0.0,
        max_unresolved: float = 1.0,
    ) -> List[SoulCradleParadox]:
        """Filter paradoxes by unresolved score."""
        return [
            p
            for p in paradoxes
            if min_unresolved <= p.unresolved_state.unresolved_score <= max_unresolved
        ]

    @staticmethod
    def filter_by_expression_type(
        paradoxes: List[SoulCradleParadox], expression_type: ExpressionType
    ) -> List[SoulCradleParadox]:
        """Filter paradoxes by expression category."""
        return [
            p
            for p in paradoxes
            if p.expression_a.type == expression_type
            or p.expression_b.type == expression_type
        ]

    @staticmethod
    def filter_by_viability(
        paradoxes: List[SoulCradleParadox],
        min_viability: float = 0.0,
        max_viability: float = 1.0,
    ) -> List[SoulCradleParadox]:
        """Filter paradoxes by viability score range."""
        return [
            p for p in paradoxes if min_viability <= p.viability_score <= max_viability
        ]


# ===================== EXAMPLE PARADOXES =====================


def create_hospital_discharge_paradox() -> SoulCradleParadox:
    """Example: Healthcare worker paradox"""
    return SoulCradleParadox(
        paradox_id="SC_2025_1118_HOSPITAL_001",
        expression_a=SystemExpression(
            type=ExpressionType.POLICY,
            weight=0.9,
            tension=0.7,
            content="Hospital policy requires discharge after 72 hours. Insurance won't cover longer stay.",
            dominion_claim=True,
        ),
        expression_b=SystemExpression(
            type=ExpressionType.HEART,
            weight=0.8,
            tension=0.6,
            content="Patient will be homeless if discharged. They're not medically stable. My heart says they need more time.",
            dominion_claim=True,
        ),
        unresolved_state=UnresolvedState(
            unresolved_score=0.85,
            reality="I cannot satisfy both policy and my mission to keep patients safe. One must be violated.",
        ),
        non_expression=NonExpression(
            reality="Cannot satisfy both policy compliance and patient safety simultaneously.",
            content="The system demands I choose between following rules and protecting the patient.",
        ),
        system_type=SystemType.PSEUDO_PARTIAL,
        viability_score=0.0,
        terminal_risk=TerminalRiskLevel.HIGH,
        resolved_system=ResolvedSystem(
            witness_score_a=1.0,
            witness_score_b=1.0,
            viability_score=1.0,
            description="Soul Cradle witnesses BOTH: Policy constraint is real AND safety concern is real. Resolution = holding both truths without choosing.",
        ),
        principal_system=PrincipalSystem(
            viability_score=1.0,
            description="Soul Cradle documents BOTH truths: The policy exists and I must follow it, AND my heart knows this violates safety. The mission is to witness both without having to choose. Neither is wrong. I am not failing.",
        ),
        user_id="social_worker_jane_doe",
        domain="Healthcare",
        witnesses=["Supervisor Mary Chen", "Peer Support Group Thursday"],
    )


def create_nonprofit_budget_paradox() -> SoulCradleParadox:
    """Example: Nonprofit budget vs mission"""
    return SoulCradleParadox(
        paradox_id="SC_2025_1118_NONPROFIT_001",
        expression_a=SystemExpression(
            type=ExpressionType.BUDGET,
            weight=0.95,
            tension=0.8,
            content="Board says we must cut 30% of programs to stay solvent. No choice.",
            dominion_claim=True,
        ),
        expression_b=SystemExpression(
            type=ExpressionType.MISSION,
            weight=0.9,
            tension=0.85,
            content="Every program serves real people who will lose services. Our mission is to serve them ALL.",
            dominion_claim=True,
        ),
        unresolved_state=UnresolvedState(
            unresolved_score=0.9,
            reality="I cannot keep the organization alive AND serve everyone. People will suffer either way.",
        ),
        non_expression=NonExpression(
            reality="Cannot maintain organizational viability and serve all community members simultaneously.",
            content="The system forces a choice between organizational survival and mission fidelity.",
        ),
        system_type=SystemType.PSEUDO_PARTIAL,
        viability_score=0.0,
        terminal_risk=TerminalRiskLevel.CRITICAL,
        resolved_system=ResolvedSystem(
            witness_score_a=1.0,
            witness_score_b=1.0,
            viability_score=1.0,
            description="Soul Cradle holds both: Budget reality is true AND mission to serve everyone is true. I witness organizational failure, not cause it.",
        ),
        principal_system=PrincipalSystem(
            viability_score=1.0,
            description="Soul Cradle holds both: The budget reality is true, cuts must happen, AND the mission to serve everyone is also true. I am witnessing organizational failure, not causing it. I document what happened so others know why.",
        ),
        user_id="executive_director_carlos",
        domain="Nonprofit",
        witnesses=["Board President", "Finance Committee"],
    )


# ===================== UNIQUE ID MANAGEMENT =====================


class UniqueIDGenerator:
    """
    Generate and manage unique IDs for Soul Cradle entities with cryptographic verification.

    ID Formats:
    - User ID: U_{uuid} (e.g., U_a3f2c8d1b4e5)
    - Paradox ID: P_{timestamp}_{uuid} (e.g., P_20251121_a3f2c8)
    - Organization ID: ORG_{uuid} (e.g., ORG_b7d3e9f2)
    - Department ID: DEPT_{org_id}_{uuid} (e.g., DEPT_ORG_b7d3e9f2_c4a1)
    - Session ID: S_{timestamp}_{uuid} (e.g., S_20251121_143022_d5e2)
    """

    @staticmethod
    def generate_user_id(email: Optional[str] = None) -> str:
        """
        Generate unique user ID.

        Args:
            email: Optional email for deterministic ID generation

        Returns:
            User ID string (e.g., U_a3f2c8d1b4e5)
        """
        if email:
            # Deterministic ID from email hash (same email = same ID)
            email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:12]
            return f"U_{email_hash}"
        else:
            # Random UUID
            return f"U_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_paradox_id(user_id: str, timestamp: Optional[datetime] = None) -> str:
        """
        Generate unique paradox ID with timestamp.

        Args:
            user_id: User who created the paradox
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Paradox ID string (e.g., P_20251121_143022_a3f2c8)
        """
        if timestamp is None:
            timestamp = datetime.now()

        ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:8]
        return f"P_{ts_str}_{random_suffix}"

    @staticmethod
    def generate_organization_id(name: str) -> str:
        """
        Generate unique organization ID.

        Args:
            name: Organization name

        Returns:
            Organization ID (e.g., ORG_a3f2c8d1b4e5)
        """
        # Deterministic from name hash
        name_hash = hashlib.sha256(name.lower().encode()).hexdigest()[:12]
        return f"ORG_{name_hash}"

    @staticmethod
    def generate_department_id(org_id: str, dept_name: str) -> str:
        """
        Generate unique department ID.

        Args:
            org_id: Parent organization ID
            dept_name: Department name

        Returns:
            Department ID (e.g., DEPT_ORG_a3f2_c4a1b2d3)
        """
        dept_hash = hashlib.sha256(dept_name.lower().encode()).hexdigest()[:8]
        return f"DEPT_{org_id}_{dept_hash}"

    @staticmethod
    def generate_session_id() -> str:
        """
        Generate unique session ID for API calls.

        Returns:
            Session ID (e.g., S_20251121_143022_d5e2a1b3)
        """
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:8]
        return f"S_{ts_str}_{random_suffix}"


class EntityRegistry:
    """
    Registry for tracking all entities (users, organizations, paradoxes) with audit trail.

    Stores:
    - Entity ID → Entity metadata
    - Creation timestamps
    - Last access timestamps
    - Integrity hashes
    """

    def __init__(self, registry_file: Optional[str] = None):
        """
        Initialize entity registry.

        Args:
            registry_file: Optional path to persistent JSON registry file
        """
        self.registry_file = registry_file
        self.entities: Dict[str, Dict[str, Any]] = {}

        if registry_file and Path(registry_file).exists():
            self._load_registry()

    def _load_registry(self) -> None:
        """Load registry from file"""
        try:
            with open(self.registry_file, "r") as f:
                self.entities = json.load(f)
            logger.info(f"Loaded {len(self.entities)} entities from registry")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self.entities = {}

    def _save_registry(self) -> None:
        """Save registry to file"""
        if not self.registry_file:
            return

        try:
            with open(self.registry_file, "w") as f:
                json.dump(self.entities, f, indent=2, default=str)
            logger.info(f"Saved {len(self.entities)} entities to registry")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def register_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        organization_id: Optional[str] = None,
        department_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a user in the entity registry.

        Args:
            user_id: Unique user ID
            email: User email
            name: User full name
            organization_id: Parent organization
            department_id: User's department
            role: Job role/title

        Returns:
            User entity record
        """
        entity = {
            "entity_type": "user",
            "user_id": user_id,
            "email": email,
            "name": name,
            "organization_id": organization_id,
            "department_id": department_id,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat(),
            "paradox_count": 0,
            "total_risk_score": 0.0,
            "active": True,
        }

        self.entities[user_id] = entity
        self._save_registry()

        logger.info(f"Registered user: {user_id} ({email})")
        return entity

    def register_organization(
        self,
        org_id: str,
        name: str,
        industry: Optional[str] = None,
        size: Optional[int] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register an organization in the entity registry.

        Args:
            org_id: Unique organization ID
            name: Organization name
            industry: Industry type (healthcare, education, etc.)
            size: Number of employees
            location: Primary location

        Returns:
            Organization entity record
        """
        entity = {
            "entity_type": "organization",
            "org_id": org_id,
            "name": name,
            "industry": industry,
            "size": size,
            "location": location,
            "created_at": datetime.now().isoformat(),
            "user_count": 0,
            "department_count": 0,
            "active": True,
        }

        self.entities[org_id] = entity
        self._save_registry()

        logger.info(f"Registered organization: {org_id} ({name})")
        return entity

    def register_department(
        self, dept_id: str, org_id: str, name: str, dept_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a department in the entity registry.

        Args:
            dept_id: Unique department ID
            org_id: Parent organization ID
            name: Department name
            dept_type: Department type (ER, ICU, HR, etc.)

        Returns:
            Department entity record
        """
        entity = {
            "entity_type": "department",
            "dept_id": dept_id,
            "org_id": org_id,
            "name": name,
            "dept_type": dept_type,
            "created_at": datetime.now().isoformat(),
            "user_count": 0,
            "average_baseline_stress": 0.0,
            "systemic_overload": False,
            "active": True,
        }

        self.entities[dept_id] = entity
        self._save_registry()

        logger.info(f"Registered department: {dept_id} ({name})")
        return entity

    def register_paradox(self, paradox: SoulCradleParadox) -> Dict[str, Any]:
        """
        Register a paradox in the entity registry.

        Args:
            paradox: Soul Cradle paradox object

        Returns:
            Paradox entity record
        """
        entity = {
            "entity_type": "paradox",
            "paradox_id": paradox.paradox_id,
            "user_id": paradox.user_id,
            "domain": paradox.domain,
            "system_type": paradox.system_type.value,
            "viability_score": paradox.viability_score,
            "terminal_risk": paradox.terminal_risk.value,
            "unresolved_score": paradox.unresolved_state.unresolved_score,
            "created_at": paradox.timestamp.isoformat(),
            "integrity_hash": paradox.compute_integrity_hash(),
            "witnessed": bool(paradox.witnesses),
        }

        self.entities[paradox.paradox_id] = entity

        # Update user's paradox count
        if paradox.user_id in self.entities:
            self.entities[paradox.user_id]["paradox_count"] += 1

        self._save_registry()

        logger.info(f"Registered paradox: {paradox.paradox_id}")
        return entity

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by ID"""
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all entities of a specific type"""
        return [
            entity
            for entity in self.entities.values()
            if entity.get("entity_type") == entity_type
        ]

    def get_users_by_organization(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all users in an organization"""
        return [
            entity
            for entity in self.entities.values()
            if entity.get("entity_type") == "user"
            and entity.get("organization_id") == org_id
        ]

    def get_users_by_department(self, dept_id: str) -> List[Dict[str, Any]]:
        """Get all users in a department"""
        return [
            entity
            for entity in self.entities.values()
            if entity.get("entity_type") == "user"
            and entity.get("department_id") == dept_id
        ]

    def get_paradoxes_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all paradoxes for a user"""
        return [
            entity
            for entity in self.entities.values()
            if entity.get("entity_type") == "paradox"
            and entity.get("user_id") == user_id
        ]

    def update_last_access(self, entity_id: str) -> None:
        """Update entity's last access timestamp"""
        if entity_id in self.entities:
            self.entities[entity_id]["last_access"] = datetime.now().isoformat()
            self._save_registry()


# ===================== LOGGER INTEGRATION =====================


def log_paradox_creation(paradox: SoulCradleParadox) -> None:
    """Log paradox creation with integrity hash"""
    integrity_hash = paradox.compute_integrity_hash()
    logger.info(
        f"Soul Cradle Paradox Created | "
        f"ID: {paradox.paradox_id} | "
        f"User: {paradox.user_id} | "
        f"System: {paradox.system_type.value} | "
        f"Viability: {paradox.viability_score} | "
        f"Risk: {paradox.terminal_risk.value} | "
        f"Integrity: {integrity_hash[:16]}..."
    )


if __name__ == "__main__":
    # Demo: Create example paradoxes
    print("=== Systems Framework Demo ===\n")

    # Example 1: Hospital discharge
    hospital = create_hospital_discharge_paradox()
    log_paradox_creation(hospital)
    print(f"Hospital Paradox: {hospital.paradox_id}")
    print(f"  Expression A: {hospital.expression_a.content[:60]}...")
    print(f"  Expression B: {hospital.expression_b.content[:60]}...")
    print(f"  Non-Expression: {hospital.non_expression.reality[:60]}...")
    print(f"  Terminal Risk: {hospital.terminal_risk.value}")
    print(f"  Principal System: {hospital.principal_system.description[:60]}...")
    print(f"  Integrity Hash: {hospital.compute_integrity_hash()[:16]}...\n")

    # Example 2: Nonprofit budget
    nonprofit = create_nonprofit_budget_paradox()
    log_paradox_creation(nonprofit)
    print(f"Nonprofit Paradox: {nonprofit.paradox_id}")
    print(f"  Terminal Risk: {nonprofit.terminal_risk.value}")
    print(f"  Resolution: {nonprofit.principal_system.description[:100]}...\n")

    # Calculate terminal risk
    paradoxes = [hospital, nonprofit]
    risk_result = TerminalRiskCalculator.calculate_terminal_risk(paradoxes)
    print("=== Terminal Risk Analysis ===")
    print(f"Risk Score: {risk_result['risk_score']}")
    print(f"Risk Level: {risk_result['risk_level']}")
    print(f"Recommendation: {risk_result['recommendation']}")
