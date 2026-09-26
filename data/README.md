# Data layer

## Primary data source

The Phase 2 primary source is the public Hugging Face dataset thetrademarkk/india-index-options-1m. Its dataset card describes 1-minute OHLCV(+OI) bars for NIFTY, BANKNIFTY and SENSEX, with NIFTY index data in index/NIFTY.parquet and option data stored per expiry under options/NIFTY/YYYY-MM-DD.parquet.

The dataset is marked CC BY-NC 4.0 and explicitly warns users to verify against official exchange data before relying on it.

## Why raw files are not committed

The source is large and exchange-derived market data may have redistribution constraints. The repository therefore stores the source manifest, transformation code, retrieval parameters and hashes, while GitHub Actions caches the source files between runs.

A compact derived strategy-input dataset can be committed only after confirming that the relevant license permits redistribution.

## Required columns

### Index
- timestamp (IST)
- open
- high
- low
- close
- trading_day
- symbol

### Options
- timestamp (IST)
- open
- high
- low
- close
- volume
- open_interest
- trading_day
- symbol
- strike
- option_type
- expiry

## Data quality rules

- Normalize all timestamps to Asia/Kolkata.
- Use exchange-listed expiry identifiers from contract data, not weekday assumptions.
- Preserve the historical NIFTY expiry-day transition: contracts expiring on or before 31-Aug-2025 remain Thursday; contracts expiring on or after 01-Sep-2025 use Tuesday under NSE's transition notice.
- Never fill a missing option quote by looking into a future timestamp.
- Record missing or sparse contracts rather than silently interpolating.
- Compare spot and option timestamps before selecting the 09:20 IST research observation.
- Validate final settlement observations against official NSE data where possible.

## Phase 2 output

The key derived table is the strategy-input table used by Phase 3. It should contain one row per eligible research entry with:

entry_timestamp, spot_at_entry, near_expiry, next_expiry, strike_candidate, option entry prices for all four legs, near_settlement, next_settlement, lot_size, source revision, and data-quality flags.
