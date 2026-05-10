# Titan Studio PRO 🎙️
### Professional Voice Studio — Always Free

A powerful Android TTS (Text-to-Speech) application built with Python + Kivy.
Supports 30+ languages, neural voices, multiple emotions, batch processing, and more.

---

## Features

- **Neural Voices** via Microsoft Edge TTS — natural, human-like quality
- **30+ Languages** including Hindi, Urdu, Arabic, English, and more
- **Male & Female** voice selection per language
- **10 Emotion Modes** — Normal, Happy, Sad, Whisper, Shout, Sarcasm, Excited, Calm, Serious, Fearful
- **8 Voice Presets** — Narrator, Newsreader, Story, Meditation, Commercial, Robot, Poet, Audiobook
- **Speed & Pitch** sliders for fine control
- **File Import** — TXT, PDF, DOCX, SRT, CSV
- **Batch Queue** — generate multiple voices in one go
- **Voice History** — playback and manage all generated files
- **Auto-Save** to internal storage (`/storage/emulated/0/Titan Studio PRO/Audio/`)
- **RTL Support** — Urdu, Arabic text input direction
- **Offline Fallback** — gTTS used when edge-tts unavailable

---

## Voice Quality

| Engine | Quality | Internet | Notes |
|--------|---------|----------|-------|
| **edge-tts** | ⭐⭐⭐⭐⭐ Natural | Required | Microsoft neural voices. Best quality. |
| **gTTS** | ⭐⭐ Robotic | Required | Google Translate TTS. Fallback only. |

**Recommendation:** Always install `edge-tts` for professional results.

---

## Project Structure

```
TitanStudioPRO/
├── main.py              # Main application code
├── buildozer.spec       # Android build configuration
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── CHANGELOG.md         # Version history
├── p4a_recipes/         # Custom python-for-android recipes
│   ├── edge_tts/        # Recipe for edge-tts
│   │   └── __init__.py
│   └── aiohttp/         # Recipe for aiohttp (edge-tts dependency)
│       └── __init__.py
├── AI.png               # App icon (optional, place here)
└── presplash.png        # Splash screen (optional, place here)
```

---

## Build Instructions (APK)

### Prerequisites

```bash
# Ubuntu/Debian recommended for building
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

pip install buildozer cython
```

### Build Steps

```bash
# 1. Clone or place your project files
cd TitanStudioPRO/

# 2. Install Python dependencies (for development/testing)
pip install -r requirements.txt

# 3. Build debug APK (first build takes 20-40 minutes)
buildozer android debug

# 4. Find your APK in:
ls bin/
# titanstudiopro-13.0.0-arm64-v8a_armeabi-v7a-debug.apk

# 5. Deploy directly to connected Android device (USB debugging on):
buildozer android debug deploy run

# For release APK (set keystore in buildozer.spec first):
# buildozer android release
```

### Build Tips

- First build downloads Android SDK + NDK (~2-3 GB). Be patient.
- Use Ubuntu 20.04 or 22.04 for best compatibility
- If build fails on `aiohttp` or `edge-tts`, see Troubleshooting below
- Always run `buildozer android clean` before a fresh build if something breaks

---

## Development Setup (PC/Desktop)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run on desktop
python main.py
```

---

## Troubleshooting

### Voice not saving
- Go to **Phone Settings → Apps → Titan Studio PRO → Permissions → Storage → Allow**
- On Android 11+, you may need to allow "Manage all files" permission
- The app automatically falls back to its private data directory if storage is denied

### "No Internet" error
- Make sure Wi-Fi or mobile data is ON
- The app checks internet before generating
- Try again after a few seconds

### edge-tts not working / robotic voice
- The app is using gTTS as fallback
- Install edge-tts: this is handled automatically via `requirements` in `buildozer.spec`
- If building APK, make sure `edge-tts` is in the `requirements` line in `buildozer.spec`

### Build fails on aiohttp/edge-tts
- Try removing `edge-tts` and `aiohttp` from `buildozer.spec` requirements
- The app will use gTTS fallback — it still works, just lower quality
- Or use the custom p4a_recipes included in this project

### App crashes on launch
```bash
# Check logcat for errors
adb logcat | grep -i "python\|kivy\|titan"
```

---

## Permissions Explained

| Permission | Why needed |
|-----------|-----------|
| `INTERNET` | Required for TTS generation (edge-tts and gTTS both need internet) |
| `WRITE_EXTERNAL_STORAGE` | Save audio files to internal storage (Android 9 and below) |
| `READ_EXTERNAL_STORAGE` | Read files for import (TXT, PDF, DOCX) |
| `MANAGE_EXTERNAL_STORAGE` | Full storage access on Android 11+ |

---

## License

Titan Studio PRO — Always Free.
For personal and commercial use.
