# Phase 9G Rissin source validation\n\nSeparate source-validation branch for testing whether the rissin/nse-options-intraday dataset provides pre-entry far-expiry intraday quotes and the exact 17-strike grid needed by the frozen strategy. No performance result is produced by this branch.\n

### Tooling correction — 2026-09-27
Run 1 failed because the validator compared an Arrow timezone-aware timestamp column with string filter bounds. This was a validation-code defect; no source-coverage conclusion was drawn. The filter now uses the dataset's date column with a typed Arrow scalar.

### Tooling correction 2 — 2026-09-27
The first automated patch encoded a literal backslash-n in the Python import line, causing a SyntaxError before any data were read. This was a repository-editing defect only; no source inference was accepted. The source-validation branch is being rerun from a corrected file.
