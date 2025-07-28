[app]
# (str) Title of your application
title = MyKivyApp

# (str) Package name
package.name = mykivyapp

# (str) Package domain (must be unique)
package.domain = org.example

# (str) Source code where main.py is located
source.dir = .

# (str) Main .py file of your app
source.main = main.py

# (list) List of inclusions using pattern matching
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0.0

# (str) Application requirements
# Example: requirements = python3,kivy,requests
requirements = python3,kivy

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions required by your app
android.permissions = INTERNET

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

[buildozer]
# (int) Log level (0 = error, 1 = warn, 2 = info, 3 = debug)
log_level = 2

# (str) Directory where buildozer state is stored
build_dir = .buildozer

# (bool) Copy library instead of linking
copy_libs = 1

[android]
# (list) Android application requirements
requirements = python3,kivy

# (str) Android entry point
entrypoint = org.kivy.android.PythonActivity

