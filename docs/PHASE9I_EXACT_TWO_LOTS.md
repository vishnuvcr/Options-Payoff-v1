# Phase 9I — Exact Two-Lot Top-Two-Strike H1 Analysis

**Status:** COMPLETE  
**Branch:** `phase-9I-top-two-strikes`  
**Accepted final artifact:** workflow 36429144866 / artifact 10972304314  
**Parent control:** Phase 9G corrected H1

## Research question

What happens if, at each accepted Phase 9G weekly entry timestamp, the strategy enters **two lots/positions**, using the two distinct strikes with the largest estimated equal Max Profit = Max Loss flatline values across the complete 17-strike universe?

## Exact rule tested

- Keep the accepted Phase 9G 131 entry timestamps fixed.
- At each timestamp, evaluate all 17 distinct shifts ATM-400 through ATM+400 in 50-point increments.
- Rank all available candidates by static flatline value, descending.
- Select the top two **distinct** strikes, even if the second-ranked flatline is non-positive.
- Execute a complete four-leg H1 position at each selected strike.
- Use the same near-expiry far-leg exit convention.
- Use the same 0.25% premium slippage, ₹20/order brokerage and statutory-cost model.
- No 2.5% threshold, no additional filter, no dynamic management.

This directly tests the user's literal "two lots every qualifying week" interpretation. It is different from the earlier **top-two-positive** sensitivity, where a second position was opened only when its flatline was positive.

## Reproducibility gate

The rank-1 component reproduced the accepted Phase 9G H1 control:

- 131/131 rows matched.
- All selected rank-1 strikes matched.
- Maximum absolute P&L difference: approximately ₹3.2e-12.

Therefore the difference is attributable to adding the second ranked position rather than changing the original entry rule.

## Results

| Metric | One-lot control | Exact two-lot variant |
|---|---:|---:|
| Weekly cycles | 131 | 131 |
| Realized positions | 131 | 262 |
| Net P&L | ₹71,868.76 | **₹87,362.19** |
| Incremental rank-2 P&L | — | **₹15,493.43** |
| Position win rate | 58.78% | 56.11% |
| Weekly-cycle win rate | 58.78% | 53.44% |
| Profit factor | 2.285 | 1.651 |
| Maximum drawdown | -₹15,704.24 | **-₹36,888.35** |
| Mean position P&L | ₹548.62 | ₹333.44 |
| Mean weekly-cycle P&L | ₹548.62 | **₹666.89** |

## Incremental second-strike economics

The second selected position contributed:

- **+₹15,493.43 net**
- 131 additional positions
- 53.44% win rate
- Profit factor 1.198
- Mean +₹118.27 per second position
- Median +₹69.12
- Bootstrap 95% CI for mean second-position P&L: **₹-212.70 to ₹438.82**

The point estimate is positive, but the bootstrap interval includes zero, so the historical evidence is not strong enough to establish a robust positive incremental effect.

## Risk effect

The additional position substantially increases downside variability:

- maximum drawdown changes from **-₹15,704.24** to **-₹36,888.35**;
- approximately **2.35×** the control drawdown magnitude;
- profit factor falls from 2.285 to 1.651;
- weekly-cycle win rate falls from 58.78% to 53.44%.

Thus the additional ₹15,493.43 historical P&L came with materially greater drawdown and weaker efficiency of gains versus losses.

## Interpretation

The two-lot rule increases absolute historical P&L because it adds a second ranked position in every qualifying week. The correct comparison is therefore not simply ₹87,362 versus ₹71,869: it also requires considering additional capital/margin, execution costs and risk.

The second-ranked position was **historically profitable in aggregate**, but only modestly so relative to its added risk. The result should not be interpreted as evidence of a guaranteed improvement or as a 100% win-rate mechanism.

## Relationship to the earlier top-two-positive test

Two separate variants were tested:

1. **Top-two-positive:** add the second strike only when its static flatline is positive. Result: 67 additional positions, **-₹11,450.33** incremental net P&L.
2. **Exact two-lot:** always take the two highest-ranked distinct strikes at every accepted signal. Result: 131 additional positions, **+₹15,493.43** incremental net P&L.

The difference is important: the exact-two-lot result includes second-ranked strikes whose static flatline was not positive. Therefore the two results answer different questions and must not be combined.

## Limitations

1. This is historical in-sample research, not an untouched chronological holdout.
2. The 1-minute option data use observed closes rather than guaranteed contemporaneous executable bid/ask fills.
3. The incremental result has substantial uncertainty; its bootstrap interval includes zero.
4. Capital/margin-normalized return was not the primary acceptance metric in this phase.
5. The strategy still depends on the frozen Phase 9G data-quality and execution assumptions.

## Decision

**Do not replace the Phase 9G one-strike research control yet.**

The exact-two-lot variant is a promising **candidate for prospective/out-of-sample testing** because its pooled historical incremental P&L is positive, but its lower profit factor and approximately 2.35× drawdown mean the result is not sufficient by itself for adoption.

A proper next phase should test the exact-two-lot rule on an untouched chronological holdout and report return on deployed capital/margin, incremental cost, drawdown, and stability by year/regime.

