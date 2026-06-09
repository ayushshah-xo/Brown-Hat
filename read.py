"""
================================================================
  read.py — Text Reader Mode for Sukuna Robot
  Run: python3 read.py

  Type or paste ANY text in English or Nepali.
  The robot will read it aloud with jaw movement.
  Type 'quit' to exit.
================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice.tts import TTS
from config import SCHOOL

# ── Try to load jaw servo ─────────────────────────────────
jaw = None
try:
    from motion.servos import RobotServos
    servos = RobotServos()
    jaw = servos.jaw
    print("  ✓  Jaw servo connected — mouth will move while speaking")
except Exception as e:
    print(f"  ⚠  Jaw servo not available ({e}) — audio only")

# ── Init TTS ──────────────────────────────────────────────
print("  → Loading TTS engine...", end=" ", flush=True)
tts = TTS()
print("✓")

# ── Language detection ────────────────────────────────────
def detect_language(text: str) -> str:
    """Simple detection: if text contains Devanagari characters → Nepali."""
    for ch in text:
        if '\u0900' <= ch <= '\u097F':   # Devanagari Unicode range
            return "ne"
    return "en"

# ── Banner ────────────────────────────────────────────────
print("\n" + "=" * 55)
print(f"   {SCHOOL['robot_name']} — Text Reader Mode")
print(f"   Type or paste text → robot reads it aloud")
print(f"   Language auto-detected (English / Nepali)")
print(f"   Type 'quit' to exit | 'en'/'ne' to force language")
print("=" * 55 + "\n")

# ── Main loop ─────────────────────────────────────────────
forced_lang = None

while True:
    try:
        print()
        text = input("  📝  Paste text (or 'quit'/'en'/'ne'): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Goodbye!")
        break

    if not text:
        continue

    # Commands
    if text.lower() == "quit":
        print("  Goodbye!")
        break
    if text.lower() == "en":
        forced_lang = "en"
        print("  ✓  Forced language: English")
        continue
    if text.lower() == "ne":
        forced_lang = "ne"
        print("  ✓  Forced language: Nepali")
        continue
    if text.lower() == "auto":
        forced_lang = None
        print("  ✓  Language: auto-detect")
        continue

    # Detect language
    lang = forced_lang if forced_lang else detect_language(text)
    lang_name = "Nepali" if lang == "ne" else "English"

    print(f"\n  🌐  Language detected: {lang_name}")
    print(f"  🔊  Speaking now...\n")

    # Split long text into sentences for natural pauses
    import re
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[।.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) > 1:
        print(f"  📖  {len(sentences)} sentences — reading paragraph...")
        for i, sentence in enumerate(sentences, 1):
            print(f"       [{i}/{len(sentences)}] {sentence[:60]}{'...' if len(sentence)>60 else ''}")
            tts.speak(sentence, lang=lang, jaw=jaw)
    else:
        tts.speak(text, lang=lang, jaw=jaw)

    print("\n  ✅  Done reading.")
