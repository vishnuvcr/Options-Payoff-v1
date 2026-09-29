# Phase 10B — Signal persistence confirmation

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question

Does requiring a positive exact-17-strike surface to persist for 5, 10, 15 or 30 minutes improve the frozen Phase 9G H1 strategy?

## Operational definition

The scan continues through every available intraday timestamp. At each exact-17 positive surface, the system looks exactly N minutes ahead on the same trading day. If that future surface is also exact-17 and positive, entry occurs at the confirmation timestamp and the normal maximum-positive-flatline strike selector is applied there. If confirmation fails, scanning continues to the next exact-17 positive timestamp.

This preserves the no-skip rule while adding only a predeclared confirmation delay.

## Frozen control
- 131 complete Phase 9G H1 trades
- Control net P&L: ₹71,868.76

## Results

| variant   |   trades |   weekly_cycles |   net_pnl_inr |   mean_pnl_inr |   median_pnl_inr |   win_rate_pct |   profit_factor |   max_drawdown_inr |   total_costs_inr |
|:----------|---------:|----------------:|--------------:|---------------:|-----------------:|---------------:|----------------:|-------------------:|------------------:|
| control   |      131 |             131 |     71868.8   |      548.616   |         352.694  |        58.7786 |        2.28525  |           -15704.2 |          28948.1  |
| 5m        |       57 |              57 |     -1964.26  |      -34.4607  |        -113.942  |        47.3684 |        0.940251 |           -14156.1 |          12462.3  |
| 10m       |       49 |              49 |      -145.326 |       -2.96584 |        -143.729  |        46.9388 |        0.994911 |           -13356.3 |          10609.7  |
| 15m       |       45 |              45 |      4006.76  |       89.0392  |         -51.2844 |        48.8889 |        1.15977  |           -11616.3 |           9628.57 |
| 30m       |       38 |              38 |      -646.71  |      -17.0187  |         -50.0843 |        50      |        0.971218 |           -12402.2 |           8378.42 |

## Paired inference

| variant   |   paired_cycles |   confirmed_cycles |   mean_difference_inr |   median_difference_inr |   net_difference_inr |   block_bootstrap_low_inr |   block_bootstrap_high_inr |   paired_permutation_p |       bh_q |
|:----------|----------------:|-------------------:|----------------------:|------------------------:|---------------------:|--------------------------:|---------------------------:|-----------------------:|-----------:|
| 5m        |             131 |                 57 |              -563.611 |                -158.654 |             -73833   |                  -821.381 |                   -288.792 |            0.000149993 | 0.00019999 |
| 10m       |             131 |                 49 |              -549.726 |                -178.564 |             -72014.1 |                  -807.877 |                   -286.42  |            0.000149993 | 0.00019999 |
| 15m       |             131 |                 45 |              -518.031 |                -116.317 |             -67862   |                  -771.907 |                   -258.27  |            0.000149993 | 0.00019999 |
| 30m       |             131 |                 38 |              -553.553 |                -285.538 |             -72515.5 |                  -825.972 |                   -267.201 |            0.00019999  | 0.00019999 |

## Decision

No confirmation delay met the full predeclared promotion evidence. The frozen Phase 9G H1 control is retained.

## Limitations

- Historical option observations are close-price proxies, not executable bid/ask quotes.
- Confirmation is evaluated only at exact minute timestamps represented in the source index/option data; missing confirmation observations do not count as confirmation.
- The test requires exact 17 unique strikes at both the initial positive observation and confirmation observation.
