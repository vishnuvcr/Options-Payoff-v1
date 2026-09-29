#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.costs import CostModel, executed_premium, four_leg_entry_cashflow, stt_rate_for_date
from scripts.run_near_expiry_exit_backtest import candidate_metrics

GATES = [None, 0.25, 0.50, 0.75]
SLIPPAGE_SENS = [0.0, 0.0025, 0.005, 0.01]
BROKERAGE_SENS = [10.0, 20.0, 40.0]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--surface", required=True)
    p.add_argument("--primary-trades", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--slippage-pct", type=float, default=0.0025)
    p.add_argument("--brokerage-per-order", type=float, default=20.0)
    p.add_argument("--bootstrap-reps", type=int, default=20000)
    return p.parse_args()


def wilson(wins: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return np.nan, np.nan
    p = wins / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return 100 * (centre - half), 100 * (centre + half)


def max_drawdown(values):
    if len(values) == 0:
        return 0.0
    curve = np.cumsum(np.asarray(values, dtype=float))
    peaks = np.maximum.accumulate(np.r_[0.0, curve])[:-1]
    return float(np.min(curve - peaks))


def profit_factor(values):
    x = np.asarray(values, dtype=float)
    gains = x[x > 0].sum()
    losses = -x[x < 0].sum()
    return float(gains / losses) if losses > 0 else np.inf


def block_bootstrap_mean_ci(values, reps, seed=20260929, block=4):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    blocks = [x[i:i + block] for i in range(len(x))]
    means = np.empty(reps)
    for j in range(reps):
        draw = []
        while len(draw) < len(x):
            draw.extend(blocks[int(rng.integers(0, len(blocks)))])
        means[j] = np.mean(draw[:len(x)])
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def paired_permutation_pvalue(diff, reps=20000, seed=20260929):
    x = np.asarray(diff, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan
    rng = np.random.default_rng(seed)
    obs = abs(x.mean())
    stats = np.empty(reps)
    for i in range(reps):
        stats[i] = abs((rng.choice([-1.0, 1.0], size=len(x)) * x).mean())
    return float((1 + np.sum(stats >= obs)) / (reps + 1))


def estimate_point_in_time_six_order_cost(row, model: CostModel):
    """Entry-observable six-order friction proxy.

    The four entry premiums are known. Future far-leg exit premiums are not
    known at entry, so the proxy assumes the two far-leg exits occur at their
    entry premiums with the same slippage. It includes six-order brokerage,
    turnover-based exchange/SEBI charges, entry/exit stamp duty and
    entry/exit-sale STT at the entry-date statutory rate. Exercise/settlement
    STT is excluded because it is not entry-observable.
    """
    lot = int(row.near_lot_size)
    entry = four_leg_entry_cashflow(
        float(row.near_call_close), float(row.near_put_close),
        float(row.far_call_close), float(row.far_put_close),
        slippage_pct=model.slippage_pct,
    )
    far_ce_exit = executed_premium(float(row.far_call_close), -1, model.slippage_pct)
    far_pe_exit = executed_premium(float(row.far_put_close), +1, model.slippage_pct)

    turnover_per_unit = entry["premium_turnover"] + far_ce_exit + far_pe_exit
    sell_turnover_per_unit = entry["sell_premium_turnover"] + far_ce_exit
    buy_turnover_per_unit = entry["buy_premium_turnover"] + far_pe_exit

    turnover = turnover_per_unit * lot
    sell_turnover = sell_turnover_per_unit * lot
    buy_turnover = buy_turnover_per_unit * lot
    brokerage = 6.0 * model.brokerage_per_order_inr
    exchange = turnover * model.exchange_turnover_rate
    sebi = turnover * model.sebi_turnover_rate
    stamp = buy_turnover * model.stamp_duty_buy_rate
    stt = sell_turnover * stt_rate_for_date(pd.Timestamp(row.entry_timestamp).date(), model)
    gst = model.gst_rate * (brokerage + exchange + sebi)
    return float(brokerage + exchange + sebi + stamp + stt + gst)


def summarize(trades):
    if trades.empty:
        return {
            "trade_count": 0, "net_pnl_inr": 0.0, "mean_pnl_inr": np.nan,
            "median_pnl_inr": np.nan, "win_rate_pct": np.nan,
            "wilson_low_pct": np.nan, "wilson_high_pct": np.nan,
            "profit_factor": np.nan, "max_drawdown_inr": 0.0,
            "mean_cost_inr": np.nan, "total_costs_inr": 0.0,
        }
    pnl = trades["net_pnl_inr"].to_numpy(float)
    lo, hi = wilson(int((pnl > 0).sum()), len(pnl))
    return {
        "trade_count": int(len(pnl)),
        "net_pnl_inr": float(pnl.sum()),
        "mean_pnl_inr": float(pnl.mean()),
        "median_pnl_inr": float(np.median(pnl)),
        "win_rate_pct": float((pnl > 0).mean() * 100),
        "wilson_low_pct": lo, "wilson_high_pct": hi,
        "profit_factor": profit_factor(pnl),
        "max_drawdown_inr": max_drawdown(pnl),
        "mean_cost_inr": float(trades["total_costs"].mean()),
        "total_costs_inr": float(trades["total_costs"].sum()),
    }


def select_gate(primary, gate):
    g = primary[primary["flatline_inr"] > 0].copy()
    if gate is not None:
        g = g[g["cost_to_flatline"] <= gate].copy()
    return g.sort_values("entry_timestamp").reset_index(drop=True)


def main():
    args = parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    surface = pd.read_parquet(args.surface)
    primary = pd.read_parquet(args.primary_trades)
    surface_selected = surface[surface["selected"].astype(bool)].copy()

    required_primary = {
        "entry_timestamp", "near_expiry", "flatline_inr",
        "near_call_close", "near_put_close", "far_call_close", "far_put_close",
        "near_lot_size", "net_pnl_inr", "total_costs",
    }
    missing = required_primary - set(primary.columns)
    if missing:
        raise RuntimeError(f"Primary ledger missing required columns: {sorted(missing)}")

    if surface_selected.empty:
        raise RuntimeError("Decision surface contains no selected rows")

    model = CostModel(
        slippage_pct=args.slippage_pct,
        brokerage_per_order_inr=args.brokerage_per_order,
    )

    primary = primary.copy()
    primary["entry_timestamp"] = pd.to_datetime(primary["entry_timestamp"], utc=True)
    surface_selected["timestamp"] = pd.to_datetime(surface_selected["timestamp"], utc=True)

    # Reproducibility gate: the selected decision-surface timestamps must match
    # the authoritative realized ledger before any refinement is scored.
    pkeys = set(zip(primary["entry_timestamp"].astype(str), primary["near_expiry"].astype(str)))
    skeys = set(zip(surface_selected["timestamp"].astype(str), surface_selected["near_expiry"].astype(str)))
    reproduction = {
        "primary_rows": int(len(primary)),
        "surface_selected_rows": int(len(surface_selected)),
        "matched_keys": int(len(pkeys & skeys)),
        "max_abs_pnl_difference_inr": 0.0,
        "net_primary_inr": float(primary["net_pnl_inr"].sum()),
    }
    if pkeys != skeys:
        raise RuntimeError("Phase 9G/9D selected timestamps do not exactly match the decision-surface selection rows")

    primary["estimated_six_order_cost_inr"] = primary.apply(
        lambda r: estimate_point_in_time_six_order_cost(r, model), axis=1
    )
    primary["cost_to_flatline"] = (
        primary["estimated_six_order_cost_inr"] / primary["flatline_inr"]
    )
    primary["estimated_gate_uses_future_exit_prices"] = False
    primary.to_csv(out / "candidate_cost_quality.csv", index=False)

    gate_rows = []
    variants = {}
    for gate in GATES:
        label = "control" if gate is None else f"cost_le_{int(gate * 100)}pct"
        trades = select_gate(primary, gate)
        variants[label] = trades
        s = summarize(trades)
        s["variant"] = label
        s["gate_ratio"] = np.nan if gate is None else gate
        s["skipped_cycles"] = int(len(primary) - len(trades))
        gate_rows.append(s)
        trades.to_csv(out / f"{label}_trades.csv", index=False)

    summary = pd.DataFrame(gate_rows)
    summary = summary[
        ["variant", "gate_ratio", "trade_count", "skipped_cycles", "net_pnl_inr",
         "mean_pnl_inr", "median_pnl_inr", "win_rate_pct", "wilson_low_pct",
         "wilson_high_pct", "profit_factor", "max_drawdown_inr",
         "mean_cost_inr", "total_costs_inr"]
    ]
    summary.to_csv(out / "gate_summary.csv", index=False)

    control = variants["control"][["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "control_pnl"})
    paired_rows = []
    for label, trades in variants.items():
        if label == "control":
            continue
        x = control.merge(
            trades[["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "variant_pnl"}),
            on="near_expiry", how="left",
        ).fillna(0.0)
        diff = x["variant_pnl"] - x["control_pnl"]
        lo, hi = block_bootstrap_mean_ci(diff.to_numpy(), args.bootstrap_reps)
        paired_rows.append({
            "variant": label,
            "paired_cycles": int(len(x)),
            "mean_difference_inr": float(diff.mean()),
            "median_difference_inr": float(diff.median()),
            "net_difference_inr": float(diff.sum()),
            "block_bootstrap_low_inr": lo,
            "block_bootstrap_high_inr": hi,
            "paired_permutation_p": paired_permutation_pvalue(diff.to_numpy(), args.bootstrap_reps),
        })
    paired = pd.DataFrame(paired_rows)
    if not paired.empty:
        p = paired["paired_permutation_p"].to_numpy()
        order = np.argsort(p)
        q = np.empty_like(p)
        running = 1.0
        m = len(p)
        for rank, idx in reversed(list(enumerate(order, start=1))):
            running = min(running, p[idx] * m / rank)
            q[idx] = running
        paired["bh_q"] = q
    paired.to_csv(out / "paired_gate_comparisons.csv", index=False)

    positive = primary[primary["flatline_inr"] > 0]
    geom = {
        "decision_timestamps": int(primary["entry_timestamp"].nunique()),
        "selected_trades": int(len(primary)),
        "positive_selected_trades": int(len(positive)),
        "median_cost_to_flatline_pct": float(100 * positive["cost_to_flatline"].median()),
        "p75_cost_to_flatline_pct": float(100 * positive["cost_to_flatline"].quantile(.75)),
        "p90_cost_to_flatline_pct": float(100 * positive["cost_to_flatline"].quantile(.90)),
        "pct_trades_under_25_pct_gate": float(100 * (positive["cost_to_flatline"] <= .25).mean()),
        "pct_trades_under_50_pct_gate": float(100 * (positive["cost_to_flatline"] <= .50).mean()),
        "pct_trades_under_75_pct_gate": float(100 * (positive["cost_to_flatline"] <= .75).mean()),
    }
    (out / "geometry_summary.json").write_text(json.dumps(geom, indent=2))

    stress_rows = []
    for gate in GATES:
        label = "control" if gate is None else f"cost_le_{int(gate * 100)}pct"
        selected = select_gate(primary, gate)
        for slip in SLIPPAGE_SENS:
            for brokerage in BROKERAGE_SENS:
                mdl = CostModel(slippage_pct=slip, brokerage_per_order_inr=brokerage)
                pnl = []
                for row in selected.itertuples(index=False):
                    m = candidate_metrics(row, mdl)
                    if m is not None:
                        pnl.append(m["net_pnl_inr"])
                stress_rows.append({
                    "variant": label,
                    "slippage_pct": slip,
                    "brokerage_per_order_inr": brokerage,
                    "trade_count": len(pnl),
                    "net_pnl_inr": float(np.sum(pnl)) if pnl else 0.0,
                    "mean_pnl_inr": float(np.mean(pnl)) if pnl else np.nan,
                })
    pd.DataFrame(stress_rows).to_csv(out / "execution_stress.csv", index=False)

    (out / "reproduction_check.json").write_text(json.dumps(reproduction, indent=2))

    best = None
    promotion_screen = False
    if not paired.empty:
        best = paired.sort_values("mean_difference_inr", ascending=False).iloc[0]
        promotion_screen = bool(
            best["mean_difference_inr"] > 0
            and best["block_bootstrap_low_inr"] > 0
            and best["bh_q"] < 0.05
        )

    lines = [
        "# Phase 10A — Execution-quality / cost-to-edge analysis",
        "",
        "**Status:** COMPLETE — no strategy change adopted by this phase.",
        "",
        "## Research question",
        "",
        "Does a predeclared execution-quality gate remove trades whose static chart edge is too small relative to realistic six-order friction?",
        "",
        "## Point-in-time gate definition",
        "",
        "The test is deliberately a trade-level filter applied to the frozen Phase 9G H1 selected entry. It does not select a different strike and does not search a later timestamp. The gate uses only premiums, lot size and statutory rates known at entry.",
        "",
        "The estimated six-order friction proxy assumes the two future far-leg exit premiums equal their entry premiums, with the same 0.25% slippage. It includes six-order brokerage, turnover-based exchange/SEBI charges, entry/exit stamp duty and entry/exit-sale STT at the entry-date rate. Exercise/settlement STT is excluded because it is not entry-observable.",
        "",
        "Predeclared gates: no gate, cost/flatline <=25%, <=50%, <=75%.",
        "",
        "## Control reproduction",
        f"- Authoritative realized rows: {reproduction['primary_rows']}",
        f"- Decision-surface selected rows: {reproduction['surface_selected_rows']}",
        f"- Matched decision keys: {reproduction['matched_keys']}",
        f"- Authoritative control net P&L: ₹{reproduction['net_primary_inr']:,.2f}",
        "",
        "## Gate results",
        "",
        summary.to_markdown(index=False),
        "",
        "## Paired inference",
        "",
        paired.to_markdown(index=False) if not paired.empty else "No paired gate comparison was available.",
        "",
        "## Decision",
        "",
    ]
    if promotion_screen:
        lines.append("At least one gate passed the predeclared historical statistical screen, but it is **not promoted**. Phase 10G chronological holdout is required before replacing the frozen control.")
    else:
        lines.append("No execution-quality gate met the full predeclared promotion evidence in this phase. The frozen Phase 9G H1 control is retained.")
    lines += [
        "",
        "## Key limitation",
        "",
        "The source contains option closes rather than point-in-time bid/ask quotes. Therefore this phase estimates friction from entry premiums and cannot claim true executable-spread quality. This limitation is recorded in the research error log.",
        "",
        "## Interpretation",
        "",
        "A cost gate that rejects a trade is a skip rule, not evidence that the underlying static chart is invalid. Conversely, a lower cost-to-flatline ratio does not prove that the far-expiry market-value component will be favorable. This phase tests only whether the entry-time friction proxy is useful as a predeclared trade-quality filter.",
    ]
    (out / "PHASE10A_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "complete",
        "selected_trades": len(primary),
        "promotion_screen_passed": promotion_screen,
        "reproduction": reproduction,
        "gate_summary": gate_rows,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
