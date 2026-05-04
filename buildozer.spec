[app]
title = Titan AI Studio Pro
package.name = titanai.studio
package.domain = org.titan.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt,wav
version = 5.3.0

requirements = python3,kivy==2.2.1,gTTS,requests,certifi,chardet,idna,urllib3,pillow,pyjnius,setuptools

orientation = portrait
fullscreen = 0
android.wakelock = True

# Enhanced permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
