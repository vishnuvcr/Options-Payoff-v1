# Phase 10A — Execution-quality / cost-to-edge analysis

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question

Does a predeclared execution-quality gate remove trades whose static chart edge is too small relative to realistic six-order friction?

## Gate definition

At the frozen Phase 9G H1 selected entry, reject the trade when the point-in-time estimated six-order friction divided by the positive static flatline exceeds the gate. The test does not choose another strike and does not search a later timestamp.

The proxy uses only entry-observable premiums and lot size. Future far-leg exit premiums are proxied by their entry premiums with the same 0.25% slippage. It includes six-order brokerage, turnover-based exchange/SEBI charges, entry/exit stamp duty and entry/exit-sale STT at the entry-date rate. Exercise/settlement STT is excluded because it is not entry-observable.

Predeclared gates: no gate, <=25%, <=50%, <=75%.

## Control reproduction
- Authoritative realized rows: 169
- Selected decision-surface rows: 172
- Matched realized rows: 169
- Selected rows without complete realized ledger: 3
- Authoritative control net P&L: ₹125,688.82

## Gate results

| variant       |   gate_ratio |   trade_count |   skipped_cycles |   net_pnl_inr |   mean_pnl_inr |   median_pnl_inr |   win_rate_pct |   wilson_low_pct |   wilson_high_pct |   profit_factor |   max_drawdown_inr |   mean_cost_inr |   total_costs_inr |
|:--------------|-------------:|--------------:|-----------------:|--------------:|---------------:|-----------------:|---------------:|-----------------:|------------------:|----------------:|-------------------:|----------------:|------------------:|
| control       |       nan    |           169 |                0 |      125689   |        743.721 |          538.173 |        63.9053 |          56.4296 |           70.763  |         2.9413  |          -16200.6  |         220.503 |          37265    |
| cost_le_25pct |         0.25 |            16 |              153 |       37323.8 |       2332.74  |         2623.56  |        87.5    |          63.9772 |           96.5023 |        31.3972  |           -1227.87 |         221.844 |           3549.5  |
| cost_le_50pct |         0.5  |            39 |              130 |       77625.3 |       1990.39  |         1989.63  |        87.1795 |          73.2943 |           94.3972 |        26.7694  |           -1238.37 |         224.841 |           8768.79 |
| cost_le_75pct |         0.75 |            60 |              109 |       84784.2 |       1413.07  |         1237.34  |        76.6667 |          64.5637 |           85.5604 |         6.62725 |           -4223.06 |         223.995 |          13439.7  |

## Paired inference

| variant       |   paired_cycles |   mean_difference_inr |   median_difference_inr |   net_difference_inr |   block_bootstrap_low_inr |   block_bootstrap_high_inr |   paired_permutation_p |       bh_q |
|:--------------|----------------:|----------------------:|------------------------:|---------------------:|--------------------------:|---------------------------:|-----------------------:|-----------:|
| cost_le_25pct |             169 |              -522.87  |                -130.586 |             -88365   |                  -824.455 |                 -228.63    |            0.000349983 | 0.00104995 |
| cost_le_50pct |             169 |              -284.4   |                   0     |             -48063.6 |                  -578.134 |                    8.56799 |            0.0270986   | 0.040648   |
| cost_le_75pct |             169 |              -242.039 |                   0     |             -40904.6 |                  -499.245 |                    7.69    |            0.040948    | 0.040948   |

## Decision

No execution-quality gate met the full predeclared promotion evidence in this phase. The frozen Phase 9G H1 control is retained.

## Limitations

- The cached source contains option closes rather than point-in-time bid/ask quotes, so this is an execution-friction proxy rather than a true executable-spread model.
- The exit-price proxy is intentionally conservative/explicit and is used only to construct an entry-time cost ratio; it is not treated as a forecast of realized exit prices.
- Three of the 172 selected Phase 9D cycles were incomplete for realized P&L because of lot-size incompatibility; they remain in the selection surface but are excluded from realized control metrics, matching the authoritative H1 convention.

## Interpretation

This phase tests whether the static chart edge is large enough relative to entry-time friction. It does not establish that a lower cost-to-flatline ratio predicts favorable far-expiry revaluation, and it does not change the frozen strike/timing rule unless a later chronological holdout supports the refinement.
