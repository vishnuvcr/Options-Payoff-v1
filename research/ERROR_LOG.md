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
