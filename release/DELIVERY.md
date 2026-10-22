# Delivery status — UzluksizBCMS Desktop 1.0.0

Workspace: `/workspace/UzluksizBCMS-Desktop`, independent of `/workspace/himoya`.

The native Qt application implements all seven functional modules with SQLite, administrator authentication, backup/restore, optional marked demo data, Uzbek interface, charts, PDF/CSV exports and supporting documentation. **78 automated tests passed**. See `docs/TEST_RESULTS.md` and `release/test-results.xml`.

Windows user database: `%LOCALAPPDATA%\UzluksizBCMS\uzluksiz.sqlite3` (created at first normal launch). No normal business database or default password is preinstalled. Example/smoke databases are isolated test artifacts.

`dist/UzluksizBCMS` is a verified **Linux** one-file executable. Its current size/hash and fresh launch/export/persistence results are in `release/linux-package-verification.json`. It is not usable as a Windows EXE.

**Requested Windows artifact: not built.** `dist/UzluksizBCMS.exe` does not exist because the host is Linux and PyInstaller requires native Windows Python. Windows EXE size and Windows launch verification are unavailable. `release/windows-build-status.json` records the blocked Windows-target attempt. No Windows, Wine or remote Windows builder was available.

On Windows 10/11 x64, extract `UzluksizBCMS-Desktop-1.0.0-source.zip` into a new empty folder, then run `build.ps1` using Python 3.12 x64. It builds the actual windowed one-file EXE, runs automated tests and executable smoke verification, and records its size/hash. Finish the native offline desktop checks in `docs/WINDOWS_RELEASE.md` before distributing it as verified.

Deferred scope includes multiple accounts/roles, encrypted database, cloud sync, automatic scheduling, resource-capacity simulation, MSI installation, signing and automatic updates. See `docs/KNOWN_LIMITATIONS.md`. No DGU registration or ISO certification is claimed.

Cloud `install_script` and `start_skill` were saved as a draft. To retain this prepared cloud setup, review and save those changes in environment settings, then publish the environment. Draft persistence is confirmed; publication/new-task restoration has not been performed or verified.
