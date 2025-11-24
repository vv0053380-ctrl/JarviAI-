[app]
title = Jarvis Ultimate
package.name = jarvis.ultimate.pro
package.domain = org.vinay
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 2.0
HEAVY REQUIREMENTS (KivyMD + Network + Audio)
requirements = python3,kivy==2.3.0,kivymd,requests,gtts,android,pyjnius,pillow
FULL PERMISSIONS FOR AUTOMATION
android.permissions = INTERNET,RECORD_AUDIO,CALL_PHONE,READ_CONTACTS,WRITE_EXTERNAL_STORAGE
ANDROID 14 SETTINGS
android.api = 34
android.minapi = 24
android.accept_sdk_license = True
android.presplash_color = #000000
orientation = portrait
fullscreen = 1
[buildozer]
log_level = 2
warn_on_root = 1
