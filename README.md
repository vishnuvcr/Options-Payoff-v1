# Options-Payoff-v1

Research repository for testing the clarified cross-expiry NIFTY options strategy.

## Current status

**Phase 7 — payoff-platform semantics and maximum equal-flatline selection: ACTIVE**

The previous full-grid study is now a historical comparator. The user has changed the selection rule again:

- evaluate every 50-point strike from ATM-400 through ATM+400, including ATM;
- compute the estimated positive flatline max-profit=max-loss value for each candidate;
- select exactly one candidate per timestamp: the maximum estimated equal max-profit=max-loss value;
- keep the historical 2.5% percentage as a separately labeled sensitivity until the platform's exact historical margin denominator is reconstructed;
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

The exact Sensibull-style percentage uses margin required as its denominator; the current historical dataset does not contain that margin series. Phase 7 therefore uses the reproducible INR flatline value as the primary score and keeps the old 2.5% proxy only as a sensitivity.

### Phase 7 empirical result

The requested rule was evaluated on the cached 09:20 NIFTY candidate dataset:

- every 50-point common strike from ATM-400 through ATM+400;
- require the legacy 2.5% chart-percentage proxy to be >2.5%;
- select the single eligible strike with the maximum estimated equal max-profit=max-loss value.

At 0.25% premium slippage and ₹20/order brokerage:

- 905 grid timestamps
- 48 selected timestamps/trades
- ₹166,866.51 net P&L
- ₹3,476.39 mean trade P&L
- 60.42% win rate
- 1.56 profit factor
- -₹124,060.72 maximum drawdown
- 19 losing trades

The static chart component contributed ₹36,138.75; realized S2-S1 contributed ₹142,545.00 before entry slippage and fees. All 19 losing trades were already negative before modeled fees.

Full Phase 7 results: [docs/PHASE7_RESULTS.md](docs/PHASE7_RESULTS.md) and [results/phase7/summary.json](results/phase7/summary.json).

The exact Sensibull percentage denominator remains unresolved because its public formula uses margin required, while the historical margin series is not in the cached dataset. The 2.5% gate above is therefore an explicit proxy, not a claimed exact Sensibull reconstruction.
