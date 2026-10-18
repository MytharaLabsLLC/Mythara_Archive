"""
Generate Mythara AI Representative Voice using ElevenLabs API

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please set it in .env file.")

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Adam (deep, authoritative)
# Alternative voices:
# "N2lVS1w4EtoT3dr4eOWO" = Callum (Scottish)
# "nPczCjzI2devNBz1zQrb" = Brian (thoughtful, sentient)
# "XB0fDUnXU5powFXDhCwa" = Charlotte (female sentient)

# Load script
script_path = "DESCRIPT_PASTE_READY_SCRIPT.txt"
with open(script_path, "r", encoding="utf-8") as f:
    script_text = f.read()

print(f"📝 Loaded script: {len(script_text)} characters")
print(f"🎤 Using voice: Adam (ID: {VOICE_ID})")

# API endpoint
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Headers
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
}

# Request payload
data = {
    "text": script_text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.40,
        "use_speaker_boost": True
    }
}

print("🎙️ Generating voice with ElevenLabs...")
print("⏳ This may take 30-60 seconds...")

# Make API request
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    # Save audio file
    output_path = "core/static/mythara-voice.mp3"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    print(f"✅ SUCCESS! Voice generated and saved to: {output_path}")
    print(f"📊 File size: {len(response.content) / 1024:.2f} KB")
    print("\n📋 Next steps:")
    print("1. Listen to the file to verify quality")
    print("2. Commit and push to GitHub")
    print("3. Video will appear on pricing page!")
    
else:
    print(f"❌ ERROR: {response.status_code}")
    print(f"Response: {response.text}")
    print("\n💡 Possible issues:")
    print("- API key expired or invalid")
    print("- Insufficient credits")
    print("- Voice ID not found")
