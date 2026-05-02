[app]
title = Titan AI Studio Ultra
package.name = titan.ai.studio.v6
package.domain = org.titan.godmode
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav
version = 6.0.9

requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3, pydub, ffpyplayer, setuptools, pillow, pyjnius, numpy

orientation = portrait
fullscreen = 0
android.wakelock = True

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, VIBRATE, MODIFY_AUDIO_SETTINGS

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.enable_androidx = True
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
