# 📋 Changelog — Titan AI Studio Pro

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [6.0.0] — 2026-05-07 — Major Industry-Grade Rewrite

### 🆕 Added
- Real `AI.png` logo shown in loading screen, header, and taskbar
- Internal storage support — no SD card required
- Smart storage detection — SD card option only shown when physical card present
- Staggered animation on History list items (0.07s delay per item)
- Slide-in animation on History screen entry
- Progress bar animation on loading screen
- Press bounce animation on all buttons (`FlatBtn`)
- Disabled button visual feedback (opacity 0.4)
- Play/Stop toggle in History screen with auto-reset
- Confirm dialog before clearing history
- `PermissionError` handling with user-friendly popup
- Build summary step in GitHub Actions (APK name, size, commit)
- Gradle cache in CI/CD pipeline
- Concurrency cancel-in-progress in CI/CD
- `CHANGELOG.md` (this file)
- `.gitignore` for Python/Android/IDE/OS files
- `README.md` with full project documentation

### 🐛 Fixed
- **Critical: Female/Male gender bug** — Lambda closure was capturing wrong variable; now uses `n=name` default arg pattern
- **Storage: SD card only** — App now always offers internal storage paths first
- **Logo: "SS" text in taskbar** — `AI.png` used for icon, splash, and header
- **Language validation** — Improved error messages, proper Unicode script checks
- **Script mismatch errors** — Clear popup telling user which script to write in

### 🎨 Changed
- UI cards for Language, Gender, Speed, Text Input sections
- All sizes use `dp()` and `sp()` for proper screen density scaling
- Status label shows emoji indicators (✅ ⚠ ⚡)
- History items show 🎵 icon and file existence check
- History "Clear" button now shows confirmation dialog
- Download success popup says "Great!" instead of "OK"
- Studio screen header is compact and icon-based

### 🔧 Technical
- All widget sizes in `dp()` / `sp()` — density independent
- `voice_sel` is always a plain `str`, never a lambda
- `_worker` thread uses `VOICE_TLD.get(self.voice_sel)` directly
- `get_internal_storage_path()` tries 3 paths with fallback
- `get_save_dirs()` always returns internal storage first
- Code: 1414 lines, clean `ast.parse()` verified

---

## [5.4.0] — 2026-05-06 — Previous Release

### Added
- 12 language support
- Male/Female voice selection
- Speed slider
- File import (TXT, PDF, DOCX)
- Download history screen
- SD card save options

### Known Issues (fixed in 6.0.0)
- Gender selection bug (always female)
- No internal storage option
- Logo shows "SS" text instead of image
- No screen transition animations
- Small UI elements on large screens
