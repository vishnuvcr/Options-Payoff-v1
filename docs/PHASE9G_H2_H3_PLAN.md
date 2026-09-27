# Phase 9G — H2/H3 far-expiry selection research

**Branch:** `phase-9G-h2-h3-far-expiry-selection`
**Parent:** Phase 9F completed corrected-H1 cross-market/regime audit

## Operational definitions

- **H1:** far expiry = the next eligible weekly expiry after the near weekly expiry (rank 1). This is the current corrected baseline.
- **H2:** far expiry = the second eligible weekly expiry after the near weekly expiry (rank 2).
- **H3:** far expiry = the third eligible weekly expiry after the near weekly expiry (rank 3).

These are fixed calendar-horizon variants. No dynamic far-expiry switching is allowed inside this phase.

## Research questions

1. Does changing only the far-expiry horizon from H1 to H2 or H3 alter realized net P&L after the same near-expiry manual-close convention and costs?
2. Does H2 or H3 change the first-positive decision timestamp and selected strike distribution relative to H1?
3. Are any H2/H3 economic differences stable across chronological years?
4. On the same weekly cycles, what is the paired per-cycle P&L difference H2-H1 and H3-H1?
5. Do execution-cost stresses change the relative ordering of the predefined horizons?
6. Which horizon, if any, should become a candidate for a later independent holdout — without turning the comparison into a dynamic selector in this phase?

## Frozen strategy components

All of the following stay identical across H1/H2/H3:

- NIFTY 1-minute scanning from 09:20 through 15:29 IST.
- Continue across later timestamps and later trading days within the same weekly cycle until the first positive/all-green flatline appears.
- At the first positive timestamp, evaluate the common ATM-400..ATM+400 50-point grid and select the maximum positive estimated equal Max Profit = Max Loss candidate.
- Near CE/PE settle at near weekly expiry.
- Far CE/PE are manually squared off at the near-expiry close using the last available far-option bar at or before the near-expiry index close.
- 0.25% premium slippage and ₹20/order are the primary cost assumptions; ₹10/₹20/₹40 brokerage and 0.50%/1.00% slippage remain sensitivity checks.
- No 2.5% margin threshold, no Greek filter, no India-VIX filter, no FII/DII filter, and no Phase 9F regime filter.

## Statistical methodology

Each horizon is evaluated independently with:

- complete realized trade count and incomplete selection audit;
- net/gross P&L, costs, mean/median trade P&L;
- win rate with Wilson 95% interval;
- profit factor and maximum drawdown;
- annual chronological cohorts;
- IID and four-trade circular block bootstrap for mean trade P&L;
- paired per-near-expiry differences against H1 where both horizons have complete trades;
- 20,000 paired sign-permutation draws for H2-H1 and H3-H1 mean-difference p-values;
- Benjamini-Hochberg correction across the two primary paired comparisons.

The comparison is predeclared. No horizon is chosen based on a later subgroup or regime result.

## Data construction

Yearly Actions jobs regenerate H1/H2/H3 decision surfaces from the cached Hugging Face NIFTY option source and NIFTY index history. Each horizon reuses the same intraday timestamps and near-expiry cycle definition; only the far-expiry rank changes.

Derived compact per-year selected ledgers and final merged horizon ledgers are stored under `results/phase9g` so subsequent analysis does not redownload source data.

Phase 9G explicitly checks that the H1 rank-1 reconstruction reproduces the authoritative Phase 9D baseline: 169 complete realized trades and the same primary net P&L within a documented floating-point tolerance. Failure of this invariant stops the phase.

## Interpretation

A horizon with a positive historical paired difference is not automatically a deployable strategy. A later untouched-data holdout is required before production use. The phase may identify a horizon as a **candidate for further validation** but may not create a dynamic expiry selector.

## Phase-exit criteria

- H1/H2/H3 ledgers reproducibly reconstructed.
- H1 baseline reproduction passes.
- Pairwise H2-H1/H3-H1 statistics completed.
- Annual and execution sensitivity tables completed.
- Incomplete selections and data-availability differences documented.
- One fixed horizon may be nominated for a later independent holdout, or the baseline may remain the candidate if no robust improvement appears.

## Required outputs

- `docs/PHASE9G_RESULTS.md`
- `results/phase9g/horizon_summary.csv`
- `results/phase9g/annual_summary.csv`
- `results/phase9g/paired_comparisons.csv`
- `results/phase9g/execution_sensitivity.csv`
- `results/phase9g/bootstrap.json`
- `results/phase9g/h1_reproduction_check.json`
- Actions evidence artifact
- updated README/status/activity/error logs