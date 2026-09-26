# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 0 | Initial GitHub repository contained no files. | No existing plan/log/code could be reused. | Bootstrapped repository governance. |
| 2026-09-26 | 0 | A single payoff line cannot safely represent two expiries. | Could create a false impression of a flat, low-risk payoff. | Track near and next expiry separately. |
| 2026-09-26 | 0 | 2.5% threshold has no specified denominator. | Trigger is otherwise non-reproducible. | Keep denominator configurable and report sensitivity. |
| 2026-09-26 | 1 | Initial local test harness was shortened. | It did not execute every final repository assertion. | Future validation uses exact repository files in CI. |
| 2026-09-26 | 2 | Primary public dataset exposes OHLCV/OI rather than bid/ask history. | Direct executable spread cannot be reconstructed. | Use explicit slippage sensitivity and seek quote-level validation. |
| 2026-09-26 | 2 | NIFTY lot size varies historically. | Multi-year rupee P&L could be mis-scaled. | Use expiry-date lot calendar and exclude unequal-lot pairs. |
| 2026-09-26 | 3 | Initial cost model omitted expiry exercise STT. | Net P&L could be overstated. | Added applicable exercise STT on long-leg intrinsic value. |
| 2026-09-26 | 3 | Container could not resolve raw.githubusercontent.com. | Exact checked-in runtime could not be executed locally. | Manual GitHub Actions remains authoritative. |
| 2026-09-26 | 3 | Paytm Money public brokerage figures require account-level reconciliation. | Hard-coding an uncertain rate could misstate net P&L. | Keep brokerage configurable. |
| 2026-09-26 | 5 | Regime variables can introduce look-ahead if same-day end-of-day values are joined to 09:20 entries. | Would invalidate causal timing. | Phase 5 requires point-in-time data known at or before entry and freezes regime values at entry. |
| 2026-09-26 | 5 | Current Paytm Money public F&O FAQ states Rs.10 per unique executed order, while the research model retains a higher conservative default. | Using an unverified historical broker schedule could bias net P&L. | Record Rs.10 as the current public rate, keep brokerage configurable, and use contract-note reconciliation for historical broker-specific results. |
| 2026-09-26 | 5 | Phase 5 empirical execution attempted without a validated trade ledger would create unsupported results. | Could produce fabricated or incomplete regime conclusions. | Added a prerequisite check and explicitly gated execution on Phase 3/4 artifacts. |

| 2026-09-26 | 5 | GitHub Actions API currently reports zero workflow runs for the repository. | There is no existing Phase 3/4 artifact available to consume. | Confirmed execution is genuinely pending rather than merely missing from the local session; empirical phases remain gated. |

## Logging rule

Append new rows for reproducible mistakes, failed assumptions, data-quality issues or workflow failures. Do not delete historical rows.
| 2026-09-26 | 5 | Separate Phase 4/5 workflow runs cannot see Phase 3's workspace files by path alone. | Manual workflow buttons could fail even after a successful Phase 3 run. | Phase 4 and Phase 5 now accept a Phase 3 run ID and download the named artifact before analysis. |
| 2026-09-26 | 3 | Configured-capital trigger mode was wired into the CLI but not passed into `trigger_base`, so that mode could not execute. | One of the declared denominator sensitivity modes would fail at runtime. | Pass the configured capital value explicitly and add the mode to the execution path. |
| 2026-09-26 | 3 | The chart trigger numerator used observed premiums while its buy-premium denominator used slippage-adjusted execution premiums. | Trigger percentage changed with the execution shock, mixing signal definition with cost stress. | Chart trigger now uses observed entry premiums; slippage is applied only to realized execution/P&L. |

| 2026-09-26 | 3 | Phase 3 originally rebuilt the Phase 2 input table instead of consuming a prior validated Phase 2 artifact. | Could waste bandwidth and weaken the intended cached-data workflow. | Phase 3 now accepts an optional Phase 2 run ID and downloads the phase-2-strategy-inputs artifact; rebuilding remains the explicit fallback. |
