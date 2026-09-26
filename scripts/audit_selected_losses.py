#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

REQUIRED = [
    "entry_timestamp","entry_date","candidate_label","shift_points","strike",
    "near_expiry","next_expiry","spot_at_entry","lot_size","chart_pnl_inr",
    "chart_return_pct","gross_pnl_inr","net_pnl_inr","total_costs_inr",
    "premium_turnover_inr","brokerage","exchange_transaction","sebi_fee",
    "stamp_duty","stt_entry","stt_exercise","gst","exercised_intrinsic_inr",
    "selected_reason",
]

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--selected-trades", required=True)
    p.add_argument("--out-dir", default="results/loss_audit")
    p.add_argument("--expected-trades", type=int, default=63)
    return p.parse_args()

def fmt_inr(x):
    return f"₹{x:,.2f}"

def main():
    args=parse_args()
    df=pd.read_parquet(args.selected_trades)
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: {}".format(missing))
    df["entry_timestamp"]=pd.to_datetime(df["entry_timestamp"], errors="coerce")
    df["entry_date"]=pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    df=df.sort_values(["entry_timestamp","shift_points","strike"]).reset_index(drop=True)

    losses=df[df["net_pnl_inr"]<0].copy()
    wins=df[df["net_pnl_inr"]>0].copy()

    losses["gross_to_chart_drag_inr"]=losses["gross_pnl_inr"]-losses["chart_pnl_inr"]
    losses["fee_drag_inr"]=losses["net_pnl_inr"]-losses["gross_pnl_inr"]
    losses["is_pre_fee_loss"]=losses["gross_pnl_inr"]<0
    losses["is_cost_only_flip"]=(losses["gross_pnl_inr"]>=0)&(losses["net_pnl_inr"]<0)
    losses["loss_share_pct"]=(-losses["net_pnl_inr"]/-losses["net_pnl_inr"].sum())*100.0
    losses["abs_shift_points"]=losses["shift_points"].abs()
    losses["selection_family"]=losses["shift_points"].apply(lambda x: "ATM" if int(x)==0 else "Fallback")
    losses=losses.sort_values(["net_pnl_inr","entry_timestamp"], ascending=[True,True]).reset_index(drop=True)
    losses["loss_rank"]=losses.index+1

    total=float(df["net_pnl_inr"].sum())
    wins_total=float(wins["net_pnl_inr"].sum())
    losses_total=float(losses["net_pnl_inr"].sum())
    reconciliation_error=total-(wins_total+losses_total)

    summary={
        "selected_trade_rows":int(len(df)),
        "loss_count":int(len(losses)),
        "win_count":int(len(wins)),
        "flat_count":int((df["net_pnl_inr"]==0).sum()),
        "total_net_pnl_inr":total,
        "gross_wins_inr":wins_total,
        "gross_losses_inr":losses_total,
        "reconciliation_error_inr":reconciliation_error,
        "loss_rate_pct":float(100.0*len(losses)/len(df)) if len(df) else None,
        "largest_loss_inr":float(losses["net_pnl_inr"].min()) if len(losses) else None,
        "median_loss_inr":float(losses["net_pnl_inr"].median()) if len(losses) else None,
        "mean_loss_inr":float(losses["net_pnl_inr"].mean()) if len(losses) else None,
        "total_costs_on_losses_inr":float(losses["total_costs_inr"].sum()),
        "pre_fee_loss_count":int(losses["is_pre_fee_loss"].sum()),
        "cost_only_flip_count":int(losses["is_cost_only_flip"].sum()),
        "fallback_loss_count":int((losses["shift_points"]!=0).sum()),
        "atm_loss_count":int((losses["shift_points"]==0).sum()),
        "worst_date":str(losses.loc[losses["net_pnl_inr"].idxmin(),"entry_date"]) if len(losses) else None,
    }

    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    loss_cols=[
        "loss_rank","entry_timestamp","entry_date","selection_family","candidate_label",
        "selected_reason","shift_points","abs_shift_points","strike","near_expiry",
        "next_expiry","spot_at_entry","lot_size","chart_return_pct","chart_pnl_inr",
        "gross_pnl_inr","gross_to_chart_drag_inr","total_costs_inr","fee_drag_inr",
        "net_pnl_inr","loss_share_pct","premium_turnover_inr","brokerage",
        "exchange_transaction","sebi_fee","stamp_duty","stt_entry","stt_exercise",
        "gst","exercised_intrinsic_inr","is_pre_fee_loss","is_cost_only_flip",
    ]
    losses[loss_cols].to_csv(out/"loss_trades.csv", index=False)

    by_shift=(
        losses.groupby(["selection_family","shift_points"], as_index=False)
        .agg(losses=("net_pnl_inr","size"), total_loss=("net_pnl_inr","sum"),
             mean_loss=("net_pnl_inr","mean"), median_loss=("net_pnl_inr","median"),
             worst_loss=("net_pnl_inr","min"), total_costs=("total_costs_inr","sum"),
             total_pre_fee_pnl=("gross_pnl_inr","sum"))
        .sort_values("total_loss")
    )
    by_date=(
        losses.groupby("entry_date", as_index=False)
        .agg(losses=("net_pnl_inr","size"), total_loss=("net_pnl_inr","sum"),
             worst_loss=("net_pnl_inr","min"), total_costs=("total_costs_inr","sum"))
        .sort_values("total_loss")
    )
    by_shift.to_csv(out/"losses_by_shift.csv",index=False)
    by_date.to_csv(out/"losses_by_date.csv",index=False)
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    md=[
        "# Loss-trade audit — corrected 63-row grid backtest","",
        "This audit reads the Phase 3 selected-trade artifact directly; it does not regenerate or alter the strategy selection.","",
        "## Reconciliation","",
        "- Selected rows: **{}** (expected {})".format(len(df),args.expected_trades),
        "- Winning rows: **{}**".format(len(wins)),
        "- Losing rows: **{}**".format(len(losses)),
        "- Total net P&L: **{}**".format(fmt_inr(total)),
        "- Wins contribution: **{}**".format(fmt_inr(wins_total)),
        "- Loss contribution: **{}**".format(fmt_inr(losses_total)),
        "- Reconciliation error: **{}**".format(fmt_inr(reconciliation_error)),
        "",
        "## What causes a selected trade to lose?","",
        "Every selected row passed the chart trigger under the working buy-premium denominator. The loss diagnosis separates the positive entry-chart edge from the subsequent cross-expiry economic outcome and modeled fees.","",
        "- Losses with negative gross P&L before fees: **{} / {}**".format(int(losses["is_pre_fee_loss"].sum()),len(losses)),
        "- Losses created only by fees from non-negative gross P&L: **{} / {}**".format(int(losses["is_cost_only_flip"].sum()),len(losses)),
        "- ATM losses: **{}**".format(int((losses["shift_points"]==0).sum())),
        "- Fallback losses: **{}**".format(int((losses["shift_points"]!=0).sum())),
        "- Total modeled costs on losing trades: **{}**".format(fmt_inr(float(losses["total_costs_inr"].sum()))),
        "",
        "## Every losing trade","",
        "| Rank | Date | Shift | Strike | Spot | Chart % | Chart P&L | Gross P&L | Costs | Net P&L | Near Expiry | Next Expiry |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _,r in losses.iterrows():
        md.append("| {} | {} | {:+d} | {:.0f} | {:.2f} | {:.2f}% | {} | {} | {} | {} | {} | {} |".format(
            int(r["loss_rank"]),r["entry_date"],int(r["shift_points"]),r["strike"],r["spot_at_entry"],
            r["chart_return_pct"],fmt_inr(r["chart_pnl_inr"]),fmt_inr(r["gross_pnl_inr"]),
            fmt_inr(r["total_costs_inr"]),fmt_inr(r["net_pnl_inr"]),r["near_expiry"],r["next_expiry"]
        ))

    md += [
        "","## Losses by strike shift","",
        "| Family | Shift | Loss count | Total loss | Mean loss | Worst loss | Total costs | Pre-fee P&L |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in by_shift.iterrows():
        md.append("| {} | {:+d} | {} | {} | {} | {} | {} | {} |".format(
            r["selection_family"],int(r["shift_points"]),int(r["losses"]),fmt_inr(r["total_loss"]),
            fmt_inr(r["mean_loss"]),fmt_inr(r["worst_loss"]),fmt_inr(r["total_costs"]),fmt_inr(r["total_pre_fee_pnl"])
        ))

    md += ["","## Losses by entry date","",
           "| Date | Loss count | Total loss | Worst loss | Costs |",
           "|---|---:|---:|---:|---:|"]
    for _,r in by_date.iterrows():
        md.append("| {} | {} | {} | {} | {} |".format(
            r["entry_date"],int(r["losses"]),fmt_inr(r["total_loss"]),fmt_inr(r["worst_loss"]),fmt_inr(r["total_costs"])
        ))

    md += ["","## Cost anatomy",""]
    for col in ["brokerage","exchange_transaction","sebi_fee","stamp_duty","stt_entry","stt_exercise","gst"]:
        md.append("- {}: {}".format(col,fmt_inr(float(losses[col].sum()))))
    md += ["","## Interpretation","",
           "chart_pnl_inr is the positive entry-chart quantity used for selection. gross_pnl_inr is the slippage-adjusted economic P&L before modeled fees. net_pnl_inr is after modeled costs. Therefore a loss with negative gross P&L is already an economic loss before fees; a cost-only flip is loss created by fees."]
    (out/"LOSS_TRADE_ANALYSIS.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
