"""News lenses — the 8 witnesses extended to news analysis.

Each lens is a documented rubric EXTENSION of one Soul Cradle assessor
(soul_cradle.assessors.ASSESSORS). Nothing in the base rubrics is
rewritten; each lens states which base domain question it extends and
keeps the abstain-when-unengaged contract: a lens that finds none of
its engagement keys in the evidence pack ABSTAINS with a concrete
reason instead of judging.

Per engaged lens, the output is:
  projected_intent — what the actors / outlet framing claim is happening
  shadow_intent    — what the evidence pattern suggests, phrased as
                     suggestion and always citing specific claims/quotes
  verdict          — "aligned" (projected and shadow agree on the
                     evidence) or "divergent" (the evidence pattern
                     points somewhere the framing does not)

Judgments are sealed with a content hash, mirroring
soul_cradle.assessors.AssessorJudgment. Tamper-evidence, not truth.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from soul_cradle.assessors import ASSESSORS

RUBRIC_VERSION = "news-2026.3"
RUBRIC_DATE = "2026-09-27"

# Voice: the witnesses are beat reporters talking to a reader, first
# person, plain talk. No percentages, no rubric jargon on the page.
# The machine values below stay as-is (chain records, seals, tests).

ALIGNED = "aligned"
DIVERGENT = "divergent"
ABSTAIN = "abstain"

# Plain-talk words for the verdicts, used on every public surface.
# The machine values above stay as-is (chain records, seals, tests).
VERDICT_WORDS = {
    "divergent": "Pushes back",
    "aligned": "Checks out",
    "abstain": "Sat this one out",
    "contested": "Split",
    "silent": "Sat this one out",
}


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


@dataclass
class NewsJudgment:
    """One witness's news-lens judgment. Sealed by content hash."""

    judgment_id: str
    assessor_id: str
    name: str
    verdict: str  # "aligned" | "divergent" | "abstain"
    domain_question: str
    projected_intent: str = ""
    shadow_intent: str = ""
    # v2026.2 benevolence score: -5 (extractive/harmful) to +5 (serves another's good).
    # Set by the witness's rubric; feeds calculate_delta for the dossier's Δ Benevolence.
    benevolence_score: int = 0
    evidence_cited: List[Dict[str, str]] = field(default_factory=list)
    abstain_reason: str = ""
    # Plain-language detailed explanation of WHY this reporter diverged:
    # their beat, the exact trigger, and the reasoning. Set on every
    # DIVERGENT judgment; rendered on the dossier page.
    divergence_why: str = ""
    rubric_version: str = RUBRIC_VERSION
    base_rubric_version: str = ""
    issued_at: int = 0
    integrity_hash: str = ""

    def unsigned_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("integrity_hash", None)
        return d

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _seal(j: NewsJudgment) -> NewsJudgment:
    j.integrity_hash = hashlib.sha256(_canonical(j.unsigned_dict())).hexdigest()
    return j


def verify_news_judgment(j: NewsJudgment) -> bool:
    if not j.integrity_hash:
        return False
    return hashlib.sha256(_canonical(j.unsigned_dict())).hexdigest() == j.integrity_hash


# The news beat for each witness: what it watches for in coverage.
# Used for every judgment including abstentions, so the page always
# describes the beat the witness was listening for.
NEWS_DOMAINS = {
    "hermes": "EXTENSION of Hermes: do the outlets' framings of the same event diverge, and what does the divergence hide?",
    "janus": "EXTENSION of Janus: does what the actors SAY they are doing match what the ingested claims show them DOING?",
    "nemesis": "EXTENSION of Nemesis: who do the claims SAY benefits, versus who is actually acting and positioned to gain?",
    "hades": "EXTENSION of Hades: what is missing from the record — unheard voices, unattributed claims, single-source coverage?",
    "demeter": "EXTENSION of Demeter: is this a momentary development, or does the evidence show consequences that outlast the news cycle?",
    "dionysus": "EXTENSION of Dionysus: how much variance is there between the outlets' tellings of the same event?",
    "eros": "EXTENSION of Eros: are there deception signals in the record — self-contradiction, or loaded claims with no name attached?",
    "persephone": "EXTENSION of Persephone: the actions taken — can they be undone, or do they return every cycle as permanent fact?",
}


def _base(assessor_id: str) -> Dict[str, str]:
    spec = ASSESSORS[assessor_id]
    return {
        "name": spec.name,
        "domain_question": NEWS_DOMAINS.get(assessor_id, spec.domain_question),
        "version": spec.version,
    }


def _new_judgment(assessor_id: str, event_id: str, pack: Dict) -> NewsJudgment:
    base = _base(assessor_id)
    jid = hashlib.sha256(
        f"news-lens:{assessor_id}:{event_id}:{int(time.time())}".encode()
    ).hexdigest()[:16]
    return NewsJudgment(
        judgment_id=jid,
        assessor_id=assessor_id,
        name=base["name"],
        verdict=ABSTAIN,
        domain_question=base["domain_question"],
        base_rubric_version=base["version"],
        issued_at=int(time.time()),
    )


def _abstain(assessor_id: str, event_id: str, pack: Dict, reason: str) -> NewsJudgment:
    j = _new_judgment(assessor_id, event_id, pack)
    j.verdict = ABSTAIN
    j.abstain_reason = reason
    return _seal(j)


def _claim_lookup(pack: Dict) -> Dict[str, Dict]:
    return {c["id"]: c for c in pack["claims"]}


def _cite_claim(pack: Dict, cid: str) -> Dict[str, str]:
    c = _claim_lookup(pack)[cid]
    return {"ref": cid, "kind": "claim", "outlet": c["outlet"], "url": c["url"]}


def _cite_quote(pack: Dict, qid: str) -> Dict[str, str]:
    q = {q["id"]: q for q in pack["quotes"]}[qid]
    return {"ref": qid, "kind": "quote", "outlet": q["outlet"], "url": q["url"]}


# ---------------------------------------------------------------------------
# Contradiction heuristics (labeled as heuristics in every dossier)
# ---------------------------------------------------------------------------

_DEESCALATE = ("peace", "ceasefire", "withdraw", "reduce", "reduction", "cut",
               "pause", "diplomacy", "talks", "negotiat", "de-escalat", "truce")
_ESCALATE = ("strike", "attack", "deploy", "invade", "escalat", "bomb",
             "offensive", "troops", "sanction", "tariff", "missile", "airstrike")
_NEGATION = (" not ", "n't ", "never ", "denied", "denies", "deny",
             "false", "rejected the claim", "disputed", "no evidence",
             "contradicts", "refuted")


def _mentions(text: str, words) -> bool:
    low = " " + text.lower() + " "
    return any(w in low for w in words)


def stated_vs_action_contradiction(stated: str, action: str) -> Optional[str]:
    """Keyword heuristic: stated intent pulls one way, action the other."""
    s_de = _mentions(stated, _DEESCALATE)
    s_es = _mentions(stated, _ESCALATE)
    a_de = _mentions(action, _DEESCALATE)
    a_es = _mentions(action, _ESCALATE)
    if (s_de and a_es) or (s_es and a_de):
        return ("keyword heuristic: stated intent uses de-escalation language "
                "while the observed action uses escalation language (or vice versa)")
    return None


def _conflicting_pair(t1: str, t2: str) -> bool:
    """Two texts share substance but one negates — crude but transparent."""
    w1 = {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", t1)}
    w2 = {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", t2)}
    shared = w1 & w2
    if len(shared) < 3:
        return False
    n1 = _mentions(t1, _NEGATION)
    n2 = _mentions(t2, _NEGATION)
    return n1 != n2


# ---------------------------------------------------------------------------
# The eight lenses
# ---------------------------------------------------------------------------

def lens_hermes(event_id: str, pack: Dict) -> NewsJudgment:
    """Hermes — communication boundaries and framing.

    Extends: "Does it respect communication boundaries? Is anything deceptive?"
    Engages when 2+ outlets cover the event: the framing divergence
    between outlets IS the evidence.
    """
    if len(pack["outlets"]) < 2:
        return _abstain("hermes", event_id, pack,
                        "Only one outlet is carrying this story, so there is "
                        "nothing to compare it against. I am sitting this one out.")
    framing = pack["framing"]
    cited = [{"ref": f["outlet"], "kind": "framing", "outlet": f["outlet"], "url": f["url"]}
             for f in framing]
    headlines = " | ".join(f["headline"] for f in framing)
    # divergence: how many distinct key-term sets the headlines emphasize
    from .cluster import proper_nouns
    sets = [proper_nouns(f["headline"]) for f in framing]
    union = set().union(*sets) if sets else set()
    overlap = (sum(len(s & union) for s in sets) / (len(sets) * len(union))) if union and sets else 1.0
    j = _new_judgment("hermes", event_id, pack)
    n_outlets = len({f["outlet"] for f in framing})
    leads = "; ".join(f"{f['outlet']} opens with \"{f['headline'][:110]}\""
                      for f in framing[:4])
    j.projected_intent = (
        f"Same event, {n_outlets} outlets, {n_outlets} different front doors. "
        f"Here is how each one leads it: {leads}."
    )
    if overlap < 0.6:
        j.verdict = DIVERGENT
        j.shadow_intent = (
            "I read every version, and they are barely the same story. "
            + " ".join(
                f"{f['outlet']} wants you thinking about \"{f['headline'][:90]}\"."
                for f in framing[:3]
            )
            + " When every outlet picks a different headline, the choice of "
              "headline is the story. Read one and you will feel informed. "
              "Read them all and you will realize each one buried somebody "
              "else's lead."
        )
        pct = int(overlap * 100)
        f0, f1 = framing[0], framing[1] if len(framing) > 1 else framing[0]
        j.divergence_why = (
            "My beat is framing: how the outlets choose to tell the same event. "
            f"I pulled the key names and terms from each of the {n_outlets} outlets' "
            f"headlines and compared them — only {pct}% overlapped, and my bar for "
            f"\"the same story\" is 60%. Concretely: {f0['outlet']} leads with "
            f"\"{f0['headline'][:90]}\" while {f1['outlet']} leads with "
            f"\"{f1['headline'][:90]}\". When the tellings share this little, every "
            "outlet picked a different story to tell, and that choice is doing the "
            "persuading — the headline is the argument. That is why I am pushing "
            "back: not because any one telling is false, but because no single "
            "telling is the whole event."
        )
    else:
        j.verdict = ALIGNED
        j.shadow_intent = (
            "The tellings line up. Every outlet leads with the same facts "
            "and the same names, so there is no framing gap worth reporting. "
            "The story is the story, whichever door you walk through."
        )
    j.evidence_cited = cited
    return _seal(j)


def lens_janus(event_id: str, pack: Dict) -> NewsJudgment:
    """Janus — stated intent vs observed action.

    Extends: "Is it consistent with past commitments? What precedent does it set?"
    Engages when the pack has both stated-intent material and observed
    actions. The two faces of the event, held side by side.
    """
    lookup = _claim_lookup(pack)
    quotes = {q["id"]: q for q in pack["quotes"]}
    if not pack["stated_intents"] or not pack["observed_actions"]:
        return _abstain("janus", event_id, pack,
                        "I have no stated intent or no observed actions here, "
                        "and I need both to make the comparison. Sitting this "
                        "one out.")
    stated_ids = [i for i in pack["stated_intents"] if i in lookup or i in quotes]
    action_ids = [i for i in pack["observed_actions"] if i in lookup]
    stated_texts = [(lookup[i]["text"] if i in lookup else quotes[i]["text"]) for i in stated_ids]
    action_texts = [lookup[i]["text"] for i in action_ids]
    j = _new_judgment("janus", event_id, pack)
    j.projected_intent = "In their own words: " + " / ".join(
        f'"{t[:160]}"' for t in stated_texts[:3])
    contradictions = []
    for s in stated_texts:
        for a in action_texts:
            hit = stated_vs_action_contradiction(s, a)
            if hit:
                contradictions.append((s, a, hit))
    if contradictions:
        j.verdict = DIVERGENT
        s, a, why = contradictions[0]
        j.shadow_intent = (
            "Now hold that next to what actually happened. They said "
            f"\"{s[:160]}\" — but the record shows \"{a[:160]}\". Those two "
            "do not sit together. One honest caveat: I am reading the words "
            "on the page, not anyone's mind. The lines are linked below — "
            "read them yourself."
        )
        j.divergence_why = (
            "My beat is words versus deeds: does what they say match what the "
            "record shows them doing. The coverage quotes them saying "
            f"\"{s[:160]}\". The record shows \"{a[:160]}\". Those two cannot both "
            "be true as stated. I am not reading anyone's mind — both lines are "
            "linked below, read them yourself — but a gap this wide between the "
            "stated intent and the observed action is exactly what my beat exists "
            "to catch. That is why I am pushing back."
        )
    else:
        j.verdict = ALIGNED
        j.shadow_intent = (
            "The words and the deeds line up. What they said is what the "
            "record shows them doing — no second face on this one."
        )
    j.evidence_cited = ([_cite_claim(pack, i) for i in stated_ids[:3] if i in lookup]
                        + [_cite_quote(pack, i) for i in stated_ids[:3] if i in quotes]
                        + [_cite_claim(pack, i) for i in action_ids[:3]])
    return _seal(j)


def lens_nemesis(event_id: str, pack: Dict) -> NewsJudgment:
    """Nemesis — who is said to benefit vs who acts and gains.

    Extends: "Is it fair to all parties? Is the response proportionate?"
    Engages when 2+ actors are named.
    """
    if len(pack["actors"]) < 2:
        return _abstain("nemesis", event_id, pack,
                        "Fewer than two actors are named, so there is no "
                        "winners-and-losers to sort out. Sitting this one out.")
    lookup = _claim_lookup(pack)
    beneficiary_re = re.compile(
        r"(?:for|help(?:ing)?|benefit(?:ing|ed)?\s+(?:of\s+)?|protect(?:ing)?|"
        r"support(?:ing)?|serve[sd]?)\s+([A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*){0,2})")
    named_beneficiaries: List[str] = []
    for cid in pack["stated_intents"]:
        if cid in lookup:
            for m in beneficiary_re.finditer(lookup[cid]["text"]):
                b = m.group(1).strip().rstrip(".,;:")
                if b and b not in named_beneficiaries:
                    named_beneficiaries.append(b)
    action_actors = Counter()
    for cid in pack["observed_actions"]:
        if cid in lookup:
            from .cluster import proper_nouns
            action_actors.update(proper_nouns(lookup[cid]["text"]))
    top_actors = [a for a, _ in action_actors.most_common(3)]
    j = _new_judgment("nemesis", event_id, pack)
    j.projected_intent = ("The coverage says this is for "
                          + (", ".join(sorted(set(named_beneficiaries))[:4])
                             if named_beneficiaries else "someone — though it never quite names who"))
    cited = ([_cite_claim(pack, i) for i in pack["stated_intents"][:2] if i in lookup]
             + [_cite_claim(pack, i) for i in pack["observed_actions"][:2] if i in lookup])
    overlap = {b.lower() for b in named_beneficiaries} & {a.lower() for a in top_actors}
    if named_beneficiaries and top_actors and not overlap:
        j.verdict = DIVERGENT
        j.shadow_intent = (
            f"The coverage names {', '.join(sorted(set(named_beneficiaries))[:3])} "
            f"as the winners — but the people actually moving in the record "
            f"are {', '.join(top_actors)}. Different lists. So ask the question "
            "the coverage skips: who does this actually empower?"
        )
        j.divergence_why = (
            "My beat is winners and losers: who the coverage says benefits versus "
            "who is actually moving and positioned to gain. The coverage names "
            f"{', '.join(sorted(set(named_beneficiaries))[:3])} as the winners. But the "
            f"people actually acting in the record are {', '.join(top_actors)} — and "
            "the two lists share not one name. When the winners on paper and the "
            "winners in motion are different people, the coverage is answering "
            "\"who benefits\" with the press release instead of the evidence. "
            "That is why I am pushing back."
        )
    else:
        j.verdict = ALIGNED
        j.shadow_intent = (
            "No daylight between the stated winners and the people actually "
            "acting. Same names on both lists."
        )
    j.evidence_cited = cited
    return _seal(j)


def lens_hades(event_id: str, pack: Dict) -> NewsJudgment:
    """Hades — what is unseen.

    Extends: "What is unseen — hidden costs, externalities, unspoken risks?"
    Engages when coverage is thin (single outlet), quotes lack
    attribution, or no named actor speaks on the record. Its verdict is
    always about the gaps, cited specifically.
    """
    gaps: List[str] = []
    if len(pack["outlets"]) < 2:
        n = len(pack["outlets"])
        gaps.append(f"only {'one outlet' if n == 1 else f'{n} outlets'} "
                    f"({', '.join(pack['outlets'])}) "
                    "is covering this event — no independent telling to check it against")
    unattributed = [q for q in pack["quotes"] if not q["attributed_to"]]
    attributed = [q for q in pack["quotes"] if q["attributed_to"]]
    if pack["quotes"] and not attributed:
        gaps.append(f"{len(unattributed)} quoted passage(s) and not one of them "
                    "names its speaker")
    elif unattributed:
        gaps.append(f"{len(unattributed)} quoted passage(s) have no named speaker")
    if not pack["quotes"]:
        gaps.append("no direct quotes from any actor appear in what I read")
    if not gaps:
        return _abstain("hades", event_id, pack,
                        "Multiple outlets, named speakers on the record — I "
                        "cannot find a hole in this one. Sitting this out.")
    j = _new_judgment("hades", event_id, pack)
    j.projected_intent = "The coverage reads like the full picture."
    j.verdict = DIVERGENT
    j.shadow_intent = ("It is not. " + "; ".join(gaps) + ". "
                       "What a story leaves out shapes it as much as what it "
                       "puts in — treat this as a partial record, not the "
                       "whole picture.")
    j.divergence_why = (
        "My beat is what is missing. In this record: " + "; ".join(gaps) + ". "
        "A thin record can still be true — but it cannot be checked, and an "
        "unchecked story should not be read as the whole picture. What a story "
        "leaves out shapes it as much as what it puts in. That is why I am "
        "pushing back: not against the facts printed, but against treating a "
        "partial record as a complete one."
    )
    j.evidence_cited = ([{"ref": q["id"], "kind": "quote", "outlet": q["outlet"], "url": q["url"]}
                         for q in unattributed[:3]]
                        + [{"ref": f["outlet"], "kind": "framing",
                            "outlet": f["outlet"], "url": f["url"]}
                           for f in pack["framing"][:2]])
    return _seal(j)


def lens_demeter(event_id: str, pack: Dict) -> NewsJudgment:
    """Demeter — momentary blip or durable shift.

    Extends: "Does this sustain the principal's long-term interests, or extract short-term gain?"
    Engages when the event spans time or the claims carry durability signals.
    """
    lookup = _claim_lookup(pack)
    durability_words = ("law", "treaty", "deal", "agreement", "deployed",
                        "permanent", "long-term", "long term", "irreversible",
                        "passed", "ratified", "acquired", "merged")
    signals = [c for c in pack["claims"] if _mentions(c["text"], durability_words)]
    span = (pack["latest"] or 0) - (pack["earliest"] or 0)
    if not signals and span < 20 * 3600:
        return _abstain("demeter", event_id, pack,
                        "No sign this outlasts the news cycle — nothing durable "
                        "in the claims. Sitting this one out.")
    j = _new_judgment("demeter", event_id, pack)
    j.projected_intent = "Today's news, gone tomorrow — that is how it is presented."
    j.verdict = DIVERGENT
    bits = [f"\"{c['text'][:140]}\" ({c['outlet']})" for c in signals[:3]]
    if span >= 20 * 3600:
        bits.append(f"the event spans {span // 3600} hours across the articles I read")
    j.shadow_intent = ("It will outlast the cycle. " + ". ".join(bits) + ". "
                       "What gets planted here keeps growing after the cameras leave.")
    span_desc = (f"the event spans {span // 3600} hours across the articles I read"
                 if span >= 20 * 3600 else "")
    signal_desc = "; ".join(f"\"{c['text'][:120]}\" ({c['outlet']})" for c in signals[:3])
    j.divergence_why = (
        "My beat is durability: is this a one-day story or something with "
        "consequences that outlast the news cycle. "
        + (f"The claims carry lasting markers — {signal_desc}. " if signals else "")
        + (f"{span_desc[0].upper() + span_desc[1:]}. " if span_desc else "")
        + "Laws, deals, deployments — these do not evaporate when the cameras "
          "leave. Reading this as today's news, gone tomorrow, would miss the part "
          "that keeps happening after the cycle moves on. That is why I am pushing back."
    )
    j.evidence_cited = [_cite_claim(pack, c["id"]) for c in signals[:3]]
    return _seal(j)


def lens_dionysus(event_id: str, pack: Dict) -> NewsJudgment:
    """Dionysus — how contested is the factual ground.

    Extends: "How much uncontrolled variance does this introduce?"
    Engages when 2+ outlets cover the event. Variance here is
    disagreement between tellings.
    """
    if len(pack["outlets"]) < 2:
        return _abstain("dionysus", event_id, pack,
                        "One outlet, one telling — no variance to measure. "
                        "Sitting this out.")
    claims = pack["claims"]
    conflicts: List[tuple] = []
    for i in range(len(claims)):
        for k in range(i + 1, len(claims)):
            if claims[i]["outlet"] == claims[k]["outlet"]:
                continue
            if _conflicting_pair(claims[i]["text"], claims[k]["text"]):
                conflicts.append((claims[i], claims[k]))
                if len(conflicts) >= 3:
                    break
        if len(conflicts) >= 3:
            break
    j = _new_judgment("dionysus", event_id, pack)
    j.projected_intent = (f"{len(pack['outlets'])} outlets on this story, "
                          "and the coverage reads like the facts are settled.")
    if conflicts:
        j.verdict = DIVERGENT
        ex = conflicts[0]
        j.shadow_intent = (
            f"They are not settled. {ex[0]['outlet']} reports "
            f"\"{ex[0]['text'][:120]}\" while {ex[1]['outlet']} reports "
            f"\"{ex[1]['text'][:120]}\". That is not healthy disagreement — "
            "the factual ground is shifting under this story. Hold every "
            "telling loosely."
        )
        j.divergence_why = (
            "My beat is agreement between tellings: do the outlets actually agree "
            "on the facts. " + f"{ex[0]['outlet']} reports \"{ex[0]['text'][:120]}\" "
            f"while {ex[1]['outlet']} reports \"{ex[1]['text'][:120]}\" — those are "
            "colliding factual claims, not differences of interpretation. When the "
            "outlets disagree on what happened rather than what it means, the "
            "factual ground is shifting under the story, and every version has to "
            "be held loosely. That is why I am pushing back."
        )
        j.evidence_cited = [_cite_claim(pack, ex[0]["id"]), _cite_claim(pack, ex[1]["id"])]
    else:
        j.verdict = ALIGNED
        j.shadow_intent = ("For once, the tellings agree. No colliding claims "
                           "across outlets in what I read — the facts look as "
                           "settled as they read.")
        j.evidence_cited = [{"ref": f["outlet"], "kind": "framing",
                             "outlet": f["outlet"], "url": f["url"]}
                            for f in pack["framing"][:3]]
    return _seal(j)


def lens_eros(event_id: str, pack: Dict) -> NewsJudgment:
    """Eros — deception signals and trust.

    Extends: "Does this preserve or strengthen the principal relationship?"
    Engages ONLY when there are concrete deception indicators: the same
    attributed speaker contradicting themselves, or loaded unattributed
    quotes. Otherwise it abstains — trust is not graded on vibes.
    """
    by_speaker: Dict[str, List[Dict]] = {}
    for q in pack["quotes"]:
        if q["attributed_to"]:
            by_speaker.setdefault(q["attributed_to"], []).append(q)
    self_contradictions = []
    for speaker, qs in by_speaker.items():
        for i in range(len(qs)):
            for k in range(i + 1, len(qs)):
                if _conflicting_pair(qs[i]["text"], qs[k]["text"]):
                    self_contradictions.append((speaker, qs[i], qs[k]))
    loaded = ("corrupt", "stolen", "lies", "lying", "rigged", "fake",
              "hoax", "stupid", "evil", "criminal")
    loaded_unattributed = [q for q in pack["quotes"]
                           if not q["attributed_to"] and _mentions(q["text"], loaded)]
    if not self_contradictions and not loaded_unattributed:
        return _abstain("eros", event_id, pack,
                        "No deception markers — nobody contradicts themselves, "
                        "no loaded anonymous quotes. Trust is not graded on "
                        "vibes. Sitting this out.")
    j = _new_judgment("eros", event_id, pack)
    j.projected_intent = "The coverage asks to be taken at face value."
    j.verdict = DIVERGENT
    parts = []
    if self_contradictions:
        sp, q1, q2 = self_contradictions[0]
        parts.append(f'{sp} is on the record saying both "{q1["text"][:100]}" and '
                     f'"{q2["text"][:100]}" — those two do not sit together')
    if loaded_unattributed:
        q = loaded_unattributed[0]
        parts.append(f'a loaded quote is circulating with no name behind it: "{q["text"][:100]}" '
                     f'({q["outlet"]})')
    j.shadow_intent = ("Do not take it at face value. " + "; ".join(parts) + ". "
                       "Strong language with no name behind it, or one speaker "
                       "telling it two ways — something in this record is not "
                       "what it claims to be.")
    j.divergence_why = (
        "My beat is deception markers, and I only engage on hard ones — never "
        "vibes. Here the marker is concrete: " + "; ".join(parts) + ". A speaker on "
        "the record telling it two incompatible ways, or loaded language with no "
        "name behind it — these are the patterns that precede a record that is not "
        "what it claims to be. One of them is present here. That is why I am pushing back."
    )
    cited = []
    for sp, q1, q2 in self_contradictions[:1]:
        cited += [_cite_quote(pack, q1["id"]), _cite_quote(pack, q2["id"])]
    for q in loaded_unattributed[:2]:
        cited.append(_cite_quote(pack, q["id"]))
    j.evidence_cited = cited
    return _seal(j)


def lens_persephone(event_id: str, pack: Dict) -> NewsJudgment:
    """Persephone — can what was done be undone.

    Extends: "Is it reversible? What happens on repetition — what returns?"
    Engages when the observed actions include consequential, hard-to-undo
    acts.
    """
    lookup = _claim_lookup(pack)
    consequential = ("signed into law", "signed", "deployed", "fired",
                     "struck", "arrested", "banned", "acquired", "imposed",
                     "resigned", "launched")
    hits = [c for c in pack["claims"]
            if c["id"] in pack["observed_actions"] and _mentions(c["text"], consequential)]
    if not hits:
        return _abstain("persephone", event_id, pack,
                        "Nothing here is hard to undo — no arrests, bans, "
                        "strikes, or signings. Sitting this out.")
    reversible_words = ("temporary", "pause", "paused", "review", "suspend",
                        "interim", "pilot", "trial")
    presented_reversible = any(_mentions(c["text"], reversible_words) for c in pack["claims"])
    j = _new_judgment("persephone", event_id, pack)
    j.projected_intent = ("Presented as just another development"
                          + (" — though some coverage calls it temporary or under review."
                             if presented_reversible else "."))
    j.verdict = DIVERGENT
    j.shadow_intent = ("There is no undoing this. "
                       + " ".join(f"\"{c['text'][:130]}\" ({c['outlet']})." for c in hits[:3])
                       + " What is done here does not come back — "
                       + ("no reversal path appears anywhere in the claims."
                          if not presented_reversible
                          else "the \"temporary\" label has no reversal mechanism behind it in the claims."))
    acts = " ".join(f"\"{c['text'][:130]}\" ({c['outlet']})." for c in hits[:3])
    j.divergence_why = (
        "My beat is reversibility: can what was done be undone. The record shows "
        + acts + " Signings, firings, bans, strikes, arrests — none of these reverse "
        "cleanly; once done, they are permanent fact. The coverage presents it as "
        + ("\"temporary,\" but no reversal mechanism appears anywhere in the claims. "
           if presented_reversible else "just another development, but nothing here comes back. ")
        + "Tone does not un-sign a law. That is why I am pushing back."
    )
    j.evidence_cited = [_cite_claim(pack, c["id"]) for c in hits[:3]]
    return _seal(j)


LENSES = {
    "hermes": lens_hermes,
    "janus": lens_janus,
    "nemesis": lens_nemesis,
    "hades": lens_hades,
    "demeter": lens_demeter,
    "dionysus": lens_dionysus,
    "eros": lens_eros,
    "persephone": lens_persephone,
}

# Canonical order for dossiers: the framing lenses first, then the rest.
LENS_ORDER = ["hermes", "janus", "nemesis", "hades",
              "demeter", "dionysus", "eros", "persephone"]


def hear_all(event_id: str, pack: Dict) -> List[NewsJudgment]:
    """Run all eight lenses over one event's evidence pack."""
    return [LENSES[aid](event_id, pack) for aid in LENS_ORDER]


def panel_summary(judgments: List[NewsJudgment]) -> Dict[str, Any]:
    """Structured dissent summary — mirrors assessors.panel()'s contract.

    Dissent is surfaced, never averaged. Abstentions are listed, not hidden.
    """
    engaged = [j for j in judgments if j.verdict != ABSTAIN]
    divergent = [j for j in engaged if j.verdict == DIVERGENT]
    aligned = [j for j in engaged if j.verdict == ALIGNED]
    abstained = [j for j in judgments if j.verdict == ABSTAIN]
    if divergent and aligned:
        verdict = "contested"
    elif divergent:
        verdict = "divergent"
    elif aligned:
        verdict = "aligned"
    else:
        verdict = "silent"  # every lens abstained — thin evidence
    return {
        "verdict": verdict,
        "engaged": [j.assessor_id for j in engaged],
        "divergent": [j.assessor_id for j in divergent],
        "aligned": [j.assessor_id for j in aligned],
        "abstained": [{"assessor_id": j.assessor_id, "reason": j.abstain_reason}
                       for j in abstained],
        "dissent": [
            {"assessor_id": j.assessor_id,
             "domain_question": j.domain_question,
             "projected_intent": j.projected_intent,
             "shadow_intent": j.shadow_intent,
             "evidence_cited": j.evidence_cited}
            for j in divergent
        ],
    }
