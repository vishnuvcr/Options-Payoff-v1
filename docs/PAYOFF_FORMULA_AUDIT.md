# Payoff formula audit

Date: 2026-09-27
Authoritative code: phase-3-strike-grid / phase-6-loss-audit

## 1. Strategy legs

For common strike K:
- Near expiry: short call, long put
- Next expiry: long call, short put

Using C1, P1, C2, P2 for entry premiums:

Entry cashflow per unit = C1 - P1 - C2 + P2

## 2. One-dimensional static chart

The repository static chart applies one hypothetical terminal spot S to all four legs.

Near expiry = -max(S-K,0) + max(K-S,0) = K-S.
Next expiry = +max(S-K,0) - max(K-S,0) = S-K.

Therefore the intrinsic terms cancel:

(K-S) + (S-K) = 0.

So the static chart is:

Static chart P&L = C1 - P1 - C2 + P2

Verdict: YES. This algebra is correct for a one-dimensional chart that deliberately assigns the same hypothetical terminal spot to both expiries. The repository unit test checks that the chart is flat across terminal spot.

## 3. Actual two-expiry economic P&L

The actual position has two different settlement dates.

Near expiry = K - S1
Next expiry = S2 - K

Therefore the expiry component is:

(K-S1) + (S2-K) = S2-S1.

Gross per-unit terminal P&L = C1 - P1 - C2 + P2 + S2 - S1

Verdict: YES. This is the economically correct two-expiry P&L formula used by the research, excluding fees and execution costs.

## 4. What the corrected backtest uses

The full-grid backtest uses the entry cashflow C1 - P1 - C2 + P2 as the chart trigger. That is algebraically identical to the static one-dimensional chart because the common-spot intrinsic terms cancel.

The realized trade P&L then adds S2-S1 and subtracts modeled execution/statutory costs.

Thus the implementation separates:
1. static chart edge;
2. cross-expiry settlement movement;
3. transaction/execution costs.

That separation is correct.

## 5. Critical unresolved issue: the 2.5% denominator

The payoff numerator is well defined by the algebra above.

The current research uses a working denominator of:

near put premium + next call premium

so chart % = (C1 - P1 - C2 + P2) / (P1 + C2) × 100.

This denominator was not explicitly established from the user's original strategy description. A charting application could instead express percentage against capital, margin, spot notional, net debit/credit, or another application-specific base.

Those definitions can materially change whether a trade qualifies. The tested spot-notional denominator generated no qualifying trades from 1% through 5%.

## 6. Final conclusion

The intrinsic-value and premium-cashflow formula is not the error.

The correct conclusion is:

- The static flatline formula is mathematically correct for the artificial same-terminal-spot chart.
- The cross-expiry S2-S1 formula is mathematically correct for the actual held position.
- The unresolved item is the exact definition of the displayed 2.5% percentage denominator.
- Therefore the current positive backtest should be treated as conditional on that denominator assumption until the original chart interface is matched exactly.