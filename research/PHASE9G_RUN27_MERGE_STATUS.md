# Phase 9G run-27 final merge status

This branch exists solely to merge the completed yearly artifacts from frozen run 36313815542 using the corrected empty-ledger handling. It does not reconstruct market data. The six-artifact verification is mandatory before pooled inference.

## 2026-09-27 merge-repair checkpoint

Run 36313815542 completed all six yearly reconstruction jobs successfully; its pooled merge failed only because the frozen merge script attempted to read an empty `intraday_incomplete_selected_trades.csv` with `pd.read_csv`, raising `pandas.errors.EmptyDataError`. This is an aggregation/tooling defect, not a market-data reconstruction failure.

The corrected merger from the Rissin branch is now being promoted to this run-27 merge branch. It treats zero-byte incomplete ledgers as zero rows and catches `EmptyDataError`. The yearly artifacts remain frozen and will not be regenerated.


## Final accepted state

Corrected merge workflow **36320697995** completed successfully and produced artifact **10932342487**. All six yearly artifacts from frozen run 36313815542 were verified before aggregation. The accepted primary H1 result is 131 complete trades and ₹71,868.76 net P&L at 0.25% slippage and ₹20/order.

The earlier merge failure was caused solely by a zero-byte incomplete-selected-trades CSV being passed to pandas. Empty-ledger handling is now hardened in the merger and recorded in research/ERROR_LOG.md.
