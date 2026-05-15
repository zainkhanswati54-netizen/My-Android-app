# 🎙️ Titan Studio PRO v2.0 — Setup Guide

## TTS Engine — Kaise Kaam Karta Hai?

### Voice Quality (Best → Lowest)
App teen TTS engines use karti hai automatically:

| Priority | Engine | Quality | Notes |
|----------|--------|---------|-------|
| 1st | **Edge TTS Neural** | ⭐⭐⭐⭐⭐ | Microsoft ki natural AI voice |
| 2nd | **Azure Cognitive** | ⭐⭐⭐⭐ | Fallback Microsoft endpoint |
| 3rd | **Google TTS** | ⭐⭐⭐ | Last fallback, works everywhere |

### Available Voices

#### English
- **Male:** en-US-GuyNeural (natural American accent)
- **Female:** en-US-JennyNeural (warm, clear voice)

#### Hindi (हिंदी)
- **Male:** hi-IN-MadhurNeural
- **Female:** hi-IN-SwaraNeural

#### Urdu (اردو)
- **Male:** ur-PK-AsadNeural
- **Female:** ur-PK-UzmaNeural

---

## Build Karna (GitHub Actions)

1. GitHub pe new repository banao
2. Ye sara code push karo
3. **Actions** tab → **Build Titan Studio PRO APK** → **Run workflow**
4. Build complete hone pe APK download karo (Artifacts section mein)

## Local Build

```bash
# Flutter install hona chahiye
flutter pub get
flutter build apk --release
```

APK yahan milega:
`build/app/outputs/flutter-apk/app-release.apk`

---

## Bug Fixes in v2.1

✅ Edge TTS Neural voices properly connected  
✅ ssmlMode & lowLatency parameters fix  
✅ Breath simulation (SSML break tags)  
✅ Better internet check  
✅ 3-tier fallback system  
✅ Urdu RTL text properly handled  
✅ All Advanced Options now functional  

---

## Future Upgrade: Fish Speech / F5-TTS

Agar aap Fish Speech ya F5-TTS chahte hain (ye offline/local models hain):

1. Ye Android pe directly nahi chalte — server chahiye
2. Options:
   - **Apna VPS** pe model host karo, Flutter usse call kare
   - **Hugging Face Spaces** pe deploy karo (free)
   - **Google Colab** se temporarily run karo

### Recommended: Hugging Face Space
```
1. huggingface.co pe account banao
2. Fish Speech ya Kokoro Space fork karo  
3. Space URL apni app mein add karo
4. Flutter app us URL se audio request kare
```

Ye setup main aapke liye bhi kar sakta hun agar aap chahein.
