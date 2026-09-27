#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    expiry_pair,
    last_index_bar_on_date,
    list_nifty_expiry_files,
    load_index,
    load_option_file,
    nifty_lot_size,
)

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--start',required=True)
    p.add_argument('--end',required=True)
    p.add_argument('--entry-start-time',default='09:20')
    p.add_argument('--entry-end-time',default='15:29')
    p.add_argument('--download-workers',type=int,default=6)
    p.add_argument('--far-rank',type=int,default=1)
    p.add_argument('--out-selected',default='data/derived/intraday_selected_near_exit.parquet')
    p.add_argument('--out-scan-audit',default='data/derived/intraday_scan_audit.parquet')
    p.add_argument('--out-decision-surface',default='data/derived/intraday_decision_surface.parquet')
    return p.parse_args()

def expiry_pair(entry_date, expiries, far_rank):
    if far_rank < 1:
        raise ValueError('far-rank must be >= 1')
    xs=[x for x in expiries if x >= entry_date]
    if len(xs) <= far_rank:
        return None
    near, far=xs[0], xs[far_rank]
    # Weekly horizons H1/H2/H3 can extend up to three weekly intervals.
    if (far-near).days > 30:
        return None
    return near, far

def parse_hm(value):
    h,m=[int(x) for x in value.split(':')]
    return h,m

def _last_option_quote(df,strike,option_type,exit_ts):
    x=df[(df['trading_date']==exit_ts.date())&(df['timestamp']<=exit_ts)&(df['strike']==float(strike))&(df['option_type']==option_type)]
    if x.empty:
        return None,None
    r=x.sort_values('timestamp').iloc[-1]
    return float(r['close']),r['timestamp']

def _prepare_expiry(expiry,filename,timestamps):
    vals=list(timestamps)
    if not vals:
        return expiry,None
    return expiry,load_option_file(expiry,filename,timestamp_min=min(vals),timestamp_max=max(vals))

def main():
    args=parse_args()
    start=dt.date.fromisoformat(args.start)
    end=dt.date.fromisoformat(args.end)
    sh,sm=parse_hm(args.entry_start_time)
    eh,em=parse_hm(args.entry_end_time)
    if (eh,em)<(sh,sm):
        raise ValueError('entry-end-time must be >= entry-start-time')

    index_df=load_index()
    entry_df=index_df[
        (index_df['trading_date']>=start)&
        (index_df['trading_date']<=end)&
        ((index_df['timestamp'].dt.hour>sh)|((index_df['timestamp'].dt.hour==sh)&(index_df['timestamp'].dt.minute>=sm)))&
        ((index_df['timestamp'].dt.hour<eh)|((index_df['timestamp'].dt.hour==eh)&(index_df['timestamp'].dt.minute<=em)))
    ][['timestamp','trading_date','close']].sort_values('timestamp').copy()
    if entry_df.empty:
        raise RuntimeError('No intraday index timestamps found')

    expiry_files=list_nifty_expiry_files(start,end+dt.timedelta(days=35))
    expiry_dates=[x[0] for x in expiry_files]
    filename_by_expiry=dict(expiry_files)

    day_pair={}
    cycle_timestamps=defaultdict(list)
    expiry_needed_timestamps=defaultdict(list)
    expiry_exit_ts=defaultdict(list)
    cycle_exit_info={}

    for r in entry_df.itertuples(index=False):
        pair=expiry_pair(r.trading_date,expiry_dates,args.far_rank)
        if pair is None:
            continue
        near_expiry,far_expiry=pair
        exit_ts,settlement=last_index_bar_on_date(index_df,near_expiry)
        if exit_ts is None:
            continue
        day_pair[r.trading_date]=pair
        cycle_timestamps[near_expiry].append(r.timestamp)
        expiry_needed_timestamps[near_expiry].append(r.timestamp)
        expiry_needed_timestamps[far_expiry].append(r.timestamp)
        expiry_exit_ts[near_expiry].append(exit_ts)
        expiry_exit_ts[far_expiry].append(exit_ts)
        cycle_exit_info[near_expiry]=(exit_ts,settlement)

    needed=sorted(set(expiry_needed_timestamps)|set(expiry_exit_ts))
    prepared={}
    workers=max(1,min(args.download_workers,8))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures=[ex.submit(_prepare_expiry,expiry,filename_by_expiry[expiry],expiry_needed_timestamps[expiry]+expiry_exit_ts[expiry]) for expiry in needed]
        for f in as_completed(futures):
            expiry,df=f.result()
            prepared[expiry]=df

    spot_lookup=entry_df.set_index('timestamp')['close']
    selected=[]
    scan_audit=[]
    decision_surface=[]

    for near_expiry in sorted(cycle_timestamps):
        timestamps=pd.DatetimeIndex(sorted(set(cycle_timestamps[near_expiry])))
        far_expiry=expiry_pair(timestamps[0].date(),expiry_dates,args.far_rank)[1]
        near_df=prepared.get(near_expiry)
        far_df=prepared.get(far_expiry)
        if near_df is None or far_df is None:
            continue

        nce=near_df[near_df['option_type'].eq('CE')][['timestamp','strike','close']].rename(columns={'close':'near_call'})
        npe=near_df[near_df['option_type'].eq('PE')][['timestamp','strike','close']].rename(columns={'close':'near_put'})
        fce=far_df[far_df['option_type'].eq('CE')][['timestamp','strike','close']].rename(columns={'close':'far_call'})
        fpe=far_df[far_df['option_type'].eq('PE')][['timestamp','strike','close']].rename(columns={'close':'far_put'})

        surf=nce.merge(npe,on=['timestamp','strike'],how='inner').merge(fce,on=['timestamp','strike'],how='inner').merge(fpe,on=['timestamp','strike'],how='inner')
        surf=surf[surf['timestamp'].isin(timestamps)].copy()
        if surf.empty:
            continue
        surf['spot']=surf['timestamp'].map(spot_lookup)
        surf=surf.dropna(subset=['spot'])
        if surf.empty:
            continue

        surf['absdiff']=(surf['strike']-surf['spot']).abs()
        atm=surf.sort_values(['timestamp','absdiff','strike']).drop_duplicates('timestamp')[['timestamp','strike']].rename(columns={'strike':'atm'})
        surf=surf.merge(atm,on='timestamp',how='left')
        surf['shift_points']=surf['strike']-surf['atm']
        surf=surf[(surf['shift_points']>=-400)&(surf['shift_points']<=400)&(surf['shift_points']%50==0)].copy()
        lot=nifty_lot_size(near_expiry)
        surf['flatline_per_unit']=surf['near_call']-surf['near_put']-surf['far_call']+surf['far_put']
        surf['flatline_inr']=surf['flatline_per_unit']*lot

        all_times=pd.DataFrame({'timestamp':timestamps})
        aud=surf.groupby('timestamp').agg(
            candidate_row_count=('strike','size'),
            candidate_shift_count=('shift_points','nunique'),
            max_flatline_inr=('flatline_inr','max')
        ).reset_index()
        quote_nuniq=surf.groupby(['timestamp','shift_points'])[['near_call','near_put','far_call','far_put']].nunique()
        conflicting_shift_count=quote_nuniq.gt(1).any(axis=1).groupby(level=0).sum().rename('conflicting_shift_count').reset_index()
        aud=aud.merge(conflicting_shift_count,on='timestamp',how='left')
        pos=surf[surf['flatline_inr']>0].groupby('timestamp').size().rename('positive_count')
        pmax=surf[surf['flatline_inr']>0].groupby('timestamp')['flatline_inr'].max().rename('max_positive_flatline_inr')
        aud=all_times.merge(aud,on='timestamp',how='left').merge(pos,on='timestamp',how='left').merge(pmax,on='timestamp',how='left')
        for col in ['candidate_row_count','candidate_shift_count','conflicting_shift_count','positive_count']:
            aud[col]=aud[col].fillna(0).astype(int)
        aud['near_expiry']=near_expiry
        # The strategy requires all 17 unique strike shifts and unambiguous quotes.
        aud['decision']=(aud['candidate_shift_count']==17) & (aud['conflicting_shift_count']==0) & (aud['positive_count']>0)
        aud['reason']='no_positive_candidate'
        aud.loc[(aud['candidate_shift_count']!=17) & (aud['positive_count']>0),'reason']='incomplete_17_strike_set'
        aud.loc[(aud['candidate_shift_count']==17) & (aud['conflicting_shift_count']>0) & (aud['positive_count']>0),'reason']='conflicting_duplicate_quotes'
        aud.loc[aud['decision'],'reason']='positive_candidate_found'
        scan_audit.append(aud[['near_expiry','timestamp','candidate_row_count','candidate_shift_count','conflicting_shift_count','positive_count','max_flatline_inr','max_positive_flatline_inr','decision','reason']])

        valid_times=set(aud.loc[aud['decision'],'timestamp'])
        positive=surf[(surf['flatline_inr']>0) & (surf['timestamp'].isin(valid_times))].sort_values(['timestamp','flatline_inr','shift_points'],ascending=[True,False,True])
        if positive.empty:
            continue
        win=positive.iloc[0].copy()
        decision_ts=win['timestamp']
        surf_dec=surf[surf['timestamp'].eq(decision_ts)].copy()
        surf_dec['near_expiry']=near_expiry
        surf_dec['far_expiry']=far_expiry
        surf_dec['selected']=False
        surf_dec.loc[(surf_dec['strike']==win['strike'])&(surf_dec['shift_points']==win['shift_points']),'selected']=True
        decision_surface.append(surf_dec[['timestamp','near_expiry','far_expiry','spot','atm','shift_points','strike','near_call','near_put','far_call','far_put','flatline_per_unit','flatline_inr','selected']])

        exit_ts,near_settlement=cycle_exit_info[near_expiry]
        fc,fc_ts=_last_option_quote(far_df,win['strike'],'CE',exit_ts)
        fp,fp_ts=_last_option_quote(far_df,win['strike'],'PE',exit_ts)
        selected.append({
            'entry_timestamp':decision_ts,'entry_date':pd.Timestamp(decision_ts).date(),'spot_at_entry':float(win['spot']),
            'near_expiry':near_expiry,'far_expiry':far_expiry,'near_exit_timestamp':exit_ts,
            'far_call_exit_timestamp':fc_ts,'far_put_exit_timestamp':fp_ts,
            'candidate_label':'ATM' if int(win['shift_points'])==0 else ('ATM_PLUS_%d'%abs(int(win['shift_points'])) if int(win['shift_points'])>0 else 'ATM_MINUS_%d'%abs(int(win['shift_points']))),
            'shift_points':int(win['shift_points']),'strike':float(win['strike']),
            'near_call_close':float(win['near_call']),'near_put_close':float(win['near_put']),
            'far_call_close':float(win['far_call']),'far_put_close':float(win['far_put']),
            'near_settlement':float(near_settlement),'far_call_exit_close':fc,'far_put_exit_close':fp,
            'execution_fidelity':'1-minute historical close proxy; selection checked every available timestamp from 09:20 through 15:29',
            'near_lot_size':lot,'far_lot_size':nifty_lot_size(far_expiry),
            'net_entry_cashflow_per_unit':float(win['flatline_per_unit']),
            'flatline_per_unit':float(win['flatline_per_unit']),'flatline_inr':float(win['flatline_inr']),
        })
        # Do not check later timestamps in this weekly cycle after the first positive timestamp.

    selected_columns=[
        'entry_timestamp','entry_date','spot_at_entry','near_expiry','far_expiry',
        'near_exit_timestamp','far_call_exit_timestamp','far_put_exit_timestamp',
        'candidate_label','shift_points','strike','near_call_close','near_put_close',
        'far_call_close','far_put_close','near_settlement','far_call_exit_close',
        'far_put_exit_close','execution_fidelity','near_lot_size','far_lot_size',
        'net_entry_cashflow_per_unit','flatline_per_unit','flatline_inr'
    ]
    selected_df=pd.DataFrame(selected)
    if selected_df.empty:
        selected_df=pd.DataFrame(columns=selected_columns)
    else:
        selected_df=selected_df.sort_values('entry_timestamp').reset_index(drop=True)
    audit_df=pd.concat(scan_audit,ignore_index=True) if scan_audit else pd.DataFrame()
    surface_df=pd.concat(decision_surface,ignore_index=True) if decision_surface else pd.DataFrame()
    Path(args.out_selected).parent.mkdir(parents=True,exist_ok=True)
    selected_df.to_parquet(args.out_selected,index=False)
    audit_df.to_parquet(args.out_scan_audit,index=False)
    surface_df.to_parquet(args.out_decision_surface,index=False)
    meta={
        'dataset':DATASET,'start':args.start,'end':args.end,'expiry_file_search_end':(end+dt.timedelta(days=35)).isoformat(),
        'entry_start_time_ist':args.entry_start_time,'entry_end_time_ist':args.entry_end_time,'far_rank':args.far_rank,
        'scan_frequency':'every available NIFTY 1-minute timestamp',
        'skipping_rule':'none based on 09:20; continue intraday and across following trading days until first positive candidate in each weekly cycle',
        'weekly_cycles_with_opportunity':int(selected_df['near_expiry'].nunique()),
        'selected_trades':int(len(selected_df)),
        'selected_chart_positive_pct':float(100*(selected_df['flatline_inr']>0).mean()),'horizon_label':f'H{args.far_rank}',
        'scan_rows':int(len(audit_df)),'decision_surface_rows':int(len(surface_df)),
        'complete_17_unique_shift_timestamp_count':int((audit_df['candidate_shift_count']==17).sum()) if not audit_df.empty else 0,
        'incomplete_positive_timestamp_count':int(((audit_df['candidate_shift_count']!=17)&(audit_df['positive_count']>0)).sum()) if not audit_df.empty else 0,
        'conflicting_duplicate_quote_timestamp_count':int(((audit_df['conflicting_shift_count']>0)&(audit_df['positive_count']>0)).sum()) if not audit_df.empty else 0,
    }
    Path(args.out_selected).with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2,default=str),encoding='utf-8')
    print(json.dumps(meta,indent=2,default=str))

if __name__=='__main__':
    main()
