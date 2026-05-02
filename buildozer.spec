[app]
title = Pro Voice Studio
package.name = voicestudiopro
package.domain = org.pro.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Critical Fix: Added 'chardet' and 'idna' for network stability
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, android, ffpyplayer

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.accept_sdk_license = True
android.meta_data = android.permission.MANAGE_EXTERNAL_STORAGE=1

[buildozer]
log_level = 2
warn_on_root = 1
