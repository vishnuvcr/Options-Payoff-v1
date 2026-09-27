# Phase 9A — Correct near-expiry manual-close methodology

## Operational strategy

At entry, for a common strike K:

1. Sell the near-expiry CE.
2. Buy the near-expiry PE.
3. Buy the next/far-expiry CE.
4. Sell the next/far-expiry PE.

The entry observation is the 09:20 IST close proxy. Every weekly cycle is scanned chronologically across the 17 strikes ATM-400 through ATM+400 in 50-point increments. The first observation with a positive/all-green static flatline is the entry observation, and the strike with the largest positive estimated equal max-profit=max-loss flatline is selected.

## Exit convention

All four legs are closed at the near weekly expiry.

- The near CE and near PE settle naturally at the near-expiry index settlement.
- The far CE and far PE are manually squared off at their observed market prices at the near-expiry close. The implementation uses the last far-option bar on or before the last available NIFTY index bar of that expiry date.

The far legs are not held to their own expiry.

## Correct gross P&L

Let C1/P1 be near-expiry entry premiums, Cf/Pf far-expiry entry premiums, S1 the near-expiry index settlement, and Qc/Qp the far-option market prices used for manual near-expiry closure.

Before costs:

`gross P&L per unit = C1 - P1 - Cf + Pf + (K - S1) + Qc - Qp`

The K-S1 term is the combined payoff of the near short-call/long-put pair at the common strike.

## Slippage and fees

Slippage is applied to executed entry and far-leg exit premiums before computing gross cash P&L.

The cost engine accounts for six executable option orders: four entry orders, one far CE sale at near expiry, and one far PE buyback at near expiry. The near-expiry options are settled, not separately squared off.

Statutory charges include exchange turnover charges, SEBI turnover fee, stamp duty, STT on option sales, STT on the exercised long put intrinsic value, and GST on applicable brokerage/exchange/SEBI charges.

Entry sales use the entry-date statutory rate; far-leg exit sales and near-expiry exercise use the near-expiry date. Brokerage is parameterized so Phase 9B can test the Paytm Money ₹10/order current FAQ value alongside the repository's historical ₹20/order baseline and a ₹40 stress case.

## Data integrity

The workflow requires every selected trade to have a near-expiry exit timestamp, far CE and far PE exit timestamps, both far exit timestamps at or before the near-expiry close, and non-missing entry and exit premiums for the selected strike.

## Research status

No realized-P&L result from the superseded far-expiry-holding implementation may be reused as evidence for this strategy. H2/H3 experiments remain frozen until corrected H1 is complete.
