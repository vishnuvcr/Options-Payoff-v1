# Payoff formula audit — corrected exit convention

Date: 2026-09-27

## 1. Strategy legs

For common strike K:
- Near expiry: short call, long put
- Far expiry: long call, short put

Entry cashflow per unit = C1 - P1 - Cf + Pf

## 2. One-dimensional static chart

The repository static chart applies one hypothetical terminal spot S to all four legs, even though the expiries differ.

Near pair intrinsic = K-S
Far pair intrinsic = S-K

Therefore they cancel and the chart is:

Static chart P&L = C1 - P1 - Cf + Pf

This remains a valid description of the platform-style same-terminal-spot chart metric.

## 3. Actual user exit convention

The user has now explicitly clarified that all four legs are closed at the near weekly expiry. The near-expiry options settle there. The far-expiry options are manually squared off at the near-expiry close.

Let QC(T1) be the executable sale price of the far-expiry call at T1, and QP(T1) be the executable repurchase price of the far-expiry put at T1.

The near short-call + long-put pair has payoff:

K - S1

The far long-call + short-put pair is closed for:

QC(T1) - QP(T1)

Therefore the correct gross per-unit P&L is:

P&L(T1) = C1 - P1 - Cf + Pf + (K-S1) + QC(T1) - QP(T1)

This is not equal to C1 - P1 - Cf + Pf + Sfar-S1 unless the far options are actually held to the far expiry. The previous backtest made that latter assumption.

## 4. Research validity correction

The previous Phase 7B/7C/8A realized-P&L results were calculated with far-expiry settlement values and therefore modeled a different holding period. They are superseded for the user's actual strategy.

The entry-time flatline/strike-selection calculation remains valid as an entry-chart metric, but realized P&L must be rebuilt using point-in-time far-option exit prices at the near-expiry close.

## 5. Required corrected data

A corrected historical backtest requires, for every selected candidate:
- near-expiry settlement/close;
- far-expiry call price at the near-expiry exit timestamp;
- far-expiry put price at the near-expiry exit timestamp;
- exact exit timestamp convention;
- exit slippage and transaction costs.

Far-expiry settlement is not a valid substitute.
