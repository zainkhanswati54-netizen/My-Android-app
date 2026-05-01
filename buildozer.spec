[app]
title = Voice Bot Pro
package.name = voicebot
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Requirements
requirements = python3, kivy, gTTS, requests

orientation = portrait
fullscreen = 0

# Android specific
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
android.api = 31
android.minapi = 21
android.sdk = 31

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
