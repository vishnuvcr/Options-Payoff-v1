# Phase 4 — Statistical validation and robustness

## Objective

Determine whether the strategy's positive results, if any, survive realistic execution assumptions and alternative definitions of the 2.5% trigger denominator.

## Primary tests

1. Full-period net P&L, win rate, profit factor and maximum drawdown.
2. Bootstrap 95% confidence interval for mean trade P&L.
3. Monthly aggregation to detect concentration in a small number of periods.
4. Walk-forward split: development period followed by untouched test period.
5. Slippage sensitivity at 0%, 0.10%, 0.25%, 0.50% and 1.00% of premium.
6. Trigger threshold sensitivity at 1%, 1.5%, 2%, 2.5%, 3%, 4% and 5%.
7. Trigger denominator sensitivity: buy-premium, spot-notional and configured-capital.
8. ATM versus ATM−400/ATM+400 selection frequencies and separate P&L.
9. Exclusion sensitivity for missing/sparse quotes and lot-transition weeks.

## Statistical caution

Trades are time-series observations, not independent identically distributed draws. Bootstrap results are descriptive and will be supplemented by block/bootstrap-by-week sensitivity. No statistical significance claim will be made from a naive iid test alone.

## Validation gate

A strategy configuration is considered research-positive only if net P&L remains positive after conservative costs in the untouched test period and is not driven by a small number of observations. This is a methodology gate, not a recommendation to trade.

## Regime analysis

Phase 5 will condition results on realized volatility, VIX/India VIX where available, trend, gap size, option IV/skew, FII/DII flow, USD/INR, global equity futures and major corporate/news-event windows where data can be matched without look-ahead.