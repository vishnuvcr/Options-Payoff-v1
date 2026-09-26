# Research status

**As of:** 2026-09-26  
**Active branch:** phase-6-manuscript-grid  
**Overall status:** Phase 6 complete for the clarified full strike-grid strategy

| Phase | Status | Corrected evidence |
|---|---|---|
| 0 Governance | COMPLETE | Repository plan, instructions, logs and sources maintained. |
| 1 Specification | COMPLETE | Four-leg algebra and flat-chart vs cross-expiry payoff distinguished. |
| 2 Data | COMPLETE | Run 36255238050 supplied the core NIFTY index/options dataset. |
| 3 Backtest | COMPLETE | Run 36262958536 implemented ATM first, then every 50-point shift from -500 to +500; 63 trade rows, 52 entry timestamps. |
| 4 Validation | COMPLETE | Run 36263760476 completed uncertainty, walk-forward, threshold, slippage, denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Run 36263974629 completed point-in-time trend/volatility/entry-move attribution on the corrected 63-trade ledger. |
| 6 Manuscript | COMPLETE | Corrected manuscript, result snapshots and figures added. |

## Corrected primary result

Working implementation assumptions:

- 2.5% trigger denominator: sum of the two long-option premiums (not explicitly specified by the user)
- slippage: 0.25% per option premium
- brokerage: ₹20 per executed order
- historical lot size by expiry
- 09:20 close proxy for option execution
- exit at expiry

Results:

- 891 eligible entry timestamps
- 63 selected four-leg trade rows
- 52 distinct selected timestamps
- 24 ATM trades
- 39 fallback-grid trades
- 5.84% entry-timestamp selection rate
- total net P&L: ₹168,665.95
- mean trade P&L: ₹2,677.24
- median trade P&L: ₹6,831.26
- win rate: 60.32%
- profit factor: 1.37
- maximum drawdown: -₹194,854.37

## Key validation findings

- iid bootstrap 95% CI for mean trade P&L: -₹2,750 to ₹7,903.
- weekly block-bootstrap 95% CI: -₹5,628 to ₹9,958.
- chronological train segment: 45 trades, -₹50,828.
- chronological test segment: 18 trades, +₹219,494.
- 2.5% buy-premium result remains positive through 1% slippage; net P&L falls from ₹174,021 at 0% slippage to ₹152,600 at 1%.
- brokerage sensitivity remains positive at ₹10, ₹20 and ₹40/order.
- tested spot-notional denominator produced no qualifying trades from 1% through 5% thresholds.
- 50-point fallback selection materially changes the trade set: 39 of 63 trades are fallback-grid trades.

## Regime attribution

Descriptive point-in-time results on the corrected ledger:

- trend: down mean +₹6,035 (33 trades), sideways -₹7,145 (5), up +₹209 (25)
- volatility: high -₹12,183 (12), low +₹413 (25), medium +₹11,713 (26)
- entry move: down -₹3,350 (12), small +₹3,517 (19), up +₹4,439 (32)

These are descriptive associations, not additional trading rules.

## Current conclusion

The clarified rule is reproducible and historically positive under one explicit implementation, but the evidence is not sufficient to treat it as robust, denominator-independent or risk-free arbitrage. The main unresolved issue is the exact denominator used by the original payoff-chart interface for the 2.5% condition.

## Key outputs

- docs/MANUSCRIPT.md
- results/phase3_grid_summary.json
- results/phase4_grid_validation_summary.json
- results/phase4_grid_robustness.csv
- results/phase4_grid_brokerage_sensitivity.csv
- results/phase5_grid_regime_summary.csv
- docs/figures/grid_*.svg

## Next research priorities

Quote-level bid/ask validation, official settlement-price validation, exact recovery of the payoff-chart percentage definition, cross-market/FII-DII/India VIX/option-IV integration, and an untouched out-of-sample validation period.
