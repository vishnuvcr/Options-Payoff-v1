# Final Research Conclusion — Current State

## Strategy under final user specification

The current specification is:

1. Scan every weekly expiry cycle.
2. At the first available entry observation where a positive/all-green payoff candidate exists, evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point increments.
3. Select the strike with the maximum positive estimated equal max-profit=max-loss flatline.
4. Trade one candidate for that weekly cycle.
5. No 2.5% threshold, no margin percentage filter and no threshold-based skipping.

## Evidence accumulated

### Phase 7B — baseline weekly strategy

In the cached historical sample:

- 63 weekly cycles;
- 63 trades;
- 0 threshold-based skips;
- net P&L **₹-9,627.90**;
- win rate **57.14%**;
- profit factor approximately **0.98**;
- modeled costs **₹9,861.15**;
- maximum drawdown approximately **₹-174,083**.

The positive static chart contribution was approximately **₹20,213**, while the realized (S_2-S_1) contribution was approximately **₹-19,980** before costs.

### Phase 7C — Greeks and entry features

No tested single Greek, IV-term-structure, IV-skew or moneyness feature provided sufficient evidence to replace the maximum-positive-flatline selector.

### Phase 8A — S2-S1 predictability

The target (S_2-S_1) has:

- mean about **+4.77 index points**;
- standard deviation about **392.59 points**;
- positive outcome in **57.14%** of the 63 current weekly cycles.

An all-timestamp expanding walk-forward predictor used 905 prior entry timestamps across 255 weekly cycles for training, then evaluated 43 strictly OOS weekly decision cycles.

The best directional model, Histogram Gradient Boosting, achieved only **53.49%** sign accuracy and AUC about **0.541**. Random Forest achieved **51.16%** sign accuracy and AUC about **0.514**.

The Random Forest predicted-positive trade filter increased the same-test P&L from **₹-10,634.75** to **₹91,388.05**, but:

- the improvement reversed in the middle chronological block;
- paired bootstrap mean improvement was about **₹2,372.62/week**;
- 95% bootstrap interval was **₹-2,740.68 to ₹7,993.14**.

The evidence is therefore not stable enough to justify deployment.

## Scientific conclusion

The current evidence does **not** establish a reliable positive trading edge for the final positive-flatline weekly strategy.

The central finding is not that the green flatline is useless. It correctly identifies a useful static algebraic property of the position. The problem is that the actual economic result depends materially on the inter-expiry settlement movement (S_2-S_1), and that component has not proved predictably exploitable with the available entry information.

Likewise, the current dataset does not support adding a simple Greek or IV filter to repair the strategy.

## Trading-rule conclusion

No new entry filter is adopted.

The research therefore leaves the strategy in its current form rather than curve-fitting a rule to the historical sample.

## Future research

The next scientifically justified improvement would require a materially stronger information set rather than another arbitrary model search. Candidates include point-in-time futures basis, full option OI/volume/liquidity, India VIX and volatility term structure, global index futures, USD/INR, gold, FII/DII flows and news/event regime variables, together with substantially larger quote-level and independent out-of-sample data.

Any such extension must be predeclared, cached, strictly point-in-time, transaction-cost aware, and validated on an untouched period before it can change the strategy.

## Bottom line

**Do not treat the current strategy as a validated live trading strategy.**

The research has identified the key economic mechanism and tested both simple Greek-based and S2-S1-based improvements. Neither has yet produced sufficiently stable out-of-sample evidence to support deployment.
