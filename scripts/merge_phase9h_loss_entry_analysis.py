#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

VARIANTS = [
    "first_positive","second_valid_timestamp","delay_15m","delay_30m","delay_60m","delay_120m",
    "same_timestamp_any_candidate","best_later_frozen_selector","best_later_any_candidate"
]

def wilson(k,n,z=1.959963984540054):
    if not n: return (None,None)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/den
    return (c-h)*100,(c+h)*100

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input-dir",required=True); p.add_argument("--out-dir",required=True); a=p.parse_args()
    root=Path(a.input_dir); lf=sorted(root.rglob("loss_trade_entry_detail.csv")); vf=sorted(root.rglob("entry_variant_trade_rows.csv"))
    if not lf or not vf: raise SystemExit("Missing Phase 9H yearly artifacts")
    details=pd.concat([pd.read_csv(x) for x in lf],ignore_index=True)
    variants=pd.concat([pd.read_csv(x) for x in vf],ignore_index=True)
    variants=variants.dropna(subset=["net_pnl_inr"]).drop_duplicates(["near_expiry","cycle_entry_timestamp","variant"])
    details=details.drop_duplicates(["near_expiry","entry_timestamp"])
    rows=[]
    for v,g in variants.groupby("variant",sort=False):
        pnl=g.net_pnl_inr.astype(float); n=len(pnl); w=int((pnl>0).sum()); lo,hi=wilson(w,n)
        rows.append({
            "variant":v,"trades":n,"net_pnl_inr":float(pnl.sum()),"mean_net_pnl_inr":float(pnl.mean()),
            "median_net_pnl_inr":float(pnl.median()),"win_rate_pct":float(w/n*100),
            "win_rate_wilson_low_pct":lo,"win_rate_wilson_high_pct":hi,
            "losing_trades":int((pnl<0).sum()),"increment_vs_baseline_inr":float((g.net_pnl_inr-g.baseline_net_pnl_inr).sum()),
            "status":"frozen primary" if v=="first_positive" else
                     "ex-post diagnostic / upper bound" if v in {"same_timestamp_any_candidate","best_later_frozen_selector","best_later_any_candidate"} else
                     "predeclared timing variant; in-sample"
        })
    summary=pd.DataFrame(rows); summary["order"]=summary.variant.map({v:i for i,v in enumerate(VARIANTS)}).fillna(999); summary=summary.sort_values(["order","variant"]).drop(columns="order")
    losses=details[details.baseline_net_pnl_inr<0].copy()
    checks=[
        ("same_timestamp_any_candidate","same_timestamp_any_candidate_rescues_loss"),
        ("second_valid_timestamp","second_valid_timestamp_rescues_loss"),
        ("delay_15m","delay_15m_rescues_loss"),("delay_30m","delay_30m_rescues_loss"),
        ("delay_60m","delay_60m_rescues_loss"),("delay_120m","delay_120m_rescues_loss"),
        ("best_later_frozen_selector","best_later_frozen_selector_rescues_loss"),
        ("best_later_any_candidate","best_later_any_candidate_rescues_loss")]
    resc=[]
    for v,col in checks:
        flags=losses[col].fillna(False).astype(bool)
        vals=pd.to_numeric(losses.loc[flags,f"{v}_net_pnl_inr"],errors="coerce") if f"{v}_net_pnl_inr" in losses else pd.Series([],dtype=float)
        resc.append({"variant":v,"baseline_losing_trades":len(losses),
                     "losses_rescued_to_positive":int(flags.sum()),
                     "rescue_rate_pct":float(flags.mean()*100) if len(flags) else None,
                     "baseline_loss_pnl_inr":float(losses.baseline_net_pnl_inr.sum()),
                     "positive_rescue_pnl_sum_inr":float(vals.dropna().sum())})
    rescue=pd.DataFrame(resc)
    overlap=[]
    for _,r in losses.iterrows():
        same=bool(r.get("same_timestamp_any_candidate_rescues_loss",False))
        fixed=any(bool(r.get(f"delay_{m}m_rescues_loss",False)) for m in (15,30,60,120))
        later=bool(r.get("best_later_any_candidate_rescues_loss",False))
        overlap.append({"near_expiry":r.near_expiry,"entry_timestamp":r.entry_timestamp,
                        "baseline_net_pnl_inr":r.baseline_net_pnl_inr,
                        "same_timestamp_strike_rescue":same,"fixed_delay_rescue":fixed,
                        "later_entry_upper_bound_rescue":later,
                        "any_bounded_oracle_rescue":same or fixed or later})
    overlap=pd.DataFrame(overlap)
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    details.to_csv(out/"loss_trade_entry_detail.csv",index=False); variants.to_csv(out/"entry_variant_trade_ledger.csv",index=False)
    summary.to_csv(out/"entry_variant_summary.csv",index=False); rescue.to_csv(out/"loss_rescue_summary.csv",index=False); overlap.to_csv(out/"loss_rescue_mechanism_overlap.csv",index=False)
    md=[
        "# Phase 9H — Loss-trade entry analysis","",
        "## Research question",
        "Can the realized H1 losses be changed to profit by modifying only entry timing or entry strike while keeping the frozen payoff construction, H1 horizon, near-expiry far-leg close and cost model unchanged?","",
        "## Sample",
        f"- Complete realized H1 cycles in this run: {len(variants[variants.variant=='first_positive'])}.",
        f"- Baseline losing cycles analyzed: {len(losses)}.",
        f"- Baseline net P&L across analyzed complete cycles: ₹{variants[variants.variant=='first_positive'].baseline_net_pnl_inr.sum():,.2f}.","",
        "## Tests",
        "1. Same-timestamp strike substitution (ex-post upper bound).",
        "2. Next exact-17 valid timestamp with the normal maximum-flatline selector.",
        "3. First valid timestamp at or after 15/30/60/120 minutes after the baseline decision.",
        "4. Best later timestamp under the unchanged selector (ex-post diagnostic).",
        "5. Best later timestamp/strike across all candidates (strongest entry-only ex-post upper bound).","",
        "## Full-sample economics",summary.to_markdown(index=False),"",
        "## Loss rescue counts",rescue.to_markdown(index=False),"",
        "## Interpretation",
        "Rescue counts are diagnostic. An entry rule should only be adopted if it is prospectively defined, improves the full sample rather than just losses, and is then tested on untouched data. Ex-post upper bounds are not deployable rules.",
    ]
    (out/"PHASE9H_LOSS_ENTRY_ANALYSIS.md").write_text("\n".join(md),encoding="utf-8")
    (out/"summary.json").write_text(json.dumps({
        "phase":"9H","complete_cycles":int(variants[variants.variant=="first_positive"].shape[0]),
        "loss_cycles":int(len(losses)),
        "baseline_net_pnl_inr":float(variants[variants.variant=="first_positive"].baseline_net_pnl_inr.sum()),
        "delays_minutes":[15,30,60,120],
        "ex_post_variants":["same_timestamp_any_candidate","best_later_frozen_selector","best_later_any_candidate"]
    },indent=2))

if __name__=="__main__": main()
