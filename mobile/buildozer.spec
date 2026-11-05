[app]
title = QR Connect
package.name = qrconnect
package.domain = org.qrconnect
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg
version = 0.2.0
requirements = python3,kivy==2.3.1,requests,plyer
orientation = portrait
fullscreen = 0

[android]
permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 35
android.minapi = 26
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
