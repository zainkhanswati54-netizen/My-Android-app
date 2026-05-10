# Titan Studio PRO — Changelog

All notable changes to this project are documented here.

---

## [13.0.0] - 2025 | FIXES EDITION

### Fixed
- **Storage Bug (Critical):** Voice was not saving to device. Root cause was permission failure on Android 10+. Now uses a 3-layer smart save system:
  1. Tries `/storage/emulated/0/Titan Studio PRO/Audio/` (internal storage)
  2. Falls back to app's private data directory if permissions denied (no permission needed)
  3. Shows clear error message with exact steps if both fail
- **SD Card Bug:** Previous code could mistakenly detect `/sdcard` (which may point to SD card on some devices). Now explicitly targets `/storage/emulated/0` which is always internal phone storage
- **Gender Selection in gTTS:** Male/Female selection was not correctly affecting gTTS fallback voice. Fixed TLD mapping per gender:
  - Male → `com` (US English accent)
  - Female → `co.uk` (UK English accent, more distinct)
- **gTTS Robotic Sound:** `slow=True` was used at speed ≤30% which made voice worse. Changed to `slow=False` as default; `slow=True` only at speed ≤20%
- **Android Permissions:** Added `MANAGE_EXTERNAL_STORAGE` request for Android 11+. Permission callback now always proceeds (save function handles fallback gracefully instead of blocking)
- **gTTS Error Message:** Now shows helpful tip to install edge-tts for better quality

### Improved
- Storage path detection is now much more reliable across different Android versions and manufacturers
- Error messages are more specific and actionable
- `get_titan_folder()` has graceful fallback chain: external → app private dir

---

## [12.0.0] - CLEAN UI EDITION

### Fixed
- Voice generation "No Internet" issue — better retry logic, DNS fallback, timeout increased to 90s
- All button text properly centered (text_size fix)
- All emoji removed — replaced with safe text icons (emoji causes broken boxes on many Android devices)
- Folder banner "[Folder]" text overlap — fixed layout
- Quick Guide text alignment — fully fixed
- Every single button is functional — none are decorative/broken
- Import file buttons show proper labels
- Header layout — no overlapping text
- gTTS fallback works when edge-tts fails

### Added
- Clean professional dark UI
- Animated waveform visualizer
- Batch Queue screen
- Voice History screen with playback
- Settings screen
- 30+ language support
- 10 emotion modes (Normal, Happy, Sad, Whisper, Shout, Sarcasm, Excited, Calm, Serious, Fearful)
- 8 voice presets (Narrator, Newsreader, Story, Meditation, Commercial, Robot, Poet, Audiobook)
- File import: TXT, PDF, DOCX, SRT, CSV
- Speed and Pitch sliders
- RTL language support (Urdu, Arabic)
- Auto-save to Titan Studio PRO/Audio/ folder

---

## [11.x.x] - Earlier versions

Internal development builds. Not publicly released.
