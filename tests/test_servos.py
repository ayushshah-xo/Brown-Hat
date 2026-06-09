"""
================================================================
  tests/test_servos.py — Servo Calibration Tool
  Run this FIRST to make sure your servos work correctly.
  Usage:  python tests/test_servos.py
================================================================
"""

import sys
import time
sys.path.insert(0, "..")

print("\n=== Sukuna Robot — Servo Test ===\n")

try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
    for ch in [3, 0, 5]:
        kit.servo[ch].set_pulse_width_range(500, 2500)
    print("✅  PCA9685 found — hardware mode\n")
    HW = True
except Exception as e:
    print(f"⚠️  PCA9685 not found ({e})\n   Running in PRINT-ONLY mode.\n")
    HW = False


def move(channel, angle, label):
    print(f"   Channel {channel} ({label}) → {angle}°")
    if HW:
        kit.servo[channel].angle = angle
    time.sleep(1.0)


print("── TEST 1: Jaw ──────────────────────────────")
print("  Jaw should CLOSE (neutral position)")
move(0, 90, "jaw closed")
print("  Jaw should OPEN")
move(0, 120, "jaw open")
print("  Jaw back to closed")
move(0, 90, "jaw closed")

print("\n── TEST 2: Left Eye ─────────────────────────")
print("  Left eye should be OPEN")
move(1, 90, "left eye open")
print("  Left eye should CLOSE (blink down)")
move(1, 60, "left eye closed")
print("  Left eye back to open")
move(1, 90, "left eye open")

print("\n── TEST 3: Right Eye ────────────────────────")
print("  Right eye should be OPEN")
move(2, 90, "right eye open")
print("  Right eye should CLOSE (mirror of left)")
move(2, 120, "right eye closed")
print("  Right eye back to open")
move(2, 90, "right eye open")

print("\n── TEST 4: Blink both eyes ──────────────────")
print("  Both eyes should blink together")
if HW:
    kit.servo[1].angle = 60
    kit.servo[2].angle = 120
    time.sleep(0.15)
    kit.servo[1].angle = 90
    kit.servo[2].angle = 90
    time.sleep(0.5)
print("  Blink complete")

print("""
══════════════════════════════════════════════
  ✅  Test complete!

  If any servo moved the WRONG way:
  → Open config.py
  → Adjust SERVO_LIMITS for that servo
  → Run this test again

  Example fix — jaw opens wrong way:
    "jaw": {"closed": 90, "open": 60}   ← swap these numbers
══════════════════════════════════════════════
""")
