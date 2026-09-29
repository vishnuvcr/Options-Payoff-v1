#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from marginism import RiskEngine

OUTPUT_COLUMNS = ['entry_timestamp','entry_date','candidate_label','near_expiry','next_expiry','shift_points','strike','spot_at_entry','lot_size','chart_pnl_inr','chart_return_pct','gross_pnl_inr','net_pnl_inr','total_costs_inr','premium_turnover_inr','margin_required_inr','max_profit_pct_margin','span_inr','exposure_inr','option_premium_reported_inr','additional_inr','rank','source_spn_version']

def reconstruct_date(task):
    date_key, records, span_dir, span_version, symbols = task
    ymd = pd.Timestamp(date_key).strftime('%Y%m%d')
    paths = list(Path(span_dir).glob(f'nsccl.{ymd}.*.spn'))
    preferred = [p for p in paths if f'.{span_version.lower()}.' in p.name.lower()]
    if not preferred:
        raise FileNotFoundError(f'No SPN file for {date_key} variant={span_version}')
    spn = sorted(preferred)[0]
    engine = RiskEngine.from_file(str(spn), symbols=symbols)
    rows = []
    for r in records:
        qty=int(r['lot_size']); strike=float(r['strike'])
        position=[
          {'symbol':'NIFTY','instrument':'CE','expiry':str(r['near_expiry']),'strike':strike,'transaction_type':'SELL','quantity':qty},
          {'symbol':'NIFTY','instrument':'PE','expiry':str(r['near_expiry']),'strike':strike,'transaction_type':'BUY','quantity':qty},
          {'symbol':'NIFTY','instrument':'CE','expiry':str(r['next_expiry']),'strike':strike,'transaction_type':'BUY','quantity':qty},
          {'symbol':'NIFTY','instrument':'PE','expiry':str(r['next_expiry']),'strike':strike,'transaction_type':'SELL','quantity':qty},
        ]
        final=engine.basket(position,as_of_date=date_key)['data']['final']
        margin=float(final['total']); chart=float(r['chart_pnl_inr'])
        rows.append({
          'entry_timestamp':r['entry_timestamp'],'entry_date':date_key,'candidate_label':r.get('candidate_label',''),
          'near_expiry':r.get('near_expiry',''),'next_expiry':r.get('next_expiry',''),'shift_points':int(r['shift_points']),
          'strike':strike,'spot_at_entry':float(r['spot_at_entry']),'lot_size':qty,'chart_pnl_inr':chart,
          'chart_return_pct':float(r.get('chart_return_pct',float('nan'))),'gross_pnl_inr':float(r.get('gross_pnl_inr',float('nan'))),
          'net_pnl_inr':float(r.get('net_pnl_inr',float('nan'))),'total_costs_inr':float(r.get('total_costs_inr',float('nan'))),
          'premium_turnover_inr':float(r.get('premium_turnover_inr',float('nan'))),'margin_required_inr':margin,
          'max_profit_pct_margin':100.0*chart/margin if margin>0 else None,'span_inr':float(final['span']),
          'exposure_inr':float(final['exposure']),'option_premium_reported_inr':float(final['option_premium']),
          'additional_inr':float(final['additional']),'rank':int(r.get('rank',0)),'source_spn_version':spn.name,
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates',required=True); ap.add_argument('--span-dir',required=True); ap.add_argument('--out',required=True)
    ap.add_argument('--date-col',default='entry_date'); ap.add_argument('--span-version',default='i1'); ap.add_argument('--max-shift-points',type=int,default=400)
    ap.add_argument('--symbols',default='NIFTY'); ap.add_argument('--workers',type=int,default=6)
    args=ap.parse_args()
    df=pd.read_csv(args.candidates)
    df=df[df['shift_points'].between(-args.max_shift_points,args.max_shift_points)].copy()
    required={'entry_timestamp','entry_date','shift_points','strike','spot_at_entry','lot_size','chart_pnl_inr'}
    missing=required-set(df.columns)
    if missing: raise ValueError(f'missing columns: {sorted(missing)}')
    symbols=[s.strip() for s in args.symbols.split(',') if s.strip()]
    tasks=[(str(entry_date),g.to_dict('records'),args.span_dir,args.span_version,symbols) for entry_date,g in df.groupby(args.date_col,sort=True)]
    rows=[]
    with ProcessPoolExecutor(max_workers=max(1,args.workers)) as ex:
        futures=[ex.submit(reconstruct_date,t) for t in tasks]
        for fut in as_completed(futures):
            rows.extend(fut.result())
    result_df=pd.DataFrame(rows,columns=OUTPUT_COLUMNS)
    if not result_df.empty: result_df=result_df.sort_values(['entry_timestamp','shift_points'])
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); result_df.to_csv(out,index=False)
    print(f'rows={len(result_df)} timestamps={result_df.entry_timestamp.nunique() if not result_df.empty else 0} dates={len(tasks)} workers={max(1,args.workers)}')

if __name__=='__main__':
    main()
