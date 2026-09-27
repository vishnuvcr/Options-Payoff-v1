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


def build_weekly_dataset(strategy_inputs: str, selected_csv: str) -> pd.DataFrame:
    src = pd.read_parquet(strategy_inputs)
    selected = pd.read_csv(selected_csv)
    src["entry_timestamp"] = pd.to_datetime(src["entry_timestamp"])
    src["near_expiry"] = pd.to_datetime(src["near_expiry"])
    src["next_expiry"] = pd.to_datetime(src["next_expiry"])
    selected["entry_timestamp"] = pd.to_datetime(selected["entry_timestamp"])
    selected["weekly_cycle"] = pd.to_datetime(selected["weekly_cycle"]).dt.date.astype(str)
    src["weekly_cycle"] = src["near_expiry"].dt.date.astype(str)
    src = src[src.status.eq("ok")].copy()
    src = src[src.shift_points.between(-400,400) & (src.shift_points % 50 == 0)].copy()

    # Only the information visible at the first-positive decision observation of each weekly cycle.
    keys = selected[["entry_timestamp","weekly_cycle","shift_points"]].copy()
    keys["selected"] = True
    src = src.merge(keys, on=["entry_timestamp","weekly_cycle","shift_points"], how="left")
    src["selected"] = src["selected"].fillna(False)

    selected_lookup = selected[["entry_timestamp","weekly_cycle","shift_points","chart_pnl_inr","net_pnl_inr","total_costs_inr","lot_size","estimated_equal_max_profit_loss_inr"]].copy()
    selected_lookup = selected_lookup.rename(columns={"chart_pnl_inr":"selected_chart_pnl_inr","net_pnl_inr":"selected_net_pnl_inr","total_costs_inr":"selected_costs_inr","lot_size":"selected_lot_size","estimated_equal_max_profit_loss_inr":"selected_flatline_inr"})

    # Build IV/Greek proxies for every positive candidate at the decision observation.
    feat = src.copy()
    feat["estimated_equal_max_profit_loss_inr"] = (
        feat["near_call_close"] - feat["near_put_close"] - feat["next_call_close"] + feat["next_put_close"]
    ) * feat["near_lot_size"]
    feat = feat[feat["estimated_equal_max_profit_loss_inr"] > 0].copy()
    feat = add_greek_features(feat)

    feat = feat.merge(selected_lookup, on=["entry_timestamp","weekly_cycle","shift_points"], how="left")

    rows=[]
    numeric_surface = [
        "iv_near_mean","iv_next_mean","iv_term_spread",
        "near_iv_skew_call_minus_put","next_iv_skew_call_minus_put",
        "abs_net_delta","abs_net_gamma","abs_net_vega","abs_net_theta_day",
        "net_delta","net_gamma","net_vega","net_theta_day",
        "moneyness_pct","abs_moneyness_pct","estimated_equal_max_profit_loss_inr","flatline_to_spot_pct"
    ]
    for (week,ts), g in feat.groupby(["weekly_cycle","entry_timestamp"], sort=True):
        selected_rows=g[g["selected"]].copy()
        if selected_rows.empty:
            continue
        s=selected_rows.iloc[0]
        row={
            "weekly_cycle":pd.Timestamp(week),
            "entry_timestamp":pd.Timestamp(ts),
            TARGET:float(s["next_settlement"]-s["near_settlement"]),
            "selected_chart_pnl_inr":float(s["selected_chart_pnl_inr"]),
            "selected_net_pnl_inr":float(s["selected_net_pnl_inr"]),
            "selected_costs_inr":float(s["selected_costs_inr"]),
            "selected_lot_size":float(s["selected_lot_size"]),
            "selected_flatline_inr":float(s["selected_flatline_inr"]),
            "selected_shift_points":float(s["shift_points"]),
            "spot_at_entry":float(s["spot_at_entry"]),
            "candidate_count":int(len(g)),
        }
        # selected-candidate features
        for c in numeric_surface:
            row["sel_"+c]=float(s[c]) if pd.notna(s[c]) else np.nan
        # surface summaries at the actual decision timestamp
        for c in numeric_surface:
            vals=pd.to_numeric(g[c],errors="coerce")
            for agg_name,agg_fn in [("mean","mean"),("median","median"),("std","std"),("min","min"),("max","max")]:
                row[f"surf_{c}_{agg_name}"]=float(getattr(vals,agg_fn)()) if vals.notna().any() else np.nan
        # surface range / asymmetry
        row["surf_iv_term_spread_range"]=row["surf_iv_term_spread_max"]-row["surf_iv_term_spread_min"]
        row["surf_moneyness_range"]=row["surf_moneyness_pct_max"]-row["surf_moneyness_pct_min"]
        row["surf_flatline_range"]=row["surf_estimated_equal_max_profit_loss_inr_max"]-row["surf_estimated_equal_max_profit_loss_inr_min"]
        rows.append(row)

    w=pd.DataFrame(rows).sort_values("entry_timestamp").reset_index(drop=True)
    # Add lagged realized S2-S1; at week t these values are known from prior completed cycles.
    for lag in (1,2,3):
        w[f"lag{lag}_{TARGET}"]=w[TARGET].shift(lag)
    # Entry-time calendar / spot-state variables.
    w["dow"]=w.entry_timestamp.dt.dayofweek
    w["month"]=w.entry_timestamp.dt.month
    w["days_between_expiries"]=(pd.to_datetime(w.entry_timestamp.dt.date)+pd.Timedelta(days=7)-pd.to_datetime(w.entry_timestamp.dt.date)).dt.days
    # Spot change from prior decision observation.
    w["spot_change_pct"]=100.0*w["spot_at_entry"].pct_change()
    return w


def walk_forward_predict(w: pd.DataFrame, min_train: int=31):
    feature_cols=[
        c for c in w.columns
        if c.startswith(("sel_","surf_"))
    ] + ["spot_at_entry","candidate_count","selected_shift_points","selected_flatline_inr","lag1_"+TARGET,"lag2_"+TARGET,"lag3_"+TARGET,"dow","month","spot_change_pct"]
    feature_cols=[c for c in feature_cols if c in w.columns]
    models={
        "ridge":make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),Ridge(alpha=10.0)),
        "random_forest":make_pipeline(SimpleImputer(strategy="median"),RandomForestRegressor(n_estimators=300,max_depth=3,min_samples_leaf=4,random_state=7,n_jobs=-1)),
        "hist_gradient_boost":make_pipeline(SimpleImputer(strategy="median"),HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=5,learning_rate=0.05,l2_regularization=5.0,random_state=7))
    }
    preds={name:np.full(len(w),np.nan) for name in models}
    for i in range(min_train,len(w)):
        train=w.iloc[:i]
        test=w.iloc[[i]]
        Xtr=train[feature_cols]
        ytr=train[TARGET]
        Xte=test[feature_cols]
        for name,m in models.items():
            m.fit(Xtr,ytr)
            preds[name][i]=float(m.predict(Xte)[0])
    return feature_cols,preds


def summarize_model(w,pred):
    rows=[]
    for model,p in pred.items():
        mask=np.isfinite(p)
        y=w.loc[mask,TARGET].to_numpy(float)
        ph=p[mask]
        rows.append({
            "model":model,
            "test_weeks":int(mask.sum()),
            "mae_per_unit":float(mean_absolute_error(y,ph)),
            "rmse_per_unit":float(mean_squared_error(y,ph)**0.5),
            "sign_accuracy_pct":float(100*np.mean(np.sign(y)==np.sign(ph))),
            "corr":float(np.corrcoef(y,ph)[0,1]) if len(y)>1 else np.nan,
        })
    return pd.DataFrame(rows)


def evaluate_trade_filter(w,preds):
    out=[]
    baseline_total=float(w.selected_net_pnl_inr.sum())
    for model,p in preds.items():
        mask=np.isfinite(p)
        # Evaluate only the same out-of-sample weeks used for prediction.
        z=w.loc[mask].copy()
        z["pred_target"]=p[mask]
        for rule in ["all","pred_positive","expected_net_positive"]:
            if rule=="all":
                take=np.ones(len(z),dtype=bool)
            elif rule=="pred_positive":
                take=z.pred_target>0
            else:
                # Entry-time expected total P&L = observed static flatline + predicted S2-S1 x lot - already-modeled costs.
                take=(z.selected_chart_pnl_inr + z.pred_target*z.selected_lot_size - z.selected_costs_inr)>0
            trades=z.loc[take]
            out.append({
                "model":model,
                "rule":rule,
                "test_weeks":int(len(z)),
                "traded_weeks":int(len(trades)),
                "coverage_pct":float(100*len(trades)/len(z)),
                "net_pnl_inr":float(trades.selected_net_pnl_inr.sum()),
                "mean_net_pnl_inr":float(trades.selected_net_pnl_inr.mean()) if len(trades) else np.nan,
                "win_rate_pct":float(100*(trades.selected_net_pnl_inr>0).mean()) if len(trades) else np.nan,
                "baseline_same_test_net_pnl_inr":float(z.selected_net_pnl_inr.sum()),
                "delta_vs_baseline_inr":float(trades.selected_net_pnl_inr.sum()-z.selected_net_pnl_inr.sum()),
            })
    return pd.DataFrame(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--strategy-inputs",required=True)
    ap.add_argument("--selected",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    w=build_weekly_dataset(args.strategy_inputs,args.selected)
    feature_cols,preds=walk_forward_predict(w,min_train=31)
    model_stats=summarize_model(w,preds)
    filter_stats=evaluate_trade_filter(w,preds)

    w2=w.copy()
    for name,p in preds.items():
        w2["pred_"+name]=p
    w.to_csv(out/"weekly_s2_s1_dataset.csv",index=False)
    w2.to_csv(out/"weekly_s2_s1_predictions.csv",index=False)
    model_stats.to_csv(out/"s2_s1_model_metrics.csv",index=False)
    filter_stats.to_csv(out/"s2_s1_trade_filter_results.csv",index=False)

    summary={
        "weekly_cycles":int(len(w)),
        "target_name":TARGET,
        "target_mean_per_unit":float(w[TARGET].mean()),
        "target_std_per_unit":float(w[TARGET].std()),
        "target_positive_rate_pct":float(100*(w[TARGET]>0).mean()),
        "baseline_total_net_pnl_inr":float(w.selected_net_pnl_inr.sum()),
        "walk_forward_start":31,
        "feature_count":int(len(feature_cols)),
        "feature_method":"entry-time selected-candidate Greeks/IV/moneyness plus cross-strike surface summaries, spot and lagged historical S2-S1",
        "no_lookahead":"At week t, only rows through week t-1 are used to fit the predictor; current-week features are evaluated only after the first-positive entry observation is defined.",
        "primary_filter":"predicted S2-S1 > 0",
        "economic_filter":"selected static flatline + predicted S2-S1*lot - modeled costs > 0",
        "caveat":"63 weeks is a small sample; this phase tests predictability and economic usefulness, not statistical proof of a permanent edge."
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print(model_stats.to_string(index=False))
    print(filter_stats.to_string(index=False))


if __name__=="__main__":
    main()
