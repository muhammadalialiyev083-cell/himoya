# MASTER DEVELOPMENT PROMPT — UZLUKSIZ BCMS DESKTOP

## 1. YOUR ROLE AND MAIN OBJECTIVE

Act as a Senior Desktop Software Engineer, Python Architect, UI/UX Designer, Database Engineer, QA Automation Engineer and Windows Release Engineer.

Your mission is to independently design, implement, test, package and deliver a **real, functional, offline-first Windows desktop application** named:

**UzluksizBCMS Desktop — Business Continuity Management System**

Version: **1.0.0 MVP**

The software supports my scientific research topic:

"Tashkilotlarda biznes uzluksizligini boshqarish tizimini loyihalash dasturini ishlab chiqish."

This is a standalone software product intended for demonstration, research and eventual EHM software registration (DGU) in Uzbekistan.

**CRITICAL: I need actual working application files and a compiled Windows .exe, NOT only code samples, UI mockups, HTML files, screenshots or implementation recommendations.**

Work autonomously until all MVP acceptance criteria are satisfied.

---

## 2. ABSOLUTE PROJECT ISOLATION

I have existing software projects. They must remain completely untouched.

Mandatory requirements:

- Create a completely NEW project from scratch.
- Use a separate directory named `UzluksizBCMS-Desktop`.
- Prefer an empty directory inside my Windows Documents folder.
- Do not access, edit, delete, overwrite, refactor, migrate or otherwise modify existing projects.
- Do not reuse or copy any existing repository code.
- Do not modify existing Git repositories.
- Do not modify any existing backend, frontend, API, database or deployment configuration.
- Do not change global Python packages or system environment variables.
- Use a project-local Python virtual environment.
- All build artifacts must remain inside the new project.
- If the proposed folder contains existing files, choose a new, unused folder rather than overwriting anything.
- Never perform destructive operations outside this new workspace.

The new application must have its own source code, database schema, design system, business logic, tests and release process.

## 3. REQUIRED TECHNOLOGY STACK

Build a real native-style desktop application.

Primary stack:

- Programming language: Python 3.12, 64-bit
- Desktop GUI: PySide6 / Qt Widgets
- Local database: SQLite
- Data access: Python sqlite3 with parameterized queries and a repository layer
- UI styling: Qt Style Sheets (QSS)
- Reports: Qt printing/PDF facilities
- CSV exports: Python standard library
- Testing: pytest
- Packaging: PyInstaller
- Operating system: Windows 10/11 x64
- Architecture: Modular desktop application

Do not use Django, Flask, React, browser-based frontends, Electron, remote servers or online databases.

The end user must NOT need to install Python, SQLite or development tools.

The finished EXE must run independently and must not require an internet connection.

Keep dependencies minimal and pin tested versions.

## 4. SOFTWARE ARCHITECTURE

Use a clean and maintainable layered architecture:

1. Presentation Layer — PySide6 windows, dialogs and widgets.
2. Application Layer — use cases and coordination.
3. Domain Layer — business continuity rules and calculations.
4. Persistence Layer — SQLite repositories.
5. Reporting Layer — PDF and CSV generation.
6. Infrastructure Layer — configuration, database initialization, backup and logging.

Separate business logic from UI code.

Do not put all functionality into one large Python file.

Suggested structure:

```text
UzluksizBCMS-Desktop/
│
├── app/
│   ├── main.py
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── algorithms/
│   ├── ui/
│   ├── reports/
│   └── resources/
│
├── tests/
├── docs/
├── scripts/
├── assets/
├── requirements.txt
├── build.ps1
├── README.md
├── USER_MANUAL.md
└── release/
```

Adapt this structure when necessary, while maintaining clean separation.

## 5. REQUIRED MVP FUNCTIONALITY

Implement the following seven interconnected functional modules.

Every feature must operate on real SQLite data.

No nonfunctional buttons, empty placeholder screens, fake calculations or simulated database operations are permitted.

### MODULE 1 — ORGANIZATION MANAGEMENT

Create a practical organization management interface.

Allow the user to:

- Create an organization profile.
- Specify organization name, industry, description and responsible person.
- Add, edit and delete departments.
- Assign business processes to departments.
- Save information persistently.
- View organization statistics.

For MVP, support one active organization with multiple departments.

Use working CRUD operations and input validation.

### MODULE 2 — BUSINESS PROCESS MANAGEMENT

Create a full business process registry.

Each process must contain:

- Unique process identifier.
- Process name.
- Description.
- Department.
- Responsible person.
- Critical resources.
- IT dependency description.
- Operational status.

Implement:

- Create process.
- Edit process.
- Delete process with confirmation.
- Search and filter.
- View process details.
- Assign criticality based on its BIA result.
- Maintain references to relevant risks and continuity plans.

Prevent invalid references and orphaned records.

### MODULE 3 — BUSINESS IMPACT ANALYSIS (BIA)

This is one of the most important modules.

Implement a working analytical engine.

Each business process must be assessed using:

- Financial impact: 0–5
- Operational impact: 0–5
- Reputational impact: 0–5
- Legal/compliance impact: 0–5
- Maximum Tolerable Period of Disruption (MTPD), in hours
- Recovery Time Objective (RTO), in hours
- Recovery Point Objective (RPO), in hours

Create an explicit, deterministic weighted impact algorithm.

Default formula:

BIA_SCORE = 20 × (
0.30 × Financial
+ 0.35 × Operational
+ 0.20 × Reputational
+ 0.15 × Compliance
)

Results range from 0 to 100.

Classify:

- 75–100: Critical
- 50–74.99: High
- 25–49.99: Medium
- 0–24.99: Low

Allow users to view the score, individual input values, calculation explanation and priority classification.

For processes with equal scores, use shorter RTO as the secondary ordering criterion.

Validation:

- MTPD must be greater than zero.
- RTO must be greater than zero.
- RTO cannot exceed MTPD.
- RPO cannot be negative.
- All impact values must remain within their defined ranges.

Do not automatically treat RPO as identical to RTO.

These are application-defined research scoring parameters, not official ISO formulas. Label them accordingly.

Implement a real priority ranking table and visualization.

### MODULE 4 — RISK ASSESSMENT

Build a practical risk register.

For each risk:

- Risk title.
- Related business process.
- Threat description.
- Vulnerability description.
- Likelihood: 1–5.
- Impact: 1–5.
- Existing mitigation.
- Risk owner.
- Recommended action.
- Risk status.

Calculate:

RISK_SCORE = LIKELIHOOD × IMPACT

Classify:

- 1–5: Low
- 6–10: Medium
- 11–15: High
- 16–25: Critical

Create:

- Risk scoring engine.
- Color-coded 5×5 risk matrix.
- Risk register.
- Process-to-risk relationships.
- Risk detail and editing screen.
- Filtering by severity.
- Dashboard risk metrics.

The matrix must update when risk information changes.

### MODULE 5 — RECOVERY STRATEGY AND CONTINUITY PLANNING

Develop an actual Business Continuity Plan management module.

The user must be able to:

- Create recovery strategies.
- Link a strategy to a business process.
- Define recovery actions.
- Define required resources.
- Specify responsible personnel.
- Define recovery priorities.
- Create continuity plans.
- Add ordered recovery steps.
- Edit, save and delete plans.
- View plan readiness and completion information.

Each continuity plan should contain:

- Plan identifier.
- Plan name.
- Business process.
- Risk association, when applicable.
- Responsible person.
- Recovery objectives.
- Numbered recovery procedures.
- Resources.
- Review date.
- Status.

Support printing/exporting a continuity plan to PDF.

PDF reports must display Uzbek Latin text and special characters correctly.

### MODULE 6 — DISRUPTION SCENARIO AND TABLETOP SIMULATION

Implement a simple but genuinely functional scenario analysis feature.

For MVP, this is a tabletop simulation, not a real cyberattack or infrastructure failure simulator.

Allow users to:

- Create a disruption scenario.
- Select affected business processes.
- Define expected disruption duration.
- Record available recovery resources.
- Select associated recovery plans.
- Define expected response actions.
- Compare expected disruption duration against process RTO and MTPD.
- Identify recovery target violations.
- Generate a scenario assessment.
- Save and reopen results.

Suggested scenarios:

- Data center outage.
- Ransomware incident.
- Power failure.
- Network service interruption.
- Critical employee unavailability.

Implement deterministic rule-based evaluation.

Clearly differentiate model estimates from measured real-world recovery times.

No fabricated ML predictions or claims of experimentally validated accuracy.

### MODULE 7 — DASHBOARD AND REPORTING

Create a professional dashboard that displays real metrics from SQLite.

Include:

- Total business processes.
- Total departments.
- Critical processes.
- High and critical risks.
- Completed BIA assessments.
- Continuity plans.
- Scenario assessments.
- Business process priority chart.
- Risk severity distribution.

Create at least two fully operational reports:

1. Business Continuity Assessment Report (PDF).
2. Risk and Priority Register (PDF/CSV).

Support exporting current results to user-selected folders.

Reports should include:

- Organization name.
- Generated date.
- Summary.
- Calculated values.
- Priority/risk classification.
- Relevant recommendations based on explicit rules.
- Methodology and formula explanations.

Never display invented metrics as actual results.

## 6. DESKTOP UI/UX REQUIREMENTS

Create a distinctive and polished Windows desktop interface.

Design language:

- Modern Windows 11 aesthetic.
- Enterprise-grade dashboard.
- Clean typography.
- Consistent spacing.
- Light background.
- Deep navy sidebar.
- Teal or emerald accents.
- Subtle Uzbek national ornamental elements, used sparingly.
- Modern icons and cards.
- Rounded corners where appropriate.
- Accessible contrast.
- Clear data tables and analytical charts.

Primary interface language: **Uzbek (Latin alphabet)**.

Use clear professional terminology.

Main sidebar navigation:

1. Boshqaruv paneli
2. Tashkilot
3. Biznes jarayonlari
4. BIA tahlili
5. Risklarni baholash
6. Uzluksizlik rejalari
7. Simulyatsiya
8. Hisobotlar
9. Sozlamalar

Design for a minimum practical display resolution of 1366×768.

Make dialogs and tables usable with smaller laptop displays.

Use a real Qt application window, not a browser or localhost website.

Ensure the UI remains responsive while reports and calculations execute.

Include meaningful empty states, success messages, validation messages and error dialogs.

No decorative buttons without functionality.

## 7. LOCAL DATABASE AND DATA SAFETY

The application must be offline-first.

Use SQLite with enforced foreign keys, transactions and proper relational integrity.

Required entities include:

- Organization
- Department
- BusinessProcess
- BIAAssessment
- Risk
- RecoveryStrategy
- ContinuityPlan
- RecoveryStep
- Scenario
- ScenarioAffectedProcess
- ScenarioResult

Add schema versioning and a safe initialization mechanism.

Store user data in a writable per-user Windows application data directory, for example:

`%LOCALAPPDATA%\UzluksizBCMS\`

Do not store mutable data in the packaged EXE, temporary extraction directory or Program Files.

Required database capabilities:

- Automatic initial database creation.
- Persistent data after application restart.
- Safe schema upgrades.
- Database transaction handling.
- Referential integrity.
- Explicit delete confirmations.
- SQLite database backup.
- Restore from a validated backup.
- Clear error handling.
- Prevention of uncontrolled data loss.

Use realistic optional demo data.

Demo records must be clearly marked as examples and must never be presented as real research findings.

Include an option to initialize demo data without replacing existing information.

## 8. SECURITY REQUIREMENTS

For MVP, provide a single local administrator profile.

On first launch:

- Create an administrator account.
- Set an administrator password.
- Save a salted password hash.
- Never store a plaintext password.
- Require authentication when reopening the application.

Use a reliable password hashing mechanism available in the selected Python environment.

Do not create a hardcoded default administrator password.

Prevent SQL injection using parameterized statements.

Never use dangerous dynamic code execution for database operations.

Do not claim that the SQLite database is encrypted unless actual encryption is implemented and verified.

Keep application logs free of passwords and other secrets.

## 9. SCIENTIFIC AND ANALYTICAL QUALITY

The application must be suitable for demonstrating an academic software development result.

The following research-oriented capabilities must actually work:

- Business process criticality analysis.
- Deterministic BIA weighted scoring.
- Risk assessment matrix.
- Automated business process priority ranking.
- RTO and MTPD comparison.
- Rule-based disruption scenario analysis.
- Recovery plan traceability.
- Analytical reporting.

Provide clear technical documentation explaining all formulas.

ISO 22301 principles can inform the application structure, but do not claim ISO certification or full standard compliance.

Do not use invented scientific citations or unverified methodology claims.

Document where calculation weights and thresholds can be changed by future researchers.

## 10. AUTOMATED TESTING

Use pytest.

Write tests covering:

- Database initialization.
- CRUD operations.
- Foreign key integrity.
- BIA score calculations.
- BIA priority thresholds.
- Invalid RTO/MTPD values.
- Risk scoring.
- Risk category boundaries.
- Process priority ranking.
- Scenario evaluation.
- Database persistence.
- Backup and restore.
- Authentication.
- PDF and CSV report generation.

Include edge cases.

At minimum, execute a real end-to-end workflow:

1. Start application.
2. Create administrator.
3. Create organization.
4. Create department.
5. Register a business process.
6. Perform BIA.
7. Register a risk.
8. Create recovery strategy.
9. Create continuity plan.
10. Evaluate disruption scenario.
11. Generate PDF report.
12. Close application.
13. Restart application.
14. Verify that saved data remains available.

Use automated tests wherever feasible and verify the desktop interface interactively when the environment supports GUI interaction.

Fix discovered defects before release.

## 11. WINDOWS EXE GENERATION

**This section is mandatory.**

After implementation and verification, generate a real Windows executable.

Final application name:

`UzluksizBCMS.exe`

Target operating system:

Windows 10/11 x64.

Use PyInstaller as the primary packaging tool.

Requirements:

- Include the necessary Python runtime and application dependencies.
- Include Qt platform plugins and application assets.
- No terminal window should appear when opening the final EXE.
- No browser should open.
- No Python installation should be required on the end-user computer.
- Keep application data outside the executable.
- Provide a professional application icon.
- Verify that the GUI opens correctly.
- Verify that SQLite read/write operations work after packaging.
- Verify that PDF and CSV exports work in the packaged application.
- Verify that the executable works without an internet connection.

Prefer one-file packaging.

Initial example:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "UzluksizBCMS" app/main.py
```

Adapt this command to include required assets, module paths, icons and hidden imports.

Provide a reproducible PowerShell build script:

`build.ps1`

The final build must appear at:

`dist\UzluksizBCMS.exe`

If one-file packaging has compatibility problems, investigate and fix them. A working one-folder release may be used temporarily for diagnosis, but do not misrepresent it as a completed single-file EXE.

Do not treat a successful packaging command as proof that the application works.

Launch and verify the packaged executable.

If the current environment does not support Windows binary compilation, prepare the complete Windows build pipeline and clearly state that Windows compilation has not yet been performed. Never claim an EXE exists unless it has actually been built.

## 12. DGU-ORIENTED DOCUMENTATION

Prepare supporting documentation in the `docs` directory.

Include:

- Software description.
- Purpose and target users.
- Functional modules.
- System architecture.
- Database structure.
- Algorithms and formulas.
- User operating instructions.
- Windows installation and launch instructions.
- Development stack.
- Software version.
- Test results.
- Known limitations.
- Source code file inventory.
- Screenshot instructions or actual screenshots if supported.

Prepare documents that can later support EHM software registration.

Do not claim that DGU registration has been obtained.

## 13. DEVELOPMENT WORKFLOW

Do not stop after creating a plan.

Execute the following development phases.

### Phase 1 — Foundation

Create a new isolated workspace, virtual environment, dependency files, database initialization and desktop application skeleton.

Launch the application successfully.

### Phase 2 — Core functionality

Implement organization management, departments, business processes, BIA and risk assessment.

Ensure all CRUD operations work.

### Phase 3 — Continuity planning

Implement recovery strategies, recovery plans and scenario assessment.

Connect these modules to the core data model.

### Phase 4 — Analytics and design

Implement the dashboard, charts, PDF/CSV reports and professional Uzbek-language UI styling.

### Phase 5 — Quality assurance

Write and execute tests.

Fix failures, broken navigation, invalid calculations and data persistence problems.

### Phase 6 — Windows packaging

Run the real EXE build pipeline.

Verify the output file.

Test application launch and persistence.

### Phase 7 — Delivery

Provide a final release summary.

## 14. STRICT DEFINITION OF DONE

The MVP is complete only when:

- The application is implemented as a real PySide6 desktop program.
- All seven functional modules operate.
- Data is stored and retrieved correctly using SQLite.
- BIA calculations produce verifiable results.
- Risk assessment calculations work.
- Recovery plans can be saved and reopened.
- Scenario analysis produces rule-based results.
- Reports export successfully.
- The application runs offline.
- The administrator can sign in.
- Tests have been executed and results documented.
- Windows packaging has been attempted and verified.
- The final compiled EXE exists when the Windows build environment supports it.
- The original projects remain unchanged.

No TODO screens, fictitious functionality or placeholder business logic may be counted as completed features.

## 15. FINAL OUTPUT

At the end, report:

1. Project workspace location.
2. Implemented features.
3. Database location.
4. Automated test results.
5. Final EXE path.
6. EXE size.
7. Windows launch verification.
8. Known issues.
9. Features intentionally deferred beyond MVP.

**Required final deliverable:**

`UzluksizBCMS.exe`

Do not finish with only a Git repository, Python source files or an architectural explanation.

If blocked by a genuine environmental constraint, report the exact blocker, preserve all completed work and leave reproducible build instructions.

## FINAL EXECUTION DIRECTIVE

You are responsible for execution, implementation, testing and release preparation.

Make reasonable technical decisions independently.

Keep the MVP achievable and production-conscious rather than over-engineered.

Work directly in the isolated new project directory.

Preserve all existing projects without modification.

Begin creating the application now and continue through the build and verification stages.

**SUCCESS = A REAL, TESTED, OFFLINE WINDOWS BUSINESS CONTINUITY MANAGEMENT APPLICATION WITH A WORKING EXE DISTRIBUTION.**