# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Email Campaign Generator - Mythara Products
Generates personalized sales emails for different customer types.
"""

import os
from datetime import datetime

class EmailCampaignGenerator:
    """Generates sales emails for Mythara products."""
    
    def __init__(self):
        self.sender_email = "Mythara.Engine@yahoo.com"
        self.sender_name = "Herbert Velez Jr."
        self.company = "Mythara Engine"
        
    def generate_cold_email_ssip_audit(self, prospect_name: str, company_name: str, industry: str) -> dict:
        """Generate cold email for SSIP Audit (early adopter $500)."""
        
        subject = f"AI Compliance Audit - {company_name} ({industry})"
        
        body = f"""Hi {prospect_name},

I noticed {company_name} is working with AI models in {industry}. With regulations tightening (EU AI Act, NIST AI RMF), compliance audits are becoming mandatory.

**What if you could prove your AI is trustworthy - cryptographically?**

We're offering our Symbolic Safety Integrity Protocol (SSIP) Compliance Readiness Assessment:

✅ Cryptographic proof of AI model integrity
✅ Readiness assessment report for regulators
✅ Hash chain audit trail
✅ 5-day turnaround

**Early Adopter Pricing**: $500
A straightforward flat price for early users — no gimmicks.

Perfect for {industry} companies facing:
- Regulatory scrutiny (OCC, CFPB, FDA, FTC)
- Customer trust issues
- Insurance/liability requirements

**Ready to secure your AI compliance?**

Reply to this email or pay directly:
🔗 PayPal Invoice: [I'll send custom invoice]
💬 Quick call: Herbievelezjr@gmail.com

Best,
{self.sender_name}
Founder, Mythara Engine
Mythara.Engine@yahoo.com
"""
        
        return {
            "to": f"{prospect_name} <email@{company_name.lower().replace(' ', '')}.com>",
            "subject": subject,
            "body": body,
            "product": "MYTH-AUDIT-001",
            "price": "$500",
            "urgency": "none (no fake deadline)"
        }
    
    def generate_cold_email_monthly_sub(self, prospect_name: str, company_name: str, industry: str) -> dict:
        """Generate cold email for Monthly Subscription ($300/mo early adopter)."""
        
        subject = f"Unlimited AI Audits for {company_name} - $300/mo"
        
        body = f"""Hi {prospect_name},

If {company_name} is deploying multiple AI models, manual audits get expensive fast.

**What if you could validate UNLIMITED models for one flat monthly fee?**

Mythara Engine Monthly Subscription:
✅ Unlimited AI model validations
✅ Real-time API access
✅ 24-hour support
✅ Readiness assessment reports included

**Early Adopter**: $300/month
A flat early-user rate for unlimited validations.

Perfect for {industry} teams:
- Running A/B tests on AI models
- Continuous deployment pipelines
- Scaling AI across departments

**Start validating today:**

Reply with "YES" and I'll send the PayPal subscription link.
Or pay directly: Mythara.Engine@yahoo.com

First month starts immediately. Cancel anytime.

Best,
{self.sender_name}
Mythara Engine
Mythara.Engine@yahoo.com
"""
        
        return {
            "to": f"{prospect_name} <email@{company_name.lower().replace(' ', '')}.com>",
            "subject": subject,
            "body": body,
            "product": "MYTH-SUB-MONTH",
            "price": "$300/month",
            "urgency": "none (early-adopter rate)"
        }
    
    def generate_cold_email_enterprise(self, prospect_name: str, company_name: str, industry: str) -> dict:
        """Generate cold email for Enterprise License ($25k/year)."""
        
        subject = f"Enterprise AI Compliance Platform - {company_name}"
        
        body = f"""Hi {prospect_name},

{company_name} is scaling AI across {industry}. That means compliance complexity is growing exponentially.

**What if your entire AI infrastructure was auditable - on-premise?**

Mythara Enterprise License ($25k/year):
✅ Full platform deployment (on-premise or cloud)
✅ Unlimited custom clauses for your domain
✅ Dedicated account manager
✅ Priority SLA (1-hour response)
✅ White-glove onboarding

Built for {industry} enterprises with:
- 50+ AI models in production
- Strict data residency requirements
- Regulatory reporting obligations

**Let's discuss your compliance architecture:**

📞 Book 30-min call: [Reply with your availability]
📧 Email questions: Herbievelezjr@gmail.com
💳 Ready to start: I'll send enterprise contract

**Volume discount available**: 5+ licenses get 15% off + free custom clause ($10k value)

Best,
{self.sender_name}
Founder, Mythara Engine
Mythara.Engine@yahoo.com

P.S. NDA available upon request.
"""
        
        return {
            "to": f"{prospect_name} <email@{company_name.lower().replace(' ', '')}.com>",
            "subject": subject,
            "body": body,
            "product": "MYTH-ENT-YEAR",
            "price": "$25,000/year",
            "urgency": "Volume discounts available"
        }
    
    def generate_email_list(self) -> list:
        """Generate list of target prospects with personalized emails."""
        
        prospects = [
            # Banking / Finance
            {"name": "Chief Risk Officer", "company": "Regional Bank", "industry": "Banking"},
            {"name": "Compliance Director", "company": "Credit Union", "industry": "Finance"},
            {"name": "AI Lead", "company": "FinTech Startup", "industry": "Finance"},
            
            # Healthcare
            {"name": "CISO", "company": "Hospital System", "industry": "Healthcare"},
            {"name": "CTO", "company": "HealthTech Company", "industry": "Healthcare"},
            
            # Tech Companies
            {"name": "Head of AI", "company": "SaaS Company", "industry": "Technology"},
            {"name": "ML Engineer", "company": "Tech Startup", "industry": "Technology"},
            
            # Government / Defense
            {"name": "Program Manager", "company": "Defense Contractor", "industry": "Defense"},
            
            # Insurance
            {"name": "Underwriting Director", "company": "Insurance Company", "industry": "Insurance"},
        ]
        
        emails = []
        
        for prospect in prospects:
            # Choose product based on industry
            if prospect["industry"] in ["Banking", "Finance"]:
                email = self.generate_cold_email_ssip_audit(
                    prospect["name"], 
                    prospect["company"], 
                    prospect["industry"]
                )
            elif prospect["industry"] in ["Healthcare", "Defense"]:
                email = self.generate_cold_email_enterprise(
                    prospect["name"], 
                    prospect["company"], 
                    prospect["industry"]
                )
            else:
                email = self.generate_cold_email_monthly_sub(
                    prospect["name"], 
                    prospect["company"], 
                    prospect["industry"]
                )
            
            emails.append(email)
        
        return emails
    
    def save_campaign(self, emails: list, campaign_name: str):
        """Save email campaign to file."""
        
        filename = f"email_campaign_{campaign_name}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Mythara Email Campaign: {campaign_name}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total Emails: {len(emails)}\n")
            f.write("="*80 + "\n\n")
            
            for i, email in enumerate(emails, 1):
                f.write(f"EMAIL #{i}\n")
                f.write("-"*80 + "\n")
                f.write(f"To: {email['to']}\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"Product: {email['product']} ({email['price']})\n")
                f.write(f"Urgency: {email['urgency']}\n")
                f.write("\n" + email['body'] + "\n")
                f.write("="*80 + "\n\n")
        
        print(f"✅ Campaign saved: {filename}")
        print(f"📧 {len(emails)} emails ready to send")
        return filename


def main():
    """Generate and save email campaign."""
    
    generator = EmailCampaignGenerator()
    
    print("🚀 Generating Mythara Sales Email Campaign...")
    print("")
    
    emails = generator.generate_email_list()
    
    print(f"📧 Generated {len(emails)} personalized emails")
    print("")
    
    # Save campaign
    filename = generator.save_campaign(emails, "cold_outreach_nov2025")
    
    print("")
    print("📋 NEXT STEPS:")
    print("")
    print("1. Open file:", filename)
    print("2. Copy email content")
    print("3. Send via your Mythara.Engine@yahoo.com email")
    print("4. Replace placeholder emails with real prospect addresses")
    print("5. Send PayPal invoices when they reply 'YES'")
    print("")
    print("💡 TIP: Send 10 emails/day to avoid spam filters")
    print("💡 TIP: Personalize the first line for each prospect")
    print("💡 TIP: Follow up after 3 days if no response")
    print("")
    print("🎯 Planning benchmarks (typical cold-email ranges, not promises):")
    print("   - Reply rate: ~5-10% (roughly 0-1 replies per 10 emails)")
    print("   - Close rate: ~20-30% of replies — track actuals and adjust")
    print("")


if __name__ == "__main__":
    main()
