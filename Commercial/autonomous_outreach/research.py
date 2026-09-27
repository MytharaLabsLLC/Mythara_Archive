# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Per-prospect research briefs.

The anti-fake-personalization contract:
  * A brief records ONLY verified facts, each with a source ("website",
    "launch post", "repo", "herb-note", ...).
  * The drafter (voice.py) may reference ONLY facts present in the brief.
  * Facts NOT in the brief MUST NOT appear in the email. No "loved your
    recent post", no "I see you're hiring" unless the brief says so with
    a source.
  * Unknowns are explicit. "I don't know much about your setup yet" is an
    honest sentence and beats an invented one every time.

Briefs are produced by real research (Herb, the main agent, or a research
subagent) and stored on the prospect record. This module validates and
stores them; it never invents them.
"""

from typing import Any, Dict, List, Optional

from . import prospects


REQUIRED_KEYS = ("facts", "reason_for_contact")


def build_brief(
    facts: List[Dict[str, str]],
    reason_for_contact: str,
    unknowns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Validate and build a brief. Each fact: {'fact': ..., 'source': ...}."""
    if not isinstance(facts, list):
        raise ValueError("facts must be a list of {'fact','source'} dicts")
    clean: List[Dict[str, str]] = []
    for f in facts:
        fact = (f.get("fact") or "").strip()
        source = (f.get("source") or "").strip()
        if not fact or not source:
            raise ValueError("every fact needs both 'fact' and 'source'")
        clean.append({"fact": fact, "source": source})
    reason = (reason_for_contact or "").strip()
    if not reason:
        raise ValueError("reason_for_contact is required — no reason, no email")
    return {
        "facts": clean,
        "reason_for_contact": reason,
        "unknowns": [u for u in (unknowns or []) if u.strip()],
    }


def attach_brief(pid: str, brief: Dict[str, Any]) -> Dict[str, Any]:
    """Validate, attach to the prospect, and mark researched."""
    for key in REQUIRED_KEYS:
        if key not in brief:
            raise ValueError(f"brief missing {key!r}")
    d = prospects.update(
        pid, research_brief=brief, status=prospects.STATUS_RESEARCHED
    )
    return d


def brief_facts(pid: str) -> List[Dict[str, str]]:
    d = prospects.get(pid) or {}
    brief = d.get("research_brief") or {}
    return brief.get("facts", [])


def check_copy_against_brief(body: str, pid: str) -> List[str]:
    """Heuristic guard: flag sentences that LOOK like personalization claims.

    Returns a list of suspect lines (for the drafter to fix or justify).
    This is a backstop, not a proof — the real guarantee is that the
    composer only ever renders brief facts.
    """
    suspects: List[str] = []
    patterns = (
        "loved your",
        "great post",
        "noticed you",
        "saw that you",
        "congrats on",
        "impressive",
    )
    for line in body.splitlines():
        low = line.lower()
        if any(p in low for p in patterns):
            suspects.append(line.strip())
    return suspects
