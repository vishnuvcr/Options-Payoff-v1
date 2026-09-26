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

where the four option premiums are entry prices and S1/S2 are the near/next expiry index settlements.

## Cost model

Base parameters are configurable. The current 2026 reference inputs are:

- Paytm Money brokerage: ₹20 per executed order in the base model.
- 4 executed orders per selected four-leg entry.
- NSE equity-option transaction-charge reference: ₹3,553 per crore of premium turnover from 1 March 2026, represented as 0.03553%.
- SEBI turnover fee: 0.0001%.
- Equity-option stamp duty: 0.003% on buyer turnover.
- GST: 18% on brokerage plus exchange/SEBI service charges.
- STT on option sale: 0.10% before 1 April 2026 and 0.15% from 1 April 2026.
- STT on option exercise: 0.125% before 1 April 2026 and 0.15% from 1 April 2026, applied to the intrinsic value of long legs at expiry.
- Slippage: configurable; 0.25% of premium is the initial research shock because the Phase 2 source lacks bid/ask quotes.

These are research inputs rather than a claim about a particular user's exact contract note. Paytm Money's current pricing calculator notes that not every possible platform/depository/other fee is included, so a live-use reconciliation must use the user's actual contract note.

## Selection and validation

The output includes every complete candidate and the selected trades, so researchers can compare the triggered sample with rejected ATM/-400/+400 candidates and test alternative trigger denominators.

## Important limitations

1. Phase 3 requires a verified lot-size calendar; the engine deliberately requires lot size as an explicit input instead of silently using a modern lot size for old contracts.
2. Phase 2 uses 09:20 close proxies rather than bid/ask quotes, so slippage is a sensitivity assumption until quote-level data can be validated.
3. The chart trigger is separated from realized P&L. A candidate can pass the static chart trigger and still lose money when S2 < S1 or when costs exceed the gross edge.

## Outputs

- candidate_results.parquet
- selected_trades.parquet
- summary.json

Statistical validation, walk-forward tests, drawdowns and regime attribution remain Phase 4 and Phase 5 tasks.

## Historical NIFTY lot-size calendar

The backtest now derives lot size from the expiry date rather than using one modern lot for the full sample. The research calendar is: 75 through the July 2021 weekly cycle; 50 from August 2021 through the April 2024 weekly cycle; 25 from the May 2, 2024 weekly cycle through the final old-lot weekly contracts; 75 for new weekly contracts from November 2024; and 65 from the January 6, 2026 weekly cycle. The 2024 and 2025 changes retained old lots for already-existing weekly/monthly contracts until their expiry, so the implementation keys the lot to the actual expiry date. Transition observations where the near and next expiry have different lots are excluded from the one-for-one spread backtest rather than being silently treated as equal notional. These dates are supported by NSE/market circular summaries. citeturn4search2turn4search0turn4search1turn3search27
