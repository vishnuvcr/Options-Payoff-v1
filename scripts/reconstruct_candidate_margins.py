#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from marginism import RiskEngine

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates',required=True)
    ap.add_argument('--span-dir',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--date-col',default='entry_date')
    ap.add_argument('--span-version',default='i1')
    ap.add_argument('--skip-missing',action='store_true')
    ap.add_argument('--max-shift-points',type=int,default=400)
    ap.add_argument('--symbols',default='NIFTY',
                    help='Comma-separated SPAN portfolio symbols to parse; default NIFTY only.')
    args=ap.parse_args()
    df=pd.read_csv(args.candidates)
    df=df[df['shift_points'].between(-args.max_shift_points,args.max_shift_points)].copy()
    required={'entry_timestamp','entry_date','shift_points','strike','spot_at_entry','lot_size','chart_pnl_inr'}
    missing=required-set(df.columns)
    if missing: raise ValueError(f'missing columns: {sorted(missing)}')
    span_dir=Path(args.span_dir)
    symbols=[s.strip() for s in args.symbols.split(',') if s.strip()]
    rows=[]
    cache={}
    for entry_date, g in df.groupby(args.date_col, sort=True):
        date_key=str(entry_date)
        if date_key in cache:
            cached=cache[date_key]
            if cached is None:
                continue
            engine,spn_name=cached
        else:
            ymd=pd.Timestamp(date_key).strftime('%Y%m%d')
            candidates=list(span_dir.glob(f'nsccl.{ymd}.'+'*.spn'))
            preferred=[p for p in candidates if f'.{args.span_version.lower()}.' in p.name.lower()]
            if not preferred:
                if args.skip_missing:
                    cache[date_key]=None
                    continue
                raise FileNotFoundError(f'No SPN file for {date_key} variant={args.span_version}')
            spn=sorted(preferred)[0]
            engine=RiskEngine.from_file(str(spn), symbols=symbols)
            spn_name=spn.name
            cache[date_key]=(engine,spn_name)
        for r in g.itertuples(index=False):
            qty=int(r.lot_size)
            strike=float(r.strike)
            position=[
              {'symbol':'NIFTY','instrument':'CE','expiry':str(r.near_expiry),'strike':strike,'transaction_type':'SELL','quantity':qty},
              {'symbol':'NIFTY','instrument':'PE','expiry':str(r.near_expiry),'strike':strike,'transaction_type':'BUY','quantity':qty},
              {'symbol':'NIFTY','instrument':'CE','expiry':str(r.next_expiry),'strike':strike,'transaction_type':'BUY','quantity':qty},
              {'symbol':'NIFTY','instrument':'PE','expiry':str(r.next_expiry),'strike':strike,'transaction_type':'SELL','quantity':qty},
            ]
            result=engine.basket(position,as_of_date=date_key)
            final=result['data']['final']
            margin=float(final['total'])
            chart=float(r.chart_pnl_inr)
            rows.append({
              'entry_timestamp':r.entry_timestamp,
              'entry_date':date_key,
              'candidate_label':getattr(r,'candidate_label',''),
              'near_expiry':getattr(r,'near_expiry',''),
              'next_expiry':getattr(r,'next_expiry',''),
              'shift_points':int(r.shift_points),
              'strike':strike,
              'spot_at_entry':float(r.spot_at_entry),
              'lot_size':qty,
              'chart_pnl_inr':chart,
              'chart_return_pct':float(getattr(r,'chart_return_pct',float('nan'))),
              'gross_pnl_inr':float(getattr(r,'gross_pnl_inr',float('nan'))),
              'net_pnl_inr':float(getattr(r,'net_pnl_inr',float('nan'))),
              'total_costs_inr':float(getattr(r,'total_costs_inr',float('nan'))),
              'premium_turnover_inr':float(getattr(r,'premium_turnover_inr',float('nan'))),
              'margin_required_inr':margin,
              'max_profit_pct_margin':100.0*chart/margin if margin>0 else None,
              'span_inr':float(final['span']),
              'exposure_inr':float(final['exposure']),
              'option_premium_reported_inr':float(final['option_premium']),
              'additional_inr':float(final['additional']),
              'source_spn_version':spn_name,
            })
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    result_df=pd.DataFrame(rows)
    if result_df.empty:
        result_df=pd.DataFrame(columns=['entry_timestamp','entry_date','candidate_label','near_expiry','next_expiry','shift_points','strike','spot_at_entry','lot_size','chart_pnl_inr','chart_return_pct','gross_pnl_inr','net_pnl_inr','total_costs_inr','premium_turnover_inr','margin_required_inr','max_profit_pct_margin','span_inr','exposure_inr','option_premium_reported_inr','additional_inr','source_spn_version'])
    else:
        result_df=result_df.sort_values(['entry_timestamp','shift_points'])
    result_df.to_csv(out,index=False)
    print(f'rows={len(result_df)} timestamps={result_df.entry_timestamp.nunique() if not result_df.empty else 0}')

if __name__=='__main__':
    main()
