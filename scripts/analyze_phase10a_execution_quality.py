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
    x = np.asarray(values, dtype=float)
    curve = np.cumsum(x)
    return float(np.min(curve - np.maximum.accumulate(np.r_[0.0, curve])[:-1]))


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
    n = len(x)
    blocks = [x[i:i+block] for i in range(n)]
    means = np.empty(reps)
    for j in range(reps):
        draw = []
        while len(draw) < n:
            draw.extend(blocks[int(rng.integers(0, len(blocks)))])
        means[j] = np.mean(draw[:n])
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def paired_permutation_pvalue(diff, reps=20000, seed=20260929):
    x = np.asarray(diff, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan
    rng = np.random.default_rng(seed)
    obs = abs(x.mean())
    signs = rng.choice(np.array([-1.0, 1.0]), size=(reps, len(x)))
    stats = np.abs((signs * x).mean(axis=1))
    return float((1 + np.sum(stats >= obs)) / (reps + 1))


def estimate_point_in_time_six_order_cost(row, model: CostModel):
    """Entry-observable six-order friction proxy.

    Four entry premiums are observed. The two future exit premiums are not
    observable, so the proxy assumes the far CE sale and far PE buy occur at
    their entry premiums with the same slippage. It includes brokerage,
    exchange/SEBI charges, entry/exit stamp duty and entry/exit-sale STT using
    the entry-date statutory rate. It deliberately excludes exercise/settlement
    STT because that is not entry-observable.
    """
    lot = int(row.near_lot_size)
    entry = four_leg_entry_cashflow(
        float(row.near_call), float(row.near_put),
        float(row.far_call), float(row.far_put),
        slippage_pct=model.slippage_pct,
    )
    far_ce_exit = executed_premium(float(row.far_call), -1, model.slippage_pct)
    far_pe_exit = executed_premium(float(row.far_put), +1, model.slippage_pct)

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
    stt = sell_turnover * stt_rate_for_date(pd.Timestamp(row.timestamp).date(), model)
    gst = model.gst_rate * (brokerage + exchange + sebi)
    total = brokerage + exchange + sebi + stamp + stt + gst
    return float(total)


def actual_candidate_ledger(surface, model):
    rows = []
    for row in surface.itertuples(index=False):
        m = candidate_metrics(row, model)
        if m is None:
            continue
        rows.append({
            "timestamp": row.timestamp,
            "entry_date": pd.Timestamp(row.timestamp).date(),
            "near_expiry": row.near_expiry,
            "far_expiry": row.far_expiry,
            "shift_points": int(row.shift_points),
            "strike": float(row.strike),
            "flatline_inr": float(row.flatline_inr),
            "estimated_all_green_flatline": bool(row.flatline_inr > 0),
            "estimated_six_order_cost_inr": estimate_point_in_time_six_order_cost(row, model),
            "near_call": float(row.near_call),
            "near_put": float(row.near_put),
            "far_call": float(row.far_call),
            "far_put": float(row.far_put),
            **m,
        })
    return pd.DataFrame(rows)


def select_variant(candidates, gate):
    g = candidates.copy()
    g = g[g["flatline_inr"] > 0].copy()
    if gate is not None:
        g = g[(g["estimated_six_order_cost_inr"] / g["flatline_inr"]) <= gate].copy()
    if g.empty:
        return g
    g = g.sort_values(
        ["near_expiry", "timestamp", "flatline_inr", "shift_points"],
        ascending=[True, True, False, True],
    )
    return g.groupby("near_expiry", sort=True, as_index=False).head(1).copy()


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
        "trade_count": int(len(trades)),
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


def main():
    args = parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    surface = pd.read_parquet(args.surface)
    primary = pd.read_parquet(args.primary_trades)

    required = {"timestamp", "near_expiry", "flatline_inr", "near_call", "near_put", "far_call", "far_put"}
    missing = required - set(surface.columns)
    if missing:
        raise RuntimeError(f"Decision surface missing required columns: {sorted(missing)}")

    model = CostModel(
        slippage_pct=args.slippage_pct,
        brokerage_per_order_inr=args.brokerage_per_order,
    )
    candidates = actual_candidate_ledger(surface, model)
    if candidates.empty:
        raise RuntimeError("No complete candidate rows could be evaluated")

    candidates["cost_to_flatline"] = candidates["estimated_six_order_cost_inr"] / candidates["flatline_inr"]
    candidates.to_csv(out / "candidate_cost_quality.csv", index=False)

    # The frozen control is the rank-1 positive candidate at each existing
    # Phase 9G decision timestamp. It must reproduce the accepted ledger.
    control = select_variant(candidates, None)
    primary_dates = pd.to_datetime(primary["entry_timestamp"]).dt.tz_localize(None).dt.normalize()
    control_dates = pd.to_datetime(control["timestamp"]).dt.tz_localize(None).dt.normalize()
    control = control.copy()
    control["entry_timestamp"] = control["timestamp"]
    control["primary_match_date"] = control_dates.isin(set(primary_dates))
    if control["trade_count"] if "trade_count" in control else False:
        pass

    gate_rows = []
    variant_trades = {}
    for gate in GATES:
        label = "control" if gate is None else f"cost_le_{int(gate*100)}pct"
        trades = select_variant(candidates, gate)
        variant_trades[label] = trades
        s = summarize(trades)
        s["variant"] = label
        s["gate_ratio"] = np.nan if gate is None else gate
        s["positive_candidates_available"] = int((candidates["flatline_inr"] > 0).sum())
        s["eligible_candidates"] = int(
            len(candidates) if gate is None else
            (candidates["flatline_inr"] > 0).mul(candidates["cost_to_flatline"] <= gate).sum()
        )
        gate_rows.append(s)
        trades.to_csv(out / f"{label}_trades.csv", index=False)

    summary = pd.DataFrame(gate_rows)
    control_pnl = variant_trades["control"][["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "control_pnl"})
    paired_rows = []
    for label, trades in variant_trades.items():
        if label == "control":
            continue
        x = control_pnl.merge(
            trades[["near_expiry", "net_pnl_inr"]].rename(columns={"net_pnl_inr": "variant_pnl"}),
            on="near_expiry", how="outer",
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
    summary.to_csv(out / "gate_summary.csv", index=False)

    # Entry-time opportunity geometry.
    geom = candidates[candidates["flatline_inr"] > 0].copy()
    geom_summary = {
        "candidate_rows": int(len(candidates)),
        "decision_timestamps": int(candidates["timestamp"].nunique()),
        "positive_candidate_rows": int(len(geom)),
        "positive_candidate_rate_pct": float(100 * len(geom) / len(candidates)),
        "median_cost_to_flatline_pct": float(100 * geom["cost_to_flatline"].median()),
        "p75_cost_to_flatline_pct": float(100 * geom["cost_to_flatline"].quantile(0.75)),
        "p90_cost_to_flatline_pct": float(100 * geom["cost_to_flatline"].quantile(0.90)),
        "pct_positive_under_25_pct_gate": float(100 * (geom["cost_to_flatline"] <= .25).mean()),
        "pct_positive_under_50_pct_gate": float(100 * (geom["cost_to_flatline"] <= .50).mean()),
        "pct_positive_under_75_pct_gate": float(100 * (geom["cost_to_flatline"] <= .75).mean()),
    }
    (out / "geometry_summary.json").write_text(json.dumps(geom_summary, indent=2, default=str))

    # Execution stress on each gate using the same entry-time gate membership.
    stress_rows = []
    for gate in GATES:
        label = "control" if gate is None else f"cost_le_{int(gate*100)}pct"
        selected_ids = set(variant_trades[label]["near_expiry"].astype(str))
        base = candidates.copy()
        eligible = base[base["flatline_inr"] > 0].copy()
        if gate is not None:
            eligible = eligible[eligible["cost_to_flatline"] <= gate]
        eligible = eligible.sort_values(["near_expiry", "timestamp", "flatline_inr"], ascending=[True, True, False])
        eligible = eligible.groupby("near_expiry", sort=True, as_index=False).head(1)
        for slip in SLIPPAGE_SENS:
            for brokerage in BROKERAGE_SENS:
                mdl = CostModel(slippage_pct=slip, brokerage_per_order_inr=brokerage)
                pnl = []
                for row in eligible.itertuples(index=False):
                    # candidate_metrics requires the raw realized exit inputs,
                    # so rebuild a minimal row from the surface.
                    surfrow = surface[
                        (surface["timestamp"] == row.timestamp) &
                        (surface["near_expiry"] == row.near_expiry) &
                        (surface["shift_points"] == row.shift_points)
                    ]
                    if surfrow.empty:
                        continue
                    m = candidate_metrics(surfrow.iloc[0], mdl)
                    if m is not None:
                        pnl.append(m["net_pnl_inr"])
                stress_rows.append({
                    "variant": label, "slippage_pct": slip,
                    "brokerage_per_order_inr": brokerage,
                    "trade_count": len(pnl),
                    "net_pnl_inr": float(np.sum(pnl)) if pnl else 0.0,
                    "mean_pnl_inr": float(np.mean(pnl)) if pnl else np.nan,
                })
    pd.DataFrame(stress_rows).to_csv(out / "execution_stress.csv", index=False)

    # Reproduction check against the authoritative Phase 9G control.
    # Match on expiry and entry timestamp and compare net P&L where available.
    prim = primary.copy()
    prim["entry_timestamp"] = pd.to_datetime(prim["entry_timestamp"], utc=True)
    ctrl = variant_trades["control"].copy()
    ctrl["entry_timestamp"] = pd.to_datetime(ctrl["timestamp"], utc=True)
    merged = prim[["entry_timestamp", "near_expiry", "net_pnl_inr"]].merge(
        ctrl[["entry_timestamp", "near_expiry", "net_pnl_inr"]],
        on=["entry_timestamp", "near_expiry"], how="inner", suffixes=("_primary", "_reconstructed"),
    )
    reproduction = {
        "primary_rows": int(len(prim)),
        "control_rows": int(len(ctrl)),
        "matched_rows": int(len(merged)),
        "max_abs_pnl_difference_inr": float(np.max(np.abs(merged["net_pnl_inr_primary"] - merged["net_pnl_inr_reconstructed"]))) if not merged.empty else None,
        "net_primary_inr": float(prim["net_pnl_inr"].sum()),
        "net_reconstructed_inr": float(ctrl["net_pnl_inr"].sum()),
    }
    (out / "reproduction_check.json").write_text(json.dumps(reproduction, indent=2, default=str))

    # Markdown result is deliberately generated by the same workflow that
    # computes the tables, avoiding a hand-edited conclusion.
    best = paired.sort_values("mean_difference_inr", ascending=False).iloc[0].to_dict() if not paired.empty else None
    promotion = False
    if best is not None:
        promotion = (
            best["mean_difference_inr"] > 0
            and best["block_bootstrap_low_inr"] > 0
            and best.get("bh_q", 1.0) < 0.05
        )
    lines = [
        "# Phase 10A — Execution-quality / cost-to-edge analysis",
        "",
        "**Status:** COMPLETE — no strategy change adopted by this phase.",
        "",
        "## Point-in-time gate definition",
        "",
        "At each frozen Phase 9G decision timestamp, all positive candidates are evaluated. The gate uses only entry-observable premiums and lot size. The estimated six-order friction proxy assumes the two future far-leg exit premiums equal their entry premiums, with the same 0.25% slippage. It includes six-order brokerage, turnover-based exchange/SEBI charges, entry/exit stamp duty and entry/exit-sale STT at the entry-date rate. Exercise/settlement STT is excluded because it is not entry-observable.",
        "",
        "Predeclared gates: no gate, cost/flatline <=25%, <=50%, <=75%.",
        "",
        "## Control reproduction",
        f"- Matched rows: {reproduction['matched_rows']} / {reproduction['primary_rows']}",
        f"- Maximum absolute P&L difference: {reproduction['max_abs_pnl_difference_inr']}",
        f"- Primary net P&L: ₹{reproduction['net_primary_inr']:,.2f}",
        f"- Reconstructed control net P&L: ₹{reproduction['net_reconstructed_inr']:,.2f}",
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
    if promotion:
        lines.append("A gate met the predeclared statistical screen on the tested historical population. It is **not promoted yet**: Phase 10G chronological holdout is required before any change to the frozen control.")
    else:
        lines.append("No execution-quality gate met the full predeclared promotion evidence in this phase. The frozen Phase 9G H1 control is retained. Phase 10A does not justify a strategy change.")
    lines += [
        "",
        "## Limitations",
        "",
        "- The source contains close-only option observations rather than point-in-time bid/ask quotes, so this is an execution-friction proxy, not a true executable spread model.",
        "- The six-order proxy cannot observe future far-leg exit prices at entry; the entry-price proxy is used specifically to avoid look-ahead.",
        "- The test begins at the already-established Phase 9G first-positive decision timestamp. It does not create a new later-entry rule when the gate rejects that timestamp.",
        "- Results are historical research evidence, not a guarantee of future execution or profit.",
    ]
    (out / "PHASE10A_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "complete",
        "candidates": len(candidates),
        "decision_timestamps": int(candidates["timestamp"].nunique()),
        "control_trades": len(control),
        "promotion_screen_passed": promotion,
        "reproduction": reproduction,
        "gate_summary": gate_rows,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
