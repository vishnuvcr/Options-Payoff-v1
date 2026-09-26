#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--trades", required=True)
    p.add_argument("--out", default="results/phase4/brokerage_sensitivity.csv")
    p.add_argument("--baseline-brokerage", type=float, default=20.0)
    p.add_argument("--rates", default="10,20,40")
    args = p.parse_args()

    df = pd.read_parquet(args.trades)
    if df.empty:
        raise RuntimeError("No selected trades")
    rates = [float(x.strip()) for x in args.rates.split(",") if x.strip()]
    n = len(df)
    baseline_total = float(df["net_pnl_inr"].sum())

    rows = []
    for rate in rates:
        total = baseline_total + n * 4.0 * (args.baseline_brokerage - rate)
        mean = total / n
        rows.append(
            {
                "brokerage_per_order_inr": rate,
                "n_trades": n,
                "total_net_pnl_inr": total,
                "mean_net_pnl_inr": mean,
                "delta_vs_20_inr": total - baseline_total,
                "note": "Adjustment uses the fixed four-entry-order cost structure in the Phase 3 model.",
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(json.dumps({"output": str(out), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
