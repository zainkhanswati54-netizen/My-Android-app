[app]

# (str) Title of your application
title = Titan AI Voice Studio Pro

# (str) Package name
package.name = titanai.studiopro

# (str) Package domain (needed for android packaging)
package.domain = org.titan.corp

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,mp3,json,ttf

# (str) Application version
version = 3.0.1

# (list) Application requirements
# Maine extra heavy libraries add ki hain taake size bada rahe aur app stable ho
requirements = python3, kivy==2.2.1, gTTS, requests, certifi, chardet, idna, urllib3, android, hostpython3, openssl, sqlite3, pydub, ffpyplayer, setuptools

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) use manual orientation
android.skip_update = False

# (bool) if True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) enable AndroidX support (Critical for new phones)
android.enable_androidx = True

# (list) The Android libs to copy in the libs directory
# Isse app ka size maintain rehta hai aur crash nahi hota

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Copy library to project
android.copy_libs = 1

# (str) The name of the main activity
android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to exclude from the APK
# Inhe empty rakhein taake koi zaroori cheez delete na ho
android.exclude_exts = 

# (str) Path to a custom whitelist file
# android.whitelist = 

# (list) List of Java classes to add to the compilation classpath
# android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) Java sources to add to the project
# android.add_src = 

# (list) Android AAR archives to add
# android.add_aars = 

# (list) Gradle dependencies
# android.gradle_dependencies = 

# (list) add external libraries to copy into the lib directory
# android.add_libs_armeabi_v7a = libs/armeabi-v7a/libfoo.so

# (bool) indicates whether the screen should stay on
android.wakelock = True

# (list) Android meta-data messages
# android.meta_data = 

# (list) Android runtime permissions
# android.runtime_permissions = 

# (str) Android OBB mode
# android.obb_mode = main

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifacts
bin_dir = ./bin

# (list) List of architectures to build
# architectures = armeabi-v7a, arm64-v8a
