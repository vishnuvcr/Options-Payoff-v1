# Phase 7A — Exact historical margin-denominator selection

## Objective

Replace the historical 2.5% buy-premium proxy with the margin-required denominator used by the payoff platform, reconstruct that margin from NSE/NSCCL SPAN risk data, and rerun the user's requested strike-selection rule:

- common strikes only;
- ATM-400 through ATM+400;
- 50-point increments;
- keep candidates with estimated max profit = max loss percentage > 2.5%;
- among eligible candidates, select the maximum estimated equal max-profit=max-loss value in INR;
- compare maximum-percentage selection as a sensitivity.

## Margin calibration

The user's screenshot showed standalone margin ₹88,076 for the 23,450 four-leg, 65-unit position. The exact position was reconstructed from NSE/NSCCL SPAN data. The closest same-day intraday SPAN snapshot produced consolidated margin ₹87,812.40, a 0.2993% difference from the screenshot. All five intraday revisions i1-i5 were within 0.91%; i5 was closest.

Therefore the historical denominator is now empirically calibrated as margin required, not option premium.

For the screenshot:
- 2.5% of ₹88,076 = ₹2,201.90
- 2.5% of ₹87,812.40 = ₹2,195.31

## Historical SPAN coverage

The Phase 3 research sample contained 891 entry dates with candidate observations.

Historical NSE SPAN archive probing found:
- i1 coverage: 100%
- i2 coverage: 100%
- i3 coverage: 100%
- i4 coverage: 100%
- i5 coverage: 100%
- settlement/sensitivity s coverage: 100%

A no-look-ahead primary interpretation uses the i1 begin-day SPAN snapshot. The s file is retained as a sensitivity.

## Completeness of the historical 2.5% search

The corrected workflow uses 2% ELM per short NIFTY index-option leg, giving a 4% spot-notional lower bound for the two short legs combined. Any candidate whose chart flatline is at or below 2.5% of this lower bound cannot reach 2.5% of the actual margin required.

The corrected workflow also enforces the requested ±400 candidate range.

A preliminary run used a deliberately looser 1% per-short lower bound and the wider cached ±500 grid. That produced 296 possible candidate rows, but it was only a superset. After applying the correct ELM lower bound and requested ±400 range, only 31 candidate rows across 11 timestamps needed exact margin reconstruction.

## Exact primary result — i1 SPAN

| Date | Shift | Flatline ₹ | Margin ₹ | Max-profit % | Net P&L ₹ |
|---|---:|---:|---:|---:|---:|
| 2021-08-04 | +100 | 2,305.00 | 50,406.50 | 4.5728% | 5,609.49 |
| 2022-04-04 | +300 | 2,675.00 | 52,124.90 | 5.1319% | -5,791.42 |
| 2022-05-25 | -250 | 1,242.50 | 46,991.30 | 2.6441% | 23,853.19 |
| 2022-06-30 | -400 | 1,672.50 | 62,961.30 | 2.6564% | 19,008.91 |

At 0.25% premium slippage per leg and ₹20 per executed order:
- 4 trades
- ₹42,680.17 net P&L
- mean ₹10,670.04
- median ₹12,309.20
- win rate 75.0%
- profit factor 8.37
- maximum drawdown -₹5,791.42
- largest loss -₹5,791.42
- largest win ₹23,853.19
- modeled costs ₹647.48

The maximum-percentage selection and maximum-INR selection chose the same strike on all 4 timestamps.

## Settlement-file sensitivity

Using the same ±400 range and the settlement/sensitivity SPAN snapshot:
- 3 qualifying trades
- ₹23,671.26 net P&L
- mean ₹7,890.42
- win rate 66.67%
- profit factor 5.09
- maximum drawdown -₹5,791.42

The selected shifts were +100, +300 and -250. Maximum-percentage and maximum-INR selection again matched on all qualifying timestamps.

## Why this changes the earlier Phase 7 result

The earlier Phase 7 result used an explicitly labelled buy-premium proxy denominator and found 48 qualifying trades.

The exact margin denominator is much more selective: 4 primary trades under the corrected ±400 rule.

Therefore the earlier ₹166,866.51 point estimate is no longer the appropriate estimate for the user's actual 2.5% platform rule. It remains a historical comparator only.

## Statistical interpretation

The exact margin-denominator primary sample contains only 4 trades. This is too small for meaningful bootstrap confidence intervals, Sharpe/Sortino inference, or claims of a stable statistical edge. The result is an exact historical reconstruction of the rule, not evidence of a robust standalone trading edge.

## Reproducibility artifacts

- `results/phase7a/exact_margin_selected_i1.csv`
- `results/phase7a/exact_margin_selected_s.csv`
- `results/phase7a/exact_margin_summary.json`
- `results/phase7a/span_coverage_summary.json`
- `docs/MARGIN_RECONSTRUCTION.md`

The completed GitHub Actions run containing the raw historical SPAN cache and candidate-level margin reconstruction is run 36286676530, artifact 10921011598.