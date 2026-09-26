#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.costs import CostModel, four_leg_entry_cashflow, transaction_costs, trigger_base
from src.options_payoff import (
    estimated_equal_max_profit_loss,
    intrinsic_value,
    static_flatline_value,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--inputs', required=True)
    p.add_argument('--out-dir', default='results/phase7')
    p.add_argument('--lot-size', type=int, required=False)
    p.add_argument('--threshold-pct', type=float, default=2.5,
                   help='Legacy chart-percent threshold, retained only for sensitivity/compatibility.')
    p.add_argument('--trigger-base-mode',
                   choices=['buy_premium', 'spot_notional', 'configured_capital'],
                   default='buy_premium')
    p.add_argument('--configured-capital-per-lot', type=float)
    p.add_argument('--slippage-pct', type=float, default=0.0025)
    p.add_argument('--selection-mode',
                   choices=['max_equal_flatline', 'legacy_order'],
                   default='max_equal_flatline')
    p.add_argument('--selection-score',
                   choices=['equal_max_profit_loss_inr', 'chart_return_pct', 'max_profit_pct_margin'],
                   default='equal_max_profit_loss_inr',
                   help='Primary score for max_equal_flatline. chart_return_pct uses the configured trigger denominator and is not a proprietary Sensibull-margin replication.')
    p.add_argument('--selection-max-shift-points', type=int, default=400)
    p.add_argument('--selection-step-points', type=int, default=50)
    p.add_argument('--min-equal-max-profit-loss-inr', type=float, default=0.0)
    p.add_argument('--min-chart-return-pct', type=float, default=2.5,
                   help='Legacy 2.5% proxy gate when margin data are unavailable.')
    p.add_argument('--margin-column', default=None,
                   help='Optional candidate column containing reconstructed margin required in INR.')
    p.add_argument('--min-margin-profit-pct', type=float, default=2.5,
                   help='Margin-based max-profit percentage gate when margin-column is supplied.')
    p.add_argument('--fallback-order', default='ATM_MINUS_400,ATM_PLUS_400')
    return p.parse_args()


def candidate_row_metrics(row, args, model):
    near_lot = int(row.near_lot_size) if hasattr(row, 'near_lot_size') else args.lot_size
    next_lot = int(row.next_lot_size) if hasattr(row, 'next_lot_size') else args.lot_size
    if near_lot != next_lot:
        return None
    lot_size = args.lot_size if args.lot_size else near_lot

    premiums = [
        row.near_call_close,
        row.near_put_close,
        row.next_call_close,
        row.next_put_close,
    ]
    if any(pd.isna(x) for x in premiums) or pd.isna(row.near_settlement) or pd.isna(row.next_settlement):
        return None

    execs = four_leg_entry_cashflow(*premiums, slippage_pct=model.slippage_pct)
    raw_buy_premium_per_unit = float(row.near_put_close) + float(row.next_call_close)
    raw_buy_premium_inr = raw_buy_premium_per_unit * lot_size
    base = trigger_base(
        args.trigger_base_mode,
        float(row.spot_at_entry),
        lot_size,
        raw_buy_premium_inr,
        args.configured_capital_per_lot,
    )

    # This is the one-dimensional payoff-chart value: the same hypothetical
    # terminal spot is applied to both expiries, so the intrinsic terms cancel.
    flatline_value_per_unit = static_flatline_value(
        float(row.strike),
        str(row.near_expiry),
        str(row.next_expiry),
        float(row.near_call_close),
        float(row.near_put_close),
        float(row.next_call_close),
        float(row.next_put_close),
    )
    chart_pnl = flatline_value_per_unit * lot_size
    chart_return = 100.0 * chart_pnl / base if base > 0 else None

    # Sanity check against the cached algebraic entry cashflow.
    cached_chart_pnl = float(row.net_entry_cashflow_per_unit) * lot_size
    if abs(chart_pnl - cached_chart_pnl) > 1e-8:
        raise ValueError(
            f'flatline formula mismatch at {row.entry_timestamp} strike {row.strike}: '
            f'{chart_pnl} != {cached_chart_pnl}'
        )

    equal = estimated_equal_max_profit_loss(flatline_value_per_unit, lot_size)

    margin_required = None
    margin_profit_pct = None
    if args.margin_column and hasattr(row, args.margin_column):
        raw_margin = getattr(row, args.margin_column)
        if raw_margin is not None and not pd.isna(raw_margin) and float(raw_margin) > 0:
            margin_required = float(raw_margin)
            margin_profit_pct = 100.0 * equal['estimated_equal_max_profit_loss_inr'] / margin_required
    gross_per_unit = (
        float(row.net_entry_cashflow_per_unit)
        + float(row.next_settlement)
        - float(row.near_settlement)
    )
    gross_pnl = gross_per_unit * lot_size
    long_call_intrinsic = intrinsic_value(
        'CE', float(row.next_settlement), float(row.strike)
    )
    long_put_intrinsic = intrinsic_value(
        'PE', float(row.near_settlement), float(row.strike)
    )
    costs = transaction_costs(
        pd.Timestamp(row.entry_timestamp).date(),
        execs['premium_turnover'],
        execs['sell_premium_turnover'],
        execs['buy_premium_turnover'],
        long_call_intrinsic,
        long_put_intrinsic,
        lot_size,
        model,
    )
    net_pnl = gross_pnl - costs['total_costs']

    return {
        'chart_pnl_inr': chart_pnl,
        'chart_return_pct': chart_return,
        'estimated_max_profit_inr': equal['estimated_max_profit_inr'],
        'estimated_min_pnl_inr': equal['estimated_min_pnl_inr'],
        'estimated_equal_max_profit_loss_inr': equal['estimated_equal_max_profit_loss_inr'],
        'estimated_all_green_flatline': equal['estimated_all_green_flatline'],
        'estimated_flatline_is_constant': equal['estimated_flatline_is_constant'],
        'estimated_max_profit_pct_of_trigger_base': chart_return,
        'margin_required_inr': margin_required,
        'max_profit_pct_margin': margin_profit_pct,
        'gross_pnl_inr': gross_pnl,
        'net_pnl_inr': net_pnl,
        'total_costs_inr': costs['total_costs'],
        'premium_turnover_inr': execs['premium_turnover'] * lot_size,
        **costs,
    }


def _grid_candidates(group: pd.DataFrame, args) -> pd.DataFrame:
    max_shift = abs(int(args.selection_max_shift_points))
    step = abs(int(args.selection_step_points))
    if step <= 0:
        raise ValueError('selection-step-points must be > 0')
    if max_shift % step != 0:
        raise ValueError('selection-max-shift-points must be divisible by selection-step-points')

    x = group.copy()
    x = x[x['shift_points'].abs() <= max_shift]
    x = x[x['shift_points'].abs() % step == 0]
    return x


def select_trades(candidates: pd.DataFrame, args) -> pd.DataFrame:
    selected = []

    for ts, group in candidates.groupby('entry_timestamp', sort=True):
        if args.selection_mode == 'legacy_order':
            order = ['ATM'] + [x.strip() for x in args.fallback_order.split(',') if x.strip()]
            by_label = {r.candidate_label: r for r in group.itertuples(index=False)}
            chosen = None
            for label in order:
                r = by_label.get(label)
                if r is None:
                    continue
                if r.chart_return_pct is not None and r.chart_return_pct > args.threshold_pct:
                    chosen = r
                    break
            if chosen is not None:
                selected.append({**chosen._asdict(), 'selected_reason': 'legacy_chart_trigger'})
            continue

        grid = _grid_candidates(group, args)
        grid = grid[grid['estimated_all_green_flatline']]
        grid = grid[
            grid['estimated_equal_max_profit_loss_inr'] >
            float(args.min_equal_max_profit_loss_inr)
        ]
        if args.margin_column:
            if args.margin_column not in grid.columns:
                raise ValueError(f'margin column not found: {args.margin_column}')
            grid = grid[
                grid['max_profit_pct_margin'].notna()
                & (grid['max_profit_pct_margin'] > float(args.min_margin_profit_pct))
            ]
        elif args.min_chart_return_pct is not None:
            grid = grid[
                grid['chart_return_pct'].notna()
                & (grid['chart_return_pct'] > float(args.min_chart_return_pct))
            ]
        if grid.empty:
            continue

        if args.selection_score == 'equal_max_profit_loss_inr':
            ranked = grid.copy()
            ranked['_score'] = ranked['estimated_equal_max_profit_loss_inr']
        elif args.selection_score == 'chart_return_pct':
            ranked = grid[grid['chart_return_pct'].notna()].copy()
            ranked['_score'] = ranked['chart_return_pct']
        elif args.selection_score == 'max_profit_pct_margin':
            ranked = grid[grid['max_profit_pct_margin'].notna()].copy()
            ranked['_score'] = ranked['max_profit_pct_margin']
        else:
            raise ValueError(f'Unsupported selection score: {args.selection_score}')

        if ranked.empty:
            continue

        ranked['_abs_shift'] = ranked['shift_points'].abs()
        best = ranked.sort_values(
            by=['_score', 'estimated_equal_max_profit_loss_inr', '_abs_shift'],
            ascending=[False, False, True],
        ).iloc[0]
        selected.append({
            **best.drop(labels=['_score', '_abs_shift']).to_dict(),
            'selected_reason': 'max_equal_flatline_grid',
        })

    return pd.DataFrame(selected)


def main():
    args = parse_args()
    df = pd.read_parquet(args.inputs)
    required = [
        'entry_timestamp',
        'candidate_label',
        'shift_points',
        'strike',
        'near_call_close',
        'near_put_close',
        'next_call_close',
        'next_put_close',
        'near_settlement',
        'next_settlement',
        'net_entry_cashflow_per_unit',
        'status',
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'missing columns: {missing}')

    model = CostModel(slippage_pct=args.slippage_pct)
    df = df[df.status.eq('ok')].copy()

    candidate_records = []
    for row in df.itertuples(index=False):
        metrics = candidate_row_metrics(row, args, model)
        if metrics is None:
            continue
        candidate_records.append({
            'entry_timestamp': row.entry_timestamp,
            'entry_date': row.entry_date,
            'candidate_label': row.candidate_label,
            'shift_points': int(row.shift_points),
            'strike': row.strike,
            'near_expiry': row.near_expiry,
            'next_expiry': row.next_expiry,
            'spot_at_entry': row.spot_at_entry,
            'lot_size': (args.lot_size if args.lot_size else int(row.near_lot_size)),
            **metrics,
        })

    candidates = pd.DataFrame(candidate_records)
    if candidates.empty:
        raise RuntimeError('No complete candidate rows available')

    trades = select_trades(candidates, args)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    candidates.to_parquet(out / 'candidate_results.parquet', index=False)
    trades.to_parquet(out / 'selected_trades.parquet', index=False)

    grid_mask = (
        candidates.shift_points.abs().le(abs(args.selection_max_shift_points))
        & candidates.shift_points.ne(0)
        | candidates.shift_points.eq(0)
    )
    grid_candidates = candidates[
        candidates.shift_points.abs().le(abs(args.selection_max_shift_points))
        & (candidates.shift_points.abs() % abs(args.selection_step_points) == 0)
    ]
    positive_flatline = grid_candidates[grid_candidates.estimated_all_green_flatline]

    entries = int(candidates['entry_timestamp'].nunique())
    selected_entries = int(trades['entry_timestamp'].nunique()) if not trades.empty else 0
    summary = {
        'candidate_rows': int(len(candidates)),
        'eligible_entry_timestamps': entries,
        'grid_candidate_rows': int(len(grid_candidates)),
        'positive_flatline_grid_rows': int(len(positive_flatline)),
        'selected_trades': int(len(trades)),
        'selected_entry_timestamps': selected_entries,
        'selection_rate_pct': float(100 * selected_entries / entries) if entries else 0.0,
        'mean_net_pnl_inr': float(trades.net_pnl_inr.mean()) if not trades.empty else None,
        'median_net_pnl_inr': float(trades.net_pnl_inr.median()) if not trades.empty else None,
        'win_rate_pct': float(100 * (trades.net_pnl_inr > 0).mean()) if not trades.empty else None,
        'total_net_pnl_inr': float(trades.net_pnl_inr.sum()) if not trades.empty else 0.0,
        'total_costs_inr': float(trades.total_costs_inr.sum()) if not trades.empty else 0.0,
        'mean_estimated_equal_max_profit_loss_inr': (
            float(trades.estimated_equal_max_profit_loss_inr.mean())
            if not trades.empty else None
        ),
        'max_estimated_equal_max_profit_loss_inr': (
            float(trades.estimated_equal_max_profit_loss_inr.max())
            if not trades.empty else None
        ),
        'selection_mode': args.selection_mode,
        'selection_score': args.selection_score,
        'selection_max_shift_points': abs(args.selection_max_shift_points),
        'selection_step_points': abs(args.selection_step_points),
        'min_equal_max_profit_loss_inr': args.min_equal_max_profit_loss_inr,
        'legacy_threshold_pct': args.threshold_pct,
        'optional_min_chart_return_pct': args.min_chart_return_pct,
        'margin_column': args.margin_column,
        'min_margin_profit_pct': args.min_margin_profit_pct,
        'trigger_base_mode': args.trigger_base_mode,
        'slippage_pct': args.slippage_pct,
        'lot_size': args.lot_size,
        'note': 'The equal-max-profit=max-loss value is the positive flatline of the one-dimensional chart. It is not the true worst-case loss of the held cross-expiry position.',
    }
    (out / 'summary.json').write_text(
        json.dumps(summary, indent=2, default=str),
        encoding='utf-8',
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == '__main__':
    main()
