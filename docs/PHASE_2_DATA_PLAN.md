# Phase 2 — Data acquisition and validation

## Objective

Create a reproducible, cached and validated historical dataset capable of evaluating the Phase 1 strategy without look-ahead.

## Date coverage

Default target: 2021-06-01 through the latest completed week available in the primary dataset.

The pipeline is date-parameterized so validation can be rerun on shorter windows.

## Expiry mapping

Historical expiry dates will be inferred from the option-file names and contract data.

The pipeline must not assume today's Tuesday expiry for the whole historical sample. NSE's June 2025 transition states that contracts expiring on or before 31-Aug-2025 retain the prior Thursday expiry and contracts expiring on or after 01-Sep-2025 use Tuesday.

## Entry extraction

At each eligible research entry timestamp:

1. Obtain NIFTY spot.
2. Identify the nearest currently listed weekly expiry T1 and the next weekly expiry T2.
3. Determine ATM as the nearest listed strike to spot.
4. Construct candidates K, K-400 and K+400.
5. Extract the four required option prices for each candidate.
6. Record the exact source timestamps and data-quality flags.
7. Record the two later settlement values S1 and S2.

## Price selection

Phase 2 retains OHLC and does not decide the final execution fill. Phase 3 will choose:
- conservative buy-at-ask / sell-at-bid when quote data are available;
- midpoint or close fallback only if explicitly allowed by sensitivity settings.

If only OHLC is available, the workflow marks the row as an execution-fidelity downgrade rather than pretending that close equals executable price.

## Validation

Required checks:
- duplicate timestamps/contracts
- impossible negative prices
- missing expiry files
- missing four-leg combinations
- stale/zero-volume quotes
- spot/option timestamp alignment
- strike availability for +/-400 candidates
- lot-size validity
- settlement observation completeness
- historical expiry-day transition

## Cross-source validation

A subset of dates will be compared against:
- NSE official contract/settlement information
- an independent public NIFTY options dataset

Discrepancies will be logged and quantified before Phase 3.

## Output

- data/source manifest
- cached raw files or cache keys
- compact strategy-input table
- data-quality report
- checksum/revision record
