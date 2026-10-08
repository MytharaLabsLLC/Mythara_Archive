# How to Make Tutorial Videos for Mythara Engine

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

> **⚠️ SCRIPT DRAFTS (November 2025) — voice-standard pass Sept 2026.** The scripts below describe a pilot signup flow that **no longer exists** (all Stripe webhooks were deleted; there is no $49 pilot, no live payment path, no hosted service to demo). **Do not record, share, or publish these scripts without rewriting them.** Corrected claims are noted inline.

---

## Quick Start: Free Tools You Already Have

### Option 1: Windows Built-in (Easiest)
**Xbox Game Bar** - Already on your Windows PC

1. **Start recording:**
   - Press `Windows + G` (opens Xbox Game Bar)
   - Click the **Record** button (circle icon)
   - Or press `Windows + Alt + R` to start/stop

2. **What it records:**
   - Your screen + microphone
   - Saves to: `C:\Users\YourName\Videos\Captures`
   - Format: MP4 (ready to upload)

3. **Tips:**
   - Close unnecessary windows first
   - Speak clearly into your mic
   - Show your Railway dashboard or pricing page

---

## Option 2: OBS Studio (Professional, Free)

**Download:** https://obsproject.com/

### Why OBS?
- Better quality
- More control (can hide sensitive info)
- Can record specific windows only
- Add overlays, transitions

### Quick Setup (5 minutes):

1. **Install OBS Studio**
   - Download from obsproject.com
   - Install with default settings

2. **First Recording Setup:**
   ```
   1. Open OBS
   2. Click "+" under "Sources"
   3. Choose "Display Capture" (whole screen)
      OR "Window Capture" (just browser)
   4. Click "Start Recording"
   5. Do your tutorial
   6. Click "Stop Recording"
   ```

3. **Videos save to:**
   - Default: `C:\Users\YourName\Videos`
   - Change in: Settings → Output → Recording Path

### OBS Settings for Mythara Tutorials:

```
Settings → Output:
- Recording Quality: High Quality, Medium File Size
- Recording Format: MP4
- Encoder: x264

Settings → Video:
- Base Resolution: 1920x1080
- Output Resolution: 1920x1080
- FPS: 30

Settings → Audio:
- Desktop Audio: Default
- Mic/Auxiliary Audio: Your microphone
```

---

## Tutorial Scripts (What to Say)

### Video 1: "What is Mythara? (2 min)"

**Show:** mytharaarchive-production.up.railway.app

**Script:**
```
"Hi, I'm Herbert from Mythara. Let me show you what we do.

[Open pricing page]

Mythara holds the space when your mission conflicts with compliance. 

[Scroll to Soul Cradle section]

Say you're a hospital social worker. Policy says discharge this patient. 
Your heart says they'll be homeless. Both are true.

[Click chat bubble]

Soul Cradle documents that paradox. Measures the cost to your soul 
and the mission. Creates an immutable record.

[Show pricing tiers]

We donate Soul Cradle to healthcare, banking, justice, nonprofits, 
civil service, education—the industries carrying impossible weight.

[Pause on Pilot tier]

Try it: $49 for 7 days. Full access. See if it fits your reality.

Questions? Email Mythara.Engine@yahoo.com"
```

**Length:** ~90 seconds  
**File name:** `01_what_is_mythara.mp4`

---

### Video 2: "How to Start Your Pilot (3 min)"

**Show:** Pilot signup process

**Script:**
```
"Let me show you how to start your Mythara Pilot.

[Open pricing page]

Scroll down to the Pilot tier. $49 for 7 days, full access.

[Scroll to Pilot section]

Check the Terms box. Click Subscribe.

[Click Subscribe button - BLUR the Stripe payment page]

You'll enter your payment info here. Takes 2 minutes.

[After payment - show confirmation]

That's it. You're in. Full access to Mythara for 7 days.

[Show the main dashboard/interface if available]

Most people know by day three if it's the right fit.

And if you upgrade to Enterprise? That $49 gets credited back.

So you're really just testing it with our money.

Questions? Email Mythara.Engine@yahoo.com"
```

**Length:** ~2 minutes  
**File name:** `02_pilot_signup.mp4`

---

### Video 3: "Soul Cradle Explained (4 min)"

**Show:** Soul Cradle documentation example

**Script:**
```
"Let's talk about Soul Cradle.

[Show example scenario on screen - text overlay or whiteboard]

Hospital social worker. Patient needs care. Policy says discharge. 
Heart says keep them safe.

[Show Soul Cradle interface if available, or explain conceptually]

Soul Cradle documents:
- What policy said
- What your heart said  
- What you actually did
- The emotional weight of that choice

[Show cryptographic hash example or explain]

We generate a cryptographic hash. Timestamp it. The result is tamper-evident: if anyone alters the record, the chain shows it. *(The chain proves a record is unaltered — it does not prove the record is true, and nothing here is immutable.)*

[Show aggregate view - or describe]

Leadership sees the pattern across your org. They spot burnout 
before people break.

[Show audit trail or describe]

Tamper-evident. Human-readable. *(Do not claim "audit-ready" or "court-ready" — legal admissibility and audit acceptance are aspirations, not current claims.)*

We donate Soul Cradle to the industries that need it most:
Healthcare, banking, justice, nonprofits, civil service, education.

It's included in every tier. No charge. *(Aspiration: the planned free tier for qualifying organizations has not launched.)*

Because some things shouldn't have a price.

Questions? Email Mythara.Engine@yahoo.com"
```

**Length:** ~3 minutes  
**File name:** `03_soul_cradle_explained.mp4`

---

## Quick Recording Workflow

### Before Recording:
1. **Clean your desktop**
   - Close unnecessary tabs/windows
   - Hide personal info
   - Set browser to fullscreen (F11)

2. **Prepare your script**
   - Print it or have it on another screen
   - Practice once without recording

3. **Check audio**
   - Test microphone (say "test test test")
   - Eliminate background noise
   - Speak clearly, not too fast

### During Recording:
1. **Take your time**
   - Pause between sections
   - You can edit out mistakes later

2. **Show clearly**
   - Move mouse slowly
   - Highlight important parts
   - Zoom in if needed (Windows + "+" key)

3. **Speak naturally**
   - Imagine explaining to a friend
   - Energy matters—sound interested!

### After Recording:
1. **Review the video**
   - Watch it once
   - Note any major mistakes
   - Decide if you need to re-record

2. **Basic editing (if needed)**
   - Windows Photos app can trim videos
   - Or use Clipchamp (free, built into Windows 11)
   - Cut out long pauses or mistakes

---

## Where to Host Videos

### Option 1: YouTube (Recommended)
**Why:** Free, unlimited storage, easy embedding

1. **Upload:**
   - Go to YouTube.com → Your Channel
   - Click "Create" → "Upload Video"
   - Drag your MP4 file

2. **Settings:**
   - Title: "What is Mythara Engine?"
   - Visibility: **Unlisted** (so only people with link can see)
   - Description: Add link to mytharaarchive-production.up.railway.app

3. **Get embed code:**
   - Click "Share" → "Embed"
   - Copy the `<iframe>` code
   - Add to your pricing.html

### Option 2: Vimeo
**Why:** More professional, no ads, better privacy

- Free tier: 5GB storage per week
- Same process as YouTube
- Cleaner player, better branding

### Option 3: Self-hosted (Railway)
**Why:** Full control, your domain

**Not recommended** unless you have:
- Video compression knowledge
- CDN setup (videos are HUGE)
- Bandwidth budget

---

## Tutorial Series Outline

**Total: 6 videos, ~15 minutes**

### Core Videos (Must-have):
1. ✅ What is Mythara? (2 min)
2. ✅ How to Start Your Pilot (3 min)
3. ✅ Soul Cradle Explained (4 min)

### Advanced Videos (Nice-to-have):
4. ⚡ Enterprise Features Overview (3 min)
5. ⚡ API Integration Basics (3 min)
6. ⚡ HIPAA & Security Deep Dive (4 min) *(script must frame honestly — no HIPAA certification exists; cover the tamper-evident record design, not compliance claims)*

---

## Production Timeline

### Week 1: Core Videos
- **Day 1:** Record Video 1 (What is Mythara)
- **Day 2:** Record Video 2 (Pilot Signup)
- **Day 3:** Record Video 3 (Soul Cradle)
- **Day 4:** Review, re-record if needed
- **Day 5:** Upload to YouTube/Vimeo

### Week 2: Integration
- **Day 1:** Add video embeds to pricing.html
- **Day 2:** Update chatbot responses to mention videos
- **Day 3:** Test on Railway
- **Day 4:** Share with first pilot customers

---

## Equipment You Need

### Minimum (You have this):
- ✅ Windows PC with mic
- ✅ Browser (Chrome/Edge)
- ✅ Xbox Game Bar (built-in)

### Better (Optional):
- 🎤 USB Microphone ($30-50) - Blue Snowball, Fifine
- 🎧 Headphones (to hear yourself clearly)
- 💡 Good lighting (sit facing a window)

### Not needed:
- ❌ Camera (screen recording only)
- ❌ Professional editing software
- ❌ Green screen
- ❌ Fancy setup

---

## Quick Start Command

**Right now, record your first video:**

```powershell
# 1. Open Xbox Game Bar
# Press Windows + G

# 2. Click Record button (circle icon)

# 3. Open your Railway app
Start-Process "https://mytharaarchive-production.up.railway.app"

# 4. Talk through what Mythara does (2 minutes)

# 5. Press Windows + Alt + R to stop

# 6. Find your video
explorer.exe "$env:USERPROFILE\Videos\Captures"
```

Your first tutorial is done!

---

## Tips from Successful Tutorial Creators

1. **Keep it SHORT** - 2-3 minutes max
2. **One topic per video** - Don't try to cover everything
3. **Show, don't just tell** - Click things, demonstrate
4. **Energy matters** - Sound like you care
5. **Imperfect is better than nothing** - Ship it!

---

## Editing (If You Want)

### Free Tools:

**Clipchamp (Windows 11):**
- Built into Windows 11
- Drag/drop editing
- Trim, cut, add text overlays
- Export to MP4

**DaVinci Resolve (Advanced):**
- Professional editor, free version
- Overkill for simple tutorials
- Use only if you know video editing

**Windows Photos App (Simplest):**
- Open video in Photos
- Click "Edit & Create" → "Trim"
- Cut out mistakes
- Save

---

## Common Mistakes to Avoid

1. ❌ **Too long** - Keep under 5 minutes
2. ❌ **No audio** - Always check mic is on
3. ❌ **Too fast** - Slow down, breathe
4. ❌ **Showing passwords** - ALWAYS blur sensitive info
5. ❌ **Mumbling** - Speak clearly, project voice
6. ❌ **Waiting for perfection** - Ship the first version

---

## Next Steps

1. **Today:** Record "What is Mythara?" (2 min)
2. **Tomorrow:** Upload to YouTube (unlisted)
3. **Day 3:** Add embed to pricing page
4. **Day 4:** Update chatbot to say "Watch our 2-minute video"

You don't need to be perfect. You just need to start.

---

**Questions?**
- Need help with OBS setup?
- Want me to review your script?
- Stuck on something?

Just ask and I'll walk you through it.
