# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Prospect discovery for the autonomous outreach machine.

This module FINDS real prospects from public web sources. It plugs into
the existing store (prospects.add_prospect / prospects.import_csv) and the
existing 0-100 rubric (prospects.score_prospect) — it replaces neither.

The honesty contract (same as prospects.py and research.py):
  * NEVER invent data. A record enters the store only if every non-empty
    field carries a public source URL. validate_record() enforces this and
    raises on anything unattributed.
  * Emails are recorded as observed or as explicitly flagged guesses:
      - observed on a public page -> email_verified=True, source URL kept.
      - pattern-guessed (e.g. first.last@domain from a listed pattern) ->
        email_verified=False and the notes carry "EMAIL UNVERIFIED" plus the
        basis of the guess. Never presented as confirmed.
  * Signals fed to the rubric are caller-attested from OBSERVED facts only.
    contactable=True requires a verified email. Unknowns score 0 — the
    machine says the pipeline is thin instead of inflating it.
  * Discovery writes status="new" records only. Nothing discovered here is
    sendable: run.py only touches prospects with a research brief attached
    by research.py, which re-verifies everything independently.

Polite crawling (fetch toolkit):
  * robots_allows() — pure-function robots.txt evaluator. Callers must check
    the target site's robots.txt before fetching and obey it.
  * RateLimiter — minimum interval between fetches to one host plus
    exponential backoff on HTTP 429, with a cap. Never hammer anyone.
  * This module does NOT fetch the network itself in this environment: page
    text arrives via the caller's approved web-reading tools and is passed
    to the extract_* helpers with its source URL. The fetch rules above
    bind whatever does the fetching.

No purchased lists, no dark patterns, no fake-personalization fodder.
"""

import csv
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from . import config
from . import prospects


# ---------------------------------------------------------------------------
# Record schema
# ---------------------------------------------------------------------------
# A discovery record is a plain dict:
#   org            (required) organization / firm / company name
#   contact_name   (optional) person name, ONLY if publicly listed
#   role           (optional) their role/title, ONLY if publicly listed
#   email          (optional) observed or pattern-guessed address
#   email_verified (bool)     True iff the exact address was observed in
#                             fetched public page text (not guessed)
#   email_source   (optional) URL where the email was observed, or a
#                             description of the guess basis
#   field_sources  {field: url} — a public source URL for EVERY non-empty
#                             field among org/contact_name/role/email
#   niche          (optional) e.g. "family-law-tx", "ai-agent-startups"
#   source_name    (optional) e.g. "firm-website", "yc-directory"
#   observations   (optional) [{fact, source}] observed, attributable facts
#                             usable later by research.py
#   fetched_at     auto-added ISO timestamp on validation

REQUIRED_ATTRIBUTION_FIELDS = ("org", "contact_name", "role", "email")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def validate_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Enforce the attribution contract. Raises ValueError on any gap.

    Returns a normalized copy with fetched_at stamped.
    """
    if not isinstance(rec, dict):
        raise ValueError("record must be a dict")
    org = (rec.get("org") or "").strip()
    if not org:
        raise ValueError("record needs an org name — never invent one")
    sources = rec.get("field_sources") or {}
    if not isinstance(sources, dict):
        raise ValueError("field_sources must be a {field: url} dict")
    for field in REQUIRED_ATTRIBUTION_FIELDS:
        val = (rec.get(field) or "")
        if isinstance(val, str):
            val = val.strip()
        if val:
            url = (sources.get(field) or "").strip()
            if not url:
                raise ValueError(
                    f"field {field!r} has a value but no source URL — "
                    "every field must be attributed"
                )
            _require_http_url(url, field)
    email = (rec.get("email") or "").strip()
    if email:
        if not EMAIL_RE.fullmatch(email):
            raise ValueError(f"not a valid email: {email!r}")
        if not isinstance(rec.get("email_verified"), bool):
            raise ValueError(
                "email present but email_verified is not a bool — "
                "observed or guessed must be declared"
            )
        if not rec["email_verified"] and not (rec.get("email_source") or "").strip():
            raise ValueError(
                "unverified (pattern-guessed) email needs email_source "
                "describing the basis of the guess"
            )
    obs = rec.get("observations") or []
    for o in obs:
        if not (o.get("fact") or "").strip() or not (o.get("source") or "").strip():
            raise ValueError("every observation needs both 'fact' and 'source'")
    out = dict(rec)
    out["org"] = org
    out["fetched_at"] = _now()
    return out


def _require_http_url(url: str, field: str) -> None:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise ValueError(f"field {field!r} source is not a valid http(s) URL: {url!r}")


# ---------------------------------------------------------------------------
# Email helpers
# ---------------------------------------------------------------------------

def extract_emails_from_text(text: str) -> List[str]:
    """Harvest literal email addresses from fetched page text.

    An address found this way is OBSERVED, not guessed — but the caller must
    still pass the page URL as its source so validate_record() accepts it.
    """
    seen: List[str] = []
    for m in EMAIL_RE.finditer(text or ""):
        addr = m.group(0).lower()
        # skip obvious non-contacts
        if addr.endswith((".png", ".jpg", ".gif", ".svg")):
            continue
        if addr not in seen:
            seen.append(addr)
    return seen


def derive_email_pattern(
    first: str, last: str, domain: str, pattern: str = "first.last"
) -> Tuple[str, bool]:
    """Build a pattern-guessed address. ALWAYS returns verified=False.

    Patterns: first.last | firstlast | f.last | first | first_last.
    The guess basis (pattern + domain + the listed name it came from) must
    be recorded by the caller in email_source. Never presented as confirmed.
    """
    first = (first or "").strip().lower()
    last = (last or "").strip().lower()
    domain = (domain or "").strip().lower()
    if not first or not domain:
        raise ValueError("derive_email_pattern needs at least a first name and domain")
    local = {
        "first.last": f"{first}.{last}" if last else first,
        "firstlast": f"{first}{last}",
        "f.last": f"{first[0]}.{last}" if last else first,
        "first": first,
        "first_last": f"{first}_{last}" if last else first,
    }.get(pattern)
    if local is None:
        raise ValueError(f"unknown email pattern: {pattern!r}")
    return f"{local}@{domain}", False


# ---------------------------------------------------------------------------
# Signal mapping (honest: observed facts only)
# ---------------------------------------------------------------------------

def signals_for_record(rec: Dict[str, Any]) -> Dict[str, bool]:
    """Map a validated record to the 5 rubric signals.

    contactable=True ONLY for verified emails. Everything else needs an
    observation whose text supports it (keyword heuristics over the
    observation facts, each of which already carries a source).
    Unknowns stay False — no inflation.
    """
    signals: Dict[str, bool] = {
        "deploys_ai_agents": False,
        "agent_trust_pain": False,
        "contactable": bool(rec.get("email_verified")),
        "team_size_fit": False,
        "budget_signal": False,
    }
    facts = " ".join(
        (o.get("fact") or "") for o in (rec.get("observations") or [])
    ).lower()
    niche = (rec.get("niche") or "").lower()
    org = (rec.get("org") or "").lower()

    if any(k in facts for k in ("ai agent", "ai agents", "agentic", "autonomous agent")):
        signals["deploys_ai_agents"] = True
    if any(k in facts for k in (
        "soc 2", "compliance", "audit", "enterprise customer",
        "trust", "security review", "incident", "oversight",
        "governance", "permissioning",
    )):
        signals["agent_trust_pain"] = True
    if any(k in facts for k in (
        "boutique", "small firm", "solo", "founder-led", "founded by",
        "founding team", "founders", "co-founder", "2-person",
        "small team", "team of", " attorneys", "seed", "pre-seed",
        "series a",
    )):
        signals["team_size_fit"] = True
    if any(k in facts for k in (
        "raised", "funding", "backed", "hiring", "accelerator",
        "yc ", "yc-", "$", "million",
    )):
        signals["budget_signal"] = True
    # Law-firm niche: small/mid-size firms are the team_size_fit by construction
    # when the firm site itself shows a small attorney roster... only if observed.
    _ = (niche, org)  # niche/org kept for future explicit rules, not vibes
    return signals


# ---------------------------------------------------------------------------
# Import into the prospect store (the existing import path)
# ---------------------------------------------------------------------------

def _attribution_notes(rec: Dict[str, Any]) -> str:
    lines = [f"discovery source: {rec.get('source_name') or 'unknown'}",
             f"niche: {rec.get('niche') or 'unknown'}"]
    for field in REQUIRED_ATTRIBUTION_FIELDS:
        val = rec.get(field)
        if val:
            lines.append(f"{field}: {val}  <- {rec['field_sources'].get(field)}")
    if rec.get("email"):
        lines.append(
            "email_verified: YES (observed on public page)"
            if rec.get("email_verified")
            else f"EMAIL UNVERIFIED — pattern-guessed, basis: {rec.get('email_source')}"
        )
    for o in rec.get("observations") or []:
        lines.append(f"observed: {o['fact']}  <- {o['source']}")
    lines.append(f"fetched_at: {rec.get('fetched_at')}")
    return "\n".join(lines)


def import_records(
    records: List[Dict[str, Any]], source_name: str = "discovery"
) -> Dict[str, Any]:
    """Validate + import discovery records into the prospect store.

    Uses prospects.add_prospect (the existing import path): scoring comes
    from the existing rubric, duplicates by email are refused and counted
    as skipped. Returns {'added': n, 'skipped': n, 'errors': [...]}.
    Every record keeps full source attribution in its notes.
    """
    added, skipped = 0, 0
    errors: List[str] = []
    for i, raw in enumerate(records):
        try:
            rec = validate_record(raw)
        except ValueError as exc:
            errors.append(f"record {i} ({(raw.get('org') if isinstance(raw, dict) else '?')}) invalid: {exc}")
            skipped += 1
            continue
        if not rec.get("source_name"):
            rec["source_name"] = source_name
        signals = signals_for_record(rec)
        try:
            prospects.add_prospect(
                name=(rec.get("contact_name") or "").strip() or rec["org"],
                email=rec.get("email") or "",
                company=rec["org"],
                role=(rec.get("role") or "").strip(),
                signals=signals,
                source=f"discovery:{rec['source_name']}",
                notes=_attribution_notes(rec),
            )
            added += 1
        except ValueError as exc:
            # invalid email shape or duplicate — counted, never forced in
            errors.append(f"record {i} ({rec['org']}) not imported: {exc}")
            skipped += 1
    return {"added": added, "skipped": skipped, "errors": errors}


def to_csv_rows(records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Render validated records as rows for prospects.import_csv.

    Lets discovery output flow through the pre-existing CSV import path too.
    Signal columns use 'yes'/'no' per import_csv's contract.
    """
    rows: List[Dict[str, str]] = []
    for raw in records:
        rec = validate_record(raw)
        signals = signals_for_record(rec)
        rows.append({
            "name": (rec.get("contact_name") or "").strip() or rec["org"],
            "email": (rec.get("email") or "").strip(),
            "company": rec["org"],
            "role": (rec.get("role") or "").strip(),
            "notes": _attribution_notes(rec),
            "deploys_ai_agents": "yes" if signals["deploys_ai_agents"] else "no",
            "agent_trust_pain": "yes" if signals["agent_trust_pain"] else "no",
            "contactable": "yes" if signals["contactable"] else "no",
            "team_size_fit": "yes" if signals["team_size_fit"] else "no",
            "budget_signal": "yes" if signals["budget_signal"] else "no",
        })
    return rows


def write_csv(records: List[Dict[str, Any]], path: str) -> str:
    """Write discovery records to a CSV importable by prospects.import_csv."""
    rows = to_csv_rows(records)
    fieldnames = ["name", "email", "company", "role", "notes",
                  "deploys_ai_agents", "agent_trust_pain", "contactable",
                  "team_size_fit", "budget_signal"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return path


# ---------------------------------------------------------------------------
# Polite fetch toolkit (binds whatever performs the fetching)
# ---------------------------------------------------------------------------

class RateLimiter:
    """Minimum interval between fetches to a host + exponential 429 backoff.

    Pure logic: clock and sleeper are injectable so tests never wait.
    A fetcher calls wait(host) before each request and note_result(host,
    status) after. On 429 the host's backoff doubles (up to backoff_max_s);
    any non-429 success resets it.
    """

    def __init__(
        self,
        min_interval_s: float = 2.0,
        backoff_base_s: float = 5.0,
        backoff_max_s: float = 300.0,
        clock: Optional[Callable[[], float]] = None,
        sleeper: Optional[Callable[[float], None]] = None,
    ):
        self.min_interval_s = min_interval_s
        self.backoff_base_s = backoff_base_s
        self.backoff_max_s = backoff_max_s
        self._clock = clock or time.monotonic
        self._sleep = sleeper or time.sleep
        self._last_fetch: Dict[str, float] = {}
        self._backoff_until: Dict[str, float] = {}
        self._backoff_level: Dict[str, int] = {}

    def wait(self, host: str) -> float:
        """Sleep until this host may be fetched. Returns seconds waited."""
        now = self._clock()
        wait_s = 0.0
        ready_at = self._backoff_until.get(host, 0.0)
        if ready_at > now:
            wait_s = max(wait_s, ready_at - now)
        last = self._last_fetch.get(host)
        if last is not None:
            gap = self.min_interval_s - (now - last)
            if gap > 0:
                wait_s = max(wait_s, gap)
        if wait_s > 0:
            self._sleep(wait_s)
            now = self._clock()
        self._last_fetch[host] = now
        return wait_s

    def note_result(self, host: str, status: int) -> None:
        """Feed back the HTTP status. 429 escalates backoff; else resets."""
        if status == 429:
            level = self._backoff_level.get(host, 0)
            delay = min(self.backoff_base_s * (2 ** level), self.backoff_max_s)
            self._backoff_until[host] = self._clock() + delay
            self._backoff_level[host] = level + 1
        else:
            self._backoff_until.pop(host, None)
            self._backoff_level.pop(host, None)

    def backoff_level(self, host: str) -> int:
        return self._backoff_level.get(host, 0)


def robots_allows(robots_text: str, user_agent: str, path: str) -> bool:
    """Minimal robots.txt evaluator (pure function, no network).

    Groups by User-agent (exact match preferred, '*' fallback). Within the
    winning group, the longest matching Allow/Disallow rule wins; ties go to
    Allow. No matching rule -> allowed. Malformed lines are ignored.
    """
    groups: List[Tuple[List[str], List[Tuple[str, str]]]] = []
    cur_agents: List[str] = []
    cur_rules: List[Tuple[str, str]] = []
    ua = (user_agent or "").lower()

    def flush() -> None:
        if cur_agents or cur_rules:
            groups.append((cur_agents, cur_rules))

    for raw in (robots_text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "user-agent":
            if cur_rules:
                flush()
                cur_agents, cur_rules = [], []
            cur_agents.append(val.lower())
        elif key in ("allow", "disallow"):
            cur_rules.append((key, val))
    flush()

    chosen: Optional[List[Tuple[str, str]]] = None
    for agents, rules in groups:
        if ua in agents:
            chosen = rules
            break
    if chosen is None:
        for agents, rules in groups:
            if "*" in agents:
                chosen = rules
                break
    if not chosen:
        return True

    best: Optional[Tuple[str, str]] = None
    for kind, rule_path in chosen:
        if not rule_path:
            if kind == "disallow":
                continue  # "Disallow:" (empty) = allow all
            best_len = -1
        else:
            rp = rule_path
            # simple prefix match; '*' wildcards treated as prefix up to '*'
            if "*" in rp:
                rp = rp.split("*")[0]
            if not path.startswith(rp):
                continue
            best_len = len(rp)
        if best is None or best_len > len(best[1].split("*")[0]):
            best = (kind, rule_path)
    if best is None:
        return True
    return best[0] == "allow"


# ---------------------------------------------------------------------------
# Source adapters (each yields validated record dicts)
# ---------------------------------------------------------------------------
# Adapters are small, niche-specific extractors over fetched page text.
# They never invent: every field they set must come from the text with the
# page URL recorded in field_sources.

def adapt_firm_contact_page(
    org: str,
    page_text: str,
    page_url: str,
    niche: str = "family-law",
    source_name: str = "firm-website",
) -> List[Dict[str, Any]]:
    """One record per observed email on a firm's public contact page.

    Contact name/role stay unset unless the caller supplies a verified
    pairing — heuristic name guessing is fabrication-adjacent and stays out.
    """
    emails = extract_emails_from_text(page_text)
    records: List[Dict[str, Any]] = []
    for addr in emails:
        rec: Dict[str, Any] = {
            "org": org,
            "email": addr,
            "email_verified": True,
            "email_source": page_url,
            "field_sources": {"org": page_url, "email": page_url},
            "niche": niche,
            "source_name": source_name,
        }
        records.append(rec)
    return records


def adapt_startup_profile(
    org: str,
    page_text: str,
    page_url: str,
    founder_name: str = "",
    founder_role: str = "",
    niche: str = "ai-agent-startups",
    source_name: str = "startup-site",
) -> List[Dict[str, Any]]:
    """One record per observed email on a startup's public site/profile."""
    emails = extract_emails_from_text(page_text)
    records: List[Dict[str, Any]] = []
    for addr in emails:
        rec: Dict[str, Any] = {
            "org": org,
            "email": addr,
            "email_verified": True,
            "email_source": page_url,
            "field_sources": {"org": page_url, "email": page_url},
            "niche": niche,
            "source_name": source_name,
        }
        if founder_name.strip():
            # founder identity must itself be sourced — same page counts
            rec["contact_name"] = founder_name.strip()
            rec["field_sources"]["contact_name"] = page_url
        if founder_role.strip():
            rec["role"] = founder_role.strip()
            rec["field_sources"]["role"] = page_url
        records.append(rec)
    return records
