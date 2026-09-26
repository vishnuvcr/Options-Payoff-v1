# Research status

**As of:** 2026-09-26
**Active branch:** phase-3-backtest
**Overall phase:** 3 — Backtest engine and transaction-cost model IMPLEMENTED; execution pending

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | COMPLETE | Strategy equations, payoff tests and manual workflow added. |
| 2 Data | IMPLEMENTED; VALIDATION PENDING | Data manifest, extractor and manual workflow exist. Runtime execution requires GitHub Actions/network access. |
| 3 Backtest | IMPLEMENTED; VALIDATION PENDING | Gross P&L, selection rule, transaction costs, exercise STT and unit tests added. Historical run has not been executed in this session. |
| 4 Validation | NOT STARTED | Walk-forward, bootstrap and robustness analyses. |
| 5 Regimes | NOT STARTED | Conditional/regime attribution. |
| 6 Manuscript | NOT STARTED | Final research manuscript and supplements. |

## Phase 3 results so far

1. The backtest separates the static chart trigger from the realized cross-expiry P&L.
2. The selection rule is deterministic: ATM first, then configurable -400/+400 fallback order.
3. Three explicit chart-trigger denominators are supported: buy-premium, spot-notional and configured-capital.
4. The cost engine includes four order brokerages, exchange premium-turnover charges, SEBI fee, buyer stamp duty, GST, entry-sale STT, and expiry-exercise STT on intrinsic value of long options.
5. Slippage is configurable because the Phase 2 dataset does not contain bid/ask quotes.
6. Lot size is a required explicit input; it is not silently inferred across historical contract changes.

## Current research conclusion

The static flatline chart is not the realized payoff of the cross-expiry position. A selected trade can pass the chart trigger and still lose money because the realized expiry component is S2 - S1 and because costs can consume a small entry-price edge.

## Blockers

- The GitHub Actions workflow has not been manually dispatched from this session.
- A dated NIFTY lot-size calendar is still required for a multi-year rupee P&L series.
- Quote-level bid/ask data are not in the primary Phase 2 source; Phase 3 therefore uses explicit slippage sensitivity until a quote-level source is validated.
- The percentage denominator in the user's 2.5% rule remains unconfirmed; all supported denominator modes must be reported before treating any signal result as final.