#!/usr/bin/env python3
"""Validate the frozen Phase 9D H1 realized-trade ledger.

This phase deliberately avoids pandas/pyarrow so the validation can also run in
minimal environments. Inputs are the CSVs already archived by Phase 9D.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def metric(rows: list[dict[str, str]]) -> dict[str, float | int | None]:
    vals = [f(r, "net_pnl_inr") for r in rows]
    if not vals:
        return {
            "trades": 0,
            "net_pnl_inr": 0.0,
            "mean_net_pnl_inr": None,
            "median_net_pnl_inr": None,
            "win_rate_pct": None,
            "profit_factor": None,
            "max_drawdown_inr": 0.0,
            "total_costs_inr": 0.0,
            "largest_win_inr": None,
            "largest_loss_inr": None,
        }
    wins = [x for x in vals if x > 0]
    losses = [x for x in vals if x < 0]
    gross_profit = sum(wins)
    gross_loss = -sum(losses)
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for x in vals:
        equity += x
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return {
        "trades": len(vals),
        "net_pnl_inr": sum(vals),
        "mean_net_pnl_inr": statistics.mean(vals),
        "median_net_pnl_inr": statistics.median(vals),
        "win_rate_pct": 100.0 * len(wins) / len(vals),
        "profit_factor": (gross_profit / gross_loss) if gross_loss else math.inf,
        "max_drawdown_inr": max_dd,
        "total_costs_inr": sum(f(r, "total_costs") for r in rows),
        "largest_win_inr": max(vals),
        "largest_loss_inr": min(vals),
    }


def wilson_ci(wins: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = wins / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) / n) + z * z / (4.0 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def iid_bootstrap(values: list[float], reps: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(reps):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lo = means[int(0.025 * reps)]
    hi = means[int(0.975 * reps) - 1]
    return lo, hi


def circular_block_bootstrap(values: list[float], block_len: int, reps: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(values)
    blocks_needed = math.ceil(n / block_len)
    means = []
    for _ in range(reps):
        total = 0.0
        count = 0
        for _ in range(blocks_needed):
            start = rng.randrange(n)
            for j in range(block_len):
                total += values[(start + j) % n]
                count += 1
                if count == n:
                    break
            if count == n:
                break
        means.append(total / n)
    means.sort()
    lo = means[int(0.025 * reps)]
    hi = means[int(0.975 * reps) - 1]
    return lo, hi


def year(row: dict[str, str]) -> int:
    return int(row["entry_date"][:4])


def as_time(row: dict[str, str]) -> str:
    return datetime.fromisoformat(row["entry_timestamp"]).time().isoformat()


def annual_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for y in sorted({year(r) for r in rows}):
        cohort = [r for r in rows if year(r) == y]
        m = metric(cohort)
        wins = sum(f(r, "net_pnl_inr") > 0 for r in cohort)
        lo, hi = wilson_ci(wins, len(cohort))
        m.update(
            {
                "calendar_year": y,
                "win_rate_wilson_low_pct": 100.0 * lo,
                "win_rate_wilson_high_pct": 100.0 * hi,
            }
        )
        out.append(m)
    return out


def anchored_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    ys = sorted({year(r) for r in rows})
    out = []
    for y in ys:
        if y == ys[0]:
            continue
        train = [r for r in rows if year(r) < y]
        test = [r for r in rows if year(r) == y]
        tm = metric(test)
        wins = sum(f(r, "net_pnl_inr") > 0 for r in test)
        lo, hi = wilson_ci(wins, len(test))
        out.append(
            {
                "test_year": y,
                "historical_years_before_test": len({year(r) for r in train}),
                "train_trades": len(train),
                "train_net_pnl_inr": metric(train)["net_pnl_inr"],
                "test_trades": tm["trades"],
                "test_net_pnl_inr": tm["net_pnl_inr"],
                "test_mean_net_pnl_inr": tm["mean_net_pnl_inr"],
                "test_win_rate_pct": tm["win_rate_pct"],
                "test_profit_factor": tm["profit_factor"],
                "test_max_drawdown_inr": tm["max_drawdown_inr"],
                "test_win_rate_wilson_low_pct": 100.0 * lo,
                "test_win_rate_wilson_high_pct": 100.0 * hi,
            }
        )
    return out


def execution_sensitivity(evidence_dir: Path) -> list[dict[str, object]]:
    out = []
    for p in sorted(evidence_dir.glob("results/phase9d_slip_*/intraday_selected_trades.csv")):
        name = p.parent.name.replace("phase9d_slip_", "")
        # Stored directory names encode decimal dots as p, e.g. 0p0025.
        slip = float(name.replace("p", "."))
        r = read_csv(p)
        m = metric(r)
        out.append(
            {
                "scenario": name,
                "slippage_pct": slip * 100.0,
                "brokerage_per_order_inr": 20.0,
                **m,
            }
        )
    for broker in (10, 20, 40):
        p = evidence_dir / f"results/phase9d_broker_{broker}/intraday_selected_trades.csv"
        if p.exists():
            r = read_csv(p)
            out.append(
                {
                    "scenario": f"broker_{broker}",
                    "slippage_pct": 0.25,
                    "brokerage_per_order_inr": float(broker),
                    **metric(r),
                }
            )
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--bootstrap-reps", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=20260927)
    args = ap.parse_args()

    primary = args.evidence_dir / "results/phase9d_primary/intraday_selected_trades.csv"
    incomplete = args.evidence_dir / "results/phase9d_primary/intraday_incomplete_selected_trades.csv"
    if not primary.exists():
        raise SystemExit(f"Missing authoritative selected-trade CSV: {primary}")

    rows = read_csv(primary)
    if len(rows) != 169:
        raise SystemExit(f"Expected 169 complete realized trades, found {len(rows)}")
    if any(f(r, "estimated_equal_max_profit_loss_inr") <= 0 for r in rows):
        raise SystemExit("Frozen-rule invariant failed: selected static flatline is not positive.")
    if any(r["estimated_all_green_flatline"].lower() != "true" for r in rows):
        raise SystemExit("Frozen-rule invariant failed: selected chart is not all-green.")
    if any(year(r) < 2021 or year(r) > 2026 for r in rows):
        raise SystemExit("Unexpected calendar year in authoritative ledger.")

    # Point-in-time/chronology checks.
    for r in rows:
        entry = datetime.fromisoformat(r["entry_timestamp"])
        near_exit = datetime.fromisoformat(r["near_exit_timestamp"])
        if entry >= near_exit:
            raise SystemExit(f"Entry is not before near-expiry exit: {r['entry_timestamp']}")
        if r["far_call_exit_timestamp"] and datetime.fromisoformat(r["far_call_exit_timestamp"]) > near_exit:
            raise SystemExit("Far call exit occurs after near expiry.")
        if r["far_put_exit_timestamp"] and datetime.fromisoformat(r["far_put_exit_timestamp"]) > near_exit:
            raise SystemExit("Far put exit occurs after near expiry.")

    # Incomplete selection audit is intentionally preserved.
    incomplete_rows = read_csv(incomplete) if incomplete.exists() else []
    reasons = defaultdict(int)
    for r in incomplete_rows:
        reasons[r.get("reason", "unknown")] += 1

    primary_metrics = metric(rows)
    wins = sum(f(r, "net_pnl_inr") > 0 for r in rows)
    wr_lo, wr_hi = wilson_ci(wins, len(rows))

    annual = annual_rows(rows)
    anchored = anchored_rows(rows)
    sens = execution_sensitivity(args.evidence_dir)

    values = [f(r, "net_pnl_inr") for r in rows]
    iid_lo, iid_hi = iid_bootstrap(values, args.bootstrap_reps, args.seed)
    block_lo, block_hi = circular_block_bootstrap(values, 4, args.bootstrap_reps, args.seed + 1)

    time_bands = {
        "09:20-09:59": [],
        "10:00-11:59": [],
        "12:00-13:59": [],
        "14:00-15:29": [],
    }
    shift_bands = defaultdict(list)
    for r in rows:
        hhmm = as_time(r)[:5]
        if "09:20" <= hhmm <= "09:59":
            time_bands["09:20-09:59"].append(r)
        elif "10:00" <= hhmm <= "11:59":
            time_bands["10:00-11:59"].append(r)
        elif "12:00" <= hhmm <= "13:59":
            time_bands["12:00-13:59"].append(r)
        else:
            time_bands["14:00-15:29"].append(r)
        shift_bands[int(float(r["shift_points"]))].append(r)

    timing_summary = [
        {"entry_time_band": k, **metric(v)} for k, v in time_bands.items() if v
    ]
    shift_summary = [
        {"shift_points": k, **metric(v)} for k, v in sorted(shift_bands.items())
    ]

    # Validation classification intentionally avoids a "deployable" label.
    all_years_positive = all(x["net_pnl_inr"] > 0 for x in annual)
    all_anchor_positive = all(x["test_net_pnl_inr"] > 0 for x in anchored)
    uncertainty_includes_zero = iid_lo <= 0.0 or block_lo <= 0.0
    validation_state = (
        "historically_positive_but_uncertain"
        if primary_metrics["net_pnl_inr"] > 0 and uncertainty_includes_zero
        else "historically_positive_with_positive_bootstrap_lower_bound"
        if primary_metrics["net_pnl_inr"] > 0
        else "historical_result_not_positive"
    )

    summary = {
        "phase": "9E",
        "status": "complete",
        "source_run_id": 36302077730,
        "source_artifact": "phase-9D-final-H1-evidence",
        "rule_frozen": True,
        "complete_realized_trades": len(rows),
        "incomplete_selected_trades": len(incomplete_rows),
        "incomplete_reasons": dict(reasons),
        "primary_metrics": primary_metrics,
        "primary_win_rate_wilson_95_ci_pct": [100.0 * wr_lo, 100.0 * wr_hi],
        "bootstrap": {
            "iid_mean_pnl_95_ci_inr": [iid_lo, iid_hi],
            "circular_block4_mean_pnl_95_ci_inr": [block_lo, block_hi],
            "repetitions": args.bootstrap_reps,
            "seed": args.seed,
        },
        "calendar_years_all_positive": all_years_positive,
        "anchored_holdout_years_all_positive": all_anchor_positive,
        "validation_state": validation_state,
        "note": (
            "Temporal holdouts are rule-frozen historical diagnostics, not pristine "
            "future-data validation, because the same 2021-2026 sample was observed during "
            "strategy development. No parameters were tuned on holdout results."
        ),
    }

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "annual.csv", annual)
    write_csv(out / "anchored_holdouts.csv", anchored)
    write_csv(out / "execution_sensitivity.csv", sens)
    write_csv(out / "entry_time_bands.csv", timing_summary)
    write_csv(out / "shift_bands.csv", shift_summary)
    (out / "bootstrap.json").write_text(
        json.dumps(summary["bootstrap"], indent=2), encoding="utf-8"
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = []
    report.append("# Phase 9E — Frozen-rule H1 validation")
    report.append("")
    report.append(f"Authoritative source run: **{summary['source_run_id']}**")
    report.append("")
    report.append(
        "This phase keeps the Phase 9D entry, strike-selection, exit and transaction-cost "
        "rules frozen. It does not introduce or tune a new filter."
    )
    report.append("")
    report.append("## Primary result")
    report.append("")
    report.append(f"- Complete realized trades: **{primary_metrics['trades']}**")
    report.append(f"- Net P&L: **₹{primary_metrics['net_pnl_inr']:,.2f}**")
    report.append(f"- Mean trade P&L: **₹{primary_metrics['mean_net_pnl_inr']:,.2f}**")
    report.append(f"- Win rate: **{primary_metrics['win_rate_pct']:.2f}%**")
    report.append(f"- Profit factor: **{primary_metrics['profit_factor']:.3f}**")
    report.append(f"- Maximum drawdown: **₹{primary_metrics['max_drawdown_inr']:,.2f}**")
    report.append(
        f"- Win-rate Wilson 95% CI: **{100.0*wr_lo:.2f}% to {100.0*wr_hi:.2f}%**"
    )
    report.append("")
    report.append("## Uncertainty")
    report.append("")
    report.append(
        f"- IID bootstrap 95% CI for mean P&L: **₹{iid_lo:,.2f} to ₹{iid_hi:,.2f}**"
    )
    report.append(
        f"- Circular four-trade block bootstrap 95% CI: **₹{block_lo:,.2f} to ₹{block_hi:,.2f}**"
    )
    report.append("")
    report.append("## Calendar-year cohorts")
    report.append("")
    report.append("| Year | Trades | Net P&L | Mean | Win rate | PF | Max DD |")
    report.append("|---:|---:|---:|---:|---:|---:|---:|")
    for x in annual:
        report.append(
            f"| {x['calendar_year']} | {x['trades']} | ₹{x['net_pnl_inr']:,.2f} | "
            f"₹{x['mean_net_pnl_inr']:,.2f} | {x['win_rate_pct']:.2f}% | "
            f"{x['profit_factor']:.3f} | ₹{x['max_drawdown_inr']:,.2f} |"
        )
    report.append("")
    report.append("## Anchored chronological holdouts")
    report.append("")
    report.append(
        "| Test year | Prior-trade count | Test trades | Test net P&L | Test win rate | Test PF |"
    )
    report.append("|---:|---:|---:|---:|---:|---:|")
    for x in anchored:
        report.append(
            f"| {x['test_year']} | {x['train_trades']} | {x['test_trades']} | "
            f"₹{x['test_net_pnl_inr']:,.2f} | {x['test_win_rate_pct']:.2f}% | "
            f"{x['test_profit_factor']:.3f} |"
        )
    report.append("")
    report.append("## Execution sensitivity")
    report.append("")
    report.append("| Scenario | Slippage | Brokerage/order | Trades | Net P&L | Win rate | PF |")
    report.append("|---|---:|---:|---:|---:|---:|---:|")
    for x in sens:
        report.append(
            f"| {x['scenario']} | {x['slippage_pct']:.2f}% | ₹{x['brokerage_per_order_inr']:,.0f} | "
            f"{x['trades']} | ₹{x['net_pnl_inr']:,.2f} | {x['win_rate_pct']:.2f}% | "
            f"{x['profit_factor']:.3f} |"
        )
    report.append("")
    report.append("## Incomplete selections")
    report.append("")
    report.append(
        f"{len(incomplete_rows)} Phase 9D selections remain excluded from realized P&L because their near/far expiry lot sizes were incompatible."
    )
    report.append("")
    report.append("## Interpretation")
    report.append("")
    report.append(
        "The rule remained historically profitable in the archived sample and in the "
        "calendar-year/anchored test diagnostics, but the bootstrap intervals still cross zero. "
        "Accordingly this phase treats the result as **historically positive but uncertain**, "
        "not as evidence of a guaranteed or deployable edge."
    )
    report.append("")
    report.append(
        "The temporal diagnostics are not a pristine future holdout because the 2021-2026 sample "
        "was already available during strategy development. The next genuinely independent "
        "validation requires a new, untouched data period."
    )
    report.append("")
    report.append("## Timing and strike-shift diagnostics")
    report.append("")
    report.append(
        "Entry-time and shift-band files are descriptive diagnostics only; no new filter is adopted from them in Phase 9E."
    )
    (out / "PHASE9E_VALIDATION.md").write_text(chr(10).join(report) + chr(10), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
