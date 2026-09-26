# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Phase:** 0 — Research bootstrap  
**Status:** Initialized; Phase 1 specification is next.  
**Date:** 2026-09-26

The strategy under study is:

1. Sell an ATM call and buy an ATM put in the near weekly expiry.
2. Buy an ATM call and sell an ATM put in the next weekly expiry.
3. Reproduce the user's payoff-chart trigger, including the >2.5% threshold.
4. When ATM does not qualify, test a common strike shifted by -400 and +400 points.
5. Hold to expiry/settlement according to the strategy rules.
6. Include bid/ask execution assumptions, slippage, brokerage, statutory charges and other transaction costs.

### Important modeling note

The near-week and next-week synthetic-forward legs have different expiries. Therefore, a single one-dimensional payoff chart that assigns the same terminal spot price to both expiries can show a misleading flat line. The research engine will separately model the underlying settlement at the two expiries and will retain the original chart rule only as a signal to be tested.

## Research files

- research/RESEARCH_PLAN.md
- research/STATUS.md
- research/ERROR_LOG.md
- research/ACTIVITY_LOG.md
- research/SOURCES.md
- research/RESEARCH_INSTRUCTIONS.md

## Phases

- Phase 0 — Bootstrap and research governance
- Phase 1 — Strategy specification and analytical validation
- Phase 2 — Market-data acquisition, cleaning and cache
- Phase 3 — Backtest engine and transaction-cost model
- Phase 4 — Statistical validation and robustness
- Phase 5 — Regime/cross-market attribution
- Phase 6 — Manuscript, conclusion and future research

Each research phase will live on its own Git branch and expose a manual GitHub Actions workflow.

## Scope

Default test market: NIFTY 50 weekly index options, because NSE currently lists four weekly NIFTY 50 option expiries and the weekly expiry is Tuesday (or the preceding trading day when Tuesday is a holiday). This is a documented default, not a claim that the strategy is suitable for trading.

The backtest will remain parameterized so another eligible underlying can be substituted later.

## Costs

The model will use dated, configurable cost inputs rather than silently assuming zero friction. In particular, NSE states that from 1 April 2026 the STT rate on sale of an option is 0.15% of option premium; broker brokerage and other charges are modeled separately.

## Reproducibility

Data sources, dataset hashes/versions, assumptions, code versions, and backtest outputs will be recorded so results can be regenerated without repeatedly downloading the same data.
