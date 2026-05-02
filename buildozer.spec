[app]
title = Pro Voice Generator
package.name = voicebotpro
package.domain = org.pro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Requirements: Ismein ffpyplayer audio driver ka kaam karega
requirements = python3, kivy, gTTS, requests, certifi, android, ffpyplayer

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

# Permissions: Storage access ke liye ye lazmi hain
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MODIFY_AUDIO_SETTINGS

# Android SDK Settings
android.api = 31
android.minapi = 21
android.accept_sdk_license = True

# Isse app ko storage ki full access milti hai (Naye Androids ke liye)
android.meta_data = android.permission.MANAGE_EXTERNAL_STORAGE=1

[buildozer]
log_level = 2
warn_on_root = 1
