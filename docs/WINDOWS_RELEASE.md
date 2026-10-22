# Windows build and release verification

## Current verified status

The real Windows x64 one-file EXE was compiled on GitHub Actions and published as an MVP prerelease. **79 Windows tests passed, with no failures or skips**. Its packaged Qt offscreen launch, authentication, SQLite, backup/restore, PDF/CSV and close/reopen checks passed. Native interactive Windows and clean-machine sign-off remain outstanding.

- [Download UzluksizBCMS.exe](https://github.com/muhammadalialiyev083-cell/himoya/releases/download/windows-mvp-6/UzluksizBCMS.exe)
- [Release and runner evidence](https://github.com/muhammadalialiyev083-cell/himoya/releases/tag/windows-mvp-6)
- Size: **50,674,955 bytes**.
- SHA-256: `82c8946f8d265aff070070e8d9f65bca5ee456bb63c924c3f4708432bb24d6ef`.

The Linux host independently downloaded the actual released EXE with HTTP 200, matched its size/hash, verified x64 GUI PE headers and inspected the bundled Python runtime, qwindows plugin, schema and Noto font. Execution evidence comes from the native Windows runner; this Linux host cannot execute Windows software.

The initial Windows-only pefile conflict and missing offscreen PDF font were fixed without weakening assertions or disabling verification. The native runner became available after the owner authorized publishing this project to GitHub.

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
