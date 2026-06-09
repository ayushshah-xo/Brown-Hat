"""
================================================================
  robot.py — Main Entry Point
  Run this file to start the robot:
      python robot.py

  The boot order is:
    1. Servos  → jaw + eye blink (starts immediately)
    2. STT     → microphone listener
    3. TTS     → speaker
    4. School  → knowledge base (teachers, school info)
    5. LLM     → AI brain (Groq / OpenAI / offline)
    6. Listen  → main loop

  Press Ctrl+C to stop cleanly.
================================================================
"""

import sys
import time
import logging
import importlib
import brain.web_search as _ws_module
importlib.reload(_ws_module)
from brain.web_search import search as web_search, needs_search
from voice.song_player import wants_song, play_song
from pathlib import Path
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['ALSA_CARD'] = '0'

# ── Logging setup ─────────────────────────────────────────────────────────
from config import LOGS_DIR, LOG_LEVEL, SCHOOL, DEFAULT_LANGUAGE

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(name)-18s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOGS_DIR / "robot.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("Robot.Main")


# ── Greeting messages ─────────────────────────────────────────────────────
GREETINGS = {
    "ne": "नमस्ते! म {name} हुँ, {school} को AI सहयोगी। 'सुकुना' भन्नुस् र म सुन्नेछु।",
    "hi": "नमस्ते! मैं {name} हूँ, {school} का AI सहायक। 'सुकुना' बोलिए और मैं सुनूँगा।",
    "en": "Hello! I am {name}, the AI assistant for {school}. Say 'Sukuna' and I will listen.",
}
READY_PROMPT = {
    "ne": "हजुर? म सुनिरहेछु।",
    "hi": "जी? मैं सुन रहा हूँ।",
    "en": "Yes? I am listening.",
}
FALLBACK = {
    "ne": "माफ गर्नुस्, मैले बुझिनँ। फेरि भन्नुस् कि?",
    "hi": "माफ कीजिए, मैं समझ नहीं पाया। फिर बोलिए?",
    "en": "Sorry, I did not understand. Could you say that again?",
}


class Robot:
    def __init__(self):
        self.language = DEFAULT_LANGUAGE
        self.servos   = None
        self.stt      = None
        self.tts      = None
        self.school   = None
        self.llm      = None

    # ── Boot ──────────────────────────────────────────────────────────────
    def boot(self):
        self._banner()

        self._step("Servo motors", self._init_servos)
        self._step("Speech recognition", self._init_stt)
        self._step("Text-to-speech", self._init_tts)
        self._step("School knowledge", self._init_school)
        self._step("AI brain", self._init_llm)

        self._greet()
        self._run()

    def _init_servos(self):
        from motion.servos import RobotServos
        self.servos = RobotServos()   # starts eye blink loop automatically

    def _init_stt(self):
        from voice.stt import STT
        self.stt = STT()

    def _init_tts(self):
        from voice.tts import TTS
        self.tts = TTS()

    def _init_school(self):
        from brain.school_brain import SchoolBrain
        self.school = SchoolBrain()

    def _init_llm(self):
        from brain.llm import LLMBrain
        self.llm = LLMBrain()

    # ── Main loop ─────────────────────────────────────────────────────────
    def _run(self):
        """
        Main event loop.
        Waits for wake word, then starts listen→think→speak cycle.
        Runs forever until Ctrl+C.
        """
        logger.info("Robot is running. Say the wake word to start.")
        print("\n  ✅  Robot is ready. Say 'Sukuna' or press Enter to talk.\n")

        try:
            while True:
                # For simplicity without a TFLite wake word model,
                # we use Enter key OR a simple audio energy threshold.
                try:
                    input("  ↵  Press Enter to talk (or Ctrl+C to quit): ")
                except EOFError:
                    # Running headless — just listen on energy threshold
                    time.sleep(0.5)
                    self._interaction_cycle()
                    continue

                self._interaction_cycle()

        except KeyboardInterrupt:
            self._shutdown()

    def _interaction_cycle(self):
        """One full listen → think → speak cycle."""
        import brain.intent_parser as intent_parser

        # Acknowledge
        self._say(READY_PROMPT.get(self.language, READY_PROMPT["ne"]))

        # Listen
        logger.info("Listening for user input...")
        user_text = self.stt.listen(language=self.language)

        if not user_text:
            logger.info("Nothing heard")
            self._say(FALLBACK.get(self.language, FALLBACK["en"]))
            return

        logger.info(f"User: '{user_text}'")
        print(f"\n  🎤  You said: {user_text}")

        # ── 0. Song request ───────────────────────────────────────────────
        song_path = wants_song(user_text)
        if song_path:
            logger.info(f"Song request: {song_path}")
            play_song(song_path, jaw=None, tts=self.tts, lang=self.language)
            return

        # ── 1. Check for servo command (fires instantly, no LLM) ──────────
        cmd = intent_parser.parse(user_text, language=self.language)
        if cmd:
            logger.info(f"Servo command: {cmd['servo']}/{cmd['action']}")
            if self.servos:
                if cmd["action"] == "blink2":
                    self.servos.eyes.blink_once()
                    time.sleep(0.3)
                    self.servos.eyes.blink_once()
                else:
                    self.servos.execute_command(cmd["servo"], cmd["action"])
            self._say(cmd["ack"])
            return

        # ── 2. Try school knowledge base ──────────────────────────────────
        if self.school:
            answer = self.school.answer(user_text, language=self.language)
            if answer:
                logger.info("Answered from school knowledge base")
                print(f"  🤖  Sukuna: {answer}")
                self._say(answer)
                return

# ── 3. Web search for news/general questions ──────────────────────
        if needs_search(user_text):
            logger.info("Searching web...")
            print("  🌐  Searching the web...")
            try:
                answer = web_search(user_text, language=self.language)
            except Exception as e:
                logger.error(f"Web search failed: {e}")
                answer = None
                logger.info(f"Web search answer value: '{answer}'")
            if answer:
                if answer:
                    logger.info(f"Web answer: '{answer[:80]}'")
                print(f"  🤖  Sukuna: {answer}")
                # News is always in English
                jaw = self.servos.jaw if self.servos else None
                self.tts.speak(answer, lang="en", jaw=jaw)
                return
            else:
                logger.info(f"DEBUG web answer = {repr(answer)}")

        # ── 4. Ask the LLM (cloud or offline) ────────────────────────────
        if self.llm:
            logger.info("Asking LLM...")
            answer = self.llm.query(user_text, language=self.language)
            if answer:
                logger.info(f"LLM answer: '{answer[:80]}'")
                print(f"  🤖  Sukuna: {answer}")
                self._say(answer)
                return

        # ── 4. Fallback ───────────────────────────────────────────────────
        self._say(FALLBACK.get(self.language, FALLBACK["ne"]))

    # ── Helpers ───────────────────────────────────────────────────────────
    def _say(self, text: str):
        """Speak text with jaw sync."""
        if not text or not self.tts:
            return
        jaw = self.servos.jaw if self.servos else None
        self.tts.speak(text, lang=self.language, jaw=jaw)

    def _greet(self):
        msg_template = GREETINGS.get(self.language, GREETINGS["ne"])
        msg = msg_template.format(
            name=SCHOOL["robot_name"],
            school=SCHOOL["name"],
        )
        logger.info(f"Startup greeting: {msg}")
        self._say(msg)

    def _shutdown(self):
        logger.info("Shutting down...")
        if self.servos:
            self.servos.shutdown()
        logger.info("Goodbye.")
        sys.exit(0)

    def _step(self, name: str, fn):
        try:
            print(f"  → Loading {name}...", end=" ", flush=True)
            fn()
            print("✓")
            logger.info(f"{name} ready")
        except Exception as e:
            print(f"⚠️  (non-fatal: {e})")
            logger.warning(f"{name} failed (non-fatal): {e}")

    def _banner(self):
        print("\n" + "=" * 55)
        print(f"   {SCHOOL['robot_name']} — {SCHOOL['name']}")
        print(f"   Nepal | Language: {DEFAULT_LANGUAGE.upper()}")
        print("=" * 55 + "\n")


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    robot = Robot()
    robot.boot()
