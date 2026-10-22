# Research algorithms and traceability

These are explicit application-defined research parameters, **not official ISO formulas** or claims of certified compliance.

## Weighted business impact

Inputs F, O, R and C are finite numbers from 0 to 5. The GUI accepts two decimal places.

`BIA = 20 × (0.30F + 0.35O + 0.20R + 0.15C)`

The result ranges from 0 to 100. Classification uses the calculation rounded to six decimal places; display rounds to two decimals. This avoids common binary floating-point noise at exact thresholds. Thresholds: `[75,100]` Critical/Kritik; `[50,75)` High/Yuqori; `[25,50)` Medium/O‘rta; `[0,25)` Low/Past. Example: F=4, O=5, R=3, C=3 → **80.00**, Kritik.

MTPD and RTO must be positive finite hours; RTO cannot exceed MTPD. RPO is a separate nonnegative finite hours value and is never derived from RTO. RPO is recorded/reported, not used in the BIA weighting or the disruption-duration comparison. Ranking sorts by descending BIA score, ascending RTO, then process code for reproducibility. Unassessed processes have no assumed criticality and do not appear in the scored ranking.

## Risk matrix

Likelihood and impact are integers from 1 to 5; score = their product. Classification: 1–5 Low, 6–10 Medium, 11–15 High, 16–25 Critical. The 5×5 matrix counts actual registered risks for each pair. It includes all statuses; a closed risk remains a historical register entry. The dashboard uses the same dataset. A color is a category, not an independently measured probability.

## Tabletop evaluation

For each selected process, compare expected duration D against its current BIA targets:

- If BIA is absent, both violation values are unknown and the recommendation is to assess BIA.
- `D > RTO` marks an RTO violation.
- `D > MTPD` marks an MTPD violation and recommends alternative operations.
- Equality is within the target. If only RTO is violated, recommend stronger recovery resources.
- A missing selected plan for the process adds a planning recommendation.

The scenario stores available resources and response actions as user inputs. The model does not pretend to calculate time savings from uncalibrated resources. D is a user estimate, not a measured recovery time. There is no ML prediction, probabilistic attack simulation or fabricated accuracy statistic. Each evaluation stores inputs, process limits, recommendations, selected plan identifiers/names and evaluation time. Editing a scenario clears prior results; changing a BIA/plan requires explicit reevaluation to obtain a new snapshot.

## Plan completion and readiness

Completion = completed recovery steps / total steps × 100, rounded to an integer; no steps means 0%. Readiness requires at least one step, all complete, nonempty responsible person/objectives/resources, approved status and review date on or after today's local date. This is a checklist indicator, not proof of operational resilience.

## Rule-driven reporting

Missing BIA triggers a coverage recommendation. High/critical risks trigger a mitigation review. Incomplete/unapproved/overdue plans trigger a readiness recommendation. Risk entries without a user-written recommendation receive a category-based action. Reports show formulas and distinguish NAMUNA examples from actual research evidence.

## Future research changes

Edit weights, thresholds and scenario rules in `app/algorithms/scoring.py`, and adjust boundary tests in `tests/test_algorithms.py`. Update formula text in `app/reports/export.py`, `app/ui/registry.py`, `app/ui/window.py` and this document together. These parameters are deliberately not end-user settings in MVP; changing them is a versioned research/code change. No scientific citations have been invented.
