[app]
title = AI Voice Studio Titan
package.name = aivoicestudiotitan
package.domain = org.titan.voice
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3
version = 2.1.0

# Adding MORE packages to increase size and stability
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3

orientation = portrait
android.archs = arm64-v8a, armeabi-v7a
android.api = 31
android.minapi = 21

# Size and stability fixes
android.copy_libs = 1
android.accept_sdk_license = True
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# High quality build settings
android.release_artifact = apk
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
