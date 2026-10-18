import os
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Add all Mythara products to Loyverse via API.
Uses Loyverse API to create items with SKUs, prices, and descriptions.
"""

import requests
import json

# Loyverse API credentials
# QUICKFIX FIX: Moved to environment variable (CWE-798)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")  # Set via environment
API_BASE_URL = "https://api.loyverse.com/v1.0"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Mythara products
PRODUCTS = [
    {
        "item_name": "Mythara SSIP Compliance Readiness Assessment",
        "sku": "MYTH-AUDIT-001",
        "category": "Professional Services",
        "price": 2500.00,
        "description": "Single AI model validation with cryptographic proof. Includes integrity hash chain and readiness assessment report.",
        "track_stock": False
    },
    {
        "item_name": "Mythara Engine - Monthly",
        "sku": "MYTH-SUB-MONTH",
        "category": "SaaS Subscription",
        "price": 500.00,
        "description": "Unlimited model validations with API access and 24-hour support.",
        "track_stock": False
    },
    {
        "item_name": "Mythara Engine - Annual",
        "sku": "MYTH-SUB-YEAR",
        "category": "SaaS Subscription",
        "price": 5000.00,
        "description": "Annual subscription with priority support and custom clause per quarter. Save $1000 vs monthly.",
        "track_stock": False
    },
    {
        "item_name": "Mythara Enterprise License",
        "sku": "MYTH-ENT-YEAR",
        "category": "Enterprise",
        "price": 25000.00,
        "description": "Full platform with on-premise deployment and unlimited custom clauses. Includes dedicated account manager.",
        "track_stock": False
    },
    {
        "item_name": "Custom Clause Development",
        "sku": "MYTH-CUSTOM-001",
        "category": "Custom Development",
        "price": 10000.00,
        "description": "Domain-specific SSIP clause engineering with testing suite and 30-day support.",
        "track_stock": False
    },
    {
        "item_name": "Training & Onboarding",
        "sku": "MYTH-TRAIN-001",
        "category": "Training",
        "price": 1000.00,
        "description": "Live workshop with API integration and best practices guide. Includes recorded session.",
        "track_stock": False
    },
    {
        "item_name": "VoIP Bot License",
        "sku": "MYTH-VOIP-2026",
        "category": "Enterprise Software",
        "price": 1500000.00,
        "description": "Full VoIP bot source code with 5 voice personas and 6 months support. Ships Q1 2026.",
        "track_stock": False
    },
    {
        "item_name": "Extended Audit Suite",
        "sku": "MYTH-ADDON-AUDIT",
        "category": "Add-Ons",
        "price": 5000.00,
        "description": "Quarterly compliance audits for ongoing validation.",
        "track_stock": False
    },
    {
        "item_name": "Bespoke Accessibility",
        "sku": "MYTH-ADDON-ACCESS",
        "category": "Add-Ons",
        "price": 3000.00,
        "description": "Custom braille and audio token generation.",
        "track_stock": False
    },
    {
        "item_name": "Priority SLA",
        "sku": "MYTH-ADDON-SLA",
        "category": "Add-Ons",
        "price": 2000.00,
        "description": "1-hour response time guarantee.",
        "track_stock": False
    },
    {
        "item_name": "Dedicated Infrastructure",
        "sku": "MYTH-ADDON-INFRA",
        "category": "Add-Ons",
        "price": 8000.00,
        "description": "Private AWS/Azure deployment.",
        "track_stock": False
    },
    {
        "item_name": "Source Code Escrow Unlock",
        "sku": "MYTH-ADDON-ESCROW",
        "category": "Add-Ons",
        "price": 15000.00,
        "description": "Full source code access with rebuild rights.",
        "track_stock": False
    }
]


def create_item(product):
    """Create a single item in Loyverse."""
    
    # Loyverse API format
    payload = {
        "item_name": product["item_name"],
        "reference_id": product["sku"],  # SKU goes here
        "description": product["description"],
        "track_stock": product["track_stock"],
        "sold_by_weight": False,
        "is_composite": False,
        "use_production": False,
        "components": [],
        "variants": [
            {
                "variant_name": product["item_name"],
                "sku": product["sku"],
                "reference_id": product["sku"],
                "price": product["price"],
                "cost": 0,
                "default_price_money": {
                    "amount": int(product["price"] * 100),  # Convert to cents
                    "currency": "USD"
                }
            }
        ]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/items",
        headers=HEADERS,
        json=payload
    )
    
    return response


def add_all_products():
    """Add all Mythara products to Loyverse."""
    
    print("🚀 Adding Mythara products to Loyverse...\n")
    
    success_count = 0
    failed_count = 0
    
    for product in PRODUCTS:
        print(f"Adding: {product['item_name']} ({product['sku']})...", end=" ")
        
        try:
            response = create_item(product)
            
            if response.status_code in [200, 201]:
                print("✅ Success")
                success_count += 1
            else:
                print(f"❌ Failed ({response.status_code})")
                print(f"   Error: {response.text}")
                failed_count += 1
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            failed_count += 1
    
    print(f"\n✅ Added: {success_count}/{len(PRODUCTS)} products")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count} products")
    
    print("\nNext steps:")
    print("1. Go to Loyverse dashboard → Items")
    print("2. Upload icons from: Commercial/assets/glyphs_png/dark/128/")
    print("3. Set up discount codes (EARLY20, PILOT3M)")


if __name__ == "__main__":
    add_all_products()
