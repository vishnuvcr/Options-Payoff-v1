# Current Strategy Specification — Frozen Phase 9G H1

**Version:** 1.0  
**Date:** 2026-09-27  
**Status:** Research-candidate / frozen control  
**Authoritative branch:** `phase-9H-loss-entry-analysis`  
**Frozen control:** Phase 9G corrected H1 reconstruction  
**Entry-change audit:** Phase 9H-A completed; no entry modification adopted

---

## 1. Strategy in one paragraph

For each NSE NIFTY weekly-expiry cycle, begin checking the option surface at **09:20 IST**, but do **not** treat 09:20 as a skip gate. Check every available 1-minute observation from 09:20 through 15:29 and continue on subsequent trading days in the same weekly cycle until the **first valid timestamp** at which the required 17-strike universe contains at least one **positive/all-green static flatline**. At that timestamp, evaluate **all 17 common strikes from ATM-400 through ATM+400 in 50-point steps**, select the strike with the **largest positive estimated equal Max Profit = Max Loss flatline value**, and enter the four-leg cross-expiry position at that common strike. The H1 control uses the **immediately next weekly expiry** as the far expiry. At the near weekly expiry, the near CE/PE settle and the far CE/PE are **manually squared off at observed market prices**; the far legs are not held to their own expiry.

There is **no 2.5% entry threshold, no margin-percentage gate, no ATM-first fallback ordering, no fixed waiting period, no Greek filter, no VIX/global-market filter, and no dynamic H1/H2/H3 switching** in the frozen rule.

---

## 2. Instruments and contract pairing

Underlying:
- NIFTY 50 index options.

For every weekly cycle:
- **Near expiry (T1):** the first upcoming NSE-defined weekly expiry used by the cycle.
- **Far expiry (T2):** the immediately following weekly expiry after T1.
- H1 means this fixed one-week separation between the near and far contracts.

The four legs use the **same strike K**:
1. Sell 1 lot of T1 Call (CE), strike K.
2. Buy 1 lot of T1 Put (PE), strike K.
3. Buy 1 lot of T2 Call (CE), strike K.
4. Sell 1 lot of T2 Put (PE), strike K.

Research backtests use historically applicable lot sizes. The selected near/far contracts must have compatible executable lot sizing. Do not replace a missing or incompatible leg with a synthetic settlement price.

---

## 3. Strike universe

At each candidate entry timestamp, determine the ATM strike and construct exactly these 17 shifts:

```
-400, -350, -300, -250, -200, -150, -100, -50,
0,
+50, +100, +150, +200, +250, +300, +350, +400
```

Thus:

```
K = ATM + shift
```

where the shift is in NIFTY index points.

### Critical selection rule

**All 17 strikes are evaluated at the same decision timestamp.**

There is no:
- ATM-first trade,
- fallback-to-±50 sequence,
- fallback-to-±400 sequence,
- hand-picked strike,
- strike selection based on future information.

The candidate with the highest positive flatline value wins.

---

## 4. Exact 17-strike completeness requirement

A timestamp is a valid decision observation only when the complete required surface can be evaluated.

For each of the 17 shifts:
- the near CE quote exists;
- the near PE quote exists;
- the far CE quote exists;
- the far PE quote exists;
- the strike identity is unique.

Duplicate raw quote rows are not counted as extra strikes. The research definition is **17 unique shift points**.

If duplicate records for the same contract/strike contain conflicting values, the timestamp is invalid for strategy execution.

If fewer than the required 17 unique shifts can be evaluated, the timestamp cannot trigger a trade even if a partial subset appears profitable.

This prevents a favorable result from a partial strike universe from creating a false signal.

---

## 5. Intraday scan schedule

For each weekly cycle:

### Step 1 — Start
Begin scanning at **09:20 IST** on the first eligible trading day.

### Step 2 — Check every available minute
Evaluate each available NIFTY observation from **09:20 through 15:29 IST**.

### Step 3 — Continue later the same day
If there is no positive valid candidate at 09:20, continue to later timestamps that day.

### Step 4 — Continue on later days
If the day ends without a qualifying timestamp, continue scanning subsequent trading days belonging to the same weekly cycle.

### Step 5 — Stop at the first qualifying timestamp
The **first valid timestamp** where at least one of the 17 candidates has a positive flatline is the decision timestamp.

Once a trade is entered:
- stop scanning that weekly cycle;
- do not enter a second candidate later in the same cycle.

### Step 6 — No qualifying timestamp
If no valid positive candidate occurs before the cycle's near-expiry exit window, the cycle has no trade.

---

## 6. Static payoff / flatline calculation

At a candidate strike K and entry time t, define the observed premiums:

- C1 = near-expiry CE premium, sold.
- P1 = near-expiry PE premium, bought.
- C2 = far-expiry CE premium, bought.
- P2 = far-expiry PE premium, sold.

The static chart flatline is:

```
F(K,t) = C1 - P1 - C2 + P2
```

Interpretation:
- C1 and P2 are premiums received.
- P1 and C2 are premiums paid.
- The four legs use the same strike K.

A qualifying candidate requires:

```
F(K,t) > 0
```

The platform-style static chart therefore shows a positive flatline. The research treats this as the **estimated equal Max Profit = Max Loss chart value**.

### Important distinction

The positive flatline is an **entry-time static chart metric**.

It is **not** the same thing as guaranteed realized trading profit because the far-expiry options remain alive after the near expiry and must be liquidated at their then-current market prices.

---

## 7. Exact strike-selection rule

At the first valid timestamp t:

1. Compute F(K,t) for every one of the 17 strikes.
2. Discard candidates where F(K,t) <= 0.
3. Among the remaining candidates, select:

```
K* = argmax_K F(K,t)
```

4. Enter only the selected K*.

Therefore the operative logic is:

> **First valid timestamp with any positive candidate -> evaluate all 17 strikes -> choose the largest positive flatline.**

There is no additional threshold.

---

## 8. Entry orders

For the selected strike K*:

### Near expiry T1
- Sell T1 CE, strike K*.
- Buy T1 PE, strike K*.

### Far expiry T2
- Buy T2 CE, strike K*.
- Sell T2 PE, strike K*.

The research position is one matched lot of the four contracts, subject to the historical contract lot-size rules.

The four-leg position should be treated operationally as one spread package. The research model does not give one leg permission to be omitted because another leg is difficult to fill.

---

## 9. Entry price / execution model

The historical research primary execution model uses:
- **0.25% premium slippage** on option-premium executions.
- **₹20 per executed order** as the primary brokerage assumption.
- Full transaction-cost accounting including the modeled STT, exchange charges, SEBI fee, stamp duty and GST applicable to each transaction.

The research framework also evaluates alternative brokerage and slippage scenarios.

The current research baseline should therefore be understood as:
- four entry-leg transactions;
- plus two far-leg exit transactions at near expiry;
- near-expiry CE/PE settle rather than requiring market exit orders.

This is a **six-transaction economic model** for the four-leg position.

---

## 10. Near-expiry exit rule

The most important corrected rule is the exit convention.

At the near weekly expiry T1:

### Near-expiry legs
- The short T1 CE settles according to the exchange's index-option settlement mechanism.
- The long T1 PE settles according to the exchange's index-option settlement mechanism.

### Far-expiry legs
The T2 options are **not** held to T2.

Instead:
- Sell the long T2 CE at its executable market price at/near the T1 close.
- Buy back the short T2 PE at its executable market price at/near the T1 close.

In the historical reconstruction, the far-leg exit quote is the observed available option bar at or before the near-expiry index close.

The four-leg position is therefore fully closed at T1.

---

## 11. Correct economic P&L

Let:
- S1 = NIFTY settlement at the near expiry;
- QC(T1) = executable sale price of the far-expiry CE at T1;
- QP(T1) = executable repurchase price of the far-expiry PE at T1.

Before transaction costs, the corrected economic P&L is:

```
P&L(T1)
= C1 - P1 - C2 + P2
  + (K - S1)
  + QC(T1) - QP(T1)
```

Then subtract all modeled execution and statutory costs.

The decomposition is useful:

```
static entry flatline
+ near-expiry settlement component
+ far-expiry manual-close component
- transaction costs
```

This is the correct H1 economics used by the accepted Phase 9G control.

---

## 12. What the strategy does NOT do

The frozen strategy does **not**:

- require Max Profit % > 2.5%;
- use margin percentage as a trade gate;
- use the old buy-premium denominator;
- trade only ATM;
- trade ATM first and then search fallbacks;
- wait a fixed 15/30/60/120 minutes;
- choose the best later timestamp with hindsight;
- use a future price to decide whether to enter;
- predict S2-S1 using a model;
- filter by reconstructed Greeks;
- filter by IV skew/term structure;
- filter by India VIX;
- filter by FII/DII;
- filter by global risk-on/risk-off;
- dynamically decide between H1, H2 and H3 after seeing conditions;
- hold the far options to their own expiry;
- substitute missing far-leg exit prices with far-expiry settlement.

Any of these would constitute a strategy change and requires a new prospective research phase.

---

## 13. How to handle a day with no qualifying signal

Example:

- 09:20: no positive full-17-strike flatline -> continue.
- 10:15: no positive full-17-strike flatline -> continue.
- 12:40: partial 12/17 strike surface has a positive candidate -> **invalid; continue**.
- 13:05: full 17/17 surface, but every F(K,t) <= 0 -> continue.
- 14:20: full 17/17 surface, one or more F(K,t) > 0 -> **enter now**, select maximum positive F.
- Stop scanning the weekly cycle after entry.

If the entire trading day has no qualifying observation:
- continue on the next eligible trading day in the same weekly cycle.

---

## 14. How to handle duplicate or bad data

Do not force a decision when:
- a required option leg is missing;
- a contract identity is ambiguous;
- the 17 shifts are not uniquely represented;
- conflicting duplicate prices exist;
- the near/far contracts cannot be matched to the intended expiries;
- the near/far lot-size relationship is incompatible.

The research principle is:

> **Invalid data produces no signal; it does not produce an invented favorable signal.**

---

## 15. Position management after entry

The frozen H1 rule has no discretionary intratrade re-selection.

After entry:
- do not replace the strike because another strike later has a larger flatline;
- do not reopen the position at a later timestamp;
- do not roll from H1 to H2/H3 dynamically;
- do not add a new stop-loss;
- do not add a profit target;
- do not close early based on P&L unless a separately tested exit rule is introduced.

The predefined exit is the near-expiry close of all four legs.

---

## 16. Strategy pseudocode

```
for each weekly cycle:

    define near expiry T1
    define next weekly expiry T2

    entered = False

    for each valid 1-minute timestamp t:
        if t < 09:20 or t > 15:29:
            continue

        build the complete 17-strike surface
        if not exactly 17 unique shifts:
            continue

        for shift in [-400,-350,...,0,...,+350,+400]:
            K = ATM + shift

            F[K] = near_CE
                   - near_PE
                   - far_CE
                   + far_PE

        eligible = all K where F[K] > 0

        if eligible is empty:
            continue

        K_star = strike with maximum F[K]

        enter:
            short T1 CE K_star
            long  T1 PE K_star
            long  T2 CE K_star
            short T2 PE K_star

        entered = True
        break

    if entered:
        at T1 near-expiry close:
            settle T1 CE/PE
            sell T2 CE at observed executable price
            buy back T2 PE at observed executable price
            record all costs

    else:
        record "no qualifying opportunity"
```

---

## 17. Research-status interpretation

The static selection condition is designed so that a selected trade has a positive chart flatline. Therefore the **selected static-chart positivity rate is 100% by construction**.

That does **not** mean realized P&L has a 100% win rate.

For the accepted Phase 9G H1 control:
- 131 complete realized trades;
- 54 realized losses;
- 77 realized wins;
- realized win rate 58.78%;
- net P&L ₹71,868.76 under the primary historical cost model;
- profit factor 2.29.

Phase 9H-A then tested whether those 54 losses were mainly an entry-timing/strike problem.

The bounded entry-counterfactual union rescued:
- **14/54 losses (25.9%)**.

The strongest hindsight upper bound—best later valid timestamp plus any strike—rescued:
- **38/54 losses (70.4%)**.

But even that hindsight upper bound left:
- **16/54 losses unrecovered**.

Therefore no entry modification was adopted.

---

## 18. Current research conclusion about this strategy

The current strategy is a **research candidate**, not a guaranteed-profit or 100%-win strategy.

The strongest supported statement is:

> The strategy identifies cross-expiry option combinations with a positive static flatline and then selects the largest such flatline at the first valid intraday opportunity, but realized profitability depends on the subsequent near-expiry settlement and the market value of the still-live far-expiry options.

The Phase 9G H1 result is the current control for further research. The Phase 9H-A loss-entry study did not justify changing the entry rule.

---

## 19. Non-negotiable implementation checklist

Before any live/paper-trading decision, verify all of the following:

- [ ] Correct near and next weekly expiries.
- [ ] Correct common strike K.
- [ ] All 17 shifts evaluated.
- [ ] Exactly 17 unique strike surfaces available.
- [ ] No conflicting duplicate quotes.
- [ ] 09:20 is only the first check.
- [ ] Scan continues minute-by-minute until the first valid positive timestamp.
- [ ] No 2.5% threshold applied.
- [ ] No ATM-first preference.
- [ ] Maximum positive flatline selected.
- [ ] Four legs entered at the same selected strike.
- [ ] Near expiry is the mandatory full-exit point.
- [ ] Far CE/PE are manually squared off at near expiry.
- [ ] No far-leg hold to its own expiry.
- [ ] Brokerage, slippage, STT and other applicable charges included.
- [ ] Actual broker execution prices are recorded.
- [ ] A complete trade ledger is retained.

---

## 20. Research governance note

This document is the frozen operational specification for the accepted Phase 9G H1 control. Phase 9H-A is diagnostic only and does not change the rule.

Any future change to:
- entry timing,
- strike selection,
- threshold,
- expiry horizon,
- exit timing,
- cost model,
- risk management,
- regime filter,
- prediction filter,

must be treated as a new prospective hypothesis and tested across the full population before adoption.
