# Options-Payoff-v1

Research repository for testing the clarified cross-expiry NIFTY options strategy.

## Current status

**Phase 7A — exact historical margin-denominator selection: COMPLETE**

The current research rule is now the exact platform-calibrated version. The superseded proxy studies remain in the repository only as comparators:

- evaluate every 50-point strike from ATM-400 through ATM+400, including ATM;
- compute the estimated positive flatline max-profit=max-loss value for each candidate;
- select exactly one candidate per timestamp: the maximum estimated equal max-profit=max-loss value;
- require reconstructed margin-based max-profit=max-loss percentage > 2.5%;
- select the maximum estimated equal max-profit=max-loss value in INR;
- compare maximum margin-based percentage as a sensitivity;
- exit at expiry.

The earlier ATM/-400/+400 analysis is superseded.

### Historical comparator — superseded selection rule

Using the working buy-premium denominator, 0.25% slippage and ₹20/order brokerage:

- 891 eligible timestamps
- 63 trade rows across 52 distinct timestamps
- 24 ATM selections
- 39 fallback-grid selections
- total net P&L: **₹168,665.95**
- mean trade P&L: **₹2,677.24**
- median trade P&L: **₹6,831.26**
- win rate: **60.32%**
- profit factor: **1.37**
- maximum drawdown: **-₹194,854.37**

The 2.5% denominator remains an implementation assumption because it was not specified in the strategy description. A tested spot-notional denominator produced no qualifying trades across 1%–5% thresholds.

### Superseded phase runs

- Phase 2: 36255238050
- Phase 3 full-grid: 36262958536
- Phase 4 full-grid validation: 36263760476
- Phase 5 full-grid regime attribution: 36263974629

### Manuscript and outputs

- [Research manuscript](docs/MANUSCRIPT.md)
- [Research status](research/STATUS.md)
- [Research plan](research/RESEARCH_PLAN.md)
- [Error log](research/ERROR_LOG.md)
- [Activity log](research/ACTIVITY_LOG.md)
- [Phase 3 result snapshot](results/phase3_grid_summary.json)
- [Phase 4 validation snapshot](results/phase4_grid_validation_summary.json)
- [Phase 4 robustness](results/phase4_grid_robustness.csv)
- [Phase 4 brokerage sensitivity](results/phase4_grid_brokerage_sensitivity.csv)
- [Phase 5 regime summary](results/phase5_grid_regime_summary.csv)
- [Corrected figures](docs/figures/)

### Phase 7 interpretation

The payoff chart's green flatline is a static one-spot representation. The economic cross-expiry position has terminal exposure to S2-S1, so the flatline is not by itself evidence of risk-free arbitrage.

Phase 7 now tests the requested maximum-flatline-value selection. The earlier 63-trade result is preserved only as a historical comparator for the superseded rule.

Platform review: [Streak and Sensibull payoff semantics](docs/PAYOFF_PLATFORM_REVIEW.md).

Phase 7 workflow: [.github/workflows/phase-7-max-equal-selection.yml](.github/workflows/phase-7-max-equal-selection.yml).

The exact platform denominator is now reconstructed from NSE/NSCCL SPAN margin data. The buy-premium percentage is no longer the primary gate.

### Phase 7 empirical result — superseded proxy

The earlier 48-trade Phase 7 result used the legacy buy-premium denominator only. It is retained as a historical sensitivity and is **not** the final interpretation of the user's 2.5% platform rule.

Proxy result: 48 trades, ₹166,866.51 net P&L, 60.42% win rate, PF 1.56, max drawdown -₹124,060.72.

### Phase 7A margin calibration

The user's Sensibull screenshot shows a standalone margin of ₹88,076 for the exact four-leg 23450 strategy. Using NSE/NSCCL SPAN data for 25-Sep-2026, the reconstructed consolidated margin is ₹87,812.40, only 0.2993% below the screenshot. The other same-day intraday SPAN versions are also within 0.91% of the screenshot.

Therefore the 2.5% Max Profit % denominator is now empirically calibrated as **margin required**, not option premium:

- 2.5% of screenshot margin: **₹2,201.90**
- 2.5% of closest SPAN-reconstructed margin: **₹2,195.31**

Calibration report: [docs/MARGIN_RECONSTRUCTION.md](docs/MARGIN_RECONSTRUCTION.md)
Calibration data: [results/phase7a/margin_calibration_2026-09-25.json](results/phase7a/margin_calibration_2026-09-25.json)
Intraday comparison: [results/phase7a/margin_calibration_versions_2026-09-25.json](results/phase7a/margin_calibration_versions_2026-09-25.json)

Historical SPAN coverage is 100% across the 891 entry dates. The exact primary ledger and settlement-file sensitivity ledger are committed under `results/phase7a/`.
### Phase 7A exact historical result

The 2.5% denominator is now reconstructed as margin required using NSE/NSCCL SPAN risk data. With the requested ATM-400..ATM+400 grid, 50-point steps and a >2.5% margin-based gate, the primary i1 begin-day SPAN interpretation produces **4 trades**:

- **₹42,680.17 net P&L**
- **75.0% win rate**
- **8.37 profit factor**
- **-₹5,791.42 maximum drawdown**
- **₹647.48 modeled costs**

Maximum estimated INR flatline value and maximum margin-based percentage select the same candidate on all four qualifying timestamps.

Settlement-file sensitivity produces 3 qualifying trades and ₹23,671.26 net P&L.

Full Phase 7A results: [docs/PHASE7A_RESULTS.md](docs/PHASE7A_RESULTS.md).

### Phase 7B — weekly cadence clarification

The user's operational rule is now interpreted as **one scan per weekly cycle** across all 17 common strikes (ATM-400..ATM+400). Among candidates with platform-style Max Profit % >2.5%, the highest estimated equal max-profit=max-loss value is selected; if none exceeds 2.5%, that week is skipped. The Phase 7A count of four is the number of qualifying historical observations under the exact-margin reconstruction, not the number of weekly scans. Phase 7B will map one non-look-ahead entry observation to each weekly cycle before producing a final weekly trade count.

### Phase 7B — final operational rule correction

The user's final rule is **not** a 2.5% rule. The 2.5% threshold and margin-based eligibility filter are removed.

Each weekly cycle scans all 17 common strikes from ATM-400 through ATM+400 in 50-point steps. Among candidates with a positive/all-green payoff flatline, the strike with the **maximum estimated equal max-profit=max-loss value** is selected and traded. There is no threshold-based weekly skipping.

Phase 7A's 4-trade result is therefore **superseded and must not be used as the final strategy result**. A new weekly-cadence backtest is being run on the cached candidate data.

### Phase 7B — corrected weekly result

The final rule now removes the 2.5% threshold entirely. The primary no-look-ahead interpretation is **first positive opportunity in each weekly expiry cycle**: scan all 17 strikes from ATM-400 through ATM+400, and when any positive/all-green flatline appears, trade the strike with the maximum positive flatline. No weekly cycle is skipped in the cached sample.

Preliminary baseline result: **63 weekly cycles, 63 trades, ₹-9,627.90 net P&L**, 57.14% win rate, ₹9,861.15 modeled costs. The `max_in_week` result is an ex-post oracle sensitivity and is not the primary backtest.
