# Research status

**As of:** 2026-09-26  
**Active branch:** main bootstrap  
**Overall phase:** 0 — Bootstrap complete

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | NEXT | Create phase-1 branch and encode strategy/payoff tests. |
| 2 Data | NOT STARTED | Select and validate historical NIFTY option dataset. |
| 3 Backtest | NOT STARTED | Execute historical strategy with full cost model. |
| 4 Validation | NOT STARTED | Out-of-sample and robustness analysis. |
| 5 Regimes | NOT STARTED | Conditional/regime attribution. |
| 6 Manuscript | NOT STARTED | Final research manuscript and supplements. |

## Current findings

1. The repository was empty at project start; a reproducible research structure is now being initialized.
2. NSE's current NIFTY 50 contract specification lists four weekly expiries and Tuesday weekly expiry, subject to holiday adjustment.
3. The strategy combines a short near-expiry synthetic forward with a long next-expiry synthetic forward. The different maturities make a one-dimensional flat payoff chart potentially misleading; the engine will evaluate the two expiries separately.
4. Current NSE guidance shows option-sale STT at 0.15% from 2026-04-01; this must be reflected in the cost model for 2026 trades and parameterized for earlier periods.

## Blockers

- Historical intraday option data must be sourced, licensed/qualified, cached and validated before the full backtest.
- The 2.5% denominator needs to remain explicit/configurable because the user's description does not define the reference capital/base.

## Next step

Phase 1: implement the strategy specification, payoff equations, and unit tests.


## Latest branch update — 2026-09-26

Phase 5 regime-attribution protocol has been implemented on branch `phase-5-regimes`. It is intentionally gated on the validated Phase 3/4 historical trade ledger. No empirical regime result has been fabricated. See the Phase 5 branch for the protocol, source audit, script and manual workflow.
