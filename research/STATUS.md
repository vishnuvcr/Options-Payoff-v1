# Research status

**As of:** 2026-09-27  
**Active branch:** phase-8-s2-s1-predictor  
**Overall status:** Phase 8A — S2-S1 predictability complete; no filter adopted

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
