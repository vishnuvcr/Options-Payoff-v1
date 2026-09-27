# Phase 9G — Candidate Strategy Specification After Final Reconstruction

## Current research candidate

The only candidate supported by the primary source is the **H1 fixed-next-weekly-expiry version** of the frozen rule.

### Entry

For each near-weekly expiry cycle:

1. Start at 09:20 and inspect every available 1-minute timestamp through the trading day and subsequent trading days in the same weekly cycle.
2. At each timestamp require exactly 17 unique common strikes corresponding to shifts -400 through +400 in 50-point increments.
3. Reject the timestamp if any shift has conflicting duplicate quotes.
4. Calculate the static same-spot four-leg payoff for every one of the 17 common strikes.
5. If at least one static equal-max-profit=max-loss flatline is positive, choose the candidate with the largest positive flatline.
6. Do not skip the cycle merely because 09:20 is non-positive.

### Position

At the selected strike K:

- Near weekly expiry: sell CE(K), buy PE(K).
- Next weekly expiry: buy CE(K), sell PE(K).

### Exit

At the near expiry:

- Near CE and PE settle according to the near index settlement.
- Far CE and PE are manually squared off at their last available executable quote at or before the near-expiry index close.

### Cost assumptions used in the historical study

Primary:
- 0.25% premium slippage per execution.
- ₹20 brokerage per order.
- Six executed transactions per completed trade.
- Exchange transaction charge: 0.03553% of turnover.
- SEBI fee: 0.0001% of turnover.
- Buy-side stamp duty: 0.003%.
- GST: 18% on brokerage plus exchange/SEBI charges.
- STT and exercise STT use the date-dependent rates encoded in src/costs.py.

Sensitivity:
- Slippage: 0%, 0.25%, 0.50%, 1.00%.
- Brokerage: ₹10, ₹20, ₹40/order.

## Historical primary-source evidence

131 complete H1 trades produced ₹71,868.76 net P&L at the primary cost model, with 58.78% realized wins and PF 2.29.

This is **not** a 100% realized-win strategy. The 100% quantity applies only to the static chart-positive selection condition.

## Horizon decision

H2 and H3 are **not promoted** from the primary source because its expiry-partitioned data do not contain the required pre-entry observations for the second and third weekly far expiries.

An independent Rissin reconstruction showed positive matched H2-H1 and H3-H1 differences, but that evidence is retained as source sensitivity rather than accepted as a production horizon because of source-construction differences, partial historical coverage, and lack of untouched holdout validation.

## Deployment gate

Do not treat this historical candidate as deployment-ready until all of the following are completed:

1. Untouched forward holdout.
2. Full live-expiry source coverage for H1/H2/H3.
3. Bid/ask or executable-quote reconstruction.
4. Current Paytm Money contract-note validation.
5. Liquidity/capacity and market-impact testing.
6. Live paper-trading replication of the exact 17-strike completeness rule.
