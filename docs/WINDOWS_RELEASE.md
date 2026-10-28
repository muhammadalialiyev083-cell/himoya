# Windows build and verification — UzHi 1.1.0

## Download and evidence

[GitHub Releases](https://github.com/muhammadalialiyev083-cell/himoya/releases) contains versioned Windows previews. The new design is identified by `v1.1.0-uzhi.<run-number>`. Each successful release includes the actual `UzluksizBCMS.exe`, SHA256SUMS.txt, Windows pytest XML and packaged verification JSON. The associated [Actions run](https://github.com/muhammadalialiyev083-cell/himoya/actions/workflows/windows-build.yml) contains screenshots and complete logs. An earlier `windows-mvp-*` release has the previous UI.

The build runs on Windows Server 2022 with Python 3.12 x64, PySide6 and PyInstaller. It verifies x64 PE headers and GUI subsystem, launches the frozen program without development PYTHONPATH, validates authentication, SQLite, backup/restore, PDF/CSV and starts a second EXE process to authenticate and verify persisted records. The binary bundles Qt platform plugins, native SVG identity, arrow assets, licensed Noto Sans TTF, schema and offline manual. No Linux executable is renamed to .exe.

Pull requests build test artifacts without publishing a release. Main/tag pushes publish a **prerelease only after all automated Windows and scaled UI checks pass**. A failed test, package launch, export, restart or geometry check prevents publication. No review/check override is used for merging.

## Build locally

1. Extract the source into an empty folder on Windows 10/11 x64. Do not copy a Linux virtual environment.
2. Install Python 3.12 x64 on the build machine; end users do not need Python.
3. In PowerShell run `./build.ps1`. It creates a venv, installs pinned dependencies, runs pytest, generates the original UzHi ICO, builds the windowed one-file EXE and runs both packaged smoke processes.
4. The output is `dist/UzluksizBCMS.exe`; verification metadata is in `release/win32-package-verification.json` and `release/SHA256SUMS.txt`.
5. Run `.venv/Scripts/python.exe scripts/capture_ui.py --output release/visual-review` with `QT_QPA_PLATFORM=offscreen` for additional isolated screenshots. CI repeats this at scale factors 1, 1.25 and 1.5.

## Native interactive Windows sign-off — still required

The automated checks use Qt's offscreen platform. They do not establish human desktop usability, clean-machine operation or physical monitor scaling. The downloadable preview is unsigned and has not received that interactive sign-off.

1. Use Windows 10/11 x64 without Python installed. Remove any process-only `QT_QPA_PLATFORM`/`QT_SCALE_FACTOR` overrides, disconnect the network, and double-click the EXE. Confirm native GUI, correct icon and no console/browser.
2. At 1366×768 and 1920×1080, repeat at Windows display scaling 100%, 125%, 150%. Verify readable login, no clipped labels, scrollable pages/dialogs, visible focus, popups and SVG icons in both themes.
3. Create your own administrator (10+ character password). Test mismatch, invalid login, visibility toggle, Enter/Esc, password change and restart authentication. No default password exists.
4. Use all six sidebar groups, module search (Ctrl+K), compact mode (Ctrl+B), keyboard activation, Back/Forward (Alt+Left/Right), breadcrumbs/home and the five native menus. Theme and motion choices must persist.
5. Create organization → department → process → BIA → risk → strategy → plan with ordered steps → scenario. F=4, O=5, R=3, C=3 must yield BIA 80/Kritik; likelihood=4 × impact=4 must yield 16/Kritik. An 8-hour disruption with RTO=4, MTPD=24 exceeds RTO, not MTPD.
6. Verify KPI links, filters, charts and empty states. Export assessment PDF, register PDF/CSV and plan PDF, including Uzbek `Oʻ oʻ Gʻ gʻ` and long multipage content.
7. Close/reopen while offline; confirm data remains at `%LOCALAPPDATA%\UzluksizBCMS\uzluksiz.sqlite3`. Existing records must survive upgrading from 1.0.0. Never replace this directory with the source/build output.
8. Back up, edit, restore and authenticate with the restored account. Check the automatic pre-restore safety file. Cancelled or invalid restore must leave records intact.
9. Record OS, physical resolution/scaling, EXE SHA-256, date, operator and each result. Promote only after the interactive checks pass. No ISO certification or DGU registration is claimed.
