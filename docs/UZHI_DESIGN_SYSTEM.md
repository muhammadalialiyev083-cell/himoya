# UzHi Design System — native desktop mapping

The implementation stays in Python 3.12 / PySide6 Qt Widgets. It uses the existing SQLite schema, PBKDF2 service, BCMS service and report exporter. No browser, server, network asset or schema migration is introduced.

## Reference audit

Read-only reference: `muhammadalialiyev083-cell/adolat`, `main`, retrieved 2026-10-28. Reviewed App.tsx, index.css, Dashboard.tsx, NavigationHub.tsx, UzHiLogo.tsx, favicon.svg and the public fonts directory. The live Netlify URL could not be retrieved in this environment; the source repository supplied the visual reference.

The CSS contains an older orange-red theme followed by the newer `.spark-*` / `.automark-*` navy-teal redesign. The newer rules and original UzHi identity match the requested design direction: sidebar `#0e2339`, hero gradient `#09223d → #0f3554 → #07535c`, turquoise `#00d2d3`, CTA `#34d2b6`, 12–16 px radii, 10–24 px spacing, restrained outlines and 140–320 ms transitions. The source uses a 256 px sidebar, 78 px compact mode, 60 px header, grouped links, module search, breadcrumbs, feature shortcuts and real metrics. Desktop navigation uses 284 / 76 logical pixels to accommodate Uzbek labels and Qt tree indentation.

| Reference component | Native implementation | Behavior/data source |
| --- | --- | --- |
| UzHiLogo.tsx | `UzHiLogo`, `uzhi-mark.svg`, QtSvg renderer | Exact original shield/infinity paths; finite expanding wordmark on hover/click; keyboard focus; navy app icon |
| App.tsx grouped spark sidebar | `NavigationSidebar`, `QTreeWidget` | Six icon groups, animated expansion, search, keyboard activation, compact tooltips, active group/destination |
| NavigationHub.tsx | Native catalog + setup checklist | Buttons open existing screens; checklist uses actual database record counts |
| App.tsx breadcrumbs/back | `PageHeader`, `NavigationHistory` | Back/Forward move a cursor without adding entries; new navigation truncates forward history |
| Dashboard.tsx automark hero | `GradientPanel` + real shortcuts | Organization, BIA, risk and continuity plan workflows |
| Dashboard.tsx metric cards | `MetricCard` | Eight `BCMS.metrics()` values; critical/high-risk/evaluated cards filter actual records |
| Web analytics | `Bars`, `RiskMatrix`, recovery summary | Existing rankings, risk scores and plan readiness; no invented readiness percentage |
| Web cards/forms/tables | `SectionCard`, `EmptyState`, `FormDialog`, `Registry` | Fusion palette, shared QSS, alternating rows, scrollable forms, inline required-field validation, selection actions |
| Web toast/loading | `ToastNotification`, indeterminate export progress | Overlay notifications, existing report QThread; progress shown only for real exports |
| Theme/reduced motion | Semantic `Tokens`, `QPalette`, QSettings | Complete light/dark surfaces; Windows client-area animation preference + user override + `UZHI_REDUCED_MOTION=1` |
| Web toolbar/navigation | Native `QMenuBar` / `QAction` | Working CRUD, export, backup, restore, password, themes, refresh and bundled manual |

The reference font directory contains only a WOFF2 web font and its license. The desktop uses its existing bundled SIL OFL Noto Sans TTF, with tested support for `Oʻ oʻ Gʻ gʻ` and curly apostrophes. No WOFF2 file is passed to Qt. The original font license remains bundled.

## Supported destination mapping

Organization profile and departments share the existing organization screen. Risk register and matrix share the risk screen. Strategies and plans select the correct existing tab. “Reja bosqichlari” opens the plans tab and explains that steps are edited inside a plan. Statistics opens the real dashboard, export opens real PDF/CSV options. System commands invoke existing protected actions. Setup/catalog contain genuine navigation; they introduce no scientific modules.

## Invariants

`app/algorithms/scoring.py`, database schema, data directory and authentication service remain unchanged. Financial/operational/reputational/compliance weights stay 0.30/0.35/0.20/0.15. Existing score thresholds, RTO ≤ MTPD, scenario snapshots, readiness rules, exports and restore safety copies are preserved. Destructive database operations still require confirmation. UI preferences live beside the database in `ui.ini`; business records stay in the original `uzluksiz.sqlite3`.

## Review evidence

Before/after images in [screenshots](screenshots/) use isolated NAMUNA records, never a user's database. Windows CI also captures 35 views per scale at Qt scale factors 1, 1.25 and 1.5, including 1366×768 and 1920×1080 logical window sizes, both themes, empty state, login, forms, compact navigation and every internal module. Geometry assertions catch clipped KPI values and horizontal dashboard/matrix overflow. Offscreen scale factors are automated rendering checks; they do not establish native Windows monitor/DPI behavior.
