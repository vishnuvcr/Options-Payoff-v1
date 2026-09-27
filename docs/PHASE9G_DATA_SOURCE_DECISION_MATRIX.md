# Phase 9G data-source decision matrix

| Source | Intraday | Far-expiry evidence | 17-strike potential | Cost/access | Current status |
|---|---|---|---|---|---|
| thetrademarkk/india-index-options-1m | 1-minute | Expiry files generally begin about one week before own expiry; 2026 H2/H3 sampled entry dates had zero same-day far rows | H1 works; H2/H3 incomplete | Open HF | **Rejected for pooled H2/H3 inference** |
| rissin/nse-options-intraday | 1-minute from Oct 2024 in its intraday track | Dataset exposes expiry, strike and option type; direct far-expiry coverage still needs successful validation | Potentially yes | Open HF | **Validation branch active; no result accepted yet** |
| optionsdata.shop full-chain archive | 1-minute, every live strike/expiry per vendor | Public description explicitly claims every live expiry on every trading day | Yes by vendor description | Paid | **Candidate replacement; not acquired** |
| MoneyTicks expired options archive | 1-minute, contract-addressed API/export per vendor | Public description claims every expired NIFTY contract | Potentially yes | Access/licensing gate | **Candidate replacement; not acquired** |
| SauMStats NIFTY market-data engine / 2024 Kaggle + 2026 live | 1-minute contract files documented by expiry/trade date | API explicitly queries arbitrary expiry on a trade date; actual pooled H2/H3 coverage still needs validation | Potentially yes | Dataset access required | **Candidate replacement** |
| Zerodha nearest-expiry collectors | 1-minute | Nearest-expiry design | No for H2/H3 | Account/token | **Not suitable as primary H2/H3 source** |

**Decision rule:** no H2/H3 performance result enters the manuscript unless a source passes empirical entry-time coverage checks for representative weekly cycles, including the exact 17-shift universe and all four option legs. If sources are mixed across calendar periods, source heterogeneity must be reported and the periods must not be silently pooled as though measured identically.


### Rissin validation result — 2026-09-27
The dedicated Rissin coverage workflow sampled 96 timestamps for each far-rank (H2/H3) across 2024–2026. H2 had far-expiry rows at 64/96 samples and an exact 17-shift grid at 26/96; H3 had far-expiry rows at 63/96 and an exact 17-shift grid at 15/96. The 2024 samples were pre-coverage and had zero rows; the dataset's intraday track starts in October 2024. Therefore Rissin **passes the empirical coverage gate for 2025–2026 and partially for late 2024**, but is not a complete 2021–2026 source.
