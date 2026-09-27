# Copyright © 2026 Herbert Velez Jr. All rights reserved.
"""Clause-level learning for outreach variants.

Same pattern as mythara_autonomous_sales.select_clause(): epsilon-greedy
over message variants. Each send is an arm pull; engagement is the reward.

Rewards (honest, observable only):
  reply (any)      +1.0   — they engaged
  interested       +3.0   — hot reply, routed to Herb
  question         +1.5   — engaged with substance
  unsubscribe      -2.0   — we mis-targeted or mis-toned
  complaint/bounce -3.0   — reputation damage, learn fast
  no reply          0.0   — neutral; silence is data, not failure

Stats persist in state/variant_stats.json so learning survives restarts.
"""

import json
import random
from pathlib import Path
from typing import Dict, List

from . import config
from .voice import VARIANTS

REWARDS = {
    "reply": 1.0,
    "interested": 3.0,
    "question": 1.5,
    "not_interested": 0.0,
    "unsubscribe": -2.0,
    "bounced": -1.0,
    "complaint": -3.0,
    "no_reply": 0.0,
}


def _blank() -> Dict[str, Dict[str, float]]:
    return {v: {"pulls": 0, "reward": 0.0} for v in VARIANTS}


def load_stats(path: Path | None = None) -> Dict[str, Dict[str, float]]:
    p = path or config.VARIANT_STATS_FILE
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            base = _blank()
            for v in VARIANTS:
                if v in data:
                    base[v] = {
                        "pulls": float(data[v].get("pulls", 0)),
                        "reward": float(data[v].get("reward", 0.0)),
                    }
            return base
        except (OSError, ValueError):
            pass
    return _blank()


def save_stats(stats: Dict[str, Dict[str, float]], path: Path | None = None) -> None:
    p = path or config.VARIANT_STATS_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def select_variant(
    explore_rate: float | None = None,
    path: Path | None = None,
    rng: random.Random | None = None,
) -> str:
    """Epsilon-greedy: explore with probability explore_rate, else play the
    champion (highest mean reward; ties/unplayed -> first variant)."""
    explore_rate = config.EXPLORE_RATE if explore_rate is None else explore_rate
    rng = rng or random
    stats = load_stats(path)
    if rng.random() < explore_rate:
        return rng.choice(list(VARIANTS))
    def mean(v: str) -> float:
        s = stats[v]
        return s["reward"] / s["pulls"] if s["pulls"] else 0.0
    return max(VARIANTS, key=lambda v: (mean(v), -list(VARIANTS).index(v)))


def record_outcome(
    variant: str, outcome: str, path: Path | None = None
) -> Dict[str, Dict[str, float]]:
    """Attribute one observed outcome back to the variant that earned it."""
    if outcome not in REWARDS:
        raise ValueError(f"unknown outcome {outcome!r}")
    stats = load_stats(path)
    stats[variant]["pulls"] += 1
    stats[variant]["reward"] += REWARDS[outcome]
    save_stats(stats, path)
    return stats


def champion(path: Path | None = None) -> str:
    """Current best variant by mean reward (for reporting)."""
    stats = load_stats(path)
    def mean(v: str) -> float:
        s = stats[v]
        return s["reward"] / s["pulls"] if s["pulls"] else 0.0
    return max(VARIANTS, key=lambda v: (mean(v), -list(VARIANTS).index(v)))
