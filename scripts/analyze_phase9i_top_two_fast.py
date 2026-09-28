#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from scripts.extract_near_exit_strategy_inputs import (
    DATASET, load_index, list_nifty_expiry_files, nifty_lot_size, last_index_bar_on_date
)
from scripts.run_near_expiry_exit_backtest import CostModel

SHIFTS=frozenset(range(-400,401,50))

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--start',required=True); p.add_argument('--end',required=True)
    p.add_argument('--out-dir',required=True)
    p.add_argument('--slippage-pct',type=float,default=0.0025)
    p.add_argument('--brokerage-per-order',type=float,default=20.0)
    return p.parse_args()

def pair(d,exps):
    xs=[x for x in exps if x>=d]
    if len(xs)<2 or (xs[1]-xs[0]).days>30:return None
    return xs[0],xs[1]

def _utc(v):
    return pd.Timestamp(v).tz_convert('UTC').to_pydatetime() if pd.Timestamp(v).tzinfo else pd.Timestamp(v,tz='UTC').to_pydatetime()

def filtered_option_file(expiry,filename,entry_ts,exit_dates):
    from huggingface_hub import hf_hub_download
    local=hf_hub_download(repo_id=DATASET,filename=filename,repo_type='dataset')
    filters=[]
    for ts in sorted(set(pd.DatetimeIndex(entry_ts))):
        u=_utc(ts)
        filters.append([('timestamp','=',u)])
    for d in sorted(set(exit_dates)):
        start=pd.Timestamp(d,tz='Asia/Kolkata').tz_convert('UTC').to_pydatetime()
        end=(pd.Timestamp(d,tz='Asia/Kolkata')+pd.Timedelta(days=1)).tz_convert('UTC').to_pydatetime()
        filters.append([('timestamp','>=',start),('timestamp','<',end)])
    if filters:
        try:
            t=pq.read_table(local,columns=['timestamp','strike','close','option_type'],filters=filters)
        except Exception:
            t=pq.read_table(local,columns=['timestamp','strike','close','option_type'])
    else:
        t=pq.read_table(local,columns=['timestamp','strike','close','option_type'])
    df=t.to_pandas()
    df['timestamp']=pd.to_datetime(df['timestamp'],utc=True).dt.tz_convert('Asia/Kolkata')
    df['trading_date']=df['timestamp'].dt.date
    df['strike']=pd.to_numeric(df['strike'],errors='coerce')
    df['close']=pd.to_numeric(df['close'],errors='coerce')
    df['option_type']=df['option_type'].astype(str).str.upper()
    df=df[df.option_type.isin(['CE','PE'])].dropna(subset=['timestamp','strike','close']).copy()
    df['contract_expiry']=expiry
    return df

def exit_maps(df,exit_ts):
    x=df[(df.trading_date==exit_ts.date())&(df.timestamp<=exit_ts)&df.option_type.isin(['CE','PE'])].sort_values('timestamp')
    x=x.drop_duplicates(['strike','option_type'],keep='last')
    ce=x[x.option_type.eq('CE')].set_index('strike'); pe=x[x.option_type.eq('PE')].set_index('strike')
    return ce['close'].to_dict(),pe['close'].to_dict(),ce['timestamp'].to_dict(),pe['timestamp'].to_dict()

def enrich(g,exit_ts,settlement,near,far,m):
    lot=nifty_lot_size(near); far_lot=nifty_lot_size(far); g=g.copy()
    ce_map,pe_map,ce_ts,pe_ts=g._exitmaps
    g['far_call_exit_close']=g.strike.map(ce_map); g['far_put_exit_close']=g.strike.map(pe_map)
    g['far_call_exit_timestamp']=g.strike.map(ce_ts); g['far_put_exit_timestamp']=g.strike.map(pe_ts)
    if lot!=far_lot:
        g['net_pnl_inr']=np.nan; g['gross_pnl_inr']=np.nan; g['total_costs']=np.nan; return g
    s=float(m.slippage_pct)
    sell_call=g.near_call*(1-s); buy_put=g.near_put*(1+s); buy_call=g.far_call*(1+s); sell_put=g.far_put*(1-s)
    fce=g.far_call_exit_close*(1-s); fpe=g.far_put_exit_close*(1+s)
    g['gross_pnl_inr']=(sell_call-buy_put-buy_call+sell_put+(g.strike-float(settlement))+fce-fpe)*lot
    turnover=(sell_call+buy_put+buy_call+sell_put+fce+fpe)*lot
    sell_turnover=(sell_call+sell_put+fce)*lot; buy_turnover=(buy_put+buy_call+fpe)*lot
    brokerage=6*m.brokerage_per_order_inr; exchange=turnover*m.exchange_turnover_rate; sebi=turnover*m.sebi_turnover_rate
    stamp_entry=(buy_put+buy_call)*lot*m.stamp_duty_buy_rate; stamp_exit=fpe*lot*m.stamp_duty_buy_rate
    stt_entry_rate=np.where(g.timestamp.dt.date>=dt.date(2026,4,1),m.stt_from_2026_04_01,m.stt_before_2026_04_01)
    stt_exit_rate=m.stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else m.stt_before_2026_04_01
    stt_entry=sell_turnover*stt_entry_rate; stt_exit=fce*lot*stt_exit_rate
    exercised=np.maximum(g.strike-float(settlement),0)*lot
    exercise_rate=m.exercise_stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else m.exercise_stt_before_2026_04_01
    stt_exercise=exercised*exercise_rate; gst=m.gst_rate*(brokerage+exchange+sebi)
    g['total_costs']=brokerage+exchange+sebi+stamp_entry+stamp_exit+stt_entry+stt_exit+stt_exercise+gst
    g['net_pnl_inr']=g.gross_pnl_inr-g.total_costs
    return g

def main():
    a=parse_args(); start=dt.date.fromisoformat(a.start); end=dt.date.fromisoformat(a.end)
    idx=load_index(); idx=idx[(idx.trading_date>=start)&(idx.trading_date<=end)].copy()
    entries=idx[((idx.timestamp.dt.hour>9)|((idx.timestamp.dt.hour==9)&(idx.timestamp.dt.minute>=20)))&
                ((idx.timestamp.dt.hour<15)|((idx.timestamp.dt.hour==15)&(idx.timestamp.dt.minute<=29)))][['timestamp','trading_date','close']].sort_values('timestamp')
    expfiles=list_nifty_expiry_files(start,end+dt.timedelta(days=35)); exps=[x[0] for x in expfiles]; fn=dict(expfiles)
    cycle_ts=defaultdict(list); need=defaultdict(list); exit_dates=defaultdict(set); cycle_exit={}
    for r in entries.itertuples(index=False):
        p=pair(r.trading_date,exps)
        if not p: continue
        near,far=p; exit_ts,settlement=last_index_bar_on_date(idx,near)
        if exit_ts is None: continue
        cycle_ts[near].append(r.timestamp); need[near].append(r.timestamp); need[far].append(r.timestamp)
        exit_dates[far].add(exit_ts.date()); cycle_exit[near]=(exit_ts,settlement)
    prepared={}
    def load_one(e):
        return e,filtered_option_file(e,fn[e],need[e],exit_dates.get(e,set()))
    with ThreadPoolExecutor(max_workers=6) as pool:
        fs=[pool.submit(load_one,e) for e in sorted(need)]
        for f in as_completed(fs):
            e,d=f.result(); prepared[e]=d
    spot=entries.set_index('timestamp').close
    model=CostModel(slippage_pct=a.slippage_pct,brokerage_per_order_inr=a.brokerage_per_order)
    top2=[]; cycles=[]
    for near in sorted(cycle_ts):
        timestamps=pd.DatetimeIndex(sorted(set(cycle_ts[near]))); far=pair(timestamps[0].date(),exps)[1]
        n=prepared.get(near); f=prepared.get(far)
        if n is None or f is None: continue
        exit_ts,settlement=cycle_exit[near]
        maps=exit_maps(f,exit_ts)
        nce=n[n.option_type.eq('CE')][['timestamp','strike','close']].rename(columns={'close':'near_call'})
        npe=n[n.option_type.eq('PE')][['timestamp','strike','close']].rename(columns={'close':'near_put'})
        fce=f[f.option_type.eq('CE')][['timestamp','strike','close']].rename(columns={'close':'far_call'})
        fpe=f[f.option_type.eq('PE')][['timestamp','strike','close']].rename(columns={'close':'far_put'})
        surf=nce.merge(npe,on=['timestamp','strike']).merge(fce,on=['timestamp','strike']).merge(fpe,on=['timestamp','strike'])
        surf=surf[surf.timestamp.isin(set(timestamps))].copy()
        if surf.empty: continue
        surf['spot']=surf.timestamp.map(spot); surf=surf.dropna(subset=['spot'])
        surf['absdiff']=(surf.strike-surf.spot).abs()
        atm=surf.sort_values(['timestamp','absdiff','strike']).drop_duplicates('timestamp')[['timestamp','strike']].rename(columns={'strike':'atm'})
        surf=surf.merge(atm,on='timestamp'); surf['shift_points']=surf.strike-surf.atm; surf=surf[surf.shift_points.isin(SHIFTS)].copy()
        surf['flatline_inr']=(surf.near_call-surf.near_put-surf.far_call+surf.far_put)*nifty_lot_size(near)
        qn=surf.groupby(['timestamp','shift_points'])[['near_call','near_put','far_call','far_put']].nunique()
        conflicts=qn.gt(1).any(axis=1).groupby(level=0).sum(); counts=surf.groupby('timestamp').shift_points.nunique()
        pos=surf.groupby('timestamp').flatline_inr.apply(lambda x:int((x>0).sum()))
        valid=[ts for ts in counts.index if counts.loc[ts]==17 and conflicts.get(ts,0)==0 and pos.get(ts,0)>0]
        if not valid: continue
        first=min(valid); h=surf[surf.timestamp.eq(first)].copy(); h._exitmaps=maps; h=enrich(h,exit_ts,settlement,near,far,model)
        h=h[h.flatline_inr>0].sort_values(['flatline_inr','shift_points'],ascending=[False,True]).reset_index(drop=True)
        if h.empty: continue
        take=h.head(2)
        for rank,row in enumerate(take.itertuples(index=False),1):
            top2.append({'near_expiry':str(near),'entry_timestamp':str(first),'entry_date':str(pd.Timestamp(first).date()),'rank':rank,'shift_points':int(row.shift_points),'strike':float(row.strike),'flatline_inr':float(row.flatline_inr),'gross_pnl_inr':float(row.gross_pnl_inr) if pd.notna(row.gross_pnl_inr) else np.nan,'total_costs':float(row.total_costs) if pd.notna(row.total_costs) else np.nan,'net_pnl_inr':float(row.net_pnl_inr) if pd.notna(row.net_pnl_inr) else np.nan})
        cycles.append({'near_expiry':str(near),'entry_timestamp':str(first),'positive_candidates':int(len(h)),'top1_shift':int(take.iloc[0].shift_points),'top2_shift':int(take.iloc[1].shift_points) if len(take)>1 else None,'top1_pnl':float(take.iloc[0].net_pnl_inr) if pd.notna(take.iloc[0].net_pnl_inr) else np.nan,'top2_pnl':float(take.iloc[1].net_pnl_inr) if len(take)>1 and pd.notna(take.iloc[1].net_pnl_inr) else np.nan,'combined_pnl':float(take.net_pnl_inr.sum(min_count=1))})
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(top2).to_csv(out/'top2_trade_rows.csv',index=False); pd.DataFrame(cycles).to_csv(out/'top2_cycle_summary.csv',index=False)
    (out/'metadata.json').write_text(json.dumps({'start':a.start,'end':a.end,'rows':len(top2),'rule':'first valid exact-17 positive timestamp; top two positive flatline strikes; predicate-filtered option reads'},indent=2))
if __name__=='__main__': main()
