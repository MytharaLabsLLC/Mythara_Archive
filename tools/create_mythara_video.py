#!/usr/bin/env python3
"""
Mythara Engine - AI Video Generator (TTS + Lip-sync)
Create a Mythara talking-head video by generating narration (ElevenLabs)
then lip-syncing a character image with Wav2Lip.

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Quick usage (Windows PowerShell):
1) Ensure Python 3.10+ and FFmpeg installed and on PATH.
2) Create venv and install basics:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install elevenlabs requests tqdm
3) Get Wav2Lip locally (outside this repo to keep it light):
   git clone https://github.com/Rudrabha/Wav2Lip vendor/Wav2Lip
   pip install -r vendor/Wav2Lip/requirements.txt
   # Download model checkpoints (GAN version recommended):
   # See: https://github.com/Rudrabha/Wav2Lip#steps-to-download-pre-trained-models
   # Place wav2lip_gan.pth under vendor/Wav2Lip/checkpoints/
4) Put a high-res Mythara portrait at assets/mythara_portrait.png (face visible).
5) Set ELEVENLABS_API_KEY in your environment (and optional ELEVENLABS_VOICE_ID).
6) Run:
   python tools/create_mythara_video.py \
      --image assets/mythara_portrait.png \
      --text "Welcome..." \
      --out core/static/assets/mythara_intro_v1.mp4

Notes:
- For non-human/illustrated faces, Wav2Lip works best when the mouth region is clear and frontal.
- If ElevenLabs is not desired, you can provide an existing WAV via --audio to skip TTS.
"""

import argparse
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

try:
    from elevenlabs import ElevenLabs
except Exception:
    ElevenLabs = None  # Optional; user can provide --audio instead


def tts_generate(text: str, out_wav: Path, voice_id: Optional[str] = None) -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set. Provide --audio to skip TTS or set the key.")
    if ElevenLabs is None:
        raise RuntimeError("elevenlabs package not installed. pip install elevenlabs")

    client = ElevenLabs(api_key=api_key)
    voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID")

    # Settings tuned for narration clarity
    audio = client.text_to_speech.convert(
        voice_id=voice_id or "21m00Tcm4TlvDq8ikWAM",  # Rachel fallback
        optimize_streaming_latency="0",
        output_format="wav",
        text=text,
        model_id="eleven_multilingual_v2"
    )

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with open(out_wav, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)


def run_wav2lip(face_image: Path, audio_wav: Path, out_mp4: Path, wav2lip_dir: Path, checkpoint: Optional[Path]) -> None:
    """Invoke Wav2Lip inference script as a subprocess."""
    infer_py = wav2lip_dir / "inference.py"
    if not infer_py.exists():
        raise FileNotFoundError(f"Wav2Lip inference.py not found at: {infer_py}")

    if checkpoint is None:
        checkpoint = wav2lip_dir / "checkpoints" / "wav2lip_gan.pth"
    if not checkpoint.exists():
        raise FileNotFoundError(
            f"Wav2Lip checkpoint not found. Expected: {checkpoint}.\n"
            "See https://github.com/Rudrabha/Wav2Lip#steps-to-download-pre-trained-models"
        )

    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    # Typical inference flags; adjust pads for tight cropping if needed
    cmd = [
        sys.executable, str(infer_py),
        "--checkpoint_path", str(checkpoint),
        "--face", str(face_image),
        "--audio", str(audio_wav),
        "--outfile", str(out_mp4),
    ]

    # You can tweak for non-frontal images:
    # cmd += ["--pads", "0", "10", "0", "0"]

    print("[Wav2Lip] Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    p = argparse.ArgumentParser(description="Create Mythara talking-head video (TTS + Wav2Lip)")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--text", type=str, help="Narration text for TTS")
    g.add_argument("--script", type=Path, help="Path to a .txt file with narration")
    p.add_argument("--audio", type=Path, help="Optional: pre-made WAV to skip TTS")
    p.add_argument("--image", type=Path, required=True, help="Portrait image with visible face/mouth")
    p.add_argument("--voice", type=str, help="ElevenLabs voice_id (optional)")
    p.add_argument("--wav2lip", type=Path, default=Path("vendor/Wav2Lip"), help="Path to local Wav2Lip repo")
    p.add_argument("--checkpoint", type=Path, help="Path to Wav2Lip checkpoint .pth (optional)")
    p.add_argument("--out", type=Path, default=Path("core/static/assets/mythara_intro_v1.mp4"), help="Output MP4 path")

    args = p.parse_args()

    # Resolve narration
    text = args.text
    if not text and args.script and args.script.exists():
        text = args.script.read_text(encoding="utf-8").strip()
    if not args.audio and not text:
        raise SystemExit("Provide --text/--script for TTS, or --audio to skip TTS.")

    # TTS step (if no audio provided)
    tmpdir = Path(tempfile.mkdtemp(prefix="mythara_video_"))
    audio_wav: Path
    if args.audio:
        audio_wav = args.audio
    else:
        audio_wav = tmpdir / "narration.wav"
        print("[TTS] Generating narration with ElevenLabs …")
        tts_generate(text=text or "", out_wav=audio_wav, voice_id=args.voice)
        print(f"[TTS] Saved: {audio_wav}")

    # Lip-sync step
    print("[LipSync] Running Wav2Lip …")
    run_wav2lip(
        face_image=args.image,
        audio_wav=audio_wav,
        out_mp4=args.out,
        wav2lip_dir=args.wav2lip,
        checkpoint=args.checkpoint,
    )
    print(f"[Done] Video written to: {args.out}")


if __name__ == "__main__":
    main()
