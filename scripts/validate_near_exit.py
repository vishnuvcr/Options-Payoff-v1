#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def max_drawdown(pnl: pd.Series) -> float:
    curve = pnl.cumsum()
    peak = curve.cummax()
    return float((curve - peak).min()) if len(curve) else 0.0


def iid_bootstrap_ci(x: np.ndarray, n: int = 5000, seed: int = 42) -> list[float | None]:
    if len(x) == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    samples = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def block_bootstrap_ci(df: pd.DataFrame, n: int = 5000, seed: int = 43) -> list[float | None]:
    if df.empty:
        return [None, None]
    x = df.copy()
    dates = pd.to_datetime(x["entry_timestamp"], errors="coerce")
    week = dates.dt.to_period("W-MON").astype(str)
    blocks = [g["net_pnl_inr"].astype(float).to_numpy() for _, g in x.groupby(week, sort=True)]
    if not blocks:
        return [None, None]
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        idx = rng.integers(0, len(blocks), size=len(blocks))
        sample = np.concatenate([blocks[int(i)] for i in idx])
        means.append(float(sample.mean()))
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def summarize(df: pd.DataFrame) -> dict:
    x = df.copy()
    x["entry_timestamp"] = pd.to_datetime(x["entry_timestamp"], errors="coerce")
    x = x.sort_values("entry_timestamp").reset_index(drop=True)
    pnl = pd.to_numeric(x["net_pnl_inr"], errors="coerce").dropna()
    gross = pd.to_numeric(x["gross_pnl_inr"], errors="coerce")
    costs = pd.to_numeric(x["total_costs"], errors="coerce")
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    cut = int(np.floor(len(x) * 0.70))
    train = x.iloc[:cut] if cut else x.iloc[:0]
    test = x.iloc[cut:] if cut < len(x) else x.iloc[:0]

    loss_mask = pnl < 0
    loss_rows = x.loc[loss_mask]
    gross_loss_rows = (pd.to_numeric(loss_rows["gross_pnl_inr"], errors="coerce") < 0).sum() if len(loss_rows) else 0
    cost_flip_rows = ((pd.to_numeric(loss_rows["gross_pnl_inr"], errors="coerce") >= 0)).sum() if len(loss_rows) else 0

    return {
        "n_trades": int(len(x)),
        "date_start": str(x["entry_timestamp"].min().date()) if len(x) else None,
        "date_end": str(x["entry_timestamp"].max().date()) if len(x) else None,
        "total_net_pnl_inr": float(pnl.sum()) if len(pnl) else 0.0,
        "total_gross_pnl_inr": float(gross.sum()) if len(gross) else 0.0,
        "total_costs_inr": float(costs.sum()) if len(costs) else 0.0,
        "mean_net_pnl_inr": float(pnl.mean()) if len(pnl) else None,
        "median_net_pnl_inr": float(pnl.median()) if len(pnl) else None,
        "win_rate_pct": float(100.0 * (pnl > 0).mean()) if len(pnl) else None,
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) else None,
        "max_drawdown_inr": max_drawdown(pnl),
        "largest_win_inr": float(pnl.max()) if len(pnl) else None,
        "largest_loss_inr": float(pnl.min()) if len(pnl) else None,
        "iid_bootstrap_mean_ci_95_inr": iid_bootstrap_ci(pnl.to_numpy()),
        "weekly_block_bootstrap_mean_ci_95_inr": block_bootstrap_ci(x),
        "chronological_70_30": {
            "train_trades": int(len(train)),
            "test_trades": int(len(test)),
            "train_net_pnl_inr": float(train["net_pnl_inr"].sum()) if len(train) else None,
            "test_net_pnl_inr": float(test["net_pnl_inr"].sum()) if len(test) else None,
        },
        "loss_audit": {
            "loss_count": int(len(loss_rows)),
            "losses_negative_before_fees": int(gross_loss_rows),
            "cost_only_flips": int(cost_flip_rows),
            "loss_costs_inr": float(pd.to_numeric(loss_rows["total_costs"], errors="coerce").sum()) if len(loss_rows) else 0.0,
        },
        "selection_shifts": {str(k): int(v) for k, v in x["shift_points"].value_counts().sort_index().items()},
        "mean_chart_pnl_inr": float(pd.to_numeric(x["chart_pnl_inr"], errors="coerce").mean()),
        "mean_estimated_equal_max_profit_loss_inr": float(
            pd.to_numeric(x["estimated_equal_max_profit_loss_inr"], errors="coerce").mean()
        ),
        "static_chart_contribution_total_inr": float(pd.to_numeric(x["chart_pnl_inr"], errors="coerce").sum()),
        "realized_minus_chart_total_inr": float(
            (pd.to_numeric(x["gross_pnl_inr"], errors="coerce") - pd.to_numeric(x["chart_pnl_inr"], errors="coerce")).sum()
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    primary = pd.read_csv(args.primary)
    if primary.empty:
        raise RuntimeError("No corrected weekly trades were produced")
    required = {
        "entry_timestamp", "near_exit_timestamp", "far_call_exit_timestamp",
        "far_put_exit_timestamp", "shift_points", "strike",
        "chart_pnl_inr", "estimated_equal_max_profit_loss_inr",
        "gross_pnl_inr", "net_pnl_inr", "total_costs",
    }
    missing = sorted(required - set(primary.columns))
    if missing:
        raise ValueError(f"Missing required corrected-trade columns: {missing}")

    primary["entry_timestamp"] = pd.to_datetime(primary["entry_timestamp"], errors="coerce")
    primary["near_exit_timestamp"] = pd.to_datetime(primary["near_exit_timestamp"], errors="coerce")
    primary["far_call_exit_timestamp"] = pd.to_datetime(primary["far_call_exit_timestamp"], errors="coerce")
    primary["far_put_exit_timestamp"] = pd.to_datetime(primary["far_put_exit_timestamp"], errors="coerce")

    if primary[["near_exit_timestamp","far_call_exit_timestamp","far_put_exit_timestamp"]].isna().any().any():
        raise ValueError("Corrected ledger contains missing exit timestamps")
    if (primary["far_call_exit_timestamp"] > primary["near_exit_timestamp"]).any():
        raise ValueError("Far-call exit occurs after near expiry")
    if (primary["far_put_exit_timestamp"] > primary["near_exit_timestamp"]).any():
        raise ValueError("Far-put exit occurs after near expiry")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summary = summarize(primary)

    losses = primary[primary["net_pnl_inr"] < 0].copy().sort_values("net_pnl_inr")
    losses["loss_rank"] = np.arange(1, len(losses) + 1)
    losses.to_csv(out / "corrected_loss_trades.csv", index=False)

    shift = (
        losses.groupby("shift_points", as_index=False)
        .agg(
            losses=("net_pnl_inr", "size"),
            total_loss=("net_pnl_inr", "sum"),
            mean_loss=("net_pnl_inr", "mean"),
            worst_loss=("net_pnl_inr", "min"),
            costs=("total_costs", "sum"),
        )
        .sort_values("total_loss")
    )
    shift.to_csv(out / "corrected_losses_by_shift.csv", index=False)

    weekly = (
        primary.assign(near_expiry=pd.to_datetime(primary["near_expiry"], errors="coerce"))
        .groupby("near_expiry", as_index=False)
        .agg(
            trades=("net_pnl_inr", "size"),
            gross_pnl_inr=("gross_pnl_inr", "sum"),
            total_costs=("total_costs", "sum"),
            net_pnl_inr=("net_pnl_inr", "sum"),
        )
        .sort_values("near_expiry")
    )
    weekly.to_csv(out / "corrected_weekly_pnl.csv", index=False)

    summary["validation_assertions"] = {
        "all_far_exits_on_or_before_near_expiry": True,
        "no_missing_exit_timestamps": True,
        "one_trade_per_near_expiry_cycle": int(primary["near_expiry"].nunique()) == int(len(primary)),
    }
    (out / "corrected_validation_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
