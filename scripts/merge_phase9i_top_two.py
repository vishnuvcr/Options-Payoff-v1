#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

def max_dd(x):
    s=x.cumsum()
    return float((s-s.cummax()).min())

def profit_factor(x):
    wins=x[x>0].sum(); losses=-x[x<0].sum()
    return float(wins/losses) if losses else math.inf

def stats(x):
    x=pd.Series(x,dtype=float).dropna()
    return {'trades':int(len(x)),'net_pnl_inr':float(x.sum()),'gross_wins_inr':float(x[x>0].sum()),'gross_losses_inr':float(x[x<0].sum()),'win_rate_pct':float((x>0).mean()*100),'mean_pnl_inr':float(x.mean()),'median_pnl_inr':float(x.median()),'profit_factor':profit_factor(x),'max_drawdown_inr':max_dd(x),'min_pnl_inr':float(x.min()),'max_pnl_inr':float(x.max())}

def bootstrap_mean(x,B=10000,seed=20260928):
    x=np.asarray(x,dtype=float)
    if len(x)==0:return [None,None]
    rng=np.random.default_rng(seed)
    vals=np.array([rng.choice(x,size=len(x),replace=True).mean() for _ in range(B)])
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input-dir',required=True); p.add_argument('--baseline',required=True); p.add_argument('--out-dir',required=True)
    a=p.parse_args()
    root=Path(a.input_dir); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    rows=sorted(root.rglob('top2_trade_rows.csv')); cycles=sorted(root.rglob('top2_cycle_summary.csv'))
    if not rows: raise SystemExit('No Phase 9I yearly results')
    trades=pd.concat([pd.read_csv(x) for x in rows],ignore_index=True).sort_values(['entry_timestamp','rank']).reset_index(drop=True)
    cy=pd.concat([pd.read_csv(x) for x in cycles],ignore_index=True).sort_values('entry_timestamp').reset_index(drop=True)
    base=pd.read_csv(a.baseline)
    base['entry_timestamp']=pd.to_datetime(base['entry_timestamp']); trades['entry_timestamp']=pd.to_datetime(trades['entry_timestamp'])
    top1=trades[trades['rank'].eq(1)].copy()
    m=base[['entry_timestamp','net_pnl_inr','shift_points']].merge(top1[['entry_timestamp','shift_points','net_pnl_inr']],on='entry_timestamp',how='outer',suffixes=('_base','_top1'),validate='one_to_one')
    m['pnl_abs_diff']=(m['net_pnl_inr_base']-m['net_pnl_inr_top1']).abs(); m['shift_match']=m['shift_points_base'].eq(m['shift_points_top1'])
    validation={'baseline_rows':int(len(base)),'top1_rows':int(len(top1)),'merged_rows':int(len(m)),'max_abs_pnl_difference_inr':float(m.pnl_abs_diff.max()) if len(m) else None,'all_pnl_match':bool(len(m)==len(base)==len(top1) and m.pnl_abs_diff.max()<=1e-6),'all_shift_match':bool(m.shift_match.all())}
    if not validation['all_pnl_match'] or not validation['all_shift_match']: raise SystemExit('Top-1 reconstruction does not reproduce frozen Phase 9G H1')
    combined=trades.groupby('near_expiry',as_index=False).agg(entry_timestamp=('entry_timestamp','first'),legs=('rank','count'),combined_net_pnl_inr=('net_pnl_inr','sum'),combined_gross_pnl_inr=('gross_pnl_inr','sum'),combined_costs_inr=('total_costs','sum'))
    combined=combined.sort_values('entry_timestamp').reset_index(drop=True)
    exact2=combined[combined.legs.eq(2)].copy()
    summary={
        'baseline_validation':validation,
        'cycles_with_any_positive_trade':int(len(combined)),
        'cycles_with_two_positive_candidates':int(len(exact2)),
        'cycles_with_only_one_positive_candidate':int((combined.legs==1).sum()),
        'top2_trade_level':stats(trades.net_pnl_inr),
        'top2_combined_cycle_level_all':stats(combined.combined_net_pnl_inr),
        'top2_combined_cycle_level_exact2':stats(exact2.combined_net_pnl_inr),
        'top1_control_from_top2_reconstruction':stats(top1.net_pnl_inr),
        'bootstrap_95ci_mean_top2_trade':bootstrap_mean(trades.net_pnl_inr),
        'bootstrap_95ci_mean_combined_exact2':bootstrap_mean(exact2.combined_net_pnl_inr)
    }
    trades.to_csv(out/'top2_trade_rows.csv',index=False); combined.to_csv(out/'top2_cycle_summary.csv',index=False); exact2.to_csv(out/'top2_exact2_cycles.csv',index=False); m.to_csv(out/'top2_baseline_validation.csv',index=False)
    out.joinpath('summary.json').write_text(json.dumps(summary,indent=2,default=str))
    table=pd.DataFrame([
        {'strategy':'H1 top-1 control','trades':summary['top1_control_from_top2_reconstruction']['trades'],'net_pnl_inr':summary['top1_control_from_top2_reconstruction']['net_pnl_inr'],'win_rate_pct':summary['top1_control_from_top2_reconstruction']['win_rate_pct'],'profit_factor':summary['top1_control_from_top2_reconstruction']['profit_factor'],'max_drawdown_inr':summary['top1_control_from_top2_reconstruction']['max_drawdown_inr']},
        {'strategy':'H1 top-2 positive strikes','trades':summary['top2_trade_level']['trades'],'net_pnl_inr':summary['top2_trade_level']['net_pnl_inr'],'win_rate_pct':summary['top2_trade_level']['win_rate_pct'],'profit_factor':summary['top2_trade_level']['profit_factor'],'max_drawdown_inr':summary['top2_trade_level']['max_drawdown_inr']},
        {'strategy':'H1 top-2 combined per cycle','trades':summary['top2_combined_cycle_level_all']['trades'],'net_pnl_inr':summary['top2_combined_cycle_level_all']['net_pnl_inr'],'win_rate_pct':summary['top2_combined_cycle_level_all']['win_rate_pct'],'profit_factor':summary['top2_combined_cycle_level_all']['profit_factor'],'max_drawdown_inr':summary['top2_combined_cycle_level_all']['max_drawdown_inr']}
    ])
    md=['# Phase 9I — Top-two-strikes analysis','',
        '## Strategy tested',
        'At the first valid exact-17-strike timestamp in each weekly cycle, rank all positive/all-green candidates by estimated equal Max Profit = Max Loss flatline and enter the top two distinct strikes. Each selected strike is one complete four-leg H1 position. The same 0.25% premium slippage, ₹20/order brokerage and statutory cost model as the frozen Phase 9G H1 control is used. No 2.5% gate or dynamic management is added.','',
        '## Control validation',
        f"Top-1 reconstruction exactly matches the frozen Phase 9G H1 control: **{validation['all_pnl_match']}**; maximum absolute P&L difference = ₹{validation['max_abs_pnl_difference_inr']:.10f}; strike selections match = **{validation['all_shift_match']}**.",'',
        '## Core results',table.to_markdown(index=False),'',
        '## Population structure',
        f"Weekly cycles with at least one positive candidate/trade: **{len(combined)}**.",
        f"Cycles with two positive candidates: **{len(exact2)}**.",
        f"Cycles with only one positive candidate: **{int((combined.legs==1).sum())}**.",'',
        '## Statistical uncertainty',
        f"Trade-level mean bootstrap 95% CI: ₹{summary['bootstrap_95ci_mean_top2_trade'][0]:,.2f} to ₹{summary['bootstrap_95ci_mean_top2_trade'][1]:,.2f}.",
        f"Exact-two-cycle combined mean bootstrap 95% CI: ₹{summary['bootstrap_95ci_mean_combined_exact2'][0]:,.2f} to ₹{summary['bootstrap_95ci_mean_combined_exact2'][1]:,.2f}.",'',
        '## Interpretation',
        'The top-two variant increases exposure and transaction count. The primary comparison is therefore the combined weekly-cycle P&L, not simply the larger absolute rupee P&L from having more capital at risk. A cycle with only one positive candidate is not forced to take a negative second candidate; it remains a one-position cycle in this primary definition. A separate forced-second-negative-candidate variant would be a different strategy and is not mixed into this result.']
    out.joinpath('PHASE9I_TOP_TWO_RESULTS.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(summary,indent=2,default=str))
if __name__=='__main__':main()
