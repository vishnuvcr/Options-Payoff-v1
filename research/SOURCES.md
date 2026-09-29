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


## Literature-review additions — 2026-09-27

1. **Vipul (2009), “Box-spread arbitrage efficiency of Nifty index options: The Indian evidence,” Journal of Futures Markets 29(6), 544–562.** Time-stamped NIFTY transactions data were used to identify box-spread mispricing; the reported transaction-cost-adjusted opportunities were frequent but short-lived, with liquidity/moneyness/volatility associated with mispricing. This supports testing execution realism and does not by itself establish persistence for the present cross-expiry strategy. Source: https://ideas.repec.org/a/wly/jfutmk/v29y2009i6p544-562.html

2. **Mixon (2007), “The implied volatility term structure of stock index options,” Journal of Empirical Finance 14(3), 333–354.** The paper finds some predictive content in the slope of implied-volatility term structures but reports weaker-than-expectations-hypothesis forecasting and discusses time-varying risk premia. This is directly relevant to H1/H2/H3 far-expiry comparisons because the horizon changes the option term structure being traded. Source: https://www.sciencedirect.com/science/article/pii/S0927539806000715

3. **Christoffersen et al. (2016), “Analyzing volatility risk and risk premium in option contracts: A new theory,” Journal of Financial Economics 120(1), 1–20.** The study models maturity- and strike-specific volatility surfaces and documents time variation in volatility risk premia. It motivates treating cross-maturity option differences as potentially risk-premium driven rather than automatically as arbitrage. Source: https://www.sciencedirect.com/science/article/pii/S0304405X16000052

4. **Caldana et al. (2017), “From the Samuelson volatility effect to a Samuelson correlation effect: An analysis of crude oil calendar spread options.”** Calendar-spread pricing depends on the dependence structure across maturities; empirical calibration indicates that cross-maturity dependence is material. Although the underlying market differs from NIFTY, the result reinforces that calendar structures cannot be interpreted from one-dimensional terminal-price intuition alone. Source: https://www.sciencedirect.com/science/article/pii/S0378426616302424

5. **Câmara, Krehbiel & Li (2011), “Expected returns, risk premia, and volatility surfaces implicit in option market prices,” Journal of Banking & Finance 35(1), 215–230.** The paper documents non-monotonic implied-volatility term structures and relates them to jump and risk-premium components. This supports keeping volatility-surface variables as explanatory/contextual features rather than assuming a flat forward-volatility relation. Source: https://www.sciencedirect.com/science/article/pii/S0378426610002992

### Literature implications for Phase 9G

The literature does not justify treating a positive static cross-expiry payoff chart as a guaranteed arbitrage. Empirical work on NIFTY box spreads indicates that transaction-cost-adjusted mispricing can exist but may disappear rapidly, while broader option research shows that maturity-dependent volatility, risk premia, and cross-maturity dependence materially affect option prices. Phase 9G therefore treats the static flatline as a **selection metric**, evaluates realized near-expiry P&L separately, and compares fixed far-expiry horizons with explicit execution costs and paired statistical inference.


## Additional literature — 2026-09-27

6. **Vipul (2008), “Cross-market efficiency in the Indian derivatives market: A test of put-call parity,” Journal of Futures Markets 28(9), 889–910, DOI 10.1002/fut.20325.** Using 35 months of time-stamped NIFTY transactions data, the paper reports frequent put-call parity violations and arbitrage opportunities after transaction costs that vanish quickly; patterns vary with intraday time, moneyness, volatility and days to expiry. This is directly relevant to the present study's emphasis on intraday timing, execution costs and maturity selection. Source: https://ideas.repec.org/a/wly/jfutmk/v28y2008i9p889-910.html

7. **Fournier (2024), “Modeling Conditional Factor Risk Premia Implied by Index Option Returns,” Journal of Finance, DOI 10.1111/jofi.13324.** The paper models option-return exposures and conditional risk premia across moneyness and maturity, using market return, variance-change, gamma and additional tail/volatility factors. It reinforces that cross-maturity option returns contain systematic risk-premium components and should not automatically be interpreted as pure arbitrage. Source: https://onlinelibrary.wiley.com/doi/10.1111/jofi.13324

8. **Hu, Li & Zhuo, “The Term Structure of Index Option Returns” (working paper; revised August 2026).** The study directly examines the maturity structure of index-option realized returns and finds that the term structure of option returns contains risk-premium components that differ by maturity. This is a particularly relevant conceptual reference for fixed H1/H2/H3 horizon comparison. Source: https://papers.ssrn.com/sol3/Delivery.cfm/5944594.pdf?abstractid=5944594&mirid=1

9. **Kumar, Sarva & Kumaresan (2025), “Behavioral Dynamics in Testing Markets: A Methodological Analogy to Trader and Investor Efficiency.”** Using Nifty50 spot/futures/options data from April 2018 to March 2024, the paper reports that transaction costs materially reduce the subset of apparent put-call parity violations that are exploitable. This supports explicit friction sensitivity in the present research. Source: https://doi.org/10.5281/zenodo.17567987

## Phase 10 literature / evidence additions — 2026-09-29

24. Vipul (2008), “Cross-market efficiency in the Indian derivatives market: A test of put-call parity,” *Journal of Futures Markets* 28(9), 889–910. Time-stamped NIFTY transactions data and reported short-lived parity violations motivate explicit intraday timing and execution-friction tests.
Source: https://doi.org/10.1002/fut.20325

25. Mutum, Das, Singh & Singha (2018), “Testing the Efficiency of Indian Index Options Market by Employing the Box-Spread Strategy: Empirical Evidence from S&P CNX Nifty Index,” *Indian Journal of Finance* 12(10), 21–33. Reported apparent box-spread mispricing was concentrated around illiquid levels/maturity segments and often was not exploitable after liquidity considerations.
Source: https://www.indianjournaloffinance.co.in/index.php/IJF/article/view/132492

26. Aggarwal & Gupta (2009), “Empirical Evidence on the Efficiency of Index Options Market in India,” *Asia Pacific Business Review*. Transaction costs materially affected the exploitability of apparent parity violations in Indian index options.
Source: https://doi.org/10.1177/097324700900500311

27. Kaeck, van Kervel & Seeger (2022), “Price impact versus bid–ask spreads in the index option market,” *Journal of Financial Markets* 59, 100675. The study documents large option bid-ask spreads relative to option value and examines their relation to price impact, motivating executable-spread sensitivity rather than relying only on close-price fills.
Source: https://doi.org/10.1016/j.finmar.2021.100675

28. Christoffersen et al. (2016), “Analyzing volatility risk and risk premium in option contracts: A new theory,” *Journal of Financial Economics* 120(1), 1–20. Maturity- and strike-specific volatility risk premia motivate scenario-aware cross-expiry analysis.
Source: https://doi.org/10.1016/j.jfineco.2016.01.004

29. Guo (2023), “Term spreads of implied volatility smirk and variance risk premium,” *Journal of Futures Markets*. Reports predictive content in implied-volatility term-spread factors for variance-asset returns, motivating a predeclared term-structure scenario test rather than ad-hoc Greek selection.
Source: https://doi.org/10.1002/fut.22409

30. Culp et al. (2021), “Option-Implied Spreads and Option Risk Premia,” NBER Working Paper 28941. Provides a framework for interpreting option-implied spreads as risk premia rather than pure arbitrage.
Source: https://www.nber.org/papers/w28941

These sources motivate the Phase 10 hypotheses. They do not establish that any Phase 10 refinement is profitable for this specific NIFTY strategy.
