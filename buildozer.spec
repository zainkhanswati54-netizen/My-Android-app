# =============================================================
#  Titan AI Studio Pro — buildozer.spec  v1.1.0  (Fixed)
#  Target: Android ARM64 + ARMv7  |  API 33  |  Python 3.11
# =============================================================

[app]

# ── Identity ──────────────────────────────────────────────────
title           = Titan AI Studio Pro
package.name    = titanai.studio.pro
package.domain  = org.titan.studio
version         = 1.1.0

# ── Source ────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,ttf,txt,wav,xml,md
source.include_patterns = assets/*,fonts/*,images/*,AI.png,AI.jpg,logo.png
source.exclude_dirs     = tests,bin,.buildozer,__pycache__,.git,venv,env
source.exclude_patterns = *.pyc,*.pyo,*.pyd,.DS_Store,Thumbs.db,*.spec.bak

# ── Requirements ──────────────────────────────────────────────
# IMPORTANT: edge-tts REMOVED — asyncio crashes Android
# gTTS is the primary TTS engine (Android compatible)
# requests: ElevenLabs API support
requirements =
    python3==3.11.0,
    kivy==2.2.1,
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

# ── App Icon & Splash Screen ──────────────────────────────────
presplash.filename = %(source.dir)s/AI.png
icon.filename      = %(source.dir)s/AI.png
android.presplash_color = #0A0E1A

# ── Orientation & Display ─────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Android Platform ──────────────────────────────────────────
android.api         = 33
android.minapi      = 24
android.ndk         = 25b
android.ndk_api     = 24
android.archs       = arm64-v8a, armeabi-v7a

# ── Android SDK / Build Tools ─────────────────────────────────
android.skip_update        = False
android.accept_sdk_license = True
android.enable_androidx    = True
android.copy_libs          = 1

# ── Permissions ───────────────────────────────────────────────
android.permissions =
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    WAKE_LOCK,
    RECORD_AUDIO

# ── Android Features ──────────────────────────────────────────
android.wakelock        = True
android.allow_backup    = True

# ── Gradle / Java build ───────────────────────────────────────
android.gradle_dependencies = com.google.android.material:material:1.9.0

# ── Java / Kotlin version ─────────────────────────────────────
android.compile_sdk_version  = 33
android.target_sdk_version   = 33
android.min_sdk_version      = 24

# ── App metadata ──────────────────────────────────────────────
android.manifest.app_label    = Titan AI Studio Pro
android.manifest.version_name = 1.1.0
android.manifest.version_code = 2

# ── Activity config ───────────────────────────────────────────
android.entrypoint  = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D kivy:D

android.add_jars =
android.add_src  =

# ── P4A bootstrap ─────────────────────────────────────────────
p4a.bootstrap = sdl2

# ─────────────────────────────────────────────────────────────
[buildozer]

log_level    = 2
warn_on_root = 1
bin_dir      = ./bin
