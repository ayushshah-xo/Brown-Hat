"""
================================================================
  voice/stt.py — Speech-to-Text Engine  (v2 — Better Listening)
  Deepgram cloud (~200 ms) with improved mic handling.

  KEY IMPROVEMENTS over v1:
  ─────────────────────────
  • Visual mic level bar in terminal — you can SEE if it hears you
  • Waits for speech to START before starting silence timer
  • Longer silence timeout (3.0s) — doesn't cut off mid-sentence
  • RMS threshold auto-calibrated from ambient noise at startup
  • Sends 44100 Hz audio directly — no resampling artifacts
  • Clear terminal feedback: WAITING → HEARING → PROCESSING
================================================================
"""

import logging
import queue
import time
import threading
import wave
import tempfile
import sys
from typing import Optional
from config import AUDIO, STT_ENGINE, DEEPGRAM_API_KEY, VOSK_MODELS

logger = logging.getLogger("Robot.STT")

# ── Listening constants ───────────────────────────────────────────────────
SILENCE_TIMEOUT   = 3.0    # seconds of silence before stopping (was 2.0)
SPEECH_TIMEOUT    = 15.0   # max seconds to wait for speech to begin
MIN_SPEECH_RMS    = 0.030  # minimum RMS to count as speech (calibrated below)
SHOW_LEVEL_BAR    = True   # show visual mic level in terminal


class STT:
    def __init__(self):
        self._engine = STT_ENGINE
        self._vosk_recognizers: dict = {}
        self._vosk_models: dict = {}
        self._noise_floor = MIN_SPEECH_RMS   # calibrated at startup

        if self._engine == "deepgram" and not DEEPGRAM_API_KEY:
            logger.warning("DEEPGRAM_API_KEY not set — falling back to Vosk")
            self._engine = "vosk"

        if self._engine == "vosk":
            self._preload_vosk("ne")
            logger.info("STT engine: Vosk (offline)")
        else:
            logger.info("STT engine: Deepgram (cloud ~200 ms)")

        # Calibrate noise floor
        self._calibrate_noise()

    # ── Noise calibration ─────────────────────────────────────────────────
    def _calibrate_noise(self):
        """
        Listen for 0.5 seconds at startup to measure ambient noise.
        Sets the speech threshold just above background noise level.
        """
        try:
            import sounddevice as sd
            import numpy as np
            samples = []

            def cb(indata, frames, t, status):
                samples.append(bytes(indata))

            with sd.RawInputStream(
                samplerate=AUDIO["sample_rate"],
                blocksize=AUDIO["chunk_size"],
                dtype="int16",
                channels=AUDIO["channels"],
                device=AUDIO.get("input_device"),
                callback=cb,
            ):
                time.sleep(0.5)

            if samples:
                audio = []
                for s in samples:
                    import numpy as np
                    audio.extend(
                        np.frombuffer(s, dtype=np.int16)
                        .astype(np.float32)
                    )
                import numpy as np
                arr = np.array(audio) / 32768.0
                rms = float(np.sqrt(np.mean(arr ** 2)))
                # Set threshold 3x above noise floor, minimum 0.008
                self._noise_floor = max(0.008, rms * 1.2)
                logger.info(f"Noise floor calibrated: {self._noise_floor:.4f}")
        except Exception as e:
            logger.debug(f"Noise calibration skipped: {e}")

    # ── Public interface ──────────────────────────────────────────────────
    def listen(self, language: str = "ne", timeout: float = SPEECH_TIMEOUT) -> Optional[str]:
        """
        Record from mic until silence, then transcribe.
        Shows visual level bar so user knows the mic is active.
        Returns transcribed string or None.
        """
        logger.info(f"Listening [{language}]...")
        audio_bytes = self._record_with_feedback(timeout)

        if not audio_bytes:
            return None

        print("\r  🔄  Processing speech...                    ", flush=True)

        if self._engine == "deepgram":
            return self._deepgram_transcribe(audio_bytes, language)
        else:
            return self._vosk_transcribe(audio_bytes, language)

    # ── Recording with visual feedback ────────────────────────────────────
    def _record_with_feedback(self, timeout: float) -> Optional[bytes]:
        """
        Record audio with:
        - Visual RMS bar so user sees mic activity
        - Waits for speech to START before counting silence
        - Stops after SILENCE_TIMEOUT seconds of silence after speech
        """
        try:
            import sounddevice as sd
            import numpy as np
        except ImportError:
            logger.error("sounddevice not installed")
            return None

        frames          = []
        silence_count   = [0]
        speech_started  = [False]
        done            = threading.Event()
        SILENCE_CHUNKS  = int(
            AUDIO["sample_rate"] * SILENCE_TIMEOUT / AUDIO["chunk_size"]
        )

        def callback(indata, frame_count, time_info, status):
            raw = bytes(indata)
            frames.append(raw)

            # Compute RMS
            arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
            rms = float(np.sqrt(np.mean(arr ** 2))) / 32768.0

            # Visual bar
            if SHOW_LEVEL_BAR:
                bar_len  = int(rms * 400)
                bar      = "█" * min(bar_len, 30)
                spaces   = " " * (30 - len(bar))
                status_s = "🎤 HEARING " if rms > self._noise_floor else "👂 WAITING "
                print(
                    f"\r  {status_s} [{bar}{spaces}] {rms:.3f}   ",
                    end="", flush=True
                )

            # Speech detection logic
            if rms > self._noise_floor:
                speech_started[0] = True
                silence_count[0]  = 0
            else:
                if speech_started[0]:
                    silence_count[0] += 1
                    if silence_count[0] >= SILENCE_CHUNKS:
                        done.set()

        print(
            f"\r  👂 WAITING  [{'─'*30}] speak now...   ",
            flush=True
        )

        try:
            with sd.RawInputStream(
                samplerate=AUDIO["sample_rate"],
                blocksize=AUDIO["chunk_size"],
                dtype="int16",
                channels=AUDIO["channels"],
                device=AUDIO.get("input_device"),
                callback=callback,
            ):
                done.wait(timeout=timeout)
        except Exception as e:
            logger.error(f"Microphone error: {e}")
            print()
            return None

        print()  # newline after level bar

        if not speech_started[0]:
            logger.debug("No speech detected within timeout")
            return None

        return b"".join(frames) if frames else None

    def _bytes_to_wav(self, raw_pcm: bytes) -> str:
        tmp = tempfile.mktemp(suffix=".wav")
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(AUDIO["channels"])
            wf.setsampwidth(2)
            wf.setframerate(AUDIO["sample_rate"])
            wf.writeframes(raw_pcm)
        return tmp

    # ── Deepgram ──────────────────────────────────────────────────────────
    def _deepgram_transcribe(self, raw_pcm: bytes, language: str) -> Optional[str]:
        wav_path = self._bytes_to_wav(raw_pcm)
        try:
            import httpx
            with open(wav_path, "rb") as f:
                data = f.read()

            resp = httpx.post(
                "https://api.deepgram.com/v1/listen"
                "?model=nova-2-general&detect_language=true&punctuate=true",
                headers={
                    "Authorization": f"Token {DEEPGRAM_API_KEY}",
                    "Content-Type": "audio/wav",
                },
                content=data,
                timeout=8.0,
            )
            resp.raise_for_status()
            result   = resp.json()
            text     = (result["results"]["channels"][0]
                        ["alternatives"][0]["transcript"].strip())
            detected = (result["results"]["channels"][0]
                        .get("detected_language", language))
            logger.info(f"Deepgram [{detected}]: '{text}'")
            return text or None

        except Exception as e:
            logger.warning(f"Deepgram failed ({e}) — falling back to Vosk")
            return self._vosk_transcribe(raw_pcm, language)
        finally:
            import os
            try:
                os.unlink(wav_path)
            except Exception:
                pass

    # ── Vosk ──────────────────────────────────────────────────────────────
    def _preload_vosk(self, language: str):
        model_path = VOSK_MODELS.get(language)
        if not model_path:
            return
        import os
        if not os.path.exists(model_path):
            logger.warning(f"Vosk model not found: {model_path}")
            return
        try:
            from vosk import Model, KaldiRecognizer
            m = Model(model_path)
            r = KaldiRecognizer(m, AUDIO["sample_rate"])
            self._vosk_models[language]      = m
            self._vosk_recognizers[language] = r
            logger.info(f"Vosk [{language}] loaded")
        except Exception as e:
            logger.error(f"Vosk load failed [{language}]: {e}")

    def _vosk_transcribe(self, raw_pcm: bytes, language: str) -> Optional[str]:
        import json
        if language not in self._vosk_recognizers:
            self._preload_vosk(language)
        rec = self._vosk_recognizers.get(language)
        if not rec:
            logger.error("No Vosk recognizer available")
            return None
        try:
            from vosk import KaldiRecognizer
            fresh = KaldiRecognizer(
                self._vosk_models[language], AUDIO["sample_rate"]
            )
            chunk = 4096
            for i in range(0, len(raw_pcm), chunk):
                fresh.AcceptWaveform(raw_pcm[i: i + chunk])
            result = json.loads(fresh.FinalResult())
            text   = result.get("text", "").strip()
            logger.info(f"Deepgram [{detected}]: '{text}'")
            VALID_LANGS = {"ne", "hi", "en", "en-IN", "en-US"}
            if detected not in VALID_LANGS and text:
                logger.warning(f"Rejected: detected [{detected}] not in valid langs")
                return None
            return text or None
        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")
            return None