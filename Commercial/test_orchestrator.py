# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Test Mythara Orchestrator API (live integration tests).

These tests exercise a RUNNING orchestrator server at API_URL
(Commercial/mythara_orchestrator.py served on port 5000). They are skipped
automatically when no server is reachable, so the unit-test suite stays
green without a live deployment.
"""

import os

import pytest
import requests

API_URL = os.environ.get("ORCHESTRATOR_API_URL", "http://localhost:5000")
# Must match mythara_orchestrator.VP_MASTER_TOKEN on the running server.
VP_TOKEN = os.environ.get("VP_MASTER_TOKEN", "mythara_vp_master_sanctified_2025")


def _server_reachable() -> bool:
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


requires_server = pytest.mark.skipif(
    not _server_reachable(),
    reason=f"Orchestrator server not reachable at {API_URL}",
)


@requires_server
def test_health():
    """Test health endpoint."""
    response = requests.get(f"{API_URL}/health", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["service"] == "Mythara Orchestrator"


@pytest.fixture(scope="module")
def bot_token():
    """Register a bot against the live server and yield its token."""
    response = requests.post(
        f"{API_URL}/register_bot",
        json={
            "vp_token": VP_TOKEN,
            "bot_id": "sales_bot",
            "bot_name": "Autonomous Sales Bot",
        },
        timeout=10,
    )
    assert response.status_code == 200, response.text
    token = response.json().get("bot_token")
    assert token, "registration did not return a bot_token"
    return token


@requires_server
def test_register_bot(bot_token):
    """Test bot registration (via the bot_token fixture)."""
    assert isinstance(bot_token, str) and len(bot_token) > 0


@requires_server
def test_request_approval(bot_token):
    """Test approval request."""
    response = requests.post(
        f"{API_URL}/request_approval",
        json={
            "bot_id": "sales_bot",
            "token": bot_token,
            "action": "send_email",
            "reason": "cold_outreach",
            "count": 10,
        },
        timeout=10,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    # count=10 is under the 100/day spam cap, so this should be approved
    assert data["approved"] is True
    assert "integrity_hash" in data


@requires_server
def test_dashboard():
    """Test dashboard."""
    response = requests.get(f"{API_URL}/dashboard", timeout=10)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["orchestrator_status"] == "operational"
    assert "bots" in data
    assert "recent_decisions" in data
