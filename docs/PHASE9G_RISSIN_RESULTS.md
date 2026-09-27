# Phase 9G — Corrected Rissin 2024–2026 Results

## Primary result

Using the frozen exact-17-strike selector, 09:20–15:29 scan, first valid positive timestamp, maximum positive strike at that timestamp, 0.25% premium slippage and ₹20/order brokerage:

- H1: 66 realized trades, ₹166,247.97 net, 81.82% win rate, PF 8.40, max drawdown ₹14,662.57.
- H2: 37 realized trades, ₹148,974.37 net, 94.59% win rate, PF 12.19, max drawdown ₹7,800.89.
- H3: 16 realized trades, ₹120,194.26 net, 93.75% win rate, PF 38.71, max drawdown ₹3,187.37.

## Paired horizon tests

H2-H1: 34 matched cycles, mean delta ₹1,820.88, 4-cycle block bootstrap 95% CI ₹560.37 to ₹2,749.46, sign-permutation p=0.00570, BH q=0.01140.

H3-H1: 16 matched cycles, mean delta ₹4,804.10, block bootstrap 95% CI ₹328.62 to ₹8,870.46, sign-permutation p=0.01825, BH q=0.01825.

Both fixed-horizon candidates therefore pass the preregistered paired comparison against H1 on this same-source sample.

## Exploratory H3 vs H2

On 11 matched H2/H3 cycles, H3-H2 mean delta is ₹4,522.86; the block-bootstrap CI is ₹1,724.18 to ₹7,932.38 and sign-permutation p≈0.00470. This comparison is exploratory because the preregistered primary comparison was against H1.

## Chronological robustness

The 2026-only H2-H1 and H3-H1 block-bootstrap intervals cross zero. Thus pooled 2024–2026 significance is not sufficient for claiming an untouched out-of-sample edge.

## Cost sensitivity

All three horizons remain net-positive at 0.5% and 1.0% slippage in the Rissin sample, and remain positive under ₹10 and ₹40 brokerage at 0.25% slippage.

## Interpretation

The evidence identifies H2 and H3 as fixed-horizon candidates for an untouched future holdout. It does not justify dynamic horizon switching or immediate deployment. H3 has the stronger pooled economics and also beats H2 in the exploratory matched comparison, but that comparison must be validated prospectively before production use.

No conclusion should be drawn from the current vendor's 2024 data alone: the Rissin intraday archive begins in October 2024, so its 2024 results cover only the late-2024 sample.
