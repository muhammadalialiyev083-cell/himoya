# UzluksizBCMS Desktop development
Use the existing isolated project at /workspace/UzluksizBCMS-Desktop. Each cloud task is already isolated; do not create a Git worktree unless explicitly requested. Preserve /workspace/himoya and all other projects. Install dependencies only into this project's .venv; never change global Python packages.

This cloud host is Linux and has no interactive desktop. No web service, browser preview, external credentials or database server is required. Retained dependencies are in .venv; no application process must survive publication.

From /workspace/UzluksizBCMS-Desktop:
- Validate: QT_QPA_PLATFORM=offscreen XDG_CACHE_HOME="$PWD/.cache" .venv/bin/python -m pytest -q
- Run a real Qt/SQLite/report/restart smoke check: choose a NEW empty output path under this project's release directory, then run QT_QPA_PLATFORM=offscreen XDG_CACHE_HOME="$PWD/.cache" .venv/bin/python app/main.py --self-test-dir release/<new-name>. Require exit 0 and a fresh result.json with status passed. A nonempty output directory is intentionally refused. Test credentials are random and test-only.
- For interactive use on a machine with a desktop: .venv/bin/python app/main.py. Normal user data is stored in the per-user application data directory; tests do not use it.
- Windows build: on Windows 10/11 x64 with Python 3.12 x64 run build.ps1. Target dist/UzluksizBCMS.exe. Linux PyInstaller outputs are Linux executables and cannot establish Windows readiness. Follow docs/WINDOWS_RELEASE.md for the remaining native interactive/offline verification.
- Frozen Linux verification, when dist/UzluksizBCMS is retained: .venv/bin/python scripts/verify_package.py dist/UzluksizBCMS.

No tracked files in the existing himoya repository were changed. Current source, tests, reports and documentation belong exclusively to the new standalone project. Do not present this environment as a verified Windows release.
