[app]
title = My text to voice
package.name = voicebot
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3, kivy, gTTS, requests, ffpyplayer
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
p4a.branch = master
# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21
[buildozer]
log_level = 2
warn_on_root = 1
