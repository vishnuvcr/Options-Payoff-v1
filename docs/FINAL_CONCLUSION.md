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

## Current conclusion

There is currently **no valid realized-P&L conclusion for the actual trading strategy** from the prior backtests. The correct scientific position is to treat those results as superseded and rerun the baseline with the user's actual exit convention.
