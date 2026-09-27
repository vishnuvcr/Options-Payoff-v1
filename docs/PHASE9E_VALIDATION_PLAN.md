# Phase 9E — Frozen-rule H1 validation

**Branch:** `phase-9E-h1-validation`  
**Status:** planned/executing  
**Parent evidence:** Phase 9D authoritative run 36302077730  
**Primary artifact:** `phase-9D-final-H1-evidence`

## Purpose

Phase 9E validates the **frozen Phase 9D H1 rule** without changing its entry, strike-selection, expiry, exit, or cost conventions. The purpose is to determine whether the positive Phase 9D historical result is temporally stable and how much uncertainty remains.

The rule under validation is:

1. For each weekly expiry cycle, begin checking NIFTY one-minute observations at 09:20 IST.
2. Continue through all available timestamps to 15:29 IST and across later trading days in the same weekly cycle until the first positive/all-green flatline appears.
3. At that first positive observation, evaluate the 17 common strikes ATM-400 through ATM+400 in 50-point steps.
4. Select the candidate with the maximum positive estimated equal Max Profit = Max Loss flatline value.
5. Close the four legs at the near weekly expiry; manually square off the far-expiry CE/PE at the near-expiry close using observed point-in-time option prices.
6. Primary execution model: 0.25% premium slippage and ₹20 brokerage per executed order, with the repository's statutory charge model.

No 2.5% threshold, margin gate, S2-S1 filter, Greek filter, or new parameter will be introduced in this phase.

## Research questions

**RQ9E-1.** Does the frozen rule retain positive net P&L across chronological calendar-year cohorts?

**RQ9E-2.** Do anchored chronological holdout years remain positive when all rule parameters are held fixed?

**RQ9E-3.** Does uncertainty around mean realized trade P&L remain compatible with zero after dependence-aware block bootstrap?

**RQ9E-4.** How sensitive is the temporal result to premium slippage and brokerage assumptions already defined in Phase 9D?

**RQ9E-5.** Are the remaining losses concentrated in particular entry-time or strike-shift regions that require further research rather than an immediate rule change?

## Aims

1. Validate the frozen H1 rule on a chronological basis.
2. Quantify uncertainty using both IID and circular four-trade block bootstrap diagnostics.
3. Report calendar-year and anchored holdout performance without tuning parameters on test periods.
4. Reproduce execution-cost sensitivity from the authoritative Phase 9D artifact.
5. Record the validation outcome and decide whether H2/H3 can be reopened under the predeclared research plan.

## Statistical methodology

### Primary metrics

For each cohort and holdout:

- number of complete realized trades;
- net P&L;
- mean and median net P&L per trade;
- realized win rate;
- profit factor;
- maximum drawdown within the cohort;
- total modeled costs;
- largest win and largest loss.

Win-rate confidence interval uses the Wilson 95% interval.

Mean-P&L uncertainty uses:

- 20,000 IID bootstrap resamples;
- 20,000 circular moving-block bootstrap resamples with block length 4 trades.

These intervals are historical-sample diagnostics, not forecasts.

### Chronological validation

Each calendar year is evaluated as a fixed, untouched **test cohort** in the validation report. In addition, anchored holdout diagnostics are reported for 2022, 2023, 2024, 2025 and 2026, where all earlier years are shown as historical context and the current year is the test cohort.

Because the strategy rule was designed before this Phase 9E report but the historical sample was already observed during strategy development, these are **rule-frozen temporal validation diagnostics, not a pristine future-data holdout**. A genuinely independent future holdout requires data not available when the rule was developed.

### Execution sensitivity

The validation must reproduce the Phase 9D tested scenarios:

- slippage: 0.00%, 0.25%, 0.50%, 1.00%, ₹20/order;
- brokerage: ₹10, ₹20, ₹40/order at 0.25% slippage.

The primary conclusion remains tied to 0.25% slippage and ₹20/order unless a later phase explicitly changes the cost model.

## Predeclared interpretation rules

- No rule parameter may be changed in response to a holdout-period result.
- A positive point estimate with a confidence interval spanning zero is reported as **historically positive but statistically uncertain**, not as proof of a persistent edge.
- Regime/timing/strike-shift subgroup results are descriptive unless separately preregistered and independently validated.
- The 100% selected chart-positive rate is a selection-condition metric and must never be reported as the realized win rate.
- The three Phase 9D lot-size-incompatible selections remain excluded from realized P&L; no synthetic lot normalization is allowed.

## Phase-exit rule

Phase 9E exits with one of two evidence states:

1. **Validation-supporting:** chronological cohorts remain positive, execution sensitivity remains economically positive under the tested stress cases, and uncertainty diagnostics are reported.
2. **Validation-inconclusive:** one or more of the above fails or uncertainty remains too large to support persistence.

In either state, H2/H3 may only be reopened after the report explicitly states the evidence and limitations. No new entry filter is adopted inside Phase 9E.

## Required outputs

- `docs/PHASE9E_VALIDATION.md`
- `results/phase9e/summary.json`
- `results/phase9e/annual.csv`
- `results/phase9e/anchored_holdouts.csv`
- `results/phase9e/execution_sensitivity.csv`
- `results/phase9e/bootstrap.json`
- uploaded GitHub Actions evidence artifact
- README/status/activity/error-log updates after execution

## Reproducibility

The validation consumes the archived Phase 9D artifact from run **36302077730** and does not download fresh market data. The workflow contains a manual `workflow_dispatch` entry and a push trigger for reproducible reruns.
