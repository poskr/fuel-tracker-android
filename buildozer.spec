[app]
# --- ОБЯЗАТЕЛЬНЫЕ ПОЛЯ ---
source.dir = .        # <- здесь точка означает «текущая папка»
version    = 1.0      # <- или любая другая строка версии

title               = FuelTracker
package.name        = fueltracker
package.domain      = com.yourdomain
source.include_exts = py,kv,png,jpg
requirements        = python3,kivy,requests
orientation         = portrait
fullscreen          = 0
android.permissions = INTERNET

[buildozer]
log_level    = 2
warn_on_root = 0
