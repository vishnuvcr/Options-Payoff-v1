#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    list_nifty_expiry_files,
    load_index,
    load_option_file,
    nifty_lot_size,
)

GRID = list(range(-400, 401, 50))

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2026-01-01")
    p.add_argument("--end", default="2026-12-31")
    p.add_argument("--far-ranks", default="2,3")
    p.add_argument("--sample-times", default="09:20,10:00,12:00,15:00")
    p.add_argument("--out-dir", default="results/phase9g_h2_h3_data_audit")
    return p.parse_args()

def parse_hm(s):
    h, m = [int(x) for x in s.split(":")]
    return h, m

def expiry_pair(entry_date, expiries, rank):
    xs = [x for x in expiries if x >= entry_date]
    if len(xs) <= rank:
        return None
    near, far = xs[0], xs[rank]
    if (far - near).days > 30:
        return None
    return near, far

def grid_stats(near_df, far_df, ts, spot):
    n = near_df[(near_df["timestamp"] == ts) & near_df["option_type"].isin(["CE","PE"])]
    f = far_df[(far_df["timestamp"] == ts) & far_df["option_type"].isin(["CE","PE"])]
    n_both = set(n.groupby("strike")["option_type"].nunique().loc[lambda x: x >= 2].index.astype(float))
    f_both = set(f.groupby("strike")["option_type"].nunique().loc[lambda x: x >= 2].index.astype(float))
    common = sorted(n_both & f_both)
    if not common:
        return {
            "near_both_strikes": len(n_both),
            "far_both_strikes": len(f_both),
            "common_both_strikes": 0,
            "atm": None,
            "grid_present_count": 0,
            "grid_present_shifts": [],
        }
    atm = min(common, key=lambda k: (abs(k - spot), k))
    shift_set = {int(round(k - atm)) for k in common if -400 <= k - atm <= 400 and abs((k - atm) % 50) < 1e-9}
    return {
        "near_both_strikes": len(n_both),
        "far_both_strikes": len(f_both),
        "common_both_strikes": len(common),
        "atm": atm,
        "grid_present_count": len(set(GRID) & shift_set),
        "grid_present_shifts": sorted(set(GRID) & shift_set),
    }

def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    ranks = [int(x) for x in args.far_ranks.split(",") if x.strip()]
    sample_hm = [parse_hm(x) for x in args.sample_times.split(",")]

    index_df = load_index()
    index_df = index_df[(index_df["trading_date"] >= start) & (index_df["trading_date"] <= end)].copy()
    expiry_files = list_nifty_expiry_files(start, end + dt.timedelta(days=35))
    expiry_dates = [x[0] for x in expiry_files]
    filename_by_expiry = dict(expiry_files)

    cycle_dates = sorted(index_df["trading_date"].drop_duplicates().tolist())
    selected_cycle_dates = {}
    for rank in ranks:
        seen = []
        for d in cycle_dates:
            pair = expiry_pair(d, expiry_dates, rank)
            if pair is None:
                continue
            if pair[0] not in seen:
                seen.append(pair[0])
            if len(seen) >= 8:
                break
        selected_cycle_dates[rank] = [d for d in cycle_dates if expiry_pair(d, expiry_dates, rank) and expiry_pair(d, expiry_dates, rank)[0] in set(seen)]

    all_expiries = sorted({e for rank in ranks for d in selected_cycle_dates[rank] for e in expiry_pair(d, expiry_dates, rank)})
    file_summary = []
    loaded = {}
    for expiry in all_expiries:
        filename = filename_by_expiry[expiry]
        df = load_option_file(expiry, filename)
        loaded[expiry] = df
        file_summary.append({
            "expiry": expiry,
            "filename": filename,
            "rows": int(len(df)),
            "min_timestamp": str(df["timestamp"].min()) if not df.empty else None,
            "max_timestamp": str(df["timestamp"].max()) if not df.empty else None,
            "unique_timestamps": int(df["timestamp"].nunique()) if not df.empty else 0,
            "unique_strikes": int(df["strike"].nunique()) if not df.empty else 0,
            "ce_rows": int((df["option_type"] == "CE").sum()),
            "pe_rows": int((df["option_type"] == "PE").sum()),
            "lot_size": int(nifty_lot_size(expiry)),
        })

    sample_rows = []
    for rank in ranks:
        for d in selected_cycle_dates[rank]:
            pair = expiry_pair(d, expiry_dates, rank)
            if pair is None:
                continue
            near, far = pair
            day = index_df[index_df["trading_date"] == d].sort_values("timestamp")
            for hh, mm in sample_hm:
                x = day[(day["timestamp"].dt.hour == hh) & (day["timestamp"].dt.minute == mm)]
                if x.empty:
                    continue
                row = x.iloc[0]
                ts = row["timestamp"]
                stats = grid_stats(loaded[near], loaded[far], ts, float(row["close"]))
                sample_rows.append({
                    "far_rank": rank,
                    "entry_date": str(d),
                    "entry_timestamp": str(ts),
                    "near_expiry": near,
                    "far_expiry": far,
                    "spot": float(row["close"]),
                    **stats,
                })

    sample_df = pd.DataFrame(sample_rows)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(file_summary).to_csv(out / "expiry_file_summary.csv", index=False)
    sample_df.to_csv(out / "sample_timestamp_coverage.csv", index=False)

    rank_summary = []
    for rank, g in sample_df.groupby("far_rank") if not sample_df.empty else []:
        rank_summary.append({
            "far_rank": int(rank),
            "samples": int(len(g)),
            "mean_common_both_strikes": float(g["common_both_strikes"].mean()),
            "mean_grid_present_count": float(g["grid_present_count"].mean()),
            "samples_with_any_common": int((g["common_both_strikes"] > 0).sum()),
            "samples_with_all_17": int((g["grid_present_count"] == 17).sum()),
        })
    pd.DataFrame(rank_summary).to_csv(out / "rank_summary.csv", index=False)

    meta = {
        "dataset": DATASET,
        "start": args.start,
        "end": args.end,
        "far_ranks": ranks,
        "sample_times": args.sample_times,
        "sample_cycle_limit_per_rank": 8,
        "purpose": "Diagnose why Phase 9G H2/H3 produce scan rows but zero usable decision surfaces under the exact 17-strike rule.",
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"metadata": meta, "rank_summary": rank_summary}, indent=2, default=str))

if __name__ == "__main__":
    main()
