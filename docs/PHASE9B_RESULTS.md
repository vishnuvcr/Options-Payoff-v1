# Phase 9B — Corrected H1 statistical validation

Authoritative validation run: **36297884737**.

## Primary corrected H1

| Metric | Result |
|---|---:|
| Trades | 64 |
| Weekly cycles scanned | 252 |
| Net P&L | ₹12,317.86 |
| Gross P&L | ₹25,859.55 |
| Modeled costs | ₹13,541.69 |
| Win rate | 51.56% |
| Profit factor | 1.47 |
| Max drawdown | -₹6,363.84 |
| Largest win | ₹5,254.08 |
| Largest loss | -₹3,702.34 |
| Trade-level Sharpe-like | 1.03 |
| Trade-level Sortino-like | 0.23 |
| Mean t-statistic | 1.03 |

## Uncertainty and stability

- IID bootstrap 95% CI for mean trade P&L: **-₹164.65 to +₹556.90**.
- Weekly-block bootstrap 95% CI: **-₹119.65 to +₹538.84**.
- Chronological 70/30: **₹11,280.49** in the first 44 trades and **₹1,037.36** in the last 20 trades.

## Loss audit

- 31 net losing trades.
- 27/31 were already negative before modeled costs.
- 4/31 were cost-only flips.
- Loss-side modeled costs: ₹6,765.03.
- No missing exit timestamps.
- No far-leg exit occurs after the near-expiry close.

## Execution sensitivity

| Scenario | Net P&L | Win rate |
|---|---:|---:|
| 0 bp slippage | ₹22,653.28 | 56.25% |
| 25 bp slippage | ₹12,317.86 | 51.56% |
| 50 bp slippage | ₹1,982.44 | 45.31% |
| 100 bp slippage | -₹18,688.40 | 34.38% |
| ₹10/order brokerage | ₹16,849.06 | 53.13% |
| ₹20/order brokerage | ₹12,317.86 | 51.56% |
| ₹40/order brokerage | ₹3,255.46 | 45.31% |

## Interpretation

The corrected H1 result is positive at the primary modeled cost assumption, but uncertainty around mean trade P&L includes zero and the result deteriorates sharply with wider execution friction. The evidence therefore does not justify treating the corrected H1 rule as a validated standalone trading edge.

## Research gate

H2/H3 remains a predeclared horizon experiment only. It must use exactly the same entry/selection/cost/near-expiry exit convention, with only the far-expiry horizon changed.
