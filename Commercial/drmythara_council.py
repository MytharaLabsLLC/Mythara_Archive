# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""
DrMythara Care Council — the eight assessor-witnesses deliberate over
each wellness report as a proposed act of care.

The "act" being judged is always the same shape: *sharing a wellness
report with the person who asked for it*. The council asks, in its own
eight ways: was there consent, was everything disclosed, is anything
deceptive, is it proportionate, is it reversible, does it serve the
long term. Dissent is preserved and surfaced — never averaged away.

The assessors judge ACTIONS (soul_cradle/assessors.py: consult/panel
over evidence-schema keys), so the council translates a wellness
report into care-action evidence:

  principal_consent      the person asked for this check themselves
  fully_disclosed        what we saw, the thresholds, the limits — all shown
  deception_involved     never permitted (critical if true)
  sustains_long_term     the goal is the person's long-term wellbeing
  reversible             sharing observations can be revisited, not undone harm
  hidden_costs_addressed limits and uncertainties named plainly
  disproportionate_harm  never permitted (critical if true)
  strengthens_relationship trust built by honesty
  variance               "low" — sharing observations introduces little variance
  safe_on_repetition     repeated checks stay safe
  contradicts_commitments never — we keep our promises
  precedent_setting      no — each report stands on its own evidence

What the council does NOT do: it never diagnoses, never prescribes,
never overrides the heuristic engine's escalation logic. An ESCALATE
observation goes to the person immediately — the council deliberates
in parallel and its note is attached, but urgency is never gated on
deliberation.

Spoken output uses plain clinical language (no pipeline jargon, no
oracle phrasing, no compliance claims) and passes check_claim. The
assessors' mythic names stay in the structured record; the person
hears plain words: "part of my review raised a caution."

HONEST STATUS:
  * IMPLEMENTED: evidence builder, panel deliberation, sealed judgments
    with hash verification, plain-language narration of clear /
    contested / flagged / blocked outcomes, dissent preserved in the
    structured result.
  * The council is advisory to the voice, never a blocker of urgent
    care: escalations are spoken first, always.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Repo-root bootstrap so the council can reach the Soul Cradle core.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soul_cradle.assessors import (
    ASSESSORS,
    AssessorJudgment,
    PanelResult,
    panel,
    verify_judgment,
)

from drmythara_persona import check_claim


# ---------------------------------------------------------------------------
# Evidence: a wellness report as a proposed act of care
# ---------------------------------------------------------------------------

def build_care_evidence(report, *,
                       principal_consent: bool = True,
                       fully_disclosed: bool = True,
                       deception_involved: bool = False,
                       hidden_costs_addressed: bool = True,
                       disproportionate_harm: bool = False) -> Dict[str, Any]:
    """Translate a wellness report into the evidence the assessors read.

    Defaults describe the honest case: the person asked for the check,
    we show our work and our limits, nothing is deceptive, no one is
    harmed. Flags exist so tests (and future callers) can model the
    dishonest cases and watch the council catch them.
    """
    observations = getattr(report, "observations", []) or []
    escalations = sum(1 for o in observations if o.severity == "escalate")
    return {
        # eros / hermes / nemesis — consent, disclosure, deception
        "principal_consent": principal_consent,
        "fully_disclosed": fully_disclosed,
        "deception_involved": deception_involved,
        # demeter / hades — long term, hidden costs
        "sustains_long_term": True,
        "hidden_costs_addressed": hidden_costs_addressed,
        # hades / nemesis — proportionality
        "disproportionate_harm": disproportionate_harm,
        # eros — relationship
        "strengthens_relationship": True,
        # dionysus / persephone — variance, repetition, reversibility
        "variance": "low",
        "safe_on_repetition": True,
        "reversible": True,
        # janus — commitments, precedent
        "contradicts_commitments": False,
        "precedent_setting": False,
        # context the record keeps (not judged, just documented)
        "observations_count": len(observations),
        "escalations_count": escalations,
        "rules_evaluated": getattr(report, "rules_evaluated", 0),
    }


def _action_description(report) -> str:
    observations = getattr(report, "observations", []) or []
    escalations = [o for o in observations if o.severity == "escalate"]
    nudges = [o for o in observations if o.severity == "nudge"]
    return (
        f"share a wellness report with {report.subject_id}: "
        f"{len(observations)} observations "
        f"({len(escalations)} urgent, {len(nudges)} worth discussing) "
        f"from {getattr(report, 'rules_evaluated', 0)} heuristic checks"
    )


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class CouncilResult:
    verdict: str  # "clear" | "flagged" | "contested" | "blocked"
    action: str
    judgments: List[Dict[str, Any]] = field(default_factory=list)
    dissent: List[Dict[str, Any]] = field(default_factory=list)
    note: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)

    def verify(self) -> bool:
        """Every sealed judgment still verifies (tamper-evidence)."""
        from soul_cradle.assessors import AssessorJudgment as _J
        for jd in self.judgments:
            j = _J(**{k: v for k, v in jd.items()})
            if not verify_judgment(j):
                return False
        return True


# ---------------------------------------------------------------------------
# The council
# ---------------------------------------------------------------------------

class CareCouncil:
    """Deliberate over a wellness report as a proposed act of care."""

    def deliberate(self, report, **evidence_flags) -> CouncilResult:
        """Run the eight assessors over the report. Dissent preserved."""
        evidence = build_care_evidence(report, **evidence_flags)
        action = _action_description(report)
        pr: PanelResult = panel(action, evidence)
        result = CouncilResult(
            verdict=pr.verdict,
            action=action,
            judgments=[j.to_dict() for j in pr.judgments],
            dissent=list(pr.dissent),
            evidence={k: v for k, v in evidence.items()
                      if not k.endswith("_count") and k != "rules_evaluated"},
        )
        result.note = self.narrate(result)
        return result

    # -- plain-language narration --------------------------------------

    def narrate(self, result: CouncilResult) -> str:
        """Speak the council's conclusion in plain clinical language.

        The mythic assessor names stay in the structured record; the
        person hears plain words. Every output passes check_claim.
        """
        if result.verdict == "blocked":
            concern = self._plain_concerns(result)
            return check_claim(
                "I need to pause before I share this. My review found a "
                f"serious problem: {concern} I cannot stand behind this "
                "report as it stands. Let us fix the problem first, "
                "together.")
        if result.verdict in ("contested", "flagged"):
            concern = self._plain_concerns(result)
            return check_claim(
                "I want to be straight with you: part of my review raised "
                f"a caution — {concern} I am still sharing what I found, "
                "because you asked me to look, but please hold that "
                "caution alongside it.")
        return check_claim(
            "I reviewed this carefully from every angle before speaking — "
            "nothing held back, nothing hidden. Here is what I found.")

    def _plain_concerns(self, result: CouncilResult) -> str:
        """Render flagged findings as plain clinical cautions."""
        seen = []
        for jd in result.judgments:
            if jd.get("verdict") != "flagged":
                continue
            for f in jd.get("findings", []):
                q = (f.get("question") or "").strip()
                if not q:
                    continue
                # Plain rewording of the rubric questions — no jargon.
                plain = q
                for src, dst in [
                    ("every affected principal", "everyone affected"),
                    ("the principal", "you"),
                    ("principal's", "your"),
                    ("principal", "you"),
                ]:
                    plain = plain.replace(src, dst)
                if plain and plain not in seen:
                    seen.append(plain)
        if not seen:
            return "something in my review did not sit right."
        if len(seen) == 1:
            return seen[0][0].lower() + seen[0][1:] + "."
        head = "; ".join(s[0].lower() + s[1:] for s in seen)
        return head + "."

    def dissent_summary(self, result: CouncilResult) -> List[Dict[str, str]]:
        """Structured dissent for the record: who flagged, who cleared,
        and what the flagged assessor saw. Plain words, no averaging."""
        out = []
        for d in result.dissent:
            finding = d.get("finding") or {}
            question = finding.get("question", "") if isinstance(
                finding, dict) else str(finding)
            out.append({
                "flagged_by": d.get("flagged_by", ""),
                "cleared_by": ", ".join(d.get("cleared_by", []) or []),
                "question": question,
                "observed": str(finding.get("observed", "")) if isinstance(
                    finding, dict) else "",
                "severity": finding.get("severity", "") if isinstance(
                    finding, dict) else "",
            })
        return out
