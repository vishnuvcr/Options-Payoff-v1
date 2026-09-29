# Phase 10A — Execution-quality / cost-to-edge analysis

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question

Does a predeclared execution-quality gate remove trades whose static chart edge is too small relative to realistic six-order friction?

## Frozen-control source

This phase uses the accepted Phase 9G exact-17-strike H1 ledger: 131 complete realized trades, one per weekly cycle. The superseded 169-trade Phase 9D ledger is explicitly not used.

## Gate definition

At the frozen Phase 9G selected entry, reject the trade when the point-in-time estimated six-order friction divided by the positive static flatline exceeds the gate. The test does not choose another strike and does not search a later timestamp.

The proxy uses only entry-observable premiums and lot size. Future far-leg exit premiums are proxied by their entry premiums with the same 0.25% slippage. It includes six-order brokerage, turnover-based exchange/SEBI charges, entry/exit stamp duty and entry/exit-sale STT at the entry-date rate. Exercise/settlement STT is excluded because it is not entry-observable.

Predeclared gates: no gate, <=25%, <=50%, <=75%.

## Control reproduction
- Complete realized trades: 131
- Weekly cycles: 131
- Gross P&L: ₹100,816.81
- Modeled costs: ₹28,948.05
- Net P&L: ₹71,868.76
- Static chart-positive rate: 100.0%

## Gate results

| variant       |   gate_ratio |   trade_count |   skipped_cycles |   net_pnl_inr |   mean_pnl_inr |   median_pnl_inr |   win_rate_pct |   wilson_low_pct |   wilson_high_pct |   profit_factor |   max_drawdown_inr |   mean_cost_inr |   total_costs_inr |
|:--------------|-------------:|--------------:|-----------------:|--------------:|---------------:|-----------------:|---------------:|-----------------:|------------------:|----------------:|-------------------:|----------------:|------------------:|
| control       |       nan    |           131 |                0 |       71868.8 |        548.616 |          352.694 |        58.7786 |          50.2166 |           66.8405 |         2.28525 |          -15704.2  |         220.977 |          28948.1  |
| cost_le_25pct |         0.25 |            14 |              117 |       14645.3 |       1046.09  |         1272.91  |        64.2857 |          38.7644 |           83.6553 |         4.38899 |           -3043.35 |         217.975 |           3051.66 |
| cost_le_50pct |         0.5  |            35 |               96 |       37725.3 |       1077.87  |         1022.71  |        71.4286 |          54.9451 |           83.6735 |         5.48476 |           -3043.35 |         220.242 |           7708.47 |
| cost_le_75pct |         0.75 |            62 |               69 |       48864.8 |        788.142 |          871.454 |        64.5161 |          52.0811 |           75.2573 |         3.32043 |           -7687.89 |         221.268 |          13718.6  |

## Paired inference

| variant       |   paired_cycles |   mean_difference_inr |   median_difference_inr |   net_difference_inr |   block_bootstrap_low_inr |   block_bootstrap_high_inr |   paired_permutation_p |     bh_q |
|:--------------|----------------:|----------------------:|------------------------:|---------------------:|--------------------------:|---------------------------:|-----------------------:|---------:|
| cost_le_25pct |             131 |              -436.82  |                -118.074 |             -57223.5 |                  -745.37  |                   -93.8448 |             0.00669967 | 0.020099 |
| cost_le_50pct |             131 |              -260.637 |                   0     |             -34143.5 |                  -537.577 |                    38.6292 |             0.0778961  | 0.116844 |
| cost_le_75pct |             131 |              -175.603 |                   0     |             -23004   |                  -420.515 |                    85.3898 |             0.188041   | 0.188041 |

## Decision

No execution-quality gate met the full predeclared promotion evidence in this phase. The frozen Phase 9G H1 control is retained.

## Limitations

- The cached source contains option closes rather than point-in-time bid/ask quotes, so this is an execution-friction proxy rather than a true executable-spread model.
- The exit-price proxy is intentionally explicit and is used only to construct an entry-time cost ratio; it is not treated as a forecast of realized exit prices.
- The gate is a trade/no-trade filter at the frozen selected entry; it does not test alternate-strike substitution or later same-day re-entry.

## Interpretation

This phase tests whether the static chart edge is large enough relative to entry-time friction. It does not establish that a lower cost-to-flatline ratio predicts favorable far-expiry revaluation.
