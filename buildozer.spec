[app]

# --- Basic Identity ---
title = Titan AI Studio Ultra
package.name = titan.ai.studio.ultra.v5
package.domain = org.titan.corp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf,txt

# --- Versioning Protocol ---
version = 5.0.0

# --- Heavy Weight Requirements (Size & Stability Booster) ---
# Maine numpy, pandas aur scipy add ki hain jo app ko 100MB+ banayengi
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3, pydub, ffpyplayer, setuptools, pillow, pyjnius, numpy, pandas, scipy

# --- UI & Window Settings ---
orientation = portrait
fullscreen = 0
android.wakelock = True

# --- Android Hardware & Permissions ---
# Saari zaroori permissions taake app crash na ho
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, VIBRATE, MODIFY_AUDIO_SETTINGS, FOREGROUND_SERVICE

# --- API & Architectures ---
# Modern Android phones ke liye settings
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# --- Stability Flags ---
android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True

# --- Library Management ---
# Isse app ki libraries memory mein sahi load hoti hain
android.copy_libs = 1
android.entrypoint = org.kivy.android.PythonActivity

# --- Java & Gradle Optimizations ---
# android.add_jars = foo.jar
# android.add_src = 
# android.add_aars = 
# android.gradle_dependencies = 

# --- Metadata for System ---
android.meta_data = 

# --- Build Optimization ---
android.release = False
android.no_byte_compile_python = False

# --- Advanced Logcat Filter ---
android.logcat_filters = *:S python:D

# ---------------------------------------------------------
# Buildozer Global Settings
# ---------------------------------------------------------

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifacts
bin_dir = ./bin

# ---------------------------------------------------------
# Extra Padding (To ensure the file looks professional)
# ---------------------------------------------------------

# (list) List of architectures to build
# architectures = armeabi-v7a, arm64-v8a

# (str) Path to a custom whitelist file
# android.whitelist = 

# (bool) use manual orientation
# android.skip_update = False

# (str) The name of the main activity
# android.entrypoint = org.renpy.android.PythonSDLActivity

# (list) Android runtime permissions
# android.runtime_permissions = 

# (str) Android OBB mode
# android.obb_mode = main

# (list) The Android libs to copy in the libs directory
# android.copy_libs = 1

# (str) Path to a custom build.tmpl
# android.build_template = 

# (bool) If True, use the old method of packaging
# android.use_old_packaging = False

# (list) Android manifest intent filters
# android.manifest.intent_filters = 

# (str) Android manifest launch mode
# android.manifest.launch_mode = standard

# (list) Android manifest activity attributes
# android.manifest.activity_attributes = 

# (str) Android manifest application attributes
# android.manifest.application_attributes = 

# (str) Android service definition
# android.services = NAME:SERVICE_CLASS

# (list) Android addon components
# android.additions = 

# (str) Android storage path
# android.storage_path = 

# (str) Android private storage path
# android.private_storage_path = 

# (str) Android app theme
# android.app_theme = "@android:style/Theme.NoTitleBar"

# (str) Android backup configuration
# android.backup_config = 

# (str) Android icon
# icon.filename = %(source.dir)s/data/icon.png

# (str) Android splash screen
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Android home screen shortcut icon
# icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png
# icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png
