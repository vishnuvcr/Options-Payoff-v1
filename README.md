# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current status

**Phase:** 1 — Strategy specification and analytical validation  
**Status:** COMPLETE; Phase 2 data work is next.  
**Date:** 2026-09-26

The strategy under study is:

1. Sell an ATM call and buy an ATM put in the near weekly expiry.
2. Buy an ATM call and sell an ATM put in the next weekly expiry.
3. Reproduce the user's payoff-chart trigger, including the >2.5% threshold.
4. When ATM does not qualify, test a common strike shifted by -400 and +400 points.
5. Hold to expiry/settlement according to the strategy rules.
6. Include bid/ask execution assumptions, slippage, brokerage, statutory charges and other transaction costs.

### Phase 1 finding

The four legs are a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. With a common strike K, the intrinsic expiry component is:

S(next expiry) - S(near expiry)

A one-dimensional chart that applies the same hypothetical terminal spot to both expiries will cancel the intrinsic terms and show a flat line. That flatline is therefore not a valid representation of the held-to-expiry risk.

The Phase 1 unit tests reproduce the flatline construction and independently prove that the economically correct two-expiry P&L varies with the two settlement prices.

## Research files

- research/RESEARCH_PLAN.md
- research/STATUS.md
- research/ERROR_LOG.md
- research/ACTIVITY_LOG.md
- research/SOURCES.md
- research/RESEARCH_INSTRUCTIONS.md
- docs/PHASE_1_SPECIFICATION.md
- src/options_payoff.py
- tests/test_options_payoff.py
- config/strategy_phase1.toml

## Phases

- Phase 0 — Bootstrap and research governance — COMPLETE
- Phase 1 — Strategy specification and analytical validation — COMPLETE
- Phase 2 — Market-data acquisition, cleaning and cache — NEXT
- Phase 3 — Backtest engine and transaction-cost model
- Phase 4 — Statistical validation and robustness
- Phase 5 — Regime/cross-market attribution
- Phase 6 — Manuscript, conclusion and future research

Each research phase will live on its own Git branch and expose a manual GitHub Actions workflow.

## Scope

Default test market: NIFTY 50 weekly index options, because NSE currently lists four weekly NIFTY 50 option expiries and the weekly expiry is Tuesday (or the preceding trading day when Tuesday is a holiday). This is a documented default, not a claim that the strategy is suitable for trading.

## Costs

The model uses dated, configurable cost inputs rather than silently assuming zero friction. NSE states that from 1 April 2026 the STT rate on sale of an option is 0.15% of option premium; broker brokerage and other charges are modeled separately.

## Reproducibility

Data sources, dataset versions/checksums, assumptions, code versions, and backtest outputs will be recorded so results can be regenerated without repeatedly downloading the same data.
