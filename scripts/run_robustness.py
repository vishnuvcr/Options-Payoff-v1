#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.costs import CostModel, four_leg_entry_cashflow, transaction_costs, trigger_base
from src.options_payoff import intrinsic_value


def nifty_lot_size(expiry: date) -> int:
    if expiry < date(2021, 8, 1):
        return 75
    if expiry < date(2024, 5, 2):
        return 50
    if expiry < date(2024, 11, 21):
        return 25
    if expiry < date(2026, 1, 6):
        return 75
    return 65


def parse_list(value: str, cast=float):
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def max_drawdown(pnl: pd.Series) -> float:
    if len(pnl) == 0:
        return 0.0
    curve = pnl.cumsum()
    return float((curve - curve.cummax()).min())


def summarize_selected(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "n_trades": 0,
            "total_net_pnl_inr": 0.0,
            "mean_net_pnl_inr": None,
            "median_net_pnl_inr": None,
            "win_rate_pct": None,
            "profit_factor": None,
            "max_drawdown_inr": 0.0,
            "date_start": None,
            "date_end": None,
        }
    x = df.sort_values("entry_timestamp")
    pnl = x["net_pnl_inr"].astype(float)
    years = max(
        (pd.to_datetime(x["entry_timestamp"]).max() - pd.to_datetime(x["entry_timestamp"]).min()).days / 365.25,
        1 / 365.25,
    )
    wins = pnl[pnl > 0].sum()
    losses = abs(pnl[pnl < 0].sum())
    return {
        "n_trades": int(len(x)),
        "total_net_pnl_inr": float(pnl.sum()),
        "mean_net_pnl_inr": float(pnl.mean()),
        "median_net_pnl_inr": float(pnl.median()),
        "win_rate_pct": float((pnl > 0).mean() * 100),
        "profit_factor": float(wins / losses) if losses > 0 else None,
        "max_drawdown_inr": max_drawdown(pnl),
        "trades_per_year": float(len(x) / years),
        "date_start": str(pd.to_datetime(x["entry_timestamp"]).min().date()),
        "date_end": str(pd.to_datetime(x["entry_timestamp"]).max().date()),
    }


def block_bootstrap_mean(df: pd.DataFrame, n_boot: int = 5000, seed: int = 42) -> dict:
    if df.empty:
        return {"n_blocks": 0, "ci95": [None, None], "mean": None}
    x = df.copy()
    ts = pd.to_datetime(x["entry_timestamp"])
    x["block"] = ts.dt.to_period("W-MON").astype(str)
    blocks = [g["net_pnl_inr"].to_numpy(dtype=float) for _, g in x.groupby("block")]
    rng = np.random.default_rng(seed)
    observed = float(x["net_pnl_inr"].mean())
    samples = np.empty(n_boot)
    for i in range(n_boot):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        vals = np.concatenate([blocks[j] for j in chosen])
        samples[i] = vals.mean() if len(vals) else np.nan
    samples = samples[np.isfinite(samples)]
    return {
        "n_blocks": len(blocks),
        "mean": observed,
        "ci95": [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))] if len(samples) else [None, None],
        "n_boot": int(len(samples)),
    }


def build_candidate_table(raw: pd.DataFrame, slippage: float, mode: str, configured_capital: float | None) -> pd.DataFrame:
    rows = []
    for row in raw[raw["status"].eq("ok")].itertuples(index=False):
        near_expiry = pd.Timestamp(row.near_expiry).date()
        next_expiry = pd.Timestamp(row.next_expiry).date()
        near_lot = nifty_lot_size(near_expiry)
        next_lot = nifty_lot_size(next_expiry)
        if near_lot != next_lot:
            continue
        premiums = [row.near_call_close, row.near_put_close, row.next_call_close, row.next_put_close]
        if any(pd.isna(x) for x in premiums) or pd.isna(row.near_settlement) or pd.isna(row.next_settlement):
            continue
        execs = four_leg_entry_cashflow(*map(float, premiums), slippage_pct=slippage)
        observed_buy_premium = float(row.near_put_close) + float(row.next_call_close)
        base = trigger_base(
            mode,
            float(row.spot_at_entry),
            near_lot,
            observed_buy_premium,
            configured_capital,
        )
        chart_pnl = float(row.net_entry_cashflow_per_unit) * near_lot
        chart_return = 100.0 * chart_pnl / base if base > 0 else None
        gross_per_unit = float(execs['entry_cashflow_per_unit']) + float(row.next_settlement) - float(row.near_settlement)
        gross_pnl = gross_per_unit * near_lot
        long_call_intrinsic = intrinsic_value("CE", float(row.next_settlement), float(row.strike))
        long_put_intrinsic = intrinsic_value("PE", float(row.near_settlement), float(row.strike))
        costs = transaction_costs(
            pd.Timestamp(row.entry_timestamp).date(),
            execs["premium_turnover"],
            execs["sell_premium_turnover"],
            execs["buy_premium_turnover"],
            long_call_intrinsic,
            long_put_intrinsic,
            near_lot,
            CostModel(slippage_pct=slippage),
        )
        rows.append(
            {
                "entry_timestamp": row.entry_timestamp,
                "entry_date": row.entry_date,
                "candidate_label": row.candidate_label,
                "strike": row.strike,
                "spot_at_entry": row.spot_at_entry,
                "near_expiry": row.near_expiry,
                "next_expiry": row.next_expiry,
                "lot_size": near_lot,
                "chart_return_pct": chart_return,
                "gross_pnl_inr": gross_pnl,
                "net_pnl_inr": gross_pnl - costs["total_costs"],
                "total_costs_inr": costs["total_costs"],
            }
        )
    return pd.DataFrame(rows)


def select_trades(candidates: pd.DataFrame, threshold: float) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    order = ["ATM", "ATM_MINUS_400", "ATM_PLUS_400"]
    chosen = []
    for _, group in candidates.groupby("entry_timestamp", sort=True):
        by_label = {r.candidate_label: r for r in group.itertuples(index=False)}
        picked = None
        for label in order:
            row = by_label.get(label)
            if row is not None and pd.notna(row.chart_return_pct) and row.chart_return_pct > threshold:
                picked = row
                break
        if picked is not None:
            chosen.append(picked._asdict())
    return pd.DataFrame(chosen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out-dir", default="results/phase4")
    ap.add_argument("--slippages", default="0,0.001,0.0025,0.005,0.01")
    ap.add_argument("--thresholds", default="1,1.5,2,2.5,3,4,5")
    ap.add_argument("--denominators", default="buy_premium,spot_notional")
    ap.add_argument("--configured-capital-per-lot", type=float)
    ap.add_argument("--bootstrap", type=int, default=5000)
    args = ap.parse_args()

    raw = pd.read_parquet(args.inputs)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    slippages = parse_list(args.slippages)
    thresholds = parse_list(args.thresholds)
    modes = [x.strip() for x in args.denominators.split(",") if x.strip()]
    if "configured_capital" in modes and args.configured_capital_per_lot is None:
        modes = [x for x in modes if x != "configured_capital"]

    grid = []
    label_rows = []
    baseline_selected = None
    baseline_key = None
    baseline_candidates = None

    for mode in modes:
        for slip in slippages:
            cand = build_candidate_table(raw, slip, mode, args.configured_capital_per_lot)
            for threshold in thresholds:
                selected = select_trades(cand, threshold)
                summary = summarize_selected(selected)
                summary.update({
                    "trigger_base_mode": mode,
                    "slippage_pct": slip,
                    "threshold_pct": threshold,
                    "candidate_rows": int(len(cand)),
                    "eligible_entry_timestamps": int(cand["entry_timestamp"].nunique()) if not cand.empty else 0,
                })
                grid.append(summary)
                if mode == "buy_premium" and abs(slip - 0.0025) < 1e-12 and abs(threshold - 2.5) < 1e-12:
                    baseline_selected = selected.copy()
                    baseline_candidates = cand.copy()
                    baseline_key = {"trigger_base_mode": mode, "slippage_pct": slip, "threshold_pct": threshold}

    if baseline_selected is None:
        raise RuntimeError("Baseline configuration was not evaluated")

    pd.DataFrame(grid).to_csv(out / "robustness_grid.csv", index=False)

    label_summary = (
        baseline_selected.groupby("candidate_label")
        .agg(
            trades=("net_pnl_inr", "size"),
            total_net_pnl_inr=("net_pnl_inr", "sum"),
            mean_net_pnl_inr=("net_pnl_inr", "mean"),
            median_net_pnl_inr=("net_pnl_inr", "median"),
            win_rate=("net_pnl_inr", lambda s: float((s > 0).mean())),
        )
        .reset_index()
    )
    label_summary.to_csv(out / "selection_by_label.csv", index=False)

    source_quality = {
        "raw_rows": int(len(raw)),
        "ok_rows": int(raw["status"].eq("ok").sum()),
        "candidate_strike_unavailable_rows": int(raw["status"].eq("candidate_strike_unavailable").sum()),
        "missing_settlement_rows": int(raw["status"].eq("missing_settlement").sum()),
        "lot_mismatch_rows": int(
            sum(
                1
                for r in raw[raw["status"].eq("ok")].itertuples(index=False)
                if nifty_lot_size(pd.Timestamp(r.near_expiry).date()) != nifty_lot_size(pd.Timestamp(r.next_expiry).date())
            )
        ),
    }
    (out / "data_quality_sensitivity.json").write_text(json.dumps(source_quality, indent=2))

    ts = pd.to_datetime(baseline_selected["entry_timestamp"]).sort_values().unique()
    split_index = max(1, int(len(ts) * 0.70)) if len(ts) else 1
    split_ts = pd.Timestamp(ts[min(split_index, len(ts) - 1)]) if len(ts) else None
    if split_ts is not None:
        train = baseline_selected[pd.to_datetime(baseline_selected["entry_timestamp"]) < split_ts]
        test = baseline_selected[pd.to_datetime(baseline_selected["entry_timestamp"]) >= split_ts]
    else:
        train = pd.DataFrame()
        test = pd.DataFrame()
    walkforward = {
        "baseline": baseline_key,
        "split_rule": "chronological 70/30 by unique eligible entry timestamp",
        "split_timestamp": str(split_ts) if split_ts is not None else None,
        "train": summarize_selected(train),
        "test": summarize_selected(test),
    }
    (out / "walkforward_baseline.json").write_text(json.dumps(walkforward, indent=2, default=str))

    bootstrap = block_bootstrap_mean(baseline_selected, n_boot=args.bootstrap)
    (out / "block_bootstrap_baseline.json").write_text(json.dumps(bootstrap, indent=2))

    unconditional_atm = baseline_candidates[baseline_candidates["candidate_label"].eq("ATM")].copy()
    unconditional_atm = unconditional_atm.drop_duplicates("entry_timestamp")
    (out / "unconditional_atm_baseline.json").write_text(json.dumps(summarize_selected(unconditional_atm), indent=2, default=str))

    manifest = {
        "inputs": args.inputs,
        "slippages": slippages,
        "thresholds": thresholds,
        "denominators_evaluated": modes,
        "configured_capital_per_lot": args.configured_capital_per_lot,
        "baseline": baseline_key,
        "note": "Configured-capital denominator is omitted unless explicitly supplied; no capital figure was invented.",
    }
    (out / "robustness_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(json.dumps({"baseline": baseline_key, "robustness_rows": len(grid)}, indent=2))


if __name__ == "__main__":
    main()
