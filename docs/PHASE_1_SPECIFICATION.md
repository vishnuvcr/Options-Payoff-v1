# Phase 1 — Strategy specification

## Position definition

At entry time t0:

### Near weekly expiry T1
- Sell 1 ATM call: -C1(K,T1)
- Buy 1 ATM put: +P1(K,T1)

This pair is a synthetic short forward with expiry payoff:

K - S(T1)

### Next weekly expiry T2
- Buy 1 ATM call: +C2(K,T2)
- Sell 1 ATM put: -P2(K,T2)

This pair is a synthetic long forward with expiry payoff:

S(T2) - K

### Combined expiry result

With a common strike K, the option intrinsic payoffs combine to:

S(T2) - S(T1)

The initial premium cashflow is:

C1 - P1 - C2 + P2

Therefore the gross terminal P&L per underlying unit is:

P&L = C1 - P1 - C2 + P2 + S(T2) - S(T1)

before brokerage, statutory charges, exchange charges, slippage and financing/margin effects.

## Why the original flatline chart can be misleading

If a chart applies one hypothetical terminal spot S to both expiries, the intrinsic payoff becomes:

(K - S) + (S - K) = 0

so the whole line is horizontal at the initial net premium cashflow.

That is a mathematical property of the *wrong one-expiry projection*. It does not mean the actual two-expiry position has a flat payoff.

The research engine therefore keeps two separate settlement variables:

- S1 = settlement underlying at T1
- S2 = settlement underlying at T2

and uses S2 - S1 in the expiry payoff.

## Strike-selection rule

The default candidates are:

1. ATM strike = nearest listed strike to spot at entry.
2. ATM - 400 points.
3. ATM + 400 points.

The research engine tests the user's preference order: ATM first, then the +/-400 alternatives only when the ATM candidate fails the trigger.

The 400-point adjustment is applied to the common strike, not independently to each leg.

## Trigger

The user-defined trigger is a positive flatline payoff greater than 2.5%.

The denominator for the percentage is **not specified by the user**, so Phase 1 deliberately does not hard-code a hidden denominator. Phase 3 will report the trigger under multiple explicit denominators, including margin/capital-based and premium-based measures where the data supports them.

## Entry-time assumption

To make the backtest deterministic, the default research observation point is 09:20 IST. Entry time will be sensitivity-tested in Phase 4.

This is a backtesting convention, not a recommendation that trades be entered at this time.

## Execution model

Phase 3 will support:

- buy at ask / sell at bid as a conservative base case;
- midpoint execution as a separate sensitivity case;
- explicit spread/slippage shock;
- four separate executed orders unless the broker's basket-order pricing can be evidenced;
- expiry settlement using exchange settlement data;
- all applicable brokerage, STT, SEBI, exchange, stamp-duty and GST components.

## Primary outcome variables

- net P&L per trade
- net return on declared capital/margin
- win/loss rate
- expectancy
- profit factor
- max drawdown
- tail loss statistics
- turnover and cost drag
- performance by candidate strike choice
- performance by signal/no-signal group

## Analytical falsification tests

The Phase 1 implementation specifically checks that:

1. the naive chart is flat under the common-strike/same-terminal-spot construction;
2. the actual cross-expiry P&L changes when S1 and S2 change;
3. a flat chart is not interpreted as a guaranteed profit;
4. strike selection is deterministic.

## Phase 1 conclusion

The strategy is best described as a **cross-expiry synthetic-forward spread**, not as a risk-free flat-profit position. The research question is therefore empirical: whether the observed entry premium/carry relationship is sufficiently favorable to compensate for the risk that the next-week settlement differs from the near-week settlement, after realistic costs.
