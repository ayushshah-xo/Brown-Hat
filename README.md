# 🤖 Sukuna School Robot

**AI voice robot for Sukuna Secondary School, Nepal**  
Speaks Nepali 🇳🇵 • Hindi • English  
Moves jaw while talking • Blinks eyes automatically  
Answers questions about the school, teachers, and phone numbers

---

## What it does

| When you say… | Robot does… |
|---|---|
| "Anil Thapa ko number ke ho?" | Speaks the phone number |
| "Head teacher ko naam ke ho?" | Answers "Hikmat Bahadur Basnet" |
| "Aankha khol" | Opens the eye servos |
| "Jaw band gar" | Closes the jaw servo |
| "Jhapki maar" | Blinks once |
| Any other question | Asks the AI (Groq cloud or offline) |

---

## Hardware you need

| Part | Purpose |
|---|---|
| Raspberry Pi 4 (2 GB+) | Main computer |
| PCA9685 16-channel PWM board | Controls all servos via I2C |
| 3× MG90S servo motors | Jaw (ch 0), left eye (ch 1), right eye (ch 2) |
| USB microphone | Listens to voice |
| Mini speaker + 3.5mm audio | Speaks responses |
| Jumper wires | Connects everything |

**Wiring (PCA9685 → Pi 4):**
```
PCA9685 VCC  → Pi 5V  (pin 2)
PCA9685 GND  → Pi GND (pin 6)
PCA9685 SDA  → Pi SDA (pin 3, GPIO 2)
PCA9685 SCL  → Pi SCL (pin 5, GPIO 3)
```

---

## Step-by-step setup

### Step 1 — Enable I2C on your Pi
```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
sudo reboot
```

### Step 2 — Verify I2C is working
```bash
sudo apt install i2c-tools -y
i2cdetect -y 1
# You should see "40" in the grid (PCA9685 address)
```

### Step 3 — Clone the project
```bash
git clone https://github.com/ayushshah-xo/JARVIS_SUKUNA_AI.git
cd JARVIS_SUKUNA_AI
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt --break-system-packages
sudo apt install espeak-ng ffmpeg -y
```

### Step 5 — Set up your API keys
```bash
cp .env.example .env
nano .env
# Fill in GROQ_API_KEY and DEEPGRAM_API_KEY
# Get free keys at:
#   Groq    → https://console.groq.com
#   Deepgram→ https://deepgram.com
```

### Step 6 — Calibrate your servos
Open `config.py` and adjust these values until your servos move correctly:
```python
SERVO_LIMITS = {
    "jaw":       {"closed": 90, "open": 120},  # ← change these
    "left_eye":  {"open": 90,  "closed": 60},
    "right_eye": {"open": 90,  "closed": 120},
}
```
Test with:
```bash
python tests/test_servos.py
```

### Step 7 — Run the robot!
```bash
python robot.py
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'adafruit_servokit'` | Run `pip install adafruit-circuitpython-servokit --break-system-packages` |
| `PCA9685 not found` | Check I2C wiring; run `i2cdetect -y 1` to confirm address 0x40 |
| `DEEPGRAM_API_KEY not set` | Add your key to `.env` file; robot falls back to Vosk offline |
| `gTTS error / no internet` | Switch `TTS_ENGINE = "piper"` in config.py for offline TTS |
| Servo moves too far / too little | Adjust `SERVO_LIMITS` in `config.py` |
| Jaw doesn't move | Check `SERVO_CHANNELS["jaw"] = 0` matches your physical wiring |
| No sound | Run `aplay -l` to list audio devices; set `AUDIODEV` in tts.py |

---

## Project structure (clean, easy to understand)

```
sukuna_robot/
├── robot.py              ← START HERE — runs the whole robot
├── config.py             ← ALL settings in one place
├── .env                  ← Your secret API keys (never commit this)
│
├── brain/
│   ├── school_brain.py   ← Teacher lookup + school info
│   ├── intent_parser.py  ← Detects "open eyes", "close jaw" etc.
│   └── llm.py            ← AI brain (Groq / OpenAI / offline)
│
├── voice/
│   ├── stt.py            ← Microphone → text (Deepgram or Vosk)
│   └── tts.py            ← Text → speech (gTTS, ElevenLabs, Piper)
│
├── motion/
│   └── servos.py         ← Jaw + eye blink controller
│
├── knowledge/
│   └── teachers.json     ← All 146 staff from Sukuna School PDF
│
└── tests/
    └── test_servos.py    ← Test servos without running the full robot
```

---

## Adding your own school

1. Edit `SCHOOL` in `config.py`
2. Replace `knowledge/teachers.json` with your school's staff data
3. Change `DEFAULT_LANGUAGE` to `"ne"`, `"hi"`, or `"en"`

That's it — anyone can fork this for their own school!

---

## License
MIT — Free to use, modify, and share. Please credit **Sukuna Secondary School, Nepal** 🙏
