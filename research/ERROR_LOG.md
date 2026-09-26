# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 0 | Initial GitHub repository contained no files. | No existing plan/log/code could be reused. | Bootstrapped repository governance on main. |
| 2026-09-26 | 0 | A single payoff line cannot safely represent two expiries. | Could create a false impression of a flat, low-risk payoff. | Strategy design explicitly tracks near-expiry and next-expiry settlement separately. |
| 2026-09-26 | 0 | The user's 2.5% threshold has no specified denominator. | A percentage trigger is otherwise non-reproducible. | Keep denominator configurable and report multiple economically meaningful denominators in later phases. |

## Logging rule

Add a row whenever a reproducible mistake, failed assumption, data-quality issue or workflow failure affects the research. Do not delete historical rows; append corrections with dates.

| 2026-09-26 | 5 | Phase 5 could be incorrectly interpreted as empirical evidence before the Phase 3/4 ledger exists. | Would create unsupported regime conclusions. | Branch explicitly requires a validated ledger before execution and labels current work as protocol/scaffold only. |

| 2026-09-26 | 5 | Separate Phase 4/5 workflow runs require explicit artifact handoff. | A completed Phase 3 run would not automatically expose its files to a later workflow workspace. | Repaired on `phase-5-regimes` by downloading the Phase 3 artifact by run ID. |
| 2026-09-26 | 3 | Configured-capital trigger mode was not passed through to the denominator function. | That sensitivity mode would fail at runtime. | Corrected on `phase-5-regimes`. |
| 2026-09-26 | 6 | Earlier main-branch status files still described empirical execution as pending after the completed workflow chain. | Repository navigation could present stale research state. | Main README and STATUS were synchronized with the completed Phase 6 manuscript and empirical workflow IDs. |

| 2026-09-26 | 6 | “Selected trades” was presented as if the user had supplied a separate historical trade-selection criterion. | The Phase 3 ledger filtered 891 eligible timestamps down to 28 by applying an assistant-implemented gate: ATM first, then -400/+400, requiring chart_return_pct > 2.5% using the buy-premium denominator. The user has now clarified that no such selection criterion was supplied. This makes the 28-trade result a model-imposed conditional sample, not an established result for the user's strategy. | Mark the 28-trade result provisional; do not treat it as the user's selection rule. Rerun only after the selection/trigger semantics and denominator are explicitly confirmed. No new criterion will be inferred. |


| 2026-09-26 | 3 | Earlier results used an incomplete ATM/-400/+400 fallback and were not faithful to the clarified strategy. | Prior empirical conclusions were conditional on the wrong selection rule. | Superseded them with full 50-point ±500 strike-grid runs 36262958536, 36263760476 and 36263974629. |