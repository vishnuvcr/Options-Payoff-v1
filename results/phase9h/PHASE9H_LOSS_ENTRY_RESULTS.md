# Phase 9H — Loss-trade entry analysis

Analyzed 54 realized H1 loss cycles from the frozen Phase 9G rule.

The tests are loss-level diagnostics only: same-timestamp strike substitution, next valid timestamp, fixed 15/30/60/120-minute delays, unchanged-selector later entry, and an ex-post later-entry/strike upper bound. No exit rule was changed. No ex-post variant is a deployable strategy.

## Rescue summary

| variant                      |   loss_cycles |   rescued_to_positive |   rescue_rate_pct |   sum_variant_pnl_inr |   sum_baseline_loss_pnl_inr |   mean_delta_inr |   median_delta_inr |
|:-----------------------------|--------------:|----------------------:|------------------:|----------------------:|----------------------------:|-----------------:|-------------------:|
| same_timestamp_any_candidate |            54 |                     6 |           11.1111 |             -45527.8  |                    -55918.1 |          192.413 |            66.2669 |
| second_valid_timestamp       |            52 |                     8 |           15.3846 |             -44196.4  |                    -55136.4 |          210.384 |           118.551  |
| delay_15m                    |            46 |                     8 |           17.3913 |             -39667.6  |                    -50721.8 |          240.31  |           118.551  |
| delay_30m                    |            40 |                     7 |           17.5    |             -39220.7  |                    -46341.3 |          178.014 |            82.7213 |
| delay_60m                    |            37 |                     6 |           16.2162 |             -37425.4  |                    -45345.2 |          214.048 |           276.204  |
| delay_120m                   |            35 |                     4 |           11.4286 |             -31301.4  |                    -44028.7 |          363.637 |            94.7069 |
| best_later_frozen_selector   |            52 |                    31 |           59.6154 |               5257.29 |                    -55136.4 |         1161.42  |           824.591  |
| best_later_any_candidate     |            52 |                    38 |           73.0769 |              13355.4  |                    -55136.4 |         1317.15  |           951.213  |

## Interpretation

A rescue means the same historical trade becomes positive under the stated entry counterfactual. This does not establish that the counterfactual is predictable ex ante. Any rule suggested by these diagnostics requires a separate full-sample prospective test and an untouched holdout before adoption.
