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
version = 5.1.0

# =============================================================================
# REQUIREMENTS
# — json stdlib hai, alag install nahi chahiye
# — shutil bhi stdlib hai
# — sirf wahi packages jo actually use ho rahe hain
# =============================================================================
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, pillow, pyjnius, setuptools

# =============================================================================
# ANDROID CONFIGURATION
# =============================================================================
orientation = portrait
fullscreen   = 0
android.wakelock = True

# Permissions:
# WRITE_EXTERNAL_STORAGE — Download folder mein save karne ke liye (zaruri)
# READ_EXTERNAL_STORAGE  — History se audio replay karne ke liye (zaruri)
# INTERNET               — gTTS server se connect karne ke liye (zaruri)
# ACCESS_NETWORK_STATE   — Internet check karne ke liye
# WAKE_LOCK              — Audio generate hote waqt screen off na ho
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK

android.api    = 33
android.minapi = 21
android.ndk    = 25b
android.archs  = arm64-v8a

android.skip_update      = False
android.accept_sdk_license = True
android.enable_androidx  = True
android.copy_libs        = 1
android.entrypoint       = org.kivy.android.PythonActivity

# =============================================================================
# BUILDOZER
# =============================================================================
[buildozer]
log_level    = 2
warn_on_root = 1
bin_dir      = ./bin
