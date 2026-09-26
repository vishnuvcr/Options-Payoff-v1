# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Active phase:** Phase 4 — Statistical validation and robustness
**Status:** Phase 1 analytical validation, Phase 2 data pipeline, Phase 3 backtest/cost engine and Phase 4 validation framework are implemented. Historical workflow execution remains pending because this session's runtime cannot resolve external data endpoints.
**Date:** 2026-09-26

## Key finding

The four-leg position is a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With common strike K, the actual expiry component is S2 - S1. A payoff chart that applies one identical terminal spot to both expiries will show a flat line because the two intrinsic terms cancel. The flatline therefore cannot be interpreted as a flat realized held-to-expiry payoff.

## Research branches

- `phase-1-specification` — strategy equations, analytical payoff functions and unit tests
- `phase-2-data` — historical data source, cache/extraction pipeline and literature review
- `phase-3-backtest` — trigger selection, cost model and backtest workflow

## Main research files

- `research/RESEARCH_PLAN.md` — fixed six-phase protocol
- `research/STATUS.md` — live phase/status
- `research/ERROR_LOG.md` — mistakes and corrections
- `research/ACTIVITY_LOG.md` — observable research/repository activity
- `research/SOURCES.md` — official and research sources
- `docs/PHASE_3_BACKTEST.md` — current backtest methodology

## Important safeguards

The 2.5% denominator in the original rule is not specified, so the engine tests explicit denominator modes rather than silently inventing one.

Phase 2 source bars are OHLCV/OI rather than bid/ask, so entry prices are 09:20 close proxies and Phase 3 applies configurable slippage.

A verified historical NIFTY lot-size calendar and broker-specific charges are required before final multi-year rupee P&L. Paytm Money's public pages currently show inconsistent F&O brokerage figures, so the broker rate is intentionally configurable.

Raw public market data are cached in GitHub Actions rather than blindly downloaded on every run. Each phase has a manual workflow.