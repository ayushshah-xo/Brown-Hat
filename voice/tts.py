"""
================================================================
  voice/tts.py — Multi-Engine TTS
  Routes languages to the best available TTS engine:
    English   → ElevenLabs (human quality)
    Hindi     → ElevenLabs multilingual
    Nepali    → gTTS (best Nepali pronunciation)
================================================================
"""

import logging
import hashlib
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional
from config import (TTS_ENGINE, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID,
                    PIPER_MODELS, TTS_CACHE_DIR, TTS_CACHE_ON, AUDIO)

logger = logging.getLogger("Robot.TTS")


class TTS:
    def __init__(self):
        self._engine = TTS_ENGINE
        if TTS_CACHE_ON:
            Path(TTS_CACHE_DIR).mkdir(parents=True, exist_ok=True)

        if self._engine == "elevenlabs" and not ELEVENLABS_API_KEY:
            logger.warning("ELEVENLABS_API_KEY not set — falling back to gTTS")

            self._engine = "gtts"

        self._init_pygame()
        logger.info(f"TTS engine: {self._engine} (Nepali always uses gTTS)")

    def _init_pygame(self):
        try:
            import pygame
            os.environ.setdefault("SDL_AUDIODRIVER", "alsa")
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.music.set_volume(1.0)
            logger.info("pygame audio initialized")
        except Exception as e:
            logger.warning(f"pygame init failed: {e}")

    # ── Public interface ──────────────────────────────────────────────────
    def speak(self, text: str, lang: str = "ne", jaw=None):
        if not text or not text.strip():
            return

        wav_path = self._get_or_synthesize(text, lang)
        if not wav_path:
            logger.error("TTS synthesis failed — no audio to play")
            return

        if jaw:
            import threading
            jaw_thread = threading.Thread(
                target=jaw.animate_from_audio, args=(wav_path,), daemon=True
            )
            jaw_thread.start()
            self._play(wav_path)
            jaw_thread.join(timeout=30)
        else:
            self._play(wav_path)

    # ── Synthesis routing ─────────────────────────────────────────────────
    def _get_or_synthesize(self, text: str, lang: str) -> Optional[str]:
        if TTS_CACHE_ON:
            cached = self._cache_path(text, lang)
            if os.path.exists(cached):
                return cached

        # ── Language routing ──────────────────────────────────────────────
        # Nepali always uses gTTS — best Nepali pronunciation
            if lang == "ne":
                logger.debug("Nepali → ElevenLabs Arnold")
                return self._elevenlabs_synthesize(text, lang)

        # English and Hindi use ElevenLabs if available
            logger.warning("ElevenLabs failed — using gTTS")

        return self._gtts_synthesize(text, lang)

        # Fallback chain
        if self._engine == "piper":
            return self._piper_synthesize(text, lang)

        return self._gtts_synthesize(text, lang)

    # ── gTTS (Nepali/fallback) ────────────────────────────────────────────
    def _gtts_synthesize(self, text: str, lang: str) -> Optional[str]:
        try:
            from gtts import gTTS
            # Nepali: use 'ne' directly
            # Hindi: use 'hi'
            # English: use 'en' with Indian accent for clarity
            lang_map = {
                "ne": ("ne", "com"),
                "hi": ("hi", "co.in"),
                "en": ("en", "co.in"),
            }
            tts_lang, tld = lang_map.get(lang, ("ne", "com"))

            out_path = (self._cache_path(text, lang) if TTS_CACHE_ON
                        else tempfile.mktemp(suffix=".mp3"))
            tts = gTTS(text=text, lang=tts_lang, slow=False, tld=tld)
            tts.save(out_path)
            logger.debug(f"gTTS [{lang}] → {out_path}")
            return out_path
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return self._espeak_fallback(text, lang)

    # ── ElevenLabs (English + Hindi) ──────────────────────────────────────
    def _elevenlabs_synthesize(self, text: str, lang: str) -> Optional[str]:
        try:
            import httpx
            out_path = (self._cache_path(text, lang) if TTS_CACHE_ON
                        else tempfile.mktemp(suffix=".mp3"))

            # Use multilingual model for Hindi, standard for English
            model = ("eleven_multilingual_v2" if lang == "hi"
                     else "eleven_multilingual_v2")

            resp = httpx.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                json={
                    "text": text,
                    "model_id": model,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.8,
                        "style": 0.2,
                        "use_speaker_boost": True,
                    },
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(resp.content)
            logger.debug(f"ElevenLabs [{lang}] → {out_path}")
            return out_path
        except Exception as e:
            logger.warning(f"ElevenLabs failed ({e}) — falling back to gTTS")
            return self._gtts_synthesize(text, lang)

    # ── Piper (offline) ───────────────────────────────────────────────────
    def _piper_synthesize(self, text: str, lang: str) -> Optional[str]:
        model_path = PIPER_MODELS.get(lang, PIPER_MODELS.get("en"))
        if not model_path or not os.path.exists(model_path):
            return self._gtts_synthesize(text, lang)
        try:
            try:
                from config import PIPER_BIN
                piper_bin = PIPER_BIN
            except ImportError:
                piper_bin = "/home/pi/Documents/JARVIS_SUKUNA_AI/venv/bin/piper"

            out_path = (self._cache_path(text, lang) if TTS_CACHE_ON
                        else tempfile.mktemp(suffix=".wav"))
            result = subprocess.run(
                [piper_bin, "--model", model_path, "--output_file", out_path],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=15,
            )
            if result.returncode == 0 and os.path.exists(out_path):
                return out_path
            return self._gtts_synthesize(text, lang)
        except Exception as e:
            logger.warning(f"Piper error ({e}) — using gTTS")
            return self._gtts_synthesize(text, lang)

    # ── espeak fallback ───────────────────────────────────────────────────
    def _espeak_fallback(self, text: str, lang: str) -> Optional[str]:
        logger.warning("Using espeak-ng fallback")
        lang_map = {"ne": "hi", "hi": "hi", "en": "en"}
        try:
            subprocess.run(
                ["espeak-ng", "-v", lang_map.get(lang, "en"),
                 "-s", "150", "-a", "200", text],
                timeout=10, check=False,
            )
        except Exception as e:
            logger.error(f"espeak-ng failed: {e}")
        return None

    # ── Playback with volume boost ────────────────────────────────────────
    def _play(self, audio_path: str):
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return

        # Boost with sox
        play_path = audio_path
        try:
            boosted = audio_path + "_boosted.wav"
            result = subprocess.run(
                ["sox", audio_path, "-r", "44100", boosted, "vol", "3.0"],
                capture_output=True, timeout=10
            )
            if os.path.exists(boosted) and os.path.getsize(boosted) > 0:
                play_path = boosted
        except Exception:
            play_path = audio_path

        try:
            import pygame
            import time
            pygame.mixer.music.load(play_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
        except Exception as e:
            logger.warning(f"pygame failed ({e}) — trying aplay")
            try:
                subprocess.run(
                    ["aplay", "-D", "plughw:0,0", play_path],
                    check=False, timeout=30
                )
            except Exception as e2:
                logger.error(f"aplay also failed: {e2}")
        finally:
            try:
                if play_path != audio_path and os.path.exists(play_path):
                    os.unlink(play_path)
            except Exception:
                pass

    # ── Cache helpers ─────────────────────────────────────────────────────
    def _cache_path(self, text: str, lang: str) -> str:
        # Include engine in cache key so ne/en don't conflict
        engine = "gtts" if lang == "ne" else self._engine
        h = hashlib.md5(f"{engine}:{lang}:{text}".encode()).hexdigest()
        ext = "wav" if self._engine == "piper" else "mp3"
        return str(Path(TTS_CACHE_DIR) / f"{h}.{ext}")