# Options-Payoff-v1

Research repository for testing a cross-expiry NIFTY index-options strategy.

## Current research status

**Latest protocol branch:** `phase-5-regimes`
**Latest phase:** Phase 5 — regime and cross-market attribution framework
**Empirical status:** Phase 3/4 historical execution artifacts are still required; no historical performance result is claimed. The latest Phase 5 branch also repaired cross-workflow artifact handoffs and a configured-capital trigger bug.
**Last updated:** 2026-09-26

## Key analytical finding

The four-leg position is a short synthetic forward in the near expiry plus a long synthetic forward in the next expiry. The economically relevant expiry component is the difference between the two expiry settlement levels, not a single common terminal spot. A chart that uses one terminal spot for both expiries can therefore display a flat line even though the held position has cross-expiry settlement risk.

## Phase map

- Phase 0 — governance: complete.
- Phase 1 — strategy/payoff specification: complete.
- Phase 2 — data engineering: implemented; runtime validation pending.
- Phase 3 — backtest and costs: implemented; historical execution pending.
- Phase 4 — statistical validation: implemented; execution pending Phase 3 artifacts.
- Phase 5 — regime attribution: protocol/scaffold implemented on `phase-5-regimes`; execution gated on validated trade ledger.
- Phase 6 — manuscript: not started; begins only after empirical Phases 3–5 are complete.

## Latest Phase 5 work

The regime protocol is point-in-time and covers realized volatility, India VIX, gap, trend, liquidity, option IV/term structure, FII/DII activity, USD/INR, gold, global equity benchmarks and auditable event windows. Same-day end-of-day information is prohibited for a 09:20 entry unless it was genuinely available before entry.

Official NSE sources expose historical derivatives reports, contract-wise option data, participant reports, FII derivatives statistics and India VIX history. The current Paytm Money F&O FAQ states Rs.10 brokerage per unique executed order; the research model remains configurable and retains a conservative higher-brokerage sensitivity for historical/account-specific uncertainty.

## Repository governance

- Baseline plan: `research/RESEARCH_PLAN.md`
- Instructions: `research/RESEARCH_INSTRUCTIONS.md`
- Status: `research/STATUS.md`
- Error log: `research/ERROR_LOG.md`
- Activity log: `research/ACTIVITY_LOG.md`
- Phase 5 protocol: `docs/PHASE_5_REGIME_ANALYSIS.md`
- Phase 5 source audit: `docs/PHASE_5_SOURCE_AUDIT.md`

Latest phase branch: https://github.com/vishnuvcr/Options-Payoff-v1/tree/phase-5-regimes

## Execution dependency

The current research branch has repaired Phase 2 → Phase 3 → Phase 4/5 artifact handoffs. Because the connected GitHub interface in this research session does not expose workflow dispatch, the first empirical run still requires the repository's manual workflow buttons. No performance result is claimed until those artifacts exist.
