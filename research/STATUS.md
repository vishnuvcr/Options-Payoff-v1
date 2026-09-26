# Research status

**As of:** 2026-09-27  
**Active branch:** phase-6-loss-audit  
**Overall phase:** 6A — Loss-trade audit COMPLETE

| Phase | Status | Evidence |
|---|---|---|
| 0 Bootstrap | COMPLETE | Governance, plan, sources, status and logs maintained. |
| 1 Specification | COMPLETE | Strategy equations, payoff model, strike candidates and tests validated. |
| 2 Data | COMPLETE | Run 36255238050 generated the corrected strategy input cache. |
| 3 Backtest | COMPLETE | Run 36262958536 generated the authoritative 63-row full-grid selected ledger. |
| 4 Validation | COMPLETE | Run 36263760476 completed uncertainty, walk-forward, threshold/slippage/denominator and brokerage sensitivity. |
| 5 Regimes | COMPLETE | Run 36263974629 completed point-in-time regime attribution. |
| 6 Manuscript | COMPLETE | Corrected full-grid manuscript and figures committed. |
| 6A Loss audit | COMPLETE | Run 36264710663 audited all 63 selected rows directly from the Phase 3 artifact. |

## Corrected primary result

Under the working buy-premium interpretation of the 2.5% trigger, 0.25% premium slippage and ₹20/order baseline brokerage:

- selected trade rows: 63
- distinct entry timestamps: 52
- ATM trades: 24
- fallback-grid trades: 39
- total net P&L: ₹168,665.95
- mean trade P&L: ₹2,677.24
- median trade P&L: ₹6,831.26
- win rate: 60.32%
- profit factor: 1.37
- maximum drawdown: -₹194,854.37

The iid and weekly block-bootstrap intervals for mean trade P&L both include zero. The chronological training segment was negative while the test segment was positive.

## Loss-trade audit

The authoritative 63-row selected ledger contains:

- 38 winners
- 25 losers
- losing contribution: -₹454,335.44
- winning contribution: +₹623,001.39
- largest loss: -₹55,420.58
- mean loss: -₹18,173.42
- median loss: -₹9,563.35
- 25/25 losers negative before modeled fees
- 0/25 fee-only losses
- 7 ATM losses
- 18 fallback losses
- modeled costs on losing rows: ₹3,557.82

The audit found that the 25 losing trades all passed the positive >2.5% entry-chart trigger. The realized cross-expiry economic component, not brokerage, is the dominant loss mechanism.

See docs/LOSS_TRADE_ANALYSIS.md for the complete 25-trade ledger, concentration analysis, shift analysis and cost anatomy.

## Reproducibility correction

The authoritative 63-row result comes from branch phase-3-strike-grid and run 36262958536. The later phase-6-manuscript-grid branch retains an older run_backtest.py using ATM/-400/+400. That stale script must not be used to reproduce the full-grid result; the discrepancy is logged for correction.

## Important specification limitation

The 2.5% percentage denominator remains unconfirmed. The buy-premium denominator is a working research assumption. The tested spot-notional denominator generated no qualifying trades from 1% through 5%.

## Final conclusion

The clarified rule is reproducible and had a positive historical point estimate under one explicit implementation, but the evidence is not sufficient to treat it as robust, denominator-independent or risk-free arbitrage.

The loss audit explains why: a positive static payoff-chart trigger can coexist with a strongly negative realized cross-expiry settlement outcome.
