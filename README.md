# Titan AI Studio Pro — v10.1.0

**Professional Voice Studio · Always Free · 30+ Languages**

---

## Files List (repo mein yeh sab hone chahiye)

```
repo/
├── main.py               ← Main app (Kivy)
├── buildozer.spec        ← Android build config
├── requirements.txt      ← Python dependencies
├── AI.png                ← App logo/icon (512x512 recommended)
├── build.yml             ← GitHub Actions CI/CD (Actions folder mein)
├── .gitignore
├── README.md
└── p4a_recipes/          ← Custom Android recipes
    ├── edge_tts/
    │   └── __init__.py
    └── aiohttp/
        └── __init__.py
```

> **Note:** `build.yml` ko `.github/workflows/` folder mein rakhna hai:
> `.github/workflows/build.yml`

---

## Setup (Local PC pe test karna ho to)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run app on PC (test mode)
python main.py
```

---

## Android APK Build (GitHub Actions se — EASY)

### Step 1: GitHub repo banao
```
GitHub.com → New Repository → Public ya Private (koi bhi)
```

### Step 2: Yeh files upload karo repo root mein
```
main.py
buildozer.spec
requirements.txt
AI.png
.gitignore
p4a_recipes/   (pura folder)
```

### Step 3: build.yml sahi jagah rakhna
```
.github/
  workflows/
    build.yml       ← yahan
```

### Step 4: Build chalao
```
GitHub → Actions tab → "Build Titan AI APK" → Run workflow
```

### Step 5: APK download karo
```
Actions → Latest run → Artifacts → TitanAI-Studio-Pro-v10.1-APK
```

Build time: **30-60 minutes** (first time), **10-15 minutes** (cached)

---

## TTS Engine — edge-tts (Microsoft Neural)

App ab **edge-tts** use karta hai jo gTTS se behtar hai:

| Feature | gTTS (purana) | edge-tts (naya) |
|---------|--------------|-----------------|
| Male voice | Fake (TLD trick) | Real neural voice |
| Female voice | Fake (TLD trick) | Real neural voice |
| Speed control | Sirf slow/fast | % control |
| Pitch control | Nahi | Hz control |
| Emotion | Nahi | Volume se |
| Urdu quality | Basic | Neural (AsadNeural) |
| Internet | Zaruri | Zaruri |
| Cost | Free | Free |

### Urdu Voices
- **Male:** `ur-PK-AsadNeural`
- **Female:** `ur-PK-UzmaNeural`

---

## Bugs Fixed in v10.1.0

1. **Text TextInput mein nahi dikhta** — `foreground_color=(1,1,1,1)` explicit tuple
2. **Adaptive Pacing + Enter Text overlap** — AdvancedOptionsCard height `dp(280)` → `dp(320)`
3. **Broken boxes (□) on buttons** — Saare emoji replace with plain text
4. **Gender/Speed/Pitch kaam nahi karta** — gTTS → edge-tts neural TTS
5. **Settings button broken icon** — `⚙` → `SET`

---

## Permissions (Android)

App ko yeh permissions chahiye:
- `INTERNET` — TTS ke liye
- `WRITE_EXTERNAL_STORAGE` — audio save karne ke liye
- `READ_EXTERNAL_STORAGE` — file import ke liye

---

## Support

App always free rahega. Koi subscription nahi, koi ads nahi.
