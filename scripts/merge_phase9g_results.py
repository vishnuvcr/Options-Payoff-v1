#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, random
from pathlib import Path
import numpy as np
import pandas as pd

def metric(df):
    if df.empty: return {'trades':0,'net_pnl_inr':0.0,'gross_pnl_inr':0.0,'total_costs_inr':0.0,'mean_net_pnl_inr':None,'median_net_pnl_inr':None,'win_rate_pct':None,'profit_factor':None,'max_drawdown_inr':0.0}
    x=pd.to_numeric(df['net_pnl_inr'],errors='coerce').dropna().to_numpy()
    wins=x[x>0]; losses=x[x<0]; gp=float(wins.sum()); gl=float(-losses.sum())
    eq=np.cumsum(x); peak=np.maximum.accumulate(np.maximum(eq,0)); dd=np.maximum(peak-eq,0)
    return {'trades':int(len(x)),'net_pnl_inr':float(x.sum()),'gross_pnl_inr':float(pd.to_numeric(df['gross_pnl_inr'],errors='coerce').sum()),'total_costs_inr':float(pd.to_numeric(df['total_costs'],errors='coerce').sum()),'mean_net_pnl_inr':float(x.mean()),'median_net_pnl_inr':float(np.median(x)),'win_rate_pct':float(100*len(wins)/len(x)),'profit_factor':float(gp/gl) if gl else math.inf,'max_drawdown_inr':float(dd.max())}

def wilson(wins,n,z=1.959963984540054):
    if n==0: return (float('nan'),float('nan'))
    p=wins/n; den=1+z*z/n; centre=(p+z*z/(2*n))/den; half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,centre-half),min(1,centre+half)

def bootstrap_mean(values,reps=20000,seed=20260927,block=0):
    values=np.asarray(values,dtype=float); n=len(values)
    if n==0: return [float('nan'),float('nan')]
    rng=random.Random(seed); out=[]; blocks=math.ceil(n/block) if block>1 else n
    for _ in range(reps):
        if block<=1: sample=[values[rng.randrange(n)] for _ in range(n)]
        else:
            sample=[]
            for _ in range(blocks):
                start=rng.randrange(n)
                for j in range(block):
                    sample.append(values[(start+j)%n])
                    if len(sample)==n: break
                if len(sample)==n: break
        out.append(float(np.mean(sample)))
    out.sort(); return [out[int(0.025*reps)],out[int(0.975*reps)-1]]

def paired_sign_permutation(values,reps=20000,seed=20260927):
    values=np.asarray(values,dtype=float)
    if len(values)==0: return float('nan')
    obs=float(values.mean()); rng=np.random.default_rng(seed); null=[]
    batch=5000
    remaining=reps
    while remaining>0:
        n=min(batch,remaining); signs=rng.choice(np.array([-1.0,1.0]),size=(n,len(values))); null.extend(np.mean(signs*values[None,:],axis=1)); remaining-=n
    null=np.asarray(null); return float((np.sum(np.abs(null)>=abs(obs))+1)/(reps+1))

def annual_rows(horizon_frames):
    rows=[]
    for h,df in horizon_frames.items():
        if df.empty: continue
        x=df.copy(); x['entry_date']=pd.to_datetime(x['entry_date'])
        for y,g in x.groupby(x['entry_date'].dt.year):
            m=metric(g); wins=int((pd.to_numeric(g['net_pnl_inr'],errors='coerce')>0).sum()); lo,hi=wilson(wins,len(g))
            rows.append({'horizon':h,'calendar_year':int(y),**m,'win_rate_wilson_low_pct':100*lo,'win_rate_wilson_high_pct':100*hi})
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--evidence-dir',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--bootstrap-reps',type=int,default=20000); ap.add_argument('--seed',type=int,default=20260927); args=ap.parse_args()
    root=Path(args.evidence_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    horizons={}; incomplete={}
    for rank in (1,2,3):
        parts=[]; inc_total=0
        for hfile in sorted(root.rglob('intraday_selected_trades.csv')):
            if hfile.parent.name != f'H{rank}':
                continue
            x=pd.read_csv(hfile)
            if not x.empty: parts.append(x)
            inc=hfile.parent/'intraday_incomplete_selected_trades.csv'
            if inc.exists():
                try:
                    inc_total += len(pd.read_csv(inc)) if inc.stat().st_size else 0
                except pd.errors.EmptyDataError:
                    inc_total += 0
        df=pd.concat(parts,ignore_index=True) if parts else pd.DataFrame()
        if not df.empty:
            df['entry_timestamp']=pd.to_datetime(df['entry_timestamp']); df=df.sort_values('entry_timestamp').drop_duplicates('near_expiry',keep='first')
        horizons[f'H{rank}']=df; incomplete[f'H{rank}']=int(inc_total)
        df.to_csv(out/f'H{rank}_realized_trades.csv',index=False)

    h1=horizons['H1']
    legacy_expected_trades=169
    legacy_expected_net=125688.82485334152
    observed_net=float(h1['net_pnl_inr'].sum()) if not h1.empty else 0.0
    legacy_reference={
        'legacy_phase9D_complete_trades':legacy_expected_trades,
        'legacy_phase9D_net_pnl_inr':legacy_expected_net,
        'corrected_phase9G_H1_complete_trades':int(len(h1)),
        'corrected_phase9G_H1_net_pnl_inr':observed_net,
        'trade_count_difference_vs_legacy':int(len(h1)-legacy_expected_trades),
        'net_pnl_difference_vs_legacy_inr':float(observed_net-legacy_expected_net),
        'note':'Legacy H1 is retained only as a diagnostic reference because the current protocol now requires exact 17 unique strike shifts and rejects conflicting duplicate quotes.'
    }
    (out/'h1_legacy_reference_comparison.json').write_text(json.dumps(legacy_reference,indent=2))

    summaries=[]
    for h,df in horizons.items():
        m=metric(df); wins=int((pd.to_numeric(df['net_pnl_inr'],errors='coerce')>0).sum()) if not df.empty else 0; lo,hi=wilson(wins,len(df)); vals=pd.to_numeric(df.get('net_pnl_inr',pd.Series(dtype=float)),errors='coerce').dropna().to_numpy()
        iid=bootstrap_mean(vals,args.bootstrap_reps,args.seed,0) if len(vals) else [None,None]; blk=bootstrap_mean(vals,args.bootstrap_reps,args.seed+1,4) if len(vals) else [None,None]
        summaries.append({'horizon':h,**m,'incomplete_selected_trades':incomplete[h],'win_rate_wilson_low_pct':100*lo,'win_rate_wilson_high_pct':100*hi,'iid_mean_ci_low_inr':iid[0],'iid_mean_ci_high_inr':iid[1],'block4_mean_ci_low_inr':blk[0],'block4_mean_ci_high_inr':blk[1]})
    summary_df=pd.DataFrame(summaries); summary_df.to_csv(out/'horizon_summary.csv',index=False)
    annual_rows(horizons).to_csv(out/'annual_summary.csv',index=False)

    # Predeclared selection-behaviour analysis: compare first-positive decision time
    # and selected strike displacement across fixed H1/H2/H3 horizons.
    selection_rows=[]
    for h,df in horizons.items():
        if df.empty:
            continue
        x=df.copy()
        x['entry_timestamp']=pd.to_datetime(x['entry_timestamp'],errors='coerce')
        if 'shift_points' not in x.columns:
            continue
        x['entry_hour_decimal']=x['entry_timestamp'].dt.hour + x['entry_timestamp'].dt.minute/60.0
        selection_rows.append({
            'horizon':h,
            'trades':int(len(x)),
            'mean_first_positive_minutes_after_0920':float(((x['entry_timestamp'].dt.hour*60+x['entry_timestamp'].dt.minute)-560).mean()),
            'median_first_positive_minutes_after_0920':float(((x['entry_timestamp'].dt.hour*60+x['entry_timestamp'].dt.minute)-560).median()),
            'p90_first_positive_minutes_after_0920':float(((x['entry_timestamp'].dt.hour*60+x['entry_timestamp'].dt.minute)-560).quantile(0.90)),
            'mean_selected_shift_points':float(pd.to_numeric(x['shift_points'],errors='coerce').mean()),
            'median_selected_shift_points':float(pd.to_numeric(x['shift_points'],errors='coerce').median()),
            'abs_shift_mean_points':float(pd.to_numeric(x['shift_points'],errors='coerce').abs().mean()),
            'atm_selection_pct':float(100*(pd.to_numeric(x['shift_points'],errors='coerce')==0).mean()),
        })
    pd.DataFrame(selection_rows).to_csv(out/'selection_behaviour_summary.csv',index=False)
    for h,df in horizons.items():
        if df.empty or 'shift_points' not in df.columns:
            continue
        pd.DataFrame({'shift_points':sorted(pd.to_numeric(df['shift_points'],errors='coerce').dropna().unique())}).assign(
            count=lambda z:[int((pd.to_numeric(df['shift_points'],errors='coerce')==v).sum()) for v in z['shift_points']]
        ).to_csv(out/f'{h}_strike_shift_distribution.csv',index=False)

    paired=[]
    h1k=h1[['near_expiry','net_pnl_inr']].copy(); h1k['near_expiry']=h1k['near_expiry'].astype(str); h1k=h1k.rename(columns={'net_pnl_inr':'h1_net'})
    for h in ('H2','H3'):
        df=horizons[h]
        if df.empty: continue
        y=df[['near_expiry','net_pnl_inr']].copy(); y['near_expiry']=y['near_expiry'].astype(str); y=y.rename(columns={'net_pnl_inr':f'{h.lower()}_net'}); z=h1k.merge(y,on='near_expiry',how='inner')
        if z.empty: continue
        delta=z[f'{h.lower()}_net']-z['h1_net']; ci=bootstrap_mean(delta.to_numpy(),args.bootstrap_reps,args.seed+(2 if h=='H2' else 3),4); p=paired_sign_permutation(delta.to_numpy(),args.bootstrap_reps,args.seed+(4 if h=='H2' else 5))
        paired.append({'comparison':f'{h}-H1','paired_cycles':int(len(z)),'mean_delta_inr':float(delta.mean()),'median_delta_inr':float(delta.median()),'positive_delta_pct':float(100*(delta>0).mean()),'block4_bootstrap_ci_low_inr':ci[0],'block4_bootstrap_ci_high_inr':ci[1],'paired_sign_permutation_p':p})
    paired_df=pd.DataFrame(paired)
    if not paired_df.empty:
        m=len(paired_df); order=paired_df['paired_sign_permutation_p'].sort_values().index; q=pd.Series(index=paired_df.index,dtype=float)
        for rank,idx in enumerate(order,1): q.loc[idx]=min(1.0,paired_df.loc[idx,'paired_sign_permutation_p']*m/rank)
        paired_df['bh_q_value']=q
    paired_df.to_csv(out/'paired_comparisons.csv',index=False)

    sensitivity=[]
    for p in sorted(out.glob('sensitivity_*.json')):
        x=json.loads(p.read_text()); sensitivity.append(x)
    pd.DataFrame(sensitivity).to_csv(out/'execution_sensitivity.csv',index=False)

    boot={}
    for h in ('H1','H2','H3'):
        vals=pd.to_numeric(horizons[h].get('net_pnl_inr',pd.Series(dtype=float)),errors='coerce').dropna().to_numpy()
        boot[h]={'iid_mean_ci_inr':bootstrap_mean(vals,args.bootstrap_reps,args.seed,0) if len(vals) else [None,None],'block4_mean_ci_inr':bootstrap_mean(vals,args.bootstrap_reps,args.seed+10,4) if len(vals) else [None,None]}
    (out/'bootstrap.json').write_text(json.dumps(boot,indent=2))

    candidate=False
    if not paired_df.empty:
        candidate=bool(((paired_df['mean_delta_inr']>0)&(paired_df['block4_bootstrap_ci_low_inr']>0)&(paired_df['bh_q_value']<0.05)).any())
    state='candidate_horizon_identified' if candidate else 'no_horizon_passed_predeclared_paired_test'
    summary={'phase':'9G','status':'complete','horizons':['H1','H2','H3'],'h1_legacy_reference':legacy_reference,'incomplete_selected_trades':incomplete,'paired_state':state,'primary_rule':'fixed far-expiry rank; no dynamic horizon switching','note':'Historical comparison only; any later production candidate requires untouched holdout validation.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    report=['# Phase 9G — H2/H3 far-expiry selection research','','## Corrected H1 control vs legacy H1 reference',f"Corrected Phase 9G H1: **{legacy_reference['corrected_phase9G_H1_complete_trades']} complete trades**, **₹{legacy_reference['corrected_phase9G_H1_net_pnl_inr']:.2f} net P&L**.",f"Legacy Phase 9D reference: **{legacy_reference['legacy_phase9D_complete_trades']} complete trades**, **₹{legacy_reference['legacy_phase9D_net_pnl_inr']:.2f} net P&L**.",'','## Horizon summary',summary_df.to_markdown(index=False),'','## Paired comparisons',paired_df.to_markdown(index=False) if not paired_df.empty else 'No paired comparisons available.','','## Interpretation','No dynamic far-expiry switching is allowed. A positive paired difference is a candidate for later independent holdout validation, not immediate deployment.']
    (out/'PHASE9G_RESULTS.md').write_text(chr(10).join(report)+chr(10))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()