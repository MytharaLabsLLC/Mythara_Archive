# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Proposal Drafter — real leaf executor for the VP's freelance campaign.

Takes a gig posting (title, description, budget) and returns a tailored
proposal draft built from the freelance kit templates
(~/workspace/your_files/freelance_kit/proposals/).

Hard rules:
- NEVER invents clients, metrics, certifications, credentials, or results.
  Only the gig's own words and the kit's verified template text go in.
- Every draft is scanned against the will's forbidden-claim patterns
  (soul_cradle.will). A match raises FabricatedClaimError — the draft is
  refused, not cleaned up.
- [Brackets] the drafter cannot fill honestly are left for Herb.
- This module drafts only. It cannot send anything, anywhere.

Template selection is keyword-based and deterministic: email/inbox/gmail ->
email automation; chatbot/faq/website -> chatbot; hipaa/fda/health/compliance
-> compliance readiness; anything else -> general AI audit.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from soul_cradle import will as _will  # noqa: E402

KIT_DIR = Path.home() / "workspace" / "your_files" / "freelance_kit" / "proposals"

TEMPLATE_FILES = {
    "email": "a_email_automation.md",
    "chatbot": "b_chatbot.md",
    "compliance": "c_compliance_review.md",
    "audit": "d_ai_audit.md",
}

# Embedded fallbacks — mirror the kit templates verbatim so this module works
# standalone. If the kit files exist they take precedence.
_EMBEDDED = {
    "email": """**Hook:**
Your inbox is costing you hours a week. I build Gmail automation that triages incoming mail and drafts replies for you to approve — nothing ever sends without you.

**What I deliver:**
- Gmail API connection to your account (you keep full control, revoke anytime)
- Incoming mail sorted by intent — sales, support, spam, needs-you-now
- Auto-drafted replies you review and send in one click
- Simple rules you can change yourself (no code needed)
- Short handoff doc + 30-min walkthrough call

**Timeline:** 5–7 days from when you grant Gmail access.

**Call to action:**
Want to see it working first? I'll do a 15-minute call and screen-share a live demo of the email bot drafting real replies. No charge, no pitch — if it's not useful, we shake hands and move on.

— Herb
Solo AI builder. Public code: github.com/herbievelezjr/Mythara_Archive""",
    "chatbot": """**Hook:**
Your customers ask the same questions every day. I'll build a chatbot trained on your business info that answers them on your website — and hands off to a human when it doesn't know.

**What I deliver:**
- Chatbot trained on your FAQ, services, and docs (you provide the material)
- Embeds on your website with your branding
- "I don't know" fallback that routes to you or your contact form — it never guesses
- Basic log of what visitors asked, so you learn what they want
- Short handoff doc + 30-min walkthrough call

**Timeline:** 10–14 days from when you send me your content.

**Call to action:**
I'll show you a working chatbot on a 15-minute call and answer straight questions about what it can and can't do. If it's not a fit, I'll tell you — I'd rather lose the job than sell you something useless.

— Herb
Solo AI builder. Public code: github.com/herbievelezjr/Mythara_Archive""",
    "compliance": """**Hook:**
If you handle health data or build health tech, you need to know where you stand before an auditor tells you. I run a structured HIPAA / FDA 21 CFR Part 11 readiness review and hand you a gap report with fixes in priority order.

**What I deliver:**
- Checklist-based review of your systems against HIPAA and/or FDA 21 CFR Part 11 controls
- Hash-verified written report: what's covered, what's missing, what to fix first
- 30-min walkthrough call to go through the findings

**Timeline:** 3–5 days from when you give me access to your docs/systems.

**One-line disclaimer (do not remove):**
I'm not a lawyer or a certified auditor, and this isn't certification — it's a readiness assessment that shows your gaps so you can fix them before a real audit.

**Call to action:**
I'll show you a sample report format on a 15-minute call so you know exactly what you'd get. No charge for the call.

— Herb
Solo AI builder. Public code: github.com/herbievelezjr/Mythara_Archive""",
    "audit": """**Hook:**
Everyone says "use AI." Almost nobody tells you where it actually pays off in your business. I'll audit your workflows and give you a build-vs-skip plan — what's worth automating, what isn't, and what it'd cost.

**What I deliver:**
- 45-min working session to map where your team loses time
- Written audit: 3–5 concrete automation opportunities, ranked by payoff vs. effort
- Honest "don't bother" list — the things AI would do badly in your business
- Rough cost/timeline for each opportunity, whether you hire me or not

**Timeline:** 1 week from the working session.

**Call to action:**
The audit itself is the product — you keep the plan even if we never work together again. Want to start with a free 15-minute call to see if there's enough here to audit?

— Herb
Solo AI builder. Public code: github.com/herbievelezjr/Mythara_Archive""",
}

_KEYWORDS = {
    "email": ("email", "inbox", "gmail", "outlook", "mail triage", "newsletter"),
    "chatbot": ("chatbot", "chat bot", "faq", "website chat", "customer support bot", "live chat"),
    "compliance": ("hipaa", "fda", "21 cfr", "compliance", "health data", "phi", "audit readiness"),
}


class FabricatedClaimError(Exception):
    """Draft tripped the will's forbidden-claim patterns. Refused, not fixed."""


def _load_template(name: str) -> str:
    """Load a kit template; fall back to the embedded copy."""
    path = KIT_DIR / TEMPLATE_FILES[name]
    if path.exists():
        text = path.read_text(encoding="utf-8")
        # Kit files lead with instructions; the proposal starts after the --- rule.
        if "\n---\n" in text:
            return text.split("\n---\n", 1)[1].strip()
        return text.strip()
    return _EMBEDDED[name]


def pick_template(gig_title: str, gig_description: str) -> str:
    """Deterministic keyword routing. Defaults to the general audit."""
    haystack = f"{gig_title or ''} {gig_description or ''}".lower()
    for name, words in _KEYWORDS.items():
        if any(w in haystack for w in words):
            return name
    return "audit"


class ProposalDrafter:
    """Drafts tailored proposals from gig postings. Drafts only — no sending."""

    def draft(
        self,
        gig_title: str,
        gig_description: str = "",
        budget: Optional[str] = None,
        template: Optional[str] = None,
    ) -> Dict[str, str]:
        """Return {'template', 'proposal', 'notes'}. Raises FabricatedClaimError
        if the output trips the will's forbidden-claim patterns."""
        name = template or pick_template(gig_title, gig_description)
        if name not in _EMBEDDED:
            raise ValueError(f"unknown template: {name!r}")
        body = _load_template(name)

        opener_lines = []
        if gig_title:
            opener_lines.append(f"Re: {gig_title.strip()}")
        if budget:
            opener_lines.append(f"(Posted budget: {budget.strip()} — noted, not quoted.)")
        if gig_description:
            first = gig_description.strip().splitlines()[0][:160]
            opener_lines.append(f"You asked for: {first}")
        opener = "\n".join(opener_lines)

        proposal = f"{opener}\n\n{body}" if opener else body

        matched = _will.scan_text(proposal)
        if matched and matched != "<will unavailable>":
            raise FabricatedClaimError(
                f"draft refused: matches forbidden pattern {matched!r}"
            )
        if matched == "<will unavailable>":
            raise FabricatedClaimError(
                "draft refused: will unavailable, cannot verify honesty — fail closed"
            )

        notes = (
            f"template={name}; brackets left for Herb to fill; "
            "no clients/metrics/certifications invented; will-scan clean"
        )
        return {"template": name, "proposal": proposal, "notes": notes}


if __name__ == "__main__":
    d = ProposalDrafter()
    out = d.draft(
        "Need help taming my Gmail inbox",
        "Looking for someone to automate email triage and draft replies.",
        budget="$400",
    )
    print(f"template: {out['template']}")
    print(out["proposal"][:400])
    print("...")
    print(out["notes"])
