# Titan Studio PRO v2.0 — Flutter Setup Guide
## Cyber Mint Edition

---

## Step 1: Install Flutter

1. Go to: https://flutter.dev/docs/get-started/install
2. Download Flutter SDK for Windows/Mac/Linux
3. Add Flutter to PATH
4. Run: `flutter doctor` — fix any issues shown

---

## Step 2: Install Android Studio

1. Download: https://developer.android.com/studio
2. Install Android SDK (API 33+)
3. Enable USB Debugging on your Android phone:
   - Settings > About Phone > Tap "Build Number" 7 times
   - Settings > Developer Options > USB Debugging: ON

---

## Step 3: Setup Project

```bash
# Extract this ZIP to a folder, then:
cd titan_flutter

# Install dependencies
flutter pub get

# Check everything is OK
flutter doctor
```

---

## Step 4: Run on Your Phone

```bash
# Connect phone via USB, then:
flutter devices        # See your phone listed
flutter run            # Build and install on phone
```

---

## Step 5: Build APK (to share/install)

```bash
flutter build apk --release
```

APK will be at:
`build/app/outputs/flutter-apk/app-release.apk`

---

## All Problems Fixed in v2.0:

| Problem | Fix Applied |
|---------|-------------|
| Male/Female voice galat | Edge TTS verified voices — Male/Female properly selected |
| Robotic voice | Microsoft Edge TTS — realistic neural voices |
| Features kaam nahi | Speed, Pitch, Emotion — sab properly connected |
| Language confusion | Urdu/Hindi/English ONLY — wrong script = error dialog |
| Keyboard auto-change | TextDirection.rtl for Urdu — automatic RTL keyboard |
| No characters | 8 characters: Adam, Luna, Nova, Zara, Rex, Aria, Bolt, Sage |
| Speed/Pitch broken | Sliders directly pass values to TTS API |
| Advanced settings | Breath simulation, Adaptive pacing — all working |

---

## Languages:

- 🇺🇸 **English** — en-US-GuyNeural / en-US-JennyNeural
- 🇮🇳 **Hindi** — hi-IN-MadhurNeural / hi-IN-SwaraNeural  
- 🇵🇰 **Urdu** — ur-PK-AsadNeural / ur-PK-UzmaNeural

**Language Lock:** If you select Urdu but type English → Error dialog
If you select Hindi but type English → Error dialog

---

## Architecture:

```
lib/
├── main.dart                 # App entry point
├── screens/
│   ├── splash_screen.dart    # Loading screen
│   ├── studio_screen.dart    # Main TTS screen
│   ├── history_screen.dart   # Voice history
│   └── settings_screen.dart  # Settings
├── services/
│   └── tts_service.dart      # Edge TTS API
├── models/
│   └── history_model.dart    # History storage
├── widgets/
│   ├── mint_card.dart        # Reusable cards/buttons
│   └── waveform_widget.dart  # Audio waveform
└── utils/
    └── constants.dart        # Colors, voices, configs
```

---

## Tech Stack:

- **Framework:** Flutter (Dart)
- **TTS Engine:** Microsoft Edge TTS (Free, no API key)
- **Audio:** just_audio package
- **Storage:** shared_preferences + path_provider
- **UI:** Custom Cyber Mint theme

---

*© 2025 Titan Studio PRO — Your 1 month ki mehnat + naya Flutter code*
