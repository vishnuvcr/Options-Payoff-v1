# Phase 9F — Corrected H1 cross-market and regime audit

Authoritative H1 source: **Phase 9D run 36302077730**  
Phase 9F workflow: **36304036908**  
Scope: **169 complete realized H1 trades**

## Purpose

Phase 9F was a predeclared descriptive audit. It did not alter entry timing, 17-strike selection, expiry handling, exit semantics, slippage, brokerage or taxes. It asks whether the frozen H1 result varies with pre-entry market regime and cross-market context.

## Data and point-in-time treatment

- NIFTY and India VIX: yfinance fallback was used after the installed NSE client proved schema-unstable. Coverage was 100% for NIFTY and India VIX across the 169 trades.
- BSE/Sensex: yfinance fallback; 160/169 trades had prior-session coverage.
- Global context: S&P 500, Nasdaq, Nikkei, Hang Seng, Shanghai, global VIX, gold and USD/INR. Coverage varied by series; USD/INR was 168/169, most global equity/gold series were roughly 90–95%.
- FII/DII: the available fallback contained only 16 source rows and was classified as too sparse for inference. It was excluded rather than stale-forward-filled. Therefore this phase does **not** support a FII/DII effect conclusion.
- Corporate-action and point-in-time news fields were not imputed because a reliable historical timestamped feed was not reconstructed.

## Predeclared regime results

| Context | Regime | Trades | Net P&L | Mean/trade | Win rate | PF | Mean-P&L 4-block CI |
|---|---|---:|---:|---:|---:|---:|---:|
| India VIX | Q1 | 43 | ₹53,977.01 | ₹1,255.28 | 72.09% | 8.48 | ₹724.00 to ₹1,784.66 |
| India VIX | Q2 | 42 | ₹31,223.25 | ₹743.41 | 59.52% | 3.02 | ₹319.63 to ₹1,215.03 |
| India VIX | Q3 | 42 | ₹37,563.26 | ₹894.36 | 66.67% | 3.93 | ₹423.20 to ₹1,395.88 |
| India VIX | Q4 | 42 | ₹2,925.31 | ₹69.65 | 57.14% | 1.10 | -₹504.08 to ₹665.79 |
| NIFTY opening gap | Negative | 46 | ₹31,681.91 | ₹688.74 | 60.87% | 2.80 | ₹182.37 to ₹1,249.68 |
| NIFTY opening gap | Flat | 66 | ₹46,353.77 | ₹702.33 | 66.67% | 2.59 | -₹16.17 to ₹1,311.74 |
| NIFTY opening gap | Positive | 57 | ₹47,653.15 | ₹836.02 | 63.16% | 3.65 | ₹369.47 to ₹1,308.60 |
| NIFTY vs Sensex | NIFTY outperform | 70 | ₹28,788.42 | ₹411.26 | 61.43% | 1.77 | -₹174.71 to ₹950.47 |
| NIFTY vs Sensex | Sensex outperform | 99 | ₹96,900.41 | ₹978.79 | 65.66% | 4.53 | ₹645.19 to ₹1,343.68 |
| Global risk | Risk-on | 71 | ₹40,972.49 | ₹577.08 | 67.61% | 2.27 | -₹82.10 to ₹1,133.21 |
| Global risk | Risk-off | 74 | ₹63,139.79 | ₹853.24 | 63.51% | 3.50 | ₹409.76 to ₹1,336.69 |
| Global risk | Mixed | 24 | ₹21,576.55 | ₹899.02 | 54.17% | 3.98 | ₹443.65 to ₹1,403.37 |

### Main descriptive observation

The largest visible regime deterioration was in the highest India-VIX quartile. Q4 had 42 trades, ₹2,925.31 net P&L, ₹69.65 mean P&L, PF 1.10, and a four-trade block-bootstrap interval crossing zero. The same sample's lower-VIX quartiles had materially higher mean P&L. This is a robustness observation, not a new filter.

The NIFTY-vs-Sensex split also differed descriptively: the Sensex-outperform group had a higher mean P&L and its bootstrap lower bounds were positive, while the NIFTY-outperform group had a block-bootstrap interval crossing zero. Again, this is descriptive only and is not used to change the trading rule.

NIFTY gap direction showed smaller differences and overlapping uncertainty. Global risk-off and risk-on groups were both historically positive; their dependence-aware intervals overlap zero for risk-on and remain positive for risk-off.

## Continuous associations

The strongest raw monotonic associations were:

- prior India VIX level vs trade P&L: Spearman ρ = **-0.177**, p = 0.021, BH q = **0.468**;
- global VIX close vs trade P&L: ρ = **-0.181**, p = 0.022, BH q = **0.245**;
- prior NIFTY return vs trade P&L: ρ = **-0.152**, p = 0.048, BH q = **0.352**.

No tested continuous association survived the predeclared Benjamini-Hochberg 5% threshold. Therefore no continuous market variable is promoted to a trading signal.

## Strengths

- Point-in-time as-of joins were used rather than post-entry observations.
- FII/DII data were explicitly rejected when too sparse instead of being silently propagated across years.
- Regimes were predeclared and no subgroup rule was tuned from the observed result.
- Uncertainty was reported with both IID and circular four-trade block bootstrap diagnostics.
- Multiple continuous associations were adjusted with Benjamini-Hochberg correction.
- All context variables and coverage are stored in machine-readable repository outputs.

## Limitations

- NIFTY/India VIX/Sensex/global context relied on a documented yfinance fallback rather than direct official exchange downloads.
- Quote-level external-market bid/ask data were unavailable, so these variables are explanatory context rather than executable signals.
- FII/DII coverage was inadequate for inference in this run.
- Corporate-action and news timestamp joins were not completed from a reliable point-in-time feed.
- Regime sample sizes are modest and the entire 2021–2026 trade sample was already observed during strategy development, so this remains historical validation rather than a pristine future holdout.

## Phase conclusion

Phase 9F completes the required non-optimizing cross-market/regime audit. It identifies a descriptive deterioration of the frozen H1 results in the highest India-VIX quartile and a descriptive difference in the NIFTY-vs-Sensex relative-performance split, while no continuous association survives multiple-testing correction.

**No regime filter, FII/DII filter, global-market filter, or entry rule is adopted.**

## Next phase

H2/H3 far-expiry selection research can now reopen under a separate preregistered branch. That phase must keep the corrected H1 entry rule and near-expiry manual-close convention fixed, and it must evaluate whether alternative far-expiry selections change the economics without using future information.