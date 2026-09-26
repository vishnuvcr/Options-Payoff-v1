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


def iid_bootstrap_mean_ci(x: np.ndarray, n: int = 5000, seed: int = 42) -> list[float | None]:
    if len(x) == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    samples = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def weekly_block_bootstrap_mean_ci(df: pd.DataFrame, n: int = 5000, seed: int = 43) -> list[float | None]:
    if df.empty:
        return [None, None]
    x = df.copy()
    dates = pd.to_datetime(x["entry_timestamp"], utc=True)
    week = dates.dt.to_period("W-MON").astype(str)
    blocks = [g["net_pnl_inr"].astype(float).to_numpy() for _, g in x.groupby(week, sort=True)]
    if not blocks:
        return [None, None]
    rng = np.random.default_rng(seed)
    samples = []
    n_blocks = len(blocks)
    for _ in range(n):
        total = []
        for idx in rng.integers(0, n_blocks, size=n_blocks):
            total.extend(blocks[int(idx)].tolist())
        samples.append(float(np.mean(total)))
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def chronological_split(df: pd.DataFrame) -> dict[str, float | int | None]:
    x = df.sort_values("entry_timestamp").reset_index(drop=True)
    if len(x) < 4:
        return {
            "train_trades": int(len(x)),
            "test_trades": 0,
            "train_net_pnl_inr": float(x["net_pnl_inr"].sum()) if len(x) else 0.0,
            "test_net_pnl_inr": None,
        }
    cut = max(1, int(np.floor(len(x) * 0.70)))
    train = x.iloc[:cut]
    test = x.iloc[cut:]
    return {
        "train_trades": int(len(train)),
        "test_trades": int(len(test)),
        "train_net_pnl_inr": float(train["net_pnl_inr"].sum()),
        "test_net_pnl_inr": float(test["net_pnl_inr"].sum()),
        "train_mean_net_pnl_inr": float(train["net_pnl_inr"].mean()),
        "test_mean_net_pnl_inr": float(test["net_pnl_inr"].mean()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_parquet(args.trades)
    if df.empty:
        raise RuntimeError("No Phase 7 selected trades")
    df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"], utc=True)
    df = df.sort_values("entry_timestamp").reset_index(drop=True)
    pnl = pd.to_numeric(df["net_pnl_inr"], errors="coerce").dropna()
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    result = {
        "n_trades": int(len(pnl)),
        "date_start": str(df["entry_timestamp"].min().date()),
        "date_end": str(df["entry_timestamp"].max().date()),
        "total_net_pnl_inr": float(pnl.sum()),
        "mean_net_pnl_inr": float(pnl.mean()),
        "median_net_pnl_inr": float(pnl.median()),
        "win_rate_pct": float(100.0 * (pnl > 0).mean()),
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) else None,
        "max_drawdown_inr": max_drawdown(pnl),
        "largest_win_inr": float(pnl.max()),
        "largest_loss_inr": float(pnl.min()),
        "total_costs_inr": float(df["total_costs_inr"].sum()) if "total_costs_inr" in df else None,
        "mean_estimated_equal_max_profit_loss_inr": float(df["estimated_equal_max_profit_loss_inr"].mean()) if "estimated_equal_max_profit_loss_inr" in df else None,
        "max_estimated_equal_max_profit_loss_inr": float(df["estimated_equal_max_profit_loss_inr"].max()) if "estimated_equal_max_profit_loss_inr" in df else None,
        "iid_bootstrap_mean_ci_95_inr": iid_bootstrap_mean_ci(pnl.to_numpy()),
        "weekly_block_bootstrap_mean_ci_95_inr": weekly_block_bootstrap_mean_ci(df),
        "chronological_70_30": chronological_split(df),
        "shift_counts": {str(k): int(v) for k, v in df["shift_points"].value_counts().sort_index().items()} if "shift_points" in df else {},
        "positive_flatline_rate_pct": float(100.0 * df["estimated_all_green_flatline"].mean()) if "estimated_all_green_flatline" in df else None,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
