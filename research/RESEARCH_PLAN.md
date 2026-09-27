# Research plan — Options-Payoff-v1

**Version:** 2.0  
**Plan status:** Updated 2026-09-27 because the user materially changed the selection rule from ordered fallback selection to exhaustive maximum-flatline selection.

## Research questions

**RQ1.** Does the specified cross-expiry synthetic-forward strategy generate positive net P&L after realistic Indian index-options transaction costs?

**RQ2.** Does the user's one-dimensional payoff-chart metric — a positive flat line whose chart-reported max profit equals max loss — identify trades that subsequently outperform the unconditional strategy?

**RQ3.** When every common strike from -400 through +400 points in 50-point steps is evaluated, does selecting the candidate with the maximum estimated max-profit=max-loss flatline value improve net outcomes?

**RQ4.** How do results change across volatility, trend, gap, liquidity, option-implied-volatility term-structure and broader market regimes?

**RQ5.** Are any apparent profits explained by execution assumptions, bid/ask selection, settlement conventions, or data-quality artifacts rather than a stable market effect?

## Primary hypothesis

The chart-triggered rule will only be considered supported if it shows economically meaningful and statistically robust net performance after costs, out-of-sample validation and conservative execution assumptions.

A flat chart by itself is not treated as evidence of a risk-free or guaranteed return.

## Aims

1. Formalize the strategy mathematically and operationally.
2. Build a reproducible data pipeline for weekly NIFTY option contracts.
3. Backtest the exact trigger plus predefined strike shifts.
4. Measure performance after costs and slippage.
5. Stress-test the result across market regimes and alternative assumptions.
6. Produce a complete research manuscript.

## Objectives

- Define unambiguous entry time, ATM rule, strike-shift rule, expiry pairing, sizing and settlement logic.
- Reconstruct the original payoff-chart metric.
- Independently compute economically correct two-expiry P&L.
- Compare signal-selected trades with rejected trades and relevant benchmarks.
- Record every trade decision and the reason for it.
- Estimate win rate, average/median trade return, expectancy, profit factor, max drawdown, Sharpe/Sortino/Calmar where appropriate, tail losses, turnover and cost drag.
- Use confidence intervals and bootstrap/time-series robustness tests rather than relying only on point estimates.
- Separate discovery from final validation.

## Phase 0 — Bootstrap and governance

**Branch:** phase-0-bootstrap

Outputs:
- repository instructions
- plan, status, error and activity logs
- source register
- README framework

Exit criteria:
- all governance files exist and are linked.

## Phase 1 — Strategy specification and analytical validation

**Branch:** phase-1-specification

Tasks:
1. Encode the four option legs.
2. Define ATM and -400/+400 common-strike candidates.
3. Define near and next weekly expiries.
4. Define an explicit entry observation timestamp (configurable; default 09:20 IST for research).
5. Reproduce the user's static payoff-chart metric.
6. Derive the correct two-expiry settlement P&L.
7. Add unit tests showing the difference between the static chart and the economically correct cross-expiry outcome.
8. Define the >2.5% threshold denominator as a configurable research parameter rather than silently assuming one.

Exit criteria:
- deterministic strategy specification
- executable payoff functions
- passing unit tests
- no ambiguity in expiry/strike mapping within the code.

## Phase 2 — Market-data acquisition, cleaning and cache

**Branch:** phase-2-data

Primary market:
- NIFTY 50 option contracts
- NIFTY spot/index settlement
- contract metadata, expiry, strike, option type, volume and OI where available

Candidate data sources:
- NSE official historical/option-chain sources
- Hugging Face public datasets containing NIFTY option history
- GitHub research pipelines/datasets
- other public datasets for cross-checks

Process:
- store source metadata and checksums
- normalize timestamps to IST
- validate expiry calendars
- validate strike/contract identity
- detect duplicates, stale/missing observations and impossible prices
- create a compact research subset from larger public datasets where licensing allows

Exit criteria:
- reproducible dataset build
- data validation report
- cached/derived data sufficient for the Phase 3 workflow.

## Phase 3 — Backtest engine and transaction-cost model

**Branch:** phase-3-backtest

Core execution:
- entry using conservative bid/ask assumptions
- explicit slippage model
- four-leg order accounting
- settlement at actual exchange expiry
- configurable position size
- no look-ahead
- no use of future expiry prices in entry selection

Cost model:
- brokerage per executed order
- STT
- exchange transaction charges
- SEBI turnover fee
- stamp duty
- GST where applicable
- any documented broker-specific fee
- optional sensitivity to wider spreads/slippage

Main comparisons:
- exact ATM trigger
- ATM only without trigger
- ATM + -400/+400 fallback
- randomized/blocked benchmark controls
- simple synthetic-forward/calendar benchmarks

Exit criteria:
- complete trade ledger
- net P&L and capital/margin series
- reproducible performance tables and figures.

## Phase 4 — Statistical validation and robustness

**Branch:** phase-4-validation

Analyses:
- descriptive statistics
- confidence intervals
- block/bootstrap inference
- walk-forward or time-split out-of-sample validation
- sensitivity to entry time
- sensitivity to threshold
- sensitivity to slippage/spreads
- sensitivity to strike-shift size
- sensitivity to capital denominator
- multiple-testing awareness for exploratory variants

Exit criteria:
- primary and sensitivity results separated
- predeclared evaluation metrics reported
- uncertainty quantified.

## Phase 5 — Regime and cross-market attribution

**Branch:** phase-5-regimes

Where data availability supports it, stratify by:
- realized volatility
- India VIX / analogous volatility measures
- option IV level and IV term structure
- trend and gap regime
- option OI/volume/liquidity
- FII/DII activity
- global equity futures/indices
- USD/INR
- gold
- major corporate/news-event periods
- market microstructure/liquidity conditions

Goal:
- determine whether any edge is conditional rather than unconditional
- distinguish selection effects from structural arbitrage.

Exit criteria:
- regime tables and interaction/attribution analysis
- clear separation between confirmatory and exploratory findings.

## Phase 6 — Manuscript and final conclusion

**Branch:** phase-6-manuscript

Required manuscript sections:
- abstract
- introduction
- research questions/hypotheses
- literature review
- data
- methodology
- transaction-cost model
- results
- robustness
- regime analysis
- discussion
- strengths
- limitations
- conclusion
- future research
- reproducibility appendix
- data dictionary
- trade-ledger appendix
- supplementary figures/tables

Exit criteria:
- complete reproducible manuscript
- final strategy assessment framed as research evidence, not a trading guarantee
- research stopped after the predefined phases.


## Phase 7 — Payoff-platform semantics and exhaustive maximum-flatline selection

**Branch:** phase-7-max-equal-selection

Rationale:
- The user clarified that the relevant 2.5% field is the payoff-builder max-profit/max-loss percentage, not a self-defined return denominator.
- Sensibull publicly documents max-profit/max-loss percentage as maximum profit or maximum loss divided by margin required. Public Streak material documents payoff graphs and max-profit/max-loss but does not publish a comparable percentage formula.
- For the user's four-leg mixed-expiry structure, the static same-terminal-spot chart remains a flat line; that chart value is an estimated chart metric, not the true worst-case loss of the held two-expiry position.

Selection protocol:
1. Evaluate every common strike at ATM-400, ATM-350, ... ATM, ... ATM+350, ATM+400.
2. Keep only strikes present for all four option legs at both expiries.
3. Compute the positive flatline value from the four observed entry premiums.
4. Record estimated max profit, estimated min/max chart P&L, and the equal max-profit=max-loss value in INR.
5. Select exactly one strike per entry timestamp: the candidate with the highest estimated equal max-profit=max-loss value.
6. Do not use the old ATM-first/fallback ordering.
7. Use the reconstructed margin-required denominator for the primary backtest; retain the buy-premium result only as a historical sensitivity.
8. Re-run downstream validation only to the extent statistically meaningful; with four exact qualifying i1 trades, treat inferential statistics as exploratory and report the exact ledger instead.

Primary Phase 7 score:
- `equal_max_profit_loss_inr` — the positive static flatline value per lot.

Secondary/sensitivity score:
- `chart_return_pct` using the repository's configurable denominator, explicitly labeled as a research proxy rather than a proprietary Sensibull reproduction.

Exit criteria:
- exhaustive -400..+400 selection is reproducibly implemented;
- tests pass;
- Phase 7 primary and 2.5% sensitivity ledgers are generated;
- platform-semantics review is documented;
- downstream validation is either rerun or explicitly shown as pending.

## Decision rules

The research must not declare a strategy successful based on a single backtest or a flat payoff chart. Any positive result must survive realistic execution costs and predefined out-of-sample/robustness checks.

## Default assumptions pending empirical verification

- Underlying: NIFTY 50.
- Weekly expiry: NSE-defined weekly contracts.
- Entry observation: 09:20 IST.
- Candidate strikes: ATM, ATM-400, ATM+400.
- Holding: settlement/expiry as specified, with near and next expiry tracked separately.
- Threshold: 2.5% of reconstructed margin required.
- Position size: 1 lot by default for reporting; scale tests later.

## Phase 7A — Historical margin reconstruction and platform-percentage calibration

**Branch:** phase-7A-margin-reconstruction

Objective:
- Replace the legacy buy-premium proxy for the 2.5% max-profit/max-loss percentage with a reproducible margin-required denominator wherever historical margin data can be reconstructed.

Calibration target:
- User screenshot: NIFTY 23140.50; 1-lot 29-Sep-2026/06-Oct-2026 four-leg position at 23450 strike; Sensibull standalone margin ₹88,076.
- The screenshot is date-identified as 25-Sep-2026 using the exact NIFTY 23140.50 close and contemporaneous Sep futures quote.

Method:
1. Obtain the daily NSE Clearing SPAN risk-parameter file for 25-Sep-2026 and, where available, the appropriate intraday file nearest the screenshot time.
2. Reconstruct the four-leg portfolio using 65 NIFTY units.
3. Calculate SPAN scan risk, calendar-spread charge and exposure/ELM components using the published SPAN inputs.
4. Report multiple margin definitions (SPAN, SPAN+exposure, and premium-inclusive variants) and compare them with ₹88,076.
5. Record the closest reproducible definition and the residual mismatch, if any; do not force a match.
6. Build a compact historical-margin cache containing only the NIFTY contracts/17 strike candidates needed by this research rather than committing raw multi-GB SPAN archives.
7. Rerun the full 17-strike selection using exact/reconstructed margin-required percentage where coverage permits.
8. Compare maximum percentage selection versus maximum ₹ flatline-value selection.

Exit criteria:
- screenshot-date calibration report completed;
- reproducible margin calculation code and manual workflow committed;
- exact historical margin denominator used for any rerun is documented;
- downstream performance results are either rerun with the calibrated denominator or explicitly marked as proxy results.
## Phase 7A completion rule

Phase 7A is complete when the platform denominator is calibrated, historical SPAN coverage is demonstrated, all candidates capable of exceeding 2.5% are reconstructed, the ±400 rule is enforced, and an exact qualifying trade ledger is produced. This has now been achieved: 4 i1 primary trades, 3 settlement-file sensitivity trades.

## Phase 7B — Weekly decision cadence and strike-scan semantics

**Branch:** phase-7B-weekly-cadence

User clarification now treated as the primary operational interpretation: **scan once per weekly trading cycle, evaluate all 17 common strikes from ATM-400 to ATM+400, choose the strike with the maximum estimated equal max-profit=max-loss value among candidates that satisfy the >2.5% platform percentage gate, and trade that selected strike for that week. If no strike satisfies the gate, do not trade that week.**

Critical distinction:
- scanning every week does not imply a trade every week;
- the 2.5% gate decides whether that week's selected candidate is tradable;
- the current Phase 7A '4 trades' figure counts qualifying historical observations under the available dataset/margin reconstruction and must not be described as the number of weekly scans performed.

Before the weekly result is treated as final, the backtest must map each weekly expiry cycle to exactly one entry observation without look-ahead. The exact weekly entry day/time must not be invented; it must come from the user's documented execution convention or the dataset's actual observation schedule.

## Phase 7B correction — user's latest rule

The 2.5% threshold is **removed from the strategy**. Margin reconstruction remains a research capability but is no longer part of trade eligibility.

Operational rule:
- every weekly cycle is scanned;
- evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point increments;
- only a positive/all-green flatline qualifies;
- select the candidate with the maximum positive estimated equal max-profit=max-loss value;
- do not use a 2.5% gate, margin percentage, or buy-premium denominator;
- there is no intentional skip caused by a percentage threshold.

The weekly implementation uses one observation per near-expiry weekly cycle. The primary implementation uses the first available 09:20 observation in that cycle, with the last available observation reported as a timing sensitivity. This makes the weekly cadence explicit without using future information.

## Phase 7B operational definition

The primary no-look-ahead implementation is **first positive opportunity per weekly expiry cycle**: scan the 17 common strikes at each available 09:20 observation in chronological order; when at least one candidate has a positive all-green flatline, select the strike with the maximum positive flatline and trade it; then stop scanning that weekly cycle. This produces exactly one trade per weekly cycle without a 2.5% threshold or margin gate. `max_in_week` is retained only as an ex-post oracle sensitivity.


## Phase 7B final protocol

The final strategy removes the 2.5% threshold, margin percentage filter and buy-premium denominator. Each weekly expiry cycle is scanned chronologically at available 09:20 observations across the 17 common strikes ATM-400..ATM+400. The first observation with any positive/all-green flatline is the entry observation; at that observation, trade the candidate with the maximum positive estimated equal max-profit=max-loss value. This produces one trade per historical cycle in the cached sample with no look-ahead and no threshold-based skips.

`max_in_week` is retained only as an ex-post oracle sensitivity and is not used for the primary result.
