**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

# Pricing Sheets for Loyverse / POS Setup

Quick reference for adding Mythara products to your POS system.

---

## Products to Add

### 1. SSIP Compliance Audit (One-Time)
- **Name:** Mythara SSIP Compliance Audit
- **SKU:** MYTH-AUDIT-001
- **Price:** $2,500 (Early adopter: $500)
- **Category:** Professional Services
- **Icon:** `assets/glyphs/ssip_audit.svg`
- **Track Inventory:** No (service)
- **Tax:** Exempt (B2B professional service)

### 2. Monthly Subscription
- **Name:** Mythara Engine - Monthly
- **SKU:** MYTH-SUB-MONTH
- **Price:** $500/month (Early adopter: $300/month)
- **Category:** SaaS Subscription
- **Icon:** `assets/glyphs/engine_subscription_monthly.svg`
- **Track Inventory:** No (digital service)
- **Tax:** Exempt

### 3. Annual Subscription
- **Name:** Mythara Engine - Annual
- **SKU:** MYTH-SUB-YEAR
- **Price:** $5,000/year
- **Category:** SaaS Subscription
- **Icon:** `assets/glyphs/engine_subscription_annual.svg`
- **Track Inventory:** No (digital service)
- **Tax:** Exempt

### 4. Enterprise License
- **Name:** Mythara Enterprise License (Annual)
- **SKU:** MYTH-ENT-YEAR
- **Price:** $25,000/year
- **Category:** Enterprise
- **Icon:** `assets/glyphs/enterprise_license.svg`
- **Track Inventory:** No (digital service)
- **Tax:** Exempt

### 5. Custom Clause Development
- **Name:** Custom Clause Development
- **SKU:** MYTH-CUSTOM-001
- **Price:** $10,000 one-time
- **Category:** Custom Development
- **Icon:** `assets/glyphs/custom_clause_dev.svg`
- **Track Inventory:** No (service)
- **Tax:** Exempt

### 6. Training & Onboarding
- **Name:** Mythara Training & Onboarding
- **SKU:** MYTH-TRAIN-001
- **Price:** $1,000 one-time
- **Category:** Training
- **Icon:** `assets/glyphs/training_onboarding.svg`
- **Track Inventory:** No (service)
- **Tax:** Exempt

### 7. VoIP Bot License (Q1 2026)
- **Name:** Mythara VoIP Bot License
- **SKU:** MYTH-VOIP-2026
- **Price:** $1,500,000 one-time
- **Category:** Enterprise Software
- **Icon:** `assets/glyphs/voip_bot_license.svg`
- **Track Inventory:** No (digital license)
- **Tax:** Exempt

---

## Loyverse Import CSV (Optional)

If Loyverse supports CSV import, use this format:

```csv
Name,SKU,Price,Category,Tax,Track Inventory
"Mythara SSIP Compliance Audit",MYTH-AUDIT-001,2500,"Professional Services","Exempt",No
"Mythara Engine - Monthly",MYTH-SUB-MONTH,500,"SaaS Subscription","Exempt",No
"Mythara Engine - Annual",MYTH-SUB-YEAR,5000,"SaaS Subscription","Exempt",No
"Mythara Enterprise License (Annual)",MYTH-ENT-YEAR,25000,"Enterprise","Exempt",No
"Custom Clause Development",MYTH-CUSTOM-001,10000,"Custom Development","Exempt",No
"Mythara Training & Onboarding",MYTH-TRAIN-001,1000,"Training","Exempt",No
"Mythara VoIP Bot License",MYTH-VOIP-2026,1500000,"Enterprise Software","Exempt",No
```

---

## Categories to Create in Loyverse

1. **Professional Services** (for audits)
2. **SaaS Subscription** (for monthly/annual plans)
3. **Enterprise** (for large contracts)
4. **Custom Development** (for clause engineering)
5. **Training** (for onboarding)
6. **Enterprise Software** (for VoIP bot)

---

## Payment Methods to Enable

- ACH/Bank Transfer (preferred for large amounts)
- Cash App ($MytharaEngine)
- Cryptocurrency (BTC, ETH, USDC)
- Invoice (Net 30 for Enterprise)

---

## Discount Codes to Set Up

| Code | Discount | Valid Until | Notes |
|------|----------|-------------|-------|
| EARLY20 | $2,000 off | Nov 15, 2025 | SSIP Audit: $2,500 → $500 |
| PILOT3M | 40% off | Nov 15, 2025 | Monthly: $500 → $300 (first 3 months) |
| VOLUME3 | 10% off | Ongoing | 3+ Annual Subscriptions |
| VOLUME5 | 15% off | Ongoing | 5+ Enterprise Licenses |

---

## Icon Setup Instructions

Icons ship as SVG in `Commercial/assets/glyphs/` (e.g. `ssip_audit.svg`, `engine_subscription_monthly.svg`). The PNG variants at `Commercial/assets/glyphs_png/dark/128/` referenced below are not currently in the repo — export the SVGs to 128×128 PNG before uploading, or upload the SVG directly if Loyverse accepts it.

1. **Icon source:** `Commercial/assets/glyphs/` folder (SVG)
   
2. **In Loyverse:**
   - Go to each product
   - Click "Edit"
   - Upload the icon (exported 128×128 PNG from the SVG, or the SVG itself)
   - Choose the dark variant for POS screens (best for POS screens)

3. **For light mode displays:**
   - Export the SVG to a light variant — the `glyphs_png/light/` PNG set is not in the repo either.

---

## Quick Add Script (Manual Entry)

1. Open Loyverse POS app
2. Go to **Items** → **Add Item**
3. Enter details from list above
4. Upload icon (128×128 PNG from dark/ folder)
5. Save
6. Repeat for all 7 products

**Time estimate:** 10-15 minutes for all products

---

## Notes

- All prices are USD
- All items marked as "services" (no inventory tracking needed)
- Tax-exempt for B2B transactions
- Icons provided in 3 color variants (dark/light/brand) and 4 sizes (32/64/128/256)

---

For questions: Herbievelezjr@gmail.com

