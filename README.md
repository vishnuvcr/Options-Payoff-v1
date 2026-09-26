# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current research status

**Active phase:** Phase 6A — loss-trade audit and reproducibility correction  
**Status:** COMPLETE  
**Date:** 2026-09-27

### Superseded result

The earlier 28-trade ATM/±400 result is superseded and must not be used as evidence for the clarified strategy.

### Corrected full-grid result

The authoritative corrected implementation tests ATM first and, when ATM fails, every 50-point common-strike shift from -500 through +500, retaining every qualifying fallback strike.

Authoritative runs:
- Phase 2: 36255238050
- Phase 3 grid: 36262958536
- Phase 4 validation: 36263760476
- Phase 5 regimes: 36263974629
- Phase 6A loss audit: 36264710663

Baseline under the working buy-premium denominator, 0.25% slippage and ₹20/order brokerage:
- 63 trade rows
- 52 distinct entry timestamps
- 24 ATM trades
- 39 fallback-grid trades
- ₹168,665.95 net P&L
- ₹2,677.24 mean trade P&L
- 60.32% win rate
- 1.37 profit factor
- -₹194,854.37 maximum drawdown

The 2.5% denominator is not explicitly confirmed by the original strategy description. The buy-premium denominator is a working implementation assumption. The tested spot-notional denominator generated no qualifying trades from 1% through 5%.

### Loss-trade audit — 2026-09-27

A direct artifact-backed audit was run against the authoritative 63-row Phase 3 selected-trade file.

- 38 winning rows
- 25 losing rows
- losing contribution: -₹454,335.44
- winning contribution: +₹623,001.39
- largest loss: -₹55,420.58
- 25/25 losers were negative before modeled brokerage/statutory fees
- 0/25 were fee-only losses
- 7 ATM losses and 18 fallback losses
- modeled costs on losing rows: ₹3,557.82

The key result is that every losing trade passed the positive >2.5% entry-chart trigger. The dominant failure mechanism is therefore the realized cross-expiry economic outcome, not transaction costs.

Full audit: docs/LOSS_TRADE_ANALYSIS.md

### Reproducibility correction

The 63-row result is authoritative from branch phase-3-strike-grid and run 36262958536.

A later phase-6-manuscript-grid branch contains a stale copy of scripts/run_backtest.py using the old ATM/±400 fallback order. That stale script must not be used to reproduce the 63-row result. The discrepancy is recorded in the phase-6-loss-audit error log and status.

### Research outputs

- docs/MANUSCRIPT.md — complete research manuscript
- docs/LOSS_TRADE_ANALYSIS.md — complete 25-loss ledger and diagnosis
- results/phase3_grid_summary.json
- results/phase4_grid_validation_summary.json
- results/phase4_grid_robustness.csv
- results/phase4_grid_brokerage_sensitivity.csv
- results/phase5_grid_regime_summary.csv

### Research status and governance

Research plan: research/RESEARCH_PLAN.md  
Instructions: research/RESEARCH_INSTRUCTIONS.md  
Status: research/STATUS.md  
Error log: research/ERROR_LOG.md  
Activity log: research/ACTIVITY_LOG.md  
Sources: research/SOURCES.md

Each phase remains on its own branch and exposes a manual GitHub Actions workflow.

## Main conclusion

Under the current working denominator and execution assumptions, the corrected full-grid backtest is historically positive, but the uncertainty intervals include zero, the chronology is strongly time-dependent, and the exact chart-percentage denominator remains unresolved.

The loss audit shows why the positive aggregate cannot be interpreted as a risk-free payoff-chart arbitrage: the static chart edge can be positive while the realized two-expiry settlement component is strongly negative.
