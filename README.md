# EgyStickers — animated Egyptian stickers for WhatsApp (Android)

## Build
1. Install Android Studio (latest) and open this folder. Accept the Gradle/AGP upgrade prompt if shown.
2. Plug in a phone (USB debugging on) or start an emulator with WhatsApp, then press Run, or Build > Build APK(s).
3. In the app tap "ضيف الباك لواتساب" and confirm in WhatsApp.

## Add / change stickers
Edit tools/make_stickers.py (SPECS list), run `python3 tools/make_stickers.py` (needs `pip install pillow`).
It rewrites app/src/main/assets/{stickers,pack.json,tray.png}. Or drop your own files in assets/stickers and list them in pack.json.
WhatsApp limits for animated stickers: 512x512 WebP, <= 500 KB, <= 10 s, 3 to 30 stickers per pack, tray icon 96x96 < 50 KB.
