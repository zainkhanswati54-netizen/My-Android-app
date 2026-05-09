# Titan Studio PRO — v12.0.0

**Professional Voice Studio · Always Free · 30+ Languages**

---

## v12.0.0 Mein Kya Fix Hua

| # | Problem | Fix |
|---|---------|-----|
| 1 | "No Internet" error generate karte waqt | 3x retry logic, 60s timeout, better error message |
| 2 | Broken boxes `⊠` buttons pe | Saare emoji hataye, clean text labels |
| 3 | Urdu/Hindi keyboard change nahi hota | RTL mode + hint text + instructions |
| 4 | Voice generate nahi hoti | Improved async handling + gTTS fallback |
| 5 | Settings button broken icon | Clean "SET" text button |

---

## Files Structure

```
TitanStudioPRO/
├── main.py                          ← Main app (FIXED v12)
├── buildozer.spec                   ← Android build config
├── requirements.txt                 ← Python dependencies
├── AI.png                           ← App logo/icon
├── .gitignore
├── README.md
├── p4a_recipes/
│   ├── edge_tts/
│   │   └── __init__.py              ← edge-tts Android recipe
│   └── aiohttp/
│       └── __init__.py              ← aiohttp Android recipe
└── .github/
    └── workflows/
        └── build.yml                ← GitHub Actions CI/CD
```

---

## PC Pe Test Karna

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run app
python main.py
```

---

## Android APK Build (GitHub Actions)

### Step 1: GitHub repo banao
```
GitHub.com → New Repository → Public
```

### Step 2: Yeh SAARI files upload karo (exact structure ke saath)
```
main.py
buildozer.spec
requirements.txt
requirements.txt
AI.png
.gitignore
p4a_recipes/edge_tts/__init__.py
p4a_recipes/aiohttp/__init__.py
.github/workflows/build.yml
```

### Step 3: Build chalao
```
GitHub → Actions tab → "Build Titan Studio PRO APK" → Run workflow
```

### Step 4: APK download karo
```
Actions → Latest run → Artifacts → TitanStudio-PRO-v12-APK
```

Build time: **30-60 minutes** (first time), **10-15 minutes** (cached)

---

## Urdu Keyboard Kaise Use Karein

App khud keyboard nahi badal sakta — yeh Android ki limitation hai.

**Solution:**
1. Phone Settings → Language & Input → Virtual Keyboard
2. Manage Keyboards → **Urdu** ON karein
3. App mein Urdu language select karein
4. Text box tap karein
5. Keyboard ke neeche **globe icon** press karein → Urdu keyboard aajayega

---

## TTS Engine (edge-tts)

| Feature | gTTS | edge-tts |
|---------|------|----------|
| Male voice | Fake | Real Neural |
| Female voice | Fake | Real Neural |
| Urdu quality | Basic | Neural |
| Speed control | Limited | Full % |
| Pitch control | No | Yes |
| Internet | Zaruri | Zaruri |
| Cost | Free | Free |

**Urdu Voices:**
- Male: `ur-PK-AsadNeural`
- Female: `ur-PK-UzmaNeural`
