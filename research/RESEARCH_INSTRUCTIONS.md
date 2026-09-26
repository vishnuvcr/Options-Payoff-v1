# Research operating instructions

## Purpose

This file records the repository-level operating rules for the Options-Payoff-v1 research project.

## Research requirements

- Define research questions before modeling.
- Conduct a broad literature and data-source review.
- State aims, objectives, methodology, statistical analyses, results, inference, discussion, strengths, limitations, conclusions, and future directions.
- Keep a detailed phase plan. Change the plan only when the research design materially changes.
- Keep an error log. Every reproducible mistake or failed step that affects the work should be recorded.
- Update status after every material research step.
- Maintain an observable activity log for repository work and research decisions.
- Keep README status and links current.
- Keep every phase on its own Git branch.
- Give each phase a manual GitHub Actions workflow.
- Cache important datasets/artifacts where licensing permits; otherwise cache reproducible retrieval metadata, checksums, and derived subsets.
- Include realistic bid/ask, slippage, brokerage, taxes, exchange/SEBI charges and other applicable transaction costs.
- Search multiple market-data sources where practical: NSE/BSE, open datasets, GitHub, Kaggle, Hugging Face and other legitimate sources.
- For market/trading research, evaluate applicable market regime, volatility, option data, OI/volume, FII/DII, global markets, gold and corporate/news variables where the chosen design can support them.
- Stop at the predefined research phases rather than extending indefinitely.
- Finish with a structured manuscript and supporting tables/figures.

## Non-negotiable modeling safeguard

A cross-expiry options position must not be evaluated using a single terminal spot price for both expiries. The engine must track the near-expiry settlement and the next-expiry settlement separately.

## Data-license safeguard

Do not redistribute proprietary exchange data unless its license/terms permit it. Where raw data cannot be committed, retain source URLs, retrieval dates, checksums, transformation code and derived research summaries instead.
