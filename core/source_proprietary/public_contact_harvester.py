#!/usr/bin/env python3
"""
Mythara Engine - Public Database Contact Harvester
Legally extracts business contacts from public government databases.

Copyright © 2025 Herbert Velez Jr. All rights reserved.

Data Sources (All Public & Legal):
- CMS Hospital Compare (Healthcare)
- FDIC BankFind (Banking)
- IRS Tax Exempt Org (Nonprofits)
- State Secretary of State Business Registries
- USA.gov Federal Agency Directory
"""

import requests
import csv
from typing import List, Dict, Optional
from datetime import datetime
import time
import os


class PublicContactHarvester:
    """
    Harvest business contacts from public databases only.
    100% legal, 100% free.
    """

    def __init__(self, output_dir: str = "prospecting_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mythara Business Development (Mythara.Engine@yahoo.com)"
            }
        )

    # ============================================
    # HEALTHCARE CONTACTS (CMS Hospital Compare)
    # ============================================

    def get_hospitals(self, state: str = None, limit: int = 10000) -> List[Dict]:
        """
        Get hospitals from CMS Hospital Compare API.
        Free, public data from Medicare.gov
        If state=None, gets ALL hospitals in USA.
        """
        if state:
            print(f"\n🏥 Fetching hospitals in {state}...")
        else:
            print("\n🏥 Fetching ALL hospitals in USA...")

        # CMS Hospital General Information API
        url = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"

        params = {"limit": limit, "offset": 0}

        # Add state filter if specified
        if state:
            params["conditions[0][property]"] = "state"
            params["conditions[0][value]"] = state

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            hospitals = []
            for record in data.get("results", []):
                hospital = {
                    "name": record.get("facility_name", ""),
                    "address": record.get("address", ""),
                    "city": record.get("city", ""),
                    "state": record.get("state", ""),
                    "zip": record.get("zip_code", ""),
                    "phone": record.get("phone_number", ""),
                    "type": record.get("hospital_type", ""),
                    "ownership": record.get("hospital_ownership", ""),
                    "emergency_services": record.get("emergency_services", ""),
                    "industry": "Healthcare",
                    "source": "CMS Hospital Compare",
                }
                hospitals.append(hospital)

            print(f"✅ Found {len(hospitals)} hospitals")
            return hospitals

        except Exception as e:
            print(f"❌ Error fetching hospitals: {e}")
            return []

    # ============================================
    # BANKING CONTACTS (FDIC BankFind)
    # ============================================

    def get_banks(self, state: str = None, limit: int = 10000) -> List[Dict]:
        """
        Get banks from FDIC BankFind API.
        Free, public data from FDIC.gov
        If state=None, gets ALL banks in USA.
        """
        if state:
            print(f"\n🏦 Fetching banks in {state}...")
        else:
            print("\n🏦 Fetching ALL banks in USA...")

        # FDIC BankFind API
        url = "https://banks.data.fdic.gov/api/institutions"

        params = {"limit": limit, "offset": 0, "format": "json"}

        # Add state filter if specified
        if state:
            params["filters"] = f"STNAME:'{state}'"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            banks = []
            for record in data.get("data", []):
                bank = {
                    "name": record.get("NAME", ""),
                    "address": record.get("ADDRESS", ""),
                    "city": record.get("CITY", ""),
                    "state": record.get("STNAME", ""),
                    "zip": record.get("ZIP", ""),
                    "phone": "",  # FDIC doesn't include phone in API
                    "cert_number": record.get("CERT", ""),
                    "charter_class": record.get("CHARTER", ""),
                    "assets": record.get("ASSET", ""),
                    "industry": "Banking",
                    "source": "FDIC BankFind",
                }
                banks.append(bank)

            print(f"✅ Found {len(banks)} banks")
            return banks

        except Exception as e:
            print(f"❌ Error fetching banks: {e}")
            return []

    # ============================================
    # NONPROFIT CONTACTS (IRS Tax Exempt Org)
    # ============================================

    def get_nonprofits(self, state: str = "CO", limit: int = 100) -> List[Dict]:
        """
        Get nonprofits from IRS Tax Exempt Organization dataset.
        Public 990 data - completely legal.
        """
        print(f"\n💜 Fetching nonprofits in {state}...")

        # IRS Tax Exempt Org dataset on data.gov
        # Note: This is a large dataset, using state filter

        # For demo purposes, using a smaller sample
        # Real implementation would download full dataset and filter locally

        nonprofits = []

        # Sample data structure (real implementation downloads CSV)
        print("⚠️  Nonprofit data requires CSV download from IRS.gov")
        print(
            "📥 Download from: https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads"
        )
        print("💡 File: 'Exempt Organizations Business Master File Extract (EO BMF)'")

        return nonprofits

    # ============================================
    # COLORADO BUSINESS REGISTRY
    # ============================================

    def get_colorado_businesses(
        self, entity_type: str = "Corporation", limit: int = 100
    ) -> List[Dict]:
        """
        Get businesses from Colorado Secretary of State.
        Public business registry - free access.
        """
        print(f"\n🏢 Fetching Colorado businesses ({entity_type})...")

        # Colorado SOS has a public search but no open API
        # This would require web scraping their public search form
        # OR downloading their bulk data files

        print("⚠️  Colorado SOS requires manual download")
        print(
            "📥 Download from: https://www.sos.state.co.us/biz/BusinessEntityCriteriaExt.do"
        )
        print("💡 Use 'Business Search' and export results")

        return []

    # ============================================
    # FEDERAL AGENCIES (USA.gov)
    # ============================================

    def get_federal_agencies(self) -> List[Dict]:
        """
        Get federal agencies from USA.gov directory.
        Public contact information.
        """
        print("\n🏛️ Fetching federal agencies...")

        # Federal Agency Directory API
        url = "https://www.usa.gov/api/USAGovAPI/contacts.json"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            agencies = []
            for record in data.get("contact", []):
                agency = {
                    "name": record.get("name", ""),
                    "description": record.get("description", ""),
                    "url": record.get("url", ""),
                    "phone": record.get("phone", ""),
                    "email": record.get("email", ""),
                    "address": record.get("street1", ""),
                    "city": record.get("city", ""),
                    "state": record.get("state", ""),
                    "zip": record.get("zip", ""),
                    "industry": "Government",
                    "source": "USA.gov Federal Directory",
                }
                agencies.append(agency)

            print(f"✅ Found {len(agencies)} federal agencies")
            return agencies

        except Exception as e:
            print(f"❌ Error fetching agencies: {e}")
            return []

    # ============================================
    # LAW ENFORCEMENT (FBI CJIS Directory)
    # ============================================

    def get_law_enforcement(self, state: str = None) -> List[Dict]:
        """
        Get law enforcement agencies.
        Note: This requires manual data compilation from public sources.
        """
        print("\n👮 Fetching law enforcement agencies...")

        # Law enforcement data typically from:
        # - State police departments (public contact pages)
        # - County sheriff's offices (public records)
        # - Municipal police departments (city websites)

        print("⚠️  Law enforcement contact data requires manual compilation")
        print("📥 Sources:")
        print("   - State police websites (each state has public directory)")
        print("   - National Sheriff's Association directory")
        print("   - Municipal police department websites")

        return []

    # ============================================
    # SCHOOL DISTRICTS (NCES Directory)
    # ============================================

    def get_school_districts(self, state: str = None, limit: int = 10000) -> List[Dict]:
        """
        Get school districts from National Center for Education Statistics.
        Public data from Department of Education.
        """
        if state:
            print(f"\n🎓 Fetching school districts in {state}...")
        else:
            print("\n🎓 Fetching ALL school districts in USA...")

        # NCES Public School District data
        # Note: NCES has downloadable datasets but no direct REST API
        # Data available at: https://nces.ed.gov/ccd/pubagency.asp

        print("⚠️  School district data requires CSV download from NCES")
        print("📥 Download from: https://nces.ed.gov/ccd/pubagency.asp")
        print("💡 File: 'Public Elementary/Secondary School Universe Survey Data'")

        return []

    # ============================================
    # DEPARTMENT OF DEFENSE ENTITIES
    # ============================================

    def get_dod_entities(self) -> List[Dict]:
        """
        Get DoD entities from Defense.gov directory.
        Public contact information.
        """
        print("\n🪖 Fetching Department of Defense entities...")

        # DoD has public contact directories but no API
        # Available at: https://www.defense.gov/Resources/Military-Departments/

        # Sample DoD entities (public knowledge)
        dod_entities = [
            {
                "name": "Department of the Army",
                "url": "https://www.army.mil",
                "phone": "(703) 695-2442",
                "address": "The Pentagon",
                "city": "Arlington",
                "state": "VA",
                "zip": "22202",
                "industry": "DoD",
                "source": "Defense.gov",
            },
            {
                "name": "Department of the Navy",
                "url": "https://www.navy.mil",
                "phone": "(703) 697-7391",
                "address": "The Pentagon",
                "city": "Arlington",
                "state": "VA",
                "zip": "22202",
                "industry": "DoD",
                "source": "Defense.gov",
            },
            {
                "name": "Department of the Air Force",
                "url": "https://www.af.mil",
                "phone": "(703) 697-6061",
                "address": "The Pentagon",
                "city": "Arlington",
                "state": "VA",
                "zip": "22202",
                "industry": "DoD",
                "source": "Defense.gov",
            },
            {
                "name": "Defense Information Systems Agency (DISA)",
                "url": "https://www.disa.mil",
                "phone": "(703) 607-6001",
                "address": "P.O. Box 549",
                "city": "Fort Meade",
                "state": "MD",
                "zip": "20755",
                "industry": "DoD",
                "source": "Defense.gov",
            },
        ]

        print(f"✅ Found {len(dod_entities)} DoD entities (sample)")
        print("⚠️  Full DoD directory requires manual compilation from Defense.gov")

        return dod_entities

    # ============================================
    # LOCAL GOVERNMENT (City/County)
    # ============================================

    def get_local_governments(self, state: str = None) -> List[Dict]:
        """
        Get local government contacts (cities, counties).
        Data from National League of Cities / NACo.
        """
        if state:
            print(f"\n🏛️ Fetching local governments in {state}...")
        else:
            print("\n🏛️ Fetching local governments nationwide...")

        print("⚠️  Local government data requires compilation from:")
        print("   - National League of Cities: https://www.nlc.org")
        print("   - National Association of Counties: https://www.naco.org")
        print("   - State municipal league websites")
        print("   - Individual city/county websites (public contact info)")

        return []

    # ============================================
    # EMAIL FINDER (Hunter.io FREE tier)
    # ============================================

    def find_email(self, company_name: str, domain: str = None) -> Optional[str]:
        """
        Find email using Hunter.io free tier (50 searches/month).
        Requires API key from hunter.io (free account).
        """
        api_key = os.getenv("HUNTER_API_KEY")

        if not api_key:
            return None

        # Extract domain from company name if not provided
        if not domain:
            # Simple domain guess: companyname.com
            domain = company_name.lower().replace(" ", "").replace(",", "") + ".com"

        url = "https://api.hunter.io/v2/domain-search"
        params = {"domain": domain, "api_key": api_key, "limit": 1}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            emails = data.get("data", {}).get("emails", [])
            if emails:
                return emails[0].get("value")

        except Exception:
            pass

        return None

    # ============================================
    # EXPORT TO CSV
    # ============================================

    def export_to_csv(self, contacts: List[Dict], filename: str):
        """Export contacts to CSV file"""
        filepath = os.path.join(self.output_dir, filename)

        if not contacts:
            print("⚠️  No contacts to export")
            return

        # Get all unique keys from contacts
        fieldnames = set()
        for contact in contacts:
            fieldnames.update(contact.keys())
        fieldnames = sorted(list(fieldnames))

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contacts)

        print(f"✅ Exported {len(contacts)} contacts to {filepath}")

    # ============================================
    # RUN ALL HARVESTERS
    # ============================================

    def harvest_all(self, state: str = None):
        """
        Run all harvesters and export results.
        If state=None, harvests ENTIRE USA.
        """
        print("=" * 60)
        print("MYTHARA LABS - PUBLIC DATABASE CONTACT HARVESTER")
        print("=" * 60)
        if state:
            print(f"Target State: {state}")
        else:
            print("Target: ENTIRE USA 🇺🇸")
        print(f"Output Directory: {self.output_dir}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)

        all_contacts = []

        # Healthcare (this may take a while for entire USA)
        hospitals = self.get_hospitals(state=state, limit=10000)
        all_contacts.extend(hospitals)
        filename_suffix = state if state else "USA"
        self.export_to_csv(
            hospitals,
            f"hospitals_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv",
        )
        time.sleep(2)  # Rate limiting

        # Banking
        banks = self.get_banks(state=state, limit=10000)
        all_contacts.extend(banks)
        self.export_to_csv(
            banks, f"banks_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        time.sleep(2)

        # Federal Agencies (always nationwide)
        agencies = self.get_federal_agencies()
        all_contacts.extend(agencies)
        self.export_to_csv(
            agencies, f"federal_agencies_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        time.sleep(1)

        # Department of Defense
        dod = self.get_dod_entities()
        all_contacts.extend(dod)
        self.export_to_csv(dod, f"dod_entities_{datetime.now().strftime('%Y%m%d')}.csv")
        time.sleep(1)

        # Law Enforcement (manual compilation required)
        law_enforcement = self.get_law_enforcement(state=state)
        if law_enforcement:
            all_contacts.extend(law_enforcement)
            self.export_to_csv(
                law_enforcement,
                f"law_enforcement_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv",
            )

        # School Districts (manual download required)
        schools = self.get_school_districts(state=state)
        if schools:
            all_contacts.extend(schools)
            self.export_to_csv(
                schools,
                f"school_districts_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv",
            )

        # Local Governments (manual compilation required)
        local_gov = self.get_local_governments(state=state)
        if local_gov:
            all_contacts.extend(local_gov)
            self.export_to_csv(
                local_gov,
                f"local_governments_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv",
            )

        # Master list
        self.export_to_csv(
            all_contacts,
            f"all_contacts_{filename_suffix}_{datetime.now().strftime('%Y%m%d')}.csv",
        )

        print("\n" + "=" * 60)
        print("✅ HARVEST COMPLETE")
        print(f"Total Contacts: {len(all_contacts)}")
        print(f"Healthcare: {len(hospitals)}")
        print(f"Banking: {len(banks)}")
        print(f"Federal Government: {len(agencies)}")
        print(f"Department of Defense: {len(dod)}")
        if law_enforcement:
            print(f"Law Enforcement: {len(law_enforcement)}")
        if schools:
            print(f"School Districts: {len(schools)}")
        if local_gov:
            print(f"Local Governments: {len(local_gov)}")
        print("=" * 60)

        return all_contacts


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    print("""
    MYTHARA LABS - PUBLIC DATABASE CONTACT HARVESTER
    
    Legal, free contact data from public government sources.
    
    SETUP:
    1. (Optional) Get free Hunter.io API key for email finder
       Sign up at: https://hunter.io/users/sign_up
       Free tier: 50 email searches/month
       Set environment variable: HUNTER_API_KEY=your_key_here
    
    2. Run this script to harvest contacts
    
    SOURCES:
    - CMS Hospital Compare (healthcare facilities)
    - FDIC BankFind (banks and credit unions)
    - IRS Tax Exempt Org (nonprofits)
    - USA.gov Federal Directory (government agencies)
    
    OUTPUT:
    - CSV files in prospecting_data/ folder
    - Ready to import into CRM or email tool
    
    ===============================================
    """)

    # Initialize harvester
    harvester = PublicContactHarvester()

    # Harvest contacts for ENTIRE USA (pass state=None for all states)
    # Or specify a state: harvester.harvest_all(state="CO")
    contacts = harvester.harvest_all(state=None)  # ENTIRE USA

    print("\n📧 Next Steps:")
    print("1. Review CSV files in prospecting_data/ folder")
    print("2. Import into your CRM (HubSpot, Salesforce, etc.)")
    print("3. Use Hunter.io to find executive emails (Operations VP, CEO)")
    print("4. Send personalized outreach about Soul Cradle")
    print("5. Track responses and follow-ups")
    print("\n✅ 100% Legal | 100% Free | 100% Mythara")
