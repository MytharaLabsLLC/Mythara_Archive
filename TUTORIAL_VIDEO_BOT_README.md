# Mythara Tutorial Video Bot

> **Status: partially complete.** The 3 slide guides exist in `tutorial_audio/`, but the 3 MP3 voiceover files are NOT present — they were never generated or were removed. Re-run `generate_simple_tutorials.py` to create them.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

## What Happened

The plan was an **automated multimedia bot** that creates tutorial videos:

⚠️ **3 slide guides created** (exact instructions for each video) — present in `tutorial_audio/`
❌ **3 tutorial audio files** (British female voiceover) — NOT present; re-run the generator

---

## Generated Files

### Tutorial 1: "What is Mythara Engine?" (90 seconds)
- **Audio:** `tutorial_audio/01_what_is_mythara.mp3` — MISSING (regenerate)
- **Guide:** `tutorial_audio/01_what_is_mythara_SLIDES.txt` — present
- **Script:** Explains Soul Cradle, mission, pilot pricing

### Tutorial 2: "How to Start Your Pilot" (2 minutes)
- **Audio:** `tutorial_audio/02_pilot_signup.mp3` — MISSING (regenerate)
- **Guide:** `tutorial_audio/02_pilot_signup_SLIDES.txt` — present
- **Script:** Step-by-step pilot signup walkthrough

### Tutorial 3: "Soul Cradle Explained" (3 minutes)
- **Audio:** `tutorial_audio/03_soul_cradle.mp3` — MISSING (regenerate)
- **Guide:** `tutorial_audio/03_soul_cradle_SLIDES.txt` — present
- **Script:** Deep dive on Soul Cradle functionality

---

## How to Use This RIGHT NOW

### Option 1: EASIEST (5 minutes total per video)

1. **Press `Windows + G`** (opens Xbox Game Bar)
2. **Click Record button**
3. **Open:** https://mytharaarchive-production.up.railway.app
4. **Play audio file:** `tutorial_audio/01_what_is_mythara.mp3`
5. **Navigate page** while voiceover plays (90 seconds)
6. **Press `Windows + Alt + R`** to stop
7. **Done!** Video saved to: `C:\Users\Mythara\Videos\Captures`

**That's it.** You now have a tutorial video.

### Option 2: Run Launcher Script

```powershell
.\run_video_bot.ps1
```

This will:
- Show you all generated files
- Play the first audio file (if you want)
- Give you step-by-step instructions
- Open the tutorial_audio folder

---

## The Bot Code

### Simple Version
**File:** `generate_simple_tutorials.py` (present in repo root)

**What it does:**
- Generates MP3 voiceover files (British female, Google TTS)
- Creates slide guides with exact scripts and timing
- Gives you 3 recording options (easiest to professional)

**Run it to generate the missing MP3s:**
```powershell
python generate_simple_tutorials.py
```

### Advanced Version (For Later)
**File:** `generate_tutorial_videos.py`

**What it does:**
- Full video automation (screen recording + voiceover sync)
- Title cards, thumbnails, editing
- Requires more dependencies (moviepy, opencv, elevenlabs)

**Not needed yet.** Use the simple version first.

---

## Next Steps (After Recording)

### 1. Upload to YouTube
- Go to YouTube.com → Your Channel → Upload
- Drag MP4 from `C:\Users\Mythara\Videos\Captures`
- Set to **"Unlisted"** (only people with link can see)
- Title: "What is Mythara Engine? | 90 Second Overview"
- Description: Copy from `01_what_is_mythara_SLIDES.txt`

### 2. Get Embed Code
- Click **Share → Embed**
- Copy the `<iframe>` code
- Example:
```html
<iframe width="560" height="315" 
  src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
  frameborder="0" allowfullscreen>
</iframe>
```

### 3. Add to Pricing Page (when one exists)

**Note:** `core/static/pricing.html` is not in the repo — there is no pricing page to update yet. When one exists, add the embed below.

**Option A:** Add to hero section (top of page)
**Option B:** Add below Soul Cradle section
**Option C:** Add in chatbot responses

```html
<!-- Add this where you want video -->
<div class="video-container" style="max-width: 800px; margin: 2rem auto;">
    <h3>Watch: What is Mythara? (90 seconds)</h3>
    <iframe width="100%" height="450" 
      src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
      frameborder="0" allowfullscreen>
    </iframe>
</div>
```

### 4. Update Chatbot
**Note:** `core/static/pricing.html` is not in the repo — the chatbot code below is a template for when a pricing page exists.

Change training/support response:
```javascript
if (lowerInput.includes('training') || lowerInput.includes('onboarding')) {
    return 'Watch our 90-second intro video above, then we walk you through everything personally...';
}
```

Add video quick reply button:
```javascript
quickReplies = [
    "Watch 2-min video",
    "Start pilot now",
    "Talk to founder"
];
```

---

## Why This Is Better Than Manual Recording

### What the Bot Does
✅ Writes draft scripts (unvalidated messaging)  
✅ Generates British voiceover (consistent quality, once run)  
✅ Creates slide guides (exact timing, what to show when)  
✅ Handles 3 tutorials in 2 minutes (would take hours manually)

### What You Do
✅ Press Windows + G  
✅ Click Record  
✅ Navigate page while audio plays  
✅ Stop recording  

**Total time per video: 2-5 minutes**

---

## Technical Details

### Dependencies (Already Installed)
- `gtts` (Google Text-to-Speech) - Generates voiceovers
- `requests` - HTTP client for TTS API
- `click` - Command-line interface

### Audio Settings
- **Voice:** British English female (en-GB)
- **Format:** MP3 (universally compatible)
- **Quality:** 24kbps (clear speech, small file size)
- **Accent:** `tld='co.uk'` (British pronunciation)

### Script Content
- **Tutorial 1:** Mission/Soul Cradle overview + pilot CTA
- **Tutorial 2:** Step-by-step pilot signup process
- **Tutorial 3:** Deep dive on Soul Cradle functionality

All scripts are drafts.

---

## Troubleshooting

### "I don't see the audio files"
Check: `tutorial_audio/` folder in repo root

### "Audio won't play"
Try: Right-click → Open with → Windows Media Player

### "Xbox Game Bar won't open"
Enable it: Settings → Gaming → Xbox Game Bar → On

### "Video quality is bad"
Use Option 2 from slide guides (OBS Studio, free download)

### "I want to re-record audio"
Run: `python generate_simple_tutorials.py` (regenerates all files)

---

## Quick Comparison

| Method | Time | Quality | Difficulty |
|--------|------|---------|------------|
| **Bot + Xbox Game Bar** | 5 min | Good | Easy |
| Manual recording | 30 min | Variable | Medium |
| Professional editing | 2 hours | Excellent | Hard |

**Recommendation:** Start with bot + Xbox Game Bar. If you like the result, do all 3 tutorials. If you want better quality, upgrade to OBS Studio (still free).

---

## What You Can Say Now (Chatbot)

### Before Videos
❌ "We have video tutorials" (you didn't)  
❌ "Check out our Slack channel" (didn't exist)

### After Videos (Today!)
✅ "Watch our 90-second overview video"  
✅ "See the pilot signup walkthrough"  
✅ "Watch how Soul Cradle works"

**Update chatbot training response** after uploading to YouTube.

---

## Files in This Package

```
📦 Mythara Tutorial Video Bot
├── 🎤 generate_simple_tutorials.py    # Main bot (run to generate MP3s)
├── 🎬 generate_tutorial_videos.py     # Advanced version (optional)
├── 🚀 run_video_bot.ps1              # Quick launcher script
├── 📄 TUTORIAL_VIDEO_BOT_README.md   # This file
└── 📁 tutorial_audio/                # Generated files (MP3s missing — regenerate)
    ├── 01_what_is_mythara.mp3        # MISSING
    ├── 01_what_is_mythara_SLIDES.txt # present
    ├── 02_pilot_signup.mp3           # MISSING
    ├── 02_pilot_signup_SLIDES.txt    # present
    ├── 03_soul_cradle.mp3            # MISSING
    └── 03_soul_cradle_SLIDES.txt     # present
```

---

## Summary

**You asked:** "I want a multimedia bot do it for me"

**Current state:**
- ✅ Multimedia bot code (generates audio + slide guides)
- ✅ Slide guides created (3, in `tutorial_audio/`)
- ❌ MP3s not generated — run `python generate_simple_tutorials.py` first
- ✅ Easy workflow (Windows + G → Record → Done)

**Next action:** Generate the MP3s, then press `Windows + G` and record your first tutorial.

**Time investment:** 2 minutes now, 10 minutes to upload, videos live on your site.

---

**Questions?** Read the slide guides in `tutorial_audio/` — they have exact step-by-step instructions for each recording method.

**Ready?** Run: `.\run_video_bot.ps1`
