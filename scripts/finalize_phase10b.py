#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(".")
res = root / "results" / "phase10b"
summary = (res / "confirmation_summary.csv").read_text()
paired = (res / "paired_confirmation_comparisons.csv").read_text()
promo = json.loads((res / "promotion_screen.json").read_text())

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
status = root / "research" / "STATUS.md"
activity = root / "research" / "ACTIVITY_LOG.md"
errors = root / "research" / "ERROR_LOG.md"
readme = root / "README.md"

status_text = status.read_text()
status_text = status_text.replace("**As of:** 2026-09-29  ", f"**As of:** {stamp}  ", 1)
status_text = status_text.replace("**Active branch:** phase-10A-execution-quality", "**Active branch:** phase-10B-signal-persistence", 1)
status_text = status_text.replace(
    "**Overall status:** Phase 10A COMPLETE — execution-quality / cost-to-edge gate tested; frozen one-strike Phase 9G H1 control retained",
    "**Overall status:** Phase 10B COMPLETE — signal-persistence confirmation tested; frozen one-strike Phase 9G H1 control retained",
    1,
)
status_text += f"""
## Phase 10B — signal persistence

**Status:** COMPLETE — no strategy change adopted.

- [Phase 10B result report](../results/phase10b/PHASE10B_RESULTS.md)
- [Confirmation summary](../results/phase10b/confirmation_summary.csv)
- [Paired confirmation comparisons](../results/phase10b/paired_confirmation_comparisons.csv)
- Promotion screen passed: {promo['passed']}
- Best historical variant considered: {promo['best_variant']}
"""
status.write_text(status_text)

activity_text = activity.read_text()
activity_text += f"""
| {stamp} | 10B | Signal-persistence confirmation | Tested 5, 10, 15 and 30 minute exact-17 positive-surface confirmation windows using the frozen Phase 9G source structure; no confirmation rule was promoted automatically. |
| {stamp} | 10B | Result publication | Published the confirmation summary, paired inference and promotion screen under results/phase10b/. |
"""
activity.write_text(activity_text)

errors_text = errors.read_text()
errors_text += f"""
| {stamp} | 10B | Execution-data limitation | Confirmation analysis uses historical 1-minute close observations and exact-minute confirmation timestamps; it does not claim executable bid/ask fills. | Treat confirmation results as historical research evidence only and require Phase 10G holdout before promotion. | Limitation documented in the Phase 10B report. |
"""
errors.write_text(errors_text)

readme_text = readme.read_text()
marker = "## Phase 10B — signal persistence"
if marker in readme_text:
    readme_text = readme_text[:readme_text.index(marker)]
readme_text += f"""
## Phase 10B — signal persistence

**Complete on {stamp}; no strategy change adopted.**

Phase 10B tested whether a positive exact-17-strike surface must persist for 5, 10, 15 or 30 minutes before entry.

- [Phase 10B result report](results/phase10b/PHASE10B_RESULTS.md)
- [Confirmation summary](results/phase10b/confirmation_summary.csv)
- [Paired inference](results/phase10b/paired_confirmation_comparisons.csv)
- Promotion screen: **{promo['passed']}**
- Best historical variant: **{promo['best_variant']}**

The frozen Phase 9G H1 control remains the research candidate unless Phase 10G chronological holdout supports a predeclared refinement.
"""
readme.write_text(readme_text)
