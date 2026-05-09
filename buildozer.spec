# =============================================================
#  Titan AI Studio Pro — buildozer.spec
#  Version 10.0.0  |  Ultra Mega Rewrite
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
version         = 10.0.0

# ── Source ────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,ttf,txt,wav,xml,md
source.include_patterns = assets/*,fonts/*,images/*,AI.png,AI.jpg,logo.png
source.exclude_dirs     = tests,bin,.buildozer,__pycache__,.git,venv,env
source.exclude_patterns = *.pyc,*.pyo,*.pyd,.DS_Store,Thumbs.db,*.spec.bak

# ── Main entry ────────────────────────────────────────────────
# If your file is named main.py, this line is auto-detected.
# Uncomment only if you rename it:
# android.entrypoint_activity = main

# ── Requirements ──────────────────────────────────────────────
# Pinned for reproducible builds. Do NOT remove version pins.
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
# Place AI.png in same folder as this spec file.
# Recommended size: 512x512 px for icon, 1024x500 px for presplash.
presplash.filename = %(source.dir)s/AI.png
icon.filename      = %(source.dir)s/AI.png

# Presplash background color (matches app C_BG = #020817)
android.presplash_color = #020817

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
# All permissions needed by Titan AI Studio Pro:
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
# Use gradle for better compatibility
android.gradle_dependencies = com.google.android.material:material:1.9.0

# ── Java / Kotlin version ─────────────────────────────────────
android.compile_sdk_version  = 33
android.target_sdk_version   = 33
android.min_sdk_version      = 24

# ── Adaptive Icon (Android 8.0+) ─────────────────────────────
# Uncomment if you have separate foreground/background icon files:
# android.adaptive_icon_fg = %(source.dir)s/icon_fg.png
# android.adaptive_icon_bg = %(source.dir)s/icon_bg.png

# ── App metadata for Play Store ───────────────────────────────
# These appear in Google Play Store listing:
android.manifest.app_label    = Titan AI Studio Pro
android.manifest.version_name = 10.0.0
android.manifest.version_code = 100

# ── Network Security (required for HTTP in newer Android) ──────
# Allows gTTS to connect (it uses HTTPS, so this is fine):
# android.manifest.network_security_config = network_security_config.xml

# ── Activity config ───────────────────────────────────────────
android.entrypoint  = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D kivy:D

# Screen stays on while generating audio
android.add_activities =

# ── Extra Java source files (optional) ────────────────────────
android.add_jars =
android.add_src  =

# ── AAB vs APK ────────────────────────────────────────────────
# For direct install / testing: leave commented (produces APK)
# For Play Store upload: uncomment the line below (produces AAB)
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

# ── P4A (python-for-android) bootstrap ───────────────────────
# sdl2 is the standard bootstrap for Kivy apps
p4a.bootstrap = sdl2

# ── P4A source (optional, use if you need latest p4a fixes) ───
# p4a.source_dir = /path/to/python-for-android

# ── Local recipes (optional) ──────────────────────────────────
# p4a.local_recipes = ./p4a_recipes

# ── iOS (not configured — Android only) ───────────────────────
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

# ─────────────────────────────────────────────────────────────
[buildozer]

# Log verbosity: 0 = quiet, 1 = normal, 2 = verbose (recommended)
log_level   = 2
warn_on_root = 1

# Output directory for compiled APK/AAB
bin_dir = ./bin

# ── Build cache ───────────────────────────────────────────────
# Speeds up repeated builds. Do NOT delete .buildozer/ between builds
# unless you're fixing dependency issues.
# To force clean rebuild: buildozer android clean && buildozer android debug
