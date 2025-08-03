[app]
# --------------------------------------------------------------------------
# (Обязательные поля)
# --------------------------------------------------------------------------
title                = Fuel Tracker
package.name         = fueltracker
package.domain       = org.example
source.dir           = .
source.include_exts  = py,png,jpg,kv,atlas
version              = 1.0
requirements         = python3,kivy,requests
orientation          = landscape
fullscreen           = 0
android.permissions  = INTERNET

# --------------------------------------------------------------------------
# Настройки Android
# --------------------------------------------------------------------------
android.api          = 33
android.minapi       = 21
android.sdk          = 33
android.ndk          = 25b
android.archs        = arm64-v8a

[buildozer]
log_level            = 2
warn_on_root         = 1
