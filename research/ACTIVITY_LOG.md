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
| 2026-09-26 | 1 | Updated research status | Phase 1 marked complete; Phase 2 data engineering is next. |
| 2026-09-26 | 2 | Selected primary data source | thetrademarkk/india-index-options-1m selected for 1-minute NIFTY index/options data; source manifest added. |
| 2026-09-26 | 2 | Added data specification | Historical expiry transition, no-look-ahead rules, source validation and output schema documented. |
| 2026-09-26 | 2 | Added strategy-input extractor | Builds per-entry ATM/-400/+400 candidate rows from the NIFTY index and per-expiry option files. |
| 2026-09-26 | 2 | Added manual GitHub Actions workflow | Workflow caches Hugging Face files and uploads the derived strategy-input table as an artifact. |
| 2026-09-26 | 2 | Added initial literature review | Research references on put-call parity, synthetic forwards and transaction-cost frictions recorded. |