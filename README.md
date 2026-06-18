<div align="center">

# 🤖 Brownhat — Voice & AI-Controlled Robotic Head

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-C51A4A?logo=raspberrypi&logoColor=white)](https://raspberrypi.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

A fully voice-controlled, AI-powered robotic head built on a Raspberry Pi with 3D-printed parts and servo motors. Brownhat responds to voice commands in real time, moves expressively, and can hold conversations using integrated AI.

</div>

---

## 📸 Demo

> _Add a GIF or screenshot here — e.g.:_
> ![Brownhat Demo](assets/demo.gif)

---

## ✨ Features

- 🎙️ **Voice Control** — Responds to spoken commands using speech recognition
- 🤖 **AI Integration** — Powered by a language model for natural conversation
- 🔩 **Servo-Driven Motion** — Smooth head movements (pan, tilt, facial expressions)
- 🖨️ **3D Printed Chassis** — Fully open-source mechanical design
- 🍓 **Raspberry Pi Brain** — Runs entirely on a Raspberry Pi 5

---

## 🗂️ Repository Structure

```
Brownhat/
├── src/
│   ├── main.py              # Entry point
│   ├── voice/               # Speech recognition & TTS
│   ├── ai/                  # AI model integration
│   └── motors/              # Servo control logic
├── models/                  # 3D printable STL files
├── config/
│   └── settings.yaml        # Hardware & model config
├── assets/                  # Images, GIFs, diagrams
├── requirements.txt
└── README.md
```

---

## 🛠️ Hardware Requirements

| Component | Specification |
|-----------|---------------|
| Single-board computer | Raspberry Pi 5 (4GB+ RAM recommended) |
| Servo motors | Standard PWM servos × N (see wiring diagram) |
| Power supply | 5V/3A for Pi + separate 6V for servos |
| Microphone | USB microphone or USB audio adapter |
| 3D printed parts | PLA/PETG, ~N hours print time |

> **Wiring diagram:** _(Add a link or image here)_

---

## ⚙️ Software Requirements

- Python 3.10+
- Raspberry Pi OS (64-bit recommended)
- See [`requirements.txt`](requirements.txt) for Python dependencies

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ayushshah-xo/Robotic_Head.git
cd Robotic_Head
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure settings

```bash
cp config/settings.yaml.example config/settings.yaml
# Edit settings.yaml to match your hardware (GPIO pins, servo ranges, AI API key)
```

### 4. Run Brownhat

```bash
python src/main.py
```

---

## 🔧 Configuration

Key settings in `config/settings.yaml`:

```yaml
servo:
  pan_pin: 18        # GPIO pin for pan servo
  tilt_pin: 19       # GPIO pin for tilt servo

voice:
  language: "en-US"
  wake_word: "brownhat"

ai:
  model: "your-model-here"
  api_key: "YOUR_API_KEY"   # Or set via environment variable
```

---

## 🖨️ 3D Printing

All STL files are in the [`models/`](models/) directory.

| Part | Material | Infill |
|------|----------|--------|
| Head shell | PLA | 20% |
| Servo mount | PETG | 40% |
| Neck joint | PETG | 40% |

> Slicing profiles for Cura/PrusaSlicer are included in `models/`.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Ayush Shah**
- GitHub: [@ayushshah-xo](https://github.com/ayushshah-xo)

---

<div align="center">

⭐ If you found this project useful, please consider giving it a star!

</div>
