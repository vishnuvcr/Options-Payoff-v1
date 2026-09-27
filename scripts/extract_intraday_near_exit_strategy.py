#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

from src.intraday_selection import max_positive_candidate

from scripts.extract_near_exit_strategy_inputs import (
    DATASET,
    build_entry_lookup,
    build_exit_lookups,
    common_from_lookup,
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
    p.add_argument('--out-selected',default='data/derived/intraday_selected_near_exit.parquet')
    p.add_argument('--out-scan-audit',default='data/derived/intraday_scan_audit.parquet')
    p.add_argument('--out-decision-surface',default='data/derived/intraday_decision_surface.parquet')
    return p.parse_args()

def parse_hm(value):
    h,m=[int(x) for x in value.split(':')]
    return h,m

def main():
    args=parse_args()
    start=dt.date.fromisoformat(args.start)
    end=dt.date.fromisoformat(args.end)
    sh,sm=parse_hm(args.entry_start_time)
    eh,em=parse_hm(args.entry_end_time)
    if (eh,em) < (sh,sm):
        raise ValueError('entry-end-time must be >= entry-start-time')

    index_df=load_index()
    entry_df=index_df[
        (index_df['trading_date']>=start)
        &(index_df['trading_date']<=end)
        &(
            (index_df['timestamp'].dt.hour>sh)
            |((index_df['timestamp'].dt.hour==sh)&(index_df['timestamp'].dt.minute>=sm))
        )
        &(
            (index_df['timestamp'].dt.hour<eh)
            |((index_df['timestamp'].dt.hour==eh)&(index_df['timestamp'].dt.minute<=em))
        )
    ].copy().sort_values('timestamp')
    expiry_files=list_nifty_expiry_files(start,end)
    expiry_dates=[x[0] for x in expiry_files]
    filename_by_expiry=dict(expiry_files)

    day_pairs={}
    cycle_entries=defaultdict(list)
    expiry_entry_times=defaultdict(list)
    expiry_exit_timestamps=defaultdict(list)
    needed_expiries=set()
    for row in entry_df[['timestamp','trading_date']].itertuples(index=False):
        pair=expiry_pair(row.trading_date,expiry_dates)
        if pair is None:
            continue
        near_expiry,far_expiry=pair
        exit_ts,_=last_index_bar_on_date(index_df,near_expiry)
        if exit_ts is None:
            continue
        day_pairs[row.trading_date]=pair
        cycle_entries[near_expiry].append(row.timestamp)
        expiry_entry_times[near_expiry].append(row.timestamp)
        expiry_entry_times[far_expiry].append(row.timestamp)
        expiry_exit_timestamps[near_expiry].append(exit_ts)
        expiry_exit_timestamps[far_expiry].append(exit_ts)
        needed_expiries.update(pair)

    prepared={}
    for expiry in sorted(needed_expiries):
        ts_list=expiry_entry_times.get(expiry,[])
        exit_list=expiry_exit_timestamps.get(expiry,[])
        all_ts=list(ts_list)+list(exit_list)
        tmin=min(all_ts) if all_ts else None
        tmax=max(all_ts) if all_ts else None
        df=load_option_file(expiry,filename_by_expiry[expiry],timestamp_min=tmin,timestamp_max=tmax)
        prepared[expiry]={
            'entry':build_entry_lookup(df),
            'exit':build_exit_lookups(df,exit_list),
        }

    selected=[]
    scan_audit=[]
    decision_surface=[]

    for near_expiry in sorted(cycle_entries):
        far_candidates={}
        for ts in sorted(cycle_entries[near_expiry]):
            pair=day_pairs[pd.Timestamp(ts).date()]
            if pair!=(near_expiry,pair[1]):
                pass
            _,far_expiry=pair
            far_candidates[ts]=far_expiry
        decided=False
        for ts in sorted(cycle_entries[near_expiry]):
            far_expiry=far_candidates[ts]
            near_lookup=prepared[near_expiry]['entry']
            far_lookup=prepared[far_expiry]['entry']
            near_exit_ts,near_settlement=last_index_bar_on_date(index_df,near_expiry)
            if near_exit_ts is None:
                continue
            far_exit_lookup=prepared[far_expiry]['exit'].get(near_expiry,{})
            common=common_from_lookup(near_lookup,far_lookup,ts)
            row_spot=index_df.loc[index_df['timestamp'].eq(ts),'close']
            if row_spot.empty or not common:
                scan_audit.append({'near_expiry':near_expiry,'timestamp':ts,'candidate_count':0,'positive_count':0,'max_positive_flatline_inr':None,'decision':False,'reason':'no_complete_common_strike_surface'})
                continue
            spot=float(row_spot.iloc[0])
            atm=min(common,key=lambda k:abs(k-spot))
            candidates=[]
            for shift in range(-400,401,50):
                strike=atm+shift
                if strike not in common:
                    continue
                nrow=near_lookup.get(ts,{}).get(float(strike),{})
                frow=far_lookup.get(ts,{}).get(float(strike),{})
                if not {'CE','PE'}.issubset(nrow) or not {'CE','PE'}.issubset(frow):
                    continue
                flat=float(nrow['CE'])-float(nrow['PE'])-float(frow['CE'])+float(frow['PE'])
                lot=nifty_lot_size(near_expiry)
                candidates.append({
                    'timestamp':ts,'near_expiry':near_expiry,'far_expiry':far_expiry,
                    'strike':float(strike),'shift_points':int(shift),'spot_at_entry':spot,
                    'near_call_close':float(nrow['CE']),'near_put_close':float(nrow['PE']),
                    'far_call_close':float(frow['CE']),'far_put_close':float(frow['PE']),
                    'near_settlement':near_settlement,'near_exit_timestamp':near_exit_ts,
                    'far_call_exit_close':far_exit_lookup.get((float(strike),'CE'),(None,None))[0],
                    'far_call_exit_timestamp':far_exit_lookup.get((float(strike),'CE'),(None,None))[1],
                    'far_put_exit_close':far_exit_lookup.get((float(strike),'PE'),(None,None))[0],
                    'far_put_exit_timestamp':far_exit_lookup.get((float(strike),'PE'),(None,None))[1],
                    'flatline_per_unit':flat,'flatline_inr':flat*lot,
                })
            positive=[x for x in candidates if x['flatline_inr']>0]
            max_flat=max([x['flatline_inr'] for x in candidates],default=None)
            scan_audit.append({
                'near_expiry':near_expiry,'timestamp':ts,
                'candidate_count':len(candidates),'positive_count':len(positive),
                'max_flatline_inr':max_flat,
                'max_positive_flatline_inr':max([x['flatline_inr'] for x in positive],default=None),
                'decision':bool(positive),'reason':'positive_candidate_found' if positive else 'no_positive_candidate',
            })
            if not positive:
                continue
            winner=max_positive_candidate(candidates)
            if winner is None:
                continue
            # Record the full 17-strike decision surface at the actual decision timestamp.
            for x in candidates:
                x['selected']=bool(x is winner)
                decision_surface.append(x)
            selected.append(winner)
            decided=True
            break

        if not decided:
            # This is not a 09:20 skip. It means the entire available intraday window
            # for the weekly cycle contained no positive candidate.
            pass

    selected_df=pd.DataFrame(selected)
    audit_df=pd.DataFrame(scan_audit)
    surface_df=pd.DataFrame(decision_surface)
    if selected_df.empty:
        raise RuntimeError('No intraday positive opportunities were found')
    Path(args.out_selected).parent.mkdir(parents=True,exist_ok=True)
    selected_df.to_parquet(args.out_selected,index=False)
    audit_df.to_parquet(args.out_scan_audit,index=False)
    surface_df.to_parquet(args.out_decision_surface,index=False)
    meta={
        'dataset':DATASET,'start':args.start,'end':args.end,
        'entry_start_time_ist':args.entry_start_time,'entry_end_time_ist':args.entry_end_time,
        'scan_frequency':'every available NIFTY index timestamp (1-minute source data), beginning at 09:20 IST',
        'skipping_rule':'none based on 09:20; continue intraday and then next trading day within the same weekly cycle until a positive candidate appears',
        'weekly_cycles_scanned':int(audit_df['near_expiry'].nunique()),
        'selected_trades':int(len(selected_df)),
        'selected_chart_positive_pct':float(100*(selected_df['flatline_inr']>0).mean()),
        'scan_rows':int(len(audit_df)),
        'decision_surface_rows':int(len(surface_df)),
    }
    Path(args.out_selected).with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2,default=str),encoding='utf-8')
    print(json.dumps(meta,indent=2,default=str))

if __name__=='__main__':
    main()
