# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
MytharaConnect Voice Interface - 1980s Retro Computer Voice

Uses Windows SAPI (Speech API) with classic robotic voice settings
for that nostalgic 80s computer aesthetic.
"""

import subprocess
import platform

class RetroVoice:
    """
    1980s-style computer voice using Windows Text-to-Speech
    
    Features:
    - Robotic, monotone delivery (like old Apple II or Commodore 64)
    - Slow, deliberate speech rate
    - Classic "computer is thinking" pauses
    """
    
    def __init__(self):
        self.system = platform.system()
        if self.system == "Windows":
            self.voice_available = True
        else:
            self.voice_available = False
            print("⚠️  Retro voice only available on Windows")
    
    def speak(self, text: str, rate: int = -2):
        """
        Speak text with retro computer voice
        
        Args:
            text: Text to speak
            rate: Speech rate (-10 to 10, default -2 for slower 80s feel)
        """
        if not self.voice_available:
            return
        
        # PowerShell command for Windows SAPI with robotic settings
        # Rate -2 = slower, more deliberate (80s computer style)
        ps_command = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = {rate}
$synth.Volume = 80
$synth.Speak('{text.replace("'", "''")}')
"""
        
        try:
            subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
        except Exception as e:
            print(f"⚠️  Voice error: {e}")
    
    def announce_startup(self):
        """Classic 80s computer startup announcement"""
        self.speak("Mythara Connect. Sales agent. Activated.")
        
    def announce_industry_detected(self, industry: str):
        """Announce detected industry"""
        self.speak(f"Industry detected. {industry.replace('_', ' ')}.")
    
    def announce_validation_status(self, approved: bool, risk_score: int):
        """Announce validation results"""
        if approved and risk_score < 40:
            self.speak(f"Validation complete. Risk score. {risk_score}. Approved for auto send.")
        elif approved and risk_score < 70:
            self.speak(f"Validation complete. Risk score. {risk_score}. Medium risk. Sending with warnings.")
        else:
            self.speak(f"Validation failed. Risk score. {risk_score}. Human review required.")
    
    def announce_violations(self, violation_count: int):
        """Announce governance violations"""
        self.speak(f"Warning. {violation_count} governance violations detected. Email blocked.")
    
    def announce_demo_start(self):
        """Classic 80s demo start"""
        self.speak("Initiating demonstration. Industry aware sales system. Stand by.")
    
    def announce_scenario(self, scenario_name: str):
        """Announce demo scenario"""
        # Clean up scenario name for speech
        clean_name = scenario_name.replace("(", "").replace(")", "").replace("-", "")
        self.speak(f"Scenario. {clean_name}.")


def add_voice_to_connect():
    """
    Add retro voice announcements to MytharaConnect
    
    Integration points:
    - Startup: "Mythara Connect activated"
    - Industry detection: "Industry detected: Banking"
    - Validation: "Risk score 45, approved for sending"
    - Violations: "Warning, 2 violations detected"
    """
    return RetroVoice()


# Demo of retro voice
if __name__ == '__main__':
    print("="*80)
    print("MYTHARA CONNECT - 1980s RETRO VOICE DEMO")
    print("="*80)
    
    voice = RetroVoice()
    
    if voice.voice_available:
        print("\n🔊 Testing retro computer voice...\n")
        
        # Classic startup sequence
        voice.speak("Mythara Connect. Sales agent. Online.")
        
        # Industry detection
        voice.speak("Analyzing prospect email domain.")
        voice.speak("Industry detected. Banking and financial services.")
        
        # Validation announcement
        voice.speak("Running multi tier validation.")
        voice.speak("Risk score. Forty five.")
        voice.speak("Approved for auto send.")
        
        # Violation warning
        voice.speak("Warning. Pricing violation detected.")
        voice.speak("Email blocked. Human review required.")
        
        print("\n✅ Retro voice demo complete!")
        print("\nTo integrate with MytharaConnect:")
        print("1. Import: from mythara_connect_voice import RetroVoice")
        print("2. Initialize: voice = RetroVoice()")
        print("3. Use: voice.announce_startup()")
    else:
        print("\n⚠️  Retro voice requires Windows with SAPI")
