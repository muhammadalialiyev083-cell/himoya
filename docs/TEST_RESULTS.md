# Executed test results — 1.0.0 MVP

Date: **2026-10-22**. Host: Linux x86_64. Python 3.12.14. PySide6 6.9.3. Qt platform: `offscreen`. All packages are installed in this project's `.venv`.

## Final automated suite

Command, from the project root:

```bash
QT_QPA_PLATFORM=offscreen XDG_CACHE_HOME="$PWD/.cache" \
  .venv/bin/python -m pytest -q --junitxml=release/test-results.xml
```

**78 passed; 0 failed; 0 errors; 0 skipped.** The final run took approximately 4 seconds. The machine-readable runner evidence is `release/test-results.xml`; each parametrized case actually executed. Test databases and temporary exports are kept under the project's `.test-data` directory.

| Area | Executed cases | Outcome |
| --- | ---: | --- |
| BIA weights, threshold edges, invalid impacts/targets, risk boundaries, disruption equality/violation/unknown rules | 51 | Passed |
| Initialization, parameterized CRUD, foreign keys, uniqueness, atomic rollback, ranking tie-breaks, persistence, backup/restore, corrupted/future databases, authentication, link consistency and readiness | 17 | Passed |
| Three real PDF report types, extracted Uzbek glyphs and values, CSV Unicode/formula protection, escaped HTML and empty reports | 7 | Passed |
| Full Qt form workflow and delete confirmation/cascade effects | 2 | Passed |
| Isolated application smoke with Python network connections denied; refusal to overwrite prior evidence | 1 | Passed |

## Real desktop workflow exercised

The UI test shows the Qt main window and uses actual modal forms to create the administrator, organization, department, process, BIA, risk, strategy, plan/ordered steps and scenario. It evaluates the scenario through the UI, checks BIA 80.00, risk-matrix counts, dashboard values, navigation to all nine pages, search and severity filters. It exports a PDF through the real background worker, closes the window/database, authenticates again, opens a fresh window/connection and verifies persisted records and recovery procedures.

Qt is offscreen here. These are actual Qt widgets and window lifecycle checks, not HTML mockups, but they do not establish interactive mouse/display quality on Windows.

## Source entry point and executable checks

The CLI smoke mode creates a fresh test-only database, a random administrator password, a visible-to-Qt main window, marked example records, all three PDF reports plus CSV, a screenshot and a SQLite backup. It closes/reopens both window and database, checks authentication and records, restores the backup, and writes `result.json`. No secret values are written into that result.

The native Linux one-file PyInstaller executable is tested by `scripts/verify_package.py`, which launches the built binary without relying on `PYTHONPATH` or `PYTHONHOME`. Its fresh output reports are parsed independently with pypdf/csv, checking Uzbek text, computed values and files. See `release/linux-package-verification.json` for the actual binary size/hash and result directory. Linux packaging is not Windows release evidence.

The offline smoke test denies Python socket connections during the full workflow. There are no network APIs, online assets or remote services in the application. A physical disconnected Windows-machine test remains unrun.

## Setup repeatability and isolation

`scripts/cloud_install.sh` was executed successfully: the local pinned dependency installation is repeatable and the suite passed. Complete `install_script` and `start_skill` instructions were saved in the cloud configuration draft for review; saving did not publish or apply a new environment version. Existing `himoya` files were not edited, and its Git status remained clean/unborn as before. No global package installation or remote publication was performed.

## Outstanding release checks

| Check | Result |
| --- | --- |
| Windows-target packaging invocation on this Linux host | Blocked with exit 2; native Windows Python is required |
| Actual Windows PE/EXE build | Unrun; no Windows host attached |
| Windows EXE size/hash | Unavailable; no EXE exists here |
| Native Windows GUI, no-console startup and scaling | Unrun |
| Packaged Windows persistence/PDF/CSV/offline checks | Unrun; automated pipeline and manual procedure supplied |
| Clean Windows machine without Python | Unrun |
| DGU registration / ISO certification | Not claimed |

The MVP implementation is testable here, but Windows distribution acceptance is **not complete**. Run `build.ps1` on Windows and follow `docs/WINDOWS_RELEASE.md` to close those release gates. Earlier development failures were fixed before the final 78-case run; the final XML records the final outcome.
