# Activity log

This is the observable research/repository activity log. It records actions, outputs and decisions; it is not a transcript of private internal reasoning.

| Date | Phase | Step | Outcome |
|---|---|---|---|
| 2026-09-26 | 0 | Inspected repository metadata | Repository is public, empty, default branch main, write access available. |
| 2026-09-26 | 0 | Reviewed current NIFTY contract specification | NIFTY 50 has four weekly option expiries; weekly expiry is Tuesday subject to holiday adjustment. |
| 2026-09-26 | 0 | Reviewed broker/regulatory cost references | Paytm Money currently describes a flat brokerage model; NSE states 2026 option-sale STT is 0.15%. Costs will remain configurable and dated. |
| 2026-09-26 | 0 | Reviewed public historical-data sources | Candidate public datasets exist on Hugging Face and GitHub; licensing/coverage will be validated in Phase 2. |
| 2026-09-26 | 0 | Formalized research plan | Six research phases defined; Phase 1 is next.

| 2026-09-26 | 5 | Created `phase-5-regimes` branch | Added frozen regime attribution protocol, source audit, executable scaffold and manual workflow; empirical execution remains gated. |

| 2026-09-26 | 5 | Audited continuation after user approval | Repaired Phase 4/5 artifact handoffs and corrected Phase 3 configured-capital trigger plumbing on `phase-5-regimes`; empirical execution remains pending. |
| 2026-09-26 | 6 | Completed empirical research chain | Phase 2 run 36255238050, Phase 3 run 36256634939, Phase 4 run 36257292327 and Phase 5 run 36257664922 completed successfully; final result snapshots and manuscript were committed to phase-6-manuscript. |
| 2026-09-26 | 6 | Final research conclusion recorded | The tested buy-premium specification produced positive historical net P&L, but denominator ambiguity, sparse selection, concentration, uncertainty and execution/settlement proxies prevent a robust/risk-free interpretation. |

| 2026-09-26 | 6 | User challenged the meaning of “selected trades” | Audited the Phase 3 code. It explicitly chooses ATM, then -400, then +400 when chart_return_pct > 2.5%, with buy_premium as the default denominator. This was an implementation choice, not a separately confirmed user-provided historical selection criterion. Results are now treated as provisional pending specification clarification. |
