**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

# Invoice Template — Mythara Engine

Use this template when a deal closes. Send as PDF or Word doc.

---

## Standard Invoice (Copy-Paste)

```
INVOICE

From:
Herbert Velez Jr.
Mythara Engine
Mythara.Engine@yahoo.com
[Your Address]
[City, State ZIP]

To:
[Customer Company Name]
[Customer Contact Name]
[Customer Address]
[City, State ZIP]

Invoice Number: INV-[YYYYMMDD]-001
Invoice Date: [Date]
Due Date: Net 15 (or Net 30 for enterprise)

---

DESCRIPTION                                    AMOUNT
─────────────────────────────────────────────────────
Mythara Engine Development License             $2,500.00
30-day evaluation with full source access
Includes: SSIP runtime, API implementation,
validation suite, documentation, commercial
use rights (non-exclusive)

OR

Mythara Engine Early Adopter License           $500.00
30-day evaluation with full source access
Limited-time pricing for pilot adopters

---

Subtotal:                                      $2,500.00
Tax:                                           $0.00 (software exempt in most states)
TOTAL DUE:                                     $2,500.00

---

PAYMENT INSTRUCTIONS:

ACH/Wire Transfer (preferred):
  [Your Bank Name]
  Account Name: Herbert Velez Jr.
  Routing: [Your Routing Number]
  Account: [Your Account Number]

Check (if needed):
  Payable to: Herbert Velez Jr.
  Mail to: [Your Address]

Zelle/Venmo (for small amounts):
  Zelle: Mythara.Engine@yahoo.com
  Venmo: @[YourHandle] (if applicable)

PayPal (add 3% processing fee):
  PayPal.me/[YourLink]

---

TERMS:
- Payment due within 15 days of invoice date (Net 15)
- Late payments subject to 1.5% monthly interest
- W-9 available upon request
- Questions? Email Mythara.Engine@yahoo.com

Thank you for your business!

Herbert Velez Jr.
Mythara Engine
```

---

## W-9 Instructions

When a customer asks for a W-9 (they will for accounts payable):

1. **Download blank W-9** from IRS.gov: https://www.irs.gov/pub/irs-pdf/fw9.pdf
2. **Fill it out:**
   - **Name:** Herbert Velez Jr.
   - **Business name:** Leave blank (or write "Mythara Engine — Sole Proprietorship")
   - **Tax classification:** Check "Individual/sole proprietor"
   - **Address:** Your home address
   - **SSN:** Your Social Security Number (Part I, box 2)
   - **Sign and date**
3. **Save as PDF:** `W9_Herbert_Velez_Jr_2025.pdf`
4. **Send to customer** (usually AP team or procurement)

**Security note:** Only send W-9 to verified customers who are paying you. Never post publicly.

---

## Payment Methods Ranked (Fastest to Slowest)

| Method | Speed | Fees | Best For |
|---|---|---|---|
| Zelle | Same day | $0 | Small deals ($500–$2,500) |
| ACH/Wire | 1–3 days | $0–$25 | Enterprise ($2,500+) |
| Check | 5–10 days | $0 | Old-school companies |
| PayPal | Same day | 3% | Last resort |
| Credit card (Stripe) | 2–3 days | 2.9% + $0.30 | If you set up Stripe (optional) |

**Recommendation for now:**
- **$500–$2,500:** Accept Zelle or ACH (no fees, fast)
- **$2,500+:** ACH or wire only (more professional)
- Avoid PayPal unless customer insists (3% hurts margins)

---

## Invoice Numbering System

Format: `INV-[YYYYMMDD]-[Sequential Number]`

Examples:
- First invoice: `INV-20251104-001`
- Second invoice (same day): `INV-20251104-002`
- Next day: `INV-20251105-001`

Keep a simple tracking sheet:

| Invoice # | Date | Customer | Amount | Status | Paid Date |
|---|---|---|---|---|---|
| INV-20251104-001 | 11/4/25 | Sample Client | $2,500 | SAMPLE | |
| INV-20251104-002 | 11/4/25 | Sample Client | $500 | SAMPLE | |

---

## What to Do When Customer Says "We Need a Contract"

Some customers (especially enterprise) will say: "We need a licensing agreement before we can pay."

**Fast response (copy-paste):**

> "Absolutely — I can send you our standard Development License Agreement. It covers:
> - Non-exclusive commercial use rights
> - 30-day evaluation period
> - Source code access (private GitHub repo invite)
> - Support via email
> - No liability for pilot/eval use
> 
> I can send it as a PDF or Word doc — whichever your legal team prefers. (No customers yet — this is the playbook for when the first one arrives.)
> 
> Would you like me to send that over now?"

**Then use a standard licensing agreement.** The repo does not currently ship a development-license template (`Licensee_Packet/` has only the invitation email and access README) — draft one or use a vetted template before a customer asks. A starting point for the agreement's content:

---

## When Customer Asks "Do You Have a Business Bank Account?"

**Honest answer (for now):**

> "I'm operating as a sole proprietor right now, so payments go to my personal account under Herbert Velez Jr. I can accept ACH, wire, Zelle, or check — whichever works best for your AP team.
> 
> Once we close a few more deals, I'll be forming an LLC and opening a business account. But for your procurement team, the W-9 and invoice with my SSN is totally standard for sole proprietor software licensing."

**Most B2B customers don't care** — they pay freelancers and consultants (sole props) all the time. The W-9 makes it legitimate.

---

## When to Form the LLC

Wait until you hit **$25k–$50k in revenue** (10–20 deals), then:

1. **File LLC in Colorado:** $50 online at sos.state.co.us
2. **Get EIN from IRS:** Free at irs.gov (takes 5 minutes)
3. **Open business bank account:** Chase, BoA, or local credit union
4. **Update invoices/W-9** to use LLC name and EIN instead of SSN

Until then, **sole proprietorship is fine and saves you $500–$1,000** in setup costs.

---

## Quick Checklist for First Deal

- [ ] Customer says "yes, let's do it"
- [ ] Send invoice (use template above)
- [ ] Send W-9 if they request it
- [ ] Send licensing agreement if they request it (or just say "invoice = agreement" for $500–$2,500 deals)
- [ ] Give them private GitHub repo access once payment clears
- [ ] Send welcome email with INSTALL.md and quickstart
- [ ] Log payment in tracking spreadsheet
- [ ] Celebrate 🎉 (you just closed your first commercial software deal)

---

## Example Email When Sending Invoice

**Subject:** Mythara Engine — Invoice and next steps

---

Hi [First Name],

Thanks for moving forward with Mythara! Attached is your invoice for the 30-day Development License.

**Invoice:** INV-20251104-001  
**Amount:** $2,500 (or $500 for early adopter)  
**Payment:** ACH preferred (details on invoice), or Zelle/check  
**Due:** Net 15 (by [Date])  

**Next steps:**
1. Process payment via ACH or Zelle
2. I'll send your private GitHub repo invite within 24 hours of payment clearing
3. Setup guide walks you through installation (10 minutes)

**W-9:** Attached (if you need it for AP)

Let me know if your team has any questions — happy to jump on a call to help with setup.

Looking forward to working together!

— Herbert Velez Jr.  
Mythara.Engine@yahoo.com

---

**You're ready to invoice. Now go close deals.**
