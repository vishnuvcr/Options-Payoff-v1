# Loss-trade audit — corrected 63-row grid backtest

Source: authoritative Phase 3 run 36262958536, artifact phase-3-backtest-results; loss audit workflow 36264710663.

## Reconciliation

| Metric | Result |
|---|---:|
| Selected rows | 63 |
| Winners | 38 |
| Losers | 25 |
| Total net P&L | ₹168,665.95 |
| Winning contribution | ₹623,001.39 |
| Losing contribution | -₹454,335.44 |
| Largest loss | -₹55,420.58 |
| Mean loss | -₹18,173.42 |
| Median loss | -₹9,563.35 |
| Costs on losing trades | ₹3,557.82 |
| Losses negative before fees | 25 / 25 |
| Fee-only losses | 0 / 25 |
| ATM losses | 7 |
| Fallback losses | 18 |

## Core finding

Every losing trade passed the >2.5% chart trigger under the working buy-premium denominator. All 25 losers were already negative before statutory and brokerage fees. The dominant failure mode is therefore the cross-expiry economic outcome, not transaction costs.

Across the 25 losers, entry-chart P&L summed to +₹19,661.25, slippage-adjusted gross economic P&L summed to -₹450,777.62, and final net P&L was -₹454,335.44. Costs were only about 0.79% of gross losses.

## Every losing trade

| Rank | Date | Shift | Strike | Spot | Chart % | Chart P&L | Gross P&L | Costs | Net P&L | Near | Next |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 2022-06-07 | +300 | 16750 | 16446.70 | 3.45% | ₹710.00 | -₹55,269.71 | ₹150.87 | -₹55,420.58 | 2022-06-09 | 2022-06-16 |
| 2 | 2022-06-07 | -200 | 16250 | 16446.70 | 4.28% | ₹775.00 | -₹55,192.54 | ₹129.35 | -₹55,321.89 | 2022-06-09 | 2022-06-16 |
| 3 | 2022-06-06 | -450 | 16100 | 16555.05 | 3.82% | ₹1,062.50 | -₹54,954.36 | ₹147.92 | -₹55,102.28 | 2022-06-09 | 2022-06-16 |
| 4 | 2022-02-17 | +300 | 17750 | 17438.00 | 8.17% | ₹1,545.00 | -₹51,385.96 | ₹159.78 | -₹51,545.74 | 2022-02-17 | 2022-02-24 |
| 5 | 2023-10-17 | ATM | 19800 | 19822.05 | 3.40% | ₹327.50 | -₹38,093.92 | ₹123.79 | -₹38,217.71 | 2023-10-19 | 2023-10-26 |
| 6 | 2022-01-13 | -400 | 17850 | 18237.65 | 2.74% | ₹565.00 | -₹24,579.62 | ₹133.77 | -₹24,713.39 | 2022-01-13 | 2022-01-20 |
| 7 | 2021-10-19 | +100 | 18650 | 18569.05 | 2.79% | ₹372.50 | -₹15,737.57 | ₹149.32 | -₹15,886.89 | 2021-10-21 | 2021-10-28 |
| 8 | 2021-10-19 | -400 | 18150 | 18569.05 | 3.39% | ₹770.00 | -₹15,388.05 | ₹137.95 | -₹15,526.00 | 2021-10-21 | 2021-10-28 |
| 9 | 2022-02-08 | +150 | 17450 | 17278.10 | 3.02% | ₹532.50 | -₹14,619.37 | ₹128.05 | -₹14,747.42 | 2022-02-10 | 2022-02-17 |
| 10 | 2021-12-06 | -450 | 16700 | 17166.75 | 2.68% | ₹770.00 | -₹12,797.84 | ₹183.36 | -₹12,981.20 | 2021-12-09 | 2021-12-16 |
| 11 | 2021-09-21 | -500 | 16900 | 17413.05 | 2.81% | ₹830.00 | -₹9,559.71 | ₹195.63 | -₹9,755.34 | 2021-09-23 | 2021-09-30 |
| 12 | 2021-09-21 | -350 | 17050 | 17413.05 | 3.98% | ₹927.50 | -₹9,431.34 | ₹174.77 | -₹9,606.11 | 2021-09-23 | 2021-09-30 |
| 13 | 2022-07-07 | ATM | 16100 | 16111.20 | 2.85% | ₹322.50 | -₹9,447.36 | ₹115.99 | -₹9,563.35 | 2022-07-07 | 2022-07-14 |
| 14 | 2022-07-06 | ATM | 15850 | 15873.55 | 2.91% | ₹397.50 | -₹9,384.31 | ₹126.03 | -₹9,510.34 | 2022-07-07 | 2022-07-14 |
| 15 | 2022-07-05 | -300 | 15650 | 15933.45 | 2.76% | ₹545.00 | -₹9,267.53 | ₹150.08 | -₹9,417.61 | 2022-07-07 | 2022-07-14 |
| 16 | 2021-10-14 | ATM | 18300 | 18279.35 | 2.87% | ₹257.50 | -₹7,810.52 | ₹111.53 | -₹7,922.05 | 2021-10-14 | 2021-10-21 |
| 17 | 2021-07-15 | +50 | 15950 | 15880.55 | 2.65% | ₹285.00 | -₹7,280.78 | ₹117.33 | -₹7,398.11 | 2021-07-15 | 2021-07-22 |
| 18 | 2022-06-02 | ATM | 16450 | 16463.75 | 2.80% | ₹340.00 | -₹7,216.63 | ₹119.35 | -₹7,335.97 | 2022-06-02 | 2022-06-09 |
| 19 | 2022-05-31 | -150 | 16450 | 16580.40 | 2.64% | ₹462.50 | -₹7,121.34 | ₹129.58 | -₹7,250.92 | 2022-06-02 | 2022-06-09 |
| 20 | 2021-07-13 | +200 | 15950 | 15763.90 | 2.86% | ₹483.75 | -₹7,113.42 | ₹129.16 | -₹7,242.58 | 2021-07-15 | 2021-07-22 |
| 21 | 2022-06-01 | ATM | 16650 | 16636.60 | 3.14% | ₹477.50 | -₹7,094.62 | ₹124.82 | -₹7,219.44 | 2022-06-02 | 2022-06-09 |
| 22 | 2022-05-30 | -100 | 16450 | 16551.15 | 2.87% | ₹512.50 | -₹7,073.04 | ₹130.24 | -₹7,203.28 | 2022-06-02 | 2022-06-09 |
| 23 | 2022-04-04 | +300 | 18150 | 17854.75 | 13.65% | ₹2,675.00 | -₹5,624.70 | ₹166.72 | -₹5,791.42 | 2022-04-07 | 2022-04-13 |
| 24 | 2024-01-17 | ATM | 21850 | 21830.05 | 3.05% | ₹425.00 | -₹5,128.21 | ₹145.26 | -₹5,273.48 | 2024-01-18 | 2024-01-25 |
| 25 | 2022-04-20 | -450 | 16650 | 17092.55 | 15.03% | ₹3,290.00 | -₹4,205.17 | ₹177.15 | -₹4,382.33 | 2022-04-21 | 2022-04-28 |

## Concentration

The largest 1, 2, 3, 4 and 10 losses contribute about 12.2%, 24.4%, 36.5%, 47.8% and 74.7% of total losing P&L.

The 2022-06-06 to 2022-06-07 sequence accounts for -₹165,844.75. The 2022-05-30 to 2022-06-07 cluster accounts for -₹194,854.37, approximately the reported maximum drawdown.

Multiple fallback losses can occur at the same entry timestamp: 2022-06-07 had +300 and -200 together for -₹110,742.47; 2021-10-19 had +100 and -400 together for -₹31,412.89; 2021-09-21 had -500 and -350 together for -₹19,361.45.

## Losses by shift

| Shift | Losses | Total loss |
|---:|---:|---:|
| +300 | 3 | -₹112,757.74 |
| ATM | 7 | -₹85,042.34 |
| -450 | 3 | -₹72,465.80 |
| -200 | 1 | -₹55,321.89 |
| -400 | 2 | -₹40,239.40 |
| +100 | 1 | -₹15,886.89 |
| +150 | 1 | -₹14,747.42 |
| -500 | 1 | -₹9,755.34 |
| -350 | 1 | -₹9,606.11 |
| -300 | 1 | -₹9,417.61 |
| +50 | 1 | -₹7,398.11 |
| -150 | 1 | -₹7,250.92 |
| +200 | 1 | -₹7,242.58 |
| -100 | 1 | -₹7,203.28 |

## Trigger-strength check

Losing chart-return values range from 2.64% to 15.03%. So the problem is not limited to marginal 2.5% qualifiers. Examples: 8.17% gave -₹51,545.74; 13.65% gave -₹5,791.42; 15.03% gave -₹4,382.33.

## Cost anatomy on losers

| Cost | Amount |
|---|---:|
| Brokerage | ₹2,000.00 |
| Exchange transaction | ₹327.05 |
| SEBI fee | ₹0.92 |
| Stamp duty | ₹13.55 |
| Entry STT | ₹468.93 |
| Exercise STT | ₹328.34 |
| GST | ₹419.04 |
| Total | ₹3,557.82 |

## Conclusion

The 25 losing rows are genuine economic losses under the implemented model, not cases where brokerage alone turned a profitable gross trade negative.

The central technical issue is that the flat chart trigger measures an entry-premium relationship, while the held position has a cross-expiry settlement term. The trigger can therefore be positive while the realized two-expiry position is strongly negative.

Next audit: decompose every selected trade into entry-chart edge + cross-expiry settlement movement + slippage + statutory/broker costs, and test whether a correctly normalized chart metric predicts the cross-expiry movement out of sample.

## Reproducibility note

The authoritative 63-row result came from Phase 3 grid run 36262958536 on branch phase-3-strike-grid. The stale copy of scripts/run_backtest.py on phase-6-manuscript-grid was corrected in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4. The manuscript branch is now synchronized to the full 50-point fallback-grid implementation.

## CRITICAL CORRECTION — loss ledger superseded

The loss audit inherits the old realized-P&L convention, where the far legs were valued at far-expiry settlement. Because the user's actual exit is manual closure of all four legs at near expiry, the winner/loser classification and loss decomposition are superseded. The corrected loss audit will be regenerated from the Phase 9A near-expiry-exit ledger.
