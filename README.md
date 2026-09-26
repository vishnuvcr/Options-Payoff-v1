# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Active research phase:** Phase 3 — Backtest engine and transaction-cost model
**Status:** IMPLEMENTED; historical execution is pending manual GitHub Actions run.
**Date:** 2026-09-26

## Key analytical finding

The position is a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With common strike K, its expiry payoff is S(next expiry) - S(near expiry). A chart that applies one identical terminal spot to both expiries will look flat because the intrinsic terms cancel. That flatline is not the realized held-to-expiry payoff.

## Current implementation

- Phase 1: analytical payoff model and unit tests.
- Phase 2: reproducible NIFTY option/index data extraction with cached Hugging Face source files.
- Phase 3: chart-trigger selection, gross cross-expiry P&L, slippage, brokerage, exchange fees, SEBI fee, stamp duty, GST, entry-sale STT and expiry-exercise STT.

## Critical open inputs

The 2.5% chart denominator is not specified in the original rule, so the backtest exposes three denominator modes rather than silently selecting one.

A historical NIFTY lot-size calendar is required for multi-year rupee P&L; the Phase 3 workflow requires an explicit verified lot size for the date window.

Bid/ask quotes are not available in the primary Phase 2 dataset, so 09:20 close is only a proxy. The base research run uses configurable slippage and later validation must compare against quote-level data when available.

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
- src/options_payoff.py
- src/costs.py
- tests/test_options_payoff.py
- tests/test_costs.py
- scripts/extract_strategy_inputs.py
- scripts/run_backtest.py

## Manual workflows

- Phase 1: .github/workflows/phase-1-specification.yml
- Phase 2: .github/workflows/phase-2-data.yml
- Phase 3: .github/workflows/phase-3-backtest.yml

Each phase remains on its own branch and the workflow is manually runnable.

## Reproducibility

Source revisions, assumptions, data-quality flags, research status and errors are recorded. Raw public source data are cached in GitHub Actions instead of being downloaded blindly on every run.