#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

def max_drawdown(pnl):
    curve=pnl.cumsum()
    peak=curve.cummax()
    return float((curve-peak).min()) if len(curve) else 0.0

def bootstrap_mean_ci(x, n=5000, seed=42):
    x=np.asarray(x,dtype=float)
    if len(x)==0: return [None,None]
    rng=np.random.default_rng(seed)
    samples=rng.choice(x,size=(n,len(x)),replace=True).mean(axis=1)
    return [float(np.quantile(samples,0.025)),float(np.quantile(samples,0.975))]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--trades',required=True)
    p.add_argument('--out-dir',default='results/phase4')
    args=p.parse_args()
    df=pd.read_parquet(args.trades)
    if df.empty: raise RuntimeError('No selected trades')
    df=df.sort_values('entry_timestamp').copy()
    pnl=df.net_pnl_inr.astype(float)
    years=max((pd.to_datetime(df.entry_timestamp).max()-pd.to_datetime(df.entry_timestamp).min()).days/365.25,1/365.25)
    monthly=df.assign(month=pd.to_datetime(df.entry_timestamp).dt.to_period('M')).groupby('month').net_pnl_inr.sum()
    positive=(pnl>0).mean()
    summary={
        'n_trades':int(len(df)),
        'date_start':str(pd.to_datetime(df.entry_timestamp).min().date()),
        'date_end':str(pd.to_datetime(df.entry_timestamp).max().date()),
        'total_net_pnl_inr':float(pnl.sum()),
        'mean_net_pnl_inr':float(pnl.mean()),
        'median_net_pnl_inr':float(pnl.median()),
        'win_rate_pct':float(100*positive),
        'profit_factor':float(pnl[pnl>0].sum()/abs(pnl[pnl<0].sum())) if (pnl<0).any() else None,
        'max_drawdown_inr':max_drawdown(pnl),
        'bootstrap_mean_ci_95_pct':bootstrap_mean_ci(pnl),
        'trades_per_year':float(len(df)/years),
        'monthly_positive_rate_pct':float(100*(monthly>0).mean()),
        'largest_loss_inr':float(pnl.min()),
        'largest_win_inr':float(pnl.max()),
    }
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/'validation_summary.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    monthly.rename('net_pnl_inr').to_frame().to_csv(out/'monthly_pnl.csv')
    print(json.dumps(summary,indent=2,default=str))

if __name__=='__main__': main()