#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

EXPECTED_SHIFTS = set(range(-400, 401, 50))
KEYS = ["near_expiry", "timestamp"]
QUOTE_COLS = ["near_call", "near_put", "far_call", "far_put"]

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ap.add_argument("--selected", required=True)
ap.add_argument("--surface", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

audit = pd.read_parquet(args.audit)
selected = pd.read_parquet(args.selected)
surface = pd.read_parquet(args.surface)

required_a = {"near_expiry", "timestamp", "positive_count", "decision"}
required_s = {"near_expiry", "entry_timestamp"}
required_surface = {"near_expiry", "timestamp", "shift_points", *QUOTE_COLS}

missing_a = required_a - set(audit.columns)
missing_s = required_s - set(selected.columns)
missing_surface = required_surface - set(surface.columns)
if missing_a or missing_s or missing_surface:
    raise SystemExit(
        f"Missing columns audit={sorted(missing_a)} "
        f"selected={sorted(missing_s)} surface={sorted(missing_surface)}"
    )

audit["near_expiry"] = audit["near_expiry"].astype(str)
audit["timestamp"] = pd.to_datetime(audit["timestamp"], errors="coerce")
selected["near_expiry"] = selected["near_expiry"].astype(str)
selected["entry_timestamp"] = pd.to_datetime(selected["entry_timestamp"], errors="coerce")
surface["near_expiry"] = surface["near_expiry"].astype(str)
surface["timestamp"] = pd.to_datetime(surface["timestamp"], errors="coerce")
surface["shift_points"] = pd.to_numeric(surface["shift_points"], errors="coerce")

decision = (
    selected[["near_expiry", "entry_timestamp"]]
    .drop_duplicates()
    .rename(columns={"entry_timestamp": "timestamp"})
)

matched = decision.merge(
    audit[KEYS + ["positive_count", "decision"]],
    on=KEYS,
    how="left",
    validate="one_to_one",
)
if matched["decision"].isna().any():
    raise SystemExit("Selected timestamps could not be matched to the scan audit.")

surface_selected = surface.merge(decision, on=KEYS, how="inner")

shift_stats = (
    surface_selected.groupby(KEYS)["shift_points"]
    .nunique()
    .rename("unique_shift_count")
    .reset_index()
)

def missing_shifts(group: pd.DataFrame) -> str:
    got = {int(x) for x in group["shift_points"].dropna().tolist()}
    missing = sorted(EXPECTED_SHIFTS - got)
    extra = sorted(got - EXPECTED_SHIFTS)
    return json.dumps({"missing": missing, "extra": extra}, separators=(",", ":"))

shift_set_stats = (
    surface_selected.groupby(KEYS, group_keys=False)
    .apply(lambda g: pd.Series({"shift_set_issue": missing_shifts(g)}), include_groups=False)
    .reset_index()
)

quote_nunique = (
    surface_selected.groupby(KEYS + ["shift_points"])[QUOTE_COLS]
    .nunique(dropna=False)
)
conflicting = (
    quote_nunique.gt(1)
    .any(axis=1)
    .groupby(level=KEYS)
    .sum()
    .rename("conflicting_shift_count")
    .reset_index()
)

checks = (
    matched.merge(shift_stats, on=KEYS, how="left")
    .merge(shift_set_stats, on=KEYS, how="left")
    .merge(conflicting, on=KEYS, how="left")
)
checks["conflicting_shift_count"] = checks["conflicting_shift_count"].fillna(0).astype(int)
checks["unique_shift_count"] = checks["unique_shift_count"].fillna(0).astype(int)
checks["shift_set_issue"] = checks["shift_set_issue"].fillna(
    json.dumps({"missing": sorted(EXPECTED_SHIFTS), "extra": []}, separators=(",", ":"))
)

def passes(row: pd.Series) -> bool:
    try:
        issue = json.loads(row["shift_set_issue"])
    except Exception:
        return False
    return (
        row["unique_shift_count"] == 17
        and issue["missing"] == []
        and issue["extra"] == []
        and row["conflicting_shift_count"] == 0
    )

checks["strict_complete"] = checks.apply(passes, axis=1)

legacy_note = {
    "scan_audit_has_unique_shift_fields": "candidate_shift_count" in audit.columns,
    "legacy_candidate_count_max": int(audit["candidate_count"].max())
    if "candidate_count" in audit.columns and not audit.empty
    else None,
    "positive_scan_timestamps": int((audit["positive_count"] > 0).sum()),
}

summary = {
    "selected_trades": int(len(checks)),
    "selected_timestamps_strict_complete": int(checks["strict_complete"].sum()),
    "selected_timestamps_strict_incomplete": int((~checks["strict_complete"]).sum()),
    "all_selected_timestamps_pass_strict_completeness": bool(checks["strict_complete"].all()),
    "selected_timestamps_with_17_unique_shifts": int((checks["unique_shift_count"] == 17).sum()),
    "selected_timestamps_with_conflicting_quotes": int((checks["conflicting_shift_count"] > 0).sum()),
    **legacy_note,
}

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
(out / "h1_17_strike_completeness.json").write_text(json.dumps(summary, indent=2))
checks.to_csv(out / "h1_selected_timestamp_completeness.csv", index=False)
audit[audit["positive_count"] > 0].to_csv(
    out / "h1_positive_scan_timestamps_descriptive.csv", index=False
)

print(json.dumps(summary, indent=2))
if not summary["all_selected_timestamps_pass_strict_completeness"]:
    raise SystemExit(
        "FAIL: at least one authoritative H1 selected timestamp did not contain "
        "the exact 17-strike set or contained conflicting duplicate quotes."
    )
