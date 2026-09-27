#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

KEYS = ['entry_timestamp','shift_points','strike','near_expiry','far_expiry']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    files = sorted(Path(args.input_dir).glob('*/*.parquet'))
    if not files:
        raise RuntimeError('No Phase 9A chunk parquet files were found')
    frames = [pd.read_parquet(p) for p in files]
    df = pd.concat(frames, ignore_index=True)
    before = len(df)
    df = df.drop_duplicates(subset=KEYS, keep='first').sort_values(['entry_timestamp','shift_points','strike']).reset_index(drop=True)
    removed = before - len(df)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)
    meta = {
        'chunk_files': [str(p) for p in files],
        'rows_before_dedup': int(before),
        'rows_after_dedup': int(len(df)),
        'duplicates_removed': int(removed),
        'entry_dates': int(pd.to_datetime(df['entry_timestamp']).dt.date.nunique()),
        'near_expiries': int(df['near_expiry'].nunique()),
        'columns': list(df.columns),
    }
    Path(args.out).with_suffix('.metadata.json').write_text(json.dumps(meta, indent=2, default=str), encoding='utf-8')
    print(json.dumps(meta, indent=2, default=str))

if __name__ == '__main__':
    main()
