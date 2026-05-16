# Titan Studio PRO v2.0 — Flutter Source Code

## Project Structure
```
lib/
├── main.dart                    # App entry point
├── theme.dart                   # AppTheme colors & theme
├── utils/
│   └── constants.dart           # All constants (colors, languages, emotions, characters, presets)
├── models/
│   ├── models.dart              # Data models (AppLanguage, VoiceEmotion, etc.)
│   └── history_model.dart       # HistoryEntry + HistoryService (simple)
├── services/
│   ├── tts_service.dart         # TTS API calls + file save
│   └── history_service.dart     # SharedPreferences history storage
├── screens/
│   ├── splash_screen.dart       # Animated splash with dark theme
│   ├── studio_screen.dart       # MAIN SCREEN — full TTS studio
│   ├── history_screen.dart      # Saved recordings list
│   └── settings_screen.dart     # App settings
└── widgets/
    ├── mint_card.dart           # MintCard + MintBtn + SectionHeader
    ├── waveform_widget.dart     # Animated waveform painter
    └── widgets.dart             # Extended widgets (MintButton, EmotionChip, etc.)
```

## Features
- ✅ 3 Languages: English, Hindi, Urdu (RTL support)
- ✅ 8 Characters: Adam, Luna, Nova, Zara, Rex, Aria, Bolt, Sage
- ✅ 8 Voice Presets: Narrator, Newsreader, Story, Meditation, Commercial, Audiobook, Poet, Robot
- ✅ 8 Emotions: Normal, Happy, Sad, Whisper, Shout, Excited, Calm, Serious
- ✅ Speed & Pitch sliders
- ✅ Advanced options: Breaths, Adaptive Pacing, SSML, Low Latency
- ✅ Play preview + Save to Downloads
- ✅ History screen

## API
Uses: `https://zainkhanswati54-titan-tts-api.hf.space/tts`

## Build
```bash
flutter pub get
flutter build apk --release
```
