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
    p.add_argument('--fallback-order', default='ATM_MINUS_400,ATM_PLUS_400')
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
    base=trigger_base(args.trigger_base_mode,float(row.spot_at_entry),lot_size,execs['buy_premium_turnover'])
    chart_pnl=float(row.net_entry_cashflow_per_unit)*lot_size
    chart_return=100.0*chart_pnl/base if base>0 else None
    gross_per_unit=float(row.net_entry_cashflow_per_unit)+float(row.next_settlement)-float(row.near_settlement)
    gross_pnl=gross_per_unit*lot_size
    long_call_intrinsic=intrinsic_value('CE',float(row.next_settlement),float(row.strike))
    long_put_intrinsic=intrinsic_value('PE',float(row.near_settlement),float(row.strike))
    costs=transaction_costs(pd.Timestamp(row.entry_timestamp).date(),execs['premium_turnover'],execs['sell_premium_turnover'],execs['buy_premium_turnover'],long_call_intrinsic,long_put_intrinsic,lot_size,model)
    net_pnl=gross_pnl-costs['total_costs']
    return {'chart_pnl_inr':chart_pnl,'chart_return_pct':chart_return,'gross_pnl_inr':gross_pnl,'net_pnl_inr':net_pnl,'total_costs_inr':costs['total_costs'],'premium_turnover_inr':execs['premium_turnover']*args.lot_size,**costs}

def main():
    args=parse_args()
    df=pd.read_parquet(args.inputs)
    required=['entry_timestamp','candidate_label','strike','near_call_close','near_put_close','next_call_close','next_put_close','near_settlement','next_settlement','net_entry_cashflow_per_unit','status']
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError(f'missing columns: {missing}')
    model=CostModel(slippage_pct=args.slippage_pct)
    df=df[df.status.eq('ok')].copy()
    candidate_records=[]
    for row in df.itertuples(index=False):
        metrics=candidate_row_metrics(row,args,model)
        if metrics is None: continue
        candidate_records.append({'entry_timestamp':row.entry_timestamp,'entry_date':row.entry_date,'candidate_label':row.candidate_label,'strike':row.strike,'near_expiry':row.near_expiry,'next_expiry':row.next_expiry,'spot_at_entry':row.spot_at_entry,'lot_size':(args.lot_size if args.lot_size else int(row.near_lot_size)),**metrics})
    candidates=pd.DataFrame(candidate_records)
    if candidates.empty: raise RuntimeError('No complete candidate rows available')
    order=['ATM']+[x.strip() for x in args.fallback_order.split(',') if x.strip()]
    selected=[]
    for ts,group in candidates.groupby('entry_timestamp',sort=True):
        by_label={r.candidate_label:r for r in group.itertuples(index=False)}
        chosen=None
        for label in order:
            r=by_label.get(label)
            if r is not None and r.chart_return_pct is not None and r.chart_return_pct > args.threshold_pct:
                chosen=r; break
        if chosen is not None:
            selected.append({**chosen._asdict(),'selected_reason':'chart_trigger'})
    trades=pd.DataFrame(selected)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    candidates.to_parquet(out/'candidate_results.parquet',index=False)
    trades.to_parquet(out/'selected_trades.parquet',index=False)
    entries=int(candidates['entry_timestamp'].nunique())
    summary={'candidate_rows':int(len(candidates)),'eligible_entry_timestamps':entries,'selected_trades':int(len(trades)),'selection_rate_pct':float(100*len(trades)/entries) if entries else 0.0,'mean_net_pnl_inr':float(trades.net_pnl_inr.mean()) if not trades.empty else None,'median_net_pnl_inr':float(trades.net_pnl_inr.median()) if not trades.empty else None,'win_rate_pct':float(100*(trades.net_pnl_inr>0).mean()) if not trades.empty else None,'total_net_pnl_inr':float(trades.net_pnl_inr.sum()) if not trades.empty else 0.0,'total_costs_inr':float(trades.total_costs_inr.sum()) if not trades.empty else 0.0,'threshold_pct':args.threshold_pct,'trigger_base_mode':args.trigger_base_mode,'slippage_pct':args.slippage_pct,'lot_size':args.lot_size}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    print(json.dumps(summary,indent=2,default=str))

if __name__=='__main__': main()