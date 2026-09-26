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
