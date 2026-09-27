# Phase 9G candidate strategy — fixed H3 horizon

## Research status

**Candidate only. Not yet validated on untouched future data and not approved for live deployment.**

The corrected same-source Rissin 2024–2026 evidence identifies H3 as the strongest fixed-horizon research candidate. H3 beat H1 in the preregistered paired comparison and beat H2 in an exploratory matched-cycle comparison. The chronological 2026 comparison is supportive for H3 versus H2 but the H3-vs-H1 interval still crosses zero.

## Exact entry protocol

1. Identify the current NIFTY weekly near expiry and the **third subsequent weekly expiry** available from the entry date. This is the H3 far contract.
2. From **09:20 through 15:29 IST**, inspect every available 1-minute timestamp. 09:20 is only the first observation.
3. At each timestamp, reconstruct the exact 17-shift strike universe:
   **ATM−400, −350, −300, −250, −200, −150, −100, −50, ATM, +50, +100, +150, +200, +250, +300, +350, +400.**
4. A timestamp is invalid if any of the 17 shifts is missing, if the four required option quotes are incomplete, or if conflicting duplicate quote values exist for a shift. Continue scanning later timestamps.
5. On the first valid timestamp containing at least one positive static flatline, select the strike with the **maximum estimated positive equal-Max-Profit=Max-Loss flatline** across all 17 shifts.
6. Do not substitute ATM, −400, +400, or any other subset. There is no skip rule for inconvenient strikes.

## Four-leg position

At the selected strike:

- Near expiry: **sell CE + buy PE**
- H3 expiry: **buy CE + sell PE**

The static chart flatline is the entry cashflow of these four legs under the same-hypothetical-spot payoff construction. It is a selection metric, not a guarantee of realized profit.

## Exit convention

At the near-expiry close:

- near-expiry CE/PE are settled at the near-expiry index settlement;
- H3 CE/PE are manually closed using the latest available H3 option quotes at or immediately before the near-expiry close.

The far legs are not held to H3 expiry.

## Execution-cost model

Primary backtest assumptions:

- 0.25% premium slippage per executed option leg;
- ₹20 brokerage per order;
- exchange transaction charge 0.0003553 on turnover;
- SEBI charge 0.000001;
- buy-side stamp duty 0.00003;
- GST 18% on brokerage + exchange + SEBI charges;
- STT and exercise-STT rates follow the date-dependent repository cost model.

Sensitivity is predeclared at 0.50% and 1.00% slippage plus ₹10 and ₹40 brokerage.

## Evidence status

Same-source Rissin 2024–2026:

- H3: 16 realized trades, ₹120,194.26 net at primary costs, 93.75% realized win rate, PF 38.71.
- H3−H1: 16 matched cycles, mean +₹4,804.10, block-bootstrap 95% CI +₹328.62 to +₹8,870.46, BH q=0.01825.
- H3−H2 exploratory: 11 matched cycles, mean +₹4,522.86, block-bootstrap 95% CI +₹1,724.18 to +₹7,932.38, p≈0.00470.
- 2026-only H3−H2: 8 matched cycles, mean +₹2,328.97, block-bootstrap CI +₹1,202.76 to +₹3,455.18, p≈0.03990.

## Required next validation

The candidate must be tested on genuinely untouched future data with the rule frozen before live deployment. The test must preserve the exact 17-strike universe, H3 expiry definition, first-valid-timestamp rule, cost model, and far-leg near-expiry manual-close convention.
