# Research status

**As of:** 2026-09-27  
**Active branch:** phase-6-loss-audit  
**Overall status:** Loss-trade audit complete for the clarified full strike-grid result

| Phase | Status | Corrected evidence |
|---|---|---|
| 0 Governance | COMPLETE | Repository plan, instructions, logs and sources maintained. |
| 1 Specification | COMPLETE | Four-leg algebra and flat-chart vs cross-expiry payoff distinguished. |
| 2 Data | COMPLETE | Run 36255238050 supplied the core NIFTY index/options dataset. |
| 3 Backtest | COMPLETE | Run 36262958536 implemented ATM first, then every 50-point shift from -500 to +500; 63 trade rows, 52 entry timestamps. |
| 4 Validation | COMPLETE | Run 36263760476 completed uncertainty, walk-forward, threshold, slippage, denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Run 36263974629 completed point-in-time trend/volatility/entry-move attribution. |
| 6 Manuscript | COMPLETE | Corrected manuscript and figures added. |
| 6A Loss audit | COMPLETE | Workflow 36264710663 audited all 63 selected rows directly from the Phase 3 artifact. |

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
- total net P&L: ₹168,665.95
- mean trade P&L: ₹2,677.24
- median trade P&L: ₹6,831.26
- win rate: 60.32%
- profit factor: 1.37
- maximum drawdown: -₹194,854.37

## Loss-trade audit result

- 38 winning rows
- 25 losing rows
- 25/25 losing rows were already negative before modeled fees
- 0/25 losses were caused solely by fees
- 7 losses were ATM and 18 were fallback-grid selections
- losing rows contributed -₹454,335.44 against +₹623,001.39 from winners
- total modeled costs on losing rows: ₹3,557.82
- largest loss: -₹55,420.58
- worst concentration: 2022-05-30 through 2022-06-07, -₹194,854.37

The audit shows that the positive chart trigger did not guarantee positive realized cross-expiry economics. Every loser passed the trigger.

## Key validation findings

- iid bootstrap 95% CI for mean trade P&L: -₹2,750 to ₹7,903.
- weekly block-bootstrap 95% CI: -₹5,628 to ₹9,958.
- chronological train segment: 45 trades, -₹50,828.
- chronological test segment: 18 trades, +₹219,494.
- 2.5% buy-premium result remains positive through 1% slippage; net P&L falls from ₹174,021 at 0% slippage to ₹152,600 at 1%.
- brokerage sensitivity remains positive at ₹10, ₹20 and ₹40/order.
- tested spot-notional denominator produced no qualifying trades from 1% through 5% thresholds.

## Reproducibility correction

The authoritative 63-row result is from branch phase-3-strike-grid and run 36262958536. The earlier stale run_backtest.py on phase-6-manuscript-grid was corrected in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4.

## Key outputs

- docs/MANUSCRIPT.md
- docs/LOSS_TRADE_ANALYSIS.md
- results/phase3_grid_summary.json
- results/phase4_grid_validation_summary.json
- results/phase4_grid_robustness.csv
- results/phase4_grid_brokerage_sensitivity.csv
- results/phase5_grid_regime_summary.csv
