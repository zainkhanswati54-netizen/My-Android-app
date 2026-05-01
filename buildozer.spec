[app]
title = Pro Voice Generator
package.name = voicebotpro
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# In requirements se app stable rahegi
requirements = python3, kivy, plyer, pyobjus, android

orientation = portrait
fullscreen = 0

# Android Hardware Settings
android.archs = arm64-v8a, armeabi-v7a
android.api = 31
android.minapi = 21
android.sdk = 31

# Permissions for hardware & storage
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MODIFY_AUDIO_SETTINGS

[buildozer]
log_level = 2
warn_on_root = 1
