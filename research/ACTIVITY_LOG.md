# Activity log

This is the observable research/repository activity log. It records completed actions, outcomes and implementation decisions; it is not a transcript of private internal reasoning.

| Date | Phase | Step | Outcome |
|---|---|---|---|
| 2026-09-26 | 3 | Corrected user strategy specification | Replaced the incomplete ATM/-400/+400 implementation with the full 50-point grid from -500 to +500, ATM first and every qualifying fallback retained. |
| 2026-09-26 | 3 | Expanded candidate extraction | Generated 19,341 candidate rows; 15,701 complete, 3,498 unavailable, 142 missing settlement. |
| 2026-09-26 | 3 | Corrected runtime issues | Fixed Python path, strike-grid schema, PyArrow compatibility and trigger-denominator unit handling. |
| 2026-09-26 | 3 | Final full-grid backtest | Run 36262958536 succeeded with 63 selected trade rows across 52 timestamps. |
| 2026-09-26 | 4 | Corrected robustness workflow | Run 36263760476 succeeded after adding the missing brokerage-sensitivity helper and adapting robustness selection to the full grid. |
| 2026-09-26 | 4 | Validation completed | Bootstrap, block bootstrap, walk-forward, threshold, slippage, denominator and brokerage results generated. |
| 2026-09-26 | 5 | Corrected regime rerun | Run 36263974629 succeeded using the corrected 63-trade ledger. |
| 2026-09-26 | 6 | Corrected manuscript | Replaced the earlier 28-trade manuscript with the full-grid results and new figures. |
| 2026-09-27 | 6A | Loss audit requested | User requested a complete audit of all losing trades because of doubt about the positive aggregate result. |
| 2026-09-27 | 6A | Artifact-backed loss audit | Workflow 36264710663 read selected_trades.parquet from authoritative run 36262958536 and produced a 25-row loss ledger. |
| 2026-09-27 | 6A | Loss decomposition | All 25 losers had negative gross P&L before fees; 0 were fee-only flips. Losing rows contributed -₹454,335.44 and modeled costs on them were ₹3,557.82. |
| 2026-09-27 | 6A | Reproducibility audit | Found stale run_backtest.py on phase-6-manuscript-grid; authoritative 63-row code remains phase-3-strike-grid. |
| 2026-09-27 | 6A | Reproducibility correction | Synchronized phase-6-manuscript-grid/scripts/run_backtest.py to the authoritative full-grid implementation in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4. |

| 2026-09-27 | 6A | Payoff formula audit | Verified static chart = C1-P1-C2+P2 under the same-terminal-spot convention and actual gross cross-expiry P&L = C1-P1-C2+P2+S2-S1. |
| 2026-09-27 | 7 | Strategy change initiated | Created `phase-7-max-equal-selection` because the user replaced ATM-first/fallback ordering with exhaustive ATM-400..ATM+400 maximum-flatline selection. |
| 2026-09-27 | 7 | Platform research | Reviewed current public Streak and Sensibull material. Sensibull documents max-profit/max-loss percentage as max profit or max loss divided by margin required; Streak public material reviewed here does not publish a comparable percentage formula. |
| 2026-09-27 | 7 | Platform semantics documented | Added `docs/PAYOFF_PLATFORM_REVIEW.md`, distinguishing software chart metrics from the true two-expiry economic P&L. |
| 2026-09-27 | 7 | Strategy engine updated | Added exhaustive strike-grid helper, chart flatline estimator and maximum equal-max-profit=max-loss selection mode. |
| 2026-09-27 | 7 | Data extraction updated | Future cached strategy-input builds now generate ATM-400..ATM+400 in 50-point increments; current Phase 3 artifact remains usable for the rerun because it contains the wider grid. |
| 2026-09-27 | 7 | Tests/workflow added | Added unit coverage and manual GitHub Actions workflow `.github/workflows/phase-7-max-equal-selection.yml`. |

| 2026-09-27 | 7 | Exact empirical rerun from cached Phase 3 expanded inputs | Reproduced the prior 63-trade result exactly with a local raw Parquet decoder, then evaluated the new ATM-400..ATM+400 rule without new market-data downloads. |
| 2026-09-27 | 7 | Primary selection completed | 905 timestamps had complete candidates in the requested grid; 48 passed the 2.5% legacy proxy gate; maximum estimated equal-flatline value selected one trade per qualifying timestamp. |
| 2026-09-27 | 7 | Primary result | 48 trades, ₹166,866.51 net P&L, 60.42% win rate, PF 1.56, max drawdown -₹124,060.72 at 0.25% slippage and ₹20/order brokerage. |
| 2026-09-27 | 7 | Economic decomposition | Static chart value contributed ₹36,138.75 versus ₹142,545.00 from realized S2-S1 before entry slippage and fees. |
| 2026-09-27 | 7 | Robustness/loss audit | 95% bootstrap intervals include zero; 19/19 losing trades were negative before fees; loss-side S2-S1 contribution was -₹309,305.00. |
| 2026-09-27 | 7 | Sensitivity | Net P&L remained positive at 0%, 0.25%, 0.50% and 1.00% slippage; no-gate maximum-flatline selection produced materially worse drawdown than the 2.5%-gated rule. |
| 2026-09-27 | 7A | Started historical margin reconstruction | Created branch `phase-7A-margin-reconstruction` and calibration workflow for the screenshot position. |
| 2026-09-27 | 7A | Calibration target formalized | Screenshot position: sell 29-Sep-2026 23450 CE, buy 29-Sep-2026 23450 PE, buy 06-Oct-2026 23450 CE, sell 06-Oct-2026 23450 PE; 65 units; screenshot standalone margin ₹88,076. |
| 2026-09-27 | 7A | NSE margin methodology reviewed | NSE Clearing states that SPAN margin uses daily risk arrays over price/volatility scenarios and publishes daily SPAN risk-parameter files. |
| 2026-09-27 | 7A | NSE SPAN source recovered | Found the direct official archive pattern `nsccl.YYYYMMDD.iN.zip` and executed it in GitHub Actions. |
| 2026-09-27 | 7A | Screenshot margin reconstructed | Exact four-leg 23450 calendar/synthetic position calibrated at ₹87,812.40 versus Sensibull ₹88,076; discrepancy 0.2993%. |
| 2026-09-27 | 7A | Intraday-version calibration | i05 was closest (0.2993%); i03 was 0.4005% away; all i1-i5 were within 0.91%. |
| 2026-09-27 | 7A | Denominator resolved for screenshot | 2.5% of screenshot margin is ₹2,201.90; 2.5% of the closest reconstructed margin is ₹2,195.31. |
| 2026-09-27 | 7A | Historical SPAN coverage complete | 891/891 entry dates have i1 and settlement/sensitivity s archives available; all i1-i5 were also available in the coverage probe. |
| 2026-09-27 | 7A | Exact margin reconstruction complete | A superset of 296 candidates was reconstructed first; after enforcing the correct ±400 range and 2% per-short ELM lower bound, 31 candidates across 11 timestamps required exact margin checks. |
| 2026-09-27 | 7A | Exact primary selection | 4 i1 timestamps pass the 2.5% margin-based gate; selected shifts are +100, +300, -250 and -400. |
| 2026-09-27 | 7A | Exact primary P&L | 4 trades, ₹42,680.17 net, 75% win rate, PF 8.37, max drawdown -₹5,791.42 after modeled costs. |
| 2026-09-27 | 7A | Percentage/value ambiguity resolved empirically | Maximum margin-based percentage and maximum estimated INR flatline select identical strikes on all 4 primary timestamps. |
| 2026-09-27 | 7B | User clarified weekly operation | The intended action is one weekly scan of all 17 common strikes from ATM-400 through ATM+400, select the maximum qualifying candidate, and trade only if its platform-style max-profit=max-loss percentage exceeds 2.5%. |
| 2026-09-27 | 7B | User corrected final rule | No 2.5% threshold and no margin gate; every week scan ATM-400..ATM+400 and trade the strike with the maximum positive/all-green flatline. |
| 2026-09-27 | 7B | Weekly selector implemented | Added `scripts/weekly_positive_selection.py` and manual workflow `.github/workflows/phase-7B-weekly-positive-selection.yml`; primary cadence uses first available 09:20 observation per near-expiry cycle and last-observation timing as sensitivity. |
| 2026-09-27 | 7B | Workflow correction | Phase 7B Actions reached the payoff-metric step but failed on Python module path; corrected with `PYTHONPATH=.`. |\n| 2026-09-27 | 7B | First-positive weekly backtest | 63 weekly expiry cycles; 63 selected trades; every cycle had at least one positive/all-green candidate; net P&L ₹-9,627.90 after modeled costs. |\n
| 2026-09-27 | 7B | Final positive-only weekly backtest | 63 weekly cycles, 63 trades, 0 skips, ₹-9,627.90 net P&L, ₹233.25 gross, ₹9,861.15 costs, 57.14% win rate, PF 0.98. |
| 2026-09-27 | 7B | Final economic decomposition | Positive static chart contribution ₹20,213.00; realized S2-S1 contribution ₹-19,979.75; costs drive gross near-zero to negative net. |
| 2026-09-27 | 7B | Final uncertainty | IID and block bootstrap intervals for mean weekly P&L both include zero. |
| 2026-09-27 | 7C | Phase started | Created `phase-7C-entry-features-greeks`, added entry-feature/Greek analysis script and manual GitHub Actions workflow; analysis targets 63 primary weekly trades plus all positive candidates at their decision timestamps. |\n| 2026-09-27 | 7C | Winner/loser Greek analysis complete | 63 selected trades: 36 winners, 27 losers; no tested Greek/IV/moneyness feature remained robust after BH FDR correction. |\n| 2026-09-27 | 7C | Alternative selector testing complete | Full-coverage single-feature selectors all underperformed maximum positive flatline; paired weekly bootstrap intervals were negative. |\n| 2026-09-27 | 7C | Walk-forward testing complete | Near-expiry IV skew (maximum) was the best training-selected Greek/IV feature in both splits, but underperformed the baseline out of sample; no feature adopted. |\n| 2026-09-27 | 7C | Reproducibility outputs published | Added compact winner/loser Greek summary, selector bootstrap comparison, and walk-forward feature-selection CSVs under `results/phase7c/`. |\n| 2026-09-27 | 8A | Phase started | Created `phase-8-s2-s1-predictor`; added no-look-ahead regression/filter analysis and manual GitHub Actions workflow. |\n| 2026-09-27 | 8A | Internal S2-S1 walk-forward complete | 905 prior entry timestamps across 255 weekly cycles were used for training with equal weekly-cycle weights; 43 weekly decision cycles were strictly OOS. |\n| 2026-09-27 | 8A | S2-S1 economic filter evaluated | Random Forest produced +₹102,022.80 versus the same-test baseline, but sign accuracy was only 51.16%, AUC 0.5136, block performance reversed in the middle period, and bootstrap CI included zero. |\n| 2026-09-27 | 8A | Phase stopped per predeclared rule | No S2-S1 filter adopted; Phase 8B external-variable expansion not promoted because internal predictability was not stable enough. |\n