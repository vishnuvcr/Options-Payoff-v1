# Phase 7C — Entry-Feature and Greek Analysis

**Branch:** `phase-7C-entry-features-greeks`  
**Authoritative workflow run:** 36291838252  
**Artifact:** phase-7C-entry-features-greeks  
**Purpose:** Test whether entry-time option Greeks, IV structure, moneyness, or other observable candidate features distinguish winning and losing trades, and whether any such feature can improve strike selection within the fixed 17-strike ATM-400..ATM+400 grid.

## 1. Primary weekly rule under test

The strategy was fixed before this analysis:

1. For each weekly expiry cycle, scan observations chronologically.
2. At each available 09:20 observation, evaluate all 17 common strikes from ATM-400 to ATM+400 in 50-point steps.
3. A candidate qualifies only when the one-dimensional payoff chart is a positive/all-green flatline.
4. At the first observation in the week where at least one candidate qualifies, trade the candidate with the maximum positive estimated equal max-profit=max-loss flatline value.
5. There is no 2.5% threshold, no margin percentage gate, and no threshold-based skipping.

The 63-trade primary sample is therefore the fixed benchmark against which any additional entry feature must be tested.

## 2. Data and sample

At the first-positive decision observations:

- 63 weekly cycles
- 63 selected trades
- 36 winning trades
- 27 losing trades
- 294 positive candidate rows evaluated at the actual decision timestamps

The candidate universe remains restricted to the same 17-strike grid used by the primary strategy, so feature tests do not get an unfairly different strike universe.

The authoritative primary weekly result is:

- net P&L: **₹-9,627.90**
- mean trade P&L: **₹-152.82**
- median trade P&L: **₹2,179.37**
- win rate: **57.14%**
- modeled costs: **₹9,861.15**

All candidate outcome calculations in Phase 7C use the repository transaction-cost convention, including the existing 0.25% premium-slippage cost model and ₹20 per executed order.

## 3. Entry Greek construction

The historical dataset contains option closes but not broker/platform-reported Greeks. Therefore Phase 7C reconstructs entry Greek proxies using Black-Scholes:

- implied volatility obtained from each observed option close;
- risk-free rate (r=0);
- dividend yield (q=0);
- time-to-expiry measured to 15:30 IST on the option expiry date;
- delta, gamma, vega and theta/day calculated separately for all four legs.

Signed strategy Greek totals use the actual position signs:

- near call: -1
- near put: +1
- next call: +1
- next put: -1

Additional features:

- near- and next-expiry mean IV;
- IV term spread;
- call-minus-put IV skew for each expiry;
- absolute and signed net delta, gamma, vega and theta;
- strike moneyness and absolute moneyness;
- positive flatline magnitude.

These are **research proxies**, not a claim to reproduce Sensibull's proprietary Greek methodology exactly.

## 4. Winner vs loser comparison

Winner/loser testing used:

- Welch two-sample t-test;
- Mann-Whitney U test;
- Cliff's delta;
- Benjamini-Hochberg false-discovery-rate control across the tested feature family.

### Descriptive features with the strongest unadjusted signals

| Feature | Winner mean | Loser mean | Welch p | Mann-Whitney p | Cliff's delta | BH q |
|---|---:|---:|---:|---:|---:|---:|
| next-expiry IV skew (call-put) | -0.01095 | -0.00537 | 0.2317 | 0.0438 | -0.302 | 0.435 |
| near-expiry mean IV | 0.2660 | 0.2147 | 0.0347 | 0.0637 | +0.276 | 0.435 |
| net gamma | +0.000035 | -0.000098 | 0.0591 | 0.0637 | +0.276 | 0.435 |
| net theta/day | -3.7385 | +0.0547 | 0.2531 | 0.0510 | -0.290 | 0.435 |
| IV term spread | -0.0769 | -0.0434 | 0.0725 | 0.1318 | -0.245 | 0.540 |
| near-expiry call-put IV skew | -0.0157 | +0.0018 | 0.153 | 0.156 | -0.222 | 0.583 |
| absolute net delta | 0.0952 | 0.1942 | 0.241 | 0.294 | -0.152 | 0.771 |

The apparent differences are not robust to multiple-comparison control: **none of the tested Greek/IV/moneyness features has BH q < 0.10**. The best adjusted q is about 0.435.

### Interpretation

There are some descriptive tendencies. For example, winners have a more negative next-expiry call-minus-put IV skew proxy, higher near-expiry mean IV, less absolute delta imbalance and a different net-gamma/theta profile. However, the sample is only 63 selected trades and the signals are not statistically stable after controlling the multiple-testing family.

Thus the data do not justify converting any single Greek difference into an entry rule.

## 5. Within-week candidate analysis

At the actual decision observation, every positive candidate in the 17-strike grid was retained and compared against its realized net P&L.

Median/mean weekly Spearman associations for the main Greek-like features were generally weak and inconsistent:

- absolute net gamma: mean weekly Spearman about **+0.185**, positive in about 59% of weeks;
- near-expiry mean IV: about **+0.160**, positive in about 67% of weeks;
- near-put delta: about **+0.159**, positive in about 56% of weeks;
- absolute net vega: about **+0.028**;
- absolute net theta: about **+0.003**;
- absolute net delta: about **-0.003**;
- IV term spread: about **-0.086**;
- next-expiry IV skew: about **-0.577**, but positive correlation occurred in only about 7% of weeks.

The large-looking negative average for next-expiry IV skew is not sufficient to adopt it as a selector because selector testing and walk-forward validation below do not support improvement.

## 6. Alternative strike-selector tests

For each candidate feature, one strike per week was selected by either the maximum or minimum feature value and compared with the current **maximum positive flatline** selector.

The comparison uses paired weekly P&L and bootstrap confidence intervals. Where a feature has missing Greek values, the affected weeks are shown separately rather than treated as full-coverage evidence.

Important result:

> **Every full-coverage alternative Greek/IV/moneyness selector tested underperformed the current maximum-positive-flatline selector in-sample.**

Examples:

| Alternative selector | Mean P&L difference vs baseline | 95% paired bootstrap CI |
|---|---:|---:|
| next-expiry IV skew — minimum | -₹20.77/week | [-₹32.99, -₹10.59] |
| absolute net delta — minimum | -₹76.83/week | [-₹108.51, -₹49.51] |
| absolute net theta — minimum | -₹77.23/week | [-₹112.89, -₹46.48] |
| absolute moneyness — maximum | -₹80.23/week | [-₹161.79, -₹31.40] |
| IV term spread — minimum | -₹90.29/week | negative |
| absolute net gamma — maximum | -₹105.06/week | negative |
| IV term spread — maximum | -₹109.84/week | negative |
| absolute net delta — maximum | -₹120.94/week | negative |

The current flatline score remains the benchmark. Some feature tests have missing-Greek weeks, so reduced-coverage selectors are not treated as fair replacements.

## 7. Walk-forward validation

To reduce in-sample selection bias, an expanding-window test was run:

### Split 1

- training: 31 weeks
- test: next 16 weeks
- best Greek/IV selector chosen only from training: **near-expiry call-minus-put IV skew, maximum**
- test P&L for feature selector: **₹123,029**
- baseline test P&L: **₹124,645**
- mean difference: **-₹100.98/week**
- 95% bootstrap CI: **[-₹193.89, -₹29.63]**

### Split 2

- training: 47 weeks
- test: next 16 weeks
- same training-selected feature/direction
- test P&L for feature selector: **-₹68,751.92**
- baseline test P&L: **-₹51,002.25**
- mean difference: **-₹66.24/week**
- 95% bootstrap CI: **[-₹127.17, -₹15.44]**

The best training-selected Greek/IV selector therefore **underperformed the existing flatline selector in both walk-forward tests**.

## 8. Scientific inference

The current evidence does **not** support adding a simple single-variable Greek/IV/moneyness filter to entry strike selection.

The most important reason is not just the lack of conventional significance in the winner/loser comparison. More importantly:

1. apparent winner/loser differences disappear after multiple-testing correction;
2. alternative feature-based strike selectors underperform the baseline;
3. the best training-selected feature in two expanding walk-forward tests also underperforms out of sample.

Therefore the research conclusion for this phase is:

**Keep the existing strike-selection score as the positive estimated equal max-profit=max-loss flatline. Do not replace it with an individual Greek, IV-skew, IV-term-structure, or moneyness rule based on this sample.**

## 9. Limitations

- 63 weekly trades is a small sample for reliable multivariate inference.
- Historical broker/platform Greeks were not available; reconstructed Greeks are model proxies.
- The analysis uses option closes rather than full intraday bid/ask microstructure.
- IV inversion can be undefined or unstable for some deep-intrinsic observations.
- The tested alternatives are mostly one-feature selectors; nonlinear interactions may contain information not captured here.
- Multiple-testing correction is conservative and reduces power in this small sample.
- No causal interpretation should be attached to a descriptive Greek difference.

## 10. Strengths

- strict no-look-ahead weekly decision timing;
- same 17-strike candidate universe for baseline and alternative selectors;
- exact repository transaction-cost convention;
- winner/loser inference plus effect sizes;
- FDR multiple-testing correction;
- within-week rank correlation analysis;
- paired weekly bootstrap comparison;
- expanding walk-forward validation;
- no feature is adopted merely because it looks favorable in-sample.

## 11. Phase conclusion

Phase 7C is complete.

No Greek/IV/moneyness feature currently passes the evidence required to alter the entry strike-selection rule. The fixed primary rule remains:

**first positive weekly payoff observation → scan ATM-400..ATM+400 → select the maximum positive all-green equal max-profit=max-loss flatline → trade one candidate for that week.**

The next research work should therefore focus on final manuscript integration and, only where justified by the existing plan, richer point-in-time market-state variables such as IV surface shape, option OI/liquidity, futures basis and volatility regime interactions rather than adding a single-Greek rule.

### Compact result files

The workflow artifact contains `winner_loser_univariate_stats.csv`, `candidate_within_week_spearman.csv`, `candidate_feature_selection_tests.csv`, `walk_forward_feature_selection.csv`, and the 63-trade `selected_entry_features.csv`. These are generated by workflow run 36291838252 and should be treated as the reproducible Phase 7C analysis set.


## CRITICAL CORRECTION — outcome labels are superseded

Phase 7C winner/loser labels and selector P&Ls were generated from the prior weekly ledger, whose far-expiry legs were incorrectly held to the far expiry. Because the user's actual rule closes all four legs at the near expiry, these realized-outcome analyses are now **non-authoritative**.

The entry Greek construction itself can be retained, but winner/loser and selector analyses must be rerun after the corrected H=1 P&L is rebuilt.
