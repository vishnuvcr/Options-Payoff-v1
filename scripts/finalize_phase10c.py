#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(".")
res = root / "results" / "phase10c"
promo = json.loads((res / "promotion_screen.json").read_text())
summary = (res / "scenario_selector_summary.csv").read_text()
paired = (res / "paired_scenario_comparisons.csv").read_text()

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
status = root / "research" / "STATUS.md"
activity = root / "research" / "ACTIVITY_LOG.md"
errors = root / "research" / "ERROR_LOG.md"
readme = root / "README.md"

status_text = status.read_text()
status_text = status_text.replace("**As of:** 2026-09-29  ", f"**As of:** {stamp}  ", 1)
status_text = status_text.replace("**Active branch:** phase-10B-signal-persistence", "**Active branch:** phase-10C-scenario-aware-selection", 1)
status_text = status_text.replace(
    "**Overall status:** Phase 10B COMPLETE — signal-persistence confirmation tested; frozen one-strike Phase 9G H1 control retained",
    "**Overall status:** Phase 10C COMPLETE — scenario-aware strike selection tested; frozen one-strike Phase 9G H1 control retained",
    1,
)
status_text += f"""

## Phase 10C — scenario-aware strike selection

**Status:** COMPLETE — no strategy change adopted.

- [Phase 10C result report](../results/phase10c/PHASE10C_RESULTS.md)
- [Scenario selector summary](../results/phase10c/scenario_selector_summary.csv)
- [Paired comparisons](../results/phase10c/paired_scenario_comparisons.csv)
- [Candidate scenario scores](../results/phase10c/candidate_scenario_scores.csv)
- Promotion screen passed: {promo['passed']}
- Best historical variant: {promo['best_variant']}
"""
status.write_text(status_text)

activity_text = activity.read_text()
activity_text += f"""
| {stamp} | 10C | Scenario-aware selector | Evaluated the predeclared 15-state (-2/-1/0/+1/+2% spot × -5/0/+5 vol-point far-IV) grid across positive/all-green 17-strike candidates; no future realized P&L was used in selection. |
| {stamp} | 10C | Result publication | Published full candidate scenario scores, selector backtests, paired inference and promotion screen under results/phase10c/. |
"""
activity.write_text(activity_text)

errors_text = errors.read_text()
errors_text += f"""
| {stamp} | 10C | Model-based scenario limitation | Far-leg IVs are reconstructed from entry premiums with Black–Scholes r=0/q=0; they are not exchange-published executable IVs. | Treat scenario rankings as model-based research evidence and require Phase 10G holdout before any adoption. | Limitation documented in Phase 10C report. |
"""
errors.write_text(errors_text)

readme_text = readme.read_text()
marker = "## Phase 10C — scenario-aware strike selection"
if marker in readme_text:
    readme_text = readme_text[:readme_text.index(marker)]
readme_text += f"""
## Phase 10C — scenario-aware strike selection

**Complete on {stamp}; no strategy change adopted.**

Phase 10C tested fixed point-in-time scenario ranking across the 17-strike grid:

- spot shocks: -2%, -1%, 0%, +1%, +2%;
- far-leg IV shocks: -5, 0, +5 volatility points;
- 15 scenarios per eligible strike;
- candidate eligibility remains positive/all-green static flatline.

- [Phase 10C result report](results/phase10c/PHASE10C_RESULTS.md)
- [Scenario selector summary](results/phase10c/scenario_selector_summary.csv)
- [Paired inference](results/phase10c/paired_scenario_comparisons.csv)
- [Candidate scenario scores](results/phase10c/candidate_scenario_scores.csv)
- Promotion screen: **{promo['passed']}**
- Best historical variant: **{promo['best_variant']}**

The frozen Phase 9G H1 control remains the research candidate unless Phase 10G chronological holdout supports a predeclared refinement.
"""
readme.write_text(readme_text)
