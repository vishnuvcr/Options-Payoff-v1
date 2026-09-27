#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.run_near_expiry_exit_backtest import CostModel, candidate_metrics

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--inputs',required=True)
    p.add_argument('--out-dir',required=True)
    p.add_argument('--slippage-pct',type=float,default=0.0025)
    p.add_argument('--brokerage-per-order',type=float,default=20.0)
    return p.parse_args()

def main():
    args=parse_args()
    model=CostModel(slippage_pct=args.slippage_pct,brokerage_per_order_inr=args.brokerage_per_order)
    df=pd.read_parquet(args.inputs)
    if df.empty:
        raise RuntimeError('No intraday selected trades found')
    rows=[]
    incomplete=[]
    for row in df.itertuples(index=False):
        m=candidate_metrics(row,model)
        if m is None:
            missing=[]
            for field in ['near_call_close','near_put_close','far_call_close','far_put_close','near_settlement','far_call_exit_close','far_put_exit_close','near_lot_size','far_lot_size']:
                if not hasattr(row, field) or pd.isna(getattr(row, field)):
                    missing.append(field)
            incomplete.append({
                'entry_timestamp':row.entry_timestamp,'entry_date':row.entry_date,
                'near_expiry':row.near_expiry,'far_expiry':row.far_expiry,
                'strike':row.strike,'shift_points':row.shift_points,
                'reason':reason,'missing_fields':','.join(missing),
                'missing_fields':','.join(missing),
            })
            continue
        rows.append({
            'entry_timestamp':row.entry_timestamp,
            'entry_date':pd.Timestamp(row.entry_timestamp).date(),
            'candidate_label':'ATM' if int(row.shift_points)==0 else ('ATM_PLUS_%d'%abs(int(row.shift_points)) if int(row.shift_points)>0 else 'ATM_MINUS_%d'%abs(int(row.shift_points))),
            'shift_points':int(row.shift_points),'strike':float(row.strike),
            'near_expiry':row.near_expiry,'far_expiry':row.far_expiry,
            'near_exit_timestamp':row.near_exit_timestamp,
            'far_call_exit_timestamp':row.far_call_exit_timestamp,
            'far_put_exit_timestamp':row.far_put_exit_timestamp,
            **m
        })
    trades=pd.DataFrame(rows)
    if not trades.empty:
        trades=trades.sort_values('entry_timestamp').reset_index(drop=True)
    incomplete_df=pd.DataFrame(incomplete)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    trades.to_csv(out/'intraday_selected_trades.csv',index=False)
    trades.to_parquet(out/'intraday_selected_trades.parquet',index=False)
    incomplete_df.to_csv(out/'intraday_incomplete_selected_trades.csv',index=False)
    summary={
        'weekly_cycles':int(trades['near_expiry'].nunique()),
        'selected_weekly_cycles':int(df['near_expiry'].nunique()),
        'selected_trades':int(len(df)),
        'realized_trade_rows':int(len(trades)),
        'incomplete_selected_trades':int(len(incomplete_df)),
        'chart_positive_win_rate_pct':float(100*(df['flatline_inr']>0).mean()),
        'realized_win_rate_pct':float(100*(trades['net_pnl_inr']>0).mean()) if not trades.empty else None,
        'net_pnl_inr':float(trades['net_pnl_inr'].sum()),
        'gross_pnl_inr':float(trades['gross_pnl_inr'].sum()),
        'total_costs_inr':float(trades['total_costs'].sum()),
        'mean_net_pnl_inr':float(trades['net_pnl_inr'].mean()) if not trades.empty else None,
        'median_net_pnl_inr':float(trades['net_pnl_inr'].median()) if not trades.empty else None,
        'losing_trades':int((trades['net_pnl_inr']<0).sum()),
        'slippage_pct':args.slippage_pct,
        'brokerage_per_order_inr':args.brokerage_per_order,
        'selection_rule':'first intraday timestamp from 09:20 onward with any positive flatline; at that timestamp choose maximum positive flatline across ATM-400..ATM+400',
        'no_0920_skip_rule':True,
    }
    (out/'summary_intraday_near_exit.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    print(json.dumps(summary,indent=2,default=str))

if __name__=='__main__':
    main()
