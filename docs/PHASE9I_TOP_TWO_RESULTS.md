# Phase 9I — Two-lot / top-two-strike analysis

## Research question

At each accepted Phase 9G H1 entry timestamp, what happens if the strategy enters two separate one-lot H1 positions: the two distinct strikes with the largest estimated equal Max Profit=Max Loss flatline values across ATM-400..ATM+400?

## Experimental control

The accepted Phase 9G H1 decision set is held fixed at 131 realized trades. This prevents Phase 9I from changing the entry-scan logic while testing only the additional strike/position.

The four-leg structure, near-expiry exit, 0.25% premium slippage, ₹20/order brokerage and modeled Indian option taxes/fees are unchanged.

## Reproducibility gate

The Phase 9I rank-1 selection reproduces the accepted Phase 9G ledger exactly:

- 131/131 entry timestamps matched.
- 131/131 selected strikes matched.
- Maximum absolute P&L difference: ₹0.0000000000032.

Therefore the two-lot comparison is an isolated sizing/selection experiment, not a reimplementation of the baseline.

## Primary literal interpretation: two lots every accepted week

Rank both distinct strikes across all 17 candidates by estimated flatline value and trade rank 1 and rank 2.

| Metric | One-lot control | Two-lot | Change |
|---|---:|---:|---:|
| Positions | 131 | 262 | +131 |
| Net P&L | ₹71,868.76 | ₹87,362.19 | +₹15,493.43 |
| Win rate | 58.78% | 56.11% | -2.67 pp |
| Profit factor | 2.29 | 1.65 | -0.63 |
| Max drawdown | -₹15,704.24 | -₹36,888.35 | -₹21,184.12 |
| Mean P&L / position | ₹548.62 | ₹333.44 | -₹215.17 |
| Median P&L / position | ₹352.69 | ₹168.61 | -₹184.09 |

The second position contributed **₹15,493.43** net P&L, with 131 additional trades, mean ₹118.27 and win rate 53.44%. Its profit factor was 1.20.

The additional position increased modeled costs by approximately **₹28,497.27** and generated approximately **₹43,990.70** gross P&L.

## Important rule distinction: all-green second strike

The frozen strategy requires a positive/all-green static flatline. If that requirement is retained for rank 2, only 67 of the 131 weeks have a second positive candidate.

For those 67 additional trades, the second-strike net P&L was **-₹11,450.33**. The remaining 64 weeks have a negative rank-2 static flatline; those 64 trades generated **+₹26,943.77** net in the historical sample.

Thus the positive-rank-2 and literal-top-two variants are materially different strategies.

## Bootstrap uncertainty

For the literal two-lot variant, the IID bootstrap 95% interval for mean P&L per position was ₹95.79 to ₹559.45.

For the incremental second-strike position, the IID bootstrap 95% interval for mean P&L per added position was **-₹212.70 to ₹438.82**, which includes zero.

For combined weekly P&L, the IID bootstrap 95% interval for mean weekly P&L was **₹13.12 to ₹1,307.35**.

These intervals are exploratory because the sample is a historical, temporally dependent sequence rather than iid observations.

## Interpretation

The historical sample does not show that adding a second strike creates a uniformly stronger risk-adjusted strategy.

It does show that, under the literal top-two-every-week rule, the second position added positive aggregate P&L in this sample. However:

1. drawdown more than doubled in magnitude;
2. profit factor fell from 2.29 to 1.65;
3. win rate fell;
4. the incremental second-strike mean has a bootstrap interval crossing zero;
5. much of the incremental aggregate result came from rank-2 candidates whose static flatline was negative, which is outside the original all-green signal condition.

Therefore Phase 9I should **not** silently replace the frozen strategy. The literal top-two-every-week rule is a separate candidate strategy requiring prospective/out-of-sample validation before adoption.

## Conclusion

The two-lot experiment changes the economics substantially. In this historical control sample, selecting the top two distinct strikes every accepted week increased net P&L from ₹71,868.76 to ₹87,362.19, but also increased maximum drawdown from ₹15,704.24 to ₹36,888.35 and reduced profit factor from 2.29 to 1.65.

The evidence is therefore mixed rather than a simple improvement. The second-strike position has positive aggregate historical P&L under the literal top-two rule, but its standalone uncertainty includes zero and the result partly depends on trading rank-2 candidates that do not satisfy the original positive/all-green flatline condition.

**No change to the frozen production/research control is adopted from Phase 9I.**
