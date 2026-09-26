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
| 2026-09-26 | 1 | Added deterministic Phase 1 tests | Local unit tests passed for flat chart construction, two-expiry P&L, hidden-loss case, strike shifts and threshold logic. |
| 2026-09-26 | 1 | Added manual GitHub Actions workflow | Phase 1 workflow can be run manually from GitHub Actions. |
| 2026-09-26 | 1 | Updated research status | Phase 1 marked complete; Phase 2 data engineering is next.
