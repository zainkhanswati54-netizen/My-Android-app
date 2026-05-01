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

# Ye permissions crash ko rokengi
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MODIFY_AUDIO_SETTINGS

# Requirements mein ffpyplayer add karna zaroori hai audio ke liye
requirements = python3, kivy, gTTS, requests, certifi, android, ffpyplayer

[buildozer]
log_level = 2
warn_on_root = 1
