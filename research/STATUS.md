# Research status

**As of:** 2026-09-26  
**Active branch:** phase-1-specification  
**Overall phase:** 1 — Strategy specification and analytical validation COMPLETE

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | COMPLETE | Strategy equations, strike candidates, threshold helper, tests, and manual workflow added. |
| 2 Data | NEXT | Select, acquire and validate historical NIFTY option data. |
| 3 Backtest | NOT STARTED | Execute historical strategy with full cost model. |
| 4 Validation | NOT STARTED | Out-of-sample and robustness analysis. |
| 5 Regimes | NOT STARTED | Conditional/regime attribution. |
| 6 Manuscript | NOT STARTED | Final research manuscript and supplements. |

## Phase 1 results

1. The position can be decomposed into a short near-expiry synthetic forward and a long next-expiry synthetic forward.
2. For a common strike K, the expiry intrinsic component is S2 - S1, not zero.
3. A one-dimensional chart that applies the same terminal spot to both expiries is flat at the initial net premium cashflow. This is a projection artifact, not evidence of flat realized P&L.
4. The 2.5% threshold must remain parameterized because the original rule does not specify the denominator.
5. Default deterministic research assumptions are NIFTY 50, 09:20 IST entry observation, ATM/-400/+400 common-strike candidates and one lot for reporting.

## Verification

Phase 1 unit tests pass locally for:
- static flatline payoff construction
- cross-expiry P&L directionality
- a hidden-loss example
- strike-candidate construction
- strict >2.5% threshold logic

## Blockers

- Historical intraday option data must be sourced, licensed/qualified, cached and validated before Phase 3.
- The primary backtest needs exact entry fills and settlement prices for both expiries.
