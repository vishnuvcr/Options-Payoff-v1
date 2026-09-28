# Phase 9I — Two-strike / top-two-positive-strike H1 analysis

**Status:** COMPLETE  
**Branch:** `phase-9I-top-two-strikes`  
**Final merge-only workflow:** 36429144740  
**Final artifact:** 10971858546  
**Accepted parent control:** Phase 9G corrected H1

## 1. Research question

Does adding the second-highest positive estimated equal Max Profit = Max Loss strike at the first valid exact-17-strike decision timestamp improve the historical economics of the frozen Phase 9G H1 strategy?

The test changes only the number of selected strikes. Entry timing, strike universe, flatline qualification, H1 horizon, near-expiry exit convention, execution-cost model and data-quality gates remain unchanged.

## 2. Exact variant tested

For each weekly cycle:

1. Scan chronologically from 09:20 through 15:29 across all eligible trading days.
2. Require the complete 17-shift universe: ATM-400 through ATM+400 in 50-point increments.
3. Require no conflicting duplicate quotes.
4. Stop at the first valid timestamp where at least one candidate has a positive flatline.
5. Rank all positive candidates by the estimated equal Max Profit = Max Loss flatline.
6. Select the **top two distinct positive strikes** at that same timestamp.
7. Each selected strike is a complete four-leg H1 position:
   - short near CE;
   - long near PE;
   - long far CE;
   - short far PE.
8. Close the far CE/PE at near-expiry observed market prices and settle the near-expiry legs.
9. Apply the frozen 0.25% premium-slippage model, ₹20/order brokerage and the same statutory charges.

### Important interpretation

This is **not** a forced-two-lot rule. A second position is opened only when a second positive eligible strike exists. In the historical sample, 67 of 131 cycles had two realized positive candidates; 64 cycles had only one realized candidate.

A separate “exactly two lots every week even when the second-ranked strike is non-positive” variant has **not** been tested and would be a materially different strategy definition.

## 3. Reproducibility gate

The rank-1 component of the Phase 9I reconstruction reproduces the accepted Phase 9G H1 control exactly:

- control rows: 131
- rank-1 rows: 131
- merged rows: 131
- maximum absolute P&L difference: approximately ₹3.2e-12
- all rank-1 P&L values match: **True**
- all rank-1 strike selections match: **True**

This is the key guard against accidentally changing the underlying H1 strategy while testing the second position.

## 4. Results

| Metric | Frozen H1 top-1 | Top-2 positive-strike variant |
|---|---:|---:|
| Realized individual positions | 131 | 198 |
| Weekly cycles | 131 | 131 |
| Net P&L | ₹71,868.76 | ₹60,418.42 |
| Mean position P&L | ₹548.62 | ₹305.14 |
| Median position P&L | ₹352.69 | ₹168.61 |
| Win rate | 58.78% | 56.06% |
| Profit factor | 2.285 | 1.607 |
| Maximum drawdown | -₹15,704.24 | -₹31,812.54 |

The top-two variant therefore produced **₹11,450.33 less net P&L** than the one-strike control under the same historical cost model.

## 5. Incremental second-strike contribution

The 67 rank-2 realized positions contributed:

- net P&L: **-₹11,450.33**
- mean P&L: **-₹170.90**
- median P&L: **₹21.50**
- win rate: **50.75%**
- profit factor: **0.737**
- maximum drawdown of the incremental series: **-₹25,066.44**
- bootstrap 95% CI for mean rank-2 P&L: **-₹621.02 to ₹222.88**

The interval includes zero, so the historical sample does not provide robust evidence of a positive incremental second-strike contribution.

## 6. Combined weekly-cycle result

When rank-1 and rank-2 P&Ls are aggregated within each weekly cycle:

- 131 weekly cycles;
- net P&L: **₹60,418.42**;
- mean weekly P&L: **₹461.21**;
- win rate: **57.25%**;
- profit factor: **1.616**;
- maximum drawdown: **-₹31,812.54**;
- bootstrap 95% CI for mean weekly P&L: **-₹68.08 to ₹942.13**.

Again, the uncertainty interval includes zero.

## 7. Annual incremental behaviour

Rank-2 net contribution by calendar year:

| Year | Rank-2 positions | Rank-2 net P&L |
|---|---:|---:|
| 2021 | 10 | ₹6,617.86 |
| 2022 | 29 | -₹1,684.30 |
| 2023 | 8 | -₹1,879.98 |
| 2024 | 10 | -₹2,564.96 |
| 2025 | 7 | **-₹15,876.41** |
| 2026 | 3 | ₹3,937.46 |

The second-strike contribution is therefore not temporally stable. The large negative 2025 contribution is material to the pooled result.

## 8. Economic interpretation

The second-ranked strike does not simply duplicate the first-strike opportunity. Once the first strike is selected, the second strike is selected using the same positive static flatline criterion, but its subsequent near-expiry cross-expiry economics can still be unfavorable.

Adding a second strike also increases capital usage, number of option orders and aggregate transaction costs. Consequently, a larger absolute rupee P&L would not by itself establish improvement; normalized return on deployed capital and risk would also be required.

In this historical sample the observed direction is the opposite: the incremental second-strike component is negative, total net P&L falls, profit factor falls, realized win rate falls, and maximum drawdown approximately doubles relative to the one-strike control.

## 9. Limitations

1. The 2021–2026 sample was already observed during research development, so this is rule-frozen historical validation rather than an untouched future holdout.
2. The underlying market data are historical 1-minute close proxies, not contemporaneous executable bid/ask fills.
3. The second-strike rule was tested only when the second candidate itself was positive. A forced-two-position variant remains untested.
4. Capital/margin normalization is not yet the primary comparison metric in this phase.
5. Source construction and execution-price uncertainty remain limitations already documented for Phase 9G.

## 10. Decision

**No change is made to the frozen Phase 9G H1 strategy.**

Phase 9I provides a negative incremental historical result for the screened second positive strike under the accepted cost and exit model. The evidence does not support promoting the top-two-positive-strike variant as the new control.

The frozen one-strike H1 strategy remains the research candidate. Any exact-two-lot implementation, including a forced second strike when fewer than two positive candidates exist, must be treated as a separate preregistered variant.

## 11. Reproducibility outputs

- [Final summary](../results/phase9i_fast/summary.json)
- [Top-two trade ledger](../results/phase9i_fast/top2_trade_rows.csv)
- [Cycle summary](../results/phase9i_fast/top2_cycle_summary.csv)
- [Yearly rank contribution](../results/phase9i_fast/top2_yearly_summary.csv)
- [Top-1 control validation](../results/phase9i_fast/top2_baseline_validation.csv)
- [Top-1 vs top-2 metrics](../results/phase9i_fast/top2_vs_top1_metrics.csv)
