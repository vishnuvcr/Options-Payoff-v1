# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 0 | Initial GitHub repository contained no files. | No existing plan/log/code could be reused. | Bootstrapped repository governance on main. |
| 2026-09-26 | 0 | A single payoff line cannot safely represent two expiries. | Could create a false impression of a flat, low-risk payoff. | Strategy design explicitly tracks near-expiry and next-expiry settlement separately. |
| 2026-09-26 | 0 | The user's 2.5% threshold has no specified denominator. | A percentage trigger is otherwise non-reproducible. | Keep denominator configurable and report multiple economically meaningful denominators in later phases. |
| 2026-09-26 | 0 | First repository-write script failed because embedded backticks broke the tool-call JavaScript string. | No repository data were committed by the failed call. | Rewrote the file payloads without the conflicting delimiters and completed the bootstrap successfully. |
| 2026-09-26 | 1 | The first local test harness was a shortened copy rather than the exact repository test file. | It did not execute every final repository assertion. | Re-verified the formulas and repository test design; future phases will execute the exact checked-out repository files in CI. |

## Logging rule

Add a row whenever a reproducible mistake, failed assumption, data-quality issue or workflow failure affects the research. Do not delete historical rows; append corrections with dates.
