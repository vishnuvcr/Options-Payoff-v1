#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


CONTROL_NET = 71868.75950141653
CONTROL_TRADES = 131


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--control", required=True)
    p.add_argument("--results-dir", required=True)
    p.add_argument("--bootstrap-reps", type=int, default=20000)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--slippage-pct", type=float, default=0.0025)
    p.add_argument("--brokerage-per-order", type=float, default=20.0)
    return p.parse_args()


def profit_factor(x):
    a = np.asarray(x, dtype=float)
    wins = a[a > 0].sum()
    losses = -a[a < 0].sum()
    return float(wins / losses) if losses > 0 else np.inf


def max_drawdown(x):
    a = np.asarray(x, dtype=float)
    if len(a) == 0:
        return 0.0
    curve = np.cumsum(a)
    peaks = np.maximum.accumulate(np.r_[0.0, curve])[:-1]
    return float(np.min(curve - peaks))


def block_bootstrap_mean_ci(values, reps, block=4, seed=20260929):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    blocks = [x[i:i + block] for i in range(len(x))]
    means = np.empty(reps)
    for i in range(reps):
        draw = []
        while len(draw) < len(x):
            draw.extend(blocks[int(rng.integers(0, len(blocks)))])
        means[i] = np.mean(draw[:len(x)])
    return float(np.quantile(means, .025)), float(np.quantile(means, .975))


def paired_permutation_p(diff, reps, seed=20260929):
    x = np.asarray(diff, dtype=float)
    if len(x) == 0:
        return np.nan
    rng = np.random.default_rng(seed)
    obs = abs(x.mean())
    exceed = 0
    for _ in range(reps):
        stat = abs((rng.choice([-1.0, 1.0], len(x)) * x).mean())
        exceed += int(stat >= obs)
    return float((1 + exceed) / (reps + 1))


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return 100 * (centre - half), 100 * (centre + half)


def summarize(df):
    if df.empty:
        return {
            "trades": 0, "weekly_cycles": 0, "net_pnl_inr": 0.0,
            "mean_pnl_inr": np.nan, "median_pnl_inr": np.nan,
            "win_rate_pct": np.nan, "win_ci_low_pct": np.nan, "win_ci_high_pct": np.nan,
            "profit_factor": np.nan, "max_drawdown_inr": 0.0, "total_costs_inr": 0.0,
        }
    x = df["net_pnl_inr"].to_numpy(float)
    ci_lo, ci_hi = wilson(int((x > 0).sum()), len(x))
    return {
        "trades": int(len(x)),
        "weekly_cycles": int(df["near_expiry"].nunique()),
        "net_pnl_inr": float(x.sum()),
        "mean_pnl_inr": float(x.mean()),
        "median_pnl_inr": float(np.median(x)),
        "win_rate_pct": float(100 * (x > 0).mean()),
        "win_ci_low_pct": ci_lo,
        "win_ci_high_pct": ci_hi,
        "profit_factor": profit_factor(x),
        "max_drawdown_inr": max_drawdown(x),
        "total_costs_inr": float(df["total_costs"].sum()) if "total_costs" in df else np.nan,
    }


def read_trade(path):
    df = pd.read_csv(path)
    if df.empty:
        return df
    df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"], utc=True)
    df["near_expiry"] = pd.to_datetime(df["near_expiry"]).dt.date
    return df


def main():
    args = parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    control_input = pd.read_csv(args.control)
    if len(control_input) != CONTROL_TRADES:
        raise RuntimeError(f"Frozen Phase 9G control has {len(control_input)} rows, expected {CONTROL_TRADES}")

    control_res = read_trade(out / "control" / "intraday_selected_trades.csv")
    control = summarize(control_res)
    if control["trades"] != CONTROL_TRADES or abs(control["net_pnl_inr"] - CONTROL_NET) > 0.01:
        raise RuntimeError(
            f"Phase 9G control reproduction failed: trades={control['trades']} net={control['net_pnl_inr']}"
        )

    variants = {
        "control": out / "control" / "intraday_selected_trades.csv",
        "median": out / "median" / "intraday_selected_trades.csv",
        "p10": out / "p10" / "intraday_selected_trades.csv",
        "worst": out / "worst" / "intraday_selected_trades.csv",
    }
    results = {}
    summary_rows = []
    for name, path in variants.items():
        df = read_trade(path)
        results[name] = df
        s = summarize(df)
        summary_rows.append({"variant": name, **s})

    control_cycles = pd.DataFrame({
        "near_expiry": control_res["near_expiry"],
        "control_pnl": control_res["net_pnl_inr"],
    })

    paired_rows = []
    for name in ("median", "p10", "worst"):
        df = results[name]
        v = (
            df[["near_expiry", "net_pnl_inr"]]
            .rename(columns={"net_pnl_inr": "variant_pnl"})
            if not df.empty
            else pd.DataFrame(columns=["near_expiry", "variant_pnl"])
        )
        x = control_cycles.merge(v, on="near_expiry", how="left")
        covered = int(x["variant_pnl"].notna().sum())
        x = x[x["variant_pnl"].notna()].copy()
        diff = (x["variant_pnl"] - x["control_pnl"]).to_numpy(float)
        lo, hi = block_bootstrap_mean_ci(diff, args.bootstrap_reps)
        paired_rows.append({
            "variant": name,
            "paired_cycles": int(len(x)),
            "covered_cycles": covered,
            "unavailable_cycles": int(len(x) - covered),
            "mean_difference_inr": float(diff.mean()),
            "median_difference_inr": float(np.median(diff)),
            "net_difference_inr": float(diff.sum()),
            "block_bootstrap_low_inr": lo,
            "block_bootstrap_high_inr": hi,
            "paired_permutation_p": paired_permutation_p(diff, args.bootstrap_reps),
        })

    paired = pd.DataFrame(paired_rows)
    p = paired["paired_permutation_p"].to_numpy(float)
    order = np.argsort(p)
    q = np.empty_like(p)
    running = 1.0
    m = len(p)
    for rank, idx in reversed(list(enumerate(order, start=1))):
        running = min(running, p[idx] * m / rank)
        q[idx] = running
    paired["bh_q"] = q

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "scenario_selector_summary.csv", index=False)
    paired.to_csv(out / "paired_scenario_comparisons.csv", index=False)

    if paired.empty:
        raise RuntimeError("No paired scenario comparisons available")
    best = paired.sort_values("mean_difference_inr", ascending=False).iloc[0]
    promotion = bool(
        best["mean_difference_inr"] > 0
        and best["block_bootstrap_low_inr"] > 0
        and best["bh_q"] < 0.05
    )
    promotion_payload = {
        "passed": promotion,
        "best_variant": str(best["variant"]),
        "criteria": {
            "mean_difference_gt_zero": bool(best["mean_difference_inr"] > 0),
            "bootstrap_low_gt_zero": bool(best["block_bootstrap_low_inr"] > 0),
            "bh_q_lt_0_05": bool(best["bh_q"] < 0.05),
        },
    }
    (out / "promotion_screen.json").write_text(json.dumps(promotion_payload, indent=2))

    report = f"""# Phase 10C — Scenario-aware strike selection

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question

Can the frozen 17-strike selector be improved by ranking positive/all-green candidates using a fixed, point-in-time scenario grid for the full near-expiry position rather than the static same-spot flatline alone?

## Frozen scenario grid

- Near-expiry spot shock: -2%, -1%, 0%, +1%, +2%.
- Far-leg IV shock: -5, 0, +5 volatility points.
- Total scenarios per candidate: 15.
- Far CE/PE values at the near-expiry horizon use Black–Scholes with r=0 and q=0.
- IVs are inverted only from entry-time observed premiums.
- Entry slippage: {args.slippage_pct:.4%}; brokerage: ₹{args.brokerage_per_order:.2f}/order.
- Only positive/all-green static-flatline candidates are eligible.
- Tie-break: scenario score, then static flatline, then shift from ATM.

## Control reproduction

- Complete frozen Phase 9G trades: {control['trades']}
- Control net P&L: ₹{control['net_pnl_inr']:,.2f}

## Results

{summary.to_markdown(index=False)}

## Paired inference versus the frozen control

{paired.to_markdown(index=False)}

## Decision

{("A scenario selector passed the historical promotion screen; it is not promoted and still requires Phase 10G chronological holdout." if promotion else "No scenario selector met the full predeclared promotion screen. The frozen Phase 9G H1 control is retained.")}

## Interpretation

Scenario-aware ranking is evaluated on the complete weekly decision population and does not use realized P&L, future spot, or future option prices to choose the strike. Its only future-horizon element is a fixed theoretical revaluation horizon and fixed stress grid declared before scoring.

## Limitations

- Historical option observations are close-price proxies, not executable bid/ask quotes.
- Black–Scholes IV is a model-based reconstruction rather than an exchange-published IV surface.
- Some candidates may lack a valid IV inversion; such cycles are reported as unavailable rather than filled synthetically.
- The scenario score is a research selector, not a guarantee of realized profit.
"""
    (out / "PHASE10C_RESULTS.md").write_text(report)
    print(json.dumps({"status": "complete", "promotion": promotion_payload, "summary": summary_rows, "paired": paired_rows}, indent=2, default=str))


if __name__ == "__main__":
    main()
