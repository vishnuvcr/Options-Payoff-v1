# Options-Payoff-v1

Research repository for testing the clarified cross-expiry NIFTY options strategy.

## Current status

**Phase 8A — S2-S1 predictability: COMPLETE; no S2-S1 filter adopted**

Current operational rule:
- every weekly expiry cycle is scanned chronologically;
- at the first available observation where any candidate has a positive/all-green flatline, evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point steps;
- trade the candidate with the maximum positive estimated equal max-profit=max-loss flatline value;
- no 2.5% threshold, no margin percentage gate, and no threshold-based skipping.

Phase 7C tested reconstructed entry Greeks, IV term structure/skew, moneyness, and Greek imbalance against 63 weekly trades (36 winners, 27 losers). No tested feature remained robust after multiple-testing correction; simple feature-based strike selectors all underperformed the maximum-positive-flatline baseline; the best training-selected Greek/IV selector also underperformed it in both expanding walk-forward test blocks.

Phase 8A then tested whether the dominant economic term, future (S_2-S_1), could be predicted from entry-time information and used as a trade filter. The all-timestamp walk-forward design used 905 prior entry timestamps across 255 weekly cycles for training and 43 strictly OOS weekly decision cycles. Predictive sign accuracy was only 44.2% (Ridge), 51.2% (Random Forest), and 53.5% (HGB). The strongest apparent economic improvement came from Random Forest, but its paired bootstrap 95% CI included zero and its chronological block performance was unstable.

Therefore **no S2-S1 filter is adopted**. The primary entry-strike rule remains unchanged.

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

The Phase 7A margin reconstruction remains in the repository as a platform-semantics research artifact, but the margin-based 2.5% gate is no longer part of the user's final strategy.

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
### Phase 7A exact historical result — superseded

The earlier exact-margin result used a >2.5% gate and produced **4 qualifying observations**. This is retained only as historical evidence because the user subsequently removed the 2.5% rule and margin gate.

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


### Phase 7B final result

The 2.5% threshold and margin filter are removed. The final rule evaluates all 17 strikes from ATM-400 to ATM+400 in 50-point steps and selects the maximum positive/all-green flatline. The primary no-look-ahead operationalization is the first positive 09:20 opportunity in each weekly expiry cycle.

Result: **63 weekly cycles, 63 trades, 0 skipped weeks, ₹-9,627.90 net P&L** after 0.25% premium slippage and ₹20/order brokerage; 57.14% win rate, PF 0.98, max drawdown ₹-174,083.24, modeled costs ₹9,861.15.

The positive static chart component totaled ₹20,213.00, while realized cross-expiry S2-S1 contribution totaled ₹-19,979.75 before costs. IID 95% CI for mean weekly P&L: ₹-4,996 to ₹4,410; four-week block CI: ₹-4,024 to ₹4,739.

See [docs/PHASE7B_RESULTS.md](docs/PHASE7B_RESULTS.md) and [results/phase7b/summary.json](results/phase7b/summary.json).

### Phase 7C — Entry Greeks and feature discrimination

The current research is testing whether entry-time Greeks, IV term structure/skew, moneyness, and Greek imbalance differ between winning and losing trades and whether they can improve strike selection within the same 17-strike weekly grid. Features are treated as hypotheses only; multiple-testing correction, paired weekly bootstrap and out-of-sample validation are required before adopting any new selector.

### Phase 7C — Entry Greeks / feature selection conclusion

The winner-versus-loser study and candidate-level tests are complete. Across 63 weekly trades (36 winners, 27 losers), reconstructed entry Greeks, IV term structure/skew and moneyness show descriptive differences but **no robust feature survives multiple-testing correction**. Simple feature-based strike selectors all underperform the maximum-positive-flatline baseline, and the best training-selected Greek/IV selector underperformed it in both expanding walk-forward test blocks. No Greek-based strike filter has been added to the strategy.

Detailed report: [docs/ENTRY_FEATURE_GREEK_ANALYSIS.md](docs/ENTRY_FEATURE_GREEK_ANALYSIS.md) (workflow run 36291838252).

Compact Phase 7C outputs: [winner/loser Greek summary](results/phase7c/winner_loser_greek_summary.csv), [selector bootstrap comparison](results/phase7c/selector_bootstrap_summary.csv), and [walk-forward feature selection](results/phase7c/walk_forward_feature_selection.csv).

### Phase 8A — Predicting the cross-expiry S2-S1 component

The next research question is whether the future settlement difference (S_2-S_1), which dominated the economics of the current strategy, can be predicted from entry-time information. Phase 8A uses only cached internal option/surface/spot information with expanding one-week-ahead walk-forward validation. The predefined filters are predicted S2-S1 > 0 and expected trade P&L > 0 after modeled costs. External variables such as futures basis, India VIX, global markets, USD/INR, gold and FII/DII flows are reserved for Phase 8B only if the internal baseline shows predictive signal.


### Phase 8A — S2-S1 predictor conclusion

The S2-S1 term is the dominant economic risk component of the strategy, but it was not predictable robustly enough out of sample with the cached internal information. Random Forest improved the same-test OOS P&L from ₹-10,634.75 to ₹91,388.05 when filtering on predicted S2-S1 > 0, a +₹102,022.80 difference, but directional accuracy was only 51.16%, AUC 0.5136, and chronological block differences were +₹140,877, -₹58,226 and +₹19,372. The paired weekly bootstrap mean improvement was +₹2,372.62/week with a 95% CI of ₹-2,740.68 to ₹7,993.14.

This is treated as an unstable research signal, not a usable trading rule.

Detailed report: [Phase 8A S2-S1 results](docs/PHASE8_S2_S1_RESULTS.md)  
Compact model summary: [results/phase8/s2_s1_model_summary.csv](results/phase8/s2_s1_model_summary.csv)  
Chronological stability: [results/phase8/s2_s1_block_stability.csv](results/phase8/s2_s1_block_stability.csv)

### Final research conclusion

The current research does not validate a deployable trading edge for the final positive-flatline weekly strategy. The static green payoff chart is not sufficient because the actual cross-expiry economics are dominated by S2-S1. Phase 8A tested whether S2-S1 could be predicted from entry-time information, but out-of-sample directional accuracy remained close to chance and the apparent economic uplift was unstable across chronological blocks.

**No Greek filter and no S2-S1 filter has been added.**

Consolidated conclusion: [docs/FINAL_CONCLUSION.md](docs/FINAL_CONCLUSION.md).


## Phase 9 — Far-expiry selection grid

A new predeclared research extension is staged on branch phase-9-far-expiry-selection-grid.

The experiment keeps the near weekly expiry unchanged but lets the far leg expiry be chosen from:
- next week (H=1);
- next-next week (H=2);
- next-next-next week (H=3).

For each weekly decision, all 17 common strikes and all three far-expiry horizons are evaluated. The primary experimental selector is the maximum positive estimated equal max-profit=max-loss flatline.

A critical implementation issue is overlap: H=2/H=3 positions remain open after the near expiry, so the new backtest must use a portfolio-level chronological ledger with overlapping positions, transaction costs, slippage and capital/margin usage.

Phase 9 is currently design/staging only; no new trading conclusion has been accepted yet.
