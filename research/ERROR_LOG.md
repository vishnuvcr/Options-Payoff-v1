# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 0 | Initial GitHub repository contained no files. | No existing plan/log/code could be reused. | Bootstrapped repository governance on main. |
| 2026-09-26 | 0 | A single payoff line cannot safely represent two expiries. | Could create a false impression of a flat, low-risk payoff. | Strategy design explicitly tracks near-expiry and next-expiry settlement separately. |
| 2026-09-26 | 0 | The user's 2.5% threshold has no specified denominator. | A percentage trigger is otherwise non-reproducible. | Keep denominator configurable and report multiple economically meaningful denominators in later phases. |
| 2026-09-26 | 0 | First repository-write script failed because embedded backticks broke the tool-call JavaScript string. | No repository data were committed by the failed call. | Rewrote the file payloads without the conflicting delimiters and completed the bootstrap successfully. |
| 2026-09-26 | 1 | The first local test harness was a shortened copy rather than the exact repository test file. | It did not execute every final repository assertion. | Re-verified the formulas and repository test design; future phases will execute the exact checked-out repository files in CI. |
| 2026-09-26 | 2 | First Phase 2 write payloads failed because JavaScript template/quote syntax conflicted with GitHub Actions expressions and embedded shell quoting. | The Phase 2 repository mutation did not occur in those failed calls. | Switched to line-array file construction; subsequent Phase 2 files were written successfully. |
| 2026-09-26 | 2 | Primary public dataset exposes OHLCV/OI bars rather than bid/ask quote history. | Direct bid/ask execution cannot be reconstructed from this source alone. | Label Phase 2 entries as close proxies and require Phase 3 spread/slippage sensitivity or quote-level cross-validation. |
| 2026-09-26 | 2 | NIFTY lot size varies historically and is not present as a trusted field in the selected source. | Per-lot rupee P&L cannot be finalized without a dated lot-size calendar. | Leave lot_size unset in Phase 2 and add a verified dated lot-size table in Phase 3. |
| 2026-09-26 | 2 | Autonomous Phase 2 produced the strategy-input artifact but `gh workflow run phase-3-backtest.yml --ref phase-3-backtest` returned HTTP 404 because the target workflow is not on the default branch. | Phase chaining stopped after valid Phase 2 data were built. | Replaced workflow-dispatch chaining with cross-branch trigger files plus `push` path triggers; future phase handoffs now operate from their own phase branches. |

## Logging rule

Add a row whenever a reproducible mistake, failed assumption, data-quality issue or workflow failure affects the research. Do not delete historical rows; append corrections with dates.