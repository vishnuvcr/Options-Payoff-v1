# Phase 9I — Top-two-strike results

At the first valid exact-17-strike positive timestamp in each weekly cycle, the top two distinct positive flatline strikes were evaluated as separate four-leg H1 positions. The same 0.25% slippage, ₹20/order brokerage, statutory charges and near-expiry far-leg close convention were used.

## Reproducibility gate

Top-1 exactly reproduces the accepted Phase 9G H1 control: **True**; maximum absolute P&L difference ₹0.0000000000; strike selections match **True**.

## Key counts

Cycles with a positive signal: **131**. Cycles with two positive candidates: **67**. Cycles with only one positive candidate: **64**.

## Metrics

| strategy                   |   trades |   net_pnl_inr |   win_rate_pct |   profit_factor |   max_drawdown_inr |
|:---------------------------|---------:|--------------:|---------------:|----------------:|-------------------:|
| Top-1 control              |      131 |       71868.8 |        58.7786 |         2.28525 |           -15704.2 |
| Top-2 trade-level          |      198 |       60418.4 |        56.0606 |         1.6072  |           -31812.5 |
| Top-2 combined cycle-level |      131 |       60418.4 |        57.2519 |         1.61602 |           -31812.5 |

## Interpretation

The absolute rupee P&L of the two-strike variant is not sufficient evidence of improvement because it deploys additional capital and incurs additional four-leg entry plus two-leg exit economics for the second position. The incremental second-strike series and cycle-level combined results are therefore reported separately.
