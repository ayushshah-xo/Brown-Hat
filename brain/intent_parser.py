"""
================================================================
  brain/intent_parser.py — Servo Command Detector
  Detects physical commands BEFORE hitting the LLM.
  "Open your eyes" fires the servo in ~50 ms, no API call.
  Supports Nepali, Hindi, and English phrases.
================================================================
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("Robot.IntentParser")

# ── Pattern → (servo, action) map ────────────────────────────────────────
# Each key is a regex pattern. First match wins.
SERVO_PATTERNS = [
    # ── Eyes / आँखा ──────────────────────────────────────────────────────
    (r"(aankha|आँखा|आंख|eye|eyes).*(khol|kholnus|open|ugar|उगार|खोल)",     ("eyes", "open")),
    (r"(khol|open|ugar).*(aankha|आँखा|आंख|eye|eyes)",                        ("eyes", "open")),
    (r"(aankha|आँखा|आंख|eye|eyes).*(band|बन्द|बंद|close|shut)",             ("eyes", "close")),
    (r"(band|बन्द|close|shut).*(aankha|आँखा|आंख|eye|eyes)",                  ("eyes", "close")),
    (r"(jhapki|झपकी|jhap|blink|palkein|पलकें)",                              ("eyes", "blink")),
    (r"(do\s*baar|दुईपटक|दो\s*बार|twice).*(jhapki|blink|झपकी)",             ("eyes", "blink2")),

    # ── Jaw / मुख ────────────────────────────────────────────────────────
    (r"(muh|मुख|jaw|mouth).*(khol|open|kholnus|खोल)",                        ("jaw", "open")),
    (r"(khol|open).*(muh|मुख|jaw|mouth)",                                     ("jaw", "open")),
    (r"(muh|मुख|jaw|mouth).*(band|बन्द|close|shut)",                         ("jaw", "close")),
    (r"(band|close|shut).*(muh|मुख|jaw|mouth)",                               ("jaw", "close")),
]

# ── Spoken acknowledgements ────────────────────────────────────────────────
ACK = {
    ("eyes", "open"):  {
        "ne": "ठीक छ, आँखा खोल्दैछु।",
        "hi": "ठीक है, आँखें खोल रहा हूँ।",
        "en": "Sure, opening my eyes.",
    },
    ("eyes", "close"): {
        "ne": "ठीक छ, आँखा बन्द गर्दैछु।",
        "hi": "ठीक है, आँखें बंद कर रहा हूँ।",
        "en": "Closing my eyes.",
    },
    ("eyes", "blink"): {
        "ne": "झपकी मारिरहेछु!",
        "hi": "झपकी मार रहा हूँ!",
        "en": "Blinking!",
    },
    ("eyes", "blink2"): {
        "ne": "दुईपटक झपकी!",
        "hi": "दो बार झपकी!",
        "en": "Blinking twice!",
    },
    ("jaw", "open"):  {
        "ne": "मुख खोल्दैछु।",
        "hi": "मुँह खोल रहा हूँ।",
        "en": "Opening my jaw.",
    },
    ("jaw", "close"): {
        "ne": "मुख बन्द गर्दैछु।",
        "hi": "मुँह बंद कर रहा हूँ।",
        "en": "Closing my jaw.",
    },
}


def parse(text: str, language: str = "ne") -> Optional[dict]:
    """
    Check if the text contains a physical servo command.

    Returns a dict like:
        {"servo": "eyes", "action": "open", "ack": "ठीक छ, आँखा खोल्दैछु।"}
    or None if no command detected (→ send to LLM).
    """
    text_lower = text.lower().strip()

    for pattern, (servo, action) in SERVO_PATTERNS:
        if re.search(pattern, text_lower):
            ack_map = ACK.get((servo, action), {})
            ack     = ack_map.get(language, ack_map.get("ne", "ठीक छ।"))
            logger.info(f"Intent detected: {servo}/{action} | '{text[:50]}'")
            return {"servo": servo, "action": action, "ack": ack}

    return None
