# Architecture and database

Version 1.0.0; Python 3.12 x64; PySide6 6.9.3; SQLite through the standard-library `sqlite3` driver. Presentation is native Qt Widgets styled with QSS. There is no web server or online runtime dependency.

## Layers

| Layer | Modules | Responsibility |
| --- | --- | --- |
| Presentation | `app/ui/` | Uzbek navigation, scrollable forms, registries, charts, risk matrix, confirmations and validation messages |
| Application | `app/services/bcms.py` | Validated use cases, relational consistency, plan transactions, scenario evaluation and dashboard queries |
| Domain | `app/algorithms/scoring.py` | Pure deterministic BIA, risk and disruption rules |
| Persistence | `app/repositories/records.py` | Allowlisted identifiers and parameterized CRUD |
| Infrastructure | `app/database/`, `app/core/`, `app/services/auth.py` | Versioned initialization, backup/restore, per-user storage, single-instance lock, password hashes and safe logs |
| Reporting | `app/reports/export.py` | Escaped report HTML rendered directly to PDF with Qt, UTF-8 CSV; immutable data snapshot passed to UI's background worker |

Qt HTML is used only as in-memory document markup for PDF rendering and rich-text detail dialogs. The application is not a browser frontend. `QTextDocument`/`QPdfWriter` provide Unicode font embedding. User data is HTML-escaped. CSV cells with spreadsheet formula prefixes are quoted with a leading apostrophe. Worker threads never use the UI thread's SQLite connection.

## Schema v1

The authoritative schema is `app/database/schema.sql`; `PRAGMA user_version=1` records its version. Every connection enables foreign keys. New databases initialize inside an explicit transaction. Unsupported newer databases and unknown unversioned schemas are rejected without an automatic destructive conversion. Future migrations must first make a SQLite backup and execute transactional version-to-version steps; there is no historical schema migration in this first release.

| Table | Relationship / notable constraints |
| --- | --- |
| `admin` | Singleton `id=1`; username, random salt, PBKDF2-SHA256 digest and iteration count |
| `organization` | Singleton `id=1`, required name |
| `department` | Organization FK restricted; name unique within organization |
| `business_process` | Department FK restricted; unique code |
| `bia_assessment` | One per process; cascade on process deletion; bounded impact values, positive MTPD/RTO, RTO≤MTPD, RPO≥0 |
| `risk` | Process FK restricted; integer likelihood/impact 1–5 |
| `recovery_strategy` | Process FK restricted; priority 1–5 |
| `continuity_plan` | Process FK restricted; unique code; risk and strategy set NULL when their records are deleted |
| `recovery_step` | Plan FK cascade; unique positive position per plan; Boolean completion |
| `scenario` | Nonnegative expected duration |
| `scenario_affected_process` | Many-to-many scenario/process; process deletion restricted |
| `scenario_plan` | Many-to-many scenario/plan; plan/scenario removal cascades join records |
| `scenario_result` | Scenario FK cascade; UTC timestamp and JSON snapshot |

Application use cases enforce that a plan's risk/strategy and a scenario's selected plans refer to the relevant process. Editing a linked risk/strategy cannot move it away from its plan's process. Editing a plan cannot move it away from the processes selected in a referring scenario. Process deletion cannot leave orphan risks, strategies, plans or scenario links. BIA alone cascades with a process, as stated in the delete confirmation.

Plan fields and all numbered recovery steps are replaced atomically in one savepoint. Scenario fields, process links, plan links and invalidation of prior scenario results are committed in one transaction. Evaluations append timestamped immutable snapshots; BIA/plan edits do not silently rewrite historical results. UI and documentation instruct the user to rerun an assessment after such changes.

## Backup and restore

Backups use SQLite's online backup API to a temporary file, run integrity/foreign-key/schema checks, then atomically replace the selected destination. Restore validates the source in read-only mode, checks exact v1 table definitions, columns and foreign keys, rejects triggers/views, writes a pre-restore safety backup, creates a checked candidate database through the backup API and atomically replaces the active file. Invalid candidates do not replace active data. The UI demands explicit confirmation and then authentication using the restored account.

## Security boundary

PBKDF2-HMAC-SHA256 uses 600,000 iterations and a 32-byte random salt; digest comparison is constant time. There is no hardcoded administrator or password. SQL values are bound parameters; dynamic table/column identifiers come from internal allowlists. Authentication protects the application session; SQLite and backup files are not encrypted and remain accessible to an OS user with file access. Apply OS ACLs and disk encryption separately. Logs record session events only, never passwords, digest values or business record contents. Crash errors shown to users avoid dumping exception details.

One normal application instance per data directory is enforced by Qt's `QLockFile`. Test-only CLI verification creates an isolated empty directory and does not open normal user data.
