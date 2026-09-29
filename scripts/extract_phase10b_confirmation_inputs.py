#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    expiry_pair,
    last_index_bar_on_date,
    list_nifty_expiry_files,
    load_index,
    load_option_file,
    nifty_lot_size,
)
from scripts.extract_intraday_near_exit_strategy import _last_option_quote


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--scan-audit", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--delay-minutes", type=int, required=True)
    p.add_argument("--download-workers", type=int, default=4)
    p.add_argument("--out", required=True)
    return p.parse_args()


def build_surface(df_near, df_far, timestamp, spot, near_expiry, far_expiry):
    nce = df_near[df_near["option_type"].eq("CE")][["timestamp", "strike", "close"]].rename(columns={"close": "near_call"})
    npe = df_near[df_near["option_type"].eq("PE")][["timestamp", "strike", "close"]].rename(columns={"close": "near_put"})
    fce = df_far[df_far["option_type"].eq("CE")][["timestamp", "strike", "close"]].rename(columns={"close": "far_call"})
    fpe = df_far[df_far["option_type"].eq("PE")][["timestamp", "strike", "close"]].rename(columns={"close": "far_put"})
    surf = (
        nce.merge(npe, on=["timestamp", "strike"], how="inner")
           .merge(fce, on=["timestamp", "strike"], how="inner")
           .merge(fpe, on=["timestamp", "strike"], how="inner")
    )
    surf = surf[surf["timestamp"].eq(timestamp)].copy()
    if surf.empty:
        return surf
    surf["spot"] = float(spot)
    surf["absdiff"] = (surf["strike"] - surf["spot"]).abs()
    atm = surf.sort_values(["absdiff", "strike"]).iloc[0]["strike"]
    surf["atm"] = float(atm)
    surf["shift_points"] = surf["strike"] - surf["atm"]
    surf = surf[
        (surf["shift_points"] >= -400)
        & (surf["shift_points"] <= 400)
        & (surf["shift_points"] % 50 == 0)
    ].copy()
    if surf.duplicated(["strike", "shift_points"]).any():
        for key, g in surf.groupby(["strike", "shift_points"], dropna=False):
            if len(g) > 1:
                if g[["near_call", "near_put", "far_call", "far_put"]].nunique(dropna=False).max() > 1:
                    raise RuntimeError(f"Conflicting duplicate confirmation quote rows at {timestamp}: {key}")
        surf = surf.drop_duplicates(["strike", "shift_points"], keep="first")
    surf["near_expiry"] = near_expiry
    surf["far_expiry"] = far_expiry
    lot = nifty_lot_size(near_expiry)
    surf["flatline_per_unit"] = surf["near_call"] - surf["near_put"] - surf["far_call"] + surf["far_put"]
    surf["flatline_inr"] = surf["flatline_per_unit"] * lot
    return surf


def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    delay = dt.timedelta(minutes=args.delay_minutes)

    audit = pd.read_parquet(args.scan_audit)
    audit["timestamp"] = pd.to_datetime(audit["timestamp"], utc=True)
    audit["near_expiry"] = pd.to_datetime(audit["near_expiry"]).dt.date
    required_audit = {"near_expiry", "timestamp", "positive_count"}
    missing_audit = required_audit - set(audit.columns)
    if missing_audit:
        raise RuntimeError(f"Authoritative scan audit missing columns: {sorted(missing_audit)}")

    # Exact-17 positive observations are the only points at which a
    # confirmation window is allowed to begin. If the window fails, scanning
    # continues to the next exact-17 positive observation: no skip-at-09:20
    # behaviour is introduced.
    eligible = audit[
        (audit["positive_count"] > 0)
        & (audit["timestamp"].dt.date >= start)
        & (audit["timestamp"].dt.date <= end)
    ].copy()
    eligible = eligible.sort_values(["near_expiry", "timestamp"])

    expiry_files = dict(list_nifty_expiry_files(start, end))
    index_df = load_index()
    index_lookup = index_df.set_index("timestamp")["close"]
    expiry_exit = {}
    for expiry in sorted(eligible["near_expiry"].unique()):
        exit_ts, settlement = last_index_bar_on_date(index_df, expiry)
        if exit_ts is None:
            continue
        expiry_exit[expiry] = (exit_ts, settlement)

    # First determine which confirmation timestamps can pass using only the
    # audit. This sharply bounds the option-data read to the actual tests.
    candidates = []
    for expiry, g in eligible.groupby("near_expiry", sort=True):
        for row in g.itertuples(index=False):
            target = row.timestamp + delay
            if target.date() != row.timestamp.date():
                continue
            if target in set(audit.loc[audit["near_expiry"].eq(expiry), "timestamp"]):
                candidates.append((expiry, row.timestamp, target))

    if not candidates:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame().to_csv(args.out, index=False)
        print(json.dumps({
            "delay_minutes": args.delay_minutes,
            "weekly_cycles": int(eligible["near_expiry"].nunique()),
            "selected_trades": 0,
            "confirmed_cycles": 0,
            "dataset": DATASET,
        }, indent=2))
        return

    target_by_expiry = defaultdict(set)
    for expiry, initial_ts, target in candidates:
        target_by_expiry[expiry].add(target)
        far_expiry = expiry_pair(initial_ts.date(), sorted(expiry_files)[0:]) if False else None

    # Map each near expiry to its paired far expiry from the first relevant
    # trading date in that cycle.
    pair_by_near = {}
    for expiry, initial_ts, target in candidates:
        pair_by_near[expiry] = expiry_pair(initial_ts.date(), sorted(expiry_files.keys()))

    needed = set()
    timestamps_by_expiry = defaultdict(set)
    for near_expiry, initial_ts, target in candidates:
        far_expiry = pair_by_near[near_expiry][1]
        needed.update([near_expiry, far_expiry])
        timestamps_by_expiry[near_expiry].add(initial_ts)
        timestamps_by_expiry[near_expiry].add(target)
        timestamps_by_expiry[far_expiry].add(initial_ts)
        timestamps_by_expiry[far_expiry].add(target)
        if near_expiry in expiry_exit:
            timestamps_by_expiry[far_expiry].add(expiry_exit[near_expiry][0])

    prepared = {}
    for expiry in sorted(needed):
        if expiry not in expiry_files:
            raise RuntimeError(f"Missing expiry file mapping for {expiry}")
        ts = sorted(timestamps_by_expiry[expiry])
        prepared[expiry] = load_option_file(
            expiry,
            expiry_files[expiry],
            timestamp_min=min(ts),
            timestamp_max=max(ts),
        )

    selected = []
    # Scan each weekly cycle chronologically. At the first positive exact-17
    # timestamp whose future confirmation surface remains exact-17 and
    # positive, enter at the confirmation timestamp using the normal maximum
    # positive-flatline strike selector.
    for near_expiry, g in eligible.groupby("near_expiry", sort=True):
        cycle = g.sort_values("timestamp")
        pair = pair_by_near.get(near_expiry)
        if pair is None:
            continue
        far_expiry = pair[1]
        near_df = prepared.get(near_expiry)
        far_df = prepared.get(far_expiry)
        if near_df is None or far_df is None:
            continue
        exit_info = expiry_exit.get(near_expiry)
        if exit_info is None:
            continue
        exit_ts, near_settlement = exit_info

        for row in cycle.itertuples(index=False):
            target = row.timestamp + delay
            if target.date() != row.timestamp.date():
                continue
            if target not in index_lookup.index:
                continue

            initial_surf = build_surface(
                near_df, far_df, row.timestamp, index_lookup.loc[row.timestamp],
                near_expiry, far_expiry,
            )
            if initial_surf.empty:
                continue
            if initial_surf["shift_points"].nunique() != 17:
                continue
            if initial_surf["flatline_inr"].max() <= 0:
                continue

            surf = build_surface(
                near_df, far_df, target, index_lookup.loc[target],
                near_expiry, far_expiry,
            )
            if surf.empty:
                raise RuntimeError(f"Audit says exact-17 positive but reconstructed surface is empty: {near_expiry} {target}")
            if surf["shift_points"].nunique() != 17:
                # Missing strikes at confirmation means confirmation failed.
                continue
            if surf["shift_points"].duplicated().any():
                continue

            positive = surf[surf["flatline_inr"] > 0].sort_values(
                ["flatline_inr", "shift_points"], ascending=[False, True]
            )
            if positive.empty:
                raise RuntimeError(f"Audit says positive confirmation but reconstructed surface is non-positive: {near_expiry} {target}")
            win = positive.iloc[0]
            fc, fc_ts = _last_option_quote(far_df, float(win["strike"]), "CE", exit_ts)
            fp, fp_ts = _last_option_quote(far_df, float(win["strike"]), "PE", exit_ts)
            if fc is None or fp is None:
                continue

            lot = nifty_lot_size(near_expiry)
            selected.append({
                "entry_timestamp": target,
                "entry_date": target.date(),
                "initial_signal_timestamp": row.timestamp,
                "confirmation_delay_minutes": args.delay_minutes,
                "spot_at_entry": float(index_lookup.loc[target]),
                "near_expiry": near_expiry,
                "far_expiry": far_expiry,
                "near_exit_timestamp": exit_ts,
                "far_call_exit_timestamp": fc_ts,
                "far_put_exit_timestamp": fp_ts,
                "candidate_label": "ATM" if int(win["shift_points"]) == 0 else (
                    f"ATM_PLUS_{abs(int(win['shift_points']))}" if int(win["shift_points"]) > 0
                    else f"ATM_MINUS_{abs(int(win['shift_points']))}"
                ),
                "shift_points": int(win["shift_points"]),
                "strike": float(win["strike"]),
                "near_call_close": float(win["near_call"]),
                "near_put_close": float(win["near_put"]),
                "far_call_close": float(win["far_call"]),
                "far_put_close": float(win["far_put"]),
                "near_settlement": float(near_settlement),
                "far_call_exit_close": float(fc),
                "far_put_exit_close": float(fp),
                "execution_fidelity": "1-minute historical close proxy; exact-17 confirmation after a positive initial surface",
                "near_lot_size": lot,
                "far_lot_size": nifty_lot_size(far_expiry),
                "flatline_per_unit": float(win["flatline_per_unit"]),
                "flatline_inr": float(win["flatline_inr"]),
            })
            break

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(selected).sort_values("entry_timestamp") if selected else pd.DataFrame()
    df.to_csv(out, index=False)
    meta = {
        "delay_minutes": args.delay_minutes,
        "eligible_exact17_positive_observations": int(len(eligible)),
        "weekly_cycles_considered": int(eligible["near_expiry"].nunique()),
        "confirmed_cycles": int(df["near_expiry"].nunique()) if not df.empty else 0,
        "selected_trades": int(len(df)),
        "dataset": DATASET,
        "selection_rule": "scan every exact-17 positive timestamp; require exact-17 positive surface at t+delay; enter at confirmation timestamp and select maximum positive flatline",
    }
    out.with_suffix(".metadata.json").write_text(json.dumps(meta, indent=2, default=str))
    print(json.dumps(meta, indent=2, default=str))


if __name__ == "__main__":
    main()
