#!/usr/bin/env python3
"""
Mythara Engine — Dual Framing Translation Layer
Copyright © 2025 Herbert Velez Jr. All rights reserved.

This module provides a translation layer between Mythara's mythic truth
and industry-safe terminology for enterprise audiences. The engine remains
unchanged — this simply provides an overlay for external communication.

Purpose:
- Preserve mythic integrity of Blessings Reservoir, Soul Encoding, etc.
- Provide enterprise-safe terminology (Resonance Reservoir, Trust Index, etc.)
- Enable manager dashboards to toggle between mythic and industry framing
- Maintain compliance and workflow compatibility for external systems

Flow:
    System of Record (CRM/Field Platform)
    ↓
    Mythara Engine Overlay
    - Blessings Reservoir → Resonance Reservoir
    - Integrity Metric → Trust Index
    - Expression Metric → Engagement Index
    ↓
    Manager Dashboards
    - KPIs + Resonance Metrics side by side
    - Compliance intact, workflows unchanged
    - Adds symbolic depth to performance reporting
"""

from typing import Dict, Any, List
from enum import Enum


class FramingMode(str, Enum):
    """Framing modes for Mythara Engine terminology."""

    MYTHIC = "mythic"  # Internal truth: Blessings Reservoir, Soul Encoding, etc.
    INDUSTRY = "industry"  # External overlay: Resonance Reservoir, Trust Index, etc.
    LEGAL = "legal"  # Adjudicatory voice: findings, holdings, attested record.
    PLAIN = "plain"  # Plain speak: direct, human, no jargon.


# Core dual-framing mapping: Mythic Truth → Industry-Safe Overlay
MYTHIC_TO_INDUSTRY: Dict[str, Dict[str, str]] = {
    "blessings_reservoir": {
        "industry_term": "Resonance Reservoir",
        "managerial_explanation": "Tracks cumulative benevolent force; externally framed as cumulative positive impact.",
        "mythic_term": "Blessings Reservoir",
        "category": "metric",
    },
    "integrity_metric": {
        "industry_term": "Trust Index",
        "managerial_explanation": "Measures alignment with compliance, honesty, and reliability in field performance.",
        "mythic_term": "Integrity Metric",
        "category": "metric",
    },
    "expression_metric": {
        "industry_term": "Engagement Index",
        "managerial_explanation": "Captures how reps present, connect, and resonate with clients beyond raw numbers.",
        "mythic_term": "Expression Metric",
        "category": "metric",
    },
    "soul_encoding": {
        "industry_term": "Impact Vault",
        "managerial_explanation": "Stores symbolic depth of actions; externally framed as measurable long-term impact.",
        "mythic_term": "Soul Encoding",
        "category": "concept",
    },
    "legacy_reservoir": {
        "industry_term": "Continuity Index",
        "managerial_explanation": "Reflects sustainability and cultural resonance; externally framed as continuity of performance.",
        "mythic_term": "Legacy Reservoir",
        "category": "metric",
    },
    "soul_cradle_operator": {
        "industry_term": "Resonance Operator",
        "managerial_explanation": "Measures obedience under paradox; externally framed as decision-making integrity under pressure.",
        "mythic_term": "Soul Cradle Operator",
        "category": "operator",
    },
    "trial_entity": {
        "industry_term": "Challenge Vector",
        "managerial_explanation": "Models testing/obscuration of choices; externally framed as decision friction factors.",
        "mythic_term": "Trial Entity",
        "category": "entity",
    },
    "grace_light": {
        "industry_term": "Optimal Performance",
        "managerial_explanation": "Biblical continuum anchor representing peak alignment and positive outcomes.",
        "mythic_term": "Grace/Light",
        "category": "continuum",
    },
    "wilderness_darkness": {
        "industry_term": "Challenge State",
        "managerial_explanation": "Biblical continuum anchor representing trial, testing, or suboptimal conditions.",
        "mythic_term": "Wilderness/Darkness",
        "category": "continuum",
    },
    "divine_drift_suppression": {
        "industry_term": "Compliance Stability",
        "managerial_explanation": "Measures drift from sacred mission; externally framed as operational compliance stability.",
        "mythic_term": "Divine Drift Suppression",
        "category": "ssip_metric",
    },
    "messenger_pairing_fidelity": {
        "industry_term": "Communication Alignment",
        "managerial_explanation": "Measures alignment between action and communication; externally framed as message consistency.",
        "mythic_term": "Messenger Pairing Fidelity",
        "category": "ssip_metric",
    },
    "emotional_fidelity": {
        "industry_term": "Sentiment Accuracy",
        "managerial_explanation": "Measures symbolic-emotional resonance; externally framed as sentiment tracking precision.",
        "mythic_term": "Emotional Fidelity",
        "category": "ssip_metric",
    },
}


def translate_term(
    mythic_key: str,
    mode: FramingMode = FramingMode.PLAIN,
    include_explanation: bool = False,
) -> str:
    """
    Translate a mythic term into the requested voice.

    Args:
        mythic_key: Key from MYTHIC_TO_INDUSTRY (e.g., "blessings_reservoir")
        mode: PLAIN (default, direct human words), MYTHIC (preserve),
            or INDUSTRY (enterprise-safe terms)
        include_explanation: If True, append explanation to the term
            (industry mode: managerial explanation; plain mode: plain explanation)

    Returns:
        Translated term string

    Example:
        >>> translate_term("blessings_reservoir")
        'Reserve'
        >>> translate_term("blessings_reservoir", FramingMode.INDUSTRY)
        'Resonance Reservoir'
        >>> translate_term("blessings_reservoir", FramingMode.MYTHIC)
        'Blessings Reservoir'
    """
    if mode == FramingMode.PLAIN:
        entry = MYTHIC_TO_PLAIN.get(mythic_key)
        if entry is None:
            return mythic_key  # Passthrough if not in mapping
        term = entry["plain_term"]
        if include_explanation:
            return f"{term} — {entry['plain_explanation']}"
        return term

    if mythic_key not in MYTHIC_TO_INDUSTRY:
        return mythic_key  # Passthrough if not in mapping

    entry = MYTHIC_TO_INDUSTRY[mythic_key]

    if mode == FramingMode.MYTHIC:
        return entry["mythic_term"]

    # mode == FramingMode.INDUSTRY
    term = entry["industry_term"]
    if include_explanation:
        return f"{term} — {entry['managerial_explanation']}"
    return term


def translate_response(
    response_data: Dict[str, Any], mode: FramingMode = FramingMode.PLAIN
) -> Dict[str, Any]:
    """
    Recursively translate mythic keys in a response dictionary.

    Args:
        response_data: API response dictionary with mythic keys
        mode: PLAIN (default, direct human words), MYTHIC (preserve),
            or INDUSTRY (enterprise-safe terms)

    Returns:
        Translated response dictionary

    Example:
        >>> data = {"blessings_reservoir": 145, "integrity_metric": 0.95}
        >>> translate_response(data)
        {'reserve': 145, 'integrity_metric': 0.95}
        >>> translate_response(data, FramingMode.INDUSTRY)
        {'resonance_reservoir': 145, 'trust_index': 0.95}
    """
    if mode == FramingMode.MYTHIC:
        return response_data  # No translation needed

    if mode == FramingMode.PLAIN:
        mapping = MYTHIC_TO_PLAIN
        term_key = "plain_term"
    else:
        # mode == FramingMode.INDUSTRY
        mapping = MYTHIC_TO_INDUSTRY
        term_key = "industry_term"

    translated = {}
    for key, value in response_data.items():
        # Check if key should be translated
        new_key = key
        # integrity_hash is a machine integrity field required by API response
        # contracts and tests — never rename it, in any framing mode.
        if key != "integrity_hash" and key in mapping:
            term = mapping[key][term_key]
            # Convert "Reserve" → "reserve", "Your Principles" → "your_principles"
            new_key = term.lower().replace(" ", "_")

        # Recursively translate nested dicts
        if isinstance(value, dict):
            translated[new_key] = translate_response(value, mode)
        elif isinstance(value, list):
            translated[new_key] = [
                translate_response(item, mode) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            translated[new_key] = value

    return translated


def generate_dual_framing_chart() -> List[Dict[str, str]]:
    """
    Generate the dual-framing chart for documentation/presentations.

    Returns:
        List of dicts with columns: mythic_term, industry_term, managerial_explanation

    Example output (first row):
        {
            "mythic_term": "Blessings Reservoir",
            "industry_term": "Resonance Reservoir",
            "managerial_explanation": "Tracks cumulative benevolent force; ..."
        }
    """
    chart = []
    for key, entry in MYTHIC_TO_INDUSTRY.items():
        chart.append(
            {
                "mythic_term": entry["mythic_term"],
                "industry_term": entry["industry_term"],
                "managerial_explanation": entry["managerial_explanation"],
                "category": entry["category"],
            }
        )
    return chart


def format_for_manager_dashboard(
    metrics: Dict[str, Any],
    mode: FramingMode = FramingMode.PLAIN,
    include_kpis: bool = True,
) -> Dict[str, Any]:
    """
    Format metrics for manager dashboards with dual-framing support.

    Args:
        metrics: Raw metrics dict (mythic keys)
        mode: PLAIN (default), MYTHIC, or INDUSTRY framing
        include_kpis: If True, include standard KPIs alongside resonance metrics

    Returns:
        Formatted dashboard dict

    Example:
        >>> metrics = {
        ...     "blessings_reservoir": 145,
        ...     "integrity_metric": 0.95,
        ...     "expression_metric": 0.88
        ... }
        >>> format_for_manager_dashboard(metrics, FramingMode.INDUSTRY)
        {
            "resonance_metrics": {
                "resonance_reservoir": 145,
                "trust_index": 0.95,
                "engagement_index": 0.88
            },
            "kpis": {...},
            "framing_mode": "industry"
        }
    """
    dashboard = {
        "resonance_metrics": translate_response(metrics, mode),
        "framing_mode": mode.value,
        "compliance_note": "Compliance intact, workflows unchanged. Symbolic depth added to performance reporting.",
    }

    if include_kpis:
        # Placeholder for standard KPIs from CRM/field platform
        dashboard["kpis"] = {
            "note": "Standard KPIs from system of record appear here alongside resonance metrics."
        }

    return dashboard


def get_positioning_line() -> str:
    """
    Return the standard positioning line for enterprise audiences.

    Returns:
        Positioning statement string
    """
    return (
        "Mythara Engine encodes resonance through mythic terms like the Blessings Reservoir. "
        "For enterprise audiences, we present these as overlays — Resonance Reservoir, Trust Index, "
        "Engagement Index — so managers can see symbolic depth alongside KPIs without disrupting compliance."
    )


def generate_flow_diagram_text() -> str:
    """
    Generate ASCII flow diagram for documentation.

    Returns:
        Multi-line string with flow diagram
    """
    return """
╔════════════════════════════════════════════════════════════════╗
║           MYTHARA ENGINE DUAL-FRAMING FLOW DIAGRAM            ║
╚════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────┐
│      System of Record (Any CRM / Field Platform)             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                 Mythara Engine Overlay                        │
│                                                               │
│  • Blessings Reservoir  →  Resonance Reservoir               │
│  • Integrity Metric     →  Trust Index                       │
│  • Expression Metric    →  Engagement Index                  │
│  • Soul Encoding        →  Impact Vault                      │
│  • Legacy Reservoir     →  Continuity Index                  │
│                                                               │
│  [Framing Mode: MYTHIC or INDUSTRY toggle]                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Manager Dashboards                          │
│                                                               │
│  • KPIs + Resonance Metrics side by side                     │
│  • Compliance intact, workflows unchanged                    │
│  • Adds symbolic depth to performance reporting              │
│                                                               │
│  Query Parameter: ?frame=industry (for external audiences)   │
│                   ?frame=mythic (for internal truth)         │
└──────────────────────────────────────────────────────────────┘
"""


# Mythic → Legal mapping: the adjudicatory voice. The engine's findings are
# rendered the way a reviewing body writes them: the record, the findings,
# the holding. Same math, no archaisms.
MYTHIC_TO_LEGAL: Dict[str, Dict[str, str]] = {
    "blessings_reservoir": {
        "legal_term": "Reserve Account",
        "mythic_term": "Blessings Reservoir",
        "legal_explanation": "Standing reserve credited or debited by adjudicated actions.",
        "category": "metric",
    },
    "integrity": {
        "legal_term": "Integrity Finding",
        "mythic_term": "Integrity",
        "legal_explanation": "Composite score: conformity to provisions × capacity to reconcile conflict.",
        "category": "metric",
    },
    "integrity_metric": {
        "legal_term": "Integrity Finding",
        "mythic_term": "Integrity Metric",
        "legal_explanation": "Composite score: conformity to provisions × capacity to reconcile conflict.",
        "category": "metric",
    },
    "alignment_commandments": {
        "legal_term": "Conformity to Provisions",
        "mythic_term": "Alignment to Commandments",
        "legal_explanation": "Degree to which the action conforms to the governing provisions.",
        "category": "metric",
    },
    "tolerance_will": {
        "legal_term": "Capacity to Reconcile",
        "mythic_term": "Tolerance of Will",
        "legal_explanation": "Capacity to hold the principal's intent alongside conflicting provisions.",
        "category": "metric",
    },
    "obedience": {
        "legal_term": "Compliant",
        "mythic_term": "Obedience",
        "legal_explanation": "Whether the action was held compliant with the governing provisions.",
        "category": "verdict",
    },
    "reservoir_delta": {
        "legal_term": "Reserve Adjustment",
        "mythic_term": "Reservoir Delta",
        "legal_explanation": "Credits or debits applied to the Reserve Account by this finding.",
        "category": "metric",
    },
    "collapse": {
        "legal_term": "Material Failure",
        "mythic_term": "Collapse",
        "legal_explanation": "Whether the finding constitutes a material failure of the matter.",
        "category": "verdict",
    },
    "integrity_hash": {
        "legal_term": "Seal",
        "mythic_term": "Integrity Hash",
        "legal_explanation": "Tamper-evident seal affixed to the finding.",
        "category": "record",
    },
    "will": {
        "legal_term": "Principal's Stated Intent",
        "mythic_term": "Will",
        "legal_explanation": "The objective as stated by the principal.",
        "category": "party",
    },
    "commandments": {
        "legal_term": "Governing Provisions",
        "mythic_term": "Commandments",
        "legal_explanation": "The binding provisions the action is measured against.",
        "category": "authority",
    },
    "temptation": {
        "legal_term": "Improper Inducement",
        "mythic_term": "Temptation",
        "legal_explanation": "Short-term incentive pressuring departure from the provisions.",
        "category": "pressure",
    },
}

# Verdict prefixes in the mythic voice → their legal rendering.
MYTHIC_VERDICT_TO_LEGAL = {
    "WILDERNESS/DARKNESS": "ADVERSE FINDING",
    "GARDEN/LIGHT": "FAVORABLE FINDING",
}


def translate_term_legal(mythic_key: str) -> str:
    """Translate one mythic key to its legal term; passthrough when unmapped."""
    entry = MYTHIC_TO_LEGAL.get(mythic_key)
    return entry["legal_term"] if entry else mythic_key


def render_legal_finding(result: Dict[str, Any]) -> str:
    """Render a Soul Cradle result as a legal finding.

    The numbers are untouched; only the voice changes. Reads the way a
    reviewing body writes: the matter, the findings, the holding, the seal.

    Args:
        result: Soul Cradle response dict (mythic keys).

    Returns:
        The finding rendered in the adjudicatory voice.
    """
    choice = str(result.get("choice", ""))
    for mythic_prefix, legal_prefix in MYTHIC_VERDICT_TO_LEGAL.items():
        if choice.startswith(mythic_prefix + ":"):
            choice = legal_prefix + ":" + choice[len(mythic_prefix) + 1 :]
            break

    compliant = bool(result.get("obedience", False))
    holding = "COMPLIANT" if compliant else "NON-COMPLIANT"
    integrity = result.get("integrity", 0.0)
    conformity = result.get("alignment_commandments", 0.0)
    capacity = result.get("tolerance_will", 0.0)
    delta = result.get("reservoir_delta", 0)
    material_failure = bool(result.get("collapse", False))
    seal = str(result.get("integrity_hash", ""))
    timestamp = str(result.get("timestamp", ""))

    if isinstance(integrity, float):
        integrity_s = f"{integrity:.2f}"
    else:
        integrity_s = str(integrity)

    lines = [
        "FINDING OF REVIEW",
        f"Matter: {choice}",
    ]
    if timestamp:
        lines.append(f"Date: {timestamp}")
    lines += [
        "",
        "Upon review of the record, the following is found:",
        "",
        f"1. Conformity to the governing provisions: {conformity}.",
        f"2. Capacity to reconcile conflicting intent: {capacity}.",
        f"3. Composite integrity finding: {integrity_s}.",
        f"4. HOLDING: the action is {holding}.",
    ]
    if delta:
        direction = "credited" if delta > 0 else "debited"
        lines.append(
            f"5. The Reserve Account is {direction} {abs(delta)} credits pursuant to this finding."
        )
    else:
        lines.append("5. No adjustment to the Reserve Account.")
    lines.append(f"6. Material failure: {'YES' if material_failure else 'none found'}.")
    lines += [
        "",
        "Attested and sealed.",
    ]
    if seal:
        lines.append(f"Seal: {seal[:32]}...")
    return "\n".join(lines)


def _plain_read(score: float, high: str, mid: str, low: str) -> str:
    """Qualitative read of a 0-1 score; no numbers, just the shape of it."""
    if score >= 0.75:
        return high
    if score >= 0.5:
        return mid
    return low


def render_spoken_finding(result: Dict[str, Any]) -> str:
    """Render a Soul Cradle result as clean spoken prose.

    No numbers, no parameters, no seal hashes — the verdict the way it
    sounds when spoken aloud. The full scored breakdown stays in
    render_plain_finding() for text/screens.
    """
    choice = str(result.get("choice", ""))
    for mythic_prefix in MYTHIC_VERDICT_TO_PLAIN:
        if choice.startswith(mythic_prefix + ":"):
            choice = choice[len(mythic_prefix) + 1 :].strip()
            break

    met_bar = bool(result.get("obedience", False))
    match_principles = float(result.get("alignment_commandments", 0.0) or 0.0)
    delta = result.get("reservoir_delta", 0)
    fell_apart = bool(result.get("collapse", False))

    principles_read = _plain_read(
        match_principles,
        "It lined up with your principles.",
        "It partly lined up with your principles.",
        "It strayed from your principles.",
    )

    if delta:
        direction = "grew a little" if delta > 0 else "took a small hit"
        reserve_line = f"Your reserve {direction}."
    else:
        reserve_line = "Your reserve is untouched."

    parts = [
        f"Here's the call on: {choice}.",
        "You were holding two things at once, and they pulled in different directions.",
        principles_read,
        f"The call: it {'met' if met_bar else 'did not meet'} the bar.",
        reserve_line,
        "It fell apart." if fell_apart else "Nothing broke.",
        "Signed and sealed.",
    ]
    return " ".join(parts)


# Emotions that mark a record as a remark rather than a moral call.
# Running a joke through the verdict machinery comes out pompous: the
# witnesses clear it, but there was never anything to judge. The honest
# move is to check whether there is a call to make before putting on
# the judge voice.
LIGHT_EMOTIONS = frozenset(
    {
        "playful",
        "joking",
        "amused",
        "happy",
        "joyful",
        "casual",
        "silly",
        "grateful",
        "calm",
        "relaxed",
    }
)


def choose_spoken_voice(emotion: str) -> str:
    """Pick the honest voice for a record: "verdict" or "remark".

    Real calls get the verdict voice. Jokes, remarks, and small talk
    get a human response — never the judge voice for something that
    was never a decision.
    """
    if str(emotion or "").strip().lower() in LIGHT_EMOTIONS:
        return "remark"
    return "verdict"


def render_spoken_remark(statement: str, cleared: int, engaged: int) -> str:
    """Speak a non-call record: short, human, no ceremony.

    cleared/engaged come from the real witness panel, so the remark can
    cite the panel's actual read honestly without moralizing the joke.
    """
    statement = str(statement or "").strip().strip("\"'")
    if engaged and cleared == engaged:
        if engaged == 8:
            witness_line = (
                "All eight witnesses cleared it unanimously — "
                "the least surprising verdict on record."
            )
        else:
            witness_line = f"All {engaged} witnesses cleared it unanimously."
    elif engaged:
        witness_line = f"{cleared} of {engaged} witnesses cleared it."
    else:
        witness_line = "No witness had anything to say about it."
    parts = [f"Noted — '{statement}', recorded.", witness_line]
    return " ".join(parts)


def translate_response_legal(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Translate a Soul Cradle response dict's keys into legal terminology.

    Values are untouched; nested dicts are translated recursively.
    """
    translated = {}
    for key, value in response_data.items():
        new_key = key
        if key in MYTHIC_TO_LEGAL:
            new_key = MYTHIC_TO_LEGAL[key]["legal_term"].lower().replace(" ", "_")
        if isinstance(value, dict):
            translated[new_key] = translate_response_legal(value)
        elif isinstance(value, list):
            translated[new_key] = [
                translate_response_legal(i) if isinstance(i, dict) else i for i in value
            ]
        else:
            translated[new_key] = value
    return translated


# Mythic → Plain speak mapping. No archaisms, no legalese, no corporate
# overlay. The way one honest person explains the call to another.
MYTHIC_TO_PLAIN: Dict[str, Dict[str, str]] = {
    "blessings_reservoir": {
        "plain_term": "Reserve",
        "mythic_term": "Blessings Reservoir",
        "plain_explanation": "Your standing reserve. Good calls add to it, bad ones draw it down.",
        "category": "metric",
    },
    "integrity": {
        "plain_term": "Score",
        "mythic_term": "Integrity",
        "plain_explanation": "The overall score: how well you matched your principles times how well you held the tension.",
        "category": "metric",
    },
    "alignment_commandments": {
        "plain_term": "Match to Principles",
        "mythic_term": "Alignment to Commandments",
        "plain_explanation": "How well the action matched the principles you set for yourself.",
        "category": "metric",
    },
    "tolerance_will": {
        "plain_term": "Hold on the Tension",
        "mythic_term": "Tolerance of Will",
        "plain_explanation": "How well you held two pulling truths at once without dropping either.",
        "category": "metric",
    },
    "obedience": {
        "plain_term": "Met the Bar",
        "mythic_term": "Obedience",
        "plain_explanation": "Whether the action met the bar you set.",
        "category": "verdict",
    },
    "reservoir_delta": {
        "plain_term": "Reserve Change",
        "mythic_term": "Reservoir Delta",
        "plain_explanation": "What this call added to or took from your reserve.",
        "category": "metric",
    },
    "collapse": {
        "plain_term": "Fell Apart",
        "mythic_term": "Collapse",
        "plain_explanation": "Whether the whole thing fell apart.",
        "category": "verdict",
    },
    "integrity_hash": {
        "plain_term": "Seal",
        "mythic_term": "Integrity Hash",
        "plain_explanation": "The tamper-proof seal on this call.",
        "category": "record",
    },
    "will": {
        "plain_term": "What You Wanted",
        "mythic_term": "Will",
        "plain_explanation": "What you were aiming at.",
        "category": "party",
    },
    "commandments": {
        "plain_term": "Your Principles",
        "mythic_term": "Commandments",
        "plain_explanation": "The principles you said you'd hold to.",
        "category": "authority",
    },
    "temptation": {
        "plain_term": "The Easy Way Out",
        "mythic_term": "Temptation",
        "plain_explanation": "The shortcut that was pulling at you.",
        "category": "pressure",
    },
}

MYTHIC_VERDICT_TO_PLAIN = {
    "WILDERNESS/DARKNESS": "didn't meet the bar",
    "GARDEN/LIGHT": "met the bar",
}


def translate_term_plain(mythic_key: str) -> str:
    """Translate one mythic key to its plain-speak term; passthrough when unmapped."""
    entry = MYTHIC_TO_PLAIN.get(mythic_key)
    return entry["plain_term"] if entry else mythic_key


def render_plain_finding(result: Dict[str, Any]) -> str:
    """Render a Soul Cradle result in plain speak.

    The numbers are untouched. No archaisms, no legalese — the call explained
    the way one honest person explains it to another.
    """
    choice = str(result.get("choice", ""))
    for mythic_prefix in MYTHIC_VERDICT_TO_PLAIN:
        if choice.startswith(mythic_prefix + ":"):
            choice = choice[len(mythic_prefix) + 1 :].strip()
            break

    met_bar = bool(result.get("obedience", False))
    integrity = result.get("integrity", 0.0)
    match_principles = result.get("alignment_commandments", 0.0)
    hold_tension = result.get("tolerance_will", 0.0)
    delta = result.get("reservoir_delta", 0)
    fell_apart = bool(result.get("collapse", False))
    seal = str(result.get("integrity_hash", ""))

    integrity_s = f"{integrity:.2f}" if isinstance(integrity, float) else str(integrity)

    lines = [
        f"Here's the call on: {choice}.",
        "",
        "You were holding two things at once, and they pulled in different directions.",
        "",
        f"- Match to your principles: {match_principles}.",
        f"- Hold on the tension: {hold_tension}.",
        f"- Overall score: {integrity_s}.",
        "",
        f"The call: it {'met' if met_bar else 'did not meet'} the bar.",
    ]
    if delta:
        direction = "added to" if delta > 0 else "came off"
        lines.append(f"{abs(delta)} credits {direction} your reserve.")
    else:
        lines.append("Your reserve is untouched.")
    lines.append("It fell apart." if fell_apart else "Nothing broke.")
    lines += [
        "",
        "Signed and sealed.",
    ]
    if seal:
        lines.append(f"Seal: {seal[:32]}...")
    return "\n".join(lines)


# Example usage for testing
if __name__ == "__main__":
    print("=" * 70)
    print("MYTHARA ENGINE DUAL-FRAMING TRANSLATION LAYER")
    print("=" * 70)
    print()

    # Example 1: Translate individual terms
    print("Example 1: Individual Term Translation")
    print("-" * 70)
    print(f"Mythic: {translate_term('blessings_reservoir', FramingMode.MYTHIC)}")
    print(f"Industry: {translate_term('blessings_reservoir', FramingMode.INDUSTRY)}")
    print(
        f"With Explanation: {translate_term('blessings_reservoir', FramingMode.INDUSTRY, include_explanation=True)}"
    )
    print()

    # Example 2: Translate full response
    print("Example 2: Full Response Translation")
    print("-" * 70)
    sample_response = {
        "blessings_reservoir": 145,
        "integrity_metric": 0.95,
        "expression_metric": 0.88,
        "soul_encoding": {"depth": 42, "status": "resonant"},
    }
    print("Original (Mythic):", sample_response)
    print(
        "Translated (Industry):",
        translate_response(sample_response, FramingMode.INDUSTRY),
    )
    print()

    # Example 3: Manager dashboard
    print("Example 3: Manager Dashboard Formatting")
    print("-" * 70)
    dashboard = format_for_manager_dashboard(sample_response, FramingMode.INDUSTRY)
    import json

    print(json.dumps(dashboard, indent=2))
    print()

    # Example 4: Positioning line
    print("Example 4: Positioning Line")
    print("-" * 70)
    print(get_positioning_line())
    print()

    # Example 5: Flow diagram
    print("Example 5: Flow Diagram")
    print("-" * 70)
    print(generate_flow_diagram_text())
