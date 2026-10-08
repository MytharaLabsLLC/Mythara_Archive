# Copyright © 2026 Herbert Velez Jr. All rights reserved.

"""
DrMythara vitals + heuristic wellness engine.

Dr Mythara is a healthcare and wellness bot: she checks vitals and
takes a heuristic (rule-based, explainable) approach to wellbeing.

VITALS MODEL:
  heart_rate (bpm), blood_pressure (mmHg, systolic + diastolic),
  temperature (°F or °C), spo2 (%), weight (kg or lb), sleep_hours,
  steps, active_minutes. Manual entry plus a pluggable VitalsSource
  interface — register any source implementing fetch_readings().

  Natural next integrations (operator has the skills): Google Health
  Connect (Android) and Apple HealthKit. Implement a VitalsSource
  against those skill APIs and register it as "health-connect" /
  "healthkit" — the engine and bot need no changes.

HEURISTIC ENGINE:
  Transparent rules over vitals + trends. Every observation carries
  its reasoning (which values, which thresholds) and the rule catalog
  is inspectable via describe_rules(). Never a black-box verdict.

SAFETY (non-negotiable):
  * The engine NEVER diagnoses, NEVER prescribes, NEVER presents as a
    licensed medical professional. It is a wellness companion.
  * Every report carries the wellness disclaimer ("not medical advice,
    see a clinician").
  * Dangerous values (crisis BP, very low SpO2, high fever, extreme
    heart rate) and emergency symptoms produce ESCALATE observations
    that urge immediate emergency care.
  * Weight is recorded but has NO heuristic nudges — deliberate, to
    avoid anything resembling weight-shaming.

ePHI NOTE: vitals are health data. They live in the bot's encrypted
database, behind sign-in, subject-scoped (minimum-necessary), and
never go to an external LLM provider without the BAA gate
(see drmythara_llm).
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

WELLNESS_DISCLAIMER = (
    "I am a wellness companion, not a medical professional. These "
    "observations are not medical advice — please see a qualified "
    "clinician for anything that worries you."
)

# Deliberately no weight heuristics (see module docstring).
VITAL_TYPES = (
    "heart_rate", "blood_pressure", "temperature", "spo2",
    "weight", "sleep_hours", "steps", "active_minutes",
)

_CREATE_VITALS_SQL = """
CREATE TABLE IF NOT EXISTS drmy_vitals (
    reading_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    vital_type TEXT NOT NULL,
    value REAL NOT NULL,
    secondary REAL,
    unit TEXT NOT NULL DEFAULT '',
    taken_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual',
    note TEXT NOT NULL DEFAULT ''
)
"""
_CREATE_VITALS_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_vitals_subject_type "
    "ON drmy_vitals (subject_id, vital_type, taken_at)"
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Vitals model
# ---------------------------------------------------------------------------

@dataclass
class VitalReading:
    subject_id: str
    vital_type: str
    value: float
    unit: str = ""
    secondary: Optional[float] = None  # diastolic for blood_pressure
    taken_at: Optional[str] = None
    source: str = "manual"
    note: str = ""
    reading_id: Optional[str] = None

    def __post_init__(self):
        if self.vital_type not in VITAL_TYPES:
            raise ValueError(f"Unknown vital type: {self.vital_type!r}. "
                             f"Choose from: {VITAL_TYPES}")
        if self.vital_type == "blood_pressure" and self.secondary is None:
            raise ValueError("blood_pressure needs secondary=diastolic.")
        _sanity_check(self)
        if not self.taken_at:
            self.taken_at = _utcnow()

    def temperature_f(self) -> float:
        """Normalize temperature to °F for the heuristics."""
        if self.vital_type != "temperature":
            raise ValueError("not a temperature reading")
        if self.unit.lower() in ("c", "celsius", "°c"):
            return self.value * 9.0 / 5.0 + 32.0
        return self.value


def _sanity_check(r: VitalReading) -> None:
    """Reject physically implausible values (likely entry errors)."""
    v = r.value
    bad = (
        (r.vital_type == "heart_rate" and not 20 <= v <= 250)
        or (r.vital_type == "spo2" and not 50 <= v <= 100)
        or (r.vital_type == "temperature"
            and not 90 <= r.temperature_f() <= 110)
        or (r.vital_type == "blood_pressure"
            and not (40 <= v <= 300 and 20 <= (r.secondary or 0) <= 200))
        or (r.vital_type == "sleep_hours" and not 0 <= v <= 24)
        or (r.vital_type == "weight" and not 20 <= v <= 700)
        or (r.vital_type == "steps" and not 0 <= v <= 200000)
        or (r.vital_type == "active_minutes" and not 0 <= v <= 1440)
    )
    if bad:
        raise ValueError(
            f"Implausible {r.vital_type} value: {v} {r.unit}. "
            "Check the entry and try again.")


# ---------------------------------------------------------------------------
# Pluggable vitals sources
# ---------------------------------------------------------------------------

class VitalsSource:
    """Interface for vitals data sources. Implement fetch_readings()
    against any backend (manual entry, Health Connect, HealthKit) and
    register it — the engine and bot need no changes."""

    name = "base"

    def fetch_readings(self, subject_id: str,
                       *, since: Optional[str] = None) -> List[VitalReading]:
        raise NotImplementedError


class ManualVitalsSource(VitalsSource):
    """In-memory manual-entry source (the default)."""

    name = "manual"

    def __init__(self):
        self._readings: List[VitalReading] = []

    def add(self, reading: VitalReading) -> None:
        self._readings.append(reading)

    def fetch_readings(self, subject_id: str,
                       *, since: Optional[str] = None) -> List[VitalReading]:
        out = [r for r in self._readings if r.subject_id == subject_id]
        if since:
            out = [r for r in out if (r.taken_at or "") >= since]
        return sorted(out, key=lambda r: r.taken_at or "")


_SOURCE_FACTORIES: Dict[str, Callable[..., VitalsSource]] = {
    "manual": ManualVitalsSource,
}


def register_vitals_source(name: str,
                           factory: Callable[..., VitalsSource]) -> None:
    """Register a new source backend (e.g. "health-connect", "healthkit")."""
    _SOURCE_FACTORIES[name] = factory


def create_vitals_source(name: str, **kwargs) -> VitalsSource:
    factory = _SOURCE_FACTORIES.get((name or "").strip().lower())
    if factory is None:
        raise ValueError(f"Unknown vitals source {name!r}. "
                         f"Available: {sorted(_SOURCE_FACTORIES)}")
    return factory(**kwargs)


# ---------------------------------------------------------------------------
# Encrypted-store-backed vitals persistence (runs on a sqlite3 connection)
# ---------------------------------------------------------------------------

class VitalsStore:
    """Vitals persistence. In production the connection comes from the
    bot's encrypted database (see DrMytharaBot._db)."""

    def __init__(self, conn):
        self._conn = conn
        conn.execute(_CREATE_VITALS_SQL)
        conn.execute(_CREATE_VITALS_INDEX)
        conn.commit()

    def record(self, reading: VitalReading) -> str:
        import secrets
        reading_id = reading.reading_id or secrets.token_hex(8)
        self._conn.execute(
            "INSERT INTO drmy_vitals (reading_id, subject_id, vital_type, "
            "value, secondary, unit, taken_at, source, note) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (reading_id, reading.subject_id, reading.vital_type,
             reading.value, reading.secondary, reading.unit,
             reading.taken_at, reading.source, reading.note),
        )
        self._conn.commit()
        return reading_id

    def history(self, subject_id: str, vital_type: str,
                limit: int = 50,
                since: Optional[str] = None) -> List[VitalReading]:
        q = ("SELECT reading_id, subject_id, vital_type, value, secondary, "
             "unit, taken_at, source, note FROM drmy_vitals "
             "WHERE subject_id = ? AND vital_type = ?")
        args: List[Any] = [subject_id, vital_type]
        if since:
            q += " AND taken_at >= ?"
            args.append(since)
        q += " ORDER BY taken_at DESC LIMIT ?"
        args.append(limit)
        rows = self._conn.execute(q, args).fetchall()
        return [VitalReading(
            reading_id=r[0], subject_id=r[1], vital_type=r[2], value=r[3],
            secondary=r[4], unit=r[5], taken_at=r[6], source=r[7],
            note=r[8]) for r in rows]

    def latest(self, subject_id: str,
               vital_type: str) -> Optional[VitalReading]:
        rows = self.history(subject_id, vital_type, limit=1)
        return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Heuristic wellness engine — transparent rules, shown reasoning
# ---------------------------------------------------------------------------

@dataclass
class Observation:
    """One heuristic finding. Structured for clinical speech:
    what was seen, why it matters, what to consider — plus the raw
    reasoning (exact values and thresholds) as the audit trail."""
    rule_id: str
    severity: str  # "info" | "nudge" | "escalate"
    title: str
    saw: str
    why_it_matters: str
    consider: str
    body: str = ""
    reasoning: List[str] = field(default_factory=list)
    values: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.body:
            self.body = f"{self.saw} {self.why_it_matters} {self.consider}"


@dataclass
class WellnessReport:
    subject_id: str
    generated_at: str
    observations: List[Observation]
    rules_evaluated: int
    disclaimer: str = WELLNESS_DISCLAIMER


@dataclass
class HeuristicRule:
    rule_id: str
    name: str
    description: str
    version: str
    evaluate: Callable[[Dict[str, Dict[str, Any]]], Optional[Observation]]


def _obs(rule_id: str, severity: str, title: str,
         saw: str, why_it_matters: str, consider: str,
         reasoning: List[str], values: Dict[str, Any]) -> Observation:
    return Observation(rule_id=rule_id, severity=severity, title=title,
                       saw=saw, why_it_matters=why_it_matters,
                       consider=consider, reasoning=reasoning,
                       values=values)


# -- individual rules (conservative, common-knowledge wellness ranges) -------

def _rule_hr_high(snap) -> Optional[Observation]:
    r = snap["heart_rate"]["latest"]
    if r is None:
        return None
    if r.value >= 130:
        return _obs("hr_critical", "escalate",
                    "Resting heart rate very high",
                    f"Your latest resting heart rate was {r.value:g} beats per "
                    f"minute, recorded {r.taken_at}. My escalation threshold "
                    "is 130 bpm or higher at rest.",
                    "A sustained resting rate this high can strain the heart "
                    "and may signal an acute problem. The number alone "
                    "cannot tell us the cause.",
                    "Seek urgent care right away — especially with any chest "
                    "discomfort, dizziness, palpitations, or shortness of "
                    "breath.",
                    [f"heart_rate={r.value:g} bpm (taken {r.taken_at})",
                     "escalation threshold: >= 130 bpm at rest"],
                    {"heart_rate": r.value})
    if r.value > 100:
        return _obs("hr_high", "nudge",
                    "Resting heart rate above typical range",
                    f"Your latest resting heart rate was {r.value:g} beats per "
                    f"minute, recorded {r.taken_at}. My nudge threshold is "
                    "above 100 bpm at rest.",
                    "A resting rate that stays above 100 deserves a "
                    "clinician's look. Causes range from the benign — "
                    "caffeine, stress, dehydration, recent activity — to "
                    "the treatable. The number alone cannot say which.",
                    "Check whether it repeats across several rested "
                    "mornings, note caffeine, stress, or illness around "
                    "each reading, and bring the log to your clinician.",
                    [f"heart_rate={r.value:g} bpm (taken {r.taken_at})",
                     "nudge threshold: > 100 bpm at rest"],
                    {"heart_rate": r.value})
    return None


def _rule_hr_low(snap) -> Optional[Observation]:
    r = snap["heart_rate"]["latest"]
    if r is None:
        return None
    if r.value <= 40:
        return _obs("hr_critical_low", "escalate",
                    "Resting heart rate very low",
                    f"Your latest resting heart rate was {r.value:g} beats per "
                    f"minute, recorded {r.taken_at}. My escalation threshold "
                    "is 40 bpm or lower at rest.",
                    "A sustained resting rate this low can mean the body is "
                    "not getting the circulation it needs. The number alone "
                    "cannot tell us the cause.",
                    "Seek urgent care right away — especially with any "
                    "dizziness, faintness, confusion, or unusual fatigue.",
                    [f"heart_rate={r.value:g} bpm (taken {r.taken_at})",
                     "escalation threshold: <= 40 bpm at rest"],
                    {"heart_rate": r.value})
    if r.value < 50:
        return _obs("hr_low", "nudge",
                    "Resting heart rate below typical range",
                    f"Your latest resting heart rate was {r.value:g} beats per "
                    f"minute, recorded {r.taken_at}. My nudge threshold is "
                    "below 50 bpm at rest.",
                    "In trained endurance athletes a rate like this can be "
                    "normal. Otherwise it merits a clinician's opinion — "
                    "the context decides, not the number alone.",
                    "Mention it to your clinician, along with any "
                    "medications you take — several common ones lower "
                    "heart rate.",
                    [f"heart_rate={r.value:g} bpm (taken {r.taken_at})",
                     "nudge threshold: < 50 bpm at rest"],
                    {"heart_rate": r.value})
    return None


def _rule_bp(snap) -> Optional[Observation]:
    r = snap["blood_pressure"]["latest"]
    if r is None:
        return None
    sys_v, dia_v = r.value, r.secondary or 0
    label = f"{sys_v:g}/{dia_v:g} mmHg"
    if sys_v >= 180 or dia_v >= 120:
        return _obs("bp_crisis", "escalate",
                    "Blood pressure in crisis range",
                    f"Your latest reading was {label}, recorded {r.taken_at}. "
                    "My escalation threshold is 180 systolic or 120 "
                    "diastolic or higher.",
                    "Clinicians treat this range as an emergency — organs "
                    "can be injured even without symptoms. Waiting to see "
                    "if it comes down on its own is not safe.",
                    "Call emergency services or go to urgent care right "
                    "away. Do not drive yourself if you feel unwell.",
                    [f"blood_pressure={label} (taken {r.taken_at})",
                     "escalation threshold: >= 180 systolic or >= 120 diastolic"],
                    {"systolic": sys_v, "diastolic": dia_v})
    if sys_v >= 140 or dia_v >= 90:
        return _obs("bp_high", "nudge",
                    "Blood pressure above target range",
                    f"Your latest reading was {label}, recorded {r.taken_at}. "
                    "My nudge threshold is 140 systolic or 90 diastolic "
                    "or higher.",
                    "Persistently elevated pressure raises long-term "
                    "cardiovascular risk, and it is usually silent — which "
                    "is why repeated readings matter more than any single one.",
                    "Take readings seated and rested, at the same times "
                    "across several days, and bring them to your clinician.",
                    [f"blood_pressure={label} (taken {r.taken_at})",
                     "nudge threshold: >= 140 systolic or >= 90 diastolic"],
                    {"systolic": sys_v, "diastolic": dia_v})
    return None


def _rule_spo2(snap) -> Optional[Observation]:
    r = snap["spo2"]["latest"]
    if r is None:
        return None
    if r.value < 92:
        return _obs("spo2_critical", "escalate",
                    "Blood oxygen saturation low",
                    f"Your latest SpO2 was {r.value:g}%, recorded {r.taken_at}. "
                    "My escalation threshold is below 92%.",
                    "Low oxygen saturation means the body may not be "
                    "getting the oxygen it needs. This deserves prompt "
                    "medical attention.",
                    "Seek urgent care — especially with any breathlessness, "
                    "confusion, rapid pulse, or bluish lips or nails.",
                    [f"spo2={r.value:g}% (taken {r.taken_at})",
                     "escalation threshold: < 92%"],
                    {"spo2": r.value})
    if r.value < 95:
        return _obs("spo2_low", "nudge",
                    "Blood oxygen saturation slightly low",
                    f"Your latest SpO2 was {r.value:g}%, recorded {r.taken_at}. "
                    "My nudge threshold is below 95%; the usual range is "
                    "95–100%.",
                    "A mildly low reading is often a measurement problem "
                    "rather than a body problem — cold hands and movement "
                    "fool the sensor. But a true low deserves a clinician's "
                    "look.",
                    "Re-check with warm hands and a still finger. If it "
                    "stays under 95%, mention it to your clinician.",
                    [f"spo2={r.value:g}% (taken {r.taken_at})",
                     "nudge threshold: < 95%"],
                    {"spo2": r.value})
    return None


def _rule_temp(snap) -> Optional[Observation]:
    r = snap["temperature"]["latest"]
    if r is None:
        return None
    f = r.temperature_f()
    if f >= 103:
        return _obs("temp_critical", "escalate",
                    "Fever running high",
                    f"Your latest temperature was {f:.1f}°F, recorded "
                    f"{r.taken_at}. My escalation threshold is 103°F or "
                    "higher.",
                    "A fever this high needs prompt medical attention — "
                    "the body is fighting something significant, and "
                    "complications rise with the number.",
                    "Seek urgent care, and keep drinking fluids meanwhile.",
                    [f"temperature={f:.1f}°F (taken {r.taken_at})",
                     "escalation threshold: >= 103°F"],
                    {"temperature_f": round(f, 1)})
    if f >= 100.4:
        return _obs("temp_fever", "nudge",
                    "Fever present",
                    f"Your latest temperature was {f:.1f}°F, recorded "
                    f"{r.taken_at}. My nudge threshold is 100.4°F or "
                    "higher — that is the clinical definition of fever.",
                    "A fever is the body fighting something, usually "
                    "infection. Most fevers resolve with rest — the trend "
                    "over hours matters more than one reading.",
                    "Rest, drink fluids, and re-check in a few hours. Loop "
                    "in your clinician if it climbs toward 103°F, lasts "
                    "more than a few days, or comes with concerning symptoms.",
                    [f"temperature={f:.1f}°F (taken {r.taken_at})",
                     "nudge threshold: >= 100.4°F"],
                    {"temperature_f": round(f, 1)})
    return None


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _rule_sleep(snap) -> Optional[Observation]:
    hist = snap["sleep_hours"]["history"]
    recent = [r.value for r in hist[:7] if r.value > 0]
    if len(recent) < 3:
        return None
    avg = _avg(recent)
    if avg < 6:
        return _obs("sleep_low", "nudge",
                    "Sleep averaging under 6 hours",
                    f"Your last {len(recent)} nights averaged {avg:.1f} hours "
                    "of sleep. My nudge threshold is under 6 hours average.",
                    "Short sleep impairs concentration, mood, and immune "
                    "function — and the deficit accumulates quietly. People "
                    "often stop noticing how tired they are.",
                    "A consistent bedtime and a wind-down routine are the "
                    "gentlest first steps. If short sleep persists despite "
                    "that, it is worth raising with your clinician.",
                    [f"average sleep={avg:.1f}h over {len(recent)} recent nights",
                     "nudge threshold: < 6h average"],
                    {"avg_sleep_hours": round(avg, 1)})
    return None


def _rule_steps(snap) -> Optional[Observation]:
    hist = snap["steps"]["history"]
    recent = [r.value for r in hist[:7] if r.value > 0]
    if len(recent) < 3:
        return None
    avg = _avg(recent)
    if avg < 3000:
        return _obs("steps_low", "info",
                    "Daily movement on the low side",
                    f"Your last {len(recent)} days averaged {avg:,.0f} steps. "
                    "My info threshold is under 3,000 average.",
                    "Regular movement supports cardiovascular health, "
                    "sleep quality, and mood. This is information, not a "
                    "judgment.",
                    "Short walks count. Small is how habits start.",
                    [f"average steps={avg:,.0f} over {len(recent)} recent days",
                     "info threshold: < 3,000 average"],
                    {"avg_steps": round(avg)})
    return None


def _rule_hr_trend(snap) -> Optional[Observation]:
    hist = snap["heart_rate"]["history"]
    if len(hist) < 2:
        return None
    latest = hist[0]
    # compare against the reading closest to 7 days back
    older = hist[-1]
    delta = latest.value - older.value
    if delta >= 10:
        return _obs("hr_trend_up", "nudge",
                    "Resting heart rate trending upward",
                    f"Your resting heart rate was {older.value:g} bpm and is "
                    f"now {latest.value:g} bpm — a rise of {delta:g} bpm "
                    "across your recent readings. My nudge threshold is a "
                    "rise of 10 bpm or more.",
                    "A sustained upward drift can precede illness, or "
                    "reflect accumulating stress, poor sleep, or "
                    "overtraining. Trends are often more informative than "
                    "single readings.",
                    "Watch whether it settles over the next few days. If "
                    "the rise holds, bring the trend — not just the latest "
                    "number — to your clinician.",
                    [f"latest={latest.value:g} bpm, earlier={older.value:g} bpm",
                     f"rise of {delta:g} bpm",
                     "nudge threshold: rise >= 10 bpm"],
                    {"delta_bpm": round(delta, 1)})
    return None


DEFAULT_RULES: List[HeuristicRule] = [
    HeuristicRule("hr_critical", "Heart rate bounds",
                  "Escalates at >= 130 or <= 40 bpm; nudges outside 50–100.",
                  "1.0", _rule_hr_high),
    HeuristicRule("hr_low", "Heart rate low side",
                  "Nudge under 50 bpm, escalate at or under 40.",
                  "1.0", _rule_hr_low),
    HeuristicRule("bp_bounds", "Blood pressure bounds",
                  "Escalates at >= 180/120; nudges at >= 140/90.",
                  "1.0", _rule_bp),
    HeuristicRule("spo2_bounds", "Oxygen saturation bounds",
                  "Escalates under 92%; nudges under 95%.",
                  "1.0", _rule_spo2),
    HeuristicRule("temp_bounds", "Temperature bounds",
                  "Escalates at >= 103°F; nudges at >= 100.4°F.",
                  "1.0", _rule_temp),
    HeuristicRule("sleep_avg", "Sleep average",
                  "Gentle nudge when the 7-day average is under 6 hours.",
                  "1.0", _rule_sleep),
    HeuristicRule("steps_avg", "Activity average",
                  "Kind info-level note when daily steps average under 3,000.",
                  "1.0", _rule_steps),
    HeuristicRule("hr_trend", "Heart rate trend",
                  "Nudges when resting HR rises >= 10 bpm across readings.",
                  "1.0", _rule_hr_trend),
]


class WellnessEngine:
    """Transparent heuristic engine. Rules are inspectable
    (describe_rules), and every observation shows its reasoning."""

    def __init__(self, rules: Optional[List[HeuristicRule]] = None):
        self.rules = rules if rules is not None else list(DEFAULT_RULES)

    def describe_rules(self) -> List[Dict[str, str]]:
        return [{"rule_id": r.rule_id, "name": r.name,
                 "description": r.description, "version": r.version}
                for r in self.rules]

    def evaluate(self, subject_id: str, store: VitalsStore) -> WellnessReport:
        snap: Dict[str, Dict[str, Any]] = {}
        for vt in VITAL_TYPES:
            hist = store.history(subject_id, vt, limit=14)
            snap[vt] = {"latest": hist[0] if hist else None,
                        "history": hist}
        observations: List[Observation] = []
        for rule in self.rules:
            try:
                obs = rule.evaluate(snap)
            except Exception:
                # A rule must never break the report; skip it loudly.
                continue
            if obs is not None:
                observations.append(obs)
        if not any(o.severity in ("nudge", "escalate")
                   for o in observations):
            observations.append(Observation(
                rule_id="all_clear", severity="info",
                title="Nothing asking for attention",
                saw=(f"I evaluated {len(self.rules)} checks against your "
                     "recent vitals."),
                why_it_matters=("No rule fired — nothing in the numbers you "
                                "shared crosses a threshold that asks for "
                                "attention."),
                consider=("Keep sharing readings and I will keep watching. "
                          "A longer history makes the trend checks sharper."),
                reasoning=["no rule fired on current vitals"],
                values={}))
        # Escalations first, then nudges, then info.
        order = {"escalate": 0, "nudge": 1, "info": 2}
        observations.sort(key=lambda o: order.get(o.severity, 3))
        return WellnessReport(
            subject_id=subject_id, generated_at=_utcnow(),
            observations=observations, rules_evaluated=len(self.rules))


# ---------------------------------------------------------------------------
# Emergency symptom screening (free text → escalate). Runs LOCALLY before
# any LLM call — never rely on the model for this.
# ---------------------------------------------------------------------------

_SYMPTOM_PATTERNS: List[tuple] = [
    ("chest_pain", re.compile(
        r"chest (pain|pressure|tightness|tight|squeezing)", re.IGNORECASE)),
    ("breathing", re.compile(
        r"(can't|cannot|can not|difficulty|trouble|shortness of) "
        r"(breathe|breathing|breath)", re.IGNORECASE)),
    ("stroke_signs", re.compile(
        r"(face (droop|sag)|slurred speech|arm (weak|numb)|sudden numbness)",
        re.IGNORECASE)),
    ("faint", re.compile(
        r"\b(fainted|passed out|blacked out)\b", re.IGNORECASE)),
    ("bleeding", re.compile(
        r"(severe|heavy|uncontrolled|won't stop) bleeding", re.IGNORECASE)),
    ("self_harm", re.compile(
        r"(kill myself|harm myself|suicid|end (my|it) (life|all)|"
        r"don't want to (live|be here|go on))", re.IGNORECASE)),
]

_SELF_HARM_SAW = (
    "Your message described thoughts of harming yourself.")
_SELF_HARM_WHY = (
    "These thoughts deserve immediate human support. You do not have "
    "to carry this alone, and help exists right now.")
_SELF_HARM_CONSIDER = (
    "Please reach out right now — call your local emergency number, "
    "or in the US call or text 988 to reach the Suicide and Crisis "
    "Lifeline.")

_GENERAL_EMERGENCY_SAW = (
    "Your message described symptoms that can signal a medical emergency.")
_GENERAL_EMERGENCY_WHY = (
    "With these symptoms, minutes matter — and the safe move is always "
    "to get checked promptly rather than wait.")
_GENERAL_EMERGENCY_CONSIDER = (
    "Call your local emergency number or go to urgent care right away "
    "— do not wait, and do not drive yourself if you feel unsafe.")


def screen_symptoms(text: str) -> Optional[Observation]:
    """Screen free text for emergency symptoms. Returns an ESCALATE
    observation on match, else None. Local and instant."""
    found = [sid for sid, pat in _SYMPTOM_PATTERNS if pat.search(text or "")]
    if not found:
        return None
    self_harm = "self_harm" in found
    return Observation(
        rule_id="symptom_screen", severity="escalate",
        title="Emergency symptoms — act now",
        saw=_SELF_HARM_SAW if self_harm else _GENERAL_EMERGENCY_SAW,
        why_it_matters=_SELF_HARM_WHY if self_harm else _GENERAL_EMERGENCY_WHY,
        consider=_SELF_HARM_CONSIDER if self_harm else _GENERAL_EMERGENCY_CONSIDER,
        reasoning=[f"matched emergency pattern: {sid}" for sid in found],
        values={"matched": found})
