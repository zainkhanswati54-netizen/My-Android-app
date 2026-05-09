# =============================================================
#  Titan AI Studio Pro — buildozer.spec
#  Version 1.0.0  |  Professional Voice Studio
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
# =============================================================

[app]

# ── Identity ──────────────────────────────────────────────────
title           = Titan AI Studio Pro
package.name    = titanai.studio.pro
package.domain  = org.titan.studio
version         = 1.0.0

# ── Source ────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,ttf,txt,wav,xml,md
source.include_patterns = assets/*,fonts/*,images/*,AI.png,AI.jpg,logo.png
source.exclude_dirs     = tests,bin,.buildozer,__pycache__,.git,venv,env
source.exclude_patterns = *.pyc,*.pyo,*.pyd,.DS_Store,Thumbs.db,*.spec.bak

# ── Requirements ──────────────────────────────────────────────
# edge-tts: Free Microsoft voices (male/female/mood aware)
# gTTS:     Google TTS fallback
# requests: ElevenLabs API + network calls
requirements =
    python3==3.11.0,
    kivy==2.2.1,
    edge-tts,
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

# Presplash background color (matches app dark theme #0A0E1A)
android.presplash_color = #0A0E1A

# ── Orientation & Display ─────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Android Platform ──────────────────────────────────────────
android.api         = 33
android.minapi      = 24
android.ndk         = 25b
android.ndk_api     = 24

# Build for both ARM64 (modern phones) and ARMv7 (older phones)
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
    MANAGE_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    WAKE_LOCK,
    FOREGROUND_SERVICE,
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

# ── App metadata for Play Store ───────────────────────────────
android.manifest.app_label    = Titan AI Studio Pro
android.manifest.version_name = 1.0.0
android.manifest.version_code = 1

# ── Activity config ───────────────────────────────────────────
android.entrypoint  = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D kivy:D

# ── Extra Java source files ───────────────────────────────────
android.add_jars =
android.add_src  =

# ── AAB vs APK ────────────────────────────────────────────────
# For direct install/testing: leave commented (produces APK)
# For Play Store upload: uncomment below (produces AAB)
# android.release_artifact = aab

# ── Signing (release builds only) ─────────────────────────────
# Generate keystore once:
#   keytool -genkey -v -keystore titan_release.keystore
#            -alias titan -keyalg RSA -keysize 2048 -validity 10000
#
# Then uncomment:
# android.keystore         = titan_release.keystore
# android.keystore_passwd  = YOUR_KEYSTORE_PASSWORD
# android.keyalias         = titan
# android.keyalias_passwd  = YOUR_KEY_PASSWORD

# ── P4A bootstrap ─────────────────────────────────────────────
p4a.bootstrap = sdl2

# ─────────────────────────────────────────────────────────────
[buildozer]

log_level    = 2
warn_on_root = 1
bin_dir      = ./bin
