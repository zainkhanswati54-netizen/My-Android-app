# Titan Studio PRO — Project Structure

```
TitanStudioPRO/
│
├── main.py                          # Main app (v13.0.0) - sab screens + logic
│
├── buildozer.spec                   # Android APK build config
├── requirements.txt                 # Python packages list
├── build.sh                         # Build helper script (./build.sh)
├── .gitignore                       # Git ignore rules
│
├── README.md                        # Full documentation
├── CHANGELOG.md                     # Version history
│
├── AI.png                           # App icon (aap khud rakhein - 512x512)
├── presplash.png                    # Splash screen image (optional)
│
├── p4a_recipes/                     # Custom Android build recipes
│   ├── edge_tts/
│   │   └── __init__.py              # edge-tts Android recipe
│   ├── aiohttp/
│   │   └── __init__.py              # aiohttp Android recipe
│   └── aiofiles/
│       └── __init__.py              # aiofiles Android recipe
│
├── bin/                             # [Auto-generated] Final APK yahan aata hai
│   └── titanstudiopro-13.0.0-debug.apk
│
└── .buildozer/                      # [Auto-generated] Build cache (1-3 GB)
    └── android/
        └── platform/
            ├── android-sdk/         # Android SDK (auto download)
            ├── android-ndk/         # Android NDK (auto download)
            └── build-arm64-v8a/     # Compiled files
```

---

## Phone pe App save karta hai yahan:

```
/storage/emulated/0/              ← Internal Storage (SD card NAHI hai)
└── Titan Studio PRO/
    ├── Audio/                    ← Generated MP3 files yahan save hote hain
    │   ├── Titan_Hindi_Male_1234567890.mp3
    │   ├── Titan_English_Female_1234567891.mp3
    │   └── ...
    ├── Imported/                 ← Import kiye gaye files
    ├── Exports/                  ← Future use
    ├── Cloned/                   ← Future use
    └── Queue/                    ← Batch queue temp files
```

## App ki Private Data (Permission nahi chahiye):

```
/data/data/org.titanstudio.titanstudiopro/files/
├── history_v3.json               ← Voice history records
├── settings_v3.json              ← App settings
├── batch_queue_v3.json           ← Batch queue data
└── tts_preview.mp3               ← Temporary preview file
```

---

## Screens Flow:

```
Loading Screen
     │
     ▼  (3.6 seconds)
Studio Screen  ──────────►  History Screen
     │                            │
     │                            ▼ (Back)
     │                       Studio Screen
     │
     ├──────────────────►  Batch Queue Screen
     │                            │
     │                            ▼ (Back)
     │                       Studio Screen
     │
     └──────────────────►  Settings Screen
                                  │
                                  ▼ (Back)
                             Studio Screen
```

---

## TTS Engine Flow:

```
User clicks "Generate Audio"
         │
         ▼
   Check Internet
    (socket test)
         │
    ┌────┴────┐
    │         │
  YES         NO
    │         │
    ▼         ▼
edge-tts    gTTS
(Neural)  (Fallback)
    │         │
    │  FAIL   │
    ├────────►│
    │         │
    ▼         ▼
   Audio Ready!
   Play / Save
```

---

## Save Flow (v13 - Smart Fallback):

```
Save Voice clicked
        │
        ▼
Try /storage/emulated/0/Titan Studio PRO/Audio/
        │
   Can write?
   ┌─────┴──────┐
  YES           NO
   │             │
   ▼             ▼
 SAVED!    Try app private dir
           /data/data/.../files/Audio/
                    │
               Can write?
              ┌──────┴──────┐
             YES            NO
              │              │
              ▼              ▼
           SAVED!       Show Error
        (app folder)   + instructions
```
