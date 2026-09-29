#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    list_nifty_expiry_files,
    load_index,
    load_option_file,
    nifty_lot_size,
    last_index_bar_on_date,
)
from scripts.run_near_expiry_exit_backtest import (
    CostModel,
    executed_premium,
    stt_rate_for_date,
    four_leg_entry_cashflow,
    static_flatline_value,
    estimated_equal_max_profit_loss,
)


OFFSETS = {
    "baseline": None,
    "60m": 60,
    "120m": 120,
    "180m": 180,
    "1d": "1d",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--selected", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--download-workers", type=int, default=4)
    p.add_argument("--slippage-pct", type=float, default=0.0025)
    p.add_argument("--brokerage-per-order", type=float, default=20.0)
    return p.parse_args()


def previous_trading_close(index_df, expiry):
    dates = sorted(pd.to_datetime(index_df["trading_date"]).dt.date.unique())
    prev = [d for d in dates if d < expiry]
    if not prev:
        return None, None
    return last_index_bar_on_date(index_df, prev[-1])


def common_option_quote(near_df, far_df, strike, target):
    n = near_df[
        (near_df["strike"] == float(strike))
        & (near_df["option_type"].isin(["CE", "PE"]))
        & (near_df["timestamp"] <= target)
    ][["timestamp", "option_type", "close"]].copy()
    f = far_df[
        (far_df["strike"] == float(strike))
        & (far_df["option_type"].isin(["CE", "PE"]))
        & (far_df["timestamp"] <= target)
    ][["timestamp", "option_type", "close"]].copy()
    if n.empty or f.empty:
        return None
    n = n.drop_duplicates(["timestamp", "option_type"], keep="last")
    f = f.drop_duplicates(["timestamp", "option_type"], keep="last")
    npiv = n.pivot(index="timestamp", columns="option_type", values="close")
    fpiv = f.pivot(index="timestamp", columns="option_type", values="close")
    both = npiv.join(fpiv, how="inner", lsuffix="_near", rsuffix="_far")
    needed = ["CE_near", "PE_near", "CE_far", "PE_far"]
    both = both.dropna(subset=needed)
    if both.empty:
        return None
    ts = both.index.max()
    r = both.loc[ts]
    return {
        "timestamp": ts,
        "near_call": float(r["CE_near"]),
        "near_put": float(r["PE_near"]),
        "far_call": float(r["CE_far"]),
        "far_put": float(r["PE_far"]),
    }


def early_costs(entry_date, exit_date, entry_exec, exit_near_call, exit_near_put,
                exit_far_call, exit_far_put, lot, model):
    entry_turnover = entry_exec["premium_turnover"]
    entry_sell = entry_exec["sell_premium_turnover"]
    entry_buy = entry_exec["buy_premium_turnover"]
    exit_turnover = exit_near_call + exit_near_put + exit_far_call + exit_far_put
    # At exit: near CE and far PE are buys; near PE and far CE are sells.
    exit_sell = exit_near_put + exit_far_call
    exit_buy = exit_near_call + exit_far_put
    turnover = (entry_turnover + exit_turnover) * lot
    sell_turnover = (entry_sell + exit_sell) * lot
    buy_turnover = (entry_buy + exit_buy) * lot
    brokerage = 6.0 * model.brokerage_per_order_inr
    exchange = turnover * model.exchange_turnover_rate
    sebi = turnover * model.sebi_turnover_rate
    stamp_entry = entry_buy * lot * model.stamp_duty_buy_rate
    stamp_exit = exit_buy * lot * model.stamp_duty_buy_rate
    stt_entry_sales = entry_sell * lot * stt_rate_for_date(entry_date, model)
    stt_exit_sales = exit_sell * lot * stt_rate_for_date(exit_date, model)
    gst = model.gst_rate * (brokerage + exchange + sebi)
    total = (
        brokerage + exchange + sebi + stamp_entry + stamp_exit
        + stt_entry_sales + stt_exit_sales + gst
    )
    return {
        "brokerage": brokerage,
        "exchange_transaction": exchange,
        "sebi_fee": sebi,
        "stamp_duty_entry": stamp_entry,
        "stamp_duty_exit": stamp_exit,
        "stt_entry_sales": stt_entry_sales,
        "stt_exit_sales": stt_exit_sales,
        "gst": gst,
        "total_costs": total,
    }


def compute_trade(row, quote, exit_spot, exit_date, model):
    lot = int(row.near_lot_size)
    entry = four_leg_entry_cashflow(
        float(row.near_call_close), float(row.near_put_close),
        float(row.far_call_close), float(row.far_put_close),
        slippage_pct=model.slippage_pct,
    )
    nc = executed_premium(quote["near_call"], +1, model.slippage_pct)
    np_ = executed_premium(quote["near_put"], -1, model.slippage_pct)
    fc = executed_premium(quote["far_call"], -1, model.slippage_pct)
    fp = executed_premium(quote["far_put"], +1, model.slippage_pct)

    # Entry cashflow + exit cashflow of all four legs.
    gross_per_unit = entry["entry_cashflow_per_unit"] - nc + np_ + fc - fp
    costs = early_costs(
        pd.Timestamp(row.entry_timestamp).date(), exit_date, entry,
        nc, np_, fc, fp, lot, model,
    )
    flatline = static_flatline_value(
        float(row.strike), str(row.near_expiry), str(row.far_expiry),
        float(row.near_call_close), float(row.near_put_close),
        float(row.far_call_close), float(row.far_put_close),
    )
    equal = estimated_equal_max_profit_loss(flatline, lot)
    return {
        "exit_timestamp": quote["timestamp"],
        "exit_spot": float(exit_spot),
        "gross_pnl_inr": gross_per_unit * lot,
        "net_pnl_inr": gross_per_unit * lot - costs["total_costs"],
        "total_costs": costs["total_costs"],
        "chart_pnl_inr": flatline * lot,
        "estimated_equal_max_profit_loss_inr": equal["estimated_equal_max_profit_loss_inr"],
        "premium_turnover_inr": (entry["premium_turnover"] + nc + np_ + fc + fp) * lot,
        **costs,
    }


def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = CostModel(
        slippage_pct=args.slippage_pct,
        brokerage_per_order_inr=args.brokerage_per_order,
    )

    selected = pd.read_csv(args.selected)
    selected["entry_timestamp"] = pd.to_datetime(selected["entry_timestamp"], utc=True)
    selected["near_expiry"] = pd.to_datetime(selected["near_expiry"]).dt.date
    selected["far_expiry"] = pd.to_datetime(selected["far_expiry"]).dt.date
    if selected.empty:
        raise RuntimeError("Selected ledger is empty")

    index_df = load_index()
    index_df["trading_date"] = pd.to_datetime(index_df["trading_date"]).dt.date
    index_lookup = index_df.set_index("timestamp")["close"]
    expiry_files = dict(list_nifty_expiry_files(start, end))

    rows_by_year = []
    for row in selected.sort_values("entry_timestamp").itertuples(index=False):
        near_expiry = row.near_expiry
        far_expiry = row.far_expiry
        expiry_ts, _ = last_index_bar_on_date(index_df, near_expiry)
        if expiry_ts is None:
            continue
        targets = {"baseline": expiry_ts}
        for name, offset in OFFSETS.items():
            if name == "baseline":
                continue
            if offset == "1d":
                ts, _ = previous_trading_close(index_df, near_expiry)
                targets[name] = ts
            else:
                targets[name] = expiry_ts - pd.Timedelta(minutes=offset)

        valid_targets = [x for x in targets.values() if x is not None]
        min_ts, max_ts = min(valid_targets), max(valid_targets)
        if near_expiry not in expiry_files or far_expiry not in expiry_files:
            raise RuntimeError(f"Missing expiry file for {near_expiry}/{far_expiry}")

        near_df = load_option_file(
            near_expiry, expiry_files[near_expiry],
            timestamp_min=min_ts - pd.Timedelta(days=1),
            timestamp_max=max_ts,
        )
        far_df = load_option_file(
            far_expiry, expiry_files[far_expiry],
            timestamp_min=min_ts - pd.Timedelta(days=1),
            timestamp_max=max_ts,
        )

        for name, target in targets.items():
            if target is None:
                rows_by_year.append({"entry_timestamp": row.entry_timestamp, "near_expiry": near_expiry, "variant": name, "status": "unavailable"})
                continue
            quote = common_option_quote(near_df, far_df, row.strike, target)
            if quote is None:
                rows_by_year.append({"entry_timestamp": row.entry_timestamp, "near_expiry": near_expiry, "variant": name, "status": "unavailable"})
                continue
            spot = index_lookup.get(quote["timestamp"])
            if pd.isna(spot):
                rows_by_year.append({"entry_timestamp": row.entry_timestamp, "near_expiry": near_expiry, "variant": name, "status": "unavailable"})
                continue
            m = compute_trade(row, quote, float(spot), quote["timestamp"].date(), model)
            rows_by_year.append({
                "entry_timestamp": row.entry_timestamp,
                "entry_date": pd.Timestamp(row.entry_timestamp).date(),
                "near_expiry": near_expiry,
                "far_expiry": far_expiry,
                "variant": name,
                "strike": float(row.strike),
                "shift_points": int(row.shift_points),
                "candidate_label": row.candidate_label,
                "status": "ok",
                **m,
            })
        del near_df, far_df

    result = pd.DataFrame(rows_by_year)
    result.to_csv(out / "exit_timing_trade_ledger.csv", index=False)

    summary = []
    for variant, g in result.groupby("variant", sort=False):
        ok = g[g["status"] == "ok"].copy()
        pnl = ok["net_pnl_inr"].to_numpy(float)
        if len(pnl):
            curve = np.cumsum(pnl)
            dd = float(np.min(curve - np.maximum.accumulate(np.r_[0.0, curve])[:-1]))
            wins = pnl[pnl > 0].sum()
            losses = -pnl[pnl < 0].sum()
            pf = wins / losses if losses else np.inf
        else:
            dd, pf = 0.0, np.nan
        summary.append({
            "variant": variant,
            "trades": int(len(ok)),
            "unavailable": int((g["status"] != "ok").sum()),
            "net_pnl_inr": float(pnl.sum()) if len(pnl) else 0.0,
            "mean_pnl_inr": float(pnl.mean()) if len(pnl) else np.nan,
            "median_pnl_inr": float(np.median(pnl)) if len(pnl) else np.nan,
            "win_rate_pct": float(100 * (pnl > 0).mean()) if len(pnl) else np.nan,
            "profit_factor": float(pf),
            "max_drawdown_inr": dd,
            "total_costs_inr": float(ok["total_costs"].sum()) if len(ok) else 0.0,
            "p10_pnl_inr": float(np.quantile(pnl, .10)) if len(pnl) else np.nan,
            "worst_trade_inr": float(np.min(pnl)) if len(pnl) else np.nan,
        })
    pd.DataFrame(summary).to_csv(out / "exit_timing_summary.csv", index=False)
    (out / "metadata.json").write_text(json.dumps({
        "dataset": DATASET,
        "variants": list(OFFSETS),
        "baseline": "near-expiry close",
        "60m_120m_180m": "minutes before near-expiry index close",
        "1d": "last available index bar on previous trading day",
        "exit_execution": "all four legs closed at the latest common option timestamp at or before target",
        "cost_model": {"slippage_pct": args.slippage_pct, "brokerage_per_order": args.brokerage_per_order},
        "no_exercise_stt_for_early_exit": True,
    }, indent=2, default=str))
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
