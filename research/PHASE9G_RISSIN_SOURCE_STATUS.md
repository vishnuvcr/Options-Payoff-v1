# Phase 9G Rissin source validation\n\nSeparate source-validation branch for testing whether the rissin/nse-options-intraday dataset provides pre-entry far-expiry intraday quotes and the exact 17-strike grid needed by the frozen strategy. No performance result is produced by this branch.\n

### Tooling correction — 2026-09-27
Run 1 failed because the validator compared an Arrow timezone-aware timestamp column with string filter bounds. This was a validation-code defect; no source-coverage conclusion was drawn. The filter now uses the dataset's date column with a typed Arrow scalar.
