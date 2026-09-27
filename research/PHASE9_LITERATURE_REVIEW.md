# Phase 9 literature review — cross-expiry option spreads, payoff charts and trading costs

## Scope

This phase reviews theory and empirical evidence directly relevant to the corrected strategy: same-strike synthetic-forward legs across adjacent expiries, calendar/time spreads, expiry-date mark-to-market, option transaction costs, and the interpretation of retail payoff charts.

## Directly relevant NIFTY evidence

Slivka, Liang & Xue (2020), An Empirical Study of Nifty 50 Option Time Spreads, Indian Journal of Finance 14(8-9), 8-19. DOI 10.17010/ijf/2020/v14i8-9/154944. The study develops preliminary rules for NIFTY 50 call time spreads using day-end data from 2015-2019 and reports positive out-of-sample results for its rules. It is directly relevant because it establishes that NIFTY time-spread behaviour has been studied empirically, but the documented strategy is not the same as the present four-leg mixed call/put construction or the present near-expiry manual-close convention.
Sources: https://www.indianjournaloffinance.co.in/index.php/IJF/article/view/154944 ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3704896

John (2026), The Vega Paradox in Double Calendar Spreads: Evidence from Nifty 50 Weekly Options and the Volatility Term Structure. A recent preprint examines double calendars involving short near-weekly calls/puts and long longer-dated calls/puts and reports a high-stress-period disconnect between weekly idiosyncratic volatility and the volatility term structure. This is treated as a research lead rather than established peer-reviewed evidence.
Source: https://www.researchgate.net/publication/402165746_The_Vega_Paradox_in_Double_Calendar_Spreads_Evidence_from_Nifty_50_Weekly_Options_and_the_Volatility_Term_Structure

## Option parity and synthetic-forward structure

Put-call parity links European calls, puts and forward contracts and implies that a long call plus short put at the same strike/expiry replicates a long forward. This is the mathematical basis for interpreting the present four-leg construction as a spread between two synthetic-forward exposures rather than as a universally flat economic position.
Sources: Bossu, Put-Call Parity, DOI 10.1002/9780470061602.eqf07042; Back, Option Pricing, Oxford University Press, DOI 10.1093/acprof:oso/9780190241148.003.0016.

## Calendar/time-spread pricing and term structure

Seok, Brorsen & Niyibizi (2018), Modeling calendar spread options, Agricultural Finance Review 78(5), 551-570, DOI 10.1108/AFR-09-2017-0088. The paper develops a two-factor framework for options on futures calendar spreads and emphasizes joint dynamics across maturities.

Schneider & Tavin (2018), From the Samuelson volatility effect to a Samuelson correlation effect, Journal of Banking & Finance 95, 185-202, DOI 10.1016/j.jbankfin.2016.12.001. The study models and calibrates calendar spread options and highlights maturity-dependent dependence between contracts. This supports treating the far-leg value at near expiry as a separate stochastic object rather than replacing it with its own expiry settlement.

Frau, Fusai & Kyriakou (2025), Energy Commodities and Calendar Spread Options, Energy Economics 151, 108809, DOI 10.1016/j.eneco.2025.108809. Although the asset class differs, the work reinforces the methodological point that cross-maturity option structures require modelling joint term structure and volatility dynamics.

## Transaction costs and execution

Trading Costs for Listed Options: The Implications for Market Efficiency (Journal of Financial Economics, 1980, DOI 10.1016/0304-405X(80)90016-1) reports that accounting for option trading costs, especially bid-ask spreads, can eliminate apparent abnormal returns in the tested setting.

Govindaraj, Li & Zhao (2020), The Effect of Option Transaction Costs on Informed Trading in the Options Market Around Earnings Announcements, Journal of Business Finance & Accounting 47(5-6), 615-644, DOI 10.1111/jbfa.12443. The study finds predictive effects are stronger where relative option bid-ask spreads are lower, illustrating why liquidity and execution assumptions must be part of empirical design.

Recent option-factor research also uses effective-spread assumptions rather than midpoint fills and reports net returns after those costs. This supports Phase 9 sensitivity testing across several slippage levels.

## Retail payoff-platform semantics

Sensibull documents a custom Strategy Builder that displays payoff diagrams, max profit, max loss, margin required, time decay and Greeks. Its later Payoff Table documentation explicitly distinguishes P&L on a selected target date from expiry-day P&L. An educational YouTube walkthrough also describes expiry and target-date curves.
Sources:
- https://blog.sensibull.com/2018/08/17/announcing-custom-strategy-builder/
- https://blog.sensibull.com/2023/07/06/payoff-table-on-strategy-builder-analyse-widgets/
- https://sensibull.com/
- NiftyBN, YouTube, 15-May-2020: https://www.youtube.com/watch?v=Kx1opAo_y70

Options Education provides a calendar-spread example specifically noting limitations of P&L graphs when expirations differ and explaining the challenge caused by different expiration dates.
Source: https://www.optionseducation.org/videolibrary/calendar-spread-example

## Implications for this research

1. The entry payoff chart is a useful screening representation, but it does not by itself identify the realized P&L of a mixed-expiry position at the near expiry.
2. The far-expiry CE/PE values at near expiry are economically material and must be observed/reconstructed, not replaced by far-expiry settlement.
3. NIFTY time-spread evidence exists, but external results cannot be transferred to this four-leg selector without a direct backtest.
4. Transaction costs, bid/ask effects and liquidity must be part of the primary interpretation, not an afterthought.
5. The corrected H1 design therefore separates static chart selection from realized economic P&L and validates both gross and net outcomes.

## Limitations

Much of the formal calendar-spread literature concerns commodity or futures options rather than NIFTY index options. The 2026 NIFTY double-calendar item is a preprint lead, not established peer-reviewed evidence. Retail platform documentation explains product functionality but does not constitute independent validation of a strategy's profitability.
