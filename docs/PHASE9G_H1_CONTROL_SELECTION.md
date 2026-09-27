# Phase 9G — H1 control selection behaviour

Source: authoritative Phase 9D H1 artifact from workflow run **36302077730**. This is a control-description result only; it does not select H2/H3.

## Selection-strike distribution

| Shift (points) | Trades | Share |
|---:|---:|---:|
| -400 | 35 | 20.71% |
| -350 | 28 | 16.57% |
| -300 | 18 | 10.65% |
| -250 | 12 | 7.10% |
| -200 | 5 | 2.96% |
| -150 | 1 | 0.59% |
| -100 | 7 | 4.14% |
| -50 | 4 | 2.37% |
| 0 | 1 | 0.59% |
| +50 | 2 | 1.18% |
| +150 | 3 | 1.78% |
| +200 | 4 | 2.37% |
| +250 | 3 | 1.78% |
| +300 | 12 | 7.10% |
| +350 | 15 | 8.88% |
| +400 | 19 | 11.24% |

The control selected **ATM only once out of 169 complete realized trades**. Thus the present rule is materially different from an ATM-only implementation and from a simple ±400 fallback rule.

## First-positive decision timing

Among 169 complete realized H1 trades, the first qualifying time was:

| Window from 09:20 | Trades |
|---|---:|
| 09:20 exactly | 39 |
| 09:21–09:25 | 20 |
| 09:26–09:35 | 15 |
| 09:36–09:50 | 16 |
| 09:51–10:20 | 9 |
| 10:21–11:20 | 12 |
| 11:21–13:20 | 18 |
| 13:21–15:29 | 40 |

Mean delay from 09:20 was **106.08 minutes**; median **25 minutes**; P90 **340.2 minutes**; maximum **369 minutes**. This is direct evidence that 09:20 must remain the first observation rather than a trade/no-trade gate.

These statistics will be compared with H2/H3 after their fixed-horizon reconstructions complete.

## H1 annual control reference

| Year | Complete trades | Net P&L (₹) | Mean/trade (₹) | Win rate | Profit factor |
|---:|---:|---:|---:|---:|---:|
| 2021 | 28 | 12,833.78 | 458.35 | 53.57% | 2.63 |
| 2022 | 46 | 15,283.53 | 332.25 | 60.87% | 1.73 |
| 2023 | 34 | 48,635.63 | 1,430.46 | 79.41% | 14.19 |
| 2024 | 30 | 26,613.84 | 887.13 | 66.67% | 4.49 |
| 2025 | 17 | 1,708.07 | 100.47 | 35.29% | 1.08 |
| 2026 | 14 | 20,613.98 | 1,472.43 | 85.71% | 9.76 |

At the primary cost assumption (0.25% premium slippage and ₹20/order), the authoritative H1 result is **169 complete trades, ₹125,688.82 net P&L, 63.91% realized win rate and PF 2.94**. The same selected trades remained net-positive at ₹10 and ₹40 brokerage and at 0%, 0.5% and 1.0% premium slippage in the authoritative sensitivity artifact. These are historical robustness checks, not out-of-sample guarantees.

The 2025 cohort is a useful stress-period within the observed sample: profitability was positive but close to break-even after costs. This supports the Phase 9G requirement to compare H2/H3 year-by-year rather than relying on aggregate P&L alone.
