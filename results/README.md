# Empirical result snapshots

These files are immutable snapshots copied from completed GitHub Actions artifacts used for the manuscript.

Phase 3:
- workflow run 36256634939
- baseline: >2.5% chart trigger, buy-premium denominator, 0.25% premium slippage
- 28 selected trades from 891 eligible entry timestamps

Phase 4:
- workflow run 36257292327
- full descriptive validation, block bootstrap, 70/30 chronological split, threshold/slippage/denominator sensitivity, brokerage sensitivity
- current public Paytm Money brokerage is handled separately from the historical configurable baseline

Phase 5:
- workflow run 36257664922
- point-in-time NIFTY spot-derived categorical regimes only
- cross-market/FII-DII/India VIX/IV-history attribution remains a data-extension item rather than an invented result
