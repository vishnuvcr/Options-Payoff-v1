# Phase 9F — Corrected H1 cross-market and regime audit

**Branch:** `phase-9F-regime-crossmarket-audit`
**Parent:** Phase 9E frozen-rule validation
**Purpose:** describe when the corrected H1 rule performs differently across pre-entry market regimes and cross-market conditions without changing the entry rule.

## Research questions

1. Does corrected H1 performance vary materially by India VIX regime?
2. Does performance differ after positive/negative global overnight moves?
3. Does USD/INR, gold, crude, and global-equity context co-move with trade outcomes?
4. Does same-day institutional flow context (FII/FPI and DII) describe winner/loser dispersion?
5. Do NSE/BSE relative-market conditions and NIFTY/Sensex overnight gaps correspond to different realized P&L distributions?
6. Are option-surface conditions (entry-time IV/volume/open-interest proxies already in the cached trade ledger) associated with the observed outcomes?
7. Which contextual variables have sufficient timestamp coverage to support a future point-in-time audit?

## Non-optimization rule

This phase is descriptive. No regime, feature, threshold, or subgroup discovered here can be converted into a new trade filter. Any apparent subgroup difference is reported with uncertainty and treated as a hypothesis for a separate preregistered validation phase.

## Point-in-time alignment

Only information available by the actual strategy entry timestamp may be attached as an explanatory variable.

- India VIX: latest completed/available observation before entry; daily closing value is used only when the entry-time value is unavailable.
- Global indices and Cboe VIX: prior-session close because these sessions precede the Indian cash open.
- Gold: latest completed LBMA/market observation known before the entry.
- USD/INR: latest completed session/reference observation known before the entry.
- FII/FPI and DII: prior completed trading-day cash-market flow, unless the source's timestamp clearly establishes earlier availability.
- NIFTY/Sensex: prior close and same-day opening-gap measures constructed without using the future trade outcome.
- Corporate actions/news: record only event dates/timestamps available before entry; do not use retrospective headlines or post-entry classifications.

## Context-source hierarchy

1. NSE official historical index/India VIX data and FII/FPI-DII reports.
2. BSE official Sensex/index data.
3. RBI/FBIL reference-rate data for USD/INR where available.
4. Cboe historical VIX data for global volatility.
5. LBMA/IBA gold benchmark for gold context.
6. FRED/yfinance/open-source GitHub sources only as documented fallbacks/cross-checks.
7. The repository's Hugging Face NIFTY options dataset remains the primary point-in-time option-data source already recorded in data/SOURCE_MANIFEST.json.

## Regime definitions

Regimes are predeclared before observing the H1 outcome:

- India VIX: sample quartiles.
- Global overnight equity return composite: sign of prior-session S&P 500 and Nasdaq returns, with Nikkei/Hang Seng/Shanghai context recorded separately.
- USD/INR and gold: sign and sample tercile bands of prior-session returns.
- FII/FPI and DII: positive/negative net-flow flags plus absolute-magnitude terciles.
- NIFTY opening gap: negative/flat/positive sign groups plus continuous gap.
- NSE/BSE relative move: NIFTY minus Sensex normalized daily return where both are available.
- Cross-market stress flag: conjunction of elevated India VIX and negative global equity context, used descriptively only.

## Statistical analysis

For every predeclared subgroup:

- trade count;
- total and mean/median net P&L;
- realized win rate with Wilson 95% interval;
- profit factor;
- maximum drawdown within subgroup in chronological order;
- bootstrap 95% interval for mean net P&L using IID resampling;
- four-trade circular block bootstrap for dependence sensitivity.

For continuous context variables, compute Spearman rank correlation with net trade P&L and bootstrap confidence intervals. Apply Benjamini-Hochberg correction to the descriptive association family. These tests are not used to select a new trading rule.

## Data-quality requirements

- Every context series must have source URL, retrieval date, coverage dates, timestamp convention and license/provenance recorded.
- Compact joined context data must be cached under `results/phase9f` and/or `data/phase9f` so later workflow runs do not redownload unchanged data unnecessarily.
- Missingness must be reported by variable and year.
- Any fallback source must be explicitly labeled in `source_used` and never silently mixed with the primary source.

## Corporate actions and news

NIFTY methodology already adjusts index levels for constituent corporate actions; therefore this phase records corporate-action/news availability and major event windows as context rather than attempting to restate index prices. Where a point-in-time corporate/news feed cannot be reconstructed reliably, the variable remains a limitation and is not imputed.

## Phase-exit criteria

Phase 9F is complete when the corrected 169-trade H1 ledger has a reproducible point-in-time context join, source coverage/missingness audit, predeclared regime summaries, uncertainty estimates, and an explicit statement of which contextual variables are and are not usable. No trading rule is changed in this phase.

## Sources inspected for this phase

- NSE historical index and India VIX archive.
- NSE FII/FPI and DII trading-activity report.
- NSE corporate actions/corporate filings.
- BSE official Sensex market-data pages.
- RBI/FBIL USD/INR reference-rate documentation.
- Cboe VIX historical data.
- LBMA precious-metal price information.
- GitHub open-source FII/DII, India VIX and global-market datasets as documented fallbacks.
- Hugging Face NIFTY index-options dataset already recorded in this repository.