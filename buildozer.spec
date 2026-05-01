[app]
title = Pro Voice Bot
package.name = voicebotpro
package.domain = org.pro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Simple and Clean Requirements
requirements = python3, kivy, gTTS, requests, certifi, android
orientation = portrait
fullscreen = 0

# Android Architecture
android.archs = arm64-v8a, armeabi-v7a
android.api = 31
android.minapi = 21

# Necessary Permissions
android.permissions = INTERNET, MODIFY_AUDIO_SETTINGS

[buildozer]
log_level = 2
warn_on_root = 1
