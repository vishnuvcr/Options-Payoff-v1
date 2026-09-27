# Final research strategy specification — corrected current version

## Entry-time rule

At the configured research observation time (09:20 IST in the historical study):

1. Identify the near weekly and far weekly expiries used by the tested variant.
2. Set ATM from the NIFTY underlying used by the option dataset.
3. Evaluate every common strike from ATM-400 through ATM+400 in 50-point increments, including ATM.
4. For the H=1 baseline, build:
   - sell near-expiry CE;
   - buy near-expiry PE;
   - buy next-expiry CE;
   - sell next-expiry PE.
5. Calculate the static flatline max-profit=max-loss value from the four entry premiums.
6. At the first positive/all-green observation in the weekly cycle, select the candidate with the maximum positive flatline value.
7. No 2.5% threshold, margin gate or threshold-based skipping is part of the current user rule.

## Correct execution and exit model

All four legs are closed at the near weekly expiry.

- Near-expiry CE/PE: settle/expire at near expiry.
- Far-expiry CE/PE: manually square off at the near-expiry close using the far option's observed executable market prices at that time.

The corrected gross P&L per unit is:

C1 - P1 - Cf + Pf + (K-S1) + Qfar_CE(T1) - Qfar_PE(T1)

before costs/slippage.

All entry and exit execution costs must be charged. The far-leg manual close is two additional option transactions and cannot be replaced by far-expiry settlement values.

## Research status

The prior historical realized-P&L results are superseded because the old backtest held the far options to their own expiry. A corrected H=1 baseline is now required before any performance conclusion or far-expiry H=2/H=3 experiment.

## Required next confirmation

Rebuild the historical dataset with point-in-time far-option prices at the near-expiry close, run the corrected 17-strike H=1 weekly backtest, audit all selected and non-selected candidates, and then perform validation. Only after that should far-expiry selection be tested.
