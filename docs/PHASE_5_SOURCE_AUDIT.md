# Phase 5 source audit — regime and execution context

Date audited: 2026-09-26

## Exchange and market-structure sources

1. NSE Equity Derivatives Contract Specifications — NIFTY 50 weekly options, expiry convention and strike scheme.
   https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications
2. NSE NIFTY 50 F&O — contract information and lot-size reference.
   https://www.nseindia.com/static/products-services/equity-derivatives-nifty50
3. NSE All Reports — derivatives reports including daily settlement prices, participant-wise OI/trading volumes and FII derivatives statistics.
   https://www.nseindia.com/all-reports-derivatives
4. NSE Historical Contract-wise Price Volume Data — historical option contract fields and date/expiry/strike filters.
   https://www.nseindia.com/report-detail/fo_eq_security
5. NSE Historical Data — India VIX.
   https://www.nseindia.com/reports-indices-historical-vix

## FX and macro sources

6. RBI press release on the USD/INR reference-rate methodology.
   https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=36787
7. RBI Weekly Statistical Supplement — historical INR/USD and interest-rate context; after July 2018 the reference-rate dissemination is through FBIL.
   https://www.rbi.org.in/scripts/WSSView.aspx?Id=25702

## Broker execution source

8. Paytm Money F&O FAQ — current public page states Rs.10 brokerage for every unique executed F&O order.
   https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web

## Research implication

Official NSE sources are appropriate for contract metadata, historical derivatives reports and India VIX. The research still requires point-in-time construction: a variable observed only at end of day cannot be used to classify a 09:20 entry. Current Paytm Money public brokerage is recorded as Rs.10 per unique executed order, but historical broker-specific conclusions should be reconciled against the actual contract note for the relevant dates. The research engine therefore keeps brokerage configurable and retains a conservative higher-brokerage sensitivity.