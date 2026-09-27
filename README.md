# Options-Payoff-v1

> **LIVE RESEARCH STATUS — 27-Sep-2026**
>
> **Phase 9A is the authoritative research phase.** The actual strategy closes all four legs at the near weekly expiry: near-expiry CE/PE settle; far-expiry CE/PE are manually squared off using their observed market prices at the near-expiry close. All earlier realized-P&L conclusions based on holding the far legs to their own expiry are superseded.
>
> Current corrected H1 execution: GitHub Actions run **36296334057** on `phase-9-near-expiry-exit-correction` is rebuilding the full entry grid with point-in-time far-leg exit prices. Unit tests have passed; the data-reconstruction step is active. H2/H3 remain frozen until H1 is complete.
>
> A second execution-cost audit also corrected entry slippage in gross P&L and exit/exercise STT date handling before accepting any H1 result. The corrected workflow models six economic transactions (four entries + two far-leg manual exits), 0.25% premium slippage, ₹20/order brokerage for the primary historical ledger, and includes broker-cost sensitivity. Current Paytm Money F&O guidance says ₹10 per executed unique F&O order, while older published Paytm Money material documents a ₹20 regime; this ambiguity is treated as a sensitivity rather than silently resolved.
>
> Phase 9B validation is pre-wired to run automatically after a successful Phase 9A v3 run and will produce the corrected loss audit, bootstrap/time-split statistics, slippage sensitivity, Paytm Money brokerage sensitivity, and weekly ledger.
>
--- 

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

The phase-6-manuscript-grid branch was found to contain a stale copy of scripts/run_backtest.py using the old ATM/±400 fallback order; it was corrected in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4.

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


## Phase 9A — Corrected H1 near-expiry manual-close baseline

Authoritative Actions run **36297418698** completed successfully. The corrected strategy closes all four legs at the near weekly expiry; far CE/PE are manually squared off at observed prices at or before the near-expiry index close.

Primary H1 result at 0.25% premium slippage and ₹20/order brokerage:
- 252 weekly cycles scanned
- 64 selected trades
- gross P&L ₹25,859.55
- modeled costs ₹13,541.69
- net P&L ₹12,317.86
- win rate 51.56%
- profit factor 1.47
- maximum drawdown approximately -₹6,363.84

Independent audit: 27/31 losers were already negative before fees; 4/31 net losses were cost-only flips; all selected trades have complete far-leg exit timestamps and none exits after near expiry.

These results supersede all previous realized-P&L numbers based on holding the far legs to their own expiry. Full details: `docs/PHASE9A_RESULTS.md`.

**Current state:** Phase 9A is complete. Phase 9B statistical validation is next; H2/H3 remain frozen until that validation is complete.


## Phase 9B — Corrected H1 statistical validation

Phase 9B run **36297884737** completed successfully against the authoritative Phase 9A artifact.

Primary corrected H1:
- 64 selected trades / 252 weekly cycles
- net P&L ₹12,317.86
- gross P&L ₹25,859.55
- modeled costs ₹13,541.69
- win rate 51.56%
- profit factor 1.47
- max drawdown -₹6,363.84
- trade-level Sharpe-like 1.03; Sortino-like 0.23
- IID bootstrap 95% CI for mean trade P&L: -₹164.65 to +₹556.90
- weekly-block bootstrap 95% CI: -₹119.65 to +₹538.84
- chronological 70/30: +₹11,280.49 train, +₹1,037.36 test
- 50 bp slippage: +₹1,982.44 net
- 100 bp slippage: -₹18,688.40 net
- ₹40/order brokerage: +₹3,255.46 net

Research interpretation: the corrected H1 result is not robust enough to be treated as a validated standalone trading edge under realistic execution uncertainty. This supersedes all previous realized-P&L conclusions based on holding the far legs to their own expiry.

Phase 9C H2/H3 corrected-horizon workflow is queued in GitHub Actions run **36297960485**. No H2/H3 result is treated as available until that run completes.


## Critical Phase 9D correction — intraday recheck

**The previously reported Phase 9A/9B H1 results are superseded.** The implementation incorrectly treated 09:20 as the only entry observation of each trading day. The actual strategy uses 09:20 as the first check, then keeps checking later intraday timestamps on the same day and subsequent trading days of that weekly cycle until a positive/all-green opportunity appears.

The corrected Phase 9D implementation scans every available 1-minute timestamp from 09:20 to 15:29, evaluates ATM-400..ATM+400, chooses the maximum positive flatline at the first positive timestamp, and records an auditable scan history.

Important distinction: the selected **chart flatline win rate is expected to be 100% by construction**, because the strategy only enters when the flatline is positive. That does not automatically imply a 100% realized trading P&L win rate for a mixed-expiry position whose far legs are later liquidated at market prices. The new research reports both metrics separately.

Current workflow: **Phase 9D — Intraday Recheck Near-Expiry Strategy**.


## Phase 9G — H2/H3 far-expiry selection EXECUTING

The corrected H1 control has passed the Phase 9E historical validation and the Phase 9F contextual audit without adopting a new filter. Phase 9G now evaluates fixed H1/H2/H3 far-expiry horizons under the same intraday first-positive rule and near-expiry manual-close convention. Dynamic horizon switching is not permitted.

Active research branch: [phase-9G-h2-h3-far-expiry-selection](https://github.com/vishnuvcr/Options-Payoff-v1/tree/phase-9G-h2-h3-far-expiry-selection)  
Plan: [docs/PHASE9G_H2_H3_PLAN.md](https://github.com/vishnuvcr/Options-Payoff-v1/blob/phase-9G-h2-h3-far-expiry-selection/docs/PHASE9G_H2_H3_PLAN.md)

The current Actions reconstruction runs are **36304489832** and **36304477026**. Earlier setup failures are logged. A pre-analysis audit also identified a sensitivity-stage input-schema mismatch; no sensitivity result is being accepted until that is corrected and rerun.
