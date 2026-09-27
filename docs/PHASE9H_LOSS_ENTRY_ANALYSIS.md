# Phase 9H-A — Loss-trade entry analysis

**Status:** COMPLETE  
**Branch:** `phase-9H-loss-entry-analysis`  
**Accepted workflow:** 36325328644  
**Accepted commit:** ec75cb20e8e23f0550f8d615e796eea815e3d161  
**Primary cost model:** 0.25% premium slippage, ₹20/order, six transactions  
**Frozen control:** Phase 9G exact-17-strike H1 rule

## 1. Research question

For the 54 realized H1 losses produced by the frozen Phase 9G rule, could changing only the entry strike or entry time have turned individual losses into positive realized trades while leaving the expiry horizon, exit convention, payoff construction and transaction-cost model unchanged?

## 2. Data and controls

The analysis reused the frozen Phase 9G realized-loss ledger and scan audit rather than redefining the strategy. Every candidate timestamp remained subject to the exact 17 unique shifts from ATM-400 through ATM+400 in 50-point increments, no conflicting duplicate quotes, and a positive static flatline.

The realized economics used the same near-expiry manual-close convention as Phase 9G:
- near-weekly short CE and long PE settle at the near index close;
- next-weekly long CE and short PE are manually closed using their observed near-expiry option quotes;
- identical slippage, brokerage, STT, stamp duty, exchange/SEBI charges and GST were applied.

A hard regression gate compared every Phase 9H baseline loss P&L with the frozen Phase 9G loss ledger. All six yearly jobs passed; maximum difference was below 1e-6 INR.

## 3. Loss population

There were **54 net losing trades out of 131 complete H1 trades**. Their combined baseline net P&L was **₹-55,918.13**.

Importantly, **45 of the 54 losses were already negative before modeled fees**, while **9 were non-negative gross but became net losses after transaction costs**. Therefore not every loss is an entry-selection problem.

## 4. Predeclared counterfactuals

### A. Same timestamp, different strike
At the original first-positive timestamp, replace the selected strike with the best realized candidate among all 17 shifts. This is an ex-post strike-selection upper bound.

**6/54 losses (11.1%)** were rescued. The loss-subset P&L improved from ₹-55,918.13 to ₹-45,527.80.

The rescued cases were concentrated in 2021–2023; none of the 2024–2026 losses were rescued by this same-timestamp counterfactual.

### B. Second valid exact-17 timestamp
Move to the next qualifying exact-17 timestamp and retain the normal maximum-positive-flatline selector.

**8/54 losses (14.8% of all losses; 8/52 when restricted to cycles with a second valid timestamp)** were rescued.

### C. Fixed delays
Waiting for the first qualifying exact-17 timestamp at or after a fixed delay produced:

| Delay | Rescued / 54 losses | Rescue rate over all losses |
|---|---:|---:|
| 15 min | 8 | 14.8% |
| 30 min | 7 | 13.0% |
| 60 min | 6 | 11.1% |
| 120 min | 4 | 7.4% |

The available-case rescue rates are higher because some loss cycles do not have a later qualifying timestamp after the specified delay. None of these fixed-delay tests eliminates the loss population.

### D. Best later timestamp, unchanged strike selector
Choose the **best later qualifying timestamp after the baseline entry**, but keep the frozen maximum-positive-flatline strike selector.

This rescued **31/54 losses (57.4%)** when counted over all original losses; 31/52 among cycles with a later realized candidate.

This is an **ex-post upper bound**, because the choice of the best later timestamp uses future realized P&L.

### E. Best later timestamp + any strike
Allow the strongest entry-only ex-post freedom: any later valid timestamp and any candidate strike.

This rescued **38/54 losses (70.4%)**; 38/52 among cycles with at least one later candidate.

Even this broad upper bound left **16 losses** unrecovered. Those unrecovered losses include several large drawdowns, including losses around ₹2,500–₹3,500.

## 5. Practical entry-change conclusion

Considering only the bounded, plausibly predeclared mechanisms — same-timestamp strike substitution plus the next valid timestamp and fixed 15/30/60/120-minute delays — the union rescued **14 of 54 losses (25.9%)**.

That means the majority, **40/54 losses**, were **not** converted to profit by those bounded entry changes.

The broader ex-post upper bound rescued 40/54 only when the same-timestamp strike alternative is combined with arbitrary later timestamp/strike freedom. That is not evidence of an implementable rule.

## 6. What the rescued losses have in common

The rescued cases do not point to one stable deterministic entry modification. The profitable counterfactual shifts vary substantially across trades, including negative and positive shifts, and the successful delay varies by case.

There is also temporal instability:
- same-timestamp strike rescues occurred in 2021–2023 but not 2024–2026;
- fixed-delay rescues were concentrated mainly in 2021–2023, with a few in 2025 and none in 2024/2026.

This makes a universal “always wait X minutes” or “always move to Y shift” interpretation unsupported by the loss audit alone.

## 7. The important upper-bound result

The strongest counterfactual is useful diagnostically because it answers an information-limit question:

> Even after granting hindsight to choose a later timestamp and any of the 17 strikes, 16 losses still could not be made positive.

Therefore the losing trades are not predominantly explained by a simple mistimed entry. A substantial component arises from the subsequent cross-expiry economics after entry.

## 8. Interpretation

The loss audit therefore does **not** identify a single entry modification capable of producing a 100% realized-win strategy.

It does identify a smaller set of losses that are sensitive to entry timing/strike. That is a hypothesis for prospective testing, not an accepted strategy change.

The fixed-delay variants improve individual losses in some cases, but their loss-subset aggregate remains materially negative. Same-timestamp alternative-strike selection also improves the loss subset but leaves it negative.

The only variants that make the loss subset positive are the explicitly ex-post later-entry selectors. Because they use future information, they cannot be used as trading rules.

## 9. Strengths

- Uses the exact current 17-strike universe and completeness rule.
- Preserves the frozen H1 exit convention and transaction-cost model.
- Evaluates entry counterfactuals at actual historical quote timestamps.
- Covers every one of the 54 realized losses.
- Independently validates the baseline P&L against the accepted Phase 9G ledger.
- Separates practical bounded tests from ex-post upper bounds.

## 10. Limitations

The tests are counterfactual historical diagnostics and therefore are not out-of-sample evidence. The ex-post variants deliberately use future information and are not deployable.

The fixed-delay and second-timestamp tests are loss-focused; they do not by themselves establish that the corresponding entry rule improves winners or full-sample expectancy. That requires a separate prospective full-sample test.

The underlying primary source still uses historical close proxies rather than a complete executable bid/ask tape, so live implementation may experience additional spread and market-impact differences.

## 11. Phase conclusion

**Yes, some historical losses could have been turned into profits by changing entry.**

But the important quantitative result is:

- **14/54 (25.9%)** were rescued by the bounded entry changes tested without hindsight-rich arbitrary optimization.
- **40/54** required either broader ex-post freedom or remained losses.
- **38/54** could be rescued by the strongest later-time/any-strike ex-post upper bound, but this is not tradable evidence.
- **16/54 remained losses even under that strongest tested later-entry/strike upper bound.**

Therefore **no entry modification is adopted** from Phase 9H-A.

## 12. Next research decision

The next legitimate step is not another loss-by-loss optimization loop. A candidate entry modification should first be defined prospectively — for example, a fixed delay rule or a predeclared observable criterion — and then tested on the **full 131-trade population**, followed by an untouched chronological holdout.

Until that happens, the Phase 9G frozen H1 entry rule remains the research candidate.
