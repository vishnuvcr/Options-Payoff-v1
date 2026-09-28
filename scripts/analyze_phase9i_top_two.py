#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET, load_index, list_nifty_expiry_files, load_option_file,
    last_index_bar_on_date, nifty_lot_size
)
from scripts.run_near_expiry_exit_backtest import CostModel

SHIFTS = frozenset(range(-400, 401, 50))

def args():
    p=argparse.ArgumentParser()
    p.add_argument('--start',required=True); p.add_argument('--end',required=True)
    p.add_argument('--scan-audit',required=True); p.add_argument('--out-dir',required=True)
    p.add_argument('--entry-start-time',default='09:20'); p.add_argument('--entry-end-time',default='15:29')
    p.add_argument('--slippage-pct',type=float,default=0.0025); p.add_argument('--brokerage-per-order',type=float,default=20.0)
    return p.parse_args()

def pair(d, expiries):
    xs=[x for x in expiries if x>=d]
    if len(xs)<2 or (xs[1]-xs[0]).days>30: return None
    return xs[0],xs[1]

def build_far_exit_maps(far_df, exit_ts):
    x=far_df[(far_df.trading_date==exit_ts.date())&(far_df.timestamp<=exit_ts)&far_df.option_type.isin(['CE','PE'])].sort_values('timestamp')
    x=x.drop_duplicates(['strike','option_type'],keep='last')
    ce=x[x.option_type.eq('CE')].set_index('strike'); pe=x[x.option_type.eq('PE')].set_index('strike')
    return ce['close'].to_dict(),pe['close'].to_dict(),ce['timestamp'].to_dict(),pe['timestamp'].to_dict()

def enrich_surface(h, exit_ts, settlement, near, far, maps, model):
    g=h.copy(); ce_map,pe_map,ce_ts,pe_ts=maps
    g['far_call_exit_close']=g['strike'].map(ce_map); g['far_put_exit_close']=g['strike'].map(pe_map)
    g['far_call_exit_timestamp']=g['strike'].map(ce_ts); g['far_put_exit_timestamp']=g['strike'].map(pe_ts)
    g['entry_date']=g['timestamp'].dt.date
    lot=nifty_lot_size(near); far_lot=nifty_lot_size(far)
    if lot!=far_lot:
        g['realizable']=False; g['net_pnl_inr']=np.nan; g['gross_pnl_inr']=np.nan; g['total_costs']=np.nan
        return g
    s=float(model.slippage_pct)
    sell_call=g['near_call']*(1-s); buy_put=g['near_put']*(1+s); buy_call=g['far_call']*(1+s); sell_put=g['far_put']*(1-s)
    far_call_exit=g['far_call_exit_close']*(1-s); far_put_exit=g['far_put_exit_close']*(1+s)
    g['realizable']=~(g['far_call_exit_close'].isna()|g['far_put_exit_close'].isna())
    g['gross_pnl_inr']=(sell_call-buy_put-buy_call+sell_put+(g['strike']-float(settlement))+far_call_exit-far_put_exit)*lot
    turnover=(sell_call+buy_put+buy_call+sell_put+far_call_exit+far_put_exit)*lot
    sell_turnover=(sell_call+sell_put+far_call_exit)*lot; buy_turnover=(buy_put+buy_call+far_put_exit)*lot
    brokerage=6.0*model.brokerage_per_order_inr; exchange=turnover*model.exchange_turnover_rate; sebi=turnover*model.sebi_turnover_rate
    stamp_entry=(buy_put+buy_call)*lot*model.stamp_duty_buy_rate; stamp_exit=far_put_exit*lot*model.stamp_duty_buy_rate
    stt_entry_rate=np.where(g['entry_date']>=dt.date(2026,4,1),model.stt_from_2026_04_01,model.stt_before_2026_04_01)
    stt_exit_rate=model.stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else model.stt_before_2026_04_01
    stt_entry=sell_turnover*stt_entry_rate; stt_exit=far_call_exit*lot*stt_exit_rate
    exercised=np.maximum(g['strike']-float(settlement),0.0)*lot
    exercise_rate=model.exercise_stt_from_2026_04_01 if exit_ts.date()>=dt.date(2026,4,1) else model.exercise_stt_before_2026_04_01
    stt_exercise=exercised*exercise_rate; gst=model.gst_rate*(brokerage+exchange+sebi)
    g['total_costs']=brokerage+exchange+sebi+stamp_entry+stamp_exit+stt_entry+stt_exit+stt_exercise+gst
    g['net_pnl_inr']=g['gross_pnl_inr']-g['total_costs']
    return g

def process_year(a):
    start,end=dt.date.fromisoformat(a.start),dt.date.fromisoformat(a.end)
    sh,sm=map(int,a.entry_start_time.split(':')); eh,em=map(int,a.entry_end_time.split(':'))
    idx=load_index()
    entries=idx[(idx.trading_date>=start)&(idx.trading_date<=end)&
        (((idx.timestamp.dt.hour>sh)|((idx.timestamp.dt.hour==sh)&(idx.timestamp.dt.minute>=sm))))&
        (((idx.timestamp.dt.hour<eh)|((idx.timestamp.dt.hour==eh)&(idx.timestamp.dt.minute<=em))))][['timestamp','trading_date','close']].sort_values('timestamp')
    exps_files=list_nifty_expiry_files(start,end+dt.timedelta(days=35)); exps=[x[0] for x in exps_files]; fn=dict(exps_files)
    cycle_ts=defaultdict(list); need=defaultdict(list); exits=defaultdict(list); cycle_exit={}
    for r in entries.itertuples(index=False):
        p=pair(r.trading_date,exps)
        if not p: continue
        near,far=p; exit_ts,settlement=last_index_bar_on_date(idx,near)
        if exit_ts is None: continue
        cycle_ts[near].append(r.timestamp); need[near].append(r.timestamp); need[far].append(r.timestamp)
        exits[near].append(exit_ts); exits[far].append(exit_ts); cycle_exit[near]=(exit_ts,settlement)
    prepared={}
    def load_one(exp):
        ts=need[exp]+exits[exp]
        return exp,load_option_file(exp,fn[exp],timestamp_min=min(ts),timestamp_max=max(ts))
    with ThreadPoolExecutor(max_workers=6) as pool:
        fs=[pool.submit(load_one,e) for e in sorted(set(need)|set(exits))]
        for f in as_completed(fs):
            e,dd=f.result(); prepared[e]=dd
    spot=entries.set_index('timestamp').close; model=CostModel(slippage_pct=a.slippage_pct,brokerage_per_order_inr=a.brokerage_per_order)
    # The frozen audit is loaded as an independent guard that the expected H1 scan artifact is present.
    audit=pd.read_parquet(a.scan_audit)
    audit['timestamp']=pd.to_datetime(audit['timestamp'])
    audit=audit[(audit.timestamp.dt.date>=start)&(audit.timestamp.dt.date<=end)]
    if audit.empty: raise RuntimeError('Frozen Phase 9G scan audit is empty for this year')
    top2_rows=[]; cycle_rows=[]; candidate_rows=[]
    for near in sorted(cycle_ts):
        timestamps=pd.DatetimeIndex(sorted(set(cycle_ts[near])))
        far=pair(timestamps[0].date(),exps)[1]; n=prepared.get(near); f=prepared.get(far)
        if n is None or f is None: continue
        exit_ts,settlement=cycle_exit[near]; maps=build_far_exit_maps(f,exit_ts)
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
        conflicts=qn.gt(1).any(axis=1).groupby(level=0).sum(); counts=surf.groupby('timestamp').shift_points.nunique(); pos=surf.groupby('timestamp').flatline_inr.apply(lambda x:int((x>0).sum()))
        valid_idx=pd.Index([ts for ts in counts.index if int(counts.loc[ts])==17 and int(conflicts.get(ts,0))==0 and int(pos.get(ts,0))>0])
        if len(valid_idx)==0: continue
        first_ts=valid_idx.min(); h=surf[surf.timestamp.eq(first_ts)].copy(); h=enrich_surface(h,exit_ts,settlement,near,far,maps,model)
        h=h[h.flatline_inr>0].sort_values(['flatline_inr','shift_points'],ascending=[False,True]).reset_index(drop=True)
        if h.empty: continue
        top=h.head(2).copy()
        for rank,row in enumerate(top.itertuples(index=False),1):
            candidate_rows.append({'near_expiry':str(near),'entry_timestamp':str(first_ts),'rank':rank,'shift_points':int(row.shift_points),'strike':float(row.strike),'flatline_inr':float(row.flatline_inr),'gross_pnl_inr':float(row.gross_pnl_inr),'total_costs':float(row.total_costs),'net_pnl_inr':float(row.net_pnl_inr)})
            top2_rows.append({'near_expiry':str(near),'entry_timestamp':str(first_ts),'entry_date':str(pd.Timestamp(first_ts).date()),'rank':rank,'shift_points':int(row.shift_points),'strike':float(row.strike),'flatline_inr':float(row.flatline_inr),'gross_pnl_inr':float(row.gross_pnl_inr),'total_costs':float(row.total_costs),'net_pnl_inr':float(row.net_pnl_inr)})
        cycle_rows.append({'near_expiry':str(near),'entry_timestamp':str(first_ts),'status':'two_positive_candidates' if len(top)==2 else 'only_one_positive_candidate','positive_candidates':int(len(h)),'top1_shift':int(top.iloc[0].shift_points),'top2_shift':None if len(top)<2 else int(top.iloc[1].shift_points),'top1_pnl':float(top.iloc[0].net_pnl_inr),'top2_pnl':None if len(top)<2 else float(top.iloc[1].net_pnl_inr),'combined_pnl':float(top.net_pnl_inr.sum())})
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(top2_rows).to_csv(out/'top2_trade_rows.csv',index=False)
    pd.DataFrame(cycle_rows).to_csv(out/'top2_cycle_summary.csv',index=False)
    pd.DataFrame(candidate_rows).to_csv(out/'top2_ranked_candidates.csv',index=False)
    (out/'metadata.json').write_text(json.dumps({'dataset':DATASET,'start':a.start,'end':a.end,'slippage_pct':a.slippage_pct,'brokerage_per_order_inr':a.brokerage_per_order,'rule':'first valid exact-17-strike positive timestamp; top two distinct positive flatline strikes','rows':len(top2_rows)},indent=2))

def main(): process_year(args())
if __name__=='__main__': main()
