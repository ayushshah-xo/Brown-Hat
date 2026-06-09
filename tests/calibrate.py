"""
================================================================
  tests/calibrate.py — Interactive Servo Calibration
  Run this to find the EXACT right angles for YOUR servos.
  Usage:  python tests/calibrate.py
================================================================
"""
import sys, time
sys.path.insert(0, "..")

print("\n" + "="*55)
print("  SUKUNA ROBOT — Interactive Servo Calibration")
print("="*55)

try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
    for ch in [0, 4, 5]:
        kit.servo[ch].set_pulse_width_range(500, 2500)
    HW = True
    print("  ✅  PCA9685 found — REAL servos will move\n")
except Exception as e:
    kit = None
    HW = False
    print(f"  ⚠️   No hardware ({e})\n  Running in print-only mode.\n")

def move(ch, angle):
    print(f"     Channel {ch} → {angle}°")
    if HW:
        try:
            kit.servo[ch].angle = angle
        except Exception as e:
            print(f"     ERROR: {e}")
    time.sleep(0.6)

def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        sys.exit(0)

# ── Which channels are plugged in? ────────────────────────────
print("  First — tell me which channel each servo is on.")
print("  Look at your PCA9685 board. The channels are numbered")
print("  0-15 on the board itself.\n")

jaw_ch      = ask("  What channel is JAW plugged into? [default=0]: ") or "0"
left_eye_ch = ask("  What channel is LEFT EYE plugged into? [default=1]: ") or "1"
right_eye_ch= ask("  What channel is RIGHT EYE plugged into? [default=2]: ") or "2"

jaw_ch       = int(jaw_ch)
left_eye_ch  = int(left_eye_ch)
right_eye_ch = int(right_eye_ch)

print(f"\n  Using: jaw=ch{jaw_ch}  left_eye=ch{left_eye_ch}  right_eye=ch{right_eye_ch}\n")

# ── JAW calibration ───────────────────────────────────────────
print("─"*55)
print("  JAW CALIBRATION")
print("─"*55)
print("  I will sweep the jaw servo from 60° to 150°.")
print("  Watch it move and note which angle looks natural.\n")

jaw_closed = 90
jaw_open   = 120

print("  Sweeping jaw now...")
for angle in range(60, 151, 10):
    move(jaw_ch, angle)
    print(f"     Current angle: {angle}°  ← does this look like 'mouth closed'? (y/n)")

v = ask("\n  What angle should CLOSED (rest position) be? [default=90]: ") or "90"
jaw_closed = int(v)
move(jaw_ch, jaw_closed)
print(f"  Jaw closed at {jaw_closed}° — does it look closed? ", end="")
ask("Press Enter to continue...")

v = ask(f"  What angle should OPEN (max open) be? [default=120]: ") or "120"
jaw_open = int(v)
move(jaw_ch, jaw_open)
print(f"  Jaw open at {jaw_open}° — does it look naturally open? ", end="")
ask("Press Enter to continue...")

move(jaw_ch, jaw_closed)

# ── LEFT EYE calibration ──────────────────────────────────────
print("\n" + "─"*55)
print("  LEFT EYE CALIBRATION")
print("─"*55)

left_open   = 60
left_closed = 90

print("  Sweeping left eye servo...")
for angle in range(50, 131, 10):
    move(left_eye_ch, angle)

v = ask("\n  What angle = eye OPEN (normal position)? [default=90]: ") or "90"
left_open = int(v)
move(left_eye_ch, left_open)
ask("  Good? Press Enter to continue...")

v = ask(f"  What angle = eye CLOSED (blink)? [default=60]: ") or "60"
left_closed = int(v)
move(left_eye_ch, left_closed)
time.sleep(0.15)
move(left_eye_ch, left_open)
ask("  Did it blink? Press Enter to continue...")

# ── RIGHT EYE calibration ─────────────────────────────────────
print("\n" + "─"*55)
print("  RIGHT EYE CALIBRATION")
print("─"*55)

right_open   = 60
right_closed = 90

print("  Sweeping right eye servo...")
for angle in range(50, 131, 10):
    move(right_eye_ch, angle)

v = ask("\n  What angle = eye OPEN? [default=90]: ") or "90"
right_open = int(v)
move(right_eye_ch, right_open)
ask("  Good? Press Enter to continue...")

v = ask(f"  What angle = eye CLOSED (blink)? [default=120]: ") or "120"
right_closed = int(v)
move(right_eye_ch, right_closed)
time.sleep(0.15)
move(right_eye_ch, right_open)
ask("  Did it blink? Press Enter to continue...")

# ── Test blink together ───────────────────────────────────────
print("\n  Testing BOTH eyes blinking together...")
move(left_eye_ch,  left_closed)
move(right_eye_ch, right_closed)
time.sleep(0.12)
move(left_eye_ch,  left_open)
move(right_eye_ch, right_open)
ask("  Both eyes blinked? Press Enter to see your config...")

# ── Print the config block to copy ────────────────────────────
print("\n" + "="*55)
print("  ✅  COPY THIS INTO config.py")
print("="*55)
print(f"""
SERVO_CHANNELS = {{
    "jaw":       {jaw_ch},
    "left_eye":  {left_eye_ch},
    "right_eye": {right_eye_ch},
}}

SERVO_LIMITS = {{
    "jaw": {{
        "closed": {jaw_closed},
        "open":   {jaw_open},
    }},
    "left_eye": {{
        "open":   {left_open},
        "closed": {left_closed},
    }},
    "right_eye": {{
        "open":   {right_open},
        "closed": {right_closed},
    }},
}}
""")
print("  Open config.py and replace the SERVO_CHANNELS and")
print("  SERVO_LIMITS sections with the values above.")
print("="*55 + "\n")
