#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import mannwhitneyu, spearmanr, ttest_ind
from statsmodels.stats.multitest import multipletests
from statsmodels.api import Logit, add_constant
from scipy.special import ndtr


SIGNS = {"near_call": -1.0, "near_put": 1.0, "next_call": 1.0, "next_put": -1.0}


def norm_pdf(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def bs_price(S, K, T, r, sigma, cp):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(S-K, 0.0) if cp == "C" else max(K-S, 0.0)
    sq = math.sqrt(T)
    d1 = (math.log(S/K) + (r + 0.5*sigma*sigma)*T) / (sigma*sq)
    d2 = d1 - sigma*sq
    df = math.exp(-r*T)
    if cp == "C":
        return S*ndtr(d1) - K*df*ndtr(d2)
    return K*df*ndtr(-d2) - S*ndtr(-d1)


def implied_vol(price, S, K, T, r, cp):
    if not np.isfinite(price) or price <= 0 or T <= 0 or S <= 0 or K <= 0:
        return np.nan
    intrinsic = max(S-K, 0.0) if cp == "C" else max(K-S, 0.0)
    upper = S if cp == "C" else K*math.exp(-r*T)
    if price < intrinsic - 1e-6 or price > upper + 1e-6:
        return np.nan
    lo, hi = 1e-6, 5.0
    f = lambda v: bs_price(S, K, T, r, v, cp) - price
    try:
        if f(lo) * f(hi) > 0:
            return np.nan
        return float(brentq(f, lo, hi, maxiter=100))
    except Exception:
        return np.nan


def bs_greeks(S, K, T, r, sigma, cp):
    if not np.isfinite(sigma) or sigma <= 0 or T <= 0 or S <= 0 or K <= 0:
        return {k: np.nan for k in ("delta","gamma","vega","theta_day")}
    sq = math.sqrt(T)
    d1 = (math.log(S/K) + (r + 0.5*sigma*sigma)*T) / (sigma*sq)
    d2 = d1 - sigma*sq
    pdf = norm_pdf(d1)
    df = math.exp(-r*T)
    delta = ndtr(d1) if cp == "C" else ndtr(d1)-1.0
    gamma = pdf/(S*sigma*sq)
    vega = S*pdf*sq/100.0
    if cp == "C":
        theta = -(S*pdf*sigma)/(2*sq) - r*K*df*ndtr(d2)
    else:
        theta = -(S*pdf*sigma)/(2*sq) + r*K*df*ndtr(-d2)
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta_day": theta/365.0}


def candidate_payoff_and_cost(row, slippage_pct=0.0025):
    premiums = [row.near_call_close, row.near_put_close, row.next_call_close, row.next_put_close]
    if any(pd.isna(x) for x in premiums):
        return None
    K = float(row.strike)
    lot = float(row.near_lot_size)
    # Same one-dimensional terminal-spot chart: intrinsic terms cancel.
    flatline = float(row.near_call_close - row.near_put_close - row.next_call_close + row.next_put_close) * lot
    # Execution cashflow with symmetric percentage slippage.
    short_call = float(row.near_call_close) * (1-slippage_pct)
    long_put = float(row.near_put_close) * (1+slippage_pct)
    long_call = float(row.next_call_close) * (1+slippage_pct)
    short_put = float(row.next_put_close) * (1-slippage_pct)
    entry_cash_per_unit = -short_call + long_put - long_call + short_put
    gross = (entry_cash_per_unit + float(row.next_settlement) - float(row.near_settlement)) * lot
    return flatline, gross


def add_greek_features(df: pd.DataFrame, r=0.0, expiry_hour=15, expiry_minute=30):
    out = []
    for row in df.itertuples(index=False):
        ts = pd.Timestamp(row.entry_timestamp)
        S = float(row.spot_at_entry)
        K = float(row.strike)
        near_exp = pd.Timestamp(row.near_expiry).tz_localize(ts.tz) + pd.Timedelta(hours=expiry_hour, minutes=expiry_minute)
        next_exp = pd.Timestamp(row.next_expiry).tz_localize(ts.tz) + pd.Timedelta(hours=expiry_hour, minutes=expiry_minute)
        T_near = max((near_exp - ts).total_seconds() / (365.0*24*3600), 1e-8)
        T_next = max((next_exp - ts).total_seconds() / (365.0*24*3600), 1e-8)
        rowd = row._asdict()
        leg_specs = [
            ("near_call", float(row.near_call_close), T_near, "C"),
            ("near_put", float(row.near_put_close), T_near, "P"),
            ("next_call", float(row.next_call_close), T_next, "C"),
            ("next_put", float(row.next_put_close), T_next, "P"),
        ]
        totals = {k: 0.0 for k in ("delta","gamma","vega","theta_day")}
        ivs = {}
        for name, price, T, cp in leg_specs:
            iv = implied_vol(price, S, K, T, r, cp)
            g = bs_greeks(S, K, T, r, iv, cp)
            ivs[name+"_iv"] = iv
            for key,val in g.items():
                rowd[name+"_"+key] = val
                if np.isfinite(val):
                    totals[key] += SIGNS[name]*val
        rowd["tau_near_years"] = T_near
        rowd["tau_next_years"] = T_next
        rowd["iv_near_mean"] = np.nanmean([ivs["near_call_iv"], ivs["near_put_iv"]])
        rowd["iv_next_mean"] = np.nanmean([ivs["next_call_iv"], ivs["next_put_iv"]])
        rowd["iv_term_spread"] = rowd["iv_next_mean"] - rowd["iv_near_mean"]
        rowd["near_iv_skew_call_minus_put"] = ivs["near_call_iv"] - ivs["near_put_iv"]
        rowd["next_iv_skew_call_minus_put"] = ivs["next_call_iv"] - ivs["next_put_iv"]
        rowd["abs_net_delta"] = abs(totals["delta"])
        rowd["abs_net_gamma"] = abs(totals["gamma"])
        rowd["abs_net_vega"] = abs(totals["vega"])
        rowd["abs_net_theta_day"] = abs(totals["theta_day"])
        rowd["net_delta"] = totals["delta"]
        rowd["net_gamma"] = totals["gamma"]
        rowd["net_vega"] = totals["vega"]
        rowd["net_theta_day"] = totals["theta_day"]
        rowd["moneyness_pct"] = 100.0*(K-S)/S
        rowd["abs_moneyness_pct"] = abs(rowd["moneyness_pct"])
        rowd["flatline_to_spot_pct"] = 100.0*rowd["estimated_equal_max_profit_loss_inr"]/(S*float(row.lot_size))
        out.append(rowd)
    return pd.DataFrame(out)


def cliffs_delta(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if len(x)==0 or len(y)==0:
        return np.nan
    ranks = np.concatenate([x, y])
    order = pd.Series(ranks).rank(method="average").to_numpy()
    rx = order[:len(x)].sum()
    return (2*rx - len(x)*(len(x)+len(y)+1)) / (len(x)*len(y))


def univariate_trade_stats(selected):
    selected = selected.copy()
    selected["win"] = selected.net_pnl_inr > 0
    win = selected[selected.win]
    loss = selected[~selected.win]
    features = [c for c in selected.columns if c.startswith(("near_","next_","iv_","abs_net_","net_","tau_","moneyness","flatline_to_"))]
    rows=[]
    for f in features:
        if f in {"near_expiry","next_expiry"}:
            continue
        a=pd.to_numeric(win[f], errors="coerce").dropna()
        b=pd.to_numeric(loss[f], errors="coerce").dropna()
        if len(a)<3 or len(b)<3:
            continue
        t_p=ttest_ind(a,b,equal_var=False,nan_policy="omit").pvalue
        u_p=mannwhitneyu(a,b,alternative="two-sided").pvalue
        rows.append({"feature":f,"winner_n":len(a),"loser_n":len(b),"winner_mean":a.mean(),"loser_mean":b.mean(),"winner_median":a.median(),"loser_median":b.median(),"welch_p":t_p,"mw_p":u_p,"cliffs_delta":cliffs_delta(a,b)})
    res=pd.DataFrame(rows)
    if not res.empty:
        res["bh_q"]=multipletests(res["mw_p"],method="fdr_bh")[1]
        res=res.sort_values(["bh_q","mw_p","feature"])
    return res


def candidate_selector_test(candidates, feature, direction):
    rows=[]
    for week,g in candidates.groupby("weekly_cycle",sort=True):
        pool=g[np.isfinite(g[feature])].copy()
        if pool.empty:
            continue
        idx=pool[feature].idxmax() if direction=="max" else pool[feature].idxmin()
        chosen=pool.loc[idx]
        rows.append({"weekly_cycle":week,"net_pnl_inr":chosen.net_pnl_inr})
    return pd.DataFrame(rows)


def cluster_selector_stats(candidates, feature):
    results=[]
    for direction in ("max","min"):
        trades=candidate_selector_test(candidates,feature,direction)
        if trades.empty: continue
        results.append({
            "feature":feature,"direction":direction,"weeks":len(trades),
            "total_net_pnl_inr":trades.net_pnl_inr.sum(),
            "mean_net_pnl_inr":trades.net_pnl_inr.mean(),
            "win_rate_pct":100*(trades.net_pnl_inr>0).mean(),
        })
    return results


def candidate_within_week_correlations(candidates):
    feats=[c for c in candidates.columns if c in [
        "estimated_equal_max_profit_loss_inr","near_call_iv","near_put_iv","next_call_iv","next_put_iv",
        "iv_near_mean","iv_next_mean","iv_term_spread","near_iv_skew_call_minus_put","next_iv_skew_call_minus_put",
        "near_call_delta","near_put_delta","next_call_delta","next_put_delta",
        "near_call_gamma","near_put_gamma","next_call_gamma","next_put_gamma",
        "near_call_vega","near_put_vega","next_call_vega","next_put_vega",
        "near_call_theta_day","near_put_theta_day","next_call_theta_day","next_put_theta_day",
        "abs_net_delta","abs_net_gamma","abs_net_vega","abs_net_theta_day","moneyness_pct","abs_moneyness_pct"
    ]]
    rows=[]
    for f in feats:
        rs=[]
        for _,g in candidates.groupby("weekly_cycle"):
            z=g[[f,"net_pnl_inr"]].dropna()
            if len(z)>=4 and z[f].nunique()>1 and z.net_pnl_inr.nunique()>1:
                rs.append(spearmanr(z[f],z.net_pnl_inr).statistic)
        if rs:
            a=np.array(rs,float)
            rows.append({"feature":f,"weeks_with_correlation":len(a),"mean_weekly_spearman":a.mean(),"median_weekly_spearman":np.median(a),"positive_corr_fraction":np.mean(a>0)})
    return pd.DataFrame(rows).sort_values("mean_weekly_spearman",ascending=False)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--strategy-inputs",required=True)
    ap.add_argument("--selected",required=True)
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--slippage-pct",type=float,default=0.0025)
    args=ap.parse_args()

    src=pd.read_parquet(args.strategy_inputs)
    selected=pd.read_csv(args.selected)
    selected["entry_timestamp"]=pd.to_datetime(selected["entry_timestamp"])
    selected["weekly_cycle"]=pd.to_datetime(selected["weekly_cycle"]).dt.date.astype(str)

    # Restrict candidate pool to the actual decision timestamps used by the first-positive strategy.
    key=set(zip(selected.entry_timestamp.astype(str),selected.weekly_cycle))
    src["entry_timestamp"]=pd.to_datetime(src["entry_timestamp"])
    src["near_expiry"]=pd.to_datetime(src["near_expiry"])
    src["next_expiry"]=pd.to_datetime(src["next_expiry"])
    src["weekly_cycle"]=src["near_expiry"].dt.date.astype(str)
    src=src[src.status.eq("ok")]
    src=src[src.shift_points.between(-400,400) & (src.shift_points%50==0)]
    src=src[src.apply(lambda r:(str(r.entry_timestamp),r.weekly_cycle) in key,axis=1)].copy()

    # Match the selection file to mark the actually selected candidate.
    sel_key=selected[["entry_timestamp","weekly_cycle","shift_points"]].copy()
    sel_key["selected"]=True
    src=src.merge(sel_key,on=["entry_timestamp","weekly_cycle","shift_points"],how="left")
    src["selected"]=src["selected"].fillna(False)

    # Only candidates that were positive/all-green at the decision time are eligible for the actual selection.
    # Recreate chart flatline from entry premiums; no future values are used in selection.
    src["estimated_equal_max_profit_loss_inr"]=(src.near_call_close-src.near_put_close-src.next_call_close+src.next_put_close)*src.near_lot_size
    src["positive_at_entry"]=src.estimated_equal_max_profit_loss_inr>0
    eligible=src[src.positive_at_entry].copy()

    # Compute costs/outcome using the same four-leg economics as the backtest.
    def row_pnl(r):
        x=candidate_payoff_and_cost(r,args.slippage_pct)
        if x is None:return np.nan
        flat,gross=x
        # Approximate the repository's costs are already represented by its selected result.
        # For candidates, use the same flatline + cross-expiry settlement then subtract a conservative fixed cost proxy.
        return gross
    eligible["gross_pnl_proxy_inr"]=eligible.apply(row_pnl,axis=1)
    eligible["gross_pnl_proxy_inr_per_lot"]=eligible.gross_pnl_proxy_inr

    # Join exact selected net P&L for selected rows; candidate-level comparisons use gross P&L to avoid
    # implying broker fees are feature-dependent. The primary trade-level analysis remains on exact net P&L.
    selected_cols=["entry_timestamp","weekly_cycle","shift_points","net_pnl_inr","estimated_equal_max_profit_loss_inr"]
    s2=selected[selected_cols].rename(columns={"net_pnl_inr":"selected_net_pnl_inr","estimated_equal_max_profit_loss_inr":"selected_flatline_inr"})
    eligible=eligible.merge(s2,on=["entry_timestamp","weekly_cycle","shift_points"],how="left")
    eligible["candidate_outcome_label"]=np.where(eligible.selected, eligible.selected_net_pnl_inr>0, eligible.gross_pnl_proxy_inr>0)

    feat=add_greek_features(eligible)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    feat.to_csv(out/"candidate_entry_features.csv",index=False)
    selected_feat=feat[feat.selected].copy()
    selected_feat.to_csv(out/"selected_entry_features.csv",index=False)

    stats=univariate_trade_stats(selected_feat.rename(columns={"selected_net_pnl_inr":"net_pnl_inr"}))
    stats.to_csv(out/"winner_loser_univariate_stats.csv",index=False)
    cor=candidate_within_week_correlations(feat)
    cor.to_csv(out/"candidate_within_week_spearman.csv",index=False)

    selector_rows=[]
    for f in [
        "estimated_equal_max_profit_loss_inr","iv_term_spread","near_iv_skew_call_minus_put","next_iv_skew_call_minus_put",
        "abs_net_delta","abs_net_gamma","abs_net_vega","abs_net_theta_day","moneyness_pct","abs_moneyness_pct",
        "near_call_iv","near_put_iv","next_call_iv","next_put_iv"
    ]:
        if f in feat.columns:
            selector_rows.extend(cluster_selector_stats(feat,f))
    sel_df=pd.DataFrame(selector_rows)
    # Baseline is max positive flatline; all rows are the positive candidate set at the actual first-positive decision time.
    baseline=sel_df[(sel_df.feature=="estimated_equal_max_profit_loss_inr")&(sel_df.direction=="max")]
    sel_df.to_csv(out/"candidate_feature_selection_tests.csv",index=False)

    summary={
        "selected_trades":int(len(selected_feat)),
        "selected_winners":int((selected_feat.net_pnl_inr>0).sum()),
        "selected_losers":int((selected_feat.net_pnl_inr<=0).sum()),
        "candidate_rows_at_decision_times":int(len(feat)),
        "candidate_weeks":int(feat.weekly_cycle.nunique()),
        "black_scholes_rate_assumption":0.0,
        "greeks_method":"Black-Scholes implied-volatility inversion from observed option close, r=0, q=0; T measured to 15:30 IST expiry. These are entry-Greek proxies, not proprietary Sensibull Greeks.",
        "positive_candidate_definition":"static one-dimensional flatline > 0 at the decision timestamp",
        "primary_rule":"first positive weekly observation; among positive candidates maximize estimated equal max-profit=max-loss flatline",
        "selector_test_note":"Each alternative feature selects one candidate per week by max/min. These are exploratory univariate tests and must not be treated as an optimized final strategy without out-of-sample validation."
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print(stats.head(20).to_string(index=False))


if __name__=="__main__":
    main()
