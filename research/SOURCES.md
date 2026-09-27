# Source register

## Official / primary sources

1. NSE — NIFTY 50 F&O contract specifications. Current NSE page states four weekly expiries and Tuesday weekly expiry, with holiday adjustment.
2. NSE — Revision in Expiry Day of Index and Stock Derivatives Contracts, 17-Jun-2025. New contracts expiring on or before 31-Aug-2025 kept Thursday; contracts expiring on or after 01-Sep-2025 moved to Tuesday.
3. NSE — Securities Transaction Tax / SEBI fees / other levies. Current page lists option-sale STT 0.15% from 01-Apr-2026, 0.10% before that; exercise STT 0.15% from 01-Apr-2026, 0.125% before that; SEBI fee 0.0001%; equity-option stamp duty 0.003%; GST 18% on broker services.
4. NSE — Finance & Accounts circular NSE/FA/73061 dated 27-Feb-2026. Equity-option transaction-charge outflow is ₹3,553 per crore of premium turnover from 01-Mar-2026 (transaction charge ₹3,552 plus ₹0.01 IPFT contribution).
5. NSE — Contract Information page. Current page links the permitted-lot-size CSV and contract metadata.
6. Paytm Money — pricing update, Jan-2025. Brokerage aligned to a flat ₹20 across segments from 15-Jan-2025.
7. Paytm Money — brokerage calculator. Notes that its displayed calculation does not include every platform/depository/other fee.

## Public research/data sources

8. Hugging Face — thetrademarkk/india-index-options-1m. 1-minute NIFTY/BANKNIFTY/SENSEX index and option OHLCV/OI data, CC BY-NC 4.0; option data are stored by expiry.
9. Hugging Face — rissin/nse-options-intraday. Historical Indian index options and intraday data; daily history notes NSE F&O bhavcopy lineage.
10. Hugging Face — artist-23/nifty-options-data. NIFTY options data covering 2020-2025 with spot, IV, OI and price fields.
11. GitHub — SatvikBajpai/nifty-options-greeks. Reproducible NIFTY historical-options/Greeks pipeline; repository notes that source data are not redistributed.

## Research literature / conceptual sources

12. Vipul (2008), Cross-market efficiency in the Indian derivatives market: A test of put-call parity, Journal of Futures Markets 28(9), 889–910. DOI 10.1002/fut.20325.
13. Mohanti & Priyan (2015), An Empirical Test of Cross-Market Efficieny of Indian Index Options Market Using Put-Call Parity Condition.
14. Azzone & Baviera (2020), Synthetic forwards and cost of funding in the equity derivative market, arXiv:2011.03795.
15. Nisbet (1992), Put-call parity theory and an empirical test of the efficiency of the London Traded Options Market, Journal of Banking & Finance 16(2), 381–403.
16. Shin (2026), The P behind Q: Empirical Evidence from Physical Drift in Put-call Parity, SSRN 6762800.
17. Wilkens (2026), Here Today, Gone Today: First Evidence on European Zero-Day Options, SSRN 7094758.

Source retrieval dates and substantive-use citations are maintained in the research manuscript and phase documents.

## Payoff-platform sources — Phase 7

18. Sensibull Blog, “Minor Update on Sensibull Strategy Builder,” 22-Jul-2022. Documents the displayed percentage formula: Max Profit % = Max Profit / Margin needed × 100; Max Loss % = Max Loss / Margin needed × 100.
19. Sensibull / Trading Q&A, “Multi-leg Options Strategies by Sensibull,” Jun-2018. Sensibull explains that max profit/max loss shown are expiry-day quantities and provides the standard premium/strike-width arithmetic, including a conservative STT buffer.
20. Sensibull / Trading Q&A, “Sensibull - The Options Trading Platform,” Sep-2020. Sensibull notes that calendar-spread max profit/loss can be materially off in extreme events because the open option's IV can fluctuate; it suggests reading scenario P&L from the graph and treating the estimate cautiously.
21. Streak current product listing (Google Play), updated 07-Sep-2026. Documents current option functionality including payoff graphs, option-chain integration, underlying/time-based option strategies, and ATM/ITM/OTM/live-premium selection.
22. Streak Terms / disclosures. Public Streak material describes options payoff graphs as hypothetical and not guaranteed representations of actual outcomes.

These Phase 7 platform sources are used to separate (a) the static payoff-chart metric, (b) the displayed max-profit/max-loss percentage, and (c) the true economic P&L of a mixed-expiry position.


## 2026 live-pricing verification note

23. Paytm Money 2026 public educational material describes a flat ₹20-per-executed-order model; its public F&O FAQ page currently displays ₹10 per executed F&O order. Because these public pages are internally inconsistent and Paytm documents account-specific legacy rates, Phase 9G keeps the predeclared ₹20/order primary assumption and tests ₹10 and ₹40 as sensitivity cases. Live deployment should use the user's current contract-note brokerage rate, not the research default.
