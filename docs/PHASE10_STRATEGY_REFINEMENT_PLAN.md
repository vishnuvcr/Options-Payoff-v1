# Phase 10 — Strategy Refinement Research Plan

**Branch:** `phase-10-strategy-refinement`  
**Parent control:** Phase 9G corrected H1 one-strike strategy  
**Date:** 2026-09-29  
**Status:** PLANNED — no refinement adopted yet

## Purpose

Improve realized win rate and/or net expectancy of the frozen H1 strategy without repeating the earlier research errors:

- no look-ahead;
- no loss-only optimization as a final rule;
- no tuning on the final holdout;
- no partial 17-strike surfaces;
- no substitution of far-expiry settlement for observed near-expiry far-leg exits;
- no silent changes to the six-transaction cost model;
- no dynamic H1/H2/H3 switching;
- no acceptance of a point estimate without uncertainty and chronological validation.

The Phase 10 objective is **not** to force a 100% realized win rate. The existing evidence shows that the positive static payoff-chart condition is only a selection metric and that substantial realized losses arise from the subsequent cross-expiry economics.

## Research questions

**RQ10.1 — Execution quality:** Does a predeclared liquidity / execution-quality gate remove trades whose static edge is too small relative to realistic four-leg entry and two-leg exit costs?

**RQ10.2 — Entry confirmation:** Does delaying entry until a signal persists or remains valid for a predeclared confirmation window improve full-sample expectancy and win rate without erasing too much opportunity?

**RQ10.3 — Scenario-aware strike selection:** Can the 17-strike selector be improved by ranking candidates on a point-in-time stress-tested estimate of the full near-expiry economic P&L, rather than the static same-spot flatline alone?

**RQ10.4 — Exit timing:** Does a predeclared early-close rule reduce tail losses caused by adverse revaluation of the far-expiry legs before the near expiry?

**RQ10.5 — Interaction control:** Does combining only individually supported refinements produce incremental benefit, or are apparent improvements caused by multiple testing?

**RQ10.6 — Sizing:** Is concentrating additional size on rank-1 preferable on a risk-normalized basis to adding rank-2 strikes? This is a sizing/risk question, not an entry-edge question.

## Why these questions are prioritized

Phase 9H-A showed that bounded entry changes could rescue 14/54 losses (25.9%) in hindsight-free-style counterfactual tests, but the majority of losses were not explained by a simple strike or delay change. Phase 9I showed that adding rank-2 strikes increased absolute historical P&L only under a broader two-lot interpretation while reducing win rate and profit factor and increasing drawdown. Earlier Greek/IV feature selectors and the Phase 8A S2-S1 predictor did not provide stable out-of-sample improvements.

The refinement phase therefore moves from single-feature prediction toward the structural components of the strategy:
1. executable edge versus cost;
2. confirmation of signal persistence;
3. full-position stress behaviour;
4. exit management.

## Frozen control

The control is exactly the Phase 9G H1 specification:

- scan 09:20–15:29 IST every available minute and continue across later trading days in the weekly cycle;
- require exactly 17 unique common strikes: ATM-400..ATM+400 in 50-point steps;
- first valid timestamp with any positive static flatline triggers evaluation;
- select the maximum positive equal-Max-Profit=Max-Loss candidate;
- same-strike four-leg H1 position;
- near CE/PE settle at near expiry;
- far CE/PE are manually squared off at observed near-expiry prices;
- primary model: 0.25% premium slippage and ₹20/order with all modeled Indian transaction charges.

## Phase 10A — Execution-quality / cost-to-edge gate

### Hypothesis

A large part of apparent payoff-chart edge may be too small relative to realistic execution friction, especially because the strategy requires four entry legs and two far-leg exits. Indian index-option studies also report that apparent parity mispricing can be concentrated in less-liquid contracts and that market frictions can prevent exploitation. The research will therefore test a predeclared executable-quality gate rather than assuming the chart edge is fully tradable.

### Candidate variables

Only variables observable at entry may be used:

- estimated combined entry turnover and modeled six-transaction cost;
- static flatline value;
- cost-to-flatline ratio;
- option premium/tick-size ratio;
- open interest and traded volume, where point-in-time data are available;
- missing/stale quote flags;
- cross-expiry quote-age difference;
- contract-specific liquidity score, if data coverage is sufficient.

### Predeclared candidate gates

Do not tune continuously. Test a small fixed family:

- no gate (control);
- estimated total execution cost <= 25% of static flatline;
- <= 50%;
- <= 75%.

Where bid/ask data become available, replace the crude slippage-only approximation with executable spread-based costs and report both models.

### Acceptance

A gate is only a candidate if it improves full-sample net expectancy and/or win rate while not causing an unacceptable deterioration in trade count, and the improvement survives chronological holdout and execution stress.

## Phase 10B — Entry confirmation / persistence

### Hypothesis

Some first-positive signals may be transient. A short predeclared confirmation interval may avoid entries that immediately lose their edge, while still retaining enough opportunities.

### Candidate rules

At the first valid positive signal, do not enter immediately. Instead require that a valid positive 17-strike surface remains present for a fixed confirmation period. Test only:

- 5 minutes;
- 10 minutes;
- 15 minutes;
- 30 minutes.

For each candidate, at the eventual entry timestamp use the normal maximum-positive-flatline selector. No future realized P&L is used.

### Required outputs

- trade count;
- mean/median P&L;
- win rate and Wilson interval;
- profit factor;
- max drawdown;
- delay distribution;
- skipped opportunities;
- slippage/brokerage sensitivity.

The Phase 9H loss-only rescue numbers are diagnostic only. Selection must be evaluated on the entire weekly population.

## Phase 10C — Scenario-aware strike selection

### Hypothesis

The current selector optimizes a same-spot static flatline, while the realized position contains a far-leg market-value component at near expiry. A better entry selector may maximize a conservative estimate of the entire position's P&L under plausible spot/IV states at near expiry.

### Point-in-time scenario engine

For each of the 17 candidate strikes at entry:

1. compute the static flatline;
2. infer option IVs from observed premiums using the existing documented inversion assumptions;
3. simulate a predeclared grid of near-expiry states:
   - spot shock: -2%, -1%, 0%, +1%, +2%;
   - far-leg IV shock: -5 vol-points, 0, +5 vol-points;
4. revalue the far CE/PE at the near-expiry horizon using only entry-time information;
5. subtract conservative entry/exit cost assumptions;
6. derive fixed summary scores:
   - median scenario P&L;
   - 10th-percentile scenario P&L;
   - worst-grid P&L;
   - scenario P&L dispersion.

Do not tune the grid after viewing results.

### Candidate selectors

- current maximum static flatline (control);
- maximum median scenario P&L;
- maximum 10th-percentile scenario P&L;
- maximum worst-grid P&L.

### Acceptance

A selector must be evaluated on all decision timestamps, not only losses, and must demonstrate an improvement that persists in untouched chronological data.

## Phase 10D — Exit-timing refinement

### Hypothesis

The far-expiry legs are the major source of path-dependent realized loss. The fixed near-expiry exit may leave profitable or deteriorating positions exposed longer than necessary.

### Predeclared exit candidates

Test only a small fixed set:

1. baseline: near-expiry exit;
2. scheduled exit 60 minutes before near-expiry close;
3. 120 minutes before;
4. 180 minutes before;
5. 1 trading day before near expiry.

At each exit point, close all four legs using the same transaction-cost framework. If a candidate requires option prices not supported by the source, mark it unavailable rather than filling the gap with settlement.

### Risk-management sensitivity

As a separate subtest, evaluate a fixed total-position stop/target only if the data contain continuous executable enough prices. Predeclare a small grid such as:
- stop = -1x static flatline, -2x;
- target = +1x, +2x static flatline.

No adaptive or loss-specific targets are permitted.

### Acceptance

Exit candidates are judged on full-sample net P&L, win rate, profit factor, drawdown, tail loss, cost drag and year-by-year stability.

## Phase 10E — Controlled combinations

Only the top one or two candidates that pass their own full-sample and training-period checks may be combined.

Combinations must be assembled in a fixed order:

1. execution-quality gate;
2. entry confirmation;
3. scenario-aware selector;
4. exit refinement.

No more than two new mechanisms may be combined before the holdout. This prevents the phase from becoming an unrestricted parameter search.

## Phase 10F — Sizing and rank-1 concentration

Compare, on the exact same entry timestamps:

- one-lot rank-1 control;
- two lots at rank-1;
- literal top-two strikes;
- top-two-positive only.

Primary outputs must include:
- net P&L;
- P&L per deployed margin;
- max drawdown;
- margin utilization;
- incremental cost;
- win rate;
- profit factor.

A sizing variant cannot be called a strategy improvement merely because absolute P&L is larger.

## Phase 10G — Untouched chronological holdout

### Split

Use an explicit chronological split with no tuning on the final segment. The exact split must be fixed before result inspection.

Recommended structure:

- development: earliest 70%;
- validation: next 15%;
- untouched holdout: latest 15%.

If data-source coverage or expiry changes make that split invalid, document the alternative before evaluation.

### Promotion criteria

A refinement may replace the control only when:

1. it is fully defined before holdout scoring;
2. it improves the primary metric on validation;
3. it does not materially worsen risk metrics without a compensating economic justification;
4. it remains positive/acceptable under execution stress;
5. the holdout confirms the direction of the improvement;
6. confidence intervals do not contradict the claimed direction;
7. the gain is not explained by one short historical cluster.

## Statistical analysis

Primary metrics:

- net P&L;
- mean weekly-cycle P&L;
- median P&L;
- realized win rate with Wilson 95% CI;
- profit factor;
- maximum drawdown;
- P&L per deployed margin;
- cost drag.

Inference:

- paired weekly-cycle differences against the frozen control;
- circular block bootstrap;
- permutation tests for paired differences where suitable;
- multiple-testing correction across the predeclared candidate family;
- annual and chronological-cohort stability;
- execution-cost sensitivity.

## Data and execution requirements

The phase must prefer point-in-time executable data. Where only OHLC/close data exist, the analysis must report that limitation and retain the conservative slippage model.

The Paytm Money cost model must be verified against a current contract note before any live/paper-trading conclusion. The repository's ₹20/order historical primary assumption remains a sensitivity parameter rather than a claim about current brokerage.

## External evidence to integrate

The literature review for Phase 10 should incorporate:

- Indian NIFTY put-call parity / box-spread efficiency and liquidity evidence;
- option-market bid/ask and price-impact research;
- implied-volatility term-structure / volatility-risk-premium research;
- execution and transaction-cost research for index options;
- current exchange/broker execution and fee documents where relevant.

Existing research suggests that apparent option parity violations can be concentrated in illiquid contracts and that trading frictions materially affect exploitability. These sources motivate the execution-quality and liquidity tests; they do not establish that this strategy has an edge.

## Error-prevention gates

Before each subphase:

- verify the latest `CURRENT_STRATEGY_SPEC.md`;
- verify the latest error log;
- verify the authoritative control artifact hash;
- verify the 17-strike unique-surface gate;
- verify the near-expiry far-leg exit convention;
- verify that the candidate rule is frozen before scoring;
- add every implementation/data error to `research/ERROR_LOG.md`;
- update `research/STATUS.md`, `research/ACTIVITY_LOG.md`, and README.

## Phase exit

Phase 10 stops after Phase 10G. It does not open an indefinite ML/pattern-mining loop.

At exit the repository must contain:

- final accepted refinement, if any;
- frozen alternative(s) rejected and why;
- full manuscript update;
- result tables;
- figures;
- error log;
- activity log;
- statistical appendix;
- untouched holdout report;
- future research proposals.

If no refinement survives holdout, the correct conclusion is that the current Phase 9G control remains the research candidate.
