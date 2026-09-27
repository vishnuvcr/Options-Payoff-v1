# Phase 7B — Weekly positive-only maximum-flatline rule

## Final strategy rule

- One trade per weekly expiry cycle.
- Evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point increments.
- No 2.5% threshold.
- No margin-based percentage filter.
- A candidate qualifies only when the payoff chart shows a positive/all-green flatline.
- Select the strike with the maximum positive estimated equal max-profit=max-loss flatline value.
- Primary no-look-ahead timing used for the historical reconstruction: scan 09:20 observations through the weekly cycle and trade at the first observation where at least one positive candidate exists.

## Final historical result

The cached research sample contains 63 distinct near-expiry weekly cycles. The primary rule found at least one positive candidate in every cycle and therefore produced one trade in every cycle.

| Metric | Result |
|---|---:|
| Weekly cycles | 63 |
| Trades | 63 |
| Positive weeks | 63 |
| Skipped weeks | 0 |
| Net P&L | ₹-9,627.90 |
| Gross P&L | ₹233.25 |
| Modeled costs | ₹9,861.15 |
| Win rate | 57.14% |
| Profit factor | 0.98 |
| Max drawdown | ₹-174,083.24 |
| Largest win | ₹34,652.56 |
| Largest loss | ₹-55,786.13 |

Every selected payoff-chart flatline was positive. Nevertheless, the realized cross-expiry economics offset the positive static chart component.

### Economic decomposition

`static flatline contribution = +₹20,213.00`

`realized cross-expiry S2-S1 contribution = -₹19,979.75`

`gross P&L = +₹233.25`

`modeled costs = -₹9,861.15`

`net P&L = -₹9,627.90`

Thus, the positive green payoff chart did not translate into a positive realized return under this historical weekly implementation.

## Statistical uncertainty

IID bootstrap 95% CI for mean weekly trade P&L: ₹-4,996 to ₹4,410.

Four-week block bootstrap 95% CI: ₹-4,024 to ₹4,739.

The interval includes zero; the 63-week result does not establish a stable positive expectancy.

## Timing sensitivities

- First available observation of each cycle: 38 trades, ₹-32,986.60 net. The positive-only condition is not available at the first observation in every cycle.
- Last available observation: 41 trades, ₹177,070.15 net. It does not satisfy the user's no-skip-every-week rule because 22 cycles have no positive candidate at that late observation.
- Best-positive-in-week oracle: 63 trades, ₹3,135.05 net. This uses future observations within each cycle and is therefore an ex-post sensitivity, not a deployable trading rule.

The primary first-positive rule is the only tested implementation that simultaneously preserves no look-ahead, positivity, and one trade in every historical weekly cycle in this dataset.

## Important correction to earlier results

The earlier 2.5%-margin result of four trades is superseded. The user explicitly removed the 2.5% rule, so it is no longer part of the strategy.

The earlier 48-trade Phase 7 result also remains superseded because it used the old buy-premium percentage proxy.

## Limitations

The historical option execution is still based on the repository's 09:20 close-proxy execution model plus 0.25% premium slippage and ₹20 brokerage/order. Live deployment would require actual bid/ask execution and broker-specific charges on the execution date.

The primary timing rule — first positive opportunity within the weekly cycle — is an operationalization of the user's weekly/no-skip instruction. A different fixed weekly entry time would change the result and is therefore retained as a documented sensitivity rather than silently substituted.

## Reproducibility

GitHub Actions run: 36290510390.

Artifact: 10922191628.

Primary ledger artifact file: `weekly_selected_first_positive.csv`.