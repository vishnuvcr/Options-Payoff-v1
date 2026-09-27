# Final research strategy specification — current version

## Entry-time rule

At the configured research observation time (09:20 IST in the historical study):

1. Identify the near weekly and next weekly NIFTY expiries.
2. Set ATM from the NIFTY underlying used by the option dataset.
3. Evaluate every common strike from ATM-400 through ATM+400 in 50-point increments, including ATM.
4. For each strike, build:
   - sell near-expiry CE;
   - buy near-expiry PE;
   - buy next-expiry CE;
   - sell next-expiry PE.
5. Calculate the static flatline max-profit=max-loss value from the four entry premiums.
6. Calculate/reconstruct the portfolio margin required using the contemporaneous NSE/NSCCL SPAN risk file. The historical primary implementation uses the i1 begin-day SPAN snapshot because it is available before the trade decision; later snapshots are sensitivity analyses.
7. Compute:

`Max Profit % = estimated equal max-profit=max-loss value / margin required × 100`

8. Keep only candidates with Max Profit % strictly greater than 2.5%.
9. Among the remaining candidates, select the one with the largest estimated equal max-profit=max-loss **value in INR**.
10. The maximum-percentage selector is a sensitivity. In the exact historical qualifying sample it selected the same strike as the maximum-INR selector.

## Execution model

- 1 lot by default.
- 0.25% premium slippage per option leg in the research baseline.
- ₹20 brokerage per executed order.
- Include exchange transaction charges, SEBI fee, stamp duty, GST, STT and exercise-related costs according to the repository's dated cost model.
- No future settlement or future option price may enter the entry decision.

## Exit

The historical study holds the position through the defined settlement/expiry logic used by the backtest engine. The static payoff chart is not treated as the realized two-expiry P&L.

## Research status

The exact margin-denominator reconstruction is complete. The calibrated screenshot margin was ₹88,076 versus a closest SPAN reconstruction of ₹87,812.40 (0.2993% difference).

Under the 2021–2023 cached sample and the exact ±400 rule, the primary i1 interpretation generated 4 qualifying timestamps and ₹42,680.17 net P&L after modeled costs/slippage.

That four-trade sample is too small to establish a stable statistical edge. The specification is therefore a reproducible **research candidate strategy**, not a validated profit guarantee.

## Required next confirmation

Before live deployment, the strategy should be paper-traded or evaluated on a larger independent period using the same exact margin methodology, with bid/ask execution rather than close-price proxies and with broker-specific Paytm Money charges verified for the live date.