#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import pandas as pd
import pyarrow.dataset as ds
from huggingface_hub import hf_hub_download

from scripts.extract_near_exit_strategy_inputs import DATASET as BASE_INDEX_DATASET, list_nifty_expiry_files, load_index

RISSIN_DATASET = "rissin/nse-options-intraday"
GRID = list(range(-400, 401, 50))

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--years", default="2024,2025,2026")
    p.add_argument("--cycles-per-year", type=int, default=8)
    p.add_argument("--sample-times", default="09:20,10:00,12:00,15:00")
    p.add_argument("--out-dir", default="results/phase9g_rissin_source_validation")
    return p.parse_args()

def parse_hm(v):
    h,m=[int(x) for x in v.split(":")]
    return h,m

def expiry_pair(entry_date, expiries, rank):
    xs=[x for x in expiries if x >= entry_date]
    if len(xs) <= rank:
        return None
    return xs[0], xs[rank]

def day_slice(dataset, trading_day):
    start=f"{trading_day.isoformat()} 00:00:00"
    end=f"{trading_day.isoformat()} 23:59:59"
    filt=(ds.field("timestamp") >= start) & (ds.field("timestamp") <= end)
    table=dataset.to_table(filter=filt, columns=["timestamp","expiry","strike","option_type","close","underlying"])
    if table.num_rows==0:
        return pd.DataFrame(columns=["timestamp","expiry","strike","option_type","close","underlying"])
    x=table.to_pandas()
    x["timestamp"]=pd.to_datetime(x["timestamp"],errors="coerce")
    x["expiry"]=pd.to_datetime(x["expiry"],errors="coerce").dt.date
    x["strike"]=pd.to_numeric(x["strike"],errors="coerce")
    x["close"]=pd.to_numeric(x["close"],errors="coerce")
    x["option_type"]=x["option_type"].astype(str).str.upper()
    return x.dropna(subset=["timestamp","expiry","strike","close"])

def common_grid_count(day_df, ts, far_expiry, spot):
    x=day_df[(day_df["timestamp"].eq(ts)) & (day_df["expiry"].eq(far_expiry)) & day_df["option_type"].isin(["CE","PE"])]
    both=x.groupby("strike")["option_type"].nunique()
    strikes=set(both[both>=2].index.astype(float))
    if not strikes:
        return {"far_rows":0,"common_both_strikes":0,"grid_present_count":0,"grid_present_shifts":[],"atm":None}
    atm=min(strikes,key=lambda k:(abs(k-spot),k))
    shifts={int(round(k-atm)) for k in strikes if -400<=k-atm<=400 and abs((k-atm)%50)<1e-9}
    return {
        "far_rows":int(len(x)),
        "common_both_strikes":int(len(strikes)),
        "grid_present_count":int(len(set(GRID)&shifts)),
        "grid_present_shifts":sorted(set(GRID)&shifts),
        "atm":float(atm)
    }

def main():
    args=parse_args()
    years=[int(x) for x in args.years.split(",") if x.strip()]
    sample_times=[parse_hm(x) for x in args.sample_times.split(",")]

    index_df=load_index()
    expiry_files=list_nifty_expiry_files(dt.date(min(years),1,1),dt.date(max(years),12,31)+dt.timedelta(days=35))
    expiries=[x[0] for x in expiry_files]

    rows=[]
    file_meta=[]

    for year in years:
        filename=f"upstox_intraday/NIFTY/NIFTY_{year}.parquet"
        local=hf_hub_download(repo_id=RISSIN_DATASET,filename=filename,repo_type="dataset")
        dataset=ds.dataset(local,format="parquet")
        schema=[f.name+":"+str(f.type) for f in dataset.schema]
        file_meta.append({"year":year,"filename":filename,"schema":schema})

        year_idx=index_df[index_df["trading_date"].map(lambda d:d.year==year)].copy()
        near_expiries=sorted({e for e in expiries if e.year==year})
        chosen=[]
        for near in near_expiries:
            candidates=year_idx[(year_idx["trading_date"]<=near)&(year_idx["trading_date"]>=near-dt.timedelta(days=6))]
            if candidates.empty:
                continue
            entry_date=min(candidates["trading_date"].unique())
            if entry_date not in chosen:
                chosen.append(entry_date)
            if len(chosen)>=args.cycles_per_year:
                break

        for entry_date in chosen:
            for ts_hour,ts_min in sample_times:
                idx=year_idx[(year_idx["trading_date"]==entry_date)&(year_idx["timestamp"].dt.hour==ts_hour)&(year_idx["timestamp"].dt.minute==ts_min)]
                if idx.empty:
                    continue
                idxrow=idx.iloc[0]
                ts=idxrow["timestamp"]
                spot=float(idxrow["close"])
                day_df=day_slice(dataset,entry_date)
                for rank in (2,3):
                    pair=expiry_pair(entry_date,expiries,rank)
                    if pair is None:
                        continue
                    near,far=pair
                    stats=common_grid_count(day_df,ts,far,spot)
                    rows.append({
                        "year":year,"entry_date":str(entry_date),"entry_timestamp":str(ts),
                        "far_rank":rank,"near_expiry":str(near),"far_expiry":str(far),
                        "spot":spot,**stats
                    })

    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/"coverage_samples.csv",index=False)
    pd.DataFrame(file_meta).to_json(out/"source_file_metadata.json",orient="records",indent=2)

    sample=pd.DataFrame(rows)
    summary=[]
    if not sample.empty:
        for rank,g in sample.groupby("far_rank"):
            summary.append({
                "far_rank":int(rank),
                "samples":int(len(g)),
                "samples_with_far_rows":int((g.far_rows>0).sum()),
                "samples_with_common_ce_pe_strikes":int((g.common_both_strikes>0).sum()),
                "samples_with_exact_17_grid":int((g.grid_present_count==17).sum()),
                "mean_far_rows":float(g.far_rows.mean()),
                "mean_common_both_strikes":float(g.common_both_strikes.mean()),
                "mean_grid_present_count":float(g.grid_present_count.mean())
            })
    pd.DataFrame(summary).to_csv(out/"summary.csv",index=False)
    meta={
        "source":RISSIN_DATASET,
        "index_reference_dataset":BASE_INDEX_DATASET,
        "years":years,
        "cycles_per_year":args.cycles_per_year,
        "sample_times":args.sample_times,
        "purpose":"Validate whether an independent intraday dataset contains pre-entry observations for far weekly expiries and the exact 17-strike grid."
    }
    (out/"metadata.json").write_text(json.dumps(meta,indent=2))
    print(json.dumps({"metadata":meta,"summary":summary},indent=2))

if __name__=="__main__":
    main()
