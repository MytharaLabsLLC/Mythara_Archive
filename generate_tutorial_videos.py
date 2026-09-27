"""
Mythara Tutorial Video Generator Bot

Copyright © 2025 Herbert Velez Jr. All rights reserved.

Automatically generates tutorial videos using:
- Text-to-speech (ElevenLabs or Google TTS)
- Screen recording automation
- Video editing (moviepy)
- Thumbnail generation
"""

import os
import time
from pathlib import Path
from datetime import datetime
import json

# Video generation
try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ImageClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  moviepy not installed. Run: pip install moviepy")

# Text-to-speech
try:
    from elevenlabs import generate, save, Voice
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️  elevenlabs not installed. Run: pip install elevenlabs")

# Screen recording
try:
    import pyautogui
    import cv2
    import numpy as np
    SCREEN_RECORDING_AVAILABLE = True
except ImportError:
    SCREEN_RECORDING_AVAILABLE = False
    print("⚠️  Screen recording not available. Run: pip install pyautogui opencv-python")

# Image generation (for thumbnails)
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not installed. Run: pip install pillow")


class TutorialVideoBot:
    """Generates professional tutorial videos automatically"""
    
    def __init__(self, output_dir="tutorial_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # API keys from environment
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
        
        # Video settings
        self.fps = 30
        self.resolution = (1920, 1080)
        
        print(f"🎬 Mythara Tutorial Video Bot initialized")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"✅ moviepy: {MOVIEPY_AVAILABLE}")
        print(f"✅ elevenlabs: {ELEVENLABS_AVAILABLE}")
        print(f"✅ screen recording: {SCREEN_RECORDING_AVAILABLE}")
        print(f"✅ PIL: {PIL_AVAILABLE}")
    
    def generate_voiceover(self, script, output_file, voice="British Female"):
        """Generate voiceover audio from script"""
        print(f"🎤 Generating voiceover: {output_file}")
        
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            try:
                # Use ElevenLabs for high-quality British female voice
                audio = generate(
                    text=script,
                    voice=Voice(voice_id="EXAVITQu4vr4xnSDxMaL"),  # Bella - British
                    model="eleven_monolingual_v1"
                )
                save(audio, str(output_file))
                print(f"✅ ElevenLabs voiceover saved: {output_file}")
                return str(output_file)
            except Exception as e:
                print(f"⚠️  ElevenLabs failed: {e}, falling back to gTTS")
        
        # Fallback to Google TTS
        try:
            from gtts import gTTS
            tts = gTTS(text=script, lang='en', tld='co.uk')  # British accent
            tts.save(str(output_file))
            print(f"✅ Google TTS voiceover saved: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"❌ Failed to generate voiceover: {e}")
            return None
    
    def create_title_card(self, title, duration=3):
        """Create an opening title card"""
        print(f"🎨 Creating title card: {title}")
        
        if not PIL_AVAILABLE:
            print("⚠️  PIL not available, skipping title card")
            return None
        
        # Create image
        img = Image.new('RGB', self.resolution, color=(139, 92, 246))  # Mythara purple
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font
        try:
            font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((self.resolution[0] - text_width) // 2, 
                   (self.resolution[1] - text_height) // 2 - 50)
        draw.text(position, title, fill='white', font=font)
        
        # Draw subtitle
        subtitle = "Mythara Engine"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_position = ((self.resolution[0] - sub_width) // 2, position[1] + 100)
        draw.text(sub_position, subtitle, fill='white', font=subtitle_font)
        
        # Save temporary image
        temp_path = self.output_dir / f"title_{int(time.time())}.png"
        img.save(str(temp_path))
        
        if MOVIEPY_AVAILABLE:
            clip = ImageClip(str(temp_path)).set_duration(duration)
            return clip
        
        return None
    
    def record_screen(self, duration, output_file):
        """Record screen for specified duration"""
        print(f"📹 Recording screen for {duration} seconds...")
        
        if not SCREEN_RECORDING_AVAILABLE:
            print("⚠️  Screen recording not available")
            return None
        
        # Get screen size
        screen_size = pyautogui.size()
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(output_file), fourcc, self.fps, screen_size)
        
        start_time = time.time()
        print(f"🔴 Recording started... (will record for {duration}s)")
        
        while time.time() - start_time < duration:
            # Capture screenshot
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
            
            # Show progress
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0:
                print(f"⏱️  {elapsed}/{duration} seconds recorded...")
        
        out.release()
        print(f"✅ Screen recording saved: {output_file}")
        return str(output_file)
    
    def create_tutorial_video(self, tutorial_config):
        """
        Create a complete tutorial video from config
        
        Config format:
        {
            "title": "What is Mythara?",
            "filename": "01_what_is_mythara",
            "sections": [
                {
                    "type": "title_card",
                    "text": "What is Mythara Engine?",
                    "duration": 3
                },
                {
                    "type": "voiceover",
                    "script": "Hi, I'm Herbert from Mythara...",
                    "screen_recording_duration": 90
                }
            ]
        }
        """
        print(f"\n{'='*60}")
        print(f"🎬 Creating tutorial: {tutorial_config['title']}")
        print(f"{'='*60}\n")
        
        if not MOVIEPY_AVAILABLE:
            print("❌ moviepy is required. Run: pip install moviepy")
            return None
        
        clips = []
        audio_clips = []
        
        for i, section in enumerate(tutorial_config['sections']):
            section_type = section.get('type')
            
            if section_type == 'title_card':
                # Create title card
                title_clip = self.create_title_card(
                    section['text'],
                    section.get('duration', 3)
                )
                if title_clip:
                    clips.append(title_clip)
            
            elif section_type == 'voiceover':
                # Generate voiceover audio
                audio_file = self.output_dir / f"audio_{i}.mp3"
                audio_path = self.generate_voiceover(
                    section['script'],
                    audio_file
                )
                
                if audio_path:
                    # Record screen while voiceover plays
                    video_file = self.output_dir / f"screen_{i}.mp4"
                    duration = section.get('screen_recording_duration', 60)
                    
                    print(f"\n📹 Recording screen segment {i+1}...")
                    print(f"💡 TIP: Open your Railway app now!")
                    print(f"💡 Navigate and demonstrate features for {duration} seconds")
                    print(f"⏰ Recording starts in 5 seconds...\n")
                    time.sleep(5)
                    
                    video_path = self.record_screen(duration, video_file)
                    
                    if video_path:
                        video_clip = VideoFileClip(video_path)
                        audio_clip = AudioFileClip(audio_path)
                        
                        # Sync video with audio
                        video_clip = video_clip.set_audio(audio_clip)
                        clips.append(video_clip)
        
        if not clips:
            print("❌ No clips generated")
            return None
        
        # Concatenate all clips
        print(f"\n🔧 Combining {len(clips)} clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Export final video
        output_filename = self.output_dir / f"{tutorial_config['filename']}.mp4"
        print(f"\n💾 Exporting final video: {output_filename}")
        
        final_video.write_videofile(
            str(output_filename),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        print(f"\n✅ Tutorial video created: {output_filename}")
        print(f"📊 Duration: {final_video.duration:.1f} seconds")
        print(f"📁 Size: {output_filename.stat().st_size / 1024 / 1024:.1f} MB")
        
        return str(output_filename)
    
    def generate_thumbnail(self, title, subtitle, output_file):
        """Generate a professional thumbnail for the video"""
        print(f"🖼️  Generating thumbnail: {output_file}")
        
        if not PIL_AVAILABLE:
            print("⚠️  PIL not available")
            return None
        
        # Create thumbnail (1280x720 for YouTube)
        img = Image.new('RGB', (1280, 720), color=(139, 92, 246))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 70)  # Bold
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_position = ((1280 - title_width) // 2, 250)
        draw.text(title_position, title, fill='white', font=title_font)
        
        # Draw subtitle
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_position = ((1280 - sub_width) // 2, 400)
        draw.text(sub_position, subtitle, fill=(230, 230, 230), font=subtitle_font)
        
        img.save(str(output_file))
        print(f"✅ Thumbnail saved: {output_file}")
        return str(output_file)


# Tutorial configurations
TUTORIALS = [
    {
        "title": "What is Mythara Engine?",
        "filename": "01_what_is_mythara",
        "sections": [
            {
                "type": "title_card",
                "text": "What is Mythara?",
                "duration": 3
            },
            {
                "type": "voiceover",
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
                "screen_recording_duration": 90
            }
        ]
    },
    {
        "title": "How to Start Your Mythara Pilot",
        "filename": "02_pilot_signup",
        "sections": [
            {
                "type": "title_card",
                "text": "Start Your Pilot",
                "duration": 3
            },
            {
                "type": "voiceover",
                "script": """Let me show you how to start your Mythara Pilot.

Scroll down to the Pilot tier. 49 dollars for 7 days, full access.

Check the Terms box. Click Subscribe.

You'll enter your payment info. Takes 2 minutes.

That's it. You're in. Full access to Mythara for 7 days.

You'll know quickly whether it's the right fit.

And if you upgrade to Enterprise? That 49 dollars gets credited back.

So you're really just testing it with our money.

Questions? Email Mythara.Engine@yahoo.com""",
                "screen_recording_duration": 120
            }
        ]
    },
    {
        "title": "Soul Cradle Explained",
        "filename": "03_soul_cradle",
        "sections": [
            {
                "type": "title_card",
                "text": "Soul Cradle",
                "duration": 3
            },
            {
                "type": "voiceover",
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
                "screen_recording_duration": 180
            }
        ]
    }
]


def main():
    """Generate all tutorial videos"""
    print("\n" + "="*60)
    print("🎬 MYTHARA TUTORIAL VIDEO GENERATOR")
    print("="*60 + "\n")
    
    bot = TutorialVideoBot()
    
    # Check dependencies
    missing_deps = []
    if not MOVIEPY_AVAILABLE:
        missing_deps.append("moviepy")
    if not PIL_AVAILABLE:
        missing_deps.append("pillow")
    
    if missing_deps:
        print("\n⚠️  Missing dependencies:")
        for dep in missing_deps:
            print(f"   pip install {dep}")
        print("\nInstall these first, then run again.\n")
        return
    
    # Generate each tutorial
    for i, tutorial in enumerate(TUTORIALS, 1):
        print(f"\n{'='*60}")
        print(f"📹 Tutorial {i}/{len(TUTORIALS)}: {tutorial['title']}")
        print(f"{'='*60}\n")
        
        # Create video
        video_path = bot.create_tutorial_video(tutorial)
        
        if video_path:
            # Generate thumbnail
            thumbnail_path = bot.output_dir / f"{tutorial['filename']}_thumbnail.png"
            bot.generate_thumbnail(
                tutorial['title'],
                "Mythara Engine Tutorial",
                thumbnail_path
            )
            
            print(f"\n✅ Tutorial {i} complete!")
            print(f"📹 Video: {video_path}")
            print(f"🖼️  Thumbnail: {thumbnail_path}")
        else:
            print(f"\n❌ Tutorial {i} failed")
        
        print("\n")
    
    print("\n" + "="*60)
    print("🎉 ALL TUTORIALS GENERATED")
    print("="*60)
    print(f"\n📁 Videos saved to: {bot.output_dir}")
    print("\nNext steps:")
    print("1. Review videos in tutorial_videos/")
    print("2. Upload to YouTube (unlisted)")
    print("3. Add embed codes to pricing.html")
    print("4. Update chatbot responses")


if __name__ == "__main__":
    main()
