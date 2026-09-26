# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Phase:** 2 — Market-data acquisition, cleaning and cache
**Status:** Phase 2 data build validated in GitHub Actions; 2,763 candidate rows were generated for 2021-06-01 through 2026-08-31 (2,128 `ok`, 610 shifted-strike unavailable, 25 missing-settlement). Phase 3 handoff has been repaired to use branch-local trigger files.
**Date:** 2026-09-26

The strategy under study is:

1. Sell an ATM call and buy an ATM put in the near weekly expiry.
2. Buy an ATM call and sell an ATM put in the next weekly expiry.
3. Reproduce the user's payoff-chart trigger, including the >2.5% threshold.
4. When ATM does not qualify, test a common strike shifted by -400 and +400 points.
5. Hold to expiry/settlement according to the strategy rules.
6. Include bid/ask execution assumptions, slippage, brokerage, statutory charges and other transaction costs.

### Phase 1 finding

The four legs are a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With a common strike K, the intrinsic expiry component is S(next expiry) - S(near expiry). A one-dimensional chart that applies the same hypothetical terminal spot to both expiries will show a flat line because the two synthetic-forward intrinsic terms cancel. That flatline is not a valid representation of the held-to-expiry cross-expiry P&L.

### Phase 2 data finding

The primary public research dataset is thetrademarkk/india-index-options-1m on Hugging Face. The pipeline uses the NIFTY index file plus per-expiry option files, preserves the historical Thursday-to-Tuesday NIFTY expiry transition, and caches downloaded source files in GitHub Actions. The dataset provides OHLCV/OI bars, not bid/ask quotes, so Phase 2 marks the base entry prices as 09:20 close proxies. Phase 3 must stress execution costs explicitly rather than treating closes as executable quotes.

## Research files

- research/RESEARCH_PLAN.md
- research/STATUS.md
- research/ERROR_LOG.md
- research/ACTIVITY_LOG.md
- research/SOURCES.md
- research/RESEARCH_INSTRUCTIONS.md
- docs/PHASE_1_SPECIFICATION.md
- docs/PHASE_2_DATA_PLAN.md
- docs/LITERATURE_REVIEW.md
- src/options_payoff.py
- tests/test_options_payoff.py
- scripts/extract_strategy_inputs.py
- data/SOURCE_MANIFEST.json

## Phases

- Phase 0 — Bootstrap and research governance — COMPLETE
- Phase 1 — Strategy specification and analytical validation — COMPLETE
- Phase 2 — Market-data acquisition, cleaning and cache — IN PROGRESS
- Phase 3 — Backtest engine and transaction-cost model
- Phase 4 — Statistical validation and robustness
- Phase 5 — Regime/cross-market attribution
- Phase 6 — Manuscript, conclusion and future research

Each research phase will live on its own Git branch and expose a manual GitHub Actions workflow.

## Scope

Default test market: NIFTY 50 weekly index options. Current NSE contract specifications list four weekly expiries and Tuesday weekly expiry, subject to holiday adjustment. The historical pipeline also respects the 2025 transition from Thursday to Tuesday.

## Costs

The model uses dated, configurable cost inputs rather than silently assuming zero friction. NSE states that from 1 April 2026 the STT rate on sale of an option is 0.15% of option premium; broker brokerage and other charges are modeled separately.

## Reproducibility

Data sources, dataset versions/checksums, assumptions, code versions, and backtest outputs will be recorded so results can be regenerated without repeatedly downloading the same source files.