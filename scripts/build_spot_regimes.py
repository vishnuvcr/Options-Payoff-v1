#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from math import sqrt
import numpy as np
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_parquet(args.inputs)
    need = {"entry_timestamp", "candidate_label", "spot_at_entry"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    x = (
        df.sort_values("entry_timestamp")
        .drop_duplicates("entry_timestamp")
        [["entry_timestamp", "entry_date", "spot_at_entry"]]
        .copy()
    )
    x["entry_timestamp"] = pd.to_datetime(x["entry_timestamp"], utc=True)
    x["spot_at_entry"] = pd.to_numeric(x["spot_at_entry"], errors="coerce")
    x = x.dropna(subset=["entry_timestamp", "spot_at_entry"]).sort_values("entry_timestamp").reset_index(drop=True)

    # All state variables use only observations strictly before the current 09:20 entry.
    s = x["spot_at_entry"]
    daily_ret = np.log(s / s.shift(1))
    x["entry_return_1d"] = s / s.shift(1) - 1.0
    x["trend_5d_return"] = s.shift(1) / s.shift(6) - 1.0
    x["trend_20d_return"] = s.shift(1) / s.shift(21) - 1.0
    x["realized_vol_20d_ann"] = daily_ret.shift(1).rolling(20).std() * sqrt(252.0)

    x["trend_regime"] = pd.Series(
        ["down" if v <= -0.01 else "up" if v >= 0.01 else "sideways" for v in x["trend_20d_return"]],
        index=x.index,
    )
    x["vol_regime"] = pd.Series(
        ["low" if v < 0.15 else "high" if v >= 0.25 else "medium" for v in x["realized_vol_20d_ann"]],
        index=x.index,
    )
    x["entry_move_regime"] = pd.Series(
        ["down_move" if v <= -0.005 else "up_move" if v >= 0.005 else "small_move" for v in x["entry_return_1d"]],
        index=x.index,
    )

    x["regime_source"] = "Phase-2 09:20 NIFTY spot series; point-in-time only"
    x["realized_vol_definition"] = "annualized std of prior 20 log returns"
    x["trend_definition"] = "prior-day 09:20 spot versus spot 20 observations earlier"
    x["entry_move_definition"] = "current 09:20 spot versus prior 09:20 spot"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    x.to_csv(out, index=False)


if __name__ == "__main__":
    main()
