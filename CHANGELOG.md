# Titan AI Studio Pro — Changelog

All notable changes are documented here.

---

## [1.0.0] — 2026-05-09  ← CURRENT VERSION

### Fixed
- **Double splash screen removed** — app now shows loading screen only once on startup
- **Broken square icons fixed** — all icons now use proper Unicode emojis (⚙ ♂ ♀ 🎭 etc.)
- **Gender selection now works** — Male/Female toggle correctly changes the voice engine
- **Mood/Emotion selection now works** — Happy, Sad, Whisper, Shout, Sarcasm, Excited, Serious all properly applied during generation
- **Speed & Pitch sliders aligned** — both controls are now on the same baseline, no more uneven text
- **Version corrected** — was incorrectly showing v10.0.0, now properly v1.0.0

### Added
- **Edge TTS engine** — free Microsoft neural voices with male/female and mood support
- **Auto folder creation** — app creates `TitanAIStudio/Audio/`, `Cloned/`, `Imports/`, etc. automatically on first launch
- **Professional audio player** — round ▶ play button with progress slider and timer display
- **Save button** — dedicated 💾 button next to player
- **History popup** — view and replay last 20 generated audio files
- **Batch Queue** — add multiple texts to queue for batch generation
- **Character/word/line counter** — live counter below text input
- **Status messages** — real-time feedback during generation (generating, done, error)
- **API key persistence** — ElevenLabs key saved to `Presets/api_key.txt`, loaded on startup
- **Settings screen** — folder structure viewer, API key input, About section

### Changed
- **Voice engine priority**: ElevenLabs (if key set) → Edge TTS → gTTS fallback
- **Save path**: `TitanAIStudio/Audio/titan_YYYYMMDD_HHMMSS.mp3`
- **Presplash color** updated to match dark theme `#0A0E1A`
- **Build workflow** artifact renamed to `TitanAIStudioPro-v1.0.0-APK`

---

## [0.9.0] — Internal build (previously labeled v10.0.0 by mistake)

### Known Issues (all fixed in v1.0.0)
- Double loading screen on app start
- Square boxes shown instead of icons throughout the app
- Male voice selection had no effect — female voice always generated
- Mood selection (Happy, Sad, etc.) had no effect on output
- Speed and Pitch labels were misaligned vertically
- Audio files saved to arbitrary internal storage path
- Version number incorrectly set to 10.0.0
-
