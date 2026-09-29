#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd

def dd(x):
    c=np.cumsum(np.asarray(x,float));return float(np.min(c-np.maximum.accumulate(np.r_[0.,c])[:-1])) if len(c) else 0.
def pf(x):
    x=np.asarray(x,float);w=x[x>0].sum();l=-x[x<0].sum();return w/l if l else np.inf
def boot(x,reps=20000,seed=20260929):
    x=np.asarray(x,float);rng=np.random.default_rng(seed);return np.quantile([np.mean(rng.choice(x,len(x),replace=True)) for _ in range(reps)],[.025,.975])

def main():
    p=argparse.ArgumentParser();p.add_argument("--margin-ledger",required=True);p.add_argument("--out-dir",required=True);a=p.parse_args()
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(a.margin_ledger)
    d["entry_timestamp"]=pd.to_datetime(d["entry_timestamp"],utc=True)
    d["net_pnl_inr"]=pd.to_numeric(d["net_pnl_inr"],errors="raise")
    d["margin_required_inr"]=pd.to_numeric(d["margin_required_inr"],errors="raise")
    d["chart_pnl_inr"]=pd.to_numeric(d["chart_pnl_inr"],errors="raise")
    d=d.sort_values(["entry_timestamp","rank"])
    variants={}
    rank1=d[d.rank.eq(1)].groupby("near_expiry",as_index=False).agg(net_pnl_inr=("net_pnl_inr","sum"),margin_required_inr=("margin_required_inr","sum"))
    variants["1x_rank1"]=rank1
    x=rank1.copy();x["net_pnl_inr"]*=2;x["margin_required_inr"]*=2;variants["2x_rank1"]=x
    literal=d.groupby("near_expiry",as_index=False).agg(net_pnl_inr=("net_pnl_inr","sum"),margin_required_inr=("margin_required_inr","sum"))
    variants["literal_top2"]=literal
    pos=d[(d.rank.eq(1)) | ((d.rank.eq(2)) & (d.chart_pnl_inr>0))]
    positive=pos.groupby("near_expiry",as_index=False).agg(net_pnl_inr=("net_pnl_inr","sum"),margin_required_inr=("margin_required_inr","sum"))
    variants["top2_positive"]=positive
    rows=[]
    for name,x in variants.items():
        pnl=x.net_pnl_inr.to_numpy(float);margin=x.margin_required_inr.to_numpy(float)
        lo,hi=boot(pnl)
        rows.append({"variant":name,"weekly_cycles":len(x),"net_pnl_inr":pnl.sum(),"mean_pnl_inr":pnl.mean(),"win_rate_pct":100*(pnl>0).mean(),"profit_factor":pf(pnl),"max_drawdown_inr":dd(pnl),"total_margin_capital_inr":margin.sum(),"mean_margin_inr":margin.mean(),"net_pnl_per_1_lakh_margin":100000*pnl.sum()/margin.sum(),"mean_cycle_pnl_per_1_lakh_margin":100000*np.mean(pnl/margin),"bootstrap_mean_low_inr":lo,"bootstrap_mean_high_inr":hi})
    summary=pd.DataFrame(rows);summary.to_csv(out/"sizing_margin_summary.csv",index=False)
    summary["margin_efficiency_rank"]=summary["net_pnl_per_1_lakh_margin"].rank(ascending=False,method="min")
    summary.to_csv(out/"sizing_margin_summary.csv",index=False)
    (out/"PHASE10F_RESULTS.md").write_text(f"""# Phase 10F — Margin-normalized sizing

**Status:** COMPLETE — no sizing change adopted.

## Variants
- 1× rank-1 frozen control.
- 2× rank-1 same strike.
- literal top-two distinct strikes.
- top-two-positive: rank-1 plus rank-2 only when rank-2 static flatline is positive.

Historical daily NSE/NSCCL SPAN i1 is used for required margin. Two-lot margin is doubled for the same position; top-two variants sum position-level SPAN requirements.

## Results

{summary.to_markdown(index=False)}

## Interpretation

The sizing comparison is descriptive and does not constitute a strategy promotion. Any candidate still requires Phase 10G chronological holdout.
""")
    print(summary.to_string(index=False))

if __name__=="__main__":main()
