# Phase 8A — S2-S1 Predictability and Economic Filter

**Branch:** `phase-8-s2-s1-predictor`  
**Authoritative workflow:** 36293974453  
**Artifact:** phase-8A-s2-s1-predictability (artifact 10922764992)

## 1. Research question

The Phase 7B P&L decomposition showed that the static green payoff line did not determine realized economics. The central economic term was the cross-expiry settlement difference:

[
P&L = (C_1-P_1-C_2+P_2) + (S_2-S_1) - 	ext{execution/cost adjustments}.
]

The Phase 8 question was whether an **entry-time estimate** of (S_2-S_1) could be used as a weekly trade filter.

## 2. Critical strike-selection implication

At a given entry timestamp, (S_2-S_1) is common to all 17 candidate strikes. Therefore an estimate of (S_2-S_1) cannot, by itself, change which strike has the largest flatline value.

It can only:

1. act as a weekly trade/no-trade filter; or
2. interact with strike-dependent variables in a more complex model.

The Phase 8A primary test therefore used it as a trade filter.

## 3. No-look-ahead methodology

Two predictor designs were tested.

### A. Sparse weekly model

Training data consisted of previously selected weekly cycles only.

Features available at entry:
- selected-candidate IV and Greek proxies;
- positive-candidate surface summaries;
- moneyness;
- flatline state;
- spot level and spot change;
- calendar variables;
- lagged realized (S_2-S_1).

Models:
- Ridge regression
- Random Forest regression
- Histogram Gradient Boosting regression

Validation:
- expanding walk-forward;
- first 31 weekly cycles reserved for initial training;
- next 32 selected weekly decisions evaluated strictly out of sample.

### B. All-timestamp model

The sparse design was expanded because only 63 selected weeks provide very little training information.

The all-timestamp model used:
- **905 historical entry timestamps**;
- **255 weekly expiry cycles** in the cached dataset;
- all prior timestamps from earlier weekly cycles for training;
- equal weekly-cycle weighting so weeks with many timestamps did not dominate;
- the same 17-strike surface/Greek/IV features;
- the current week's test features taken only from its actual first-positive decision timestamp.

After the initial 31 weekly cycles, **43 weekly decision cycles** were strictly out of sample.

No realized (S_2-S_1) from the test cycle was used as an entry input.

## 4. Target distribution

Across the 63 current primary weekly trades:

- mean (S_2-S_1): **+4.77 index points**
- standard deviation: **392.59 points**
- positive (S_2-S_1): **57.14%** of weeks

The very small mean relative to the dispersion is important: the target is highly variable.

## 5. Out-of-sample predictive accuracy

### Sparse selected-week model — 32 OOS weeks

| Model | MAE (points) | RMSE (points) | Sign accuracy | Correlation |
|---|---:|---:|---:|---:|
| Ridge | 433.66 | 531.13 | 53.13% | +0.075 |
| Random Forest | 361.81 | 442.19 | 50.00% | -0.092 |
| Hist. Gradient Boosting | 391.13 | 473.24 | 46.88% | -0.144 |

The Ridge filter improved the net result in this particular 32-week block by ₹17,468, but this was not stable enough to adopt; its first-half gain was almost completely offset in the second half.

### All-timestamp model — 43 OOS weekly decision cycles

| Model | MAE (points) | RMSE (points) | Sign accuracy | AUC |
|---|---:|---:|---:|---:|
| Ridge | 416.20 | 501.54 | 44.19% | 0.486 |
| Random Forest | 382.08 | 477.43 | 51.16% | 0.514 |
| Hist. Gradient Boosting | 393.34 | 489.96 | 53.49% | 0.541 |

The best sign classifier was Hist. Gradient Boosting, but its AUC was only about 0.54. Random Forest was almost exactly chance at about 0.51.

## 6. Economic trade-filter test

The current primary strategy on the 43 OOS test weeks produced:

**₹-10,634.75**

Applying a strict predicted-(S_2-S_1>0) filter:

| Model | Weeks traded | Net P&L | Change vs baseline |
|---|---:|---:|---:|
| Ridge | 18 | ₹-5,022.63 | +₹5,612.13 |
| Random Forest | 23 | ₹91,388.05 | +₹102,022.80 |
| Hist. Gradient Boosting | 20 | ₹64,981.67 | +₹75,616.43 |

These large improvements are **not sufficient evidence of a reliable edge** because model classification was close to random and the time-block behaviour was unstable.

## 7. Stability test

The all-timestamp Random Forest filter showed:

| Time block | Baseline | RF filter | Difference |
|---|---:|---:|---:|
| First 15 OOS weeks | ₹-104,760.52 | ₹36,116.50 | **+₹140,877.03** |
| Middle 14 weeks | ₹157,021.28 | ₹98,795.21 | **-₹58,226.07** |
| Last 14 weeks | ₹-62,895.51 | ₹-43,523.66 | **+₹19,371.85** |

The same instability appears for Histogram Gradient Boosting.

For the Random Forest filter, paired weekly bootstrap:

- mean improvement: **+₹2,372.62/week**
- 95% CI: **₹-2,740.68 to ₹7,993.14**
- sign accuracy: **51.16%**
- AUC: **0.5136**

For Histogram Gradient Boosting:

- mean improvement: **+₹1,758.52/week**
- 95% CI: **₹-3,680.81 to ₹7,624.21**
- sign accuracy: **53.49%**
- AUC: **0.5407**

For Ridge:

- mean improvement: **+₹130.51/week**
- 95% CI: **₹-4,710.56 to ₹5,446.23**
- sign accuracy: **44.19%**
- AUC: **0.4864**

All bootstrap intervals include zero.

## 8. Interpretation

The apparent economic uplift from the Random Forest and Gradient Boosting filters is not supported by sufficiently strong predictive discrimination.

The models are predicting a target with very high dispersion and weak out-of-sample directional accuracy. The largest improvement comes from a subset filter whose performance reverses substantially across chronological blocks.

Therefore the data do **not** justify converting predicted (S_2-S_1) into a live weekly trade filter.

## 9. Decision

**Phase 8A conclusion: do not adopt an (S_2-S_1) filter.**

The result is not that (S_2-S_1) is mathematically irrelevant. It is the opposite: it is the dominant economic risk term. The result is that, with the information presently cached and the available sample, we cannot predict it reliably enough out of sample to use as an entry decision.

Because the Phase 8 stop rule was to avoid endless predictor searching when the internal baseline is not stable, **Phase 8A is considered complete and the external-variable expansion is not promoted to a new trading rule.**

## 10. Strengths

- strict chronological walk-forward validation;
- no use of future (S_2-S_1) in prediction;
- expanded training set using all prior entry timestamps;
- equal weekly-cycle weighting;
- multiple model classes;
- explicit transaction-cost model;
- direct economic trade-filter evaluation;
- chronological stability testing;
- paired weekly bootstrap uncertainty.

## 11. Limitations

- only 43 OOS weekly decision cycles in the expanded test;
- target dispersion is much larger than its mean;
- historical option closes are not full quote-level bid/ask data;
- some predictors are reconstructed Greek/IV proxies;
- no point-in-time futures-basis/FII-DII/global-market feature set was added in this phase;
- the NIFTY regime history in this cached dataset is limited relative to the breadth needed for high-confidence machine-learning claims.

## 12. Final implication for the strategy

The primary strategy remains:

**first positive weekly opportunity → scan ATM-400..ATM+400 → select maximum positive flatline → trade one candidate.**

Its current historical implementation remains negative after modeled costs.

Phase 8 does not rescue it through an (S_2-S_1) filter.

The research should therefore move to final synthesis rather than adding more predictors without a new, predeclared source of information or a materially larger independent dataset.


## CRITICAL CORRECTION — Phase 8A is superseded

The Phase 8A predictor was trained and evaluated against a realized-P&L decomposition that assumed the far-expiry options remained open until the far expiry. The user's actual strategy manually closes those far legs at the near expiry. Consequently the S2-S1 target and all Phase 8A economic filter results are not valid for the actual strategy and must not be used for deployment decisions.

Phase 8A may be retained as a historical analysis of a different holding-period variant, but it is not part of the corrected strategy evidence.
