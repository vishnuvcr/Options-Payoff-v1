# Phase 7A — Historical margin reconstruction

## Calibration observation

The user provided a Sensibull Strategy Builder screenshot showing:

- NIFTY spot: 23,140.50
- 1× 29-Sep-2026 23,450 CE short
- 1× 29-Sep-2026 23,450 PE long
- 1× 06-Oct-2026 23,450 CE long
- 1× 06-Oct-2026 23,450 PE short
- Sensibull standalone margin: ₹88,076
- Target-day futures prices shown by Sensibull: 29-Sep FUT 23,190 and 06-Oct FUT 23,197

Public historical market data identify 23,140.50 as the NIFTY 50 close on 25-Sep-2026; contemporaneous futures data show the Sep NIFTY future at 23,190 and a 65-unit NIFTY lot. citeturn979735search1turn979735search5

Thus the screenshot is treated as a 25-Sep-2026 calibration observation. The target margin is not inferred from spot × quantity; it is an empirical target for validating a reconstructed exchange-margin calculation.

## Why spot and quantity are not sufficient

NSE Clearing's SPAN system evaluates the portfolio across price/volatility risk scenarios using daily risk arrays. Those risk arrays are supplied in daily SPAN Risk Parameter files. citeturn979735search8turn979735search0

NSE Clearing's data list explicitly includes daily SPAN Risk Parameter Files and historical margin/volatility data as public/shareable research data. citeturn593430view0

For a multi-expiry option portfolio, the margin therefore depends on:

- the exact contracts and strikes;
- signed quantities and lot size;
- the daily SPAN risk arrays;
- calendar-spread offset rules;
- exposure/ELM rules;
- and, depending on the displayed platform field, whether premium or other broker-level components are added separately.

## Phase 7A calculation

The workflow uses the open-source `marginism` 0.1.1 implementation as an independent executable reference for NSE/NSCCL SPAN files. It calculates consolidated basket margin from the supplied `.spn` file and reports SPAN, exposure, option-premium and additional components.

The repository does not force the ₹88,076 screenshot value to equal any one component. It reports:

1. reconstructed consolidated basket margin;
2. SPAN component;
3. exposure component;
4. option-premium component;
5. additional/ELM component;
6. difference from the screenshot target;
7. whether the difference is within 1%.

## Percentage denominator

Sensibull publicly documents its displayed Max Profit % as:

`Max Profit / Margin needed × 100`

and Max Loss % analogously. Therefore, once the correct historical margin denominator is calibrated, the strategy's 2.5% gate becomes:

`estimated max profit / reconstructed margin required × 100 > 2.5%`.

For the screenshot target alone, 2.5% of ₹88,076 is ₹2,201.90. This is a calibration number, not a backtest result.

## Important distinction

The screenshot's Target Day Futures Prices are Sensibull's target-day assumptions for scenario/P&L display. They should not be confused with the realized future settlement values used in historical P&L.

Likewise, margin reconstruction solves the **capital/percentage denominator** question. It does not eliminate the separate economic `S2-S1` exposure created by holding the synthetic positions to different expiries.

## Phase 7A exit criteria

The phase is complete only after either:

- a reproducible SPAN-based margin matches the screenshot closely enough to justify using it as the historical denominator; or
- a documented mismatch remains, with the reason isolated and the backtest retaining a clearly labeled proxy rather than claiming exact platform replication.
## Calibration result — screenshot position

The Phase 7A workflow successfully downloaded the NSE Clearing/NSCCL SPAN archive for 25-Sep-2026 and reconstructed the user's exact four-leg position with `marginism`.

| Quantity | Value |
|---|---:|
| Sensibull screenshot standalone margin | ₹88,076.00 |
| Reconstructed SPAN component | ₹27,647.10 |
| Reconstructed exposure component | ₹60,165.30 |
| Reconstructed option-premium component | ₹529.75 |
| Reconstructed total | **₹87,812.40** |
| Difference | **-₹263.60** |
| Absolute difference | **0.2993% of screenshot margin** |

The independent SPAN reconstruction therefore matches the screenshot's standalone margin to within 0.30%. This is strong calibration evidence that the capital denominator can be reconstructed from exchange SPAN data rather than approximated from spot notional or premium.

For this exact screenshot position:

`₹88,076 × 2.5% = ₹2,201.90`

Using the independently reconstructed margin instead:

`₹87,812.40 × 2.5% = ₹2,195.31`

The difference between these two 2.5% thresholds is only ₹6.59 for this calibration position.

### Margin formula validated by the calibration

The consolidated initial/final margin is exactly `SPAN ₹27,647.10 + exposure ₹60,165.30 = ₹87,812.40`. The `option_premium ₹529.75` field is reported separately by the engine and is not added to the consolidated margin total. The authoritative calibration output should therefore use the consolidated basket total ₹87,812.40.

### Historical implication

The 2.5% denominator question is now resolved in principle: it is a **margin-required denominator**, and the SPAN-based reconstruction reproduces the user's screenshot closely. The remaining work is to generate the historical margin series for the full candidate set and attach a margin value to every entry timestamp/strike.

That historical series should use the exchange's contemporaneous SPAN archive for each entry date, not today's margin rates retroactively.
## Direct NSE SPAN source and checksum

The calibration used the official archive naming/pattern documented by an independent open-source NSE/NSCCL margin integration: `https://nsearchives.nseindia.com/archives/nsccl/span/nsccl.20260925.i5.zip`. The extracted SPAN payload was `nsccl.20260925.i05.spn` with SHA-256 `b1d00132a6397e5b8d5b13524f89142605fefc8901cecabe370ff73509ba0f3f`.

The complete calibration report is committed at `results/phase7a/margin_calibration_2026-09-25.json`.
## Historical candidate reconstruction result

The historical coverage probe found i1, i2, i3, i4, i5 and settlement/sensitivity s SPAN archives for all 891 entry dates in the Phase 3 sample.

The exact primary workflow uses i1 as the no-look-ahead margin snapshot. The user's current ±400 grid and 2.5% rule reduce the exact margin reconstruction to 31 candidates across 11 timestamps after applying the 4% combined ELM lower bound of the two short index-option legs. All 31 were evaluated with full SPAN basket margin.

Four i1 candidates pass the 2.5% margin-based gate, and maximum-INR and maximum-percentage selection are identical:

- 2021-08-04, +100, 4.5728%
- 2022-04-04, +300, 5.1319%
- 2022-05-25, -250, 2.6441%
- 2022-06-30, -400, 2.6564%

The exact primary ledger and settlement-file sensitivity ledger are stored under `results/phase7a/`.