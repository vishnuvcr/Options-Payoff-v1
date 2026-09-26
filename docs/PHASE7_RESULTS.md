# Phase 7 results — maximum estimated max-profit=max-loss selection

**Date:** 2026-09-27  
**Primary implementation:** 0.25% premium slippage per leg, ₹20 brokerage per executed order, historical lot sizes, 09:20 IST option close proxy, settlement/expiry exit.

## Selection rule

For every entry timestamp:

1. Evaluate every common strike from ATM-400 through ATM+400 in 50-point steps, including ATM.
2. Calculate the one-dimensional static flatline value:
`C1 - P1 - C2 + P2` per index point.
3. Apply the requested 2.5% eligibility gate. Because the exact historical platform margin denominator is unavailable, the current backtest uses the repository's legacy buy-premium denominator as an explicit proxy.
4. Among candidates passing the gate, select the single strike with the largest estimated equal max-profit=max-loss **value in INR**.

## Platform interpretation

Sensibull publicly documents the displayed max-profit/max-loss percentage as maximum profit or maximum loss divided by margin required. Therefore the legacy buy-premium percentage cannot be treated as an exact Sensibull reproduction. The value-based Phase 7 rule is the primary reproducible interpretation until historical margin can be reconstructed.

Streak currently advertises option payoff graphs and option-chain/ATM/ITM/OTM functionality, but the public material reviewed does not publish an equivalent percentage formula.

## Primary empirical result

| Metric | Result |
|---|---:|
| Grid candidates | 13,824 complete rows |
| Entry timestamps in grid | 905 |
| Timestamps with proxy >2.5% | 48 |
| Selected trades | 48 |
| Net P&L | ₹166,866.51 |
| Mean trade P&L | ₹3,476.39 |
| Median trade P&L | ₹6,242.51 |
| Win rate | 60.42% |
| Profit factor | 1.56 |
| Max drawdown | -₹124,060.72 |
| Largest loss | -₹55,321.89 |
| Largest win | ₹35,233.55 |
| Modeled costs | ₹7,334.77 |

## What drives the P&L?

The static flatline component contributed only **₹36,138.75** across the 48 selected trades.

The realized cross-expiry settlement component contributed **₹142,545.00**:

`S2 - S1` = next-expiry settlement minus near-expiry settlement, multiplied by lot size.

After 0.25% entry slippage, gross P&L before modeled statutory/broker fees was ₹174,201.28. The difference between static chart value plus realized `S2-S1` and this gross result is execution slippage.

This confirms the central economic caveat: the green flatline is not the dominant source of realized P&L for the held two-expiry position.

## Loss audit

- 19 of 48 trades lost money.
- Losing contribution: **-₹299,970.18**.
- 19/19 losers were already negative before modeled fees.
- Fee-only flips: **0**.
- Loss-side `S2-S1` contribution: **-₹309,305.00**.
- Loss-side static chart contribution: **+₹13,681.25**.

Thus the loss mechanism is the cross-expiry settlement movement, not brokerage.

## Robustness

95% iid bootstrap CI for mean trade P&L: **-₹1,943.61 to ₹8,927.91**.

95% weekly block-bootstrap CI: **-₹3,672.56 to ₹9,932.60**.

Chronological 70/30 split:

- train: 33 trades, **+₹18,711.33**
- test: 15 trades, **+₹148,155.17**

These intervals include zero and the test-period contribution is highly concentrated, so the historical point estimate is not sufficient to establish a robust edge.

## Slippage sensitivity

| Slippage | Net P&L |
|---:|---:|
| 0% | ₹171,346.72 |
| 0.25% | ₹166,866.51 |
| 0.50% | ₹162,386.29 |
| 1.00% | ₹153,425.87 |

## Selection-rule sensitivity

Removing the 2.5% gate and selecting the maximum positive flatline at every timestamp produced 146 trades, ₹116,595.80 net P&L, 56.85% win rate and a -₹379,090.18 maximum drawdown.

Selecting by the maximum legacy proxy percentage instead of maximum INR flatline selected the same strike on 31/48 timestamps and different strikes on 17/48. Its net P&L was ₹166,211.41.

That difference matters: the exact platform margin denominator could change which strike is selected.

## Regime attribution

The strongest descriptive regime was medium realized-volatility (21 trades, mean net P&L ₹11,658.63, profit factor 4.27). High-volatility trades were negative on average (9 trades, mean -₹7,806.15, profit factor 0.48). Down-trend observations were also positive on average (25 trades, mean ₹7,760.37). These are exploratory subgroup descriptions, not independent confirmation.

## Conclusion

The requested exhaustive-strike strategy is now implemented and empirically evaluated on the cached historical candidate set. Under the explicit proxy-based 2.5% gate and maximum estimated flatline-value selection, the historical point estimate is positive after modeled costs and slippage.

However, the statistical intervals include zero, the result is concentrated in particular periods/regimes, and the static payoff chart does not represent the true two-expiry economic risk. The realized `S2-S1` component dominates the selected-trade P&L.

The exact Sensibull-style 2.5% denominator remains the principal unresolved specification item. The next research step should therefore be historical margin reconstruction or direct chart replication before treating the percentage-based selector as exact.