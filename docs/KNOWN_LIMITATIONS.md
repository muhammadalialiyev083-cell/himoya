# Known limitations and deferred scope

- Windows compilation and native interactive verification require Windows and remain outstanding in this Linux workspace. No Windows executable, size or Windows launch success is claimed.
- Interactive physical-display QA is unrun here; Qt offscreen widgets, form actions, screenshots and PDF rendering are tested. Font rendering and display scaling on actual Windows need release sign-off.
- Single local administrator and one organization; no role management, multi-user server, cloud sync or concurrent shared-database editing. The normal app locks its data directory.
- The password gates the UI; SQLite and backups are unencrypted. OS users who can read/modify the database have access to the data. There is no password-recovery backdoor.
- Schema v1 safely initializes and rejects unknown/newer versions; there is no historical migration to test in this first version. A future schema change requires a backed-up transactional migration.
- Scenario results are deterministic estimates of user-entered duration. They do not simulate malware, real infrastructure, resource capacity or probabilistic recovery; no measured accuracy is claimed. Resource lists do not automatically reduce disruption times.
- Historical scenario results are snapshots. BIA or plan edits require reevaluation; changing a scenario invalidates its saved results. No audit-history editor or immutable regulatory audit trail is included.
- Readiness is a checklist measure, not assurance of real-world recovery. RPO is recorded separately but no data-loss-volume simulator exists.
- The dashboard counts all registered risks regardless of status. Closed risks remain in the register and its metrics. Large-data performance and enterprise-scale stress tests are outside MVP. Charts display the top eight scored processes; the ranking table and reports include all.
- PDF generation is threaded; database writes, authentication and backup are synchronous local operations. Very large databases/password checks may briefly occupy the UI. No long-running network tasks exist.
- Executable signing, an MSI installer, automatic updates, enterprise policy deployment, automatic scheduled backups, attachments, notifications and advanced exercise scheduling are deferred.
- DGU application submission, legal authorship details, ISO certification and full ISO compliance verification are outside this delivery. This package provides technical supporting documentation only.
