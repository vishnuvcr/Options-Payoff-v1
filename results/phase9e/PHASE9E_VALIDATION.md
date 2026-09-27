# Phase 9E — Frozen-rule H1 validation

Authoritative source run: **36302077730**

This phase keeps the Phase 9D entry, strike-selection, exit and transaction-cost rules frozen. It does not introduce or tune a new filter.

## Primary result

- Complete realized trades: **169**
- Net P&L: **₹125,688.82**
- Mean trade P&L: **₹743.72**
- Win rate: **63.91%**
- Profit factor: **2.941**
- Maximum drawdown: **₹16,200.65**
- Win-rate Wilson 95% CI: **56.43% to 70.76%**

## Uncertainty

- IID bootstrap 95% CI for mean P&L: **₹441.82 to ₹1,039.55**
- Circular four-trade block bootstrap 95% CI: **₹413.92 to ₹1,066.30**

## Calendar-year cohorts

| Year | Trades | Net P&L | Mean | Win rate | PF | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 28 | ₹12,833.78 | ₹458.35 | 53.57% | 2.627 | ₹4,124.97 |
| 2022 | 46 | ₹15,283.53 | ₹332.25 | 60.87% | 1.729 | ₹7,715.00 |
| 2023 | 34 | ₹48,635.63 | ₹1,430.46 | 79.41% | 14.192 | ₹1,122.21 |
| 2024 | 30 | ₹26,613.84 | ₹887.13 | 66.67% | 4.491 | ₹2,299.68 |
| 2025 | 17 | ₹1,708.07 | ₹100.47 | 35.29% | 1.077 | ₹16,200.65 |
| 2026 | 14 | ₹20,613.98 | ₹1,472.43 | 85.71% | 9.762 | ₹1,648.85 |

## Anchored chronological holdouts

| Test year | Prior-trade count | Test trades | Test net P&L | Test win rate | Test PF |
|---:|---:|---:|---:|---:|---:|
| 2022 | 28 | 46 | ₹15,283.53 | 60.87% | 1.729 |
| 2023 | 74 | 34 | ₹48,635.63 | 79.41% | 14.192 |
| 2024 | 108 | 30 | ₹26,613.84 | 66.67% | 4.491 |
| 2025 | 138 | 17 | ₹1,708.07 | 35.29% | 1.077 |
| 2026 | 155 | 14 | ₹20,613.98 | 85.71% | 9.762 |

## Execution sensitivity

| Scenario | Slippage | Brokerage/order | Trades | Net P&L | Win rate | PF |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0.00% | ₹20 | 169 | ₹155,747.51 | 66.27% | 3.891 |
| 0p0025 | 0.25% | ₹20 | 169 | ₹125,688.82 | 63.91% | 2.941 |
| 0p005 | 0.50% | ₹20 | 169 | ₹95,630.14 | 57.40% | 2.239 |
| 0p01 | 1.00% | ₹20 | 169 | ₹35,512.76 | 51.48% | 1.336 |
| broker_10 | 0.25% | ₹10 | 169 | ₹137,654.02 | 65.09% | 3.277 |
| broker_20 | 0.25% | ₹20 | 169 | ₹125,688.82 | 63.91% | 2.941 |
| broker_40 | 0.25% | ₹40 | 169 | ₹101,758.42 | 57.99% | 2.375 |

## Incomplete selections

3 Phase 9D selections remain excluded from realized P&L because their near/far expiry lot sizes were incompatible.

## Interpretation

The rule remained historically profitable in the archived sample and in the calendar-year/anchored test diagnostics, but the bootstrap intervals still cross zero. Accordingly this phase treats the result as **historically positive but uncertain**, not as evidence of a guaranteed or deployable edge.

The temporal diagnostics are not a pristine future holdout because the 2021-2026 sample was already available during strategy development. The next genuinely independent validation requires a new, untouched data period.

## Timing and strike-shift diagnostics

Entry-time and shift-band files are descriptive diagnostics only; no new filter is adopted from them in Phase 9E.
