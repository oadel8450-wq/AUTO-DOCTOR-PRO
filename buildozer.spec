
[app]

title = AUTO DOCTOR PRO
package.name = autodoctorpro
package.domain = com.aldlgroup

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf

version = 1.0
version_code = 1

requirements = python3,kivy,pyjnius,reportlab

orientation = portrait
fullscreen = 0

# Android SDK
android.api = 33
android.minapi = 23

# Android NDK
android.ndk = 25b

# Android architectures
android.archs = arm64-v8a, armeabi-v7a

# Python-for-Android
p4a.branch = master

# Android permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

# Android build settings
android.accept_sdk_license = True
android.allow_backup = True

# Application settings
android.private_storage = True
android.wakelock = True

# SDK update settings
android.skip_update = True

[buildozer]

log_level = 2
warn_on_root = 1
