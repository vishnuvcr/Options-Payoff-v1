# Research status

**As of:** 2026-09-26
**Active branch:** phase-5-regimes
**Overall phase:** 5 — Regime attribution framework IMPLEMENTED; workflow handoffs repaired; empirical execution still gated on Phase 3/4 artifacts

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | COMPLETE | Strategy equations, payoff tests and manual workflow added. |
| 2 Data | IMPLEMENTED; VALIDATION PENDING | Extractor, source manifest and cache workflow exist; runtime artifact still required. |
| 3 Backtest | IMPLEMENTED; VALIDATION PENDING | Cost-aware ledger exists in code; historical run has not been executed in this session. |
| 4 Validation | IMPLEMENTED; EXECUTION PENDING | Statistical/robustness framework exists; requires Phase 3 results. |
| 5 Regimes | FRAMEWORK COMPLETE; EXECUTION BLOCKED | Point-in-time regime protocol, script and manual workflow added; requires validated trade ledger. |
| 6 Manuscript | NOT STARTED | Starts after empirical Phases 3–5 are complete. |

## Current analytical findings

1. The static flatline chart is not the realized payoff of the cross-expiry position.
2. The economically relevant expiry component is S2 - S1, plus the entry premium edge and transaction costs.
3. The 2.5% denominator is unspecified and must remain an explicit sensitivity dimension.
4. Historical NIFTY lot-size changes require expiry-specific treatment; unequal-lot pairs are excluded from the one-for-one spread sample.
5. Primary public data lack bid/ask history, so close-based execution is only a proxy.

## Phase 5 protocol result

Regime attribution is now predeclared across realized volatility, India VIX, gap, trend, liquidity, IV level/term structure, FII/DII activity, USD/INR, gold, global equity benchmarks and event windows where point-in-time data are available. The protocol prohibits using future or same-day end-of-day information that was not known at the 09:20 entry.

## Blockers

- GitHub Actions run-history audit previously reported zero workflow runs for the repository; no empirical Phase 3/4 artifact is currently available to consume.
- Phase 4/5 workflow handoffs have been repaired so future manual runs can pull the Phase 3 artifact by run ID.
- Phase 3/4 historical artifacts are required before empirical regime analysis.
- Quote-level bid/ask and IV surface history remain a separate data requirement.
- The user's exact 2.5% denominator remains unconfirmed; supported alternatives must be reported.