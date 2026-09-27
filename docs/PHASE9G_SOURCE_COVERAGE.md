# Phase 9G H2/H3 source-coverage finding

The corrected Phase 9G reconstruction found that the Hugging Face source used for the H1 control does not contain the required pre-entry observations for H2/H3 far weekly expiries.

## Audit result

The dedicated coverage audit sampled 152 representative timestamps for each of far-rank 2 and far-rank 3. In every sampled case, the far-expiry file had **zero rows on the entry date**, hence zero common CE/PE strikes and zero exact 17-shift surfaces.

The underlying expiry files themselves are populated, but their historical windows typically begin about eight calendar days before their own expiry. For example, the 20-Jan-2026 expiry file begins on 12-Jan-2026, and the 27-Jan-2026 expiry file begins on 19-Jan-2026. That window is sufficient for H1, but not for H2/H3 when the strategy must enter during the near-expiry cycle.

## Interpretation

NSE currently specifies four weekly NIFTY 50 option expiry contracts and 50-point strike spacing for weekly/monthly contracts. Therefore the absence of H2/H3 rows in this particular dataset must **not** be interpreted as non-existence of the exchange contracts. It is a data-coverage limitation.

No H2/H3 P&L inference is accepted from this source. A source containing pre-entry intraday quotes for all live expiries is required before the far-expiry comparison can be completed.

## Candidate replacement sources

A currently advertised commercial source, optionsdata.shop, claims 1-minute NIFTY full-chain data for every live strike and expiry from June 2021 through September 2026. Its public documentation states that the archive is rebuilt from ICICI Breeze API data and delivered as Parquet/CSV, without IV/Greeks/bid-ask. This is a source lead only; no paid data were purchased or used in the present result.

A second open-source lead is SauMStats' NIFTY options data engine, which documents a 2024 Kaggle dataset and 2026 live data organized by expiry and trade date. The repository does not itself establish that the historical 2024 data contain the exact pre-entry H2/H3 observations needed here, so it remains a candidate source to test rather than an accepted substitute.

## Acceptance rule

The Phase 9G strategy remains frozen. H2/H3 will only be re-run after source validation confirms that the same entry timestamp contains all four quoted legs for the chosen far expiry and the exact 17-strike grid can be reconstructed without look-ahead.
