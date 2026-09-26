# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 0 | Initial GitHub repository contained no files. | No existing plan/log/code could be reused. | Bootstrapped repository governance on main. |
| 2026-09-26 | 0 | A single payoff line cannot safely represent two expiries. | Could create a false impression of a flat, low-risk payoff. | Strategy design explicitly tracks near-expiry and next-expiry settlement separately. |
| 2026-09-26 | 0 | The user's 2.5% threshold has no specified denominator. | A percentage trigger is otherwise non-reproducible. | Keep denominator configurable and report multiple economically meaningful denominators in later phases. |

## Logging rule

Add a row whenever a reproducible mistake, failed assumption, data-quality issue or workflow failure affects the research. Do not delete historical rows; append corrections with dates.

| 2026-09-26 | 5 | Phase 5 could be incorrectly interpreted as empirical evidence before the Phase 3/4 ledger exists. | Would create unsupported regime conclusions. | Branch explicitly requires a validated ledger before execution and labels current work as protocol/scaffold only. |
