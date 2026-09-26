# Literature review — initial evidence base

## 1. Put-call parity and synthetic forwards

Put-call parity implies that, for a common strike and expiry, a long call plus short put behaves like a synthetic long forward. This is the theoretical basis for treating the two call/put pairs in the strategy as synthetic forward positions. Empirical work also shows that parity implementation is affected by funding, capital and execution frictions.

## 2. Indian index-option evidence

Indian NIFTY studies have reported measurable put-call parity deviations, but the estimated exploitable amount is sensitive to transaction costs and trading constraints. Vipul (2008) used transaction-level NIFTY data and reported frequent parity violations, with patterns related to time of day, moneyness, volatility and days to expiry. Mohanti & Priyan (2015) reported that transaction costs materially reduced the proportion of apparently exploitable violations.

These findings support testing this strategy with explicit trading costs rather than interpreting a positive static payoff or mid-price discrepancy as an arbitrage profit.

## 3. Transaction costs and execution

The broader options literature shows that option spreads and commissions can eliminate many apparent parity violations. Recent 2026 evidence from European index options similarly reports tight parity at quoted mid-prices but substantially larger costs once spreads are crossed, especially near expiry. This is directly relevant to a four-leg strategy whose gross edge may be small relative to cumulative execution cost.

## 4. Implication for this study

The strategy should therefore be evaluated as an empirical cross-expiry synthetic-forward spread, not as a guaranteed arbitrage. Primary analyses must use conservative execution assumptions, dated taxes/fees, and out-of-sample validation.

## Key references

1. Vipul (2008), Cross-market efficiency in the Indian derivatives market: A test of put-call parity, Journal of Futures Markets 28(9), 889–910. DOI 10.1002/fut.20325.
2. Mohanti & Priyan (2015), An Empirical Test of Cross-Market Efficieny of Indian Index Options Market Using Put-Call Parity Condition.
3. Azzone & Baviera (2020), Synthetic forwards and cost of funding in the equity derivative market, arXiv:2011.03795.
4. Nisbet (1992), Put-call parity theory and an empirical test of the efficiency of the London Traded Options Market, Journal of Banking & Finance 16(2), 381–403.
5. Shin (2026), The P behind Q: Empirical Evidence from Physical Drift in Put-call Parity, SSRN 6762800.
6. Wilkens (2026), Here Today, Gone Today: First Evidence on European Zero-Day Options, SSRN 7094758.

Source URLs and retrieval dates are maintained in research/SOURCES.md.