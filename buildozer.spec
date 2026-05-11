[app]

# ── Basic Info ──────────────────────────────────────────────
title = Titan Studio PRO
package.name = titanstudiopro
package.domain = org.titanstudio

# ── Source ──────────────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,ttf,json,wav,pt,onnx
source.exclude_dirs = tests, bin, build, .git, __pycache__, venv, .venv

# ── Version ─────────────────────────────────────────────────
version = 2.0.0

# ── Requirements ────────────────────────────────────────────
# Kokoro TTS replaces edge-tts.
# kokoro needs numpy, soundfile (libsndfile), and torch (or onnxruntime).
# For Android, onnxruntime is lighter than torch.
#
# IMPORTANT: kokoro on Android uses onnxruntime backend.
# If kokoro build fails, use the lightweight kokoro-onnx package:
#   Change 'kokoro' to 'kokoro-onnx' below.
#
# soundfile on Android needs libsndfile.so - included via p4a recipe.
# numpy is available as a p4a recipe.
requirements = python3,kivy==2.3.0,gtts,requests,urllib3,certifi,charset-normalizer,idna,numpy,soundfile,onnxruntime,kokoro

# ── Orientation ─────────────────────────────────────────────
orientation = portrait

# ── Icon & Presplash ────────────────────────────────────────
icon.filename = %(source.dir)s/AI.png
# presplash.filename = %(source.dir)s/presplash.png

# ── Android Permissions ─────────────────────────────────────
# INTERNET needed for gTTS fallback (non-English languages)
# WRITE/READ for saving audio files
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# ── Android API Levels ──────────────────────────────────────
# minapi 21 = Android 5.0+
# target 33 = Android 13
android.minapi = 24
android.ndk_api = 24
android.api = 33

# ── Architecture ────────────────────────────────────────────
# arm64-v8a  = modern phones (2016+), 64-bit
# armeabi-v7a = older phones, 32-bit
android.archs = arm64-v8a, armeabi-v7a

# ── Android SDK/NDK ─────────────────────────────────────────
android.ndk = 25b
android.sdk = 33

# ── Android Features ────────────────────────────────────────
android.allow_backup = True
android.wakelock = False

# ── Entry Point ─────────────────────────────────────────────
android.entrypoint = org.kivy.android.PythonActivity

# ── Fullscreen ──────────────────────────────────────────────
fullscreen = 0

# ── Log Level ───────────────────────────────────────────────
log_level = 2

# ── p4a (python-for-android) ────────────────────────────────
# Use develop branch for latest numpy/soundfile recipe fixes
# p4a.branch = develop

# ── Extra libs for soundfile (libsndfile) ───────────────────
# android.add_libs_armeabi_v7a = libs/armeabi-v7a/libsndfile.so
# android.add_libs_arm64_v8a   = libs/arm64-v8a/libsndfile.so

[buildozer]

# ── Build Directory ─────────────────────────────────────────
build_dir = ./.buildozer

# ── Bin Directory ───────────────────────────────────────────
bin_dir = ./bin

# ── Warn on root ────────────────────────────────────────────
warn_on_root = 1

# ── Android Debug Key ───────────────────────────────────────
# For release builds:
# android.keystore = /path/to/your/keystore.jks
# android.keystore_alias = your_alias
# android.keystore_passwd = your_password
# android.keyalias_passwd = your_key_password
