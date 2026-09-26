# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Active research phase:** Phase 2 — Market-data acquisition, cleaning and cache
**Status:** Phase 1 complete; Phase 2 pipeline implemented and awaiting manual GitHub Actions execution/validation.
**Date:** 2026-09-26

### Live research branches

- phase-1-specification — strategy equations, payoff tests and Phase 1 workflow
- phase-2-data — data manifest, extractor, literature review and Phase 2 workflow

The agreed six-phase research plan is unchanged.

## Key analytical finding so far

The position is a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With common strike K, its expiry payoff is S(next expiry) - S(near expiry). A chart that applies one identical terminal spot to both expiries will look flat because the intrinsic terms cancel. Therefore the flatline chart cannot be treated as the strategy's realized held-to-expiry payoff.

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
- src/options_payoff.py
- tests/test_options_payoff.py
- scripts/extract_strategy_inputs.py

## Phase structure

0. Bootstrap and governance
1. Strategy specification and analytical validation
2. Market-data acquisition, cleaning and cache
3. Backtest engine and transaction-cost model
4. Statistical validation and robustness
5. Regime and cross-market attribution
6. Manuscript and final conclusion

Each phase is implemented on its own branch and has a manual GitHub Actions workflow.

## Data and execution safeguards

The Phase 2 source is the public thetrademarkk/india-index-options-1m dataset on Hugging Face. Its OHLCV/OI bars are sufficient to construct a historical research input table but do not provide bid/ask quotes, so Phase 2 marks prices as 09:20 close proxies. Phase 3 must therefore apply conservative spread/slippage assumptions and verify dated broker/exchange charges before net profitability is assessed.

Historical NIFTY expiry handling is data-driven and preserves the 2025 Thursday-to-Tuesday expiry transition.

## Reproducibility

Important source metadata, checksums/revisions, transformations, data-quality flags and research status are recorded in the repository. Raw public data are cached in GitHub Actions rather than blindly re-downloaded on every run.