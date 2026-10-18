# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""Quick test of Soul Status API endpoint"""

import sys
sys.path.insert(0, 'core/source_proprietary')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test soul status endpoint (mythic framing)
response = client.get(
    "/v1/soul/status",
    headers={"Authorization": "Bearer dev_test_key_001"}
)

print("=== SOUL STATUS (MYTHIC FRAMING) ===")
print(f"Status Code: {response.status_code}")
print(response.json())

# Test with industry framing
response2 = client.get(
    "/v1/soul/status?frame=industry",
    headers={"Authorization": "Bearer dev_test_key_001"}
)

print("\n=== SOUL STATUS (INDUSTRY FRAMING) ===")
print(f"Status Code: {response2.status_code}")
print(response2.json())
