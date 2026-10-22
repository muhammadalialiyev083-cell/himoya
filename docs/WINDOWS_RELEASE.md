# Windows build and release verification

## Current status

The implementation environment is Linux x86_64 with Python 3.12.14. No Windows VM, Windows Python runtime, Windows desktop or Wine is attached. A Windows-target build invocation was made through `scripts/build.py --target windows`; it exited 2 with the documented native-target requirement. PyInstaller cannot cross-compile a Windows PE executable from a Linux Python installation. See `release/windows-build-status.json`.

**No Windows EXE has been compiled here. Windows size, launch, persistence and offline acceptance remain unverified.** A Linux one-file binary, when present, is packaging evidence for Linux only.

## Build on Windows 10/11 x64

1. Copy/extract the project into a new, empty directory such as `%USERPROFILE%\Documents\UzluksizBCMS-Desktop`. Preserve existing projects. Do not copy the Linux `.venv`, `build/` or `dist/` directories.
2. Install Python 3.12 x64 on the build machine if absent. End users will not need Python.
3. From PowerShell in the new directory run `./build.ps1`. If local execution policy prevents a script, use a permitted process-scoped policy for this reviewed script according to your organization; do not change machine-wide policy.
4. The script creates `.venv`, installs pinned direct dependencies plus Windows-only PyInstaller support libraries, runs pytest, writes `release/windows-test-results.xml`, generates `assets/UzluksizBCMS.ico`, builds a one-file windowed PE and launches its isolated smoke test.
5. Expected output: `dist\UzluksizBCMS.exe`. The verifier records actual size and SHA-256 in `release/win32-package-verification.json`, plus fresh reports, screenshot, SQLite and restart evidence in `release/packaged-smoke-<timestamp>/`.

Only the EXE is needed for end users. Qt plugins, Python runtime, schema and icon are bundled. The application is unsigned; an organization may separately sign a verified release with its own certificate. No signing certificate or account is embedded.

## Native interactive sign-off (required)

The automated executable test runs a real Qt window using the offscreen platform, creates its own random test-only administrator, checks data, PDF/CSV, backup/restore and reopen. It does **not** replace these real desktop checks:

1. On Windows 10/11 x64, remove any process-only `QT_QPA_PLATFORM=offscreen` override, disconnect network access and double-click `dist\UzluksizBCMS.exe`.
2. Confirm the native window opens without a console or browser. Test at 1366×768 including Windows display scaling. Confirm the app icon, dialogs, keyboard focus, scrolling and Uzbek characters.
3. Create a non-default administrator account and log in. Create organization → department → process → BIA → risk → strategy → plan with ordered steps → scenario.
4. For F=4, O=5, R=3, C=3 confirm BIA 80/Kritik. For likelihood=4 and impact=4 confirm risk 16/Kritik. With RTO=4, MTPD=24 and disruption=8 confirm RTO violation but no MTPD violation.
5. Export assessment PDF, risk PDF/CSV and plan PDF to a chosen user folder. Open and print a PDF, confirm `O‘zbekiston`, `o‘`, `g‘` and table values, and inspect CSV. Check long multipage reports.
6. Close and reopen the EXE while offline, authenticate and verify every record. Verify data is under `%LOCALAPPDATA%\UzluksizBCMS`, not PyInstaller's `_MEI...` directory.
7. Make a backup, edit a record, restore the backup and authenticate using the backup account. Confirm both restoration and the pre-restore safety file. Confirm invalid backups leave data intact.
8. Repeat on a clean Windows machine without Python or development packages. Record OS version, EXE hash/size, checks, date and operator. Keep actual failures distinct from skipped checks.

Do not mark Windows release complete until these checks have been executed. The existing `.github/workflows/windows-build.yml` can build and automate checks on a Windows runner after the user puts this standalone project into its own repository. That workflow has not been triggered here and does not itself perform the human desktop sign-off.
