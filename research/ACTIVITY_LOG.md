# Activity log

This is the observable research/repository activity log. It records actions, outputs and decisions; it is not a transcript of private internal reasoning.

| Date | Phase | Step | Outcome |
|---|---|---|---|
| 2026-09-26 | 0 | Inspected repository metadata | Repository is public, empty, default branch main, write access available. |
| 2026-09-26 | 0 | Reviewed current NIFTY contract specification | NIFTY 50 has four weekly option expiries; weekly expiry is Tuesday subject to holiday adjustment. |
| 2026-09-26 | 0 | Reviewed broker/regulatory cost references | Paytm Money current material supports a flat brokerage model for the applicable account population; NSE states 2026 option-sale STT is 0.15%. |
| 2026-09-26 | 0 | Reviewed public historical-data sources | Candidate public datasets exist on Hugging Face and GitHub; licensing/coverage will be validated in Phase 2. |
| 2026-09-26 | 0 | Formalized research plan | Six research phases defined; Phase 1 is next. |
| 2026-09-26 | 1 | Implemented strategy/payoff functions | Encoded the four legs, static chart payoff, correct cross-expiry payoff, strike candidates and threshold helper. |
| 2026-09-26 | 1 | Added deterministic Phase 1 tests | Unit tests passed in the local mirrored harness for flat chart construction, cross-expiry P&L, hidden-loss case, strike shifts and threshold logic. |
| 2026-09-26 | 1 | Added manual GitHub Actions workflow | Phase 1 workflow can be run manually from GitHub Actions. |
| 2026-09-26 | 2 | Selected primary data source | thetrademarkk/india-index-options-1m selected for 1-minute NIFTY index/options data; source manifest added. |
| 2026-09-26 | 2 | Added data specification | Historical expiry transition, no-look-ahead rules, source validation and output schema documented. |
| 2026-09-26 | 2 | Added strategy-input extractor | Builds per-entry ATM/-400/+400 candidate rows from the NIFTY index and per-expiry option files. |
| 2026-09-26 | 2 | Added manual GitHub Actions workflow | Workflow caches Hugging Face files and uploads the derived strategy-input table as an artifact. |
| 2026-09-26 | 2 | Added initial literature review | Research references on put-call parity, synthetic forwards and transaction-cost frictions recorded. |
| 2026-09-26 | 3 | Added transaction-cost model | Added brokerage, exchange, SEBI, stamp duty, GST, entry STT and expiry-exercise STT components. |
| 2026-09-26 | 3 | Added backtest engine | Added deterministic ATM then fallback selection, configurable 2.5% trigger denominator and selected-trade/candidate outputs. |
| 2026-09-26 | 3 | Added manual Phase 3 workflow | Workflow rebuilds Phase 2 inputs, runs the backtest and uploads results. |
| 2026-09-26 | 3 | Added correction for expiry STT | Long-leg intrinsic value at expiry is now charged under the applicable exercise-STT rate. |
| 2026-09-26 | 3 | Attempted exact-runtime validation | Environment could not resolve raw.githubusercontent.com; no claim of an executed GitHub Actions backtest is made. |
| 2026-09-26 | 3 | Verified historical NIFTY lot-size transitions | Encoded expiry-date lot sizes and excluded unequal-lot transition pairs from the one-for-one spread sample. |

| 2026-09-26 | 4 | Added validation framework | Added bootstrap CI, monthly aggregation, profit factor, drawdown and validation-gate workflow; execution awaits Phase 3 output artifact. |

| 2026-09-26 | 4 | Implemented full robustness grid, chronological holdout, block bootstrap and selection-by-strike analysis. | Phase 4 now operationalizes the predeclared sensitivity plan using the Phase 2 strategy-input artifact. |
