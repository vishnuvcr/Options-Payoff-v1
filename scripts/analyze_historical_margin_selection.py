#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--margins',required=True)
    ap.add_argument('--out-dir',required=True)
    ap.add_argument('--threshold-pct',type=float,default=2.5)
    args=ap.parse_args()
    df=pd.read_csv(args.margins)
    if df.empty: raise RuntimeError('No reconstructed candidate margins')
    df['max_profit_pct_margin']=pd.to_numeric(df['max_profit_pct_margin'],errors='coerce')
    eligible=df[df['max_profit_pct_margin']>args.threshold_pct].copy()
    rows_value=[]; rows_pct=[]
    for ts,g in eligible.groupby('entry_timestamp',sort=True):
        best_value=g.sort_values(['chart_pnl_inr','max_profit_pct_margin','shift_points'],ascending=[False,False,True]).iloc[0]
        best_pct=g.sort_values(['max_profit_pct_margin','chart_pnl_inr','shift_points'],ascending=[False,False,True]).iloc[0]
        rows_value.append(best_value.to_dict())
        rows_pct.append(best_pct.to_dict())
    value_df=pd.DataFrame(rows_value)
    pct_df=pd.DataFrame(rows_pct)
    def summary(x):
        if x.empty: return {'selected_trades':0}
        pnl=pd.to_numeric(x['net_pnl_inr'],errors='coerce') if 'net_pnl_inr' in x else pd.Series(dtype=float)
        out={
          'selected_trades':int(len(x)),
          'selected_timestamps':int(x['entry_timestamp'].nunique()),
          'mean_chart_pnl_inr':float(x['chart_pnl_inr'].mean()),
          'mean_margin_required_inr':float(x['margin_required_inr'].mean()),
          'mean_max_profit_pct_margin':float(x['max_profit_pct_margin'].mean()),
          'max_max_profit_pct_margin':float(x['max_profit_pct_margin'].max()),
          'shift_counts':{str(k):int(v) for k,v in x['shift_points'].value_counts().sort_index().items()},
        }
        if len(pnl):
          out.update({
            'net_pnl_inr':float(pnl.sum()),
            'mean_net_pnl_inr':float(pnl.mean()),
            'win_rate_pct':float(100*(pnl>0).mean()),
            'profit_factor':float(pnl[pnl>0].sum()/abs(pnl[pnl<0].sum())) if (pnl<0).any() else None,
          })
        return out
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    eligible.to_csv(out/'margin_eligible_candidates.csv',index=False)
    value_df.to_csv(out/'selected_by_max_value.csv',index=False)
    pct_df.to_csv(out/'selected_by_max_percentage.csv',index=False)
    result={
      'threshold_pct':args.threshold_pct,
      'candidate_rows_reconstructed':int(len(df)),
      'eligible_rows':int(len(eligible)),
      'eligible_timestamps':int(eligible['entry_timestamp'].nunique()),
      'max_value_selection':summary(value_df),
      'max_percentage_selection':summary(pct_df),
      'same_strike_count':int((value_df.set_index('entry_timestamp')['shift_points']==pct_df.set_index('entry_timestamp')['shift_points']).sum()) if not value_df.empty and len(value_df)==len(pct_df) else None,
      'note':'This is the exact margin-denominator selection on the reconstructed candidate subset. The subset is prefiltered using the standard 2% index-option exposure lower bound on the two short options; candidates outside the subset cannot reach 2.5% under that lower-bound assumption.'
    }
    (out/'summary.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    print(json.dumps(result,indent=2,default=str))

if __name__=='__main__':
    main()
