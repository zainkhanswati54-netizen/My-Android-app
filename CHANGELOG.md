# Titan Studio PRO — CHANGELOG

## v1.0.0 — CYBER MINT EDITION (Latest)

### Bug Fixes:

**[FIX 1] AI.png Icon**
- App icon `AI.png` now properly shown on Loading Screen and Studio header
- Both screens search for AI.png → AI.jpg → logo.png in order

**[FIX 2] Urdu/Hindi/Arabic Box Issue — FIXED**
- Root cause: Default font doesn't support non-Latin scripts → shows □□□ boxes
- Fix: `LabelBase.register()` called at startup for Noto fonts
- Font auto-switches when language changes:
  - Urdu → NotoNastaliqUrdu
  - Hindi/Bengali/Punjabi/Tamil/Telugu → NotoSansDevanagari
  - Arabic → NotoNaskhArabic
  - Chinese/Japanese/Korean → NotoSansCJK
- Falls back gracefully if Noto fonts not installed

**[FIX 3] Auto Keyboard Switch per Language**
- TextInput font changes immediately when language spinner changes
- RTL indicator message updated to guide user to switch keyboard
- On Android: attempts to invoke correct IME locale via pyjnius
- LANG_KEYBOARD_LOCALE map covers 24+ languages

**[FIX 4] Text Alignment Fixed**
- All Label widgets now bind `width → text_size` properly
- Text never clips, wraps correctly, aligns center/left/right as intended
- FlatBtn text_size = widget size → button text always centered

**[FIX 5] Male Voice Fixed + Advanced Options Work**
- Verified all Edge-TTS Male voice IDs (e.g. en-US-GuyNeural confirmed)
- Added Punjabi and Catalan to EDGE_VOICES table
- Advanced Options now actually applied during generation:
  - Breath Simulation → inserts pauses at sentence ends
  - Adaptive Pacing → reduces speed for long texts
  - SSML Support → wraps text in <speak> tags for edge-tts
  - Low Latency → UI flag (edge-tts handles internally)

**[FIX 6] Speed Above Pitch (Vertical Layout)**
- Speed card now placed ABOVE Pitch card (separate full-width cards)
- Each card has header row with label + current value displayed
- Sliders are full-width → much easier to adjust numbers
- Replaces old side-by-side cramped layout

**[FIX 7] Version → 1.0 MINT EDITION**
- Version string changed from v14.0 to v1.0
- Subtitle reads "v1.0 Mint Edition — Always Free"
- About page updated

---

## v14.0.0 — Previous version
(See original CHANGELOG)
