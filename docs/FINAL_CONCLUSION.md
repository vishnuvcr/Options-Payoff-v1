# Final Research Conclusion — Current State

## Critical validity correction — 2026-09-27

The user's actual exit rule is:

- all four legs are closed at the near weekly expiry;
- the near CE/PE expire/settle there;
- the far CE/PE are manually closed at the same near-expiry close.

An audit of the authoritative backtest code found that the previous realized-P&L calculation used the far-expiry settlement for the far CE/PE legs. In `scripts/run_backtest.py`, the prior gross P&L was calculated from the entry cashflow plus `next_settlement - near_settlement`, and the far-leg exit costs were based on intrinsic values at the far settlement.

That is **not the user's strategy**. It models holding the far-expiry legs to their own expiry.

### Consequence

The following historical results are now **superseded and non-authoritative for the actual strategy**:

- Phase 7B realized net P&L, win rate, drawdown and economic decomposition;
- Phase 7C winner/loser labels and Greek-selector performance, because those labels use the incorrect realized P&L;
- Phase 8A S2-S1 target/predictor and economic-filter results, because they were built around the incorrect far-expiry-hold economics;
- the prior final deployment conclusion insofar as it relied on those realized-P&L results.

The entry-time static flatline computation remains valid as an algebraic/chart metric. It does **not** establish the corrected strategy's profitability.

## Correct economic formula

For a selected common strike K, with near expiry at T1 and a far option pair that is manually closed at T1, let Q_C(T1) and Q_P(T1) be the actual executable far-call sale and far-put repurchase prices at the near-expiry close. Before transaction costs:

\[
P\&L(T1)=C_1-P_1-C_f+P_f+(K-S_1)+Q_C(T1)-Q_P(T1).
\]

Execution slippage, brokerage, exchange charges, STT, stamp duty, SEBI fee and GST must then be applied to the actual entry and four-leg exit transactions.

## Corrective phase

**Phase 9A — near-expiry manual-close reconstruction** is now the authoritative research phase.

It will first rebuild the current H=1 strategy with the correct exit convention using point-in-time far-option prices at the near-expiry close. The 17-strike, positive-flatline, maximum-flatline selection rule is retained for this reconstruction so that the exit correction is isolated from other changes.

Only after the corrected H=1 baseline is established will H=2/H=3 far-expiry selection be researched.


## Phase 9D — Corrected intraday H1 result

The user's 09:20 observation is now treated as the **first check, not a skip gate**. The corrected extractor checks every available 1-minute observation from 09:20 through 15:29 and continues across later trading days within the same weekly cycle until the first positive/all-green candidate appears. At that timestamp it selects the maximum positive flatline across ATM-400..ATM+400.

The authoritative H1 run is **36302077730**. The merged audit contains 172 selected weekly-cycle entries, 448,280 checked timestamps and 17,606 decision-surface rows. Three selected entries have incompatible near/far lot sizes and are retained as incomplete rather than assigned a synthetic exit price, leaving 169 complete realized trades.

At 0.25% premium slippage and ₹20/order brokerage, the 169 complete trades produced **₹162,953.84 gross P&L, ₹37,265.02 modeled costs and ₹125,688.82 net P&L**, with a 63.91% realized win rate and profit factor 2.94. Maximum drawdown on the realized-trade sequence was ₹16,200.65. Sensitivity remained positive at 0.5% and 1.0% slippage and at ₹40/order brokerage in the tested scenarios.

This is a materially different and more complete empirical result than the superseded 09:20-only studies. It supports continued validation of the corrected H1 rule, but it is **not yet sufficient to declare a deployable trading edge** because the present result is a historical in-sample reconstruction. Independent walk-forward/holdout validation, regime robustness, and execution robustness remain required.

See [docs/PHASE9D_RESULTS.md](PHASE9D_RESULTS.md). H2/H3 research remains frozen until the corrected H1 validation phase is complete.
