[app]
title = Pro Voice Generator
package.name = voicebotpro
package.domain = org.pro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Requirements (No duplicates)
requirements = python3, kivy, gTTS, requests, certifi, android, ffpyplayer

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MODIFY_AUDIO_SETTINGS

android.api = 31
android.minapi = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
