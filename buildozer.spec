# =============================================================
#  Titan Studio PRO — buildozer.spec
#  Version 12.0.0  |  FIXED EDITION
#  Target: Android ARM64 + ARMv7  |  API 33  |  Python 3.11
#
#  BUILD COMMAND:
#    buildozer android debug        ← for testing
#    buildozer android release      ← for Play Store
#
#  FIRST TIME SETUP:
#    pip install buildozer cython
#    buildozer android debug        ← downloads NDK/SDK automatically
#
#  NOTE: Run on Linux/Ubuntu. Windows users → use WSL2 or Docker.
#
#  FIXES v12.0.0:
#    ✅ edge-tts retry logic (3 attempts, 60s timeout)
#    ✅ Emoji icons removed — clean text labels
#    ✅ RTL keyboard support (Urdu/Arabic)
#    ✅ Better error messages
# =============================================================

[app]

# ── Identity ──────────────────────────────────────────────────
title           = Titan Studio PRO
package.name    = titanstudio.pro
package.domain  = org.titan.studio
version         = 12.0.0

# ── Source ────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,ttf,txt,wav,xml,md
source.include_patterns = assets/*,fonts/*,images/*,AI.png,AI.jpg,logo.png,p4a_recipes/*
source.exclude_dirs     = tests,bin,.buildozer,__pycache__,.git,venv,env
source.exclude_patterns = *.pyc,*.pyo,*.pyd,.DS_Store,Thumbs.db,*.spec.bak

# ── Requirements ──────────────────────────────────────────────
requirements =
    python3==3.11.0,
    kivy==2.2.1,
    edge-tts==6.1.9,
    aiohttp==3.9.3,
    aiosignal==1.3.1,
    frozenlist==1.4.1,
    async-timeout==4.0.3,
    attrs==23.2.0,
    multidict==6.0.5,
    yarl==1.9.4,
    websockets==12.0,
    gTTS==2.5.1,
    requests==2.31.0,
    certifi==2024.2.2,
    chardet==5.2.0,
    idna==3.6,
    urllib3==2.2.1,
    pillow==10.2.0,
    pyjnius,
    android,
    setuptools>=68.0.0

# ── p4a custom recipes ────────────────────────────────────────
p4a.local_recipes = ./p4a_recipes

# ── App Icon & Splash Screen ──────────────────────────────────
presplash.filename = %(source.dir)s/AI.png
icon.filename      = %(source.dir)s/AI.png

# Presplash background (matches C_BG = #020817)
android.presplash_color = #020817

# ── Orientation ───────────────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Android Platform ──────────────────────────────────────────
android.api         = 33
android.minapi      = 24
android.ndk         = 25b
android.ndk_api     = 24

# ARM64 (modern) + ARMv7 (older phones)
android.archs       = arm64-v8a, armeabi-v7a

# ── SDK ───────────────────────────────────────────────────────
android.skip_update        = False
android.accept_sdk_license = True
android.enable_androidx    = True
android.copy_libs          = 1

# ── Permissions ───────────────────────────────────────────────
android.permissions =
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    MANAGE_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    CHANGE_NETWORK_STATE,
    WAKE_LOCK,
    FOREGROUND_SERVICE

# ── Wakelock ──────────────────────────────────────────────────
android.wakelock        = True
android.allow_backup    = True

# ── Gradle ────────────────────────────────────────────────────
android.gradle_dependencies = com.google.android.material:material:1.9.0

# ── SDK versions ──────────────────────────────────────────────
android.compile_sdk_version  = 33
android.target_sdk_version   = 33
android.min_sdk_version      = 24

# ── App manifest metadata ─────────────────────────────────────
android.manifest.app_label    = Titan Studio PRO
android.manifest.version_name = 12.0.0
android.manifest.version_code = 120

# ── Activity ──────────────────────────────────────────────────
android.entrypoint  = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D kivy:D

# ── P4A bootstrap ────────────────────────────────────────────
p4a.bootstrap = sdl2

# ─────────────────────────────────────────────────────────────
[buildozer]

log_level   = 2
warn_on_root = 1
bin_dir = ./bin
