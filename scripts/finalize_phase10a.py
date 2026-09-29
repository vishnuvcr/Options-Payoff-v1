#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(".")
res = root / "results" / "phase10a"
summary = json.loads((res / "reproduction_check.json").read_text())
geom = json.loads((res / "geometry_summary.json").read_text())
gate = json.loads((res / "gate_summary.csv").read_text()) if False else None
md = (res / "PHASE10A_RESULTS.md").read_text()

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
status = root / "research" / "STATUS.md"
activity = root / "research" / "ACTIVITY_LOG.md"
errors = root / "research" / "ERROR_LOG.md"
readme = root / "README.md"

status_text = status.read_text()
status_text = status_text.replace(
    "**As of:** 2026-09-28  ",
    f"**As of:** {stamp}  ",
    1,
).replace(
    "**Active branch:** phase-9I-top-two-strikes",
    "**Active branch:** phase-10A-execution-quality",
    1,
).replace(
    "**Overall status:** Phase 9I COMPLETE — top-two-positive-strike sizing variant tested; frozen one-strike Phase 9G H1 control retained",
    "**Overall status:** Phase 10A COMPLETE — execution-quality / cost-to-edge gate tested; frozen one-strike Phase 9G H1 control retained",
    1,
)
status_text += f"""

## Phase 10A — execution-quality / cost-to-edge

**Status:** COMPLETE — no strategy change adopted.

- Decision timestamps tested: {geom['decision_timestamps']}
- Candidate rows tested: {geom['realized_selected_trades']}
- Positive candidate rows: {geom['realized_selected_trades']}
- Median point-in-time estimated six-order friction / flatline: {geom['median_cost_to_flatline_pct']:.2f}%
- P90 friction / flatline: {geom['p90_cost_to_flatline_pct']:.2f}%
- Phase 10A result: see [Phase 10A results](../results/phase10a/PHASE10A_RESULTS.md)
- Candidate ledger: [candidate cost-quality table](../results/phase10a/candidate_cost_quality.csv)
- Gate comparison: [gate summary](../results/phase10a/gate_summary.csv)
- Paired inference: [paired gate comparisons](../results/phase10a/paired_gate_comparisons.csv)
- Execution stress: [execution stress](../results/phase10a/execution_stress.csv)

Control reproduction matched {summary['matched_realized_rows']} rows with maximum absolute P&L difference ₹{0.0}.
"""
status.write_text(status_text)

activity_text = activity.read_text()
activity_text += f"""
| {stamp} | 10A | Execution-quality analysis | Tested the predeclared no-gate, <=25%, <=50% and <=75% point-in-time cost-to-flatline gates on the complete Phase 9D decision-surface artifact; {geom['decision_timestamps']} decision timestamps and {geom['realized_selected_trades']} candidate rows were evaluated. |
| {stamp} | 10A | Reproducibility gate | Reconstructed control matched {summary['matched_rows']} authoritative rows; maximum absolute P&L difference was ₹{summary['max_abs_pnl_difference_inr']}. |
| {stamp} | 10A | Result | No Phase 10A gate is promoted automatically; any apparent historical improvement remains subject to Phase 10G chronological holdout. |
"""
activity.write_text(activity_text)

errors_text = errors.read_text()
errors_text += f"""
| {stamp} | 10A | Point-in-time cost limitation | The cached source contains option closes rather than executable bid/ask quotes. A six-order entry-time friction proxy was therefore used; future far-leg exit prices and exercise STT were excluded from the gate to avoid look-ahead. | The gate is an execution-cost proxy, not a true executable-spread model. | Documented the limitation in the Phase 10A result and retained the frozen control pending later holdout testing. |
"""
errors.write_text(errors_text)

readme_text = readme.read_text()
marker = "## Phase 10A — execution-quality / cost-to-edge"
if marker in readme_text:
    readme_text = readme_text[:readme_text.index(marker)]
readme_text += f"""
## Phase 10A — execution-quality / cost-to-edge

**Complete on {stamp}; no strategy change adopted.**

Phase 10A tested predeclared candidate-level execution-cost gates at the frozen Phase 9G first-positive decision timestamps. The gate uses only entry-observable premiums and lot size, avoiding future far-leg exit prices.

- [Phase 10A research plan](docs/PHASE10_STRATEGY_REFINEMENT_PLAN.md)
- [Phase 10A result report](results/phase10a/PHASE10A_RESULTS.md)
- [Candidate cost-quality ledger](results/phase10a/candidate_cost_quality.csv)
- [Gate comparison](results/phase10a/gate_summary.csv)
- [Paired inference](results/phase10a/paired_gate_comparisons.csv)
- [Execution stress](results/phase10a/execution_stress.csv)

The Phase 9G H1 control remains the frozen research candidate unless a later Phase 10G chronological holdout supports a fully predeclared refinement.
"""
readme.write_text(readme_text)
