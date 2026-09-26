# Phase 5 — Regime and cross-market attribution

## Purpose

Phase 5 is a pre-registered attribution layer. It does not create a new trading rule before Phase 4 validation is complete. Its purpose is to test whether any Phase 4 performance is concentrated in observable market regimes and whether the apparent edge survives conditioning.

## Required inputs

1. Phase 3 selected-trade ledger with entry timestamp, strike choice, chart-trigger denominator, gross/net P&L and cost fields.
2. NIFTY spot/index return series.
3. India VIX historical series where available.
4. Option IV level and term-structure fields, preferably from quote/surface data rather than inferred from future observations.
5. Option OI and volume/liquidity measures.
6. FII/FPI and DII participant activity.
7. USD/INR reference/market series.
8. Gold benchmark.
9. Global equity/futures benchmark(s).
10. Corporate/news-event calendar only where timestamps and source provenance are auditable.

NSE publishes historical derivatives reports including daily settlement prices, contract-wise price/volume data, participant-wise open interest/trading volumes and FII derivatives statistics. NSE also publishes historical India VIX data. These sources are preferred for exchange-derived regime variables. RBI documentation records the USD/INR reference-rate methodology and notes that dissemination moved to FBIL in July 2018; the research pipeline must preserve the source actually used for each date.

## Point-in-time rule

Every regime variable must be known at or before the 09:20 IST entry observation. End-of-day values from the entry date are prohibited unless the variable is explicitly available before entry.

For weekly trades, the regime observation is frozen at entry. No later revision is permitted.

## Predeclared regime variables

| Variable | Primary transformation | Regime construction |
|---|---|---|
| Realized volatility | trailing 5D and 20D annualized volatility | low / middle / high terciles from development sample |
| India VIX | entry-day/latest available value | low / middle / high terciles |
| Gap | open-to-prior-close % | negative / neutral / positive; magnitude sensitivity |
| Trend | 20D and 60D return | down / flat / up |
| Liquidity | option volume/OI and quote availability | sparse / normal / liquid |
| IV level | ATM IV when available | low / middle / high terciles |
| IV term structure | next-minus-near IV | negative / flat / positive |
| FII/DII | latest available flow/position measure | signed bins; lagged to avoid look-ahead |
| USD/INR | 5D return | appreciation / neutral / depreciation |
| Gold | 5D return | negative / neutral / positive |
| Global equity | prior-session benchmark return | negative / neutral / positive |
| Event window | predeclared event calendar | event / non-event |

Tercile cut points are estimated using the development segment only and then frozen for the test segment.

## Statistical analysis

For each regime report number of trades, mean/median/standard deviation of net P&L, win rate, profit factor where defined, maximum drawdown within the regime sequence, bootstrap or block-bootstrap confidence interval, and fraction of total net P&L attributable to the regime.

Primary interaction model:

    net_pnl_t = alpha + beta_regime * regime_t + beta_controls * controls_t + epsilon_t

Use heteroskedasticity/autocorrelation-robust inference where appropriate. Because the number of trades may be small, regression results are secondary to descriptive stratification.

Multiple regime splits are exploratory. No regime is promoted to a new trading rule solely because it has the highest observed mean.

## Structural attribution tests

1. Signal versus unconditional benchmark: compare triggered trades with all eligible ATM trades under identical cost assumptions.
2. ATM versus fallback: report ATM and -400/+400 separately; do not pool them if selection probabilities differ materially.
3. Cross-expiry move attribution: decompose gross P&L into entry premium edge, S2 minus S1, and transaction costs.
4. Cost attribution: show brokerage, exchange charges, SEBI fee, stamp duty, GST, STT and slippage separately.
5. Execution-quality sensitivity: compare close-proxy results with conservative spread/slippage scenarios.
6. Data-quality exclusion sensitivity: rerun after excluding sparse or questionable quotes.
7. Calendar concentration: identify whether results depend on a small number of expiry weeks, crisis windows or contract-transition periods.

## Acceptance criteria

Phase 5 does not declare a strategy successful. It can only provide attribution evidence.

A regime finding is considered reproducible only when the regime variable is point-in-time valid, its construction is fixed before test evaluation, the observation count is reported, the effect persists under predefined cost/slippage sensitivity, the result is not explained solely by one or two trades, and confirmatory versus exploratory analyses are explicit.

## Data availability limitation

The Phase 2 primary public dataset contains bar OHLCV/OI rather than historical bid/ask quotes. Therefore quote-level liquidity and IV analyses must be marked unavailable or use a separately validated quote source. The regime workflow must never manufacture a bid/ask spread from OHLC data and label it as observed.

## Exit criterion

Phase 5 is complete only after Phase 4 has produced a valid trade ledger. Until then this branch contains the frozen attribution protocol and executable analysis scaffold, not empirical regime conclusions.