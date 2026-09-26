# Phase 3 — Backtest and transaction-cost model

## Backtest target

The engine consumes the Phase 2 candidate table and applies the user's selection rule: test ATM first; only if ATM does not exceed the configured 2.5% chart trigger does it consider the -400 and +400 common-strike candidates.

Because the original percentage denominator is not specified, the engine supports three explicit trigger bases:

- buy_premium: percentage of the two long-option premiums
- spot_notional: percentage of spot × lot size
- configured_capital: percentage of a user-supplied capital amount per lot

The first is the code default only so the workflow remains deterministic; it is not treated as the user's confirmed denominator. Final interpretation will report sensitivity across all supported bases.

## Gross P&L

For each selected trade:

`gross P&L = (C1 - P1 - C2 + P2 + S2 - S1) × lot_size`

where the four option premiums are entry prices and S1/S2 are the actual near/next expiry index settlements.

## Cost model

Base parameters are configurable. The current 2026 reference inputs are:

- Paytm Money brokerage: ₹20 per executed order in the base model.
- 4 executed orders per selected four-leg entry.
- NSE equity-option transaction-charge reference: ₹3,553 per crore of premium turnover from 1 March 2026, represented as 0.03553%.
- SEBI turnover fee: 0.0001%.
- Equity-option stamp duty: 0.003% on buyer turnover.
- GST: 18% on brokerage plus exchange/SEBI service charges.
- STT: 0.10% on option-sale premium before 1 April 2026; 0.15% from 1 April 2026.
- Slippage: configurable; 0.25% of premium is the initial conservative research shock because the Phase 2 source lacks bid/ask quotes.

These are research inputs rather than a claim about a particular user's exact contract note. Paytm Money's current pricing material notes that its brokerage calculator does not include every possible platform/depository/other fee, so the final live-cost check must reconcile against the user's contract note.

## Selection and validation

The output includes every complete candidate and the selected trades, so researchers can compare the triggered sample with the rejected ATM/-400/+400 candidates and test alternative trigger denominators.

## Important limitation

Phase 3 cannot yet be treated as the final historical result until two data items are verified: (1) a dated NIFTY lot-size calendar, and (2) quote-level bid/ask or a validated spread/slippage model. The engine deliberately requires lot size as an explicit input instead of silently using a modern lot size for old contracts.

## Outputs

- candidate_results.parquet
- selected_trades.parquet
- summary.json

Statistical validation, walk-forward tests, drawdowns and regime attribution remain Phase 4 and Phase 5 tasks.