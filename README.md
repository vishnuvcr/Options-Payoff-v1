# Options-Payoff-v1

> **CRITICAL RESEARCH STATUS — 2026-09-27:** The user's exit convention has been clarified: all four legs are closed at the **near weekly expiry**; the far-expiry CE/PE legs are manually squared off at that time. Repository audit found that the prior realized-P&L backtest instead valued the far legs at their **own far-expiry settlement**. Therefore the historical realized-P&L results in Phases 3–8 that depend on that exit convention are **superseded and must not be treated as evidence for the actual strategy**. A corrective H=1 backtest is being rebuilt on `phase-9-near-expiry-exit-correction`. The entry-time static flatline/strike-selection calculation remains a separate chart-metric hypothesis, but it is not a validated P&L result.

Research repository for testing the clarified cross-expiry NIFTY options strategy.

## Current status

**Phase 9E — frozen-rule H1 validation: COMPLETE; no new filter adopted**

Current operational rule:
- every weekly expiry cycle is scanned chronologically;
- at the first available observation where any candidate has a positive/all-green flatline, evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point steps;
- trade the candidate with the maximum positive estimated equal max-profit=max-loss flatline value;
- no 2.5% threshold, no margin percentage gate, and no threshold-based skipping.

Phase 7C tested reconstructed entry Greeks, IV term structure/skew, moneyness, and Greek imbalance against 63 weekly trades (36 winners, 27 losers). No tested feature remained robust after multiple-testing correction; simple feature-based strike selectors all underperformed the maximum-positive-flatline baseline; the best training-selected Greek/IV selector also underperformed it in both expanding walk-forward test blocks.

Phase 8A then tested whether the dominant economic term, future (S_2-S_1), could be predicted from entry-time information and used as a trade filter. The all-timestamp walk-forward design used 905 prior entry timestamps across 255 weekly cycles for training and 43 strictly OOS weekly decision cycles. Predictive sign accuracy was only 44.2% (Ridge), 51.2% (Random Forest), and 53.5% (HGB). The strongest apparent economic improvement came from Random Forest, but its paired bootstrap 95% CI included zero and its chronological block performance was unstable.

Therefore **no S2-S1 filter is adopted**. The primary entry-strike rule remains unchanged.

### Historical comparator — superseded selection rule

Using the working buy-premium denominator, 0.25% slippage and ₹20/order brokerage:

- 891 eligible timestamps
- 63 trade rows across 52 distinct timestamps
- 24 ATM selections
- 39 fallback-grid selections
- total net P&L: **₹168,665.95**
- mean trade P&L: **₹2,677.24**
- median trade P&L: **₹6,831.26**
- win rate: **60.32%**
- profit factor: **1.37**
- maximum drawdown: **-₹194,854.37**

The 2.5% denominator remains an implementation assumption because it was not specified in the strategy description. A tested spot-notional denominator produced no qualifying trades across 1%–5% thresholds.

### Superseded phase runs

- Phase 2: 36255238050
- Phase 3 full-grid: 36262958536
- Phase 4 full-grid validation: 36263760476
- Phase 5 full-grid regime attribution: 36263974629

### Manuscript and outputs

- [Research manuscript](docs/MANUSCRIPT.md)
- [Research status](research/STATUS.md)
- [Research plan](research/RESEARCH_PLAN.md)
- [Error log](research/ERROR_LOG.md)
- [Activity log](research/ACTIVITY_LOG.md)
- [Phase 3 result snapshot](results/phase3_grid_summary.json)
- [Phase 4 validation snapshot](results/phase4_grid_validation_summary.json)
- [Phase 4 robustness](results/phase4_grid_robustness.csv)
- [Phase 4 brokerage sensitivity](results/phase4_grid_brokerage_sensitivity.csv)
- [Phase 5 regime summary](results/phase5_grid_regime_summary.csv)
- [Corrected figures](docs/figures/)

### Phase 7 interpretation

The payoff chart's green flatline is a static one-spot representation. The economic cross-expiry position has terminal exposure to S2-S1, so the flatline is not by itself evidence of risk-free arbitrage.

Phase 7 now tests the requested maximum-flatline-value selection. The earlier 63-trade result is preserved only as a historical comparator for the superseded rule.

Platform review: [Streak and Sensibull payoff semantics](docs/PAYOFF_PLATFORM_REVIEW.md).

Phase 7 workflow: [.github/workflows/phase-7-max-equal-selection.yml](.github/workflows/phase-7-max-equal-selection.yml).

The Phase 7A margin reconstruction remains in the repository as a platform-semantics research artifact, but the margin-based 2.5% gate is no longer part of the user's final strategy.

### Phase 7 empirical result — superseded proxy

The earlier 48-trade Phase 7 result used the legacy buy-premium denominator only. It is retained as a historical sensitivity and is **not** the final interpretation of the user's 2.5% platform rule.

Proxy result: 48 trades, ₹166,866.51 net P&L, 60.42% win rate, PF 1.56, max drawdown -₹124,060.72.

### Phase 7A margin calibration

The user's Sensibull screenshot shows a standalone margin of ₹88,076 for the exact four-leg 23450 strategy. Using NSE/NSCCL SPAN data for 25-Sep-2026, the reconstructed consolidated margin is ₹87,812.40, only 0.2993% below the screenshot. The other same-day intraday SPAN versions are also within 0.91% of the screenshot.

Therefore the 2.5% Max Profit % denominator is now empirically calibrated as **margin required**, not option premium:

- 2.5% of screenshot margin: **₹2,201.90**
- 2.5% of closest SPAN-reconstructed margin: **₹2,195.31**

Calibration report: [docs/MARGIN_RECONSTRUCTION.md](docs/MARGIN_RECONSTRUCTION.md)
Calibration data: [results/phase7a/margin_calibration_2026-09-25.json](results/phase7a/margin_calibration_2026-09-25.json)
Intraday comparison: [results/phase7a/margin_calibration_versions_2026-09-25.json](results/phase7a/margin_calibration_versions_2026-09-25.json)

Historical SPAN coverage is 100% across the 891 entry dates. The exact primary ledger and settlement-file sensitivity ledger are committed under `results/phase7a/`.
### Phase 7A exact historical result — superseded

The earlier exact-margin result used a >2.5% gate and produced **4 qualifying observations**. This is retained only as historical evidence because the user subsequently removed the 2.5% rule and margin gate.

- **₹42,680.17 net P&L**
- **75.0% win rate**
- **8.37 profit factor**
- **-₹5,791.42 maximum drawdown**
- **₹647.48 modeled costs**

Maximum estimated INR flatline value and maximum margin-based percentage select the same candidate on all four qualifying timestamps.

Settlement-file sensitivity produces 3 qualifying trades and ₹23,671.26 net P&L.

Full Phase 7A results: [docs/PHASE7A_RESULTS.md](docs/PHASE7A_RESULTS.md).

### Phase 7B — weekly cadence clarification

The user's operational rule is now interpreted as **one scan per weekly cycle** across all 17 common strikes (ATM-400..ATM+400). Among candidates with platform-style Max Profit % >2.5%, the highest estimated equal max-profit=max-loss value is selected; if none exceeds 2.5%, that week is skipped. The Phase 7A count of four is the number of qualifying historical observations under the exact-margin reconstruction, not the number of weekly scans. Phase 7B will map one non-look-ahead entry observation to each weekly cycle before producing a final weekly trade count.

### Phase 7B — final operational rule correction

The user's final rule is **not** a 2.5% rule. The 2.5% threshold and margin-based eligibility filter are removed.

Each weekly cycle scans all 17 common strikes from ATM-400 through ATM+400 in 50-point steps. Among candidates with a positive/all-green payoff flatline, the strike with the **maximum estimated equal max-profit=max-loss value** is selected and traded. There is no threshold-based weekly skipping.

Phase 7A's 4-trade result is therefore **superseded and must not be used as the final strategy result**. A new weekly-cadence backtest is being run on the cached candidate data.

### Phase 7B — corrected weekly result

The final rule now removes the 2.5% threshold entirely. The primary no-look-ahead interpretation is **first positive opportunity in each weekly expiry cycle**: scan all 17 strikes from ATM-400 through ATM+400, and when any positive/all-green flatline appears, trade the strike with the maximum positive flatline. No weekly cycle is skipped in the cached sample.

Preliminary baseline result: **63 weekly cycles, 63 trades, ₹-9,627.90 net P&L**, 57.14% win rate, ₹9,861.15 modeled costs. The `max_in_week` result is an ex-post oracle sensitivity and is not the primary backtest.


### Phase 7B final result

The 2.5% threshold and margin filter are removed. The final rule evaluates all 17 strikes from ATM-400 to ATM+400 in 50-point steps and selects the maximum positive/all-green flatline. The primary no-look-ahead operationalization is the first positive 09:20 opportunity in each weekly expiry cycle.

Result: **63 weekly cycles, 63 trades, 0 skipped weeks, ₹-9,627.90 net P&L** after 0.25% premium slippage and ₹20/order brokerage; 57.14% win rate, PF 0.98, max drawdown ₹-174,083.24, modeled costs ₹9,861.15.

The positive static chart component totaled ₹20,213.00, while realized cross-expiry S2-S1 contribution totaled ₹-19,979.75 before costs. IID 95% CI for mean weekly P&L: ₹-4,996 to ₹4,410; four-week block CI: ₹-4,024 to ₹4,739.

See [docs/PHASE7B_RESULTS.md](docs/PHASE7B_RESULTS.md) and [results/phase7b/summary.json](results/phase7b/summary.json).

### Phase 7C — Entry Greeks and feature discrimination

The current research is testing whether entry-time Greeks, IV term structure/skew, moneyness, and Greek imbalance differ between winning and losing trades and whether they can improve strike selection within the same 17-strike weekly grid. Features are treated as hypotheses only; multiple-testing correction, paired weekly bootstrap and out-of-sample validation are required before adopting any new selector.

### Phase 7C — Entry Greeks / feature selection conclusion

The winner-versus-loser study and candidate-level tests are complete. Across 63 weekly trades (36 winners, 27 losers), reconstructed entry Greeks, IV term structure/skew and moneyness show descriptive differences but **no robust feature survives multiple-testing correction**. Simple feature-based strike selectors all underperform the maximum-positive-flatline baseline, and the best training-selected Greek/IV selector underperformed it in both expanding walk-forward test blocks. No Greek-based strike filter has been added to the strategy.

Detailed report: [docs/ENTRY_FEATURE_GREEK_ANALYSIS.md](docs/ENTRY_FEATURE_GREEK_ANALYSIS.md) (workflow run 36291838252).

Compact Phase 7C outputs: [winner/loser Greek summary](results/phase7c/winner_loser_greek_summary.csv), [selector bootstrap comparison](results/phase7c/selector_bootstrap_summary.csv), and [walk-forward feature selection](results/phase7c/walk_forward_feature_selection.csv).

### Phase 8A — Predicting the cross-expiry S2-S1 component

The next research question is whether the future settlement difference (S_2-S_1), which dominated the economics of the current strategy, can be predicted from entry-time information. Phase 8A uses only cached internal option/surface/spot information with expanding one-week-ahead walk-forward validation. The predefined filters are predicted S2-S1 > 0 and expected trade P&L > 0 after modeled costs. External variables such as futures basis, India VIX, global markets, USD/INR, gold and FII/DII flows are reserved for Phase 8B only if the internal baseline shows predictive signal.


### Phase 8A — S2-S1 predictor conclusion

The S2-S1 term is the dominant economic risk component of the strategy, but it was not predictable robustly enough out of sample with the cached internal information. Random Forest improved the same-test OOS P&L from ₹-10,634.75 to ₹91,388.05 when filtering on predicted S2-S1 > 0, a +₹102,022.80 difference, but directional accuracy was only 51.16%, AUC 0.5136, and chronological block differences were +₹140,877, -₹58,226 and +₹19,372. The paired weekly bootstrap mean improvement was +₹2,372.62/week with a 95% CI of ₹-2,740.68 to ₹7,993.14.

This is treated as an unstable research signal, not a usable trading rule.

Detailed report: [Phase 8A S2-S1 results](docs/PHASE8_S2_S1_RESULTS.md)  
Compact model summary: [results/phase8/s2_s1_model_summary.csv](results/phase8/s2_s1_model_summary.csv)  
Chronological stability: [results/phase8/s2_s1_block_stability.csv](results/phase8/s2_s1_block_stability.csv)

### Final research conclusion

The current research does not validate a deployable trading edge for the final positive-flatline weekly strategy. The static green payoff chart is not sufficient because the actual cross-expiry economics are dominated by S2-S1. Phase 8A tested whether S2-S1 could be predicted from entry-time information, but out-of-sample directional accuracy remained close to chance and the apparent economic uplift was unstable across chronological blocks.

**No Greek filter and no S2-S1 filter has been added.**

Consolidated conclusion: [docs/FINAL_CONCLUSION.md](docs/FINAL_CONCLUSION.md).


## Phase 9A — Correct exit semantics

The corrected operational P&L for a selected strike is based on:

`entry cashflow + near-expiry intrinsic payoff + far-call market sale price at near expiry - far-put market repurchase price at near expiry - all costs`

The corrected backtest therefore requires point-in-time prices for the far-expiry options at the near-expiry close. Far-expiry settlement is not an acceptable substitute.

The H=2/H=3 far-expiry selection experiment is paused until the corrected H=1 baseline is completed.

## Phase 9D — Corrected intraday H1 baseline

The final operational interpretation is now implemented: **09:20 is the first check, not a skip gate**. Every available NIFTY 1-minute timestamp from 09:20 through 15:29 is checked; if no positive/all-green payoff exists, the scan continues later that day and across subsequent trading days in the same weekly cycle. At the first positive timestamp, all 17 strikes from ATM-400 through ATM+400 are evaluated and the maximum positive estimated equal Max Profit = Max Loss candidate is selected.

The authoritative H1 run is **36302077730**. It checked **448,280 intraday timestamps**, generated **17,606 decision-surface rows**, and selected **172 weekly-cycle entries**. Three entries had incompatible near/far expiry lot sizes and were retained in the audit but excluded from realized P&L, leaving **169 complete realized trades**.

At **0.25% premium slippage and ₹20/order brokerage**, the corrected near-expiry manual-close model produced:

- **Gross P&L:** ₹162,953.84
- **Modeled costs:** ₹37,265.02
- **Net P&L:** **₹125,688.82**
- **Realized win rate:** 63.91%
- **Profit factor:** 2.94
- **Maximum drawdown:** ₹16,200.65
- **Mean realized-trade P&L:** ₹743.72
- **Static chart-positive rate:** 100% (a selection-condition metric, not a realized win rate)

Execution sensitivity remained positive at 0.5% and 1.0% premium slippage and at ₹40/order brokerage in the tested historical sample. IID and four-trade block bootstrap intervals for mean realized-trade P&L were approximately ₹442–₹1,039 and ₹444–₹1,069 respectively.

Detailed report: [docs/PHASE9D_RESULTS.md](docs/PHASE9D_RESULTS.md)  
Compact summary: [results/phase9d/summary.json](results/phase9d/summary.json)  
Execution sensitivity: [results/phase9d/sensitivity.csv](results/phase9d/sensitivity.csv)  
Incomplete-selection audit: [results/phase9d/incomplete_selected_trades.csv](results/phase9d/incomplete_selected_trades.csv)

**Research status:** corrected H1 baseline complete; independent walk-forward/holdout validation is next. H2/H3 far-expiry selection remains frozen until that validation phase completes.


## Phase 9E — Corrected H1 validation

Phase 9E froze the corrected Phase 9D intraday strategy and validated the authoritative 2021–2026 ledger without changing the rule.

- Source workflow: **36302077730**; validation workflow: **36303117489**
- 172 selected weekly-cycle entries; 169 complete realized trades; 3 lot-size-incompatible selections retained in audit
- Net P&L at 0.25% premium slippage and ₹20/order: **₹125,688.82**
- Realized win rate: **63.91%**; Wilson 95% CI: **56.43%–70.76%**
- Profit factor: **2.94**
- Maximum drawdown: **₹16,200.65**
- IID bootstrap 95% CI for mean trade P&L: **₹441.82–₹1,039.55**
- Circular 4-trade block bootstrap 95% CI: **₹413.92–₹1,066.30**
- Every 2021–2026 calendar-year cohort and every anchored 2022–2026 test cohort was positive in this historical sample.
- Net P&L remained positive in the tested 0.00%, 0.25%, 0.50% and 1.00% slippage scenarios and at ₹10/₹20/₹40 brokerage.

Important limitation: these are **rule-frozen historical diagnostics, not a pristine future holdout**, because the 2021–2026 data was already observed during development. No new entry filter is adopted from Phase 9E.

Detailed report: [docs/PHASE9E_VALIDATION.md](docs/PHASE9E_VALIDATION.md)  
Machine-readable results: [results/phase9e/summary.json](results/phase9e/summary.json)  
Validation workflow: [.github/workflows/phase-9E-h1-validation.yml](.github/workflows/phase-9E-h1-validation.yml)

**Next:** a non-optimizing point-in-time cross-market/regime audit of the corrected H1 ledger; H2/H3 remains frozen until that audit completes.

## Phase 9F — Cross-market and regime audit COMPLETE

Phase 9F completed a descriptive, point-in-time contextual audit of the corrected H1 ledger without changing the trading rule.

- Workflow: **36304036908**
- 169 complete trades analyzed
- India VIX and NIFTY coverage: 100%; Sensex: 160/169
- FII/DII source had only 16 recoverable rows and was excluded from inference under strict recency controls
- Highest India-VIX quartile: 42 trades, **₹2,925.31 net P&L**, **₹69.65 mean/trade**, PF **1.10**, dependence-aware CI crossing zero
- Sensex-outperform group: **₹978.79 mean/trade**; NIFTY-outperform group: **₹411.26** — descriptive only
- No continuous market-context association survived BH correction at 5%
- No regime filter or global/FII-DII filter adopted

Detailed report: [docs/PHASE9F_RESULTS.md](docs/PHASE9F_RESULTS.md)  
Source/plan: [docs/PHASE9F_REGIME_CROSSMARKET_PLAN.md](docs/PHASE9F_REGIME_CROSSMARKET_PLAN.md)  
Machine-readable results: [results/phase9f/summary.json](results/phase9f/summary.json)  
Workflow: [.github/workflows/phase-9F-regime-crossmarket-audit.yml](.github/workflows/phase-9F-regime-crossmarket-audit.yml)

**Next:** H2/H3 far-expiry selection research is reopened on a separate preregistered branch; the H1 rule remains frozen while that research runs.


## Phase 9G — H2/H3 far-expiry selection COMPLETE — corrected primary result

Phase 9G is reconstructing fixed H1/H2/H3 far-expiry horizons on the corrected intraday rule, using 1-minute observations from 09:20–15:29 and near-expiry manual closure of far CE/PE. The predeclared comparison does not allow dynamic horizon switching and retains H1 as the control.

Active Actions runs: **36304489832** and **36304477026** (yearly H1/H2/H3 reconstruction). Earlier runs **36304359045** and **36304459132** failed before any accepted statistical result and are logged in the error register.

A pre-analysis schema audit also found that the execution-sensitivity stage currently passes an already-realized CSV back into a raw-input recalculation function. No sensitivity output is being accepted. The raw fields will be retained/reused before Phase 9G is declared complete.

Plan: [docs/PHASE9G_H2_H3_PLAN.md](docs/PHASE9G_H2_H3_PLAN.md)  
Phase status: [research/STATUS.md](research/STATUS.md)  
Error log: [research/ERROR_LOG.md](research/ERROR_LOG.md)


### Phase 9G correction checkpoint — 2026-09-27
The Phase 9G pipeline has been corrected before accepting results: quote-level fields are preserved through the realized ledger, a hard sensitivity schema gate is added, and first-positive/strike-selection behaviour is now included in the merger outputs. Corrected workflow run **36305850007** is queued. No H2/H3 conclusion has been accepted.


### H1 control behavioural baseline — 2026-09-27
The authoritative H1 control artifact (run 36302077730) shows materially non-ATM selection: among 169 complete realized trades, ATM was selected only once; the largest groups were -400 (35), -350 (28), -300 (18), +400 (19), and +350 (15). First-positive timing also extends well beyond the opening minute: 39 decisions occurred at 09:20, while 40 occurred after 13:20. See [Phase 9G H1 control selection analysis](docs/PHASE9G_H1_CONTROL_SELECTION.md) and [machine-readable strike distribution](results/phase9g_h1_control_shift_distribution.csv).


### Phase 9G execution checkpoint — run 10
Run **36307233038** is the accepted Phase 9G execution candidate. It includes the strict all-17-strike decision rule and the independent H1 completeness gate. Older run 36305850007 is obsolete and its output is excluded from final inference.


### Corrected execution trigger — 2026-09-27
The Phase 9G branch has been reset to concurrency group **v2** after the stale reconstruction process occupied the original group. This status update intentionally triggers the corrected workflow definition.


### Legacy H1 control superseded — 2026-09-27
The authoritative Phase 9D audit found the old 169-trade control did not consistently evaluate the exact 17-strike universe: only 45/172 selected timestamps had the complete prescribed set. The historical 169-trade result is therefore diagnostic only. The corrected Phase 9G reconstruction is the operative control.


### Phase 9G live reconstruction checkpoint — 2026-09-27
Run **36313815542** is the current corrected execution and remains **in progress** on the frozen exact-17-strike commit **63b399a9a1d631316dd5233bc684a4ee0a197b25**. The H1 completeness gate has completed successfully. All six yearly H1/H2/H3 reconstruction jobs have completed checkout, dependency installation and option-data caching and are currently in the reconstruction step. No yearly P&L, horizon comparison, sensitivity, or H2/H3 conclusion has been accepted yet.


### Phase 9G source-coverage finding — 2026-09-27
The corrected run has now completed 2024 and 2026 H1 reconstructions. Interim H1 results are 26 realized trades / ₹20,656.83 net for 2024 and 14 realized trades / ₹21,014.63 net for 2026, at the primary 0.25% slippage + ₹20/order cost model. These are interim yearly results only, not the pooled Phase 9G conclusion.

A dedicated H2/H3 data-coverage audit then found a source limitation in thetrademarkk/india-index-options-1m: across 152 sampled timestamps for each of far-rank 2 and far-rank 3, the far-expiry file had zero rows on the entry date, hence zero common CE/PE strikes and zero exact 17-shift surfaces. The expiry files typically start about eight calendar days before their own expiry, which is enough to cover H1 but not H2/H3 entry dates. This is documented in docs/PHASE9G_SOURCE_COVERAGE.md and results/phase9g_h2_h3_source_coverage_audit.json.

Interpretation: H2/H3 zero counts from this source are a data-coverage limitation, not a strategy result. NSE currently specifies four weekly NIFTY 50 option expiries, so the absence of H2/H3 observations in this dataset cannot be interpreted as non-existence of the contracts. A source with pre-entry intraday quotes for every live expiry is required before H2/H3 inference is accepted.


### Phase 9G interim H1 control checkpoint — 2026-09-27
Three yearly corrected H1 reconstructions are now complete: 2021 = 14 realized trades / ₹9,732.04 net; 2024 = 26 realized trades / ₹20,656.83 net; 2026 = 14 realized trades / ₹21,014.63 net. Combined interim H1 = **54 realized trades / ₹51,403.50 net / 72.22% realized win rate** under 0.25% slippage + ₹20/order. This is **not the final Phase 9G result** until 2022, 2023 and 2025 finish and the full sensitivity/statistical audit is accepted.


### Phase 9G data-source and interim-control update — 2026-09-27
The completed corrected H1 ledgers for 2021, 2024 and 2026 were independently recomputed: **54 realized trades, ₹51,403.50 net P&L, PF 5.32, max drawdown ₹2,299.68, 72.22% realized win rate** under 0.25% slippage + ₹20/order. These are interim only; 2022/2023/2025 remain in reconstruction.

See [Phase 9G data-source decision matrix](docs/PHASE9G_DATA_SOURCE_DECISION_MATRIX.md).
### Phase 9G cross-source sensitivity finding — 2026-09-27
The same frozen H1 rule produces materially different measured economics across the two tested datasets: 2024 HF-source H1 = ₹20,656.83 versus Rissin = ₹18,690.31; 2026 HF-source H1 = ₹21,014.63 versus Rissin = ₹58,226.92. This is treated as **source/measurement sensitivity**, not evidence that either vendor is superior. H2/H3 comparisons will therefore remain within-source and source provenance will be explicit. See [cross-source sensitivity](docs/PHASE9G_CROSS_SOURCE_SENSITIVITY.md).


## Phase 9G — FINAL CORRECTED RESULT — 2026-09-27

The exact-17-strike Phase 9G reconstruction is complete on the frozen primary-source run **36313815542**. All six yearly reconstruction jobs succeeded. The original pooled merge failed only because an empty incomplete CSV was passed to pandas; the aggregation was repaired without rerunning any market-data reconstruction. Corrected merge workflow **36320697995** succeeded.

### Primary H1 result

- **131 complete realized trades**
- **₹71,868.76 net P&L**
- ₹100,816.81 gross P&L
- ₹28,948.05 modeled costs
- **58.78% realized win rate**; Wilson 95% CI 50.22%–66.84%
- **Profit factor 2.29**
- **₹15,704.24 maximum drawdown**
- Mean trade P&L ₹548.62
- IID bootstrap 95% CI for mean ₹212.77–₹867.02
- Four-trade block bootstrap 95% CI ₹199.66–₹872.13
- **100% static chart-positive rate**, which is not a 100% realized win rate

### Selection behaviour

- Median first-positive decision delay: **210 minutes after 09:20**
- P90 delay: **357 minutes**
- ATM selection: **0%**
- Median selected shift: **-250 points**
- Mean absolute shift: **329.4 points**

The result therefore confirms that the exact rule is not equivalent to an ATM-only or 09:20-only strategy.

### H2/H3 status

The primary Hugging Face source cannot adjudicate H2/H3 because the far-rank-2 and far-rank-3 expiry partitions lack pre-entry intraday observations. This is a source-coverage limitation, not a zero-performance result. No H2/H3 horizon is promoted.

An independent Rissin source produced positive same-source paired H2-H1 and H3-H1 differences, but these are retained only as source-sensitivity evidence because of source-construction differences, partial coverage and lack of untouched holdout validation.

### Execution sensitivity

The primary H1 result remains positive through 0.50% modeled slippage at all tested ₹10/₹20/₹40 brokerage levels. At 1.00% slippage it remains positive at ₹10 and ₹20 brokerage, but is negative at ₹40 brokerage.

### Final conclusion

**The current H1 rule has positive historical net P&L after modeled costs, but it does not have a 100% realized win rate. H2/H3 remain unadjudicated on the primary source. No dynamic horizon-switching rule is adopted.**

Detailed final report: [docs/PHASE9G_FINAL_RESULTS.md](docs/PHASE9G_FINAL_RESULTS.md)  
Candidate specification: [docs/PHASE9G_CANDIDATE_STRATEGY_FINAL.md](docs/PHASE9G_CANDIDATE_STRATEGY_FINAL.md)  
Final summary: [results/phase9g/final_summary.json](results/phase9g/final_summary.json)  
Annual results: [results/phase9g/annual_summary.csv](results/phase9g/annual_summary.csv)  
Execution sensitivity: [results/phase9g/execution_sensitivity.csv](results/phase9g/execution_sensitivity.csv)  
Strike distribution: [results/phase9g/H1_strike_shift_distribution.csv](results/phase9g/H1_strike_shift_distribution.csv)  
Merged workflow artifact: [GitHub Actions run 36320697995](https://github.com/vishnuvcr/Options-Payoff-v1/actions/runs/36320697995)


## Phase 9H — Loss-trade entry analysis — OPEN

The frozen Phase 9G H1 strategy is now being stress-tested specifically through its realized losing trades. The objective is not to optimize the strategy freely, but to answer a bounded question: could an observed loss have been turned profitable by changing only the entry strike or entry time?

Predeclared tests:
- same-timestamp alternative strike across all 17 shifts;
- second valid exact-17 timestamp;
- 15/30/60/120-minute entry delays;
- ex-post later-entry upper bounds, clearly labeled non-deployable.

No exit optimization or new market filter is introduced. Results will be compared on the full sample before any candidate change can be considered.

Plan: research/RESEARCH_PLAN.md
Status: research/STATUS.md
Error log: research/ERROR_LOG.md
Workflow: .github/workflows/phase-9H-loss-entry-analysis.yml


## Phase 9H-A — targeted loss-cycle analysis — OPEN

The first Phase 9H implementation was narrowed to the 54 realized losing H1 trades. For each loss, the research reconstructs exact-17 valid timestamps and all 17 candidate strikes needed to test whether changing only the entry could have produced a positive realized outcome.

No exit rule, horizon, cost model, or market filter is being changed. Any rescue result is an ex-post diagnostic; it is not a trading rule until a separate prospective full-sample and untouched-holdout test supports it.
