#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.costs import CostModel, executed_premium, four_leg_entry_cashflow, stt_rate_for_date, exercise_stt_rate_for_date
from src.options_payoff import estimated_equal_max_profit_loss, intrinsic_value, static_flatline_value, near_expiry_manual_close_pnl

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--inputs',required=True)
    p.add_argument('--out-dir',required=True)
    p.add_argument('--slippage-pct',type=float,default=0.0025)
    p.add_argument('--brokerage-per-order',type=float,default=20.0)
    return p.parse_args()

def six_transaction_costs(entry_date, exit_date, entry_exec, far_call_exit_exec, far_put_exit_exec, near_put_intrinsic, lot, model):
    entry_turnover = entry_exec['premium_turnover']
    entry_sell = entry_exec['sell_premium_turnover']
    entry_buy = entry_exec['buy_premium_turnover']
    exit_turnover = far_call_exit_exec + far_put_exit_exec
    exit_sell = far_call_exit_exec
    exit_buy = far_put_exit_exec
    turnover = (entry_turnover + exit_turnover) * lot
    sell_turnover = (entry_sell + exit_sell) * lot
    buy_turnover = (entry_buy + exit_buy) * lot
    brokerage = 6.0 * model.brokerage_per_order_inr
    exchange = turnover * model.exchange_turnover_rate
    sebi = turnover * model.sebi_turnover_rate
    stamp_entry = entry_exec['buy_premium_turnover'] * lot * model.stamp_duty_buy_rate
    stamp_exit = exit_buy * lot * model.stamp_duty_buy_rate
    stt_entry_sales = entry_sell * lot * stt_rate_for_date(entry_date, model)
    stt_exit_sales = exit_sell * lot * stt_rate_for_date(exit_date, model)
    exercise_value = near_put_intrinsic * lot
    stt_exercise = exercise_value * exercise_stt_rate_for_date(exit_date, model)
    gst = model.gst_rate * (brokerage + exchange + sebi)
    total = brokerage + exchange + sebi + stamp + stt_sales + stt_exercise + gst
    return {
        'brokerage': brokerage, 'exchange_transaction': exchange, 'sebi_fee': sebi,
        'stamp_duty_entry': stamp_entry, 'stamp_duty_exit': stamp_exit,
        'stamp_duty': stamp_entry + stamp_exit,
        'stt_entry_sales': stt_entry_sales, 'stt_exit_sales': stt_exit_sales,
        'stt_sale_transactions': stt_entry_sales + stt_exit_sales,
        'stt_exercise': stt_exercise, 'gst': gst,
        'exercised_intrinsic_inr': exercise_value, 'total_costs': total
    }

def candidate_metrics(row, model):
    if pd.isna(row.near_call_close) or pd.isna(row.near_put_close) or pd.isna(row.far_call_close) or pd.isna(row.far_put_close):
        return None
    if pd.isna(row.near_settlement) or pd.isna(row.far_call_exit_close) or pd.isna(row.far_put_exit_close):
        return None
    if int(row.near_lot_size) != int(row.far_lot_size):
        return None
    lot = int(row.near_lot_size)
    entry_exec = four_leg_entry_cashflow(
        float(row.near_call_close), float(row.near_put_close),
        float(row.far_call_close), float(row.far_put_close),
        slippage_pct=model.slippage_pct
    )
    flatline = static_flatline_value(
        float(row.strike), str(row.near_expiry), str(row.far_expiry),
        float(row.near_call_close), float(row.near_put_close),
        float(row.far_call_close), float(row.far_put_close)
    )
    equal = estimated_equal_max_profit_loss(flatline, lot)
    near_spot = float(row.near_settlement)
    far_call_exit_exec = executed_premium(float(row.far_call_exit_close), -1, model.slippage_pct)
    far_put_exit_exec = executed_premium(float(row.far_put_exit_close), +1, model.slippage_pct)
    gross_per_unit = near_expiry_manual_close_pnl(
        near_spot, float(row.strike),
        entry_exec['sell_call'], entry_exec['buy_put'],
        entry_exec['buy_call'], entry_exec['sell_put'],
        far_call_exit_exec, far_put_exit_exec
    )
    long_put_intrinsic = intrinsic_value('PE', near_spot, float(row.strike))
    costs = six_transaction_costs(
        pd.Timestamp(row.entry_timestamp).date(),
        pd.Timestamp(row.near_exit_timestamp).date(),
        entry_exec, far_call_exit_exec, far_put_exit_exec,
        long_put_intrinsic, lot, model
    )
    return {
        'chart_pnl_inr': flatline * lot,
        'estimated_max_profit_inr': equal['estimated_max_profit_inr'],
        'estimated_min_pnl_inr': equal['estimated_min_pnl_inr'],
        'estimated_equal_max_profit_loss_inr': equal['estimated_equal_max_profit_loss_inr'],
        'estimated_all_green_flatline': equal['estimated_all_green_flatline'],
        'estimated_flatline_is_constant': True,
        'far_call_exit_executed_per_unit': far_call_exit_exec,
        'far_put_exit_executed_per_unit': far_put_exit_exec,
        'gross_pnl_inr': gross_per_unit * lot,
        'net_pnl_inr': gross_per_unit * lot - costs['total_costs'],
        'premium_turnover_inr': (entry_exec['premium_turnover'] + far_call_exit_exec + far_put_exit_exec) * lot,
        **costs,
    }

def select_first_positive_week(df):
    rows=[]
    for expiry, g in df.groupby('near_expiry', sort=True):
        g=g.sort_values('entry_timestamp')
        for ts, h in g.groupby('entry_timestamp', sort=True):
            pool=h[h['estimated_all_green_flatline'] & (h['estimated_equal_max_profit_loss_inr']>0)].copy()
            if pool.empty:
                continue
            pool=pool.sort_values(['estimated_equal_max_profit_loss_inr','shift_points'],ascending=[False,True])
            r=pool.iloc[0].copy()
            r['weekly_cycle']=expiry
            r['decision_timestamp']=ts
            r['decision_observation']='first_positive'
            rows.append(r)
            break
    return pd.DataFrame(rows)

def main():
    args=parse_args()
    model=CostModel(slippage_pct=args.slippage_pct, brokerage_per_order_inr=args.brokerage_per_order)
    df=pd.read_parquet(args.inputs)
    df=df[df['status'].eq('ok')].copy()
    records=[]
    for row in df.itertuples(index=False):
        m=candidate_metrics(row,model)
        if m is None:
            continue
        records.append({
            'entry_timestamp':row.entry_timestamp,'entry_date':row.entry_date,
            'candidate_label':row.candidate_label,'shift_points':int(row.shift_points),
            'strike':float(row.strike),'near_expiry':row.near_expiry,'far_expiry':row.far_expiry,
            'near_exit_timestamp':row.near_exit_timestamp,
            'far_call_exit_timestamp':row.far_call_exit_timestamp,
            'far_put_exit_timestamp':row.far_put_exit_timestamp,
            **m
        })
    cand=pd.DataFrame(records)
    if cand.empty: raise RuntimeError('No corrected candidates available')
    trades=select_first_positive_week(cand)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    cand.to_parquet(out/'candidate_results_near_exit.parquet',index=False)
    trades.to_csv(out/'weekly_selected_first_positive_near_exit.csv',index=False)
    summary={
        'weekly_cycles':int(cand['near_expiry'].nunique()),
        'candidate_rows':int(len(cand)),
        'selected_trades':int(len(trades)),
        'positive_weeks':int(len(trades)),
        'net_pnl_inr':float(trades['net_pnl_inr'].sum()) if not trades.empty else 0.0,
        'gross_pnl_inr':float(trades['gross_pnl_inr'].sum()) if not trades.empty else 0.0,
        'total_costs_inr':float(trades['total_costs'].sum()) if not trades.empty else 0.0,
        'win_rate_pct':float(100*(trades['net_pnl_inr']>0).mean()) if not trades.empty else None,
        'mean_net_pnl_inr':float(trades['net_pnl_inr'].mean()) if not trades.empty else None,
        'median_net_pnl_inr':float(trades['net_pnl_inr'].median()) if not trades.empty else None,
        'slippage_pct':args.slippage_pct,
        'brokerage_per_order_inr':args.brokerage_per_order,
        'exit_rule':'All four legs closed at near expiry; far CE/PE manually squared off at near-expiry option closes.'
    }
    (out/'summary_near_exit.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    print(json.dumps(summary,indent=2,default=str))

if __name__=='__main__':
    main()
