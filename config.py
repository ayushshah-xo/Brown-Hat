"""
================================================================
  SUKUNA SCHOOL ROBOT — config.py
  ✏️  Edit THIS file to customise your robot.
  Everything — pins, language, API keys, school info — lives here.
================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()                         # reads .env file if present
BASE_DIR = Path(__file__).parent.resolve()

# ── 1. SCHOOL INFO ────────────────────────────────────────────────────────
SCHOOL = {
    "name":         "Sukuna Secondary School",
    "location":     "Nepal",
    "head_teacher": "Hikmat Bahadur Basnet",
    "phone":        "+977 021-545366",
    "email":        "schoolsukuna@gmail.com",
    "website":      "https://sukunaschool.edu.np",
    "robot_name":   "Sukuna",
}

# ── 2. LANGUAGE ───────────────────────────────────────────────────────────
#   "ne" = Nepali (primary), "hi" = Hindi, "en" = English
DEFAULT_LANGUAGE    = "ne"
SUPPORTED_LANGUAGES = ["ne", "hi", "en"]

# ── 3. AI / LLM ───────────────────────────────────────────────────────────
#   Switch AI_MODE here:
#     "groq"    → fastest cloud LLM  (needs GROQ_API_KEY)  ← RECOMMENDED
#     "openai"  → OpenAI GPT         (needs OPENAI_API_KEY)
#     "offline" → local Mistral GGUF (no internet needed)
AI_MODE         = os.getenv("AI_MODE", "groq")
GROQ_API_KEY    = os.getenv("GROQ_API_KEY",   "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL_GROQ  = "llama-3.1-8b-instant"      # fastest Groq model
LLM_MODEL_OAI   = "gpt-4o-mini"           # cheapest OpenAI model
LLM_TIMEOUT     = 8                        # seconds before timeout

# Offline LLM (only used when AI_MODE = "offline")
LLM_OFFLINE_PATH = str(BASE_DIR / "models" / "llm" /
                        "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
LLM_N_THREADS    = 4         # all 4 Pi 4 cores
LLM_MAX_TOKENS   = 200

# ── 4. SPEECH-TO-TEXT (STT) ───────────────────────────────────────────────
#   "deepgram" → cloud, ~200 ms  (needs DEEPGRAM_API_KEY) ← RECOMMENDED
#   "vosk"     → offline, ~1.5 s (no internet needed)
STT_ENGINE       = os.getenv("STT_ENGINE", "deepgram")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")

VOSK_MODELS = {                           # only used when STT_ENGINE="vosk"
    "ne": str(BASE_DIR / "models" / "vosk" / "vosk-model-ne"),
    "hi": str(BASE_DIR / "models" / "vosk" / "vosk-model-small-hi"),
    "en": str(BASE_DIR / "models" / "vosk" / "vosk-model-small-en-us-0.15"),
}

# ── 5. TEXT-TO-SPEECH (TTS) ───────────────────────────────────────────────
#   "elevenlabs" → best quality, streaming (needs ELEVENLABS_API_KEY) ← RECOMMENDED
#   "gtts"       → Google TTS, free, good Nepali/Hindi
#   "piper"      → offline neural TTS
TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "sk_23d4f71c16ddd30523d5d931eb7e3a5e317b170fbba8c27b")
ELEVENLABS_VOICE_ID = "VR6AewLTigWG4xSOukaG"  # Arnold - strong male
"""ELEVENLABS_VOICE_ID = "pqHfZKP75CvOlQylNhV4"""

PIPER_BIN = "/home/pi/Documents/JARVIS_SUKUNA_AI/venv/bin/piper"

PIPER_MODELS = {
    "en": "/home/pi/Documents/JARVIS_SUKUNA_AI/models/piper/en_US-ryan-medium.onnx",
    "ne": "/home/pi/Documents/JARVIS_SUKUNA_AI/models/piper/en_US-ryan-medium.onnx",
    "hi": "/home/pi/Documents/JARVIS_SUKUNA_AI/models/piper/en_US-ryan-medium.onnx",
}

# ── 6. WAKE WORD ──────────────────────────────────────────────────────────
WAKE_WORDS = ["sukuna", "सुकुना", "hey sukuna"]   # say any of these

# ── 7. AUDIO ─────────────────────────────────────────────────────────────
AUDIO = {
    "sample_rate":     44100,   # USB mic only supports 44100
    "channels":        1,
    "chunk_size":      4096,
    "silence_timeout": 2.0,
    "output_volume":   1.0,     # maximum volume
    "input_device":    1,       # USB Audio Device (card 1)
    "output_device":   0,       # bcm2835 Headphones (audio jack)
}

# ── 8. SERVO / HARDWARE (PCA9685 via I2C) ────────────────────────────────
I2C_ADDRESS = 0x40              # default PCA9685 address
SERVO_FREQ  = 50                # Hz (standard servo)
SERVO_PULSE = (500, 2500)       # pulse width range for all servos

# Channel numbers on PCA9685 board — confirmed from your hardware
SERVO_CHANNELS = {
    "jaw":        0,    # jaw open/close
    "left_brow":  4,    # left eyebrow (blink up/down)
    "right_brow": 5,    # right eyebrow (mirrored)
}

# Exact angles from your working code — do not change unless servo is remounted
SERVO_LIMITS = {
    "jaw": {
        "closed": 65,   # SAFE_MIN — mouth at rest
        "open":   85,   # SAFE_MAX — mouth open while speaking
    },
    "left_brow": {
        "down": 35,     # neutral / resting position
        "up":   120,    # raised (blink / expression)
    },
    "right_brow": {
        "down": 120,    # neutral (mirrored from left)
        "up":   35,     # raised (mirrored from left)
    },
}

# Blink timing
BLINK_INTERVAL_MIN = 2.5    # seconds between blinks (random range)
BLINK_INTERVAL_MAX = 3.5    # matches your original 2.5–3.5 range
BLINK_CLOSE_SECS   = 0.10   # brow closes
BLINK_OPEN_SECS    = 0.12   # brow opens back

# ── 9. KNOWLEDGE BASE ────────────────────────────────────────────────────
KNOWLEDGE_DIR    = BASE_DIR / "knowledge"
TEACHERS_JSON    = BASE_DIR / "knowledge" / "teachers.json"  # from your PDF
QA_MIN_SCORE     = 2         # minimum keyword matches to trust a QA answer

# ── 10. PERFORMANCE ───────────────────────────────────────────────────────
TTS_CACHE_DIR    = BASE_DIR / "logs" / "tts_cache"
TTS_CACHE_ON     = True
LOGS_DIR         = BASE_DIR / "logs"
LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO")
