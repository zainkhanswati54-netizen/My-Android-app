[app]
title = Pro Voice Studio
package.name = voicestudio
package.domain = org.pro.voice
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Critical requirements for Audio and Internet
requirements = python3, kivy, gTTS, requests, certifi, android, ffpyplayer

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

# Permissions fix for Android 11+
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.accept_sdk_license = True

# Meta-data for storage stability
android.meta_data = android.permission.MANAGE_EXTERNAL_STORAGE=1

[buildozer]
log_level = 2
warn_on_root = 1
