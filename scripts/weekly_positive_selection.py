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
    selected_rows = []
    diagnostics = []
    for expiry, g in x.groupby('near_expiry', sort=True):
        g = g.sort_values('entry_timestamp')
        chosen = None
        chosen_ts = None
        positive_count = 0
        if observation == 'max_in_week':
            pool = g[g['estimated_all_green_flatline'].fillna(False) & (g['estimated_equal_max_profit_loss_inr'] > 0)].copy()
            positive_count = len(pool)
            if not pool.empty:
                pool['_score'] = pool['estimated_equal_max_profit_loss_inr']
                chosen = pool.sort_values(['_score','entry_timestamp','shift_points'], ascending=[False,True,True]).iloc[0].copy()
                chosen_ts = chosen['entry_timestamp']
        elif observation == 'first_positive':
            for ts, h in g.groupby('entry_timestamp', sort=True):
                pool = h[h['estimated_all_green_flatline'].fillna(False) & (h['estimated_equal_max_profit_loss_inr'] > 0)].copy()
                positive_count += len(pool)
                if not pool.empty:
                    pool['_score'] = pool['estimated_equal_max_profit_loss_inr']
                    chosen = pool.sort_values(['_score','shift_points'], ascending=[False,True]).iloc[0].copy()
                    chosen_ts = ts
                    break
        else:
            chosen_ts = g['entry_timestamp'].iloc[0] if observation == 'first_observation' else g['entry_timestamp'].iloc[-1]
            h = g[g['entry_timestamp'] == chosen_ts].copy()
            pool = h[h['estimated_all_green_flatline'].fillna(False) & (h['estimated_equal_max_profit_loss_inr'] > 0)].copy()
            positive_count = len(pool)
            if not pool.empty:
                pool['_score'] = pool['estimated_equal_max_profit_loss_inr']
                chosen = pool.sort_values(['_score','shift_points'], ascending=[False,True]).iloc[0].copy()
        if chosen is None:
            diagnostics.append({'weekly_cycle':expiry,'decision_timestamp':str(chosen_ts) if chosen_ts is not None else None,'positive_candidates':int(positive_count),'selected_positive':False})
            continue
        chosen['weekly_cycle'] = expiry
        chosen['decision_observation'] = observation
        chosen['positive_at_selection'] = True
        chosen['positive_candidate_count_at_selection'] = int(positive_count)
        selected_rows.append(chosen.drop(labels=['_score']))
        diagnostics.append({'weekly_cycle':expiry,'decision_timestamp':str(chosen_ts),'positive_candidates':int(positive_count),'selected_shift_points':int(chosen['shift_points']),'selected_positive':True})
    return pd.DataFrame(selected_rows), pd.DataFrame(diagnostics)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--observation', choices=['first_positive','first_observation','last_observation','max_in_week'], default='first')
    args = ap.parse_args()

    df = pd.read_parquet(args.inputs)
    df = df[df.get('status', 'ok').eq('ok')].copy() if 'status' in df.columns else df.copy()
    selected, diagnostics = select_weekly(df, args.observation)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    selected.to_csv(out / f'weekly_selected_{args.observation}.csv', index=False)
    diagnostics.to_csv(out / f'weekly_diagnostics_{args.observation}.csv', index=False)
    summary = {
        'observation_rule': args.observation,
        'weekly_cycles': int(selected['weekly_cycle'].nunique()) if not selected.empty else 0,
        'weekly_cycles_with_positive_candidate': int((selected['positive_candidate_count_at_selection'] > 0).sum()) if not selected.empty else 0,
        'selected_trades': int(len(selected)),
        'positive_selected_trades': int(selected['positive_at_selection'].sum()) if not selected.empty else 0,
        'non_positive_selected_trades': int((~selected['positive_at_selection']).sum()) if not selected.empty else 0,
        'weeks_without_positive_candidate': int((selected['positive_candidate_count_at_selection'] == 0).sum()) if not selected.empty else 0,
        'total_net_pnl_inr': float(selected['net_pnl_inr'].sum()) if not selected.empty else 0.0,
        'mean_net_pnl_inr': float(selected['net_pnl_inr'].mean()) if not selected.empty else None,
        'median_net_pnl_inr': float(selected['net_pnl_inr'].median()) if not selected.empty else None,
        'win_rate_pct': float(100*(selected['net_pnl_inr']>0).mean()) if not selected.empty else None,
        'total_costs_inr': float(selected['total_costs_inr'].sum()) if not selected.empty else 0.0,
        'mean_flatline_inr': float(selected['estimated_equal_max_profit_loss_inr'].mean()) if not selected.empty else None,
        'shift_counts': {str(k): int(v) for k,v in (selected['shift_points'].value_counts().sort_index().items() if not selected.empty else [])},
        'note': 'No 2.5% threshold, margin filter or percentage gate is used. Exactly one candidate is selected at the chosen weekly observation; a non-positive week is diagnosed rather than silently skipped.'
    }
    (out / f'weekly_summary_{args.observation}.json').write_text(json.dumps(summary, indent=2, default=str), encoding='utf-8')
    print(json.dumps(summary, indent=2, default=str))

if __name__ == '__main__':
    main()
