# Research plan — Options-Payoff-v1

**Version:** 2.3  
**Plan status:** Updated 2026-09-27 to add Phase 9H bounded loss-trade entry perturbation analysis without changing the frozen H1 candidate rule.

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

## Phase 7C — Entry-feature / Greek discrimination analysis

Objective: determine whether observable entry parameters differ systematically between profitable and unprofitable selected trades, and whether any such parameter can improve **entry-strike selection** within the 17-strike ATM-400..ATM+400 candidate grid.

Feature families:
- individual-leg implied volatility and Greeks (delta, gamma, vega, theta/day) for all four legs;
- signed aggregate strategy Greeks and absolute Greek imbalance;
- IV term structure (next-expiry IV minus near-expiry IV) and call-put skew for each expiry;
- strike moneyness and absolute moneyness;
- positive flatline magnitude and normalized flatline size.

Greek construction: Black-Scholes implied-volatility inversion from the observed option close, with r=0 and q=0 and expiry time fixed at 15:30 IST. These are **research proxies**, not a claim to reproduce Sensibull's proprietary inputs exactly. The r/q assumption is tested as a modelling limitation, not treated as observed truth.

Statistical plan:
1. At the 63 actual weekly decision observations, compare winning and losing selected trades with Welch's t-test, Mann-Whitney U, and Cliff's delta.
2. Control the univariate multiple-comparison family with Benjamini-Hochberg FDR.
3. At each weekly decision, evaluate every positive candidate's entry features and realized net P&L; compute within-week Spearman associations.
4. Test alternative one-feature strike selectors (max/min each feature) against the baseline maximum-flatline selector using paired weekly differences and bootstrap 95% intervals.
5. Treat all feature selection findings as exploratory until out-of-sample confirmation is run.

Entry-selection criterion for any follow-on feature hypothesis: it must be observable at entry, operate inside the same 17-strike grid, survive transaction costs, and show stability under time-split/out-of-sample validation.
## Phase 7C completion rule and result

Phase 7C is complete when entry Greeks/IV/moneyness are compared between winners and losers, candidate-level within-week relationships are tested, alternative single-feature strike selectors are benchmarked against the maximum-positive-flatline rule, and at least one time-split/walk-forward test is completed. These criteria are met in workflow 36291838252.

Result: none of the tested Greek/IV/moneyness features survives the multiple-comparison evidence threshold, all full-coverage simple alternative selectors underperform the baseline, and the best training-selected Greek/IV selector underperforms the baseline in both expanding walk-forward test blocks. **No new feature is adopted into the primary strategy.**

## Phase 8 — Predictability of the cross-expiry (S_2-S_1) component

Rationale: the Phase 7B decomposition showed that the static positive flatline was largely offset by the realized cross-expiry settlement difference. Phase 8 tests whether an **entry-time estimate** of (S_2-S_1) can improve the weekly trade decision.

### Phase 8A — Internal information baseline

Target: (S_2-S_1) per index point for each weekly cycle.

Predictors available at entry only:
- selected candidate and positive-candidate surface IV/Greek summaries;
- moneyness and flatline state;
- NIFTY spot at entry and entry-to-entry spot change;
- calendar variables;
- lagged realized (S_2-S_1) from completed prior weekly cycles.

Models:
- ridge regression;
- random forest regression;
- histogram gradient boosting regression.

Validation:
- expanding walk-forward, one week ahead;
- initial training window 31 weeks;
- 32 strictly out-of-sample weeks;
- target prediction error and sign accuracy;
- economic trade filters using predicted (S_2-S_1), with the existing transaction-cost model.

Predefined trade filters:
1. predicted (S_2-S_1>0);
2. expected total trade P&L (=) observed static flatline + predicted (S_2-S_1	imes lot - modeled costs >0).

No threshold is tuned on the out-of-sample results.

### Phase 8B — External market-state expansion

Only if the internal-information baseline gives evidence of useful predictability, add point-in-time external variables that can plausibly forecast the cross-expiry move: NIFTY futures basis, India VIX/volatility regime, global index futures, USD/INR, gold, FII/DII flow, option OI/volume and relevant news/event regime indicators. External data must be cached in the repository and joined strictly by information availability time.

### Phase 8 stop rule

Do not declare (S_2-S_1) useful unless the walk-forward predictor improves the existing weekly strategy after costs and remains stable across time blocks. If it does not, the research should document the negative result and stop this branch rather than endlessly searching for predictors.


## Phase 8A completion rule and result

Phase 8A is complete when:
- the future (S_2-S_1) target is defined without ambiguity;
- entry-only predictors are constructed;
- expanding walk-forward prediction is performed;
- the resulting trade filter is evaluated after transaction costs;
- chronological stability and bootstrap uncertainty are reported.

These criteria were met in workflow 36293974453.

Result:
- the all-timestamp design used 905 historical entry timestamps from 255 weekly cycles for training and produced 43 strictly out-of-sample weekly decision cycles after the initial 31-cycle training window;
- out-of-sample sign accuracy was only 44.2% (Ridge), 51.2% (Random Forest), and 53.5% (Histogram Gradient Boosting);
- the best model AUC was about 0.541;
- the Random Forest filter's apparent +₹102,022 OOS improvement versus the negative baseline was unstable across chronological blocks and its paired bootstrap 95% CI included zero;
- therefore **no S2-S1 predictor/filter is adopted**.

Per the predefined stop rule, Phase 8B external-variable expansion is not promoted unless a materially larger independent dataset or a new predeclared information source becomes available. The current branch is therefore treated as a completed negative/insufficient-evidence result rather than an invitation to keep optimizing predictors.


## Phase 9A — Correct exit semantics: close all four legs at near expiry

**Branch:** phase-9-near-expiry-exit-correction

### Critical protocol correction

The user's actual execution convention is now explicit: all four legs are closed at the near weekly expiry. The two near-expiry options expire/settle naturally; the two far-expiry options are manually squared off at the near-expiry close.

The previous backtest implementation did not model this. It used the far-expiry settlement (`next_settlement`) to value the far CE/PE legs. That corresponds to holding the far options to their own expiry, not manually closing them at the near expiry.

Therefore the previous realized-P&L ledgers and analyses that depend on them are **superseded/invalid for the user's actual execution rule** and must not be used to accept or reject the strategy.

### Correct near-expiry-close P&L

Let Q_C(T1) and Q_P(T1) be the observed market prices used to manually close the far-expiry call and put at the near-expiry close. Before costs:

P&L(T1) = C1 - P1 - Cfar + Pfar + (K - S1) + Q_C(T1) - Q_P(T1)

where K-S1 is the combined expiry payoff of the near short-call/long-put pair.

This must replace the prior `C1-P1-C2+P2+(S2-S1)` formula for the operational strategy.

### Required data

The corrected backtest needs point-in-time far-expiry option prices at the near-expiry exit timestamp. Entry prices alone and far-expiry settlement prices are insufficient.

The workflow must:
- identify the exact near-expiry exit timestamp convention;
- obtain/derive the far CE and far PE exit prices at that timestamp;
- apply the same execution/slippage model to far-leg manual exits;
- apply all exchange/broker/tax costs to the additional exit transactions;
- preserve the entry-time positive-flatline selection rule without look-ahead;
- independently audit all 63 historical weekly cycles before any new conclusion.

### Impact assessment

The following are frozen until the corrected exit backtest is complete:
- Phase 7B net P&L and win/loss statistics;
- Phase 7B economic decomposition based on S2-S1;
- Phase 7C winner/loser and selector studies, because they use the old realized P&L labels;
- Phase 8A S2-S1 prediction/filter study, because its target/economic evaluation was based on holding the far legs to far expiry;
- any final deployment conclusion derived from those realized-P&L results.

The entry-time static flatline calculation itself remains a valid description of the one-dimensional chart metric, but it is not evidence about the corrected near-expiry-exit P&L.

### Phase 9A stop rule

Do not run far-expiry H=2/H=3 selection yet. First reproduce the corrected H=1 strategy with the exact near-expiry manual-close convention. Only after the corrected H=1 baseline is established should H=2/H=3 be compared.


## Phase 9A execution-cost calibration amendment

Because the user explicitly requires Paytm Money costs, the corrected H1 validation must distinguish the strategy P&L from a broker-specific implementation layer. The current Paytm Money F&O FAQ states ₹10 brokerage per executed unique F&O order (checked 27-Sep-2026). Paytm Money also has older published material showing a ₹20 flat brokerage regime for newer accounts from 15-Jan-2025. Therefore the primary corrected ledger retains the repository's ₹20/order conservative assumption for continuity, but Phase 9B must run a broker-cost sensitivity at ₹10/order and document the account-era ambiguity rather than silently treating either rate as universal. Official/current Paytm Money source: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web


## Phase 9E — Frozen-rule H1 validation

**Branch:** phase-9E-h1-validation

This phase is a rule-frozen validation layer on top of the authoritative Phase 9D corrected intraday H1 reconstruction. It does not alter the strategy.

### Validation protocol

1. Consume only the archived Phase 9D H1 evidence from run 36302077730.
2. Verify the 169 complete realized trades and retain the 3 incompatible-lot selections only as audit exclusions.
3. Recheck the frozen invariants: positive/all-green selected chart, chronological entry/exit ordering, and no far-leg exit after near expiry.
4. Produce calendar-year cohorts for 2021–2026.
5. Produce anchored chronological holdout diagnostics for 2022–2026 with no test-period parameter tuning.
6. Estimate mean-P&L uncertainty with 20,000 IID and 20,000 circular four-trade block bootstrap resamples.
7. Reproduce predefined slippage and brokerage sensitivity already evaluated in Phase 9D.
8. Report descriptive entry-time and strike-shift diagnostics without adopting any new filter.
9. Write the validation report, machine-readable outputs, workflow artifact, and phase logs.

### Interpretation rule

A positive historical point estimate with an uncertainty interval crossing zero is classified as historically positive but statistically uncertain. The 100% chart-positive selection-condition rate is never interpreted as realized win rate. Because the 2021–2026 sample was already observed during strategy development, these diagnostics are temporal/rule-frozen validation rather than a pristine future-data holdout. A genuinely independent holdout requires new untouched market data.

### Exit criteria

- validation results reproducibly generated from the Phase 9D artifact;
- annual and anchored chronological outputs present;
- bootstrap uncertainty reported;
- execution sensitivity reported;
- limitations and data-contamination caveat documented;
- no strategy rule changes made during validation.

H2/H3 far-expiry selection remains frozen until Phase 9E concludes.


## Phase 9F — Corrected H1 cross-market and regime audit

**Branch:** `phase-9F-regime-crossmarket-audit`

Phase 9F is a non-optimizing descriptive audit of the corrected H1 trade ledger. It will join point-in-time market context from NSE/India VIX, FII/FPI and DII, BSE/Sensex, USD/INR, gold, global equity indices and global volatility. Any subgroup association remains hypothesis-generating and cannot change the trade rule inside this phase.

Exit criteria: reproducible context join for the 169 complete trades, source/coverage audit, predeclared regime summaries, dependence-aware uncertainty, explicit limitations, and no strategy-rule changes. H2/H3 remains frozen until Phase 9F completes.


## Phase 9F exit record

Phase 9F is complete. The 169-trade H1 ledger was joined to point-in-time NIFTY/India VIX, Sensex and global cross-market context without changing the trading rule. Sparse FII/DII data were excluded from inference. No continuous association survived BH correction at 5%. The only material robustness observations were descriptive: weaker economics in the highest India-VIX quartile and a difference by NIFTY-vs-Sensex relative performance. No filter adopted.

## Phase 9G — H2/H3 far-expiry selection research

**Status:** executing on branch `phase-9G-h2-h3-far-expiry-selection`. The corrected run 27 reconstruction is the operative Phase 9G execution.

The H1 entry rule, first-positive timestamp logic, 17-strike ATM-400..ATM+400 grid, near-expiry manual-close exit convention, 0.25% premium slippage, broker-cost sensitivity and statutory cost model remain fixed. Phase 9G will test the research question left frozen by earlier corrections: whether the choice of the far expiry beyond the near weekly expiry changes realized economics when the far CE/PE are manually closed at near expiry.

The phase must be run as a preregistered comparison of predefined H2/H3 candidate expiry horizons, with no future-data selection, separate yearly/chronological diagnostics, execution-cost sensitivity and multiple-testing correction where candidate selectors are compared. No regime insight from Phase 9F can become an entry filter inside Phase 9G.


### Phase 9G execution checkpoint — 2026-09-27
Run **36313815542** is frozen at commit **63b399a9a1d631316dd5233bc684a4ee0a197b25**. The execution uses the exact 17 unique shifts from -400 to +400 in 50-point increments, rejects conflicting duplicate quote groups, and scans later timestamps when an earlier timestamp is incomplete. H1 completeness passed; yearly H1/H2/H3 reconstruction is still running. Acceptance remains blocked until realized ledgers, paired horizon comparisons, cost sensitivity, multiple-comparison controls, and selection-behaviour diagnostics are all generated and audited.


### Phase 9G-S — H2/H3 source validation gate
**Status:** opened after a reproducible source-coverage defect was identified.

Before any H2/H3 performance inference, the source must be able to reconstruct all four option legs for the selected far expiry at the same intraday entry timestamp and support the exact 17-strike ATM-400..ATM+400 universe. The current Hugging Face source fails this gate for far-rank 2 and 3 because its expiry-partitioned files do not overlap the required pre-entry dates.

Candidate replacement-source classes now recorded for validation include:
1. A full-chain 1-minute archive claiming every NIFTY strike and every live expiry from June 2021–September 2026.
2. The rissin/nse-options-intraday Hugging Face dataset, which exposes expiry, strike and option type in its 1-minute intraday track from October 2024 onward.
3. The SauMStats NIFTY market-data engine / 2024 Kaggle raw archive plus 2026 live data, to be tested for actual far-expiry pre-entry coverage.
4. Authenticated broker/API archives such as ICICI Breeze-derived pipelines or MoneyTicks where legally available.

Acceptance gate: source coverage must be demonstrated on representative predeclared weekly cycles before any horizon comparison is pooled. If multiple sources are needed, source provenance and measurement heterogeneity must be analyzed explicitly rather than silently mixing them.


## Phase 9G final exit record — 2026-09-27

**Status: COMPLETE.**

Primary frozen reconstruction run 36313815542 completed all six yearly jobs. Corrected merge run 36320697995 accepted the six frozen yearly artifacts.

Primary-source H1 acceptance result:
- 131 complete realized trades.
- ₹71,868.76 net P&L at 0.25% slippage and ₹20/order.
- 58.78% realized win rate.
- PF 2.29.
- ₹15,704.24 maximum drawdown.
- 100% static chart-positive selection rate, not 100% realized wins.
- H1 decision-time and selected-strike distributions persisted.

H2/H3 primary-source acceptance gate failed on data coverage, not economics: the far-rank-2/3 expiry partitions lacked the required pre-entry observations. Therefore H2/H3 are not assigned zero performance and are not used to choose a production horizon.

Independent Rissin reconstruction is retained only as source-sensitivity evidence. Its matched H2-H1 and H3-H1 results do not justify horizon promotion because source construction differs and there is no untouched holdout.

Phase 9G exit criteria are satisfied:
- exact 17-strike rule audited;
- yearly reconstructions complete;
- corrected pooled merge complete;
- annual cohorts persisted;
- execution sensitivity persisted;
- bootstrap uncertainty persisted;
- H2/H3 source coverage documented;
- cross-source sensitivity documented;
- error/activity logs updated;
- final manuscript and candidate specification published.

**Phase 9G decision:** retain the fixed H1 next-weekly-expiry rule as the research candidate; do not introduce dynamic H2/H3 switching. Proceed only to untouched forward-holdout and executable-quote validation before any deployment claim.


## Phase 9H — Loss-trade entry analysis

**Branch:** phase-9H-loss-entry-analysis

### Research question
For each realized H1 loss under the exact current 17-strike rule, could a change to entry timing or entry strike have turned that individual loss into a positive trade while leaving the payoff construction, H1 next-weekly horizon, near-expiry manual far-leg close and cost model unchanged?

### Predeclared bounded tests
1. Same-timestamp strike substitution across all 17 shifts, reported only as an ex-post upper bound.
2. Second exact-17 valid timestamp, keeping the maximum-positive-flatline selector.
3. First valid exact-17 positive timestamp at or after 15, 30, 60 and 120 minutes after the baseline decision.
4. Best later timestamp under the unchanged selector, labeled ex-post diagnostic.
5. Best later timestamp/strike across all candidates, labeled the strongest ex-post entry-only upper bound.

### Scientific controls
- Primary cost model remains 0.25% premium slippage and ₹20/order.
- No exit optimization is permitted in Phase 9H.
- No unbounded search over arbitrary entry times, strike rules, thresholds or market filters is permitted.
- Rescue counts are descriptive; a new rule may only be considered after full-sample comparison and later untouched holdout validation.
- Ex-post upper bounds cannot be adopted as trading rules.

### Phase 9H-A scope correction
The first implementation attempted to recompute every complete H1 cycle solely to obtain full-sample economics. This was unnecessarily expensive for the user's immediate research question. Phase 9H-A therefore focuses first on the 54 realized loss cycles only.

For each loss cycle, reconstruct all exact-17 positive decision timestamps and the 17-strike candidate surface needed to evaluate:
- same-timestamp strike substitution;
- second valid timestamp;
- 15/30/60/120-minute delays;
- unchanged-selector later entry;
- ex-post later timestamp/strike upper bound.

A counterfactual that rescues a loss is diagnostic only. If a bounded mechanism shows a sufficiently consistent pattern, a separate prospective full-sample validation phase will be opened before any strategy change.

### Outputs / exit criteria
- Per-loss rescue ledger covering all recoverable H1 loss cycles.
- Rescue counts and rescue P&L by predefined mechanism.
- Representative case-level details.
- Phase 9H loss-entry report and machine-readable CSV/JSON outputs.
- No rule adoption from ex-post rescue results alone.
- No recursive optimization loop.


## Phase 9H-A final exit record — 2026-09-27

**Status: COMPLETE.**

Accepted workflow: **36325328644**. Result persistence commit: **ec75cb20e8e23f0550f8d615e796eea815e3d161**.

The 54 realized H1 losses were reconstructed under the exact 17-strike rule and the frozen near-expiry manual-close cost model.

Primary findings:
- 54/131 complete H1 trades were net losses.
- 45/54 were already gross-negative before fees; 9/54 were gross-nonnegative but became net losses after modeled costs.
- Same-timestamp alternative strike rescued 6/54.
- Second valid timestamp rescued 8/54 among the 52 cycles with a second valid opportunity.
- Fixed 15/30/60/120-minute delays rescued 8/54, 7/54, 6/54 and 4/54 respectively.
- The union of same-timestamp strike substitution plus the bounded second/fixed-delay tests rescued 14/54 losses (25.9%).
- Ex-post best-later unchanged-selector rescued 31/54.
- Ex-post best-later/any-strike rescued 38/54.
- Even the strongest ex-post later-entry/strike test left 16/54 losses unrecovered.

No entry modification is adopted. Any prospective rule suggested by the loss audit must be tested on the full 131-trade population and then an untouched holdout. The research will not recursively optimize individual losses.


## Phase 9I — Top-two-positive-strike sizing variant

**Branch:** `phase-9I-top-two-strikes`

### Research question
Does adding the second-highest positive estimated equal Max Profit = Max Loss strike at the first valid exact-17-strike decision timestamp improve the historical H1 strategy relative to the frozen one-strike Phase 9G control?

### Variant definition
The variant preserves every frozen Phase 9G rule except position count:
- scan 09:20–15:29 across later trading days within the weekly cycle;
- require the complete 17 unique strike-shift universe ATM-400..ATM+400 in 50-point steps and no conflicting duplicates;
- enter at the first valid timestamp with at least one positive/all-green flatline;
- rank positive candidates by estimated equal Max Profit = Max Loss flatline;
- select the top two **distinct positive** strikes at that same timestamp when two positive candidates exist;
- use the unchanged four-leg H1 construction, near-expiry manual far-leg close and transaction-cost model.

This is not a forced-two-position rule. A cycle with only one positive candidate remains a one-position cycle. A forced second position with a non-positive second-ranked candidate must be tested as a separate future variant.

### Acceptance gates
1. Rank-1 reconstruction must reproduce the accepted 131-trade Phase 9G H1 control exactly before rank-2 inference is accepted.
2. Report rank-2 incremental P&L separately from combined weekly-cycle P&L.
3. Report realized position count, weekly-cycle count, win rate, profit factor, maximum drawdown and bootstrap uncertainty.
4. Report annual rank-2 contribution to assess temporal stability.
5. Do not replace the frozen one-strike control solely because total absolute rupee P&L changes with additional capital deployment.
6. No strategy adoption without a separate prospective/untouched validation design.

### Phase 9I final exit record — 2026-09-28

Phase 9I is complete. Final merge-only workflow **36429144740** accepted the six frozen yearly artifacts generated under the corrected Phase 9I implementation. The rank-1 component reproduced the 131-trade Phase 9G H1 control to numerical precision and exactly matched the accepted strike selections.

Accepted historical result for the top-two-positive variant:
- 131 weekly signal cycles;
- 67 cycles with a second realized positive candidate;
- 198 realized individual positions in total;
- top-two net P&L **₹60,418.42** versus top-1 control **₹71,868.76**;
- incremental second-strike contribution **-₹11,450.33** across 67 positions;
- top-two trade-level win rate **56.06%** and PF **1.61**;
- top-two maximum drawdown **-₹31,812.54** versus control **-₹15,704.24**;
- bootstrap 95% CI for mean rank-2 P&L: **₹-621.02 to ₹222.88**.

**Decision:** do not change the frozen Phase 9G one-strike strategy. The top-two-positive variant is retained as a completed historical sizing experiment. A forced exact-two-lot variant remains a separate, currently untested strategy definition.

Detailed report: [docs/PHASE9I_TOP_TWO_STRIKES.md](../docs/PHASE9I_TOP_TWO_STRIKES.md)
Machine-readable results: [results/phase9i_fast/summary.json](../results/phase9i_fast/summary.json)
Workflow: [36429144740](https://github.com/vishnuvcr/Options-Payoff-v1/actions/runs/36429144740)


## Phase 9I — Two-lot top-two-strike sizing experiment

**Branch:** phase-9I-top-two-strikes

Research question: If the accepted Phase 9G entry timestamp is held fixed, does entering two distinct strikes with the largest estimated equal Max Profit=Max Loss flatline values improve economic performance versus the one-strike control?

Design:
1. Freeze the accepted 131 Phase 9G entry timestamps and one-lot rank-1 selections.
2. Evaluate all 17 distinct ATM-400..ATM+400 strikes at each accepted timestamp.
3. Rank by estimated equal flatline value and select the top two distinct strikes.
4. Preserve the H1 near-expiry exit, execution assumptions, taxes, slippage and brokerage.
5. Compare literal top-two-every-week against the original one-strike control.
6. Separately report the sensitivity that requires the second strike to remain positive/all-green.
7. Do not adopt the two-lot rule without prospective/out-of-sample validation.

Exit criteria: exact rank-1 reproduction, complete top-two ledger, incremental P&L/cost/drawdown analysis, uncertainty summary, and documented adoption decision.

## Phase 10 — Strategy Refinement

**Branch:** `phase-10-strategy-refinement`  
**Status:** PLANNED / ACTIVE from 2026-09-29

Phase 10 moves from loss-specific diagnostics and unvalidated sizing changes to a bounded refinement program focused on execution quality, entry confirmation, scenario-aware strike selection, exit timing and risk-normalized sizing.

The authoritative detailed plan is [docs/PHASE10_STRATEGY_REFINEMENT_PLAN.md](../docs/PHASE10_STRATEGY_REFINEMENT_PLAN.md).

### Research questions
- Does an entry cost-to-edge / liquidity gate improve realized net expectancy?
- Does predeclared signal persistence (5/10/15/30 minutes) improve full-sample outcomes?
- Does a point-in-time stress-tested full-position selector outperform the static flatline selector?
- Does a predeclared earlier exit reduce tail losses from far-leg revaluation?
- Do controlled combinations survive chronological holdout without multiple-testing artifacts?
- Does concentrating size on rank 1 outperform adding rank 2 on a margin-normalized basis?

### Guardrails
No look-ahead; exact 17-strike completeness; unchanged H1 control; observed near-expiry far-leg exits; full transaction costs and slippage; full-population tests before loss-rescue conclusions; explicit validation/holdout; no indefinite ML search.

### Phase-exit rule
Phase 10 stops after the predefined 10G untouched chronological holdout. If no refinement survives, the Phase 9G H1 control remains the research candidate.
