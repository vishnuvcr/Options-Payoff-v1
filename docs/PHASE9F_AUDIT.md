# Phase 9F — Cross-market and regime audit

Authoritative workflow: **36304036908**  
Source H1 workflow: **36302077730**  
Trades: **169 complete realized trades**

## Scope

This phase was deliberately descriptive. The corrected H1 entry/strike/exit rule was frozen. No regime filter, timing filter, or strike filter was introduced.

Context was joined point-in-time where reproducible, using NIFTY/India VIX, NIFTY-vs-Sensex relative performance, global equity/volatility, USD/INR and gold. FII/DII data were too sparse in the available fallback source and were excluded rather than forward-filled.

## Regime summaries

| Context | Regime | Trades | Net P&L | Mean/trade | Win rate | PF | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|
| India VIX | Q1 | 43 | ₹53,977.01 | ₹1,255.28 | 72.09% | 8.48 | ₹3,477.12 |
| India VIX | Q2 | 42 | ₹31,223.25 | ₹743.41 | 59.52% | 3.02 | ₹4,296.04 |
| India VIX | Q3 | 42 | ₹37,563.26 | ₹894.36 | 66.67% | 3.93 | ₹4,738.17 |
| India VIX | Q4 | 42 | ₹2,925.31 | ₹69.65 | 57.14% | 1.10 | ₹10,052.11 |
| NIFTY gap | Flat | 66 | ₹46,353.77 | ₹702.33 | 66.67% | 2.59 | ₹21,683.03 |
| NIFTY gap | Negative | 46 | ₹31,681.91 | ₹688.74 | 60.87% | 2.80 | ₹6,100.09 |
| NIFTY gap | Positive | 57 | ₹47,653.15 | ₹836.02 | 63.16% | 3.65 | ₹5,006.80 |
| NIFTY vs Sensex | NIFTY outperform | 70 | ₹28,788.42 | ₹411.26 | 61.43% | 1.77 | ₹15,050.31 |
| NIFTY vs Sensex | Sensex outperform | 99 | ₹96,900.41 | ₹978.79 | 65.66% | 4.53 | ₹5,556.48 |
| Global context | Mixed | 24 | ₹21,576.55 | ₹899.02 | 54.17% | 3.98 | ₹1,838.03 |
| Global context | Risk-off | 74 | ₹63,139.79 | ₹853.24 | 63.51% | 3.50 | ₹5,311.57 |
| Global context | Risk-on | 71 | ₹40,972.49 | ₹577.08 | 67.61% | 2.27 | ₹16,801.45 |

These are descriptive cohort results; they must not be read as evidence that one regime should be traded while another is avoided.

## Continuous associations

The strongest unadjusted Spearman associations with trade P&L were:

- Prior global VIX level: rho **-0.181**, p **0.022**
- Prior India VIX level: rho **-0.177**, p **0.021**
- Prior NIFTY return: rho **-0.152**, p **0.048**

After Benjamini-Hochberg correction across the tested association family, **none** remained below q = 0.05. Phase 9F therefore does not establish a statistically robust contextual predictor.

## Key observations

1. The rule remained positive across every predeclared India-VIX quartile, but the highest-VIX quartile had much smaller mean P&L (₹69.65/trade) and PF 1.10, with bootstrap intervals crossing zero.
2. NIFTY opening-gap groups were all positive; the point estimates were relatively close, so there is no basis here for a gap-direction filter.
3. The Sensex-outperforming cohort had higher aggregate/mean P&L than the NIFTY-outperforming cohort, but this is descriptive and may reflect calendar composition or confounding.
4. Global risk-on, risk-off and mixed groups were all historically positive; no global-risk filter is justified by this audit.
5. The audit does **not** support converting any contextual variable into a trading rule.

## Data coverage and source limitations

- NIFTY and India VIX coverage in the joined ledger was effectively complete after fallback sourcing.
- Global series had roughly 90–99% coverage depending on variable.
- USD/INR had 99.4% coverage.
- FII/DII fallback data contained only 16 usable rows and was excluded from regime analysis.
- Point-in-time quote-level bid/ask data for external markets was unavailable.
- Corporate-action and news timestamps were not reliably reconstructable for every trade, so they were not imputed.
- Because the authoritative H1 sample is 2021–2026 and was already observed during strategy development, this remains a historical contextual audit rather than prospective validation.

## Phase conclusion

**Phase 9F is complete.** No new trading rule was created.

The contextual audit does not invalidate the corrected H1 historical result, but it also does not establish an independent cross-market predictor that should be used to alter entries. H2/H3 expiry-selection research can now be reopened under a separate preregistered phase, with the H1 rule itself remaining frozen.

Machine-readable outputs are in `results/phase9f/`.
