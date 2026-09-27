**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

# DOMAIN + EMAIL SETUP — mytharalabs.com

This guide helps you configure DNS and email for mytharalabs.com after purchasing the domain (Namecheap assumed). It includes ready-to-use DNS templates for popular providers and a short checklist to verify everything.

## What you need
- Access to your domain registrar DNS (Namecheap Dashboard)
- Your chosen email provider (pick ONE):
  - Namecheap Private Email (Starter)
  - Zoho Mail (Lite/Standard — IMAP required for the bot)
  - Fastmail
  - Cloudflare Email Routing + Brevo (forwarding + authenticated outbound)

## Nameservers and DNS strategy

Pick one strategy:
- Keep Namecheap BasicDNS (simple). You can add records directly in Namecheap.
- Or move to Cloudflare (free): change nameservers at Namecheap to the two Cloudflare NS values. Cloudflare gives fast DNS, DDoS protections, and free DNSSEC.

DNSSEC:
- PremiumDNS includes DNSSEC if you stay on Namecheap. Cloudflare provides DNSSEC free. If you keep Namecheap BasicDNS without PremiumDNS, DNSSEC availability may be limited; Cloudflare is the easiest path to enable DNSSEC at no cost.

## Email provider options (pros/cons)
- Namecheap Private Email (Starter)
  - Pros: Simple, integrated billing, IMAP/SMTP supported, reasonably priced.
  - Cons: Fewer advanced admin features than Fastmail/Zoho.
- Zoho Mail (Lite/Standard)
  - Pros: Business suite, good deliverability, IMAP supported on paid tiers; often supports PayPal.
  - Cons: Free plan may restrict IMAP/POP (avoid free if bot needs IMAP).
- Fastmail
  - Pros: Excellent deliverability, powerful admin, IMAP/SMTP solid.
  - Cons: More expensive than the others.
- Cloudflare Email Routing + Brevo (Send-only)
  - Pros: $0 routing (forwards to an existing inbox), Brevo free tier can send; great for lightweight setups.
  - Cons: More pieces to manage; forwarding inbox is read-only unless you set up an SMTP sender (Brevo); IMAP remains wherever you forward to.

## DNS templates by provider
Replace <...> placeholders with provider-issued values. Priority numbers (10/20/50) are typical; keep what the provider instructs if different.

### Namecheap Private Email
- MX records
  - Name: @
  - Type: MX
  - Values:
    - mx1.privateemail.com (Priority 10)
    - mx2.privateemail.com (Priority 20)
- SPF (TXT)
  - Name: @
  - Value: v=spf1 include:spf.privateemail.com ~all
- DKIM (TXT)
  - Name: default._domainkey
  - Value: <paste DKIM value from Private Email control panel>
- DMARC (TXT)
  - Name: _dmarc
  - Value: v=DMARC1; p=none; rua=mailto:dmarc@mytharalabs.com; sp=none; fo=1

IMAP/SMTP
- IMAP: mail.privateemail.com, Port 993, SSL/TLS
- SMTP: mail.privateemail.com, Port 465, SSL/TLS

### Zoho Mail (Lite/Standard)
- MX records
  - Name: @
  - Values:
    - mx.zoho.com (Priority 10)
    - mx2.zoho.com (Priority 20)
    - mx3.zoho.com (Priority 50)
- SPF (TXT)
  - Name: @
  - Value: v=spf1 include:zoho.com ~all
- DKIM (TXT)
  - Name: <selector>._domainkey
  - Value: <paste DKIM value from Zoho Admin>
- DMARC (TXT)
  - Name: _dmarc
  - Value: v=DMARC1; p=none; rua=mailto:dmarc@mytharalabs.com; sp=none; fo=1

IMAP/SMTP
- IMAP: imap.zoho.com, Port 993, SSL/TLS
- SMTP: smtp.zoho.com, Port 465, SSL/TLS

### Fastmail
- MX records
  - Name: @
  - Values:
    - in1-smtp.messagingengine.com (Priority 10)
    - in2-smtp.messagingengine.com (Priority 20)
- SPF (TXT)
  - Name: @
  - Value: v=spf1 include:spf.messagingengine.com ~all
- DKIM (TXT)
  - Name: fm1._domainkey
  - Value: <paste DKIM value from Fastmail>
- DMARC (TXT)
  - Name: _dmarc
  - Value: v=DMARC1; p=none; rua=mailto:dmarc@mytharalabs.com; sp=none; fo=1

IMAP/SMTP
- IMAP: imap.fastmail.com, Port 993, SSL/TLS
- SMTP: smtp.fastmail.com, Port 465, SSL/TLS

### Cloudflare Email Routing + Brevo (optional path)
1) In Cloudflare, enable Email Routing for mytharalabs.com and create a route:
   - Alias: contact@mytharalabs.com → Destination: <your existing inbox>
   - Cloudflare will propose MX and TXT records; approve/apply.
2) Outbound via Brevo (to send as @mytharalabs.com):
   - Add domain in Brevo, follow wizard to add:
     - SPF (TXT): v=spf1 include:spf.brevo.com ~all
     - DKIM (CNAME): <selector>._domainkey → <selector>-domainkey.brevo.com
     - Optional bounce domain CNAME as instructed.

IMAP/SMTP
- IMAP remains wherever you forward to (e.g., your personal inbox). For SMTP, use Brevo SMTP if you want to send as @mytharalabs.com.

## Verification checklist
- MX records resolve and match the provider
- SPF TXT present and passes: check with https://dmarcian.com/spf-survey/
- DKIM selector published and passing: send a test email to a Gmail inbox and view original headers (dkim=pass)
- DMARC policy present (start with p=none; switch to p=quarantine or p=reject after you monitor reports)
- Send & receive tests:
  - From @mytharalabs.com → external inbox (Gmail/Outlook) — check inbox/spam
  - From external inbox → @mytharalabs.com — confirm delivery

## Bot configuration (IMAP/SMTP)
Update your bot’s environment/config to point at the chosen provider’s IMAP/SMTP hosts above. If 2FA is enabled, create an app-specific password (Zoho/Fastmail/Namecheap Private Email support this) and use it for IMAP/SMTP.

- Recommended mailbox: founder@mytharalabs.com or hello@mytharalabs.com
- Recommended aliases: sales@, support@ → deliver to the primary mailbox

## Notes
- Start DMARC with p=none to collect reports safely. After at least 1–2 weeks of monitoring, consider p=quarantine or p=reject for spoofing protection.
- If you later host a website, add an A/AAAA or CNAME record and enable HTTPS (Cloudflare proxy or Let’s Encrypt).