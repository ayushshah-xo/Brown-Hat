<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Mono&size=13&duration=2500&pause=800&color=6EE7B7&center=true&vCenter=true&width=700&lines=Raspberry+Pi+4+%C2%B7+Servo+Motors+%C2%B7+Python;Wake-Word+Activation+%C2%B7+Multilingual+AI;Offline+%2B+Online+AI+%C2%B7+Groq+%2B+Ollama;Natural+Speech+Synthesis+%C2%B7+Real-time+Facial+Expressions" />

# 🤖 Brown Hat

### Open-Source AI Humanoid Robot Built on Raspberry Pi

An AI-powered robotic head featuring wake-word activation, multilingual conversation, online/offline AI processing, natural speech synthesis, internet-assisted responses, and real-time servo-driven facial expressions.

Designed, printed, assembled, and programmed entirely from scratch.

<br>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://python.org)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-4-C51A4A?style=flat-square\&logo=raspberry-pi\&logoColor=white)](https://raspberrypi.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ayushshah-xo/Brown-Hat?style=flat-square\&color=facc15)](https://github.com/ayushshah-xo/Brown-Hat/stargazers)

</div>

---

## 🎥 Watch Brown Hat in Action

<p align="center">
  <a href="https://youtu.be/T0bWZ5AiFkI">
    <img src="https://img.youtube.com/vi/T0bWZ5AiFkI/maxresdefault.jpg" alt="Brown Hat Demo">
  </a>
</p>

<p align="center">
  <b>▶ Click the image to watch the full demonstration</b>
</p>

---

## 📖 Table of Contents

* Overview
* Features
* Why Brown Hat?
* System Architecture
* Hardware
* Repository Structure
* Getting Started
* CAD & STL Files
* Roadmap
* Contributing
* Author

---

# 🧠 Overview

Brown Hat is an open-source humanoid robot platform powered by Raspberry Pi 4.

The project combines artificial intelligence, speech recognition, speech synthesis, and servo-driven facial animation into a single robotic system capable of natural human interaction.

Brown Hat listens for a wake word, understands spoken language, generates responses using online or offline language models, speaks naturally, and expresses itself through synchronized facial movements.

The goal is simple:

> Build a fully reproducible AI robot that anyone can assemble, improve, and learn from.

Unlike many robotics kits, Brown Hat was designed from the ground up—including hardware design, electronics integration, software architecture, and mechanical assembly.

---

# ✨ Features

| Feature                       | Description                                      |
| ----------------------------- | ------------------------------------------------ |
| 🎤 Wake Word Detection        | Activates only when called                       |
| 🌍 Multilingual Conversations | Understands and responds in multiple languages   |
| 🧠 Online AI                  | Fast responses powered by Groq                   |
| 🔌 Offline AI                 | Local fallback using Ollama                      |
| 🗣️ Natural Speech Synthesis  | Converts AI responses into speech                |
| 😐 Facial Expressions         | Real-time servo-driven facial animation          |
| 👀 Autonomous Eye Blinking    | Natural eye movement behavior                    |
| 👄 Jaw Synchronization        | Mouth movement synchronized with speech          |
| 🎭 Expression Engine          | Independent control of eyes, eyebrows, and mouth |
| 🌐 Internet Search            | Retrieves information from the web               |
| ⚡ Low-Latency Pipeline        | Fast end-to-end response generation              |
| 🖨️ Open Source               | Fully reproducible and modifiable                |

---

# 🚀 Why Brown Hat?

Most AI assistants exist only as software.

Brown Hat brings artificial intelligence into the physical world.

The project demonstrates how modern language models can be integrated into a robotic platform capable of:

* Listening
* Understanding
* Speaking
* Expressing emotions
* Operating online or offline
* Interacting naturally with humans

Brown Hat is intended to serve as a learning platform for makers, students, robotics enthusiasts, and AI developers.

---

# ⚙️ System Architecture

```text
User Speaks
      │
      ▼
Wake Word Detection
      │
      ▼
Speech Recognition
      │
      ▼
Language Detection
      │
      ▼
AI Processing Layer
 ├── Groq (Online)
 └── Ollama (Offline)
      │
      ▼
Response Generation
      │
      ▼
Text-To-Speech
      │
      ▼
Audio Playback
      │
      ├────────────► Jaw Movement
      ├────────────► Eye Blinking
      └────────────► Facial Expressions
```

The facial animation system runs independently from the conversational pipeline, ensuring smooth and responsive expressions while audio is being played.

---

# 🔧 Hardware

| Component            | Purpose                 |
| -------------------- | ----------------------- |
| Raspberry Pi 4       | Main compute unit       |
| PCA9685 Servo Driver | PWM servo control       |
| Servo Motors         | Facial actuation        |
| USB Microphone       | Voice input             |
| Speaker              | Voice output            |
| Audio Amplifier      | Audio amplification     |
| 5V Power Supply      | Stable power delivery   |
| 3D Printed Structure | Robot frame and housing |

---

# 📁 Repository Structure

```text
Brown-Hat/
│
├── brain/          # AI logic
├── knowledge/      # Knowledge and configuration
├── motion/         # Servo control and expressions
├── songs/          # Song playback modules
├── tests/          # Testing scripts
├── voice/          # Speech recognition and TTS
│
├── robot.py        # Main entry point
├── config.py       # Configuration
├── read.py         # Utility scripts
├── requirements.txt
└── .gitignore
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/ayushshah-xo/Brown-Hat.git

cd Brown-Hat
```

---

## 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Install System Packages

```bash
sudo apt update

sudo apt install espeak python3-pyaudio portaudio19-dev alsa-utils
```

---

## 4. Optional Offline AI Setup

```bash
curl -fsSL https://ollama.com/install.sh | sh

ollama pull tinyllama
```

Brown Hat automatically switches between online and offline AI modes depending on connectivity.

---

## 5. Configure

Open:

```python
config.py
```

Example:

```python
GROQ_API_KEY = "YOUR_API_KEY"

WAKE_WORD = "brown hat"

LANGUAGE = "en"
```

---

## 6. Launch Brown Hat

```bash
python3 robot.py
```

Say the wake word and begin interacting.

---

# 🖨️ CAD & STL Files

The software repository contains only the source code.

Hardware files are maintained separately.

## CAD Files

```text
PASTE YOUR CAD REPOSITORY LINK HERE
```

## STL Files

```text
PASTE YOUR STL REPOSITORY LINK HERE
```

These repositories contain the printable and editable files required to build your own Brown Hat robot.

---

# 📦 Core Technologies

### Software

* Python
* Groq API
* Ollama
* SpeechRecognition
* PyAudio
* Requests
* eSpeak
* PCA9685 Servo Control

### Hardware

* Raspberry Pi 4
* Servo Motors
* PCA9685 Driver Board
* USB Microphone
* Speaker System
* 3D Printed Components

---

# 🛣️ Roadmap

## Current Capabilities

* Wake word activation
* Speech recognition
* Online AI responses
* Offline AI fallback
* Multilingual support
* Facial expressions
* Eye blinking
* Jaw synchronization
* Internet search

## Future Goals

* Long-term memory
* Camera integration
* Computer vision
* Face recognition
* Emotion recognition
* Mobile application
* Additional facial degrees of freedom
* Expanded personality system

---

# 🤝 Contributing

Contributions are welcome.

Whether you're interested in:

* Robotics
* Artificial Intelligence
* Embedded Systems
* Mechanical Design
* 3D Printing
* Raspberry Pi Development

there is room to contribute.

### Contribution Process

1. Fork the repository
2. Create a new branch
3. Implement your changes
4. Commit your work
5. Open a pull request

All contributions are appreciated.

---

# 👤 Author

## Ayush Shah

Student • Robotics Builder • Open-Source Developer

### GitHub

https://github.com/ayushshah-xo

### Project Repository

https://github.com/ayushshah-xo/Brown-Hat

### Demo Video

https://youtu.be/T0bWZ5AiFkI

---

<div align="center">

### ⭐ If Brown Hat inspired you, consider starring the repository.

Building open-source robotics, one servo at a time.

</div>
