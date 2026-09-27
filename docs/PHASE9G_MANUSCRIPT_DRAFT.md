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

## 8. Frozen H1 Control Evidence

The authoritative corrected H1 control contains:
- 169 complete realized trades;
- ₹125,688.82 net P&L;
- 63.91% realized win rate;
- profit factor 2.94;
- ₹16,200.65 maximum drawdown;
- mean net P&L ₹743.72 per trade.

The H1 selection behaviour is materially non-ATM:
- ATM was selected once in the 169 complete realized trades;
- -400 was selected 35 times;
- -350 was selected 28 times;
- -300 was selected 18 times;
- +400 was selected 19 times;
- +350 was selected 15 times.

First-positive timing was also distributed through the trading day rather than concentrated at 09:20. The median delay was 25 minutes after 09:20, while the P90 delay was 340.2 minutes.

Annual H1 cohorts were historically net-positive across 2021–2026, but the 2025 cohort was much weaker than the other years. This is retained as a temporal-stability stress observation.

## 9. Results — H2/H3

**Pending corrected Phase 9G reconstruction.**

This section will be populated only from the authoritative run that passes the strict 17-strike completeness gate and H1 control reproduction.

Required tables:
1. H1/H2/H3 aggregate performance.
2. H1/H2/H3 annual cohorts.
3. Paired H2-H1 and H3-H1 differences.
4. Execution-cost sensitivity.
5. First-positive decision-time distribution.
6. Selected-strike distribution.
7. Completeness and exclusion audit.

Required figures:
1. Equity curves.
2. Drawdowns.
3. Annual net P&L.
4. Paired-delta distribution.
5. Decision-time distribution.
6. Strike-selection heatmap/distribution.
7. Cost-sensitivity curves.

## 10. Discussion

The interpretation will distinguish:
- static chart geometry;
- entry-time selection;
- realized economic P&L;
- execution costs;
- statistical evidence;
- data completeness;
- temporal stability.

A positive H1 or H2/H3 result will not be described as a guaranteed 100% win-rate strategy. The 100% quantity relevant to the static chart is the positivity of the selected chart condition; realized trade outcomes are evaluated independently.

## 11. Strengths

- Exact chronological rule is explicitly encoded.
- All 17 strike candidates are required.
- No separate 09:20 skip gate.
- Far-expiry legs are marked using observed near-expiry prices.
- Transaction costs are explicit and stress-tested.
- H2/H3 are fixed variants rather than dynamically selected after observing results.
- Paired inference controls for common weekly opportunities.
- Repository logs preserve corrections and methodological changes.

## 12. Limitations

1. The 2021–2026 period is historical data already observed during research development and therefore is not a pristine untouched future holdout.
2. One-minute close prices are used as execution proxies rather than full order-book bid/ask histories.
3. Some historical option strikes may have incomplete quote availability; incomplete 17-strike timestamps are now excluded from qualification and audited.
4. Broker pricing can change; live execution should use the actual contract-note economics in force at deployment.
5. Slippage is modeled parametrically rather than reconstructed from complete historical order-book depth.
6. The strategy may have capacity/liquidity constraints that are not fully represented by one-lot historical simulation.

## 13. Conclusion

**Pending H2/H3 acceptance tests.**

The study is designed to answer whether the cross-expiry positive-flatline selection rule corresponds to robust realized profitability after costs, not merely whether the static payoff chart appears positive.

## 14. Future Research

Potential extensions after the predefined Phase 9G decision include:
- untouched future holdout testing;
- full historical bid/ask reconstruction;
- liquidity/capacity analysis;
- alternative execution algorithms;
- intraday volatility-surface conditioning;
- contract-level market-impact modeling;
- independent replication on additional index-option datasets.

These are future directions, not components of the current acceptance decision.
