#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

REQUIRED_TRADES = {'entry_timestamp', 'net_pnl_inr'}

def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path)

def summarize(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for key, g in df.groupby(group_col, dropna=False):
        pnl = pd.to_numeric(g['net_pnl_inr'], errors='coerce').dropna()
        wins = (pnl > 0).sum()
        gross_win = pnl[pnl > 0].sum()
        gross_loss = -pnl[pnl < 0].sum()
        rows.append({
            'regime': key,
            'trades': int(len(pnl)),
            'mean_net_pnl_inr': float(pnl.mean()) if len(pnl) else float('nan'),
            'median_net_pnl_inr': float(pnl.median()) if len(pnl) else float('nan'),
            'win_rate': float(wins / len(pnl)) if len(pnl) else float('nan'),
            'profit_factor': float(gross_win / gross_loss) if gross_loss else float('inf'),
            'total_net_pnl_inr': float(pnl.sum()) if len(pnl) else 0.0,
        })
    return pd.DataFrame(rows)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--trades', required=True, type=Path)
    ap.add_argument('--regimes', type=Path, default=None)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    trades = read_table(args.trades)
    missing = REQUIRED_TRADES - set(trades.columns)
    if missing:
        raise ValueError(f'Missing trade columns: {sorted(missing)}')
    trades['entry_timestamp'] = pd.to_datetime(trades['entry_timestamp'], utc=True)
    trades = trades.sort_values('entry_timestamp').reset_index(drop=True)
    if args.regimes is not None:
        regimes = read_table(args.regimes)
        if 'entry_timestamp' not in regimes.columns:
            raise ValueError('Regime table must contain entry_timestamp')
        regimes['entry_timestamp'] = pd.to_datetime(regimes['entry_timestamp'], utc=True)
        regimes = regimes.sort_values('entry_timestamp')
        trades = pd.merge_asof(trades, regimes, on='entry_timestamp', direction='backward', allow_exact_matches=True)
    summaries = []
    if args.regimes is not None:
        for col in regimes.columns:
            if col == 'entry_timestamp' or col not in trades.columns:
                continue
            summaries.append(summarize(trades.dropna(subset=[col]), col).assign(variable=col))
    if summaries:
        result = pd.concat(summaries, ignore_index=True)
    else:
        result = pd.DataFrame([{'variable':'overall','regime':'all','trades':len(trades),
            'mean_net_pnl_inr':trades['net_pnl_inr'].mean(),
            'median_net_pnl_inr':trades['net_pnl_inr'].median(),
            'win_rate':(trades['net_pnl_inr'] > 0).mean(),
            'profit_factor':float(trades.loc[trades['net_pnl_inr'] > 0, 'net_pnl_inr'].sum() / -trades.loc[trades['net_pnl_inr'] < 0, 'net_pnl_inr'].sum()) if (trades['net_pnl_inr'] < 0).any() else float('inf'),
            'total_net_pnl_inr':trades['net_pnl_inr'].sum()}])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)

if __name__ == '__main__':
    main()