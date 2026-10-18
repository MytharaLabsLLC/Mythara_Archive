#!/usr/bin/env python3
"""
Mythara Engine - Universal CRM Integration Module
Writes paradox events, SSIP metrics, and Soul Cradle data to any CRM system.

Supported CRMs:
- Salesforce
- HubSpot
- Microsoft Dynamics 365
- Zoho CRM
- ServiceNow
- Custom REST APIs

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import os
import logging
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import httpx
from enum import Enum

logger = logging.getLogger(__name__)


class CRMProvider(str, Enum):
    """Supported CRM providers"""

    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    DYNAMICS365 = "dynamics365"
    ZOHO = "zoho"
    SERVICENOW = "servicenow"
    CUSTOM = "custom"


class CRMConfig(BaseModel):
    """Universal CRM configuration"""

    provider: CRMProvider
    api_url: str = Field(..., description="Base API URL")
    api_key: Optional[str] = Field(None, description="API key (HubSpot, Zoho)")
    access_token: Optional[str] = Field(None, description="OAuth access token")
    client_id: Optional[str] = Field(None, description="OAuth client ID")
    client_secret: Optional[str] = Field(None, description="OAuth client secret")
    tenant_id: Optional[str] = Field(None, description="Microsoft tenant ID")
    instance_name: Optional[str] = Field(
        None, description="Instance name (Dynamics, ServiceNow)"
    )
    custom_headers: Optional[Dict[str, str]] = Field(
        None, description="Custom HTTP headers"
    )


class MytharaEvent(BaseModel):
    """Universal Mythara event structure"""

    event_type: Literal["paradox", "ssip_metric", "soul_cradle"]
    name: str
    timestamp: datetime
    data: Dict[str, Any]
    integrity_hash: str
    department: Optional[str] = None
    user_id: Optional[str] = None


class CRMIntegration:
    """Universal CRM integration handler"""

    def __init__(self, config: CRMConfig):
        self.config = config
        self.provider = config.provider

    async def push_event(self, event: MytharaEvent) -> Optional[str]:
        """Push event to CRM based on provider"""

        if self.provider == CRMProvider.SALESFORCE:
            return await self._push_to_salesforce(event)
        elif self.provider == CRMProvider.HUBSPOT:
            return await self._push_to_hubspot(event)
        elif self.provider == CRMProvider.DYNAMICS365:
            return await self._push_to_dynamics365(event)
        elif self.provider == CRMProvider.ZOHO:
            return await self._push_to_zoho(event)
        elif self.provider == CRMProvider.SERVICENOW:
            return await self._push_to_servicenow(event)
        elif self.provider == CRMProvider.CUSTOM:
            return await self._push_to_custom_api(event)
        else:
            logger.error(f"Unsupported CRM provider: {self.provider}")
            return None

    # ============================================
    # SALESFORCE INTEGRATION
    # ============================================

    async def _push_to_salesforce(self, event: MytharaEvent) -> Optional[str]:
        """Push to Salesforce custom object"""

        object_type = {
            "paradox": "Mythara_Paradox_Event__c",
            "ssip_metric": "Mythara_SSIP_Metric__c",
            "soul_cradle": "Mythara_Soul_Cradle__c",
        }.get(event.event_type)

        url = f"{self.config.api_url}/services/data/v59.0/sobjects/{object_type}"
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }

        # Map to Salesforce field names
        payload = {
            "Name": event.name,
            "Mythara_Event_Type__c": event.event_type,
            "Timestamp__c": event.timestamp.isoformat(),
            "Integrity_Hash__c": event.integrity_hash,
            "Department__c": event.department,
            "User_ID__c": event.user_id,
            **{f"{k}__c": v for k, v in event.data.items()},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(
                    f"✅ Salesforce: Created {object_type} - {result.get('id')}"
                )
                return result.get("id")
        except httpx.HTTPError as e:
            logger.error(f"❌ Salesforce push failed: {e}")
            return None

    # ============================================
    # HUBSPOT INTEGRATION
    # ============================================

    async def _push_to_hubspot(self, event: MytharaEvent) -> Optional[str]:
        """Push to HubSpot custom object or timeline event"""

        url = f"{self.config.api_url}/crm/v3/objects/mythara_events"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        # HubSpot uses properties dict
        payload = {
            "properties": {
                "mythara_event_type": event.event_type,
                "event_name": event.name,
                "timestamp": event.timestamp.isoformat(),
                "integrity_hash": event.integrity_hash,
                "department": event.department or "",
                "user_id": event.user_id or "",
                **event.data,
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ HubSpot: Created event - {result.get('id')}")
                return result.get("id")
        except httpx.HTTPError as e:
            logger.error(f"❌ HubSpot push failed: {e}")
            return None

    # ============================================
    # MICROSOFT DYNAMICS 365 INTEGRATION
    # ============================================

    async def _push_to_dynamics365(self, event: MytharaEvent) -> Optional[str]:
        """Push to Dynamics 365 custom entity"""

        entity_name = "mythara_events"
        url = f"{self.config.api_url}/api/data/v9.2/{entity_name}"
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }

        # Dynamics uses underscore prefix for custom fields
        payload = {
            "mythara_name": event.name,
            "mythara_eventtype": event.event_type,
            "mythara_timestamp": event.timestamp.isoformat(),
            "mythara_integrityhash": event.integrity_hash,
            "mythara_department": event.department,
            "mythara_userid": event.user_id,
            **{f"mythara_{k}": v for k, v in event.data.items()},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()

                # Dynamics returns entity ID in location header
                entity_id = (
                    response.headers.get("OData-EntityId", "")
                    .split("(")[-1]
                    .split(")")[0]
                )
                logger.info(f"✅ Dynamics 365: Created entity - {entity_id}")
                return entity_id
        except httpx.HTTPError as e:
            logger.error(f"❌ Dynamics 365 push failed: {e}")
            return None

    # ============================================
    # ZOHO CRM INTEGRATION
    # ============================================

    async def _push_to_zoho(self, event: MytharaEvent) -> Optional[str]:
        """Push to Zoho CRM custom module"""

        module_name = "Mythara_Events"
        url = f"{self.config.api_url}/crm/v2/{module_name}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "data": [
                {
                    "Name": event.name,
                    "Event_Type": event.event_type,
                    "Timestamp": event.timestamp.isoformat(),
                    "Integrity_Hash": event.integrity_hash,
                    "Department": event.department,
                    "User_ID": event.user_id,
                    **event.data,
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                record_id = result.get("data", [{}])[0].get("details", {}).get("id")
                logger.info(f"✅ Zoho CRM: Created record - {record_id}")
                return record_id
        except httpx.HTTPError as e:
            logger.error(f"❌ Zoho CRM push failed: {e}")
            return None

    # ============================================
    # SERVICENOW INTEGRATION
    # ============================================

    async def _push_to_servicenow(self, event: MytharaEvent) -> Optional[str]:
        """Push to ServiceNow custom table"""

        table_name = "u_mythara_events"
        url = f"{self.config.api_url}/api/now/table/{table_name}"
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "u_name": event.name,
            "u_event_type": event.event_type,
            "u_timestamp": event.timestamp.isoformat(),
            "u_integrity_hash": event.integrity_hash,
            "u_department": event.department,
            "u_user_id": event.user_id,
            **{f"u_{k}": v for k, v in event.data.items()},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                sys_id = result.get("result", {}).get("sys_id")
                logger.info(f"✅ ServiceNow: Created record - {sys_id}")
                return sys_id
        except httpx.HTTPError as e:
            logger.error(f"❌ ServiceNow push failed: {e}")
            return None

    # ============================================
    # CUSTOM REST API INTEGRATION
    # ============================================

    async def _push_to_custom_api(self, event: MytharaEvent) -> Optional[str]:
        """Push to any custom REST API endpoint"""

        headers = self.config.custom_headers or {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload = {
            "event_type": event.event_type,
            "name": event.name,
            "timestamp": event.timestamp.isoformat(),
            "integrity_hash": event.integrity_hash,
            "department": event.department,
            "user_id": event.user_id,
            "data": event.data,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.api_url, json=payload, headers=headers, timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                record_id = result.get("id") or result.get("record_id") or "success"
                logger.info(f"✅ Custom API: Event pushed - {record_id}")
                return record_id
        except httpx.HTTPError as e:
            logger.error(f"❌ Custom API push failed: {e}")
            return None

    async def test_connection(self) -> bool:
        """Test connection to CRM"""
        try:
            if self.provider == CRMProvider.SALESFORCE:
                url = f"{self.config.api_url}/services/data/v59.0/sobjects"
            elif self.provider == CRMProvider.HUBSPOT:
                url = f"{self.config.api_url}/crm/v3/objects"
            elif self.provider == CRMProvider.DYNAMICS365:
                url = f"{self.config.api_url}/api/data/v9.2/EntityDefinitions"
            elif self.provider == CRMProvider.ZOHO:
                url = f"{self.config.api_url}/crm/v2/settings/modules"
            elif self.provider == CRMProvider.SERVICENOW:
                url = f"{self.config.api_url}/api/now/table/sys_user?sysparm_limit=1"
            else:
                url = self.config.api_url

            headers = {}
            if self.config.access_token:
                headers["Authorization"] = f"Bearer {self.config.access_token}"
            elif self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info(f"✅ {self.provider.value} connection test successful")
                return True

        except httpx.HTTPError as e:
            logger.error(f"❌ {self.provider.value} connection test failed: {e}")
            return False


# ============================================
# SETUP INSTRUCTIONS GENERATOR
# ============================================


def generate_crm_setup_instructions(provider: CRMProvider) -> str:
    """Generate setup instructions for specific CRM provider"""

    instructions = {
        CRMProvider.SALESFORCE: """
SALESFORCE SETUP:
1. Create custom objects: Mythara_Paradox_Event__c, Mythara_SSIP_Metric__c, Mythara_Soul_Cradle__c
2. Add custom fields (all with __c suffix): Name, Event_Type, Timestamp, Integrity_Hash, Department, User_ID
3. Create Connected App for OAuth
4. Provide: Instance URL, Client ID, Client Secret, Username, Password, Security Token
""",
        CRMProvider.HUBSPOT: """
HUBSPOT SETUP:
1. Go to Settings → Data Management → Objects
2. Create custom object: "Mythara Events"
3. Add properties: event_type, timestamp, integrity_hash, department, user_id
4. Generate Private App token (Settings → Integrations → Private Apps)
5. Provide: API base URL (https://api.hubapi.com), API key
""",
        CRMProvider.DYNAMICS365: """
MICROSOFT DYNAMICS 365 SETUP:
1. Go to Settings → Customizations → Customize the System
2. Create new entity: "mythara_events"
3. Add fields: name, eventtype, timestamp, integrityhash, department, userid
4. Register Azure AD app for authentication
5. Provide: Instance URL, Tenant ID, Client ID, Client Secret, Access Token
""",
        CRMProvider.ZOHO: """
ZOHO CRM SETUP:
1. Setup → Customization → Modules and Fields
2. Create custom module: "Mythara Events"
3. Add fields: Name, Event_Type, Timestamp, Integrity_Hash, Department, User_ID
4. Generate OAuth token (Setup → Developer Space → Self Client)
5. Provide: API base URL (https://www.zohoapis.com), OAuth token
""",
        CRMProvider.SERVICENOW: """
SERVICENOW SETUP:
1. Navigate to System Definition → Tables
2. Create table: "u_mythara_events"
3. Add columns: u_name, u_event_type, u_timestamp, u_integrity_hash, u_department, u_user_id
4. Create OAuth client (System OAuth → Application Registry)
5. Provide: Instance URL, Client ID, Client Secret, Access Token
""",
        CRMProvider.CUSTOM: """
CUSTOM API SETUP:
1. Implement REST endpoint that accepts POST requests
2. Endpoint should accept JSON with: event_type, name, timestamp, integrity_hash, department, user_id, data
3. Return JSON with "id" or "record_id" field
4. Provide: API endpoint URL, authentication method (Bearer token or custom headers)
""",
    }

    return instructions.get(
        provider, "Setup instructions not available for this provider."
    )


# Example usage
async def example_multi_crm():
    """Example showing multiple CRM integrations"""

    # Salesforce
    sf_config = CRMConfig(
        provider=CRMProvider.SALESFORCE,
        api_url="https://mycompany.salesforce.com",
        access_token="00D...",
    )

    # HubSpot
    hs_config = CRMConfig(
        provider=CRMProvider.HUBSPOT,
        api_url="https://api.hubapi.com",
        # QUICKFIX FIX: Moved to environment variable (CWE-798)
        api_key=os.getenv("API_KEY", ""),  # Set via environment
    )

    # Create event
    event = MytharaEvent(
        event_type="paradox",
        name="Healthcare Discharge Paradox",
        timestamp=datetime.now(),
        data={
            "soul_will": "Keep patient safe",
            "commandment": "Policy requires discharge",
            "tension_score": 0.87,
        },
        integrity_hash="a1b2c3d4e5f6...",
        department="Emergency Dept",
    )

    # Push to both CRMs
    sf = CRMIntegration(sf_config)
    hs = CRMIntegration(hs_config)

    sf_id = await sf.push_event(event)
    hs_id = await hs.push_event(event)

    print(f"✅ Event synced to Salesforce: {sf_id}")
    print(f"✅ Event synced to HubSpot: {hs_id}")


if __name__ == "__main__":

    print("Mythara Engine - Universal CRM Integration")
    print("=" * 60)
    print("\nSupported CRMs:")
    for provider in CRMProvider:
        print(f"  • {provider.value.title()}")
    print("\n" + "=" * 60)
