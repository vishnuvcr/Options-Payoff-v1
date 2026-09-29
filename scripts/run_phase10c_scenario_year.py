#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import ndtr

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    expiry_pair,
    last_index_bar_on_date,
    list_nifty_expiry_files,
    load_index,
    load_option_file,
    nifty_lot_size,
)
from scripts.run_near_expiry_exit_backtest import six_transaction_costs
from src.costs import CostModel, executed_premium, four_leg_entry_cashflow


SPOT_SHOCKS = (-0.02, -0.01, 0.0, 0.01, 0.02)
IV_SHOCK_POINTS = (-5.0, 0.0, 5.0)
SCENARIO_COLUMNS = [
    "scenario_spot_shock_pct",
    "scenario_far_iv_shock_points",
    "scenario_net_pnl_inr",
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--decision-surface", required=True)
    p.add_argument("--selected", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--download-workers", type=int, default=4)
    p.add_argument("--slippage-pct", type=float, default=0.0025)
    p.add_argument("--brokerage-per-order", type=float, default=20.0)
    return p.parse_args()


def norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def bs_price(S, K, T, r, sigma, cp):
    if T <= 0:
        return max(S - K, 0.0) if cp == "C" else max(K - S, 0.0)
    if sigma <= 0:
        return max(S - K, 0.0) if cp == "C" else max(K - S, 0.0)
    sq = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sq)
    d2 = d1 - sigma * sq
    df = math.exp(-r * T)
    if cp == "C":
        return S * ndtr(d1) - K * df * ndtr(d2)
    return K * df * ndtr(-d2) - S * ndtr(-d1)


def implied_vol(price, S, K, T, cp):
    if not np.isfinite(price) or price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return np.nan
    intrinsic = max(S - K, 0.0) if cp == "C" else max(K - S, 0.0)
    upper = S if cp == "C" else K
    if price < intrinsic - 1e-6 or price > upper + 1e-6:
        return np.nan

    def f(vol):
        return bs_price(S, K, T, 0.0, vol, cp) - price

    lo, hi = 1e-6, 5.0
    try:
        flo, fhi = f(lo), f(hi)
        if flo * fhi > 0:
            return np.nan
        return float(brentq(f, lo, hi, maxiter=100))
    except Exception:
        return np.nan


def expiry_timestamp(expiry):
    return pd.Timestamp(expiry).tz_localize("Asia/Kolkata") + pd.Timedelta(
        hours=15, minutes=30
    )


def build_exit_lookup(df, exit_timestamps):
    out = {}
    for ts in sorted(exit_timestamps):
        x = df[(df["trading_date"] == ts.date()) & (df["timestamp"] <= ts)].copy()
        if x.empty:
            out[ts] = {}
            continue
        x = x.sort_values("timestamp").drop_duplicates(
            ["strike", "option_type"], keep="last"
        )
        out[ts] = {
            (float(r.strike), str(r.option_type)): (float(r.close), r.timestamp)
            for r in x.itertuples(index=False)
        }
    return out


def scenario_net(row, spot_scenario, far_iv_ce, far_iv_pe, t_far, exit_date, model):
    lot = int(row.near_lot_size)
    K = float(row.strike)
    entry = four_leg_entry_cashflow(
        float(row.near_call),
        float(row.near_put),
        float(row.far_call),
        float(row.far_put),
        slippage_pct=model.slippage_pct,
    )

    near_pair = -max(spot_scenario - K, 0.0) + max(K - spot_scenario, 0.0)

    far_call_mid = bs_price(spot_scenario, K, t_far, 0.0, far_iv_ce, "C")
    far_put_mid = bs_price(spot_scenario, K, t_far, 0.0, far_iv_pe, "P")
    far_call_exit = executed_premium(far_call_mid, -1, model.slippage_pct)
    far_put_exit = executed_premium(far_put_mid, +1, model.slippage_pct)

    gross_per_unit = (
        entry["entry_cashflow_per_unit"]
        + near_pair
        + far_call_exit
        - far_put_exit
    )

    near_put_intrinsic = max(K - spot_scenario, 0.0)
    costs = six_transaction_costs(
        pd.Timestamp(row.entry_timestamp).date(),
        exit_date,
        entry,
        far_call_exit,
        far_put_exit,
        near_put_intrinsic,
        lot,
        model,
    )
    return float(gross_per_unit * lot - costs["total_costs"])


def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model = CostModel(
        slippage_pct=args.slippage_pct,
        brokerage_per_order_inr=args.brokerage_per_order,
    )

    surface = pd.read_parquet(args.decision_surface)
    selected = pd.read_csv(args.selected)
    for df in (surface, selected):
        df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"] if "entry_timestamp" in df.columns else df["timestamp"], utc=True)
    surface["timestamp"] = pd.to_datetime(surface["timestamp"], utc=True)
    surface["near_expiry"] = pd.to_datetime(surface["near_expiry"]).dt.date
    surface["far_expiry"] = pd.to_datetime(surface["far_expiry"]).dt.date
    selected["near_expiry"] = pd.to_datetime(selected["near_expiry"]).dt.date
    selected["far_expiry"] = pd.to_datetime(selected["far_expiry"]).dt.date
    selected["shift_points"] = pd.to_numeric(selected["shift_points"]).astype(int)

    if len(selected) != 131:
        raise RuntimeError(f"Frozen Phase 9G selected ledger must contain 131 complete rows, found {len(selected)}")

    index_df = load_index()
    index_lookup = index_df.set_index("timestamp")["close"]

    selected = selected.sort_values("entry_timestamp").copy()
    decision_keys = list(
        selected[["near_expiry", "entry_timestamp", "far_expiry"]].itertuples(index=False, name=None)
    )

    # Validate the exact decision-surface geometry used by the frozen control.
    cycle_candidates = {}
    for near_expiry, entry_ts, far_expiry in decision_keys:
        group = surface[
            (surface["near_expiry"] == near_expiry)
            & (surface["far_expiry"] == far_expiry)
            & (surface["timestamp"] == entry_ts)
        ].copy()
        group = group[group["shift_points"].between(-400, 400)]
        group = group[(group["shift_points"] % 50) == 0]
        if len(group) != 17 or group["shift_points"].nunique() != 17:
            raise RuntimeError(
                f"Exact-17 decision surface missing for cycle {near_expiry} at {entry_ts}: "
                f"rows={len(group)}, unique_shifts={group['shift_points'].nunique()}"
            )
        cycle_candidates[near_expiry] = group.sort_values("shift_points")

    expiry_files = dict(list_nifty_expiry_files(start, end))
    needed = defaultdict(set)
    far_expiry_to_exit_ts = defaultdict(set)
    exit_info = {}

    for near_expiry, entry_ts, far_expiry in decision_keys:
        exit_ts, settlement = last_index_bar_on_date(index_df, near_expiry)
        if exit_ts is None or settlement is None:
            raise RuntimeError(f"Missing near-expiry index close for {near_expiry}")
        exit_info[near_expiry] = (exit_ts, settlement)
        far_expiry_to_exit_ts[far_expiry].add(exit_ts)

    far_paths = {}
    def download_one(expiry):
        if expiry not in expiry_files:
            raise RuntimeError(f"Missing far-expiry file mapping for {expiry}")
        return expiry, expiry_files[expiry]

    with ThreadPoolExecutor(max_workers=max(1, min(args.download_workers, 8))) as ex:
        futures = [ex.submit(download_one, expiry) for expiry in sorted(far_expiry_to_exit_ts)]
        for fut in as_completed(futures):
            expiry, filename = fut.result()
            far_paths[expiry] = filename

    far_exit = {}
    for expiry in sorted(far_paths):
        timestamps = sorted(far_expiry_to_exit_ts[expiry])
        df = load_option_file(
            expiry,
            far_paths[expiry],
            timestamp_min=min(timestamps),
            timestamp_max=max(timestamps),
        )
        far_exit[expiry] = build_exit_lookup(df, set(timestamps))
        del df

    scenario_rows = []
    selector_rows = {
        "control": [],
        "median": [],
        "p10": [],
        "worst": [],
    }

    for near_expiry, entry_ts, far_expiry in decision_keys:
        candidates = cycle_candidates[near_expiry].copy()
        spot = index_lookup.get(entry_ts)
        if pd.isna(spot):
            raise RuntimeError(f"Missing entry spot for {near_expiry} at {entry_ts}")
        exit_ts, _settlement = exit_info[near_expiry]
        far_exit_map = far_exit[far_expiry].get(exit_ts, {})

        candidate_records = []
        for r in candidates.itertuples(index=False):
            K = float(r.strike)
            flatline = float(r.flatline_inr)
            if not np.isfinite(flatline) or flatline <= 0:
                continue

            far_expiry_ts = expiry_timestamp(far_expiry)
            entry_local = entry_ts.tz_convert("Asia/Kolkata")
            T_entry_far = max(
                (far_expiry_ts - entry_local).total_seconds() / (365.0 * 24 * 3600),
                1e-8,
            )
            iv_ce = implied_vol(float(r.far_call), float(spot), K, T_entry_far, "C")
            iv_pe = implied_vol(float(r.far_put), float(spot), K, T_entry_far, "P")
            if not (np.isfinite(iv_ce) and np.isfinite(iv_pe)):
                continue

            T_far_at_exit = (
                far_expiry_ts - exit_ts
            ).total_seconds() / (365.0 * 24 * 3600)
            if T_far_at_exit <= 0:
                continue

            nets = []
            for spot_shock in SPOT_SHOCKS:
                S_scn = float(spot) * (1.0 + spot_shock)
                for iv_shock in IV_SHOCK_POINTS:
                    sigma_ce = max(iv_ce + iv_shock / 100.0, 1e-6)
                    sigma_pe = max(iv_pe + iv_shock / 100.0, 1e-6)
                    pnl = scenario_net(
                        r,
                        S_scn,
                        sigma_ce,
                        sigma_pe,
                        T_far_at_exit,
                        exit_ts.date(),
                        model,
                    )
                    nets.append((spot_shock, iv_shock, pnl))

            vals = np.array([x[2] for x in nets], dtype=float)
            if len(vals) != 15 or not np.isfinite(vals).all():
                continue

            rec = {
                "near_expiry": near_expiry,
                "far_expiry": far_expiry,
                "entry_timestamp": entry_ts,
                "spot_at_entry": float(spot),
                "strike": K,
                "shift_points": int(r.shift_points),
                "candidate_label": "ATM"
                if int(r.shift_points) == 0
                else (
                    f"ATM_PLUS_{abs(int(r.shift_points))}"
                    if int(r.shift_points) > 0
                    else f"ATM_MINUS_{abs(int(r.shift_points))}"
                ),
                "near_call_close": float(r.near_call),
                "near_put_close": float(r.near_put),
                "far_call_close": float(r.far_call),
                "far_put_close": float(r.far_put),
                "flatline_inr": flatline,
                "flatline_per_unit": float(r.flatline_per_unit),
                "far_call_iv": float(iv_ce),
                "far_put_iv": float(iv_pe),
                "scenario_median_inr": float(np.median(vals)),
                "scenario_p10_inr": float(np.quantile(vals, 0.10)),
                "scenario_worst_inr": float(np.min(vals)),
                "scenario_mean_inr": float(np.mean(vals)),
                "scenario_sd_inr": float(np.std(vals)),
            }
            candidate_records.append(rec)

            for ss, vv, pnl in nets:
                scenario_rows.append({
                    **{k: rec[k] for k in (
                        "near_expiry","far_expiry","entry_timestamp","spot_at_entry",
                        "strike","shift_points","candidate_label","flatline_inr",
                        "far_call_iv","far_put_iv"
                    )},
                    "scenario_spot_shock_pct": ss,
                    "scenario_far_iv_shock_points": vv,
                    "scenario_net_pnl_inr": pnl,
                })

        if not candidate_records:
            continue

        cdf = pd.DataFrame(candidate_records)
        # The frozen selector is the maximum static positive flatline.
        for name, score_col in (
            ("control", "flatline_inr"),
            ("median", "scenario_median_inr"),
            ("p10", "scenario_p10_inr"),
            ("worst", "scenario_worst_inr"),
        ):
            chosen = cdf.sort_values(
                [score_col, "flatline_inr", "shift_points"],
                ascending=[False, False, True],
            ).iloc[0]
            if name == "control":
                frozen_shift = int(selected.loc[
                    (selected["near_expiry"] == near_expiry)
                    & (selected["entry_timestamp"] == entry_ts),
                    "shift_points"
                ].iloc[0])
                if int(chosen["shift_points"]) != frozen_shift:
                    raise RuntimeError(
                        f"Control selector mismatch for {near_expiry}: "
                        f"decision surface selected {chosen['shift_points']} but frozen control has {frozen_shift}"
                    )

            fc = far_exit_map.get((float(chosen["strike"]), "CE"))
            fp = far_exit_map.get((float(chosen["strike"]), "PE"))
            if fc is None or fp is None:
                continue

            selector_rows[name].append({
                "entry_timestamp": entry_ts,
                "entry_date": entry_ts.date(),
                "near_expiry": near_expiry,
                "far_expiry": far_expiry,
                "near_exit_timestamp": exit_ts,
                "far_call_exit_timestamp": fc[1],
                "far_put_exit_timestamp": fp[1],
                "candidate_label": chosen["candidate_label"],
                "shift_points": int(chosen["shift_points"]),
                "strike": float(chosen["strike"]),
                "near_call_close": chosen["near_call_close"],
                "near_put_close": chosen["near_put_close"],
                "far_call_close": chosen["far_call_close"],
                "far_put_close": chosen["far_put_close"],
                "near_settlement": float(_settlement),
                "far_call_exit_close": float(fc[0]),
                "far_put_exit_close": float(fp[0]),
                "near_lot_size": nifty_lot_size(near_expiry),
                "far_lot_size": nifty_lot_size(far_expiry),
                "flatline_inr": float(chosen["flatline_inr"]),
                "scenario_median_inr": float(chosen["scenario_median_inr"]),
                "scenario_p10_inr": float(chosen["scenario_p10_inr"]),
                "scenario_worst_inr": float(chosen["scenario_worst_inr"]),
                "scenario_mean_inr": float(chosen["scenario_mean_inr"]),
                "scenario_sd_inr": float(chosen["scenario_sd_inr"]),
                "status": "ok",
            })

    out_control = out_dir / "control.csv"
    selected.to_csv(out_control, index=False)
    for name, rows in selector_rows.items():
        out = out_dir / f"selector_{name}.csv"
        pd.DataFrame(rows).to_csv(out, index=False)

    scen = pd.DataFrame(scenario_rows)
    scen.to_csv(out_dir / "candidate_scenario_scores.csv", index=False)

    coverage = {
        name: int(len(rows)) for name, rows in selector_rows.items()
    }
    metadata = {
        "dataset": DATASET,
        "weekly_cycles": int(len(decision_keys)),
        "scenario_count_per_candidate": 15,
        "spot_shocks_pct": [x * 100 for x in SPOT_SHOCKS],
        "far_iv_shock_points": list(IV_SHOCK_POINTS),
        "selectors": ["control", "median", "p10", "worst"],
        "coverage": coverage,
        "selection_rule": "positive/all-green static flatline candidates only; score on fixed entry-time scenario grid; tie-break by static flatline then shift ascending",
        "black_scholes": {"r": 0.0, "q": 0.0, "iv_source": "entry premium inversion"},
        "cost_model": {"slippage_pct": args.slippage_pct, "brokerage_per_order": args.brokerage_per_order},
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str))
    print(json.dumps(metadata, indent=2, default=str))


if __name__ == "__main__":
    main()
