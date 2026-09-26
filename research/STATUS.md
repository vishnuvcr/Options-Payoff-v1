# Research status

**As of:** 2026-09-26
**Active branch:** phase-5-regimes
**Overall phase:** 5 — Regime attribution framework implemented; empirical execution still gated on historical workflow artifacts

| Phase | Status | Evidence / next action |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance files initialized. |
| 1 Specification | COMPLETE | Strategy equations, payoff tests and manual workflow added. |
| 2 Data | IMPLEMENTED; VALIDATION PENDING | Extractor, source manifest and cache workflow exist; runtime artifact still required. |
| 3 Backtest | IMPLEMENTED; VALIDATION PENDING | Cost-aware ledger exists in code; historical run has not been executed. |
| 4 Validation | IMPLEMENTED; EXECUTION PENDING | Bootstrap/monthly/walk-forward/sensitivity framework exists; requires Phase 3 results. |
| 5 Regimes | FRAMEWORK COMPLETE; EXECUTION BLOCKED | Point-in-time protocol, source audit, script and manual workflow added; requires a validated trade ledger. |
| 6 Manuscript | NOT STARTED | Starts after empirical Phases 3–5 are complete. |

## Current analytical findings

1. The static flatline chart is not the realized payoff of the cross-expiry position.
2. The economically relevant expiry component is S2 - S1, plus the entry premium edge and transaction costs.
3. The 2.5% denominator is unspecified and must remain an explicit sensitivity dimension.
4. Historical NIFTY lot-size changes require expiry-specific treatment; unequal-lot pairs are excluded from the one-for-one synthetic-forward sample.
5. Primary public data lack bid/ask history, so close-based execution is only a proxy.

## Current protocol status

Phase 5 regime attribution is predeclared across realized volatility, India VIX, gap, trend, liquidity, IV level/term structure, FII/DII activity, USD/INR, gold, global equity benchmarks and event windows where point-in-time data are available. Same-day end-of-day information that was not known at the 09:20 entry is prohibited.

## Blockers

- No completed Phase 3/4 historical workflow artifact is currently available to consume.
- The current research environment does not expose workflow dispatch; the first empirical execution therefore requires the repository's manual workflow buttons.
- Phase 4/5 workflow handoffs have been repaired so later runs can download a selected Phase 3 artifact by run ID.
- Quote-level bid/ask and IV-surface history remain separate data requirements.
- The user's exact 2.5% denominator remains unconfirmed; supported alternatives must be reported.

## Next executable step

Run Phase 2 manually, record its run ID, pass that run ID into Phase 3, then pass the Phase 3 run ID into Phase 4 and Phase 5. Do not start Phase 6 until empirical outputs are available and validated.
