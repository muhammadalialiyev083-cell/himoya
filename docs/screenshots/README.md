# Native Qt screenshot evidence

Before/after captures have been generated and inspected locally using only isolated NAMUNA records and blank login fields. Public image publication is pending explicit approval after automatic approval review rejected the upload. No production database was used.

The review generator is `scripts/capture_ui.py`. It captures 35 views per scale (100%, 125%, 150%), including both themes, login, empty states, compact navigation and internal modules. Windows CI runs the same geometry checks and uploads visual-review.json metadata. PNG publication is disabled while approval is pending.

Before captures come from target commit 7671d06. These offscreen captures do not establish interactive Windows sign-off.
