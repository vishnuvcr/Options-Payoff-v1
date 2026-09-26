# Payoff-platform semantics review

**Date:** 2026-09-27  
**Purpose:** Determine what the public documentation shows about Streak and Sensibull payoff charts and the max-profit/max-loss percentage relevant to the user's strategy.

## 1. Streak

Streak's current public product material says its options module includes payoff graphs, option-chain integration, and underlying/time-based option strategies. The platform's risk disclosure also warns that payoff graphs are hypothetical and may not represent actual outcomes.

A public Streak example shows standard limited-risk spread arithmetic: the maximum profit is the net premium credit, while the maximum loss is the spread width less that credit. This is ordinary expiry payoff math.

However, the public Streak material reviewed here does **not** publish a formula for a percentage attached to max profit/max loss. Therefore this research does not claim that Streak uses Sensibull's percentage denominator.

## 2. Sensibull

Sensibull's public Strategy Builder documentation states that the payoff graph is accompanied by max profit, max loss, breakeven, margin, and other risk metrics. Sensibull's July 2022 feature note explicitly defines the displayed percentage as:

`Max Profit % = Max Profit / Margin needed * 100`

and, analogously,

`Max Loss % = Max Loss / Margin needed * 100`.

Sensibull also states that max profit/max loss are expiry-day quantities, while the target-day payoff is a separate projected P&L calculation.

The platform later added a payoff table that shows P&L on both the target day and expiry day.

## 3. Important mixed-expiry caveat

The user's position has two different expiries. Sensibull discussions of calendar spreads state that max-profit/max-loss estimates for calendar spreads can be materially wrong in extreme events because the unexpired option can change value with implied volatility.

Therefore, a software payoff chart for this strategy should be treated as an **estimated chart metric**, not as proof of the true worst-case economic P&L of holding the position through two different expiry dates.

This matches the research engine's separate calculation:

`Economic P&L = C1 - P1 - C2 + P2 + (S2 - S1) - costs`

while the one-dimensional flat chart is:

`Static chart P&L = C1 - P1 - C2 + P2`.

## 4. Interpretation of the user's 2.5%

The user's clarification is consistent with the **max-profit/max-loss percentage displayed by an options strategy builder**, rather than the repository's earlier `buy_premium` return denominator.

For Sensibull, the published denominator is **margin required**. The exact historical margin required for each NIFTY four-leg mixed-expiry position is not present in the current cached option-price dataset. It therefore must not be silently reconstructed as the old buy-premium denominator.

## 5. Phase 7 strategy implementation

The requested strategy change is implemented on `phase-7-max-equal-selection`:

1. Evaluate every common strike at ATM-400 through ATM+400 in 50-point increments, including ATM.
2. Compute the positive flatline value from the four observed entry premiums.
3. Treat the flatline's maximum and minimum chart P&L as the same estimated value.
4. Select exactly one candidate per entry timestamp: the candidate with the maximum estimated equal-max-profit=max-loss **value**.
5. Retain a separate 2.5% sensitivity using the repository's historical trigger denominator, explicitly labeled a proxy.
6. Do not describe that proxy as an exact Sensibull replication until historical margin requirements are reconstructed.

## 6. Research implication

The strategy-selection rule is now materially different from the superseded ATM-first/fallback logic. All downstream performance, validation, regime and manuscript results based on the old selection rule must be treated as historical comparators rather than evidence for the new rule.