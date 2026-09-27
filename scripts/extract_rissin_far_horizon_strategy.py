#!/usr/bin/env python3
from __future__ import annotations

import argparse, datetime as dt, json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
from huggingface_hub import hf_hub_download

from scripts.extract_near_exit_strategy_inputs import (
    DATASET as SPOT_DATASET,
    list_nifty_expiry_files,
    load_index,
    nifty_lot_size,
    last_index_bar_on_date,
)

RISSIN_DATASET = "rissin/nse-options-intraday"
GRID = list(range(-400,401,50))

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    p.add_argument("--entry-start-time",default="09:20")
    p.add_argument("--entry-end-time",default="15:29")
    p.add_argument("--far-rank",type=int,required=True)
    p.add_argument("--out-selected",required=True)
    p.add_argument("--out-scan-audit",required=True)
    p.add_argument("--out-decision-surface",required=True)
    return p.parse_args()

def hm(v):
    h,m=[int(x) for x in v.split(":")]
    return h,m

def expiry_pair(d, expiries, rank):
    xs=[x for x in expiries if x>=d]
    if len(xs)<=rank:
        return None
    near,far=xs[0],xs[rank]
    return near,far

def normalize(df):
    if df.empty:
        return df
    df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
    df["expiry"]=pd.to_datetime(df["expiry"],errors="coerce").dt.date
    df["strike"]=pd.to_numeric(df["strike"],errors="coerce")
    df["close"]=pd.to_numeric(df["close"],errors="coerce")
    df["option_type"]=df["option_type"].astype(str).str.upper()
    return df.dropna(subset=["timestamp","expiry","strike","close"]).copy()

def load_expiry(dataset, expiry, start_date, end_date):
    e=expiry.isoformat()
    filt=(ds.field("date")>=start_date.isoformat())&(ds.field("date")<=end_date.isoformat())&(ds.field("expiry")==e)
    table=dataset.to_table(filter=filt,columns=["timestamp","expiry","strike","option_type","close"])
    return normalize(table.to_pandas())

def main():
    args=parse_args()
    start=dt.date.fromisoformat(args.start); end=dt.date.fromisoformat(args.end)
    sh,sm=hm(args.entry_start_time); eh,em=hm(args.entry_end_time)
    idx=load_index()
    entry=idx[(idx.trading_date>=start)&(idx.trading_date<=end)]
    entry=entry[((entry.timestamp.dt.hour>sh)|((entry.timestamp.dt.hour==sh)&(entry.timestamp.dt.minute>=sm)))&
                ((entry.timestamp.dt.hour<eh)|((entry.timestamp.dt.hour==eh)&(entry.timestamp.dt.minute<=em)))]
    entry=entry[["timestamp","trading_date","close"]].sort_values("timestamp")
    if entry.empty: raise RuntimeError("No entry timestamps")

    expiry_files=list_nifty_expiry_files(start,end+dt.timedelta(days=35))
    expiries=[x[0] for x in expiry_files]
    local=hf_hub_download(repo_id=RISSIN_DATASET,filename=f"upstox_intraday/NIFTY/NIFTY_{start.year}.parquet",repo_type="dataset")
    dataset=ds.dataset(local,format="parquet")

    cycles={}
    for row in entry.itertuples(index=False):
        pair=expiry_pair(row.trading_date,expiries,1)
        if pair is None: continue
        cycles.setdefault(pair[0],[]).append(row)

    selected=[]; scans=[]; surfaces=[]
    for near_expiry,cycle_rows in sorted(cycles.items()):
        timestamps=sorted({r.timestamp for r in cycle_rows})
        if not timestamps: continue
        first_date=min(t.date() for t in timestamps)
        pair=expiry_pair(first_date,expiries,args.far_rank)
        if pair is None or pair[0]!=near_expiry: continue
        far_expiry=pair[1]
        exit_ts,settlement=last_index_bar_on_date(idx,near_expiry)
        if exit_ts is None: continue

        near_df=load_expiry(dataset,near_expiry,first_date,near_expiry)
        far_df=load_expiry(dataset,far_expiry,first_date,near_expiry)
        if near_df.empty or far_df.empty:
            # create audit rows showing unavailable coverage
            scans.append(pd.DataFrame({"near_expiry":[near_expiry]*len(timestamps),"timestamp":timestamps,
                "candidate_row_count":[0]*len(timestamps),"candidate_shift_count":[0]*len(timestamps),
                "shift_set_complete":[False]*len(timestamps),"conflicting_shift_count":[0]*len(timestamps),
                "positive_count":[0]*len(timestamps),"max_flatline_inr":[np.nan]*len(timestamps),
                "max_positive_flatline_inr":[np.nan]*len(timestamps),"decision":[False]*len(timestamps),
                "reason":["no_far_or_near_source_rows"]*len(timestamps)}))
            continue

        nce=near_df[near_df.option_type.eq("CE")][["timestamp","strike","close"]].rename(columns={"close":"near_call"})
        npe=near_df[near_df.option_type.eq("PE")][["timestamp","strike","close"]].rename(columns={"close":"near_put"})
        fce=far_df[far_df.option_type.eq("CE")][["timestamp","strike","close"]].rename(columns={"close":"far_call"})
        fpe=far_df[far_df.option_type.eq("PE")][["timestamp","strike","close"]].rename(columns={"close":"far_put"})
        surf=nce.merge(npe,on=["timestamp","strike"],how="inner").merge(fce,on=["timestamp","strike"],how="inner").merge(fpe,on=["timestamp","strike"],how="inner")
        surf=surf[surf.timestamp.isin(timestamps)].copy()
        if surf.empty: continue
        spot=entry.set_index("timestamp")["close"]
        surf["spot"]=surf.timestamp.map(spot)
        surf=surf.dropna(subset=["spot"])
        if surf.empty: continue

        atm=surf.assign(absdiff=(surf.strike-surf.spot).abs()).sort_values(["timestamp","absdiff","strike"]).drop_duplicates("timestamp")[["timestamp","strike"]].rename(columns={"strike":"atm"})
        surf=surf.merge(atm,on="timestamp",how="left")
        surf["shift_points"]=surf.strike-surf.atm
        surf=surf[(surf.shift_points>=-400)&(surf.shift_points<=400)&(surf.shift_points%50==0)].copy()
        lot=nifty_lot_size(near_expiry)
        surf["flatline_per_unit"]=surf.near_call-surf.near_put-surf.far_call+surf.far_put
        surf["flatline_inr"]=surf.flatline_per_unit*lot

        all_times=pd.DataFrame({"timestamp":pd.DatetimeIndex(timestamps)})
        agg=surf.groupby("timestamp").agg(candidate_row_count=("strike","size"),candidate_shift_count=("shift_points","nunique"),max_flatline_inr=("flatline_inr","max")).reset_index()
        qn=surf.groupby(["timestamp","shift_points"])[["near_call","near_put","far_call","far_put"]].nunique()
        conflicts=qn.gt(1).any(axis=1).groupby(level=0).sum().rename("conflicting_shift_count").reset_index()
        shift_sets=surf.groupby("timestamp").shift_points.agg(lambda s:frozenset(pd.to_numeric(s,errors="coerce").dropna().astype(int))).rename("shift_set").reset_index()
        posmax=surf[surf.flatline_inr>0].groupby("timestamp").agg(positive_count=("shift_points","nunique"),max_positive_flatline_inr=("flatline_inr","max")).reset_index()
        aud=all_times.merge(agg,on="timestamp",how="left").merge(conflicts,on="timestamp",how="left").merge(shift_sets,on="timestamp",how="left").merge(posmax,on="timestamp",how="left")
        for c in ["candidate_row_count","candidate_shift_count","conflicting_shift_count","positive_count"]: aud[c]=aud[c].fillna(0).astype(int)
        aud["shift_set_complete"]=aud.shift_set.map(lambda s:isinstance(s,frozenset) and s==frozenset(GRID))
        aud["near_expiry"]=near_expiry
        aud["decision"]=aud.shift_set_complete&(aud.conflicting_shift_count==0)&(aud.positive_count>0)
        aud["reason"]="no_positive_candidate"
        aud.loc[(~aud.shift_set_complete)&(aud.positive_count>0),"reason"]="incomplete_17_strike_set"
        aud.loc[aud.shift_set_complete&(aud.conflicting_shift_count>0)&(aud.positive_count>0),"reason"]="conflicting_duplicate_quotes"
        aud.loc[aud.decision,"reason"]="positive_candidate_found"
        scans.append(aud[["near_expiry","timestamp","candidate_row_count","candidate_shift_count","shift_set_complete","conflicting_shift_count","positive_count","max_flatline_inr","max_positive_flatline_inr","decision","reason"]])

        valid=set(aud.loc[aud.decision,"timestamp"])
        positive=surf[(surf.flatline_inr>0)&surf.timestamp.isin(valid)].sort_values(["timestamp","flatline_inr","shift_points"],ascending=[True,False,True])
        if positive.empty: continue
        win=positive.iloc[0]
        ts=win.timestamp
        sdec=surf[surf.timestamp.eq(ts)].copy()
        sdec["near_expiry"]=near_expiry; sdec["far_expiry"]=far_expiry; sdec["selected"]=False
        sdec.loc[(sdec.strike==win.strike)&(sdec.shift_points==win.shift_points),"selected"]=True
        surfaces.append(sdec[["timestamp","near_expiry","far_expiry","spot","atm","shift_points","strike","near_call","near_put","far_call","far_put","flatline_per_unit","flatline_inr","selected"]])

        # Far legs are manually closed at the final index bar on or before near-expiry close.
        fexit=far_df[(far_df.timestamp.dt.date==exit_ts.date())&(far_df.timestamp<=exit_ts)&(far_df.strike==float(win.strike))]
        fc=fexit[fexit.option_type.eq("CE")].sort_values("timestamp")
        fp=fexit[fexit.option_type.eq("PE")].sort_values("timestamp")
        fcrow=fc.iloc[-1] if not fc.empty else None; fprow=fp.iloc[-1] if not fp.empty else None
        selected.append({
            "entry_timestamp":ts,"entry_date":ts.date(),"spot_at_entry":float(win.spot),
            "near_expiry":near_expiry,"far_expiry":far_expiry,"near_exit_timestamp":exit_ts,
            "far_call_exit_timestamp":None if fcrow is None else fcrow.timestamp,
            "far_put_exit_timestamp":None if fprow is None else fprow.timestamp,
            "candidate_label":"ATM" if int(win.shift_points)==0 else ("ATM_PLUS_%d"%abs(int(win.shift_points)) if int(win.shift_points)>0 else "ATM_MINUS_%d"%abs(int(win.shift_points))),
            "shift_points":int(win.shift_points),"strike":float(win.strike),
            "near_call_close":float(win.near_call),"near_put_close":float(win.near_put),
            "far_call_close":float(win.far_call),"far_put_close":float(win.far_put),
            "near_settlement":float(settlement),
            "far_call_exit_close":None if fcrow is None else float(fcrow.close),
            "far_put_exit_close":None if fprow is None else float(fprow.close),
            "execution_fidelity":"1-minute Rissin/Upstox historical close proxy; first valid timestamp from 09:20 to 15:29",
            "near_lot_size":lot,"far_lot_size":nifty_lot_size(far_expiry),
            "net_entry_cashflow_per_unit":float(win.flatline_per_unit),"flatline_per_unit":float(win.flatline_per_unit),"flatline_inr":float(win.flatline_inr)
        })

    cols=['entry_timestamp','entry_date','spot_at_entry','near_expiry','far_expiry','near_exit_timestamp','far_call_exit_timestamp','far_put_exit_timestamp','candidate_label','shift_points','strike','near_call_close','near_put_close','far_call_close','far_put_close','near_settlement','far_call_exit_close','far_put_exit_close','execution_fidelity','near_lot_size','far_lot_size','net_entry_cashflow_per_unit','flatline_per_unit','flatline_inr']
    selected_df=pd.DataFrame(selected)
    if selected_df.empty: selected_df=pd.DataFrame(columns=cols)
    else: selected_df=selected_df.sort_values("entry_timestamp").reset_index(drop=True)
    scan_df=pd.concat(scans,ignore_index=True) if scans else pd.DataFrame()
    surf_df=pd.concat(surfaces,ignore_index=True) if surfaces else pd.DataFrame()
    Path(args.out_selected).parent.mkdir(parents=True,exist_ok=True)
    selected_df.to_parquet(args.out_selected,index=False)
    scan_df.to_parquet(args.out_scan_audit,index=False)
    surf_df.to_parquet(args.out_decision_surface,index=False)
    meta={
        "dataset":RISSIN_DATASET,"start":args.start,"end":args.end,"far_rank":args.far_rank,
        "entry_start_time_ist":args.entry_start_time,"entry_end_time_ist":args.entry_end_time,
        "scan_frequency":"every available NIFTY 1-minute timestamp",
        "skipping_rule":"continue intraday and later trading days until first valid positive candidate in each weekly cycle",
        "weekly_cycles_with_opportunity":int(selected_df.near_expiry.nunique()),
        "selected_trades":int(len(selected_df)),
        "selected_chart_positive_pct":float(100*(selected_df.flatline_inr>0).mean()) if not selected_df.empty else None,
        "scan_rows":int(len(scan_df)),"decision_surface_rows":int(len(surf_df)),
        "exact_17_shift_timestamp_count":int(scan_df.shift_set_complete.sum()) if not scan_df.empty else 0,
        "incomplete_positive_timestamp_count":int(((~scan_df.shift_set_complete)&(scan_df.positive_count>0)).sum()) if not scan_df.empty else 0,
        "conflicting_duplicate_quote_timestamp_count":int(((scan_df.conflicting_shift_count>0)&(scan_df.positive_count>0)).sum()) if not scan_df.empty else 0
    }
    Path(args.out_selected).with_suffix(".metadata.json").write_text(json.dumps(meta,indent=2,default=str))
    print(json.dumps(meta,indent=2,default=str))

if __name__=="__main__": main()
