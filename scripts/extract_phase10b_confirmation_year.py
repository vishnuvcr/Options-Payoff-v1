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


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--scan-audit", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--delay-minutes", type=int, nargs="+", required=True)
    p.add_argument("--download-workers", type=int, default=4)
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def quote_lookup(df, timestamps):
    sub = df[df["timestamp"].isin(timestamps)].copy()
    if sub.empty:
        return {}
    keys = ["timestamp", "strike", "option_type"]
    dup = sub.groupby(keys)["close"].nunique(dropna=False)
    if (dup > 1).any():
        raise RuntimeError(f"Conflicting duplicate option quotes: {dup[dup > 1].index[0]}")
    sub = sub.drop_duplicates(keys, keep="first")
    out = defaultdict(dict)
    for r in sub.itertuples(index=False):
        out[r.timestamp][(float(r.strike), str(r.option_type))] = float(r.close)
    return dict(out)


def exit_lookup(df, timestamps):
    out = {}
    for ts in sorted(timestamps):
        x = df[(df["trading_date"] == ts.date()) & (df["timestamp"] <= ts)].copy()
        if x.empty:
            out[ts] = {}
            continue
        x = x.sort_values("timestamp").drop_duplicates(["strike", "option_type"], keep="last")
        out[ts] = {
            (float(r.strike), str(r.option_type)): (float(r.close), r.timestamp)
            for r in x.itertuples(index=False)
        }
    return out


def surface(near_q, far_q, timestamp, spot, near_expiry):
    near = near_q.get(timestamp, {})
    far = far_q.get(timestamp, {})
    strikes = sorted(set(k[0] for k in near).intersection(k[0] for k in far))
    common = [
        s for s in strikes
        if (s, "CE") in near and (s, "PE") in near
        and (s, "CE") in far and (s, "PE") in far
    ]
    if not common:
        return pd.DataFrame()
    atm = min(common, key=lambda s: (abs(s - float(spot)), s))
    rows = []
    for strike in common:
        shift = strike - atm
        if shift < -400 or shift > 400 or shift % 50 != 0:
            continue
        nc, np = near[(strike, "CE")], near[(strike, "PE")]
        fc, fp = far[(strike, "CE")], far[(strike, "PE")]
        flat = nc - np - fc + fp
        rows.append({
            "strike": float(strike),
            "shift_points": int(shift),
            "near_call": float(nc),
            "near_put": float(np),
            "far_call": float(fc),
            "far_put": float(fp),
            "flatline_per_unit": float(flat),
            "flatline_inr": float(flat) * nifty_lot_size(near_expiry),
        })
    return pd.DataFrame(rows)



OUTPUT_COLUMNS = [
    "entry_timestamp","entry_date","initial_signal_timestamp","confirmation_delay_minutes",
    "spot_at_entry","near_expiry","far_expiry","near_exit_timestamp",
    "far_call_exit_timestamp","far_put_exit_timestamp","candidate_label","shift_points",
    "strike","near_call_close","near_put_close","far_call_close","far_put_close",
    "near_settlement","far_call_exit_close","far_put_exit_close","execution_fidelity",
    "near_lot_size","far_lot_size","flatline_per_unit","flatline_inr",
]
def main():
    args = parse_args()
    delays = sorted(set(args.delay_minutes))
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = pd.read_parquet(args.scan_audit)
    audit["timestamp"] = pd.to_datetime(audit["timestamp"], utc=True)
    audit["near_expiry"] = pd.to_datetime(audit["near_expiry"]).dt.date
    missing = {"near_expiry", "timestamp", "positive_count"} - set(audit.columns)
    if missing:
        raise RuntimeError(f"Authoritative scan audit missing columns: {sorted(missing)}")

    eligible = audit[
        (audit["positive_count"] > 0)
        & (audit["timestamp"].dt.date >= start)
        & (audit["timestamp"].dt.date <= end)
    ].sort_values(["near_expiry", "timestamp"])

    expiry_files = dict(list_nifty_expiry_files(start, end))
    expiry_dates = sorted(expiry_files)
    index_df = load_index()
    index_lookup = index_df.set_index("timestamp")["close"]

    exit_info = {}
    for expiry in sorted(eligible["near_expiry"].unique()):
        ts, settle = last_index_bar_on_date(index_df, expiry)
        if ts is not None:
            exit_info[expiry] = (ts, settle)

    audit_times = {
        e: set(g["timestamp"].tolist())
        for e, g in eligible.groupby("near_expiry")
    }

    candidates = {d: defaultdict(list) for d in delays}
    pairs = {}
    needed_ts = defaultdict(set)
    exit_ts_by_expiry = defaultdict(set)

    for near_expiry, g in eligible.groupby("near_expiry", sort=True):
        pair = expiry_pair(g.iloc[0]["timestamp"].date(), expiry_dates)
        if pair is None:
            continue
        pairs[near_expiry] = pair
        far_expiry = pair[1]
        if near_expiry in exit_info:
            exit_ts_by_expiry[far_expiry].add(exit_info[near_expiry][0])
        for r in g.itertuples(index=False):
            for delay in delays:
                target = r.timestamp + dt.timedelta(minutes=delay)
                if target.date() != r.timestamp.date():
                    continue
                if target not in audit_times.get(near_expiry, set()):
                    continue
                candidates[delay][near_expiry].append((r.timestamp, target))
                needed_ts[near_expiry].update([r.timestamp, target])
                needed_ts[far_expiry].update([r.timestamp, target])

    prepared = {}
    for expiry in sorted(set(needed_ts) | set(exit_ts_by_expiry)):
        if expiry not in expiry_files:
            raise RuntimeError(f"Missing expiry file mapping for {expiry}")
        vals = sorted(needed_ts.get(expiry, set()) | exit_ts_by_expiry.get(expiry, set()))
        tmin, tmax = (min(vals), max(vals)) if vals else (None, None)
        df = load_option_file(expiry, expiry_files[expiry], timestamp_min=tmin, timestamp_max=tmax)
        prepared[expiry] = (
            quote_lookup(df, needed_ts.get(expiry, set())),
            exit_lookup(df, exit_ts_by_expiry.get(expiry, set())),
        )
        del df

    cache = {}
    results = {d: [] for d in delays}

    for delay in delays:
        for near_expiry in sorted(candidates[delay]):
            pair = pairs.get(near_expiry)
            if pair is None or near_expiry not in exit_info:
                continue
            far_expiry = pair[1]
            exit_ts, settlement = exit_info[near_expiry]
            near_q = prepared[near_expiry][0]
            far_q = prepared[far_expiry][0]
            for initial_ts, target in sorted(candidates[delay][near_expiry]):
                spot0 = index_lookup.get(initial_ts)
                spot1 = index_lookup.get(target)
                if pd.isna(spot0) or pd.isna(spot1):
                    continue
                k0 = (near_expiry, far_expiry, initial_ts)
                if k0 not in cache:
                    cache[k0] = surface(near_q, far_q, initial_ts, float(spot0), near_expiry)
                s0 = cache[k0]
                if s0.empty or s0["shift_points"].nunique() != 17 or s0["flatline_inr"].max() <= 0:
                    continue

                k1 = (near_expiry, far_expiry, target)
                if k1 not in cache:
                    cache[k1] = surface(near_q, far_q, target, float(spot1), near_expiry)
                s1 = cache[k1]
                if s1.empty or s1["shift_points"].nunique() != 17:
                    continue
                positive = s1[s1["flatline_inr"] > 0].sort_values(
                    ["flatline_inr", "shift_points"], ascending=[False, True]
                )
                if positive.empty:
                    continue
                win = positive.iloc[0]
                ex = prepared[far_expiry][1].get(exit_ts, {})
                ce = ex.get((float(win["strike"]), "CE"))
                pe = ex.get((float(win["strike"]), "PE"))
                if ce is None or pe is None:
                    continue

                shift = int(win["shift_points"])
                label = "ATM" if shift == 0 else ("ATM_PLUS_%d" % shift if shift > 0 else "ATM_MINUS_%d" % abs(shift))
                results[delay].append({
                    "entry_timestamp": target,
                    "entry_date": target.date(),
                    "initial_signal_timestamp": initial_ts,
                    "confirmation_delay_minutes": delay,
                    "spot_at_entry": float(spot1),
                    "near_expiry": near_expiry,
                    "far_expiry": far_expiry,
                    "near_exit_timestamp": exit_ts,
                    "far_call_exit_timestamp": ce[1],
                    "far_put_exit_timestamp": pe[1],
                    "candidate_label": label,
                    "shift_points": shift,
                    "strike": float(win["strike"]),
                    "near_call_close": float(win["near_call"]),
                    "near_put_close": float(win["near_put"]),
                    "far_call_close": float(win["far_call"]),
                    "far_put_close": float(win["far_put"]),
                    "near_settlement": float(settlement),
                    "far_call_exit_close": float(ce[0]),
                    "far_put_exit_close": float(pe[0]),
                    "execution_fidelity": "1-minute historical close proxy; exact-17 confirmation after a positive initial surface",
                    "near_lot_size": nifty_lot_size(near_expiry),
                    "far_lot_size": nifty_lot_size(far_expiry),
                    "flatline_per_unit": float(win["flatline_per_unit"]),
                    "flatline_inr": float(win["flatline_inr"]),
                })
                break

    for delay in delays:
        out = out_dir / ("phase10b_%dm.csv" % delay)
        df = (pd.DataFrame(results[delay], columns=OUTPUT_COLUMNS).sort_values("entry_timestamp") if results[delay] else pd.DataFrame(columns=OUTPUT_COLUMNS))
        df.to_csv(out, index=False)
        meta = {
            "delay_minutes": delay,
            "eligible_exact17_positive_observations": int(len(eligible)),
            "weekly_cycles_considered": int(eligible["near_expiry"].nunique()),
            "confirmed_cycles": int(df["near_expiry"].nunique()) if not df.empty else 0,
            "selected_trades": int(len(df)),
            "dataset": DATASET,
            "selection_rule": "scan every exact-17 positive timestamp; require exact-17 positive surface at t+delay; enter at confirmation timestamp and select maximum positive flatline",
            "shared_year_process": True,
            "unique_expiry_files_loaded": int(len(prepared)),
        }
        (out_dir / ("phase10b_%dm.metadata.json" % delay)).write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")

    print(json.dumps({
        str(d): {"selected_trades": len(results[d]), "confirmed_cycles": len({x["near_expiry"] for x in results[d]})}
        for d in delays
    }, indent=2))


if __name__ == "__main__":
    main()
