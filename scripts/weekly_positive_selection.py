#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

def select_weekly(df: pd.DataFrame, observation: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {'entry_timestamp','entry_date','near_expiry','shift_points','strike','estimated_all_green_flatline','estimated_equal_max_profit_loss_inr','chart_pnl_inr','net_pnl_inr','total_costs_inr','spot_at_entry'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'missing columns: {sorted(missing)}')
    x = df[df['shift_points'].between(-400, 400) & (df['shift_points'] % 50 == 0)].copy()
    x['entry_timestamp'] = pd.to_datetime(x['entry_timestamp'])
    x['near_expiry'] = pd.to_datetime(x['near_expiry']).dt.date.astype(str)
    x = x[x['estimated_all_green_flatline'].fillna(False)].copy()
    x = x[x['estimated_equal_max_profit_loss_inr'] > 0].copy()
    cycles = []
    for expiry, g in x.groupby('near_expiry', sort=True):
        g = g.sort_values('entry_timestamp')
        chosen_ts = g['entry_timestamp'].iloc[0] if observation == 'first' else g['entry_timestamp'].iloc[-1]
        h = g[g['entry_timestamp'] == chosen_ts].copy()
        if h.empty:
            continue
        h['_score'] = h['estimated_equal_max_profit_loss_inr']
        best = h.sort_values(['_score','shift_points'], ascending=[False, True]).iloc[0].copy()
        best['weekly_cycle'] = expiry
        best['decision_observation'] = observation
        best['positive_at_selection'] = bool(best['chart_pnl_inr'] > 0)
        cycles.append(best.drop(labels=['_score']))
    selected = pd.DataFrame(cycles)
    return selected, x

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--observation', choices=['first','last'], default='first')
    args = ap.parse_args()

    df = pd.read_parquet(args.inputs)
    df = df[df.get('status', 'ok').eq('ok')].copy() if 'status' in df.columns else df.copy()
    selected, positive = select_weekly(df, args.observation)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    selected.to_csv(out / f'weekly_selected_{args.observation}.csv', index=False)
    summary = {
        'observation_rule': args.observation,
        'weekly_cycles_with_positive_candidate': int(selected['weekly_cycle'].nunique()) if not selected.empty else 0,
        'selected_trades': int(len(selected)),
        'positive_selected_trades': int(selected['positive_at_selection'].sum()) if not selected.empty else 0,
        'non_positive_selected_trades': int((~selected['positive_at_selection']).sum()) if not selected.empty else 0,
        'total_net_pnl_inr': float(selected['net_pnl_inr'].sum()) if not selected.empty else 0.0,
        'mean_net_pnl_inr': float(selected['net_pnl_inr'].mean()) if not selected.empty else None,
        'median_net_pnl_inr': float(selected['net_pnl_inr'].median()) if not selected.empty else None,
        'win_rate_pct': float(100*(selected['net_pnl_inr']>0).mean()) if not selected.empty else None,
        'total_costs_inr': float(selected['total_costs_inr'].sum()) if not selected.empty else 0.0,
        'mean_flatline_inr': float(selected['estimated_equal_max_profit_loss_inr'].mean()) if not selected.empty else None,
        'shift_counts': {str(k): int(v) for k,v in (selected['shift_points'].value_counts().sort_index().items() if not selected.empty else [])},
        'note': 'No 2.5% threshold, margin filter or percentage gate is used. The only candidate constraint is a positive all-green flatline; exactly one candidate is selected at the weekly observation.'
    }
    (out / f'weekly_summary_{args.observation}.json').write_text(json.dumps(summary, indent=2, default=str), encoding='utf-8')
    print(json.dumps(summary, indent=2, default=str))

if __name__ == '__main__':
    main()
