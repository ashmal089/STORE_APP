[app]
# (str) Title of your application
title = MyApp

# (str) Package name
package.name = myapp

# (str) Package domain (must be unique)
package.domain = org.example

# (str) Source code where main.py is located
source.dir = .

# (str) Main .py file of your app
source.main = main.py

# (list) List of inclusions using pattern matching
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application requirements
# Example: requirements = python3,kivy
requirements = python3,kivy

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions required by your app (comma-separated)
android.permissions = INTERNET

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# (str) Path to the icon
icon.filename = %(source.dir)s/data/icon.png

[buildozer]
# (int) Log level (0 = error, 1 = warn, 2 = info, 3 = debug)
log_level = 2

# (str) The directory where the buildozer state is stored
build_dir = .buildozer

# (str) Android SDK/NDK versions
android.sdk = 24
android.ndk = 23b

# (bool) Copy library instead of linking
copy_libs = 1

[android]
# (list) Android application requirements (comma-separated)
requirements = python3,kivy

# (str) Android entry point
entrypoint = org.kivy.android.PythonActivity

