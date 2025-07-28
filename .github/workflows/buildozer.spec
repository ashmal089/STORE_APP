[app]

# (str) Title of your application
title = My Billing App

# (str) Package name
package.name = mybillingapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mycompany

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# (list) Application requirements
# (add any additional libraries your app needs)
requirements = python3,kivy

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions (add permissions if your app needs them)
#android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Target Android API (recommended is 31 or latest supported)
android.api = 31

# (list) The Android architectures to build for.
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support (for modern apps)
android.enable_androidx = True

# (bool) Indicate whether the screen should stay on
#android.wakelock = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (str) Path to build output (apk will be here)
# bin_dir = ./bin
