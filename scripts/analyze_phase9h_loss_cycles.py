#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd

from scripts.extract_near_exit_strategy_inputs import DATASET, load_index, list_nifty_expiry_files, load_option_file, nifty_lot_size
from scripts.run_near_expiry_exit_backtest import CostModel

SHIFTS = frozenset(range(-400,401,50))
DELAYS = (15,30,60,120)

def args():
    p=argparse.ArgumentParser()
    p.add_argument('--losses',required=True)
    p.add_argument('--scan-audit',required=True)
    p.add_argument('--start',required=True)
    p.add_argument('--end',required=True)
    p.add_argument('--out-dir',required=True)
    p.add_argument('--slippage-pct',type=float,default=.0025)
    p.add_argument('--brokerage-per-order',type=float,default=20)
    return p.parse_args()

def exit_maps(df,exit_ts):
    x=df[(df.trading_date==exit_ts.date())&(df.timestamp<=exit_ts)&df.option_type.isin(['CE','PE'])].sort_values('timestamp').drop_duplicates(['strike','option_type'],keep='last')
    return tuple(x[x.option_type.eq(t)].set_index('strike')['close'].to_dict() for t in ['CE','PE']) + tuple(x[x.option_type.eq(t)].set_index('strike')['timestamp'].to_dict() for t in ['CE','PE'])

def pnl_surface(g,near,far,exit_ts,settlement,maps,model):
    ce_exit,pe_exit,ce_ts,pe_ts=maps
    lot=nifty_lot_size(near); far_lot=nifty_lot_size(far); s=model.slippage_pct
    g=g.copy()
    g['far_call_exit_close']=g.strike.map(ce_exit); g['far_put_exit_close']=g.strike.map(pe_exit)
    g['far_call_exit_timestamp']=g.strike.map(ce_ts); g['far_put_exit_timestamp']=g.strike.map(pe_ts)
    g['entry_date']=g.timestamp.dt.date; g['near_lot_size']=lot; g['far_lot_size']=far_lot
    if lot!=far_lot:
        g['net_pnl_inr']=np.nan; return g
    sc=g.near_call*(1-s); bp=g.near_put*(1+s); bc=g.far_call*(1+s); sp=g.far_put*(1-s)
    fce=g.far_call_exit_close*(1-s); fpe=g.far_put_exit_close*(1+s)
    g['gross_pnl_inr']=(sc-bp-bc+sp+(g.strike-float(settlement))+fce-fpe)*lot
    turnover=(sc+bp+bc+sp+fce+fpe)*lot; sell=(sc+sp+fce)*lot; buy=(bp+bc+fpe)*lot
    brokerage=6*model.brokerage_per_order_inr
    exchange=turnover*model.exchange_turnover_rate; sebi=turnover*model.sebi_turnover_rate
    stamp_entry=(bp+bc)*lot*model.stamp_duty_buy_rate; stamp_exit=fpe*lot*model.stamp_duty_buy_rate
    stt_entry_rate=np.where(g.entry_date>=dt.date(2026,4,1),model.stt_from_2026_04_01,model.stt_before_2026_04_01)
    stt_exit_rate=model.stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else model.stt_before_2026_04_01
    stt_entry=sell*stt_entry_rate; stt_exit=fce*lot*stt_exit_rate
    exercise=np.maximum(g.strike-float(settlement),0)*lot
    exercise_rate=model.exercise_stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else model.exercise_stt_before_2026_04_01
    stt_ex=exercise*exercise_rate; gst=model.gst_rate*(brokerage+exchange+sebi)
    g['total_costs']=brokerage+exchange+sebi+stamp_entry+stamp_exit+stt_entry+stt_exit+stt_ex+gst
    g['net_pnl_inr']=g.gross_pnl_inr-g.total_costs
    g['realizable']=~(g.far_call_exit_close.isna()|g.far_put_exit_close.isna())
    return g

def main(a):
    losses=pd.read_csv(a.losses)
    losses=losses[losses.net_pnl_inr<0].copy()
    scan=pd.read_parquet(a.scan_audit)
    idx=load_index()
    start=dt.date.fromisoformat(a.start); end=dt.date.fromisoformat(a.end)
    exp_files=list_nifty_expiry_files(start,end+dt.timedelta(days=35))
    fn=dict(exp_files)
    cycles=[]; need={}
    for r in losses.itertuples(index=False):
        near=pd.Timestamp(r.near_expiry).date()
        far=pd.Timestamp(r.far_expiry).date()
        exit_ts=pd.Timestamp(r.near_exit_timestamp)
        settlement=float(r.near_settlement)
        gscan=scan[(scan.near_expiry.astype(str)==str(near)) & scan.decision.eq(True)].copy()
        ts=sorted(pd.to_datetime(gscan.timestamp).unique())
        if not ts: continue
        cycles.append({'loss':r,'near':near,'far':far,'exit_ts':exit_ts,'settlement':settlement,'valid':ts})
        need.setdefault(near,[]).extend(ts+[exit_ts]); need.setdefault(far,[]).extend(ts+[exit_ts])
    prepared={}
    def load_one(e):
        ts=need[e]
        return e,load_option_file(e,fn[e],timestamp_min=min(ts),timestamp_max=max(ts))
    if need:
        with ThreadPoolExecutor(max_workers=min(6,len(need))) as pool:
            fs=[pool.submit(load_one,e) for e in sorted(need)]
            for f in as_completed(fs):
                e,df=f.result(); prepared[e]=df
    model=CostModel(slippage_pct=a.slippage_pct,brokerage_per_order_inr=a.brokerage_per_order)
    details=[]; variants=[]
    spot=idx.set_index('timestamp').close
    for cyc in cycles:
        near,far,exit_ts,settlement=cyc['near'],cyc['far'],cyc['exit_ts'],cyc['settlement']
        n=prepared[near]; f=prepared[far]
        nce=n[n.option_type.eq('CE')][['timestamp','strike','close']].rename(columns={'close':'near_call'})
        npe=n[n.option_type.eq('PE')][['timestamp','strike','close']].rename(columns={'close':'near_put'})
        fce=f[f.option_type.eq('CE')][['timestamp','strike','close']].rename(columns={'close':'far_call'})
        fpe=f[f.option_type.eq('PE')][['timestamp','strike','close']].rename(columns={'close':'far_put'})
        surf=nce.merge(npe,on=['timestamp','strike']).merge(fce,on=['timestamp','strike']).merge(fpe,on=['timestamp','strike'])
        surf=surf[surf.timestamp.isin(cyc['valid'])].copy()
        surf['spot']=surf.timestamp.map(spot); surf=surf.dropna(subset=['spot'])
        surf['absdiff']=(surf.strike-surf.spot).abs()
        atm=surf.sort_values(['timestamp','absdiff','strike']).drop_duplicates('timestamp')[['timestamp','strike']].rename(columns={'strike':'atm'})
        surf=surf.merge(atm,on='timestamp')
        surf['shift_points']=surf.strike-surf.atm
        surf=surf[surf.shift_points.isin(SHIFTS)].copy()
        surf['flatline_inr']=(surf.near_call-surf.near_put-surf.far_call+surf.far_put)*nifty_lot_size(near)
        q=surf.groupby(['timestamp','shift_points'])[['near_call','near_put','far_call','far_put']].nunique()
        conflicts=q.gt(1).any(axis=1).groupby(level=0).sum()
        cnt=surf.groupby('timestamp').shift_points.nunique()
        pos=surf.groupby('timestamp').flatline_inr.apply(lambda x:int((x>0).sum()))
        valid=[ts for ts in cyc['valid'] if int(cnt.get(ts,0))==17 and int(conflicts.get(ts,0))==0 and int(pos.get(ts,0))>0]
        surf=pnl_surface(surf[surf.timestamp.isin(valid)],near,far,exit_ts,settlement,exit_maps(f,exit_ts),model)
        selected=surf[surf.flatline_inr>0].sort_values(['timestamp','flatline_inr','shift_points'],ascending=[True,False,True]).drop_duplicates('timestamp')
        if selected.empty: continue
        first=valid[0]
        b=selected[selected.timestamp.eq(first)]
        if b.empty: continue
        base=b.iloc[0]; base_pnl=float(base.net_pnl_inr)
        choices={'first_positive':base}
        z=selected[selected.timestamp.eq(valid[1])] if len(valid)>1 else pd.DataFrame()
        choices['second_valid_timestamp']=None if z.empty else z.iloc[0]
        for m in DELAYS:
            z=selected[selected.timestamp.ge(first+pd.Timedelta(minutes=m))].sort_values('timestamp')
            choices[f'delay_{m}m']=None if z.empty else z.iloc[0]
        z=selected[selected.timestamp.gt(first)].dropna(subset=['net_pnl_inr'])
        choices['best_later_frozen_selector']=None if z.empty else z.sort_values('net_pnl_inr',ascending=False).iloc[0]
        z=surf[(surf.timestamp>first)&surf.net_pnl_inr.notna()]
        choices['best_later_any_candidate']=None if z.empty else z.sort_values('net_pnl_inr',ascending=False).iloc[0]
        z=surf[(surf.timestamp==first)&surf.net_pnl_inr.notna()]
        choices['same_timestamp_any_candidate']=None if z.empty else z.sort_values('net_pnl_inr',ascending=False).iloc[0]
        for name,row in choices.items():
            pnl=None if row is None or pd.isna(row.get('net_pnl_inr',np.nan)) else float(row.net_pnl_inr)
            variants.append({'variant':name,'entry_date':str(first.date()),'entry_timestamp':None if row is None else str(row.timestamp),'shift_points':None if row is None else int(row.shift_points),'net_pnl_inr':pnl,'baseline_net_pnl_inr':base_pnl,'rescues_loss':bool(pnl is not None and pnl>0)})
        d={'entry_date':str(first.date()),'entry_timestamp':str(first),'near_expiry':str(near),'baseline_shift':int(base.shift_points),'baseline_net_pnl_inr':base_pnl,'valid_timestamp_count':len(valid)}
        for name,row in choices.items():
            pnl=None if row is None or pd.isna(row.get('net_pnl_inr',np.nan)) else float(row.net_pnl_inr)
            d[f'{name}_entry_timestamp']=None if row is None else str(row.timestamp)
            d[f'{name}_shift']=None if row is None else int(row.shift_points)
            d[f'{name}_net_pnl_inr']=pnl
            d[f'{name}_rescues_loss']=bool(pnl is not None and pnl>0)
        details.append(d)
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    vdf=pd.DataFrame(variants)
    pd.DataFrame(details).to_csv(out/'loss_trade_entry_detail.csv',index=False)
    vdf.to_csv(out/'entry_variant_trade_rows.csv',index=False)
    (out/'summary.json').write_text(json.dumps({'dataset':DATASET,'loss_cycles_input':int(len(losses)),'loss_cycles_reconstructed':int(len(details)),'rescues_by_variant':{v:int(g.rescues_loss.sum()) for v,g in vdf.groupby('variant')}},indent=2))

if __name__=='__main__':
    main(args())
