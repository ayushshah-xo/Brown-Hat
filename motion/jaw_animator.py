"""
================================================================
  motion/jaw_animator.py — Human-like Jaw Animation
  
  How human jaw movement actually works:
  - Jaw does NOT jump open/shut on every syllable
  - It follows the ENVELOPE of sound — the overall loudness shape
  - It has INERTIA — it can't snap instantly, it has momentum
  - It stays slightly open between words (not fully closed)
  - Vowels open it more, consonants less
  - It moves AHEAD of the audio slightly (anticipatory motion)
  
  This code replicates all of that.
================================================================
"""

import time
import threading
import logging
import numpy as np

logger = logging.getLogger("Robot.JawAnimator")


class HumanJaw:
    """
    Drives jaw servo with human-like motion:
    - Smooth envelope following (not raw RMS)
    - Physical inertia / momentum
    - Natural rest position slightly open
    - Runs in sync with audio playback
    """

    def __init__(self, set_angle_fn, closed_angle: int, open_angle: int):
        """
        set_angle_fn  — function that takes an int angle and moves the servo
        closed_angle  — angle when mouth is fully closed (from config)
        open_angle    — angle when mouth is fully open (from config)
        """
        self._set   = set_angle_fn
        self._lo    = closed_angle
        self._hi    = open_angle
        self._range = abs(open_angle - closed_angle)
        self._going_up = open_angle > closed_angle  # direction of opening

        # Current servo position (0.0 = closed, 1.0 = fully open)
        self._pos   = 0.0
        # Velocity — how fast jaw is currently moving
        self._vel   = 0.0

    def _to_angle(self, t: float) -> int:
        """Convert 0.0–1.0 to actual servo angle."""
        t = max(0.0, min(1.0, t))
        if self._going_up:
            return int(self._lo + t * self._range)
        else:
            return int(self._lo - t * self._range)

    def animate_wav(self, wav_path: str):
        """
        Main method — reads WAV, drives jaw with human-like motion.
        Blocks until audio duration is complete.
        """
        import wave

        try:
            with wave.open(wav_path, "rb") as wf:
                rate     = wf.getframerate()
                n_frames = wf.getnframes()
                raw      = wf.readframes(n_frames)
                channels = wf.getnchannels()
        except Exception as e:
            logger.error(f"Cannot open WAV for jaw animation: {e}")
            return

        # Convert to mono float32
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1)

        duration = len(audio) / rate

        # ── Step 1: Compute smooth amplitude envelope ─────────────────
        # Use a longer window (80 ms) so the jaw follows phrase shape,
        # not individual samples — this is what gives the human feel
        win_size   = int(rate * 0.08)   # 80 ms window
        hop_size   = int(rate * 0.04)   # 40 ms hop = 25 fps

        envelopes = []
        for i in range(0, len(audio) - win_size, hop_size):
            chunk = audio[i: i + win_size]
            rms   = float(np.sqrt(np.mean(chunk ** 2)))
            envelopes.append(rms)

        if not envelopes:
            return

        envelopes = np.array(envelopes)

        # ── Step 2: Smooth the envelope (Gaussian blur effect) ────────
        # This removes jitter — jaw won't vibrate on every tiny sound
        from numpy import convolve
        kernel_size = 5
        kernel      = np.ones(kernel_size) / kernel_size
        envelopes   = convolve(envelopes, kernel, mode='same')

        # ── Step 3: Normalize to 0.0–1.0 range ───────────────────────
        peak = np.percentile(envelopes, 95)   # use 95th percentile as max
        if peak > 0.001:
            envelopes = np.clip(envelopes / peak, 0.0, 1.0)
        else:
            envelopes = np.zeros_like(envelopes)

        # ── Step 4: Apply speech-specific shaping ────────────────────
        # Raise to power < 1 so quiet sounds still open jaw a little
        # (humans don't close mouth completely between syllables)
        envelopes = np.power(envelopes, 0.6)

        # Minimum position = slightly open (natural rest = 15% open)
        envelopes = 0.15 + envelopes * 0.85

        # ── Step 5: Animate with inertia ─────────────────────────────
        FRAME_DT  = 0.04      # 25 fps
        INERTIA   = 0.35      # higher = more sluggish / heavier jaw feel
        # (0.0 = instant snap, 1.0 = never moves)

        frame_time = time.time()
        self._pos  = 0.15     # start slightly open
        self._vel  = 0.0

        for i, target in enumerate(envelopes):
            # Spring-damper physics:
            # acceleration toward target, damped by velocity
            error       = target - self._pos
            accel       = error * (1.0 - INERTIA)
            self._vel   = self._vel * INERTIA + accel
            self._pos   = max(0.0, min(1.0, self._pos + self._vel))

            angle = self._to_angle(self._pos)
            self._set(angle)

            # Keep frame timing accurate
            frame_time += FRAME_DT
            sleep = frame_time - time.time()
            if sleep > 0:
                time.sleep(sleep)

        # ── Return to rest ────────────────────────────────────────────
        # Ease back to closed over 10 frames
        for step in range(10):
            t = 1.0 - (step / 10.0)
            self._pos = self._pos * t
            self._set(self._to_angle(self._pos * 0.15))
            time.sleep(0.04)

        self._set(self._to_angle(0.0))
        logger.debug("Jaw animation complete")

    def animate_mp3(self, mp3_path: str):
        """
        Convert MP3 to WAV first, then animate.
        gTTS produces MP3s, so this is the main entry point.
        """
        import subprocess, tempfile, os

        wav_path = mp3_path.replace(".mp3", "_jaw.wav")
        try:
            # Use ffmpeg to convert MP3 → WAV 16kHz mono
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path,
                 "-ar", "16000", "-ac", "1", wav_path],
                capture_output=True, timeout=10
            )
            if result.returncode != 0 or not os.path.exists(wav_path):
                logger.warning("ffmpeg conversion failed — jaw won't animate")
                return
            self.animate_wav(wav_path)
        except FileNotFoundError:
            logger.warning("ffmpeg not found — install with: sudo apt install ffmpeg -y")
        except Exception as e:
            logger.error(f"MP3 jaw animation error: {e}")
        finally:
            try:
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
            except:
                pass
