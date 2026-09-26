# Research status

**As of:** 2026-09-27  
**Active branch:** phase-7A-margin-reconstruction  
**Overall status:** Phase 7A — screenshot margin calibration COMPLETE; historical per-entry margin cache PENDING

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
| 7 Payoff semantics + maximum-flatline selection | COMPLETE | 48-trade primary ledger evaluated; robustness, loss decomposition, slippage sensitivity and regime attribution completed. |

## Historical comparator — superseded selection rule

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

## Phase 7 outputs

- docs/MANUSCRIPT.md
- docs/LOSS_TRADE_ANALYSIS.md
- results/phase3_grid_summary.json
- results/phase4_grid_validation_summary.json
- results/phase4_grid_robustness.csv
- results/phase4_grid_brokerage_sensitivity.csv
- results/phase5_grid_regime_summary.csv
- docs/PAYOFF_PLATFORM_REVIEW.md
- .github/workflows/phase-7-max-equal-selection.yml


## Phase 7 specification

Primary rule:
- candidate strikes: ATM-400 to ATM+400 in 50-point steps, including ATM;
- selection: one candidate per timestamp, maximizing the positive estimated equal max-profit=max-loss flatline value;
- primary score: estimated equal max-profit=max-loss value in INR;
- 2.5% legacy percentage gate: sensitivity only, because the exact platform margin denominator has not yet been reconstructed.

The previous 63-trade result is preserved as historical evidence for the superseded ATM-first/full-grid fallback rule and must not be reported as the Phase 7 result.


## Phase 7 primary result

- grid timestamps: 905
- eligible timestamps after legacy 2.5% proxy gate: 48
- selected trades: 48
- net P&L: ₹166,866.51
- mean trade P&L: ₹3,476.39
- median trade P&L: ₹6,242.51
- win rate: 60.42%
- profit factor: 1.56
- maximum drawdown: -₹124,060.72
- largest loss: -₹55,321.89
- largest win: ₹35,233.55
- modeled costs: ₹7,334.77

## Phase 7 robustness

- iid bootstrap 95% CI for mean: -₹1,943.61 to ₹8,927.91
- weekly block bootstrap 95% CI: -₹3,672.56 to ₹9,932.60
- chronological 70/30: train ₹18,711.33; test ₹148,155.17
- net P&L at 0%, 0.25%, 0.50%, 1.00% slippage: ₹171,346.72; ₹166,866.51; ₹162,386.29; ₹153,425.87

## Phase 7 economic decomposition

- total static flatline P&L: ₹36,138.75
- total realized S2-S1 contribution: ₹142,545.00
- losses: 19
- losing contribution: -₹299,970.18
- loss-side S2-S1 contribution: -₹309,305.00
- 19/19 losses negative before fees
- 0 fee-only losses

See docs/PHASE7_RESULTS.md for detailed results and interpretation.
## Phase 7A status

Calibration target: Sensibull standalone margin ₹88,076 for the screenshot-identifiable 25-Sep-2026 NIFTY 23450 four-leg position, one 65-unit lot. NSE Clearing publishes daily SPAN risk-parameter files and historical margin/volatility data; Phase 7A reconstructs this denominator before replacing the legacy percentage proxy. See `.github/workflows/phase-7A-margin-reconstruction.yml`.

## Phase 7A calibration result

- Sensibull screenshot standalone margin: ₹88,076.00
- Reconstructed consolidated SPAN+exposure margin from NSE 25-Sep-2026 i05 SPAN: ₹87,812.40
- Difference: -₹263.60 (-0.2993%)
- i03 version: ₹87,723.22 (-0.4005%)
- i04 version: ₹87,532.12 (-0.6175%)
- i02 version: ₹87,437.48 (-0.7250%)
- i01 version: ₹87,276.41 (-0.9078%)
- The exact margin method is therefore calibrated to within 1% of the screenshot.
- 2.5% of the observed ₹88,076 margin = ₹2,201.90; 2.5% of the closest reconstructed ₹87,812.40 = ₹2,195.31.

The remaining Phase 7A task is historical margin reconstruction for all backtest entry dates/strikes. The screenshot denominator itself is now resolved.