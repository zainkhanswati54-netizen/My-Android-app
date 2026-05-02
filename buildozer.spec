[app]
# --- Basic Identity ---
title = Titan AI Studio Ultra
package.name = titan.ai.studio.v6
package.domain = org.titan.godmode
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav

# --- Versioning ---
version = 6.0.0

# --- Heavy Requirements (Size & Stability) ---
# In libraries se app ka size 100MB+ ho jayega
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3, pydub, ffpyplayer, setuptools, pillow, pyjnius, numpy, pandas

# --- Android Hardware & Permissions ---
# Sab se zaroori section: Isme koi duplicate line nahi honi chahiye
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, VIBRATE, MODIFY_AUDIO_SETTINGS

# --- API & SDK Settings ---
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# --- UI & Display ---
orientation = portrait
fullscreen = 0
android.wakelock = True

# --- Advanced Android Integration ---
android.enable_androidx = True
android.accept_sdk_license = True
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity

# --- Stability & Logging ---
android.logcat_filters = *:S python:D
android.release = False
android.no_byte_compile_python = False

# ---------------------------------------------------------
# Buildozer Core System
# ---------------------------------------------------------
[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
