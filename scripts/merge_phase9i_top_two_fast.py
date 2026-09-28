#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd

def max_dd(x):
    s=pd.Series(x,dtype=float).fillna(0).cumsum()
    return float((s-s.cummax()).min())
def pf(x):
    x=pd.Series(x,dtype=float).dropna(); loss=-x[x<0].sum()
    return float(x[x>0].sum()/loss) if loss else float('inf')
def stats(x):
    x=pd.Series(x,dtype=float).dropna()
    return {'trades':int(len(x)),'net_pnl_inr':float(x.sum()),'win_rate_pct':float((x>0).mean()*100),'mean_pnl_inr':float(x.mean()),'median_pnl_inr':float(x.median()),'profit_factor':pf(x),'max_drawdown_inr':max_dd(x),'min_pnl_inr':float(x.min()),'max_pnl_inr':float(x.max())}
def boot(x,B=10000,seed=20260928):
    x=np.asarray(pd.Series(x,dtype=float).dropna()); rng=np.random.default_rng(seed)
    vals=np.array([rng.choice(x,size=len(x),replace=True).mean() for _ in range(B)])
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]
def main():
    p=argparse.ArgumentParser(); p.add_argument('--input-dir',required=True); p.add_argument('--baseline',required=True); p.add_argument('--out-dir',required=True); a=p.parse_args()
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    trades=pd.concat([pd.read_csv(x) for x in sorted(Path(a.input_dir).rglob('top2_trade_rows.csv'))],ignore_index=True)
    cycles=pd.concat([pd.read_csv(x) for x in sorted(Path(a.input_dir).rglob('top2_cycle_summary.csv'))],ignore_index=True)
    trades['entry_timestamp']=pd.to_datetime(trades['entry_timestamp']); cycles['entry_timestamp']=pd.to_datetime(cycles['entry_timestamp'])
    base=pd.read_csv(a.baseline); base['entry_timestamp']=pd.to_datetime(base['entry_timestamp'])
    top1=trades[trades['rank'].eq(1) & trades['net_pnl_inr'].notna()].copy()
    m=base[['entry_timestamp','net_pnl_inr','shift_points']].merge(top1[['entry_timestamp','net_pnl_inr','shift_points']],on='entry_timestamp',how='outer',suffixes=('_base','_top1'),validate='one_to_one')
    m['abs_pnl_diff']=(m.net_pnl_inr_base-m.net_pnl_inr_top1).abs(); m['shift_match']=m.shift_points_base.eq(m.shift_points_top1)
    validation={'baseline_rows':len(base),'top1_rows':len(top1),'merged_rows':len(m),'max_abs_pnl_difference_inr':float(m.abs_pnl_diff.max()),'all_pnl_match':bool(len(m)==len(base)==len(top1) and m.abs_pnl_diff.max()<=1e-6),'all_shift_match':bool(m.shift_match.all())}
    if not validation['all_pnl_match'] or not validation['all_shift_match']: raise SystemExit('Top-1 does not reproduce frozen Phase 9G H1')
    valid_cycles=cycles[cycles['top1_pnl'].notna()].copy()
    rank_counts=trades[trades['net_pnl_inr'].notna()].groupby('near_expiry')['rank'].nunique().rename('realized_rank_count')
    cycles2=valid_cycles.merge(rank_counts,on='near_expiry',how='left')
    cycles2['realized_rank_count']=cycles2['realized_rank_count'].fillna(0).astype(int)
    exact2=cycles2[cycles2['realized_rank_count'].ge(2)]
    s1=stats(top1.net_pnl_inr); s2=stats(trades.net_pnl_inr); sc=stats(cycles2.combined_pnl); se=stats(exact2.combined_pnl)
    incremental=trades[trades['rank'].eq(2)].net_pnl_inr.dropna()
    year_trade=trades.dropna(subset=['net_pnl_inr']).assign(year=pd.to_datetime(trades.dropna(subset=['net_pnl_inr'])['entry_timestamp']).dt.year).groupby(['year','rank'])['net_pnl_inr'].agg(['count','sum','mean']).reset_index()
    summary={'baseline_validation':validation,'weekly_cycles_with_signal':int(len(cycles2)),'cycles_with_two_positive_candidates':int(len(exact2)),'cycles_with_only_one_realized_candidate':int((cycles2.realized_rank_count==1).sum()),'top1_control':s1,'top2_trade_level':s2,'top2_cycle_level':sc,'top2_exact2_cycle_level':se,'second_strike_increment':stats(incremental),'bootstrap95_mean_top2_trade':boot(trades.net_pnl_inr),'bootstrap95_mean_second_strike':boot(incremental),'bootstrap95_mean_combined_cycle':boot(cycles2.combined_pnl)}
    pd.DataFrame([{'metric':'net_pnl_inr','top1':s1['net_pnl_inr'],'top2':s2['net_pnl_inr'],'delta':s2['net_pnl_inr']-s1['net_pnl_inr']},
                  {'metric':'win_rate_pct','top1':s1['win_rate_pct'],'top2':s2['win_rate_pct'],'delta':s2['win_rate_pct']-s1['win_rate_pct']},
                  {'metric':'profit_factor','top1':s1['profit_factor'],'top2':s2['profit_factor'],'delta':s2['profit_factor']-s1['profit_factor']},
                  {'metric':'max_drawdown_inr','top1':s1['max_drawdown_inr'],'top2':s2['max_drawdown_inr'],'delta':s2['max_drawdown_inr']-s1['max_drawdown_inr']}]).to_csv(out/'top2_vs_top1_metrics.csv',index=False)
    trades.to_csv(out/'top2_trade_rows.csv',index=False); cycles2.to_csv(out/'top2_cycle_summary.csv',index=False); m.to_csv(out/'top2_baseline_validation.csv',index=False); year_trade.to_csv(out/'top2_yearly_summary.csv',index=False)
    out.joinpath('summary.json').write_text(json.dumps(summary,indent=2,default=str))
    out.joinpath('PHASE9I_TOP_TWO_RESULTS.md').write_text(
      '# Phase 9I — Top-two-strike results\n\n'
      'At the first valid exact-17-strike positive timestamp in each weekly cycle, the top two distinct positive flatline strikes were evaluated as separate four-leg H1 positions. The same 0.25% slippage, ₹20/order brokerage, statutory charges and near-expiry far-leg close convention were used.\n\n'
      '## Reproducibility gate\n\n'
      f"Top-1 exactly reproduces the accepted Phase 9G H1 control: **{validation['all_pnl_match']}**; maximum absolute P&L difference ₹{validation['max_abs_pnl_difference_inr']:.10f}; strike selections match **{validation['all_shift_match']}**.\n\n"
      '## Key counts\n\n'
      f"Cycles with a positive signal: **{len(cycles2)}**. Cycles with two positive candidates: **{len(exact2)}**. Cycles with only one positive candidate: **{int((cycles2.legs==1).sum())}**.\n\n"
      '## Metrics\n\n'+pd.DataFrame([
        {'strategy':'Top-1 control','trades':s1['trades'],'net_pnl_inr':s1['net_pnl_inr'],'win_rate_pct':s1['win_rate_pct'],'profit_factor':s1['profit_factor'],'max_drawdown_inr':s1['max_drawdown_inr']},
        {'strategy':'Top-2 trade-level','trades':s2['trades'],'net_pnl_inr':s2['net_pnl_inr'],'win_rate_pct':s2['win_rate_pct'],'profit_factor':s2['profit_factor'],'max_drawdown_inr':s2['max_drawdown_inr']},
        {'strategy':'Top-2 combined cycle-level','trades':sc['trades'],'net_pnl_inr':sc['net_pnl_inr'],'win_rate_pct':sc['win_rate_pct'],'profit_factor':sc['profit_factor'],'max_drawdown_inr':sc['max_drawdown_inr']}
      ]).to_markdown(index=False)+'\n\n'
      '## Interpretation\n\nThe absolute rupee P&L of the two-strike variant is not sufficient evidence of improvement because it deploys additional capital and incurs additional four-leg entry plus two-leg exit economics for the second position. The incremental second-strike series and cycle-level combined results are therefore reported separately.\n'
    )
if __name__=='__main__':main()
