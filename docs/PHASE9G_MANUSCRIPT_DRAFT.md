# Phase 9G — Fixed Far-Expiry Horizon Research Manuscript Draft

## Abstract

This study evaluates a specified four-leg NIFTY index-options cross-expiry strategy in which, at each available one-minute observation from 09:20 to 15:29 IST, the researcher evaluates common-strike candidates spanning ATM-400 through ATM+400 in 50-point increments. A timestamp can qualify only when all 17 candidates have the required option quotes. The first qualifying timestamp in each weekly cycle is selected, and among the 17 candidates the maximum positive estimated equal Max Profit = Max Loss flatline is chosen. The current research compares three preregistered fixed far-expiry horizons (H1, H2, H3) using the same selection mechanism.

The study distinguishes the static one-dimensional payoff-chart metric from economically realized cross-expiry P&L. The far-expiry legs are manually closed using observed market prices at near-expiry exit rather than valued at their own terminal expiry. Transaction costs include brokerage, exchange transaction charges, SEBI charges, stamp duty, STT and GST, with explicit premium slippage sensitivity. The primary comparison is paired H2/H3 versus H1 on the same weekly opportunities, supplemented by dependence-aware bootstrap confidence intervals, sign-permutation inference, multiple-comparison control, yearly stability, and selection-behaviour analysis.

H2/H3 results remain pending the corrected Phase 9G reconstruction. The frozen H1 control contains 169 complete realized trades with ₹125,688.82 net P&L, 63.91% realized win rate and profit factor 2.94 at the primary cost assumption. These H1 results are a control reference, not a guarantee of future performance.

## 1. Introduction

The motivating observation is that a particular four-leg cross-expiry options structure can produce a visually flat positive payoff line when the same hypothetical terminal spot is applied to both expiries. Such a chart can appear to imply equal positive maximum and minimum payoff. However, the near-expiry and far-expiry contracts do not terminate simultaneously, so a static payoff chart is not equivalent to the realized economic P&L of the position when the far legs are closed at near expiry.

The present study therefore asks whether the chart-selection rule is associated with economically positive net performance after realistic execution assumptions, and whether the choice of far-expiry horizon changes the outcome.

## 2. Research Questions

### RQ1
Does the specified cross-expiry strategy produce positive realized net P&L after Indian index-option transaction costs and conservative premium slippage?

### RQ2
Does the positive flatline selection condition identify economically favorable trades when realized P&L is evaluated at near-expiry exit?

### RQ3
Does changing the fixed far-expiry horizon from H1 to H2 or H3 change net performance relative to the H1 control on the same weekly opportunities?

### RQ4
How do decision timing, selected strike displacement, yearly stability, and cost sensitivity differ across H1, H2 and H3?

### RQ5
Are observed effects robust to data completeness, transaction-cost assumptions, dependence-aware inference and multiple-comparison correction?

## 3. Strategy Specification

At each eligible NIFTY trading timestamp from 09:20 through 15:29 IST:

1. Identify the current near expiry and the fixed far expiry corresponding to H1, H2 or H3.
2. Define ATM from the NIFTY spot/index price at that timestamp.
3. Evaluate exactly 17 common strikes: ATM-400, ATM-350, ..., ATM-50, ATM, ATM+50, ..., ATM+350, ATM+400.
4. Require all 17 candidates to be evaluable before a timestamp can qualify.
5. For each common strike construct:
   - short near-expiry call;
   - long near-expiry put;
   - long far-expiry call;
   - short far-expiry put.
6. Calculate the static flatline metric from the four entry premiums.
7. A timestamp qualifies only if at least one of the 17 candidates has a positive equal Max Profit = Max Loss flatline.
8. Select the first qualifying timestamp in the weekly cycle.
9. At that timestamp select the candidate with the maximum positive estimated equal Max Profit = Max Loss.
10. If 09:20 does not qualify, continue through later timestamps and subsequent trading days of the same weekly cycle.
11. For realized P&L, the near-expiry pair is settled at near-expiry index settlement and the far-expiry pair is manually closed using the last observed far-leg prices on or before the near-expiry exit timestamp.

The former 2.5% entry threshold is not part of the current strategy.

## 4. Data

Primary option and index history is reconstructed from the project’s cached Hugging Face research dataset, with timestamps normalized to Asia/Kolkata. The repository also records source provenance and broader public-source literature/data review.

Quality controls include expiry identity, strike identity, timestamp normalization, quote completeness, lot-size changes, missing observations and cross-expiry contract availability.

A critical new safeguard is that a positive result from fewer than 17 evaluable strikes is not considered a valid decision observation.

## 5. Transaction-Cost Model

The primary execution model uses 0.25% premium slippage and ₹20 brokerage per executed order.

The realized near-expiry convention produces:
- four entry orders;
- two far-leg manual exit orders;
- near-expiry settlement of the expiring index-option legs.

The model includes applicable:
- brokerage;
- exchange transaction charges;
- SEBI turnover fees;
- stamp duty;
- STT on relevant option sales;
- exercise STT where applicable;
- GST on the modeled fee components.

Sensitivity tests include 0%, 0.25%, 0.50% and 1.00% premium slippage where supported, plus ₹10, ₹20 and ₹40 brokerage per order.

## 6. Statistical Analysis

The primary unit of comparison is the weekly cycle.

For each horizon:
- total complete trades;
- gross P&L;
- net P&L;
- mean and median net P&L per trade;
- realized win rate;
- profit factor;
- maximum drawdown;
- transaction-cost drag;
- first-positive decision-time distribution;
- selected-strike distribution;
- annual cohort results.

For H2 and H3 versus H1, matched weekly cycles are compared using paired P&L differences. The primary inference reports:
- mean paired difference;
- median paired difference;
- proportion of positive paired differences;
- circular block-bootstrap confidence interval using four-trade blocks;
- sign-permutation p-value;
- Benjamini-Hochberg adjusted q-value across the H2/H3 comparisons.

A horizon is not changed merely because its aggregate historical P&L is larger. The preregistered paired comparison, confidence interval, multiple-comparison adjustment, yearly stability and execution-cost checks must all support the result.

## 7. Literature Context

Published work on NIFTY option arbitrage and broader option markets shows that apparent option-price inefficiencies can be transient and strongly affected by execution costs, liquidity, volatility and the cross-maturity volatility surface. This literature motivates separating the static chart identity from the realized trading outcome and treating cross-expiry selection as an empirical question rather than assuming that a positive chart is a risk-free arbitrage.

The repository’s literature register includes work on NIFTY box-spread efficiency, implied-volatility term structure, volatility risk premia and calendar-spread dependence.

## 8. Frozen H1 Control Evidence — Corrected Phase 9G

The authoritative corrected Phase 9G H1 reconstruction contains **131 complete realized trades** and 2 incomplete selected rows under the exact 17-unique-shift/no-conflicting-duplicate rule.

Primary cost model:
- 0.25% premium slippage per execution;
- ₹20 brokerage per executed order;
- six transactions per completed trade;
- date-dependent STT/exercise STT plus exchange, SEBI, stamp duty and GST.

Primary H1 results:
- gross P&L: **₹100,816.81**;
- modeled costs: **₹28,948.05**;
- net P&L: **₹71,868.76**;
- mean net P&L/trade: **₹548.62**;
- median: **₹352.69**;
- realized win rate: **58.78%**;
- Wilson 95% CI: **50.22%–66.84%**;
- profit factor: **2.29**;
- maximum drawdown: **₹15,704.24**;
- IID bootstrap 95% CI for mean: **₹212.77–₹867.02**;
- circular four-trade block bootstrap 95% CI: **₹199.66–₹872.13**.

The static chart-positive rate is 100%, but this is a property of the selection criterion and is not a realized 100% win rate.

Selection behaviour:
- median first-positive delay: 210 minutes after 09:20;
- P90 delay: 357 minutes;
- ATM selection: 0%;
- median selected shift: -250 points;
- mean absolute selected shift: 329.4 points.

The annual H1 cohort table is persisted in results/phase9g/annual_summary.csv. The 2025 cohort is negative (-₹2,596.87; 31.25% wins), so the result is not uniformly positive across calendar years.

## 9. Results — H2/H3

### 9.1 Primary source

The primary Hugging Face source produced no qualifying H2 or H3 trades. These zeros are **not interpreted as economic zero performance**.

A dedicated source-coverage audit sampled 152 representative entry timestamps for each far-rank. Every sample had zero same-day rows in the corresponding far-expiry partition, zero common CE/PE strikes and zero exact 17-shift surfaces. The partition windows generally begin roughly one weekly cycle before their own expiry. Thus the source lacks the pre-entry observations required to evaluate H2/H3 without look-ahead.

Therefore:
- H2 is **not adjudicated** on the primary source.
- H3 is **not adjudicated** on the primary source.
- No zero-P&L comparison is performed.
- No dynamic horizon switching is introduced.

### 9.2 Independent source sensitivity

The independent Rissin reconstruction for 2024–2026 produced:
- H1: 66 trades, ₹166,247.97 net, 81.82% realized wins, PF 8.40;
- H2: 37 trades, ₹148,974.37 net, 94.59% realized wins, PF 12.19;
- H3: 16 trades, ₹120,194.26 net, 93.75% realized wins, PF 38.71.

Matched same-source paired comparisons were:
- H2-H1: 34 paired cycles, mean delta ₹1,820.88, block-bootstrap 95% CI ₹560.37–₹2,749.46, sign-permutation p=0.00570, BH q=0.01140.
- H3-H1: 16 paired cycles, mean delta ₹4,804.10, block-bootstrap 95% CI ₹328.62–₹8,870.46, sign-permutation p=0.01825, BH q=0.01825.

These are source-sensitivity findings only. They do not establish that H2 or H3 is the production horizon because the source construction differs from the primary dataset, the history is partial, and the comparison is not an untouched future holdout.

## 10. Execution-Cost Sensitivity

For the primary H1 source, net P&L was:

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

The result is therefore sensitive to execution quality, becoming negative in the most adverse tested combination.

## 11. Discussion

The central distinction is between static payoff-chart geometry and realized cross-expiry economics. For this four-leg structure, the one-dimensional same-spot chart collapses to the entry premium cashflow. A positive flatline therefore guarantees only that the selected chart metric is positive.

The realized trade, however, experiences different settlement dates and manual exit prices for the far-expiry legs. Consequently the positive chart metric is not a risk-free arbitrage certificate. In the corrected H1 sample, all selected charts were positive while only 58.78% of realized trades were profitable.

The chronology also matters. The median first-positive observation occurred 210 minutes after 09:20, so an implementation that checks only the opening observation is a materially different strategy.

## 12. Strengths

- Exact 17 unique shifts are enforced.
- Conflicting duplicate quotes are rejected.
- The no-skip chronological rule is explicit.
- All 17 strike shifts are evaluated before selecting the maximum.
- Far-expiry legs are manually closed at near expiry using observed option prices.
- Six transaction costs and date-dependent statutory charges are modeled.
- Execution sensitivity is explicit.
- H2/H3 source coverage is audited before inference.
- Heterogeneous data sources are not silently pooled.
- Errors and corrections are retained in the repository.

## 13. Limitations

1. 2021–2026 is historical data already observed during research development, not a pristine future holdout.
2. One-minute closes are execution proxies rather than complete bid/ask/order-book histories.
3. Missing historical option quotes can prevent a timestamp from satisfying the exact 17-strike requirement.
4. The primary source lacks valid pre-entry H2/H3 coverage.
5. Rissin source sensitivity is not an independent future holdout.
6. Brokerage schedules may change; deployment should use current contract-note economics.
7. One-lot historical simulation does not establish capacity or market-impact tolerance.
8. The strategy does not have a guaranteed 100% realized win rate.

## 14. Conclusion

The final Phase 9G evidence supports a narrow historical conclusion:

**The exact current H1 rule produced positive net P&L after modeled costs on the primary 2021–2026 dataset, but its realized win rate was 58.78%, not 100%. The static chart-positive condition was 100%. H2/H3 could not be adjudicated on the primary source because the required pre-entry far-expiry observations were absent.**

No dynamic horizon selector is adopted. No H2/H3 horizon is promoted. The result is a historical research finding rather than a deployment guarantee.

## 15. Future Research

Potential extensions after the predefined Phase 9G decision include:
- untouched future holdout testing;
- full historical bid/ask reconstruction;
- liquidity/capacity analysis;
- alternative execution algorithms;
- intraday volatility-surface conditioning;
- contract-level market-impact modeling;
- independent replication on additional index-option datasets.

These are future directions, not components of the current acceptance decision.


## 16. Legacy-control supersession note

The authoritative Phase 9D H1 artifact was independently audited against the current exact 17-strike specification. Of 172 historical selected timestamps in that legacy artifact, only 45 contained the exact prescribed 17 unique strike shifts; 127 were missing at least one prescribed shift. No conflicting quote values were found among the audited decision surfaces. The legacy 169-trade H1 result is therefore retained only as historical diagnostic evidence and is **not** the control for Phase 9G inference. The corrected H1 control is reconstructed from the raw option data under the current exact rule and is compared with H2/H3 on matched weekly opportunities.

This distinction is essential because simply filtering the legacy trades down to the 45 complete timestamps would not reconstruct the first qualifying timestamp under the corrected rule: a later timestamp within the same weekly cycle could become the valid first qualifying opportunity after incomplete timestamps are rejected.


## Phase 9G source-coverage limitation identified

A dedicated audit of the current Hugging Face source (thetrademarkk/india-index-options-1m) found that its expiry-partitioned option files generally begin only about one weekly cycle before the file's own expiry. This is sufficient for the H1 construction, because the next weekly expiry file overlaps the current near-expiry trading week, but it does not provide the far-rank-2 or far-rank-3 contract at the earlier entry dates required by the strategy.

Across 152 sampled timestamps for each of far-rank 2 and far-rank 3, there were zero same-day rows in the far-expiry file, zero common CE/PE strikes, and zero exact 17-shift grids. The resulting H2/H3 zero-opportunity counts are therefore classified as data-source coverage failure, not economic evidence.

This conclusion is consistent with the exchange contract structure: NSE currently specifies four weekly NIFTY 50 option expiry contracts and a 50-point strike interval for weekly/monthly contracts. The data source limitation cannot be used to infer non-existence of the underlying contracts.

A replacement source must provide pre-entry intraday observations for every live expiry. The Phase 9G rule remains frozen; no H2/H3 selector or dynamic horizon switching is introduced merely to work around the data limitation.

## Interim corrected H1 results

Run 27 has completed 2024 and 2026. Under the primary execution-cost model (0.25% premium slippage and ₹20/order brokerage), 2024 contains 26 realized trades with ₹20,656.83 net P&L, while 2026 contains 14 realized trades with ₹21,014.63 net P&L. These are interim calendar-year results only and are not a pooled Phase 9G conclusion until all yearly reconstructions and the predeclared statistical audit complete.


## Interim corrected H1 checkpoint
Three corrected H1 yearly artifacts are complete. The combined interim subset (2021, 2024, 2026) contains 54 realized trades, ₹51,403.50 net P&L and 72.22% realized win rate under 0.25% slippage plus ₹20/order brokerage. The subset is descriptive only until the remaining years and predeclared sensitivity/statistical tests complete.

## Cross-source measurement sensitivity

A source-sensitivity audit compared the corrected H1 control across the current Hugging Face source and the independent Rissin source for years with overlap. The 2024 net results were ₹20,656.83 (HF) versus ₹18,690.31 (Rissin); in 2026 they were ₹21,014.63 versus ₹58,226.92. The discrepancy demonstrates that historical option-data source construction and coverage can materially change measured P&L even when the trading rule and primary cost model are fixed. The study therefore treats source provenance as part of the measurement model, does not select a preferred vendor from these discrepancies, and does not silently pool horizons across heterogeneous sources.
