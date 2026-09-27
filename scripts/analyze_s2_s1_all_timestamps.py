#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.analyze_entry_features import add_greek_features


TARGET="s2_minus_s1_per_unit"


def build_timestamp_features(strategy_inputs: str, selected_csv: str):
    src=pd.read_parquet(strategy_inputs)
    sel=pd.read_csv(selected_csv,parse_dates=["entry_timestamp"])
    src["entry_timestamp"]=pd.to_datetime(src["entry_timestamp"])
    src["near_expiry"]=pd.to_datetime(src["near_expiry"])
    src["next_expiry"]=pd.to_datetime(src["next_expiry"])
    src["weekly_cycle"]=src["near_expiry"].dt.date.astype(str)
    src=src[src.status.eq("ok")]
    src=src[src.shift_points.between(-400,400) & (src.shift_points%50==0)].copy()
    # Exact 17-strike surface only. The target is identical across strikes at a given timestamp.
    feat=src.copy()
    feat["estimated_equal_max_profit_loss_inr"]=(feat["near_call_close"]-feat["near_put_close"]-feat["next_call_close"]+feat["next_put_close"])*feat["near_lot_size"]
    feat=add_greek_features(feat)
    feat[TARGET]=feat["next_settlement"]-feat["near_settlement"]

    surface_cols=[
        "spot_at_entry","iv_near_mean","iv_next_mean","iv_term_spread",
        "near_iv_skew_call_minus_put","next_iv_skew_call_minus_put",
        "abs_net_delta","abs_net_gamma","abs_net_vega","abs_net_theta_day",
        "net_delta","net_gamma","net_vega","net_theta_day",
        "moneyness_pct","abs_moneyness_pct","estimated_equal_max_profit_loss_inr","flatline_to_spot_pct"
    ]
    rows=[]
    for (week,ts),g in feat.groupby(["weekly_cycle","entry_timestamp"],sort=True):
        row={"weekly_cycle":week,"entry_timestamp":ts,TARGET:float(g[TARGET].iloc[0]),
             "spot_at_entry":float(g.spot_at_entry.iloc[0]),"candidate_count":int(len(g))}
        for c in surface_cols:
            vals=pd.to_numeric(g[c],errors="coerce")
            if c=="spot_at_entry":
                continue
            row[f"{c}_mean"]=float(vals.mean())
            row[f"{c}_median"]=float(vals.median())
            row[f"{c}_std"]=float(vals.std()) if vals.notna().sum()>1 else 0.0
            row[f"{c}_min"]=float(vals.min())
            row[f"{c}_max"]=float(vals.max())
        rows.append(row)
    t=pd.DataFrame(rows).sort_values("entry_timestamp").reset_index(drop=True)

    # Lagged completed-cycle target. Compute from cycle-level targets so repeated within-cycle rows do not create fake lags.
    cycle_target=t.groupby("weekly_cycle",sort=True)[TARGET].first().to_frame()
    cycle_target["lag1"]=cycle_target[TARGET].shift(1)
    cycle_target["lag2"]=cycle_target[TARGET].shift(2)
    t=t.merge(cycle_target[["lag1","lag2"]],left_on="weekly_cycle",right_index=True,how="left")
    t["dow"]=t.entry_timestamp.dt.dayofweek
    t["month"]=t.entry_timestamp.dt.month
    t["spot_change_pct"]=100*t.spot_at_entry.pct_change()
    t["cycle_index"]=pd.factorize(t.weekly_cycle,sort=True)[0]

    # Identify the first-positive decision observation and the selected trade outcome for each test cycle.
    sel["weekly_cycle"]=pd.to_datetime(sel["weekly_cycle"]).dt.date.astype(str)
    decision=sel[["weekly_cycle","entry_timestamp","net_pnl_inr","chart_pnl_inr","total_costs_inr","lot_size","shift_points"]].rename(
        columns={"entry_timestamp":"decision_timestamp","net_pnl_inr":"selected_net_pnl_inr","chart_pnl_inr":"selected_chart_pnl_inr","total_costs_inr":"selected_costs_inr","lot_size":"selected_lot_size","shift_points":"selected_shift_points"}
    )
    return t,decision


def walk_forward(t,decision,min_train_cycles=31):
    cycles=sorted(t.weekly_cycle.unique())
    feature_cols=[c for c in t.columns if c.endswith(("_mean","_median","_std","_min","_max"))]
    feature_cols += ["spot_at_entry","candidate_count","lag1","lag2","dow","month","spot_change_pct"]
    feature_cols=[c for c in feature_cols if c in t.columns]
    models={
        "ridge":make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),Ridge(alpha=10.0)),
        "random_forest":make_pipeline(SimpleImputer(strategy="median"),RandomForestRegressor(n_estimators=400,max_depth=4,min_samples_leaf=6,random_state=11,n_jobs=-1)),
        "hist_gradient_boost":make_pipeline(SimpleImputer(strategy="median"),HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=6,learning_rate=0.05,l2_regularization=8.0,random_state=11))
    }
    preds={name:[] for name in models}
    for idx in range(min_train_cycles,len(cycles)):
        cycle=cycles[idx]
        train=t[t.weekly_cycle.isin(cycles[:idx])].copy()
        # Equalize weekly importance despite multiple observations within the same cycle.
        counts=train.weekly_cycle.value_counts()
        weights=train.weekly_cycle.map(lambda x:1.0/counts.loc[x]).to_numpy(float)
        test=decision[decision.weekly_cycle==cycle]
        if test.empty:
            continue
        obs=test.decision_timestamp.iloc[0]
        test_feat=t[(t.weekly_cycle==cycle)&(t.entry_timestamp==obs)]
        if test_feat.empty:
            continue
        y=train[TARGET]
        for name,m in models.items():
            try:
                m.fit(train[feature_cols],y,sample_weight=weights)
            except TypeError:
                m.fit(train[feature_cols],y)
            p=float(m.predict(test_feat[feature_cols].iloc[[0]])[0])
            row=test.iloc[0].to_dict()
            row["predicted_target"]=p
            row["model"]=name
            row["weekly_cycle_index"]=idx
            row["actual_target"]=float(test_feat[TARGET].iloc[0])
            preds[name].append(row)
    return feature_cols,{k:pd.DataFrame(v) for k,v in preds.items()}


def summarize(preds):
    rows=[]
    for name,d in preds.items():
        y=d.actual_target.to_numpy(float)
        p=d.predicted_target.to_numpy(float)
        rows.append({
            "model":name,"test_weeks":len(d),"mae":mean_absolute_error(y,p),
            "rmse":mean_squared_error(y,p)**0.5,
            "sign_accuracy_pct":100*np.mean(np.sign(y)==np.sign(p)),
            "corr":np.corrcoef(y,p)[0,1] if len(y)>1 else np.nan
        })
    return pd.DataFrame(rows)


def evaluate(preds):
    rows=[]
    for name,d in preds.items():
        baseline=float(d.selected_net_pnl_inr.sum())
        for rule in ("all","pred_positive","expected_net_positive"):
            if rule=="all":
                take=np.ones(len(d),bool)
            elif rule=="pred_positive":
                take=d.predicted_target>0
            else:
                take=(d.selected_chart_pnl_inr+d.predicted_target*d.selected_lot_size-d.selected_costs_inr)>0
            tr=d.loc[take]
            rows.append({
                "model":name,"rule":rule,"weeks":len(d),"traded_weeks":len(tr),
                "coverage_pct":100*len(tr)/len(d),
                "net_pnl_inr":tr.selected_net_pnl_inr.sum(),
                "mean_net_pnl_inr":tr.selected_net_pnl_inr.mean() if len(tr) else np.nan,
                "win_rate_pct":100*(tr.selected_net_pnl_inr>0).mean() if len(tr) else np.nan,
                "baseline_same_test_net_pnl_inr":baseline,
                "delta_vs_baseline_inr":tr.selected_net_pnl_inr.sum()-baseline
            })
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--strategy-inputs",required=True)
    ap.add_argument("--selected",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    t,decision=build_timestamp_features(args.strategy_inputs,args.selected)
    features,preds=walk_forward(t,decision,min_train_cycles=31)
    m=summarize(preds); f=evaluate(preds)
    t.to_csv(out/"all_timestamp_s2_s1_features.csv",index=False)
    decision.to_csv(out/"weekly_decisions.csv",index=False)
    for name,d in preds.items(): d.to_csv(out/f"predictions_{name}.csv",index=False)
    m.to_csv(out/"all_timestamp_model_metrics.csv",index=False)
    f.to_csv(out/"all_timestamp_trade_filter_results.csv",index=False)
    summary={
        "entry_timestamps":int(len(t)),
        "weekly_cycles":int(t.weekly_cycle.nunique()),
        "test_cycles":int(max((len(v) for v in preds.values()),default=0)),
        "feature_count":int(len(features)),
        "training_unit":"all prior entry timestamps with equal weekly-cycle weights",
        "target":TARGET,
        "no_lookahead":"For each test weekly cycle, only all timestamps from earlier weekly cycles are used for fitting; test features are from that week's first-positive decision timestamp.",
        "stop_rule":"Do not adopt a predictor unless walk-forward economics improve after costs across more than one time block."
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print(m.to_string(index=False))
    print(f.to_string(index=False))


if __name__=="__main__":
    main()
