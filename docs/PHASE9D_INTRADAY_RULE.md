# Phase 9D — Correct no-skip intraday strategy definition

## Critical correction

The previous Phase 9A/9B research evaluated only the 09:20 observation each trading day. That was not the user's strategy.

09:20 is only the **first check**.

If the static payoff estimate is not positive at 09:20, the algorithm continues checking later available intraday timestamps on the same trading day. If no positive opportunity appears that day, it continues on the next trading day of the same weekly expiry cycle. There is no 2.5% threshold, no margin gate, and no 09:20-based weekly skip.

## Exact entry protocol

At every available NIFTY 1-minute timestamp from 09:20 through 15:29 IST:

1. Determine the current near weekly expiry and the following far weekly expiry.
2. Determine the available ATM reference strike from complete four-leg surfaces.
3. Evaluate every strike ATM-400, ATM-350, ..., ATM, ..., ATM+350, ATM+400.
4. Require all four prices at that timestamp: near CE, near PE, far CE, far PE.
5. Compute the static same-terminal-spot flatline:
`F = C1 - P1 - C2 + P2`.
6. If every candidate is non-positive, do not skip the day or week; move to the next available intraday timestamp.
7. At the **first timestamp** with at least one positive candidate, select the candidate with the largest positive F.
8. Enter the four legs at that timestamp.
9. Stop looking for another entry during that weekly cycle.

## Exit

All four legs are closed at the near weekly expiry. Near CE/PE settle; far CE/PE are manually closed at observed market prices at or before the near-expiry index close.

## Chart win rate versus realized win rate

The selected chart metric is positive by construction. Therefore the corrected workflow must report:

- `chart_positive_win_rate_pct`: expected to be 100% for selected trades.
- `realized_win_rate_pct`: actual net-P&L percentage after far-leg mark-to-market and costs.

The second measure is not mathematically guaranteed to be 100% because the static chart applies one hypothetical terminal spot across two expiries, whereas the actual trade liquidates the far options at their observed market prices at the near expiry.

Sensibull documents target-date/time P&L as a separate concept from expiry-day P&L and notes that approximate P&L can change with market conditions, implied volatility and the exact exit date. citeturn198794search0turn198794search9

## Cross-verification artifacts

The corrected workflow produces:

- `intraday_selected_near_exit.parquet`: exactly one selected trade per weekly cycle where a positive opportunity is found.
- `intraday_scan_audit.parquet`: every intraday timestamp checked, number of valid strikes, number positive, maximum flatline, and whether it triggered.
- `intraday_decision_surface.parquet`: all available ±400/50-point candidate values at every actual decision timestamp.

These artifacts are intended to make a manual strategy audit possible without trusting the summary P&L alone.

## Research consequence

All Phase 9A/9B realized-P&L results based on 09:20-only selection are superseded. H2/H3 results produced from that same cadence are also non-authoritative. Phase 9D must establish the corrected H1 baseline before H2/H3 are rerun.
