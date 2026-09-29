# Phase 10C — Scenario-aware strike selection

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question

Can the frozen 17-strike selector be improved by ranking positive/all-green candidates using a fixed, point-in-time scenario grid for the full near-expiry position rather than the static same-spot flatline alone?

## Frozen scenario grid

- Near-expiry spot shock: -2%, -1%, 0%, +1%, +2%.
- Far-leg IV shock: -5, 0, +5 volatility points.
- Total scenarios per candidate: 15.
- Far CE/PE values at the near-expiry horizon use Black–Scholes with r=0 and q=0.
- IVs are inverted only from entry-time observed premiums.
- Entry slippage: 0.2500%; brokerage: ₹20.00/order.
- Only positive/all-green static-flatline candidates are eligible.
- Tie-break: scenario score, then static flatline, then shift from ATM.

## Control reproduction

- Complete frozen Phase 9G trades: 131
- Control net P&L: ₹71,868.76

## Results

| variant   |   trades |   weekly_cycles |   net_pnl_inr |   mean_pnl_inr |   median_pnl_inr |   win_rate_pct |   win_ci_low_pct |   win_ci_high_pct |   profit_factor |   max_drawdown_inr |   total_costs_inr |
|:----------|---------:|----------------:|--------------:|---------------:|-----------------:|---------------:|-----------------:|------------------:|----------------:|-------------------:|------------------:|
| control   |      131 |             131 |       71868.8 |        548.616 |          352.694 |        58.7786 |          50.2166 |           66.8405 |         2.28525 |           -15704.2 |           28948.1 |
| median    |      129 |             129 |       64184.7 |        497.556 |          206.69  |        58.9147 |          50.2866 |           67.0273 |         2.11579 |           -16782.4 |           28214.1 |
| p10       |      129 |             129 |       64687   |        501.45  |          240.926 |        58.1395 |          49.5117 |           66.2966 |         2.15316 |           -16027.2 |           27828   |
| worst     |      129 |             129 |       64811.1 |        502.412 |          240.926 |        58.1395 |          49.5117 |           66.2966 |         2.15582 |           -15442.5 |           27773.1 |

## Paired inference versus the frozen control

| variant   |   paired_cycles |   covered_cycles |   unavailable_cycles |   mean_difference_inr |   median_difference_inr |   net_difference_inr |   block_bootstrap_low_inr |   block_bootstrap_high_inr |   paired_permutation_p |      bh_q |
|:----------|----------------:|-----------------:|---------------------:|----------------------:|------------------------:|---------------------:|--------------------------:|---------------------------:|-----------------------:|----------:|
| median    |             129 |              129 |                    0 |              -46.2783 |                       0 |             -5969.91 |                  -88.8134 |                   -4.15117 |              0.0301985 | 0.0438978 |
| p10       |             129 |              129 |                    0 |              -42.3841 |                       0 |             -5467.55 |                  -88.2548 |                   -2.28346 |              0.0422979 | 0.0438978 |
| worst     |             129 |              129 |                    0 |              -41.4222 |                       0 |             -5343.46 |                  -86.7318 |                   -2.39376 |              0.0438978 | 0.0438978 |

## Decision

No scenario selector met the full predeclared promotion screen. The frozen Phase 9G H1 control is retained.

## Interpretation

Scenario-aware ranking is evaluated on the complete weekly decision population and does not use realized P&L, future spot, or future option prices to choose the strike. Its only future-horizon element is a fixed theoretical revaluation horizon and fixed stress grid declared before scoring.

## Limitations

- Historical option observations are close-price proxies, not executable bid/ask quotes.
- Black–Scholes IV is a model-based reconstruction rather than an exchange-published IV surface.
- Some candidates may lack a valid IV inversion; such cycles are reported as unavailable rather than filled synthetically.
- The scenario score is a research selector, not a guarantee of realized profit.
