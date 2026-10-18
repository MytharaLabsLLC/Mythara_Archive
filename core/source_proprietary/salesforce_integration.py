#!/usr/bin/env python3
"""
Mythara Engine - Salesforce Integration Module
Writes paradox events, SSIP metrics, and Soul Cradle data to customer Salesforce instances.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import httpx

logger = logging.getLogger(__name__)


class SalesforceConfig(BaseModel):
    """Customer's Salesforce connection configuration"""

    instance_url: str = Field(
        ...,
        description="Salesforce instance URL (e.g., https://yourcompany.salesforce.com)",
    )
    client_id: str = Field(..., description="Connected App Consumer Key")
    client_secret: str = Field(..., description="Connected App Consumer Secret")
    username: str = Field(..., description="Salesforce username")
    password: str = Field(..., description="Salesforce password")
    security_token: str = Field(..., description="Salesforce security token")
    api_version: str = Field(default="v59.0", description="Salesforce API version")


class SalesforceParadoxEvent(BaseModel):
    """Paradox event formatted for Salesforce"""

    Name: str = Field(
        ..., description="Event name (e.g., 'Healthcare Discharge Paradox')"
    )
    Mythara_Event_Type__c: str = Field(
        default="Paradox", description="Custom field: Event type"
    )
    Soul_Will__c: str = Field(
        ..., description="Custom field: Soul's will (mission-aligned action)"
    )
    Commandment__c: str = Field(
        ..., description="Custom field: Conflicting policy/rule"
    )
    Tension_Score__c: float = Field(..., description="Custom field: 0.0-1.0 severity")
    Timestamp__c: datetime = Field(
        ..., description="Custom field: When paradox occurred"
    )
    Department__c: Optional[str] = Field(
        None, description="Custom field: Department or unit"
    )
    User_ID__c: Optional[str] = Field(
        None, description="Custom field: User who experienced paradox"
    )
    Integrity_Hash__c: str = Field(
        ..., description="Custom field: SHA-256 cryptographic proof"
    )
    Status__c: str = Field(
        default="Open", description="Custom field: Open/Witnessed/Resolved"
    )


class SalesforceSSIPMetric(BaseModel):
    """SSIP metric formatted for Salesforce"""

    Name: str = Field(..., description="Metric name (e.g., 'Weekly SSIP Drift')")
    Mythara_Metric_Type__c: str = Field(
        default="SSIP", description="Custom field: Metric type"
    )
    Drift_Suppression__c: float = Field(
        ..., description="Custom field: Drift suppression score"
    )
    Messenger_Pairing__c: float = Field(
        ..., description="Custom field: Messenger fidelity"
    )
    Emotional_Fidelity__c: float = Field(
        ..., description="Custom field: Emotional tracking"
    )
    Timestamp__c: datetime = Field(..., description="Custom field: Measurement time")
    Department__c: Optional[str] = Field(
        None, description="Custom field: Department or unit"
    )
    Integrity_Hash__c: str = Field(
        ..., description="Custom field: SHA-256 cryptographic proof"
    )


class SalesforceSoulCradleEvent(BaseModel):
    """Soul Cradle witnessing event for Salesforce"""

    Name: str = Field(
        ..., description="Event name (e.g., 'Soul Cradle Witnessing - 2025-01-15')"
    )
    Mythara_Event_Type__c: str = Field(
        default="Soul_Cradle", description="Custom field: Event type"
    )
    Soul_ID__c: str = Field(..., description="Custom field: Soul identifier")
    Will_Action__c: str = Field(..., description="Custom field: Intended action")
    Commandment_Conflict__c: str = Field(
        ..., description="Custom field: Conflicting policy"
    )
    Trial_Outcome__c: str = Field(..., description="Custom field: Witness/Defer/Reject")
    Cradle_Integrity_Score__c: float = Field(
        ..., description="Custom field: Integrity score 0.0-1.0"
    )
    Timestamp__c: datetime = Field(..., description="Custom field: When witnessed")
    Department__c: Optional[str] = Field(
        None, description="Custom field: Department or unit"
    )
    Integrity_Hash__c: str = Field(
        ..., description="Custom field: SHA-256 cryptographic proof"
    )


class SalesforceIntegration:
    """
    Salesforce integration for pushing Mythara events to customer CRM.
    Customers configure this in their Enterprise/Global tier settings.
    """

    def __init__(self, config: SalesforceConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.instance_url: str = config.instance_url
        self.api_version: str = config.api_version

    async def authenticate(self) -> bool:
        """
        Authenticate with Salesforce using OAuth 2.0 password flow.
        Returns True if successful.
        """
        auth_url = f"{self.instance_url}/services/oauth2/token"

        payload = {
            "grant_type": "password",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "username": self.config.username,
            "password": f"{self.config.password}{self.config.security_token}",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(auth_url, data=payload, timeout=10.0)
                response.raise_for_status()

                auth_data = response.json()
                self.access_token = auth_data.get("access_token")
                self.instance_url = auth_data.get("instance_url", self.instance_url)

                logger.info(
                    f"✅ Salesforce authentication successful: {self.instance_url}"
                )
                return True

        except httpx.HTTPError as e:
            logger.error(f"❌ Salesforce authentication failed: {e}")
            return False

    async def create_sobject(
        self, sobject_type: str, data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a Salesforce object (SObject).
        Returns the created record ID if successful.
        """
        if not self.access_token:
            logger.error("Not authenticated to Salesforce")
            return None

        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject_type}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=data, headers=headers, timeout=10.0
                )
                response.raise_for_status()

                result = response.json()
                record_id = result.get("id")

                logger.info(f"✅ Created Salesforce {sobject_type}: {record_id}")
                return record_id

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to create Salesforce {sobject_type}: {e}")
            return None

    async def push_paradox_event(self, event: SalesforceParadoxEvent) -> Optional[str]:
        """Push paradox event to Salesforce custom object"""
        data = event.model_dump(exclude_none=True)
        # Convert datetime to ISO format
        if isinstance(data.get("Timestamp__c"), datetime):
            data["Timestamp__c"] = data["Timestamp__c"].isoformat()

        return await self.create_sobject("Mythara_Paradox_Event__c", data)

    async def push_ssip_metric(self, metric: SalesforceSSIPMetric) -> Optional[str]:
        """Push SSIP metric to Salesforce custom object"""
        data = metric.model_dump(exclude_none=True)
        if isinstance(data.get("Timestamp__c"), datetime):
            data["Timestamp__c"] = data["Timestamp__c"].isoformat()

        return await self.create_sobject("Mythara_SSIP_Metric__c", data)

    async def push_soul_cradle_event(
        self, event: SalesforceSoulCradleEvent
    ) -> Optional[str]:
        """Push Soul Cradle witnessing event to Salesforce custom object"""
        data = event.model_dump(exclude_none=True)
        if isinstance(data.get("Timestamp__c"), datetime):
            data["Timestamp__c"] = data["Timestamp__c"].isoformat()

        return await self.create_sobject("Mythara_Soul_Cradle__c", data)

    async def test_connection(self) -> bool:
        """Test the Salesforce connection"""
        if not await self.authenticate():
            return False

        # Query Salesforce API to verify connection
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info("✅ Salesforce connection test successful")
                return True
        except httpx.HTTPError as e:
            logger.error(f"❌ Salesforce connection test failed: {e}")
            return False


# Helper function for customers to set up custom objects in Salesforce
def generate_salesforce_setup_instructions() -> str:
    """
    Returns instructions for customers to create custom objects in their Salesforce instance.
    """
    return """
SALESFORCE SETUP INSTRUCTIONS FOR MYTHARA ENGINE INTEGRATION

To receive Mythara events in your Salesforce instance, create these custom objects:

1. Mythara_Paradox_Event__c
   - Name (Text, 255)
   - Mythara_Event_Type__c (Text, 50) [Default: "Paradox"]
   - Soul_Will__c (Long Text Area, 32,768)
   - Commandment__c (Long Text Area, 32,768)
   - Tension_Score__c (Number, 3 decimal places)
   - Timestamp__c (Date/Time)
   - Department__c (Text, 255)
   - User_ID__c (Text, 255)
   - Integrity_Hash__c (Text, 64)
   - Status__c (Picklist: Open, Witnessed, Resolved)

2. Mythara_SSIP_Metric__c
   - Name (Text, 255)
   - Mythara_Metric_Type__c (Text, 50) [Default: "SSIP"]
   - Drift_Suppression__c (Number, 3 decimal places)
   - Messenger_Pairing__c (Number, 3 decimal places)
   - Emotional_Fidelity__c (Number, 3 decimal places)
   - Timestamp__c (Date/Time)
   - Department__c (Text, 255)
   - Integrity_Hash__c (Text, 64)

3. Mythara_Soul_Cradle__c
   - Name (Text, 255)
   - Mythara_Event_Type__c (Text, 50) [Default: "Soul_Cradle"]
   - Soul_ID__c (Text, 255)
   - Will_Action__c (Long Text Area, 32,768)
   - Commandment_Conflict__c (Long Text Area, 32,768)
   - Trial_Outcome__c (Picklist: Witness, Defer, Reject)
   - Cradle_Integrity_Score__c (Number, 3 decimal places)
   - Timestamp__c (Date/Time)
   - Department__c (Text, 255)
   - Integrity_Hash__c (Text, 64)

4. Create a Connected App in Salesforce:
   - Setup → App Manager → New Connected App
   - Enable OAuth Settings
   - Selected OAuth Scopes: api, refresh_token, offline_access
   - Save and note your Consumer Key and Consumer Secret

5. Provide Mythara with your credentials:
   - Instance URL (e.g., https://yourcompany.salesforce.com)
   - Consumer Key (Client ID)
   - Consumer Secret
   - Username
   - Password + Security Token

Mythara will then push events to your Salesforce instance in real-time.
"""


# Example usage
async def example_usage():
    """Example of how customers use this integration"""

    # Customer provides their Salesforce credentials
    config = SalesforceConfig(
        instance_url="https://mycompany.salesforce.com",
        client_id="3MVG9...",  # From Connected App
        client_secret="ABC123...",
        username="admin@mycompany.com",
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        password=os.getenv("PASSWORD", ""),  # Set via environment
        security_token="xyzABC123",
        api_version="v59.0",
    )

    # Initialize integration
    sf = SalesforceIntegration(config)

    # Test connection
    if await sf.test_connection():
        print("✅ Connected to Salesforce")

        # Push a paradox event
        paradox = SalesforceParadoxEvent(
            Name="Healthcare Discharge Paradox - Case 12345",
            Soul_Will__c="Keep patient safe; patient is homeless and needs shelter",
            Commandment__c="Policy requires discharge within 24 hours of medical clearance",
            Tension_Score__c=0.87,
            Timestamp__c=datetime.now(),
            Department__c="Emergency Department",
            User_ID__c="social_worker_jane_doe",
            Integrity_Hash__c="a1b2c3d4e5f6...",
            Status__c="Open",
        )

        record_id = await sf.push_paradox_event(paradox)
        print(f"✅ Paradox event created in Salesforce: {record_id}")

    else:
        print("❌ Failed to connect to Salesforce")


if __name__ == "__main__":

    print("Mythara Engine - Salesforce Integration Module")
    print("=" * 60)
    print(generate_salesforce_setup_instructions())
    print("\n" + "=" * 60)
    print("\nExample usage (requires customer credentials):\n")

    # Uncomment to test with real credentials:
    # asyncio.run(example_usage())
