# Research status

**As of:** 2026-09-29  
**Active branch:** phase-10C-scenario-aware-selection
**Overall status:** Phase 10C COMPLETE — scenario-aware strike selection tested; frozen one-strike Phase 9G H1 control retained

| Phase | Status | Corrected evidence |
|---|---|---|
| 0 Governance | COMPLETE | Repository plan, instructions, logs and sources maintained. |
| 1 Specification | COMPLETE | Four-leg algebra and flat-chart vs cross-expiry payoff distinguished. |
| 2 Data | COMPLETE | Run 36255238050 supplied the core NIFTY index/options dataset. |
| 3 Backtest | COMPLETE | Run 36262958536 implemented ATM first, then every 50-point shift from -500 to +500; 63 trade rows, 52 entry timestamps. |
| 4 Validation | COMPLETE | Run 36263760476 completed uncertainty, walk-forward, threshold, slippage, denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Run 36263974629 completed point-in-time trend/volatility/entry-move attribution. |
| 6 Manuscript | COMPLETE | Corrected manuscript and figures added. |
| 6A Loss audit | COMPLETE | Workflow 36264710663 audited all 63 selected rows directly from the Phase 3 artifact. |
| 7 Payoff semantics + maximum-flatline selection | COMPLETE | 48-trade primary ledger evaluated; robustness, loss decomposition, slippage sensitivity and regime attribution completed. |

## Historical comparator — superseded selection rule

Working implementation assumptions:

- 2.5% trigger denominator: sum of the two long-option premiums (not explicitly specified by the user)
- slippage: 0.25% per option premium
- brokerage: ₹20 per executed order
- historical lot size by expiry
- 09:20 close proxy for option execution
- exit at expiry

Results:

- 891 eligible entry timestamps
- 63 selected four-leg trade rows
- 52 distinct selected timestamps
- 24 ATM trades
- 39 fallback-grid trades
- total net P&L: ₹168,665.95
- mean trade P&L: ₹2,677.24
- median trade P&L: ₹6,831.26
- win rate: 60.32%
- profit factor: 1.37
- maximum drawdown: -₹194,854.37

## Loss-trade audit result

- 38 winning rows
- 25 losing rows
- 25/25 losing rows were already negative before modeled fees
- 0/25 losses were caused solely by fees
- 7 losses were ATM and 18 were fallback-grid selections
- losing rows contributed -₹454,335.44 against +₹623,001.39 from winners
- total modeled costs on losing rows: ₹3,557.82
- largest loss: -₹55,420.58
- worst concentration: 2022-05-30 through 2022-06-07, -₹194,854.37

The audit shows that the positive chart trigger did not guarantee positive realized cross-expiry economics. Every loser passed the trigger.

## Key validation findings

- iid bootstrap 95% CI for mean trade P&L: -₹2,750 to ₹7,903.
- weekly block-bootstrap 95% CI: -₹5,628 to ₹9,958.
- chronological train segment: 45 trades, -₹50,828.
- chronological test segment: 18 trades, +₹219,494.
- 2.5% buy-premium result remains positive through 1% slippage; net P&L falls from ₹174,021 at 0% slippage to ₹152,600 at 1%.
- brokerage sensitivity remains positive at ₹10, ₹20 and ₹40/order.
- tested spot-notional denominator produced no qualifying trades from 1% through 5% thresholds.

## Reproducibility correction

The authoritative 63-row result is from branch phase-3-strike-grid and run 36262958536. The earlier stale run_backtest.py on phase-6-manuscript-grid was corrected in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4.

## Phase 7 outputs

- docs/MANUSCRIPT.md
- docs/LOSS_TRADE_ANALYSIS.md
- results/phase3_grid_summary.json
- results/phase4_grid_validation_summary.json
- results/phase4_grid_robustness.csv
- results/phase4_grid_brokerage_sensitivity.csv
- results/phase5_grid_regime_summary.csv
- docs/PAYOFF_PLATFORM_REVIEW.md
- .github/workflows/phase-7-max-equal-selection.yml


## Phase 7 specification

Primary rule:
- candidate strikes: ATM-400 to ATM+400 in 50-point steps, including ATM;
- selection: one candidate per timestamp, maximizing the positive estimated equal max-profit=max-loss flatline value;
- primary score: estimated equal max-profit=max-loss value in INR;
- 2.5% legacy percentage gate: sensitivity only, because the exact platform margin denominator has not yet been reconstructed.

The previous 63-trade result is preserved as historical evidence for the superseded ATM-first/full-grid fallback rule and must not be reported as the Phase 7 result.


## Phase 7 primary result

- grid timestamps: 905
- eligible timestamps after legacy 2.5% proxy gate: 48
- selected trades: 48
- net P&L: ₹166,866.51
- mean trade P&L: ₹3,476.39
- median trade P&L: ₹6,242.51
- win rate: 60.42%
- profit factor: 1.56
- maximum drawdown: -₹124,060.72
- largest loss: -₹55,321.89
- largest win: ₹35,233.55
- modeled costs: ₹7,334.77

## Phase 7 robustness

- iid bootstrap 95% CI for mean: -₹1,943.61 to ₹8,927.91
- weekly block bootstrap 95% CI: -₹3,672.56 to ₹9,932.60
- chronological 70/30: train ₹18,711.33; test ₹148,155.17
- net P&L at 0%, 0.25%, 0.50%, 1.00% slippage: ₹171,346.72; ₹166,866.51; ₹162,386.29; ₹153,425.87

## Phase 7 economic decomposition

- total static flatline P&L: ₹36,138.75
- total realized S2-S1 contribution: ₹142,545.00
- losses: 19
- losing contribution: -₹299,970.18
- loss-side S2-S1 contribution: -₹309,305.00
- 19/19 losses negative before fees
- 0 fee-only losses

See docs/PHASE7_RESULTS.md for detailed results and interpretation.
## Phase 7A status

Calibration target: Sensibull standalone margin ₹88,076 for the screenshot-identifiable 25-Sep-2026 NIFTY 23450 four-leg position, one 65-unit lot. SPAN-based reconstruction calibrated the consolidated margin to ₹87,812.40 (0.2993% below the screenshot). Historical SPAN i1 and s coverage was 100% for all 891 entry dates. See `.github/workflows/phase-7A-margin-reconstruction.yml` and `docs/PHASE7A_RESULTS.md`.

## Phase 7A calibration result

- Sensibull screenshot standalone margin: ₹88,076.00
- Reconstructed consolidated SPAN+exposure margin from NSE 25-Sep-2026 i05 SPAN: ₹87,812.40
- Difference: -₹263.60 (-0.2993%)
- i03 version: ₹87,723.22 (-0.4005%)
- i04 version: ₹87,532.12 (-0.6175%)
- i02 version: ₹87,437.48 (-0.7250%)
- i01 version: ₹87,276.41 (-0.9078%)
- The exact margin method is therefore calibrated to within 1% of the screenshot.
- 2.5% of the observed ₹88,076 margin = ₹2,201.90; 2.5% of the closest reconstructed ₹87,812.40 = ₹2,195.31.

The remaining Phase 7A task is historical margin reconstruction for all backtest entry dates/strikes. The screenshot denominator itself is now resolved.
## Phase 7A exact result

- Strategy range: ATM-400..ATM+400 in 50-point steps
- Historical margin denominator: NSE/NSCCL SPAN-based margin required
- Primary snapshot: i1 begin-day SPAN, no look-ahead
- Exact qualifying i1 trades: 4
- i1 net P&L: ₹42,680.17
- i1 mean trade P&L: ₹10,670.04
- i1 win rate: 75.0%
- i1 profit factor: 8.37
- i1 max drawdown: -₹5,791.42
- i1 modeled costs: ₹647.48
- Maximum-value vs maximum-percentage selection: identical on all 4 qualifying timestamps

Settlement-file sensitivity produced 3 qualifying trades and ₹23,671.26 net P&L.

The earlier 48-trade/₹166,866.51 Phase 7 result used the superseded buy-premium percentage proxy and must now be treated only as a sensitivity/comparator.
## Phase 7B status

User clarification: the intended operation is one weekly scan across all 17 strikes (ATM-400..ATM+400) and, when at least one candidate exceeds 2.5%, trade the maximum candidate for that weekly cycle. The prior 4-trade number is not a count of weekly scans; it is the count of qualifying historical observations in the exact-margin dataset. Weekly-cycle mapping remains to be implemented without look-ahead.

## Phase 7B rule correction

The 2.5% rule is removed. Margin is no longer a trade-entry denominator. Every weekly cycle is scanned across ATM-400..ATM+400; the maximum positive/all-green flatline candidate is traded. No threshold-based skipping is used.

## Phase 7B preliminary result

The first-positive no-look-ahead rule produced 63 weekly cycles and 63 trades, with positive candidates in every cycle. Baseline net P&L is ₹-9,627.90 after 0.25% premium slippage and ₹20/order brokerage. Win rate 57.14%; modeled costs ₹9,861.15. This is the current primary result pending artifact-backed full statistical analysis.


## Phase 7B final result

- 63 weekly cycles
- 63 trades
- 0 skipped cycles
- positive candidate in every cycle
- net P&L ₹-9,627.90
- gross P&L ₹233.25
- modeled costs ₹9,861.15
- win rate 57.14%
- profit factor 0.98
- maximum drawdown ₹-174,083.24
- largest win ₹34,652.56
- largest loss ₹-55,786.13
- IID bootstrap 95% CI for mean weekly P&L: ₹-4,996 to ₹4,410
- four-week block bootstrap 95% CI: ₹-4,024 to ₹4,739

Phase 7A's four-trade margin-gated result is superseded by the user's latest positive-only rule.

## Phase 7C — Entry-feature / Greek analysis OPEN

The primary weekly rule is fixed: first positive observation in the weekly cycle, then maximum positive flatline across the 17 strikes. This phase tests whether entry Greeks, IV structure, moneyness, or other observable parameters contain additional strike-selection information. No feature is accepted as a new rule before out-of-sample validation.

## Phase 7C result

63 selected weekly trades contained 36 winners and 27 losers. Greek/IV/moneyness winner-loser differences were not robust after Benjamini-Hochberg correction (best q ≈ 0.435 among tested Greek/IV features). Every full-coverage single-feature selector tested underperformed maximum positive flatline. Walk-forward training selected near-expiry call-put IV skew (maximum) in both splits, but it underperformed the baseline by ₹100.98/week and ₹66.24/week respectively in the two 16-week test blocks. Primary strike-selection rule remains unchanged.

Reproducibility tables published under `results/phase7c/`; detailed methodology/results are in `docs/ENTRY_FEATURE_GREEK_ANALYSIS.md`. Phase 7C is frozen unless the primary rule or underlying data changes.

## Phase 8A — S2-S1 predictor analysis OPEN

Hypothesis: the cross-expiry settlement difference can be predicted sufficiently well from information available at the first-positive entry observation to improve the weekly trade/no-trade decision. The first test is deliberately internal-data-only; external market variables are reserved for Phase 8B if justified by the internal baseline.

## Phase 8A result

The economically important cross-expiry S2-S1 term is not predicted robustly enough to use as an entry filter. Across 43 strictly OOS weekly decision cycles, model sign accuracy was 44.2% (Ridge), 51.2% (Random Forest), and 53.5% (HGB). The strongest OOS filter uplift was Random Forest (+₹102,022.80 versus the same-test baseline), but chronological block results were +₹140,877, -₹58,226, and +₹19,372, and the paired bootstrap 95% CI was ₹-2,740.68 to ₹7,993.14. No filter adopted.

## Current phase matrix

| Phase | Current status | Key conclusion |
|---|---|---|
| 7A Margin reconstruction | COMPLETE / superseded | 2.5% margin denominator reconstructed but later removed from user's final rule. |
| 7B Weekly positive-only rule | COMPLETE | 63 weekly trades; net ₹-9,627.90 after modeled costs. |
| 7C Greeks / entry features | COMPLETE | No single Greek/IV/moneyness feature robust enough to adopt. |
| 8A S2-S1 predictability | COMPLETE | No sufficiently stable OOS S2-S1 filter; no predictor adopted. |
| 8B External variables | NOT PROMOTED | Predeclared stop rule prevents open-ended predictor search without stronger independent data. |
| 9H Loss-trade entry analysis | OPEN | Tests bounded entry-time/strike alternatives around realized H1 losses; no strategy change accepted yet. |

Current consolidated conclusion: **the final positive-flatline weekly strategy is not validated as a deployable edge under the cached historical implementation.** See `docs/PHASE8_S2_S1_RESULTS.md` and `docs/FINAL_CONCLUSION.md`.


## Critical correction — prior realized-P&L backtests superseded

**As of 2026-09-27, the user's exit convention was clarified:** all four legs are closed at the near weekly expiry; far-expiry CE/PE legs are manually squared off at that near-expiry close.

Repository inspection shows the prior backtest calculated:
`gross_pnl = entry_cashflow + next_settlement - near_settlement`
and calculated far-leg exit costs using intrinsic values at `next_settlement`.

That is a different strategy: it holds the far-expiry legs until their own expiry. It is not the user's manual near-expiry close convention.

Accordingly, **the prior realized-P&L results must be treated as superseded/invalid for the actual trading rule**. This affects Phase 7B P&L, Phase 7C winner/loser classification, and Phase 8A S2-S1 prediction/economic-filter results. The static entry flatline/selection calculation is retained only as an entry-chart hypothesis.

## Phase 9A status — OPEN

Primary task: rebuild the H=1 baseline using far-expiry option market prices at the near-expiry close, including manual exit slippage and all transaction costs. No H=2/H=3 research should be accepted until this corrected baseline is complete.


## Phase 9A execution checkpoint

The corrected code and regression tests are committed on `phase-9-near-expiry-exit-correction`.

- Primary GitHub Actions run: **36296081746** (in progress)
- Unit tests: passed before data reconstruction
- Exit convention: near-expiry short CE/long PE settle; far-expiry long CE/short PE are manually closed at their last available option bar at or before the near-expiry index close
- Slippage: 0.25% per premium leg
- Costs: entry four-leg costs + two far-leg exit transactions + applicable exercise STT on the near long put
- H=2/H=3 research: frozen until this H=1 corrected ledger is complete
- Previous realized-P&L results: superseded for the actual strategy


## Phase 9A latest correction checkpoint

Before accepting any realized H1 output, three implementation audits are now resolved: (1) far legs use observed near-expiry option prices rather than far-expiry settlement; (2) entry and far-leg exit slippage is included in realized gross P&L, not only fees; (3) entry and near-expiry exit/exercise tax dates are handled separately. Phase 9A v3 run **36296334057** is executing the corrected code. Phase 9B validation is prepared on `phase-9B-near-exit-validation` and will trigger from successful v3 completion.


## Phase 9A completed result

Authoritative GitHub Actions run **36297418698** completed successfully using the corrected near-expiry manual-close convention. The H1 artifact contains **252 weekly cycles**, **64 selected trades**, **₹12,317.86 net P&L**, **₹25,859.55 gross P&L**, **₹13,541.69 modeled costs**, **51.56% win rate**, and **1.47 profit factor** at 0.25% premium slippage and ₹20/order brokerage. Independent audit found 27/31 losers already negative before costs, 4 cost-only flips, no missing far-leg exits, and no far-leg exit after near expiry. See `docs/PHASE9A_RESULTS.md`.

Phase 9B is now the next required validation phase. H2/H3 remain frozen until Phase 9B completes.


## Phase 9D correction

The prior Phase 9A/9B H1 realized-P&L results are superseded because they only evaluated 09:20 each trading day. The corrected strategy now scans every available 1-minute timestamp from 09:20 through 15:29 and continues across subsequent trading days within the same weekly cycle until the first positive/all-green candidate appears. There is no 2.5% threshold or 09:20 skip criterion. The new workflow is building the auditable intraday ledger.

## Phase 9D — corrected intraday H1 status

**Status: COMPLETE — corrected H1 baseline produced.**

Authoritative run: **36302077730**.

The final no-skip intraday ledger checks every available 1-minute observation from 09:20 through 15:29 and continues across subsequent trading days within each weekly cycle until the first positive/all-green candidate. It then selects the maximum positive flatline across ATM-400..ATM+400.

Coverage: **172 selected weekly-cycle entries**, **448,280 checked timestamps**, **17,606 decision-surface rows**. Three selections have incompatible near/far lot sizes and are excluded only from realized-P&L arithmetic; they remain in the audit. Complete realized trades: **169**.

Primary execution model: 0.25% premium slippage, ₹20/order brokerage, six executed transactions, near-expiry manual closure of far CE/PE using observed option prices.

Primary result: **₹162,953.84 gross P&L, ₹37,265.02 modeled costs, ₹125,688.82 net P&L, 63.91% realized win rate, PF 2.94, max drawdown ₹16,200.65**.

Execution sensitivity remains positive at 0.5% and 1.0% slippage and at ₹40/order brokerage in the tested historical sample.

The static chart-positive rate is 100% by the selection rule; it must not be interpreted as a 100% realized win rate. The complete H1 result is an in-sample historical reconstruction and requires independent walk-forward/holdout validation before deployment.

**Next phase:** corrected H1 validation/robustness. H2/H3 far-expiry selection research remains frozen until that validation is complete.

See [docs/PHASE9D_RESULTS.md](../docs/PHASE9D_RESULTS.md).


## Phase 9E — frozen-rule H1 validation

**Status: COMPLETE.**

Branch `phase-9E-h1-validation` freezes the corrected Phase 9D strategy and runs chronological calendar-year cohorts, anchored holdouts, bootstrap uncertainty, and predefined execution sensitivity using the authoritative Phase 9D evidence artifact from run **36302077730**. No strategy parameter is tuned in the holdout analysis and H2/H3 remain frozen.

Workflow **36303117489** completed successfully. The validation consumed only the authoritative Phase 9D artifact from run **36302077730**.

## Phase 9E — frozen-rule H1 validation COMPLETE

- Authoritative H1 source: run **36302077730**
- Validation workflow: **36303117489**
- Complete realized trades: **169**; incomplete selections: **3** (lot_size_mismatch)
- Net P&L: **₹125,688.82**
- Mean trade P&L: **₹743.72**
- Win rate: **63.91%** (Wilson 95% CI **56.43%–70.76%**)
- Profit factor: **2.94**
- Max drawdown: **₹16,200.65**
- IID mean-P&L bootstrap 95% CI: **₹441.82–₹1,039.55**
- Circular 4-trade block bootstrap 95% CI: **₹413.92–₹1,066.30**
- All 2021–2026 annual cohorts and all anchored 2022–2026 test cohorts were positive.
- Execution sensitivity remained positive through 1.00% premium slippage and ₹40/order brokerage in the tested scenarios.

**Interpretation:** historical validation checks pass for the frozen rule, but this is not a clean future holdout. The 2021–2026 sample was already observed during strategy development. No new filter has been adopted.

**Next phase:** non-optimizing point-in-time cross-market/regime audit of the corrected H1 ledger. H2/H3 remains frozen until that audit is complete.

## Phase 9F — cross-market and regime audit

**Status: EXECUTING.**

Branch `phase-9F-regime-crossmarket-audit` is running a non-optimizing point-in-time contextual audit of the corrected H1 ledger. It covers NSE/India VIX, FII/FPI-DII, BSE/Sensex, global equity/volatility, USD/INR and gold where reproducible, with source coverage and missingness recorded. No new trading filter is permitted in this phase.

The first workflow attempt (36303419672) failed on a date arithmetic bug before any result was accepted; the script has been corrected and rerun.


## Phase 9F — corrected H1 cross-market/regime audit COMPLETE

- Workflow: **36304036908**
- Scope: **169 complete realized H1 trades**
- NIFTY/India VIX coverage: **100%** using documented yfinance fallback
- Sensex coverage: **160/169 (94.7%)**
- FII/DII: **excluded from inference** because only **16** source rows were recoverable and strict point-in-time recency controls made coverage inadequate
- India-VIX Q4: **42 trades, ₹2,925.31 net, ₹69.65 mean, PF 1.10; block-bootstrap CI crosses zero**
- NIFTY-vs-Sensex: Sensex-outperform group **₹978.79 mean/trade** vs NIFTY-outperform **₹411.26**, but no new rule adopted
- Global risk: risk-off **₹853.24 mean/trade**, risk-on **₹577.08**; descriptive only
- No continuous association survived Benjamini-Hochberg correction at 5%

**Conclusion:** Phase 9F is complete. It provides regime diagnostics and source-coverage limitations but does not alter the frozen H1 rule. H2/H3 far-expiry selection is now reopened under a separately preregistered phase.

Results: `docs/PHASE9F_RESULTS.md`, `results/phase9f/summary.json`, `results/phase9f/regime_summary.csv`, `results/phase9f/continuous_associations.csv`, `results/phase9f/coverage.csv`.


## Phase 9G — current execution checkpoint

**Status: EXECUTING.** H1/H2/H3 yearly reconstructions are running in Actions. The predeclared design remains unchanged. A separate schema audit found a sensitivity-stage bug: the realized trade CSV does not yet retain all raw quote fields required to recompute costs under alternate slippage/brokerage assumptions. This is logged as a repository error and is excluded from interpretation; it will be corrected before Phase 9G can exit.


Phase 9G completeness audit also identified a predeclared analysis gap: the final report must compare first-positive decision-time and selected-strike distributions across H1/H2/H3, not only realized P&L. This is now a required correction before phase exit.


## Phase 9G correction checkpoint — 2026-09-27

The sensitivity path has been hardened: realized trade ledgers now retain the raw quote-level fields required to recompute execution costs, and the workflow refuses to proceed if those fields are absent. The merger also now produces the required first-positive decision-time and selected-strike distribution summaries. **No H2/H3 conclusion is accepted yet.** Fresh corrected workflow run: 36305850007.


### 2026-09-27 — pre-result implementation audit
The Phase 9G selector was manually audited for chronology, 17-strike scan logic, maximum-positive selection, far-leg near-expiry marking, realized P&L sign conventions, six-order brokerage accounting, and STT/stamp/GST handling. No calculation defect was identified in this audit. The active data reconstruction remains the blocking step; no H2/H3 conclusion is accepted.


### Literature-review extension — 2026-09-27
Added peer-reviewed/working literature on NIFTY box-spread efficiency, implied-volatility term structure, volatility risk premia, and calendar-spread dependence. These sources will frame the Phase 9G interpretation without changing the preregistered strategy or acceptance tests.


### H1 control behavioural baseline — 2026-09-27
Phase 9G now has a frozen H1 control reference for strike-selection and decision-time behaviour. H2/H3 must be compared on the same dimensions after reconstruction; these H1 values do not alter the control.


### H1 annual stability reference — 2026-09-27
The frozen H1 control now includes annual cohort performance for 2021–2026. This reference is descriptive and will be used for the paired H2/H3 temporal comparison.


### Strict 17-strike completeness correction — 2026-09-27
The selector now requires candidate_count = 17 at a qualifying timestamp. This preserves the user's no-skipping requirement and prevents missing-option data from silently changing the selection universe. The next Phase 9G run is therefore the first run using this strict completeness rule.


### Execution governance — 2026-09-27
Run **36307233038 (Phase 9G run 10)** is the current accepted execution candidate. It includes the strict 17-strike completeness rule and H1 completeness gate. Older run 36305850007 remains an obsolete process and its outputs will not be used.


### Critical duplicate-row correction — 2026-09-27
The authoritative H1 scan audit demonstrated that raw merged row counts were not a valid measure of the 17-strike universe. The corrected rule now requires **17 unique strike shifts** and **no conflicting duplicate quotes** at a valid decision timestamp. Previous completeness failures are therefore superseded as diagnostic failures, not strategy results.


### Corrected execution reset — 2026-09-27
The earlier Phase 9G run remained in the old concurrency group. The corrected pipeline is now isolated in **concurrency group v2** and will be the accepted execution candidate. The old run's outputs remain excluded.


### Legacy H1 superseded — 2026-09-27
The old Phase 9D H1 control is **not accepted under the exact current rule**: 127/172 selected timestamps lacked one or more prescribed strike shifts. No conflicting quote values were found. Phase 9G run 27 is reconstructing the corrected H1/H2/H3 horizons from raw data under the exact 17-strike rule.


### 2026-09-27 — Run 27 live checkpoint
**Run:** 36313815542  
**Frozen execution commit:** 63b399a9a1d631316dd5233bc684a4ee0a197b25  
**State:** in progress.  
The independent H1 completeness job has completed successfully. All six yearly reconstructions (2021–2026) have passed setup, dependency and data-cache stages and remain in the exact H1/H2/H3 decision-surface reconstruction step. No horizon performance result or H2/H3 conclusion has been accepted. A transient GitHub log-artifact lookup returned 404 while jobs were still running; this is recorded as tooling availability only, not a research/data result.


### 2026-09-27 — H2/H3 source-coverage audit
Run 27 has completed yearly reconstructions for 2024 and 2026. Interim H1 results: 2024 = 26 realized trades, ₹20,656.83 net; 2026 = 14 realized trades, ₹21,014.63 net. H2/H3 in both completed years produced scan rows but no qualifying 17-strike decision surfaces.

The dedicated source audit (runs 36317177731 and 36317271416) sampled 152 timestamps for each of far-rank 2 and 3 and found zero same-day rows in the far-expiry file at every sampled entry timestamp, zero common CE/PE strikes, and zero exact 17-shift grids. The underlying source's expiry files typically begin about 8 days before their own expiry. This makes the source unsuitable for H2/H3 entry-time reconstruction. No H2/H3 performance inference is accepted.


### 2026-09-27 — Three-year interim H1 checkpoint
Corrected run 27 has now completed 2021, 2024 and 2026. Combined interim H1: **54 realized trades, ₹51,403.50 net P&L, 72.22% realized win rate** at the primary cost model. Remaining years 2022/2023/2025 are still reconstructing. No pooled Phase 9G conclusion is accepted.

### 2026-09-27 — Cross-source measurement sensitivity
The same H1 rule and primary cost model produced different annual results across the HF and Rissin datasets, especially in 2026 (net difference ₹37,212.29). This is now a formal limitation: no cross-source pooling or vendor preference is allowed without measurement-equivalence evidence.


### 2026-09-27 — Interim Rissin H2/H3 reconstruction
The corrected Rissin branch has completed 2024 and 2026. 2024: H1 11 selected/9 realized/₹18,690.31 net; H2 6/4/₹5,306.22; H3 0. 2026: H1 18/18/₹58,226.92; H2 16/15/₹78,568.51; H3 11/11/₹74,265.41. The pooled same-source paired tests across these completed years remain statistically unresolved: H2-H1 mean ₹1,272.74 with block-4 bootstrap CI crossing zero; H3-H1 mean ₹3,367.84 with CI crossing zero. No horizon selector adopted; 2025 remains pending.


## Phase 9G — FINAL STATUS — 2026-09-27

**Status: COMPLETE.**

Authoritative primary reconstruction: run **36313815542**, frozen execution commit **63b399a9a1d631316dd5233bc684a4ee0a197b25**.

All six yearly reconstruction jobs (2021–2026) completed successfully. The run-27 pooled merge initially failed only because a zero-byte incomplete CSV was passed to pandas. This aggregation defect was repaired on branch phase-9G-final-merge-run27 and the corrected merge workflow **36320697995** completed successfully using the six frozen yearly artifacts.

### Corrected primary H1

- 131 complete realized trades; 2 incomplete selected rows.
- Net P&L: **₹71,868.76**
- Gross P&L: ₹100,816.81
- Modeled costs: ₹28,948.05
- Realized win rate: **58.78%**
- Wilson 95% CI: **50.22%–66.84%**
- Profit factor: **2.29**
- Maximum drawdown: **₹15,704.24**
- IID bootstrap mean-P&L CI: **₹212.77–₹867.02**
- Four-trade block bootstrap mean-P&L CI: **₹199.66–₹872.13**
- Static chart-positive rate: **100%**; realized win rate is not 100%.

### Selection behaviour

- Median first-positive delay: 210 minutes after 09:20.
- P90 delay: 357 minutes.
- ATM selection: 0%.
- Median selected shift: -250 points.
- Mean absolute selected shift: 329.4 points.

### H2/H3 decision

The primary Hugging Face source cannot adjudicate H2/H3 because the far-rank-2 and far-rank-3 partitions do not contain the required pre-entry intraday observations. This is a data-source coverage limitation, not zero strategy performance. No H2/H3 result is interpreted as a zero-P&L result.

The independent Rissin reconstruction is retained as source-sensitivity evidence only. Its positive same-source paired H2-H1 and H3-H1 differences do not override the primary-source coverage limitation and do not justify dynamic horizon selection.

### Execution sensitivity

At the primary 0.25% slippage + ₹20/order model, H1 net P&L is ₹71,868.76. The result remains positive through 0.50% slippage at all tested brokerage levels and through 1.00% slippage at ₹10/₹20 brokerage; it is negative at 1.00% slippage + ₹40/order.

### Phase conclusion

The exact current H1 rule has positive historical net P&L after modeled costs, but not a 100% realized win rate. H2/H3 are not adjudicated from the primary source. No dynamic horizon-switching rule is adopted.

Final report: docs/PHASE9G_FINAL_RESULTS.md  
Candidate strategy: docs/PHASE9G_CANDIDATE_STRATEGY_FINAL.md  
Final machine-readable summary: results/phase9g/final_summary.json


## Phase 9H — Loss-trade entry analysis OPEN — 2026-09-27

Branch: phase-9H-loss-entry-analysis

The frozen Phase 9G H1 rule is not being changed yet. Phase 9H tests whether realized losses could have been avoided by bounded entry changes:
- alternate strike at the same valid decision timestamp;
- next valid exact-17 timestamp;
- fixed 15/30/60/120 minute waits;
- ex-post later-entry upper bounds.

No exit changes, additional market filters, or free-form timestamp optimization are allowed in this phase. Results are not yet accepted.


## Phase 9H-A — targeted loss-cycle analysis

The initial full-sample Phase 9H implementation was cancelled because the immediate research question is loss-specific and did not require recomputing all winners. The phase has been narrowed to reconstructing the exact entry decision surface only for the 54 realized H1 loss cycles. This preserves the frozen rule, the exact 17-strike completeness gate, the near-expiry far-leg exit convention, and the primary cost model.


## Phase 9H accounting correction — 2026-09-27

A first targeted loss reconstruction exposed a transaction-cost accounting defect: far-call exit STT was double-counted. The pre-fix Phase 9H outputs are explicitly invalidated. The corrected implementation now separates entry-leg sell STT from far-call exit STT and the workflow contains a hard baseline-reproduction gate against the frozen Phase 9G loss ledger.


## Phase 9H-A — FINAL STATUS — 2026-09-27

Accepted workflow: **36325328644**  
Result persistence commit: **ec75cb20e8e23f0550f8d615e796eea815e3d161**

- 54 net-loss H1 trades analyzed.
- Frozen Phase 9G baseline reproduced exactly for every loss before rescue analysis.
- Same-timestamp alternate-strike rescue: 6/54.
- Second-valid-timestamp rescue: 8/54 where a second valid timestamp existed.
- Fixed-delay rescues: 15m 8/54; 30m 7/54; 60m 6/54; 120m 4/54.
- Union of bounded practical entry counterfactuals: **14/54 (25.9%)**.
- Ex-post later timestamp with frozen strike selector: 31/54.
- Ex-post later timestamp + any strike: 38/54.
- **16/54 remained losses even under the strongest tested ex-post entry-only upper bound.**
- No entry rule adopted.

Detailed report: [docs/PHASE9H_LOSS_ENTRY_ANALYSIS.md](docs/PHASE9H_LOSS_ENTRY_ANALYSIS.md)  
Machine-readable rescue summary: [results/phase9h/loss_entry_rescue_summary.csv](results/phase9h/loss_entry_rescue_summary.csv)  
Full loss ledger: [results/phase9h/loss_trade_entry_detail.csv](results/phase9h/loss_trade_entry_detail.csv)  
Workflow: [36325328644](https://github.com/vishnuvcr/Options-Payoff-v1/actions/runs/36325328644)


## Frozen current strategy specification — 2026-09-27

Added [docs/CURRENT_STRATEGY_SPEC.md](../docs/CURRENT_STRATEGY_SPEC.md) as the definitive human-readable operating specification for the accepted Phase 9G H1 control. It freezes the entry cadence, exact 17-strike completeness rule, maximum-positive-flatline selector, four-leg construction, near-expiry manual far-leg close, and cost model. No Phase 9H-A entry modification was adopted.


## Phase 9I — Two-lot / top-two-strike analysis

**Status:** COMPLETE (candidate strategy; not adopted as control)

- Accepted Phase 9G decision set held fixed: 131 weekly entries.
- Rank-1 reproduction gate passed exactly: 131/131 strikes and timestamps match; max P&L difference < 4e-12 INR.
- Literal top-two-every-week result: 262 positions, ₹87,362.19 net, 56.11% win rate, PF 1.65, max drawdown -₹36,888.35.
- Incremental second-strike contribution: ₹15,493.43 net; 53.44% win rate; PF 1.20.
- Retaining the original positive/all-green requirement gives only 67 second-strike trades and -₹11,450.33 incremental net P&L.
- No production/research-control rule change adopted. Phase 9I is a separate candidate requiring prospective/out-of-sample validation.
- Detailed report: docs/PHASE9I_TOP_TWO_RESULTS.md.


## Phase 9I — Top-two-positive-strike sizing variant — COMPLETE

**Final merge-only workflow:** 36429144740  
**Final result artifact:** 10971858546  
**Branch:** phase-9I-top-two-strikes

The Phase 9I variant selected the top two **distinct positive** flatline strikes at the first valid exact-17-strike timestamp, using the same H1 exit and cost model as the Phase 9G control.

### Accepted results
- 131 weekly signal cycles.
- 67 cycles had a second realized positive candidate; 64 had only one.
- 198 realized individual positions: 131 rank-1 + 67 rank-2.
- Top-1 control: **₹71,868.76 net**, 58.78% wins, PF 2.285, max drawdown **-₹15,704.24**.
- Top-2 variant: **₹60,418.42 net**, 56.06% position win rate, PF 1.607, max drawdown **-₹31,812.54**.
- Incremental rank-2 contribution: **-₹11,450.33**, 67 positions, mean **-₹170.90**, PF **0.737**, win rate **50.75%**.
- Rank-2 mean-P&L bootstrap 95% CI: **₹-621.02 to ₹222.88**.
- Combined weekly-cycle mean-P&L bootstrap 95% CI: **₹-68.08 to ₹942.13**.

### Control validation
Rank-1 reproduces the accepted Phase 9G H1 control exactly: 131/131 rows, maximum absolute P&L difference approximately 3.2e-12 INR, and all selected strikes match.

### Decision
**No strategy change.** The frozen one-strike Phase 9G H1 rule remains the research candidate. Phase 9I is retained as a completed sizing experiment. A forced exact-two-lot rule when fewer than two positive candidates exist is a separate, untested variant.

Detailed report: [docs/PHASE9I_TOP_TWO_STRIKES.md](../docs/PHASE9I_TOP_TWO_STRIKES.md)  
Machine-readable results: [results/phase9i_fast/summary.json](../results/phase9i_fast/summary.json)  
Yearly rank contribution: [results/phase9i_fast/top2_yearly_summary.csv](../results/phase9i_fast/top2_yearly_summary.csv)


## Phase 9I — Exact two-lot variant — COMPLETE

- Accepted Phase 9G decision set: 131 weekly entries.
- Rank-1 reproduction: 131/131 exact; max P&L difference < 4e-12 INR.
- Exact two-lot result: 262 positions, **₹87,362.19 net P&L**, 56.11% position win rate, PF 1.651, max drawdown **-₹36,888.35**.
- Incremental second-strike contribution: **+₹15,493.43 net**, 53.44% win rate, PF 1.198.
- Bootstrap 95% CI for mean second-strike P&L: **₹-212.70 to ₹438.82**.
- Decision: retain Phase 9G one-strike as research control; exact two-lot is a candidate requiring untouched chronological holdout and margin-normalized risk analysis.
- Detailed report: [docs/PHASE9I_EXACT_TWO_LOTS.md](../docs/PHASE9I_EXACT_TWO_LOTS.md).

## Phase 10 — Strategy refinement ACTIVE

**Branch:** `phase-10-strategy-refinement`

Status: **PLANNED / ACTIVE**.

The detailed preregistered plan is [docs/PHASE10_STRATEGY_REFINEMENT_PLAN.md](../docs/PHASE10_STRATEGY_REFINEMENT_PLAN.md).

The first research targets are:
1. execution-quality / cost-to-edge gating;
2. entry-signal persistence;
3. scenario-aware strike selection;
4. predeclared exit timing;
5. controlled combinations;
6. margin-normalized sizing comparison;
7. untouched chronological holdout.

The frozen Phase 9G H1 control remains unchanged until a Phase 10 candidate passes its predefined validation and holdout gates.


## Phase 10A — execution-quality / cost-to-edge

**Status:** COMPLETE — no strategy change adopted.

- Decision timestamps tested: 169
- Candidate rows tested: 169
- Positive candidate rows: 169
- Median point-in-time estimated six-order friction / flatline: 125.43%
- P90 friction / flatline: 1559.35%
- Phase 10A result: see [Phase 10A results](../results/phase10a/PHASE10A_RESULTS.md)
- Candidate ledger: [candidate cost-quality table](../results/phase10a/candidate_cost_quality.csv)
- Gate comparison: [gate summary](../results/phase10a/gate_summary.csv)
- Paired inference: [paired gate comparisons](../results/phase10a/paired_gate_comparisons.csv)
- Execution stress: [execution stress](../results/phase10a/execution_stress.csv)

Control reproduction matched 169 rows with maximum absolute P&L difference ₹0.0.


## Phase 10A — execution-quality / cost-to-edge

**Status:** COMPLETE — no strategy change adopted.

- Decision timestamps tested: 131
- Candidate rows tested: 131
- Positive candidate rows: 131
- Median point-in-time estimated six-order friction / flatline: 87.10%
- P90 friction / flatline: 740.94%
- Phase 10A result: see [Phase 10A results](../results/phase10a/PHASE10A_RESULTS.md)
- Candidate ledger: [candidate cost-quality table](../results/phase10a/candidate_cost_quality.csv)
- Gate comparison: [gate summary](../results/phase10a/gate_summary.csv)
- Paired inference: [paired gate comparisons](../results/phase10a/paired_gate_comparisons.csv)
- Execution stress: [execution stress](../results/phase10a/execution_stress.csv)

Control reproduction matched 131 rows with maximum absolute P&L difference ₹0.0.

## Phase 10B — signal persistence

**Status:** COMPLETE — no strategy change adopted.

- [Phase 10B result report](../results/phase10b/PHASE10B_RESULTS.md)
- [Confirmation summary](../results/phase10b/confirmation_summary.csv)
- [Paired confirmation comparisons](../results/phase10b/paired_confirmation_comparisons.csv)
- Promotion screen passed: False
- Best historical variant considered: 15m


## Phase 10C — scenario-aware strike selection

**Status:** COMPLETE — no strategy change adopted.

- [Phase 10C result report](../results/phase10c/PHASE10C_RESULTS.md)
- [Scenario selector summary](../results/phase10c/scenario_selector_summary.csv)
- [Paired comparisons](../results/phase10c/paired_scenario_comparisons.csv)
- [Candidate scenario scores](../results/phase10c/candidate_scenario_scores.csv)
- Promotion screen passed: False
- Best historical variant: worst
