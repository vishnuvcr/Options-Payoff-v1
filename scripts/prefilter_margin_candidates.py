#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--exposure-rate-per-short',type=float,default=0.01,
                    help='Conservative lower-bound ELM rate per short NIFTY option; 1% means 2% total across the two short legs.')
    args=ap.parse_args()
    df=pd.read_parquet(args.candidates)
    need={'entry_timestamp','entry_date','shift_points','strike','spot_at_entry','lot_size','chart_pnl_inr'}
    missing=need-set(df.columns)
    if missing: raise ValueError(f'missing columns: {sorted(missing)}')
    # For this strategy there are two short NIFTY index options. Using the
    # calibrated/default 2% exposure rate per short option gives a 4% total
    # notional exposure lower bound before any SPAN component. A trade cannot
    # exceed 2.5% max-profit/margin unless its static flatline exceeds 0.1%
    # of spot notional.
    if args.exposure_rate_per_short <= 0 or args.exposure_rate_per_short >= 0.10:
        raise ValueError('exposure-rate-per-short must be in (0, 0.10)')
    lower_bound_margin=2.0*args.exposure_rate_per_short*df['spot_at_entry']*df['lot_size']
    df=df[df['chart_pnl_inr']>0.025*lower_bound_margin].copy()
    df['exposure_lower_bound_inr']=lower_bound_margin[df.index]
    df['lower_bound_max_profit_pct']=100.0*df['chart_pnl_inr']/df['exposure_lower_bound_inr']
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    df.sort_values(['entry_timestamp','shift_points']).to_csv(out,index=False)
    print(f'exposure_rate_per_short={args.exposure_rate_per_short}')
    print(f'candidate_rows_possible={len(df)}')
    print(f'timestamps_possible={df.entry_timestamp.nunique()}')
    print(f'dates_possible={df.entry_date.nunique()}')
    print(df[['entry_date','entry_timestamp','shift_points','strike','spot_at_entry','chart_pnl_inr','exposure_lower_bound_inr','lower_bound_max_profit_pct']].to_string(index=False))

if __name__=='__main__':
    main()
