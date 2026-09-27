# Phase 9E — Frozen-rule H1 validation

Authoritative source run: **36302077730**  
Validation workflow: **36303117489**

Phase 9E kept the Phase 9D entry, strike-selection, exit and transaction-cost rules frozen. No 2.5% threshold, margin gate, Greek filter, or S2-S1 filter was introduced.

## Primary result

- Complete realized trades: **169**
- Net P&L: **₹125,688.82**
- Mean trade P&L: **₹743.72**
- Median trade P&L: **₹538.17**
- Win rate: **63.91%**
- Profit factor: **2.941**
- Maximum drawdown: **₹16,200.65**
- Modeled costs: **₹37,265.02**
- Largest win: **₹5,825.60**
- Largest loss: **-₹10,052.11**
- Win-rate Wilson 95% CI: **56.43% to 70.76%**

## Chronological validation

All six calendar-year cohorts in the corrected 2021–2026 sample had positive net P&L:

| Year | Trades | Net P&L | Mean | Win rate | PF | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 28 | ₹12,833.78 | ₹458.35 | 53.57% | 2.627 | ₹4,124.97 |
| 2022 | 46 | ₹15,283.53 | ₹332.25 | 60.87% | 1.729 | ₹7,715.00 |
| 2023 | 34 | ₹48,635.63 | ₹1,430.46 | 79.41% | 14.192 | ₹1,122.21 |
| 2024 | 30 | ₹26,613.84 | ₹887.13 | 66.67% | 4.491 | ₹2,299.68 |
| 2025 | 17 | ₹1,708.07 | ₹100.47 | 35.29% | 1.077 | ₹16,200.65 |
| 2026 | 14 | ₹20,613.98 | ₹1,472.43 | 85.71% | 9.762 | ₹1,648.85 |

The anchored chronological test cohorts were also positive:

| Test year | Prior-trade count | Test trades | Test net P&L | Test win rate | Test PF |
|---:|---:|---:|---:|---:|---:|
| 2022 | 28 | 46 | ₹15,283.53 | 60.87% | 1.729 |
| 2023 | 74 | 34 | ₹48,635.63 | 79.41% | 14.192 |
| 2024 | 108 | 30 | ₹26,613.84 | 66.67% | 4.491 |
| 2025 | 138 | 17 | ₹1,708.07 | 35.29% | 1.077 |
| 2026 | 155 | 14 | ₹20,613.98 | 85.71% | 9.762 |

The 2025 cohort was materially weaker than the other years, with a 35.29% win rate, PF 1.077 and a ₹16,200.65 within-cohort maximum drawdown. This is a robustness observation, not a rule-change trigger.

## Uncertainty

20,000-resample diagnostics gave:

- IID bootstrap 95% CI for mean P&L: **₹441.82 to ₹1,039.55**
- Circular four-trade block bootstrap 95% CI: **₹413.92 to ₹1,066.30**

These are historical-sample uncertainty diagnostics, not forecasts. The positive lower bounds are conditional on the historical ledger and the bootstrap assumptions.

## Execution sensitivity

| Slippage | Brokerage/order | Net P&L | Win rate | PF |
|---:|---:|---:|---:|---:|
| 0.00% | ₹20 | ₹155,747.51 | 66.27% | 3.891 |
| 0.25% | ₹20 | ₹125,688.82 | 63.91% | 2.941 |
| 0.50% | ₹20 | ₹95,630.14 | 57.40% | 2.239 |
| 1.00% | ₹20 | ₹35,512.76 | 51.48% | 1.336 |
| 0.25% | ₹10 | ₹137,654.02 | 65.09% | 3.277 |
| 0.25% | ₹40 | ₹101,758.42 | 57.99% | 2.375 |

The historical result remained positive under all tested slippage/brokerage scenarios, including the 1.00% premium-slippage scenario, but the margin narrowed substantially as execution worsened.

## Descriptive timing and strike-shift diagnostics

Entry-time and strike-shift bands are stored in the Phase 9E results directory. They are descriptive only. No subgroup is adopted as a new rule.

## Incomplete selections

Three Phase 9D selected opportunities remain excluded from realized P&L because their near/far expiry lot sizes were incompatible. They remain in the audit and were not given synthetic sizing or settlement prices.

## Interpretation

The frozen rule has a positive historical point estimate in the corrected 2021–2026 reconstruction, all annual cohorts are positive, and both bootstrap lower bounds are positive under the selected resampling procedures.

However, this is **not a pristine future-data holdout**. The same 2021–2026 sample was already available during strategy development. The chronological cohorts therefore demonstrate temporal stability of the frozen rule within the observed sample, but they do not establish performance in an untouched future period.

The strategy also retains model risk from historical close-proxy execution, incomplete quote-level bid/ask information, and the three lot-size-incompatible selections.

**Phase 9E conclusion:** the corrected H1 rule passes the predefined historical validation checks, but the evidence remains historical rather than prospective. No new filter is adopted.

## Next research phase

The next phase is a descriptive, point-in-time cross-market and regime audit of the corrected H1 trade ledger, using cached NSE/India VIX/FII-DII/global-index/FX/gold/news/corporate-action context where available. This phase must remain non-optimizing: it explains when the rule performs differently without creating a new selection rule. After that, the research can proceed to the remaining H2/H3 expiry-selection question or, if genuinely untouched data becomes available, a clean future holdout.