# 🎙️ Titan AI Studio Pro

<div align="center">

![Titan AI Studio Pro](AI.png)

**Your Personal Narrator, Always Free.**

[![Build APK](https://github.com/YOUR_USERNAME/titan-ai-studio/actions/workflows/build.yml/badge.svg)](https://github.com/YOUR_USERNAME/titan-ai-studio/actions/workflows/build.yml)
![Version](https://img.shields.io/badge/version-6.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Android-green)
![Python](https://img.shields.io/badge/python-3.10-yellow)
![License](https://img.shields.io/badge/license-MIT-purple)

</div>

---

## 📱 What is Titan AI Studio Pro?

Titan AI Studio Pro is a **free, offline-capable** Android app that converts text into natural-sounding speech using Google's Text-to-Speech engine (gTTS). Supports **12 languages**, male/female voices, adjustable speed, file import, and local MP3 download.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🌐 Languages | English, Urdu, Hindi, Arabic, French, Spanish, German, Turkish, Russian, Chinese, Japanese, Korean |
| 🎤 Voices | Male & Female per language |
| ⚡ Speed control | Slow / Normal / Fast slider |
| 📂 File import | TXT, PDF, DOCX supported |
| 💾 Save audio | Internal storage, Downloads, Music, Documents |
| 📋 History | Full download history with playback |
| 🚫 No ads | 100% free, no hidden costs |

---

## 📸 Screenshots

| Splash | Main Screen | Language Select | History |
|--------|-------------|-----------------|---------|
| *(splash)* | *(main)* | *(lang)* | *(history)* |

---

## 🚀 How to Build

### Option A — GitHub Actions (Recommended)

1. Fork this repository
2. Go to **Actions** tab → **Build Titan AI APK** → **Run workflow**
3. Download the APK from the **Artifacts** section

### Option B — Local build (Linux/macOS)

```bash
# 1. Install dependencies
pip install buildozer Cython==0.29.33

# 2. Install system packages (Ubuntu/Debian)
sudo apt-get install python3-dev build-essential git \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev

# 3. Build
buildozer android debug

# APK will be in ./bin/
```

---

## 📁 Project Structure

```
titan-ai-studio/
├── main.py                  # Main application (Kivy + gTTS)
├── buildozer.spec           # Android build configuration
├── AI.png                   # App icon & splash screen
├── .github/
│   └── workflows/
│       └── build.yml        # CI/CD pipeline
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── bin/                     # Built APKs (generated, gitignored)
```

---

## 🔧 Requirements

- Python 3.10+
- Kivy 2.2.1
- gTTS 2.5.1
- Android API 33 (Android 13+), minimum API 24 (Android 7+)
- Internet connection (for TTS generation)

---

## 📖 How to Use the App

1. **Select Voice Language** from the dropdown
2. **Choose Gender**: Male or Female
3. **Adjust Speed** using the slider
4. **Type text** or **Import a file** (TXT / PDF / DOCX)
5. Tap **⚡ Generate Audio**
6. **Preview** then **Download** your voice

---

## 🛠️ Tech Stack

- **Frontend**: [Kivy](https://kivy.org/) (Python UI framework)
- **TTS Engine**: [gTTS](https://gtts.readthedocs.io/) (Google Text-to-Speech)
- **Build System**: [Buildozer](https://buildozer.readthedocs.io/)
- **CI/CD**: GitHub Actions
- **Target**: Android ARM64

---

## 📄 License

```
MIT License — Free to use, modify, and distribute.
```

---

## 👨‍💻 Author

**Titan AI Studio** — Built with ❤️ using Python & Kivy

---

<div align="center">
⭐ Star this repo if you found it useful!
</div>
