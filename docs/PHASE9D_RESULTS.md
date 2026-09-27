# Phase 9D — Corrected Intraday H1 Results

## Scope

This phase corrects the earlier 09:20-only entry cadence. The operational rule is:

1. For each weekly expiry cycle, begin checking at 09:20 IST.
2. Check every available NIFTY 1-minute observation through 15:29 IST.
3. If no positive/all-green flatline exists at 09:20, continue later the same day.
4. Continue on subsequent trading days in the same weekly cycle until the first positive observation.
5. At that first positive timestamp, evaluate all 17 common strikes from ATM-400 through ATM+400 in 50-point steps.
6. Select the strike with the maximum positive estimated equal Max Profit = Max Loss.
7. Exit all four legs at the near weekly expiry: near CE/PE settle; far CE/PE are manually squared off using their last available option bar at or before the near-expiry index close.
8. Apply 0.25% premium slippage and ₹20 brokerage per executed order in the primary scenario.

There is **no 2.5% threshold and no 09:20 skip rule**.

## Data and audit coverage

The six historical year chunks completed successfully on GitHub Actions. The merged ledger contains:

- 172 selected weekly-cycle entries.
- 448,280 intraday timestamps checked.
- 17,606 decision-surface rows at selected decision timestamps.
- 100% of selected static chart flatlines positive.
- 3 selected entries could not be converted into realized P&L because near/far expiry lot sizes were incompatible: 2021-07-26, 2024-04-25 and 2024-11-11.
- Therefore 169 selected trades have complete realized-P&L inputs.

The three incomplete selections are retained in the audit and are **not silently substituted with settlement/intrinsic prices**.

## Primary realized H1 result

At 0.25% premium slippage and ₹20/order brokerage:

| Metric | Result |
|---|---:|
| Selected weekly entries | 172 |
| Complete realized trades | 169 |
| Incomplete selections | 3 |
| Static chart-positive rate | 100.00% |
| Realized win rate | 63.91% |
| Gross P&L | ₹162,953.84 |
| Modeled costs | ₹37,265.02 |
| Net P&L | **₹125,688.82** |
| Mean net P&L / realized trade | ₹743.72 |
| Median net P&L / realized trade | ₹538.17 |
| Profit factor | 2.94 |
| Maximum drawdown | ₹16,200.65 |
| Largest win | ₹5,825.60 |
| Largest loss | ₹10,052.11 |

Modeled costs consume approximately 22.87% of gross P&L.

A deterministic 20,000-resample bootstrap of mean realized weekly-trade P&L produced an IID 95% interval of approximately **₹442–₹1,039**. A four-trade block bootstrap produced approximately **₹444–₹1,069**. These intervals describe this historical sample; they are not a guarantee of future performance.

## Execution sensitivity

With brokerage fixed at ₹20/order:

| Premium slippage | Net P&L |
|---:|---:|
| 0.00% | ₹155,747.51 |
| 0.25% | **₹125,688.82** |
| 0.50% | ₹95,630.14 |
| 1.00% | ₹35,512.76 |

With slippage fixed at 0.25%:

| Brokerage/order | Net P&L |
|---:|---:|
| ₹10 | ₹137,654.02 |
| ₹20 | **₹125,688.82** |
| ₹40 | ₹101,758.42 |

## Interpretation

The corrected intraday cadence changes the empirical result materially relative to the superseded 09:20-only studies. The static chart condition is satisfied at every selected entry by construction, but the realized result is determined by the mixed-expiry economics and execution costs.

The historical sample is economically positive under the primary modeled execution assumptions and remains positive in the tested 1% slippage and ₹40/order brokerage scenarios. This is evidence for continuing validation, **not sufficient by itself to establish a deployable trading edge**.

The next scientific step is independent validation of this corrected H1 rule (walk-forward/holdout, regime analysis, and robustness checks). H2/H3 far-expiry selection research remains frozen until that validation is completed.

## Reproducibility

Authoritative final H1 GitHub Actions run: **36302077730**.

Primary evidence is stored in the Actions artifact `phase-9D-final-H1-evidence`, including the merged intraday selection ledger, scan audit, decision surfaces, primary trade ledger, incomplete-selection audit and execution-sensitivity results.

