# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current research status

**Active phase:** Phase 6 — empirical manuscript and reproducibility package  
**Status:** COMPLETE  
**Date:** 2026-09-26

### Primary result

The corrected historical backtest selected 28 trades from 891 eligible entry timestamps under the buy-premium interpretation of the 2.5% trigger, with 0.25% slippage and ₹20/order baseline brokerage.

Net P&L was ₹166,240.97; mean trade P&L ₹5,937.18; median ₹9,431.27; win rate 67.86%; profit factor 2.33; maximum drawdown -₹48,161.45.

The iid bootstrap CI for mean trade P&L spans approximately -₹434 to ₹11,735, and the weekly block bootstrap CI spans approximately -₹1,689 to ₹12,745. The chronological 70/30 split remains positive in the 9-trade test segment.

### Important interpretation

The flatline payoff chart is not the realized economic payoff of the cross-expiry position. The correct expiry component is S(next expiry) - S(near expiry), plus the entry premium edge and costs.

The 2.5% denominator remains a material specification ambiguity. The buy-premium denominator generated trades; the tested spot-notional denominator generated none across 1%–5% thresholds.

The selected sample is sparse and concentrated: 28 trades, all from 2021-08-05 through 2024-01-17, with approximately 89.3% of total selected-trade P&L coming from May and October 2022.

### Research outputs

- docs/MANUSCRIPT.md — complete research manuscript
- results/phase3_summary.json
- results/phase4_validation_summary.json
- results/phase4_brokerage_sensitivity.csv
- results/phase4_monthly_pnl.csv
- results/phase5_regime_summary.csv
- docs/figures/*.svg

### Phase status

- Phase 0 — governance: COMPLETE
- Phase 1 — strategy/payoff specification: COMPLETE
- Phase 2 — market-data engineering: COMPLETE
- Phase 3 — cost-aware backtest: COMPLETE
- Phase 4 — statistical validation and robustness: COMPLETE
- Phase 5 — point-in-time spot-derived regime attribution: COMPLETE
- Phase 6 — manuscript and reproducibility package: COMPLETE

### Remaining research opportunities

Quote-level bid/ask validation, official settlement-price validation, India VIX, FII/DII, option-IV/term-structure, USD/INR, gold, global equity and event-window data remain future extensions. They are intentionally not presented as completed results.

### Governance

Research plan: research/RESEARCH_PLAN.md  
Instructions: research/RESEARCH_INSTRUCTIONS.md  
Status: research/STATUS.md  
Error log: research/ERROR_LOG.md  
Activity log: research/ACTIVITY_LOG.md  
Sources: research/SOURCES.md

Each phase remains on its own branch and exposes a manual GitHub Actions workflow.

The complete manuscript is on the phase-6-manuscript branch.
