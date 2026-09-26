# Research status

**As of:** 2026-09-26
**Active branch:** phase-6-manuscript
**Overall phase:** 6 — Empirical manuscript and reproducibility package COMPLETE

| Phase | Status | Evidence |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance, plan, sources, status and logs initialized. |
| 1 Specification | COMPLETE | Strategy equations, payoff model, strike candidates and tests validated. |
| 2 Data | COMPLETE | Run 36255238050 generated 2,763 candidate rows: 2,128 ok, 610 shifted-strike-unavailable, 25 missing-settlement. |
| 3 Backtest | COMPLETE | Corrected run 36256634939 generated the 28-trade cost-aware selected ledger. |
| 4 Validation | COMPLETE | Corrected run 36257292327 completed descriptive, walk-forward, block-bootstrap, threshold/slippage/denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Corrected run 36257664922 completed point-in-time NIFTY spot-derived categorical regime attribution. |
| 6 Manuscript | COMPLETE | Full manuscript, figures, result snapshots and reproducibility appendix committed on phase-6-manuscript. |

## Primary result

Under the buy-premium interpretation of the user's 2.5% trigger, 0.25% premium slippage and ₹20/order baseline brokerage:

- selected trades: 28 of 891 eligible timestamps
- total net P&L: ₹166,240.97
- mean trade P&L: ₹5,937.18
- median trade P&L: ₹9,431.27
- win rate: 67.86%
- profit factor: 2.33
- maximum drawdown: -₹48,161.45

The iid bootstrap 95% interval for mean trade P&L was approximately -₹434 to ₹11,735; the weekly block-bootstrap interval was approximately -₹1,689 to ₹12,745.

## Key robustness findings

The result remained positive across the tested 0%–1% slippage range and ₹10–₹40 brokerage sensitivity. The chronological 70/30 split was also positive in the nine-trade test segment.

The result is sparse and concentrated: all 28 selected trades occurred from 2021-08-05 through 2024-01-17, and May 2022 plus October 2022 contributed about 89.3% of total selected-trade P&L.

The denominator is a major specification issue: the buy-premium denominator generated trades, while the tested spot-notional denominator generated none across the 1%–5% threshold grid. Configured-capital sensitivity was not invented because no capital amount was supplied.

## Phase 5 interpretation

Point-in-time attribution used only prior 20-observation trend, prior 20-observation annualized volatility and prior 09:20 entry move. The descriptive sample showed the largest mean P&L in down-trend and medium-volatility buckets. These are not new trading rules and are not causal claims.

India VIX, FII/DII, option-IV/term-structure, USD/INR, gold, global-equity and event-window ingestion remain future data extensions rather than fabricated completed results.

## Final conclusion

The specified rule is reproducible and historically positive in the tested cost-aware sample, but the evidence is not strong enough to treat it as a robust, denominator-independent or risk-free arbitrage. The original flatline chart is not the correct economic payoff representation because the two synthetic forwards settle at different dates.

Principal limitations are the unresolved denominator, sparse sample, P&L concentration, confidence intervals spanning zero, close-based execution proxy, settlement proxy, incomplete cross-market attribution and account-specific historical brokerage uncertainty.

## Final manuscript

docs/MANUSCRIPT.md on the phase-6-manuscript branch is the complete research manuscript, including methods, tables, figures, discussion, strengths, limitations, conclusion, future research and reproducibility appendix.
