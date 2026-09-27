# Mythara Pricing Video Generation Guide
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

## Quick Start

### Option 1: Use Manim (Recommended - Professional Quality)

1. **Install Manim:**
   ```powershell
   py -3.11 -m pip install manim python-dotenv
   ```

2. **Generate the video:**
   ```powershell
   # Low quality preview (fast)
   py -3.11 -m manim -pql generate_pricing_video.py MytharaPricingVideo
   
   # High quality (production)
   py -3.11 -m manim -pqh generate_pricing_video.py MytharaPricingVideo
   ```

3. **Output location:**
   `media/videos/generate_pricing_video/1080p60/MytharaPricingVideo.mp4`

### Option 2: Generate Voice First, Then Sync

1. **Generate voice narration with ElevenLabs:**
   ```powershell
   # Make sure your API key is in .env file
   py -3.11 generate_mythara_voice.py
   ```
   
   This creates: `core/static/mythara-pricing-voice.mp3`

2. **Generate video with synced audio:**
   ```powershell
   py -3.11 -m manim -pqh generate_pricing_video.py MytharaPricingWithVoice
   ```

### Option 3: Quick Web-Based Alternative (No Install)

Use an online tool like:
- **Canva Video**: canva.com/create/videos/
- **Animoto**: animoto.com
- **Lumen5**: lumen5.com

Upload your script from `generate_pricing_video.py` (the narration text is embedded in the script — no separate `generate_pricing_video_script.txt` exists in the repo).

## What the Video Includes

- ✅ Animated intro with Mythara branding
- ✅ All 4 pricing tiers (Pilot, Growth, Enterprise, Sovereign)
- ✅ Cute fox mascot animations
- ✅ Professional purple/blue gradient theme
- ✅ Call-to-action ending
- ✅ ~60 seconds total duration

## Customization

Edit `generate_pricing_video.py` to customize:
- Colors (change PURPLE, BLUE, etc.)
- Timing (adjust `self.wait()` durations)
- Features text
- Pricing amounts
- Animation styles

## Embedding in a Pricing Page

> Note: `core/static/pricing.html` is not in the repo — there is no pricing page to update yet. The snippet below is a template for when one exists.

```html
<div class="video-wrapper">
    <video controls>
        <source src="mythara-pricing-video.mp4" type="video/mp4">
        Your browser doesn't support video playback.
    </video>
</div>
```

Or upload to YouTube and use iframe embed.

## Troubleshooting

**Manim not installing?**
- Install LaTeX first: https://miktex.org/download (Windows)
- Or use: `py -3.11 -m pip install manim-minimal`

**Need faster rendering?**
- Use `-ql` (low quality) for previews
- Use `-qm` (medium) for faster production renders

**Want different animation style?**
- Check Manim gallery: docs.manim.community/en/stable/examples.html
- Copy-paste animation patterns you like

## Next Steps

1. Generate the video
2. Upload to `core/static/` directory
3. Add the video embed to your pricing page (not present in the repo)
4. Test locally: `python core/source_proprietary/main.py`
5. Serve and check locally: `python core/source_proprietary/main.py` (note: no pricing.html exists yet to visit)
