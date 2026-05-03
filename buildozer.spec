[app]
# (str) Title of your application
title = Titan AI Studio

# (str) Package name
package.name = titan_ai_studio

# (str) Package domain (needed for android packaging)
package.domain = org.titan

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let's include everything needed for HQ)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (str) Application versioning
version = 1.0.6

# (list) Application requirements
# Research says: Precise versions prevent dependency hell
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, pillow

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# --- Android Specific Settings ---

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API (31 is the sweet spot for modern phones)
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Use the private storage for your app (Recommended)
android.private_storage = True

# (str) Android architectures to build for
# Fix: Sirf arm64-v8a use karein GitHub Actions ki storage bachane ke liye
android.archs = arm64-v8a

# (bool) Allow the app to accept SDK licenses automatically
android.accept_sdk_license = True

# (bool) Enable AndroidX (Mandatory for modern Kivy)
android.enable_androidx = True

# --- Buildozer Config ---

[buildozer]
# (int) Log level (2 = Error/Debug for detailed troubleshooting)
log_level = 2

# (int) Warn on root (True because we build as root on GitHub)
warn_on_root = 1
