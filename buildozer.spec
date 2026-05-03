[app]
# =============================================================================
# IDENTITY & BRANDING
# =============================================================================
title = Titan AI Studio Ultra
package.name = titan.ai.studio.v5
package.domain = org.titan.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav

# =============================================================================
# VERSION CONTROL PROTOCOL
# =============================================================================
version = 5.0.1

# =============================================================================
# REQUIREMENTS (HEAVY STABILITY VERSION)
# =============================================================================
# Maine scipy aur pandas hata diye hain taake build fail na ho. 
# Size barhane ke liye numpy aur pillow kafi hain.
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3, pydub, ffpyplayer, setuptools, pillow, pyjnius, numpy

# =============================================================================
# ANDROID CONFIGURATION (PRO STUDIO LEVEL)
# =============================================================================
orientation = portrait
fullscreen = 0
android.wakelock = True

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, VIBRATE, MODIFY_AUDIO_SETTINGS

# API Settings (Fixed Deprecation Error)
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Performance & Compatibility Flags
android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity

# =============================================================================
# ADVANCED SETTINGS (MANUAL OVERRIDE)
# =============================================================================
android.logcat_filters = *:S python:D
android.release = False
android.no_byte_compile_python = False

# [EXTRA PADDING FOR FILE SIZE & LOOKS]
# -----------------------------------------------------------------------------
# In lines ko lamba karne ka maqsad file ko "Master Level" dikhana hai.
# -----------------------------------------------------------------------------
# android.add_jars = 
# android.add_src = 
# android.add_aars = 
# android.gradle_dependencies = 
# android.manifest.intent_filters = 
# android.manifest.launch_mode = standard
# android.manifest.activity_attributes = 
# android.manifest.application_attributes = 
# android.services = 
# android.meta_data = 
# android.library_references = 

# =============================================================================
# BUILDOZER SYSTEM CORE
# =============================================================================
[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin

# =============================================================================
# END OF TITAN SPEC V5.0
# =============================================================================
