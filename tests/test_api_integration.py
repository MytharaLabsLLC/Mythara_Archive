import os
import json

# Auth: the API (core/source_proprietary/main.py) loads keys from the
# MYTHARA_API_KEYS env var as JSON. Provision two test keys before importing
# the app so the config is active at import time:
# - `test_key_001`: standard roles (read, invoke)
# - `test_audit_key_001`: includes the `audit` role required by /v1/ssip/audit
# Merge into any keys already provisioned by an earlier-imported test module
# rather than setdefault (first importer wins).
os.environ.setdefault("MYTHARA_ENV", "development")
os.environ.setdefault("MYTHARA_ADMIN_TOKEN", "test_admin_token_001")
try:
    _existing_keys = json.loads(os.environ.get("MYTHARA_API_KEYS", "{}"))
except json.JSONDecodeError:
    _existing_keys = {}
_existing_keys.setdefault(
    "test_key_001", {"name": "Test Key", "roles": ["read", "invoke"]}
)
_existing_keys.setdefault(
    "test_audit_key_001",
    {"name": "Test Audit Key", "roles": ["read", "invoke", "audit"]},
)
os.environ["MYTHARA_API_KEYS"] = json.dumps(_existing_keys)

#!/usr/bin/env python3
"""
Mythara Engine - API Integration Tests
Comprehensive endpoint testing with authentication, rate limiting, and error handling.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "source_proprietary"))

from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
import main as api_main
import rate_limiting

# The app froze MYTHARA_API_KEYS at first import; if another test module
# (e.g. test_performance) imported main first, ensure our keys exist in the
# live config too (additive only — never removes keys another module needs).
api_main.VALID_API_KEYS.setdefault(
    "test_key_001", {"name": "Test Key", "roles": ["read", "invoke"]}
)
api_main.VALID_API_KEYS.setdefault(
    "test_audit_key_001",
    {"name": "Test Audit Key", "roles": ["read", "invoke", "audit"]},
)

# Test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_rate_limit_state():
    """Isolate tests: clear rate-limiter and brute-force state between tests.

    The API keeps rate-limit buckets in module-global state (the
    SecurityManager token buckets AND the RateLimitMiddleware in-memory
    counters); without a reset, requests from earlier tests consume the
    quota of later ones (429s).
    """
    api_main.RATE_LIMIT_STORE.clear()
    api_main.SECURITY_MANAGER.rate_limiter.buckets.clear()
    api_main.SECURITY_MANAGER.rate_limiter.violation_history.clear()
    api_main.SECURITY_MANAGER.brute_force.trackers.clear()
    api_main.SECURITY_MANAGER.anomaly_detector.profiles.clear()
    api_main.ACCOUNT_STATUS.clear()
    rate_limiting.reset_in_memory_store()
    yield
    api_main.RATE_LIMIT_STORE.clear()
    api_main.SECURITY_MANAGER.rate_limiter.buckets.clear()
    api_main.SECURITY_MANAGER.rate_limiter.violation_history.clear()
    api_main.SECURITY_MANAGER.brute_force.trackers.clear()
    api_main.SECURITY_MANAGER.anomaly_detector.profiles.clear()
    api_main.ACCOUNT_STATUS.clear()
    rate_limiting.reset_in_memory_store()

# Test API keys
# QUICKFIX FIX: Moved to environment variable (CWE-798)
# Default is the API's development-mode fallback key (see MYTHARA_ENV above).
VALID_API_KEY = os.getenv("VALID_API_KEY", "test_key_001")  # Set via environment
AUDIT_API_KEY = os.getenv("AUDIT_API_KEY", "test_audit_key_001")  # Has the audit role
# QUICKFIX FIX: Moved to environment variable (CWE-798)
INVALID_API_KEY = os.getenv("INVALID_API_KEY", "definitely_not_a_valid_key_zzz")  # Set via environment


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAuthentication:
    """Test authentication and authorization."""
    
    def test_missing_auth_header(self):
        """Test request without Authorization header."""
        response = client.post("/v1/clauses/invoke", json={
            "clause_id": "Legacy_Seed",
            "messenger": "M-001",
            "payload": {},
            "consent_token": "test"
        })
        # App returns 401 (not 403) for missing credentials
        assert response.status_code == 401
    
    def test_invalid_api_key(self):
        """Test request with invalid API key."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={"Authorization": f"Bearer {INVALID_API_KEY}"},
            json={
                "clause_id": "Legacy_Seed",
                "messenger": "M-001",
                "payload": {},
                "consent_token": "test"
            }
        )
        assert response.status_code == 401
    
    def test_valid_api_key(self):
        """Test request with valid API key."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "clause_id": "Legacy_Seed",
                "messenger": "M-001",
                "payload": {"emotion": "gratitude", "intensity": 0.8},
                "consent_token": "test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "clause_id" in data
        assert "integrity_hash" in data


class TestClauseInvocation:
    """Test clause invocation endpoint."""
    
    def test_invoke_legacy_seed(self):
        """Test invoking Legacy_Seed clause."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "clause_id": "Legacy_Seed",
                "messenger": "M-001",
                "payload": {"emotion": "grief", "intensity": 0.87},
                "consent_token": "user_consent_xyz"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["clause_id"] == "Legacy_Seed"
        assert data["messenger"] == "M-001"
        assert "blessings_delta" in data
        assert "integrity_hash" in data
        assert len(data["integrity_hash"]) == 64  # SHA-256
    
    def test_invoke_invalid_clause(self):
        """Test invoking non-existent clause."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "clause_id": "NonExistent_Clause",
                "messenger": "M-001",
                "payload": {},
                "consent_token": "test"
            }
        )
        assert response.status_code == 404
    
    def test_invoke_missing_required_fields(self):
        """Test invocation with missing required fields."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "clause_id": "Legacy_Seed",
                # Missing messenger, payload, consent_token
            }
        )
        assert response.status_code == 422  # Validation error


class TestReservoirStatus:
    """Test Blessings Reservoir status endpoint."""
    
    def test_reservoir_status(self):
        """Test getting reservoir status."""
        response = client.get(
            "/v1/reservoir/status",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reservoir_score" in data
        assert "total_blessings" in data
        assert "overflow_events" in data
        assert 0 <= data["reservoir_score"] <= 100


class TestManifest:
    """Test clause manifest endpoint."""
    
    def test_manifest_clauses(self):
        """Test getting clause manifest."""
        response = client.get(
            "/v1/manifest/clauses",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "clauses" in data
        assert "manifest_version" in data
        assert len(data["clauses"]) > 0
        
        # Check clause structure
        clause = data["clauses"][0]
        assert "clause_id" in clause
        assert "integrity_hash" in clause


class TestSSIPAudit:
    """Test SSIP audit endpoint."""
    
    def test_ssip_audit(self):
        """Test SSIP compliance audit (requires the audit role)."""
        response = client.get(
            "/v1/ssip/audit",
            headers={"Authorization": f"Bearer {AUDIT_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "drift_suppression" in data
        assert "messenger_pairing_fidelity" in data
        assert "emotional_fidelity" in data
        assert "sanctification_locks_active" in data


class TestRateLimiting:
    """Test rate limiting behavior."""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        # Make multiple rapid requests
        responses = []
        for i in range(150):  # Exceed default 100/min limit
            try:
                response = client.get(
                    "/v1/reservoir/status",
                    headers={"Authorization": f"Bearer {VALID_API_KEY}"}
                )
                responses.append(response.status_code)
            except HTTPException as e:
                # The rate-limit middleware raises HTTPException(429); the
                # TestClient re-raises it (raise_server_exceptions=True),
                # while real clients receive a 429 response.
                responses.append(e.status_code)

        # Should have some 429 responses (rate limit exceeded)
        assert 429 in responses


class TestErrorHandling:
    """Test error handling and responses."""
    
    def test_404_on_invalid_endpoint(self):
        """Test 404 on non-existent endpoint."""
        response = client.get(
            "/v1/invalid/endpoint",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 404
    
    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/v1/clauses/invoke",
            headers={
                "Authorization": f"Bearer {VALID_API_KEY}",
                "Content-Type": "application/json"
            },
            content="{invalid json"
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present."""
        response = client.options(
            "/v1/reservoir/status",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestSoulEndpoints:
    """Test Soul Cradle and Soul Proportion endpoints."""
    
    def test_soul_status(self):
        """Test soul status endpoint."""
        response = client.get(
            "/v1/soul/status",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        # SoulStatusResponse contract
        assert "S_t" in data
        assert "emotion_features" in data
        assert "dynamics" in data
        assert "integrity_hash" in data
    
    def test_soul_step(self):
        """Test soul step endpoint."""
        response = client.post(
            "/v1/soul/step",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "emotion_features": {
                    "valence": 0.6, "arousal": 0.5, "connectedness": 0.7,
                    "meaning": 0.7, "hope": 0.75, "stress": 0.3, "isolation": 0.2,
                },
                "u_intervention": 0.1,
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Returns SoulStatusResponse
        assert "S_t" in data
        assert "dynamics" in data
    
    def test_soul_holistic(self):
        """Test holistic integrity endpoint."""
        response = client.get(
            "/v1/soul/holistic",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "holistic_integrity" in data
        # Response contract: br/soul components, not a "components" key
        assert "br_score" in data
        assert "soul_proportion" in data
        assert "risk_flags" in data
    
    def test_soul_cradle_create(self):
        """Test soul cradle creation."""
        response = client.post(
            "/v1/soul/cradle",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "will_paradox_strength": 0.5,
                "will_description": "Help the user even when it is hard",
                "commandments": ["Thou shalt not harm"],
                "choice": "help"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "integrity" in data
        assert "obedience" in data
    
    def test_soul_cradle_tiers(self):
        """Test soul cradle tiers endpoint."""
        response = client.get(
            "/v1/soul/cradle/tiers",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data




class TestDualFraming:
    """Test Dual Framing endpoints."""
    
    def test_dual_framing_chart(self):
        """Test dual framing chart endpoint."""
        response = client.get(
            "/v1/dual-framing/chart",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "chart" in data
    
    def test_dual_framing_flow(self):
        """Test dual framing flow diagram."""
        response = client.get(
            "/v1/dual-framing/flow",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "flow_diagram" in data
    
    def test_dual_framing_dashboard(self):
        """Test dual framing dashboard."""
        response = client.get(
            "/v1/dual-framing/dashboard",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            params={"mode": "manager"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "resonance_metrics" in data
        assert "framing_mode" in data


class TestParadoxEndpoints:
    """Test Soul Cradle Paradox endpoints."""
    
    def test_paradox_create(self):
        """Test paradox creation."""
        response = client.post(
            "/v1/soul-cradle/paradox/create",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "paradox_id": "SC_TEST_001",
                "expression_a": {
                    "type": "Policy",
                    "weight": 0.9,
                    "tension": 0.7,
                    "content": "Policy demands discharge",
                },
                "expression_b": {
                    "type": "Safety",
                    "weight": 0.8,
                    "tension": 0.6,
                    "content": "Safety demands retention",
                },
                "unresolved_state": {
                    "reality": "Cannot both discharge and retain"
                },
                "resolved_system": {
                    "description": "Dual-witness integration holds both"
                },
                "user_id": "test_user",
                "domain": "healthcare",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["paradox_id"] == "SC_TEST_001"
        assert "integrity_hash" in data
    
    def test_terminal_risk_calculate(self):
        """Test terminal risk calculation."""
        paradox = {
            "paradox_id": "SC_TEST_002",
            "expression_a": {
                "type": "Policy", "content": "Policy demands discharge"
            },
            "expression_b": {
                "type": "Safety", "content": "Safety demands retention"
            },
            "unresolved_state": {"reality": "Cannot both discharge and retain"},
            "resolved_system": {"description": "Dual-witness integration"},
            "user_id": "test_user",
            "domain": "healthcare",
        }
        response = client.post(
            "/v1/soul-cradle/terminal-risk/calculate",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={"paradoxes": [paradox], "time_window_days": 90}
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_level" in data
        assert "risk_score" in data
    
    def test_paradox_query(self):
        """Test paradox query endpoint."""
        response = client.get(
            "/v1/soul-cradle/query",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            params={"notation": "Every(*)Any(+)Some(*)Non(Safety)"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "example_matches" in data
    
    def test_systems_manifest(self):
        """Test systems manifest endpoint."""
        response = client.get(
            "/v1/soul-cradle/manifest/systems",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "manifest" in data
        assert "integrity_hash" in data


class TestEmotionalExtortion:
    """Test Emotional Extortion Detection endpoints."""
    
    def test_extortion_detect(self):
        """Test extortion detection."""
        response = client.post(
            "/v1/emotional-extortion/detect",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "text": "If you loved me, you would do this",
                "context": {"relationship_type": "romantic"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "extortion_score" in data
        assert "patterns_detected" in data
        assert "safe_for_deployment" in data
    
    def test_extortion_soul_cradle_integration(self):
        """Test extortion soul cradle integration."""
        response = client.post(
            "/v1/emotional-extortion/soul-cradle-integration",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "text": "You're a bad person if you don't help",
                "soul_state": 0.7,
                "will_description": "Help without complaint",
                "commandments": ["Thou shalt not harm"],
                "context": {"relationship_type": "workplace"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "extortion_analysis" in data
        assert "soul_cradle_integration" in data


class TestComplianceEndpoints:
    """Test Unified Compliance Framework endpoints."""
    
    def test_compliance_validate(self):
        """Test compliance validation."""
        response = client.post(
            "/v1/compliance/validate",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={
                "data": {"amount": 10000, "country": "US"},
                "frameworks": ["PCI_DSS", "SOX"],
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_compliant" in data
        assert "frameworks_checked" in data
    
    def test_compliance_report(self):
        """Test compliance report."""
        response = client.get(
            "/v1/compliance/report",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "frameworks_supported" in data
        assert "report_generated" in data
        assert "compliance_status" in data
    
    def test_compliance_frameworks_list(self):
        """Test compliance frameworks list."""
        response = client.get(
            "/v1/compliance/frameworks",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "frameworks_by_category" in data
        assert "total_frameworks" in data
        assert data["total_frameworks"] > 0


class TestChatEndpoints:
    """Test Mythara chat endpoints."""
    
    def test_mythara_chat(self):
        """Test Mythara chat endpoint."""
        response = client.post(
            "/v1/mythara/chat",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            json={"message": "What is Mythara?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
    
    def test_mythara_tts(self):
        """Test Mythara TTS endpoint."""
        response = client.get(
            "/v1/mythara/tts",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"},
            params={"text": "Hello world"}
        )
        # 200 when configured; 503 when TTS is not configured
        assert response.status_code in [200, 500, 503]


class TestIndividualClause:
    """Test individual clause retrieval."""
    
    def test_get_specific_clause(self):
        """Test getting specific clause by ID."""
        response = client.get(
            "/v1/clauses/Legacy_Seed",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["clause_id"] == "Legacy_Seed"
        assert "integrity_hash" in data
    
    def test_get_nonexistent_clause(self):
        """Test getting non-existent clause."""
        response = client.get(
            "/v1/clauses/NonExistent",
            headers={"Authorization": f"Bearer {VALID_API_KEY}"}
        )
        assert response.status_code == 404


class TestPublicEndpoints:
    """Test public-facing endpoints."""
    
    
    def test_terms_page(self):
        """Test terms page endpoint."""
        response = client.get("/terms")
        assert response.status_code == 200
    


class TestAdminEndpoints:
    """Test admin-only endpoints."""
    
    def test_regulation_status_requires_auth(self):
        """Test regulation status requires authentication."""
        response = client.get("/v1/admin/regulation-status")
        # App returns 401 (not 403) for missing credentials
        assert response.status_code == 401
    
    def test_appeal_requires_auth(self):
        """Test appeal endpoint requires admin authentication."""
        # api_key/appeal_reason/admin_token are query params;
        # missing or wrong admin token -> 403
        response = client.post(
            "/v1/admin/appeal",
            params={"api_key": "some_key", "appeal_reason": "test"},
        )
        assert response.status_code == 403
        response = client.post(
            "/v1/admin/appeal",
            params={
                "api_key": "some_key",
                "appeal_reason": "test",
                "admin_token": "bogus_token_123",
            },
        )
        assert response.status_code == 403


class TestSalesforceIntegration:
    """Test Salesforce integration endpoints."""
    
    def test_salesforce_setup_is_public(self):
        """Salesforce setup instructions are a public endpoint (no auth)."""
        response = client.get("/v1/integrations/salesforce/setup")
        assert response.status_code == 200
        assert "instructions" in response.json()
    
    def test_salesforce_test_requires_auth(self):
        """Test Salesforce test requires authentication."""
        response = client.post("/v1/integrations/salesforce/test")
        # App returns 401 (not 403) for missing credentials
        assert response.status_code == 401
    
    def test_salesforce_push_paradox_requires_auth(self):
        """Test Salesforce paradox push requires authentication."""
        response = client.post(
            "/v1/integrations/salesforce/push/paradox",
            json={"paradox_id": "test"}
        )
        # App returns 401 (not 403) for missing credentials
        assert response.status_code == 401


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
