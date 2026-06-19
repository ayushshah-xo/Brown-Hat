<div align="center">

# 🤖 Brownhat

**Open-source AI voice robot for Sukuna Secondary School, Nepal**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Platform: Raspberry Pi 4](https://img.shields.io/badge/Platform-Raspberry%20Pi%204-C51A4A.svg)](https://www.raspberrypi.org/)
[![Languages](https://img.shields.io/badge/Languages-Nepali%20%7C%20Hindi%20%7C%20English-brightgreen.svg)]()
[![Made in Nepal](https://img.shields.io/badge/Made%20in-Nepal%20🇳🇵-blue.svg)]()

Brownhat speaks Nepali, Hindi, and English · Moves its jaw while talking · Auto-blinks eyebrows · Answers questions about the school, teachers, and the world using AI

[Features](#-features) · [Hardware](#-hardware) · [Quick Start](#-quick-start) · [Voice Commands](#-voice-commands) · [Configuration](#-configuration) · [Team](#-team)

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Hardware](#-hardware)
- [Software Architecture](#-software-architecture)
- [Quick Start](#-quick-start)
- [Voice Commands](#-voice-commands)
- [Configuration](#-configuration)
- [Adapting for Your School](#-adapting-for-your-school)
- [Troubleshooting](#-troubleshooting)
- [Team](#-team)
- [License](#-license)

---

## 🧠 About

Brownhat is a student-built, open-source humanoid AI robot designed for Sukuna Secondary School in Nepal. It answers questions about the school, looks up teacher contact details, fetches live news, and holds general-knowledge conversations — all through natural voice interaction in **Nepali, Hindi, and English**.

Built from scratch by a 16-year-old student as an affordable alternative to commercial educational robots, Brownhat runs on a Raspberry Pi 4 and falls back to **fully offline AI** when internet is unavailable.

> 📺 *Add a demo video or GIF here — link your YouTube video!*

---

## ✨ Features

| Feature | Details |
|---|---|
| 🗣️ Multilingual voice | Nepali, Hindi, and English — language auto-detected |
| 🦾 Human-like jaw animation | Jaw follows audio amplitude envelope with physical inertia |
| 👁️ Auto-blinking eyebrows | Natural random blink every 2.5–3.5 seconds |
| 🏫 School knowledge base | 145 staff members with names, subjects, and phone numbers |
| 🤖 AI conversations | Groq / Llama-3.1-8b-instant (online) or Mistral 7B GGUF (offline) |
| 🔍 Live web search | DuckDuckGo integration for news and general-knowledge queries |
| 🔇 Fully offline mode | Vosk STT + Piper TTS + Mistral — zero internet required |
| 🎵 Song playback | Plays MP3s with real-time jaw sync |
| 📖 Text reader mode | Type any text; robot reads it aloud in Nepali or English |

---

## 🔧 Hardware

### Bill of Materials

| Component | Purpose | Est. Cost |
|---|---|---|
| Raspberry Pi 4 (2 GB+) | Main compute board | ~$35 |
| PCA9685 16-channel PWM board | Servo controller over I2C | ~$5 |
| 3× MG90S servo motors | Jaw, left eyebrow, right eyebrow | ~$10 |
| USB microphone | Voice input | ~$5 |
| Mini speaker + 3.5 mm cable | Voice output | ~$5 |
| Jumper wires | Connections | ~$3 |

> 🖨️ 3D-printable head chassis files are available in the `/cad/` directory of the [Robotic_Head](https://github.com/ayushshah-xo/Robotic_Head) repository.

### Wiring — PCA9685 → Raspberry Pi 4

```
PCA9685 VCC  →  Pi 5V   (Pin 2)
PCA9685 GND  →  Pi GND  (Pin 6)
PCA9685 SDA  →  Pi SDA  (Pin 3 / GPIO 2)
PCA9685 SCL  →  Pi SCL  (Pin 5 / GPIO 3)
```

### Servo Channel Map

| Servo | PCA9685 Channel | Neutral Angle |
|---|---|---|
| Jaw | 0 | 65° (closed) |
| Left eyebrow | 4 | 35° (down) |
| Right eyebrow | 5 | 120° (down, mirrored) |

---

## 🗂️ Software Architecture

```
Brown-Hat/
├── robot.py                  ← Entry point — starts the full voice loop
├── read.py                   ← Text reader mode (type text → robot speaks it)
├── config.py                 ← All settings in one file (pins, language, AI, audio)
│
├── brain/
│   ├── school_brain.py       ← Teacher lookup + school information
│   ├── intent_parser.py      ← Servo command detection (Nepali / Hindi / English)
│   ├── llm.py                ← AI engine (Groq / OpenAI / offline Mistral)
│   └── web_search.py         ← DuckDuckGo search for news and general queries
│
├── voice/
│   ├── stt.py                ← Microphone → text (Deepgram cloud or Vosk offline)
│   ├── tts.py                ← Text → speech (gTTS / ElevenLabs / Piper)
│   └── song_player.py        ← MP3 playback with jaw sync
│
├── motion/
│   ├── servos.py             ← Jaw + eyebrow servo controller
│   └── jaw_animator.py       ← Human-like jaw motion (envelope following + inertia)
│
├── knowledge/
│   ├── teachers.json         ← 145 staff members from Sukuna Secondary School
│   └── developer.txt         ← Robot self-introduction answers
│
├── tests/
│   ├── calibrate.py          ← Interactive servo calibration tool
│   └── test_servos.py        ← Test servos without running the full robot
│
└── songs/                    ← MP3 files played by the robot
    ├── nepali_song.mp3
    └── school_song.mp3
```

---

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi 4 running Raspberry Pi OS (Bookworm or Bullseye)
- Python 3.9+
- PCA9685 board wired and I2C enabled (see [Wiring](#wiring--pca9685--raspberry-pi-4))

### Step 1 — Enable I2C

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
sudo reboot
```

Verify the PCA9685 is detected at address `0x40`:

```bash
sudo apt install i2c-tools -y
i2cdetect -y 1
# You should see "40" in the output grid
```

### Step 2 — Clone the Repository

```bash
git clone https://github.com/ayushshah-xo/Brown-Hat.git
cd Brown-Hat
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
sudo apt install espeak-ng ffmpeg -y
```

### Step 4 — Set Up API Keys

Create your `.env` file from the template:

```bash
cp .env.example .env
nano .env
```

Fill in your keys — all free tiers are available:

```env
GROQ_API_KEY=your_key_here         # https://console.groq.com       (free)
DEEPGRAM_API_KEY=your_key_here     # https://deepgram.com           (free tier)
ELEVENLABS_API_KEY=your_key_here   # https://elevenlabs.io          (optional)
```

> **Note:** The robot runs without ElevenLabs — it falls back to gTTS automatically.  
> The robot also runs without internet — see [fully offline mode](#configuration).

### Step 5 — Calibrate Servos

Open `config.py` and adjust angles to match your physical build:

```python
SERVO_LIMITS = {
    "jaw":        {"closed": 65,  "open": 85},
    "left_brow":  {"down":   35,  "up":  120},
    "right_brow": {"down":  120,  "up":   35},  # mirrored from left
}
```

Run the servo test tool to confirm everything moves correctly:

```bash
python tests/test_servos.py
```

### Step 6 — Run Brownhat

```bash
python robot.py
```

Say the wake word — **"Sukuna"** or **"सुकुना"** — then ask your question.

---

## 🎤 Voice Commands

Brownhat understands servo control commands in all three languages. Physical commands are handled in ~50 ms without any API call.

### Servo Commands

| English | Nepali | Hindi | Action |
|---|---|---|---|
| "Open eyes" | "आँखा खोल" | "आँखें खोलो" | Raises eyebrows |
| "Close eyes" | "आँखा बन्द गर" | "आँखें बंद करो" | Lowers eyebrows |
| "Blink" | "झपकी मार" | "झपकी मारो" | One blink |
| "Blink twice" | "दुईपटक झपकी" | "दो बार झपकी" | Two blinks |
| "Open jaw" | "मुख खोल" | "मुँह खोलो" | Opens jaw |
| "Close jaw" | "मुख बन्द गर" | "मुँह बंद करो" | Closes jaw |

### Knowledge Commands

| Say | Response |
|---|---|
| "Anil Thapa ko number ke ho?" | Speaks the teacher's phone number |
| "Head teacher ko naam ke ho?" | "Hikmat Bahadur Basnet" |
| "Timilai kasle banayo?" | Introduces its developer |
| Any news question | DuckDuckGo live search result |
| Any other question | AI-generated answer (Groq or offline) |

---

## ⚙️ Configuration

All settings live in `config.py`. Key options:

| Setting | Default | Options |
|---|---|---|
| `AI_MODE` | `"groq"` | `"groq"`, `"openai"`, `"offline"` |
| `STT_ENGINE` | `"deepgram"` | `"deepgram"`, `"vosk"` |
| `TTS_ENGINE` | `"gtts"` | `"gtts"`, `"elevenlabs"`, `"piper"` |
| `DEFAULT_LANGUAGE` | `"ne"` | `"ne"` (Nepali), `"hi"` (Hindi), `"en"` (English) |

### Fully Offline Mode

No internet? No problem. Set these three values in `config.py`:

```python
AI_MODE    = "offline"   # Mistral 7B GGUF (download model separately)
STT_ENGINE = "vosk"      # Vosk local speech recognition
TTS_ENGINE = "piper"     # Piper neural TTS
```

Then download the offline models:

```bash
# Vosk model (Nepali)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/vosk/

# Mistral 7B (optional, ~4 GB)
# Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# Place at: models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 🏫 Adapting for Your School

Brownhat is designed to be forked for any school. Three changes are all you need:

**1. Update school info in `config.py`:**

```python
SCHOOL = {
    "name":         "Your School Name",
    "location":     "Your City, Country",
    "head_teacher": "Principal Name",
    "phone":        "+XX XXX-XXXXXXX",
    "email":        "school@example.com",
    "robot_name":   "YourRobotName",
}

WAKE_WORDS = ["yourrobotname", "hey yourrobotname"]
```

**2. Replace the knowledge base:**

Edit `knowledge/teachers.json` with your school's staff list. Each entry follows this structure:

```json
{
  "name": "Teacher Name",
  "subject": "Mathematics",
  "phone": "+977 9800000000",
  "role": "Class Teacher"
}
```

**3. Set your language:**

```python
DEFAULT_LANGUAGE = "en"   # "ne", "hi", or "en"
```

---

## 🛠️ Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'adafruit_servokit'` | `pip install adafruit-circuitpython-servokit --break-system-packages` |
| `PCA9685 not found at 0x40` | Check I2C wiring and re-run `i2cdetect -y 1` |
| `DEEPGRAM_API_KEY not set` | Add key to `.env`; robot automatically falls back to Vosk |
| `gTTS error / no internet` | Set `TTS_ENGINE = "piper"` in `config.py` |
| Servo moves too far or not enough | Adjust `SERVO_LIMITS` in `config.py`; run `python tests/calibrate.py` |
| Jaw doesn't move while speaking | Confirm `SERVO_CHANNELS["jaw"] = 0` matches your physical channel |
| No sound output | Run `aplay -l` to list audio devices; update `output_device` in `AUDIO` config |
| `OSError: [Errno -9996]` | Wrong audio input device index; try changing `input_device` in `AUDIO` config |

---

## 👥 Team

Sukuna Secondary School, Nepal.

| Name | Role |
|---|---|
| **Ayush Shah** | Lead developer — hardware, software, and AI integration |
| **Yuganshu Rizal** | Team member |
| **Suprim Ojha** | Team member |

> Ayush Shah built this project at age 16 while studying in Class 11.

---

## 📄 License

[MIT](LICENSE) — Free to use, modify, and distribute.

If you build something with Brownhat, we'd love to hear about it!  
Please credit **Sukuna Secondary School, Nepal** when sharing. 🙏

---

