# Research status

**As of:** 2026-09-26
**Active branch:** phase-2-data
**Overall phase:** 2 — Market-data acquisition, cleaning and cache COMPLETE

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | COMPLETE | Strategy equations, strike candidates, threshold helper, tests, and manual workflow added. |
| 2 Data | COMPLETE | Full-range Phase 2 artifact validated in GitHub Actions; handoff to Phase 3 repaired and re-triggerable. |
| 3 Backtest | NOT STARTED | Requires validated Phase 2 inputs and dated cost model. |
| 4 Validation | NOT STARTED | Out-of-sample and robustness analysis. |
| 5 Regimes | NOT STARTED | Conditional/regime attribution. |
| 6 Manuscript | NOT STARTED | Final research manuscript and supplements. |

## Phase 2 results so far

1. Primary data source selected: thetrademarkk/india-index-options-1m on Hugging Face.
2. Source manifest records the dataset structure, license, cross-check source and caching policy.
3. The extractor creates a long-form candidate table containing ATM, ATM-400 and ATM+400 candidates, the four option entry prices, near and next expiry settlements, and data-quality status.
4. Because source bars are OHLC rather than bid/ask quotes, the Phase 2 entry price is a 09:20 close proxy and is explicitly tagged as such.
5. Lot size is deliberately left unfilled until a dated NSE lot-size calendar is verified in Phase 3.
6. An initial literature review has been added, focusing on put-call parity, synthetic forwards and the erosion of apparent arbitrage after execution costs.

## Blockers

- The full-range autonomous Phase 2 workflow has now executed successfully; a separate handoff mechanism is used because GitHub CLI workflow dispatch requires the workflow to be present on the default branch.
- Bid/ask quote history is not present in the primary dataset; Phase 3 must either source quote-level data for a subset or use conservative slippage/spread sensitivity bands.
- Dated NIFTY lot sizes and the full Paytm Money/NSE charge stack must be verified before net P&L is treated as final.