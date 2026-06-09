"""
================================================================
  motion/servos.py — Jaw + Eyebrow Controller
  Built from your working code — exact channels and angles.

  Hardware (PCA9685):
    Channel 0 → jaw        (65=closed, 85=open)
    Channel 4 → left brow  (35=down/neutral, 120=up/blink)
    Channel 5 → right brow (120=down/neutral, 35=up — mirrored)

  Three independent systems:
    1. Jaw   — follows audio envelope while speaking
    2. Brows — auto-blink loop in background thread
    3. Both  — respond to voice commands instantly
================================================================
"""

import math
import time
import random
import threading
import logging

from config import SERVO_CHANNELS, SERVO_LIMITS, SERVO_PULSE, I2C_ADDRESS
from config import BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX

logger = logging.getLogger("Robot.Servos")

# ── Hardware init ─────────────────────────────────────────────────────────
try:
    from adafruit_servokit import ServoKit
    _kit = ServoKit(channels=16, address=I2C_ADDRESS)
    for ch in SERVO_CHANNELS.values():
        _kit.servo[ch].set_pulse_width_range(*SERVO_PULSE)
    HARDWARE_OK = True
    logger.info("PCA9685 ready — jaw ch0, left brow ch4, right brow ch5")
except Exception as e:
    _kit = None
    HARDWARE_OK = False
    logger.warning(f"PCA9685 not found ({e}) — dry-run mode")


def _set(channel: int, angle: float):
    """Set a servo channel to an angle. Silent no-op if no hardware."""
    if not HARDWARE_OK:
        return
    try:
        _kit.servo[channel].angle = float(angle)
    except Exception as e:
        logger.error(f"Servo ch{channel} → {angle}° failed: {e}")


def _ease(t: float) -> float:
    """
    Cosine ease-in-out — exactly from your working code.
    t=0.0 → 0.0,  t=1.0 → 1.0, smooth S-curve in between.
    """
    return -(math.cos(math.pi * t) - 1) / 2


# ── JAW ───────────────────────────────────────────────────────────────────
class Jaw:
    """
    Jaw servo on channel 0.
    - animate_from_audio() → human-like motion while speaking
    - open() / close()     → manual control from voice commands
    """

    CH      = SERVO_CHANNELS["jaw"]
    CLOSED  = SERVO_LIMITS["jaw"]["closed"]   # 65
    OPEN    = SERVO_LIMITS["jaw"]["open"]     # 85

    def open(self):
        _set(self.CH, self.OPEN)

    def close(self):
        _set(self.CH, self.CLOSED)

    def neutral(self):
        _set(self.CH, self.CLOSED)

    def animate_from_audio(self, audio_path: str):
        """
        Drive jaw while speaking.
        Uses your natural_jaw_motion logic — random micro-movements
        within the safe range, timed to audio duration.
        For MP3 files (gTTS output) it reads duration via mutagen/ffprobe,
        then runs the motion loop for exactly that long.
        """
        duration = self._get_audio_duration(audio_path)
        if duration is None or duration <= 0:
            duration = 3.0  # fallback estimate

        stop_flag = [False]

        def _motion_loop():
            while not stop_flag[0]:
                # Open — random position within safe range
                angle_open = random.uniform(self.CLOSED + 2, self.OPEN)
                self._smooth_move(self.CLOSED, angle_open, duration=0.08)

                time.sleep(random.uniform(0.04, 0.10))

                # Partial close — not fully shut (human jaw stays slightly open)
                angle_rest = random.uniform(self.CLOSED, self.CLOSED + 4)
                self._smooth_move(angle_open, angle_rest, duration=0.06)

                time.sleep(random.uniform(0.03, 0.08))

        t = threading.Thread(target=_motion_loop, daemon=True)
        t.start()
        time.sleep(duration)
        stop_flag[0] = True
        t.join(timeout=1.0)
        self.neutral()

    def _smooth_move(self, start: float, end: float,
                     duration: float = 0.08, steps: int = 20):
        """Move smoothly with cosine easing — from your working code."""
        for i in range(steps + 1):
            t = i / steps
            e = _ease(t)
            _set(self.CH, start + e * (end - start))
            time.sleep(duration / steps)

    def _get_audio_duration(self, path: str):
        """Get audio file duration in seconds."""
        # Method 1: mutagen (lightweight)
        try:
            from mutagen.mp3 import MP3
            return MP3(path).info.length
        except Exception:
            pass
        # Method 2: ffprobe
        try:
            import subprocess, json
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", path],
                capture_output=True, timeout=5
            )
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        except Exception:
            pass
        # Method 3: wave module (WAV only)
        try:
            import wave
            with wave.open(path) as wf:
                return wf.getnframes() / wf.getframerate()
        except Exception:
            pass
        return None


# ── EYEBROWS ──────────────────────────────────────────────────────────────
class Eyebrows:
    """
    Eyebrow servos on channels 4 (left) and 5 (right).
    Left and right are mirrored — when left goes UP, right goes DOWN.
    Auto-blink loop runs in a background thread.
    """

    L_CH    = SERVO_CHANNELS["left_brow"]    # 4
    R_CH    = SERVO_CHANNELS["right_brow"]   # 5
    L_DOWN  = SERVO_LIMITS["left_brow"]["down"]    # 35  — neutral
    L_UP    = SERVO_LIMITS["left_brow"]["up"]      # 120 — raised
    R_DOWN  = SERVO_LIMITS["right_brow"]["down"]   # 120 — neutral (mirrored)
    R_UP    = SERVO_LIMITS["right_brow"]["up"]     # 35  — raised (mirrored)

    def __init__(self):
        self._stop  = threading.Event()
        self._thread = None
        self.neutral()

    # ── Positions ─────────────────────────────────────────────────────────
    def neutral(self):
        """Resting position — brows down."""
        _set(self.L_CH, self.L_DOWN)
        _set(self.R_CH, self.R_DOWN)

    def raise_brows(self):
        """Raise both brows — surprise / expression."""
        _set(self.L_CH, self.L_UP)
        _set(self.R_CH, self.R_UP)

    # ── Smooth move (cosine easing — your exact logic) ────────────────────
    def _move(self, l_target: float, r_target: float,
              duration: float = 0.12, steps: int = 40):
        """
        Move both brows simultaneously with cosine easing.
        Reads current angles as starting points.
        """
        try:
            l_start = float(_kit.servo[self.L_CH].angle or self.L_DOWN)
            r_start = float(_kit.servo[self.R_CH].angle or self.R_DOWN)
        except Exception:
            l_start = self.L_DOWN
            r_start = self.R_DOWN

        for i in range(steps + 1):
            t = i / steps
            e = _ease(t)
            _set(self.L_CH, l_start + e * (l_target - l_start))
            _set(self.R_CH, r_start + e * (r_target - r_start))
            time.sleep(duration / steps)

    # ── Blink cycle ───────────────────────────────────────────────────────
    def blink(self):
        """
        One full blink cycle — exactly your EyebrowController.blink() logic:
        slight raise → close down → open back → neutral
        """
        # Slight expressive lift before blink
        self._move(self.L_UP + 5, self.R_UP - 5, duration=0.12)
        # Close (blink)
        self._move(self.L_DOWN, self.R_DOWN, duration=0.10)
        # Open back
        self._move(self.L_UP, self.R_UP, duration=0.12)
        # Return to neutral
        self.neutral()

    # ── Auto blink loop ───────────────────────────────────────────────────
    def start_auto_blink(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._blink_loop, daemon=True, name="BrowBlinkLoop"
        )
        self._thread.start()
        logger.info("Eyebrow blink loop started")

    def stop_auto_blink(self):
        self._stop.set()

    def _blink_loop(self):
        """Blinks every 2.5–3.5 s — your original timing."""
        while not self._stop.is_set():
            interval = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
            # Sleep in 0.1s chunks so stop event is caught quickly
            for _ in range(int(interval / 0.1)):
                if self._stop.is_set():
                    return
                time.sleep(0.1)
            self.blink()
            logger.debug("Auto blink")


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────
class RobotServos:
    """
    Single object used by robot.py and the intent parser.
    Create once at startup — blink loop starts automatically.
    """

    def __init__(self):
        self.jaw      = Jaw()
        self.eyebrows = Eyebrows()
        self.eyebrows.start_auto_blink()
        logger.info("RobotServos ready")

    def execute_command(self, servo: str, action: str):
        """
        Called by intent_parser when user says a servo command.
        Examples: "aankha khol", "jaw band kar", "jhapki maar"
        """
        cmd = (servo, action)

        if   cmd == ("jaw",   "open"):   self.jaw.open()
        elif cmd == ("jaw",   "close"):  self.jaw.close()
        elif cmd == ("eyes",  "open"):   self.eyebrows.raise_brows()
        elif cmd == ("eyes",  "close"):  self.eyebrows.neutral()
        elif cmd == ("eyes",  "blink"):  self.eyebrows.blink()
        elif cmd == ("eyes",  "blink2"):
            self.eyebrows.blink()
            time.sleep(0.3)
            self.eyebrows.blink()
        else:
            logger.warning(f"Unknown command: {servo}/{action}")

    def shutdown(self):
        """Return everything to neutral on exit."""
        self.eyebrows.stop_auto_blink()
        self.jaw.neutral()
        self.eyebrows.neutral()
        logger.info("Servos at neutral — shutdown complete")
