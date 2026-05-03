[app]
# (section) Title of your application
title = Titan AI Studio Ultra

# (section) Package name
package.name = titan_ai_ultra
package.domain = org.titan.dev

# (section) Source code where the main.py lives
source.dir = .

# (section) Source files to include (otf aur jpg lazmi hain aapke assets ke liye)
source.include_exts = py,png,jpg,kv,atlas,otf,ttf,txt
source.include_patterns = assets/*

# (section) Application version
version = 6.0.0

# (section) Application requirements
# Numpy add karne se size 40MB+ ho jayega aur processing fast hogi
requirements = python3, kivy==2.3.0, gtts, requests, certifi, urllib3, numpy, pillow

# (section) Supported orientations
orientation = portrait

# (section) Android specific settings
fullscreen = 1
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# (section) Permissions (Storage access ke liye zaroori hain)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# (section) Android architecture
android.archs = arm64-v8a, armeabi-v7a

# (section) Allow root build (GitHub Actions ke liye lazmi)
warn_on_root = 0

# (section) Icon and Splash Screen (Optional: agar aapke paas hain)
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/splash.png

[buildozer]
log_level = 2
warn_on_root = 0
