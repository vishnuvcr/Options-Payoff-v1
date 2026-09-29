#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--control", required=True)
    p.add_argument("--results-dir", required=True)
    p.add_argument("--bootstrap-reps", type=int, default=20000)
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def max_drawdown(values):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return 0.0
    curve = np.cumsum(x)
    peaks = np.maximum.accumulate(np.r_[0.0, curve])[:-1]
    return float(np.min(curve - peaks))


def profit_factor(values):
    x = np.asarray(values, dtype=float)
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    return float(wins / losses) if losses > 0 else np.inf


def block_bootstrap_mean_ci(values, reps, seed=20260929, block=4):
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


def summarize(df):
    if df.empty:
        return {"trades": 0, "net_pnl_inr": 0.0, "mean_pnl_inr": np.nan, "win_rate_pct": np.nan, "profit_factor": np.nan, "max_drawdown_inr": 0.0}
    x = df["net_pnl_inr"].to_numpy(float)
    return {
        "trades": int(len(x)),
        "weekly_cycles": int(df["near_expiry"].nunique()),
        "net_pnl_inr": float(x.sum()),
        "mean_pnl_inr": float(x.mean()),
        "median_pnl_inr": float(np.median(x)),
        "win_rate_pct": float(100 * (x > 0).mean()),
        "profit_factor": profit_factor(x),
        "max_drawdown_inr": max_drawdown(x),
        "total_costs_inr": float(df["total_costs"].sum()) if "total_costs" in df else np.nan,
    }


def main():
    args = parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    control = pd.read_csv(args.control)
    if len(control) != 131:
        raise RuntimeError(f"Phase 9G control reproduction failed: {len(control)} rows, expected 131")
    control["entry_timestamp"] = pd.to_datetime(control["entry_timestamp"], utc=True)
    control["near_expiry"] = pd.to_datetime(control["near_expiry"]).dt.date

    base = summarize(control)
    if abs(base["net_pnl_inr"] - 71868.75950141653) > 0.01:
        raise RuntimeError("Phase 9G control net P&L does not reproduce ₹71,868.76")

    rows = [{"variant": "control", **base}]
    paired_rows = []
    for delay in [5, 10, 15, 30]:
        p = out / f"{delay}m" / "intraday_selected_trades.csv"
        if not p.exists():
            raise RuntimeError(f"Missing backtest ledger for {delay}m confirmation")
        df = pd.read_csv(p)
        if not df.empty:
            df["entry_timestamp"] = pd.to_datetime(df["entry_timestamp"], utc=True)
            df["near_expiry"] = pd.to_datetime(df["near_expiry"]).dt.date
        s = summarize(df)
        rows.append({"variant": f"{delay}m", **s})

        c = control[["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "control_pnl"})
        v = df[["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "variant_pnl"}) if not df.empty else pd.DataFrame(columns=["near_expiry", "variant_pnl"])
        x = c.merge(v, on="near_expiry", how="left").fillna(0.0)
        diff = x["variant_pnl"].to_numpy(float) - x["control_pnl"].to_numpy(float)
        lo, hi = block_bootstrap_mean_ci(diff, args.bootstrap_reps)
        paired_rows.append({
            "variant": f"{delay}m",
            "paired_cycles": int(len(x)),
            "confirmed_cycles": int(len(df)),
            "mean_difference_inr": float(diff.mean()),
            "median_difference_inr": float(np.median(diff)),
            "net_difference_inr": float(diff.sum()),
            "block_bootstrap_low_inr": lo,
            "block_bootstrap_high_inr": hi,
            "paired_permutation_p": paired_permutation_p(diff, args.bootstrap_reps),
        })

    paired = pd.DataFrame(paired_rows)
    p = paired["paired_permutation_p"].to_numpy()
    order = np.argsort(p)
    q = np.empty_like(p)
    running = 1.0
    m = len(p)
    for rank, idx in reversed(list(enumerate(order, start=1))):
        running = min(running, p[idx] * m / rank)
        q[idx] = running
    paired["bh_q"] = q

    summary = pd.DataFrame(rows)
    summary.to_csv(out / "confirmation_summary.csv", index=False)
    paired.to_csv(out / "paired_confirmation_comparisons.csv", index=False)

    best = paired.sort_values("mean_difference_inr", ascending=False).iloc[0]
    promotion = bool(
        best["mean_difference_inr"] > 0
        and best["block_bootstrap_low_inr"] > 0
        and best["bh_q"] < 0.05
    )

    report = [
        "# Phase 10B — Signal persistence confirmation",
        "",
        "**Status:** COMPLETE — no strategy change adopted by this phase.",
        "",
        "## Research question",
        "",
        "Does requiring a positive exact-17-strike surface to persist for 5, 10, 15 or 30 minutes improve the frozen Phase 9G H1 strategy?",
        "",
        "## Operational definition",
        "",
        "The scan continues through every available intraday timestamp. At each exact-17 positive surface, the system looks exactly N minutes ahead on the same trading day. If that future surface is also exact-17 and positive, entry occurs at the confirmation timestamp and the normal maximum-positive-flatline strike selector is applied there. If confirmation fails, scanning continues to the next exact-17 positive timestamp.",
        "",
        "This preserves the no-skip rule while adding only a predeclared confirmation delay.",
        "",
        "## Frozen control",
        f"- 131 complete Phase 9G H1 trades",
        f"- Control net P&L: ₹{base['net_pnl_inr']:,.2f}",
        "",
        "## Results",
        "",
        summary.to_markdown(index=False),
        "",
        "## Paired inference",
        "",
        paired.to_markdown(index=False),
        "",
        "## Decision",
        "",
    ]
    if promotion:
        report.append("A confirmation delay passed the predeclared historical promotion screen. It is **not promoted yet**; Phase 10G chronological holdout is required.")
    else:
        report.append("No confirmation delay met the full predeclared promotion evidence. The frozen Phase 9G H1 control is retained.")
    report += [
        "",
        "## Limitations",
        "",
        "- Historical option observations are close-price proxies, not executable bid/ask quotes.",
        "- Confirmation is evaluated only at exact minute timestamps represented in the source index/option data; missing confirmation observations do not count as confirmation.",
        "- The test requires exact 17 unique strikes at both the initial positive observation and confirmation observation.",
    ]
    (out / "PHASE10B_RESULTS.md").write_text("\n".join(report) + "\n")
    (out / "promotion_screen.json").write_text(json.dumps({"passed": promotion, "best_variant": str(best["variant"])}, indent=2))
    print(json.dumps({"status": "complete", "control": base, "promotion_screen_passed": promotion, "paired": paired_rows}, indent=2, default=str))


if __name__ == "__main__":
    main()
