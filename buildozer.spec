[app]
title = Titan AI Studio Pro
package.name = titanai
package.domain = com.titanai.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 7.1.0

# ── Requirements (FIX: Coqui TTS remove kar diya — Android crash karta tha) ──
requirements = python3,kivy==2.2.1,gtts,requests,certifi,chardet,idna,urllib3,Pillow,PyPDF2,python-docx,setuptools

# ── Orientation ──────────────────────────────────────────────
orientation = portrait

# ── Icon & Splash ────────────────────────────────────────────
icon.filename = %(source.dir)s/AI.png
presplash.filename = %(source.dir)s/AI.png

# ── IMPORTANT: Android Permissions ──────────────────────────
# FIX: Yeh permissions missing thi — isliye crash hota tha!
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# ── Android API levels ───────────────────────────────────────
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.ndk_api = 24

# ── Architecture ─────────────────────────────────────────────
android.archs = arm64-v8a, armeabi-v7a

# ── Entry point ──────────────────────────────────────────────
fullscreen = 0

# ── Android extras ───────────────────────────────────────────
android.allow_backup = True
android.wakelock = False

# ── Gradle ───────────────────────────────────────────────────
android.gradle_dependencies =

# ── p4a branch ───────────────────────────────────────────────
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
