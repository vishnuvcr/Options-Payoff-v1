#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET, load_index, list_nifty_expiry_files, load_option_file,
    last_index_bar_on_date, nifty_lot_size
)
from scripts.run_near_expiry_exit_backtest import CostModel, candidate_metrics

SHIFTS = frozenset(range(-400, 401, 50))
DELAYS = (15, 30, 60, 120)

def args():
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--entry-start-time", default="09:20")
    p.add_argument("--entry-end-time", default="15:29")
    p.add_argument("--slippage-pct", type=float, default=.0025)
    p.add_argument("--brokerage-per-order", type=float, default=20.0)
    return p.parse_args()

def pair(d, expiries):
    xs = [x for x in expiries if x >= d]
    if len(xs) < 2 or (xs[1] - xs[0]).days > 30: return None
    return xs[0], xs[1]

def shift_label(s):
    s = int(s)
    return "ATM" if s == 0 else f"ATM_PLUS_{s}" if s > 0 else f"ATM_MINUS_{abs(s)}"

def build_far_exit_lookup(far_df, exit_ts):
    x = far_df[
        (far_df.trading_date == exit_ts.date()) &
        (far_df.timestamp <= exit_ts) &
        (far_df.option_type.isin(["CE", "PE"]))
    ].sort_values("timestamp")
    x = x.drop_duplicates(["strike", "option_type"], keep="last")
    return {
        (float(r.strike), str(r.option_type)): (float(r.close), r.timestamp)
        for r in x.itertuples(index=False)
    }

def metric_row(r, exit_ts, settlement, far_exit_lookup, model, near, far):
    strike = float(r.strike)
    fc, fc_ts = far_exit_lookup.get((strike, "CE"), (None, None))
    fp, fp_ts = far_exit_lookup.get((strike, "PE"), (None, None))
    base = pd.Series({
        "entry_timestamp": r.timestamp, "entry_date": pd.Timestamp(r.timestamp).date(),
        "near_expiry": near, "far_expiry": far,
        "near_exit_timestamp": exit_ts,
        "far_call_exit_timestamp": fc_ts,
        "far_put_exit_timestamp": fp_ts,
        "candidate_label": shift_label(r.shift_points), "shift_points": int(r.shift_points),
        "strike": strike,
        "near_call_close": float(r.near_call), "near_put_close": float(r.near_put),
        "far_call_close": float(r.far_call), "far_put_close": float(r.far_put),
        "near_settlement": float(settlement), "far_call_exit_close": fc, "far_put_exit_close": fp,
        "near_lot_size": nifty_lot_size(near), "far_lot_size": nifty_lot_size(far),
    })
    m = candidate_metrics(base, model) if fc is not None and fp is not None else None
    d = base.to_dict()
    d["realizable"] = m is not None
    if m: d.update(m)
    else: d.update({"net_pnl_inr": None, "gross_pnl_inr": None, "total_costs": None})
    return d

def select(g):
    g = g[g.flatline_inr > 0].sort_values(["flatline_inr","shift_points"], ascending=[False, True])
    return None if g.empty else g.iloc[0]

def year_run(a):
    start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    sh, sm = map(int, a.entry_start_time.split(":")); eh, em = map(int, a.entry_end_time.split(":"))
    idx = load_index()
    entries = idx[
        (idx.trading_date >= start) & (idx.trading_date <= end) &
        ((idx.timestamp.dt.hour > sh) | ((idx.timestamp.dt.hour == sh) & (idx.timestamp.dt.minute >= sm))) &
        ((idx.timestamp.dt.hour < eh) | ((idx.timestamp.dt.hour == eh) & (idx.timestamp.dt.minute <= em)))
    ][["timestamp","trading_date","close"]].sort_values("timestamp")
    exp_files = list_nifty_expiry_files(start, end + dt.timedelta(days=35))
    exps, fn = [x[0] for x in exp_files], dict(exp_files)
    cycle_ts, need, exits, cycle_exit = defaultdict(list), defaultdict(list), defaultdict(list), {}
    for r in entries.itertuples(index=False):
        p = pair(r.trading_date, exps)
        if not p: continue
        near, far = p; exit_ts, settlement = last_index_bar_on_date(idx, near)
        if exit_ts is None: continue
        cycle_ts[near].append(r.timestamp)
        need[near].append(r.timestamp); need[far].append(r.timestamp)
        exits[near].append(exit_ts); exits[far].append(exit_ts)
        cycle_exit[near] = (exit_ts, settlement)

    prepared = {}
    def load_one(exp):
        ts = need[exp] + exits[exp]
        return exp, load_option_file(exp, fn[exp], timestamp_min=min(ts), timestamp_max=max(ts))
    with ThreadPoolExecutor(max_workers=6) as pool:
        fs = [pool.submit(load_one, e) for e in sorted(set(need) | set(exits))]
        for f in as_completed(fs):
            e, df = f.result(); prepared[e] = df

    spot = entries.set_index("timestamp").close
    model = CostModel(slippage_pct=a.slippage_pct, brokerage_per_order_inr=a.brokerage_per_order)
    details, variants = [], []

    for near in sorted(cycle_ts):
        far = pair(pd.DatetimeIndex(cycle_ts[near])[0].date(), exps)[1]
        n, f = prepared.get(near), prepared.get(far)
        if n is None or f is None: continue
        exit_ts, settlement = cycle_exit[near]
        far_exit_lookup = build_far_exit_lookup(f, exit_ts)
        nce = n[n.option_type.eq("CE")][["timestamp","strike","close"]].rename(columns={"close":"near_call"})
        npe = n[n.option_type.eq("PE")][["timestamp","strike","close"]].rename(columns={"close":"near_put"})
        fce = f[f.option_type.eq("CE")][["timestamp","strike","close"]].rename(columns={"close":"far_call"})
        fpe = f[f.option_type.eq("PE")][["timestamp","strike","close"]].rename(columns={"close":"far_put"})
        surf = nce.merge(npe,on=["timestamp","strike"]).merge(fce,on=["timestamp","strike"]).merge(fpe,on=["timestamp","strike"])
        surf = surf[surf.timestamp.isin(set(cycle_ts[near]))].copy()
        if surf.empty: continue
        surf["spot"] = surf.timestamp.map(spot); surf = surf.dropna(subset=["spot"])
        surf["absdiff"] = (surf.strike-surf.spot).abs()
        atm = surf.sort_values(["timestamp","absdiff","strike"]).drop_duplicates("timestamp")[["timestamp","strike"]].rename(columns={"strike":"atm"})
        surf = surf.merge(atm,on="timestamp"); surf["shift_points"] = surf.strike-surf.atm
        surf = surf[surf.shift_points.isin(SHIFTS)].copy()
        surf["flatline_inr"] = (surf.near_call-surf.near_put-surf.far_call+surf.far_put) * nifty_lot_size(near)
        qn = surf.groupby(["timestamp","shift_points"])[["near_call","near_put","far_call","far_put"]].nunique()
        conflicts = qn.gt(1).any(axis=1).groupby(level=0).sum()
        shifts = surf.groupby("timestamp").shift_points.agg(lambda s: frozenset(pd.to_numeric(s, errors="coerce").dropna().astype(int)))
        positive = surf[surf.flatline_inr > 0].groupby("timestamp").size()
        valid = []
        for ts in sorted(set(cycle_ts[near])):
            if shifts.get(ts, frozenset()) == SHIFTS and conflicts.get(ts,0) == 0 and positive.get(ts,0) > 0:
                valid.append(ts)
        if not valid: continue

        rows = []
        for ts in valid:
            h = surf[surf.timestamp.eq(ts)].drop_duplicates(["timestamp","shift_points"])
            for r in h.itertuples(index=False):
                rows.append(metric_row(r, exit_ts, settlement, far_exit_lookup, model, near, far))
        cands = pd.DataFrame(rows)
        base = select(cands[cands.realizable.eq(True) | cands.net_pnl_inr.notna()])  # identical to frozen selector for complete cycles
        if base is None or pd.isna(base.net_pnl_inr): continue

        def frozen_at(ts):
            return select(cands[cands.timestamp if False else "entry_timestamp"].eq(ts))

        # Same-time and timing variants.
        bt = cands[cands.entry_timestamp.eq(valid[0])]
        choices = {"first_positive": select(bt)}
        choices["second_valid_timestamp"] = select(cands[cands.entry_timestamp.eq(valid[1])]) if len(valid)>1 else None
        for minutes in DELAYS:
            target = pd.Timestamp(valid[0]) + pd.Timedelta(minutes=minutes)
            later = [t for t in valid if t >= target]
            choices[f"delay_{minutes}m"] = select(cands[cands.entry_timestamp.eq(later[0])]) if later else None

        later = cands[cands.entry_timestamp > valid[0]]
        per_ts = []
        for ts, g in later.groupby("entry_timestamp", sort=True):
            z = select(g)
            if z is not None and bool(z.realizable) and pd.notna(z.net_pnl_inr): per_ts.append(z)
        choices["best_later_frozen_selector"] = max(per_ts, key=lambda x: float(x.net_pnl_inr)) if per_ts else None
        real_later = later[later.realizable.eq(True) & later.net_pnl_inr.notna()]
        choices["best_later_any_candidate"] = None if real_later.empty else real_later.sort_values("net_pnl_inr", ascending=False).iloc[0]
        real_same = bt[bt.realizable.eq(True) & bt.net_pnl_inr.notna()]
        choices["same_timestamp_any_candidate"] = None if real_same.empty else real_same.sort_values("net_pnl_inr", ascending=False).iloc[0]

        base_pnl = float(base.net_pnl_inr)
        cycle_variants = []
        for name, row in choices.items():
            pnl = None if row is None or not bool(row.realizable) or pd.isna(row.net_pnl_inr) else float(row.net_pnl_inr)
            variants.append({
                "variant": name, "near_expiry": str(near), "cycle_entry_timestamp": str(valid[0]),
                "entry_timestamp": None if row is None else str(row.entry_timestamp),
                "shift_points": None if row is None else int(row.shift_points),
                "net_pnl_inr": pnl, "baseline_net_pnl_inr": base_pnl, "status": "realized" if pnl is not None else "unrealizable"
            })
            cycle_variants.append((name, row, pnl))
        if base_pnl < 0:
            d = {
                "entry_date": str(pd.Timestamp(valid[0]).date()), "entry_timestamp": str(valid[0]),
                "near_expiry": str(near), "baseline_shift": int(base.shift_points),
                "baseline_strike": float(base.strike), "baseline_flatline_inr": float(base.flatline_inr),
                "baseline_net_pnl_inr": base_pnl, "valid_timestamp_count": len(valid)
            }
            for name, row, pnl in cycle_variants:
                d[f"{name}_entry_timestamp"] = None if row is None else str(row.entry_timestamp)
                d[f"{name}_shift"] = None if row is None else int(row.shift_points)
                d[f"{name}_net_pnl_inr"] = pnl
                d[f"{name}_rescues_loss"] = bool(pnl is not None and pnl > 0)
                d[f"{name}_delta_vs_baseline_inr"] = None if pnl is None else pnl - base_pnl
            details.append(d)

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(details).to_csv(out/"loss_trade_entry_detail.csv", index=False)
    pd.DataFrame(variants).to_csv(out/"entry_variant_trade_rows.csv", index=False)
    (out/"metadata.json").write_text(json.dumps({
        "dataset": DATASET, "start": a.start, "end": a.end,
        "slippage_pct": a.slippage_pct, "brokerage_per_order_inr": a.brokerage_per_order,
        "delays_minutes": list(DELAYS), "losses_in_year": len(details)
    }, indent=2))

if __name__ == "__main__":
    year_run(args())
