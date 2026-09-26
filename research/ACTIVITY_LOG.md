# Activity log

This is the observable research/repository activity log. It records actions, outputs and decisions; it is not a transcript of private internal reasoning.

| Date | Phase | Step | Outcome |
|---|---|---|---|
| 2026-09-26 | 0 | Inspected repository metadata | Repository was public, empty, default branch main, write access available. |
| 2026-09-26 | 0 | Reviewed current NIFTY contract specification | NIFTY 50 weekly options and Tuesday expiry convention documented. |
| 2026-09-26 | 0 | Reviewed broker/regulatory cost references | Paytm Money brokerage is configurable; NSE charge schedules are separately documented. |
| 2026-09-26 | 0 | Reviewed public historical-data sources | Public datasets and NSE report endpoints identified. |
| 2026-09-26 | 0 | Formalized research plan | Six research phases defined. |
| 2026-09-26 | 1 | Implemented strategy/payoff functions | Four legs, static chart payoff and correct cross-expiry payoff encoded. |
| 2026-09-26 | 1 | Added deterministic tests | Formula, strike-shift and threshold assertions added. |
| 2026-09-26 | 1 | Added manual workflow | Phase 1 can be manually executed in GitHub Actions. |
| 2026-09-26 | 2 | Selected primary data source | Public 1-minute NIFTY index/options source selected for reproducible extraction. |
| 2026-09-26 | 2 | Added data specification/extractor | Entry candidates and expiry pairing are generated deterministically. |
| 2026-09-26 | 2 | Added cache workflow | Source files are cached during workflow execution. |
| 2026-09-26 | 2 | Added literature review | Put-call parity, synthetic forwards and transaction-cost references recorded. |
| 2026-09-26 | 3 | Added transaction-cost model | Brokerage, exchange, SEBI, stamp duty, GST, STT and slippage components added. |
| 2026-09-26 | 3 | Added backtest engine | ATM trigger with -400/+400 fallback and configurable denominator implemented. |
| 2026-09-26 | 3 | Corrected expiry STT | Exercise STT on long-leg intrinsic value added. |
| 2026-09-26 | 3 | Corrected historical lot treatment | Expiry-specific lot sizes used; unequal-lot transition pairs excluded. |
| 2026-09-26 | 3 | Attempted exact-runtime validation | Container could not resolve raw.githubusercontent.com; no historical result was claimed. |
| 2026-09-26 | 4 | Added statistical validation framework | Bootstrap CI, monthly aggregation, walk-forward and sensitivity workflow prepared. |
| 2026-09-26 | 5 | Audited official regime-data sources | NSE historical derivatives reports and India VIX sources were verified; RBI/FBIL FX provenance documented. |
| 2026-09-26 | 5 | Added regime protocol | Point-in-time regime variables and acceptance criteria frozen before empirical execution. |
| 2026-09-26 | 5 | Added executable attribution scaffold | Script and manual GitHub Actions workflow added; execution awaits Phase 3/4 ledger. |
| 2026-09-26 | 5 | Workflow audit after continuation | Found that Phase 4/5 manual runs expected a local Phase 3 file that a separate workflow run would not have. Updated both workflows to download the selected Phase 3 artifact by run ID. Also corrected Phase 3 configured-capital trigger handling and kept chart-trigger denominator based on observed premiums while applying slippage only to realized P&L. |

| 2026-09-26 | 3 | Improved phase-to-phase data handoff | Phase 3 can now consume the cached Phase 2 strategy-input artifact by run ID, avoiding unnecessary reconstruction when that artifact exists; it retains an explicit fallback build path. |

| 2026-09-26 | 5 | Enabled autonomous empirical chain | Phase 2 now triggers Phase 3 after successful data validation; Phase 3 passes its artifact run ID to Phase 4; Phase 4 passes the Phase 3 run ID to terminal Phase 5. |
| 2026-09-26 | 5 | Added point-in-time spot-derived regime builder | Uses only pre-entry 09:20 NIFTY spot history to classify prior 20-observation trend, prior 20-observation annualized volatility, and prior-entry move. No same-day end-of-day information is used. |
| 2026-09-26 | 5 | Regime-builder runtime repair | Corrected dependency ordering and the NumPy logarithmic-return import; another bounded Phase 5 run will verify the point-in-time regime table. |
| 2026-09-26 | 5 | Corrected regime summary output | Phase 5 now reports only the predeclared categorical trend, volatility and entry-move regimes, avoiding one-row-per-continuous-value artifacts. |
| 2026-09-26 | 6 | Began Phase 6 manuscript | Empirical Phases 3–5 produced completed artifacts; manuscript structure was populated with equations, methods, tables, figures, results, discussion, limitations and future research. |
| 2026-09-26 | 6 | Added reproducibility package | Key Phase 3/4/5 result snapshots and SVG figures were committed to the Phase 6 branch. |
| 2026-09-26 | 6 | Final research assessment | Historical performance is positive under the tested buy-premium specification, but denominator ambiguity, sparse selection, concentration, uncertainty and execution-data limitations prevent a robust/risk-free interpretation. |

| 2026-09-26 | 3 | Corrected strike-selection specification | Replaced the earlier ATM/-400/+400 implementation with ATM first, then all 50-point shifts from -500 through +500 when ATM fails; every fallback strike exceeding the trigger is retained, with no extra ranking rule. |
| 2026-09-26 | 3 | Expanded Phase 3 input extraction | New extraction produced 19,341 rows: 15,701 complete, 3,498 unavailable candidate strikes, 142 missing settlements. |
| 2026-09-26 | 3 | Repaired strike-grid workflow runtime | Three reruns reached data extraction but failed at the src import. Added workflow PYTHONPATH=. and optional HF token wiring; a new rerun is in progress. |

| 2026-09-26 | 3 | Strike-grid schema repair | Added the missing shift_points field to expanded Phase 3 inputs, persisted the full candidate-shift metadata, and triggered a clean rerun. |
| 2026-09-26 | 3 | Workflow efficiency repair | Added concurrency cancellation and cache save-always so debugging cannot leave multiple long data-extraction runs consuming runners. |

| 2026-09-26 | 3 | Final corrected full-grid run | Run 36262958536 succeeded; 63 trade rows across 52 timestamps, including 24 ATM and 39 fallback-grid trades. |