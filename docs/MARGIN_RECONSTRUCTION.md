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