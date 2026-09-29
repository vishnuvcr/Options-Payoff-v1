# Phase 10D — Exit timing refinement

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question
Does closing the entire four-leg position before near expiry improve realized economics relative to the authoritative frozen Phase 9G exit convention?

## Predeclared candidates
- control: frozen Phase 9G near-expiry settlement/manual far-leg exit;
- 60, 120, 180 minutes before near-expiry close;
- previous trading-day close.

Early exits close all four legs using 0.25% premium slippage and ₹20/order. No exercise STT is charged for early exits.

## Results

| variant   |   trades |   net_pnl_inr |   mean_pnl_inr |   median_pnl_inr |   win_rate_pct |   profit_factor |   max_drawdown_inr |   total_costs_inr |   p10_pnl_inr |   worst_trade_inr |
|:----------|---------:|--------------:|---------------:|-----------------:|---------------:|----------------:|-------------------:|------------------:|--------------:|------------------:|
| baseline  |      130 |       60790.6 |        467.62  |          232.849 |        57.6923 |         2.03357 |          -16267.5  |           29619.7 |     -1263.21  |         -10191.6  |
| 60m       |      131 |       69612.2 |        531.391 |          445.448 |        72.5191 |         3.25566 |           -7085.14 |           29880.6 |     -1002.96  |          -5492.65 |
| 120m      |      131 |       93192   |        711.389 |          680.867 |        74.8092 |         5.89438 |           -4624.64 |           29882.1 |      -597.579 |          -1970.54 |
| 180m      |      131 |      104337   |        796.465 |          704.112 |        74.0458 |         8.40861 |           -3460.61 |           29955.2 |      -391.165 |          -1343.97 |
| 1d        |      128 |       97673   |        763.07  |          603.873 |        79.6875 |         8.29741 |           -2518.44 |           29495.5 |      -308.608 |          -2043.83 |

## Paired inference versus baseline

| variant   |   paired_cycles |   mean_difference_inr |   median_difference_inr |   net_difference_inr |   block_bootstrap_low_inr |   block_bootstrap_high_inr |   paired_permutation_p |     bh_q |
|:----------|----------------:|----------------------:|------------------------:|---------------------:|--------------------------:|---------------------------:|-----------------------:|---------:|
| 60m       |             131 |              -17.2259 |                -37.2941 |             -2256.59 |                 -240.105  |                    240.968 |               0.888906 | 0.888906 |
| 120m      |             131 |              162.773  |                 89.8869 |             21323.2  |                  -99.0367 |                    476.129 |               0.266837 | 0.355782 |
| 180m      |             131 |              247.849  |                 70.1355 |             32468.2  |                  -56.3007 |                    633.884 |               0.129294 | 0.355782 |
| 1d        |             128 |              225.237  |                 70.8761 |             28830.4  |                 -131.498  |                    671.223 |               0.238538 | 0.355782 |

## Decision

No exit-timing candidate met the full predeclared promotion screen. The frozen Phase 9G exit convention is retained.

## Limitations
- Historical closes are execution proxies, not bid/ask fills.
- The 1-day candidate is defined as the last available index bar on the previous trading day.
- Unavailable option observations are excluded from paired inference rather than synthetically filled.
