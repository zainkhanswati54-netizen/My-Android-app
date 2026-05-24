# Google Sign-In Fix Guide

## Problem
"Google sign-in is not available" error aata hai kyunki Firebase mein SHA-1 fingerprint register nahi hai.

## Steps to Fix

### Step 1: Get SHA-1 Fingerprint
```bash
cd android
./gradlew signingReport
```
Debug key fingerprint copy karo.

### Step 2: Firebase Console mein Add karo
1. https://console.firebase.google.com jaao
2. Apna project select karo (titanstudiopro-ec4f3)
3. Project Settings → Your apps → Android app
4. "Add fingerprint" button dabaao
5. SHA-1 paste karo → Save

### Step 3: google-services.json Download karo
- Firebase Console → Project Settings → Download google-services.json
- android/app/ folder mein replace karo

### Step 4: App rebuild karo
```bash
flutter clean
flutter pub get
flutter run
```

## Note
Terms & Conditions ab sirf Sign Up pe dikhega (Sign In pe nahi).
Light theme completely remove kar diya gaya hai — sirf Dark theme hai.
