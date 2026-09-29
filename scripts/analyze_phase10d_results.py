#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd

def block_ci(x,reps=20000,block=4,seed=20260929):
    x=np.asarray(x,float)
    if not len(x): return (np.nan,np.nan)
    rng=np.random.default_rng(seed)
    blocks=[x[i:i+block] for i in range(len(x))]
    vals=[]
    for _ in range(reps):
        draw=[]
        while len(draw)<len(x): draw.extend(blocks[int(rng.integers(0,len(blocks)))])
        vals.append(np.mean(draw[:len(x)]))
    return float(np.quantile(vals,.025)),float(np.quantile(vals,.975))

def perm_p(x,reps=20000,seed=20260929):
    x=np.asarray(x,float)
    if not len(x): return np.nan
    rng=np.random.default_rng(seed); obs=abs(x.mean()); n=0
    for _ in range(reps):
        if abs((rng.choice([-1.,1.],len(x))*x).mean())>=obs:n+=1
    return (n+1)/(reps+1)

def pf(x):
    x=np.asarray(x,float); w=x[x>0].sum(); l=-x[x<0].sum()
    return w/l if l else np.inf

def dd(x):
    c=np.cumsum(np.asarray(x,float))
    return float(np.min(c-np.maximum.accumulate(np.r_[0.,c])[:-1])) if len(c) else 0.

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",required=True);p.add_argument("--out-dir",required=True)
    p.add_argument("--bootstrap-reps",type=int,default=20000)
    p.add_argument("--control",required=True)
    a=p.parse_args(); out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(a.ledger);d["entry_timestamp"]=pd.to_datetime(d["entry_timestamp"],utc=True)
    ok=d[d.status.eq("ok")].copy()
    summ=[]
    for v,g in ok.groupby("variant",sort=False):
        x=g.sort_values("entry_timestamp")["net_pnl_inr"].to_numpy(float)
        summ.append({"variant":v,"trades":len(x),"net_pnl_inr":x.sum(),"mean_pnl_inr":x.mean(),"median_pnl_inr":np.median(x),"win_rate_pct":100*(x>0).mean(),"profit_factor":pf(x),"max_drawdown_inr":dd(x),"total_costs_inr":g["total_costs"].sum(),"p10_pnl_inr":np.quantile(x,.1),"worst_trade_inr":x.min()})
    summary=pd.DataFrame(summ);summary.to_csv(out/"exit_timing_summary.csv",index=False)
    control=pd.read_csv(a.control)
    if len(control)!=131:
        raise RuntimeError(f"Frozen Phase 9G control must contain 131 rows, found {len(control)}")
    control["near_expiry"]=pd.to_datetime(control["near_expiry"]).dt.date
    control["net_pnl_inr"]=pd.to_numeric(control["net_pnl_inr"],errors="raise")
    base=control[["near_expiry","net_pnl_inr"]].rename(columns={"net_pnl_inr":"baseline_pnl"})
    rows=[]
    for v in ["60m","120m","180m","1d"]:
        alt=ok[ok.variant.eq(v)][["near_expiry","net_pnl_inr"]].rename(columns={"net_pnl_inr":"alt_pnl"})
        alt["near_expiry"]=pd.to_datetime(alt["near_expiry"]).dt.date
        x=base.merge(alt,on="near_expiry",how="inner")
        diff=(x.alt_pnl-x.baseline_pnl).to_numpy(float)
        lo,hi=block_ci(diff,a.bootstrap_reps)
        rows.append({"variant":v,"paired_cycles":len(x),"mean_difference_inr":diff.mean() if len(diff) else np.nan,"median_difference_inr":np.median(diff) if len(diff) else np.nan,"net_difference_inr":diff.sum() if len(diff) else np.nan,"block_bootstrap_low_inr":lo,"block_bootstrap_high_inr":hi,"paired_permutation_p":perm_p(diff,a.bootstrap_reps)})
    paired=pd.DataFrame(rows)
    pvals=paired.paired_permutation_p.to_numpy(float);order=np.argsort(pvals);q=np.empty_like(pvals);run=1.;m=len(pvals)
    for rank,idx in reversed(list(enumerate(order,1))):run=min(run,pvals[idx]*m/rank);q[idx]=run
    paired["bh_q"]=q;paired.to_csv(out/"paired_exit_timing_comparisons.csv",index=False)
    best=paired.sort_values("mean_difference_inr",ascending=False).iloc[0]
    passed=bool(best.mean_difference_inr>0 and best.block_bootstrap_low_inr>0 and best.bh_q<.05)
    payload={"passed":passed,"best_variant":best.variant,"criteria":{"mean_difference_gt_zero":bool(best.mean_difference_inr>0),"bootstrap_low_gt_zero":bool(best.block_bootstrap_low_inr>0),"bh_q_lt_0_05":bool(best.bh_q<.05)}}
    (out/"promotion_screen.json").write_text(json.dumps(payload,indent=2))
    report=f"""# Phase 10D — Exit timing refinement

**Status:** COMPLETE — no strategy change adopted by this phase.

## Research question
Does closing the entire four-leg position before near expiry improve realized economics relative to the authoritative frozen Phase 9G exit convention?

## Predeclared candidates
- control: frozen Phase 9G near-expiry settlement/manual far-leg exit;
- 60, 120, 180 minutes before near-expiry close;
- previous trading-day close.

Early exits close all four legs using 0.25% premium slippage and ₹20/order. No exercise STT is charged for early exits.

## Results

{summary.to_markdown(index=False)}

## Paired inference versus baseline

{paired.to_markdown(index=False)}

## Decision

{"A candidate passed the historical screen but remains unpromoted until Phase 10G chronological holdout." if passed else "No exit-timing candidate met the full predeclared promotion screen. The frozen Phase 9G exit convention is retained."}

## Limitations
- Historical closes are execution proxies, not bid/ask fills.
- The 1-day candidate is defined as the last available index bar on the previous trading day.
- Unavailable option observations are excluded from paired inference rather than synthetically filled.
"""
    (out/"PHASE10D_RESULTS.md").write_text(report)
    print(json.dumps(payload,indent=2))
if __name__=="__main__":main()
