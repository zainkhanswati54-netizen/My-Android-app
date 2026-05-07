# =============================================================
#  Titan AI Studio Pro — buildozer.spec
#  Version 6.0.0  |  Industry-Standard Configuration
#  Target: Android ARM64  |  API 33  |  Python 3.10
# =============================================================

[app]

# ── Identity ──────────────────────────────────────────────────
title           = Titan AI Studio Pro
package.name    = titanai.studio
package.domain  = org.titan.studio
version         = 6.0.0

# ── Source ────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,ttf,txt,wav,xml
source.include_patterns = assets/*,fonts/*,images/*
source.exclude_dirs     = tests,bin,.buildozer,__pycache__,.git
source.exclude_patterns = *.pyc,*.pyo,*.pyd,.DS_Store,Thumbs.db

# ── Requirements ──────────────────────────────────────────────
# All deps pinned for reproducible builds
requirements =
    python3,
    kivy==2.2.1,
    kivymd,
    gTTS==2.5.1,
    requests==2.31.0,
    certifi==2024.2.2,
    chardet==5.2.0,
    idna==3.6,
    urllib3==2.2.1,
    pillow==10.2.0,
    pyjnius,
    setuptools

# ── Presplash & Icon ──────────────────────────────────────────
presplash.filename = %(source.dir)s/AI.png
icon.filename      = %(source.dir)s/AI.png

# ── Orientation & Display ─────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Android Platform ──────────────────────────────────────────
android.api         = 33
android.minapi      = 24
android.ndk         = 25b
android.ndk_api     = 24
android.archs       = arm64-v8a

# ── Android SDK / Build Tools ─────────────────────────────────
android.skip_update     = False
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs       = 1

# ── Permissions ───────────────────────────────────────────────
android.permissions =
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    WAKE_LOCK

# ── Hardware features ─────────────────────────────────────────
android.wakelock    = True

# ── Entry Point ───────────────────────────────────────────────
android.entrypoint  = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D

# ── App extras ────────────────────────────────────────────────
android.add_jars =

# ── Meta / Store ──────────────────────────────────────────────
# Uncomment when publishing to Play Store:
# android.release_artifact = aab

[buildozer]
log_level   = 2
warn_on_root = 1
bin_dir     = ./bin
