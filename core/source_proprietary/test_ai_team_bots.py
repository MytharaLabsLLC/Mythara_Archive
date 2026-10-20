#!/usr/bin/env python3
"""Tests for the AI-team bot suite (core/source_proprietary).

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Added 2026-10-19: the suite shipped with zero bot coverage (the only
test file, test_compliance.py, covers the compliance framework).
These tests are offline and deterministic: module import health, bot
instantiation on throwaway databases, and one pure behavior per bot
where the bot exposes one.
"""

import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SUITE_MODULES = [
    "crm_integration",
    "database",
    "dual_framing",
    "email_service",
    "legal_resources_index",
    "main",
    "monitoring",
    "mythara_accounting_vp",
    "mythara_global_governance",
    "mythara_grant_writer_bot",
    "mythara_researcher_bot",
    "mythara_sbga_bot",
    "mythara_sigma_six_blackbelt",
    "mythara_system_optimizer",
    "paradox_topology_engine",
    "public_contact_harvester",
    "rate_limiting",
    "redis_cache",
    "redis_rate_limiter",
    "robustness_framework",
    "salesforce_integration",
    "security_audit_compliance",
    "security_hardening",
    "soul_cradle_operator",
    "soul_cradle_systems_framework",
    "soul_engine_dashboard",
    "soul_proportion_model",
    "structured_logger",
    "submit_cloud_credits",
    "torts_law_framework",
    "unified_compliance_framework",
    "universal_governance_lattice",
    "websocket_manager",
    "will_integrity_guardian",
    "Risk_Override_Authority",
]


@pytest.mark.parametrize("module", SUITE_MODULES)
def test_suite_module_imports(module):
    importlib.import_module(module)


def test_grant_writer_instantiates_and_dedupes(tmp_path):
    from mythara_grant_writer_bot import MytharaGrantWriterBot

    bot = MytharaGrantWriterBot(db_path=str(tmp_path / "g.db"))
    grants = [
        {"number": "A1", "grantor": "DOE", "name": "Solar"},
        {"number": "A1", "grantor": "DOE", "name": "Solar (dup)"},
        {"number": "B2", "grantor": "NSF", "name": "AI Safety"},
    ]
    unique = bot._dedupe_grants(grants)
    assert len(unique) == 2
    # _fit_score's documented contract: base 60, +5 per keyword hit, cap 95.
    assert bot._fit_score("solar energy grant", ["solar", "energy"]) == 70
    assert bot._fit_score("unrelated text", ["solar"]) == 60


def test_researcher_instantiates_without_orchestrator(tmp_path):
    # Orchestrator is not running during tests: the bot must degrade
    # gracefully (warn and continue), never crash at construction.
    from mythara_researcher_bot import MytharaResearcherBot

    bot = MytharaResearcherBot(db_path=str(tmp_path / "r.db"))
    assert bot is not None


def test_accounting_vp_double_entry_rules(tmp_path):
    from mythara_accounting_vp import MytharaAccountingVP

    vp = MytharaAccountingVP(db_path=str(tmp_path / "a.db"))
    with pytest.raises(ValueError):
        vp.record_journal_entry(
            "2026-10-19", [("1000", 50.0)], [("2100", 49.0)], "unbalanced"
        )
    result = vp.record_journal_entry(
        "2026-10-19", [("1000", 100.0)], [("2100", 100.0)], "balanced test entry"
    )
    assert result is not None
    sheet = vp.generate_balance_sheet("2026-10-19")
    assert sheet is not None


def test_sbga_instantiates(tmp_path):
    from mythara_sbga_bot import MytharaSBGABot

    bot = MytharaSBGABot(db_path=str(tmp_path / "s.db"))
    assert bot is not None


def test_sigma_six_dpmo_math(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the blackbelt keeps its db in cwd
    from mythara_sigma_six_blackbelt import MytharaSigmaSixBlackbelt, sigma_from_dpmo

    assert sigma_from_dpmo(3.4) > 5.9  # ~6 sigma at 3.4 DPMO
    assert sigma_from_dpmo(233) > sigma_from_dpmo(6210) > sigma_from_dpmo(66807)
    assert MytharaSigmaSixBlackbelt() is not None
