# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Active research phase:** Phase 5 — Regime and cross-market attribution protocol
**Status:** FRAMEWORK IMPLEMENTED; workflow handoffs repaired; empirical execution remains gated on Phase 3/4 historical artifacts.
**Date:** 2026-09-26

## Key analytical finding

The position is a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With common strike K, its economically correct expiry component is S(next expiry) - S(near expiry). A chart that applies one identical terminal spot to both expiries will look flat because the intrinsic terms cancel. That flatline is not the realized held-to-expiry payoff.

## Current implementation

- Phase 1: analytical payoff model and unit tests.
- Phase 2: reproducible NIFTY option/index data extraction with cached public source files.
- Phase 3: chart-trigger selection, gross cross-expiry P&L, historical lot handling, slippage and transaction-cost model.
- Phase 4: statistical validation and robustness framework.
- Phase 5: point-in-time regime/cross-market attribution protocol and manual workflow.

## Critical open inputs

The 2.5% chart denominator is not specified in the original rule, so the backtest exposes multiple denominator modes rather than silently selecting one.

Historical NIFTY lot-size transitions are handled by expiry date; unequal-lot near/next pairs are excluded from the one-for-one synthetic-forward sample.

Bid/ask quotes are not available in the primary Phase 2 dataset, so 09:20 close is a proxy. Quote-level execution analysis requires a separately validated source.

## Research files

- research/RESEARCH_PLAN.md
- research/RESEARCH_INSTRUCTIONS.md
- research/STATUS.md
- research/ERROR_LOG.md
- research/ACTIVITY_LOG.md
- research/SOURCES.md
- docs/PHASE_1_SPECIFICATION.md
- docs/PHASE_2_DATA_PLAN.md
- docs/LITERATURE_REVIEW.md
- docs/PHASE_3_BACKTEST.md
- docs/PHASE_4_VALIDATION.md
- docs/PHASE_5_REGIME_ANALYSIS.md
- docs/PHASE_5_SOURCE_AUDIT.md
- scripts/analyze_regimes.py

## Manual workflows

- Phase 1: .github/workflows/phase-1-specification.yml
- Phase 2: .github/workflows/phase-2-data.yml
- Phase 3: .github/workflows/phase-3-backtest.yml
- Phase 4: .github/workflows/phase-4-validation.yml
- Phase 5: .github/workflows/phase-5-regimes.yml

Each phase remains on its own branch and the workflow is manually runnable. Phase 4 and Phase 5 now accept a completed Phase 3 run ID and download its artifact, so separate workflow runs no longer depend on a shared workspace.

### Current manual execution sequence

1. Run `Phase 2 - Data acquisition and validation` on `phase-2-data` and record the workflow run ID.
2. Run `Phase 3 - Backtest` on `phase-3-backtest` and pass the Phase 2 run ID when available. The workflow can fall back to rebuilding the inputs.
3. Run `Phase 4 - Statistical validation` on `phase-4-validation` and pass the Phase 3 run ID.
4. Run `Phase 5 - Regime Attribution` on `phase-5-regimes` and pass the same Phase 3 run ID; add a point-in-time regime table when available.
5. Only after those artifacts exist should Phase 6 manuscript work begin.

## Current research conclusion

The flatline chart remains a signal candidate, not evidence of a risk-free payoff. No historical performance conclusion has been fabricated while the required GitHub Actions artifacts are unavailable.

## Reproducibility

Source revisions, assumptions, data-quality flags, research status and errors are recorded. Public source data should be cached in GitHub Actions rather than downloaded blindly on every run.