# UzluksizBCMS Desktop 1.0.0 MVP

## Windows EXE — GitHub orqali yuklab olish

Eng qulay yo‘l: [GitHub Releases](https://github.com/muhammadalialiyev083-cell/himoya/releases) sahifasida muvaffaqiyatli yig‘ilgan Windows MVP relizini ochib, **Assets → UzluksizBCMS.exe**ni yuklab oling. Reliz faqat avtomatik sinovlar va paket tekshiruvlari o‘tgandan keyin chiqariladi. Agar reliz hali ko‘rinmasa, quyidagi Actions sahifasida yig‘ish holatini tekshiring.

1. [Actions / Build Windows EXE](https://github.com/muhammadalialiyev083-cell/himoya/actions/workflows/windows-build.yml) sahifasini oching va GitHub hisobingizga kiring.
2. Eng yangi yig‘ish muvaffaqiyatli tugaganini (yashil belgi) tekshiring. Xato yoki navbat holatida EXE hali tayyor emas.
3. Yig‘ish sahifasining **Artifacts** bo‘limidan **UzluksizBCMS-Windows-x64** faylini yuklab oling.
4. ZIPni oching; `dist/UzluksizBCMS.exe` — Windows dasturi. Foydalanuvchiga Python o‘rnatish kerak emas.

Faqat manba kodi kerak bo‘lsa: [Download ZIP](https://github.com/muhammadalialiyev083-cell/himoya/archive/refs/heads/main.zip). Bu ZIP tayyor Windows EXE emas. Yig‘ish avtomatik `main`ga push qilinganda yoki Actionsdagi `Run workflow` orqali ishlaydi. Artefaktni yuklash uchun GitHubga kirish talab qilinishi mumkin.

Offline-first, native PySide6/Qt Widgets business continuity research application. The interface is Uzbek Latin. All business records are stored in a local SQLite database; there is no server, browser frontend, online database, telemetry or API key.

**Delivery status:** implemented and tested on Linux with Qt's offscreen platform. Windows compilation is performed separately by the GitHub Actions Windows runner. Check the latest run and its actual artifacts for its outcome; the initial Linux test documents do not establish Windows success. Native interactive Windows sign-off remains separate. Do not rename the Linux executable to `.exe`.

## Start from source

Requires Python 3.12 x64 on the development machine. Use this separate project directory; do not copy files into existing projects or change global packages.

Windows PowerShell:

```powershell
Set-Location "$HOME\Documents\UzluksizBCMS-Desktop"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --cache-dir .cache\pip -r requirements-dev.txt
.\.venv\Scripts\python.exe app\main.py
```

Linux development:

```bash
cd /workspace/UzluksizBCMS-Desktop
python3 -m venv .venv
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements-dev.txt
.venv/bin/python app/main.py
```

A graphical session is needed for interactive use. For headless checks use `QT_QPA_PLATFORM=offscreen`; that does not provide an interactive desktop. No X server or browser preview is required for automated tests.

On first launch create your own administrator account and password (10+ characters). No default password is supplied. Reopening requires authentication. Backups contain the account hash as well as business data. SQLite is **not encrypted**.

## Functionality

- Organization profile and department CRUD; process registry with search, status and BIA severity filtering, detail view, and linked risks/plans.
- Weighted BIA with independent RTO/RPO/MTPD inputs and validation; deterministic priority order.
- Risk register, severity filtering, a live color-coded 5×5 matrix, and dashboard counts.
- Recovery strategies; plans linked to the same process, optional risk and strategy references, editable/reorderable numbered steps, completion and readiness rules.
- Multi-process tabletop scenarios with selected plans, explicit RTO/MTPD comparisons, saved timestamped result snapshots and reopening.
- Dashboard charts and counts read from SQLite; full assessment PDF, risk/priority PDF and UTF-8 CSV, individual plan PDF. Exports run in a background worker.
- Salted PBKDF2 administrator authentication, password change, online SQLite backup, validated restore with automatic pre-restore safety backup, first-run database initialization and schema version guard.
- Optional clearly marked `NAMUNA` records that preserve an existing organization profile.

## Data location

Windows: `%LOCALAPPDATA%\UzluksizBCMS\uzluksiz.sqlite3`.

Linux: `${XDG_DATA_HOME:-~/.local/share}/UzluksizBCMS/uzluksiz.sqlite3`.

For isolated development only, set process variable `UZLUKSIZ_DATA_DIR` to a private writable folder. Tests use temporary databases. The frozen executable never writes user records into its temporary extraction directory. A Qt lock prevents two normal application instances from using the same data directory simultaneously.

## Tests and self-test

```bash
QT_QPA_PLATFORM=offscreen XDG_CACHE_HOME="$PWD/.cache" .venv/bin/python -m pytest -q
QT_QPA_PLATFORM=offscreen .venv/bin/python app/main.py --self-test-dir release/my-new-smoke
```

The smoke output directory must be empty. It creates its own random test-only administrator password, example database, reports, screenshot and `result.json`; it never changes normal user data. Test-only passwords are not recorded in output files. See [test results](docs/TEST_RESULTS.md) for actual outcomes and limits.

## Windows one-file build

On a Windows 10/11 x64 build machine with Python 3.12 x64:

```powershell
.\build.ps1
```

This installs project-local dependencies, runs tests, renders the application icon, builds a real windowed one-file PyInstaller executable, launches that executable in an isolated smoke test, validates its database persistence and PDF/CSV exports, and reports SHA-256 and file size. End users only need the resulting `dist\UzluksizBCMS.exe`; they do not need Python or the development venv. Read [Windows release verification](docs/WINDOWS_RELEASE.md) before sign-off.

The GitHub Actions workflow in `.github/workflows/windows-build.yml` builds on Windows after a push to `main` and supports manual dispatch. The owner explicitly authorized uploading this standalone project into the initially empty `himoya` repository after the in-chat artifact download failed. No pre-existing application code was replaced.

## Documentation

- [Uzbek user manual](USER_MANUAL.md)
- [Architecture and database](docs/ARCHITECTURE.md)
- [Algorithms and research limits](docs/ALGORITHMS.md)
- [Software description for registration preparation](docs/SOFTWARE_DESCRIPTION.md)
- [Windows build and offline verification](docs/WINDOWS_RELEASE.md)
- [Test results](docs/TEST_RESULTS.md)
- [Known limitations](docs/KNOWN_LIMITATIONS.md)
- [Source inventory](docs/SOURCE_INVENTORY.md)

ISO 22301 principles inform the workflow only. No ISO certification, full standard compliance, measured recovery-time accuracy, DGU registration, or database encryption is claimed.
