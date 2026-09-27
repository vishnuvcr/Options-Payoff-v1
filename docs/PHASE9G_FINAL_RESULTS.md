# Phase 9G — Final H1/H2/H3 Far-Expiry Selection Results

## Research question

Under the frozen user rule, does selecting the maximum positive static equal-max-profit=max-loss flatline across every 50-point strike shift from ATM-400 through ATM+400 produce robust realized profitability after execution costs, and is there evidence that using the second- or third-week far expiry improves the economics?

## Frozen strategy

1. Scan chronologically from 09:20 onward; 09:20 is not a gate.
2. At each timestamp require the exact 17 unique common-strike shifts -400,-350,...,0,...,+350,+400.
3. Reject timestamps with conflicting duplicate quote values.
4. If at least one candidate has a positive static flatline, select the maximum positive flatline at that timestamp and stop scanning that weekly cycle.
5. If no qualifying timestamp occurs, continue through later timestamps/days in that weekly cycle.
6. H1 uses the next weekly expiry as the far expiry. H2/H3 use the second/third weekly expiry.
7. All four legs are closed at the near expiry. The near-expiry short CE and long PE settle intrinsically; the far CE/PE are manually squared off at their last available quote at or before the near-expiry index close.
8. Primary execution model: 0.25% premium slippage and ₹20 brokerage per executed order, six transactions per completed trade.
9. No 2.5% trigger remains in the final rule.

## Data and provenance

Primary H1/H2/H3 reconstruction: thetrademarkk/india-index-options-1m, frozen Phase 9G run 36313815542, commit 63b399a9a1d631316dd5233bc684a4ee0a197b25.

The pooled merge was independently rerun from the six frozen yearly artifacts in workflow 36320697995. The original merge failure was an empty-CSV aggregation defect and is logged separately; no yearly reconstruction was rerun.

An independent Rissin source reconstruction was also completed for 2024–2026 as a source-sensitivity study. It is not pooled with the primary source and does not override the primary H1 result.

## Primary H1 result

| Metric | Corrected Phase 9G H1 |
|---|---:|
| Complete realized trades | 131 |
| Incomplete selected rows | 2 |
| Gross P&L | ₹100,816.81 |
| Modeled costs | ₹28,948.05 |
| Net P&L | ₹71,868.76 |
| Mean net/trade | ₹548.62 |
| Median net/trade | ₹352.69 |
| Realized win rate | 58.78% |
| Wilson 95% CI | 50.22%–66.84% |
| Profit factor | 2.29 |
| Maximum drawdown | ₹15,704.24 |
| Static chart-positive rate | 100% |
| IID bootstrap 95% CI for mean | ₹212.77–₹867.02 |
| Circular 4-trade block bootstrap 95% CI | ₹199.66–₹872.13 |

The 100% figure applies to the static chart-selection condition only. It is not a 100% realized-trade win rate.

## H1 annual cohorts

| Year | Trades | Net P&L | Win rate | PF |
|---|---:|---:|---:|---:|
| 2021 | 14 | ₹9,732.04 | 64.29% | 4.16 |
| 2022 | 43 | ₹10,960.27 | 55.81% | 1.55 |
| 2023 | 18 | ₹12,101.86 | 50.00% | 4.83 |
| 2024 | 26 | ₹20,656.83 | 69.23% | 4.19 |
| 2025 | 16 | -₹2,596.87 | 31.25% | 0.88 |
| 2026 | 14 | ₹21,014.63 | 85.71% | 9.93 |

The 2025 negative cohort is an important temporal-stability stress observation.

## Selection behaviour

Across the 131 H1 trades:
- Mean first-positive delay: 184.6 minutes after 09:20.
- Median delay: 210 minutes.
- P90 delay: 357 minutes.
- Mean selected shift: -67.6 points.
- Median selected shift: -250 points.
- Mean absolute shift: 329.4 points.
- ATM selection: 0%.

The selected-shift distribution was concentrated at the outer grid, especially -400 (26 trades), -350 (25), -250 (17), +350 (18), and +400 (18). This confirms that the strategy is not an ATM-only strategy.

## H2/H3 on the primary source

The primary Hugging Face source produced zero qualifying H2 and H3 realized trades. This is not interpreted as zero strategy performance.

The dedicated source audit sampled 152 representative entry timestamps for each far-rank and found zero same-day rows in the corresponding far-expiry files, zero common CE/PE strikes, and zero exact 17-shift grids. The expiry partitions generally begin roughly one weekly cycle before their own expiry. Therefore the source does not contain the pre-entry observations required to evaluate H2/H3 without look-ahead.

Accordingly:
- H2 = not adjudicated on the primary source.
- H3 = not adjudicated on the primary source.
- No zero-P&L horizon comparison is performed.
- No dynamic horizon selector is introduced to compensate for the data limitation.

## Independent Rissin source sensitivity

The independent rissin/nse-options-intraday reconstruction provides pre-entry H2/H3 coverage for a later/partial period and therefore serves as a source-sensitivity check.

| Horizon | Trades | Net P&L | Win rate | PF |
|---|---:|---:|---:|---:|
| H1 | 66 | ₹166,247.97 | 81.82% | 8.40 |
| H2 | 37 | ₹148,974.37 | 94.59% | 12.19 |
| H3 | 16 | ₹120,194.26 | 93.75% | 38.71 |

Matched same-source comparisons were positive:
- H2-H1: 34 paired cycles; mean delta ₹1,820.88; block-bootstrap 95% CI ₹560.37–₹2,749.46; sign-permutation p 0.00570; BH q 0.01140.
- H3-H1: 16 paired cycles; mean delta ₹4,804.10; block-bootstrap 95% CI ₹328.62–₹8,870.46; sign-permutation p 0.01825; BH q 0.01825.

These results are not sufficient to promote H2 or H3 because the source construction differs materially from the primary dataset, the Rissin history begins only in late 2024, and the comparison is not an untouched future holdout. The purpose of this analysis is measurement sensitivity, not vendor selection.

## Execution-cost sensitivity — primary H1

| Slippage | Brokerage | Net P&L |
|---:|---:|---:|
| 0.00% | ₹10 | ₹104,571.86 |
| 0.00% | ₹20 | ₹95,297.06 |
| 0.00% | ₹40 | ₹76,747.46 |
| 0.25% | ₹10 | ₹81,143.56 |
| 0.25% | ₹20 | ₹71,868.76 |
| 0.25% | ₹40 | ₹53,319.16 |
| 0.50% | ₹10 | ₹57,715.25 |
| 0.50% | ₹20 | ₹48,440.45 |
| 0.50% | ₹40 | ₹29,890.85 |
| 1.00% | ₹10 | ₹10,858.64 |
| 1.00% | ₹20 | ₹1,583.84 |
| 1.00% | ₹40 | -₹16,965.76 |

The primary historical result remains positive through 0.50% modeled slippage at all tested brokerage levels, and through 1.00% slippage at ₹10/₹20 brokerage. At 1.00% slippage plus ₹40/order brokerage it becomes negative.

## Statistical interpretation

The corrected H1 mean trade P&L is positive in the historical sample, and both the IID and four-trade block bootstrap intervals for the mean are above zero. This is evidence of historical profitability under the specified reconstruction, not proof of a future edge.

The absence of a valid primary-source H2/H3 dataset prevents a legitimate primary-source horizon comparison. The independent Rissin results are supportive sensitivity evidence but cannot be silently pooled with the Hugging Face measurement.

## Discussion

The key distinction is between chart geometry and realized economics. The four-leg static same-spot chart collapses to the entry premium cashflow, so selecting a positive flatline guarantees that the static chart metric is positive at selection. It does not guarantee that the cross-expiry position will make money when the near-expiry legs settle and the far-expiry legs are manually closed.

The corrected H1 result demonstrates this directly: 131 selected trades were chart-positive, but only 58.78% had positive realized P&L. The loss mechanism is the cross-expiry mark/settlement path between entry and near expiry, together with execution costs.

The no-skip chronological rule is also economically important. The median selected decision occurred 210 minutes after 09:20, showing that an opening-only implementation is not equivalent to the researched rule.

## Strengths

1. Exact 17-unique-shift completeness is enforced.
2. Conflicting duplicate quotes are rejected.
3. No 09:20-only gate or hidden skip is used.
4. All 17 shifts are evaluated at every qualifying timestamp.
5. Maximum positive flatline selection is used rather than ATM-first fallback logic.
6. Far-expiry legs are manually closed at near expiry using observed option prices.
7. Slippage, brokerage, exchange charges, SEBI fee, stamp duty, STT, exercise STT and GST are modeled.
8. H2/H3 source coverage is audited before economic inference.
9. Cross-source results are kept separate.
10. Repository error/activity logs preserve implementation corrections.

## Limitations

1. 2021–2026 is not an untouched future holdout; it was observed during strategy development.
2. One-minute closes are execution proxies rather than complete bid/ask/order-book histories.
3. Historical quote availability can exclude timestamps under the strict 17-strike rule.
4. The primary source does not support valid H2/H3 entry-time reconstruction.
5. Rissin source sensitivity cannot substitute for an independent future holdout.
6. Brokerage schedules can change; live deployment must use current contract-note economics.
7. One-lot historical results do not establish capacity or market-impact tolerance.
8. The strategy is not a guaranteed 100% realized-win system.

## Conclusion

The final Phase 9G evidence supports the following narrow conclusion:

**The exact current H1 rule has produced positive historical net P&L after modeled costs on the primary 2021–2026 dataset, but it has a 58.78% realized win rate rather than a 100% realized win rate. The static chart condition is 100% positive by construction. H2/H3 cannot be adjudicated from the primary source because the required pre-entry far-expiry observations are absent.**

Therefore no H2/H3 horizon is promoted and no dynamic horizon-switching rule is adopted. The result is a research finding, not a deployment guarantee.

## Future research

The predefined next research step is an untouched forward holdout using a source that contains every live expiry at every entry timestamp, plus historical bid/ask or executable quote reconstruction. The holdout should freeze the current rule before observing its outcome and should include current Paytm Money contract-note costs, realistic spread/slippage, liquidity and capacity tests.

Further extensions can test regime conditioning only under a preregistered multiple-testing budget; no such filter is adopted here.

## Reproducibility

Primary merged artifact: workflow 36320697995, artifact 10932342487.

Primary machine-readable files:
- results/phase9g/final_summary.json
- results/phase9g/annual_summary.csv
- results/phase9g/execution_sensitivity.csv
- results/phase9g/H1_strike_shift_distribution.csv

The repository's Phase 9G source-coverage and cross-source sensitivity documents remain part of the evidence chain.