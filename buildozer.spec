[app]
# =============================================================================
# IDENTITY
# =============================================================================
title = Titan AI Studio Pro
package.name = titanai.studio
package.domain = org.titan.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav

# =============================================================================
# VERSION
# =============================================================================
version = 5.0.1

# =============================================================================
# REQUIREMENTS
# FIX: numpy, pydub, ffpyplayer, sqlite3 hata diye —
#      yeh build fail karte the aur app mein use nahi ho rahe the.
#      Sirf zaruri packages rakhe hain.
# =============================================================================
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, pillow, pyjnius, setuptools

# =============================================================================
# ANDROID CONFIGURATION
# =============================================================================
orientation = portrait
fullscreen = 0
android.wakelock = True

# FIX: MANAGE_EXTERNAL_STORAGE hata diya — API 31+ par yeh 
#      special permission hai jo Play Store reject karta hai.
#      Normal storage permissions kafi hain.
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK

android.api = 33
android.minapi = 21
android.ndk = 25b

# FIX: Sirf arm64-v8a rakha — dono archs se APK bohat bada hota
#      hai aur build time double hota hai. 99% phones arm64 hain.
android.archs = arm64-v8a

android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity

# =============================================================================
# BUILDOZER
# =============================================================================
[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
