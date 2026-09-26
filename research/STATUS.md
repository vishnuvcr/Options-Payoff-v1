# Research status

**As of:** 2026-09-26
**Active branch:** phase-6-manuscript
**Overall phase:** 6 — Empirical manuscript and reproducibility package COMPLETE

| Phase | Status | Evidence |
|---|---|---|
| 0 Bootstrap | COMPLETE | Repository governance, plan, status, logs and sources initialized. |
| 1 Specification | COMPLETE | Strategy equations, payoff tests and threshold helper validated. |
| 2 Data | COMPLETE | Phase 2 run 36255238050 produced 2,763 candidate rows: 2,128 ok, 610 shifted-strike-unavailable, 25 missing-settlement. |
| 3 Backtest | COMPLETE | Corrected Phase 3 run 36256634939 produced a 28-trade cost-aware selected ledger. |
| 4 Validation | COMPLETE | Corrected Phase 4 run 36257292327 completed descriptive validation, block bootstrap, walk-forward, slippage, threshold, denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Corrected categorical Phase 5 run 36257664922 completed point-in-time NIFTY spot-derived attribution. |
| 6 Manuscript | COMPLETE | Manuscript, figures, result snapshots, discussion, limitations and future research added. |

## Primary empirical result

Under the buy-premium denominator, 0.25% premium slippage and ₹20/order baseline brokerage assumption, 28 selected trades produced:

- total net P&L: ₹166,240.97
- mean trade P&L: ₹5,937.18
- median trade P&L: ₹9,431.27
- win rate: 67.86%
- profit factor: 2.33
- maximum drawdown: -₹48,161.45

The 95% iid bootstrap CI for mean trade P&L was approximately -₹434 to ₹11,735; the weekly block-bootstrap CI was approximately -₹1,689 to ₹12,745.

## Key robustness findings

- The result remained positive across 0% to 1% tested slippage.
- Brokerage sensitivity from ₹10 to ₹40 per executed order remained positive.
- The chronological 70/30 split produced positive P&L in the 9-trade test segment.
- The result is highly sparse and concentrated: 28 trades were selected from 891 eligible timestamps, and two months accounted for approximately 89.3% of total selected-trade P&L.
- The buy-premium denominator generated trades; the tested spot-notional denominator generated none from 1% through 5% thresholds.
- ATM accounted for 24 of 28 selected trades; the -400 fallback accounted for 4 and the +400 fallback for none.

## Phase 5 result

Point-in-time spot-derived attribution was completed using prior 20-observation trend, prior 20-observation annualized volatility and prior 09:20 entry move. The descriptive results showed the largest mean P&L in the prior down-trend and medium-volatility buckets. These are not new trading rules and should not be interpreted causally.

Cross-market/FII-DII/India VIX/IV-surface ingestion remains a future data-extension item, not a missing result that was fabricated.

## Final research conclusion

The specified rule is reproducible and historically positive in the tested cost-aware sample, but the evidence is not strong enough to treat it as a robust, denominator-independent or risk-free arbitrage. The original flatline chart is not the correct economic payoff representation because the two synthetic forwards settle at different dates.

The unresolved denominator, sparse selected sample, concentration of P&L, uncertainty intervals, close-based execution proxy and settlement-price proxy are the principal limitations.

## Final manuscript

See docs/MANUSCRIPT.md and the result snapshots under results/.

## Strike-grid rerun in progress

The previous 28-trade result is superseded as the primary specification. Phase 3 has been rewritten to match the clarified user rule:

1. Construct the four ATM legs.
2. Evaluate the payoff chart.
3. If ATM exceeds the 2.5% trigger, use ATM.
4. Otherwise evaluate every 50-point common-strike shift from -500 through +500 (excluding ATM).
5. Trade every fallback strike whose payoff chart exceeds 2.5%.
6. Exit at expiry.

The expanded data extraction has already completed 19,341 candidate rows (15,701 complete; 3,498 unavailable; 142 missing settlements). Net-P&L analysis is waiting on the corrected backtest workflow to complete. The earlier 28-trade statistics remain historical/provisional only.

## Final full-grid validation

Run 36263760476 succeeded using Phase 3 run 36262958536. Baseline: 63 trades, ₹168,665.95 net P&L, mean ₹2,677.24, median ₹6,831.26, win rate 60.32%, profit factor 1.37, max drawdown -₹194,854.37. IID and block-bootstrap mean intervals both include zero. Chronological train was -₹50,828; test was +₹219,494.
