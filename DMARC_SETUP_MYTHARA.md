# DMARC Compliance Setup for mythara.io

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## Current Status (as of Nov 18, 2025)

✅ **Domain**: mythara.io (active on Hostinger)
✅ **MX Records**: mx1.hostinger.com, mx2.hostinger.com
✅ **SPF**: `v=spf1 include:_spf.mail.hostinger.com ~all`
⚠️ **DMARC**: `v=DMARC1; p=none` (monitoring only, needs improvement)
❌ **SendGrid**: Not included in SPF yet

---

## Step 1: Update SPF Record (Add SendGrid)

**Current SPF:**
```
v=spf1 include:_spf.mail.hostinger.com ~all
```

**New SPF (include SendGrid):**
```
v=spf1 include:_spf.mail.hostinger.com include:sendgrid.net ~all
```

**Where to update:**
1. Log into Hostinger
2. Go to: Domains → mythara.io → DNS Zone Editor
3. Find the TXT record with SPF (starts with `v=spf1`)
4. Edit it to add `include:sendgrid.net`
5. Save

---

## Step 2: Add SendGrid DKIM Records

**Get your DKIM keys from SendGrid:**
1. Log into SendGrid dashboard: https://app.sendgrid.com/
2. Go to: Settings → Sender Authentication → Authenticate Your Domain
3. Select "mythara.io" as your domain
4. SendGrid will give you 3 CNAME records like:

```
Host: s1._domainkey.mythara.io
Points to: s1.domainkey.u12345678.wl123.sendgrid.net

Host: s2._domainkey.mythara.io
Points to: s2.domainkey.u12345678.wl123.sendgrid.net

Host: em1234.mythara.io
Points to: u12345678.wl123.sendgrid.net
```

**Add these to Hostinger DNS:**
1. In Hostinger DNS Zone Editor
2. Click "Add Record"
3. Type: CNAME
4. Add all 3 records exactly as SendGrid provides
5. Save and wait 24-48 hours for propagation

---

## Step 3: Upgrade DMARC Policy (Full Compliance)

**Current DMARC:**
```
v=DMARC1; p=none
```

**Phase 1 - Monitoring (start here):**
```
v=DMARC1; p=none; rua=mailto:dmarc@mythara.io; ruf=mailto:dmarc@mythara.io; pct=100; adkim=r; aspf=r; fo=1
```

**Phase 2 - Quarantine (after 2 weeks of clean reports):**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@mythara.io; ruf=mailto:dmarc@mythara.io; pct=10; adkim=r; aspf=r; fo=1
```

**Phase 3 - Reject (full protection):**
```
v=DMARC1; p=reject; rua=mailto:dmarc@mythara.io; ruf=mailto:dmarc@mythara.io; pct=100; adkim=s; aspf=s; fo=1
```

**What each tag means:**
- `p=none` = Monitor only (no blocking)
- `p=quarantine` = Send suspicious emails to spam
- `p=reject` = Block unauthorized emails completely
- `rua` = Aggregate reports sent here
- `ruf` = Forensic (detailed) reports sent here
- `pct` = Percentage of emails to apply policy to
- `adkim=r/s` = DKIM alignment (relaxed/strict)
- `aspf=r/s` = SPF alignment (relaxed/strict)
- `fo=1` = Generate failure report if either SPF or DKIM fails

**Where to update:**
1. In Hostinger DNS Zone Editor
2. Find the TXT record: `_dmarc.mythara.io`
3. Replace with Phase 1 policy above
4. Save

---

## Step 4: Set up DMARC Report Inbox

**Option A - Use existing email:**
Create `dmarc@mythara.io` in Hostinger email:
1. Log into Hostinger
2. Go to: Email → Add Email Account
3. Create: dmarc@mythara.io
4. Forward to: mythara@mythara.io or herbievelezjr@gmail.com

**Option B - Use free DMARC monitoring service:**
- **Valimail Monitor** (free): https://www.valimail.com/
- **Postmark DMARC Digests** (free): https://dmarc.postmarkapp.com/
- **DMARC Analyzer** (free tier): https://www.dmarcanalyzer.com/

These services will:
- Parse DMARC reports automatically
- Show you who's sending emails
- Alert on unauthorized senders
- Give compliance score

---

## Step 5: Verify Everything

**Test your setup:**

```powershell
# Check SPF
nslookup -type=TXT mythara.io

# Check DMARC
nslookup -type=TXT _dmarc.mythara.io

# Check DKIM (after SendGrid setup)
nslookup -type=CNAME s1._domainkey.mythara.io
nslookup -type=CNAME s2._domainkey.mythara.io
```

**Online tools:**
- MXToolbox: https://mxtoolbox.com/SuperTool.aspx?action=dmarc%3amythara.io
- DMARC Check: https://dmarcian.com/dmarc-inspector/
- Mail Tester: https://www.mail-tester.com/ (send test email)

---

## Timeline for Full Compliance

### Week 1: Setup
- ✅ Update SPF to include SendGrid
- ✅ Add SendGrid DKIM records
- ✅ Set DMARC to `p=none` with reporting
- ✅ Set up dmarc@mythara.io inbox

### Week 2-3: Monitor
- Check DMARC reports daily
- Verify all legitimate emails pass SPF+DKIM
- Identify any unauthorized senders

### Week 4: Quarantine
- Change DMARC policy to `p=quarantine; pct=10`
- Monitor for false positives
- Gradually increase pct to 100

### Week 6-8: Reject (Full Compliance)
- Change DMARC policy to `p=reject`
- Set alignment to strict (`adkim=s; aspf=s`)
- Monitor reports for 2 weeks
- **You're now DMARC compliant!**

---

## Quick Reference: DNS Records Needed

**Add to Hostinger DNS for mythara.io:**

| Type | Host | Value | TTL |
|------|------|-------|-----|
| TXT | @ | `v=spf1 include:_spf.mail.hostinger.com include:sendgrid.net ~all` | 3600 |
| TXT | _dmarc | `v=DMARC1; p=none; rua=mailto:dmarc@mythara.io; ruf=mailto:dmarc@mythara.io; pct=100; adkim=r; aspf=r; fo=1` | 3600 |
| CNAME | s1._domainkey | (get from SendGrid) | 3600 |
| CNAME | s2._domainkey | (get from SendGrid) | 3600 |
| CNAME | em#### | (get from SendGrid) | 3600 |

---

## Hostinger Login Info

**Where to log in:**
- URL: https://hpanel.hostinger.com/
- Or: https://www.hostinger.com/ → Login

**What you'll need:**
- Your Hostinger account email
- Hostinger password

**Once logged in:**
1. Click "Domains" in left sidebar
2. Click "mythara.io"
3. Click "DNS / Name Servers"
4. Click "DNS Zone Editor"
5. Add/edit records as shown above

---

## Current Email Bot Integration

Your email bot already uses:
- **Yahoo Mail (IMAP)**: mythara.engine@yahoo.com (for receiving)
- **SendGrid (SMTP)**: For sending (API key in .env)

**After DMARC setup:**
- Yahoo emails will continue working (separate domain)
- SendGrid emails from @mythara.io will be authenticated
- Recipients will see mythara.io as verified sender

---

## Support Resources

**If you get stuck:**
1. Hostinger Support: https://www.hostinger.com/contact
2. SendGrid Docs: https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication
3. DMARC Guide: https://dmarc.org/overview/
4. This repo's issue tracker: https://github.com/herbievelezjr/Mythara_Archive/issues

---

## Next Steps

1. **Now**: Log into Hostinger and update SPF (5 minutes)
2. **Now**: Set up SendGrid domain authentication (10 minutes)
3. **Today**: Update DMARC to Phase 1 (monitoring)
4. **This week**: Create dmarc@mythara.io inbox
5. **Next 2 weeks**: Monitor DMARC reports
6. **Month 2**: Move to quarantine/reject policies

---

**Questions? Run these commands to check current status:**

```powershell
# Full DNS check
nslookup -type=ANY mythara.io

# Email authentication check
nslookup -type=TXT mythara.io
nslookup -type=TXT _dmarc.mythara.io
nslookup -type=MX mythara.io
```
