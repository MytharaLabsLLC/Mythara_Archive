"""
Mythara Simple Tutorial Generator

Copyright © 2025 Herbert Velez Jr. All rights reserved.

Generates tutorial audio + slides (you combine them manually)
Much simpler than full video automation.
"""

import os
from pathlib import Path
from datetime import datetime

# Text-to-speech
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️  gTTS not installed. Run: pip install gtts")


TUTORIALS = [
    {
        "title": "What is Mythara Engine?",
        "filename": "01_what_is_mythara",
        "duration": "90 seconds",
        "script": """Hi, I'm Herbert from Mythara. Let me show you what we do.

Mythara holds the space when your mission conflicts with compliance. 

Say you're a hospital social worker. Policy says discharge this patient. 
Your heart says they'll be homeless. Both are true.

Soul Cradle documents that paradox. Measures the cost to your soul 
and the mission. Creates an immutable record.

We donate Soul Cradle to healthcare, banking, justice, nonprofits, 
civil service, education—the industries carrying impossible weight.

Try it: 49 dollars for 7 days. Full access. See if it fits your reality.

Questions? Email Mythara.Engine@yahoo.com""",
        "slides": [
            "Slide 1: Title - 'What is Mythara Engine?'",
            "Slide 2: Show pricing page hero section",
            "Slide 3: 'When Mission Conflicts with Compliance'",
            "Slide 4: Example scenario text",
            "Slide 5: 'Soul Cradle' section from pricing page",
            "Slide 6: Industries we serve",
            "Slide 7: Pilot pricing ($49/7 days)",
            "Slide 8: Contact info"
        ]
    },
    {
        "title": "How to Start Your Mythara Pilot",
        "filename": "02_pilot_signup",
        "duration": "2 minutes",
        "script": """Let me show you how to start your Mythara Pilot.

Scroll down to the Pilot tier. 49 dollars for 7 days, full access.

Check the Terms box. Click Subscribe.

You'll enter your payment info. Takes 2 minutes.

That's it. You're in. Full access to Mythara for 7 days.

You'll know quickly whether it's the right fit.

And if you upgrade to Enterprise? That 49 dollars gets credited back.

So you're really just testing it with our money.

Questions? Email Mythara.Engine@yahoo.com""",
        "slides": [
            "Slide 1: Title - 'Start Your Pilot'",
            "Slide 2: Pricing tiers overview",
            "Slide 3: Zoom in on Pilot tier ($49)",
            "Slide 4: Highlight 'Check terms' checkbox",
            "Slide 5: Highlight 'Subscribe' button",
            "Slide 6: '7 Days Full Access'",
            "Slide 7: 'Upgrade credits back your $49'",
            "Slide 8: Contact info"
        ]
    },
    {
        "title": "Soul Cradle Explained",
        "filename": "03_soul_cradle",
        "duration": "3 minutes",
        "script": """Let's talk about Soul Cradle.

Hospital social worker. Patient needs care. Policy says discharge. 
Heart says keep them safe.

Soul Cradle documents: What policy said. What your heart said. 
What you actually did. The emotional weight of that choice.

We generate a cryptographic hash. Timestamp it. Make it immutable.

Leadership sees the pattern across your org. They spot burnout 
before people break.

Audit-ready. Human-ready.

We donate Soul Cradle to the industries that need it most:
Healthcare, banking, justice, nonprofits, civil service, education.

It's included in every tier. No charge.

Because some things shouldn't have a price.

Questions? Email Mythara.Engine@yahoo.com""",
        "slides": [
            "Slide 1: Title - 'Soul Cradle'",
            "Slide 2: 'When Mission Conflicts with Compliance'",
            "Slide 3: Hospital scenario example",
            "Slide 4: What Soul Cradle captures (4 points)",
            "Slide 5: 'Cryptographic Hash + Timestamp'",
            "Slide 6: Leadership dashboard view",
            "Slide 7: 'Audit-ready, Human-ready'",
            "Slide 8: Industries (icons/list)",
            "Slide 9: 'Included in Every Tier'",
            "Slide 10: Contact info"
        ]
    }
]


def generate_audio_file(script, output_file, voice='en', tld='co.uk'):
    """Generate MP3 audio from script using Google TTS"""
    print(f"🎤 Generating audio: {output_file}")
    
    if not GTTS_AVAILABLE:
        print("❌ gTTS not installed. Run: pip install gtts")
        return None
    
    try:
        tts = gTTS(text=script, lang=voice, tld=tld, slow=False)
        tts.save(str(output_file))
        print(f"✅ Audio saved: {output_file}")
        return str(output_file)
    except Exception as e:
        print(f"❌ Failed to generate audio: {e}")
        return None


def generate_slide_guide(tutorial, output_file):
    """Generate a text file with slide instructions"""
    print(f"📄 Generating slide guide: {output_file}")
    
    content = f"""# {tutorial['title']}
Duration: {tutorial['duration']}

## Script
{tutorial['script']}

## Slide Sequence
"""
    
    for slide in tutorial['slides']:
        content += f"\n{slide}"
    
    content += f"""

## How to Record This Tutorial

### Option 1: PowerPoint + OBS (Recommended)
1. Create PowerPoint with these {len(tutorial['slides'])} slides
2. Open OBS Studio
3. Add "Display Capture" source
4. Click "Start Recording"
5. Open PowerPoint in Presenter View
6. Play audio file: {Path(output_file).stem}.mp3
7. Advance slides as audio plays
8. Stop recording when done

### Option 2: Manual Recording (Easiest)
1. Press Windows + G (Xbox Game Bar)
2. Click Record
3. Open Railway pricing page
4. Play audio file: {Path(output_file).stem}.mp3
5. Navigate page as audio plays
6. Press Windows + Alt + R to stop
7. Video saved to: C:\\Users\\Mythara\\Videos\\Captures

### Option 3: Professional (Best Quality)
1. Record audio separately (clearer voice)
2. Record screen navigation separately
3. Use Clipchamp or DaVinci Resolve to sync
4. Add title cards and transitions
5. Export as MP4

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Slide guide saved: {output_file}")
    return str(output_file)


def main():
    """Generate audio files and slide guides for all tutorials"""
    print("\n" + "="*60)
    print("🎤 MYTHARA SIMPLE TUTORIAL GENERATOR")
    print("="*60 + "\n")
    
    # Create output directory
    output_dir = Path("tutorial_audio")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir}\n")
    
    # Check dependencies
    if not GTTS_AVAILABLE:
        print("❌ Missing dependency: gTTS")
        print("Run: pip install gtts")
        print("\nThen run this script again.\n")
        return
    
    # Generate for each tutorial
    for i, tutorial in enumerate(TUTORIALS, 1):
        print(f"\n{'='*60}")
        print(f"📹 Tutorial {i}/{len(TUTORIALS)}: {tutorial['title']}")
        print(f"{'='*60}\n")
        
        # Generate audio
        audio_file = output_dir / f"{tutorial['filename']}.mp3"
        audio_path = generate_audio_file(tutorial['script'], audio_file)
        
        # Generate slide guide
        guide_file = output_dir / f"{tutorial['filename']}_SLIDES.txt"
        guide_path = generate_slide_guide(tutorial, guide_file)
        
        if audio_path and guide_path:
            print(f"\n✅ Tutorial {i} ready!")
            print(f"🎤 Audio: {audio_path}")
            print(f"📄 Guide: {guide_path}")
        else:
            print(f"\n❌ Tutorial {i} failed")
        
        print("\n")
    
    print("\n" + "="*60)
    print("🎉 ALL TUTORIAL AUDIO GENERATED")
    print("="*60)
    print(f"\n📁 Files saved to: {output_dir}/")
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review audio files in tutorial_audio/
2. Read each _SLIDES.txt file
3. Choose recording method:
   
   EASIEST (5 minutes per video):
   - Press Windows + G
   - Play the MP3 file
   - Navigate pricing page as audio plays
   - Done!
   
   BETTER (15 minutes per video):
   - Create PowerPoint slides (follow _SLIDES.txt)
   - Record screen while presenting
   
   BEST (30 minutes per video):
   - Record voiceover separately (your real voice)
   - Record screen separately
   - Edit in Clipchamp/DaVinci Resolve

4. Upload videos to YouTube (unlisted)
5. Add embed codes to pricing.html
6. Update chatbot to reference videos

TIP: Start with Tutorial 1 (90 seconds). 
     If it works, do the rest!
""")


if __name__ == "__main__":
    main()
