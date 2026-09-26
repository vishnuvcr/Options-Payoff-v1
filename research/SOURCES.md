# Source register

## Official / primary sources

1. NSE — NIFTY 50 contract specifications. Current page states four weekly expiry contracts and Tuesday weekly expiry, with holiday adjustment.
2. NSE — Securities Transaction Tax page. Current page states option-sale STT is 0.15% from 2026-04-01 and defines the taxable option-sale value as premium.
3. NSE — SEBI turnover fees / STT / stamp duty guidance. Current page provides SEBI fee and stamp-duty rates.
4. Paytm Money — pricing update. Current Paytm Money material states brokerage aligned to a flat ₹20 across segments from 15-Jan-2025 for the applicable account population.
5. Paytm Money — brokerage calculator. Useful for checking the complete charge stack before live use.

## Public research/data sources

6. Hugging Face — rissin/nse-options-intraday: historical Indian index options, including NIFTY daily data and recent intraday data; source notes say daily history derives from NSE F&O bhavcopy.
7. Hugging Face — thetrademarkk/india-index-options-1m: 1-minute NIFTY/BANKNIFTY/SENSEX option/index data with per-expiry parquet files.
8. Hugging Face — artist-23/nifty-options-data: large NIFTY options dataset covering 2020-2025 with spot, strike, IV, OI and price fields.
9. GitHub — SatvikBajpai/nifty-options-greeks: reproducible NIFTY historical option/greeks pipeline using NSE bhavcopy data; data itself is intentionally not redistributed by the repository.

## Research literature / conceptual sources

10. Indian index-option market-efficiency literature on put-call parity and transaction costs.
11. Recent research on synthetic forwards, put-call parity implementation frictions and path-dependent enforcement costs.
12. General options literature on calendar spreads and term-structure effects.

Full links and citations are maintained in the research notebooks/manuscript as each source is used substantively.
