# Activity log

This is the observable research/repository activity log. It records completed actions, outcomes and implementation decisions; it is not a transcript of private internal reasoning.

| Date | Phase | Step | Outcome |
|---|---|---|---|
| 2026-09-26 | 3 | Corrected user strategy specification | Replaced the incomplete ATM/-400/+400 implementation with the full 50-point grid from -500 to +500, ATM first and every qualifying fallback retained. |
| 2026-09-26 | 3 | Expanded candidate extraction | Generated 19,341 candidate rows; 15,701 complete, 3,498 unavailable, 142 missing settlement. |
| 2026-09-26 | 3 | Corrected runtime issues | Fixed Python path, strike-grid schema, PyArrow compatibility and trigger-denominator unit handling. |
| 2026-09-26 | 3 | Final full-grid backtest | Run 36262958536 succeeded with 63 selected trade rows across 52 timestamps. |
| 2026-09-26 | 4 | Corrected robustness workflow | Run 36263760476 succeeded after adding the missing brokerage-sensitivity helper and adapting robustness selection to the full grid. |
| 2026-09-26 | 4 | Validation completed | Bootstrap, block bootstrap, walk-forward, threshold, slippage, denominator and brokerage results generated. |
| 2026-09-26 | 5 | Corrected regime rerun | Run 36263974629 succeeded using the corrected 63-trade ledger. |
| 2026-09-26 | 6 | Corrected manuscript | Replaced the earlier 28-trade manuscript with the full-grid results and new figures. |
| 2026-09-27 | 6A | Loss audit requested | User requested a complete audit of all losing trades because of doubt about the positive aggregate result. |
| 2026-09-27 | 6A | Artifact-backed loss audit | Workflow 36264710663 read selected_trades.parquet from authoritative run 36262958536 and produced a 25-row loss ledger. |
| 2026-09-27 | 6A | Loss decomposition | All 25 losers had negative gross P&L before fees; 0 were fee-only flips. Losing rows contributed -₹454,335.44 and modeled costs on them were ₹3,557.82. |
| 2026-09-27 | 6A | Reproducibility audit | Found stale run_backtest.py on phase-6-manuscript-grid; authoritative 63-row code remains phase-3-strike-grid. |
