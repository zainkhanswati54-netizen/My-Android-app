# 🔥 Firebase Setup Guide — Titan Studio PRO

## Step 1: Firebase Project Banao

1. https://console.firebase.google.com par jao
2. **"Add project"** click karo
3. Project naam: `TitanStudioPRO`
4. Google Analytics: OFF kar do (optional)
5. **"Create project"** click karo

---

## Step 2: Android App Register Karo

1. Firebase Console mein **Android icon** click karo
2. Package name daro:
   ```
   com.example.titan_studio_pro
   ```
3. App nickname: `Titan Studio PRO`
4. **"Register app"** click karo
5. **`google-services.json`** download karo
6. Yeh file yahan rakho:
   ```
   android/app/google-services.json
   ```

---

## Step 3: Authentication Enable Karo

1. Firebase Console → **Authentication** → **Get started**
2. **Sign-in method** tab mein:
   - ✅ **Email/Password** → Enable karo
   - ✅ **Google** → Enable karo
     - Project support email apna email daro
     - Save karo

---

## Step 4: Google Sign-In ke liye SHA-1 Add Karo

Terminal mein run karo:
```bash
cd android
./gradlew signingReport
```

`SHA1:` wali line copy karo, Firebase Console mein:
**Project Settings → Your Apps → Add fingerprint** mein paste karo.

---

## Step 5: Build Karo

```bash
flutter pub get
flutter build apk --release --no-tree-shake-icons
```

---

## ✅ Done! App mein yeh features kaam karenge:

- Email + Password signup/login
- Google Sign-In
- Forgot password (email bhejta hai)
- Auto-login (ek baar login karo, dobara nahi maangega)
- Logout (Settings screen se)

---

## ⚠️ Important Notes

- `google-services.json` ko **GitHub par push mat karo** (private rakho)
- `.gitignore` mein add karo:
  ```
  android/app/google-services.json
  ```
- Firebase free tier (Spark plan) mein 10,000 users/month FREE hain
