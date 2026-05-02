[app]

# (str) Title of your application
title = AI Voice Studio Elite

# (str) Package name
package.name = aivoicestudioelite

# (str) Package domain (needed for android packaging)
package.domain = org.zain.voicepro

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,mp3

# (str) Application version
version = 1.0.1

# (list) Application requirements
# CRITICAL: Added all dependencies to prevent startup crash
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

# (list) The Android libs to copy in the libs directory
# This helps in maintaining app stability and size
android.copy_libs = 1

# (bool) if True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) if True, then automatically accept SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = NO, 1 = YES)
warn_on_root = 1
