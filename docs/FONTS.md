# Bundled offline font

PDF reports use the bundled Noto Sans Regular font to render and embed Uzbek Latin text on Windows, Linux and Qt's offscreen platform. System fonts alone are insufficient on the Windows offscreen platform. The application explicitly loads the font through `QFontDatabase.addApplicationFont`; PDF generation fails clearly if its resource cannot be loaded.

Upstream source: https://github.com/notofonts/noto-fonts

Downloaded over verified HTTPS from:

- `https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf`
- `https://raw.githubusercontent.com/notofonts/noto-fonts/main/LICENSE`

Bundled file: `app/resources/fonts/NotoSans-Regular.ttf` (569,208 bytes).

SHA-256: `b85c38ecea8a7cfb39c24e395a4007474fa5a4fc864f6ee33309eb4948d232d5`.

The SIL Open Font License is included unchanged as `app/resources/fonts/OFL.txt`. PyInstaller includes both files. No runtime font download or online font service is used. The application UI prefers Segoe UI where available, with Noto Sans and DejaVu Sans as fallbacks.
