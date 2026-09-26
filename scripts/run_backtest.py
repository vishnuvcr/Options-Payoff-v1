#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.costs import CostModel, four_leg_entry_cashflow, transaction_costs, trigger_base
from src.options_payoff import intrinsic_value

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--inputs', required=True)
    p.add_argument('--out-dir', default='results/phase3')
    p.add_argument('--lot-size', type=int, required=False, help='Override lot size for every row; normally omitted')
    p.add_argument('--threshold-pct', type=float, default=2.5)
    p.add_argument('--trigger-base-mode', choices=['buy_premium','spot_notional','configured_capital'], default='buy_premium')
    p.add_argument('--configured-capital-per-lot', type=float)
    p.add_argument('--slippage-pct', type=float, default=0.0025)
    p.add_argument('--fallback-max-shift-points', type=int, default=500)
    p.add_argument('--fallback-step-points', type=int, default=50)
    return p.parse_args()

def candidate_row_metrics(row, args, model):
    if hasattr(row, 'near_lot_size') and hasattr(row, 'next_lot_size'):
        near_lot=int(row.near_lot_size); next_lot=int(row.next_lot_size)
    else:
        near_lot=next_lot=args.lot_size
    if near_lot != next_lot:
        return None
    lot_size=args.lot_size if args.lot_size else near_lot
    premiums=[row.near_call_close,row.near_put_close,row.next_call_close,row.next_put_close]
    if any(pd.isna(x) for x in premiums) or pd.isna(row.near_settlement) or pd.isna(row.next_settlement):
        return None
    execs=four_leg_entry_cashflow(*premiums, slippage_pct=model.slippage_pct)
    raw_buy_premium = float(row.near_put_close) + float(row.next_call_close)
    base=trigger_base(
        args.trigger_base_mode,
        float(row.spot_at_entry),
        lot_size,
        raw_buy_premium,
        args.configured_capital_per_lot,
    )
    # The user's chart trigger is based on observed entry premiums, not the
    # execution-cost shock. Slippage is applied to realized P&L only.
    chart_pnl=float(row.net_entry_cashflow_per_unit)*lot_size
    chart_return=100.0*chart_pnl/base if base>0 else None
    gross_per_unit=float(execs['entry_cashflow_per_unit'])+float(row.next_settlement)-float(row.near_settlement)
    gross_pnl=gross_per_unit*lot_size
    long_call_intrinsic=intrinsic_value('CE',float(row.next_settlement),float(row.strike))
    long_put_intrinsic=intrinsic_value('PE',float(row.near_settlement),float(row.strike))
    costs=transaction_costs(pd.Timestamp(row.entry_timestamp).date(),execs['premium_turnover'],execs['sell_premium_turnover'],execs['buy_premium_turnover'],long_call_intrinsic,long_put_intrinsic,lot_size,model)
    net_pnl=gross_pnl-costs['total_costs']
    return {'chart_pnl_inr':chart_pnl,'chart_return_pct':chart_return,'gross_pnl_inr':gross_pnl,'net_pnl_inr':net_pnl,'total_costs_inr':costs['total_costs'],'premium_turnover_inr':execs['premium_turnover']*lot_size,**costs}

def main():
    args=parse_args()
    df=pd.read_parquet(args.inputs)
    required=['entry_timestamp','candidate_label','shift_points','strike','near_call_close','near_put_close','next_call_close','next_put_close','near_settlement','next_settlement','net_entry_cashflow_per_unit','near_lot_size','next_lot_size','status']
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError(f'missing columns: {missing}')
    model=CostModel(slippage_pct=args.slippage_pct)
    df=df[df.status.eq('ok')].copy()
    candidate_records=[]
    for row in df.itertuples(index=False):
        metrics=candidate_row_metrics(row,args,model)
        if metrics is None: continue
        candidate_records.append({'entry_timestamp':row.entry_timestamp,'entry_date':row.entry_date,'candidate_label':row.candidate_label,'shift_points':int(row.shift_points),'strike':row.strike,'near_expiry':row.near_expiry,'next_expiry':row.next_expiry,'spot_at_entry':row.spot_at_entry,'lot_size':(args.lot_size if args.lot_size else int(row.near_lot_size)),**metrics})
    candidates=pd.DataFrame(candidate_records)
    if candidates.empty: raise RuntimeError('No complete candidate rows available')
    max_shift=abs(args.fallback_max_shift_points)
    step=abs(args.fallback_step_points)
    if step == 0:
        raise ValueError('fallback-step-points must be > 0')
    selected=[]
    atm_selected=0
    fallback_selected=0
    for ts,group in candidates.groupby('entry_timestamp',sort=True):
        atm=group[group.shift_points.eq(0)]
        atm_qualifies=(not atm.empty and atm.iloc[0]['chart_return_pct'] is not None and float(atm.iloc[0]['chart_return_pct']) > args.threshold_pct)
        if atm_qualifies:
            r=atm.iloc[0].to_dict()
            r['selected_reason']='chart_trigger_atm'
            selected.append(r)
            atm_selected += 1
            continue
        fallbacks=group[
            (group.shift_points.abs() <= max_shift)
            & (group.shift_points != 0)
            & ((group.shift_points.abs() % step) == 0)
            & (group.chart_return_pct > args.threshold_pct)
        ].sort_values(by=['shift_points'], key=lambda s:s.abs())
        for _,r in fallbacks.iterrows():
            x=r.to_dict()
            x['selected_reason']='chart_trigger_fallback_grid'
            selected.append(x)
            fallback_selected += 1
    trades=pd.DataFrame(selected)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    candidates.to_parquet(out/'candidate_results.parquet',index=False)
    trades.to_parquet(out/'selected_trades.parquet',index=False)

    eligible_mask = candidates['chart_return_pct'].notna() & (candidates['chart_return_pct'] > args.threshold_pct)
    atm_mask = eligible_mask & candidates['shift_points'].eq(0)
    fallback_mask = eligible_mask & candidates['shift_points'].ne(0)
    entries=int(candidates['entry_timestamp'].nunique())
    selected_entries=int(trades['entry_timestamp'].nunique()) if not trades.empty else 0
    summary={
        'candidate_rows':int(len(candidates)),
        'eligible_entry_timestamps':entries,
        'selected_trade_rows':int(len(trades)),
        'selected_entry_timestamps':selected_entries,
        'atm_selected_trades':int(atm_selected),
        'fallback_grid_selected_trades':int(fallback_selected),
        'selection_rate_pct':float(100*selected_entries/entries) if entries else 0.0,
        'candidate_rows_above_threshold':int(eligible_mask.sum()),
        'atm_candidate_rows_above_threshold':int(atm_mask.sum()),
        'fallback_candidate_rows_above_threshold':int(fallback_mask.sum()),
        'max_chart_return_pct':float(candidates['chart_return_pct'].max()) if candidates['chart_return_pct'].notna().any() else None,
        'p95_chart_return_pct':float(candidates['chart_return_pct'].dropna().quantile(0.95)) if candidates['chart_return_pct'].notna().any() else None,
        'mean_net_pnl_inr':float(trades.net_pnl_inr.mean()) if not trades.empty else None,
        'median_net_pnl_inr':float(trades.net_pnl_inr.median()) if not trades.empty else None,
        'win_rate_pct':float(100*(trades.net_pnl_inr>0).mean()) if not trades.empty else None,
        'total_net_pnl_inr':float(trades.net_pnl_inr.sum()) if not trades.empty else 0.0,
        'total_costs_inr':float(trades.total_costs_inr.sum()) if not trades.empty else 0.0,
        'threshold_pct':args.threshold_pct,
        'trigger_base_mode':args.trigger_base_mode,
        'slippage_pct':args.slippage_pct,
        'fallback_max_shift_points':max_shift,
        'fallback_step_points':step,
        'lot_size':args.lot_size,
    }
    (out/'summary.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    print(json.dumps(summary,indent=2,default=str))

if __name__=='__main__': main()