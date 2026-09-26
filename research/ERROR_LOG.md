# Error log

| Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|
| 2026-09-26 | 3 | Previous implementation only used ATM/-400/+400. | It did not implement the user's full 50-point fallback grid. | Replaced with ATM-first plus every 50-point shift from -500 to +500. |
| 2026-09-26 | 3 | Initial grid extractor omitted shift_points. | Backtest schema validation failed. | Added shift_points to all candidate rows. |
| 2026-09-26 | 3 | Module import path failed in GitHub Actions. | Backtest did not start after data extraction. | Added PYTHONPATH=. to the workflow. |
| 2026-09-26 | 3 | PyArrow concat_tables argument was incompatible with the installed version. | Expanded data extraction stopped. | Removed the unnecessary promotion argument. |
| 2026-09-26 | 3 | Trigger denominator was multiplied by lot size twice in the grid rewrite. | Chart returns were artificially suppressed and initially produced zero qualifying trades. | Passed per-unit long-premium turnover exactly once. |
| 2026-09-26 | 3 | Zero-selection handling assumed an entry_timestamp column in an empty DataFrame. | A diagnostic run failed after valid calculations completed. | Added explicit zero-selection diagnostics and summary fields. |
| 2026-09-26 | 4 | Corrected validation branch lacked the brokerage-sensitivity helper script. | Phase 4 stopped after robustness completed. | Added the helper and reran successfully as 36263760476. |
| 2026-09-26 | 4 | Multiple debugging pushes could start simultaneous long extraction workflows. | Runner time was duplicated. | Added branch concurrency cancellation and explicit cache persistence. |
| 2026-09-27 | 6A | phase-6-manuscript-grid retained an older run_backtest.py using ATM/-400/+400 even though the authoritative full-grid result was already generated on phase-3-strike-grid. | Reproducing the 63-row result from the manuscript branch would silently reproduce the wrong selection rule. | Corrected the manuscript branch code in commit 08a82c499e3344adbb6f5403a73210a28b77d5d4. |
| 2026-09-27 | 6A | The user questioned the aggregate result and requested every losing trade. | Aggregate metrics alone could not show whether losses were fee-driven or genuine economic failures. | Added an artifact-backed loss audit. It found 25/25 losers negative before fees and 0 fee-only flips. |

| 2026-09-27 | 7 | GitHub branch-search action was initially called with incorrect argument names. | No research output was changed; the branch lookup failed before any write. | Repeated with the tool's required repo_name and query fields. |
| 2026-09-27 | 7 | Two repository-write scripts initially contained JavaScript string-syntax errors while embedding GitHub Actions expressions or Markdown backticks. | The intended files were not written in those failed calls. | Rewrote the payloads using line arrays/plain strings and then committed successfully. |
| 2026-09-27 | 7 | The exact historical max-profit/max-loss percentage denominator for the user's chart could not be inferred from Streak public material, while Sensibull documents a margin-based denominator. | Treating the old buy-premium denominator as the platform percentage would be scientifically misleading. | Phase 7 uses INR flatline value as the primary selection score and labels the 2.5% old percentage as a proxy sensitivity. |
