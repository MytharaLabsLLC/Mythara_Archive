#!/usr/bin/env python3
"""
Mythara Outreach Pipeline - Harvest to Email
Connects public database harvester to automated email outreach.

Copyright © 2025 Herbert Velez Jr. All rights reserved.

PIPELINE:
1. Harvest contacts from public databases
2. Enrich with Hunter.io emails (optional)
3. Generate personalized outreach emails
4. Export ready-to-send campaign

LEGAL COMPLIANCE:
- Uses only public government data
- CAN-SPAM compliant (business contact info)
- Includes unsubscribe mechanism
- One-time outreach per contact (no spam)
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class OutreachPipeline:
    """
    End-to-end outreach pipeline:
    Harvested contacts → Personalized emails → Ready to send
    """

    def __init__(self, contacts_csv: str, output_dir: str = "outreach_campaigns"):
        self.contacts_csv = contacts_csv
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def load_contacts(self) -> List[Dict]:
        """Load contacts from harvester CSV"""
        contacts = []
        with open(self.contacts_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append(row)
        return contacts

    def generate_email_healthcare(self, contact: Dict) -> Dict:
        """Generate personalized email for healthcare facilities"""

        hospital_name = contact.get("name", "Your Organization")
        city = contact.get("city", "")
        state = contact.get("state", "")

        subject = f"Soul Cradle for {hospital_name} — Paradox orchestration pilot"

        body = f"""Hi there,

I'm reaching out to {hospital_name} in {city}, {state} about Soul Cradle — a system that documents the impossible choices your team faces every day.

You know that moment: A social worker has to discharge a patient who'll be homeless. Policy says discharge. Her heart says keep them safe. Both are true.

Soul Cradle holds that paradox. It:
- Documents the conflict between mission and compliance
- Measures the emotional cost to your people
- Creates cryptographic records for leadership and regulators
- Prevents mission drift while maintaining compliance

We donate Soul Cradle to healthcare facilities. No charge. It's included with our 7-day $49 Pilot.

If your team is carrying that weight, let's talk: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Mythara Labs LLC — a Colorado domestic limited liability company; Articles of Organization filed with the Colorado Secretary of State on September 27, 2026, pending completion; member-managed; sole member and organizer: Herbert Velez Jr.
mytharaarchive-production.up.railway.app/pricing

P.S. — This is a one-time email. Reply with "unsubscribe" and I won't reach out again."""

        return {
            "to": contact.get("email", ""),
            "to_name": hospital_name,
            "subject": subject,
            "body": body,
            "industry": "Healthcare",
            "contact_data": contact,
        }

    def generate_email_banking(self, contact: Dict) -> Dict:
        """Generate personalized email for banks"""

        bank_name = contact.get("name", "Your Organization")
        city = contact.get("city", "")
        state = contact.get("state", "")

        subject = (
            f"Soul Cradle for {bank_name} — Managing compliance vs. mission conflicts"
        )

        body = f"""Hi there,

I'm reaching out to {bank_name} in {city}, {state} about a tool we built for the moments when regulations conflict with helping your customers.

Banker sees a family drowning financially. Knows what would help. Policy says no.

Soul Cradle documents that paradox:
- Records the conflict between policy and mission
- Measures the cost to your team's well-being
- Generates compliance-ready reports with cryptographic proofs
- Shows leadership the human impact of policy gaps

Try it free for 7 days ($49 Pilot, includes full Soul Cradle access).

If your team faces those impossible moments: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Mythara Labs LLC — a Colorado domestic limited liability company; Articles of Organization filed with the Colorado Secretary of State on September 27, 2026, pending completion; member-managed; sole member and organizer: Herbert Velez Jr.
mytharaarchive-production.up.railway.app/pricing

P.S. — One-time outreach. Reply "unsubscribe" to opt out."""

        return {
            "to": contact.get("email", ""),
            "to_name": bank_name,
            "subject": subject,
            "body": body,
            "industry": "Banking",
            "contact_data": contact,
        }

    def generate_email_government(self, contact: Dict) -> Dict:
        """Generate personalized email for government agencies"""

        agency_name = contact.get("name", "Your Agency")

        subject = (
            f"Soul Cradle for {agency_name} — When policy conflicts with public service"
        )

        body = f"""Hi there,

I'm reaching out to {agency_name} about Soul Cradle — built for civil servants trapped between policy and the people they serve.

Case worker knows a family needs help. Regulation says they don't qualify. Both are true.

Soul Cradle:
- Documents policy-vs-mission conflicts
- Measures burnout and emotional drift
- Creates audit-ready records for oversight
- Protects your people while maintaining compliance

We donate Soul Cradle to government agencies. 7-day Pilot: $49 (includes everything).

If your team is carrying that weight: Mythara.Engine@yahoo.com

Best,
Herbert Velez Jr.
Mythara Labs LLC — a Colorado domestic limited liability company; Articles of Organization filed with the Colorado Secretary of State on September 27, 2026, pending completion; member-managed; sole member and organizer: Herbert Velez Jr.
mytharaarchive-production.up.railway.app/pricing

P.S. — This is a one-time email. Reply "unsubscribe" to opt out."""

        return {
            "to": contact.get("email", ""),
            "to_name": agency_name,
            "subject": subject,
            "body": body,
            "industry": "Government",
            "contact_data": contact,
        }

    def generate_campaign(self) -> List[Dict]:
        """Generate full email campaign from harvested contacts"""

        print("\n" + "=" * 60)
        print("MYTHARA OUTREACH CAMPAIGN GENERATOR")
        print("=" * 60)

        contacts = self.load_contacts()
        print(f"✅ Loaded {len(contacts)} contacts from {self.contacts_csv}")

        emails = []

        for contact in contacts:
            industry = contact.get("industry", "").lower()

            # Generate email based on industry
            if "healthcare" in industry or "hospital" in industry:
                email = self.generate_email_healthcare(contact)
            elif "bank" in industry or "credit union" in industry:
                email = self.generate_email_banking(contact)
            elif "government" in industry or "federal" in industry:
                email = self.generate_email_government(contact)
            else:
                continue  # Skip contacts without clear industry

            # Only include if we have an email address
            if email["to"]:
                emails.append(email)

        print(f"✅ Generated {len(emails)} personalized emails")

        # Export to CSV for email tools
        self.export_campaign(emails)

        # Export to JSON for programmatic sending
        self.export_json(emails)

        return emails

    def export_campaign(self, emails: List[Dict]):
        """Export campaign to CSV for import into email tools"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"email_campaign_{timestamp}.csv"

        fieldnames = ["to", "to_name", "subject", "body", "industry"]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for email in emails:
                writer.writerow(
                    {
                        "to": email["to"],
                        "to_name": email["to_name"],
                        "subject": email["subject"],
                        "body": email["body"],
                        "industry": email["industry"],
                    }
                )

        print(f"✅ Campaign exported to: {csv_path}")
        print("   Ready to import into: Mailchimp, SendGrid, Yahoo Mail, etc.")

    def export_json(self, emails: List[Dict]):
        """Export campaign to JSON for API sending"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"email_campaign_{timestamp}.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2)

        print(f"✅ Campaign exported to: {json_path}")
        print("   Use with: email_bot.py or SendGrid API")


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    print("""
    MYTHARA OUTREACH PIPELINE
    
    STEP 1: Harvest contacts
    > py public_contact_harvester.py
    
    STEP 2: Generate email campaign
    > py outreach_pipeline.py
    
    STEP 3: Send emails
    - Import CSV into Mailchimp/SendGrid
    - OR use email_bot.py to send programmatically
    
    ===============================================
    """)

    # Find the most recent contacts file
    prospecting_dir = Path("prospecting_data")
    if prospecting_dir.exists():
        contact_files = sorted(prospecting_dir.glob("all_contacts_*.csv"), reverse=True)

        if contact_files:
            latest_file = contact_files[0]
            print(f"📂 Using contact file: {latest_file}")

            # Generate campaign
            pipeline = OutreachPipeline(str(latest_file))
            emails = pipeline.generate_campaign()

            print("\n" + "=" * 60)
            print("✅ OUTREACH CAMPAIGN READY")
            print("=" * 60)
            print(f"Total Emails: {len(emails)}")
            print("\nIndustry Breakdown:")

            healthcare_count = sum(1 for e in emails if e["industry"] == "Healthcare")
            banking_count = sum(1 for e in emails if e["industry"] == "Banking")
            gov_count = sum(1 for e in emails if e["industry"] == "Government")

            print(f"  Healthcare: {healthcare_count}")
            print(f"  Banking: {banking_count}")
            print(f"  Government: {gov_count}")

            print("\n📧 Next Steps:")
            print("1. Review generated emails in outreach_campaigns/")
            print("2. Import CSV into your email tool (Mailchimp, SendGrid, Yahoo)")
            print("3. Send first batch (start with 50-100 emails)")
            print("4. Track responses and adjust messaging")
            print("5. Follow up with interested prospects")

        else:
            print("❌ No contact files found in prospecting_data/")
            print("   Run: py public_contact_harvester.py first")
    else:
        print("❌ prospecting_data/ folder not found")
        print("   Run: py public_contact_harvester.py first")
