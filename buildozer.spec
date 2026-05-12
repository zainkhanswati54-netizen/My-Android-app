[app]

# ── Basic Info ──────────────────────────────────────────────
title = Titan Studio PRO
package.name = titanstudiopro
package.domain = org.titanstudio

# ── Source ──────────────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_dirs = tests, bin, build, .git, __pycache__, venv, .venv

# ── Version ─────────────────────────────────────────────────
version = 1.0.0

# ── Requirements ────────────────────────────────────────────
# FIX v1.2: aiohttp pinned to ==3.10.11 (fixes Python 3.14 build errors)
# FIX v1.3: kivy upgraded to ==2.3.1 (fixes Python 3.14 Cython C errors):
#   - 'too few arguments to function call, expected 6, have 5'
#   - 'member reference type int is not a pointer'
requirements = python3,kivy==2.3.1,gtts,requests,urllib3,certifi,charset-normalizer,idna,edge-tts==6.1.9,aiohttp==3.10.11,aiofiles,multidict,yarl,frozenlist,async-timeout,attrs

# ── Orientation ─────────────────────────────────────────────
orientation = portrait

# ── Icon & Presplash ────────────────────────────────────────
# Place your icon file (png, 512x512 recommended) in project root
# and uncomment these lines:
# icon.filename = %(source.dir)s/AI.png
# presplash.filename = %(source.dir)s/presplash.png

# ── Android Permissions ─────────────────────────────────────
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# ── Android API Levels ──────────────────────────────────────
# minapi 21 = Android 5.0+
# target 33 = Android 13 (stable for most apps)
android.minapi = 21
android.ndk_api = 21
android.api = 33

# ── Architecture ────────────────────────────────────────────
# arm64-v8a  = modern phones (2016+), 64-bit
# armeabi-v7a = older phones, 32-bit
# Build both for maximum compatibility
android.archs = arm64-v8a, armeabi-v7a

# ── Android SDK/NDK ─────────────────────────────────────────
# Buildozer auto-downloads these. Set versions explicitly for reproducibility.
android.ndk = 25b
android.sdk = 33

# ── Android Features ────────────────────────────────────────
android.allow_backup = True
android.wakelock = False

# ── Entry Point ─────────────────────────────────────────────
# The class name inside main.py that extends App
android.entrypoint = org.kivy.android.PythonActivity

# ── Fullscreen ──────────────────────────────────────────────
fullscreen = 0

# ── Log Level ───────────────────────────────────────────────
log_level = 2

# ── p4a (python-for-android) ────────────────────────────────
# Uncomment to use local p4a recipes directory
# p4a.local_recipes = %(source.dir)s/p4a_recipes

# p4a branch - use develop for latest fixes
# p4a.branch = develop

# Uncomment if you need to patch p4a source
# p4a.source_dir = /path/to/python-for-android

[buildozer]

# ── Build Directory ─────────────────────────────────────────
# Where build artifacts are stored
build_dir = ./.buildozer

# ── Bin Directory ───────────────────────────────────────────
# Where the final APK is placed
bin_dir = ./bin

# ── Warn on root ────────────────────────────────────────────
warn_on_root = 1

# ── Android Debug Key ───────────────────────────────────────
# For release builds, set your keystore details here:
# android.keystore = /path/to/your/keystore.jks
# android.keystore_alias = your_alias
# android.keystore_passwd = your_password
# android.keyalias_passwd = your_key_password
